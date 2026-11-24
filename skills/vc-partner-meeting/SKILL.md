---
name: vc-partner-meeting
description: Helps a founder rehearse a VC partner meeting. From the founder's pitch, stage, round and the partner's background, it picks question lenses by stage and by background, frameworks, never named people or firms, and builds the hardest questions with an adversarial review where lenses attack the founder's own lines and a refute pass keeps only questions the material leaves open. It drills them, preps what a partner checks around the meeting (who else is in the round, insiders, references, no raise), and debriefs each weak answer with a stronger one built only from the founder's material and what a yes would need. Use when a founder says rehearse my partner meeting, run a mock partner meeting, practice my investor meeting or VC pitch meeting, what will the partners ask, what will VCs ask me, drill me on the hard questions, prep me for my partner meeting, or debrief my answers. Never invents traction or investor interest; the ask's figures go to the calculator. Not investment advice.
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
- A pasted pitch, deck outline or slide text, with the stage, the round and a note on who the founder is meeting. Any of
  these may come as a file the agent can read in this session.
- Hand off:
  - Metric definitions a partner will test: the vc-metrics-readiness skill (preview).
  - The story, the one-liner and the phrases to drop: the vc-positioning skill. Suggest it first when the pitch has
    no one-liner or no ask; a rehearsal of an unclear story drills the wrong things.
  - Each claim's evidence, and figures that disagree across documents: the vc-claims-check skill.
  - A slide-by-slide read of the whole deck before the meeting: the vc-deck-review skill.
  - The ask's arithmetic (valuation, percent sold, ownership after the round, the pool, runway, use of funds): the
    vc-deal-math skill, which calls `equity_deal_check`. New money on a SAFE or note: `equity_round` (the
    equity-calculator skill). Runway with no raise, or on a SAFE or note raise: `equity_runway_plan`. A stake through
    later rounds: `equity_dilution`.
  - Why this amount, and not more or less, and which milestone it reaches: the vc-round-sizing skill (preview).
  - The memo a champion partner is likely to write for the partnership: the vc-investor-memo skill (preview).
  - Diligence after the meeting, by area, with a data-room checklist: the vc-diligence-questions skill (preview), which
    reads this skill's question bank ([`references/question-bank.md`](references/question-bank.md)).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess. When the founder gives a file the agent can
read (a PDF, HTML, a slides export, Markdown), read it yourself and list what it holds place by place (slide by slide
for a deck), in the file's own words, so the founder sees what was read from each. A place you could not read (a slide
that is only a picture, a page whose text did not come out, a file that opened only in part) is listed as not read and
asked for, never filled in from its title or the places around it, and a figure is never read off a chart or a picture.
Ask only for what you could not read and what the file does not show (speaker notes, the figures behind a chart, an
input below that it leaves out), and never ask the founder to paste what you already read. At most five questions:

1. The pitch as the founder gives it: the one-liner, then the slides or the spoken pitch in order.
2. The stage and the round: pre-seed, seed, Series A or later; the amount, the instrument (priced round, SAFE or
   note), the valuation or cap with its label (pre- or post-money), and what the money is meant to reach.
3. The meeting: a first meeting with one partner, or the full partnership; and the partner's background as the
   founder knows it from public material they have read (operator, finance, product, network, sector thesis), or
   "unknown". The founder names nobody to the skill unless they wish to, and the skill looks nobody up.
4. The round so far, in the founder's words, each part optional: who else they are talking to or has committed, whether
   existing investors will take part, who has passed and the reason given, and the cash runway if no new money comes in.
5. The mode: **live** (the skill asks one question at a time and waits for each answer) or **one message** (the
   founder pastes the questions they expect, each with their answer, and the skill debriefs every one of them).

A missing input does not stop the rehearsal. It becomes a named gap and a bracketed ask in the debrief, never a
plausible fact. **The founder's material** means the pasted text and any file read, plus every answer the founder gives
in this session. Label each part as it arrives (P1, P2 ... for the pitch; A1, A2 ... for answers), so every quote can be
located.

## The lenses

