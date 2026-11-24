---
name: vc-competitive-landscape
description: Helps a founder build the competition map and slide before a VC builds one about them. From the competitors the founder names, each fact with its source, it places each at four levels (direct, indirect, adjacent, and substitutes, doing nothing included) with the problem each solves, proposes three to five positioning axes with 1-to-5 anchors stated up front, and has the founder place every company with evidence; it suggests no placement and adds nothing into a score. It writes the substitutes story, a why customers pick us line per competitor and the answer to what if the big platform builds this, drafts the competition slide as a table and a 2x2, and runs an adversarial review where independent lenses attack the map and a refute pass drops what the founder's material answers. Use when a founder says build our competition slide, map our competitors, our competition slide is a logo grid, what if a big platform builds this, or who do we really compete with. Looks nothing up. Not investment advice.
---

# VC competitive landscape

Helps a founder build, before the first outside meeting, the competition map a partner is likely to draw about the
company anyway. It works only from what the founder knows: the competitors the founder names, each fact with its source
or marked unverified. It places each competitor at one of four levels with the problem it solves, proposes the axes
buyers choose on with their anchors stated before anything is placed, and leaves every placement to the founder. From
the founder's own material it writes the substitutes story, a "why customers pick us" line per competitor and the
answer to "what if the big platform builds this?", and drafts the competition slide as a table and a 2x2. Independent
lenses then attack the draft, and a refute pass drops every objection the founder's material answers.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
names a firm the map fits, never names a competitor or a platform itself, never adds a fact about a competitor that the
founder did not give, looks nothing up, places no company on an axis, and adds no placements into a score.

## When to use it

- "Build our competition slide." "Map our competitors." "Our competition slide is a logo grid." "What if a big
  platform builds this?" "Who do we really compete with?" "How do I answer 'why won't they just copy you'?"
- Pasted material: the founder's list of competitors with notes and sources, the current competition slide, the
  product and buyer description, notes from deals won and lost, customer interview notes. Any of these may come as a
  file the agent can read in this session.
- Hand off:
  - The whole deck, slide by slide: the vc-deck-review skill. Its competition check reads the slide this skill drafts.
  - Each claim's evidence, a competitor fact among them, and figures that disagree across documents: the
    vc-claims-check skill (preview).
  - Messaging (the one-liner, the story and the say-and-avoid list): the vc-positioning skill (preview).
  - The market's size, built bottom-up: the vc-market-sizing skill (preview).
  - The product decisions behind a difference, and what was said no to: the vc-taste-check skill (preview).
  - Rehearsing the partner meeting, where "what if they copy you?" gets asked: the vc-partner-meeting skill (preview).
  - A pass that gave competition as its reason: the vc-pass-debrief skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess, and never offer a competitor's name to fill
in. When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and list
what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what was read
from each. A place you could not read (a slide that is only a picture, a page whose text did not come out, a file that
opened only in part) is listed as not read and asked for, never filled in from its title or the places around it, and a
figure is never read off a chart or a picture. Ask only for what you could not read and what the file does not show
(speaker notes, the figures behind a chart, an input below that it leaves out), and never ask the founder to paste what
you already read.

1. **The competitors,** as the founder names them: for each, what it does and for whom, in the founder's words, and
   where each fact comes from (the competitor's own public material the founder read, a customer's words, a deal won or
   lost, a demo the founder saw), or "unverified" when the founder has no source.
2. **The product and the buyer:** what the product does, who pays for it, who uses it, and the job they buy it for.
3. **What buyers do today without buying a product for this:** by hand, a person or an outside service, or living
   with the problem, with the founder's evidence (interviews, deals lost to doing nothing).
4. **Why customers pick the product,** as the founder says it, with what shows it: a deal won against a competitor, a
   customer who switched, a customer's own words.
5. **The platform the founder worries about:** the larger product the buyer already uses that could add this, as the
   founder names it, the founder's view of why it has not, and what the company would do if it did.
6. **The current competition slide,** word for word, if there is one.
7. **Axes the founder already uses,** if any, each with what its ends mean, and the founder's placements on them.

A missing input does not stop the work. It becomes a named ask in the answer, never a plausible competitor, fact or
placement. With no competitor named at all, name none: list the four levels as open asks, propose no axes, draft no
slide, ask for the inputs in one message, and stop.

## The four levels

The grouping is the pack's own, unverified: the one the vc-deck-review and vc-claims-check skills use, with adjacent
split into three kinds and doing nothing widened into substitutes. Every competitor the founder names goes at exactly
one level, the one a buyer would compare it at.

