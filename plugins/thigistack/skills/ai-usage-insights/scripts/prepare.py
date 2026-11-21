"""Pick the period to analyse and check there is enough to say something useful.

Usage:
    python3 -I prepare.py conversations.jsonl --period auto --out selected.jsonl --summary prepare.json
    python3 -I prepare.py conversations.jsonl --period custom --from 2026-09-01 --to 2026-10-31 ...
    python3 -I prepare.py ... --older older.jsonl

--period: auto (default), 30, 90, all, or custom (with --from/--to, dates inclusive).
auto takes the last 30 days if they hold enough usable chats, else 90 days, else everything.

--older writes the chats from before the period, for a cheap pass that only feeds the loop history, on every
run. An older chat has no user message from the period's start on, and at least one before it.
Each row holds its id, start, title and first user message cut to about OLDER_CHARS characters; the most recent
OLDER_CAP are kept. Suspected test runs are left out: the pass doesn't read far enough to tell.

The skill's own chats (read_claude_ai.py marks them): a run of the monthly reminder is left out entirely, and an
insights run (a chat where the user uploaded an export) is counted in the figures but never read or labelled, so it
can't turn into a pattern, a friction or a loop.

A usable chat has at least two user messages in the period and is not a suspected
test run. Test runs are spotted as chats started on the same day with the same
first message (people testing a prompt or skill). Suspects are still read in depth,
with a label in their digest: the model decides whether each one is a test run, so
two genuine chats that happen to open the same way are not lost. The tier counts
usable chats only, so it stays on the safe side.

Tiers (on usable chats):
    fewer than 10   too_little  - basic figures only; ask for a longer period
    10 to 29        light       - "first impressions"; skills only with strong evidence
    30 to 150       full        - the full report
    more than 150   capped      - the most recent --cap chats are read in depth, the rest only counted
"""
import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

MIN_USABLE, LIGHT_UNTIL, FULL_UNTIL = 10, 30, 150
OLDER_CAP, OLDER_CHARS = 300, 200


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def norm(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())[:200]


def cut(text, limit):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[:limit].rstrip() + " …"


def older_rows(convs, start, suspects):
    """Chats with no user message from start on and at least one before it, most recent first."""
    if start is None:
        return []
    rows = []
    for c in convs:
        users = [m for m in c["messages"] if m["role"] == "user" and m["ts"]]
        if not users or c["id"] in suspects or c.get("insights_run") or any(ts(m["ts"]) >= start for m in users):
            continue
        first = next((m for m in users if m["text"].strip()), users[0])
        rows.append({"id": c["id"][:8], "date": users[0]["ts"], "title": cut(c["title"], 120),
                     "first": cut(first["text"], OLDER_CHARS)})
    rows.sort(key=lambda r: ts(r["date"]), reverse=True)
    return rows


def user_msgs_in(c, start, end):
    return [m for m in c["messages"] if m["role"] == "user" and m["ts"]
            and (start is None or ts(m["ts"]) >= start) and (end is None or ts(m["ts"]) <= end)]


def flag_test_runs(convs):
    """Same first message on the same day in 2+ chats: most likely prompt or skill testing."""
    groups = defaultdict(list)
    for c in convs:
        users = [m for m in c["messages"] if m["role"] == "user" and m["text"].strip()]
        if users and len(norm(users[0]["text"])) >= 15:
            groups[(users[0]["ts"][:10], norm(users[0]["text"]))].append(c["id"])
    suspects = set()
    for ids in groups.values():
        if len(ids) >= 2:
            suspects.update(ids)
    return suspects


