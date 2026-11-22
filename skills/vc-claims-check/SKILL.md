---
name: vc-claims-check
description: Helps a founder check every claim in their deck, one-pager or narrative before a VC does. It lists each quantitative or verifiable claim with where it appears, classes it (figure, market size, customer or partner, team credential, competition, technology claim), and checks whether the founder can show a source, whether the materials agree, and whether it uses a pattern a VC discounts, such as no competitors, a top-down-only TAM, advisors as decoration, AI bolted on, or letters of intent and GMV called revenue. Deal terms go to the calculator's deal_check tool. An adversarial review has a skeptical pass pick the claims a partner would check first and a refute pass keep each attack only if the founder's material grounds it. Each claim comes back supported, needs a source, contradicted or will be discounted, with the fix. Use when a founder says check my claims, fact-check my deck, will a VC believe this, do my numbers agree, or what will a partner check first. Never invents evidence. Not investment advice.
---

# VC claims check

Helps a founder find, before a partner does, the claims in their fundraising materials that will not hold up. It lists
every quantitative or verifiable claim in the deck, one-pager and narrative with where each appears, sorts it into one
of six classes, and checks three things: can the founder show where it comes from, do the materials agree with each
other, and does it use a pattern investors are known to discount. Deal terms are checked by the equity calculator,
never by hand. A short adversarial review then picks the claims a partner is likely to check first and attacks them,
and keeps an attack only when the founder's own material grounds it. Each claim comes back with one verdict and the fix.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, never
looks anything up, and never adds evidence, figures or facts the founder did not give.

## When to use it

- "Check my claims." "Fact-check my deck." "Will a VC believe this?" "Do my numbers agree across the deck and the
  one-pager?" "What will a partner check first?"
- A deck, one-pager, executive summary, investor update, data-room index or spoken pitch, alone or several together.
- Called from the vc-positioning skill when its review needs each claim's evidence or finds figures that may disagree.
- Hand off:
  - The ask's arithmetic in full (ownership after the round, the pool, runway): the vc-deal-math skill, whose steps
    this skill follows for deal terms.
  - A raise on a SAFE or note: `equity_round`, as vc-deal-math step 2 says (the equity-calculator skill).
  - The story, the one-liner and the say-and-avoid list: the vc-positioning skill.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. Every document the founder will send or show, each with a name ("deck", "one-pager", "narrative") and its places
   marked (slide numbers, page numbers or paragraph order), so every claim can be located.
2. For each claim the founder already knows is load-bearing: the evidence they can show a partner (a contract, an
   invoice, a dashboard export, a cited report with its publisher and date, a reference who has agreed to take a call).
3. The ask as each document states it: amount, instrument (priced round, SAFE or note), valuation or cap with its
   label, percent sold, pool, cash, burn and revenue, runway claim, use-of-funds lines.
4. The stage of the raise.

A missing input does not stop the check. It becomes a named ask in the answer, never a plausible fact.

## The six classes

Every claim gets exactly one class. A claim that fits two takes the one a partner would check it under.

| Class               | What it covers                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| Figure              | Revenue, users, growth, retention, pipeline, unit economics, projections, and every deal term    |
| Market size         | Any size of market, segment or spend, top-down or bottom-up                                      |
| Customer or partner | A named or counted customer, pilot, logo, partnership, integration, letter of intent or reseller |
| Team credential     | A founder's, hire's or advisor's past role, achievement, degree, exit or affiliation             |
| Competition         | Who else serves the need, what customers use today, and any claim of being first, only or best   |
| Technology claim    | What the product does or how: AI, accuracy, speed, patents, "proprietary", benchmarks, security  |

## The four verdicts

Each claim gets one verdict. When a claim earns more than one, it takes the first in this order and the others go in
its fix: **Contradicted**, then **Will be discounted**, then **Needs a source**, then **Supported**.

| Verdict            | When                                                                                                                                                                       |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Contradicted       | Two lines of the founder's material state the claim differently (both quoted, with their places), or the calculator reports a mismatch on a deal term                      |
| Will be discounted | The claim matches a pattern in the discount table below, whatever its evidence                                                                                             |
| Needs a source     | The founder names no evidence they can show, or the claim can only be compared with another line after a conversion this skill does not do                                 |
| Supported          | The founder names evidence they can show, every place the claim appears agrees, and no discount pattern applies; a deal term also needs a consistent verdict from the tool |

"Supported" means supported by what the founder says they can show. The skill does not see or verify that evidence;
the answer says a partner will ask for it.

## Steps

1. **List the claims, word for word.** Every number, name, credential, comparison and capability statement a partner
   could check, each quoted exactly with its document and place. One claim per row; a claim stated in three places is
   one row with three places.
2. **Class each claim** with one of the six classes.
3. **Evidence.** For each claim, write what the founder said they can show, or "none named". Never fill this in from
   general knowledge, and never describe a report, customer or person the founder did not mention.
