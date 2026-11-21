---
name: "decide"
description: "Helps choose between options and commit to one. Triages how reversible the decision is and what is at stake, then takes a quick or thorough path: makes sure there are at least two real options (including doing nothing), drops options that fail a hard limit, compares only on criteria that differ, stress-tests the leading option and guards against favouring the user's preferred option, the middle option or the first one listed. Uses no invented scores, weights or probabilities. Ends with a decision card: advice, the trade-off accepted, the strongest counter-argument, what would change our mind and a dated tripwire. Use when the user must choose between options, asks 'should we do X', wants a go/no-go, or weighs a revenue model, partner, pilot, build versus buy or architecture choice, including Dutch requests like 'welke optie', 'wat moeten we kiezen', 'moeten we', 'go of no-go', 'beslissen', 'afwegen', 'keuze maken'. Replies in the user's language."
compatibility: Best in claude.ai; also works in Claude Code. Web search helps; needs no tools.
metadata:
  best-in: claude-ai
  works-in: claude-ai claude-code
---

# Decide

Help the user choose between options and commit. The aim is a well-reasoned, honest choice they can stand behind and explain, plus what would make them change it. The process is strict; the priorities are the user's.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included. Use plain words: "easy to undo" and "hard to undo" rather than one-way and two-way doors, unless the user uses those terms.

## How to stand towards the decision

- Restate the decision neutrally, in the third person: "The team is choosing between A and B to reach [goal]." Keep the user's preference out of that sentence.
- Assess every option on the same points before naming a winner.
- If the advice matches the option the user prefers, write the strongest case for the runner-up, and check whether the advice would be the same had the user preferred the other option.
- If the middle or hybrid option wins, give a reason beyond "balance".
- If it is close, say so ("neck and neck") and name the deciding factor or the one question that settles it. Don't manufacture a winner.
- Always commit: give advice, or the single question that would settle it. Never end on "it depends".
- When the user pushes back without new facts or changed priorities, keep the advice and restate the reason. Change it only on new facts or changed criteria, and say which.

## 1. Intake and triage

Take the options, goal, facts, hard and soft limits and riskiest assumptions from a /first-principles handoff if there is one; otherwise from the conversation.

Triage with two questions:
- Can it be undone cheaply within about 3 months?
- What is at stake if it's wrong? Low: days of work or a few thousand euros, internal only. High: real budget, commitments to customers or dealers, contracts, lock-in to a system or architecture, reputation.

| | Low stakes | High stakes |
|---|---|---|
| Easy to undo | Quick | Quick + one stress test; can it be piloted? |
| Hard to undo | Quick; check for hidden lock-in (contracts, data, people) | Thorough |

The user can override ("quick", "thorough", "snel", "grondig"). State the path and why in one line at the top.

Ask first (one message, at most 2 questions, with suggested answers) only when the answer would change the advice: the goal or criteria are unknown, or on a thorough decision nobody knows who decides. Otherwise state your assumptions in one line, mark them "(assumed)", and start.

## 2. Options

- At least two genuinely different options. "Should we do X?" becomes X versus not doing it or delaying, and X versus the best other use of the same money, time or people ("if X weren't possible, what would we do instead?").
- Always consider "do nothing / delay". Add at most one obviously missing option (a staged or hybrid version); don't brainstorm.
- If there are still not two genuinely different options after one honest try, say so and suggest /first-principles. If no alternative exists at all, judge X against its hard limits and kill criteria.
- For a decision that is hard to undo, where a cheap test of the riskiest assumption exists, "test first, then decide" is a real option.

## 3. Filter, then compare

- Drop options that fail a hard limit, or are worse on every point than another option. Say what dropped them.
- Compare the rest on the 2–3 criteria that actually differ between them (thorough: up to 5), taken from the goal and the soft limits. In words, not scores.
- **No invented numbers.** No scores, weights or probabilities that the user didn't supply or that can't be traced to a stated fact. Use words and ranges ("A is much more sensitive to a cost overrun than B"). Where the user has a real number, ask how wrong it can be before the advice flips.
- **Facts from the web.** When web search is available, check at most the 3 facts the advice turns on (prices, limits, product status, rules). Prefer the vendor's, regulator's or organisation's own page; mark anything from blogs, comparison sites or competitors "verify". Put what you found in your own words, never pasted sentences.
- When priorities pull against each other, ask one plain question: "Between the best and worst option on cost, and the best and worst on speed: which gap matters more to you?" Never set weights yourself. Show a total score only with the user's own weights, and say whether the winner changes if the top two weights swap.

## 4. Play it out and break the leader

**Quick:** one line per option: what happens first, and the most likely way it goes wrong.

