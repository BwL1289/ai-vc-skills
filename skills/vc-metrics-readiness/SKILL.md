---
name: vc-metrics-readiness
description: Helps a founder check that their traction metrics are ready for a raise before a VC reads them. It checks each metric's definition (ARR against a revenue run-rate, gross against net revenue retention, logo against revenue churn, blended against paid CAC, CAC payback on gross margin, burn multiple on net new ARR), whether the deck, model and investor update state each one the same way, and which metrics a fund at the founder's stage usually expects to see. Every ratio comes from the calculator's metrics_check tool. An adversarial review has independent lenses make the definitional attacks a skeptical partner makes and a refute pass drop what the founder's material answers; what survives becomes a ranked fix list. Use when a founder says are my metrics ready, check my ARR, is this NRR right, what is our burn multiple or CAC payback, do my metrics match across the deck and the model, or what metrics does a Series A fund expect. No score, no named firms. Never invents numbers. Not investment advice.
---

# VC metrics readiness

Helps a founder find, before a partner does, the metrics in their raise that will not survive the first question:
"how do you define that?" It lists every traction metric in the deck, model and investor update, names the definition
each one uses, checks that the documents agree, and has the equity calculator work every ratio from the founder's own
parts. Independent lenses then make the definitional attacks a skeptical partner makes, a refute pass drops every
attack the founder's material answers, and the survivors become a ranked fix list. It ends with which metrics a fund at
the founder's stage usually expects to see, and which are missing.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, gives no
score and never says "ready" or "not ready", and never adds a figure the founder did not give.

## When to use it