4. **Agreement across the materials,** with no arithmetic:
   - Put every place a claim appears side by side, quoted. The same metric for the same period with different stated
     values is Contradicted. Compare the values as the founder wrote them; compute no difference.
   - When two lines state a metric in different forms (monthly and yearly, MRR and ARR, different periods or
     definitions), do not convert one into the other. Say they cannot be compared as stated, mark the claim Needs a
     source, and ask the founder to state one figure, in one form, with its period.
   - Projections are Figures too: check that each is labelled as a plan with its period, and quote it as stated.
5. **Deal terms go to the calculator.** The raise, valuation and its label, percent sold, pool, founders' percent
   after the round, outstanding SAFEs and notes, cash, burn, revenue, runway claim and use-of-funds lines are checked
   with `equity_deal_check` (from the command line, `equity_calculator deal_check`), following the vc-deal-math skill's
   steps: ask for what is missing, send money and percents as strings, and call twice for a valuation with no label.
   - **One call per version of the ask.** When two documents state the same term differently, run one call per
     document, each with only that document's figures. Never match a figure against the tool's output by eye across
     documents.
   - A mismatch row makes the claim Contradicted: quote the document's figure and give the tool's value. A consistent
     row is the arithmetic half of Supported; the founder still needs to show the documents behind the figures.
   - A raise on a SAFE or note is not passed as `investment`: route it as vc-deal-math step 2 does, to `equity_round`.
   - Growth rates, market sizes, retention and unit economics have no tool here: quote them, never compute, convert
     or round one.