| Level       | What it covers                                                                                                                                                                                   | The buyer's question                     |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------- |
| Direct      | A product that does the same job for the same kind of buyer, even one aimed at bigger or smaller buyers                                                                                          | Which products would I put side by side? |
| Indirect    | A different kind of product that meets the same need for the same buyer                                                                                                                          | What else could I buy for this need?     |
| Adjacent    | One of three kinds: a company with the same technology aimed at another use; one that sells something else to the same buyer; a platform the buyer already uses that could add this as a feature | Who could move into this?                |
| Substitutes | What the buyer does without buying a product for this: by hand (spreadsheets, email, phone calls), a person or an outside service, or doing nothing and living with the problem                  | What do I do if I buy nothing?           |

A level is not an axis placement. The skill proposes each competitor's level from the founder's own description,
quoting the line that decides it, and the founder may move it. When the description does not say what the competitor
does or for whom, its level is an open ask (`[who buys this competitor's product, and for what]`), never a guess. The
problem each competitor solves is the founder's words, quoted, or a bracketed ask. The skill names no competitor itself:
an empty level is a bracketed ask (`[what your buyers do today if they buy nothing]`, `[the tool your buyer already uses
that could add this]`), never a name, not even one the agent has heard of.

## Competitor facts

- **Only the founder's facts.** Every fact about a competitor (what it does, for whom, its price, its customers, its
  weak spots) comes from the founder, quoted, with its source as the founder gives it, or marked unverified. The agent
  adds nothing about a company it has heard of: no feature, price, funding, customer, headcount or plan, and no
  correction of the founder's facts from what it knows. A fact the founder may want to check goes to the open asks.
- **Unverified is a label, not a flaw.** A fact marked unverified stays on the map with its label. The slide shows it
  only with that label, or leaves it off. It never answers an objection that asks for evidence: it shows what the
  founder believes, not what a partner can check.
- **No running a competitor down.** A line about a competitor's weakness carries the founder's source, or it stays off
  the slide.
- **Figures as stated.** A competitor's price, a customer count, time saved: each is quoted as the founder gave it,
  never computed, converted or rounded.

## Axes

Axes are what buyers choose between products on. The skill proposes three to five, or checks the ones the founder
gives and proposes only what is missing to reach three, never more than five in all. Each axis:

- **comes from the founder's material:** a line showing buyers choose on it (a customer's words, a deal won or lost,
  the founder's buyer description), quoted; an axis with no such line is marked "buyer evidence: none given", and the
  line becomes an open ask;
- **is neutral:** named as a quality a buyer weighs ("time to go live"), never after the founder's own feature or
  description ("built for small firms" describes the company; it is not an axis), so a competitor could top it;
- **has anchors stated up front, before any company is placed:** what a 1, a 3 and a 5 mean, each something a buyer
  could observe ("1: the vendor's engineer sets it up; 3: the buyer's IT team sets it up; 5: the buyer sets it up
  alone"); an axis the founder gives without anchors gets proposed anchors for the founder to confirm;
- **has the same halves:** on every axis, 1 and 2 are the low half, 4 and 5 the high half, and 3 sits on the line.
  Say so beside the anchors; the 2x2 follows these halves and nothing else.

The founder places every company, their own included, on every axis, with the evidence for each placement (its
source, or "unverified"). The skill:

- suggests no placement, fills no cell and never changes one; a cell the founder leaves empty stays "not placed";
- adds nothing up: no total, average, weighted score or rank across axes, and no "winner";
- flags, as patterns below, the company at 5 on every axis, every competitor in the low half on every axis, and an
  axis whose anchors fit the founder's own product alone.

Until the founder has placed every company on the two axes chosen for the 2x2, draw no 2x2 and draft no slide. Give
the levels, the axes with their anchors and halves, and the empty placement table; draft the substitutes story, the
"why customers pick us" lines and the platform-risk answer; ask for the placements and every other open input in one
message; and stop. The adversarial review runs once, on the full draft, when the placements come back.

## The substitutes story

How buyers manage today without a product is often the alternative a seed company meets most (this skill's own
judgment, unverified). One short paragraph from the founder's material: what buyers do today without buying a product,
what it costs them in the founder's words, and why some have switched, with the founder's evidence. Every figure is
quoted as stated, and a gap is a bracketed ask (`[what a customer gave up when they switched]`).

## Why customers pick us

One line per competitor, in the founder's voice: "Against [competitor], customers pick us because [the founder's
reason], as [what shows it]." The reason and the evidence are the founder's, quoted; with no evidence the line ends
with a bracketed ask (`[a deal won against this competitor, or a customer's words]`). No line says "better", "faster"
or "cheaper" without the founder's figure or source, and no line runs a competitor down with a fact the founder did not
give. Each substitute gets a line too: "Instead of [the substitute], customers pick us because ...".

