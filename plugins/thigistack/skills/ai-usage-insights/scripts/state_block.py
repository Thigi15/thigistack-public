"""Write the summary block for the next run, and find last run's block (no AI involved).

Usage:
    python3 -I state_block.py write --prepare prepare.json --stats stats.json --aggregate aggregate.json \
        --synthesis synthesis.json [--loops loops.json] --reminder scheduled|existing|declined|unavailable \
        [--run-date YYYY-MM-DD] --out state_block.md
    python3 -I state_block.py find [conversations-000.zip ...] [--artifact artifact.txt] --prepare prepare.json \
        [--run-date YYYY-MM-DD] --out previous.json

write: builds the block from this run's own outputs. The model pastes it unchanged at the end of its final reply,
so the next export carries it, and in Claude publishes it to an artifact as a backup. It holds the run date, the
period, the key figures and the names of what was suggested: no quotes, no chat ids and no chat titles, and at
most MAX_BYTES. A name that would push it over is cut short.

find: looks for blocks in every chat where the user uploaded a conversations export, on every branch, and in the
artifact's text when one is given. Only a block that parses fully, with a known version and the required keys,
counts; the newest run date wins. It writes previous.json with that block and the facts the report needs for the
comparison (days since, overlap, a long gap), or writes nothing when there is no earlier run.
"""
import argparse
import html
import io
import json
import re
import zipfile
from datetime import date
from pathlib import Path

try:
    import ijson  # streams large exports without loading them whole
except ImportError:  # pragma: no cover
    ijson = None

VERSION = "0.5.0"
FORMAT = "1"
HEADER = f"AI-USAGE-INSIGHTS-STATE v{FORMAT}"
HEADER_LINE = re.compile(r"^AI-USAGE-INSIGHTS-STATE v(\S+)$")
SENTENCE = "Saved for your next AI usage insights run; please don't edit."
MAX_BYTES = 2048
NAME_LIMITS = (60, 40, 24)
MAX_LOOPS = 3
REMINDER = ("scheduled", "existing", "declined", "unavailable")
LONG_GAP_DAYS = 60
# the same pattern as read_claude_ai.py: a chat with this upload is an insights run
EXPORT_FILE = re.compile(r"^conversations(-\d+)?( \(\d+\))?\.(zip|json)$", re.I)


# ---------------------------------------------------------------- write

def suggested_names(syn, loops, quotable):
    r = syn.get("reusable", {})
    syn_loops = syn.get("loops") or {}
    cand_ids = {c["id"] for c in (loops or {}).get("candidates", [])}
    # the same rules as the report: a loop rests on a candidate, an existing loop on a work chat, at most MAX_LOOPS
    shown = [lp["title"] for lp in syn_loops.get("suggested", [])
             if lp.get("candidate") in cand_ids and (lp.get("title") or "").strip()][:MAX_LOOPS]
    existing = [e["name"] for e in syn_loops.get("existing", []) if set(e.get("chats", [])) & quotable][:MAX_LOOPS]
    return {
        "preferences": [p["title"] for p in r.get("preferences", [])],
        "project_instructions": [p["title"] for p in r.get("project_instructions", [])],
        "prompts": [p["title"] for p in r.get("prompts", [])],
        "skills": [s["title"] for s in r.get("skills", [])],
        "loops": shown,
        "existing_loops": existing,
    }


def render(data):
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return f"{SENTENCE}\n\n```\n{HEADER}\n{payload}\n```\n"


def cut(name, limit):
    name = " ".join(str(name).split())
    return name if len(name) <= limit else name[:limit].rstrip() + "…"


def write(args):
    prep = json.load(open(args.prepare, encoding="utf-8"))
    windows = json.load(open(args.stats, encoding="utf-8"))["windows"]
    st = windows.get("period") or windows["all"]
    ag = json.load(open(args.aggregate, encoding="utf-8"))
    syn = json.load(open(args.synthesis, encoding="utf-8"))
    loops = json.load(open(args.loops, encoding="utf-8")) if args.loops else None
    names = suggested_names(syn, loops, set(ag.get("quotable_chats", [])))
    data = {
        "run": args.run_date,
        "skill_version": VERSION,
        "period": {k: prep[k] for k in ("from", "to", "label")},
        "figures": {
            "chats": st["conversations"],
            "active_days": st["active_days"],
            "user_messages": st["user_messages"],
            "work_chats_analysed": ag["work_chats_analysed"],
            "edited_pct": round(st["rewound_convs_pct"]),
            "long_chats": ag.get("long_chats_over_55"),
            "feature_use_pct": {k: round(v) for k, v in st["feature_use_pct"].items() if round(v)},
            "time_share_pct": {k: round(v["share_of_time_pct"]) for k, v in ag["categories"].items()
                               if round(v["share_of_time_pct"])},
        },
        "reminder": args.reminder,
    }
    for limit in NAME_LIMITS:
        data["suggested"] = {kind: [cut(n, limit) for n in found] for kind, found in names.items()}
        text = render(data)
        if len(text.encode("utf-8")) <= MAX_BYTES:
            break
    else:
        raise SystemExit(f"the block is over {MAX_BYTES} bytes even with short names; not written")
    open(args.out, "w", encoding="utf-8").write(text)
    print(f"wrote {args.out} ({len(text.encode('utf-8'))} bytes): paste it unchanged at the end of the final reply")


