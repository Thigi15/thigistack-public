---
name: ai-usage-insights
compatibility: Best in claude.ai; also works in Claude Code. Needs Python 3.9 or newer and a claude.ai data export of your own chats. The language figures and correction detection know English and Dutch only.
metadata:
  best-in: claude-ai
  works-in: claude-ai claude-code
description: Analyse the user's own AI chat history (a claude.ai data export) and produce a personal usage report - key figures, how they work, where their time goes, friction, what to turn into preferences, project instructions, prompt templates and skills, and which recurring work could run on its own as a loop (scheduled or triggered, checking its own result), with paste-ready text and build briefs. Use when the user asks for insights into their AI or Claude usage, a usage report or "Wrapped", how they could use Claude better, which skills to build or what to automate from their history, or uploads a conversations-000.zip export. Also when they ask in Dutch, for example "mijn AI-gebruik", "inzichten in hoe ik Claude gebruik", "hoe kan ik Claude beter gebruiken", "welke skills moet ik maken" or "een overzicht van mijn gesprekken met Claude" or "wat kan ik automatiseren".
---

# AI usage insights (v0.5.0)

A monthly self-reflection report on how someone works with AI, built from an export of their own chats.
It is a personal coach, not a monitor: the user runs it on their own data and the report stays with them.

Scripts are in this skill's `scripts/` folder. Run them with `python3 -I`, from a fresh working folder
(e.g. `insights/`), passing file paths as arguments. Install dependencies once:
`pip install ijson lingua-language-detector`; if pip refuses to install system-wide, make a virtual environment
first (`python3 -m venv .venv`, activate it, then run the scripts with its `python3`). On Windows `tzdata` is required
too (`pip install tzdata`): the scripts read time zones, and Windows has no time zone data of its own. `ijson` and
`lingua-language-detector` are optional:
without them the reader loads the file whole and language figures are skipped.

## Privacy rules (always)

- Only analyse an export the user uploaded themselves, about themselves.
- Personal and mixed chats are counted, never described, quoted or named, in the report or in your replies.
- Never bring up anything from the chats about health, money, relationships, family, politics or religion.
- Don't save anything from the export to memory. Don't publish the report or share it anywhere. The only thing
  published is the summary block, to one private artifact (step 16): figures and names, no chat content.
- Quotes in the report are short, verbatim and from the user's own work messages only.
- Loops start report-only or as drafts. Never suggest one that sends, posts, deletes or buys on its own.

## Workflow

Tell the user in one line what you're about to do, then work through these steps.
Keep a task list if your platform has one.

### 1. Get the data
If no `conversations-NNN.zip` is attached (for example when the user starts the skill with its slash
command), send the opening message from `references/data-export.md` in the user's language and wait.
If they upload the wrong file or another assistant's export, handle it as that file describes.
This version reads claude.ai exports only. The export is all the skill needs; a 90-day export every month gives
the most. Last run's summary travels inside it (step 4), so there is never anything else to keep or upload.

### 2. Read
```
python3 -I <skill>/scripts/read_claude_ai.py <conversations-000.zip> [more parts] --out conversations.jsonl
```
It marks this skill's own chats: an insights run (a chat where an export was uploaded) and a run of the monthly
reminder. The scripts below keep them out of the analysis; the figures still count the insights runs. Exit code 3
(with "refused:" on stderr) means the export holds more than one account's chats, such as an organization export:
stop, delete the upload from the working folder, and give the user the Team and Enterprise steps in
`references/data-export.md`. Never work around it. Any other non-zero code is an ordinary error: fix the command.

### 3. Choose the period and check there is enough
```
python3 -I <skill>/scripts/prepare.py conversations.jsonl --period auto --out selected.jsonl --summary prepare.json --older older.jsonl
```
Use `--period 30|90|all` or `--period custom --from YYYY-MM-DD --to YYYY-MM-DD` if the user asked for one.
`--older` writes the chats from before the period for step 8.
Tell the user the `message` from prepare.json in one line.
- `too_little`: offer the basic figures only (steps 5 and 14, with a short synthesis; skip loops) and suggest a longer export.
- `light`: continue; suggest skills only with strong evidence and call the report "first impressions".
- `full` / `capped`: continue.

