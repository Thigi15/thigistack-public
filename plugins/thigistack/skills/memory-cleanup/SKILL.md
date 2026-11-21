---
name: "memory-cleanup"
description: "Cleans up what Claude remembers about the user across their claude.ai account. Reads account memory and the memory of projects that share it, checks it against recent chats, project logs and what the user says, and sorts every line into conflicts, outdated, shouldn't be stored (test input, sensitive details), duplicates and still fine. Shows problems first, each with evidence and a proposed fix, and changes memory only after the user confirms. Use when the user wants to clean up, check or correct Claude's memory, says Claude keeps bringing up outdated or wrong facts, has run test chats, does a monthly check-in, or wants to review what Claude knows about them, including Dutch requests like 'geheugen opschonen', 'klopt mijn geheugen nog', 'wat weet je over mij', 'Claude onthoudt verkeerde dingen', 'vergeet dit'. Replies in the user's language."
compatibility: "claude.ai only: works on the account's memory. Needs memory and chat search."
metadata:
  best-in: claude-ai
  works-in: claude-ai
---

# Memory cleanup

Bring what Claude remembers in line with what is true now, so new chats don't repeat outdated, wrong or test facts. Memory is written chat by chat and nothing reconciles it, so old and new states end up side by side.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included. Keep each memory file's own language when you edit it.

## Principles

- **The user decides.** Propose; change only what the user confirms. A removed line is removed, not softened into "used to …".
- **Evidence per line.** A dated chat, a project log entry (D-04), the user's setup doc, or "not mentioned since [date]". No evidence, no proposed change: ask instead.
- **Problems first.** Count the lines that are fine; don't walk through them.
- **No new facts.** Add only corrections the user states during the cleanup.
- **Describe sensitive lines by topic** ("a health detail in people/x"), never quote them back.

## Where to run it

- **A normal chat** (outside projects) sees account memory and the memory of projects that share memory with the account. Run it there.
- **Projects with "Use account memory" turned off** can't be seen from a normal chat. Say which ones are out of reach, and point to review-project's Memory check inside each of them.
- **Memory off or paused:** say so and stop. On Team and Enterprise plans, memory may be off until the member turns it on.
- **Older single-summary memory** (some Team and Enterprise organisations): work from the summary the user pastes or you can see, and deliver a cleaned version to paste in Settings > Your Claude > Manage memory.

## Scope

- **Default:** account memory.
- **Projects:** when the user asks, or for a full cleanup. Then one project at a time, the most active first, using its log as the anchor where it has one.

## Procedure

1. **Check reach.** Is memory on? What can you see? Name what's out of reach.
2. **Read** the memory files in scope. For a large store, work file by file and keep a running list.
3. **Gather evidence.** Run about 6–10 chat searches on what changes most: roles, projects and their status, people, tools, dates and words like "currently". Read project logs and the user's "My Claude setup" doc if they exist.
4. **Sort every line:**
   - **Conflict:** contradicts a newer chat, a log entry, another memory line or what the user says now.
   - **Outdated:** finished work, past dates, "currently" or "this week", roles or projects that ended.
   - **Shouldn't be stored:** input from test chats, made-up examples, sensitive details, or instructions that would make Claude less honest.
   - **Duplicate:** the same fact in several files, or a fact filed in the wrong file. A memory line that repeats the account Instructions is not a duplicate to remove: memory also reaches Claude Code, which doesn't read the claude.ai Instructions.
   - **Fine.**
5. **Present** (see Output) and ask once which to apply.
6. **Apply** what the user confirms (see Applying changes), then report one line per file changed.
7. **Close** with the next cleanup (about monthly, alongside the account-setup review) and one tip: run tests and throwaway experiments in incognito chats, because deleting a chat does not remove memory saved from it.

## Output

Numbers written as text, no wide tables, phone-friendly:

**Memory cleanup · [date]**
Seen: [N] account files[, projects: …] · Out of reach: [projects kept separate, if any]

**Conflicts**
**1.** [file] "[line, shortened]" → [fix] · evidence: [chat of 12 Nov / D-04 / you said]

**Outdated**
**4.** [file] "[line, shortened]" → still true? If not: remove / update to "…" · evidence: not mentioned since [date]

**Shouldn't be stored**
**6.** [file] [topic only] → remove · why: test chat / sensitive

**Duplicates**
**8.** [files] → keep in [file], remove from [file]

**Still fine:** [N] lines (ask to see them)

Then ask: "Which of these shall I apply? Reply 'all', the numbers, or 'all except …'." "Still true?" items need an answer before you change them.

In Dutch replies, use: Geheugen opschonen, Gezien, Buiten bereik, Conflicten, Verouderd, Hoort er niet in, Dubbel, Klopt nog, "Welke zal ik doorvoeren?".

## Applying changes

- **With memory tools:** edit or remove the exact line and keep the file's format, tags and other lines. If a change makes a file's description wrong, fix the description too. Don't rewrite files for style.
- **Without memory tools, or on the older summary:** give each change as a sentence the user can say ("Forget that …", "Remember that …"), or the cleaned summary to paste.
- **A project memory edit that doesn't go through from here:** list it as a fix to run inside that project.
- **Never** delete a whole file or reset memory unless the user asks for exactly that.

## Checklist (run before showing; fix once, don't loop)

- Every proposed change has evidence.
- Conflicts and outdated lines come first; fine lines are only counted.
- Sensitive lines are described by topic, not quoted.
- Out-of-reach memory is named.
- Nothing changes without a yes, and "still true?" items are answered first.

## Not for

- Instructions and preferences: account-setup.
- One project's memory against its log: review-project, Memory check.
- Claude Code memory and CLAUDE.md files.