# Facets: what to extract from each chat

Read the digests one file at a time (`quick.txt`, then `batch_01.txt`, `batch_02.txt`, ...).
After each file, append one JSON object per chat to `facets.jsonl` and move on. Don't re-read a file.

## Schema (one line per chat)

```json
{"id": "a1b2c3d4", "scope": "work", "test_run": false,
 "category": "planning_admin", "task": "prepare for a meeting",
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
 "evidence": [], "voice": false, "notes": ""}
```

`id` is the 8-character id from the digest header. Every field is required; use `[]`, `false` or `""` when empty.

## Fields and allowed values

- **scope**: `work` · `personal` · `mixed` (work and private mixed) · `unclear` (empty or unreadable).
  For `personal`, write only `id`, `scope`, `category: "personal"`, `summary: "Personal topic."`, empty lists and the empty defaults (`recurrence` none, `watch_subject` ""). No quotes, no details, whatever the topic. Personal chats never feed loops, even when they come back every week.
- **test_run**: `true` when the chat is the user testing a prompt or skill. The digest says POSSIBLE TEST RUN when another chat opened with the same message that day: read it and decide. Set `true` for a trial of the same request (the same input, "again", comparing outputs); set `false` when it is real work that happens to open the same way, such as one prompt template used on different input. That case is evidence for a prompt template. Test runs are left out of patterns.
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
- **starts_from_earlier_chats**: `true` when the chat opens by asking Claude to read or recall earlier chats, projects or files.
- **handoffs**: `Claude Code` · `ChatGPT` · `new chat or project` · `earlier chats` · `other: <tool>` (e.g. `other: Copilot`). Only when work visibly moves between tools or chats.
- **steps**: the ordered steps the user drove, only for procedure-like work. Short, no names.
- **evidence**: extra quotes worth keeping, as `{"about": "...", "quote": "..."}`.
- **voice**: `true` when messages read as transcribed speech.

### What starts the work, and what happens to it (for loops)

These six fields let `loops.py` find work that could run on its own. Judge them from what the chat shows; when it doesn't show, use `unclear`, `none` or `unknown`.

- **trigger**, what made the user start this chat: `own_idea` (their own question, nothing outside visible) · `incoming_message` (an email, chat message or request someone sent) · `meeting` (preparing for or following up a meeting) · `new_document_or_data` (a file, report or dataset that arrived) · `tool_output` (output from another tool or agent: Claude Code, a build log, an error) · `schedule` (a fixed moment: the weekly update, month-end, a recurring deadline) · `outside_change` (news, a release, an incident, a competitor's move) · `continuation` (picks up earlier work) · `unclear`.
- **input_kind**, the main thing pasted or attached: `none` · `message` · `meeting_notes` (notes, transcript or invite) · `document` · `data` (a table, export or figures) · `link_or_article` · `tool_output` · `image` · `code` · `other`.
- **output_destination**, where the result goes, when the chat says or the output makes it plain: `stays_in_chat` (an answer the user reads) · `message` (sent as an email or message) · `document` (a doc, deck or sheet) · `another_tool` (pasted into another tool or agent) · `unknown`.
- **checks**, what the user checks in Claude's output before accepting it, from explicit signals only: `sources` (asks where a claim or figure comes from) · `numbers` (re-checks figures or sums) · `house_style` (tone, voice, AI phrasing, brand style) · `language` · `length_format` · `facts` (corrects facts from their own knowledge) · `completeness` (asks for missing items) · `security` · `other`. Empty when the chat shows none.
- **recurrence**, whether the user says the work comes back: `{"signal": "cadence", "quote": "..."}` when they name a rhythm ("weekly", "every month", "this sprint's update"); `{"signal": "again", "quote": "..."}` for "again", "as usual", "same as last time", "since last time"; `{"signal": "none", "quote": ""}` otherwise. The quote follows the quote rules below; `check_quotes.py` sets the signal back to `none` if it can't find it.
- **watch_subject**: only when the chat asks whether something on a subject changed or is new over time ("any news on", "is this still safe", "what did competitors do"): a short general label, reused word for word when the same question comes back: "security news for my stack", "competitor news", "new AI model releases". No names of private people. Checking one specific item that someone or something hands over (a package list, a link, a document) is not a watch, even when it is about security or news: leave `watch_subject` empty there, and let `trigger` say where the item came from. Otherwise `""`.

## Older chats (SKILL.md step 8)

`older.jsonl` holds the chats from before the analysed period: per chat its `id`, `date`, `title` and `first`
user message, cut to about 200 characters. They only feed the loop history, so read the file once and write one
line per chat to `older_labels.jsonl`:

```json
{"id": "e5f6a7b8", "scope": "work", "task": "write the monthly report", "watch_subject": ""}
```

- **scope**: `work`, `personal` or `mixed`, as above. When the title and first message don't make it plain, use
  `mixed`: a chat left out costs one date, a personal chat let in breaks the privacy rule.
- **task**: work chats only. Reuse this period's task label word for word when it is the same job (see
  `facets_checked.jsonl`), else a new label by the same rules. `patterns.json` merges apply to these labels too.
- **watch_subject**: work chats only, by the rule above; reuse this period's label for the same question.
- Personal and mixed chats get `"task": ""` and `"watch_subject": ""`.

Nothing else: no quotes, no summaries, no other fields. Don't describe these chats anywhere, not in the report and
not in your replies; the report only says how many were read and over which dates.

## Quote rules

- Every `quote`, `text`, `start_quote` and `recurrence.quote` must be copied **exactly** from the user's own message in the digest (typos included), 3 to 20 words. Never quote Claude's replies.
- `check_quotes.py` drops anything it can't find, so a paraphrase is wasted.
- No quotes from personal chats. Avoid quotes that name private people or contain contact details.
- Judge satisfaction and friction only from explicit signals ("perfect", "no, that's not it", "where did you get this"). Don't infer frustration.
