"""Find work that comes back on a rhythm or after the same kind of event: loop candidates (no AI involved).

Usage:
    python3 -I loops.py selected.jsonl facets_checked.jsonl --prepare prepare.json --aggregate aggregate.json \
        [--patterns patterns.json] [--older older.jsonl --older-labels older_labels.jsonl] [--tz <IANA time zone>] \
        --out loops.json

Reads the work chats that are no test run (aggregate.json's quotable_chats) and groups them three ways:
    task    by pattern: the task label, merged through patterns.json ({"pattern": ["label", ...]})
    watch   by watch_subject: the same "has X changed" question
    check   by each check the user applies to Claude's output (sources, numbers, house style, ...)

For each group it works out, from dates only:
    occurrences   chats in this period, plus earlier dates from the older chats in the export
    started_before  how many of this period's chats started before it (they count in this period, not as earlier)
    rhythm        weekly, every two weeks, monthly, most workdays, or irregular (one missed beat allowed)
    weekday       the weekday most occurrences fall on, when that is at least 60%
    month_part    start or end of the month, for a monthly rhythm
    kind_hints    time (a rhythm, or the user names one twice), event (60%+ start from the same kind
                  of outside input), watch, check

A group is a candidate with 3 or more occurrences and at least one kind hint; a check also needs two or more
different tasks, since a check inside one task is that task's own check. A task folds into a watch candidate
only when the task itself has the watch hint: an event task that names a subject stays its own.
The model decides in the synthesis step which candidates become loops; the report shows these numbers.

The history pass (--older and --older-labels) runs every time: prepare.py's older.jsonl gives each older chat's
date, the model's older_labels.jsonl its scope, task and watch subject. Work chats among them become earlier dates,
within HISTORY_DAYS of the period's end. Nothing is kept for the next run: a 90-day export brings the months back.
"""
import argparse
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

MIN_OCCURRENCES = 3
DOMINANT = 0.6
HISTORY_DAYS = 400
EVENT_TRIGGERS = {"incoming_message", "meeting", "new_document_or_data", "tool_output"}
# name, gaps in days for one beat, gaps that mean one beat was skipped, distinct days needed
RHYTHMS = [
    ("most workdays", (1, 3), (4, 5), 5),
    ("weekly", (5, 9), (12, 16), 3),
    ("every two weeks", (11, 17), (25, 31), 3),
    ("monthly", (25, 35), (55, 65), 3),
]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SKIP_CHECKS = {"", "other", "none_seen"}


def local_day(iso, tz):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz).date().isoformat()