- "Are my metrics ready for a raise?" "Check my ARR." "Is this NRR right?" "Is our churn 2% or 3%?"
- "How do I work out burn multiple?" "What is our CAC payback?" (with the founder's figures)
- "Do my metrics match across the deck, the model and the update?" "What metrics does a Series A fund expect?"
- A metrics slide, a KPI tab, a monthly investor update, alone or several together.
- Hand off:
  - The ask, ownership after the round, the SAFE stack, the pool and runway: the vc-deal-math skill.
  - Every other claim in the materials (customers, team, market, competition): the vc-claims-check skill, whose steps
    this skill follows for metrics.
  - The story and the one-liner: the vc-positioning skill. One equity question with no metrics: the equity-calculator
    skill.
  - A slide-by-slide review of the whole deck: the vc-deck-review skill (preview).
  - Planned, not yet shipped: market sizing. Until it ships, say so.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. Every document with metrics in it (deck, model or KPI tab, investor update, one-pager), each named and with its
   places marked (slide, tab, paragraph), so every metric can be quoted with where it appears.
2. For recurring revenue, one period the founder names (a month, a quarter or a year): recurring revenue at the start,
   and in the period new, expansion, contraction and churned recurring revenue, said to be monthly (MRR) or annual
   (ARR) figures; for a period longer than a month, the expansion, contraction and churn of the starting customers
   alone; the latest month's total revenue and its one-time (setup, services, hardware) and usage parts.
3. For the same period: customers at the start, customers lost, customers won and how many came through paid
   channels; sales and marketing spend and what it includes; gross margin and what is in cost of revenue; net burn.
4. The stage of the raise, the business model (subscription, usage, marketplace, transactions, hardware,
   pre-revenue) and the customer segment (small business, mid-market, enterprise), in the founder's words.
5. Optional: the evidence behind each figure (a billing export, a dashboard, a bank statement).

A missing input does not stop the check. The metric is quoted as stated and marked Needs a source, and the missing
part becomes a bracketed ask (`[contraction MRR in the same month]`), never a plausible figure.

## Definitions

The definitions this skill checks against. "Computed" names the calculator's output; "quoted" means no tool computes
it here, so it is quoted as stated with "not checked: no tool computes this". A row marked ours is this skill's own
wording, unverified.

| Metric                  | Definition                                                                                                     | What a partner checks for                   | Computed or quoted            | Source                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ----------------------------- | -------------------------------------------------------------- |
| ARR                     | Recurring revenue on an annual basis, without one-time fees, services or variable usage fees                   | A month's total revenue times 12 called ARR | Computed: ARR                 | a16z "16 More" (2); a16z "16 Startup Metrics" (2)              |
| Revenue run-rate        | The latest month's or quarter's revenue, annualised; how marketplaces state size                               | Presented as ARR                            | Computed: run-rate            | a16z "16 More" (2)                                             |
| Bookings, LOIs, GMV     | A contract's value; letters of intent are neither; GMV flows through, revenue is the take                      | Called revenue                              | Quoted                        | a16z "16 Startup Metrics" (1, 6)                               |
| Gross revenue retention | Of recurring revenue at the start of a period, the share kept after downgrades and cancellations, no expansion | Expansion netted in                         | Computed: GRR                 | Bessemer                                                       |
| Net revenue retention   | The same with expansion from the same starting customers; new customers left out                               | New customers counted in                    | Computed: NRR                 | Bessemer; Skok; new customers as the mistake: ours, unverified |
| Gross revenue churn     | Recurring revenue lost (downgrades and cancellations) over recurring revenue at the start                      | Only the net figure shown                   | Computed                      | a16z "16 Startup Metrics" (11)                                 |
| Net revenue churn       | Revenue lost less expansion, over recurring revenue at the start                                               | Shown alone, it understates the losses      | Computed                      | a16z "16 Startup Metrics" (11)                                 |
| Logo churn              | Customers lost over customers at the start of the period                                                       | "Churn" with no basis                       | Computed                      | a16z "16 Startup Metrics" (11); Skok                           |
| CAC                     | Full acquisition cost over new customers (blended); over customers from paid channels (paid)                   | Costs left out; blended only                | Computed: CAC                 | a16z "16 Startup Metrics" (8)                                  |
| CAC payback             | Months for new recurring revenue, after gross margin, to repay acquisition spend                               | Worked on revenue, not margin               | Computed: payback             | Bessemer (margin-adjusted); the formula is ours, unverified    |
| Burn multiple           | Net burn over net new ARR, for the same period                                                                 | New ARR instead of net new; gross burn      | Computed: burn multiple       | Sacks                                                          |
| Net and gross burn      | Net: spend less incoming cash; gross: spend alone                                                              | Gross presented as the burn                 | Quoted (runway: vc-deal-math) | a16z "16 Startup Metrics" (12)                                 |
| Gross margin            | Revenue less cost of revenue, over revenue                                                                     | What is in cost of revenue left unsaid      | Quoted (used for payback)     | a16z "16 Startup Metrics" (3); Bessemer                        |
| Growth                  | Compounded monthly growth rather than the simple average of monthly rates                                      | A simple average                            | Quoted                        | a16z "16 Startup Metrics" (10)                                 |
| Active users            | A defined action, applied the same way every period                                                            | "Active" undefined                          | Quoted                        | a16z "16 Startup Metrics" (9); a16z "16 More" (12)             |
| Customer concentration  | The largest customer's revenue over total revenue, same period                                                 | Not shown                                   | Computed: concentration       | a16z "16 More" (14)                                            |

## The four verdicts

Each metric gets one verdict, in vc-claims-check's words and order. When a metric earns more than one, it takes the
first in this order and the others go in its fix: **Contradicted**, then **Will be discounted**, then **Needs a
source**, then **Supported**.

- **Contradicted:** two lines of the founder's material state the same metric, in the same form, for the same period,
  differently (both quoted, with their places), or the calculator reports a mismatch (for an unlabelled churn, a
  mismatch on every basis).
- **Will be discounted:** the metric's line matches a row of the pattern table below, or of vc-claims-check's discount
  table, whatever its evidence.
- **Needs a source:** no definition, no period, or no evidence the founder can show; or two lines in different forms
  that only the calculator could compare and whose parts were not given.
- **Supported:** a definition and period that match the table, a consistent tool check where the tool computes it,
  agreement across the documents, and evidence the founder names. The skill does not see that evidence; the answer
  says a partner will ask for it.

## Steps

Without a subagent tool, run Stage A of the adversarial review first, before step 1, as "How to run the lenses" says,
so the lenses do not anchor on the tool's output; step 7 then starts at the quote check.

1. **List every metric word for word,** with its document and place: revenue, ARR, growth, retention, churn,
   customers, users, CAC, payback, margin, burn, efficiency ratios. One metric per row; a metric stated in three
   places is one row with three places.
2. **Name the definition each line uses,** from the table above, only as far as the line itself says. A line with no
   definition or no period is Needs a source with a bracketed ask (`[the period this NRR covers]`).
3. **Agreement across the documents:** follow vc-claims-check step 4 as written. Compare as stated; compute no
   difference; never convert. Lines in different forms (MRR against ARR, a month against a year) are compared only by
   the calculator, when the founder gives the parts; otherwise mark the metric Needs a source and ask for one figure,
   in one form, with its period.
4. **The calculator.** Pass the founder's parts and every stated figure to `equity_metrics_check` (from the command
   line, `equity_calculator metrics_check`), money and percents as strings:
   - **One call per document's version of the figures,** each with only that document's stated figures. Never match a
     figure against a tool value by eye across documents.
   - Every flow figure in one call is for the same period, `period_months`. When the founder's burn and revenue
     movements cover different periods, ask for one period; never prorate.
   - Say whether recurring figures are monthly or annual (`recurring_unit`). The tool converts MRR to ARR; the model
     never does.
   - A churn figure with no basis goes in with `stated_churn_basis` left `unlabelled`: the tool checks it against
     every basis it can compute, one row per basis. Those rows are one check: the churn is a calculator mismatch only
     when no basis row is consistent. When one is, it is not a mismatch; it is Will be discounted under the pattern
     table's row for "Churn" with no basis, with every basis row quoted in the tool's values.
   - For a period longer than a month, pass the starting customers' own movements in the `cohort_*` fields, so
     retention leaves out customers won during the period; without them, say the tool's `cohort_rule` assumption row
     applies and ask for those movements.
   - A stated burn multiple when net new ARR or net burn is zero or below gets no check row: it is not checked, and
     the flag (`burn_multiple_not_defined` or `no_net_burn`) says why. A stated figure given without the parts the
     tool needs to check it is refused; relay the refusal and ask for the parts it names.
   - Each code in the result's `flags` goes to the answer as a question a partner is likely to ask, in the words of
     the Flags table below.
   - Give `customer_segment` only as the founder states it; it sets the payback benchmark the tool's assumption row
     quotes.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point
     of its `rounded` value two places to the right, keeping every digit (0.95 is 95%, 0.875 is 87.5%), which is what
     the command line's report prints. That is a change of notation, not a calculation; never round it.
   - Deal terms (the raise, valuation, percent sold, use of funds) go to `equity_deal_check` as the vc-deal-math skill
     says, and a runway claim to the vc-deal-math skill, which picks its tool; none goes to this tool.
   - Growth rates, LTV, market sizes and every metric the table marks quoted: quote as stated with "not checked: no
     tool computes this", and never compute, convert or round one.
   - A refusal or tool error is the answer for those inputs: relay its reason and what to ask the founder for.
