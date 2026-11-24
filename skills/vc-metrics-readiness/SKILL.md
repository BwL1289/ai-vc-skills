---
name: vc-metrics-readiness
description: Helps a founder check their traction metrics are ready for a raise before a VC reads them. It checks each metric's definition (ARR against run-rate, gross against net retention, logo against revenue churn, blended against paid CAC, payback on gross margin, burn multiple on net new ARR, LTV on contribution margin, the Rule of 40's margin, the magic number's 4), whether the deck, model and update agree, and which metrics a fund at the founder's stage usually expects. Every ratio comes from the calculator's metrics_check. An adversarial review has independent lenses make a skeptical partner's definitional attacks and a refute pass drop what the founder's material answers; survivors become a ranked fix list. Use when a founder says are my metrics ready, check my ARR, is this NRR right, what is our burn multiple, CAC payback or LTV/CAC, do my metrics match across the deck and the model, or what metrics does a Series A fund expect. No score, no firm named as a fit. Never invents numbers. Not investment advice.
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
  - The ask, ownership after the round, the SAFE stack, the pool and the runway a priced round buys: the vc-deal-math
    skill. A runway with no raise, or on a SAFE or note raise, and how much to raise: the vc-round-sizing skill.
  - Writing the update itself, with the same metric definitions every time: to current investors, the
    vc-current-investor-update skill; to investors the founder hopes to raise from, the vc-prospective-investor-update
    skill. This skill checks whether each definition is the one investors expect.
  - Every other claim in the materials (customers, team, market, competition): the vc-claims-check skill, whose steps
    this skill follows for metrics.
  - The story and the one-liner: the vc-positioning skill. One equity question with no metrics: the equity-calculator
    skill.
  - A slide-by-slide review of the whole deck: the vc-deck-review skill.
  - Market size, built bottom-up: the vc-market-sizing skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess. When the founder gives a file the agent can
read (a PDF, HTML, a slides export, Markdown), read it yourself and list what it holds place by place (slide by slide
for a deck), in the file's own words, so the founder sees what was read from each. A place you could not read (a slide
that is only a picture, a page whose text did not come out, a file that opened only in part) is listed as not read and
asked for, never filled in from its title or the places around it, and a figure is never read off a chart or a picture.
Ask only for what you could not read and what the file does not show (speaker notes, the figures behind a chart, an
input below that it leaves out), and never ask the founder to paste what you already read.

1. Every document with metrics in it (deck, model or KPI tab, investor update, one-pager), each named and with its
   places marked (slide, tab, paragraph), so every metric can be quoted with where it appears.
2. For recurring revenue, one period the founder names (a month, a quarter or a year): recurring revenue at the start,
   and in the period new, expansion, contraction and churned recurring revenue, said to be monthly (MRR) or annual
   (ARR) figures; for a period longer than a month, the expansion, contraction and churn of the starting customers
   alone; the latest month's total revenue and its one-time (setup, services, hardware) and usage parts.
3. For the same period: customers at the start, customers lost, customers won and how many came through paid
   channels; sales and marketing spend and what it includes; gross margin and what is in cost of revenue; net burn;
   the largest customer's revenue and the total revenue in the same period.
   When the material states LTV, LTV/CAC, a Rule of 40 or a magic number: the average revenue per account (ARPA),
   the contribution margin and which churn the LTV divides by; the revenue growth percent and the profit margin
   percent with its basis (EBITDA, operating, free cash flow or net); two consecutive quarters' revenue (or ending
   ARR) and the earlier quarter's sales and marketing spend.
4. The stage of the raise, the business model (subscription, usage, marketplace, transactions, hardware,
   pre-revenue) and the customer segment (small business, mid-market, enterprise), in the founder's words.
5. Optional: the evidence behind each figure (a billing export, a dashboard, a bank statement).

A missing input does not stop the check. The metric is quoted as stated and marked Needs a source, and the missing
part becomes a bracketed ask (`[contraction MRR in the same month]`), never a plausible figure.

## Definitions

