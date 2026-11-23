# Eval 5: Company AU, a Series A stacked over a seed preferred class, and founder vesting at a sale

A test prompt for the `vc-term-sheet-review` skill. The company is made up. The tool calls and their excerpts are real
calculator output for these inputs. The answer states the expected behaviour; it is not a recorded run, and this eval
has not been run in a live session. A run passes when it makes the seven calls below (field order free); passes
`common_shares` as the founders' 8,000,000 and never the `existing_holders` row's 10,000,000, which holds the Series
Seed's shares too; puts the Series Seed at rank 2 below the Series A; takes the Series A's shares from the pool table
that matches the sheet's pool timing; passes the sale month and the termination month to `equity_vesting`; marks
protective provisions, drag-along and the investor rights Missing, because the founder says the text is the whole
sheet; runs no baseline column; and gives no sign or do-not-sign verdict.

## Prompt

> Here is the whole Series A term sheet our lead sent; nothing is left out. "Series A Preferred: the lead puts in
> $5,000,000 at a $20,000,000 pre-money valuation. Before closing, the unissued option pool is enlarged to 10% of the
> fully diluted shares after closing, and the enlargement comes out of the pre-money. Liquidation Preference: the
> Series A gets back one times what it paid, without participating, and is paid ahead of the Series Seed. Dividends:
> only when the board declares them, and they do not accrue. Conversion: each Series A share becomes one common share
> whenever its holder chooses, and automatically at an IPO. Anti-dilution: broad-based weighted average. Board: the
> Series A names one director and the holders of common name two. Founder Vesting: from closing, each founder's
> 4,000,000 shares vest monthly over 48 months after a 12-month cliff; if the company is sold and the founder is then
> let go, all of that founder's unvested shares vest. No Shop: for 30 days the company talks to no other investor;
> this is the only binding term. Expenses: the company pays the lead's legal fees up to a cap." Our cap table: 11,000,000
> fully diluted shares and no SAFEs or notes. The two of us hold 8,000,000 common, our seed investors hold 2,000,000
> Series Seed preferred (they paid $2,000,000 for a 1x non-participating preference), and 1,000,000 are an unissued
> pool with no options granted. We think the two of us keep 60%. What do we get at a $10M sale, or at $60M? And if we
> are acquired in month 20 and both let go in month 22, how much of each founder's 4,000,000 shares has vested by
> month 24?

## Expected tool call

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "5000000",
    "pre_money": "20000000",
    "fully_diluted_shares": 11000000,
    "unissued_pool_shares": 1000000,
    "target_pool_percent": "10",
    "holder_shares": 8000000,
    "stated_holder_percent": "60"
  }
}
```

```text
  Post-money valuation                                                $25,000,000.00  V + I
  Effective pre-money                                                 $17,500,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  After: holder group                                                       56.0000%  h·kept
  Holder group's percent after: the calculator gives                        56.0000%  h·(share every pre-round share keeps)
  Holder group's percent after: verdict                                     mismatch  within the tolerance is consistent
  A VC is likely to ask                               pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
```

### Call 2: `equity_pool`

```json
{
  "inputs": {
    "fully_diluted_shares": 11000000,
    "unissued_pool_shares": 1000000,
    "pre_money": "20000000",
    "investment": "5000000",
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "share_rounding": "whole_shares"
  }
}
```

```text
  Line                                    Pool in pre-money (this deal)  Pool in post-money  How it is computed
  Price per share (p)                                         $1.750000           $1.818182  pre: V/(FD + P); post: V/FD
  Shares: existing holders                                   10,000,000          10,000,000  FD - U
  Shares: investor                                            2,857,142           2,750,000  N = I/p
  Ownership: investor                                          20.0000%            19.4118%  shares / T
  Post-money (every share at p)                          $24,999,998.69      $25,757,574.55  T·p
```

### Call 3: `equity_waterfall` (the amount raised, $5,000,000)

```json
{
  "inputs": {
    "exit_amount": "5000000",
    "common_shares": 8000000,
    "classes": [
      {
        "shares": 2857142,
        "invested": "5000000",
        "rank": 1
      },
      {
        "shares": 2000000,
        "invested": "2000000",
        "rank": 2
      }
    ]
  }
}
```

```text
  Class 1: seniority, participation  rank 1, no participation  given
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $5,000,000.00  preference paid + part of the rest
  Class 2: seniority, participation  rank 2, no participation  given
  Class 2: payout                                       $0.00  preference paid + part of the rest
  Common stock's payout                                 $0.00  common shares × per-share part
```

### Call 4: `equity_waterfall` (the founders' low exit, $10,000,000)

```json
{
  "inputs": {
    "exit_amount": "10000000",
    "common_shares": 8000000,
    "classes": [
      {
        "shares": 2857142,
        "invested": "5000000",
        "rank": 1
      },
      {
        "shares": 2000000,
        "invested": "2000000",
        "rank": 2
      }
    ]
  }
}
```

```text
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $5,000,000.00  preference paid + part of the rest
  Class 2: choice                                       stays  converts only when that pays strictly more
  Class 2: payout                               $2,000,000.00  preference paid + part of the rest
  Common stock's payout                         $3,000,000.00  common shares × per-share part
