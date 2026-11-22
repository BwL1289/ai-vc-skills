---
name: vc-positioning
description: Helps a founder tune a raise's messaging and positioning before VCs see it. It reads the founder's one-liner, narrative, ask and metrics, checks them against public frameworks (YC's seven pitch questions and seed guides, Sequoia's business-plan outline), and runs an adversarial review in which independent skeptical lenses list the strongest reasons a VC would pass, each quoting the founder's own line, and a refute pass drops every objection the founder's own material answers. It flags phrases that cost credibility, such as no competitors, our projections are conservative, or we only need 1% of the market, and returns surviving objections with rewrites, a tightened narrative, a say-and-avoid list and a script for a prep session with an existing investor. Use when a founder says tighten my pitch, stress-test my pitch, how should we position this round, what should I not say to VCs, or prep me before we go out to raise. Never invents traction; the ask's figures go to the calculator. Not investment advice.
---

# VC positioning

Helps a founder package a raise before the first outside meeting: one plain sentence that says what the company does,
a story a partner can repeat to their colleagues, and the phrases to keep or drop. It reads the founder's own material,
checks it against public frameworks for how investors read a pitch, attacks it the way a skeptical partner would, then
defends it with the founder's own words, and returns what survives: the objections still standing, a tightened
narrative, a say-and-avoid list and a script for a prep session with an existing investor. The prep session follows an
idea from a public LinkedIn post by Harry Stebbings of 20VC (November 2026): test the packaging with someone already on
your cap table before you take it to dozens of new investors.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, and never
adds a fact about the company that the founder did not give.

## When to use it

- "Tighten my pitch." "Stress-test my pitch." "Why would a VC pass on us?" "How should we position this round?"
  "What should I not say to VCs?" "Is my one-liner clear?" "Prep me before we go out to raise."
- A pasted one-liner, elevator pitch, deck outline or slide text, executive summary or intro blurb.
- Hand off:
  - The arithmetic in the ask (valuation, percent sold, option pool, SAFEs and notes, runway, use of funds): follow the
    vc-deal-math skill, which calls `equity_deal_check`. New money on a SAFE or note: `equity_round` (equity-calculator
    skill). A stake through later rounds: `equity_dilution`.
  - Planned, not yet shipped: slide-by-slide deck review, rehearsing the partner meeting, checking each claim's
    evidence. Until they ship, say so and do the messaging part here.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. The one-liner as the founder says it today, word for word.
2. The narrative in order: slide titles and text, or the spoken pitch.
3. The ask: the amount, the instrument (priced round, SAFE or note), the valuation or cap with its label (pre- or
   post-money), and the milestones the money is meant to reach.
4. Each metric as the founder states it, with its definition and period: revenue (recurring or not; bookings, GMV and
   letters of intent named as such), users, growth, retention, pipeline.
5. The stage of the raise and the kind of investor it is aimed at, in the founder's words.
6. What customers use today instead of the product, as the founder sees it.
7. Who the founder can run a prep session with: an existing investor or, with none, the closest substitute.

A missing input does not stop the review. It becomes a named gap in the answer, never a plausible figure.

## The dimensions

Each row is a question a partner answers about the company whether or not they ask it aloud. "Category" and "wedge"
are this skill's own terms, not headings in the sources; every other row follows a named public source. The last
column names the adversarial lens that attacks the row.

| #   | Dimension          | What a clear answer does                                                              | Source                                                                        | Lens                   |
| --- | ------------------ | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------- |
| 1   | What you do        | One matter-of-fact sentence a reader could describe back; "X for Y" is fine           | YC seven questions (1); Sequoia "Company purpose"; YC "How to Apply"          | Clarity and problem    |
| 2   | Category           | Tells the partner which known kind of company this is, so they know how to compare it | Our term; YC "How to Apply" (a variant of something known)                    | Clarity and problem    |
| 3   | Problem            | Whose pain, how it is handled today, why that falls short                             | Sequoia "Problem"; YC seed deck guide                                         | Clarity and problem    |
| 4   | Why now            | What changed that makes this possible or needed now, and why it was not built before  | Sequoia "Why now?"; YC seed fundraising guide (the solution slide)            | Market and why now     |
| 5   | Insight and wedge  | What the founders know that others do not, and the narrow first market they win from  | YC seven questions (4); YC "How to Apply" (insight, a toehold); wedge is ours | Competition and wedge  |
| 6   | Traction           | Period-by-period numbers with definitions; progress for the time spent                | YC seven questions (3); YC seed deck guide; a16z "16 Startup Metrics"         | Traction and proof     |
| 7   | Market             | Who exactly buys, how many, what they pay: bottom-up, with evidence                   | YC seven questions (2); YC seed fundraising guide                             | Market and why now     |
| 8   | Competition        | Direct and indirect alternatives, earlier attempts, and why customers pick this       | Sequoia "Competition / alternatives"; Dixon "The idea maze"                   | Competition and wedge  |
| 9   | Business model     | One simple way the company makes money, owned plainly                                 | YC seven questions (5); Sequoia "Business model"                              | Traction and proof     |
| 10  | Team               | Why these founders: one specific achievement each, founders before advisors           | YC seven questions (6); YC "How to Apply"; YC seed deck guide                 | Team and why you       |
| 11  | Ask and milestones | How much, on what instrument, and what it gets the company to                         | YC seven questions (7); YC seed deck guide; YC seed fundraising guide         | The ask and milestones |

