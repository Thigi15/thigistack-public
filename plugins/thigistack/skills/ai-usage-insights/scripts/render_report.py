"""Render the insights report as one self-contained HTML page (no AI involved).

Usage:
    python3 -I render_report.py --conversations conversations.jsonl --stats stats.json \
        --aggregate aggregate.json --synthesis synthesis.json [--loops loops.json] [--previous previous.json] \
        --out report.html

stats.json, aggregate.json and loops.json come from the scripts; synthesis.json is the
written part (texts, recommendations, skill seeds, loop cards). Every quote in
synthesis.json is checked against the user's own messages again here, and any
quote that can't be found is dropped and reported. Quotes and chat links are only
shown for work chats (aggregate.json's quotable_chats); any other chat is refused,
even when the quote is real. A loop card is only shown when loops.json has its
candidate (3+ occurrences), at most 3, and always starting report-only or as drafts.
"""
import argparse
import html
import json
import re
from datetime import date

# ---------------------------------------------------------------- helpers

def norm(s):
    s = (s or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def nice_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b')} {d.year}"


def esc(s):
    return html.escape(str(s), quote=True)


CATEGORY_LABELS = {
    "strategy": "Strategy & proposition work",
    "coding_automation": "Building & automation",
    "planning_admin": "Meeting prep & planning",
    "ai_setup": "AI setup, skills & prompts",
    "learning": "Learning & explanations",
    "research": "Research & checks",
    "writing": "Writing & email",
    "writing_editing": "Writing & email",
    "summarise": "Summarising sources",
    "docs_presentations": "Decks & documents",
    "data_analysis": "Data & analysis",
}
FEATURE_SKIP = {"other", "internal"}
WALKTHROUGH = [
    "What is it for, and when should it trigger and not trigger? Start from the draft triggers above.",
    "What input does it need from me each time?",
    "What are the steps, and where is judgement needed? Start from the steps above.",
    "What should the output look like: template, length, language, tone?",
    "Which rules and checks keep coming up? Start from the repeated instructions above.",
    "Which files should it carry: templates, examples, reference material?",
    "Where will I use it: only Claude, or also ChatGPT or Copilot? Keep the core instructions tool-neutral and put anything platform-specific in a short 'Platform notes' section.",
    "Personal or shareable? If shareable, leave out names, customers and internal details so it can go into a shared skills library.",
    "Test: run the draft on the example requests below and compare the result with what I actually needed.",
]
MAX_LOOPS = 3
KIND_LABELS = {"time": "Time-based", "event": "Event-based", "watch": "Watch", "check": "Check"}
LEVEL_LABELS = {"report_only": "report only", "draft_only": "drafts only"}
TRIGGER_LABELS = {
    "own_idea": "your own idea", "incoming_message": "a message someone sent", "meeting": "a meeting",
    "new_document_or_data": "a new document or data", "tool_output": "another tool's output",
    "schedule": "a fixed moment in the week or month", "outside_change": "news or a change outside",
    "continuation": "earlier work", "unclear": "something unclear",
}
RUNS_IN = {
    "claude_scheduled_task": "A scheduled task in Claude: runs in the cloud on a schedule, with your connectors and skills",
    "claude_code_routine": "A scheduled task in Claude Code, in the cloud or on your computer",
    "claude_code_hook": "A Claude Code hook: runs when something happens in a Claude Code session",
    "chatgpt_task": "A ChatGPT scheduled task",
    "copilot_scheduled_prompt": "A scheduled prompt in Microsoft 365 Copilot",
    "power_automate": "A Power Automate flow: starts on an email, a file or a Teams event",
    "own_agent": "An agent you already run yourself",
    "manual_prompt": "Not automated yet: you start it yourself with a saved prompt",
}
LOOP_WALKTHROUGH = [
    "Trigger: what exactly starts a run? A time (which days, which hour) or an event (what happens, and how will "
    "the loop notice it)? If this platform can't react to the event, can a scheduled check stand in, for example "
    "every weekday at 08:00?",
    "Input: where does each run read from, and does it have access (a connector, a folder, a link)? What should it "
    "do when the input is missing or empty?",
    "Steps and skill: which steps, in which order, and which skill does it run? If that skill doesn't exist yet, "
    "build it first.",
    "The check, before anything else: how does a run test its own result before I see it? Think of sources present, "
    "numbers traced to the input, house style, length, nothing left out. Can a separate review step do this, "
    "rather than the step that wrote it?",
    "Done and stop: what counts as a finished run, and when should it stop and tell me instead of trying again? "
    "One retry at most.",
    "Output and where I step in: where does the result land (a chat, a draft, a document), and what do I approve "
    "before anything leaves?",
    "Starting level: it starts report-only or as drafts. What has to go right, and for how many runs, before it may "
    "do more? What may it never do on its own (send, delete, buy, publish)?",
    "Noise and cost: how often is often enough? On a run with nothing new, should it stay quiet or say so?",
    "Where it runs: start from the options above, and check what my plan and organisation allow (admins can turn "
    "scheduled tasks off).",
    "Test: do one run by hand now, compare it with what I would have done, then schedule it. After the first few "
    "runs, look at the results with me and adjust.",
]


class Report:
    def __init__(self, args):
        windows = json.load(open(args.stats, encoding="utf-8"))["windows"]
        self.stats = windows.get("period") or windows["all"]
        self.agg = json.load(open(args.aggregate, encoding="utf-8"))
        self.syn = json.load(open(args.synthesis, encoding="utf-8"))
        self.loops = json.load(open(args.loops, encoding="utf-8")) if getattr(args, "loops", None) else None
        self.previous = json.load(open(args.previous, encoding="utf-8")) if getattr(args, "previous", None) else None
        # only work chats may be quoted or linked; older aggregates list them as titles
        self.quotable = set(self.agg.get("quotable_chats", self.agg.get("titles", {})))
        self.full_id, self.user_text, self.title = {}, {}, {}
        for line in open(args.conversations, encoding="utf-8"):
            c = json.loads(line)
            self.full_id[c["id"][:8]] = c["id"]
            self.title[c["id"][:8]] = c["title"] or "Untitled chat"
            self.user_text[c["id"][:8]] = norm(" \n ".join(m["text"] for m in c["messages"] if m["role"] == "user"))
        self.dropped, self.refused, self.loop_notes = [], [], []

    def chat_ok(self, chat, what="link"):
        if chat in self.quotable:
            return True
        self.refused.append((chat, what))
        return False

    # quotes are only shown if the user really wrote them, in a work chat
    def ok(self, chat, quote):
        if not self.chat_ok(chat, quote):
            return False
        if norm(quote) in self.user_text.get(chat, ""):
            return True
        self.dropped.append((chat, quote))
        return False

    def work_chats(self, chats):
        return [c for c in chats if self.chat_ok(c)]

    def link(self, chat):
        return f"https://claude.ai/chat/{self.full_id.get(chat, chat)}"

    def quote(self, q):
        if not self.ok(q["chat"], q["quote"]):
            return ""
        return (f'<blockquote><a href="{esc(self.link(q["chat"]))}" target="_blank" rel="noopener">'
                f'&ldquo;{esc(q["quote"])}&rdquo;</a></blockquote>')

    # ------------------------------------------------------------ charts

    def hbar(self, rows, unit, chart_id):
        """Single-series horizontal bars: rows = [(label, value)]."""
        if not rows:
            return ""
        vmax = max(v for _, v in rows) or 1
        lw, bw, bh, gap = 210, 380, 16, 10
        h = len(rows) * (bh + gap)
        parts = [f'<svg class="chart" viewBox="0 0 {lw + bw + 60} {h}" role="img" aria-labelledby="{chart_id}-t">']
        for i, (label, v) in enumerate(rows):
            y = i * (bh + gap)
            w = max(2.0, bw * v / vmax)
            r = min(4, w / 2)
            path = (f"M{lw},{y} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{bh - 2 * r} "
                    f"a{r},{r} 0 0 1 {-r},{r} h{-(w - r):.1f} z")
            tip = f"{label}: {v:g}{unit}"
            parts.append(f'<text class="lab" x="{lw - 10}" y="{y + bh - 4}" text-anchor="end">{esc(label)}</text>')
            parts.append(f'<rect class="hit" x="0" y="{y - 3}" width="{lw + bw + 60}" height="{bh + 6}" data-tip="{esc(tip)}"/>')
            parts.append(f'<path class="bar" d="{path}" data-tip="{esc(tip)}"/>')
            shown = f"<1{unit}" if 0 < v < 1 else f"{v:g}{unit}"
            parts.append(f'<text class="val" x="{lw + w + 6:.1f}" y="{y + bh - 4}">{esc(shown)}</text>')
        parts.append("</svg>")
        table = "".join(f"<tr><td>{esc(l)}</td><td>{v:g}{unit}</td></tr>" for l, v in rows)
        return ("".join(parts) + f'<details class="tv"><summary>Show as table</summary>'
                f"<table><tbody>{table}</tbody></table></details>")

    def columns(self, values, labels, unit, chart_id):
        """Single-series columns, e.g. messages per hour of day."""
        vmax = max(values or [0]) or 1
        cw, gap, ch, top = 20, 4, 140, 8
        w = len(values) * (cw + gap)
        parts = [f'<svg class="chart" viewBox="0 0 {w + 40} {ch + top + 24}" role="img" aria-labelledby="{chart_id}-t">']
        for frac in (0.5, 1.0):
            gy = top + ch - ch * frac
            parts.append(f'<line class="grid" x1="0" x2="{w}" y1="{gy}" y2="{gy}"/>')
            parts.append(f'<text class="axis" x="{w + 6}" y="{gy + 4}">{round(vmax * frac)}</text>')
        parts.append(f'<line class="base" x1="0" x2="{w}" y1="{top + ch}" y2="{top + ch}"/>')
        for i, v in enumerate(values):
            x = i * (cw + gap)
            hgt = ch * v / vmax
            tip = f"{labels[i]}: {v}{unit}"
            if hgt > 0:
                r = min(4, hgt / 2, cw / 2)
                y = top + ch - hgt
                path = (f"M{x},{top + ch} v{-(hgt - r):.1f} a{r},{r} 0 0 1 {r},{-r} h{cw - 2 * r} "
                        f"a{r},{r} 0 0 1 {r},{r} v{hgt - r:.1f} z")
                parts.append(f'<path class="bar" d="{path}" data-tip="{esc(tip)}"/>')
            parts.append(f'<rect class="hit" x="{x - gap / 2}" y="{top}" width="{cw + gap}" height="{ch}" data-tip="{esc(tip)}"/>')
            if i % 3 == 0:
                parts.append(f'<text class="axis" x="{x + cw / 2}" y="{top + ch + 16}" text-anchor="middle">{esc(labels[i])}</text>')
        parts.append("</svg>")
        table = "".join(f"<tr><td>{esc(l)}</td><td>{v}{unit}</td></tr>" for l, v in zip(labels, values))
        return ("".join(parts) + f'<details class="tv"><summary>Show as table</summary>'
                f"<table><tbody>{table}</tbody></table></details>")

    # ------------------------------------------------------------ pieces

    def copy_block(self, text, rows=None):
        rows = rows or min(14, max(3, text.count("\n") + 2, len(text) // 90 + 2))
        return (f'<div class="copy"><textarea readonly rows="{rows}">{esc(text)}</textarea>'
                f'<button type="button" class="copybtn">Copy</button></div>')

    def brief(self, s):
        """The self-contained text a user pastes into a fresh chat to build one skill."""
        ex = [e for e in s["examples"] if self.ok(e["chat"], e["quote"])]
        ins = [q for q in s["instructions"] if self.ok(q["chat"], q["quote"])]
        chats = self.work_chats(s["chats"])
        lines = [f"# Build a skill: {s['title']}", "",
                 "Help me build this skill. If you have a skill-creator skill, or your platform has its own skill "
                 "creator, use it. Interview me one question at a time before you write anything, and test the "
                 "draft against the example requests at the end before I save it.", "",
                 "## What my chat history shows",
                 f"Purpose: {s['purpose']}",
                 f"Seen in {len(chats)} of my chats between {nice_date(self.syn['period']['from'])} and {nice_date(self.syn['period']['to'])}.", "",
                 "Draft triggers:"] + [f"- {t}" for t in s["triggers"]] + \
                ["Not for:"] + [f"- {t}" for t in s["not_for"]] + ["", "Steps seen in my chats:"] + \
                [f"{i}. {t}" for i, t in enumerate(s["seen_steps"], 1)] + ["", "Steps inferred (check these with me):"] + \
                [f"- {t}" for t in s["inferred_steps"]] + ["", "Instructions I keep repeating:"] + \
                [f'- "{q["quote"]}"' for q in ins] + ["", "## Design questions to go through with me"] + \
                [f"{i}. {q}" for i, q in enumerate(WALKTHROUGH, 1)] + ["", "Suggested files to attach:"] + \
                [f"- {a}" for a in s["assets"]] + ["", "## Example requests (real, from my chats)"] + \
                [f'{i}. "{e["quote"]}"' for i, e in enumerate(ex, 1)] + ["", "## Source chats (claude.ai; open them if you can)"] + \
                [f"- {self.link(c)}" for c in chats] + ["", "## Leave out"] + [f"- {t}" for t in s["leave_out"]] + \
                ["", "When the skill is ready, tell me how to save it on this platform."]
        return "\n".join(lines)

    # ------------------------------------------------------------ loops

    def skill_titles(self):
        """The suggested skills' titles by name: a loop that needs one first names it as its card does."""
        return {(s.get("name") or "").strip(): s["title"]
                for s in (self.syn.get("reusable") or {}).get("skills", []) if (s.get("title") or "").strip()}

    def valid_loops(self):
        """Loop cards that rest on a computed candidate, at most MAX_LOOPS, never past drafts."""
        cands = {c["id"]: c for c in (self.loops or {}).get("candidates", [])}
        valid = []
        for lp in (self.syn.get("loops") or {}).get("suggested", []):
            c = cands.get(lp.get("candidate"))
            if not c:
                self.loop_notes.append(("DROPPED (loop without a candidate of 3+ occurrences)", lp.get("title")))
                continue
            if not (lp.get("title") or "").strip():
                self.loop_notes.append(("DROPPED (loop without a title)", lp.get("candidate")))
                continue
            if len(valid) >= MAX_LOOPS:
                self.loop_notes.append((f"DROPPED (over the limit of {MAX_LOOPS} loops)", lp.get("title")))
                continue
            if lp.get("start_level") not in LEVEL_LABELS:
                self.loop_notes.append((f"CHANGED (start level {lp.get('start_level')!r} set to report_only)",
                                        lp.get("title")))
                lp = {**lp, "start_level": "report_only"}
            if lp.get("kind") not in KIND_LABELS:
                self.loop_notes.append((f"CHANGED (kind {lp.get('kind')!r} set to {c['kind_hints'][0]!r})",
                                        lp["title"]))
                lp = {**lp, "kind": c["kind_hints"][0]}
            skill = lp.get("skill") or {}
            if skill.get("status") in ("exists", "build_first") and not (skill.get("name") or "").strip():
                self.loop_notes.append((f"CHANGED (skill status {skill['status']!r} without a name set to none)",
                                        lp["title"]))
                lp = {**lp, "skill": {"name": "", "status": "none"}}
            elif skill.get("status") == "build_first" and skill["name"].strip() not in self.skill_titles():
                self.loop_notes.append((f"NOTE (skill {skill['name']!r} is not among the skills to build)",
                                        lp["title"]))
            valid.append((lp, c))
        return valid

    @staticmethod
    def loop_evidence(c):
        s = f"{c['occurrences']} times from {nice_date(c['first'])} to {nice_date(c['last'])}"
        counts = []
        if c.get("earlier_occurrences"):
            counts.append(f"{c['earlier_occurrences']} from older chats in the export")
        if c.get("started_before"):
            counts.append(f"{c['started_before']} started before this period")
        if counts:
            s += f" ({', '.join(counts)})"
        rhythm = c.get("rhythm")
        if rhythm and rhythm != "irregular":
            s += f" · {rhythm}"
            if c.get("weekday"):
                s += f", mostly on {c['weekday']}s"
            if c.get("month_part"):
                s += f", {c['month_part']}"
        elif rhythm == "irregular":
            s += " · no fixed rhythm"
        return s

    @staticmethod
    def loop_trigger_line(c):
        if c["source"] == "check":
            return f"You applied this check in {c['occurrences']} chats, in: {', '.join(c.get('patterns', [])) or 'several tasks'}."
        trig = c.get("trigger") or {}
        total = sum(trig.values())
        if not total:
            return ""
        top, n = max(trig.items(), key=lambda kv: kv[1])
        return f"Started by {TRIGGER_LABELS.get(top, top)} in {n} of {total} chats this period."

    def loop_brief(self, lp, c):
        quotes = [q for q in lp.get("quotes", []) if self.ok(q["chat"], q["quote"])]
        chats = self.work_chats(c["chats"])
        skill = lp.get("skill") or {}
        title = self.skill_titles().get(skill.get("name"))
        to_build = (f"the {title} skill, which I still need to build (see Skills to build)" if title
                    else f"a {skill.get('name')} skill, which I still need to build")
        skill_line = {"exists": f"my {skill.get('name')} skill", "build_first": to_build}.get(
            skill.get("status"), "no skill")
        steps = [f"{i}. {s['text']}" + ("" if s.get("seen") else " (inferred: check this with me)")
                 for i, s in enumerate(lp.get("steps", []), 1)]
        lines = [f"# Build a loop: {lp['title']}", "",
                 "Help me set this up as a loop: work that runs on its own when its trigger comes, checks its own "
                 "result and reports to me. Interview me one question at a time before you set anything up. Design "
                 "the check first, and start it report-only or as drafts: nothing gets sent, changed or deleted "
                 "without me.", "",
                 "## What my chat history shows",
                 f"Kind of loop: {KIND_LABELS.get(lp.get('kind'), lp.get('kind'))}",
                 f"Seen {self.loop_evidence(c)}.",
                 self.loop_trigger_line(c), "",
                 "## The loop as drafted",
                 f"Why: {lp.get('why', '')}",
                 f"Trigger: {lp.get('trigger', '')}",
                 f"Input: {lp.get('input', '')}",
                 "Steps:"] + steps + [
                 f"Skill: {skill_line}",
                 f"Check: {lp.get('check', '')}",
                 f"Done when: {lp.get('done_when', '')}",
                 f"Result goes to: {lp.get('output', '')}",
                 f"Where I step in: {lp.get('you_step_in', '')}",
                 f"Starting level: {LEVEL_LABELS[lp['start_level']]}", "",
                 "Where it could run:"] + [f"- {RUNS_IN.get(r, r)}" for r in lp.get("runs_in", [])] + [
                 "", "## Design questions to go through with me"] + \
                [f"{i}. {q}" for i, q in enumerate(LOOP_WALKTHROUGH, 1)] + \
                ["", "## What I said (real, from my chats)"] + [f'- "{q["quote"]}"' for q in quotes] + \
                ["", "## Source chats (claude.ai; open them if you can)"] + [f"- {self.link(x)}" for x in chats] + \
                ["", "When it is set up, tell me where I can see its runs, and how to pause or stop it."]
        return "\n".join(lines)

    def loop_card(self, lp, c):
        skill = lp.get("skill") or {}
        title = self.skill_titles().get(skill.get("name"))
        to_build = (f"Needs the <strong>{esc(title)}</strong> skill first (see Skills to build)" if title
                    else f"Needs a <code>{esc(skill.get('name'))}</code> skill first")
        skill_html = {"exists": f"Runs your <code>{esc(skill.get('name'))}</code> skill", "build_first": to_build}.get(
            skill.get("status"), "No skill needed")
        steps = "".join(f"<li>{esc(s['text'])}{'' if s.get('seen') else ' <span class=tag>inferred</span>'}</li>"
                        for s in lp.get("steps", []))
        rows = [("Starts", esc(lp.get("trigger", ""))), ("Reads", esc(lp.get("input", ""))),
                ("Steps", f"<ol class='steps'>{steps}</ol>"), ("Skill", skill_html),
                ("Checks itself", esc(lp.get("check", ""))), ("Done when", esc(lp.get("done_when", ""))),
                ("Result goes to", esc(lp.get("output", ""))), ("You step in", esc(lp.get("you_step_in", ""))),
                ("Can run in", "<br>".join(esc(RUNS_IN.get(r, r)) for r in lp.get("runs_in", [])))]
        quotes = "".join(self.quote(q) for q in lp.get("quotes", []))
        return (f"<div class='card loop'><div class='loophead'><h4>{esc(lp['title'])}</h4>"
                f"<span class='pill'>{esc(KIND_LABELS.get(lp.get('kind'), lp.get('kind')))}</span>"
                f"<span class='pill level'>Starts as: {LEVEL_LABELS[lp['start_level']]}</span></div>"
                f"<p>{esc(lp.get('why', ''))}</p><p class='note'>{esc(self.loop_evidence(c))}. "
                f"{esc(self.loop_trigger_line(c))}</p>{quotes}<dl class='loopgrid'>" +
                "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl>"
                f"<details><summary>Build this loop: copy and paste into a new chat</summary>"
                f"{self.copy_block(self.loop_brief(lp, c), 14)}</details></div>")

    def history_note(self):
        """One line in the notes when loops.py read the older chats, so the report can't leave it out."""
        hp = (self.loops or {}).get("history_pass") or {}
        if not hp.get("chats"):
            return []
        return [f"Loop history also used {hp['chats']} older chats from {nice_date(hp['from'])} to "
                f"{nice_date(hp['to'])}, read from title and first message only."]

    def previous_note(self):
        """The facts about last run for "Since last time", from state_block.py find; the synthesis compares."""
        if not self.previous:
            return ""
        block, days = self.previous["block"], self.previous["days_since"]
        start, end = date.fromisoformat(block["period"]["from"]), date.fromisoformat(block["period"]["to"])
        span = (f"{start.day} {start.strftime('%b')} to {end.day} {end.strftime('%b')}" if start.year == end.year
                else f"{nice_date(block['period']['from'])} to {nice_date(block['period']['to'])}")
        s = f"Previous run: {nice_date(block['run'])}, covering {span}, {days} day{'' if days == 1 else 's'} ago."
        if self.previous.get("overlap"):
            s += " The two periods overlap by more than half, so the comparison is light."
        if self.previous.get("long_gap"):
            s += " That is a long gap, so the figures are far apart."
        return f"<p class='note'>{esc(s)}</p>"

    def loops_section(self):
        out = ["<section id='loops'><h2>Put it on a loop</h2>"]
        if self.loops is None:
            out.append("<p class='note'>Loops were not checked in this run.</p></section>")
            return "".join(out)
        syn_loops = self.syn.get("loops") or {}
        valid = self.valid = self.valid_loops()
        out.append("<p class='lead'>Some work comes back on a rhythm, or after the same kind of event. A loop runs it "
                   "for you: it starts on its own, checks its own result and reports to you. Every loop here starts "
                   "report-only or as drafts, so nothing is sent or changed without you.</p>")
        if valid:
            out.append("<div class='loops'>" + "".join(self.loop_card(lp, c) for lp, c in valid) + "</div>")
        else:
            out.append("<p>Nothing came back often enough, or on a clear enough trigger, to run on its own yet.</p>")
        existing = []
        for e in syn_loops.get("existing", []):
            chats = self.work_chats(e.get("chats", []))
            if not chats:
                continue
            if len(existing) >= MAX_LOOPS:
                break
            links = " ".join(f'<a href="{esc(self.link(x))}" target="_blank" rel="noopener">{esc(self.title.get(x, "chat"))}</a>'
                             for x in chats)
            existing.append(f"<li><strong>{esc(e['name'])}</strong> ({esc(RUNS_IN.get(e.get('where'), e.get('where', '')))}): "
                            f"{esc(e.get('what', ''))} <em>Next step:</em> {esc(e.get('suggestion', ''))} "
                            f"<span class='src'>{links}</span></li>")
        if existing:
            out.append("<h3>Loops you already run</h3><ul class='points'>" + "".join(existing) + "</ul>")
        not_yet = syn_loops.get("not_yet", [])
        if not_yet:
            out.append("<h3>Not a loop yet</h3><ul class='points'>" +
                       "".join(f"<li><strong>{esc(n['pattern'])}:</strong> {esc(n['why'])}</li>" for n in not_yet) +
                       "</ul>")
        out.append("</section>")
        return "".join(out)

    # ------------------------------------------------------------ page

    def render(self):
        st, ag, syn = self.stats, self.agg, self.syn
        g = syn["at_a_glance"]
        langs = st.get("language_user_msgs", {})
        long_work = ag.get("long_chats_over_55", sum(1 for t, _ in ag["longest_chats_user_turns"] if t > 55))
        tiles = [
            (str(st["conversations"]), "chats"),
            (f'{st["active_days"]}', "active days"),
            (str(ag["work_chats_analysed"]), "work chats analysed"),
            (f'{round(st["rewound_convs_pct"])}%', "of chats had an edited message"),
            (str(long_work), "work chats past 55 turns"),
        ]
        if sum(langs.values()):
            top, cnt = max(langs.items(), key=lambda kv: kv[1])
            name = {"en": "English", "nl": "Dutch"}.get(top, top)
            tiles.append((f"{round(100 * cnt / sum(langs.values()))}%", f"of your messages in {name}"))
        cats = {}
        for k, v in ag["categories"].items():
            lab = CATEGORY_LABELS.get(k, k)
            cats[lab] = cats.get(lab, 0) + v["share_of_time_pct"]
        cat_rows = sorted(((k, round(v) if v >= 1 else round(v, 1)) for k, v in cats.items()), key=lambda kv: -kv[1])
        feat_rows = [(k, round(v)) for k, v in st["feature_use_pct"].items() if k not in FEATURE_SKIP][:8]
        hours = [st["hours"].get(str(h), st["hours"].get(h, 0)) for h in range(24)]

        out = []
        a = out.append
        a(f"<header><p class='eyebrow'>AI usage insights &middot; {esc(syn['period']['source'])}</p>"
          f"<h1>How you worked with AI</h1>"
          f"<p class='sub'>{esc(syn['period']['label'])}: {esc(nice_date(syn['period']['from']))} to {esc(nice_date(syn['period']['to']))}</p></header>")
        a("<nav>" + " ".join(f'<a href="#{i}">{t}</a>' for i, t in [
            ("glance", "At a glance"), ("figures", "Key figures"), ("work", "How you work"), ("works", "What works"),
            ("friction", "Friction"), ("reuse", "Make it reusable"), ("loops", "Loops"), ("pack", "Context pack"),
            ("share", "Share"),
            ("notes", "Notes")]) + "</nav>")

        a("<section id='glance'><h2>At a glance</h2><div class='glance'>")
        a(f"<div class='card'><h3>What's working</h3><p>{esc(g['working'])}</p></div>")
        a(f"<div class='card'><h3>What's in the way</h3><p><strong>On Claude's side:</strong> {esc(g['in_the_way_claude'])}</p>"
          f"<p><strong>On your side:</strong> {esc(g['in_the_way_you'])}</p></div>")
        a("<div class='card'><h3>Quick wins</h3><ol>" + "".join(f"<li>{esc(w)}</li>" for w in g["quick_wins"]) + "</ol></div>")
        a(f"<div class='card'><h3>A bigger idea</h3><p>{esc(g['bigger'])}</p></div></div></section>")

        a("<section id='figures'><h2>Key figures</h2><div class='tiles'>" +
          "".join(f"<div class='tile'><span class='num'>{esc(n)}</span><span class='cap'>{esc(c)}</span></div>" for n, c in tiles) +
          "</div>")
        a("<div class='charts'>")
        a("<figure><figcaption id='c1-t'>Share of your time in chat, by kind of work</figcaption>" +
          self.hbar(cat_rows, "%", "c1") + "<p class='note'>Work chats only. Time is estimated from the gaps between "
          "messages, so read it as a relative split, not hours.</p></figure>")
        a("<figure><figcaption id='c2-t'>Your messages by hour of day</figcaption>" +
          self.columns(hours, [f"{h:02d}:00" for h in range(24)], " messages", "c2") + "</figure>")
        a("<figure><figcaption id='c3-t'>Features used, share of chats</figcaption>" +
          self.hbar(feat_rows, "%", "c3") + "</figure>")
        a("</div></section>")

        a("<section id='work'><h2>How you work</h2><ul class='points'>" +
          "".join(f"<li>{esc(p)}</li>" for p in syn["how_you_work"]) + "</ul></section>")

        a("<section id='works'><h2>What works</h2><div class='grid3'>")
        for w in syn["what_works"]:
            links = "<br>".join(f'<a href="{esc(self.link(c))}" target="_blank" rel="noopener">{esc(self.title.get(c, "chat"))}</a>'
                                for c in self.work_chats(w["chats"]))
            a(f"<div class='card'><h3>{esc(w['title'])}</h3><p>{esc(w['text'])}</p><p class='src'>{links}</p></div>")
        a("</div></section>")

        a("<section id='friction'><h2>Friction</h2><div class='cols'>")
        for side, title in (("claude", "On Claude's side"), ("you", "On your side")):
            a(f"<div><h3 class='side'>{title}</h3>")
            for f in [x for x in syn["friction"] if x["side"] == side]:
                qs = "".join(self.quote(q) for q in f["quotes"])
                a(f"<div class='card'><h4>{esc(f['title'])}</h4><p>{esc(f['text'])}</p>{qs}"
                  f"<p class='fix'><strong>Fix:</strong> {esc(f['fix'])}</p></div>")
            a("</div>")
        a("</div></section>")

        r = {"preferences": [], "project_instructions": [], "prompts": [], "skills": [], "covered": [],
             "not_worth_it": [], **syn.get("reusable", {})}
        a("<section id='reuse'><h2>Make it reusable</h2><p class='lead'>Each pattern goes to the form that fits it. "
          "Small things are ready to paste. Skills come with a brief: paste it into a fresh chat to build the skill "
          "properly there.</p>")
        a("<h3>1. Preferences <span class='tag'>paste into your profile preferences</span></h3>")
        for p in r["preferences"]:
            ev = [q for q in p["evidence"] if self.ok(q["chat"], q["quote"])]
            a(f"<div class='card'><h4>{esc(p['title'])}</h4>{self.copy_block(p['text'], 3)}"
              f"<details><summary>Why: {len(ev)} times in your chats</summary>" +
              "".join(self.quote(q) for q in ev) + "</details></div>")
        a("<h3>2. Project instructions <span class='tag'>paste into the project's instructions</span></h3>")
        for p in r["project_instructions"]:
            ev = [q for q in p["evidence"] if self.ok(q["chat"], q["quote"])]
            a(f"<div class='card'><h4>{esc(p['title'])}</h4><p class='note'>{esc(p['where'])}</p>{self.copy_block(p['text'], 5)}"
              f"<details><summary>Why: {len(ev)} examples</summary>" + "".join(self.quote(q) for q in ev) + "</details></div>")
        a("<h3>3. Prompt templates</h3>")
        for p in r["prompts"]:
            ev = [q for q in p["evidence"] if self.ok(q["chat"], q["quote"])]
            a(f"<div class='card'><h4>{esc(p['title'])}</h4><p>{esc(p['why'])}</p>{self.copy_block(p['text'], 4)}"
              f"<details><summary>Evidence</summary>" + "".join(self.quote(q) for q in ev) + "</details></div>")
        a("<h3>4. Skills to build</h3><div class='grid3'>")
        for s in r["skills"]:
            a(f"<div class='card skill'><h4>{esc(s['title'])}</h4><p>{esc(s['purpose'])}</p>"
              f"<p class='note'>Seen in {len([c for c in s['chats'] if c in self.quotable])} chats"
              f"{' &middot; shareable' if s.get('shareable') else ''}</p>"
              f"<ol class='steps'>" + "".join(f"<li>{esc(t)}</li>" for t in s["seen_steps"]) + "</ol>"
              f"<details><summary>Build brief: copy and paste into a new chat</summary>{self.copy_block(self.brief(s), 14)}</details></div>")
        a("</div><h3>Already covered by your skills</h3><ul class='points'>" +
          "".join(f"<li><strong>{esc(c['pattern'])}</strong> ({c['chats']} chats): your <code>{esc(c['skill'])}</code> skill. "
                  f"Next month shows whether it gets used.</li>" for c in r["covered"]) + "</ul>")
        a("<h3>Not worth a skill</h3><ul class='points'>" +
          "".join(f"<li><strong>{esc(n['pattern'])}:</strong> {esc(n['why'])}</li>" for n in r["not_worth_it"]) + "</ul></section>")

        self.valid = []
        a(self.loops_section())

        a("<section id='pack'><h2>Your context pack</h2><p class='lead'>A short profile built from what you keep "
          "explaining. Paste it into custom instructions here, or into ChatGPT or Copilot, so new chats start informed.</p>" +
          self.copy_block(syn["context_pack"], 14) + "</section>")

        shareable = [(s["title"], s["purpose"]) for s in r["skills"] if s.get("shareable")]
        shareable += [(lp["title"], lp.get("why", "")) for lp, _ in self.valid if lp.get("shareable")]
        a("<section id='share'><h2>Skills and loops you could share</h2><p class='lead'>Only if you want to. These "
          "patterns look general enough for colleagues. Strip personal details first; the build brief lists what to "
          "leave out.</p><ul class='points'>" +
          "".join(f"<li><strong>{esc(t)}</strong>: {esc(p)}</li>" for t, p in shareable) + "</ul></section>")

        a(f"<section id='notes'><h2>Since last time</h2>{self.previous_note()}<p>{esc(syn['trends'])}</p>"
          "<h2>About this report</h2><ul class='points'>" +
          "".join(f"<li>{esc(c)}</li>" for c in syn["coverage"] + self.history_note()) +
          "<li>Something here wrong or not useful? Say so in next month's run and it will be dropped.</li></ul>"
          f"<p class='note'>Generated {date.today().isoformat()}. This report is yours: it isn't shared with anyone unless you share it.</p></section>")
        return PAGE.replace("{{BODY}}", "\n".join(out))


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI usage insights</title>
<style>
:root{--bg:#fcfcfb;--card:#ffffff;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--line:#e1e0d9;--accent:#2a78d6;--soft:#f3f2ee}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--card:#222220;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--line:#2c2c2a;--accent:#3987e5;--soft:#262624}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
main{max-width:960px;margin:0 auto;padding:40px 24px 80px}
header .eyebrow{color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-size:12px;margin:0}
h1{font-size:34px;line-height:1.15;margin:6px 0 4px}h2{font-size:22px;margin:0 0 14px}h3{font-size:17px;margin:22px 0 10px}h4{margin:0 0 6px;font-size:15px}
.sub{color:var(--ink2);margin:0}
nav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 0;margin:24px 0 8px;display:flex;flex-wrap:wrap;gap:4px 14px;font-size:14px;z-index:2}
nav a{color:var(--ink2);text-decoration:none}nav a:hover{color:var(--accent)}
section{padding:28px 0;border-bottom:1px solid var(--line)}section:last-child{border-bottom:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:12px}
.card h3{margin-top:0}.card p{margin:0 0 8px}.card p:last-child{margin-bottom:0}
.glance{display:grid;grid-template-columns:1fr 1fr;gap:12px}.glance .card{margin:0}
.glance ol{margin:0;padding-left:20px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-bottom:22px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.tile .num{display:block;font-size:28px;font-weight:650;line-height:1.1}.tile .cap{color:var(--ink2);font-size:13px}
.charts figure{margin:0 0 26px}figcaption{font-weight:600;margin-bottom:10px}
svg.chart{width:100%;max-width:700px;height:auto;display:block;overflow:visible}
.bar{fill:var(--accent)}.hit{fill:transparent}.lab{fill:var(--ink2);font-size:13px}.val{fill:var(--ink2);font-size:12px}
.axis{fill:var(--muted);font-size:11px}.grid{stroke:var(--line);stroke-width:1}.base{stroke:var(--muted);stroke-width:1}
.tv{font-size:13px;color:var(--ink2);margin-top:6px}.tv table{border-collapse:collapse;margin-top:6px}.tv td{padding:2px 12px 2px 0;border-bottom:1px solid var(--line)}
.note{color:var(--muted);font-size:13px}
.points{padding-left:20px;margin:0}.points li{margin-bottom:6px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}.grid3 .card{margin:0}
.src a{color:var(--accent);font-size:13px;margin-right:8px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:18px}.side{margin-top:0;color:var(--ink2)}
blockquote{margin:8px 0;padding:6px 10px;border-left:3px solid var(--line);background:var(--soft);border-radius:0 6px 6px 0;font-size:14px}
blockquote a{color:var(--ink2);text-decoration:none}blockquote a:hover{color:var(--accent)}
.fix{font-size:14px}
.lead{color:var(--ink2);margin-top:0}
.tag{font-weight:400;font-size:12px;color:var(--muted);margin-left:6px}
.copy{position:relative;margin:8px 0}
.copy textarea{width:100%;resize:vertical;font:13px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--ink);background:var(--soft);border:1px solid var(--line);border-radius:8px;padding:10px 12px;padding-right:76px}
.copybtn{position:absolute;top:8px;right:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:6px;padding:4px 10px;font-size:13px;cursor:pointer}
.copybtn:hover{border-color:var(--accent);color:var(--accent)}
details summary{cursor:pointer;color:var(--ink2);font-size:14px}
.steps{padding-left:20px;font-size:14px;color:var(--ink2);margin:6px 0 10px}
code{background:var(--soft);padding:1px 5px;border-radius:4px;font-size:14px}
.loops{display:grid;gap:12px}.loops .card{margin:0}
.loophead{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 8px;margin-bottom:6px}.loophead h4{margin:0 6px 0 0}
.pill{font-size:12px;color:var(--ink2);border:1px solid var(--line);border-radius:999px;padding:1px 9px}
.pill.level{color:var(--accent);border-color:var(--accent)}
dl.loopgrid{display:grid;grid-template-columns:140px 1fr;gap:6px 14px;margin:10px 0 12px;font-size:14px}
dl.loopgrid dt{color:var(--muted)}dl.loopgrid dd{margin:0}dl.loopgrid .steps{margin:0}
@media (max-width:720px){dl.loopgrid{grid-template-columns:1fr}dl.loopgrid dt{margin-top:6px}}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--bg);font-size:12px;padding:4px 8px;border-radius:6px;opacity:0;transition:opacity .1s;z-index:5}
@media (max-width:720px){.glance,.cols{grid-template-columns:1fr}h1{font-size:28px}}
@media print{nav,.copybtn,#tip{display:none}details{display:block}}
</style></head><body><main>
{{BODY}}
</main><div id="tip"></div>
<script>
(function(){
  var tip=document.getElementById('tip');
  document.querySelectorAll('[data-tip]').forEach(function(el){
    el.addEventListener('mousemove',function(e){tip.textContent=el.getAttribute('data-tip');tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY-28)+'px';tip.style.opacity=1;});
    el.addEventListener('mouseleave',function(){tip.style.opacity=0;});
  });
  document.querySelectorAll('.copybtn').forEach(function(b){
    b.addEventListener('click',function(){
      var ta=b.parentNode.querySelector('textarea');
      var done=function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy';},1500);};
      var fallback=function(){ta.focus();ta.select();try{document.execCommand('copy');done();}catch(e){b.textContent='Select and copy';}};
      if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(ta.value).then(done,fallback);}else{fallback();}
    });
  });
})();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    for k in ("conversations", "stats", "aggregate", "synthesis", "out"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--loops")
    ap.add_argument("--previous", help="previous.json from state_block.py find, when it found last run's block")
    args = ap.parse_args()
    rep = Report(args)
    page = rep.render()
    open(args.out, "w", encoding="utf-8").write(page)
    print(f"wrote {args.out} ({len(page) // 1024} KB)")
    for d in sorted(set(rep.dropped)):
        print("DROPPED (quote not found):", d)
    for d in sorted(set(rep.refused)):
        print("DROPPED (not a work chat):", d)
    for note, title in rep.loop_notes:
        print(f"{note}: {title}")


if __name__ == "__main__":
    main()
