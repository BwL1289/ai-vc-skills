---
name: equity-calculator
description: Exact startup equity arithmetic with the equity_calculator command or its MCP tools. Use whenever someone asks whether a fundraise or a stake is worth it (Paul Graham's equity equation), how much equity a hire is worth or what to offer them, how big an option pool to add and what it does to the price per share (the option-pool shuffle), how SAFEs or convertible notes convert in a priced round (caps, discounts, MFN, note interest), how a stake dilutes over several rounds, how many shares have vested at a given month (cliff, termination, acceleration, exercise cost), or who gets what at an exit (liquidation preferences, participation, caps). Run the calculator instead of doing the arithmetic by hand.
---

# Equity calculator

The calculator works seven scenarios exactly (rational arithmetic, no floating point) and returns every value, the
exact fractions, and the assumptions each result rests on, each with its source. Use it for the numbers; do not
work them out by hand, and do not round or re-derive what it returns.

## Which scenario answers which question

| Question                                                                              | Scenario    | MCP tool           |
| ------------------------------------------------------------------------------------- | ----------- | ------------------ |
| Is selling n% worth it for an m-times better average outcome?                         | `investor`  | `equity_investor`  |
| What is the most of the company a hire is worth, and what should the offer be?        | `employee`  | `equity_employee`  |
| How many pool shares does a target pool need, and what is the price per share?        | `pool`      | `equity_pool`      |
| How do SAFEs and notes convert in a priced round, and what is the cap table after it? | `round`     | `equity_round`     |
| What is my stake after these rounds?                                                  | `dilution`  | `equity_dilution`  |
| How many shares have vested at month M, and what do they cost or are they worth?      | `vesting`   | `equity_vesting`   |
| Who gets what when the company is sold for E?                                         | `waterfall` | `equity_waterfall` |

## Running it

**MCP tools** (`equity_calculator_mcp`). Each scenario tool takes one argument, `inputs`, an object with that
scenario's fields, and returns the same JSON text as `equity_calculator <scenario> --json`:

```json
{ "inputs": { "equity_percent": "7", "outcome_multiplier": "1.10" } }
```

| Scenario  | Fields (required in bold)                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| investor  | `equity_percent` or (`pre_money` and `investment`); `outcome_multiplier` or `growth_percent`; `holder_percent`                                                                                                                                                                                                                                                                                                                                                                  |
| employee  | `outcome_multiplier` or `gain_percent`; `offered_percent`; `annual_cost` with `valuation`; `margin_percent`; `cost_years`                                                                                                                                                                                                                                                                                                                                                       |
| pool      | **`fully_diluted_shares`**, `unissued_pool_shares`, **`pre_money`**, **`investment`**, **`target_pool_percent`**, `pool_timing` (`pre_money` or `post_money`), `share_rounding` (`exact` or `whole_shares`)                                                                                                                                                                                                                                                                     |
| round     | **`fully_diluted_shares`**, `unissued_pool_shares`, **`pre_money`**, **`investment`**, `target_pool_percent`, `pool_timing`, **`instruments`**: a list of `{"kind": "safe", "purchase_amount", "valuation_cap", "discount_percent", "mfn"}` and `{"kind": "note", "principal", "interest_rate_percent", "months_outstanding"` or `"issue_date"` and `"conversion_date", "compounding", "stub_rule", "day_count", "valuation_cap", "discount_percent", "interest_paid_in_cash"}` |
| dilution  | **`holder_percent`**, **`rounds`**: a list of `{"investor_percent"` or `"pre_money"` and `"investment", "pool_percent"}`                                                                                                                                                                                                                                                                                                                                                        |
| vesting   | **`grant_shares`**, **`month`**, `total_months`, `cliff_months`, `strike_price`, `common_price`, `termination_month`, `acceleration` (`none`, `single_trigger`, `double_trigger`), `acceleration_percent`, `acceleration_base` (`unvested` or `grant`), `change_of_control_month`, `share_rounding`                                                                                                                                                                             |
| waterfall | **`exit_amount`**, **`common_shares`**, **`classes`**: a list of `{"shares", "invested", "preference_multiple", "rank", "participation"` (`none`, `full`, `capped`), `"cap_multiple"}`                                                                                                                                                                                                                                                                                          |

Send money, percents and multipliers as JSON strings (`"7"`, `"1.10"`, `"8000000"`): a JSON number with a decimal
point arrives as a binary float and keeps only about 15 digits. Percents are percents (`"7"` is 7%). Share counts
are whole numbers. `equity_workbook` exists only when the server was started with `--output-dir DIR`: it takes
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

1. Pick the scenario, ask for any required input that is missing, and run it. State any value you had to assume.
2. Give the headline numbers as the tool prints them (the `rounded` value with its unit, or the exact fraction when
   precision matters). Do not round them again or recompute them.
3. Quote the assumptions the result lists. Each has a source; say plainly when it is `unverified` (standard
   arithmetic no cited source fixes, such as every option-pool, note and waterfall convention), and say how to change
   a default when the user's terms differ.
4. A refusal or a tool error is the answer for those inputs: relay the reason and what to change. Never guess a
   number the calculator refused to give.
5. The calculator works the arithmetic of the terms given. It does not read a term sheet or a cap table file, and it
   is not legal, tax or investment advice: say so when the question needs either.

## The formulas and their sources

Sources: **PG** is Paul Graham, "The Equity Equation", <https://paulgraham.com/equity.html> (July 2007).
**Altman** is Sam Altman, "Employee Equity", <https://blog.samaltman.com/employee-equity> (April 2014). **YC** is
Y Combinator's post-money SAFE forms (valuation cap, discount, MFN) and their user guide,
<https://www.ycombinator.com/documents>. Everything else is standard arithmetic, labelled `unverified` in the results.

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

## Limits

A decimal input has at most 28 significant digits and, when nonzero, a size from 1e-15 up to (not including) 1e16. A round
takes at most 50 SAFEs and notes, a dilution at most 20 rounds and a waterfall at most 12 classes. Anything past a
limit is refused with a message naming the field.