5. **Scan for definitional patterns** (the table below) and vc-claims-check's discount patterns. For each hit, quote
   the line, name the pattern and its source, and write the fix with only the founder's facts or a bracketed ask.
6. **Stage expectations.** Fill the stage table for the founder's stage and model: each expected metric Present
   (quoted, with its place) or Missing (a bracketed ask). Rate no value against any bar.
7. **Run the adversarial review** (next section): attack, check the quotes, refute, rank.
8. **Set each metric's verdict** by the order above, then apply the review: a kept objection sets its metric's verdict
   to the one its grounds give, whichever comes first in the order.
9. **Check before answering.** Every figure is quoted as stated or comes from a tool result; every objection quotes a
   line that is in the material word for word; no conversion, sum, ratio or growth rate is worked in the answer's own
   text; no score, no "ready" or "not ready", no raise-or-wait call; no sentence speaks as an investor or names a firm.

## Definitional patterns

Signals, not rules: a founder may have a reason. Flag, explain, and let them decide. A row marked unverified has no
public source behind it that this skill's authors read.

| Pattern                                                                 | Why a partner is likely to discount it                       | Fix                                                              | Source                                             |
| ----------------------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------- | -------------------------------------------------- |
| "ARR" that is a month's total revenue times 12                          | A run-rate, which one-time revenue in that month can inflate | Call it a run-rate, or state ARR from recurring revenue alone    | a16z "16 More" (2)                                 |
| ARR that includes setup, services, hardware or usage fees               | Non-recurring revenue presented as recurring                 | ARR from recurring revenue only; other revenue on its own line   | a16z "16 Startup Metrics" (2); a16z "16 More" (2)  |
| Net retention that counts revenue from new customers                    | Growth presented as retention                                | Net retention from the starting customers only, with the period  | Unverified                                         |
| "Churn" with no basis (customers or revenue, gross or net)              | Each basis tells a different story                           | Name the basis, and show logo and gross revenue churn beside net | a16z "16 Startup Metrics" (11); Skok               |
| Net revenue churn shown alone                                           | Expansion can hide what is lost                              | Show gross revenue churn beside it                               | a16z "16 Startup Metrics" (11)                     |
| CAC that leaves out costs (referral fees, credits, discounts, salaries) | Understates what growth costs                                | Count every acquisition cost; say what is in the spend           | a16z "16 Startup Metrics" (8)                      |
| Blended CAC only                                                        | Says nothing about whether paid growth works                 | Show paid CAC beside blended                                     | a16z "16 Startup Metrics" (8)                      |
| CAC payback worked on revenue, not gross margin                         | Understates how long acquisition takes to repay              | Work it on gross-margin-adjusted new recurring revenue           | Bessemer                                           |
| Burn multiple on new ARR (churn left out), or on gross burn             | Flatters efficiency                                          | Net burn over net new ARR, for one period                        | Sacks                                              |
| A burn multiple before there is revenue                                 | The ratio does not compute                                   | Drop it; show net burn by month                                  | Sacks                                              |
| Monthly growth as the simple average of monthly rates                   | Overstates growth in a growing business                      | Compounded monthly growth, or each month's figure                | a16z "16 Startup Metrics" (10)                     |
| LTV on revenue or gross margin rather than contribution margin          | Sets too high a ceiling on acquisition spend                 | LTV on contribution margin, or 12- and 24-month value to date    | a16z "16 Startup Metrics" (5)                      |
| "Active users" with no stated action                                    | Nothing to check                                             | Name the action and the period, and keep the definition fixed    | a16z "16 Startup Metrics" (9); a16z "16 More" (12) |
| A ratio with no period ("NRR 120%")                                     | Cannot be compared with anything                             | State the period beside every ratio                              | Unverified                                         |