## Steps

1. **Quote first.** List what the founder said under each dimension, word for word. Do not tidy it yet.
2. **Mark each dimension** Clear, Needs work or Missing, quoting the line that decides it. Give no overall score: a
   number from one conversation is not calibrated and invites false comfort.
3. **Scan for phrases** from the table below, and for anything that works the same way. For each hit: quote it, say
   what a partner is likely to hear, name the source, and give a rewrite that uses only facts the founder gave. Where
   a rewrite needs a fact they did not give, write a bracketed ask: `[number of paying customers today]`.
4. **Numbers.** Collect every figure the founder states.
   - The ask's figures (raise, valuation and its label, percent sold, pool, SAFEs and notes, cash, burn, runway claim,
     use-of-funds lines): run the check as the vc-deal-math skill describes, with `equity_deal_check`, and use only
     the tool's values. A raise on a SAFE or note goes to `equity_round` as vc-deal-math step 2 says. A mismatch goes
     to the top of the answer: a story whose numbers disagree undercuts every message in it.
   - Growth rates, market sizes, retention and unit economics: no tool in this repository computes them. Quote them as
     stated, check only that each has a definition and a period, and never compute, convert or round one (no monthly
     growth turned into yearly, no "1% of the market is").
5. **Run the adversarial review** (next section): attack, check the quotes, refute, rank.
6. **Draft the tightened narrative** (rules below), starting from the surviving objections' rewrites.
7. **Draft the prep script** (below), with the branch for a founder who has no existing investor.
8. **Check before answering.** Every fact in the narrative appears in the founder's material or in a tool result;
   every figure is quoted as stated or comes from a tool; every surviving objection quotes a line that is in the
   material word for word; no sentence speaks as an investor or imitates a named person.

## Adversarial review

The dimension table says what is missing; this review says what will lose the meeting. One set of independent lenses
attacks the founder's material, a second pass defends it using only that material, and only the objections the
defence cannot answer reach the founder. The founder then sees both: what survived, and what was tested and fell.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people: none is a named investor, firm
or author, and none speaks in the first person as an investor.

| Lens                   | What it tests                                                                                             | Dimensions |
| ---------------------- | --------------------------------------------------------------------------------------------------------- | ---------- |
| Clarity and problem    | Could a partner say back what the company does, which known kind of company it is, and whose pain it ends | 1, 2, 3    |
| Market and why now     | Who exactly buys, how many there are, and what changed to make this the moment                            | 4, 7       |
| Traction and proof     | Whether the numbers show progress, each with a definition and a period, and how the company makes money   | 6, 9       |
| Competition and wedge  | The alternatives (doing nothing included), earlier attempts, the insight, and the narrow first market     | 5, 8       |
| Team and why you       | Why these founders, shown by specific achievements rather than adjectives                                 | 10         |
| The ask and milestones | The amount, the instrument, what the money reaches, and whether the obvious risk is named                 | 11         |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to pass
  because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here. Bring in no outside fact about the company, its market or its
  competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the founder's line it is about, quoted word for word;
  why a partner is likely to read that line as a reason to pass; and how much it hurts (ends the meeting, weakens it,
  or minor).
- A reason you cannot tie to a line the founder wrote is not an objection. List it apart as a gap, worded as a
  question to the founder.
- Return "nothing found" rather than a weak objection.

**How to run the lenses.** When the agent has a subagent tool (in Claude Code, the Agent or Task tool), run the lenses
as parallel subagents. Give each one only the founder's material and its lens brief: not this skill's other sections,
not the dimension table, not another lens's output, so no lens anchors on another. Without a subagent tool, run them
one after another, and write each lens's objections down in full before reading the next lens's brief; never revise
an earlier lens's list after a later one.

**The calculator's mismatches** from step 4 do not go through the lenses. Each mismatch row is added to the
survivors as ends the meeting, quoting the figure as the deck states it, with the tool's value as the reason. It is
not refuted: the calculator computed it.

### Check the quotes

Before Stage B, check every objection's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same objection about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each objection gets its own refute pass, which argues the founder's side using only the founder's material. With a
subagent tool, run one subagent per objection, given the founder's material and that one objection only; without
one, take the objections one at a time and decide each before reading the next. The pass returns one verdict:

- **Dropped, answered:** the material already answers the objection. Quote the founder's line that answers it. The
  rewrite may still move that line earlier, where a partner will see it.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on a fact
  that is not in the material.
- **Kept:** neither holds. When the founder's best answer would need something the material does not contain, the
  objection stays and that something becomes the evidence to add, as a bracketed ask.

The refute pass invents nothing on the founder's behalf: no figure, customer, plan, partnership or argument the
founder did not give. When it cannot decide, the objection is kept.

### Rank what survives

Order the kept objections in three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**.
Within a tier, an objection raised by more than one lens comes first. The tier is a judgment, not a probability: give
no percentages and no score. For each survivor write:

- the founder's line, quoted word for word;
- why a partner is likely to read it that way, in one or two plain sentences;
- a concrete rewrite that uses only the founder's facts, or the evidence to add, as a bracketed ask.

**Where the survivors go.** The top three become the biggest issues at the head of the answer. A survivor that turns
on a phrase joins the say-and-avoid list. Each rewrite is carried into the tightened narrative. The top survivors go
into the prep script, so the existing investor can say whether new investors will raise them too.

## Phrases that cost credibility

Signals, not rules: a founder may have a reason. Flag, explain, and let them decide. A row marked unverified has no
public source behind it that this skill's authors read; say so when you use it.

| Phrase or pattern                                                                | What a partner is likely to hear                      | Say instead                                                                                    | Source                                                                                                             |
| -------------------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| "We have no competitors", "nobody else does this"                                | The market is not real, or the founder has not looked | Name the alternatives, including doing it by hand or doing nothing, and why customers pick you | Sequoia "Competition / alternatives"; YC "How to Apply" (obstacles you have not considered); Dixon "The idea maze" |
| "We only need 1% of the market", "if we get just 1% of a $X billion market"      | Top-down sizing that never narrowed the customer      | Who exactly buys, how many of them, what each pays: the founder's own numbers                  | YC seven questions (2); YC seed fundraising guide (what not to do: inflated market sizes)                          |
| "Our projections are conservative"                                               | Unverified: common in founder advice, no source read  | Label projections as a plan and show the two or three assumptions that drive them              | Unverified; YC seed fundraising guide advises against detailed financials at seed                                  |
| "Transforming", "revolutionizing", "AI-powered platform for"                     | Nothing a reader could describe back                  | What it is, for whom, in plain words; an "X for Y" analogy is fine                             | YC "How to Apply" (marketing language); YC seven questions (jargon)                                                |
| "Our edge is a better UX", "we execute better", "easy to use"                    | A claim to execute well, not an insight               | The specific thing you know or do that others do not                                           | YC "How to Apply"; YC seven questions (4)                                                                          |
| "Strong traction", "great momentum" with no number; cumulative charts; downloads | Vanity, or a number being hidden                      | A period-by-period figure with its definition                                                  | a16z "16 Startup Metrics" (13, 14); YC seed deck guide                                                             |
| Letters of intent or bookings called revenue; GMV called revenue                 | An inflated top line that diligence will undo         | Name each metric for what it is                                                                | a16z "16 Startup Metrics" (1, 6)                                                                                   |
| "We're raising $X" with nothing after it                                         | Cannot tell what the money buys                       | The amount and the milestones it reaches                                                       | YC seed deck guide; YC seven questions (7)                                                                         |
| Team as adjectives ("passionate", "world-class"); advisors up front              | Generic claims that carry no weight                   | One specific achievement per founder; founders before advisors                                 | YC "How to Apply"; YC seed deck guide                                                                              |
| The obvious risk left out                                                        | The founder has not thought of it                     | Name it and the plan for it                                                                    | YC "How to Apply"                                                                                                  |
| "What do you think?" as the close                                                | No ask                                                | State the ask                                                                                  | YC seven questions (7)                                                                                             |
| Asking for an NDA; negotiating valuation in the first meeting                    | Inexperience                                          | Drop the NDA; take terms away to discuss later                                                 | YC seed fundraising guide (what not to do)                                                                         |

## The tightened narrative

- **One-liner:** two or three options, matter-of-fact. Test each the way the sources suggest: could a reader who sees
  only this sentence describe the product back?
- **Order:** keep the founder's order unless a dimension is missing or buried. Offer YC's seed deck order (title,
  problem, solution, traction, insight, business model, market, team, ask) or Sequoia's outline as the alternative.
- **Never stronger than the facts.** No number, customer name, growth claim, partnership or credential that is not in
  the founder's material or a tool result. Every gap is a bracketed ask.
- **Shorter, in the founder's voice.** Cut words that carry nothing; keep the founder's own terms where they are clear.
- **Answer the survivors.** Each surviving objection's rewrite appears in the narrative, or its bracketed ask does.
- **The repeatable line:** mark the one sentence a partner should be able to repeat to their partners on Monday.

