---
name: vc-deck-review
description: Helps a founder review their pitch deck the way a partner reads it before the meeting. It maps every slide to ten dimensions (problem, solution, why now, market, product, traction, business model, competition, team, and the ask with its use of funds), marks each one evidence present, missing or contradicted with one fix, checks the first and last slides, and checks the competition slide at four levels, platform risk and doing nothing included. Claims go through the vc-claims-check steps, the ask's figures to the calculator's deal_check tool. An adversarial review has independent lenses attack the deck and a refute pass drop what the deck already answers; what survives becomes a ranked fix list. It says which kind of early investor the story fits, never a named firm, and gives no score. Use when a founder says review my deck, tear apart my pitch deck, is my deck ready to send, what will a partner think of my deck, or which investors fit this deck. Never invents traction. Not investment advice.
---

# VC deck review

Helps a founder read their own deck the way a partner will, before it is sent or presented. It maps every slide to ten
dimensions a partner checks, marks each one by the evidence the deck shows (present, missing or contradicted) with one
fix, applies a few first-slide and last-slide rules, and checks the competition section at four levels. Claims are
checked with the vc-claims-check steps and the ask's arithmetic with the equity calculator, never by hand. Independent
lenses then attack the deck and a refute pass drops every objection the deck already answers; the survivors become a
ranked fix list. It ends with the kind of investor the story fits, by stage and type.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
names a firm the deck fits, gives no score, and never adds a fact about the company that the founder did not give.

## When to use it

- "Review my deck." "Tear apart my pitch deck." "Is my deck ready to send?" "What will a partner think of my deck?"
  "Which investors fit this deck?" "What should I fix before Monday's meeting?"
- A deck as slide text, or a deck file the agent can read in this session, alone or with a one-pager or narrative.
- Built for pre-seed and seed decks. A deck for a later round gets the same review, with a note that the investor-fit
  table covers early investors only.
- Hand off:
  - The one-liner, the story and the say-and-avoid list: the vc-positioning skill. Point the founder to it when the
    first slide or the problem fails, or when they ask how to say it.
  - Claims: this skill runs the vc-claims-check steps for every claim in the deck. For its skeptic and refute pass on
    the claims alone, the founder runs that skill on its own.
  - The ask's arithmetic in full (ownership after the round, the pool, the SAFE stack, runway): the vc-deal-math
    skill, whose steps this skill follows. One equity question with no deck: the equity-calculator skill.
  - Rehearsing the partner meeting once the deck is ready: the vc-partner-meeting skill (preview).
  - A term sheet the founder was offered: the vc-term-sheet-review skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. The deck, slide by slide: its number, its title, every word on it, and for each chart, table or picture what it
   shows, with the figures as the founder would state them. Figures are never read off a picture.
2. The ask as the deck states it: the amount, the instrument (priced round, SAFE or note), the valuation or cap with
   its label (pre- or post-money), percent sold, cash on hand, burn and revenue today and planned, the runway claim,
   the use-of-funds lines; with SAFEs, notes or a pool top-up, what the vc-deal-math skill's step 2 asks for.
3. How the deck will be used (sent ahead and left behind, or presented live), the stage of the raise, and the kind
   of investor the founder plans to pitch, in their words.
4. For each claim the founder knows is load-bearing: the evidence they can show a partner.
5. Optional: any document sent with the deck (a one-pager, a narrative), so figures can be compared across them.

A missing input does not stop the review. It becomes a named gap in the answer, never a plausible figure.

## The ten dimensions

Each row is a question a partner answers from the deck whether or not they ask it aloud. Splitting "product" (what
exists today) from "solution" (what it does for the customer) is this skill's own choice; every other row follows a
named public source. The last column names the lens that attacks the row.