def rhythm_of(days):
    """days: sorted distinct ISO dates."""
    ds = [date.fromisoformat(d) for d in days]
    gaps = [(b - a).days for a, b in zip(ds, ds[1:])]
    for name, base, missed, need in RHYTHMS:
        if len(ds) < need or not gaps:
            continue
        in_base = [base[0] <= g <= base[1] for g in gaps]
        in_missed = [missed[0] <= g <= missed[1] for g in gaps]
        if not all(b or m for b, m in zip(in_base, in_missed)):
            continue
        if sum(in_missed) > 1 and sum(in_base) < 2 * len(gaps) / 3:
            continue
        # gaps of 3 or 4 days fit "most workdays" one by one, but a median of 3 is twice a week
        if name == "most workdays" and sorted(gaps)[len(gaps) // 2] > 2:
            continue
        return name, gaps
    return "irregular", gaps


def weekday_of(days, rhythm):
    if len(days) < 3 or rhythm == "most workdays":
        return None, None
    counts = Counter(WEEKDAYS[date.fromisoformat(d).weekday()] for d in days)
    top, n = counts.most_common(1)[0]
    share = n / len(days)
    return (top, round(share, 2)) if share >= DOMINANT else (None, round(share, 2))


def month_part_of(days, rhythm):
    if rhythm != "monthly":
        return None
    dom = [date.fromisoformat(d).day for d in days]
    if sum(d <= 7 for d in dom) / len(dom) >= DOMINANT:
        return "start of the month"
    if sum(d >= 24 for d in dom) / len(dom) >= DOMINANT:
        return "end of the month"
    return None


def kind_hints(source, rhythm, triggers, signals):
    if source == "check":
        return ["check"]
    hints = []
    if rhythm not in ("irregular", None) or signals.count("cadence") >= 2:
        hints.append("time")
    total = sum(triggers.values())
    top, top_n = triggers.most_common(1)[0] if total else ("", 0)
    if top in EVENT_TRIGGERS and top_n / total >= DOMINANT:
        hints.append("event")
    if source == "watch" or (top == "outside_change" and top_n / total >= DOMINANT):
        hints.append("watch")
    return hints


def load_patterns(path):
    if not path:
        return {}
    data = json.load(open(path, encoding="utf-8"))
    data = data.get("patterns", data)
    mapping = {}
    for name, labels in data.items():
        mapping[name.strip().lower()] = name.strip().lower()
        for label in labels:
            mapping[label.strip().lower()] = name.strip().lower()
    return mapping


def older_history(older_path, labels_path, pattern_of, tz):
    """The older work chats as earlier dates per (source, label), plus what the report's note needs."""
    dates = {}
    for line in open(older_path, encoding="utf-8"):
        if line.strip():
            row = json.loads(line)
            dates[row["id"]] = local_day(row["date"], tz)
    history, read = defaultdict(list), set()
    for line in open(labels_path, encoding="utf-8"):
        if not line.strip():
            continue
        label = json.loads(line)
        # only chats prepare.py wrote, each once: a label for any other id has no date we can trust
        if label.get("id") not in dates or label["id"] in read:
            continue
        read.add(label["id"])
        if label.get("scope") != "work":
            continue
        task = (label.get("task") or "").strip().lower()
        watch = (label.get("watch_subject") or "").strip().lower()
        for source, value in (("task", pattern_of.get(task, task)), ("watch", watch)):
            if value:
                history[(source, value)].append(dates[label["id"]])
    days = sorted(dates[i] for i in read)
    info = {"chats": len(read), "from": days[0] if days else None, "to": days[-1] if days else None}
    return {key: sorted(found) for key, found in history.items()}, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conversations")
    ap.add_argument("facets")
    ap.add_argument("--prepare", required=True)
    ap.add_argument("--aggregate", required=True)
    ap.add_argument("--patterns")
    ap.add_argument("--older", help="prepare.py's older.jsonl, for the history pass")
    ap.add_argument("--older-labels", help="the model's labels for older.jsonl")
    ap.add_argument("--tz", default="UTC", help="the user's IANA time zone; SKILL.md always passes it")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if bool(args.older) != bool(args.older_labels):
        ap.error("--older and --older-labels go together")
    tz = ZoneInfo(args.tz)
    prep = json.load(open(args.prepare, encoding="utf-8"))
    period_from, period_to = prep["from"], prep["to"]

    convs = {}
    for line in open(args.conversations, encoding="utf-8"):
        c = json.loads(line)
        convs[c["id"][:8]] = c
    facets = [json.loads(l) for l in open(args.facets, encoding="utf-8") if l.strip()]
    # aggregate.py decides which chats are work and no test run; reading its list keeps the two in step
    quotable = set(json.load(open(args.aggregate, encoding="utf-8"))["quotable_chats"])
    work = [f for f in facets if f["id"] in convs and f["id"] in quotable]
    pattern_of = load_patterns(args.patterns)

    groups = defaultdict(lambda: {"chats": [], "triggers": Counter(), "inputs": Counter(), "outputs": Counter(),
                                  "checks": Counter(), "categories": Counter(), "patterns": set(),
                                  "signals": [], "quotes": []})
    for f in work:
        first = next((m for m in convs[f["id"]]["messages"] if m["role"] == "user" and m["ts"]), None)
        if not first:
            continue
        day = local_day(first["ts"], tz)
        task = (f.get("task") or "").strip().lower()
        pattern = pattern_of.get(task, task)
        keys = []
        if pattern:
            keys.append(("task", pattern))
        if (f.get("watch_subject") or "").strip():
            keys.append(("watch", f["watch_subject"].strip().lower()))
        keys += [("check", c) for c in sorted(set(f.get("checks", []))) if c not in SKIP_CHECKS]
        rec = f.get("recurrence") or {}
        for key in keys:
            g = groups[key]
            g["chats"].append((day, f["id"]))
            g["triggers"][f.get("trigger") or "unclear"] += 1
            g["inputs"][f.get("input_kind") or "none"] += 1
            g["outputs"][f.get("output_destination") or "unknown"] += 1
            g["categories"][f.get("category") or "unclear"] += 1
            for c in set(f.get("checks", [])):
                g["checks"][c] += 1
            if pattern:
                g["patterns"].add(pattern)
            g["signals"].append(rec.get("signal", "none"))
            if rec.get("signal", "none") != "none" and rec.get("quote"):
                g["quotes"].append({"chat": f["id"], "quote": rec["quote"]})

    previous, history_pass = older_history(args.older, args.older_labels, pattern_of, tz) if args.older else ({}, None)

    cutoff = (date.fromisoformat(period_to) - timedelta(days=HISTORY_DAYS)).isoformat()
    candidates = []
    for (source, label), g in groups.items():
        current = sorted(d for d, _ in g["chats"])
        # older.jsonl holds no chat with a message in this period, so an earlier date never repeats a current one
        earlier = [d for d in previous.get((source, label), []) if cutoff <= d < period_from]
        all_dates = earlier + current
        days = sorted(set(all_dates))
        rhythm, gaps = rhythm_of(days) if source != "check" else (None, [])
        weekday, weekday_share = weekday_of(days, rhythm) if source != "check" else (None, None)
        hints = kind_hints(source, rhythm, g["triggers"], g["signals"])
        if len(all_dates) < MIN_OCCURRENCES or not hints:
            continue
        if source == "check" and len(g["patterns"]) < 2:
            continue
        candidates.append({
            "id": f"{source}:{label}", "source": source, "label": label, "kind_hints": hints,
            "chats": [cid for _, cid in sorted(g["chats"])],
            "occurrences": len(all_dates), "earlier_occurrences": len(earlier),
            "started_before": sum(d < period_from for d in current),
            "first": all_dates[0], "last": all_dates[-1], "days": len(days),
            "months_seen": len({d[:7] for d in all_dates}),
            "rhythm": rhythm, "median_gap_days": sorted(gaps)[len(gaps) // 2] if gaps else None,
            "weekday": weekday, "weekday_share": weekday_share, "month_part": month_part_of(days, rhythm),
            "trigger": dict(g["triggers"].most_common()), "input_kind": dict(g["inputs"].most_common()),
            "output_destination": dict(g["outputs"].most_common()), "checks": dict(g["checks"].most_common()),
            "categories": dict(g["categories"].most_common()), "patterns": sorted(g["patterns"]),
            "recurrence_quotes": g["quotes"][:3],
        })

    # a watch task whose chats all sit inside a watch candidate is the same loop: keep the watch one. A task
    # started by an event (a package list handed over) stays its own, even when its chats name a subject
    watches = [c for c in candidates if c["source"] == "watch"]
    kept = []
    for c in candidates:
        if (c["source"] == "task" and "watch" in c["kind_hints"]
                and any(set(c["chats"]) <= set(w["chats"]) for w in watches)):
            continue
        kept.append(c)
    kept.sort(key=lambda c: (-c["occurrences"], c["id"]))

    result = {
        "period": {"from": period_from, "to": period_to},
        "min_occurrences": MIN_OCCURRENCES,
        **({"history_pass": history_pass} if history_pass else {}),
        "candidates": kept,
    }
    json.dump(result, open(args.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    older = f" and {history_pass['chats']} older chats" if history_pass else ""
    print(f"{len(kept)} loop candidates from {len(work)} work chats{older}; wrote {args.out}")
    for c in kept:
        print(f"  {c['id']}: {c['occurrences']}x, {c['rhythm'] or '-'}, hints {', '.join(c['kind_hints'])}")


if __name__ == "__main__":
    main()
