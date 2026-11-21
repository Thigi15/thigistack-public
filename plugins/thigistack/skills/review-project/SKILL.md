---
name: "review-project"
description: "Reviews a claude.ai project along the way. Reads the project log first, then the project's chats, and reports where the project stands against its goal (decisions, progress, open items) and what it covered. Flags stale open items, decisions without a reason, tripwires past their date, contradictions with logged decisions, unlogged decisions and drift. Proposes log updates, instruction changes and an updated index line. Also checks the project's memory against the log, writes a steering-committee update, and pauses or closes a project with lessons learned. Use when the user asks where a project stands, wants a project review, status check, memory check or leadership update, or wants to pause, close or clean up a project, including Dutch requests like 'waar staan we', 'review het project', 'projectstatus', 'stuurgroep-update', 'projectgeheugen opschonen', 'project afronden', 'project afsluiten', 'project pauzeren'. Replies in the user's language."
compatibility: claude.ai only: reviews a claude.ai project. Needs Claude Docs and chat search.
metadata:
  best-in: claude-ai
  works-in: claude-ai
---

# Review project

Take stock of a project: what was meant to happen, what did happen, what was decided, what's open, and what has gone stale or contradictory. Then propose the updates that keep the project healthy.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included. Write log entries in the log's own language and labels.

## Principles

- **Log first, chats second.** The project log is the record; chats fill in what was never logged.
- **Say what you covered.** Chat search returns a sample, not everything. Never claim to have read every chat.
- **Separate facts from inferences.** Facts come from the log, a quoted chat or a file; label anything else as your reading of it.
- **Propose, then apply.** Log changes go into the log doc as suggestions, one card per entry, and the user accepts or rejects each card there. Without suggestions, show them in chat and apply only after a yes. Claude can't edit project instructions, so those come as a before-and-after to paste.
- **Housekeeping is not a decision.** Keep apart what follows from the log or a quoted chat (archiving a withdrawn entry, a missing source file) from what only the user can settle: a decision to log, an owner, a date, whether something happened. Never fill those in yourself: write "owner: ?" or "status: verify", and ask.

## Pick the mode

- **Status check:** log only, no search. For a quick "where are we" ("waar staan we").
- **Review** (default): log plus chats, with flags and proposals.
- **Steering committee / leadership update:** a review plus a separate version for stakeholders.
- **Pause:** a review plus a restart note.
- **Close:** a final review with lessons learned.
- **Memory check:** brings the project's memory in line with the log. For "clean up project memory", or when new chats in the project repeat outdated facts. See Memory check.

## Review procedure

1. **Find the log.** Use the link in the project instructions. If there's none, look for a doc artifact named "Project log – …" (or "Projectlog – …" in older or Dutch projects) for this project. If there is no log at all, the first deliverable is to create one (see The project log) from the instructions and what the chats show, and confirm it with the user. If the log is an index with one doc per topic (an ongoing project), review the index first, then the topic docs it lists; flag topic docs with no update past the threshold, and topics discussed in chats that have no doc.
2. **Read the log:** brief, decisions, open items, and its "updated" date. **With a repo** (the instructions have a Repo block): take the progress of the code work from the repo's task list in project knowledge (the file the Repo block names, e.g. docs/TASKS.md), not from the log. If it may be out of date, ask the user to select Sync now first. Don't flag code work as missing from the log's open items; the code, then the task list, then the log decide the state of the work. A repo without a task list: the log's open items hold the code work too.
3. **Search the project's chats,** at most about 8 searches:
   - decision language, in the languages the project uses: "decided", "we'll go with", "chose", "agreed", "besloten", "we gaan", "gekozen", "akkoord"
   - the topic of each active decision, to find contradictions
   - the topic of each open item, to find progress that was never logged
   - the most recent chats, for what's new
4. **Write the coverage line,** e.g. "7 searches, about 14 of roughly 40 chats seen; older chats about X not checked."
5. **Compare against the goal** and "done when" in the brief.
6. **Flag** (see below). If you can see the project's memory, also count the memory lines that conflict with the log, list the top 3 under Signals, and offer a Memory check for the rest.
7. **Propose** the updates (see Output), and apply the log changes only after a yes.
8. **Suggest the next review:** at the next milestone, 2–3 working days before a steering committee, or in 2–4 weeks for an active project.

## What to flag

- Open items with no update for 14 days or more (or the threshold set in the brief)
- Open items past their date, or without an owner
- Decisions without a reason or an owner
- Tripwires whose date has passed
- Chats that contradict an active decision: quote both briefly, with dates, and ask which one stands
- Decisions made in chats but never logged
- Drift: work that doesn't serve the goal or the deliverables
- Items marked "done" without evidence
- Instructions that are out of date: a changed audience, a rule that keeps being ignored, or a length above about 500 words
- Duplicate or outdated files in knowledge, such as two copies of the log
- A main log tab that has grown long (about 20 or more active decisions, or done items older than a month still listed): propose moving them to the Archive tab
- Log entries that record a status rather than a decision: propose turning them into an open item's update, or dropping them
- With a repo and a task list: log entries that the task list has overtaken, such as a decision a card has since changed, or an open item that is now a card. The card wins for the state of the work: propose superseding the decision with a new entry, or turning the open item into a pointer to the card ("see FEAT-12"), keeping its id
- Entries still marked "verify" from when the log was seeded: list them so the user can confirm, correct or drop each one