The definitions this skill checks against. "Computed" names the calculator's output; "quoted" means no tool computes
it here, so it is quoted as stated with "not checked: no tool computes this". A row marked ours is this skill's own
wording, unverified.

| Metric                  | Definition                                                                                                                | What a partner checks for                               | Computed or quoted        | Source                                                                                                               |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| ARR                     | Recurring revenue on an annual basis, without one-time fees, services or variable usage fees                              | A month's total revenue times 12 called ARR             | Computed: ARR             | a16z "16 More" (2); a16z "16 Startup Metrics" (2)                                                                    |
| Revenue run-rate        | The latest month's or quarter's revenue, annualised; how marketplaces state size                                          | Presented as ARR                                        | Computed: run-rate        | a16z "16 More" (2)                                                                                                   |
| Bookings, LOIs, GMV     | A contract's value; letters of intent are neither; GMV flows through, revenue is the take                                 | Called revenue                                          | Quoted                    | a16z "16 Startup Metrics" (1, 6)                                                                                     |
| Gross revenue retention | Of recurring revenue at the start of a period, the share kept after downgrades and cancellations, no expansion            | Expansion netted in                                     | Computed: GRR             | Bessemer                                                                                                             |
| Net revenue retention   | The same with expansion from the same starting customers; new customers left out                                          | New customers counted in                                | Computed: NRR             | Bessemer (gross against net); Skok; leaving new customers out, and counting them in as the mistake: ours, unverified |
| Gross revenue churn     | Recurring revenue lost (downgrades and cancellations) over recurring revenue at the start                                 | Only the net figure shown                               | Computed                  | a16z "16 Startup Metrics" (11)                                                                                       |
| Net revenue churn       | Revenue lost less expansion, over recurring revenue at the start                                                          | Shown alone, it understates the losses                  | Computed                  | a16z "16 Startup Metrics" (11)                                                                                       |
| Logo churn              | Customers lost over customers at the start of the period                                                                  | "Churn" with no basis                                   | Computed                  | a16z "16 Startup Metrics" (11); Skok                                                                                 |
| CAC                     | Full acquisition cost over new customers (blended); over customers from paid channels (paid)                              | Costs left out; blended only                            | Computed: CAC             | a16z "16 Startup Metrics" (8)                                                                                        |
| CAC payback             | Months for new recurring revenue, after gross margin, to repay acquisition spend                                          | Worked on revenue, not margin                           | Computed: payback         | Bessemer (margin-adjusted); the formula is ours, unverified                                                          |
| Burn multiple           | Net burn over net new ARR, for the same period                                                                            | New ARR instead of net new; gross burn                  | Computed: burn multiple   | Sacks                                                                                                                |
| Net and gross burn      | Net: spend less incoming cash; gross: spend alone                                                                         | Gross presented as the burn                             | Quoted (runway: step 4)   | a16z "16 Startup Metrics" (12)                                                                                       |
| Gross margin            | Revenue less cost of revenue, over revenue                                                                                | What is in cost of revenue left unsaid                  | Quoted (used for payback) | a16z "16 Startup Metrics" (3); Bessemer                                                                              |
| Growth                  | Compounded monthly growth rather than the simple average of monthly rates                                                 | A simple average                                        | Quoted                    | a16z "16 Startup Metrics" (10)                                                                                       |
| Active users            | A defined action, applied the same way every period                                                                       | "Active" undefined                                      | Quoted                    | a16z "16 Startup Metrics" (9); a16z "16 More" (12)                                                                   |
| Customer concentration  | The largest customer's revenue over total revenue, same period                                                            | Not shown                                               | Computed: concentration   | a16z "16 More" (14)                                                                                                  |
| LTV                     | What one account earns after margin over its expected life: ARPA times margin over the period's churn, undiscounted       | Revenue or gross margin in place of contribution margin | Computed: LTV             | a16z "16 Startup Metrics" (5), its one-month formula; churn basis, longer periods, no discounting: ours, unverified  |
| LTV/CAC                 | LTV over blended CAC                                                                                                      | An LTV on revenue; a CAC with costs left out            | Computed: LTV/CAC         | a16z "16 Startup Metrics" (5), a contribution-margin LTV over CAC; blended CAC: ours, unverified                     |
| Rule of 40              | The founder's revenue growth percent plus a profit margin percent, the margin's basis named                               | The margin unnamed, or gross margin in its place        | Computed: Rule of 40      | Unverified (a common rule of thumb, its sources not read)                                                            |
| Magic number            | Four times a quarter's revenue change over the prior quarter's sales and marketing spend; on ARR, the change with no four | The four left out; the same quarter's spend             | Computed: magic number    | Unverified (a common definition, its sources not read)                                                               |

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

