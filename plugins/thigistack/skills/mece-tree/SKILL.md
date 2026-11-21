---
name: "mece-tree"
description: "Turns messy input into a MECE tree the user can work down. Builds a How-tree for ideas, options, todo lists, workshop output and propositions, or a Why-tree that finds root causes of a recurring problem (complaints, service issues, a falling KPI, 5 whys, fishbone). Places every input item exactly once, names the split logic per level, flags overlaps, gaps and mixed input, and ends each branch in a next step (How) or a cause with a test (Why). Also checks whether an existing list or structure is MECE, updates a tree as evidence comes in, and draws it as a diagram or whiteboard on request. Use whenever the user shares sticky notes, a whiteboard photo, a long or messy list or a recurring problem, or asks to structure, group, cluster, categorise, prioritise or find causes, including Dutch requests like 'structureer', 'ordenen', 'clusteren', 'indelen', 'maak hier een boom van', 'waarom blijft', 'oorzaak', 'opties voor', 'is dit MECE'. Replies in the user's language."
compatibility: Best in claude.ai, which draws the tree as a diagram or whiteboard; also works in Claude Code, as Markdown with a Mermaid block. Needs no tools.
metadata:
  best-in: claude-ai
  works-in: claude-ai claude-code
---

# MECE tree

Turn messy input into a tree someone can work down: every item placed once, every split named, every end point either a next step or a cause that can be tested.

**Language.** Reply in English by default. When the user writes or replies in another language, such as Dutch, switch to it, labels included.

Avoid consultant jargon in the output unless the user used it first: write "overlap", "gap", "assumption", "cause" rather than MECE, hypothesis or exhaustive.

## 1. Pick the mode

Decide in this order and stop at the first rule that settles it.

1. **Question word.** Why / what causes / waarom → **Why-tree**. How / what can we do / options / plan / hoe → **How-tree**. "Is this MECE / is this split right / check my list" → **Check mode**.
2. **Input shape.** A recurring problem, complaints, a KPI that moved, a 5-whys chain or a fishbone → Why. A list of ideas, options, todos or sticky notes → How.
3. **Mixed input.** If a real share of the items are causes and another real share are solutions (or metrics), say so in one line. Build the Why-tree, hang each solution under the cause it addresses as a candidate fix, and use metrics as the root or as evidence. Never force causes, solutions and metrics into one level.
4. **Still unclear.** Ask one question with both options written out: "Do you want to know *why* X happens, or *how* to fix X?"

Variants:
- **A metric that moved** (first-time-right %, NPS, margin, lead time): make level 1 a formula split that adds back to the root (complaints = deliveries × complaint rate). A dependable default for any change in a metric: the measurement changed / the mix changed / the rate changed. If a change in measurement could explain the move, it gets its own branch or the first check under "Start here"; never park "the drop is real" in the assumptions. Label the levels below the formula as causes, not maths.
- **Todo list for one deliverable:** order branches by sequence and dependency rather than by category.

## 2. Ask or build

Build straight away and state your assumptions in one line ("Assumption: all complaints in 2026, all product lines"). Ask one question, with suggested answers, only when:
- there is no recognisable goal or problem ("make something of this" with a random list), or
- the scope is open in a way that changes level 1 (one product line or all? B2B or B2C? this year or always?).

## 3. Quick or thorough

**Quick is the default.** Switch to thorough when the input has more than about 25 items, when the user asks for depth ("thorough", "for leadership", "grondig"), when a Why-tree has real stakes, or when the quick check keeps failing.

### Quick path
1. **Frame.** One line with the root question and the mode.
2. **Inventory.** Number the input items internally (1…n). Merge exact duplicates and say so.
3. **Split level 1** with the tightest logic available (see Split order) and name it.
4. **Place** every item in exactly one branch. Add a missing branch only where the split logic demands it, and mark it "(new)".
5. **Check** with the checklist below and fix failures before showing anything.
6. **Show** the tree, the audit and where to start.

### Thorough path (adds to the quick path)
- Pin the scope in one line: the situation, what is going wrong or changing, and the question.
- For large inputs, cluster bottom-up first, then choose the top-down split.
- Generate 2–3 candidate level-1 splits internally. Pick the one that fits the question and would most change what people do. Mention the runner-up in one line.
- Per end point, Why: status (fact / assumption / unknown), the data that would confirm or rule it out, cheapest check first. How: next step, impact/effort (H/M/L), and an owner or open question.
- Add the placement list (item → branch) at the end, kept short.