## Output (review)

Numbers written as text, no wide tables:

**Review [project] · [date] · Status 🟢 / 🟠 / 🔴**
Goal: … · Done when: …
**1. What was meant to happen, what happened:** 3–5 lines
**2. Decisions since the last review:** D-xx, one line each
**3. Open items:** X open, Y overdue, Z with no update for 14+ days, with the ones that matter named
**4. Signals ⚠️:** each flag in one line; at most about 6, the most consequential first, the rest as a count ("and 7 more, ask to see them")
**5. Proposal:**
- **Log:** laid in the log as suggestions, one card per new or changed entry. In chat, two short groups: **Housekeeping** (a count per kind) and **Needs you** (each decision, owner, date or fact only the user can give, as a question)
- **Instructions:** per change "Before: … → After: … · why: …". Write the proposed text in the language of the current instructions; if there are none, in the project's working language (English by default).
- **Index line:** the updated entry for the Projects section of "My Claude setup" (or the user's own doc by a similar name): at least status and last review
**Coverage:** the coverage line
**Next review:** when, and why then

Then say in one line that the suggestions wait in the log, to accept or reject card by card; the "updated" date is one more card. Without suggestions, ask once: "Shall I apply the log changes?" and update the log and its "updated" date after a yes. The index entry needs no question: if you can edit "My Claude setup", update the project's entry yourself in the section's own format and say so in one line; otherwise give the line to paste. If the log is a knowledge file (fallback), give the full updated log to replace the old one.

In Dutch replies, use: Statuscheck, Review, Stuurgroep / MT-update, Pauzeren, Afsluiten, Geheugencheck; Doel · Klaar wanneer; Wat zou er gebeuren, wat is er gebeurd; Besluiten sinds de vorige review; Open punten; Signalen; Voorstel; Log, Instructies (Was → Wordt), Indexregel; Dekking; Volgende review; "Zal ik de log-wijzigingen doorvoeren?"

## Memory check

Run it inside the project, where its memory is in reach.

1. **Read** the log (the anchor) and every memory line you can see for this project. Search recent chats only on topics where memory and the log disagree, or where memory has no log entry.
2. **Sort** each line: conflicts with the log or a newer chat; outdated (finished work, past dates, "currently"); shouldn't be stored (test or made-up input, sensitive details); duplicates; still fine.
3. **If a newer chat contradicts the log,** the log may be the stale one: propose the log fix first, then align memory with it.
4. **Present** conflicts first, each with a proposed fix and its evidence (D-xx, or a chat with its date); outdated lines as "still true?" questions; then duplicates; then "N lines still fine", shown only on request. Describe sensitive lines by topic; don't quote them.
5. **Apply** only what the user confirms. Change only this project's memory; list fixes for account memory separately, to run with memory-cleanup in a normal chat. If this project's memory can't be edited from here, give each fix as a sentence to say in the project ("Forget that …").

Number items as text (**1.**) and ask once: "Which of these shall I apply? Reply 'all', the numbers, or 'all except …'."

## Steering committee / leadership update

Run the review first, then write a separate version for the stakeholders:
- **Status** 🟢 / 🟠 / 🔴 with a one-sentence reason
- **Decisions needed:** first, if there are any
- **Progress** against the goal
- **Decisions taken:** at most 3
- **Top 3 risks** with what's being done about each
- **Next milestones**

In Dutch: Besluiten gevraagd, Voortgang, Genomen besluiten, Top 3 risico's, Volgende mijlpalen. No internal flags, chat references or coverage line in this version. Offer it as a doc, or as slides via a presentation skill if available. Best run 2–3 working days before the meeting, so there's time to fix what the review finds.

## Pause

Run the review, set the status to ⏸ in the brief, and add a restart note at the top of the log: "Start here:" (in Dutch: "Begin hier:") plus three lines on where it stands, what's next, and what to check first. Update the index line.

## Close

Run a final review, then:
- **Goal met?** Judge against "done when", honestly.
- **Look back**, four questions: what was supposed to happen, what happened, why the difference, what to do differently next time.
- **At most 5 lessons,** each written as an action for next time.
- **Lasting decisions** move somewhere permanent: a shared folder, or the seed for a next project.
- Status ✅ in the brief and the index line.
- **Export the log** to Markdown and keep it with the project's files (for a project with a repo: in docs/), so the record outlives the doc.
- **Archive the project, don't delete it:** deleting a project also deletes its project memory.

## The project log

Keep this format identical to the new-project skill's; change both together.

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

## Checklist (run before delivering; fix once, don't loop)

- The coverage line is there, and nothing claims full coverage
- Every flag points to a log entry, a quoted chat with its date, or a file
- Contradictions show both sides with dates
- Log changes keep IDs stable and mark superseded decisions instead of deleting them
- Instruction changes come as a before-and-after; the instructions stay under about 500 words
- The stakeholder version has no internal flags or chat references
- The index line is updated

## Not for

- Starting a project: use new-project.
- The account-wide Instructions: use account-setup.
- Choosing between options the review surfaces: use /decide, then log the result.
- Account-wide memory: use memory-cleanup in a normal chat.