## The platform-risk answer

"What if the big platform builds this?" is a question a partner is likely to ask (unverified). The answer is about the
platform the founder names, never one the skill picks, and has three parts, each a line from the founder's material or
a bracketed ask:

1. **Why it has not:** the founder's reasons the platform has not built this, in the founder's words, marked as the
   founder's view. The skill knows nothing of any company's plans and claims nothing about them.
2. **What a feature would lack:** what the company has that a platform's added feature would not (a workflow, a buyer,
   data, a channel), from the founder's facts, with what shows it.
3. **If it does:** what the company would do, in the founder's words.

Never predict what a named company will do, never write that it "will not" or "cannot" build something, and never
present the founder's view as a fact about the platform. With no platform named, ask which larger product the buyer
already uses; never name one.

## The competition slide

A draft in the founder's words, for the founder to edit:

- **Headline:** one line saying why customers pick the product, from the founder's own lines; never a bare
  "Competitive landscape" and never "no competitors".
- **Table:** one row per competitor, grouped by level, substitutes included: Level, Competitor (as the founder names
  it), The problem it solves, Why customers pick us. Only the founder's facts; an unverified fact carries its label or
  stays off.
- **2x2:** the two axes the founder picks. Offer the two with the strongest buyer evidence, quoting it, never the two
  that put the company alone in a corner. Draw it as a text grid, the first axis across and the second up, split by the
  halves: each company in the quadrant its two placements give, a company with a 3 on either axis listed on the line
  between quadrants, and each quadrant labelled with the anchors' words. A company missing a placement on either axis
  is listed under the grid as "not placed", never drawn.
- **Speaker note:** the platform-risk answer, for the question a partner is likely to ask.

## Patterns a partner is likely to discount

Signals, not rules: a founder may have a reason. Flag, quote the line, explain, and let them decide. Every row is this
skill's own judgment, unverified, except the first, which the vc-claims-check skill's discount table also lists.

| Pattern                                                                      | What a partner is likely to hear                               | Fix                                                                            |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| "No competitors", "nobody else does this", "the only company that"           | The need is not real, or the founder has not looked            | What buyers use today at all four levels, substitutes included                 |
| A grid of logos with no reason customers pick the company                    | A list, not an answer                                          | One "why customers pick us" line per competitor, with what shows it            |
| A 2x2 with the company alone in the best corner                              | A position, not a reason; the axes may have been picked for it | Axes buyers choose on, with their evidence, and the reason customers pick you  |
| The company at 5 on every axis, or every competitor in the low half          | Placements nobody could check                                  | Each placement with its evidence; a weak spot owned reads as judgment          |
| An axis with no anchors ("better", "easier", "more modern")                  | Nothing a partner could check                                  | Anchors a buyer could observe at 1, 3 and 5                                    |
| An axis named after the company's own feature or description                 | Built so only the company can top it                           | A quality buyers weigh that a competitor could top                             |
| Only direct competitors; substitutes or doing nothing left out               | The founder has not looked at what buyers do today             | The substitutes level, with the founder's evidence                             |
| A competitor's weakness with no source ("their product is outdated")         | Runs a competitor down; a partner may know them                | The founder's source, or leave it off                                          |
| "Too small for them to bother", "they will never build this", with no reason | A guess about another company's plans                          | The founder's reasons, as their view, and what the company does if it is built |
| The company's plans set beside competitors' shipped products                 | A roadmap compared with a product                              | Compare what exists today; plans labelled as plans                             |

## Steps

In the turn the review runs, without a subagent tool, run Stage A of the adversarial review first, before step 1, as
"How to run the lenses" says, so the lenses do not anchor on the map; step 8 then starts at the quote check.

1. **Quote first.** List every competitor and every fact the founder gives about it, word for word, numbered C1, C2
   and so on, each with its source as given or "unverified". Add no competitor and no fact.
2. **Place each competitor at a level** (The four levels), quoting the line that decides it, with the problem it
   solves. Each empty level becomes a bracketed ask.
3. **Axes.** Check the founder's axes and propose the rest (Axes), each with its buyer-evidence line, its anchors and
   its halves.
4. **Placements.** Record the founder's placements as given, each with its evidence; never fill a cell. With any
   company not placed on the two 2x2 axes, stop as Axes says.
5. **Draft the substitutes story, the "why customers pick us" lines and the platform-risk answer** from the founder's
   material, every gap a bracketed ask.