def window(convs, start, end, suspects):
    active = [c for c in convs if user_msgs_in(c, start, end)]
    multi = [c for c in active if len(user_msgs_in(c, start, end)) >= 2]
    usable = [c for c in multi if c["id"] not in suspects and not c.get("insights_run")]
    return active, multi, usable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--period", default="auto", choices=["auto", "30", "90", "all", "custom"])
    ap.add_argument("--from", dest="date_from")
    ap.add_argument("--to", dest="date_to")
    ap.add_argument("--cap", type=int, default=FULL_UNTIL)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--older", help="write the chats from before the period here, for the loop history pass")
    args = ap.parse_args()

    convs = [json.loads(l) for l in open(args.path, encoding="utf-8")]
    convs = [c for c in convs if any(m["ts"] for m in c["messages"])]
    reminder_runs = sum(1 for c in convs if c.get("reminder_run"))
    convs = [c for c in convs if not c.get("reminder_run")]
    if not convs:
        raise SystemExit("No conversations with messages found.")
    last = max(ts(m["ts"]) for c in convs for m in c["messages"] if m["ts"])
    first = min(ts(m["ts"]) for c in convs for m in c["messages"] if m["ts"])
    suspects = flag_test_runs(convs)

    end = None
    if args.period == "custom":
        start = datetime.fromisoformat(args.date_from).replace(tzinfo=timezone.utc) if args.date_from else None
        end = (datetime.fromisoformat(args.date_to).replace(tzinfo=timezone.utc) + timedelta(days=1)) if args.date_to else None
        label = f"{args.date_from or 'start'} to {args.date_to or 'end'}"
        chosen = "custom"
    else:
        options = [30, 90, None] if args.period == "auto" else [None if args.period == "all" else int(args.period)]
        for days in options:
            start = last - timedelta(days=days) if days else None
            _, _, usable = window(convs, start, None, suspects)
            if len(usable) >= LIGHT_UNTIL or days == options[-1]:
                break
        chosen = f"{days}d" if days else "all"
        label = f"Last {days} days" if days else "All history"

    active, multi, usable = window(convs, start, end, suspects)
    # read the most recent usable chats in depth, up to the cap; multi-turn suspects are read on top of it, so a
    # batch of test runs never pushes a genuine chat out
    to_read = sorted(usable, key=lambda c: user_msgs_in(c, start, end)[-1]["ts"], reverse=True)
    deep = {c["id"] for c in to_read[: args.cap]} | {c["id"] for c in multi
                                                     if c["id"] in suspects and not c.get("insights_run")}
    n = len(usable)
    tier = ("too_little" if n < MIN_USABLE else "light" if n < LIGHT_UNTIL else "full" if n <= FULL_UNTIL else "capped")
    messages = {
        "too_little": f"Only {n} chats with real back-and-forth in this period. That's too little to find patterns, "
                      "so the report shows basic figures only. Export a longer period (90 days or everything) for a full report.",
        "light": f"{n} usable chats: enough for first impressions. Skills are only suggested when the evidence is strong.",
        "full": f"{n} usable chats: enough for a full report.",
        "capped": f"{n} usable chats: more than one run can read. The most recent {args.cap} are read in depth; "
                  "the rest are only counted.",
    }
    with open(args.out, "w", encoding="utf-8") as out:
        for c in active:
            c["test_run_suspect"] = c["id"] in suspects
            c["deep"] = c["id"] in deep
            out.write(json.dumps(c, ensure_ascii=False) + "\n")
    older = older_rows(convs, start, suspects)
    kept = sorted(older[:OLDER_CAP], key=lambda r: ts(r["date"])) if args.older else []
    if args.older:
        with open(args.older, "w", encoding="utf-8") as out:
            out.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept))
    period_from = (start or first).date().isoformat()
    period_to = ((end - timedelta(days=1)) if end else last).date().isoformat()
    summary = {
        "period": chosen, "label": label, "from": period_from, "to": period_to,
        "since": start.isoformat() if start else None,
        "data_covers": [first.date().isoformat(), last.date().isoformat()],
        "chats_in_period": len(active),
        "single_question_chats": len(active) - len(multi),
        "multi_turn_chats": len(multi),
        "test_run_suspects": len([c for c in active if c["id"] in suspects]),
        "test_run_suspects_read": len([c for c in multi if c["id"] in suspects and c["id"] in deep]),
        "usable_chats": n, "read_in_depth": len(deep), "tier": tier, "message": messages[tier],
        "insights_runs": sum(1 for c in active if c.get("insights_run")), "reminder_runs": reminder_runs,
        "older_chats": {"count": len(older), "in_digest": len(kept),
                        "from": ts(kept[0]["date"]).date().isoformat() if kept else None,
                        "to": ts(kept[-1]["date"]).date().isoformat() if kept else None},
    }
    json.dump(summary, open(args.summary, "w", encoding="utf-8"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
