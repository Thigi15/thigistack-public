---
name: "new-project"
description: "Sets up a claude.ai project so it works from the first chat, or brings an existing project onto the same setup. Checks whether a project is the right tool, asks at most 6 questions (goal and when it's done, audience and deliverables, context to bring in, sharing, confidentiality, skills), and delivers short paste-ready project instructions, a project log doc (brief, decisions, open items) that Claude keeps up to date across chats, memory and sharing settings, files to add and a project-index line. For a project with a code repository, links the log to the repo so Claude Code and claude.ai stay aligned. Use when the user wants to start, set up or restructure a project, connect a project to a repo, asks whether something should be a project, or wants project instructions, including Dutch requests like 'nieuw project', 'project opzetten', 'project inrichten', 'projectinstructies', 'moet dit een project worden', 'koppel aan de repo'. Replies in the user's language."
compatibility: claude.ai only: prepares a claude.ai project. Needs Claude Docs for the project log; chat search helps.
metadata:
  best-in: claude-ai
  works-in: claude-ai
---

# New project

Set up a claude.ai project so every chat in it starts with the right context: short instructions, one living project log, and the right settings. Then the review-project skill can keep it healthy.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included. Write the project instructions and the log in the project's working language: English by default, or the user's language when they work in another. Deliverables can be in a different language; the instructions then say so.

## Principles

- **Short instructions.** 200–350 words; never more than about 500. For each line, ask whether removing it would cause a mistake.
- **One log, not several files.** Brief, decisions and open items live in one document. Every extra file is another thing that drifts.
- **The goal goes in the instructions.** Claude doesn't see a project's name or description; only the instructions are always in context.
- **Each layer has one job.** Personal preferences (language, length, how answers look) stay in the user's account Instructions. The project only states what differs, such as deliverables in another language.
- **Prepare, the user creates.** Claude can't create a project or edit its instructions, settings or knowledge. It prepares everything (instructions, the log doc, settings, file list) and gives click-by-click steps; the user creates the project and pastes.
- **Only verified product facts.** Don't state limits (file sizes, counts, what a plan includes) unless current documentation confirms them; otherwise say the user should check.

## 1. Is a project the right tool?

Say so plainly when it isn't:
- A one-off task, or work that fits in fewer than about 3 sessions → a plain chat.
- A repeatable method with nothing to track over time → a skill.
- A shared reference collection with no decisions to track → a project without a log.
- An ongoing project with many topics (a knowledge base, a research library) → a project with an index (see Ongoing projects with many topics).
- Otherwise: a project with a log.

## 2. Where to run it

**Default: inside the new project.** The user creates an empty project, opens a chat in it and starts this skill. The instructions then go into that same project, and the first chat already lives there. From inside, account memory (unless turned off), earlier projects' log docs (found by name) and uploaded documents are all available.

**Exception: context from past chats.** Inside a project, chat search only covers that project, so a new project can't see earlier conversations. If the user wants that context, suggest running this skill in a normal chat first ("Open a normal chat and start /new-project there"), and creating the project afterwards.

**Existing project:** run it inside that project; see Existing project.

## Existing project

For a project that already has chats, files or memory. Run it inside the project: there, chat search covers exactly this project.

1. **Read what's there:** the current instructions (they're in context), the project's memory, the files in knowledge, and the project's chats (about 6–8 searches: decisions, open questions, status, the most recent chats).
2. **Ask only what's missing** from the six questions; most answers are already in the chats.
3. **Build the log** from what you found: the brief, active decisions and open items only, each with its source and date. Superseded and finished items stay out; they're in the chats. The user confirms the entries before the log is created. If a log already exists, keep it and add only what's missing.
4. **Instructions** as a before → after, with the log link, and the Repo block if there's a repo.
5. **Repo:** see Projects with a repo. The repo usually exists already, so give the CLAUDE.md section and the files to add from GitHub.
6. **Finish with a Memory check** (review-project), so the project's memory matches the new log.

