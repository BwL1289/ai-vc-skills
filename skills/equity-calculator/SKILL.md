---
name: equity-calculator
description: Exact startup equity arithmetic with the equity_calculator command or MCP tools. Use when someone asks if a fundraise or a stake is worth it (Paul Graham's equity equation), how much equity to offer a hire, how big an option pool to add (the option-pool shuffle), how SAFEs or convertible notes convert in a priced round (caps, discounts, MFN, interest), how a stake dilutes over several rounds, how many shares have vested (cliff, termination, acceleration), or who gets what at an exit (liquidation preferences, participation, caps). deal_check checks a raise's valuation, percent sold, ownership and runway; runway_plan shows how long each raise lasts and which milestones it reaches; metrics_check checks ARR, retention, churn, CAC payback, burn multiple; market_sizing builds TAM, SAM and SOM bottom-up; instrument_compare sets a priced round beside a note; pool_plan sizes a pool from a hiring plan; raise_pipeline works the room left in a round and a funnel's term sheets. Run it instead of doing arithmetic by hand.
---

# Equity calculator

The calculator works fourteen scenarios exactly (rational arithmetic, no floating point) and returns every value, the
exact fractions, and the assumptions each result rests on, each with its source. Use it for the numbers; do not
work them out by hand, and do not round or re-derive what it returns.

## Which scenario answers which question

| Question                                                                                                        | Scenario             | MCP tool                    |
| --------------------------------------------------------------------------------------------------------------- | -------------------- | --------------------------- |
| Is selling n% worth it for an m-times better average outcome?                                                   | `investor`           | `equity_investor`           |
| What is the most of the company a hire is worth, and what should the offer be?                                  | `employee`           | `equity_employee`           |
| How many pool shares does a target pool need, and what is the price per share?                                  | `pool`               | `equity_pool`               |
| How do SAFEs and notes convert in a priced round, and what is the cap table after it?                           | `round`              | `equity_round`              |
| What is my stake after these rounds?                                                                            | `dilution`           | `equity_dilution`           |
| How many shares have vested at month M, and what do they cost or are they worth?                                | `vesting`            | `equity_vesting`            |
| Who gets what when the company is sold for E?                                                                   | `waterfall`          | `equity_waterfall`          |
| Does a deck's raise, valuation, ownership and runway add up before a VC checks it?                              | `deal_check`         | `equity_deal_check`         |
| How long does each raise last on our plan and a downside, and which milestones does it reach?                   | `runway_plan`        | `equity_runway_plan`        |
| Do our ARR, retention, churn, CAC payback and burn multiple match their parts before a VC checks them?          | `metrics_check`      | `equity_metrics_check`      |
| What are our TAM, SAM and SOM bottom-up, do they match the deck, and which assumption moves them most?          | `market_sizing`      | `equity_market_sizing`      |
| A priced round now or a convertible note now: who owns what after the next round, and who gets what at an exit? | `instrument_compare` | `equity_instrument_compare` |
| What pool does our hiring plan to the next round need, beside the pool the term sheet asks for?                 | `pool_plan`          | `equity_pool_plan`          |
| How much of the round is left, how many term sheets does our funnel give on our rates, when do we start?        | `raise_pipeline`     | `equity_raise_pipeline`     |

A founder's question about a whole raise goes to the review built for it, which runs these tools and explains what
they return: a deck's ask, ownership after the round and runway to the vc-deal-math skill; how much to raise on a
phased plan to the vc-round-sizing skill; traction metrics to the vc-metrics-readiness skill; a market slide to the
vc-market-sizing skill; a term sheet to the vc-term-sheet-review skill; an update to current investors to the
vc-current-investor-update skill; a hiring plan against a term sheet's pool ask to the vc-option-pool-plan skill; whom
to pitch, in what order, and whether the pipeline fills the round to the vc-raise-plan skill. This skill answers one
scenario on its own.

## Running it

**MCP tools** (`equity_calculator_mcp`). Each scenario tool takes one argument, `inputs`, an object with that
scenario's fields, and returns the same JSON text as `equity_calculator <scenario> --json`:

```json
{ "inputs": { "equity_percent": "7", "outcome_multiplier": "1.10" } }
```

| Scenario           | Fields (required in bold)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| investor           | `equity_percent` or (`pre_money` and `investment`); `outcome_multiplier` or `growth_percent`; `holder_percent`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| employee           | `outcome_multiplier` or `gain_percent`; `offered_percent`; `annual_cost` with `valuation`; `margin_percent`; `cost_years`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| pool               | **`fully_diluted_shares`**, `unissued_pool_shares`, **`pre_money`**, **`investment`**, **`target_pool_percent`**, `pool_timing` (`pre_money` or `post_money`), `share_rounding` (`exact` or `whole_shares`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| round              | **`fully_diluted_shares`** (SAFEs and notes left out: see below), `unissued_pool_shares`, **`pre_money`**, **`investment`**, `target_pool_percent`, `pool_timing`, **`instruments`**: a list of `{"kind": "safe", "purchase_amount", "valuation_cap", "discount_percent", "mfn"}` and `{"kind": "note", "principal", "interest_rate_percent", "months_outstanding"` or `"issue_date"` and `"conversion_date", "compounding", "stub_rule", "day_count", "valuation_cap", "discount_percent", "interest_paid_in_cash"}`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| dilution           | **`holder_percent`**, **`rounds`**: a list of `{"investor_percent"` or `"pre_money"` and `"investment", "pool_percent"}`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| vesting            | **`grant_shares`**, **`month`**, `total_months`, `cliff_months`, `strike_price`, `common_price`, `termination_month`, `acceleration` (`none`, `single_trigger`, `double_trigger`), `acceleration_percent`, `acceleration_base` (`unvested` or `grant`), `change_of_control_month`, `share_rounding`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| waterfall          | **`exit_amount`**, **`common_shares`**, **`classes`**: a list of `{"shares", "invested", "preference_multiple", "rank", "participation"` (`none`, `full`, `capped`), `"cap_multiple"}`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| deal_check         | **`investment`**; `pre_money`, `post_money` or `stated_investor_percent` (at least one); `fully_diluted_shares` (SAFEs and notes left out: see below), `unissued_pool_shares` or `unissued_pool_percent`, `target_pool_percent`, `pool_timing`, `instruments` (the same `{"kind": "safe", "purchase_amount", "valuation_cap", "discount_percent", "mfn"}` and `{"kind": "note", "principal", "interest_rate_percent", "months_outstanding"` or `"issue_date"` and `"conversion_date", "compounding", "stub_rule", "day_count", "valuation_cap", "discount_percent", "interest_paid_in_cash"}` objects as round); `holder_percent` or `holder_shares`, `stated_holder_percent`; `cash_on_hand`, `planned_monthly_gross_burn`, `planned_monthly_revenue`, `current_monthly_gross_burn`, `current_monthly_revenue`, `stated_runway_months`; `use_of_funds`: a list of `{"amount"}` or `{"percent"}`; `tolerance_points`, `tolerance_percent`, `dilution_band_percent`, `runway_band_months`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| runway_plan        | **`cash_on_hand`**, `cash_floor`, **`cases`**: the plan first, `{"name": "plan", "phases"}` with `phases` a list of `{"from_month", "gross_burn", "revenue"}`, then optionally `{"name": "downside"}` or `{"name": "lean"}` with its own `phases` or `"revenue_percent_of_plan"` and/or `"gross_burn_percent_of_plan"`; `raises`: a list of `{"amount", "lands_month", "stated_runway_months", "stated_runway_from"` (`today` or `landing`, only with `stated_runway_months`), `"use_of_funds"` (a list of `{"amount"}` or `{"percent"}`)`}`; `milestones` (months from today), `months_to_raise`, `stated_runway_months` (with no raise), `tolerance_points`, `tolerance_percent`, `runway_band_months`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| metrics_check      | **`period_months`** (1 to 36, the one period every flow figure covers), `recurring_unit` (`monthly` or `annual`); `starting_recurring` with the period's `new_recurring`, `expansion_recurring`, `contraction_recurring`, `churned_recurring`, and the starting customers' own `cohort_expansion_recurring`, `cohort_contraction_recurring`, `cohort_churned_recurring`; `month_total_revenue` with `month_one_time_revenue`, `month_usage_revenue`; `customers_start`, `customers_lost`, `customers_new`, `customers_new_paid`; `sales_marketing_spend`, `gross_margin_percent`, `net_burn`; `largest_customer_revenue` with `period_revenue`; what the document states: `stated_arr`, `stated_nrr_percent`, `stated_grr_percent`, `stated_churn_percent` with `stated_churn_basis` (`logo`, `gross_revenue`, `net_revenue` or `unlabelled`), `stated_cac`, `stated_cac_payback_months`, `stated_burn_multiple`, `stated_concentration_percent`; `tolerance_points`, `tolerance_percent`, `customer_segment` (`smb`, `mid_market`, `enterprise`), `payback_band_months`, `burn_multiple_band`, `net_revenue_churn_band_percent`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| market_sizing      | **`segments`**: a list of up to 8 `{"customers", "price", "price_period_months" (1 to 120, the months the price covers; left out or null it is read as 12 and flagged), "units_per_customer", "take_rate_percent", "serviceable_percent", "obtainable_percent"` or `"obtainable_customers"` (the SOM, at most one), `"customers_today"}`; `top_down`: a list of up to 3 `{"amount", "comparable_percent", "compare_to"` (`tam` or `sam`)`}`; `sensitivity`: a list of up to 6 `{"field"` (`customers`, `price`, `units_per_customer`, `take_rate_percent`, `serviceable_percent`, `obtainable_percent`, `obtainable_customers`), `"segment"` (1 is the first), `"values"` (1 to 4)`}`; `population`, `annual_revenue_today`, `som_years` (1 to 20), `som_target`; what the deck states: `stated_tam`, `stated_sam`, `stated_som`; `tolerance_percent`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| instrument_compare | **`founder_shares`**, **`team_shares`** and **`unissued_pool_shares`** (`0` for none), `existing_series` (a list of the same `{"shares", "invested", "preference_multiple", "rank", "participation", "cap_multiple"}` objects as waterfall, each with its own `"preference_multiple"` and `"participation"` always given), `existing_instruments` (the same `{"kind": "safe", "purchase_amount", "valuation_cap", "discount_percent", "mfn"}` and `{"kind": "note", "principal", "interest_rate_percent", "months_outstanding", "compounding", "stub_rule", "valuation_cap", "discount_percent", "interest_paid_in_cash"}` objects as round; a note gives `"months_outstanding"` as of today and its `"compounding"`, never `"issue_date"`, `"conversion_date"` or `"day_count"`); **`investment`**; option A: **`priced_pre_money`**, `priced_target_pool_percent`, `priced_pool_timing`, **`priced_preference`** (`{"standard": true}` only when the founder says standard, else `{"preference_multiple", "participation"` (`none`, `full`, `capped`), `"cap_multiple"}`, either with `"rank"`); option B: `note_valuation_cap`, `note_discount_percent`, **`note_interest_rate_percent`**, **`note_compounding`** (`simple`, `annual`, `monthly`), `note_stub_rule`, **`note_months_to_conversion`**, `note_maturity_months`, `note_interest_paid_in_cash`; **`next_rounds`**: up to 4 alternatives for the one round after today, each worked from today, `{"pre_money", "investment", "target_pool_percent", "pool_timing", "preference"}` (`preference` as `priced_preference`); **`exit_amounts`**: up to 6; `pool_at_exit` (`as_common` or `left_out`) |
| pool_plan          | **`fully_diluted_shares`**, **`unissued_pool_shares`** (`0` for none), `founder_shares` (the founders' own shares among them, for their ownership line), **`pre_money`**, **`investment`**, **`requested_pool_percent`** (the term sheet's pool after the round, created in the pre-money), **`next_round_month`** (1 to 120), **`hires`**: up to 40 `{"role", "start_month" (0 to 120), "grant_shares"` or `"grant_percent"}` (a percent of the post-round fully diluted shares; every hire the same way, never some of each)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| raise_pipeline     | **`round_size`**, `lead_cheque`, `commitments`: up to 40 `{"amount", "kind"}` (`soft` or `firm`, as the founder marks it; soft ones never counted), `pro_rata`: up to 20 amounts, `stages`: up to 8, in order, `{"name", "investors"` (today, each counted once at the furthest stage reached), `"rate_percent"` (the founder's own rate to the next stage; from the last, to a term sheet), `"rate_basis"` (`own` or `benchmark`), `"benchmark_source"}` (needed with `benchmark`), with `term_sheets_wanted`; `runway`: `{"cash_on_hand", "cash_floor", "phases"` (a list of `{"from_month", "gross_burn", "revenue"}`, as runway_plan takes them), `"months_to_raise"}`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

Send money, percents and multipliers as JSON strings (`"7"`, `"1.10"`, `"8000000"`): a JSON number with a decimal
point arrives as a binary float and keeps only about 15 digits. Percents are percents (`"7"` is 7%). Share counts,
customer counts (`customers_start`, `customers_lost`, `customers_new`, `customers_new_paid`) and month counts
(`period_months`, `price_period_months`, `from_month`, `lands_month`, `months_to_raise`, `milestones`, `som_years`,
`note_months_to_conversion`, `note_maturity_months`, a hire's `start_month`, `next_round_month`, and a sensitivity
row's `segment`) and the counts of a funnel (a stage's `investors`, `term_sheets_wanted`) are whole numbers, sent as
JSON integers, never strings; a string is refused.

`fully_diluted_shares` (in `round` and `deal_check`) counts every share before the round, granted options and the
unissued pool included, and leaves SAFEs and notes out: the tool converts them itself. Some cap tables count SAFEs
and notes in their fully diluted total; ask which way the user's does, and pass the tool its own basis. If the
user's total counts them, ask for the total without them, as a bracketed ask,
`[fully diluted shares before the round, SAFEs and notes left out]`; never subtract the SAFE or note shares yourself.

`equity_workbook` exists only when the server was started with `--output-dir DIR`: it takes
`inputs` with its `scenario` tag (`{"scenario": "round", ...}`) and a bare `file_name` ending in `.xlsx` with no control,
format or surrogate character, and writes a new file in DIR; it never overwrites a file. An answer too large for a
workbook cell (a value of 1e300 or more) is refused and no file is made. While saving, the Excel library also writes
and deletes a short-lived file in the system's temporary folder (`TMPDIR` if set), so that folder must be writable.

**Command line** (`equity_calculator`). The same scenarios as subcommands with flags, for example:

```
equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10
equity_calculator round --fully-diluted-shares 10000000 --pre-money 8000000 --investment 2000000 \
    --target-pool-percent 10 --safe "500000 valuation-cap=5000000" --note "250000 interest-rate-percent=6 months-outstanding=18 discount-percent=20"
equity_calculator vesting --grant-shares 48000 --month 30 --strike-price 0.50 --common-price 2
```

`equity_calculator <scenario> --help` lists every flag. `--json` prints the whole result instead of the report, and
`--xlsx PATH` also writes a formatted Excel workbook. Exit code 1 means the inputs were refused or have no answer
(the message says why); exit code 2 means an argument could not be read.

## Answering

1. Pick the scenario, ask for every required input that is missing, by name, and run it. Never fill a gap with a
   figure the user did not give. A value the tool fills in itself (a 48-month vesting schedule, the pool in the
   pre-money) is named in the answer as the tool's default, with how to change it, never as an assumed figure. For `deal_check`, never assume
   one: the raise, the valuation and its label, the share counts, cash, burn and revenue are the founder's own
   figures, so ask for them. For `runway_plan`, never assume one: the phases, the downside or lean percents, the
   milestones, the months to raise, the landing months and the cash floor are the founder's own figures, so ask for
   them. With no months to raise, run without it and quote the `no_time_to_raise_given` flag (each milestone was
   checked at its own month, with no time to raise after it). For `metrics_check`, every part is the founder's
   own figure for one period: never convert MRR to ARR, a quarter to a year or a percent to a count yourself (the tool
   annualises by `recurring_unit`). Each stated retention or churn figure is checked over `period_months`, so set it
   to the period the document's figure covers (1 for a monthly churn, 12 for an annual NRR), run one call per period
   when the document mixes them, and ask when the period is not stated rather than report a mismatch. When the period
   is longer than a month, ask for the starting customers' own expansion, contraction and churn
   (`cohort_expansion_recurring`, `cohort_contraction_recurring`, `cohort_churned_recurring`), or quote the
   `cohort_rule` row. For the payback benchmark, ask who the company sells to (`customer_segment`: `smb`,
   `mid_market` or `enterprise`); never assume it. A stated CAC is checked as blended CAC. For `market_sizing`,
   never assume a customer count, a price, a take rate or a share: each is the founder's own figure with the founder's
   source, so ask for it; a price is sent with the months it covers, never turned into a year by hand. A SOM is best a
   count of customers the founder plans to win; a SOM given only as a percent runs, with the `som_as_percent_only`
   flag (the SOM rests on a share, not a count of customers to win). A top-down figure is a cross-check: it never
   sets the market size. For `instrument_compare`, never assume a term: today's shares by holder group, the raise,
   option A's pre-money and series terms, option B's cap, discount, interest and months until it converts, every next
   round and every exit are the founder's own figures, so ask for them. Each next round is an alternative for the one
   round after today, worked from today, never after the one before. `{"standard": true}` goes in only when the
   founder says the terms are standard. With no next round the tool refuses (`no_next_round_given`): ask for one.
   Show A, B and B - A as the tool gives them and never say which option to take. For `pool_plan`, never assume one:
   the share counts, the round, the requested pool, the next round's month and every hire's start month and grant are
   the founder's own figures, so ask for them; with no hire the tool refuses (`no_hiring_plan_given`). Show the plan,
   the requested pool and requested - plan as the tool gives them and never say which pool to accept. For
   `raise_pipeline`, never assume one: the round, the lead's cheque, each commitment and whether it is soft or firm,
   the pro rata amounts, each stage's investors and rate, the term sheets wanted, and the cash, burn and months to
   raise are the founder's own figures, so ask for them; a stage with no rate or a commitment with no kind is refused
   (`stage_rate_missing`, `commitment_kind_missing`), and a benchmark rate goes in only with the founder's source.
   The expected term sheets are an expectation from the founder's rates, never a forecast.
2. Give the headline numbers as the tool prints them (the `rounded` value with its unit, or the exact fraction when
   precision matters). Do not round them again or recompute them. A value whose unit is `fraction` is a share of the
   whole: show it as a percent by moving the decimal point of its `rounded` value two places to the right, keeping
   every digit (0.166667 is 16.6667%), as the command line's report does; that is notation, not a calculation.
3. Quote the assumptions the result lists. Each has a source; say plainly when it is `unverified` (standard
   arithmetic no cited source fixes, such as every option-pool, note and waterfall convention), and say how to change
   a default when the user's terms differ.
4. A refusal or a tool error is the answer for those inputs: relay the reason and what to change. Never guess a
   number the calculator refused to give.
5. A result's `flags` are codes. The command line's report prints each one's meaning beside it; the MCP result does
   not. Relay a flag with its meaning from the table of the skill built on that tool: vc-deal-math for `deal_check`,
   vc-round-sizing for `runway_plan`, vc-metrics-readiness for `metrics_check`, vc-market-sizing for
   `market_sizing`, vc-deal-math's step 7 for `instrument_compare`, vc-option-pool-plan for `pool_plan`, and
   vc-raise-plan for `raise_pipeline`. A flag
   is a question to be ready for, never an error.
6. The calculator works the arithmetic of the terms given. It does not read a term sheet or a cap table file, and it
   is not legal, tax or investment advice: say so when the question needs either.

## The formulas and their sources

Sources: **PG** is Paul Graham, "The Equity Equation", <https://paulgraham.com/equity.html> (July 2007).
**Altman** is Sam Altman, "Employee Equity", <https://blog.samaltman.com/employee-equity> (April 2014). **YC** is
Y Combinator's post-money SAFE forms (valuation cap, discount, MFN) and their user guide,
<https://www.ycombinator.com/documents>. The **YC seed guide** is Y Combinator, "A guide to seed fundraising",
<https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising> (no date on the page). **a16z** is "16 Startup
Metrics", <https://a16z.com/16-startup-metrics/> (21 Aug 2015), and "16 More Startup Metrics",
<https://a16z.com/16-more-startup-metrics/> (23 Sep 2015). **Bessemer** is "Scaling to $100 Million",
<https://www.bvp.com/atlas/scaling-to-100-million> (21 Sep 2021). **Sacks** is David Sacks, "The Burn Multiple",
<https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200> (23 Apr 2020). **Skok** is David Skok, "SaaS Metrics
2.0", <https://www.forentrepreneurs.com/saas-metrics-2/> (no date on the page). The **YC pitch guide** is Y Combinator,
"How to Pitch Your Company", <https://www.ycombinator.com/library/4b-how-to-pitch-your-company> (no date on the
page). Everything else is standard arithmetic, labelled `unverified` in the results.

- **Investor (PG).** With n the stake sold and m the outcome multiplier, the holders keep R = (1 - n)·m of the whole
  company before. Accept when R > 1, break even at R = 1, reject below. Break-even multiplier m\* = 1/(1 - n), growth
  g\* = n/(1 - n). From amounts, n = I/(V + I) (unverified).
- **Employee (PG).** A hire who multiplies the outcome by i is worth at most n = (i - 1)/i; i < 1 grants nothing.
  Rule of thumb (PG): the salary's stock cost is annual cost × 1.5 years, its stake is that over the valuation, the
  retail stake is n/(1 + margin), and the offer is retail stake minus the salary's stake, floored at 0 (the floor
  unverified).
- **Option pool (unverified).** With FD every pre-round share, U the unissued pool, V the pre-money, I the investment,
  t the target and r = I/(V + I): with the pool in the pre-money, P = (t·FD - (1 - r)·U)/(1 - r - t) new shares and
  price p = (V - t(V + I))/(FD - U); with it in the post-money, p = V/FD and P = max(0, (t(FD + N) - U)/(1 - t)). The
  investor gets N = I/p shares.
- **SAFEs and notes in a round.** Each converts at the lower of its cap price and its discount price, the greater
  number of shares (YC: "convert into the greater of"). A SAFE's cap price is cap / Company Capitalization, which counts
  every pre-round share and every converting share but not the new pool (YC). The discount price is the round price
  × (1 - discount) (YC). A note's cap is taken over the pre-round shares (unverified). The pre-money buys every
  pre-round and converted share and, with the pool in the pre-money, the new pool (YC user guide example; notes
  unverified). A SAFE with both a cap and a discount takes the lower price (unverified: no current YC form has both).
- **Note interest (unverified).** Yearly compounding by default: P(1 + r/n)^(periods), a part period raised as a
  fractional power (computed to 50 digits and marked approximate); `stub_rule: simple`, `compounding: monthly` or
  `simple` change it. Rounded to the cent, half-even, before it converts.
- **Dilution (PG; the pool term unverified).** After each round, `h_k = h_(k-1)·(1 - n_k - p_k)`, with `n_k` the
  stake the round sells and `p_k` its new pool's share.
- **Vesting (Altman for the schedule).** 48 months with a 12-month cliff by default ("4 years with a 1-year cliff").
  Vested = 0 before the cliff, else G·min(months served, T)/T (monthly steps unverified). Termination forfeits the
  unvested shares; acceleration, exercise cost and intrinsic value = vested × max(0, common - strike) are unverified.
- **Exit waterfall (unverified).** Preferences (multiple × invested) are paid by rank, pro rata within a rank short
  of money; the rest is shared per share among common, converted and participating classes, a capped class stopping
  at its cap; a class converts only when that pays it strictly more. Cents are split by largest remainder, so the
  payouts add up to the exit amount.
- **Deal check (unverified, except post = pre + raise from the YC user guide).** Post-money = V + I; the investor's
  stake is its cap-table row (I/(V + I) with the pool in the pre-money); a holder group keeps its pre-round share ×
  FD/T; effective pre-money = (FD - U) × price; runway = (cash + I) / (gross burn - revenue). A stated figure within
  the tolerance (0.5 points for a percent, 2% for money or months, both inputs) is consistent, and so is a stated
  percent or runway that is the computed figure rounded half away from zero to the places it is written with, past
  the tolerance or not (people write figures rounded to the places they show: a 12-month runway against 12.40 holds,
  "12.0" does not), so send `stated_investor_percent`, `stated_holder_percent` and `stated_runway_months` as text
  with the deck's places; its row says whether it is that rounding, and the post-money and the use-of-funds total
  keep the tolerance alone. `consistent_beyond_rounding` names a figure that holds by the tolerance alone. The
  dilution (25%) and runway (18 months) bands are common benchmarks, not rules: they raise a question, never an error.
- **Runway plan (the YC seed guide for the milestone idea and the runway band; the rest unverified).** Cash above the
  floor runs down by each phase's net burn (gross burn - revenue, flat within a phase); a raise lands whole after
  `lands_month` months. Runway is when that cash first goes below zero (none when revenue covers the burn first); a
  no-raise row is always worked. A milestone is covered when the runway reaches its month plus `months_to_raise`;
  the smallest raise for it is the peak cumulative net burn from the landing month to that target less the cash above
  the floor (never below zero), none when the cash runs out before the money lands. A downside or lean case is its
  own phases or percents of the plan's. Stated runways and use-of-funds totals use deal_check's tolerances, and a
  stated runway that is the computed one rounded half away from zero to the places it is written with also holds, as
  in deal_check ("12" against 12.40 holds, "12.0" does not), so send each `stated_runway_months` as text with the
  founder's places; its row says whether it is that rounding, the use-of-funds total keeps the tolerance alone, and
  `consistent_beyond_rounding` names a runway that holds by the tolerance alone. A runway stated from landing is not
  checked when the cash runs out before the money lands. The 18-month band is the top of the guide's "raising for N months (usually 12-18)": a raise inside
  12 to 18 is within that range, so the flag is a question, never a shortfall or an error. Cash only: valuation and
  ownership stay with deal_check, round and dilution.
- **Metrics check (a16z, Bessemer, Sacks and Skok for the definitions and the three benchmarks; the rest
  unverified).** All flows are for one period. With k = 12 for monthly recurring revenue (1 for annual): ARR at the
  end = k·(S + N + E - C - X), net new ARR = k·(N + E - C - X); the latest month's ARR = 12·(T - one-time - usage),
  its run-rate 12·T (a16z: ARR excludes one-time, services and usage fees). Gross revenue retention (S - C - X)/S, net
  (S + E - C - X)/S, on the starting customers' movements when given, over the period and never annualised (Bessemer
  for the definitions; leaving new customers out is unverified). Gross revenue churn (C + X)/S, net (C + X - E)/S,
  logo churn = customers lost / at the start (a16z). Blended CAC = spend / new customers, paid = spend / paid-channel
  customers (a16z). CAC payback = spend / (new monthly recurring revenue × gross margin) (Bessemer measures it on
  gross margin; the formula is unverified), and on revenue only. Burn multiple = net burn / net new ARR (Sacks, who
  gives no ratio before revenue and says it approaches 0 as burn reaches 0); none is worked at or below zero
  (unverified), and a stated multiple then comes back `not_checked`, which keeps the overall verdict off
  consistent. Concentration = largest customer / period revenue (a16z). Each stated figure uses deal_check's
  tolerances, and a stated percent, months or multiple is also consistent when it is the computed figure rounded half
  away from zero to the places it is written with, past the tolerance or not (people write figures rounded to the
  places they show: 12 months against 12.40 holds, a 2% churn against 2.4% holds and against 2.6% does not), so send
  each as text with the document's places ("12", "12.0", "0.0"); its row says whether it is that rounding, and money
  keeps the tolerance alone. A stated ARR holds within the tolerance of either the movement's ending ARR or the latest
  month's, and `arr_basis` says which it was checked against. A churn with no basis is checked on every basis and
  holds when any does, and a churn below zero only as net revenue churn. Flags name the likely cause of a mismatch, a figure consistent by the
  tolerance alone (`consistent_beyond_rounding`) and a movement and latest month that disagree; the payback target by customer segment (Bessemer, set against the revenue-only
  payback as a floor when no margin is given), a burn multiple of 3x or more (Sacks) and one month's net revenue
  churn above 2% (Skok) raise a question, never an error.