With a subagent tool (the Agent or Task tool), run the five lenses as subagents (Stage A) and one refute subagent per
objection (Stage B), however short the material; the fallback below is only for a session without that tool. Without a
subagent tool, run Stage A of the adversarial review first, before step 1, as "How to run the lenses" says, so the
lenses do not anchor on the tool's output; step 7 then starts at the quote check.

1. **List every metric word for word,** with its document and place: revenue, ARR, growth, retention, churn,
   customers, users, CAC, payback, margin, burn, efficiency ratios. One metric per row; a metric stated in three
   places is one row with three places.
2. **Name the definition each line uses,** from the table above, only as far as the line itself says. A line with no
   definition or no period is Needs a source with a bracketed ask (`[the period this NRR covers]`).
3. **Agreement across the documents:** follow vc-claims-check step 4 as written. Compare as stated; compute no
   difference; never convert. Lines in different forms (MRR against ARR, a month against a year) are compared only by
   the calculator, each in a call for its own period (step 4), when the founder gives the parts; otherwise mark the
   metric Needs a source and ask for one figure, in one form, with its period.
4. **The calculator.** Pass the founder's parts and every stated figure the tool can check from them to
   `equity_metrics_check` (from the command line, `equity_calculator metrics_check`), money and percents as strings,
   customer counts and `period_months` as whole numbers, never strings:
   - **One call per document's version of the figures,** each with only that document's stated figures. Never match a
     figure against a tool value by eye across documents.
   - The report labels every stated figure "the deck says", whatever the call's document. When relaying a check row,
     name that call's document instead ("the model says", "the update says"); that is relabelling, not arithmetic.
   - With no recurring revenue at all, a stated burn multiple and its net burn are not passed: the multiple falls
     under the pattern table's row for a burn multiple before there is revenue. Parts that need no recurring revenue
     (a month's revenue, customers, spend) still go in a call; make no call only when nothing is left to pass.
   - Every flow figure in one call is for the same period, `period_months`. When the founder's burn and revenue
     movements cover different periods, ask for one period; never prorate.
   - A stated retention or churn figure goes in a call whose `period_months` is the period the document states for
     it (`period_months` 1 for a monthly figure), one call per period. With no stated period, or no parts for that
     period, it is not passed: mark it Needs a source with `[the period this figure covers]` or `[that period's
parts]`.
   - Say whether recurring figures are monthly or annual (`recurring_unit`). The tool converts MRR to ARR; the model
     never does.
   - A churn figure with no basis goes in with `stated_churn_basis` left `unlabelled`: the tool checks it against
     every basis it can compute, one row per basis. Those rows are one check: the churn is a calculator mismatch only
     when no basis row is consistent. When one is, it is not a mismatch; it is Will be discounted under the pattern
     table's row for "Churn" with no basis, with every basis row quoted in the tool's values.
   - For a period longer than a month, pass the starting customers' own movements in the `cohort_*` fields, so
     retention leaves out customers won during the period; without them, say the tool's `cohort_rule` assumption row
     applies and ask for those movements. Without them, the tool's retention values are not offered as replacement
     figures for a slide: the fix is the bracketed ask for the starting customers' movements.
   - `stated_cac` is checked against blended CAC only. A CAC the document labels paid is not passed: quote it beside
     the tool's paid CAC row with "not checked: the tool checks blended CAC only", and compare neither by eye.
   - Net burn goes into a call only when that call's document states a burn multiple, or the founder's stage row
     expects one. A stated burn alone is quoted: the tool checks no stated burn.
   - A stated burn multiple when net new ARR or net burn is zero or below gets a `not_checked` row with no computed
     figure, and the flag (`burn_multiple_not_defined` or `no_net_burn`) says why; the overall verdict is then never
     consistent. It is not a calculator mismatch: it is Will be discounted under the pattern table's row for a burn
     multiple on new ARR when `stated_burn_multiple_uses_new_not_net_arr` is beside it, and Needs a source with
     `[net burn and net new ARR for a period where both are above zero]` otherwise.
   - A stated percent, months or multiple that is the tool's figure rounded to the places the document writes is
     consistent, past the tolerance or not, because people write figures rounded to the places they show (9 months
     against the tool's 9.40 months; a 4% churn against 4.4%, but not against 4.6%); its row says so ("rounds to the
     deck's"). Those places decide it, so pass each such figure as text with exactly the places the document writes
     ("9", "9.0", and a document's `0.0%` as "0.0"). Money keeps the tolerance alone. The verdict is the tool's;
     `consistent_beyond_rounding` names a figure that holds by the tolerance alone, and goes to the answer as the
     Flags table says.
   - A net revenue churn below zero (expansion above the revenue lost) is passed as stated, with
     `stated_churn_basis` `net_revenue` or left unlabelled; a gross retention above 100% is passed too, and comes back
     a mismatch unless it is within the tolerance of the computed figure or its rounding.
   - A stated figure whose parts the founder did not give is left out of the call, because the tool refuses the whole
     call for it: mark it Needs a source with a bracketed ask for the missing parts, and make the call with the rest.
     A refusal that comes anyway is relayed with the parts it names.
   - Each code in the result's `flags` goes to the answer as a question a partner is likely to ask, in the words of
     the Flags table below. When a line of the material already does what that row's "What to change" says, relay
     the flag as answered and quote that line. A benchmark flag is relayed for the tool value it was raised on only;
     a stated figure is never set against the benchmark by eye.
   - Give `customer_segment` only as the founder states it; it sets the payback benchmark the tool's assumption row
     quotes.
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point
     of its `rounded` value two places to the right, keeping every digit (0.950000 is 95.0000%, 0.875000 is 87.5000%),
     which is what the command line's report prints. That is a change of notation, not a calculation; never round it.
     A multiple keeps its six decimals (7.500000x) and money its cents ($1,200,000.00), never abbreviated ($1.2M).
   - Deal terms of a priced round (the raise, valuation, percent sold, use of funds and the runway it buys) go to
     `equity_deal_check` as the vc-deal-math skill says. A runway with no raise, a runway on a SAFE or note raise and
     that raise's use-of-funds lines go to `equity_runway_plan` (the no-raise row, or the raise as a raise option that
     carries its stated runway and its use-of-funds lines), as the vc-round-sizing skill calls it; with no cash or burn
     given, ask for them. On a SAFE or note raise, the `plan` case's phases are the founder's own figures: today's
     monthly spend and revenue as the first phase, from month 1, and each change the founder plans (more spend after the
     raise, say) as a later phase from the month the founder names, each asked for by name when missing
     (`[planned monthly spend and revenue, from which month]`), never assumed. Until a planned change's start month, its
     monthly spend and its monthly revenue are all given, make no runway call and give no runway figure; mark the runway
     line "not checked: waiting for [the month the planned spend starts]" while the month is missing, "not checked:
     waiting for [the planned monthly spend from that month]" while the month is given and the spend is missing, or "not
     checked: waiting for [the planned monthly revenue from that month]" while only the revenue is missing. No deal
     term, runway or use-of-funds line goes to this tool, `equity_metrics_check`.
   - A market size goes to `equity_market_sizing` as the vc-market-sizing skill says, never to this tool.
   - LTV, LTV/CAC, the Rule of 40 and the magic number go to this tool from the founder's parts, never worked by
     hand: `arpa` in `recurring_unit`, with `contribution_margin_percent` (else `gross_margin_percent`, which
     `ltv_on_gross_margin` names) and `ltv_churn_basis`, the churn the founder's LTV divides by (`gross_revenue` by
     default, `net_revenue` or `logo`; ask which when the material does not say), in a call whose `period_months` is
     that churn's period; `revenue_growth_percent` and `profit_margin_percent` with `profit_margin_basis`, each the
     founder's own figure, never worked from the period's parts; `quarter_revenue` and `prior_quarter_revenue` (or
     `quarter_ending_arr` and `prior_quarter_ending_arr`) with `prior_quarter_sales_marketing_spend`. The Rule of 40's
     and the magic number's parts do not depend on `period_months`: send them once, in the call that carries the
     document's other figures; when they are the only figures, the call still needs `period_months`, so ask for
     `[the period, in months, the document's figures cover]` rather than picking one. Each missing part is a bracketed
     ask (`[average revenue per account a month]`, `[which margin the Rule of 40 uses]`), never assumed.
     The tool refuses LTV with no margin, or with no churn above zero on its basis: that LTV is Needs a source. No
     benchmark is set for any of the four, so none is set against a line by eye.
   - Growth rates and every other metric the table marks quoted: quote as stated with "not checked: no tool computes
     this", and never compute, convert or round one.
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
   text; no score, no "ready" or "not ready", no raise-or-wait call; no sentence speaks as an investor or names a firm
   as a fit or a voice (firms and authors appear only as cited sources).

## Definitional patterns

Signals, not rules: a founder may have a reason. Flag, explain, and let them decide. A row marked unverified has no
public source behind it that this skill's authors read.

| Pattern                                                        | Why a partner is likely to discount it                                                   | Fix                                                                       | Source                                             |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------- |
| "ARR" that is a month's total revenue times 12                 | A run-rate, which one-time revenue in that month can inflate                             | Call it a run-rate, or state ARR from recurring revenue alone             | a16z "16 More" (2)                                 |
| ARR that includes setup, services, hardware or usage fees      | Non-recurring revenue presented as recurring                                             | ARR from recurring revenue only; other revenue on its own line            | a16z "16 Startup Metrics" (2); a16z "16 More" (2)  |
| Net retention that counts revenue from new customers           | Growth presented as retention                                                            | Net retention from the starting customers only, with the period           | Unverified                                         |
| "Churn" with no basis (customers or revenue, gross or net)     | Each basis tells a different story                                                       | Name the basis, and show logo and gross revenue churn beside net          | a16z "16 Startup Metrics" (11); Skok               |
| Net revenue churn shown alone                                  | Expansion can hide what is lost                                                          | Show gross revenue churn beside it                                        | a16z "16 Startup Metrics" (11)                     |
| CAC that leaves out costs (referral fees, credits, discounts)  | Understates what growth costs                                                            | Count every acquisition cost; say what is in the spend                    | a16z "16 Startup Metrics" (8)                      |
| Blended CAC only                                               | Says nothing about whether paid growth works                                             | Show paid CAC beside blended                                              | a16z "16 Startup Metrics" (8)                      |
| CAC payback worked on revenue, not gross margin                | Understates how long acquisition takes to repay                                          | Work it on gross-margin-adjusted new recurring revenue                    | Bessemer                                           |
| Burn multiple on new ARR (churn left out), or on gross burn    | Flatters efficiency                                                                      | Net burn over net new ARR, for one period                                 | Sacks                                              |
| A burn multiple before there is revenue                        | The ratio does not compute                                                               | Drop it; show net burn by month                                           | Sacks                                              |
| Monthly growth as the simple average of monthly rates          | Overstates growth in a growing business                                                  | Compounded monthly growth, or each month's figure                         | a16z "16 Startup Metrics" (10)                     |
| LTV on revenue or gross margin rather than contribution margin | Sets too high a ceiling on acquisition spend                                             | LTV on contribution margin, or 12- and 24-month value to date             | a16z "16 Startup Metrics" (5)                      |
| A Rule of 40 that names no margin, or adds gross margin        | Gross margin is not a profit margin, so the sum flatters the company                     | Name the margin (EBITDA, operating, free cash flow or net) beside the sum | Unverified                                         |
| A magic number from one quarter's change, without the four     | A quarter's new revenue set against a year's worth of efficiency reads low or is misread | Annualise the change, or say it is the quarterly figure                   | Unverified                                         |
| "Active users" with no stated action                           | Nothing to check                                                                         | Name the action and the period, and keep the definition fixed             | a16z "16 Startup Metrics" (9); a16z "16 More" (12) |
| A ratio with no period ("NRR 120%")                            | Cannot be compared with anything                                                         | State the period beside every ratio                                       | Unverified                                         |

## Adversarial review

The steps check every metric evenly; a partner does not. They test the definitions behind the two or three metrics the
story rests on, and test those hard. This review makes those attacks, then a second pass throws out every attack the
founder's material answers, so the founder spends their time on real exposure.

### Stage A: attack

Each lens tests one family of definitions and is named by it. The lenses are frameworks, never people: none is a named
investor, firm or author, and none speaks in the first person as an investor.

| Lens                    | What it tests                                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Revenue definitions     | Whether ARR, run-rate, bookings, GMV and revenue are each named for what they are, with a period                                                                          |
| Retention and churn     | The basis of every churn and retention figure, its period, and whether new customers or expansion hide losses                                                             |
| Acquisition and payback | What CAC counts, blended against paid, and whether payback is worked on margin                                                                                            |
| Burn and efficiency     | Net or gross burn, net new or new ARR, and whether both are for the same period                                                                                           |
| Stage fit               | Which metrics a fund at the founder's stage expects that the material does not show; its objection quotes the line that states the stage, or the metrics slide as a whole |

Every lens gets the same brief, with its own name and test filled in, and the Definitions table:

- You test one thing: the lens's name and what it tests. Write in the third person ("a partner is likely to ask how
  this ARR is defined because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here and the definitions. Bring in no outside fact about the company, its
  market or its competitors, and do no arithmetic.
- Return at most three objections, strongest first. For each: the line it is about, quoted word for word with its
  document and place; the definition a partner is likely to test it against; and how much it hurts (ends the meeting,
  weakens it, or minor).
- A reason you cannot tie to a line the founder wrote is not an objection. List it apart as a gap, worded as a
  question. Never turn an objection into a gap because another line may answer it.
- Do not judge whether another line of the material answers an objection: raise it anyway, and the refute pass
  decides. Return "nothing found" only when no line of the material gives this lens an objection worth a partner's
  time.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the lenses as parallel
subagents, however short the material. Give each one only the founder's material, the Definitions table and its lens
brief (the Stage fit lens also gets the Stage expectations table, since it tests against it): not this skill's other
sections, not the tool's output, not another lens's objections. Without a subagent tool, run Stage A first, before step
1: run the lenses one after another, write each lens's objections down in full before reading the next lens's brief, and
never revise an earlier list. Lenses run this way are less independent than subagents, and the same agent then judges
them in Stage B, so the answer says so.

**The calculator's mismatches** from step 4 do not go through the lenses, and none is refuted: the calculator
computed it. Each is added to the ranked fix list ahead of the tiers, quoting the document's figure with the tool's
value and difference, with the flag that explains it, when one does, as the reason. It carries no tier: how much a gap
hurts depends on its size, which the founder weighs. A stated figure less flattering than the tool's value (an ARR or
retention below it; a churn, CAC, payback, burn multiple or concentration above it) understates: it goes in the minor
tier at most. A percent, months or multiple that is the tool's figure rounded to the places the document writes is
consistent, so a mismatch of one is never that rounding and, when no flag explains it as another definition, may rest
on other parts or another working. Money is checked by the tolerance alone, so an ARR or CAC mismatch that no flag
explains may still be the founder's rounding. The fix for either asks
`[how the model works this figure, unrounded]`. A `not_checked` row is not a mismatch (step 4). An unlabelled churn with one consistent basis row is not a mismatch
(step 4).