## 3. Quick path (default, about 5 minutes)

1. Ask questions 1–3 in one message, with suggested answers.
2. Draft the project instructions from the template.
3. Create the project log (see Where the log lives) with the brief filled in; decisions and open items empty, or seeded.
4. Deliver (see Output).

## 4. Thorough path

For shared, long-running or leadership projects, or on request. Everything in the quick path, plus:
- Questions 4–6.
- **Seeding with context** (see below).
- A conventions block in the instructions.
- A short list of knowledge files to add, with names.
- Optional: offer /mece-tree on the goal to check the scope.

## Questions (at most 6, with suggested answers)

1. **What's the goal, and when is it done?** This becomes "done when": observable criteria, ideally with a date.
2. **Who is it for, and what will you deliver?** Audience, deliverables, and their language. Note whether slides for leadership are needed.
3. **Start fresh or bring in context?** Options: past chats, an earlier project's log, documents, a code repository, or nothing. A repository changes the setup: see Projects with a repo.
4. **Will you share it, and with whom (view or edit)?**
5. **Is it confidential, or separate from your other work?** If yes, turn "Use account memory" off.
6. **Which skills belong with it?** Suggest by fit: /decide for choices, /first-principles for assumptions and propositions, /mece-tree for structure, a presentation skill for leadership output.

Skip any question the conversation already answered.

## Seeding with context

- **Past chats** (normal chat only): search the topic and summarise into a seed with four parts: decisions already made (with dates), open questions, facts or numbers, and sources.
- **An earlier project:** take only its active decisions and open items that still apply. Superseded entries stay in the old log.
- **Account memory:** don't copy it in. It already flows into the project unless the user turns it off.
- **Documents:** the 2–6 files that will be used repeatedly, not everything.
- **Every seeded item gets a source and a date.** Anything older than about 90 days, or unconfirmed, is marked "verify". The user confirms each item before it goes in. The seed is a brief, not a transcript.

## Project instructions template (200–350 words)

Write it in the project's working language and leave out what doesn't apply:

    # Project: [name]
    Goal: [one sentence]. Done when: [observable criteria, with date].
    Audience: [who]. Deliverables: [list][, in language X if different from my default].

    ## Context
    - The project log is at [link]. Read it before saying anything about status, decisions or next steps; it takes precedence over memory.
    - Key sources: [2–4 file names] and why each matters.

    ## Conventions
    - Decisions: date · decision · why · alternatives · owner · revisit by.
    - Open items: action · owner · due · status · last update.
    - [Optional: file names as YYYY-MM-DD_topic_vN; mark old versions OLD_.]
    - [Optional: name and date every source.]

    ## Keeping the log current
    - When we decide something, propose a decision entry with the reason, in one line at the end of your answer. When an action or a /decide tripwire comes up, propose an open item.
    - When I say "wrap up": update the log with everything agreed in this chat and say what's still unresolved.
    - If a request contradicts a decision in the log, say so before acting.

In a Dutch-language project, "wrap up" becomes "afronden".