# ---------------------------------------------------------------- find

def iter_sources(paths):
    """Yield binary file objects for every conversations.json found (as in read_claude_ai.py)."""
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


def uploaded_an_export(messages):
    return any(EXPORT_FILE.match((f.get("file_name") or "").strip())
               for m in messages if m.get("sender") == "human"
               for key in ("files", "files_v2", "attachments") for f in m.get(key) or [])


def message_text(m):
    texts = [b.get("text") or "" for b in m.get("content") or [] if b.get("type") == "text"]
    return "\n".join(texts) if texts else (m.get("text") or "")


def valid_date(value):
    try:
        date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False


def complete(data):
    period = data.get("period") if isinstance(data, dict) else None
    return (isinstance(data, dict) and valid_date(data.get("run")) and isinstance(data.get("skill_version"), str)
            and isinstance(period, dict) and valid_date(period.get("from")) and valid_date(period.get("to"))
            and period["from"] <= period["to"] and isinstance(period.get("label"), str) and isinstance(data.get("figures"), dict)
            and isinstance(data.get("suggested"), dict) and data.get("reminder") in REMINDER + (None,))


def blocks_in(text, notes):
    """Every complete block in text: a header line, then the JSON on the next non-empty line."""
    found = []
    lines = [line.strip() for line in text.splitlines()]
    for i, line in enumerate(lines):
        header = HEADER_LINE.match(line)
        if not header:
            continue
        if header.group(1) != FORMAT:
            notes.append(f"ignored a block of unknown version v{header.group(1)}")
            continue
        payload = next((rest for rest in lines[i + 1:] if rest), "")
        try:
            data = json.loads(payload)
        except ValueError:
            notes.append("ignored a block that isn't valid JSON")
            continue
        if complete(data):
            found.append(data)
        else:
            notes.append("ignored a block without the required keys")
    return found


def export_blocks(paths, notes):
    found = []
    for fh in iter_sources(paths):
        for conv in (ijson.items(fh, "item", use_float=True) if ijson else json.load(fh)):
            messages = conv.get("chat_messages") or []
            if uploaded_an_export(messages):
                for m in messages:
                    found += blocks_in(message_text(m), notes)
    return found


def artifact_blocks(path, notes):
    text = open(path, encoding="utf-8").read()
    # a published page holds the block as HTML: tags become line breaks, entities their characters
    return blocks_in(html.unescape(re.sub(r"<[^>]+>", "\n", text)), notes)


def days_between(start, end):
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def find(args):
    notes = []
    found = [(b, "export") for b in export_blocks(args.parts, notes)]
    if args.artifact:
        found += [(b, "artifact") for b in artifact_blocks(args.artifact, notes)]
    for note in sorted(set(notes)):
        print(f"NOTE: {note}")
    if not found:
        print("No earlier run found: there is no comparison this time. Nothing written.")
        return
    # newest run first; on the same date the export's copy, which is read first
    block, source = max(found, key=lambda pair: pair[0]["run"])
    prep = json.load(open(args.prepare, encoding="utf-8"))
    then, now = block["period"], {"from": prep["from"], "to": prep["to"]}
    overlap_days = max(0, days_between(max(then["from"], now["from"]), min(then["to"], now["to"])) + 1)
    shorter = min(days_between(then["from"], then["to"]), days_between(now["from"], now["to"])) + 1
    days_since = days_between(block["run"], args.run_date)
    previous = {"source": source, "block": block, "days_since": days_since, "overlap_days": overlap_days,
                "overlap": overlap_days / shorter > 0.5, "long_gap": days_since > LONG_GAP_DAYS}
    json.dump(previous, open(args.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"found the run of {block['run']} in the {source}, {days_since} day{'' if days_since == 1 else 's'} ago; "
          f"wrote {args.out}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    w = sub.add_parser("write")
    for k in ("prepare", "stats", "aggregate", "synthesis", "out"):
        w.add_argument(f"--{k}", required=True)
    w.add_argument("--loops")
    w.add_argument("--reminder", required=True, choices=REMINDER)
    w.add_argument("--run-date", default=date.today().isoformat(), type=lambda s: date.fromisoformat(s).isoformat())
    f = sub.add_parser("find")
    f.add_argument("parts", nargs="*", help="the export: conversations-000.zip and any further parts")
    f.add_argument("--artifact", help="the text of the 'AI usage insights: state' artifact, saved to a file")
    f.add_argument("--prepare", required=True)
    f.add_argument("--run-date", default=date.today().isoformat(), type=lambda s: date.fromisoformat(s).isoformat())
    f.add_argument("--out", required=True)
    args = ap.parse_args()
    write(args) if args.command == "write" else find(args)


if __name__ == "__main__":
    main()