- **Market sizing (the YC pitch guide for building the market bottom-up from customers and price and for preferring
  it to top-down; the YC seed guide for TAM as revenue; the rest unverified).** Per segment, annual revenue from one
  customer = price × units × 12 / the months the price covers × take rate; TAM = customers × that, summed; SAM =
  TAM × serviceable percent; SOM = the customers to win (or the serviceable customers × the share to win) × the
  annual revenue from one. The gross spend (before the take rate) is shown apart. A top-down figure's comparable part
  is set beside the bottom-up TAM or SAM, never in its place. With a horizon, the new customers a year are a straight
  line from today's. Stated TAM, SAM and SOM use deal_check's 2% tolerance. A sensitivity row works one field of one
  segment at each value, the rest at base; every total is linear in one field, so the value at which SOM reaches
  the target, and TAM or SAM the first top-down figure, is exact (or met without it, does not move, or out of range).
  Flags (a price period left out, read as yearly; double counting past the population, a bottom-up above the top-down, SAM equal to TAM, no SOM or one given only as
  a percent, a SOM grown from no customers today or below today's customers, no horizon, a SOM below or out of
  reach of the target) raise a question, never an error.

- **Priced round vs a note (the round's and the waterfall's rules above; the comparison's own conventions
  unverified).** Option A prices the raise now with the round code (existing SAFEs and notes converting in it), then
  each next round on A's exact shares. Option B issues no shares now; at each next round its note converts what it
  owes (principal plus interest, to the cent, unless paid in cash) at the lower of its cap price (cap / today's fully
  diluted shares) and discount price, beside the existing SAFEs and notes. Each exit after the next round goes
  through the waterfall on each option's classes, converted shares on their round's series terms with a preference on
  the amount converted. Ownership is shares over the total; payouts are split to the cent within each option; B - A is
  the exact difference rounded once. The note's maturity is only compared, never modelled; no anti-dilution applies.

## Limits

A decimal input has at most 28 significant digits and, when nonzero, a size from 1e-15 up to (not including) 1e16. A round
takes at most 50 SAFEs and notes, a dilution at most 20 rounds, a waterfall at most 12 classes, a deal check at
most 50 SAFEs and notes and 20 use-of-funds lines, and a runway plan at most 3 cases of 12 phases, 6 raises (20
use-of-funds lines each), 10 milestones, months up to 600 and 60 months to raise; a metrics check covers one
period of 1 to 36 months; a market size takes at most 8 segments, 3 top-down figures and 6 sensitivity rows of
up to 4 values each; a comparison takes at most 6 existing series, 4 existing SAFEs and notes, 4 next rounds and 6
exits; a pool plan at most 40 hires, each starting within 120 months; a raise pipeline at most 40 commitments, 20
pro rata amounts and 8 stages of up to 10,000 investors each, and 100 term sheets wanted. Anything past a limit is
refused with a message naming the field.