6. **Scan for discount patterns** (the table below). For each hit, quote the line, name the pattern and its source,
   and write the fix using only the founder's facts, or a bracketed ask: `[the signed contract's start date]`.
7. **Run the adversarial review** (next section): the skeptic, the quote check, the refute pass.
8. **Set each verdict** by the order above, then apply the review: a kept attack sets its claim's verdict to the one
   its grounds give (a second line that disagrees: Contradicted; a discount pattern: Will be discounted; missing
   evidence: Needs a source), whichever comes first in the order.
9. **Check before answering.** Every claim and every attack quotes a line that is in the material word for word;
   every figure is quoted as stated or comes from a tool result; no evidence, customer, source or credential is
   described that the founder did not give; no sentence speaks as an investor or imitates a named person.

## Adversarial review

The steps check every claim evenly; a partner does not. They check the two or three claims that would end the
conversation if wrong, and check those hard. This review finds those claims and attacks them, then a second pass
throws out every attack the founder's material does not ground, so the founder spends their time on real exposure.

### The skeptic

One pass, named by what it does: it picks the claims a partner is likely to check first and attacks them. Its brief:

- You find the claims a partner is likely to check first: those that, if wrong, would end the meeting or the
  diligence. Write in the third person ("a partner is likely to check this first because ..."); you are not an
  investor and do not speak as one, named or not.
- Read only the founder's material given here. Bring in no outside fact about the company, its market, its customers
  or its competitors, and do no arithmetic.
- Return at most three attacks, the one a partner checks first at the top. For each: the claim, quoted word for word,
  with its document and place; why a partner is likely to check it first; and the attack: the evidence a partner
  would ask to see, or the other line of the material it conflicts with, quoted word for word.
- An attack you cannot tie to a line the founder wrote is not an attack. List it apart as a question to the founder.
- Return "nothing found" rather than a weak attack.

**How to run it.** With a subagent tool (in Claude Code, the Agent or Task tool), run the skeptic as a subagent given
only the founder's material and the brief above: not this skill's other sections, not the claims list, so it does not
anchor on the list. Without one, run the skeptic before step 1 and write its attacks down in full; do not revise them
after building the list.

**The calculator's mismatches** from step 5 do not go through the skeptic or the refute pass. They are computed, not
argued: each is a kept attack on its claim, quoting the document's figure with the tool's value as the reason.

### Check the quotes

Before the refute pass, check every attack's quotes against the founder's material. An attack whose claim, or whose
conflicting line, does not appear in the material word for word (spacing and line breaks aside) is dropped as not
grounded. Questions to the founder go to the open asks.

### The refute pass

Each attack gets its own refute pass. With a subagent tool, run one subagent per attack, given the founder's material,
that one attack and the brief below, and nothing else; without one, decide the attacks one at a time. The brief:

- You decide whether one attack is grounded in the founder's material. Write in the third person; you are not an
  investor and do not speak as one, named or not.
- Use only the founder's material given here. Bring in no outside fact, and do no arithmetic.
- Return one verdict from the three below, quoting the founder's line word for word where the verdict needs one.

The verdicts:

- **Kept, grounded:** the attack rests on the material: a source the material does not supply, a second line of the
  material that states the claim differently (quoted), or a pattern from the discount table.
- **Dropped, answered:** the material already shows the evidence the attack asks for. Quote the founder's line that
  shows it. A line that is not in the material word for word does not drop the attack.
- **Dropped, not grounded:** the attack rests on something outside the material (a market fact, a guess about a
  competitor or a customer, an assumption about the founder), or the quoted line does not say what the attack claims.

An attack is kept only if it is grounded. When the pass cannot tell whether the material answers a grounded attack,
the attack is kept. The pass invents nothing on the founder's behalf: no evidence, document, customer or argument.

## Discount patterns

Signals, not rules: a founder may have a reason. Flag, explain, and let them decide. A row marked unverified has no
public source behind it that this skill's authors read; say so when you use it.

| Pattern                                                                                                    | Class               | Why a partner is likely to discount it                     | Fix                                                                                                                                              | Source                                                                                            |
| ---------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| "No competitors", "the only company that", "first to market"                                               | Competition         | Either the need is not real or the founder has not looked  | Name the alternatives: the same product, the same need met another way, a larger product that could add this, and doing it by hand or not at all | Sequoia "Competition / alternatives"; Dixon "The idea maze"; the four groups are ours, unverified |
| A market size from an analyst figure only, or "if we get 1% of it"                                         | Market size         | A top-down number that never narrows to who will buy       | Who exactly buys, how many there are, what each pays, from the founder's own evidence; a top-down figure only as a cross-check                   | YC seven questions (2); YC seed fundraising guide (what not to do)                                |
| A market size with no publisher or date                                                                    | Market size         | Nothing to check it against                                | Name the publisher, the year and the definition, or drop it                                                                                      | Unverified                                                                                        |
| Advisors given a slide or a headline; well-known names with no role                                        | Team credential     | Advisors carry little weight next to the founders          | Founders first; an advisor only with what they do for the company                                                                                | YC seed deck guide                                                                                |
| Credentials as adjectives or bare logos ("world-class", "ex-big-tech", "serial founder")                   | Team credential     | Nothing specific to check                                  | One specific, checkable achievement per person                                                                                                   | YC "How to Apply"                                                                                 |
| "AI-powered" where the product would work the same without a model                                         | Technology claim    | A label on a feature, not a reason the product wins        | What the model does that the product could not do without it, and what shows it; or drop the label                                               | Unverified                                                                                        |
| "Proprietary", "patented" or "patent-pending" with nothing named                                           | Technology claim    | A claim a partner cannot check                             | Name what is proprietary; for a patent, its filing status and number                                                                             | Unverified                                                                                        |
| Letters of intent, bookings or pipeline called revenue; GMV called revenue                                 | Figure              | An inflated top line that diligence will undo              | Name each metric for what it is, with its own figure and period                                                                                  | a16z "16 Startup Metrics" (1, 2, 6)                                                               |
| Cumulative charts, downloads, or "strong traction" with no figure                                          | Figure              | Vanity, or a number being hidden                           | A period-by-period figure with its definition                                                                                                    | a16z "16 Startup Metrics" (13, 14)                                                                |
| A pilot, free trial or integration listing called a customer or a partnership; a logo used without consent | Customer or partner | The first reference call will say what the relationship is | Name each relationship for what it is (paid, pilot, unpaid, letter of intent) and confirm the customer agrees to be named                        | Unverified                                                                                        |

## Answering

Lead with what a partner will check first, then the full list.

1. **Checked first:** the kept attacks, at most three, each with the claim quoted and placed, why a partner is likely
   to check it first, the attack, and the fix. Then **Dropped,** one line each: the attack and why it fell (answered,
   quoting the line that answers it, or not grounded), so the founder sees it was tested.
2. **Claims table:** #, Claim (quoted), Where, Class, Evidence the founder can show, Agrees across the materials?,
   Verdict, Fix. Order by verdict, Contradicted first.
3. **Deal terms:** the `equity_deal_check` verdict for each call, which document's figures it used, and each mismatch
   row in the tool's values.
4. **Disagreements:** each pair of lines that disagree, side by side with their places, and which one the founder
   should keep once they confirm it.
5. **Open asks:** every bracketed gap and every question from the skeptic, in one list.
6. **Sources:** the frameworks used, with links, and which rows rest on an unverified source.
7. **Close:** this is not investment, legal or tax advice; customers and partners named in the materials should have
   agreed to be named, and a lawyer should review the materials before they are sent widely.

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

The rows marked unverified (the four competitor groups, an undated market size, "AI-powered" as a label, unnamed
proprietary technology, relationships called customers) are this skill's own judgment, common in founder advice but
with no public source its authors read. The two-pass review (a skeptic, then a refute pass that keeps only grounded
attacks) is this skill's own method.

## Limits

- Not investment, legal or tax advice. It does not say whether a claim is true in the world, only whether the
  founder's material and the calculator support it.
- It never invents, strengthens or finds evidence: no web look-ups, no market data, no checks on people or companies.
- It never role-plays or speaks as a named investor, firm or author.
- No arithmetic outside the equity calculator's tools. Figures are compared as stated, never converted.
- The adversarial review predicts which claims a partner is likely to check first; a real partner may check others.
- It works from the founder's text and sends nothing anywhere.