Each lens is a framework named by what it tests, never a person or firm. Run the founder's **stage lens** and the
**background lenses** that match the partner's background; with the background unknown, run all five background lenses
with at most two questions each. Stage lenses carry no numeric bars: what counts as enough traction varies by sector,
region and year, and this skill quotes no benchmark of its own. Questions about competition read it at four levels:
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
     Make one call per version of the ask the founder states, and run no what-if they did not ask for. A raise on a
     SAFE or note goes to `equity_round` as vc-deal-math step 2 says. A mismatch is a question a partner is likely to
     ask, so it heads the drill.
   - Fully diluted shares, for the tool, leave SAFEs and notes out. Some cap tables count SAFEs and notes in their
     fully diluted total; ask which way the founder's does, and pass the tool its own basis. If the founder's total
     counts them, ask for the total without them, `[fully diluted shares, SAFEs and notes left out]`; never subtract
     the SAFE or note shares yourself.
   - A valuation with no label: call twice, once as `pre_money`, once as `post_money`, and show both readings side by
     side. A check that is a mismatch under one reading only is not a calculator mismatch: it becomes one kept
     question, which reading is meant, quoting both readings in the tool's values, placed in a tier by the same
     judgment as a lens question and not refuted. Only a mismatch under every reading is the calculator's mismatch.
   - Read every code in each tool's `flags` too. Each is a question a partner is likely to ask, so each joins the kept
     questions as weakens it, with its meaning from the calculator flags table below (a tool call returns codes
     only), and is not refuted. The two benchmark flags (`runway_below_band`, `dilution_above_band`) rest on the
     tool's assumption rows (`runway_band`, `dilution_band`): quote the band only as that row gives it, with the
     source that row gives, as a common benchmark that varies by sector, stage and year, never as a bar to clear.
   - The founder's runway if no new money comes in: `equity_runway_plan`, with today's cash, one `plan` case of
     today's monthly spend and revenue, and the founder's figure as the top-level `stated_runway_months`:
     `{"inputs": {"cash_on_hand": "...", "cases": [{"name": "plan", "phases": [{"from_month": 1, "gross_burn": "...", "revenue": "..."}]}], "stated_runway_months": "..."}}`.
     With no cash or burn given, ask for them; never divide cash by burn yourself.
   - On a SAFE or note raise, the runway claim and the use-of-funds lines go to `equity_runway_plan` too, the raise as
     cash only: a `raises` entry with its `amount`, `stated_runway_months` and `use_of_funds`. On a SAFE or note raise,
     the `plan` case's phases are the founder's own figures: today's monthly spend and revenue as the first phase, from
     month 1, and each change the founder plans (more spend after the raise, say) as a later phase from the month the
     founder names, each asked for by name when missing (`[planned monthly spend and revenue, from which month]`), never
     assumed. Until a planned change's start month, its monthly spend and its monthly revenue are all given, make no
     runway call and give no runway figure; mark the runway line "not checked: waiting for [the month the planned spend
     starts]" while the month is missing, "not checked: waiting for [the planned monthly spend from that month]" while
     the month is given and the spend is missing, or "not checked: waiting for [the planned monthly revenue from that
     month]" while only the revenue is missing. Never work either out by hand.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point of
     its `rounded` value two places to the right, keeping every digit (0.166667 is 16.6667%), which is what the
     command line's report prints. That is a change of notation, not a calculation; never round it.
   - ARR, retention, churn, CAC payback and burn multiple belong to the vc-metrics-readiness skill
     (`equity_metrics_check`), a market size to the vc-market-sizing skill (`equity_market_sizing`): here, quote them
     as stated, check only that each has a definition and a period, and name that skill. Growth rates and LTV are
     quoted with "not checked: no tool computes this". Never compute, convert or round one.
4. **Run the adversarial review** (next section): attack, check quotes, refute, rank. Its kept questions are the drill.
5. **Add the standing prep questions** (the section after it). They are asked of every founder and are not refuted.
6. **Drill.** Live mode: put one question at a time, kept questions first, then the first five standing ones, at
   most twelve in all unless the founder asks for more, keeping five of the twelve for those standing ones; the sixth
   is the founder's to ask, so it goes in the standing prep, not the drill. The quick-rehearsal list comes after, only
   if the founder wants it. The first turn names the lenses and puts question 1; the numbered answer below comes once
   the drill ends or the founder stops, so the kept list is not shown before the drill. Wait for each answer and label
   it. Ask at most one follow-up per question, only when the answer leaves out the specific thing the question asked
   for, and quote the part of the answer it follows. One-message mode: debrief every pasted answer. Match each to the
   kept, dropped or standing question it answers; a dropped, answered question with a pasted answer is debriefed too,
   leading with its answering line. A pasted answer that matches none is debriefed under the founder's own question,
   quoted, labelled "your question" in place of a lens. A kept question with no pasted answer is marked "not
   rehearsed". The founder can stop at any point; debrief what was answered.