| #   | Dimension            | What the deck needs to show                                                         | Source                                                                                        | Lens                        |
| --- | -------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | --------------------------- |
| 1   | Problem              | Whose pain, how it is handled today and why that falls short, with real particulars | Sequoia "Problem"; YC seed deck guide (problem)                                               | Problem and solution        |
| 2   | Solution             | What it does in few words, the concrete benefit, and the insight behind it          | YC seed deck guide (solution, insight); Sequoia "Solution"; YC seven questions (4)            | Problem and solution        |
| 3   | Why now              | What changed that makes this possible or needed now                                 | Sequoia "Why now?"; YC seed fundraising guide (the solution part)                             | Market and why now          |
| 4   | Market               | Who exactly buys, how many there are, what each pays: bottom-up                     | YC seven questions (2); Sequoia "Market potential"                                            | Market and why now          |
| 5   | Product              | What exists and works today, shown (screens, the user's path), apart from plans     | Ours; YC seed fundraising guide (screenshots); YC seven questions (1)                         | Problem and solution        |
| 6   | Traction             | Clear, period-by-period numbers with their definitions                              | YC seed deck guide (traction); YC seven questions (3)                                         | Traction and business model |
| 7   | Business model       | One simple way the company makes money, owned plainly                               | YC seven questions (5); YC seed deck guide; Sequoia "Business model"                          | Traction and business model |
| 8   | Competition          | The alternatives at four levels and why customers pick this                         | Sequoia "Competition / alternatives"; the four levels are ours, unverified                    | Competition                 |
| 9   | Team                 | Why these founders suit this problem; founders, not advisors                        | YC seed deck guide (team); YC seven questions (6)                                             | Team                        |
| 10  | Ask and use of funds | How much, on what instrument, what it gets the company to, what is raised already   | YC seed deck guide (the ask); YC seed fundraising guide (fundraising); YC seven questions (7) | The ask and use of funds    |

## The evidence marks

Each dimension gets one mark. When it earns more than one, it takes the first in this order: **Contradicted**, then
**Missing**, then **Present**.

- **Contradicted:** two lines of the founder's material state the same thing differently (both quoted, with their
  slides; for a figure, the same metric in the same form for the same period), or the calculator reports a mismatch
  under every reading of the valuation (step 4).
- **Missing:** no slide shows what the row needs, or the only line that does is a claim vc-claims-check marks Will be
  discounted, or an adjective with nothing a partner could check ("strong traction", "world-class team").
- **Present:** a slide shows what the row needs, quoted. A claim vc-claims-check marks Needs a source keeps the mark
  Present; the fix says what to have ready, since a partner will ask for it.

Every dimension gets one fix, the most useful single change: for Present, a move earlier or "keep as is". Give no
overall score and no score per dimension: a number from one reading is not calibrated and invites false comfort.

## First and last slides

| Rule                                                                                                                   | Source                                                                                      |
| ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| The first slide names the company and says in one line what it does                                                    | YC seed deck guide (title page); Sequoia "Company purpose"                                  |
| That line is plain enough to say back: no jargon, no marketing words, no "platform" without what it is                 | YC seven questions (1, and "Improving your answers")                                        |
| The last slide of the main deck (an appendix after it aside) carries the ask: how much and what it gets the company to | YC seed deck guide (the ask closes the template)                                            |
| A close of "Thank you", "Questions?" or "What do you think?" with no ask is not an ask                                 | YC seven questions (7); "Thank you" and "Questions?" as the last slide are ours, unverified |
| A deck sent ahead reads on its own, as a leave-behind a partner can show their colleagues                              | YC seed fundraising guide (documents you need)                                              |
| At seed, each topic is one slide or a short set (at most three)                                                        | YC seed deck guide                                                                          |

These are signals, not rules: a founder may have a reason. A deck presented live may hold the ask for the spoken close;
say so and keep the fix.

## Competition at four levels

Sequoia's outline asks for direct and indirect competitors and a plan to win. This skill checks four levels; the
grouping is its own and unverified, the same four groups vc-claims-check uses, with an outsourced service added to
doing nothing.

| Level                 | What it covers                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| Direct                | The same product for the same buyer                                                             |
| Indirect              | The same need met another way                                                                   |
| Adjacent and platform | A larger product the buyer already uses that could add this as a feature                        |
| Doing nothing         | Doing it by hand (spreadsheets, phone calls), an outsourced service, or living with the problem |

For each level, quote what the deck says or mark it missing. The skill names no competitor itself: a missing level
becomes a bracketed ask (`[the tool your buyer already uses that could add this]`). "No competitors" goes to the
vc-claims-check discount patterns. A chart that puts the company alone in the best corner shows a position, not why
customers pick it; ask for the reason (unverified).

## Steps

Without a subagent tool, run Stage A of the adversarial review first, before step 1, as "How to run the lenses" says,
so the lenses do not anchor on the marks; step 7 then starts at the quote check.

