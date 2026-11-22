"""Render the Wrapped: a short tap-through story of the month, as one self-contained HTML page (no AI involved).

Usage:
    python3 -I render_wrapped.py --prepare prepare.json --stats stats.json --aggregate aggregate.json \
        --synthesis synthesis.json --facets facets_checked.jsonl --conversations selected.jsonl \
        [--patterns patterns.json] [--loops loops.json] [--zoom zoom.json] [--previous previous.json] \
        --out ai-usage-wrapped-YYYY-MM.html

Cards, in order, each skipped when it has nothing to show (the opener, the big numbers and the summary always show):
    opener     the period
    numbers    chats, active days (one dot per day), messages, long chats
    time       the top five shares of time per kind of work
    how        how the chats went (mode), with a fixed headline per dominant mode
    use_cases  the top three recurring patterns, and whether a skill covers them
    made       what was made: up to five kinds and their counts from zoom.json, never a work item name
    fix        one friction on the user's side and one on Claude's, with their counts
    next       the first skill to build (else a prompt template or preference), then the first loop
    since      only with previous.json: chats, active days and edited share, now and then
    summary    the card to share: figures and names only

Every number comes from the scripts' files, never from synthesis.json. The texts from synthesis.json (titles, fixes,
pattern names) are held to the same rules as the report and stricter, since a card travels further:
    - an item that cites any chat outside aggregate.json's quotable_chats is left off whole;
    - a text that contains a checked quote (facets_checked.jsonl, or any quote in synthesis.json) is left off;
    - a text that equals a chat title, or contains one of three words or more, is left off;
    - a friction title or fix with a digit in it is left off: its count comes from aggregate.json.
Numbers follow synthesis.json's "language" (numfmt.py), in the markup and in the count-up.
Everything left off is listed on stdout as LEFT OFF, so the synthesis can be fixed and the page rendered again.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I leaves the script's folder off the path
from aggregate import LONG_CHAT_TURNS  # noqa: E402
from loops import load_patterns  # noqa: E402
from numfmt import js_locale, lang_of, number, percent  # noqa: E402
from render_report import LEVEL_LABELS, MADE_LABELS, esc, norm  # noqa: E402

PURPLE, ORANGE, GREEN, PINK, BLUE = "#5B3DF5", "#FF6A4D", "#0E5E4E", "#FF78B9", "#2457E6"
RED, TEAL, BLACK, CREAM, LILAC = "#D7263D", "#14B8A6", "#121212", "#F5F3EE", "#A99BFF"
DARK, LIGHT = "#111111", "#FFFFFF"

CATEGORY_LABELS = {
    "strategy": "Strategy", "planning_admin": "Meetings and planning", "research": "Research",
    "writing": "Writing", "writing_editing": "Writing", "docs_presentations": "Decks and docs",
    "data_analysis": "Data and analysis", "summarise": "Summarising", "learning": "Learning", "ai_setup": "AI setup",
    "coding_automation": "Building and automation", "translation": "Translation", "unclear": "Unclear",
}
# mode -> (headline when it leads, legend label, end of "N% of your work chats ...")
MODES = {
    "task_iteration": ("Round by round", "Back and forth", "went back and forth until the answer was right."),
    "directive": ("Hand it over", "Handing it over", "handed the task over with little back and forth."),
    "learning": ("Learning by asking", "Learning how something works", "were about understanding how something works."),
    "validation": ("Checking your work", "Checking your own work", "checked your own work or a decision."),
    "feedback_loop": ("Passing results along", "Passing results along", "passed results from another tool along."),
    "single_question": ("Quick questions", "One question", "were a single question."),
}
HEADLINE_MODES = ("task_iteration", "directive", "learning", "validation", "feedback_loop")
# the dot grids: (columns, dot px, gap px); six rows fit between the label and the divider on card 2
MAX_DOT_ROWS = 6
DAY_GRID = (16, 10, 6)
MAX_MADE_ROWS = 5
# the report language; render() sets it once per page, so every number on every card follows it
LANG = "en"
LONG_GRID = (18, 8, 5)


# ---------------------------------------------------------------- small helpers

def fmt(n):
    return number(n, LANG)


def pct(value):
    return percent(value, LANG)


def fit(text, steps):
    """The font size for a text: steps are (most characters, px), the last one applies to anything longer."""
    for most, px in steps:
        if len(text) <= most:
            return px
    return steps[-1][1]


def capital(text):
    return text[:1].upper() + text[1:]


def span_text(start, end):
    a, b = date.fromisoformat(start), date.fromisoformat(end)
    if a.year == b.year:
        return f"{a.day} {a.strftime('%b')} to {b.day} {b.strftime('%b')} {b.year}"
    return f"{a.day} {a.strftime('%b')} {a.year} to {b.day} {b.strftime('%b')} {b.year}"


def counter(value, suffix=""):
    """A number that counts up when its card shows; the final value is in the markup for no-JS and reduced motion."""
    return f'<span data-count="{int(value)}" data-suffix="{esc(suffix)}">{fmt(int(value))}{esc(suffix)}</span>'


# ---------------------------------------------------------------- what may go on a card

class Guard:
    def __init__(self, quotable, quotes, titles, work_items=()):
        self.quotable = quotable
        self.quotes = {q for q in (norm(q) for q in quotes) if len(q.split()) >= 2}
        self.titles = {t for t in (norm(t) for t in titles) if t and t != "untitled chat"}
        # work item names stay in the report: a card text that names one is left off
        self.work_items = [re.compile(r"\b%s\b" % re.escape(w)) for w in (norm(w) for w in work_items) if w]
        self.left_off = []

    def chats_ok(self, chats, what):
        outside = sorted(set(chats) - self.quotable)
        if outside:
            self.left_off.append(f"{what} (cites a chat that isn't a work chat)")
        return not outside

    def text_ok(self, text, what, digits_allowed=True):
        n = norm(text)
        if any(q in n for q in self.quotes):
            self.left_off.append(f"{what} (contains a quote from the chats)")
            return False
        if any(n == t or (len(t.split()) >= 3 and t in n) for t in self.titles):
            self.left_off.append(f"{what} (contains a chat title)")
            return False
        if any(w.search(n) for w in self.work_items):
            self.left_off.append(f"{what} (names a work item; those stay in the report)")
            return False
        if not digits_allowed and re.search(r"\d", text):
            self.left_off.append(f"{what} (has a number in it; counts come from the aggregate)")
            return False
        return True


def quotes_in(data):
    """Every quote written anywhere in synthesis.json."""
    if isinstance(data, dict):
        return [v for k, v in data.items() if k == "quote" and isinstance(v, str)] + \
            [q for k, v in data.items() if k != "quote" for q in quotes_in(v)]
    if isinstance(data, list):
        return [q for v in data for q in quotes_in(v)]
    return []


def facet_quotes(row):
    found = [f.get("quote", "") for f in row.get("friction", [])]
    found += [i.get("text", "") for i in row.get("instructions", [])]
    found += [e.get("quote", "") for e in row.get("evidence", [])]
    found += [row.get("start_quote", ""), (row.get("recurrence") or {}).get("quote", "")]
    return [q for q in found if q]


def cited_chats(item):
    return [q["chat"] for q in quotes_of(item)] + list(item.get("chats") or []) + \
        [e["chat"] for e in item.get("evidence") or [] if isinstance(e, dict) and "chat" in e]


def quotes_of(item):
    return [q for key in ("quotes", "examples", "instructions") for q in item.get(key) or []
            if isinstance(q, dict) and "chat" in q]


# ---------------------------------------------------------------- the facts behind the cards

class Facts:
    def __init__(self, args):
        load = lambda p: json.load(open(p, encoding="utf-8"))
        self.prep = load(args.prepare)
        windows = load(args.stats)["windows"]
        self.st = windows.get("period") or windows["all"]
        self.agg = load(args.aggregate)
        self.syn = load(args.synthesis)
        self.loops = load(args.loops) if args.loops else None
        self.previous = load(args.previous) if args.previous else None
        self.zoom = load(args.zoom) if args.zoom else None
        self.lang = lang_of(self.syn)
        self.pattern_of = load_patterns(args.patterns)
        quotes = quotes_in(self.syn)
        for line in open(args.facets, encoding="utf-8"):
            if line.strip():
                quotes += facet_quotes(json.loads(line))
        titles = [json.loads(line).get("title") or "" for line in open(args.conversations, encoding="utf-8")
                  if line.strip()]
        self.guard = Guard(set(self.agg.get("quotable_chats", [])), quotes, titles,
                           [i["name"] for i in (self.zoom or {}).get("work_items", [])])
        # synthesis.md: a pattern recurs with 3+ chats in 2+ weeks, 4+ chats in the light tier
        self.need = 4 if self.prep.get("tier") == "light" else 3

        self.days = self.period_days()
        self.categories = self.category_rows()
        self.modes, self.mode_lead = self.mode_rows()
        self.use_cases, self.more_cases = self.recurring_patterns()
        self.friction_you, self.friction_claude = self.friction_items()
        self.next_item, self.loop = self.next_move()
        self.since = self.since_rows()

    # period and active days
    def period_days(self):
        active = set(self.st.get("active_dates", []))
        start = min([self.prep["from"], *active])
        end = max([self.prep["to"], *active])
        first, last = date.fromisoformat(start), date.fromisoformat(end)
        return [(first + timedelta(days=i)).isoformat() for i in range((last - first).days + 1)], active

    @property
    def n_days(self):
        return len(self.days[0])

    def is_month(self):
        return self.prep.get("period") == "30d" or (self.prep.get("period") == "custom" and self.n_days <= 31)

    def last_days(self):
        """The N of a "last N days" period ("90d" -> 90), else None. n_days counts both ends, so it is N + 1."""
        period = self.prep.get("period") or ""
        return int(period[:-1]) if re.fullmatch(r"\d+d", period) else None

    def opener_title(self):
        if self.is_month():
            return "Your month with AI"
        if self.prep.get("period") == "all":
            return "Your time with AI so far"
        return f"Your last {self.last_days()} days with AI" if self.last_days() else f"Your {self.n_days} days with AI"

    def started_line(self):
        if self.is_month():
            return "This month you started"
        if self.prep.get("period") == "all":
            return "In all, you started"
        return f"In these {self.last_days() or self.n_days} days you started"

    def dots(self):
        """(unit, [filled, ...]): a dot per day, or per week or month when the period is too long for the grid."""
        days, active = self.days
        if len(days) <= DAY_GRID[0] * MAX_DOT_ROWS:
            return "day", [d in active for d in days]
        weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
        if len(weeks) <= LONG_GRID[0] * MAX_DOT_ROWS:
            return "week", [any(d in active for d in w) for w in weeks]
        months = defaultdict(bool)
        for d in days:
            months[d[:7]] |= d in active
        return "month", [months[m] for m in sorted(months)][-LONG_GRID[0] * MAX_DOT_ROWS:]

    # where the time went
    def category_rows(self):
        merged = Counter()
        for key, value in self.agg.get("categories", {}).items():
            merged[CATEGORY_LABELS.get(key, "Other")] += value["share_of_time_pct"]
        return [(label, share) for label, share in merged.most_common() if share > 0][:5]

    # how you work
    def mode_rows(self):
        total = self.agg.get("work_chats_analysed", 0)
        if not total:
            return [], None
        merged = Counter()
        for key, n in self.agg.get("mode", {}).items():
            merged[key if key in MODES else "other"] += n
        rows = [(MODES[k][1] if k in MODES else "Other", 100 * n / total, k) for k, n in merged.most_common() if n][:5]
        leaders = [(merged[k], k) for k in HEADLINE_MODES if merged[k]]
        lead = max(leaders)[1] if leaders else ("single_question" if merged["single_question"] else None)
        return rows, (lead, round(100 * merged[lead] / total)) if lead else None

    # top use cases
    def recurring_patterns(self):
        pats = defaultdict(lambda: {"chats": set(), "weeks": set(), "labels": set()})
        for label, task in self.agg.get("tasks", {}).items():
            key = label.strip().lower()
            pat = pats[self.pattern_of.get(key, key)]
            pat["chats"] |= set(task["chats"]) & self.guard.quotable
            pat["weeks"] |= set(task["weeks"])
            pat["labels"].add(key)
        recurring = sorted(((name, p) for name, p in pats.items()
                            if len(p["chats"]) >= self.need and len(p["weeks"]) >= 2),
                           key=lambda kv: (-len(kv[1]["chats"]), kv[0]))
        covered = {norm(c.get("pattern", "")) for c in self.syn.get("reusable", {}).get("covered", [])}
        skill_chats = [set(s.get("chats") or []) for s in self.syn.get("reusable", {}).get("skills", [])]
        shown = []
        for name, p in recurring:
            if len(shown) == 3:
                break
            if not self.guard.text_ok(name, f"use case {name!r}"):
                continue
            if covered & ({norm(name)} | {norm(label) for label in p["labels"]}):
                status = "a skill covers it"
            elif any(chats & p["chats"] for chats in skill_chats):
                status = "skill suggested"
            else:
                status = "no skill yet"
            shown.append((capital(name), len(p["chats"]), status))
        return shown, len(recurring) - len(shown)

    # one fix
    def friction_items(self):
        found = {"you": None, "claude": None}
        for i, item in enumerate(self.syn.get("friction", [])):
            side = item.get("side")
            if side not in found or found[side] or not (item.get("title") or "").strip():
                continue
            what = f"friction {i + 1} ({item['title']!r})"
            if not self.guard.chats_ok(cited_chats(item), what):
                continue
            if not all(self.guard.text_ok(item.get(k) or "", what, digits_allowed=False) for k in ("title", "fix")):
                continue
            count = len(self.agg.get("friction", {}).get(item.get("type"), [])) or None
            found[side] = {"title": item["title"].strip(), "fix": (item.get("fix") or "").strip(), "count": count}
        return found["you"], found["claude"]

    # your next move
    def usable(self, item, what, text_keys):
        if not self.guard.chats_ok(cited_chats(item), what):
            return False
        return all(self.guard.text_ok(item.get(k) or "", what) for k in text_keys)

    def next_move(self):
        reusable = self.syn.get("reusable", {})
        main = None
        for s in reusable.get("skills", []):
            what = f"skill {s.get('title')!r}"
            if (s.get("title") or "").strip() and s.get("chats") and self.usable(s, what, ("title", "name")):
                main = {"kind": "skill", "title": s["title"].strip(), "name": (s.get("name") or "").strip(),
                        "chats": len(set(s["chats"])), "steps": len(s.get("seen_steps") or [])}
                break
        for kind, key in (("prompt", "prompts"), ("preference", "preferences")):
            if main:
                break
            for p in reusable.get(key, []):
                if (p.get("title") or "").strip() and self.usable(p, f"{kind} {p.get('title')!r}", ("title",)):
                    main = {"kind": kind, "title": p["title"].strip()}
                    break
        candidates = {c["id"] for c in (self.loops or {}).get("candidates", [])}
        loop = None
        for lp in (self.syn.get("loops") or {}).get("suggested", []):
            if lp.get("candidate") in candidates and (lp.get("title") or "").strip() \
                    and self.usable(lp, f"loop {lp.get('title')!r}", ("title",)):
                level = lp.get("start_level") if lp.get("start_level") in LEVEL_LABELS else "report_only"
                loop = {"title": lp["title"].strip(), "level": LEVEL_LABELS[level]}
                break
        return main, loop

    # since last time
    def since_rows(self):
        if not self.previous:
            return None
        was = self.previous["block"].get("figures", {})
        now = {"chats": self.st["conversations"], "active_days": self.st["active_days"],
               "edited_pct": round(self.st["rewound_convs_pct"])}
        rows = []
        for key, label, color in (("chats", "Chats", PINK), ("active_days", "Active days", TEAL),
                                  ("edited_pct", "Edited and retried", LILAC)):
            if not isinstance(was.get(key), (int, float)):
                continue
            a, b = now[key], was[key]
            if key == "chats":
                change = ("new", "") if not b else (signed(round(100 * (a - b) / b)) + "%", "")
                detail = f"{fmt(a)}, was {fmt(b)}"
            elif key == "active_days":
                change, detail = (signed(a - b), ""), f"{a}, was {b}"
            else:
                change, detail = (signed(a - b), " pts"), f"{a}%, was {b}%"
            rows.append((label, detail, change, color))
        return rows or None


def times(n):
    return "time" if n == 1 else "times"


def signed(n):
    return f"+{fmt(n)}" if n > 0 else ("0" if n == 0 else f"−{fmt(-n)}")


# ---------------------------------------------------------------- cards

def head(month):
    return (f'<div class="blk top"><span>AI Wrapped</span><span>{esc(month)}</span></div>')


def shape(left, top, size, color, ring=0):
    fill = f"border:{ring}px solid {color}" if ring else f"background:{color}"
    return (f'<i class="shape" style="left:{left}px;top:{top}px;width:{size}px;height:{size}px;{fill}" '
            f'aria-hidden="true"></i>')


def card_opener(f, n_cards):
    title = f.opener_title()
    return ("opener", PURPLE, "light", f"{title}, {span_text(f.prep['from'], f.prep['to'])}",
            shape(190, 64, 240, ORANGE) + shape(118, 150, 124, PINK) + shape(322, 560, 26, TEAL) +
            f'<div class="blk" style="left:32px;top:292px;width:341px;display:flex;flex-direction:column;gap:20px">'
            f'<h1 class="clamp4" style="font-size:{fit(title, [(20, 68), (40, 56)])}px;line-height:.95;'
            f'font-weight:800;letter-spacing:-.04em">{esc(title)}</h1>'
            f'<p style="font-size:18px;font-weight:500;color:#E4DEFF">{esc(span_text(f.prep["from"], f.prep["to"]))}</p></div>'
            f'<div class="blk foot" style="top:652px;font-size:14px;font-weight:600">'
            f'<span>{n_cards} cards, about a minute</span><span class="tapstart">Tap to start '
            f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"></path>'
            f'<path d="M13 6l6 6-6 6"></path></svg></span></div>')


def card_numbers(f):
    st = f.st
    chats = fmt(st["conversations"])
    unit, filled = f.dots()
    if unit != "day":
        cols, size, gap = LONG_GRID
    elif len(filled) <= 33:
        cols, size, gap = (10 if len(filled) <= 30 else 11), 18, 12
    else:
        cols, size, gap = DAY_GRID
    dots = "".join(f'<span class="dot{" on" if on else ""}" style="width:{size}px;height:{size}px"></span>'
                   for on in filled)
    per = "" if unit == "day" else (f'<span style="font-size:13px;font-weight:600;margin-top:-6px">'
                                    f'Each dot is a {unit}.</span>')
    return ("numbers", ORANGE, "dark", f"{chats} chats on {st['active_days']} of {f.n_days} days",
            shape(236, 118, 210, PURPLE) + shape(290, 632, 240, GREEN) +
            f'<div class="blk" style="left:32px;top:128px;width:341px;display:flex;flex-direction:column;gap:6px">'
            f'<span style="font-size:17px;font-weight:600">{esc(f.started_line())}</span>'
            f'<span data-fit="chats" class="big" style="font-size:{fit(chats, [(3, 172), (5, 120), (99, 92)])}px">'
            f'{counter(st["conversations"])}</span>'
            f'<span style="font-size:34px;line-height:1.1;font-weight:800;letter-spacing:-.02em">chats</span></div>'
            f'<div class="blk" style="left:32px;top:392px;width:341px;display:flex;flex-direction:column;gap:14px">'
            f'<span style="font-size:20px;font-weight:600">on {st["active_days"]} of {f.n_days} days</span>'
            f'<div class="dots" style="grid-template-columns:repeat({cols},{size}px);gap:{gap}px" aria-hidden="true">'
            f'{dots}</div>{per}</div>'
            f'<div class="blk pair" style="top:532px;border-top:2px solid {DARK}">'
            f'<div><span class="mid">{counter(st["user_messages"])}</span>'
            f'<span class="small">messages from you</span></div>'
            f'<div><span class="mid">{counter(f.agg.get("long_chats_over_55", 0))}</span>'
            f'<span class="small">long chats, over {LONG_CHAT_TURNS} of your messages</span></div></div>')


def card_time(f):
    if not f.categories:
        return None
    (top_label, top_share), rest = f.categories[0], f.categories[1:]
    rows = "".join(
        f'<div class="row"><div class="rowhead"><span class="ellip" style="font-weight:700">{esc(label)}</span>'
        f'<span style="font-weight:800">{pct(share)}</span></div>'
        f'<div class="track" aria-hidden="true"><div style="width:{max(2, round(341 * share / top_share))}px"></div>'
        f'</div></div>' for label, share in rest)
    top = round(top_share)
    return ("time", GREEN, "light", f"Most of your time went to {top_label}, {pct(top_share)}",
            f'<h2 class="blk" style="left:32px;top:104px;width:341px;font-size:40px;line-height:1.02;'
            f'font-weight:800;letter-spacing:-.035em">Where your time went</h2>'
            f'<i class="shape" style="left:258px;top:218px;width:116px;height:116px;'
            f'background:conic-gradient({PINK} 0 {top}%,rgba(255,255,255,.16) {top}% 100%)" aria-hidden="true"></i>'
            f'{shape(287, 247, 58, GREEN)}'
            f'<div class="blk" style="left:32px;top:226px;width:341px;display:flex;flex-direction:column;gap:4px">'
            f'<span class="big" style="font-size:{104 if top < 100 else 84}px;line-height:.88;margin-left:-4px">'
            f'{counter(top, "%") if top_share >= 1 else "&lt;1%"}</span>'
            f'<span class="clamp2" style="width:220px;font-size:{fit(top_label, [(12, 26), (99, 22)])}px;line-height:1.15;'
            f'font-weight:800;letter-spacing:-.02em">{esc(top_label)}</span>'
            f'<i style="display:block;width:341px;height:10px;border-radius:5px;margin-top:10px;background:{PINK}" '
            f'aria-hidden="true"></i></div>'
            f'<div class="blk" style="left:32px;top:414px;width:341px;display:flex;flex-direction:column;gap:18px">'
            f'{rows}</div>'
            f'<p class="blk" style="left:32px;top:652px;width:341px;font-size:12px;line-height:1.4;font-weight:600;'
            f'color:#CFE7DF">A share of your time in work chats, estimated from the gaps between your messages. '
            f'Not hours.</p>')


def card_how(f):
    if not f.mode_lead:
        return None
    lead, share = f.mode_lead
    headline, _, tail = MODES[lead]
    alphas = ["1", ".7", ".5", ".33", ".2"]
    bar = "".join(f'<div style="flex:{max(share_, 1):.1f};background:rgba(17,17,17,{a})"></div>'
                  for (_, share_, _), a in zip(f.modes, alphas))
    legend = "".join(
        f'<div class="leg"><i style="background:rgba(17,17,17,{a})" aria-hidden="true"></i>'
        f'<span class="ellip" style="flex:1;font-weight:{700 if k == lead else 600}">{esc(label)}</span>'
        f'<span style="font-weight:800">{pct(share_)}</span></div>'
        for (label, share_, k), a in zip(f.modes, alphas))
    return ("how", PINK, "dark", f"How you work: {headline}",
            shape(215, 530, 380, BLUE, 16) + shape(270, 585, 270, PURPLE, 16) + shape(325, 640, 160, DARK, 16) +
            f'<div class="blk" style="left:32px;top:104px;width:341px;display:flex;flex-direction:column;gap:14px">'
            f'<span style="font-size:17px;font-weight:600">How you work</span>'
            f'<h2 style="font-size:{fit(headline, [(14, 58), (18, 44), (99, 40)])}px;line-height:.95;font-weight:800;'
            f'letter-spacing:-.04em">{esc(headline)}</h2>'
            f'<p style="font-size:17px;line-height:1.4;font-weight:500">{share}% of your work chats {esc(tail)}</p>'
            f'<div class="stack" aria-hidden="true">{bar}</div>'
            f'<div style="display:flex;flex-direction:column;gap:9px;font-size:14px">{legend}</div>'
            f'<p style="font-size:12px;font-weight:600;width:300px">From how each chat went, not what it was about.</p>'
            f'</div>')


def card_use_cases(f):
    if not f.use_cases:
        return None
    colors = [ORANGE, PINK, TEAL]
    rows = "".join(
        f'<div class="case"><span class="num" style="background:{color}">{i + 1}</span>'
        f'<div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:6px">'
        f'<span data-fit="case" class="name clamp2" style="font-size:{fit(name, [(24, 23), (40, 20), (99, 17)])}px">'
        f'{esc(name)}</span><span style="font-size:15px;font-weight:600;color:#DCE5FF">'
        f'{fmt(chats)} chats · {status}</span></div></div>'
        for i, ((name, chats, status), color) in enumerate(zip(f.use_cases, colors)))
    more = (f'<span style="font-size:16px;font-weight:700">+ {f.more_cases} more in your report</span>'
            if f.more_cases else "")
    return ("use_cases", BLUE, "light", "Your top use cases",
            shape(300, 136, 64, TEAL) + shape(52, 646, 300, ORANGE) +
            f'<h2 class="blk" style="left:32px;top:104px;width:260px;font-size:40px;line-height:1.02;font-weight:800;'
            f'letter-spacing:-.035em">Your top use cases</h2>'
            f'<div class="blk" style="left:32px;top:236px;width:341px;display:flex;flex-direction:column;gap:22px">'
            f'<div class="cases">{rows}</div>'
            f'<div style="display:flex;flex-direction:column;gap:8px">{more}'
            f'<span style="font-size:12px;line-height:1.4;font-weight:600;color:#DCE5FF">A use case is the same kind '
            f'of job coming back in {f.need} or more chats, in at least two different weeks.</span></div></div>')


def card_made(f):
    """Kinds and counts only: a work item name never goes on a card."""
    by_kind = ((f.zoom or {}).get("made") or {}).get("by_kind") or {}
    rows = [(MADE_LABELS.get(kind, MADE_LABELS["other"]), v["count"]) for kind, v in by_kind.items()][:MAX_MADE_ROWS]
    if not rows:
        return None
    total = sum(v["count"] for v in by_kind.values())
    top = rows[0][1]
    lines = "".join(
        f'<div class="row"><div class="rowhead"><span class="ellip" style="font-weight:700">{esc(label)}</span>'
        f'<span style="font-weight:800">{fmt(count)}</span></div>'
        f'<div class="track" aria-hidden="true"><div style="width:{max(2, round(341 * count / top))}px"></div>'
        f'</div></div>' for label, count in rows)
    return ("made", ORANGE, "light", f"What you made: {fmt(total)} things",
            shape(300, -60, 180, PINK) +
            f'<div class="blk" style="left:32px;top:104px;width:341px;display:flex;flex-direction:column;gap:6px">'
            f'<h2 style="font-size:40px;line-height:1.02;font-weight:800;letter-spacing:-.035em">What you made</h2>'
            f'<span style="font-size:17px;font-weight:600"><span class="mid" style="display:inline">'
            f'{counter(total)}</span> things to take away</span></div>'
            f'<div class="blk" style="left:32px;top:262px;width:341px;display:flex;flex-direction:column;gap:18px">'
            f'{lines}</div>'
            f'<p class="blk" style="left:32px;top:640px;width:341px;font-size:12px;line-height:1.4;font-weight:600">'
            f'By kind of work, not by format. Which pieces of work they were for is in your report.</p>')


def card_fix(f):
    main = f.friction_you or f.friction_claude
    if not main:
        return None
    other = f.friction_claude if f.friction_you else None
    count = main["count"]
    dots = ""
    if count:
        shown = min(count, 12)
        size, gap = (34, 10) if shown <= 7 else (22, 6)
        dots = (f'<div style="display:flex;align-items:center;gap:{gap}px" aria-hidden="true">' +
                "".join(f'<i class="pip" style="width:{size}px;height:{size}px"></i>' for _ in range(shown)) +
                ("<b style='font-size:18px'>+</b>" if count > shown else "") + "</div>"
                f'<span style="font-size:17px;font-weight:700">{counter(count)} {times(count)} in your work chats</span>')
    fix = (f'<div style="display:flex;flex-direction:column;gap:14px;padding-top:22px;border-top:2px solid {LIGHT}">'
           f'<span class="label">The fix</span>'
           f'<p class="clamp4" style="font-size:{fit(main["fix"], [(90, 22), (999, 18)])}px;line-height:1.3;'
           f'font-weight:700">{esc(main["fix"])}</p>'
           f'<span class="chip">The full fix is in your report</span></div>') if main["fix"] else ""
    foot = ""
    if other:
        count_text = f", {fmt(other['count'])} {times(other['count'])}" if other["count"] else ""
        foot = (f'<p class="blk clamp3" style="left:32px;top:630px;width:236px;font-size:13px;line-height:1.45;'
                f'font-weight:500;color:#FFE1E5">On Claude\'s side: {esc(other["title"])}{count_text}. '
                f'That fix is in your report too.</p>')
    return ("fix", RED, "light", f"One thing that got in the way: {main['title']}",
            shape(285, 600, 240, BLUE) +
            f'<div class="blk" style="left:32px;top:104px;width:341px;display:flex;flex-direction:column;gap:18px">'
            f'<span style="font-size:17px;font-weight:600;color:#FFE1E5">One thing that got in the way</span>'
            f'<h2 class="clamp4" style="font-size:{fit(main["title"], [(30, 46), (60, 36), (999, 30)])}px;'
            f'line-height:1.02;font-weight:800;letter-spacing:-.035em">{esc(main["title"])}</h2>'
            f'{dots}{fix}</div>{foot}')


def card_next(f):
    main, loop = f.next_item, f.loop
    if not main and not loop:
        return None
    parts = ['<span style="font-size:17px;font-weight:600">Your next move</span>']
    if main:
        title = main["title"]
        parts.append(f'<h2 data-fit="skill" class="clamp3" style="font-size:{fit(title, [(16, 48), (28, 40), (999, 34)])}px;'
                     f'line-height:1;font-weight:800;letter-spacing:-.04em">{esc(title)}</h2>')
        if main["kind"] == "skill":
            name = f" · name: {main['name']}" if main["name"] else ""
            parts.append(f'<span class="ellip" style="font-size:14px;font-weight:600">A skill to build{esc(name)}</span>')
            circles = [(main["chats"], "chat where you did it by hand", "chats where you did it by hand"),
                       (main["steps"], "step that repeats every time", "steps that repeat every time")]
            parts.append('<div class="circles">' + "".join(
                f'<div><span class="circle" style="font-size:{fit(fmt(n), [(2, 44), (3, 32), (99, 22)])}px">'
                f'{counter(n)}</span><span style="font-size:14px;line-height:1.35;font-weight:600">'
                f'{esc(one if n == 1 else many)}</span></div>' for n, one, many in circles if n) + "</div>")
        else:
            parts.append(f'<span style="font-size:14px;font-weight:600">'
                         f'{"A prompt template to save" if main["kind"] == "prompt" else "A preference to set"}</span>')
    if loop:
        parts.append(f'<div class="try"><span class="label">{"Then try" if main else "Try"}</span>'
                     f'<span class="clamp2" style="font-size:{fit(loop["title"], [(30, 24), (999, 20)])}px;'
                     f'line-height:1.1;font-weight:800;letter-spacing:-.02em">{esc(loop["title"])}</span>'
                     f'<span style="font-size:14px;line-height:1.4;font-weight:500">A loop that runs on its own, '
                     f'starting with {esc(loop["level"])}.</span></div>')
    briefs = "Each comes with a build brief in your report." if main and main["kind"] == "skill" or not main \
        else "It's paste-ready in your report."
    summary = main["title"] if main else loop["title"]
    return ("next", TEAL, "dark", f"Your next move: {summary}",
            shape(330, 250, 150, ORANGE) +
            f'<div class="blk" style="left:32px;top:104px;width:341px;display:flex;flex-direction:column;gap:14px">'
            f'{"".join(parts)}</div>'
            f'<p class="blk" style="left:32px;top:662px;width:341px;font-size:13px;font-weight:600">{briefs}</p>')


def card_since(f):
    if not f.since:
        return None
    period = f.previous["block"]["period"]
    rows = "".join(
        f'<div class="cmp"><div style="display:flex;flex-direction:column;gap:4px;min-width:0">'
        f'<span style="font-size:17px;font-weight:700">{esc(label)}</span>'
        f'<span style="font-size:14px;font-weight:500;color:#A8A8A8">{esc(detail)}</span></div>'
        f'<span class="delta" style="color:{color}">{esc(change[0])}'
        f'{f"<small>{esc(change[1])}</small>" if change[1] else ""}</span></div>'
        for label, detail, change, color in f.since)
    start, end = date.fromisoformat(period["from"]), date.fromisoformat(period["to"])
    then = f"{start.day} {start.strftime('%b')} to {end.day} {end.strftime('%b')}"
    return ("since", BLACK, "light", "Since last time",
            shape(272, -92, 230, PURPLE) +
            f'<div class="blk" style="left:32px;top:104px;width:341px;display:flex;flex-direction:column;gap:10px">'
            f'<h2 style="font-size:44px;line-height:1;font-weight:800;letter-spacing:-.035em">Since last time</h2>'
            f'<span style="font-size:15px;font-weight:500;color:#A8A8A8">Compared with {esc(then)}</span></div>'
            f'<div class="blk" style="left:32px;top:222px;width:341px;display:flex;flex-direction:column">{rows}</div>'
            f'<p class="blk" style="left:32px;top:632px;width:341px;font-size:12px;line-height:1.45;font-weight:500;'
            f'color:#A8A8A8">Only figures the scripts count are compared here. The rest of the comparison is in '
            f'your report.</p>')


def tile(label, big, small, bg, dot, ink, fit_marker=""):
    marker = f' data-fit="{fit_marker}"' if fit_marker else ""
    return (f'<div class="tile" style="background:{bg};color:{ink}">'
            f'<i class="corner" style="background:{dot}" aria-hidden="true"></i>'
            f'<span class="label" style="position:relative">{esc(label)}</span>'
            f'<div style="position:relative;display:flex;flex-direction:column;gap:4px;min-width:0">{big}'
            f'<span style="font-size:13px;font-weight:600">{esc(small)}</span></div></div>')


def card_summary(f):
    st = f.st
    chats = fmt(st["conversations"])
    tiles = [tile("Chats", f'<span data-fit="tile" class="big" style="font-size:{fit(chats, [(3, 52), (5, 40), (99, 32)])}px;'
                           f'line-height:.9">{chats}</span>',
                  f"on {st['active_days']} of {f.n_days} days", PURPLE, ORANGE, LIGHT)]

    def word_tile(label, text, small, bg, dot, ink):
        size = fit(text, [(14, 26), (24, 21), (999, 18)])
        return tile(label, f'<span class="clamp2" style="font-size:{size}px;line-height:1.05;font-weight:800;'
                           f'letter-spacing:-.025em">{esc(text)}</span>', small, bg, dot, ink)

    if f.categories:
        label, share = f.categories[0]
        tiles.append(word_tile("Most time", label, f"{pct(share)} of my time", GREEN, PINK, LIGHT))
    if f.mode_lead:
        lead, share = f.mode_lead
        tiles.append(word_tile("How I work", MODES[lead][0], f"{share}% {MODES[lead][1].lower()}", PINK, BLUE, DARK))
    if f.next_item or f.loop:
        item = f.next_item or {"kind": "loop", **f.loop}
        small = {"skill": "a skill to build", "prompt": "a prompt to save", "preference": "a preference to set",
                 "loop": "a loop to try"}[item["kind"]]
        tiles.append(word_tile("Next up", item["title"], small, TEAL, PURPLE, DARK))
    cases = ""
    if f.use_cases:
        names = " · ".join(name for name, _, _ in f.use_cases)
        cases = (f'<div class="blk wide" style="top:568px"><i class="corner low" style="background:{ORANGE}" '
                 f'aria-hidden="true"></i><span class="label" style="position:relative">Top use cases</span>'
                 f'<span class="clamp2" style="position:relative;font-size:16px;line-height:1.25;font-weight:700">'
                 f'{esc(names)}</span></div>')
    return ("summary", CREAM, "dark", "My AI month, the card to share",
            f'<div class="blk" style="left:32px;top:92px;width:341px;display:flex;flex-direction:column;gap:6px">'
            f'<h2 style="font-size:44px;line-height:1;font-weight:800;letter-spacing:-.035em">'
            f'{"My AI month" if f.is_month() else "My time with AI"}</h2>'
            f'<span style="font-size:15px;font-weight:500;color:#4A4A4A">'
            f'{esc(span_text(f.prep["from"], f.prep["to"]))}</span></div>'
            f'<div class="blk tiles" style="top:196px">{"".join(tiles)}</div>{cases}'
            f'<div class="blk foot" style="top:672px;font-size:12px;font-weight:600">'
            f'<span>Made with AI usage insights</span></div>')


# ---------------------------------------------------------------- page

CSS = """
*{box-sizing:border-box;margin:0}
html,body{height:100%}
body{background:#5B3DF5;font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;
 display:flex;align-items:center;justify-content:center;overflow:hidden;transition:background .3s}