## Split order (tightest first)

1. **Formula:** parts that add up or multiply back to the parent (revenue = volume × price).
2. **Process or sequence:** steps from start to end, e.g. the customer journey: orientation → comparison → order → payment → delivery → returns → service.
3. **Structure:** physical or organisational parts (product components, channels, departments).
4. **Opposites:** X / not X (internal / external, new / existing customers).
5. **Stakeholder:** who it concerns (customer, retailer, courier, support team).
6. **Category:** conceptual groups. Last resort; most prone to overlap.

Stock frameworks (6M, 4P, journey stages) are candidates only: rename them to fit the problem and drop empty branches. Prefer the split that would change what someone does. A split that is MECE but changes nothing (alphabetical, by weekday when nothing differs by day) is useless.

## Checklist (run before showing; fix every failure)

- **Placement:** every numbered item appears exactly once in the tree, or under "Not placed" with a reason. Count it.
- **Overlap:** for each set of siblings, try to name one real item that fits two of them. If you can, redraw the boundary or change the split.
- **Gap:** a formula split adds back to the parent; a process split covers start to end; opposites are X / not X; otherwise ask "what else could it be?". Add missing branches marked "(new)".
- **Same kind:** siblings can be named with one plural noun (causes, steps, customer groups) and sit at the same level of detail. If one sibling would fit as a child of another, move it down.
- **One logic per level:** the level's split label describes all its siblings.
- **Size:** 2–5 siblings per node; usually 3 levels, rarely 4.
- **No "Other" at level 1.** Lower down only when small and named.
- **Specific labels:** no bare "Process", "Communication", "People". Write the claim: "Courier gets the delivery slot too late".
- **End points:** Why ends in something you could measure or change, not a symptom ("customer unhappy" is a symptom). How ends in something someone could own.
- **Why-trees are never one chain:** every level has 2–4 alternatives. If the user gave a 5-whys chain, keep it as one branch and add other cause families beside it. Include at least one branch that would contradict the user's favourite explanation.

Never write "✓ MECE" as a claim. The audit lines are the proof.

## Output

There are three views. The working view below is always shown; the overview and sharing views are extras (see Views).

Working view: a nested list in chat with every number written out as text (**1.**, 1.1, 1.1.1), never as an auto-numbered markdown list: those numbers disappear when the tree is copied into Word, Teams or Miro. No code blocks, no box-drawing characters. Shape:

**[Root question]** (Why / How)
*Split: [split logic of level 1]*
Assumption: [one line, only if any]

**1. Branch** · n=… if counts exist · ⭐ if a priority
   - 1.1 End point — next step, or status + check
   - 1.2 End point (new)
