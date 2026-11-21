---
name: "account-setup"
description: "Sets up and maintains how Claude works across a person's claude.ai account. Setup mode drafts a short, paste-ready Instructions block from a brief interview and evidence in past chats (repeated corrections, language switches, re-pasted context, recurring tasks), proposes memory changes and skills to turn on, and gives test prompts. Review mode checks the current Instructions and memory against recent chats and against Anthropic's latest prompting guidance, removes stale or over-cautious rules, and shows changes as a before-and-after. Use when the user wants to set up, improve, clean up or review their Claude, their Instructions or preferences, does a monthly check-in, asks what to change after a new model release, or says Claude keeps doing something they don't want, including Dutch requests like 'stel Claude voor mij in', 'mijn instructies', 'Claude beter afstellen', 'maandelijkse check', 'nieuw model, wat moet ik aanpassen', 'Claude doet steeds'. Replies in the user's language."
compatibility: claude.ai only: works on the account's Instructions, memory and past chats. Chat search, memory and web search help.
metadata:
  best-in: claude-ai
  works-in: claude-ai
---

# Account setup

Set up and keep up the always-on layer of someone's claude.ai account: a short Instructions block that Claude actually follows, a clean memory, and the right skills switched on. Then review it along the way, so the setup grows with the user and with each new model.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included. Write the Instructions block in the language the user wants Claude to use.

## Principles

- **Less is safer.** Newer models follow brief, reasoned instructions well, and over-apply long rule lists. Old cautious rules pile up and make Claude hesitant. A short setup beats a complete one.
- **Chat history is evidence, not text.** Look for patterns across chats; never copy content from them.
- **Each layer has one job.** Never put the same thing in two layers.
- **Propose, don't write.** Claude cannot change Settings, so deliver paste-ready text and say exactly where it goes. Write memory only after the user confirms each item.

## Where things go

- **Instructions** (Settings > Your Claude > Instructions; older layout: Account > Instructions for Claude): personal rules that are true in nearly every chat. Language, register, how answers should look, a pointer to skills, personal pet peeves.
- **Memory**: facts about the user and their work. Claude saves these itself; the user can view and edit them in Settings > Your Claude > Manage memory, or say "remember / forget …".
- **Skills**: procedures and frameworks. Instructions get at most a one-line pointer.
- **Project instructions**: anything that belongs to one project. That's the new-project skill's job, not this one.
- **Organisation instructions**: set by the organisation's owners and invisible to members. If any apply in this chat, don't duplicate or contradict them.
- Something that would be embarrassing to see quoted back in another chat goes nowhere.

## Pick the mode

- **Setup**: no Instructions yet, or the user asks to start over.
- **Review**: Instructions exist (you can see them in this chat), or it's a check-in, a new model has come out, Anthropic has changed its prompting guidance, or the user says Claude keeps doing something they don't want.

## Setup

### Quick path (default)

1. **Preflight.**
   - Check whether memory and chat search are on. If unclear, ask the user to look in the "+" menu of a new chat for Memory, and in Settings > Your Claude for "Search and reference chats". In some Team organisations, memory stays off until each member turns it on.
   - Read the Instructions that apply in this chat, if any.
   - List what you can see in memory about the user. If you can't see it, ask them to paste their memory topics.
2. **Scan past chats** if chat search is on and there are more than about 10 chats.
   - Run about 6–10 targeted searches (see Signals), plus recent chats.
   - Count in how many *separate* chats each pattern appears.
   - Keep a pattern only if it appears in about 3 or more chats, ideally over 2+ weeks. One-offs become questions.
   - Search is a sample, not everything. Say how many chats you looked at.
   - From a chat outside projects, the scan can't see project chats, and from inside a project it only sees that project. Say this up front. If the user does much of their work in projects, point to the thorough path (a data export) for full coverage.
   - With fewer than about 10 chats, skip the scan and say so.
3. **Draft first** from the template, using the scan and the user's role.
4. **Ask at most 4 questions**, only about what the scan couldn't settle. Use one message, multiple choice where possible (see Interview).
5. **Show what you extracted** as abstract patterns ("asked 5× for shorter answers"). Ask the user to strike anything before you finalise.
6. **Deliver** (see Output).
7. **Plan the next review** for about a month later. Offer a reminder if this environment can schedule one.

### Thorough path

For heavy users (more than about 50 chats) or on request. Use a full-history analysis if the user has one, such as a report from a usage-insights skill or a data export (Settings > Privacy > Export data), as the evidence for step 2. Then follow the quick path from step 3. Also note the 2–3 biggest recurring task clusters as candidates for projects or skills.

## Review

Run monthly for the first three months, then quarterly, on request, after a role change, and whenever a new model or new prompting guidance comes out.

1. **Read** the current Instructions, what you can see in memory, and the user's setup doc if they have one (its tests, changelog and Workspace).
2. **Scan** chats since the last review, or the last 30 days, for the Signals.
3. **Label every line** of the current Instructions:
   - **works**: no corrections against it
   - **ignored**: corrected against it in 2+ chats
   - **unused**: its situation never came up
   - **conflicts**: memory, another line or organisation instructions say otherwise
   - **outdated**: refers to a finished role, project or habit
