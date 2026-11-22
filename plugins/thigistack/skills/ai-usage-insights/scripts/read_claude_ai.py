"""Read a claude.ai data export and write normalised conversations as JSONL.

Usage:
    python3 -I read_claude_ai.py <export_path> [<export_path> ...] --out conversations.jsonl

<export_path> can be a conversations-NNN.zip, a folder, or a conversations.json.
All parts (conversations-000.zip, conversations-001.zip, ...) can be passed at once.

Output: one JSON object per conversation, following the common schema:
    {id, source, title, url, created, updated, branched, n_messages_total, insights_run, reminder_run,
     messages: [{role, ts, text, tools, calls, tool_errors, attachments, pasted_chars,
                 files, thinking}]}

calls: per tool call, only what zoom.py needs to tell deliverables and their versions apart: the tool name, its
action, the file extension, whether it was made from an artifact type, and short hashes of the url or id and of each
path it wrote to. A tool call's url, id or path itself is never kept: file names can name customers or people.
(Uploaded attachments keep their names: digest.py shows them to the model, and they never reach the report.)

insights_run: the user uploaded a conversations export in this chat, on any branch: a run of this skill.
reminder_run: the chat opens with the monthly reminder's fixed first line.

Only the main thread is kept: from the most recent leaf message back to the
root. Edited or regenerated branches are counted (branched=True) but dropped,
so abandoned attempts are not double-counted.
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

try:
    import ijson  # streams large exports without loading them whole
except ImportError:  # pragma: no cover
    ijson = None

ROOT = "00000000-0000-4000-8000-000000000000"
# The app prepends UI state (which artifact tab was open) to some user messages.
UI_CONTEXT = re.compile(r"<artifact-view-context\b.*?</artifact-view-context>\s*", re.S)
# A chat where the user uploaded an export is a run of this skill; state_block.py uses the same pattern.
# " (1)" is how a browser names a second download of the same file.
EXPORT_FILE = re.compile(r"^conversations(-\d+)?( \(\d+\))?\.(zip|json)$", re.I)
# The monthly reminder's fixed first line (references/data-export.md); its runs are left out entirely.
REMINDER_LINE = "AI usage insights: monthly reminder"


def iter_sources(paths):
    """Yield binary file objects for every conversations.json found."""
    for p in map(Path, paths):
        if p.is_dir():
            for f in sorted(p.rglob("conversations*.json")):
                yield f.open("rb")
        elif p.suffix == ".zip":
            z = zipfile.ZipFile(p)
            for name in z.namelist():
                if Path(name).name.startswith("conversations") and name.endswith(".json"):
                    yield io.BufferedReader(z.open(name))
        else:
            yield p.open("rb")


def main_thread(messages):
    """Return the messages on the main path (latest leaf back to the root)."""
    by_id = {m["uuid"]: m for m in messages}
    has_child = {m.get("parent_message_uuid") for m in messages}
    leaves = [m for m in messages if m["uuid"] not in has_child]
    if not leaves:
        return messages
    leaf = max(leaves, key=lambda m: m.get("created_at") or "")
    path, cur, seen = [], leaf, set()
    while cur is not None and cur["uuid"] not in seen:
        seen.add(cur["uuid"])
        path.append(cur)
        cur = by_id.get(cur.get("parent_message_uuid"))
    return list(reversed(path))


def count_rewinds(messages):
    """Count user rewinds: the same parent got several user messages.

    Returns (edits, resends): edits changed the text, resends repeated it.
    """
    kids = {}
    for m in messages:
        if m.get("sender") == "human":
            kids.setdefault(m.get("parent_message_uuid"), []).append(m)
    edits = resends = 0
    for group in kids.values():
        group.sort(key=lambda m: m.get("created_at") or "")
        for a, b in zip(group, group[1:]):
            if (a.get("text") or "").strip() == (b.get("text") or "").strip():
                resends += 1
            else:
                edits += 1
    return edits, resends


# where a tool call names the thing it writes to: an id (url, id, a doc's container id) and the paths, each hashed
# on its own. A first publish carries only a path, its later edits only a url; zoom.py pairs them. A doc edit's
# `ref` names a node inside the doc, not the doc, so it is no key.
ID_KEYS = ("url", "id", "page_id")
PATH_KEYS = ("path", "file_path")
# an action is kept only when it is one word: a shell command in `command` would carry paths and names
ACTION_WORD = re.compile(r"[a-z][a-z_]{0,23}")


def short_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10] if text else ""


def call_of(block):
    """One tool call as zoom.py reads it; see the module docstring for why the targets are hashed."""
    params = block.get("input") if isinstance(block.get("input"), dict) else {}
    action = next((params[k] for k in ("action", "command", "kind") if isinstance(params.get(k), str)), "")
    action = action if ACTION_WORD.fullmatch(action) else ""
    target = next((params[k] for k in ID_KEYS if isinstance(params.get(k), str) and params[k]), "")
    container = params.get("container")
    if not target and isinstance(container, dict):
        if isinstance(container.get("id"), str):
            target = container["id"]
        elif "create" in container and not action:
            action = "create"
    paths = [params.get(k) for k in PATH_KEYS] + list(params.get("filepaths") or [])
    paths = list(dict.fromkeys(p for p in paths if isinstance(p, str) and p))
    return {"tool": block.get("name") or "", "action": action, "key": short_hash(target),
            "paths": [short_hash(p) for p in paths], "exts": [os.path.splitext(p)[1].lower() for p in paths],
            "typed": bool(params.get("type_url"))}


def normalise_message(m):
    blocks = m.get("content") or []
    starts = [b.get("start_timestamp") for b in blocks if b.get("start_timestamp")]
    texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
    if not texts and m.get("text"):
        texts = [m["text"]]
    viewing_artifact = any("<artifact-view-context" in t for t in texts)
    texts = [UI_CONTEXT.sub("", t) for t in texts]
    tools = [b.get("name") for b in blocks if b.get("type") == "tool_use"]
    errors = sum(1 for b in blocks if b.get("type") == "tool_result" and b.get("is_error"))
    attachments = [
        {"name": a.get("file_name"), "type": a.get("file_type"), "size": a.get("file_size")}
        for a in m.get("attachments") or []
    ]
    pasted = sum(len(a.get("extracted_content") or "") for a in m.get("attachments") or [])
    return {
        "role": "user" if m.get("sender") == "human" else "assistant",
        "ts": m.get("created_at"),
        "ts_start": min(starts) if starts else m.get("created_at"),  # assistant created_at is when the answer finished
        "text": "\n".join(t for t in texts if t).strip(),
        "tools": tools,
        "calls": [call_of(b) for b in blocks if b.get("type") == "tool_use"],
        "tool_errors": errors,
        "attachments": attachments,
        "pasted_chars": pasted,
        "files": len(m.get("files") or []),
        "thinking": any(b.get("type") == "thinking" for b in blocks),
        "viewing_artifact": viewing_artifact,
    }


def uploaded_an_export(messages):
    """True when any user message, on any branch, carries a conversations export."""
    return any(EXPORT_FILE.match((f.get("file_name") or "").strip())
               for m in messages if m.get("sender") == "human"
               for key in ("files", "files_v2", "attachments") for f in m.get(key) or [])


def normalise_conversation(conv):
    msgs = conv.get("chat_messages") or []
    thread = main_thread(msgs)
    edits, resends = count_rewinds(msgs)
    first = next((m for m in thread if m.get("sender") == "human"), None)
    first_text = UI_CONTEXT.sub("", (first or {}).get("text") or "").lstrip()
    return {
        "id": conv["uuid"],
        "source": "claude.ai",
        "title": conv.get("name") or "",
        "url": f"https://claude.ai/chat/{conv['uuid']}",
        "created": conv.get("created_at"),
        "updated": conv.get("updated_at"),
        "branched": len(thread) < len(msgs),
        "n_messages_total": len(msgs),
        "edits": edits,
        "resends": resends,
        "insights_run": uploaded_an_export(msgs),
        "reminder_run": first_text.startswith(REMINDER_LINE),
        "messages": [normalise_message(m) for m in thread],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    n = skipped = 0
    # An organization export (a Team or Enterprise Primary Owner's) holds every member's chats. This skill reads one
    # person's own chats only, so more than one account means stop and keep nothing. An export without account
    # fields cannot be told apart; data-export.md tells Primary Owners not to upload theirs.
    accounts = set()
    with open(args.out, "w", encoding="utf-8") as out:
        for fh in iter_sources(args.paths):
            items = ijson.items(fh, "item", use_float=True) if ijson else json.load(fh)
            for conv in items:
                account = conv.get("account")
                account = account.get("uuid") if isinstance(account, dict) else None
                if account:
                    accounts.add(account)
                if len(accounts) > 1:
                    break
                if not conv.get("chat_messages"):
                    skipped += 1
                    continue
                out.write(json.dumps(normalise_conversation(conv), ensure_ascii=False) + "\n")
                n += 1
            if len(accounts) > 1:
                break
    if len(accounts) > 1:
        os.remove(args.out)
        # 3, not 2: argparse uses 2 for a usage error, and SKILL.md acts on this code.
        print("refused: this export holds the chats of more than one account, such as an organization export. "
              "This skill reads one person's own chats only. Nothing was kept.", file=sys.stderr)
        sys.exit(3)
    print(f"wrote {n} conversations to {args.out} (skipped {skipped} empty)", file=sys.stderr)


if __name__ == "__main__":
    main()
