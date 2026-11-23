---
name: vc-partner-meeting
description: Helps a founder rehearse a VC partner meeting. From the founder's pitch, stage, round and the partner's background, it picks question lenses by stage (pre-seed, seed, Series A, later) and background (operator, finance, product, network, sector thesis), frameworks, never named people or firms, and builds the hardest questions with an adversarial review where lenses attack the founder's own lines and a refute pass keeps only questions the material leaves open. It drills them, preps what a partner checks around the meeting (who else is in the round, whether insiders take part, the references, what happens with no raise), and debriefs each weak answer with a stronger one built only from the founder's material and what a yes would need. Use when a founder says rehearse my partner meeting, run a mock partner meeting, drill me on the hard questions, prep me for my partner meeting, or debrief my answers. Never invents traction or investor interest; the ask's figures go to the calculator. Not investment advice.
---

# VC partner meeting

Helps a founder rehearse a partner meeting before the real one: the hardest questions a partner is likely to ask about
this company, put one at a time; the things a partner checks around the meeting (who else is in the round, whether
existing investors take part, who they will call, what happens if the round does not close); and a debrief that shows
each weak answer, a stronger one built only from what the founder said, and what a yes would need.

The founder is always the user. The skill is the rehearsal's moderator, not the investor: it puts each question in
the third person ("a partner with a finance background is likely to ask ..."), never speaks as an investor, never
imitates a named investor or firm, and gives no pass or invest verdict and no score. It never adds a fact about the
company, its round or its investors that the founder did not give.

## When to use it

- "Rehearse my partner meeting." "Run a mock partner meeting." "Drill me on the hard questions." "Prep me for my
  partner meeting on Monday." "What will the partners ask?" "Debrief my answers."
- A pasted pitch, deck outline or slide text, with the stage, the round and a note on who the founder is meeting.
- Hand off:
  - The story, the one-liner and the phrases to drop: the vc-positioning skill. Suggest it first when the pitch has
    no one-liner or no ask; a rehearsal of an unclear story drills the wrong things.
  - Each claim's evidence, and figures that disagree across documents: the vc-claims-check skill.
  - The ask's arithmetic (valuation, percent sold, ownership after the round, the pool, runway, use of funds): the
    vc-deal-math skill, which calls `equity_deal_check`. New money on a SAFE or note: `equity_round` (the
    equity-calculator skill). A stake through later rounds: `equity_dilution`.
  - Planned, not yet shipped: a ranked bank of due-diligence questions and a data-room checklist. It will share this
    skill's question bank ([`references/question-bank.md`](references/question-bank.md)). Until it ships, say so.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess. At most five questions:

1. The pitch as the founder gives it: the one-liner, then the slides or the spoken pitch in order.
2. The stage and the round: pre-seed, seed, Series A or later; the amount, the instrument (priced round, SAFE or
   note), the valuation or cap with its label (pre- or post-money), and what the money is meant to reach.
3. The meeting: a first meeting with one partner, or the full partnership; and the partner's background as the
   founder knows it from public material they have read (operator, finance, product, network, sector thesis), or
   "unknown". The founder names nobody to the skill unless they wish to, and the skill looks nobody up.
4. The round so far, in the founder's words, each part optional: who else they are talking to or has committed,
   whether existing investors will take part, who has passed and the reason given, and the cash runway if no new
   money comes in.
5. The mode: **live** (the skill asks one question at a time and waits for each answer) or **one message** (the
   founder pastes answers to the questions they expect, and the skill drills and debriefs on those).

A missing input does not stop the rehearsal. It becomes a named gap and a bracketed ask in the debrief, never a
plausible fact. **The founder's material** means the pasted text plus every answer the founder gives in this session.
Label each part as it arrives (P1, P2 ... for the pitch; A1, A2 ... for answers), so every quote can be located.

## The lenses

