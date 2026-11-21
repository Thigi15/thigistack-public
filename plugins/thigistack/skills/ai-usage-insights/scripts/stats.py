"""Deterministic usage statistics from normalised conversations (no AI involved).

Usage:
    python3 -I stats.py selected.jsonl --since <prepare.json "since"> --tz <the user's IANA time zone> --out stats.json
    python3 -I stats.py conversations.jsonl --days 30 90 --out stats.json

With --since, one window called "period" is computed (messages from that moment on).
active_dates lists the local dates with a message from the user; the Wrapped draws one dot per day from them.
Without it, windows are counted back from the most recent message, plus "all".
"""
import argparse
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IDLE_CAP_MIN = 10  # a reply-to-next-message gap longer than this counts as 10 minutes

# Tool name -> feature group. Names vary per surface, so match on prefixes too.
FEATURES = [
    ("web search", ("web_search", "web_search_fast", "WebSearch", "web_fetch", "WebFetch", "image_search")),
    ("deep research", ("launch_extended_search_task",)),
    ("code & files", ("bash_tool", "create_file", "str_replace", "view", "repl", "present_files",
                      "Bash", "Read", "Write", "Edit", "SendUserFile")),
    ("artifacts & docs", ("artifacts", "Artifact", "Claude Docs:", "mcp__Claude_Docs__", "mcp__claude-artifacts__")),
    ("visuals", ("visualize:", "mcp__visualize__", "chart_display")),
    ("memory", ("memory_", "mcp__memory__")),
    ("past chats", ("conversation_search", "recent_chats", "read_conversation", "mcp__claude_ai__")),
    ("project knowledge", ("project_knowledge_search",)),
    ("connectors", ("Notion:", "mcp__Notion__", "Gmail", "Google", "Slack", "gdrive", "Atlassian")),
    ("skills", ("Skill", "propose_skills", "search_skills", "search_plugins", "suggest_plugin_install")),
    ("browser", ("Claude in Chrome:", "mcp__claude-in-chrome__", "Claude_Browser")),
    ("task list", ("TaskCreate", "TaskUpdate")),
    ("display cards", ("recipe_display", "places_", "map_display", "comparison_card", "itinerary_display",
                       "step_card", "link_preview", "event_search", "fetch_sports_data", "show_recommendation",
                       "weather", "product_carousel", "featured_card")),
    ("internal", ("tool_search", "ToolSearch", "user_time", "user_location", "suggest_", "search_mcp_registry",
                  "recommend_claude_apps", "reminder_create", "Projects")),
    ("questions widget", ("ask_user_input", "AskUserQuestion")),
    ("draft messages", ("message_compose",)),
]


