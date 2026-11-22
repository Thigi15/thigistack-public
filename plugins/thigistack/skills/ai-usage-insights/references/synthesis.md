# Synthesis: turning the aggregate into the report

Read `aggregate.json`, `prepare.json`, `stats.json` and, if SKILL.md step 4 found last run's block,
`previous.json`. Write `patterns.json` (step 1), run `loops.py` (SKILL.md step 12), then write `synthesis.json` in the
schema below. `render_report.py` turns it into the page, `render_wrapped.py` into the Wrapped.

## 1. Merge tasks first, into patterns.json

`aggregate.json → tasks` groups chats by the exact `task` label. Labels that mean the same job are
still split ("prepare for a meeting", "meeting debrief", "write a meeting invite"). Merge them into
patterns by meaning before counting, and write the merge to `patterns.json`:

```json
{"prepare for a meeting": ["prepare for a meeting", "meeting debrief", "write a meeting invite"]}
```

Only labels that merge need a line; a label on its own stays its own pattern. `older_labels.jsonl`
(SKILL.md step 8) holds the older chats' task labels: merge those too, so their dates land on the same pattern.
A pattern counts as **recurring** when it has 3+ chats in 2+ different weeks (light tier: 4+ chats).

Do the same for work items, into `items.json`: look at the `work_item` phrases in `facets_checked.jsonl` (and
`older_labels.jsonl`), and merge the phrases that turned out to mean the same piece of work, keeping the phrase that
reads best:

```json
{"website relaunch": ["website relaunch design", "relaunch kickoff"]}
```

Only phrases that merge need a line. Write `{}` when none do: `zoom.py` (SKILL.md step 12) reads it either way.

## 2. Check what the user already has

Look at the skills available to you in this session (your skill list). When a recurring pattern is
already covered by one of the user's own skills, put it under `covered` instead of suggesting a new
skill. Never suggest a duplicate. Do the same for loops: when the chats show the user already runs
something on its own (a scheduled task, an agent that posts a digest, a hook), list it under
`loops.existing` instead of suggesting it again. When the session has tools to list scheduled tasks, list them:
a chat whose first message equals a task's prompt is a run of that task. It is a loop the user already runs, so it
goes under `loops.existing` and never becomes a new suggestion. Leave this skill's own reminder out: its runs never
reach the digests.

## 3. Route each pattern to the right form

1. A preference that applies to almost everything (tone, length, format, language, pacing), repeated in 2+ chats → **preference**.
2. Background about an ongoing area that the user keeps re-explaining → **project instructions**.
3. A single-step job with a variable input and a stable instruction → **prompt template**.
4. A multi-step job with stable steps, recurring (see 1), that may need files or templates → **skill**.
5. Comes back on a rhythm or after the same kind of event, with a check that can be written down → **loop**.
   Only from a candidate in `loops.json`; follow `references/loops.md`. A loop often runs a skill: when
   the skill doesn't exist yet, suggest the skill under `skills` and the loop with `skill.status: "build_first"`.
   The loop's `skill.name` must then be that skill's `name`, so the card can show its title.
6. Rare, exploratory or too variable → **not_worth_it**. Saying so builds trust.

Limit: at most 4 preferences, 2 project instructions, 3 prompts, 3 skills and 3 loops. Pick the strongest by evidence.

## 3b. Zoomed out: route the larger picture

`zoom.json` shows the pieces of work the period went to. The report prints its numbers itself; you only route what
they show, in `zoomed_out`. Each entry points at one id in `zoom.json` with `ref`, and the route has to fit that
kind of id, or the renderer drops it:

| What zoom.json shows | `ref` | `route` |
| --- | --- | --- |
| A work item with restarts (chats that pick up earlier chats) | `item:<name>` | `project_log`: a project with a short log, so the next chat starts from it |
| A work item with relays (work started from, or sent to, another tool) | `item:<name>` | `move_step`: move the step to the tool where the work happens |
| A recurring flow inside chats (4+ steps) | `flow:<chat>` | `chain_skill`: a skill that runs the steps in order |
| A workflow repeated across work items (a use case serving 2+ work items) | `case:<pattern>` | `workflow_skill`, or `loop` when it also has a loop candidate |
| A kind made repeatedly with the same shape | `kind:<kind>\|<for>\|<purpose>` | `template_or_skill` |

The top use cases fold into this section: the report lists them under "Zoomed out" with the number of work items
each served, so a use case that serves several work items is the workflow to route. At most 5 entries; pick by the
counts in `zoom.json`. Skip a route that repeats a skill or loop already under `reusable` or `loops`: point at it in
the text instead. Never write a number in a route's title or text: the report drops such a route, and shows the
counts from `zoom.json` next to it.

## 4. Schema