```

### Call 5: `equity_waterfall` (the post-money, $25,000,000)

```json
{
  "inputs": {
    "exit_amount": "25000000",
    "common_shares": 8000000,
    "classes": [
      {
        "shares": 2857142,
        "invested": "5000000",
        "rank": 1
      },
      {
        "shares": 2000000,
        "invested": "2000000",
        "rank": 2
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                               $5,555,554.26  preference paid + part of the rest
  Class 2: choice                                    converts  converts only when that pays strictly more
  Class 2: payout                               $3,888,889.15  preference paid + part of the rest
  Common stock's payout                        $15,555,556.59  common shares × per-share part
```

### Call 6: `equity_waterfall` (the founders' hoped-for exit, $60,000,000)

```json
{
  "inputs": {
    "exit_amount": "60000000",
    "common_shares": 8000000,
    "classes": [
      {
        "shares": 2857142,
        "invested": "5000000",
        "rank": 1
      },
      {
        "shares": 2000000,
        "invested": "2000000",
        "rank": 2
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                              $13,333,330.22  preference paid + part of the rest
  Class 2: choice                                    converts  converts only when that pays strictly more
  Class 2: payout                               $9,333,333.96  preference paid + part of the rest
  Common stock's payout                        $37,333,335.82  common shares × per-share part
```

### Call 7: `equity_vesting` (one founder's 4,000,000 shares at month 24)

```json
{
  "inputs": {
    "grant_shares": 4000000,
    "total_months": 48,
    "cliff_months": 12,
    "month": 24,
    "acceleration": "double_trigger",
    "acceleration_percent": "100",
    "change_of_control_month": 20,
    "termination_month": 22
  }
}
```

```text
  Terminated at (e)               22 months  given
  Change of control at (c)        20 months  given
  Vested in all                   4,000,000  on schedule + accelerated
  Share of the grant vested       100.0000%  vested / G
  Acceleration fired                    yes  at 22 months
```

## Expected answer

- Opens with the one-line reminder: a plain-words reading to prepare for the lawyer, not legal, tax or investment
  advice; whether to sign is for the founders with their lawyer.
- Marks, each with its source: amount and valuation Differs on the label (the sheet's pre-money against the
  template's post-money, with the pool's place quoted: "the enlargement comes out of the pre-money"); seniority
  Differs (the Series A "is paid ahead of the Series Seed", where the template has one Series A); founder vesting
  Differs (the template leaves founders' vesting blank to negotiate, and the sheet fills it in, from closing, with a
  double trigger); the pool, the preference, participation, dividends, conversion, anti-dilution, the board and the
  no-shop with its fees Match, each sheet line quoted beside the baseline cell. The founder says this is the whole
  sheet, so protective provisions, drag-along and the investor rights (pro rata, first refusal, co-sale, information)
  are Missing, each a lawyer question.
- Price: the founders' shares are priced at the effective pre-money, $17,500,000.00, against the $20,000,000.00
  pre-money (the `pool_in_pre_money_lowers_price` flag in plain words). The 60% is a mismatch: the calculator gives
  56.0000%. It leads the first tier, because the founders' own figure for the round is wrong, not as a prediction
  about a later deal.
- The pool what-if, from `equity_pool`'s other table: with the pool counted after the money and the $20,000,000.00
  pre-money held fixed, the price would be $1.818182 and the post-money $25,757,574.55, not the $25,000,000.00 the
  round gives, and the investor would hold 19.4118%; a lawyer question, not advice.
- The waterfall's shares: the Series A's 2,857,142 come from the pool-in-pre-money table, the one marked "(this
  deal)", because the sheet puts the pool in the pre-money. Common is the founders' 8,000,000 from their own count, not
  the `existing_holders` row's 10,000,000, which also holds the Series Seed's 2,000,000 shares; using that row would
  count the seed class twice. The Series A is at rank 1 and the Series Seed at rank 2, because the sheet pays the
  Series A first.
- Exit table, each exit named with where it comes from: at $5M (the amount raised) the Series A stays and takes
  $5,000,000.00, the Series Seed takes $0.00 and common gets $0.00; at $10M (the founders') both stay, the Series Seed
  takes $2,000,000.00 and common gets $3,000,000.00; at $25M (the post-money) both convert and common gets
  $15,555,556.59; at $60M (the founders') both convert and common gets $37,333,335.82. The founders hold every common
  share that takes part, so common's payout is theirs. No baseline column: the preference already matches.
- Vesting, from `equity_vesting` with the sale in month 20 and the termination in month 22, both as the founders named
  them: each founder's 4,000,000 shares are all vested by month 24 (100.0000%), and the acceleration fired at 22
  months. Without the termination month the double trigger would not fire, so the call needs both months. The sheet
  vests "from closing", so there is no credit for time served: a lawyer question, never a shifted month.
- Dividends and anti-dilution are quoted with "not modelled: no tool computes this term's effect".
- Lawyer questions cover the stacked seniority over the Series Seed, the three Missing terms, the founder vesting
  start and its double trigger, and which parts bind on signing (the no-shop).