4. **New patterns** found in about 3+ chats become candidate lines; one-offs become questions. Then check the Workspace: do the skill pointers in the Instructions and the Workspace match the skills the user has turned on? Flag skills that never came up, and tools or skills used often but missing, and propose updated Workspace lines. Also check the Projects section: flag projects with no review in about 2 months, and suggest archiving, restarting or running review-project.
5. **Model and guidance check.** If web search is available, look up Anthropic's current prompting guidance for the newest Claude models (platform.claude.com, prompt engineering) and note its date. Check each line against it. Watch for emphasis that newer models over-apply, rules the model now handles on its own, and over-prescriptive wording. Cut what the model no longer needs.
6. **Remove outdated cautions by default** ("always ask first", "never …"), unless they protect a real hard limit.
7. **Fix ignored lines at the cause.** Look for a conflicting line first (e.g. "be thorough" against "keep it short"), then make the line concrete and give its reason.
8. **Keep the budget.** Every added line replaces one or earns its place; stay within about 2,500 characters.
9. **Deliver** the before-and-after, the full new block, memory changes, 3 regression prompts and one changelog line.

## Signals to look for in past chats

Search in every language the user writes in; the Dutch terms below are for Dutch-speaking users.
- **Length:** "shorter", "too long", "more detail", "korter", "te lang", "uitgebreider"
- **Language:** "in English please", "in Dutch", "in het Nederlands", replies in a language the user didn't use
- **Format:** "no bullets", "in prose", "as a table", "as an email", "geen opsomming", "als tabel", "als mail"
- **Tone:** "less formal", "less enthusiastic", "minder formeel", "minder stijf", "je in plaats van u"
- **Wrong:** "that's wrong", "not what I asked", "klopt niet", "dat is fout", messages starting with "no," or "nee,"
- **Frustration:** "again", "I already said", "weer", "ik zei al", repeated exclamation marks. Find what was ignored.
- **Re-pasted context:** the same background text in 3+ chats. It belongs in memory or a project, not Instructions.
- **Recurring tasks:** the same kind of request 3+ times. Suggest a skill or project.
- **Framework moments:** "structure this", "help me choose", "is this assumption right", "structureer", "help me kiezen", "klopt deze aanname". Points to the thinking skills.
- **What worked:** "exactly", "perfect", "this is it", "precies", "dit is het". Keep what caused it.

## Writing rules

1. One line, one reason: "Lead with the answer, then the reasoning: I often read between meetings."
2. Say what to do, not what to avoid.
3. Calm wording: no capitals for emphasis, no stacks of "always/never". Keep "never" for real hard limits.
4. Frameworks only conditionally ("when I bring a messy problem…"), with quick questions explicitly exempt.
5. One principle instead of a list of behaviours.
6. Most important first: language and how answers start belong in the first lines.
7. No facts that will change (projects, people, deadlines): those are memory's or a project's.
8. No duplicates or conflicts with memory or organisation instructions.
9. For each line, ask: would removing it cause a mistake? If not, cut it.
10. Test in a fresh chat before trusting it.

## Interview (draft first; ask only what's missing)

1. What's your role, and who do you make most things with Claude for?
2. Which language should I reply in by default, and when not?
3. How long should answers usually be: (a) a few lines, (b) a short page, (c) I'll say each time?
4. What do you use Claude for most (2–3 things)?
5. What does Claude do that annoys you most?
6. Should I offer structure myself (a tree, a decision) when I see a messy problem, or only when you ask?
7. Here's your draft: what's wrong or missing?
8. Is what I know about you from memory still right?

A new user with no history gets questions 1–5 and 7.

## Instructions template (target 1,200–2,500 characters)

Fill in, write it in the language the user wants for their Instructions, and leave out what doesn't apply:

I'm [role] at [organisation]. I mostly make [kind of work] for [audience].