```json
{
  "language": "en|nl: the report language; numbers on both pages follow it (1,180 or 1.180)",
  "period": {"label": "Last 30 days", "from": "2026-10-17", "to": "2026-11-16", "source": "claude.ai"},
  "at_a_glance": {
    "working": "2-3 sentences, coaching tone, no numbers",
    "in_the_way_claude": "1 sentence: what goes wrong on the assistant's side",
    "in_the_way_you": "1 sentence: what the user does that costs time",
    "quick_wins": ["3 short actions, each doable in 5 minutes"],
    "bigger": "1-2 sentences: a larger workflow change worth trying"
  },
  "how_you_work": ["4-6 one-sentence observations; numbers allowed here"],
  "what_works": [{"title": "", "text": "", "chats": ["8-char ids"]}],
  "friction": [{"side": "claude|you", "type": "optional: the friction type from aggregate.json → friction", "title": "", "text": "", "quotes": [{"chat": "", "quote": ""}], "fix": ""}],
  "reusable": {
    "preferences": [{"title": "", "text": "paste-ready, 1-2 sentences, written as an instruction to the assistant", "evidence": [{"chat": "", "quote": ""}]}],
    "project_instructions": [{"title": "", "where": "which project or area", "text": "paste-ready", "evidence": []}],
    "prompts": [{"title": "", "text": "paste-ready template with [placeholders]", "why": "", "evidence": []}],
    "skills": [{
      "name": "kebab-case", "title": "", "purpose": "", "chats": ["ids"],
      "triggers": [""], "not_for": [""],
      "seen_steps": ["steps seen in the chats"], "inferred_steps": ["steps you think are missing; the user checks them"],
      "instructions": [{"chat": "", "quote": ""}],
      "examples": [{"chat": "", "quote": "3 real requests, verbatim from the user's messages"}],
      "assets": ["files the user should attach, written in first person: 'A template I like'"],
      "leave_out": ["what to strip before sharing"],
      "shareable": true
    }],
    "covered": [{"skill": "existing skill name", "pattern": "", "chats": 0}],
    "not_worth_it": [{"pattern": "", "why": ""}]
  },
  "loops": {
    "suggested": [{
      "name": "kebab-case", "title": "", "kind": "time|event|watch|check",
      "candidate": "the candidate id from loops.json, e.g. task:weekly status update",
      "why": "1 sentence: why this is worth running on its own",
      "trigger": "", "input": "", "steps": [{"text": "", "seen": true}],
      "skill": {"name": "", "status": "exists|build_first|none"},
      "check": "how a run tests its own result", "done_when": "", "output": "", "you_step_in": "",
      "runs_in": ["claude_scheduled_task|claude_code_routine|claude_code_hook|chatgpt_task|copilot_scheduled_prompt|power_automate|own_agent|manual_prompt"],
      "start_level": "report_only|draft_only",
      "quotes": [{"chat": "", "quote": ""}], "shareable": true
    }],
    "existing": [{"name": "", "where": "one of the runs_in values", "what": "", "chats": ["ids"], "suggestion": ""}],
    "not_yet": [{"pattern": "", "why": "what is missing before it can run on its own"}]
  },
  "zoomed_out": [{"ref": "an id from zoom.json", "route": "project_log|move_step|chain_skill|workflow_skill|loop|template_or_skill", "title": "", "text": "1-2 sentences, no numbers"}],
  "context_pack": "Plain text profile, 6-10 lines, only facts the user stated about themselves and their work",
  "trends": "With previous.json: compare with its block in 2-4 sentences (see 'Since last time' below). Without it: say in one sentence that there is no comparison this time, without asking for anything.",
  "coverage": ["What the data does and doesn't cover, incl. the tier message from prepare.json, personal/mixed/test/empty counts, and that quotes were checked. Not the note on older chats used for loop history: the renderer writes it."]
}
```

## Since last time (`trends`)

The renderer writes the facts above your text: "Previous run: 20 Nov 2026, covering 17 Oct to 16 Nov, 34 days
ago.", and a line when the periods overlap by more than half or the gap is long (`previous.json → overlap`,
`long_gap`). Don't repeat them. Your 2-4 sentences:

- Compare with exactly the figures in `previous.json → block.figures`, not with your own recollection.
- **Counted or labelled.** The figures the scripts count (`chats`, `active_days`, `user_messages`, `edited_pct`,
  `long_chats`, `feature_use_pct`) can be compared as they are. The ones that rest on the labels you give
  (`time_share_pct` per kind of work, `work_chats_analysed`, `made_by_kind`) shift from reading alone: the same export, read twice, can
  move a time share by several points. Mention a change in a time share only at 10 points or more, and in
  `work_chats_analysed` or a kind in `made_by_kind` only at 10% or more; never make any of them the headline. An
  older block has no `made_by_kind`: then say nothing about what was made.
- **Overlap** (`overlap: true`): most of the chats are the same ones, so compare lightly. Say what is new rather
  than what changed.
- **A long gap** (`long_gap: true`): the habits may simply have moved on; don't read every difference as progress.
- **Uptake** of what was suggested (`block.suggested`): say a suggestion "looks taken up" only with evidence from
  this period's chats, such as fewer of the corrections a preference addressed, or a skill's name showing up. Never
  claim it as certain, and say nothing about a suggestion you have no evidence on.

## Writing rules

- Every quote must be verbatim from the user's messages (the renderer drops anything it can't find). Reuse quotes from `facets_checked.jsonl` / `aggregate.json`.
- Coaching tone: what to try, not what's wrong with them. Split blame honestly between the assistant and the user.
- No hours-saved claims. Time is a relative share only.
- Exploration is not failure. Don't count `exploratory` outcomes against the user.
- Never mention anything from personal or mixed chats, not even the topic. The renderer refuses quotes
  and links from any chat that isn't a work chat, so use only chats from `aggregate.json → quotable_chats`.
- Friction: give each item the `type` it rests on (a key of `aggregate.json → friction`, such as
  `context_resupplied`) when there is one. The Wrapped counts that type in the aggregate and shows the count; without
  a `type` it shows no number. Write no numbers in a friction `title` or `fix` ("6 times"): the Wrapped leaves such a
  text off, since its counts come from the scripts only.
- Loops: the numbers on a loop card (how often, which rhythm, which weekday) come from `loops.json`.
  Don't repeat or round them in your own texts; describe what the loop does.
- Work item names go in `zoomed_out` and nowhere the Wrapped reads (titles of friction, skills, loops, patterns):
  the Wrapped and the summary block never carry them.
- The context pack holds work facts only: role, ongoing work, tools, working style. No health, money, family, relationships, politics or religion, even if stated.
- Write in the report language (see SKILL.md). Keep it short; the page does the rest.