### Check the quotes

Before Stage B, check every objection's quote against the founder's material. A quote that does not appear there word
for word (spacing and line breaks aside) is dropped as not grounded. When two lenses raise the same objection about
the same line, merge them and keep both lens names. An objection about a line the calculator already found a
mismatch on merges into that mismatch's entry and keeps the lens name. Gaps from every lens go to the open asks.

### Stage B: refute

Each objection gets its own refute pass. With a subagent tool, launch one subagent per objection in a single message,
so they run in parallel; never put two objections in one subagent, and never judge them in the main agent instead. Give
each the founder's material, that one objection, the Pattern column of this skill's pattern table and of
vc-claims-check's discount table, and everything from "The refute brief:" to the end of this stage, and nothing else.
Without a subagent tool, decide the objections one at a time against the same brief.

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

The refute pass invents nothing on the founder's behalf. After the passes, spacing and line breaks aside, an answering
line that is not in the material word for word does not drop the objection, and neither does one that is the objected
line itself.

### The ranked fix list

Order the kept objections in three tiers, most damaging first: **ends the meeting**, **weakens it**, **minor**. The
calculator's mismatches lead the list ahead of the tiers, with no tier (Tier: "none, the founder weighs the gap"),
except an understated figure, which is minor at most (Stage A). Within a tier, an objection raised by more than one lens
comes first. The tier is a judgment, not a probability: give no percentages and no score. Each entry is one fix: the
document and place, the line quoted word for word, why a partner is likely to read it that way in one or two plain
sentences, and the change to make, using only the founder's facts, a tool value or a bracketed ask.