def feature_of(name):
    for label, keys in FEATURES:
        if any(name == k or name.startswith(k) for k in keys):
            return label
    return "other"


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def load(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def lang_detector():
    try:
        from lingua import Language, LanguageDetectorBuilder
        det = LanguageDetectorBuilder.from_languages(Language.DUTCH, Language.ENGLISH).build()
        names = {Language.DUTCH: "nl", Language.ENGLISH: "en"}
        return lambda t: names.get(det.detect_language_of(t), "other")
    except ImportError:
        return None


def summarise(convs, tz, detect, start=None):
    """Stats for conversations active in the window; message stats only count
    messages inside the window (start=None means all data)."""
    in_win = lambda m: m["ts"] and (start is None or parse_ts(m["ts"]) >= start)
    user_turns, user_minutes, claude_minutes = [], 0.0, 0.0
    days, hours, weekdays = set(), Counter(), Counter()
    feature_convs, tool_errors = Counter(), 0
    rewound = edits = with_paste = with_files = thinking_convs = 0
    pasted_chars = 0
    langs = Counter()
    length_buckets = Counter()
    per_month = Counter()
    for c in convs:
        msgs = [m for m in c["messages"] if in_win(m)]
        users = [m for m in msgs if m["role"] == "user"]
        n = len(users)
        user_turns.append(n)
        length_buckets["1 turn" if n <= 1 else "2-3" if n <= 3 else "4-10" if n <= 10 else "11+"] += 1
        rewound += c.get("edits", 0) > 0
        edits += c.get("edits", 0)
        prev = None
        for m in c["messages"]:
            if in_win(m):
                if m["role"] == "user" and prev is not None and prev["role"] == "assistant":
                    gap = (parse_ts(m["ts"]) - parse_ts(prev["ts"])).total_seconds() / 60
                    user_minutes += min(max(gap, 0), IDLE_CAP_MIN)
                elif m["role"] == "user":
                    user_minutes += 1  # first message of a conversation: assume a minute to write it
                if m["role"] == "assistant":
                    run = (parse_ts(m["ts"]) - parse_ts(m.get("ts_start") or m["ts"])).total_seconds() / 60
                    claude_minutes += max(run, 0)
            prev = m
        for m in users:
            local = parse_ts(m["ts"]).astimezone(tz)
            days.add(local.date())
            hours[local.hour] += 1
            weekdays[local.strftime("%a")] += 1
            if detect and len(m["text"]) >= 20:
                langs[detect(m["text"][:500])] += 1
        if msgs:
            per_month[parse_ts(msgs[0]["ts"]).astimezone(tz).strftime("%Y-%m")] += 1
        feats = {feature_of(t) for m in msgs for t in m["tools"]} - {"internal"}
        feature_convs.update(feats)
        tool_errors += sum(m["tool_errors"] for m in msgs)
        with_paste += any(m["pasted_chars"] for m in users)
        with_files += any(m["files"] or m["attachments"] for m in users)
        pasted_chars += sum(m["pasted_chars"] for m in users)
        thinking_convs += any(m["thinking"] for m in msgs)
    n = len(convs) or 1
    pct = lambda x: round(100 * x / n, 1)
    return {
        "conversations": len(convs),
        "active_days": len(days),
        "active_dates": sorted(d.isoformat() for d in days),
        "user_messages": sum(user_turns),
        "user_turns_median": statistics.median(user_turns) if user_turns else 0,
        "user_turns_mean": round(statistics.mean(user_turns), 1) if user_turns else 0,
        "length_buckets": dict(length_buckets),
        "your_time_hours": round(user_minutes / 60, 1),
        "claude_working_hours": round(claude_minutes / 60, 1),
        "rewound_convs_pct": pct(rewound),
        "edits_total": edits,
        "with_pasted_text_pct": pct(with_paste),
        "with_files_pct": pct(with_files),
        "pasted_chars_total": pasted_chars,
        "extended_thinking_pct": pct(thinking_convs),
        "tool_errors": tool_errors,
        "feature_use_pct": {k: pct(v) for k, v in feature_convs.most_common()},
        "language_user_msgs": dict(langs),
        "hours": {h: hours[h] for h in range(24)},
        "weekdays": dict(weekdays),
        "per_month": dict(sorted(per_month.items())),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--days", type=int, nargs="*", default=[30, 90])
    ap.add_argument("--since", help="ISO timestamp; computes a single window called 'period'")
    ap.add_argument("--tz", default="UTC", help="the user's IANA time zone; SKILL.md always passes it")
    ap.add_argument("--out")
    args = ap.parse_args()
    tz = ZoneInfo(args.tz)
    convs = list(load(args.path))
    last = max(parse_ts(m["ts"]) for c in convs for m in c["messages"] if m["ts"])
    detect = lang_detector()
    result = {"data_until": last.isoformat(), "windows": {}}
    if args.since is not None:
        start = parse_ts(args.since) if args.since not in ("", "None", "null") else None
        sel = [c for c in convs if any(m["ts"] and (start is None or parse_ts(m["ts"]) >= start) for m in c["messages"])]
        result["windows"]["period"] = summarise(sel, tz, detect, start)
        args.days = []
    for d in (args.days + [None]) if args.days else []:
        start = last - timedelta(days=d) if d else None
        sel = [c for c in convs if any(m["ts"] and (start is None or parse_ts(m["ts"]) >= start)
                                       for m in c["messages"])]
        result["windows"][f"{d}d" if d else "all"] = summarise(sel, tz, detect, start)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(text)
    print(text)


if __name__ == "__main__":
    main()
