# Loops: work that runs on its own

A skill says *how* a job is done. A loop adds *when* it runs without the user starting it, *how* it checks
its own result, and *where* the result lands. A well-built loop has a trigger, a check it can run on its own
output, a clear point where it is done or stops, and a point where the user steps in. Most loops run a skill.

Read this after `loops.py` has written `loops.json` (SKILL.md step 12), and before writing `synthesis.json → loops`.

## 1. What loops.json gives you

Each candidate has 3 or more occurrences in work chats that are no test run, counted from dates only.
`occurrences` includes `earlier_occurrences`, from the older chats in the export, so a monthly job shows up. `started_before` counts this period's chats
that started before it. The fields you use:

- `id`: put it in the loop's `candidate`. A loop without a matching candidate is not shown.
- `kind_hints`: `time` (a rhythm, or the user named one twice), `event` (most chats start from the same kind of
  outside input), `watch` (the same "has X changed" question), `check` (the same check across two or more tasks).
- `rhythm`, `weekday`, `month_part`: the computed rhythm. `irregular` means no fixed beat.
- `trigger`, `input_kind`, `output_destination`, `checks`: counts from the facets, this period only.
- `patterns`, `chats`, `recurrence_quotes`: what the candidate covers, and quotes already checked.

The numbers on the card come from `loops.json`. Don't restate them in your own texts.

## 2. Decide: loop, not yet, or nothing

A candidate becomes a loop only when all six hold. If one fails, put it under `not_yet` and name what is missing;
if it is plainly not loop material, leave it out.

1. **A stable trigger.** A rhythm, the same kind of outside input in most chats, or the same question about the
   same subject.
2. **An input the loop can reach.** What it reads each run, and how: a connector, a folder, a link. Input that only
   exists in the user's head (a pep talk, their own judgement call) is not reachable.
3. **Repeatable steps.** The facets' `steps` and the pattern's chats show roughly the same steps each time.
4. **A check that can be written down.** A test a run can do on its own result: every claim has a source, figures
   trace back to the input, length and house style, nothing on the list left out, nothing sent. No check means
   `not_yet`, with "design the check first".
5. **Little judgement in the middle.** If the user decides something different each time, it is a skill or a
   prompt template, not a loop.
6. **Exceptions it can handle.** A run with missing or odd input can stop and say so, instead of guessing.

At most 3 loops: pick the ones with the clearest trigger and check, then the most occurrences.

## 3. The four kinds

- **Time-based** (`time`): the trigger is the rhythm. Name a concrete moment: "every Monday at 08:00" when the
  weekday is known, "the last workday of the month" for `end of the month`. Typical: a weekly update, a monthly report.
