# Facets: what to extract from each chat

Read the digests one file at a time (`quick.txt`, then `batch_01.txt`, `batch_02.txt`, ...).
After each file, append one JSON object per chat to `facets.jsonl` and move on. Don't re-read a file.
When a later batch shows which piece of work an earlier chat served, correct that chat's line in place: never
append a second line for the same id, since `check_quotes.py` keeps the first one it reads.

## Schema (one line per chat)

```json
{"id": "a1b2c3d4", "scope": "work", "test_run": false,
 "category": "planning_admin", "task": "prepare for a meeting", "work_item": "supplier tender 2027",
 "intent": "doing", "mode": "task_iteration", "output": "prose", "outcome": "achieved",
 "summary": "Prep for a supplier meeting: background, questions, agenda and follow-up email.",
 "friction": [{"type": "generic_or_ai_sounding", "quote": "the intro reads like a template, make it sound like me"}],
 "success": ["good_first_draft"],
 "instructions": [{"kind": "style", "text": "keep it short please"}],
 "context_resupplied": ["supplier background from earlier chats"],
 "starts_from_earlier_chats": true, "start_quote": "check what we discussed about this supplier last month",
 "handoffs": [], "steps": ["read up on the supplier and earlier chats", "list essential questions", "draft an agenda", "write the follow-up email"],
 "trigger": "meeting", "input_kind": "meeting_notes", "output_destination": "message",
 "checks": ["house_style"], "recurrence": {"signal": "none", "quote": ""}, "watch_subject": "",
 "made": [{"kind": "meeting_material", "for": "self", "purpose": "plan"},
          {"kind": "message", "for": "client_or_partner", "purpose": "inform"}],
 "evidence": [], "voice": false, "notes": ""}
```

(The example shows the shape. Its content is made up.)

`id` is the 8-character id from the digest header. Every field is required; use `[]`, `false` or `""` when empty.

## Fields and allowed values

- **scope**: `work` · `personal` · `mixed` (work and private mixed) · `unclear` (empty or unreadable).
  For `personal`, write only `id`, `scope`, `category: "personal"`, `summary: "Personal topic."`, empty lists and the empty defaults (`recurrence` none, `watch_subject` "", `work_item` "", `made` []). No quotes, no details, whatever the topic. Personal chats never feed loops, even when they come back every week. Mixed and unclear chats get `"work_item": ""` and `"made": []` too.
  Edge cases: admin about the user's own job (expense claims, leave, work-related sign-ups) is `work`; negotiating
  the user's own contract, pay or role terms is `mixed`; social plans with colleagues outside work are `personal`.
- **test_run**: `true` when the chat is the user testing a prompt or skill. The digest says POSSIBLE TEST RUN when another chat opened with the same message that day: read it and decide. Set `true` for a trial of the same request (the same input, "again", comparing outputs); set `false` when it is real work that happens to open the same way, such as one prompt template used on different input. That case is evidence for a prompt template. Test runs are left out of patterns.
  Ties: when two chats on the same day open with the same input, the one the user continued is `false` and the
  dropped one `true`; when none was continued, all are `true`. A chat is also `true` when the same day shows it was
  one of a set of trial prompts for a skill or prompt, even without the same opening.
