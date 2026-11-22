"""Zoom out: the pieces of work the period went to, and what was made (no AI involved).

Usage:
    python3 -I zoom.py selected.jsonl facets_checked.jsonl --aggregate aggregate.json [--patterns patterns.json] \
        [--prepare prepare.json] [--items items.json] [--older older.jsonl --older-labels older_labels.jsonl] --tz <IANA time zone> \
        --out zoom.json

Reads only the chats aggregate.json may quote (work chats that are no test run and no insights run); the
work_item and made fields of every other facet are ignored, so nothing from a personal or mixed chat gets in.
items.json merges work item phrases that mean the same piece of work ({"kept phrase": ["other phrase", ...]}),
as patterns.json merges task labels.

    work_items      per work item: chats, share of time (aggregate.py's estimate), first and last day and the span
                    in days, restarts (starts_from_earlier_chats), relays (started from another tool's output, or
                    handed to another tool), context explained again, the tools touched, and what was made per kind.
                    "one-off" chats are counted apart. Older chats with a work item only widen its span, by date.
    flows           work chats with FLOW_STEPS or more steps
    repeated_kinds  a kind made REPEAT or more times with the same shape (kind, for whom, what for)
    use_cases       the recurring patterns (3+ chats in 2+ weeks, 4+ in the light tier), with how many work items
                    each one served
    made            counts per kind, for whom and what for; the forms the tool calls made; and revision rounds:
                    versions per distinct deliverable, per kind, from chats that made one kind only (a chat that
                    made two kinds can't say which kind a file belonged to)

Every id in this file ("item:<name>", "flow:<chat>", "kind:<kind>|<for>|<purpose>", "case:<pattern>") is what
synthesis.json's zoomed_out routes point at; render_report.py drops a route whose id isn't here.
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves the script's folder off the path
from aggregate import user_minutes  # noqa: E402
from loops import load_patterns  # noqa: E402
from stats import feature_of  # noqa: E402

FLOW_STEPS = 4
REPEAT = 3
ONE_OFF = "one-off"
KINDS = ("message", "meeting_material", "document", "plan_or_strategy", "proposal_or_case", "research_or_analysis",
         "data_or_model", "design_or_visual", "product_spec", "code_or_automation", "prompt_for_ai",
         "learning_material", "status_update", "template_or_checklist", "edit_or_translation", "other")
FOR = ("self", "manager", "team_or_colleagues", "client_or_partner", "external_other", "another_ai")
PURPOSES = ("decide", "inform", "request", "plan", "build", "reference")
# handoffs that stay inside claude.ai are not a relay to another tool
NOT_A_TOOL = {"new chat or project", "earlier chats"}

# What makes a deliverable, by tool name. Names vary per surface (mcp__ prefixes), so a server is matched on its
# prefixes and the tool on the rest of the name, as stats.py FEATURES does. Only the writers named here count; a
# tool stats.py knows for something else (a search, memory, a task list, a comment) never does.
DOCS = ("Claude Docs:", "mcp__Claude_Docs__", "mcp__claude_ai_Claude_Docs__")
NOTION = ("Notion:", "mcp__Notion__", "mcp__claude_ai_Notion__")
VISUALS = ("visualize:", "mcp__visualize__")
FILE_TOOLS = {"create_file", "str_replace", "Write", "Edit", "MultiEdit"}
EXTENSIONS = {".docx": "Word document", ".doc": "Word document", ".pptx": "slide deck", ".xlsx": "spreadsheet",
              ".csv": "spreadsheet", ".pdf": "PDF", ".md": "Markdown file", ".html": "web page",
              ".skill": "skill file", ".py": "code file", ".js": "code file", ".ts": "code file",
              ".sh": "code file", ".json": "data file", ".svg": "image", ".png": "image"}
# an unknown tool counts, as form "other", only when its call says it writes; it is new when it says it creates
WRITES = {"create", "update", "publish", "edit", "write", "rewrite", "append", "replace"}
CREATES = {"create", "publish", "write"}


def tool_after(name, prefixes):
    return next((name[len(p):] for p in prefixes if name.startswith(p)), None)


def writer_of(call):
    """(form, creates) for a call that writes a version of something, or None. "file" takes its form per path."""
    name, action = call.get("tool") or "", call.get("action") or ""
    if name == "Artifact":
        if action in ("", "publish", "edit"):
            return "Artifact page", action != "edit" and not call.get("key")
        return None
    if name == "artifacts":
        return ("Artifact page", action == "create") if action in ("create", "update", "rewrite") else None
    docs = tool_after(name, DOCS)
    if docs is not None:
        if docs == "batch":
            return "Claude Docs doc", action == "create"
        return ("Claude Docs doc", docs == "create") if docs in ("update", "create") else None
    notion = tool_after(name, NOTION)
    if notion is not None:
        if notion in ("notion-create-pages", "notion-duplicate-page"):
            return "Notion page", True
        return ("Notion page", False) if notion == "notion-update-page" else None
    if name in FILE_TOOLS:
        return "file", False
    if name.startswith("message_compose"):
        return ("drafted email" if action == "email" else "drafted message"), True
    if tool_after(name, VISUALS) == "show_widget":
        return "visual", True
    if name == "launch_extended_search_task":
        return "research report", True
    if feature_of(name) == "other" and action in WRITES:
        return "other", action in CREATES
    return None


def deliverables(calls):
    """{form: (deliverables, versions)} for one chat.

    Every writing call is one version. A deliverable is counted conservatively, since a first publish carries only a
    path and its later edits only a url: per form, the most of the distinct ids, the distinct paths, and the creating
    calls that carry neither. A file a chat presents (present_files) is a deliverable of the form its extension says,
    and one version when no call in the chat wrote it (a script made it)."""
    by_form = defaultdict(lambda: {"versions": 0, "keys": set(), "paths": set(), "bare": 0})
    for call in calls:
        paths = list(zip(call.get("paths") or [], call.get("exts") or []))
        if call.get("tool") == "present_files":
            for path, ext in paths:
                by_form[EXTENSIONS.get(ext, "file")]["paths"].add(path)
            continue
        found = writer_of(call)
        if found is None:
            continue
        form, creates = found
        if form == "file":
            for path, ext in paths[:1]:
                slot = by_form[EXTENSIONS.get(ext, "file")]
                slot["versions"] += 1
                slot["paths"].add(path)
            continue
        slot = by_form[form]
        slot["versions"] += 1
        if call.get("key"):
            slot["keys"].add(call["key"])
        slot["paths"].update(path for path, _ in paths)
        if creates and not call.get("key") and not paths:
            slot["bare"] += 1
    result = {}
    for form, slot in by_form.items():
        made = max(len(slot["keys"]), len(slot["paths"]), slot["bare"]) or 1
        result[form] = (made, max(slot["versions"], made))
    return result


def clean_made(row):
    found = []
    for item in (row.get("made") or [])[:3]:
        if not isinstance(item, dict):
            continue
        found.append({"kind": item.get("kind") if item.get("kind") in KINDS else "other",
                      "for": item.get("for") if item.get("for") in FOR else "other",
                      "purpose": item.get("purpose") if item.get("purpose") in PURPOSES else "other"})
    return found


def load_items(path):
    """items.json -> {phrase: kept phrase}. Case is kept for display; matching ignores it."""
    if not path:
        return {}
    mapping = {}
    for kept, phrases in json.load(open(path, encoding="utf-8")).items():
        for phrase in [kept, *phrases]:
            mapping[" ".join(phrase.split()).lower()] = " ".join(kept.split())
    return mapping


def local_day(iso, tz):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz).date().isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conversations")
    ap.add_argument("facets")
    ap.add_argument("--aggregate", required=True)
    ap.add_argument("--patterns")
    ap.add_argument("--prepare", help="prepare.json: in the light tier a use case needs 4 chats")
    ap.add_argument("--items")
    ap.add_argument("--older")
    ap.add_argument("--older-labels")
    ap.add_argument("--tz", default="UTC")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    tz = ZoneInfo(args.tz)
    agg = json.load(open(args.aggregate, encoding="utf-8"))
    quotable = set(agg.get("quotable_chats", []))
    convs = {}
    for line in open(args.conversations, encoding="utf-8"):
        c = json.loads(line)
        if c["id"][:8] in quotable:
            convs[c["id"][:8]] = c
    rows = [json.loads(l) for l in open(args.facets, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r.get("id") in convs]
    item_of = load_items(args.items)
    # phrases that differ only in case are one work item, shown as items.json keeps it, else as first written
    for row in rows:
        phrase = " ".join((row.get("work_item") or "").split())
        item_of.setdefault(phrase.lower(), phrase)
    name_of = lambda phrase: item_of.get(" ".join(phrase.split()).lower(), " ".join(phrase.split()))

    minutes = {r["id"]: user_minutes(convs[r["id"]]) for r in rows}
    total = sum(minutes.values()) or 1
    items = defaultdict(lambda: {"chats": 0, "minutes": 0.0, "days": set(), "restarts": 0, "relays": 0,
                                 "context_again": 0, "tools": set(), "made": Counter()})
    one_off = {"chats": 0, "minutes": 0.0}
    flows, shapes = [], defaultdict(lambda: {"count": 0, "items": set()})
    by_kind = defaultdict(lambda: {"count": 0, "for": Counter(), "purpose": Counter()})
    forms, revisions, base_chats = Counter(), defaultdict(lambda: [0, 0, 0]), 0
    for row in rows:
        conv, made = convs[row["id"]], clean_made(row)
        phrase = (row.get("work_item") or "").strip()
        name = name_of(phrase) if phrase else ""
        tools = {h.strip() for h in row.get("handoffs") or []
                 if isinstance(h, str) and h.strip() and h.strip() not in NOT_A_TOOL}
        if name and name.lower() != ONE_OFF:
            it = items[name]
            it["chats"] += 1
            it["minutes"] += minutes[row["id"]]
            it["days"] |= {local_day(m["ts"], tz) for m in conv["messages"] if m.get("ts")}
            it["restarts"] += bool(row.get("starts_from_earlier_chats"))
            it["relays"] += bool(tools) or row.get("trigger") == "tool_output"
            it["context_again"] += bool(row.get("context_resupplied"))
            it["tools"] |= tools
            it["made"].update(m["kind"] for m in made)
        elif name:
            one_off["chats"] += 1
            one_off["minutes"] += minutes[row["id"]]
        steps = [s for s in row.get("steps") or [] if isinstance(s, str) and s.strip()]
        if len(steps) >= FLOW_STEPS:
            flows.append({"id": f"flow:{row['id']}", "chat": row["id"], "work_item": name, "task": row.get("task", ""),
                          "steps": steps})
        for m in made:
            shape = shapes["|".join((m["kind"], m["for"], m["purpose"]))]
            shape["count"] += 1
            if name:
                shape["items"].add(name)
            by_kind[m["kind"]]["count"] += 1
            by_kind[m["kind"]]["for"][m["for"]] += 1
            by_kind[m["kind"]]["purpose"][m["purpose"]] += 1
        made_here = deliverables([c for msg in conv["messages"] for c in msg.get("calls") or []]) if made else {}
        for form, (n, _) in made_here.items():
            forms[form] += n
        kinds = {m["kind"] for m in made}
        if len(kinds) == 1 and made_here:
            base_chats += 1
            rev = revisions[kinds.pop()]
            rev[0] += 1
            rev[1] += sum(n for n, _ in made_here.values())
            rev[2] += sum(v for _, v in made_here.values())

    # older chats: their dates widen a work item's span, nothing else
    if args.older and args.older_labels:
        dates = {}
        for line in open(args.older, encoding="utf-8"):
            if line.strip():
                o = json.loads(line)
                dates[o["id"]] = o.get("date")
        for line in open(args.older_labels, encoding="utf-8"):
            if not line.strip():
                continue
            o = json.loads(line)
            phrase = (o.get("work_item") or "").strip()
            if o.get("scope") == "work" and phrase and dates.get(o.get("id")) and name_of(phrase) in items:
                items[name_of(phrase)]["days"].add(local_day(dates[o["id"]], tz))

    work_items = []
    for name, it in items.items():
        first, last = min(it["days"]), max(it["days"])
        work_items.append({
            "id": f"item:{name}", "name": name, "chats": it["chats"],
            "share_of_time_pct": round(100 * it["minutes"] / total, 1),
            "first": first, "last": last,
            "span_days": (date.fromisoformat(last) - date.fromisoformat(first)).days + 1,
            "restarts": it["restarts"], "relays": it["relays"], "context_again": it["context_again"],
            "tools": sorted(it["tools"]), "made": dict(it["made"].most_common()),
        })
    work_items.sort(key=lambda i: (-i["share_of_time_pct"], -i["chats"], i["name"]))

    # use cases: recurring patterns, as synthesis.md section 1 defines them, with the work items they served
    pattern_of = load_patterns(args.patterns)
    tier = json.load(open(args.prepare, encoding="utf-8")).get("tier") if args.prepare else None
    need = REPEAT + 1 if tier == "light" else REPEAT
    item_by_chat = {r["id"]: name_of(r["work_item"]) for r in rows
                    if (r.get("work_item") or "").strip() and name_of(r["work_item"]).lower() != ONE_OFF}
    cases = defaultdict(lambda: {"chats": set(), "weeks": set()})
    for label, task in agg.get("tasks", {}).items():
        key = label.strip().lower()
        case = cases[pattern_of.get(key, key)]
        case["chats"] |= set(task["chats"]) & quotable
        case["weeks"] |= set(task["weeks"])
    use_cases = sorted(({"id": f"case:{p}", "pattern": p, "chats": len(c["chats"]),
                         "work_items": len({item_by_chat[x] for x in c["chats"] if x in item_by_chat})}
                        for p, c in cases.items() if len(c["chats"]) >= need and len(c["weeks"]) >= 2),
                       key=lambda c: (-c["chats"], c["pattern"]))

    result = {
        "work_items": work_items,
        "one_off_chats": one_off["chats"],
        "one_off_share_pct": round(100 * one_off["minutes"] / total, 1),
        "flows": flows,
        "repeated_kinds": sorted(({"id": f"kind:{k}", "kind": k.split("|")[0], "for": k.split("|")[1],
                                   "purpose": k.split("|")[2], "count": s["count"], "work_items": len(s["items"])}
                                  for k, s in shapes.items() if s["count"] >= REPEAT),
                                 key=lambda k: (-k["count"], k["id"])),
        "use_cases": use_cases,
        "made": {
            "chats_with_made": sum(1 for r in rows if clean_made(r)),
            "by_kind": {k: {"count": v["count"], "for": dict(v["for"].most_common()),
                            "purpose": dict(v["purpose"].most_common())}
                        for k, v in sorted(by_kind.items(), key=lambda kv: (-kv[1]["count"], kv[0]))},
            "forms": dict(forms.most_common()),
            "revisions": {k: {"chats": c, "deliverables": d, "versions": v, "per_deliverable": round(v / d, 1)}
                          for k, (c, d, v) in sorted(revisions.items()) if d},
            "revision_base_chats": base_chats,
        },
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    print(f"{len(work_items)} work items, {len(flows)} flows, {result['made']['chats_with_made']} chats made "
          f"something; wrote {args.out}")


if __name__ == "__main__":
    main()
