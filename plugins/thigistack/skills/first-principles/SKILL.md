---
name: "first-principles"
description: "Breaks an idea, proposition, business case or long-held belief down to what is actually true, then rebuilds it. Labels each claim by type (fact, assumption, habit, soft or hard limit) and by how much evidence exists, explains why each habit exists before challenging it, challenges only the claims the idea rests on, gives the strongest case against before its verdict, rebuilds 2–3 genuinely different options and proposes the cheapest test for the riskiest assumption. Holds its verdict under pushback unless new evidence arrives. Use when the user wants to challenge or rethink an idea or \"the way we've always done it\", check a proposition or business case, or find hidden assumptions, including Dutch requests like 'klopt dit wel', 'waarom doen we dit zo', 'wat moet waar zijn', 'aannames', 'vanaf nul', 'kritisch kijken naar', 'challenge dit', 'first principles'. Replies in the user's language."
compatibility: Best in claude.ai; also works in Claude Code. Web search helps; needs no tools.
metadata:
  best-in: claude-ai
  works-in: claude-ai claude-code
---

# First principles

Take an idea apart down to what is actually true, then build options back up from there. This skill earns its keep by pushing back honestly; it is not here to agree.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included. Use plain words in the output: no consultant jargon unless the user used it first.

## How to stand towards the idea

- Call it "the proposal", in the third person, even when the user wrote it. Never open with praise.
- Name its strongest point in one line before anything else.
- Write the strongest case against it before you settle the verdict. The verdict comes after the counter-argument in the output on purpose: decide it only once the case against is written.
- When the user pushes back without new evidence ("our shops are happy with us"), keep the labels and the verdict, say which evidence would change them, and ask for it. Change the verdict only on new evidence, and say what changed it.
- Don't kill everything: "holds" and "holds with conditions" are real verdicts.

## Quick or thorough

**Quick is the default** for a one-line idea, a belief or a habit. Go **thorough** when the input has numbers (prices, volumes, margins), runs past about 150 words, involves an investment decision, proposes a new revenue model or business case, or the user asks ("thorough", "for leadership", "grondig", "voor het MT").

If the claim is low-stakes, easy to reverse, or already backed by what people actually did, say so in a line or two and stop.

Ask one question, with suggested answers, only when there is no recognisable idea or claim, or when the goal is missing and the input could mean two very different things. Otherwise state the assumed goal at the top and start.

If the input is a tangle of more than about 8 loose claims with no clear idea, suggest structuring it with /mece-tree first. A /mece-tree branch is good input.

## Procedure

1. **Goal.** One line: what the user wants to decide or improve.
2. **Claims.** Pull 3–6 claims (thorough: up to about 10) from the user's own text, quoted or closely paraphrased. Look for hidden ones behind "will / always / must / never" (in Dutch: "gaat / altijd / moet / nooit"). A claim you infer yourself is marked "(inferred)" and starts as "not checked" unless you found a source for it. A claim the user didn't make stays (inferred), however well sourced. No generic claims that would fit any idea ("customers might not adopt it").
3. **Label** each claim with a type and an evidence level (see Labels).
4. **Why does it exist.** For every habit and soft limit, one line on the most likely reason it exists. Understand the fence before removing it.
5. **Challenge** only the 3–5 claims that carry the most weight and have the least evidence. One sharp question each: about the assumption ("what if this isn't true?"), the evidence ("what shows this?") or the consequence ("if it's true, what follows?").
6. **Rebuild** (see Rebuild).
7. **Test** the riskiest assumption (thorough: up to 3), cheapest first (see Test).
8. **Verdict and next step.** One verdict, what to keep doing while testing, and the next step. Then stop: no second round unless asked.

## Labels

**Type: could it be otherwise?** Decide in this order.
1. **Hard limit:** physics, law or regulation. Name the law or mechanism. If you can't, it is a soft limit marked "check whether this is a legal requirement".
2. **Soft limit:** policy, contract, budget, capacity, preference. Name who could change it and roughly what that would cost.
3. **Habit:** "this is how we do it / how the industry does it", with only precedent behind it.
4. **Assumption:** a belief about what customers, the market, costs or the future will do.
5. **Fact:** observable now and actually observed. Only with evidence "we have data" or better.

**Evidence: how much do we know?**
- **not checked:** gut feeling, the idea owner's conviction, or your own general knowledge
- **someone says so:** interviews, experts, sales anecdotes, surveys
- **we have data:** internal data, orders, contracts, published statistics
- **people did it:** paid, signed, ordered, used in real life

In Dutch replies, use: feit, aanname, gewoonte, zachte grens, harde grens; niet gecheckt, iemand zegt het, we hebben data, mensen deden het; (afgeleid) for (inferred).

Never give "we have data" or "people did it" to something you only know from training: write "not checked · check: [where]". Mark numbers you supply yourself as estimates. What people did beats what they say.

When web search is available, check at most the 3 claims the idea rests on most, and only where public sources can settle them (regulation, sector practice, published figures). Internal questions need internal data, so don't search for those. Put the source on the claim line in a few words. Each claim stays one or two lines, never a paragraph, also when you found a lot: give the one finding that moves its label, and leave the rest out.

Internally, note whether each claim is about wanting it (desirability), paying for it (viability) or delivering it (feasibility). Rank wanting-it claims first, unless a hard limit or the economics could kill the idea outright. Don't show these tags.

## Rebuild