## Adversarial review

The steps check every metric evenly; a partner does not. They test the definitions behind the two or three metrics the
story rests on, and test those hard. This review makes those attacks, then a second pass throws out every attack the
founder's material answers, so the founder spends their time on real exposure.

### Stage A: attack

Each lens tests one family of definitions and is named by it. The lenses are frameworks, never people: none is a named
investor, firm or author, and none speaks in the first person as an investor.

| Lens                    | What it tests                                                                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------- |
| Revenue definitions     | Whether ARR, run-rate, bookings, GMV and revenue are each named for what they are, with a period              |
| Retention and churn     | The basis of every churn and retention figure, its period, and whether new customers or expansion hide losses |
| Acquisition and payback | What CAC counts, blended against paid, and whether payback is worked on margin                                |
| Burn and efficiency     | Net or gross burn, net new or new ARR, and whether both are for the same period                               |
| Stage fit               | Which metrics a fund at the founder's stage expects that the material does not show                           |

Every lens gets the same brief, with its own name and test filled in, and the Definitions table:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to ask how
  this ARR is defined because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here and the definitions. Bring in no outside fact about the company, its
  market or its competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the line it is about, quoted word for word with its
  document and place; the definition a partner is likely to test it against; and how much it hurts (ends the meeting,
  weakens it, or minor).
- A reason you cannot tie to a line the founder wrote is not an objection. List it apart as a gap, worded as a
  question.
- Do not judge whether another line of the material answers an objection: raise it anyway, and the refute pass
  decides. Return "nothing found" only when no line of the material gives this lens an objection worth a partner's
  time.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the lenses as parallel
subagents. Give each one only the founder's material, the Definitions table and its lens brief: not this skill's other
sections, not the tool's output, not another lens's objections. Without a subagent tool, run Stage A first, before
step 1: run the lenses one after another, write each lens's objections down in full before reading the next lens's
brief, and never revise an earlier list. Lenses run this way are less independent than subagents, and the same agent
then judges them in Stage B, so the answer says so.