6. **Draft the slide** (The competition slide).
7. **Scan for patterns** in the founder's material and the draft. For each hit: quote the line, name the pattern, say
   what a partner is likely to hear, and give the fix using only the founder's facts, or a bracketed ask.
8. **Run the adversarial review** (next section): attack, check the quotes, refute, rank. Revise the draft for every
   survivor.
9. **Check before answering.** Every competitor, fact and reason in the answer appears in the founder's material, with
   its source or its unverified label; every placement is the founder's; no total, average or rank of placements
   appears; no competitor or platform is named that the founder did not name; every surviving objection quotes a line
   that is in the material word for word; no sentence speaks as an investor, imitates a named person or names a firm.
   Never work out how two of the founder's figures relate (a difference, a sum, a ratio or multiple, a share left over,
   "doubled") in a rewrite, a line or a table cell unless the founder's material states it or a tool returned it; quote
   both figures as stated instead ("from 2,000 to 4,500", never "more than doubled").

## Adversarial review

The map says where everyone sits; this review says what a partner is likely to push on. Independent lenses attack the
founder's material and the draft, a second pass judges each objection using only the founder's material, and only the
objections that material does not answer reach the founder, who sees both what survived and what was tested and fell.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people: none is a named investor, firm
or author, and none speaks in the first person as an investor.

| Lens                      | What it tests                                                                                                                         |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Coverage                  | Whether all four levels are on the map, substitutes and doing nothing included, and whether the alternatives a buyer weighs are there |
| Honest axes               | Whether each axis is one buyers choose on, its anchors are observable, and each placement carries evidence                            |
| Why customers pick us     | Whether each line rests on what the founder's evidence shows (a deal won, a switch, a customer's words), not a feature claimed        |
| Platform risk             | Whether the answer says why the platform has not built this, what a feature would lack, and what the company does if it is built      |
| Substitutes and switching | Whether the substitutes story shows what managing today costs the buyer and why some have switched                                    |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to push on
  this because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, not even about a competitor or platform you have heard of, and do no arithmetic.
- Return at most three objections, strongest first. For each: the founder's line it is about, quoted word for word;
  why a partner is likely to read that line as a weakness in the map; and how much it hurts (ends the meeting, weakens
  it, or minor).
- A reason you cannot tie to a line the founder wrote is not an objection. List it apart as a gap, worded as a
  question to the founder.
- Do not judge whether another line of the material answers an objection: raise it anyway, however short the
  material, and the refute pass decides. Return "nothing found" only when no line of the material gives this lens an
  objection worth a partner's time.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the lenses