- **category**: `strategy` · `planning_admin` (meeting prep, planning, admin) · `research` (looking things up, checks, comparisons) · `writing` (emails, messages, texts, editing) · `docs_presentations` · `data_analysis` · `summarise` (summarising or analysing a pasted source) · `learning` (understanding something) · `ai_setup` (prompts, skills, agents, AI tooling) · `coding_automation` · `translation` · `personal` · `unclear`.
- **task**: a short verb phrase naming the job, reused word for word when the same job comes back: "prepare for a meeting", "write a Dutch work email", "vet packages before install", "analyse a source against strategy", "evaluate a new AI tool". Keep them general, without names or topics, so they group across chats.
- **intent** (OpenAI): `asking` (wants information or advice) · `doing` (wants something made) · `expressing` (sharing feelings or views, no task).
- **mode** (Anthropic): `directive` (hands over the task, little back-and-forth) · `feedback_loop` (relays results from elsewhere, like errors or tool output) · `task_iteration` (refines the output together) · `learning` (wants to understand) · `validation` (checks own work or a decision) · `single_question` (one message only).
- **output**: `answer` · `prose` (email, message, text) · `structured_doc` · `slides` · `table_data` · `code` · `visual` · `prompt_instructions` · `none`.
- **outcome**: `achieved` · `mostly_achieved` · `partially_achieved` · `not_achieved` · `exploratory` (thinking out loud; not a failure) · `unclear` · `single_question`.
- **friction[].type**: `misunderstood_request` · `wrong_language` · `wrong_format_length` · `wrong_tone_audience` · `generic_or_ai_sounding` · `factual_error_unsourced` (wrong or unsourced facts or numbers) · `outdated_info` (world facts out of date) · `stale_context` (built on the user's old plans or assumptions) · `context_resupplied` (user had to explain background again) · `instruction_ignored` · `refusal_overcaution` · `tool_failure` (including voice cut-offs and connectors failing) · `rework_loop` (3+ corrections on the same thing) · `lost_overview` (user loses track in a long chat) · `model_limitation`.
- **success**: `good_first_draft` · `saved_research_time` · `clarified_thinking` · `caught_error` · `reusable_artifact` · `learned`.
- **instructions[].kind**: `style` · `format` · `language` · `pacing` (order of work, "brainstorm first", "one at a time") · `procedure` (how to do the task) · `tool_choice` · `audience` · `content_rule` · `principle`. Only standing instructions that could apply again, not one-off content edits.
- **context_resupplied**: short labels for background the user had to explain or paste (no names of private people).
- **starts_from_earlier_chats**: `true` only when the chat continues a piece of work from earlier chats, a project, files or artifacts ("read up on the earlier chats", "continue where we left off", "explore the project memory for the files"). `false` for searching for an old chat, analysing the chat history as such, or borrowing tone or style from earlier chats.
- **handoffs**: `Claude Code` · `ChatGPT` · `new chat or project` · `earlier chats` · `other: <tool>` (e.g. `other: Copilot`). Only when work visibly moves between tools or chats. When pasted agent output doesn't name its tool, use `other: unknown agent`. Add `earlier chats` only when the chat explicitly reads earlier chats. The relay also shows up inside a chat, as a step ("write a prompt for the coding agent"): that is a handoff too.
- **steps**: the ordered steps the user drove, only for procedure-like work. Short, no names.
- **evidence**: extra quotes worth keeping, as `{"about": "...", "quote": "..."}`.
- **voice**: `true` when messages read as transcribed speech. Real work often hides in voice chats with vague
  titles: read the messages, not the title.

### The larger picture: work_item and made (for "Zoomed out" and "What you made")

`zoom.py` reads these two fields from work chats only. Work item names appear in the report and nowhere else.

- **work_item**: the piece of work a work chat serves, at the level a manager would put on a project list: a named
  product or project, a programme or initiative, a proposal, or a standing responsibility ("vetting dev tools before
  install"). A short noun phrase.
  - Sub-tracks of one programme (its architecture, its team design, its strategy day, one of its deliverables) are
    the same work item as the programme. When unsure between a programme and one of its tracks, pick the programme.
  - Building several of the user's own AI skills or agents is one standing work item per system they belong to
    ("own AI skills library", "agent platform"), not one per skill. Test runs of a skill get that same item.
  - A session or deliverable that touches two programmes belongs to the programme that owns it.
  - Reuse the same phrase, word for word, across all batches. Keep a running list.
  - Product, project and company names are fine. No names of private people.
  - A work chat that serves no larger piece of work (a quick one-off question) gets `"one-off"`.
- **made**: up to 3 items per work chat, each `{"kind": "", "for": "", "purpose": ""}`: things actually made in the
  chat for the user to take away or use, not things only discussed. `[]` when nothing was made (a plain answer to a
  question). In a single-question chat, where the reply isn't shown, list an item only when the request asks for a
  concrete thing.
  - `kind`, the closest of these; the form, such as a deck or a sheet, does not decide the kind:
    `message` (an email, chat message, reply or request to someone) · `meeting_material` (prep, agenda, notes,
    minutes, cheat sheet, follow-up for a meeting) · `document` (a report, memo, article, policy, manual, procedure or
    letter for others to read) · `plan_or_strategy` (a roadmap, project plan, framework, canvas, goals) ·
    `proposal_or_case` (a proposal, pitch, business case or quote) · `research_or_analysis` (a research report,
    comparison, scan, list or assessment, written up for the user to keep; a plain answer is not made) ·
    `data_or_model` (a table, budget, calculation, model or dashboard) · `design_or_visual` (a mockup, poster,
    diagram, image or image prompt) · `product_spec` (requirements, user stories, a spec, customer journeys,
    personas) · `code_or_automation` (a script, app, formula, config, skill or workflow) · `prompt_for_ai` (a prompt
    or brief for another AI or agent) · `learning_material` (an explainer, training, guide or quiz) ·
    `status_update` (a progress, portfolio or weekly update) · `template_or_checklist` (a template, checklist or
    form) · `edit_or_translation` (an existing text rewritten, translated or shortened, when that text is the output
    and does not go to a person; a polished draft that goes to someone is a `message`) · `other`.
  - `for`: `self` · `manager` · `team_or_colleagues` · `client_or_partner` · `external_other` · `another_ai`.
  - `purpose`: `decide` · `inform` · `request` · `plan` · `build` · `reference`.
  - Any other value is counted as `other`. The form and the number of versions come from the tool calls, not from
    you.

### What starts the work, and what happens to it (for loops)

These six fields let `loops.py` find work that could run on its own. Judge them from what the chat shows; when it doesn't show, use `unclear`, `none` or `unknown`.

- **trigger**, what made the user start this chat: `own_idea` (their own question, nothing outside visible) · `incoming_message` (an email, chat message or request someone sent) · `meeting` (preparing for or following up a meeting) · `new_document_or_data` (a file, report or dataset that arrived) · `tool_output` (see below) · `schedule` (a fixed moment: the weekly update, month-end, a recurring deadline) · `outside_change` (news, a release, an incident, a competitor's move) · `continuation` (picks up earlier work) · `unclear`.
- **tool_output**, for `trigger` and `input_kind` alike: only when the chat starts from output another tool or agent
  produced: Claude Code, ChatGPT or another assistant (a pasted thread counts), a scanner, a build log, an alert.
  Pasted text that clearly reads as written by an agent (a task card, a report, a brief) counts, even when nothing
  names the tool. Links to artifacts or docs from earlier Claude chats are not tool output: that is `continuation`.
  A link to a web page is `link_or_article`. A provider's notice about the world (an outage, a security advisory) is
  `outside_change`; output of the user's own tool run (a scan result, a build log) is `tool_output`.
- **input_kind**, the main thing pasted or attached: `none` · `message` · `meeting_notes` (notes, transcript or invite) · `document` · `data` (a table, export or figures) · `link_or_article` · `tool_output` · `image` · `code` · `other`.
- **output_destination**, where the result goes, when the chat says or the output makes it plain: `stays_in_chat` (an answer the user reads) · `message` (sent as an email or message) · `document` (a doc, deck or sheet) · `another_tool` (pasted into another tool or agent) · `unknown`.
- **checks**, what the user checks in Claude's output before accepting it, from explicit signals only: `sources` (asks where a claim or figure comes from) · `numbers` (re-checks figures or sums) · `house_style` (tone, voice, AI phrasing, brand style) · `language` · `length_format` · `facts` (corrects facts from their own knowledge) · `completeness` (asks for missing items) · `security` · `other`. Empty when the chat shows none.
- **recurrence**, whether the user says the work comes back: `{"signal": "cadence", "quote": "..."}` when they name a rhythm ("weekly", "every month", "this sprint's update"); `{"signal": "again", "quote": "..."}` for "again", "as usual", "same as last time", "since last time"; `{"signal": "none", "quote": ""}` otherwise. The quote follows the quote rules below; `check_quotes.py` sets the signal back to `none` if it can't find it.
- **watch_subject**: only when the chat asks whether something on a subject changed or is new over time ("any news on", "is this still safe", "what did competitors do"): a short general label, reused word for word when the same question comes back: "security news for my stack", "competitor news", "new AI model releases". No names of private people. Checking one specific item that someone or something hands over (a package list, a link, a document) is not a watch, even when it is about security or news: leave `watch_subject` empty there, and let `trigger` say where the item came from. Otherwise `""`.

## Older chats (SKILL.md step 8)

`older.jsonl` holds the chats from before the analysed period: per chat its `id`, `date`, `title` and `first`
user message, cut to about 200 characters. They feed the loop history and the span of a work item, so read the file once
and write one line per chat to `older_labels.jsonl`:

```json
{"id": "e5f6a7b8", "scope": "work", "task": "write the monthly report", "watch_subject": "",
 "work_item": "quarterly reporting"}
```

- **scope**: `work`, `personal` or `mixed`, as above. When the title and first message don't make it plain, use
  `mixed`: a chat left out costs one date, a personal chat let in breaks the privacy rule.
- **task**: work chats only. Reuse this period's task label word for word when it is the same job (see
  `facets_checked.jsonl`), else a new label by the same rules. `patterns.json` merges apply to these labels too.
- **watch_subject**: work chats only, by the rule above; reuse this period's label for the same question.
- **work_item**: work chats only, by the rule above, judged from the title and first message; reuse this period's
  phrase word for word for the same piece of work. Only its date is used: it widens that work item's span.
- Personal and mixed chats get `"task": ""`, `"watch_subject": ""` and `"work_item": ""`.

Nothing else: no quotes, no summaries, no other fields. Don't describe these chats anywhere, not in the report and
not in your replies; the report only says how many were read and over which dates.

## Quote rules

- Every `quote`, `text`, `start_quote` and `recurrence.quote` must be copied **exactly** from the user's own message in the digest (typos included), 3 to 20 words. Never quote Claude's replies.
- `check_quotes.py` drops anything it can't find, so a paraphrase is wasted.
- No quotes from personal chats. Avoid quotes that name private people or contain contact details.
- Judge satisfaction and friction only from explicit signals ("perfect", "no, that's not it", "where did you get this"). Don't infer frustration.