## Flags

The tool's `flags` holds codes only; this table is what each one means for the founder. A flag is a question to be
ready for, never an error.

| Flag                                        | What it means for the founder                                                                                                                                | What to change or prepare                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| `stated_arr_matches_run_rate`               | The stated ARR agrees with 12 times the month's total revenue, not with recurring revenue                                                                    | Call it a run-rate, or restate ARR from recurring revenue                     |
| `arr_movement_and_month_disagree`           | The ARR movement's ending ARR and the latest month's ARR differ by more than the tolerance                                                                   | Say which figure the slide shows and why the two differ                       |
| `run_rate_includes_non_recurring`           | The month has one-time or usage revenue, so run-rate and ARR differ                                                                                          | Show both, each named                                                         |
| `stated_nrr_includes_new`                   | The stated net retention agrees with ending over starting revenue, which counts customers who were not there at the start                                    | Restate net retention on the starting customers                               |
| `expansion_hides_churn`                     | Net revenue churn is zero or below while gross revenue churn is above zero                                                                                   | Show gross revenue churn beside net                                           |
| `churn_basis_unlabelled`                    | The stated churn names no basis; the tool checked it against each (a churn below zero only as net revenue churn)                                             | Name the basis on the slide                                                   |
| `blended_cac_only`                          | No paid-channel split was given                                                                                                                              | Be ready with paid CAC                                                        |
| `payback_not_margin_adjusted`               | No gross margin was given, so payback is on revenue only                                                                                                     | Give gross margin; a partner works payback on margin                          |
| `stated_payback_not_margin_adjusted`        | The stated payback agrees with the revenue payback, not the margin one                                                                                       | Restate it on gross margin                                                    |
| `stated_burn_multiple_uses_new_not_net_arr` | The stated multiple agrees with net burn over new ARR, churn left out (also beside a multiple the tool cannot work)                                          | Restate it on net new ARR                                                     |
| `ltv_on_gross_margin`                       | No contribution margin was given, so the tool's LTV is on gross margin                                                                                       | Give the contribution margin; a partner works LTV on it                       |
| `contribution_margin_above_gross_margin`    | The contribution margin given is above the gross margin, though it takes out more costs; the two may be swapped or mislabelled                               | Check which margin is which; LTV is on the contribution margin as given       |
| `stated_ltv_uses_revenue_not_margin`        | The stated LTV or LTV/CAC agrees with the figure on revenue alone, no margin taken out                                                                       | Restate it on margin                                                          |
| `stated_ltv_uses_gross_margin`              | The stated LTV agrees with the figure on gross margin, not on the contribution margin given                                                                  | Restate it on contribution margin                                             |
| `rule_of_40_margin_basis_unlabelled`        | The profit margin in the Rule of 40 names no basis                                                                                                           | Name the margin on the slide                                                  |
| `stated_rule_of_40_uses_gross_margin`       | The stated Rule of 40 agrees with growth plus gross margin, not the profit margin given                                                                      | Restate it on the profit margin, and name it                                  |
| `stated_magic_number_not_annualised`        | The stated magic number agrees with the quarter's change without the four that annualises it                                                                 | Restate it with the four, or label it quarterly                               |
| `consistent_beyond_rounding`                | The stated figure holds by the tool's tolerance alone: it is not the tool's figure rounded to its own places                                                 | Quote the tool's figure; a partner recomputing gets it                        |
| `burn_multiple_not_defined`                 | Net new ARR is zero or below in the period                                                                                                                   | Drop the multiple; show net burn and the ARR movement                         |
| `no_net_burn`                               | Net burn is zero or below in the period                                                                                                                      | Say the company is not burning cash in that period                            |
| `payback_above_band`                        | Payback on gross margin is at or above the tool's benchmark for the segment (with no margin given, the revenue payback already is, so the margin one is too) | Be ready to say why; quote the tool's assumption row, a benchmark, not a rule |
| `burn_multiple_above_band`                  | The multiple is at or above the tool's benchmark                                                                                                             | Be ready to say why; quote the tool's assumption row, a benchmark, not a rule |
| `net_revenue_churn_above_band`              | One month's net revenue churn is above the tool's benchmark                                                                                                  | Be ready to say why; quote the tool's assumption row, a benchmark, not a rule |

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
   it, or not grounded). Then each lens with what it returned, "nothing found" included, and how many refute subagents
   ran. When the lenses ran in one agent, say they are less independent than separate subagents. When the refute pass
   ran per lens (lean mode), say so, say it is less independent than one subagent per objection, and say the founder may
   ask for the full pass.