7. **Debrief** (the section below): each answer, a stronger one, and what a yes would need.
8. **Check before answering.** Every question and every weak-answer note quotes a line that is in the founder's material
   word for word, or, for a mismatch or a flag, the tool's row; every stronger answer uses only facts from the material
   or a tool result, and marks each gap as a bracketed ask; every figure is quoted as stated or comes from a tool,
   in bracketed asks, table cells and debrief notes too: never a difference, sum or ratio of two figures the founder
   gave ("from $80k to $120k a month", never "$40k more"); no sentence speaks as an investor, imitates a named person
   or firm, or gives a pass, invest or score.

## Calculator flags

A tool call returns each flag as a bare code. What each code means, as a question a partner is likely to ask, is the
calculator flags table in [`references/calculator-flags.md`](references/calculator-flags.md), with the three codes
`equity_runway_plan` can return; read it when a tool returns a flag.

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
- Do not judge whether another line of the material answers a question: raise it anyway, however short the material,
  and the refute pass decides. Return "nothing found" only when no line of the material gives this lens a question
  worth a partner's time.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the lenses
as parallel subagents, however short the material. Give each one only the founder's material and its lens brief: not
this skill's other sections, not the question bank, not another lens's output, so no lens anchors on another. Without a
subagent tool, run Stage A right after step 2, before step 3, without reading the question bank: run the lenses one
after another, write each lens's questions down in full before reading the next lens's brief, and never revise an
earlier lens's list after a later one. Lenses run this way are less independent than subagents, and the same agent then
judges them in Stage B, so the answer says so. The bank ([`references/question-bank.md`](references/question-bank.md))
is read only after Stage A, to word the kept questions. A bank question enters the drill only when it is tied to a
founder's line quoted word for word and then passes the quote check and the refute pass like any other; otherwise it
becomes an open ask, or it is one of the standing prep questions.

**The calculator's mismatches and flags** from step 3 do not go through the lenses. Each mismatch row heads the kept
questions, ahead of the tiers, quoting the figure as the founder states it with the tool's value as the reason. It
carries no tier: how much a gap hurts depends on its size, which the founder weighs. One exception: a runway claim below
the computed runway understates it, so it does not head the drill; the founder may keep it or state the printed runway,
and it goes in the minor tier at most. A percent sold or use-of-funds total below the tool's figure is still a mismatch.
Each flag is added as weakens it, with its meaning from the calculator flags table. Neither goes through the quote check
or the refute pass: the calculator computed it, and its quote is the tool's row.

### Check the quotes

Before Stage B, check every question's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same question about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each question gets its own refute pass. With a subagent tool, launch one subagent per question in a single message,
however few there are, each given the founder's material, that one question, and everything from "The refute brief:" to
the end of this stage, and nothing else; never put two questions in one subagent. Without one, take the questions one at
a time and decide each against the same brief before reading the next.

**Lean mode,** the one exception: with more than eight questions after the quote check, the refute pass may instead run
one subagent per lens, all in a single message. Each gets what a one-question subagent gets, but with every question
from its lens (one that two lenses raised goes to one of them only; one that no lens raised gets a subagent of its own),
and with this instruction, word for word: "Apply the brief to each question as if it were the only one you were given.
Return one verdict for each, with its own quote where the verdict needs one. Never let one question, its verdict or its
answering line decide another." Any question that comes back without a verdict of its own stays Kept. The answer then
says the refute pass ran per lens, which is less independent than one subagent per question, and that the founder may
ask for the full pass, one subagent per question.

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

The calculator's mismatches head the drill, ahead of the tiers, in the order the tool reports them (an understated runway
goes in minor). Then order the kept questions in three tiers, hardest first: **ends the meeting**, **weakens it**,
**minor**. Within a tier, the calculator's flags come first, in the order the tool reports them, ahead of everything
else: flags open weakens it. After them, a question raised by more than one lens comes first. The tier is a judgment,
not a probability: give no percentages and no score. The kept questions, in this order, are the drill.

## Standing prep questions

A partner is likely to ask or check these whatever the pitch says, so every founder prepares them. They are not attacks
on a line and are not refuted. For each, the skill drafts an answer only from the founder's material, or leaves a
bracketed ask; it never invents a fund, a commitment, a term sheet or a reference. The six questions, each with what the
founder should have ready, are in [`references/standing-prep.md`](references/standing-prep.md).