### 4. Find last run's summary
```
python3 -I <skill>/scripts/state_block.py find <conversations-000.zip> [more parts] [--artifact artifact.txt] --prepare prepare.json --out previous.json
```
It looks for the block an earlier run pasted at the end of its reply, in every chat where an export was uploaded,
and keeps the newest that parses. In Claude, also read the backup artifact first (see "Platform notes").
When it finds nothing, it writes nothing: the report then says there is no comparison this time. Only
`previous.json` is for you; don't read the run chats themselves.

### 5. Count (no AI)
```
python3 -I <skill>/scripts/stats.py selected.jsonl --since "<since from prepare.json>" --tz <user's time zone> --out stats.json
```
Pass `--since None` when the period is "all".

### 6. Condense
```
python3 -I <skill>/scripts/digest.py selected.jsonl --outdir digests
```
This writes `quick.txt` (single-question chats) and `batch_NN.txt` files of about 15k tokens each.
Chats marked POSSIBLE TEST RUN are in the batches too: you decide in step 7 whether each one is a test.
Insights runs are left out: they are counted, never read.

### 7. Read and extract facets
Follow `references/facets.md`. Read `quick.txt`, then each batch file once, and after each file append
its facets to `facets.jsonl`. This is the expensive step: don't re-open `conversations.jsonl` or old
batches, and don't summarise batches back to the user.

### 8. Label the older chats for loop history
Only when `prepare.json → older_chats.in_digest` is above 0. Follow `references/facets.md` section "Older chats":
read `older.jsonl` once and write `older_labels.jsonl`, a scope for each chat and, for work chats only, a task and a
watch subject. Nothing else from these chats goes anywhere.

### 9. Check every quote
```
python3 -I <skill>/scripts/check_quotes.py selected.jsonl facets.jsonl --out facets_checked.jsonl
```
Dropped quotes are listed. Fix them only if the finding matters; otherwise let them go.

### 10. Combine (no AI)
```
python3 -I <skill>/scripts/aggregate.py selected.jsonl facets_checked.jsonl --out aggregate.json
```

### 11. Merge tasks into patterns
Follow `references/synthesis.md` section 1 and write `patterns.json`.

### 12. Find loop candidates (no AI)
```
python3 -I <skill>/scripts/loops.py selected.jsonl facets_checked.jsonl --prepare prepare.json --aggregate aggregate.json --patterns patterns.json [--older older.jsonl --older-labels older_labels.jsonl] --tz <user's time zone> --out loops.json
```
The older chats' dates make monthly work show up. Pass `--older` and `--older-labels` when you ran step 8.

### 13. Write the findings
Follow `references/synthesis.md`: check the user's existing skills, loops and scheduled tasks, route each pattern
(preference, project instructions, prompt, skill, loop, nothing), decide on loops with `references/loops.md`,
compare with `previous.json` if step 4 wrote one, and write `synthesis.json`.

### 14. Render
```
python3 -I <skill>/scripts/render_report.py --conversations selected.jsonl --stats stats.json --aggregate aggregate.json --synthesis synthesis.json --loops loops.json [--previous previous.json] --out ai-usage-insights-YYYY-MM.html
```
If the renderer lists dropped quotes, refused chats or dropped loops, fix `synthesis.json` and render again.
Then render the Wrapped, a short tap-through story of the same month:
```
python3 -I <skill>/scripts/render_wrapped.py --prepare prepare.json --stats stats.json --aggregate aggregate.json --synthesis synthesis.json --facets facets_checked.jsonl --conversations selected.jsonl [--patterns patterns.json] [--loops loops.json] [--previous previous.json] --out ai-usage-wrapped-YYYY-MM.html
```
Every number on it is counted by the scripts. A line starting with `LEFT OFF` means a text from `synthesis.json`
didn't go on a card (it quotes a chat, cites a chat that isn't a work chat, or a friction title or fix holds a
number). Fix that text and render again, or accept that the card shows the next item.

### 15. Monthly reminder
Find out whether the user has a monthly reminder to run this skill, and offer one if not.
- **Declined before:** if `previous.json → block.reminder` is `declined`, don't ask; the value is `declined`
  again. Only ask when the user brings it up.