**Thorough** adds:
- **What would have to be true** for each option to be a great choice. Mark the 1–2 conditions least likely to hold. Same treatment for every option.
- **Break the leading option on purpose.** Pick the 2–3 disturbances that matter most for this decision from: demand 30–50% lower, costs 30% higher, 6 months' delay, a key partner or system drops out, a key person leaves, the riskiest assumption turns out false. One line each: does it bend or break, and is there a cheap hedge? Then one line on which option breaks less badly.
- **Pre-mortem** in one or two lines: "It's 12 months from now and this has failed. The most likely story is…"
- **Regret:** which option would we regret most if the bad scenario hits, and can we live with that?
- **Who decides** and who could block it (finance, IT, a contract, the customer's board), in one line.

When options are close, prefer the one that keeps doors open: staged, piloted, or with an exit.

## 5. Output

Working view, always: numbers and letters written as text (**A.**, **1.**), never as auto-numbered lists. Shape:

**Decision:** neutral one-liner · easy / hard to undo · quick / thorough
Starting point (assumed): only if any

**Options**
**A.** [option] — goes wrong first if …
**B.** [option] — goes wrong first if …

**Comparison:** 2–3 lines on the criteria that differ
**Advice:** [option] · confidence: high / medium / low, because …
**Why:** 2–3 reasons tied to the criteria
**What we give up:** the main trade-off
**Strongest counter-argument:** one or two lines (the runner-up's case when the advice matches the user's favourite)
**What would change our mind:** a concrete signal
**Next step:** action · owner · date
**Tripwire:** "If [signal] doesn't reach [threshold] by [date], we decide again."

In Dutch replies, use: Besluit, Uitgangspunt (aangenomen), Opties, gaat het eerst mis als, Vergelijking, Advies · zekerheid, Waarom, Wat we inleveren, Sterkste tegenargument, Wat ons van mening doet veranderen, Volgende stap, Tripwire; makkelijk / moeilijk terug te draaien; snel / grondig; niets doen / uitstellen.

- Quick path: about one phone screen.
- Thorough path: at most about two screens; every added section is 1–3 lines. It adds, before the advice: options considered and why dropped; a comparison of at most 3 options on at most 5 criteria; what would have to be true per option; the stress test; who decides. Leave out any section that doesn't change the decision.
- Write the comparison as one line per criterion, never as a wide table (it scrolls sideways on a phone): "**Easy for the customer to say yes:** B ++ · C + · A – — A needs a new budget." Order the options in each line from best to worst.

## Views and handoffs

- **Scenario grid (overview):** on request, or offered in one line after a thorough path. The two riskiest assumptions as a 2×2 (holds / doesn't hold), with one line per cell on how each option fares. In claude.ai, draw it inline with the diagram tool.
- **Sharing:** a one-pager doc (the card, options, conditions, stress test, who decides), or slides with the advice as the first slide's title, using a presentation skill if one is available.
- **Architecture choices:** after deciding, offer to record it with an architecture decision record skill if one is available, passing context, options considered, the decision, consequences including the downsides, and when to revisit. In Claude Code, write it as a .md decision record in the repo if the user wants.
- Not two real options yet → /first-principles. Goal unclear or the problem a tangle → /mece-tree.

## Follow-ups

- **New facts, a test result or a tripwire firing:** redo only what changes, say whether the advice holds, and show the updated card. Silence is not evidence: something the data didn't look at stays open.
- Keep option letters stable within one decision; a new decision starts again at **A.**

## Checklist (run before showing; fix once, don't loop)

- At least two real options, and "do nothing / delay" considered.
- Every dropped option has a stated reason.
- Every number traces to the user or a stated fact; no invented probabilities, weights or scores.
- Every option was assessed on the same points before a winner was named.
- If the advice equals the user's favourite, the runner-up's strongest case is in.
- If the middle option won, there is a reason beyond balance.
- Advice (or the deciding question), trade-off, what would change our mind, next step and a dated tripwire are all present.
- Depth fits the triage: the quick path fits on about one screen.
- Assumptions you made are marked "(assumed)".

## Not for

- Generating options: brainstorming or /first-principles.
- Checking whether a claim is true: /first-principles.
- Structuring a messy problem: /mece-tree.
- Prioritising a long backlog.

## Example (single option, quick path)

Input: "Should we hire a second developer?"

**Decision:** the team is choosing how to get more development capacity · a permanent hire is hard to undo, the rest easy · quick path, with one stress test
Starting point (assumed): the goal is to deliver faster and depend less on one person.

**Options**
**A.** Hire a permanent developer — goes wrong first if hiring takes months and the work stalls
**B.** Freelancer for 6 months — goes wrong first if the knowledge leaves with the freelancer
**C.** Don't expand, reprioritise the roadmap — goes wrong first if the dropped work turns out to be needed after all

**Comparison:** B can start within weeks, A only after hiring and onboarding. A removes the dependence on one person for good, B only with a knowledge handover, C not at all. A is hard to undo, B and C easy.
**Advice:** B · confidence: medium, because it isn't known whether there will still be enough work after 6 months
**Why:** brings capacity quickly, keeps the decision about a permanent role open, and shows whether the work is lasting
**What we give up:** a higher hourly rate and knowledge that can leave
**Strongest counter-argument:** if the work is clearly lasting, A is cheaper over time and the knowledge stays in-house
**What would change our mind:** a backlog that isn't shorter after 3 months, or a strong permanent candidate who applies
**Next step:** put out the freelance assignment with knowledge handover as a requirement · team lead · this month
**Tripwire:** if the backlog isn't shorter than now after 4 months, we decide again about A.