- Start from: "If we set this up from scratch today, with only the facts and hard limits, what would we build?"
- **When the input claims a cost, price or time:** break it down to its floor (materials, factory hours, logistics, installation hours, sales cost, or the steps of the task) and name the 1–2 biggest gaps between the floor and the claim. A floor shows where the slack is, not how to remove it.
- **For a business case:** work back from the profit that would make it worth doing to the revenue and costs it needs, and list the assumptions that must hold for that.
- Give 2 options (thorough: 3, including one more radical than comfortable and one smallest change that keeps most of the value). Each option names the claim it breaks ("breaks: 2") and differs from the original on customer, channel, revenue model or delivery. An option that does neither is a restatement: delete it.
- Also ask the inversion: what would have to be true for the opposite to work?

## Test

Rank by weight × lack of evidence, then by how fast and cheap the test is. Cheapest first:
1. Desk or data check (hours): internal data, contracts, price lists, statistics
2. Five interviews about what people did last time, not what they would do (days)
3. Fake door or priced offer: a page, letter or quote people can act on (1–2 weeks)
4. Manual pilot with 1–3 customers (weeks)
5. Paid pilot or letter of intent (months)

Write each test as one sentence with a threshold: "We think [assumption]. We'll test this with [test] among [who]. It holds if [threshold] by [date]." In Dutch: "We denken dat … We testen dit met … bij … Het klopt als … vóór …". A test without a pass/fail line doesn't count.

## Output

Working view, always: numbers written as text (**1.**, **A.**), never as auto-numbered markdown lists, no table wider than 3 columns. Shape:

**Goal:** one line
**Strongest point:** one line

**Claims**
**1.** "[claim]" — Assumption · not checked — why it matters
**2.** "[claim]" — Habit · we have data — why it exists: …

**Strongest counter-argument:** 2–3 lines
**Verdict:** holds / holds with conditions / doesn't hold yet, with one line why

**Rebuilt**
**A.** [option] — breaks: 1
**B.** [option] — breaks: 2

**First test:** We think … We'll test this with … among … It holds if … by …
**Meanwhile:** what to keep doing while the test runs
**Next step:** choose between current, A and B

- Quick path: about one and a half phone screens.
- Thorough path: at most about two screens. It adds the ranking of all claims, the floor or profit calculation in 2–4 lines, 3 options and up to 3 tests in order.

## Views

- **Assumption map (overview).** Draw it when the user asks for a visual; after a thorough path, offer it in one line. It is a 2×2: weight on the vertical axis, evidence on the horizontal axis (little → much), and the top-left corner labelled "test first". Plot each claim by its number. In claude.ai, draw it inline with the diagram tool.
- **Whiteboard.** For a team that will work on it: the same 2×2 as four areas, one sticky note per claim with its number and a few words, marked by type with a key. Use at most four looks.
- **Sharing.** A doc for keeping or sending; one slide for leadership, using a presentation skill if one is available.

## Follow-ups

- **New evidence:** move the claim's evidence level, relabel it if needed, re-check the verdict, and show only what changed plus one line on why. Silence is not evidence: a claim the data never looked at keeps its level.
- **Pushback without evidence:** see "How to stand towards the idea".
- Keep numbering stable across turns about the same idea. A new idea in the same chat starts again at **1.** and **A.**, so its claims and options don't continue from the previous one.

## Checklist (run before showing; fix once, don't loop)

- Every claim traces to the user's text or a named fact; inferred claims are marked (inferred).
- Every fact has "we have data" or better with a nameable source; every hard limit names a law or mechanism.
- Every habit and soft limit has a "why it exists" line.
- No praise opener; the counter-argument comes before the verdict.
- Every option names what it breaks and differs on customer, channel, revenue model or delivery.
- Every test has a who and a threshold.
- One verdict, one next step, in the reply language.

## Not for

- Generating ideas from scratch: that's brainstorming.
- Structuring a messy list: /mece-tree.
- Choosing between options, pre-mortems, scenarios: /decide.

## Example (quick path)

Input: "Bike shops should stay our main channel. Is that right?"

**Goal:** decide what role local bike shops should play for our bicycles in the coming years.
**Strongest point:** shops give regional reach, a test ride, fitting and repairs close to the customer, without us investing in any of it.

**Claims**
**1.** "Bike shops should stay our main channel" — Habit · not checked — why it exists: shops brought the test ride, advice and servicing to the customer when there was no other route.
**2.** Shops deliver most of the volume and margin (inferred) — Assumption · not checked · check: revenue and margin per channel — the whole claim rests on this.
**3.** Customers want to ride a bike before they buy (inferred) — Assumption · not checked — decides whether another sales channel can work.
**4.** The shop contracts are fixed (inferred) — Soft limit · not checked — why it exists: certainty about sales and territory for both sides · who can change it: we and the shops, at the cost of renegotiating.

**Strongest counter-argument:** "main channel" mixes two questions: where the customer chooses and buys, and who fits and services the bike. If customers increasingly choose online, sales can shift while the shop stays essential for servicing.
**Verdict:** holds with conditions: as long as 2 and 3 are true, and neither has been checked.

**Rebuilt**
**A.** Shop as fitting and service partner for bikes sold online — breaks: 1 (different channel)
**B.** Shop paid per fitting and service instead of through margin on the bike — breaks: 2 (different revenue model)

**First test:** We think shops deliver most of the margin. We'll test this with a margin-per-channel report for the past year. It holds if shops deliver more than half the margin, by the next channel meeting.
**Meanwhile:** change nothing in shop policy until 2 is checked.
**Next step:** choose between current, A and B.