1. **Map the slides, quoting them.** For each dimension, list the slides that speak to it, word for word with the slide
   number. A slide may serve two dimensions; a dimension may have none. Do not tidy anything yet.
2. **First and last slides.** Check the first slide, the last slide, the leave-behind rule and set length against the
   table above, quoting the line that decides each.
3. **Claims.** Load the vc-claims-check skill's text first; if it is not installed, say so and leave the claims table
   out rather than improvising it. Run the vc-claims-check skill's steps 1 to 6 on the deck and any document sent with
   it: the claims listed word for word with their places, classed, their evidence, their agreement across the documents
   (compared as stated, never converted) and the discount patterns. Set each claim's verdict by that skill's order,
   without its skeptic: this skill's lenses do the attacking. The claims table feeds the marks in step 6.
4. **The ask.** The deal terms are checked once, in claims-check step 5, which follows the vc-deal-math skill:
   - A priced round: `equity_deal_check` (from the command line, `equity_calculator deal_check`), money and percents
     as strings, every stated figure, use-of-funds lines included; one call per document's version of the ask. A
     valuation with no label: call twice, once as `pre_money`, once as `post_money`. Show both readings side by side,
     as vc-deal-math step 4 does, and say a partner will ask which one is meant. A check that is a mismatch under one
     reading only is not a calculator mismatch: it becomes one fix, to label the valuation pre- or post-money, quoting
     both readings in the tool's values. Only a check that is a mismatch under every reading is the calculator's
     mismatch. In the claims table, such a claim is not Contradicted either: mark it Needs a source, with both
     readings in its fix, since no single reading gives a verdict.
   - Each code in the result's `flags` goes to the answer as a question a partner is likely to ask, in the words the
     tool prints beside it, with what to change or prepare from the vc-deal-math skill's flag table. The benchmark
     flags (`dilution_above_band`, `runway_below_band`) are common benchmarks, not rules: say so and quote the tool's
     assumption row, whose source is `unverified`. With two readings, relay the flags of each.
   - A SAFE or note: not passed as `investment`. Route it as vc-deal-math step 2 does, to `equity_round` with the next
     priced round the founder expects. On a SAFE or note raise, no tool checks the runway claim or the use-of-funds
     lines: quote them, mark them "not checked: no tool computes this for a SAFE or note raise", and never work them
     out by hand.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point of
     its `rounded` value two places to the right, keeping every digit (0.166667 is 16.6667%), which is what the
     command line's report prints. That is a change of notation, not a calculation; never round it.
   - Growth rates, market sizes, retention and unit economics have no tool here: quote them as stated and never
     compute, convert or round one.
5. **Competition.** Fill the four levels from the deck's own lines, as the section above says.
6. **Mark each dimension** Present, Missing or Contradicted by the rules above, quoting the deciding line, with one
   fix that uses only the founder's facts or a bracketed ask (`[the milestone the raise reaches]`).
7. **Run the adversarial review** (next section): attack, check the quotes, refute, rank.
8. **Which investors the story fits** (the section after the review).
9. **Check before answering.** Every fix uses only the founder's facts, a tool result or a bracketed ask; every figure
   is quoted as stated or comes from a tool; every surviving objection quotes a line that is in the deck word for word
   (an entry for a dimension no slide covers quotes none); no sentence speaks as an investor, imitates a named person or
   names a firm; no score appears.

## Adversarial review

The marks say what is missing; this review says what will lose the meeting, and in what order to fix it. Independent
lenses attack the deck, a second pass judges each objection using only the founder's material, and only what that
material does not answer reaches the ranked fix list. The founder sees both: what survived, and what was tested and fell.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people: none is a named investor, firm
or author, and none speaks in the first person as an investor.

| Lens                        | What it tests                                                                                              | Dimensions            |
| --------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------- |
| Opening and close           | Whether the first slide says what the company does, the deck ends on the ask, and it reads alone           | First and last slides |
| Problem and solution        | Whose pain, what the product does about it, and what exists and works today                                | 1, 2, 5               |
| Market and why now          | Who exactly buys, how many there are, and what changed to make this the moment                             | 3, 4                  |
| Traction and business model | Whether the numbers show progress, each with a definition and a period, and how money is made              | 6, 7                  |
| Competition                 | The alternatives at four levels (direct, indirect, adjacent and platform, doing nothing) and why this wins | 8                     |
| Team                        | Why these founders, shown by specific achievements rather than adjectives or advisors                      | 9                     |
| The ask and use of funds    | The amount, the instrument, what the money reaches, and whether the use of funds says where it goes        | 10                    |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to stop at
  slide 4 because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the deck's line it is about, quoted word for word with
  its slide; why a partner is likely to read that line as a reason to pass; and how much it hurts (ends the meeting,
  weakens it, or minor).