- **Event-based** (`event`): the trigger is the outside input (a message, a meeting, a tool's output, a new file).
  Where the platform can't react to that event, a scheduled check stands in: "every weekday at 08:00, look for new
  meeting invites for tomorrow". In coding work a Claude Code hook can react to the event itself.
- **Watch** (`watch`): a scheduled check for change on one subject. It reports only what is new, each item with its
  source, and says "nothing new" in one line or stays quiet, as the user prefers.
- **Check** (`check`): the same check across tasks becomes a checker step: a short checklist that runs on a draft
  before the user sees it. It can run on its own (every new draft in a folder gets checked), or be the `check` of
  the user's other loops and skills. Say which.

## 4. Starting level

Every loop starts at one of two levels; the renderer resets anything else to `report_only`.

- `report_only`: it tells the user what it found and changes nothing. Use it for watch and check loops, and
  whenever the result would go to other people.
- `draft_only`: it prepares the result (an email draft, a document) for the user to approve. Use it when the user
  always sends or files the result themselves.

Never suggest a loop that sends, posts, deletes, buys or changes files on its own. The build brief asks the user
what has to go right, and for how many runs, before it may do more. Put a stop rule in `done_when`: one retry at
most, and stop with a line saying what is missing when the input isn't there.

## 5. Where it can run

Checked 19-11-2026; features and plans change, so the build brief asks the user to check theirs. Suggest one to
three places in `runs_in`, the one the user already works in first (see `stats.json` features and
`aggregate.json → handoffs_chats`).

| `runs_in` | What it is | Notes |
|---|---|---|
| `claude_scheduled_task` | Scheduled tasks in Claude | All paid plans (Pro, Max, Ultra, Team, Enterprise). Runs a saved prompt on the chosen cadence with the user's connectors, skills and plugins, in the cloud; a task that needs local files or apps runs only on the computer. On Team and Enterprise, admins control access. Source: [Claude Help Center](https://support.claude.com/en/articles/13854387) |
| `claude_code_routine` | Scheduled tasks in Claude Code | Cloud tasks run without the computer; Team and Enterprise owners can turn them off for everyone. Desktop tasks run on the computer. `/loop` only lives inside an open session. Sources: [cloud](https://code.claude.com/docs/en/web-scheduled-tasks), [desktop](https://code.claude.com/docs/en/desktop-scheduled-tasks), [/loop](https://code.claude.com/docs/en/scheduled-tasks) |
| `claude_code_hook` | A Claude Code hook | Runs a command when something happens in a Claude Code session, such as before a tool runs. For event loops in coding work. Not re-checked on 19-11-2026. |
| `chatgpt_task` | ChatGPT scheduled tasks | Go, Plus, Pro, Business and Enterprise, with a limit on active tasks per plan; at most once an hour; unattended tasks may pause. Event-triggered tasks (Gmail, Slack, GitHub) on eligible plans; Enterprise admins must allow them first. Source: [OpenAI Help Center](https://help.openai.com/en/articles/10291617) |
| `copilot_scheduled_prompt` | Scheduled prompts in Microsoft 365 Copilot | In Copilot Chat, Teams and Outlook; needs a Microsoft 365 Copilot license, and admins can control them. Sources: [Microsoft Support](https://support.microsoft.com/en-us/topic/schedule-your-most-used-copilot-prompts-29dfd5fb-211a-4515-88a6-730b8074e489), [Microsoft Learn](https://learn.microsoft.com/copilot/microsoft-365/scheduled-prompts) |
| `power_automate` | A Power Automate flow | Starts on an event in Microsoft 365 (an email, a file, a Teams message). Licensing depends on the organisation. Not re-checked on 19-11-2026. |
| `own_agent` | An agent the user already runs | Only when the chats show one. |
| `manual_prompt` | Not automated yet | A saved prompt the user starts. Use it when the user's platform has no scheduler or their organisation turned it off. |

## 6. Writing a loop card

- `title`: what it delivers, in a few words ("Weekly status email draft").
- `why`: one sentence on why this is worth running on its own. Don't describe a rhythm the candidate doesn't
  show: no "every week" for an `irregular` candidate. For a watch loop the schedule is your proposal; say so.
- `trigger`, `input`: concrete, as in section 3.
- `steps`: from the chats (`seen: true`); steps you think are missing get `seen: false`, and the brief asks the user.
- `skill`: the skill it runs. `exists` only for a skill in your skill list; `build_first` when you suggest it under
  `skills`, with that skill's `name`; `none` when the steps are simple enough for the prompt itself.
- `check`, `done_when`: testable, with the stop rule from section 4.
- `output`, `you_step_in`: where the result lands, and what the user approves.
- `quotes`: one or two, from `recurrence_quotes` or the facets; verbatim, from work chats.
- `shareable`: `true` when colleagues could use it as is, without names or internal details.

## 7. Loops the user already runs, and what is not a loop yet

- `existing`: only what the chats show the user already has (they set up, fix or read a scheduled task, an agent's
  digest, a hook). Suggest one next step, usually a check or a stop rule. At most 3.
- `not_yet`: candidates that fail a test in section 2, and relays: work the user copies between tools by hand
  (`output_destination: another_tool` in several chats, or `handoffs_chats`). Say what is missing. At most 3.

## 8. Privacy

Loops come from work chats only. Never a loop, an existing loop or a `not_yet` item from a personal or mixed chat,
whatever its rhythm. The renderer refuses chats that aren't work chats.