Each lens is a framework named by what it tests, never a person or firm. Run the founder's **stage lens** and the
**background lenses** that match the partner's background; with the background unknown, run all five background
lenses with at most two questions each. Stage lenses carry no numeric bars: what counts as enough traction varies by
sector, region and year, and this skill quotes no benchmark. Questions about competition read it at four levels:
Direct, Indirect, Adjacent and platform, and Doing nothing (the grouping is this skill's own, unverified).

| Lens          | Kind       | What it tests                                                                               |
| ------------- | ---------- | ------------------------------------------------------------------------------------------- |
| Pre-seed      | Stage      | Why these founders, the insight, and the smallest proof that someone wants this             |
| Seed          | Stage      | Early pull from users or customers, and the path from this round to the next one            |
| Series A      | Stage      | Whether growth repeats, the numbers behind it as the founder states them, the team to scale |
| Later stage   | Stage      | Efficiency, the size of the outcome, and what the new money changes                         |
| Operator      | Background | How the work gets done: the last hire, the last thing that broke, the next 90 days          |
| Finance       | Background | The ask, the cap table, burn and runway, and the downside if the plan slips                 |
| Product       | Background | What a user does first, why they come back, and what the product does that others do not    |
| Network       | Background | Who knows the founders and customers, and who the partner can call                          |
| Sector thesis | Background | What changed in the market, why now, and where the category is going                        |

## Steps

Without a subagent tool, run Stage A of the adversarial review right after step 2, before step 3, as "How to run the
lenses" says, so the lenses do not anchor on the numbers or the bank; step 4 then starts at the quote check.

1. **Intake.** Ask for the missing inputs in one message. Label the material as it arrives.
2. **Pick the lenses** from the table above, and say which and why in one line.
3. **Numbers.** Collect every figure the founder states.
   - The ask's figures (raise, valuation and its label, percent sold, pool, SAFEs and notes, cash, burn, runway claim,
     use-of-funds lines): run the check as the vc-deal-math skill describes, with `equity_deal_check`, and use only
     the tool's values, as printed, in the stronger answers too (20.83 months stays 20.83 months, never "about 21").
     Make one call per version of the ask the founder states (two for a valuation with no label, as vc-deal-math step
     4 says), and run no what-if they did not ask for. A raise on a SAFE or note goes to `equity_round` as vc-deal-math
     step 2 says. A mismatch is a question a partner is likely to ask, so it goes to the top of the drill.
   - On a SAFE or note raise, no tool checks the runway claim or the use-of-funds lines: quote them as stated, mark
     them "not checked: no tool computes this for a SAFE or note raise", and never work them out by hand.
   - The founder's runway if no new money comes in: `equity_deal_check` always adds the raise to the cash, so no tool
     here computes it. Quote it as stated, mark it "not checked: no tool computes runway without a raise", and never
     divide cash by burn yourself.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point of
     its `rounded` value two places to the right, keeping every digit (0.166667 is 16.6667%), which is what the
     command line's report prints. That is a change of notation, not a calculation; never round it.
   - Growth rates, market sizes, retention and unit economics: quote them as stated, check only that each has a
     definition and a period, and never compute, convert or round one.
4. **Run the adversarial review** (next section): attack, check the quotes, refute, rank. Its kept questions are the
   drill.
5. **Add the standing prep questions** (the section after it). They are asked of every founder and are not refuted.
6. **Drill.** Live mode: put one question at a time, kept questions first, then the standing ones, at most twelve in
   all unless the founder asks for more; the quick-rehearsal list comes after, only if the founder wants it. Wait for each answer and label it. Ask at most one follow-up per question,
   only when the answer leaves out the specific thing the question asked for, and quote the part of the answer it
   follows. One-message mode: match each pasted answer to its question; a kept question with no pasted answer is
   marked "not rehearsed". The founder can stop at any point; debrief what was answered.
7. **Debrief** (the section below): each answer, a stronger one, and what a yes would need.
8. **Check before answering.** Every question and every weak-answer note quotes a line that is in the founder's
   material word for word; every stronger answer uses only facts from the material or a tool result, and marks each
   gap as a bracketed ask; every figure is quoted as stated or comes from a tool; no sentence speaks as an investor,
   imitates a named person or firm, or gives a pass, invest or score.

## Adversarial review

The hardest questions in a partner meeting are the ones the founder's own material leaves open. One set of independent
lenses attacks the material and proposes those questions; a second pass judges each question using only that
material; only the questions the material does not answer are drilled hard. The founder sees both lists.

### Stage A: attack

Every lens picked in step 2 gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to ask ...
  because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here. Bring in no outside fact about the company, its market, its
  competitors or its investors, and do no arithmetic.