as parallel subagents, however short the material. Give each one only the founder's material and its lens brief, the
material verbatim (the founder's facts, axes, placements and the lines the founder gave for the draft): not this
skill's other sections, not the patterns, not another lens's output. Without a subagent tool, run Stage A first,
before step 1: run the lenses one after another, write each lens's objections down in full before reading the next
lens's brief, and never revise an earlier list. Lenses run this way are less independent than subagents, and the same
agent then judges them in Stage B, so the answer says so.

### Check the quotes

Before Stage B, check every objection's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same objection about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each objection gets its own refute pass, which decides, using only the founder's material, whether that material
answers the objection. The pass is a judge, not the founder's advocate. With a subagent tool, launch one subagent per
objection in a single message; never put two objections in one subagent. Give each the founder's material, that one
objection, the Pattern column of the patterns table above, and everything from "The refute brief:" to the end of this
stage, and nothing else; without one, take the objections one at a time and decide each against the same brief before
reading the next.

**Lean mode,** the one exception: with more than eight objections after the quote check, the refute pass may instead run
one subagent per lens, all in a single message. Each gets what a one-objection subagent gets, but with every objection
from its lens (one that two lenses raised goes to one of them only; one that no lens raised gets a subagent of its own),
and with this instruction, word for word: "Apply the brief to each objection as if it were the only one you were given.
Return one verdict for each, with its own quote where the verdict needs one. Never let one objection, its verdict or its
answering line decide another." Any objection that comes back without a verdict of its own stays Kept. The answer then
says the refute pass ran per lens, which is less independent than one subagent per objection, and that the founder may
ask for the full pass, one subagent per objection.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third person;
  you are not an investor and do not speak as one, named or not.
- Use only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic. A claim about a competitor or a platform that the founder's material does not
  make is an outside fact, however well known the company.
- How a partner is likely to read a line is not an outside fact. An objection that an axis was picked to flatter the
  company, or that a logo grid gives no reason to pick it, rests on that reading: judge whether the material answers it.
- A fact the founder marks unverified never answers an objection that asks for evidence: it shows what the founder
  believes, not what a partner can check.
- A line that itself matches a pattern in the list you were given never answers an objection.
- Return one verdict from the three below, with the founder's line quoted word for word where the verdict needs one.
  When you cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the material other than the objected line supplies what the objection says is
  missing: the level, the evidence, the reason customers pick the company, the platform answer's part, or the cost of
  managing today. Quote the founder's line that answers it, and say whether it should move onto the slide, where a
  partner will see it.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact about the company, its market or its competitors.
- **Kept:** neither holds. When the founder's best answer would need something the material does not contain, the
  objection stays and that something becomes the evidence to add, as a bracketed ask.

The refute pass invents nothing on the founder's behalf: no competitor, fact, placement, reason or plan the founder did
not give. When it cannot decide, the objection is kept.

After the passes, check every answering line the same way as the objections' quotes: an answering line that is not in
the material word for word does not drop the objection, which stays kept, and neither does one that is the objected
line itself, one marked unverified that is offered as evidence, or one that matches a pattern in the patterns table.

### Rank what survives

Order the kept objections in three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**. Within
a tier, an objection raised by more than one lens comes first. The tier is a judgment: give no percentages and no
score. For each survivor write:

- the founder's line, quoted word for word;
- why a partner is likely to read it that way, in one or two plain sentences;
- a concrete fix that uses only the founder's facts, or the evidence to add, as a bracketed ask.

**Where the survivors go.** The top three become the biggest issues at the head of the answer. Each fix is carried
into the slide draft, the lines or the platform answer it concerns, and so is the advice to move a dropped objection's
answering line onto the slide. A survivor that turns on a pattern joins the patterns list.

## Answering

Lead with what to fix, then the map and the drafts.

1. **The biggest issues,** at most three, one line each: the top surviving objections.
2. **Adversarial review:**
   - **Survivors,** ranked, as a table: Rank, Tier, Lens, The founder's line (quoted), Why a partner reads it that way,
     Fix or evidence to add.
   - **Dropped,** one line each: the objection, its lens, and why it fell (answered, quoting the founder's line that
     answers it, or not grounded), so the founder sees it was tested.
   - When the lenses ran one after another in one agent, with no subagent tool, say so: they are less independent
     than separate subagents.
   - When the refute pass ran per lens (lean mode), say so, say it is less independent than one subagent per objection,
     and say the founder may ask for the full pass.
3. **The map:** #, Competitor (as named), Level, The problem it solves (quoted), The founder's facts (quoted), Source
   or unverified. Each empty level as a row with its bracketed ask.
4. **Axes:** Axis, What 1 means, What 3 means, What 5 means, Buyer evidence (quoted); then the halves, in one line.
5. **Placements:** one row per company, the founder's own included, one column per axis, each cell the founder's
   placement with its evidence, or "not placed". No total, average or rank column.
6. **The substitutes story.**
7. **Why customers pick us:** one line per competitor and per substitute.
8. **The platform-risk answer:** its three parts.
9. **The competition slide:** the headline, the table and the 2x2 grid with its "not placed" list; while placements
   are missing, "waiting for your placements" in place of the 2x2 and the slide.
10. **Patterns:** each line quoted, its pattern, what a partner is likely to hear, the fix.
11. **Open asks:** every bracketed gap, every lens gap and every placement still to give, in one list.
12. **Close:** this is not investment, legal or tax advice. The competitor facts are the founder's, to check before
    the deck goes out; a comparison with a named competitor should be accurate and fair, and a lawyer should review
    comparative claims before the deck is sent widely or published.

## Sources

None. This skill's authors read no public source on competition maps for it, so it cites none. The four levels are the
pack's own grouping, as the vc-deck-review and vc-claims-check skills use it; the axis rules, the halves, the patterns
and the platform answer's three parts are this skill's own judgment, common in founder advice but unverified. The
two-stage review (attack, then refute with the founder's own material) follows the vc-positioning skill's method, which
is that skill's own.

## Limits

- Not investment, legal or tax advice. It does not say whether the company will win, whether to raise, or from whom.
- No competitor research: it names no competitor or platform the founder did not name, looks nothing up, and adds no
  fact about any company, even one the agent has heard of.
- It places no company on an axis, adds no placements into a score, and ranks no one.
- It never predicts what a named company will do; the platform answer is the founder's view, labelled as such.
- It never role-plays or speaks as a named investor, firm or author, and never names a firm the map fits. Asked to,
  it offers the lenses instead and keeps the founder as the user.
- No arithmetic and no calculator tool; figures are quoted as stated.
- The review predicts what a partner is likely to push on; a real partner may know a competitor the founder did not
  name.
- It works from the founder's text and sends nothing anywhere.