- **Check:** if the session has tools to list and create scheduled tasks (some sessions load them only through a
  tool search), list the user's tasks and look for one named exactly "AI usage insights: monthly reminder".
- **Found:** say in one line when it next runs. Never create a second one. The value is `existing`. If its prompt
  doesn't start with the fixed first line (an older reminder asks to add a second file), offer once, in one line, to
  bring it up to date with the prompt from `references/data-export.md` section "Monthly reminder".
- **Notifications off:** only when the task explicitly says its notifications are off. A task without a setting of
  its own uses the account default, which may well be on (seen 20-11-2026): don't mention it then.
  When they are explicitly off and the tool can change that, include it in the offer. When it can't (the update tool
  on claude.ai, 20-11-2026), say once, in one line, that the user can switch them on in the task's own settings, and
  don't offer it.
- **None found:** ask once, in one line, whether to set a monthly reminder on the 1st of the month, in the morning,
  in the user's time zone. On a yes, create it under that exact name with the prompt from
  `references/data-export.md` section "Monthly reminder", with push notifications on if the tool allows it; the
  value is `scheduled`. On a no, it is `declined`.
- **No scheduling tool:** suggest a monthly calendar reminder in one line. The value is `unavailable`.

### 16. Write the summary for next time
```
python3 -I <skill>/scripts/state_block.py write --prepare prepare.json --stats stats.json --aggregate aggregate.json --synthesis synthesis.json --loops loops.json --reminder <value from step 15> --out state_block.md
```
It writes a sentence and a fenced block: the period, the key figures and the names of what was suggested, never a
quote, chat id or chat title. You never write or change it yourself. In Claude, also update the backup artifact
(see "Platform notes").

### 17. Deliver and reply
Give the user the report and the Wrapped, both as files; the Wrapped is not published anywhere. Mention the
Wrapped in one line: a one-minute story of the month, whose last card is the one to show a manager or the team.
Then three or four lines: the one quick win that matters most, where the build briefs
are (skills and loops), and to run it again next month with a 90-day export. Don't repeat the report.
End the reply with the contents of `state_block.md`, pasted unchanged: it is how the next run finds this one.

## Platform notes

**Claude (claude.ai):** the summary block has a backup in one private artifact titled exactly
"AI usage insights: state". Only when the session has artifact tools; without them, skip both steps.
- Step 4: if that artifact exists, read it, save its text unchanged to `artifact.txt` and pass
  `--artifact artifact.txt`. The script takes whichever block is newest, the artifact's or the export's.
- Step 16: publish the contents of `state_block.md` unchanged to that artifact, as a new version of it. Never
  create a second one, and never put anything else in it.

## Language

The skill and the page headings are in English. Write the synthesis texts in the user's language
(ask at the start if it isn't clear; default to the language most of their chats are in). Paste-ready
texts for colleagues or tools can follow the language the user works in there.

## Known limitations (v0.5)

- claude.ai exports only; ChatGPT, Gemini and Copilot readers are planned.
- Loops need 3 occurrences. A 30-day export rarely shows monthly work; a 90-day export does.
- The older chats are judged from their title and first message only, so their task labels are rougher than this
  period's. They feed the loop history and nothing else. At most 300 of them are read, the most recent first, and
  suspected test runs are left out.
- The comparison needs last run's summary block. An incognito run, or a deleted run chat, leaves no block in the
  export; in Claude, the artifact still has it.
- Whether a suggestion was taken up is inferred from chats, not seen directly.
- An insights run is recognised by its uploaded `conversations-NNN.zip`; a renamed export isn't.
- Runs of scheduled tasks are recognised by their prompt. Whether they appear in the export at all hasn't been
  confirmed yet.
- The reminder step needs scheduling tools in the session; whether they exist, and on which plans, is outside the
  skill's control. A deleted reminder is noticed at the next run, not before.
- The skill can't see whether scheduled tasks are turned on for the user's plan or organisation; the loop brief
  asks them to check.
- Page headings are English only.
- Wrapped labels are English only. Its numbers use English separators too (1,234).
- Chats don't record their project in the export, so project-level advice is inferred.
- Personal chats are only recognised after the model has read their digest.
- The "time" chart is a relative estimate from gaps between messages, not real hours.