## The prep script

Purpose: test the packaging with someone who already knows the company before the first outside meeting.

- **Who:** an existing investor, ideally the lead of the last round. With none, the closest substitute: a founder who
  recently raised from the same kind of investor, an accelerator partner, or an angel who knows the space. Say plainly
  that a substitute does not know the company's history, so steps 5 and 7 below become guesses.
- **Before:** send the one-liner, the narrative, the say-and-avoid list and the top surviving objections a day or two
  ahead.
- **Agenda** (about 45 minutes; a suggestion, not a source):
  1. Before any slides, ask them to say in one sentence what the company does. Compare it with the one-liner.
  2. Give the pitch in the time a first meeting allows. Ask them to stop you at the first line they would discount.
  3. Walk the say-and-avoid list: which would they also flag, and what would they add for the investors you are
     targeting?
  4. Ask for the three questions they expect first from a new partner. Compare them with the top surviving objections;
     a question on both lists is the one to rehearse first, out loud.
  5. The ask: does the amount and the milestone story hold up, and does every figure match what they have seen in
     your investor updates?
  6. Ask how they would describe the company in an intro email. That sentence tests the repeatable line.
  7. Ask what they would say if a new investor called them about the company, and whether they expect to take part in
     the round (our note, unverified: new investors often ask both).
- **After:** update the narrative and the list, then try it on one or two more friendly listeners before the main list.

## Answering

Lead with what to fix, then the material to take into the prep session.

1. **The biggest issues,** at most three, one line each: the top surviving objections.
2. **Adversarial review:**
   - **Survivors,** ranked, as a table: Rank, Tier, Lens, The founder's line (quoted), Why a partner reads it that way,
     Rewrite or evidence to add.
   - **Dropped,** one line each: the objection, its lens, and why it fell (answered, quoting the founder's line that
     answers it, or not grounded), so the founder sees it was tested.
3. **Dimension table:** Dimension, What you say (quoted), Clear / Needs work / Missing, Fix.
4. **Say and avoid:** each flagged phrase quoted, what a partner is likely to hear, the rewrite, the source.
5. **Numbers:** the `equity_deal_check` verdict with each mismatch row in the tool's values; then each other figure
   quoted as stated with "not checked: no tool computes this", and any that lacks a definition or a period.
6. **Tightened narrative:** one-liner options, a 30-second version, the section order with bracketed asks.
7. **Prep script,** filled in with the founder's material and the top survivors.
8. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
9. **Sources:** the frameworks used, with links, and which points rest on an unverified source.
10. **Close:** this is not investment, legal or tax advice; a lawyer should review fundraising materials before they
    are posted publicly or sent widely, and customers or partners named in a deck should have agreed to be named.

## Sources

- Y Combinator, "How to Pitch Your Company" (the seven questions):
  https://www.ycombinator.com/library/4b-how-to-pitch-your-company
- Y Combinator, "How to Apply to Y Combinator" (Paul Graham): https://www.ycombinator.com/howtoapply
- Y Combinator, "How to build your seed round pitch deck":
  https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck
- Y Combinator, "A guide to seed fundraising": https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising
- Sequoia Capital, "Writing a Business Plan": https://www.sequoiacap.com/article/writing-a-business-plan/
- Andreessen Horowitz, "16 Startup Metrics" (2015): https://a16z.com/16-startup-metrics/
- Chris Dixon, "The idea maze" (2013): https://cdixon.org/2013/08/04/the-idea-maze
- Harry Stebbings (20VC), LinkedIn post on prepping fundraising messaging with existing investors, November 2026; the
  idea only, paraphrased above.

Several of these guides are years old. They describe how investors read a pitch, which changes slowly, but say their
dates when a founder leans on one. The adversarial review's two-stage method (attack, then refute with the founder's
own material) is this skill's own, not taken from any source.

## Limits

- Not investment, legal or tax advice. It does not say whether to raise, from whom, or at what valuation.
- It never invents or strengthens traction, customers, partners, credentials or figures, in a rewrite or in a refute
  pass.
- It never role-plays or speaks as a named investor, firm or author. Asked to "be" one, it offers that firm's public
  framework instead (Sequoia's outline, YC's questions) or the adversarial review's lenses, and keeps the founder as
  the user.
- The adversarial review predicts likely objections from the founder's text; it is not a verdict on the company, and
  a real partner may raise others.
- No investor research: no target lists, fund look-ups, contact details or outreach. The founder names who they meet.
- No arithmetic outside the equity calculator's tools. Growth rates, market sizes and unit economics are quoted, not
  computed.
- The phrase table holds common signals from public guides, not rules; they vary by stage, sector, region and
  investor. One row ("conservative projections") has no public source read and is marked unverified.
- It works from the founder's text and sends nothing anywhere.