For a project with a repo, add this block after Context:

    ## Repo
    - Repo: [owner/name, or "to be created"], branch [main]. Development happens in Claude Code; this project is for the knowledge work around it.
    - In knowledge from GitHub: [files]. For progress, read [the repo's task list, e.g. docs/TASKS.md]; if it may be out of date, ask me to select Sync now.
    - Code work stays in that task list as cards. The log refers to cards by id and holds only what the business side needs.

## The project log

Keep this format identical to the review-project skill's; change both together.

    # Project log – [name]   (updated: YYYY-MM-DD)

    ## 1. Brief
    Goal · Done when · For whom · Deliverables · In scope / out of scope · Constraints · People involved · Key sources · Status: 🟢 / 🟠 / 🔴 + one line · [Optional: stale after N days, default 14]

    ## 2. Decisions (newest first)
    D-07 · 2026-11-12 · [decision]
    Why: … · Alternatives: … · Owner: … · Revisit by: [date] (tripwire: …) · Source: [chat or session, date]
    Status: active | superseded by D-09

    ## 3. Open items
    O-12 · [action] · [owner] · by [date]
    Status: open | waiting | done (evidence: …) · Last update: [date] · Source: [where it came from, date]

- **Dutch-language logs** use: Projectlog – [name] (bijgewerkt), Brief, Besluiten, Open punten; Doel · Klaar wanneer · Voor wie · Oplevering · Scope wel / niet · Randvoorwaarden · Betrokkenen · Belangrijkste bronnen; Waarom · Alternatieven · Eigenaar · Herzien vóór · Bron; actief | vervangen door; open | wacht | klaar (bewijs: …) · Laatste update.
- An existing log keeps its own language and labels; don't convert it unless the user asks.
- IDs (D-, O-) never change; superseded decisions are marked, not deleted.
- **An entry's text stays.** New facts about a decision go in a new entry that extends or supersedes it. Filling an empty field (a missing reason or owner) or settling a "verify" marker is fine once the user confirms it.
- **Archive.** At a review, superseded decisions and items done for more than about a month move to an Archive tab in the same doc, with their IDs unchanged. The main tab keeps the brief, active decisions and open items, so every chat reads only what still applies.
- A /decide decision card becomes a D-entry with its "revisit by" date and tripwire, and the tripwire also becomes an O-item with the same date.
- An item is only "done" with evidence.
- Optional sections, only when needed: Terms (new terms), Sources (research projects), Status history (steering-committee projects).
- **Layout in a doc:** one bullet per entry, its head line in bold (ID · date · decision, or ID · action · owner · by date) and its fields as sub-bullets, so it reads well on a phone; never a table. Decisions newest first, open items by due date. An existing log keeps its own layout and order: new entries copy its existing ones.

## Where the log lives

1. **Default: a doc artifact** named "Project log – [name]". Claude can find and update it from any chat. Still put its link in the instructions, so Claude never picks another project's log or creates a new one.
2. **If doc artifacts aren't available:** a Markdown file in project knowledge with a fixed name. At "wrap up", Claude gives the full updated log; the user replaces the old file and deletes it, so there is never a second copy.
3. **Optional, only if the user asks:** a file in a connected tool they can write to (SharePoint, OneDrive, Google Docs, Notion).

Project memory stays on as a safety net, never as the record.

## Ongoing projects with many topics

For a knowledge base or research library, one log doesn't fit. Use:
- **An index doc** ("[Project] – index") instead of the log: the brief, the list of topics with a one-line status and a link each, the format for a topic doc, and the project's own decisions and open items in the usual format.
- **One doc per topic** (e.g. "KB – [topic]"), each listed in the index. Before creating one, check the index so a topic never gets a second doc.
- **"Done when"** becomes "ongoing", with a review rhythm instead of an end date.
- The instructions link the index, not a single log.

## Projects with a repo

When the project includes a code repository. These steps assume the repo keeps its work items in a task list file
(below: `docs/TASKS.md`; use the repo's own file if it has another one). Without one, the log's open items hold the code
work too, and the card steps are skipped.
- **Who owns what.** Claude Code owns the development: code, the task list (task cards) and technical decisions. This project owns the knowledge work: goal, scope, stakeholders and business decisions. The log is the bridge: each side writes only what the other needs to know. From claude.ai: changes to scope, priorities and dates. From Claude Code: milestones, and technical choices that change scope, cost or timing.
- **No cards in the log.** Its open items are the non-code ones; code work is referred to by card id ("see FEAT-07").
- **Cards in another repo.** If the work items live in another repo's task list (for example skills built in one repo and released from another), name that repo and file in the Repo block, and add that file from GitHub instead.
- **What wins.** For the state of the work: the code, then docs/TASKS.md, then the log. For the goal and business decisions: the log. Memory is never the record.
- **Knowledge.** Add from GitHub (project knowledge › + › GitHub) only CLAUDE.md, docs/TASKS.md, the README and docs/, not the whole codebase, and leave out config and secret files. This works only in a private project; in a shared project, the business side learns about progress through the log. If the repo doesn't exist yet, this step comes after the repo is set up in Claude Code.
- **Instructions.** Add the Repo block (see the template).
- **CLAUDE.md.** If the user has a task-list skill in Claude Code that connects a project log, give it the log link and let it write this section. Otherwise give the user this section to add to the repo's CLAUDE.md, or to hand to Claude Code, so Claude Code reads and writes the same log:

      ## Project log
      The project log is "[log name]": [link] (a Claude Docs doc). It holds the goal, scope and business decisions; read it before changing scope or priorities. Write to it only what the business side needs: a milestone reached, or a technical choice that changes scope, cost or timing, as a D- or O-entry in the log's own format. Work items stay in [the repo's task list, e.g. docs/TASKS.md].

## Settings

- **Use account memory:** on by default. Off for confidential, client-like or unrelated projects (on the project's page, under Memory).
- **Sharing** (Team and Enterprise): "Can view" members can chat but not change anything; "Can edit" members can change instructions and knowledge. Share the log doc with the same people and check that they can open it.

## Output

Numbers written as text, no wide tables:
- **Steps:** the click-by-click order: **1.** create the project (Projects › New project; the name and description are for the user, Claude doesn't see them) **2.** paste the instructions **3.** add the files **4.** set account memory **5.** share, if needed. If you're already running inside the project, skip step 1. For an existing project instead: **1.** confirm the log entries **2.** paste the new instructions **3.** add the CLAUDE.md section and the GitHub files, if there's a repo **4.** run the Memory check.
- **Project instructions:** the block, ready to paste, with its word count. Where: open the project › Instructions.
- **Project log:** the link to the doc you created (or the file to upload, in the fallback).
- **Knowledge:** which files to add, with names.
- **Settings:** account memory on or off; who to share with and how.
- **Skills:** which ones this project uses.
- **Project index:** the project's entry in the Projects section of the user's "My Claude setup" doc (or the user's own doc by a similar name, see account-setup): name, short goal, done when, status, last review ("none yet (started [date])") and the log link; with a repo, also "repo: [owner/name]". If that doc exists and you can edit it, add the entry yourself without asking, in the section's own format (a table row if it is a table), or update the project's entry if it already has one; then say in one line that you did. Otherwise give it to paste: "[name] – [short goal] · done when: … · 🟢 · start [date] · log: [link]".
- **Repo** (only with a repo): the files to add from GitHub, and the CLAUDE.md section to paste.
- **First step:** what to start the first chat in the project with.

In Dutch replies, use: Stappen, Projectinstructies, Projectlog, Kennis, Instellingen, Skills, Projectenindex, Eerste stap.

## Checklist (run before delivering; fix once, don't loop)

- Instructions are 200–350 words and contain the goal, done when, audience, the log link and the logging rule
- No personal preferences repeated from the account Instructions
- The log has an "updated" date, and every seeded item has a source and a date
- Every manual step for the user is spelled out: paste, upload, settings, sharing
- The memory setting fits the confidentiality answer
- The project's entry is in "My Claude setup" (added or updated there, or given to paste if the doc can't be edited)
- With a repo: the Repo block is in the instructions, the CLAUDE.md section is delivered, and the log's open items hold no code cards
- Existing project: the log holds only active decisions and open items, each with a source, and the Memory check is offered at the end

## Not for

- Reviewing a running project: use review-project.
- The account-wide Instructions: use account-setup.
- CLAUDE.md for a code repository: a separate creator for Claude Code.