**2. Branch**
   *Split: [only when this level's logic is not obvious]*
   - 2.1 …

**Audit:** one line of counts (placed / merged / not placed / added), then at most two lines on what stands out: mixed input, an overlap fixed, a solution that addresses no cause, a cause that no solution addresses. Leave those two lines out if nothing stands out.
**Start here:** the 1–3 branches likely to carry most of the effect, each with one next step. Use counts when you have them.
**Not placed:** item + reason (only if any).

- Why end points carry a status: **fact** (the input contains evidence), **assumption** or **unknown**, plus one line on what would confirm or rule it out.
- How end points carry one verb-first next step or one open question.
- Check mode: a verdict line (MECE / partly / not), each overlap and gap with a concrete example, then the corrected structure. No action layer unless asked.
- Size the answer to the input. A short How list or a check fits on about one phone screen. A Why-tree may grow beyond its input because gaps get added, but on the quick path each new branch gets at most two end points.

## Input handling

- **Photo of sticky notes, a whiteboard or a Miro export:** transcribe and number the items first and show that list briefly, flagging anything unreadable, then build the tree in the same reply.
- **25–100 items:** cluster first and show the count per branch.
- **100+ items or a file (CSV, Excel):** show levels 1–2 with counts (n and %) first and offer to expand branches. Never print 100 end points. When a code tool is available, tag each item with its branch code in a table and count with code, so the counts are exact.
- **Near-duplicates:** merge only when they say the same thing, and mention it in the audit.

## Follow-ups

Keep numbering stable across turns, so the user can say "move 7 to 2.1" or "go deeper on 3". When changing the tree, show only the changed part unless the user asks for the whole tree.

**Update with evidence.** When the user brings back data, check results or findings ("coded 20 reports: 14 with courier X"), update the tree instead of rebuilding it:
- Mark each cause the evidence touches **confirmed**, **ruled out** or **partly**, with the evidence in a few words. A status changes on evidence, not on opinion. Silence is not evidence: a cause the data never looked for (no code for it, nobody asked) stays open, marked **not measured**, and is never ruled out. When the tree explains a change, a cause only counts if it grew: ask for or suggest a baseline from before the change.
- Cut ruled-out branches but keep them in a one-line "Ruled out" list, so nobody tests them again.
- Go one level deeper where a cause is confirmed (why does courier X cause more damage?), and add causes the data reveals, marked (new).
- Pick a new "Start here".
- Show the changed branches plus one line on what changed, unless the user asks for the full tree.
- If the evidence undermines the level-1 split itself, say so and propose a new split rather than patching the old one.

How-trees work the same way, with **done**, **in progress** and **dropped**.

## Views

The working view is where the tree gets worked; the other two are for looking at it and showing it. Use whatever the environment offers and fall back to the working view when a tool is missing.

**Overview (a diagram).** Draw it inline when the user asks for a visual, diagram or overview; use a whiteboard only when they want to keep working on the tree or work on it with others. After a thorough-path tree or a tree with 3+ branches, offer it in one line ("Want this as a diagram?"); don't draw it unasked.
- Levels 1–2 only: root on top, branches side by side, end points stacked under each branch. That layout fits a phone.
- Short labels (about 20 characters); detail stays in the text.
- Show what the text can't show at a glance: which items came from the input and which were added (new: dashed outline plus a legend, never colour alone), the priority branch, and counts per branch when you have them.
- At most about 4 branches with 4 end points each. Bigger: draw level 1 with counts, then offer one diagram per branch.
- In claude.ai, draw it inline with the diagram tool; make branches tappable to go deeper when the tool supports it. The diagram never replaces the working view.

**Sharing (something others can use).** When the user wants to keep, share, present or workshop the tree:
- With a team that will edit it: a whiteboard if available, drawn as a tree, not as a slide. The root question is a block on the left, each level gets its own column to the right, every branch and end point is its own block, and an arrow runs from every parent to each of its children. Don't use sections or cards in place of branches. The title is the root question; a takeaway line only states what the evidence already shows. Mark status with at most three looks plus a key (e.g. confirmed / open / new), and keep ruled-out branches on the board, faded or dashed, instead of deleting them.
- To keep or send: a doc with root question, tree, audit and "Start here".
- For leadership: one slide with the tree at levels 1–2 and "Start here", using a presentation skill if one is available.
- In Claude Code: a .md file with the working view plus a Mermaid `flowchart TD` block of levels 1–2, which GitHub and most Markdown viewers render.
- Otherwise the working view itself: it pastes cleanly into Word, Teams and Miro.

## Not for

- Picking the best of a few options: this skill structures options, it does not choose between them.
- Building a presentation storyline.
- Debugging code.

## Example (Why-tree, quick path)

Input: "Why do complaints about items arriving broken keep coming back? Our analysis: couriers are rushed → too many stops per route → planning too tight."

**Why do complaints about items arriving broken keep coming back?** (Why)
*Split: where in the chain the damage happens*
Assumption: all damage complaints in the web shop, all product lines.

**1. Warehouse and packing**
   - 1.1 Items already leave the warehouse damaged (new) — unknown · check: sample at final packing check
   - 1.2 Packaging doesn't protect fragile items well enough (new) — assumption · check: code 20 damage reports by where the damage is
**2. Transport and sorting** ⭐
   - 2.1 Couriers are rushed by tight planning (your analysis) — assumption · check: compare damage per courier and per route
   - 2.2 Damage at the sorting hub (new) — unknown · check: damage reports per hub
**3. At the customer's home**
   - 3.1 Damage from use gets reported as delivery damage (new) — assumption · check: compare report date with delivery date
   - 3.2 Damage while unpacking (new) — unknown · check: ask when the box was opened when the damage is reported

**Audit:** your analysis followed one chain (2.1); five other possible causes added (new), spread across the chain.
**Start here:** code last month's damage reports by courier, hub and report date. That tests 2.1, 2.2 and 3.1 in one go.