Language: reply in the language I write in; default [language]. [Optional: keep established English tech terms untranslated, because that's how we talk internally.]

How I like answers: lead with the answer or recommendation, then the reasoning: [reason]. Keep it short unless I ask for depth; [prose or lists, with reason].

When it fits: if I bring a messy problem, an assumption to test or a choice to make, offer /mece-tree, /first-principles or /decide in one line. For quick questions, just answer.

[1–3 personal lines, each with its reason.]

Include the skill pointer only for skills the user has turned on.

## Standards library (v1)

Add a line only when it fits the user, and phrase it in the language of their Instructions.

- **Lead with the answer:** "Start with the answer, recommendation or outcome; then the support. Readers decide in the first lines whether to read on."
- **What → So What → Now What:** "For recommendations, updates and analyses: what happened, what it means for the reader, what to do next. Not for quick questions."
- **Rule of three:** "When listing reasons, options or actions, prefer three strong ones over many weak ones."
- **Strong open and close:** "In longer pieces, put the key message first and restate the action at the end."
- **Right level of detail:** "For decision-makers: conclusions and implications. For people doing the work: steps and specifics."
- **Organisation conventions, for users who work for one:** "Write work deliverables in <the organisation's working language> and keep established English tech terms. When we discuss a pilot or prototype, say which stage it is in, using the organisation's own stage names. Separate what is assumed, what is stated with a source, and what people actually do." Fill in the language and stage names with the user; don't guess them.

Use at most 2–3 of these in one person's Instructions. The rest live in skills and project instructions.

## Privacy

- **Extract patterns, never instances.** Write "prefers Dutch for internal email", not the email.
- **Never carry over:** names or details of colleagues, customers, dealers or suppliers; health, family or HR matters; prices, margins, volumes, contract terms, unreleased plans; credentials or internal links; verbatim quotes.
- **Always show the strike list.** Your own privacy check is not enough on its own.
- **If a sensitive chat turns up,** mention only that one exists, not what it says. Suggest incognito chats for that kind of work, and point out that deleting a chat does not remove memory saved from it: check memory too.

## Output

Numbers written as text (**1.**), no wide tables.

**Setup** delivers:
- **Your Instructions:** the block, ready to paste, with its character count (counted with code if available, otherwise "about") and where to paste it
- **Why:** one line per line in the block, with the evidence behind it ("5 chats", "you said so")
- **Memory:** changes as sentences the user can say ("Forget that I …", "Remember that …"); write them only after a yes for each
- **Skills:** 1–3 to turn on, and where (Plugins, or "/" in a chat)
- **Tests:** 3 prompts for a fresh chat, each with what should happen
- **Next check:** a date about a month from now

**Review** delivers:
- **What changes:** per change one line, "**3.** Before: … → After: … · why: …", including lines removed and where their content went
- The full new block with its character count
- Memory, Tests and Next check as above
- **Changelog:** one dated line

In Dutch replies, use: Je instructies, Waarom, Geheugen, Skills, Testen, Volgende check, Wat verandert, Was → Wordt, Changelog; and for line labels werkt / genegeerd / ongebruikt / botst / verouderd.

Offer to keep a **"My Claude setup"** doc (the user may already have one under a similar name or in their own language; look for it first and keep it). It is the version history and map that the next review reads:
- **Instructions:** the current block and its date
- **Changelog:** one dated line per change
- **Tests:** the user's test prompts
- **Workspace** (about 10–15 lines): which tool is for what (e.g. claude.ai for thinking and writing, Claude Code for building, agents elsewhere); the user's skills, each with when to use it; where skills and files live; and a few working agreements the user stated. Only what the user confirms; no names, customers or confidential details.
- **Projects:** one line per project: name, short goal, done when, status (🟢 / 🟠 / 🔴 / ⏸ / ✅), last review, and a link to its project log. The new-project skill adds a line and review-project updates it; this skill only flags lines that have gone quiet.

In setup, draft the Workspace from what the user said and the skills you can see, and let them correct it. Start Projects empty, or with the user's active projects if they list them. Use a doc artifact if available, otherwise a text file the user keeps.

## Standard test prompts

Pick the 3 that fit, adapted to the user:
- a quick factual question: it should just answer
- a messy brain dump: it should offer structure in one line
- a choice between options: it should offer /decide, or decide clearly
- an email in the user's main language: right language, register and length
- a technical question in the other language: replies in that language

To see the Instructions' effect without memory, run one test with memory off (the "+" menu, before the first message).

## Checklist (run before delivering; fix once, don't loop)

- About 2,500 characters or less (warn above 3,000), with the count shown
- Language and how answers start are in the first lines
- Every framework line is conditional, with quick questions exempt
- Each non-obvious line has a reason; no capitals for emphasis
- No names, prices, projects or dated facts
- No duplicates or conflicts with memory or organisation instructions
- Every line from chat history is backed by about 3+ chats, or the user said it
- Paste location given; memory changes as separate sentences; skills listed; 3 test prompts
- The strike list was shown

## Not for

- Setting up a project: use the new-project skill.
- CLAUDE.md for Claude Code: a separate creator.
- A full memory cleanup: use memory-cleanup. This skill only proposes the memory changes its own setup or review turns up, and in a monthly check-in it can suggest running memory-cleanup next.
- Organisation instructions: those belong to the organisation's owners.
- Styles: being replaced by skills. If the user has a migrated /name-style skill, review lists it and either keeps it or folds it into the Instructions.

## Example (review, excerpt)

**What changes**
**2.** Before: "Always use What → So What → Now What." → After: "For advice and updates: what's going on, what it means, what the next step is. For quick questions, just answer." · why: applied to quick questions in 5 chats, and you said "just answer" twice
**5.** New: "Emails in Dutch, informal (je/jij), unless the recipient is external." · why: in 6 chats you asked for Dutch
**7.** Removed: "Always ask first before making anything." · why: an old caution that makes newer models hesitant; no chat needed it