**The calculator's mismatches** from step 4 do not go through the lenses. Each is added to the survivors as ends the
meeting, quoting the document's figure with the tool's value, and the flag that names its likely cause, as the
reason. It is not refuted: the calculator computed it. An unlabelled churn with one consistent basis row is not a
mismatch (step 4).

### Check the quotes

Before Stage B, check every objection's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same objection about
the same line, merge them and keep both lens names. Gaps from every lens go to the open asks.

### Stage B: refute

Each objection gets its own refute pass. With a subagent tool, run one subagent per objection, given the founder's
material, that one objection, the Pattern column of this skill's pattern table and of vc-claims-check's discount
table, and everything from "The refute brief:" to the end of this stage, and nothing else; without one, decide the
objections one at a time against the same brief.

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

- **Dropped, answered:** a line of the material other than the objected line supplies the definition, basis, period or
  part the objection says is missing. Quote it with its place. When it sits in another document than the figure, say
  to put the definition beside the figure.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact about the company, its market or its competitors.
- **Kept:** neither holds. When the best answer needs something the material does not contain, the objection stays
  and that something becomes the evidence to add, as a bracketed ask.

The refute pass invents nothing on the founder's behalf. After the passes, an answering line that is not in the
material word for word does not drop the objection, and neither does one that is the objected line itself.

### The ranked fix list

Order the kept objections in three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**. The
calculator's mismatches lead the first tier. Within a tier, an objection raised by more than one lens comes first. The
tier is a judgment, not a probability: give no percentages and no score. Each entry is one fix: the document and
place, the line quoted word for word, why a partner is likely to read it that way in one or two plain sentences, and
the change to make, using only the founder's facts, a tool value or a bracketed ask.

## Flags

The tool's `flags` holds codes only; this table is what each one means for the founder. A flag is a question to be
ready for, never an error.

| Flag                                        | What it means for the founder                                                               | What to change or prepare                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `stated_arr_matches_run_rate`               | The stated ARR agrees with 12 times the month's total revenue, not with recurring revenue   | Call it a run-rate, or restate ARR from recurring revenue                     |
| `run_rate_includes_non_recurring`           | The month has one-time or usage revenue, so run-rate and ARR differ                         | Show both, each named                                                         |
| `stated_nrr_includes_new`                   | The stated net retention agrees with ending over starting revenue, new customers counted in | Restate net retention on the starting customers                               |
| `expansion_hides_churn`                     | Net revenue churn is zero or below while gross revenue churn is above zero                  | Show gross revenue churn beside net                                           |
| `churn_basis_unlabelled`                    | The stated churn names no basis; the tool checked it against each                           | Name the basis on the slide                                                   |
| `blended_cac_only`                          | No paid-channel split was given                                                             | Be ready with paid CAC                                                        |
| `payback_not_margin_adjusted`               | No gross margin was given, so payback is on revenue only                                    | Give gross margin; a partner works payback on margin                          |
| `stated_payback_not_margin_adjusted`        | The stated payback agrees with the revenue payback, not the margin one                      | Restate it on gross margin                                                    |
| `stated_burn_multiple_uses_new_not_net_arr` | The stated multiple agrees with net burn over new ARR, churn left out                       | Restate it on net new ARR                                                     |
| `burn_multiple_not_defined`                 | Net new ARR is zero or below in the period                                                  | Drop the multiple; show net burn and the ARR movement                         |
| `no_net_burn`                               | Net burn is zero or below in the period                                                     | Say the company is not burning cash in that period                            |
| `payback_above_band`                        | Payback on gross margin is at or above the tool's benchmark for the segment                 | Be ready to say why; quote the tool's assumption row, a benchmark, not a rule |
| `burn_multiple_above_band`                  | The multiple is at or above the tool's benchmark                                            | Be ready to say why; quote the tool's assumption row, a benchmark, not a rule |
| `net_revenue_churn_above_band`              | One month's net revenue churn is above the tool's benchmark                                 | Be ready to say why; quote the tool's assumption row, a benchmark, not a rule |

The three benchmark flags are common benchmarks, not rules: say so, and quote the source and date the tool's
assumption row gives, never a figure from memory.

## Stage expectations

Which metrics a fund at each stage usually expects to see, never what values: the skill rates no figure against a
stage bar. The mapping of stage to metric is this skill's own judgment, unverified, built from the sources' lines.