- A reason you cannot tie to a line of the deck is not an objection. List it apart as a gap, worded as a question.
- Do not judge whether another line of the material answers an objection: raise it anyway, and the refute pass
  decides. Return "nothing found" only when no line of the deck gives this lens an objection worth a partner's time.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the lenses
as parallel subagents. Give each one only the founder's material and its lens brief: not this skill's other sections,
not the marks, not another lens's output. Without a subagent tool, run Stage A first, before step 1, without consulting
the dimension table or any mark: run the lenses one after another, write each lens's objections down in full before
reading the next lens's brief, and never revise an earlier list. Lenses run this way are less independent than
subagents, and the same agent then judges them in Stage B, so the answer says so.

**The calculator's mismatches** from step 4 do not go through the lenses. Each is added to the ranked fix list ahead
of the tiers, quoting the deck's figure with the tool's value and difference as the reason. It is not refuted: the
calculator computed it. It carries no tier: how much a gap hurts depends on its size and on the term, which the founder
weighs. A fix to label the valuation (a mismatch under one reading only) is not a calculator mismatch.

### Check the quotes

Before Stage B, check every objection's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same objection about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each objection gets its own refute pass, which decides, using only the founder's material, whether that material
answers the objection. With a subagent tool, run one subagent per objection, given the founder's material, that one
objection, the Pattern column of the vc-claims-check discount table, and everything from "The refute brief:" to the
end of this stage, and nothing else; without one, decide the objections one at a time against the same brief.

The refute brief:

- You decide whether the founder's material answers one objection; you argue neither side. Write in the third person;
  you are not an investor and do not speak as one, named or not.
- Use only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic.
- How a partner is likely to read a line is not an outside fact: judge whether the material answers that reading.
- A line that matches a pattern in the list you were given never answers an objection.
- Return one verdict from the three below, quoting the founder's line word for word where it needs one. When you
  cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the material other than the objected line supplies the specific thing the objection
  says is missing. Quote it with its slide. When it sits on a later slide than a partner will look for it, say to move
  it earlier.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact about the company, its market or its competitors.
- **Kept:** neither holds. When the best answer needs something the material does not contain, the objection stays
  and that something becomes the evidence to add, as a bracketed ask.

The refute pass invents nothing on the founder's behalf. After the passes, an answering line that is not in the
material word for word does not drop the objection, and neither does one that is the objected line itself.

### The ranked fix list

Order the kept objections in three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**. The
calculator's mismatches head the list, ahead of the tiers, each one under **figures that do not match (computed)**,
with no tier. Two kinds of entry that no lens raises join the tiers, placed by the same judgment and not refuted: the
step 4 fix to label a valuation, and each dimension marked Missing because no slide covers it, as "no slide covers"
that dimension, with its bracketed ask as the fix (it stays in the open asks too). Within a tier, an objection raised
by more than one lens comes first. The tier is a judgment, not a probability: give no percentages and no score. Each
entry is one fix: the slide, the deck's line quoted word for word (for a dimension no slide covers, "none"), why a
partner is likely to read it that way in one or two plain sentences, and the change to make, using only the founder's
facts or a bracketed ask. The top three become the biggest fixes at the head of the
answer; a fix that turns on the story or a phrase also points to the vc-positioning skill.

## Which investors the story fits

A lens on the founder's own deck, never a list of investors. It reads the stage the founder states against what the
deck shows, and says which kinds of investor the story as told fits best and which less, quoting the lines that decide
it. It names no firm or person, gives no check sizes and no odds, and looks nothing up. When the founder names firms
they plan to pitch, the skill does not judge those firms; the founder compares the fit with what they know of each.