#deck{position:relative;width:405px;height:720px;flex:none;border-radius:24px;overflow:hidden;
 box-shadow:0 8px 24px rgba(0,0,0,.18);transform-origin:center;--ink:#FFFFFF;--dim:rgba(255,255,255,.3)}
#deck[data-ink=dark]{--ink:#111111;--dim:rgba(17,17,17,.22)}
.bar{position:absolute;left:20px;top:14px;width:365px;display:flex;gap:4px;z-index:3}
.seg{flex:1;height:3px;border-radius:2px;background:var(--dim)}
.seg.done{background:var(--ink)}
.card{position:absolute;inset:0;overflow:hidden;display:none}
.card.on{display:block;animation:in .35s ease-out}
@keyframes in{from{opacity:0;transform:translateX(12px)}to{opacity:1;transform:none}}
.blk{position:absolute}
.top{left:32px;top:36px;width:341px;display:flex;justify-content:space-between;font-size:12px;font-weight:700;
 letter-spacing:.12em;text-transform:uppercase}
.foot{left:32px;width:341px;display:flex;justify-content:space-between;align-items:center}
.tapstart{display:flex;align-items:center;gap:6px}
.shape{position:absolute;border-radius:50%;display:block}
.big{font-weight:900;line-height:.86;letter-spacing:-.065em;font-variant-numeric:tabular-nums;margin-left:-6px;
 white-space:nowrap}
