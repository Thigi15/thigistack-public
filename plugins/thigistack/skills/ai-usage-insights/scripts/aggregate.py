"""Combine checked facets with the conversations into one summary (no AI involved).

Usage:
    python3 -I aggregate.py selected.jsonl facets_checked.jsonl --out aggregate.json

Only work chats that are not test runs feed the patterns, and never an insights run (read_claude_ai.py marks it). Personal and mixed
chats are counted, never described. Task labels are grouped as written; merging
labels that mean the same thing is left to the synthesis step.

A suspected test run that the model read decides by its own `test_run` label;
only a facet without that label falls back to prepare.py's suspicion.
`quotable_chats` lists the chats the report may quote or link: work chats that
are no test run. render_report.py refuses every other chat.
"""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime

IDLE_CAP_MIN = 10
LONG_CHAT_TURNS = 55


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def user_minutes(conv):
    """Time between Claude's answer and your next message, capped; a rough relative measure."""
    total, prev = 0.0, None
    for m in conv["messages"]:
        if m["role"] == "user":
            if prev is not None and prev["role"] == "assistant":
                total += min(max((ts(m["ts"]) - ts(prev["ts"])).total_seconds() / 60, 0), IDLE_CAP_MIN)
            else:
                total += 1
        prev = m
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conversations")
    ap.add_argument("facets")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    convs = {}
    for line in open(args.conversations, encoding="utf-8"):
        c = json.loads(line)
        convs[c["id"][:8]] = c
    facets = [json.loads(l) for l in open(args.facets, encoding="utf-8") if l.strip()]
    # an insights run is never digested; a facet for one anyway is dropped, so it can't feed patterns or loops
    facets = [f for f in facets if f["id"] in convs and not convs[f["id"]].get("insights_run")]

    is_test = lambda f: f["test_run"] if "test_run" in f else convs[f["id"]].get("test_run_suspect", False)
    work = [f for f in facets if f["scope"] == "work" and not is_test(f)]
    turns = lambda f: sum(1 for m in convs[f["id"]]["messages"] if m["role"] == "user")
    week = lambda f: ts(convs[f["id"]]["messages"][0]["ts"]).isocalendar()[1]

    by_cat = defaultdict(lambda: {"chats": 0, "minutes": 0.0})
    for f in work:
        by_cat[f["category"]]["chats"] += 1
        by_cat[f["category"]]["minutes"] += user_minutes(convs[f["id"]])
    total_min = sum(v["minutes"] for v in by_cat.values()) or 1

    friction, instructions, evidence = defaultdict(list), defaultdict(list), []
    tasks = defaultdict(lambda: {"chats": [], "weeks": set(), "categories": Counter()})
    handoffs = Counter()
    for f in work:
        for fr in f.get("friction", []):
            friction[fr["type"]].append({"chat": f["id"], "quote": fr["quote"]})
        for ins in f.get("instructions", []):
            instructions[ins["kind"]].append({"chat": f["id"], "text": ins["text"]})
        for ev in f.get("evidence", []):
            evidence.append({"chat": f["id"], **ev})
        if f.get("task"):
            t = tasks[f["task"].strip().lower()]
            t["chats"].append(f["id"])
            t["weeks"].add(week(f))
            t["categories"][f["category"]] += 1
        for h in set(f.get("handoffs", [])):
            handoffs[h] += 1

    result = {
        "chats_total": len(facets),
        "scope": dict(Counter(f["scope"] for f in facets)),
        "test_runs": sum(1 for f in facets if is_test(f)),
        "work_chats_analysed": len(work),
        "categories": {k: {"chats": v["chats"], "share_of_time_pct": round(100 * v["minutes"] / total_min, 1)}
                       for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1]["minutes"])},
        "mode": dict(Counter(f.get("mode", "single_question") for f in work).most_common()),
        "intent": dict(Counter(f.get("intent", "unclear") for f in work).most_common()),
        "output": dict(Counter(f.get("output", "none") for f in work).most_common()),
        "outcome": dict(Counter(f.get("outcome", "single_question") for f in work).most_common()),
        "success": dict(Counter(s for f in work for s in f.get("success", [])).most_common()),
        "friction": {k: v for k, v in sorted(friction.items(), key=lambda kv: -len(kv[1]))},
        "instructions_by_kind": dict(instructions),
        "evidence": evidence,
        "tasks": {k: {"chats": v["chats"], "weeks": sorted(v["weeks"]), "category": v["categories"].most_common(1)[0][0]}
                  for k, v in sorted(tasks.items(), key=lambda kv: -len(kv[1]["chats"]))},
        "starts_from_earlier_chats": [f["id"] for f in work if f.get("starts_from_earlier_chats")],
        "handoffs_chats": dict(handoffs.most_common()),
        "trigger": dict(Counter(f.get("trigger") or "unclear" for f in work).most_common()),
        "input_kind": dict(Counter(f.get("input_kind") or "none" for f in work).most_common()),
        "output_destination": dict(Counter(f.get("output_destination") or "unknown" for f in work).most_common()),
        "checks": dict(Counter(c for f in work for c in set(f.get("checks", []))).most_common()),
        "quotable_chats": sorted(f["id"] for f in work),
        "voice_chats": [f["id"] for f in work if f.get("voice")],
        "long_chats_over_55": sum(1 for f in work if turns(f) > LONG_CHAT_TURNS),
        "longest_chats_user_turns": sorted(((turns(f), f["id"]) for f in work), reverse=True)[:8],
        "titles": {f["id"]: convs[f["id"]]["title"] for f in work},
    }
    text = json.dumps(result, indent=1, ensure_ascii=False)
    open(args.out, "w", encoding="utf-8").write(text)
    print(f"{len(work)} work chats analysed; {len(result['tasks'])} task labels; "
          f"{sum(len(v) for v in friction.values())} friction quotes; wrote {args.out}")


if __name__ == "__main__":
    main()