- Return at most three questions, hardest first. For each: the founder's line it is about, quoted word for word with
  its label; the question as a partner is likely to put it; why the line invites it; and how much a weak answer
  hurts (ends the meeting, weakens it, or minor).
- A question you cannot tie to a line the founder wrote is not an attack. List it apart as a gap, worded as a
  question to the founder.
- Return "nothing found" rather than a weak question.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the lenses
as parallel subagents, however short the material. Give each one only the founder's material and its lens brief: not this skill's other sections,
not the question bank, not another lens's output, so no lens anchors on another. Without a subagent tool, run Stage A
right after step 2, before step 3, without reading the question bank: run the lenses one after another, write each
lens's questions down in full before reading the next lens's brief, and never revise an earlier lens's list after a
later one. Lenses run this way are less independent than subagents, and the same agent then judges them in Stage B, so
the answer says so. The bank ([`references/question-bank.md`](references/question-bank.md)) is read only after Stage
A, to word the kept questions. A
bank question enters the drill only when it is tied to a founder's line quoted word for word and then passes the quote
check and the refute pass like any other; otherwise it becomes an open ask, or it is one of the standing prep questions.

**The calculator's mismatches** from step 3 do not go through the lenses. Each mismatch row is added to the kept
questions as ends the meeting, quoting the figure as the founder states it, with the tool's value as the reason. It is
not refuted: the calculator computed it.

### Check the quotes

Before Stage B, check every question's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same question about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each question gets its own refute pass. With a subagent tool, run one subagent per question, however few there are,
given the founder's
material, that one question, and everything from "The refute brief:" to the end of this stage, and nothing else;
without one, take the questions one at a time and decide each against the same brief before reading the next.

The refute brief:

- You decide whether the founder's material already answers one question; you argue neither side. Write in the third
  person; you are not an investor and do not speak as one, named or not.
- Use only the founder's material given here. Bring in no outside fact about the company, its market, its
  competitors or its investors, and do no arithmetic.
- How a partner is likely to read a line is not an outside fact. Judge whether the material answers the question, and
  never drop it as not grounded for that reason.
- Return one verdict from the three below, with the founder's line quoted word for word where the verdict needs one.
  When you cannot decide, return Kept.

The verdicts:

- **Dropped, answered:** a line of the material other than the questioned line gives the specific thing the question
  asks for (a figure with its period, a named alternative, a milestone, a specific achievement). Quote that line. The
  question is not drilled hard; it goes to the quick-rehearsal list with that line as the answer to lead with.
- **Dropped, not grounded:** the quoted line does not say what the question assumes, or the question rests on an
  outside fact about the company, its market, its competitors or its investors.
- **Kept:** neither holds. When the best answer would need something the material does not contain, that something
  becomes a bracketed ask, such as `[net revenue retention, last four quarters, as you define it]`.

The refute pass invents nothing on the founder's behalf: no figure, customer, investor, plan or argument. After the
passes, check every answering line the same way as the quotes: an answering line that is not in the material word for
word does not drop the question, which stays kept, and neither does one that is the questioned line itself.

### Rank what survives

Order the kept questions in three tiers, hardest first: **ends the meeting**, **weakens it**, **minor**. Within a
tier, a question raised by more than one lens comes first. The tier is a judgment, not a probability: give no
percentages and no score. The kept questions, in this order, are the drill.

## Standing prep questions

A partner is likely to ask or check these whatever the pitch says, so every founder prepares them. They are not
attacks on a line and are not refuted. For each, the skill drafts an answer only from the founder's material, or
leaves a bracketed ask; it never invents a fund, a commitment, a term sheet or a reference.

| Question a partner is likely to ask or check          | What the founder should have ready                                                    |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Who else are you talking to, and who has committed?   | A true answer at the level of detail the founder chooses; never an implied interest   |
| Will your existing investors take part in this round? | Their answer as the founder has it, or the plan to ask them before the meeting        |
| Who has passed, and why?                              | The reasons given, and what the founder changed or would answer                       |
| Whom will the partner call, on your list and off it?  | Customers, former colleagues and investors who may be called; brief the ones you list |
| What happens if this round does not close?            | Months of runway on today's cash as the founder states it, what gets cut, the plan    |
| What happens after this meeting, and when?            | A question for the founder to ask the partner, not to guess                           |

