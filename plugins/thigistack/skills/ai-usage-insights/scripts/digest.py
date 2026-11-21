"""Condense normalised conversations into short text digests for the AI reading step.

Usage:
    python3 -I digest.py conversations.jsonl --outdir digests/ [--batch-chars 60000]

Writes:
    digests/quick.txt         one line per single-question chat (cheap label pass)
    digests/batch_NN.txt      multi-turn chat digests, grouped into batches
    digests/index.json        per chat: id, title, date, turns, batch, digest size

The digest keeps what the findings depend on: the user's messages (trimmed),
corrections (kept even in long chats), and only the gist of Claude's answers.
"""
import argparse
import json
import re
from pathlib import Path

FIRST_USER_CHARS = 700
USER_CHARS = 240
ASSISTANT_CHARS = 160
HEAD, TAIL, EXTRA_CORRECTIONS = 10, 6, 10

# Short replies that push back are the friction signal, so long chats keep them.
CORRECTION = re.compile(
    r"\b(no|not|nope|wrong|again|instead|actually|i meant|that's not|thats not|don't|dont|stop|"
    r"shorter|longer|too long|in dutch|in english|nederlands|engels|niet|nee|fout|opnieuw|"
    r"why did you|you forgot|you didn't|you didnt|still)\b",
    re.I,
)


def clean(text, limit):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[:limit].rstrip() + " …"


def feature_list(conv):
    tools = sorted({t for m in conv["messages"] for t in m["tools"]})
    return ", ".join(tools[:12]) + (" …" if len(tools) > 12 else "")


def digest(conv):
    users = [(i, m) for i, m in enumerate(conv["messages"]) if m["role"] == "user"]
    keep = set(range(min(HEAD, len(users)))) | set(range(max(0, len(users) - TAIL), len(users)))
    extra = [k for k in range(len(users)) if k not in keep and CORRECTION.search(users[k][1]["text"] or "")]
    keep |= set(extra[:EXTRA_CORRECTIONS])
    msgs = conv["messages"]
    lines = [
        f"### CHAT {conv['id'][:8]} | {conv['messages'][0]['ts'][:10]} | {conv['title']}",
        f"user turns: {len(users)} | edited-and-rerun: {conv.get('edits', 0)} | tools: {feature_list(conv) or 'none'}"
        + (" | POSSIBLE TEST RUN (same first message as another chat that day)" if conv.get("test_run_suspect") else ""),
    ]
    first_reply = next((m for m in msgs if m["role"] == "assistant" and m["text"]), None)
    skipped = 0
    for k, (i, m) in enumerate(users):
        if k not in keep:
            skipped += 1
            continue
        if skipped:
            lines.append(f"[… {skipped} user messages skipped …]")
            skipped = 0
        extras = []
        if m["pasted_chars"]:
            extras.append(f"pasted {m['pasted_chars']} chars")
        if m["attachments"] or m["files"]:
            names = [a["name"] for a in m["attachments"] if a.get("name")]
            extras.append("files: " + (", ".join(names[:3]) if names else str(m["files"])))
        tag = f" [{'; '.join(extras)}]" if extras else ""
        lines.append(f"U{k + 1}: {clean(m['text'], FIRST_USER_CHARS if k == 0 else USER_CHARS)}{tag}")
        if k == 0 and first_reply:
            lines.append(f"A(first reply gist): {clean(first_reply['text'], ASSISTANT_CHARS)}")
    if skipped:
        lines.append(f"[… {skipped} user messages skipped …]")
    last_reply = next((m for m in reversed(msgs) if m["role"] == "assistant" and m["text"]), None)
    if last_reply and last_reply is not first_reply:
        lines.append(f"A(last reply gist): {clean(last_reply['text'], ASSISTANT_CHARS)}")
    return "\n".join(lines)


def conv_is_counted_only(c):
    """prepare.py marks the chats to read in depth; others are only counted."""
    return c.get("deep") is False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--batch-chars", type=int, default=60000)
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    convs = [json.loads(l) for l in open(args.path, encoding="utf-8")]
    convs.sort(key=lambda c: c["messages"][0]["ts"] if c["messages"] else "")
    index, quick, batches, current, size = [], [], [], [], 0
    for c in convs:
        users = [m for m in c["messages"] if m["role"] == "user"]
        entry = {"id": c["id"], "title": c["title"], "date": (c["messages"][0]["ts"] or "")[:10],
                 "turns": len(users)}
        if c.get("insights_run"):
            # a run of this skill: counted in the figures, never read, so it can't become a pattern or a loop
            entry.update(batch="insights_run", chars=0)
            index.append(entry)
            continue
        if len(users) > 1 and conv_is_counted_only(c):
            entry.update(batch="counted_only", chars=0)
            index.append(entry)
            continue
        if len(users) <= 1:
            first = users[0]["text"] if users else ""
            flag = " | POSSIBLE TEST RUN" if c.get("test_run_suspect") else ""
            line = f"{c['id'][:8]} | {entry['date']} | {c['title']} | {clean(first, 300)}{flag}"
            quick.append(line)
            entry.update(batch="quick", chars=len(line))
        else:
            d = digest(c)
            if current and size + len(d) > args.batch_chars:
                batches.append(current)
                current, size = [], 0
            current.append(d)
            size += len(d)
            entry.update(batch=f"batch_{len(batches) + 1:02d}", chars=len(d))
        index.append(entry)
    if current:
        batches.append(current)
    (out / "quick.txt").write_text("\n".join(quick), encoding="utf-8")
    for n, b in enumerate(batches, 1):
        (out / f"batch_{n:02d}.txt").write_text("\n\n".join(b), encoding="utf-8")
    (out / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    total = sum(e.get("chars", 0) for e in index)
    print(f"{len(quick)} quick chats, {len(index) - len(quick)} multi-turn chats in {len(batches)} batches; "
          f"~{total // 4:,} tokens of digest in total")
    for n, b in enumerate(batches, 1):
        print(f"  batch_{n:02d}: {len(b)} chats, ~{sum(map(len, b)) // 4:,} tokens")


if __name__ == "__main__":
    main()