| Kind of investor                 | Who they are                                                                          | Source                    |
| -------------------------------- | ------------------------------------------------------------------------------------- | ------------------------- |
| Angels                           | Back companies with personal money and decide for themselves, often alone and quickly | YC seed fundraising guide |
| Seed funds and small early funds | Small funds set up to back companies at their very start                              | YC seed fundraising guide |
| Larger firms that also do seed   | Traditional firms that invest in seed rounds as well as later ones                    | YC seed fundraising guide |
| Sector or thesis funds           | Funds that invest in one market or around one view of where a market is going         | Ours, unverified          |

How a story fits a kind (this skill's judgment, unverified, and said so in the answer): a story carried by the founders
and the problem, with an early product, reads as an angel or very early story; a story with a product in use and early
numbers reads as a seed story; a story whose ask names the milestone that makes the next round possible (the YC seed
deck guide: "Series A ready" inside a year) fits larger firms that also do seed, which can invest again in that next
round; a story built on one market's shift fits a fund with a thesis on that market. The table covers early investors
only: for a deck raising a later round, say so and name no later-stage kind. When the stage the founder states and what
the deck shows disagree (a Series A label on a deck of pilots), say so as a question a partner is likely to ask, without
a threshold.

## Answering

Lead with what to fix, in order, then the evidence behind it.

1. **The biggest fixes,** at most three, one line each: the top of the ranked fix list.
2. **Ranked fix list,** as a table: Rank, Tier, Slide, Lens, The deck's line (quoted), Why a partner reads it that way,
   Fix, with the figures that do not match (computed) first, then the tiers. Then **Dropped,** one line each: the
   objection, its lens, and why it fell (answered, quoting the line that answers it and whether to move it earlier, or
   not grounded). When the lenses ran in one agent, say they are less independent than separate subagents.
3. **Dimension table:** #, Dimension, Slides, What the deck says (quoted), Evidence (Present, Missing or Contradicted),
   Fix.
4. **First and last slides:** each rule, the line that decides it, the fix.
5. **Competition at four levels:** each level, what the deck says or "missing", the bracketed ask.
6. **Numbers:** the `equity_deal_check` verdict per call with each mismatch row in the tool's values (for a valuation
   with no label, both readings side by side), and each flag as a question a partner is likely to ask; on a SAFE or note
   raise, the runway claim and use-of-funds lines with "not checked: no tool computes this for a SAFE or note raise";
   every other figure quoted as stated with "not checked: no tool computes this".
7. **Claims:** the vc-claims-check claims table, Contradicted first.
8. **Which investors the story fits:** one short paragraph, with the deciding lines quoted and the judgment marked
   unverified.
9. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
10. **Sources:** the frameworks used, with links, and which points rest on this skill's own unverified judgment.
11. **Close:** this is not investment, legal or tax advice; customers or partners named in the deck should have agreed
    to be named, and a lawyer should review the deck before it is sent widely.

## Sources

- Y Combinator, "How to build your seed round pitch deck" (Aaron Harris, 2018):
  https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck
- Y Combinator, "How to Pitch Your Company" (the seven questions):
  https://www.ycombinator.com/library/4b-how-to-pitch-your-company
- Y Combinator, "A guide to seed fundraising": https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising
- Sequoia Capital, "Writing a Business Plan": https://www.sequoiacap.com/article/writing-a-business-plan/

Several of these guides are years old; they describe how investors read a deck, which changes slowly, but say their
dates when a founder leans on one. The split of product from solution, the four competition levels, the "Thank you"
and "Questions?" closes, the sector-fund row, how a story fits a kind of investor, and where computed mismatches and
missing slides sit in the ranked fix list are this skill's own judgment, unverified. The
two-stage review (attack, then refute with the founder's own material) is this repository's own method.

## Limits

- Not investment, legal or tax advice. It does not say whether to raise, from whom, or at what valuation.
- It gives no score: no 0-100 readiness number, no grade per dimension, no odds of a yes.
- It never names a firm or person the deck fits, never role-plays or speaks as a named investor, firm or author, and
  does no investor research: no target lists, fund look-ups, contact details or outreach.
- It never invents or strengthens traction, customers, partners, credentials or figures, in a fix or in a refute pass.
- No arithmetic outside the equity calculator's tools. Growth rates, market sizes and unit economics are quoted.
- It reads text. It does not judge visual design, and reads no figure off a chart the founder did not state.
- The review predicts likely objections from the deck's text; a real partner may raise others.
- It works from the founder's material and sends nothing anywhere.