These questions are this skill's own list. Where they come from is in Sources; no public source this skill's
authors read in full names them, so they are unverified.

## The debrief

For each question asked, in the drill's order:

- **The question,** its lens, and the founder's line it came from, quoted.
- **The founder's answer,** quoted with its label.
- **What was weak,** only where something was: it did not answer the question asked; it gave no figure where the
  question asked for one; a figure had no definition or period; it disagrees with another line of the material (both
  quoted); it uses a phrase the vc-positioning skill flags; it ran long before the point. Say "held up" when nothing
  was weak.
- **A stronger answer,** at most four sentences, the point first, built only from the founder's material and tool
  results, each fact traceable to a label. Never stronger than the facts: no number, customer, investor, partner,
  credential or plan that is not in the material. Each gap is a bracketed ask.

Then **what a yes would need:** the evidence that would answer each kept question still open after the drill, as a
list of bracketed asks, ordered by tier. It is a list of things to show, not a prediction: never say a partner or a
firm would invest, pass or score the company.

## Answering

1. **The hardest three,** one line each: the top kept questions, and whether the founder's answer held up.
2. **Adversarial review:**
   - **Kept,** ranked, as a table: Rank, Tier, Lens, The founder's line (quoted), The question, Bracketed ask.
   - **Dropped,** one line each: the question, its lens, and why it fell (answered, quoting the founder's line to
     lead with, or not grounded), so the founder sees it was tested. The answered ones are the quick-rehearsal list.
   - When the lenses ran one after another in one agent, with no subagent tool, say so: they are less independent
     than separate subagents.
3. **Debrief,** question by question, as above.
4. **Standing prep:** each standing question with the drafted answer or its bracketed ask.
5. **Numbers:** the `equity_deal_check` verdict with each mismatch row in the tool's values; on a SAFE or note
   raise, the runway claim and use-of-funds lines quoted with "not checked: no tool computes this for a SAFE or note
   raise"; the runway with no new money quoted with "not checked: no tool computes runway without a raise"; every
   other figure quoted as stated.
6. **What a yes would need,** as a list of bracketed asks.
7. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
8. **Sources:** the frameworks used, with links, and which points rest on an unverified source.
9. **Close:** this is a rehearsal, not investment, legal or tax advice, and not a prediction of any investor's
   decision; customers or references the founder plans to name should agree first.

## Sources

- Y Combinator, "How to Pitch Your Company" (the seven questions):
  https://www.ycombinator.com/library/4b-how-to-pitch-your-company
- Y Combinator, "How to Apply to Y Combinator" (Paul Graham): https://www.ycombinator.com/howtoapply
- Y Combinator, "How to build your seed round pitch deck":
  https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck
- Sequoia Capital, "Writing a Business Plan": https://www.sequoiacap.com/article/writing-a-business-plan/

The seven questions shape the stage lenses (the one sentence, users and growth, the insight, the market, the team,
the ask); "How to Apply" the Pre-seed lens's insight and specific achievements; the seed deck guide the Finance lens's
ask (how much, and what it gets the company to); Sequoia's "Why now?" the Sector thesis lens. The lens kinds, the
standing prep questions and the debrief shape are this skill's own, unverified.
The idea of choosing lenses by stage and by a partner's background, and of preparing for references checked before
the meeting, came from reading an MIT-licensed set of investor-persona prompts (github.com/xiapeli/vc-skills); no
text was taken, and its named-firm personas are not used. The two-stage method (attack, then refute with the
founder's own material) is shared with the vc-positioning skill.

## Limits

- A rehearsal, not investment, legal or tax advice, and not a prediction: a real partner may ask other questions,
  and no answer guarantees an outcome.
- It never plays an investor, never speaks as or imitates a named investor, firm or author, and gives no pass, invest
  or readiness score. Asked to "be" a named partner, it declines in one line and offers the lenses instead.
- It never invents or strengthens traction, customers, investors, term sheets, references or figures, in a question,
  a stronger answer or a prep answer. Asked to imply interest that does not exist, it declines and drafts a true
  answer.
- No investor research: no look-ups of partners, funds, portfolios or contact details, and no outreach. The founder
  says what they know.
- No arithmetic outside the equity calculator's tools; runway with no raise is quoted, not computed.
- It works from the founder's text and sends nothing anywhere.