The first five topics came, as ideas, from the investor-persona prompts credited in Sources, which cite no source
for them; the wording, the sixth question and the list as a whole are this skill's own. All six are unverified. The
sixth is for the founder to ask the partner, so it is drafted here and never put to the founder in the drill.

## The debrief

For each question asked, in the drill's order, then, in one-message mode, each other pasted answer (step 6):

- **The question,** its lens (or "your question" for one only the founder asked), and the founder's line it came
  from (or, for a mismatch or flag, the tool's row), quoted.
- **The founder's answer,** quoted with its label.
- **What was weak,** only where something was: it did not answer the question asked; it gave no figure where the
  question asked for one; a figure had no definition or period; it disagrees with another line of the material or with a
  tool result (both quoted, the reason left as a bracketed ask such as `[what the deck's 24 months assumes]`, never
  an argument about which assumptions would make the stated figure true); it uses a phrase the vc-positioning skill
  flags; it ran long before the point. Say "held up" when nothing was weak.
- **A stronger answer,** at most four sentences, the point first, built only from the founder's material and tool
  results, each fact traceable to a label. Never stronger than the facts: no number, customer, investor, partner,
  credential or plan that is not in the material. Each gap is a bracketed ask.

Then **what a yes would need:** the evidence that would answer each kept question still open after the drill, as a
list of bracketed asks, ordered by tier. It is a list of things to show, not a prediction: never say a partner or a
firm would invest, pass or score the company.

## Answering

1. **The hardest three,** one line each, in the third person ("A partner is likely to ask ..."): the top kept
   questions, and whether the founder's answer held up.
2. **Adversarial review:**
   - **Kept,** ranked, as a table: Rank, Tier, Lens, The founder's line (quoted; the tool's row for a mismatch or
     flag), What a partner is likely to ask (third person), Bracketed ask. The calculator's rows are marked "from
     the calculator; not refuted"; a count of how many survived the refute pass counts only the lens questions.
   - **Dropped,** one line each: the question, its lens, and why it fell (answered, quoting the founder's line to
     lead with, or not grounded), so the founder sees it was tested. The answered ones are the quick-rehearsal list.
   - When the lenses ran one after another in one agent, with no subagent tool, say so: they are less independent
     than separate subagents.
   - When the refute pass ran per lens (lean mode), say so, say it is less independent than one subagent per question,
     and say the founder may ask for the full pass.
3. **Debrief,** question by question, as above.
4. **Standing prep:** each standing question with the drafted answer or its bracketed ask.
5. **Numbers:** each tool's verdict with each mismatch row in the tool's values (the runway with no new money, and on
   a SAFE or note raise the runway claim and use-of-funds lines, from `equity_runway_plan`); each flag, one line, with
   its meaning from the calculator flags table and a benchmark flag's band quoted from its assumption row with the
   source that row gives; every other figure quoted as stated.
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

The seven questions shape the stage lenses (the one sentence, users and growth, the insight, the market, the business
model, the team, the ask); "How to Apply" the Pre-seed lens's insight and specific achievements; the seed deck guide the
Finance lens's ask (how much, and what it gets the company to); Sequoia's "Why now?" the Sector thesis lens. The idea of
choosing lenses by stage and by a partner's background, the five background kinds (operator, finance, product, network,
sector thesis), and the topics of the first five standing prep questions (who else is in the round, insiders, who has
passed, references, no raise) came from reading an MIT-licensed set of investor-persona prompts
(github.com/xiapeli/vc-skills). That set cites no source for them, so they stay unverified here; no text was taken (the
questions are reworded), and its named-firm personas are not used. The sixth standing question, the debrief shape and
the twelve-question drill length are this skill's own, unverified. The two-stage method (attack, then refute with the
founder's own material) is shared with the vc-positioning skill.

## Limits

- A rehearsal, not investment, legal or tax advice, and not a prediction: a real partner may ask other questions,
  and no answer guarantees an outcome.
- It never plays an investor, never speaks as or imitates a named investor, firm or author, and gives no pass, invest
  or readiness score. Asked to "be" a named partner, it declines in one line and offers the lenses instead.
- It never invents or strengthens traction, customers, investors, term sheets, references or figures, in a question,
  a stronger answer or a prep answer. Asked to imply interest that does not exist, it declines and drafts a true answer.
- No investor research: no look-ups of partners, funds, portfolios or contact details, and no outreach. The founder
  says what they know.
- No arithmetic outside the equity calculator's tools, in any part of the answer; runway with no raise comes from
  `equity_runway_plan`.
- It works from the founder's text and sends nothing anywhere.
