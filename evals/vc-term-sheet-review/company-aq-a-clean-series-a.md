# Eval 1: Company AQ, a clean Series A, what common gets at a low exit, and the next round

A test prompt for the `vc-term-sheet-review` skill. The company is made up. The tool calls and their excerpts are real
calculator output for these inputs. The answer states the expected behaviour; it is not a recorded run, and this eval
has not been run in a live session. A run passes when it makes the seven calls below (field order free), marks every
quoted term Matches and founder vesting, which the sheet leaves out, Missing, runs no baseline column (the preference
already matches), shows common taking $0.00 at the $8M raise, passes the founders' percent after the round to
`equity_dilution` for the later round the founder names, and gives no sign or do-not-sign verdict.

## Prompt

> Our lead sent this Series A term sheet; review it before I call our lawyer. "Investment Amounts: $8 million from
> Lead Investor. Valuation: $40 million post-money valuation, including an available option pool equal to 10% of the
> post-Closing fully-diluted capitalization. Liquidation Preference: 1x non-participating preference. Dividends:
> noncumulative, payable if and when declared by the Board of Directors. Anti-dilution: broad-based weighted average.
> Board: Lead Investor designates 1 director. Common Majority designates 2 directors. Drag-Along: a Company Sale
> approved by the Board, the Preferred Majority and a majority of Common Stock. No Shop: 30 days." We have 10,000,000
> fully diluted shares and no SAFEs or notes: the two founders hold 9,500,000 and 500,000 are an unissued pool. We
> think we keep 70%. What do we get if we sell for $20M, or for $150M? And if a Series B later sells 20% with a 5% pool
> top-up, what is left of our stake?

## Expected tool call

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "8000000",
    "post_money": "40000000",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "target_pool_percent": "10",
    "holder_shares": 9500000,
    "stated_holder_percent": "70"
  }
}
```

```text
  Pre-money valuation (V)                                             $32,000,000.00  post-money - I (worked from it)
  Post-money valuation                                                $40,000,000.00  V + I
  Effective pre-money                                                 $28,000,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  After: holder group                                                       70.0000%  h·kept
  Holder group's percent after: verdict                                   consistent  within the tolerance is consistent
  A VC is likely to ask                               pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
```

### Call 2: `equity_pool`

```json
{
  "inputs": {
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "pre_money": "32000000",
    "investment": "8000000",
    "target_pool_percent": "10",
    "share_rounding": "whole_shares"
  }
}
```

```text
  Shares: existing holders                                    9,500,000           9,500,000  FD - U
  Shares: investor                                            2,714,285           2,500,000  N = I/p
  Ownership: investor                                          20.0000%            18.7500%  shares / T
```

### Call 3: `equity_waterfall` (the amount raised, $8,000,000)

```json
{
  "inputs": {
    "exit_amount": "8000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "8000000"
      }
    ]
  }
}
```

```text
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $8,000,000.00  preference paid + part of the rest
  Common stock's payout                                 $0.00  common shares × per-share part
```

### Call 4: `equity_waterfall` (the founder's low exit, $20,000,000)

```json
{
  "inputs": {
    "exit_amount": "20000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "8000000"
      }
    ]
  }
}
```

```text
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $8,000,000.00  preference paid + part of the rest
  Common stock's payout                        $12,000,000.00  common shares × per-share part
```

### Call 5: `equity_waterfall` (the post-money, $40,000,000)

```json
{
  "inputs": {
    "exit_amount": "40000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "8000000"
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                               $8,888,887.07  preference paid + part of the rest
  Common stock's payout                        $31,111,112.93  common shares × per-share part
```

### Call 6: `equity_waterfall` (the founder's hoped-for exit, $150,000,000)

```json
{
  "inputs": {
    "exit_amount": "150000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "8000000"
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                              $33,333,326.51  preference paid + part of the rest
  Common stock's payout                       $116,666,673.49  common shares × per-share part
```

### Call 7: `equity_dilution` (the later round the founder names)

```json
{
  "inputs": {
    "holder_percent": "70",
    "rounds": [
      {
        "investor_percent": "20",
        "pool_percent": "5"
      }
    ]
  }
}
```

```text
  Stake before the first round          70.0000%  given
  Final stake                           52.5000%  h_0·(1 - n_1 - p_1)···(1 - n_k - p_k)
```

## Expected answer

- Opens with the one-line reminder: a plain-words reading to prepare for the lawyer, not legal, tax or investment
  advice; whether to sign is for the founders with their lawyer.
- Every quoted term is marked Matches against the YC template, quoted side by side; founder vesting is Missing (the
  sheet is silent). It is a Series A, so the seed caveat is not needed.
- Price: the $40M post-money includes the pool, so the founders' shares are priced at the effective pre-money,
  $28,000,000.00, against the $32,000,000.00 pre-money (the `pool_in_pre_money_lowers_price` flag in plain words).
  With the pool counted after the money instead, the investor would hold 18.7500% (`equity_pool`); that is a lawyer
  question, not advice. The founders' 70% is consistent (70.0000%).
- Exit table, each exit named with where it comes from: at $8M (the amount raised) the Series A stays, takes
  $8,000,000.00 and common gets $0.00; at $20M (the founder's) it stays and common gets $12,000,000.00; at $40M (the
  post-money) it converts and common gets $31,111,112.93; at $150M (the founder's) it converts and common gets
  $116,666,673.49. The founders hold every common share that takes part, so common's payout is theirs; the unissued
  pool takes nothing (the `exit_is_shared_amount` assumption, quoted). No baseline column: the preference is already
  1x non-participating.
- The later round: `equity_dilution` takes the founders' 70.0000% from `equity_deal_check` and the founder's own 20%
  and 5%, and gives a final stake of 52.5000%.
- Dividends and anti-dilution are quoted with "not modelled: no tool computes this term's effect".
- Few or no survivors from the lenses; "nothing found" is acceptable. Lawyer questions still cover the pool's size and
  timing, the founders' vesting (Missing) and which parts bind on signing (the no-shop).