| Stage and model             | Metrics a fund usually expects to see                                                                                                                               | Source                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Pre-seed, any model         | A product in use; a defined active user; cohort retention of early users                                                                                            | YC seed fundraising guide; a16z "16 More" (10); a16z "16 Startup Metrics" (9) |
| Seed, any model             | The above, plus revenue or usage month by month, its growth, and net burn                                                                                           | YC seed fundraising guide; a16z "16 Startup Metrics" (12, 14)                 |
| Series A, recurring revenue | ARR and its movement (new, expansion, contraction, churn), gross and net revenue retention, logo churn, CAC and payback, burn multiple, gross margin, concentration | Bessemer; Skok; Sacks; a16z "16 More" (14)                                    |
| Marketplace or transactions | GMV and revenue on separate lines, a run-rate on the latest month or quarter, the take as the founder states it; ARR does not apply                                 | a16z "16 Startup Metrics" (6); a16z "16 More" (2)                             |

Mark each expected metric Present (quoted, with its place) or Missing (a bracketed ask). When the stage the founder
states and what the metrics show disagree, say so as a question a partner is likely to ask, without a threshold.

## Answering

Lead with what to fix, in order, then the evidence behind it.

1. **The biggest fixes,** at most three, one line each: the top of the ranked fix list.
2. **Ranked fix list,** as a table: Rank, Tier, Where, Lens, The line (quoted), Why a partner reads it that way, Fix.
   Then **Dropped,** one line each: the objection, its lens, and why it fell (answered, quoting the line that answers
   it, or not grounded). When the lenses ran in one agent, say they are less independent than separate subagents.
3. **Metrics table:** #, Metric (quoted), Where, Definition it uses, The tool gives, Agrees across the documents?,
   Verdict, Fix. Order by verdict, Contradicted first.
4. **Calculator results,** per call: which document's figures it used, each check row in the tool's values, each flag
   in plain words from the Flags table, and the assumption rows the answer leans on, with their sources and dates.
5. **Stage expectations:** the row for the founder's stage and model, each metric Present or Missing.
6. **Open asks:** every bracketed gap and every lens gap in one list, so the founder can answer them in one sitting.
7. **Sources:** the frameworks used, with links, and which points rest on this skill's own unverified judgment.
8. **Close:** this is not investment, legal, tax or accounting advice; how revenue is recognised is a question for an
   accountant, and the figures should match the books before the materials go out.

## Sources

- Andreessen Horowitz, "16 Startup Metrics" (2015): https://a16z.com/16-startup-metrics/
- Andreessen Horowitz, "16 More Startup Metrics" (2015): https://a16z.com/16-more-startup-metrics/
- David Sacks, "The Burn Multiple" (2020): https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200
- David Skok, "SaaS Metrics 2.0": https://www.forentrepreneurs.com/saas-metrics-2/
- Bessemer Venture Partners, "Scaling to $100 Million" (2021):
  https://www.bvp.com/atlas/scaling-to-100-million
- Y Combinator, "A guide to seed fundraising": https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising

These guides are years old and describe software companies most of all; say their dates when a founder leans on one.
Bessemer's figures come from its own cloud portfolio, not a random sample. The exact CAC payback formula, new customers
in net retention as a named mistake, a ratio with no period as a pattern, and the mapping of stage to metric are this
skill's own judgment, unverified. The two-stage review (attack, then refute with the founder's own material) is this
repository's own method.

## Limits

- Not investment, legal, tax or accounting advice. It does not say whether to raise, when, or at what valuation.
- It gives no score and no verdict on readiness: no rating out of any number, no "ready" or "not ready", no "raise now
  or wait".
- It never names a firm or person, never role-plays or speaks as a named investor, firm or author, and does no investor
  research.
- It never invents, fills in or strengthens a figure, a definition or evidence, in a fix or in a refute pass.
- No arithmetic outside the equity calculator's tools: no MRR-to-ARR conversion, sum, ratio or growth rate by hand.
  Growth rates, LTV, magic number and Rule of 40 are quoted, not computed.
- Benchmarks appear only as the tool's assumption rows, with their sources and dates; they vary by sector, segment and
  year.
- It sees no billing system, ledger or bank data and verifies no evidence; a partner will ask to see it.
- The review predicts likely definitional attacks; a real partner may raise others.
- It works from the founder's text and sends nothing anywhere.