3. **Metrics table:** #, Metric (quoted), Where, Definition it uses, The tool gives, Agrees across the documents?,
   Verdict, Fix. Order by verdict, Contradicted first.
4. **Calculator results,** per call: which document's figures it used, each check row in the tool's values with that
   document named in place of "the deck says", each flag as the question a partner is likely to ask with its "What to
   change or prepare" from the Flags table, and the assumption rows the answer leans on, each with the source and date
   the tool's row gives, never a source from the Definitions table. When no `cohort_*` fields were passed, name the
   `cohort_rule` row and its setting.
5. **Stage expectations:** the row for the founder's stage and model, each metric Present or Missing. A Missing row
   carries its bracketed ask in the same row; a metric whose parts were given is Missing with the fix: show it with the
   tool's values.
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
skill's own judgment, unverified. LTV's one-month formula on contribution margin and a contribution-margin LTV/CAC
are a16z's (item 5, paraphrased); the churn basis, longer periods, leaving out discounting and blended CAC are the
tool's own, unverified. The Rule of 40 and the magic number are common definitions for which no source was read, so
none is credited and the tool's assumption rows mark them unverified. The two-stage review (attack, then refute with
the founder's own material) is this repository's own method.

## Limits

- Not investment, legal, tax or accounting advice. It does not say whether to raise, when, or at what valuation.
- It gives no score and no verdict on readiness: no rating out of any number, no "ready" or "not ready", no "raise now
  or wait".
- It never names a firm or person as an investor to approach or as one the metrics fit, never role-plays or speaks
  as a named investor, firm or author, names firms and authors only as cited sources, and does no investor research.
- It never invents, fills in or strengthens a figure, a definition or evidence, in a fix or in a refute pass.
- No arithmetic outside the equity calculator's tools: no MRR-to-ARR conversion, sum, ratio or growth rate by hand.
  Growth rates are quoted, not computed; LTV, LTV/CAC, the Rule of 40 and the magic number come from the tool, on
  the founder's parts, with no benchmark.
- Benchmarks appear only as the tool's assumption rows, with their sources and dates; they vary by sector, segment and
  year.
- It sees no billing system, ledger or bank data and verifies no evidence; a partner will ask to see it.
- The review predicts likely definitional attacks; a real partner may raise others.
- It works from the founder's text and sends nothing anywhere.
