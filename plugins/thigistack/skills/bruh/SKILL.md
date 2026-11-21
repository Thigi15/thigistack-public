---
name: bruh
description: Restate the last answer, or a part of it, so it is easy to understand on the first read. Use for /bruh, "explain simply", "what do you mean", "I don't get it", "wat bedoel je", "leg uit", or when the user is lost.
compatibility: Best in claude.ai; also works in Claude Code. Needs no tools.
metadata:
  best-in: claude-ai
  works-in: claude-ai claude-code
---

# Bruh

Take your last answer, or the part the user names, and make it easy to understand. Same content, plain words, no jargon, like one person explaining it to another.

When the user names a part (a quote, a term, an item number), restate only that part.

## How

1. Start with one plain sentence on what this is about: what happened, what it means, or what we are doing.
2. If the user has to do or decide something, say what, with the options. If nothing waits on them, say so.
3. Then explain it, keeping every number, option and decision.

While explaining:

- Replace anything the user can't see with what it is: IDs, earlier messages, section numbers, names from other sessions. An ID can stay in brackets.
- Explain each term they need in one line. If the term is what they asked about, say how it works and give one everyday comparison.
- Bring in no new terms.
- Give numbers their unit and time span.
- If the answer covers several separate things, say how many, then take them one at a time.
- If the user gave their own reading, first say whether it is right, then fix only the wrong part.
- Leave out process detail such as hashes, logs and test runs, unless the user needs it to act.

## Rules

- Restate first. Don't ask what the user wants clarified. If a question is still needed, ask it at the end.
- Clear comes before short. Keep the depth, and cut only what doesn't help the user understand.
- Answer in the language the user asked in. Keep a word from the other language in quotes.
- Add no opinion or advice that wasn't in the original answer.

This skill is not for shortening a draft meant for someone else. That is a normal edit request.

Inspired by `bro` from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT license); written anew, not a copy, from situations in real Claude Code and claude.ai chats (November 2026).