.mid{display:block;font-size:38px;line-height:1;font-weight:800;letter-spacing:-.035em;font-variant-numeric:tabular-nums}
.small{display:block;font-size:13px;font-weight:600;margin-top:4px}
.pair{left:32px;width:341px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;padding-top:20px}
.dots{display:grid}
.dot{display:block;border-radius:50%;border:2px solid #111111}
.dot.on{background:#111111}
.row{display:flex;flex-direction:column;gap:7px}
.rowhead{display:flex;justify-content:space-between;gap:12px;font-size:17px;font-variant-numeric:tabular-nums}
.track{width:341px;height:6px;border-radius:3px;background:rgba(255,255,255,.18)}
.track div{height:6px;border-radius:3px;background:#FFFFFF}
.stack{display:flex;gap:3px;height:20px;border-radius:10px;overflow:hidden}
.leg{display:flex;align-items:center;gap:10px;font-variant-numeric:tabular-nums}
.leg i{width:12px;height:12px;border-radius:3px;flex:none}
.cases{display:flex;flex-direction:column;border-bottom:2px solid #FFFFFF}
.case{display:flex;align-items:center;gap:16px;padding:18px 0;border-top:2px solid #FFFFFF}
.num{width:56px;height:56px;flex:none;border-radius:50%;color:#111111;display:flex;align-items:center;
 justify-content:center;font-size:28px;font-weight:900}
.name{line-height:1.1;font-weight:800;letter-spacing:-.02em}
.pip{display:block;border-radius:50%;background:#FF78B9;flex:none}
.label{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}
.chip{align-self:flex-start;padding:8px 14px;border-radius:99px;background:#FFFFFF;color:#D7263D;font-size:13px;
 font-weight:700}
.circles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;width:290px}
.circles>div{display:flex;flex-direction:column;gap:10px}
.circle{width:84px;height:84px;border-radius:50%;background:#111111;color:#FFFFFF;display:flex;align-items:center;
 justify-content:center;font-weight:900;letter-spacing:-.04em;font-variant-numeric:tabular-nums}
.try{padding:20px;border-radius:20px;background:#5B3DF5;color:#FFFFFF;display:flex;flex-direction:column;gap:8px}
.cmp{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:18px 0;
 border-top:1px solid rgba(255,255,255,.22)}
.cmp:last-child{border-bottom:1px solid rgba(255,255,255,.22)}
.delta{font-size:50px;line-height:1;font-weight:900;letter-spacing:-.05em;font-variant-numeric:tabular-nums;
 white-space:nowrap}
.delta small{font-size:20px;letter-spacing:0;margin-left:4px}
.tiles{left:32px;width:341px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.tile,.wide{position:relative;overflow:hidden;border-radius:16px;padding:16px}
.tile{height:168px;display:flex;flex-direction:column;justify-content:space-between}
.wide{position:absolute;left:32px;width:341px;background:#2457E6;color:#FFFFFF;display:flex;flex-direction:column;gap:6px}
.corner{position:absolute;right:-22px;top:-22px;width:70px;height:70px;border-radius:50%}
.corner.low{top:auto;right:-18px;bottom:-30px;width:76px;height:76px}
.ellip{overflow:hidden;white-space:nowrap;text-overflow:ellipsis;min-width:0}
.clamp2,.clamp3,.clamp4{display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
.clamp2{-webkit-line-clamp:2}.clamp3{-webkit-line-clamp:3}.clamp4{-webkit-line-clamp:4}
.tap{position:absolute;top:0;bottom:0;z-index:2;border:0;padding:0;background:transparent;cursor:pointer}
.tap:focus-visible{outline:3px solid var(--ink);outline-offset:-6px}
.tap.prev{left:0;width:33%}.tap.next{right:0;width:67%}
.hint{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
html:not(.js) body{display:block;overflow:auto;padding:16px}
html:not(.js) #deck{height:auto;margin:0 auto;overflow:visible;box-shadow:none;background:none}
html:not(.js) .card{display:block;position:relative;height:720px;margin-bottom:16px;border-radius:24px}
html:not(.js) .bar,html:not(.js) .tap{display:none}
@media (max-width:500px){#deck{border-radius:0;box-shadow:none}.js #deck,.js .card{overflow:visible}}
@media (prefers-reduced-motion:reduce){body{transition:none}.card.on{animation:none}}
"""

JS = """
(function () {
  var cards = [].slice.call(document.querySelectorAll('section.card'));
  var segs = [].slice.call(document.querySelectorAll('.seg'));
  var deck = document.getElementById('deck');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var current = 0, startX = null;
  document.documentElement.classList.add('js');
  function scale() {
    var s = Math.min(window.innerWidth / 405, window.innerHeight / 720);
    deck.style.transform = 'scale(' + s + ')';
  }
  function countUp(card) {
    card.querySelectorAll('[data-count]').forEach(function (el) {
      var to = Number(el.getAttribute('data-count')), suffix = el.getAttribute('data-suffix') || '';
      var put = function (v) { el.textContent = v.toLocaleString(deck.getAttribute('data-locale')) + suffix; };
      if (reduce || !to) { put(to); return; }
      var t0 = null;
      function step(t) {
        if (t0 === null) t0 = t;
        var p = Math.min((t - t0) / 900, 1);
        put(Math.round(to * (1 - Math.pow(1 - p, 3))));
        if (p < 1) window.requestAnimationFrame(step);
      }
      put(0);
      window.requestAnimationFrame(step);
    });
  }
  function show(n) {
    current = Math.max(0, Math.min(cards.length - 1, n));
    cards.forEach(function (c, k) {
      c.classList.toggle('on', k === current);
      c.setAttribute('aria-hidden', k === current ? 'false' : 'true');
    });
    segs.forEach(function (s, k) { s.classList.toggle('done', k <= current); });
    deck.setAttribute('data-ink', cards[current].getAttribute('data-ink'));
    document.body.style.background = cards[current].getAttribute('data-bg');
    countUp(cards[current]);
  }
  document.querySelector('.tap.prev').addEventListener('click', function () { show(current - 1); });
  document.querySelector('.tap.next').addEventListener('click', function () { show(current + 1); });
  document.addEventListener('keydown', function (e) {
    // Space and Enter on a focused tap button press that button; handling them here too would move twice
    if (e.target.tagName === 'BUTTON' && (e.key === ' ' || e.key === 'Enter')) return;
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); show(current + 1); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(current - 1); }
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(cards.length - 1);
  });
  deck.addEventListener('touchstart', function (e) { startX = e.changedTouches[0].clientX; }, {passive: true});
  deck.addEventListener('touchend', function (e) {
    if (startX === null) return;
    var dx = e.changedTouches[0].clientX - startX;
    startX = null;
    if (Math.abs(dx) > 40) { e.preventDefault(); show(current + (dx < 0 ? 1 : -1)); }
  });
  window.addEventListener('resize', scale);
  scale();
  show(0);
})();
"""


def render(f):
    global LANG
    LANG = f.lang
    builders = [card_numbers, card_time, card_how, card_use_cases, card_made, card_fix, card_next, card_since,
                card_summary]
    middle = [card for card in (b(f) for b in builders) if card]
    cards = [card_opener(f, len(middle) + 1)] + middle
    month = date.fromisoformat(f.prep["to"]).strftime("%b %Y")
    sections = "".join(
        f'<section class="card" data-card="{name}" data-bg="{bg}" data-ink="{ink}" role="group" '
        f'aria-roledescription="card" aria-label="{i + 1} of {len(cards)}: {esc(label)}" '
        f'style="background:{bg};color:{DARK if ink == "dark" else LIGHT}">{head(month)}{body}</section>'
        for i, (name, bg, ink, label, body) in enumerate(cards))
    bar = "".join('<i class="seg"></i>' for _ in cards)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<title>AI Wrapped, {esc(month)}</title><style>{CSS}</style></head><body>'
            f'<main id="deck" data-ink="light" data-locale="{js_locale(f.lang)}" aria-live="polite">'
            f'<div class="bar" aria-hidden="true">{bar}</div>{sections}'
            f'<button class="tap prev" type="button" aria-label="Previous card"></button>'
            f'<button class="tap next" type="button" aria-label="Next card"></button>'
            f'<p class="hint">Use the arrow keys, tap, or swipe to move between cards.</p></main>'
            f'<script>{JS}</script></body></html>')


def main():
    ap = argparse.ArgumentParser()
    for k in ("prepare", "stats", "aggregate", "synthesis", "facets", "conversations", "out"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--patterns")
    ap.add_argument("--loops")
    ap.add_argument("--zoom", help="zoom.json from zoom.py")
    ap.add_argument("--previous", help="previous.json from state_block.py find, when it found last run's block")
    args = ap.parse_args()
    facts = Facts(args)
    page = render(facts)
    open(args.out, "w", encoding="utf-8").write(page)
    print(f"wrote {args.out} ({len(page) // 1024} KB, {page.count('<section class=')} cards)")
    for note in dict.fromkeys(facts.guard.left_off):
        print("LEFT OFF:", note)


if __name__ == "__main__":
    main()
