# Eval 2: Company AR, a 2x participating seed with terms the calculator does not model

A test prompt for the `vc-term-sheet-review` skill. The company is made up. The tool calls and their excerpts are real
calculator output for these inputs. The answer states the expected behaviour; it is not a recorded run, and this eval
has not been run in a live session. A run passes when it marks the preference, participation, dividends,
anti-dilution, board and redemption terms Differs or Not in the baseline with their sources, reports the founders' 75%
as a mismatch, runs every exit under the sheet's terms and under the 1x non-participating baseline with no difference
computed, quotes the not-modelled terms with the fixed string, and says nothing about whether to sign.

## Prompt

> Is this seed term sheet standard? "$3,000,000 Series Seed at a $9,000,000 pre-money valuation; investors own 25%
> fully diluted. Option pool: 10% post-closing, included in the pre-money. Liquidation Preference: 2x, fully
> participating. Dividends: 8% cumulative. Anti-dilution: full ratchet. Board: two Investor designees and one Founder.
> Redemption: at the option of the Investors after five years." Our three founders hold all 6,000,000 shares, there is
> no pool yet and no SAFE or note. We think we keep 75%. An acquirer floated $30M last month: what would we get?

## Expected tool call

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "9000000",
    "stated_investor_percent": "25",
    "fully_diluted_shares": 6000000,
    "target_pool_percent": "10",
    "holder_shares": 6000000,
    "stated_holder_percent": "75"
  }
}
```

```text
  Post-money valuation                                                $12,000,000.00  V + I
  Effective pre-money                                                  $7,800,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  Investors' percent: verdict                                             consistent  within the tolerance is consistent
  Holder group's percent after: the calculator gives                        65.0000%  h·(share every pre-round share keeps)
  Holder group's percent after: verdict                                     mismatch  within the tolerance is consistent
  A VC is likely to ask                               pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
```

### Call 2: `equity_pool`

```json
{
  "inputs": {
    "fully_diluted_shares": 6000000,
    "pre_money": "9000000",
    "investment": "3000000",
    "target_pool_percent": "10",
    "share_rounding": "whole_shares"
  }
}
```

```text
  Shares: existing holders                                    6,000,000           6,000,000  FD - U
  Shares: investor                                            2,307,692           2,000,000  N = I/p
```

### Call 3: `equity_waterfall` (the post-money, $12,000,000, run first: it prints the preference owed, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "12000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                 $7,666,666.51  preference paid + part of the rest
  Common stock's payout                           $4,333,333.49  common shares × per-share part
```

### Call 4: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "12000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                               $3,333,333.01  preference paid + part of the rest
  Common stock's payout                         $8,666,666.99  common shares × per-share part
```

### Call 5: `equity_waterfall` (that preference owed, $6,000,000, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "6000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                 $6,000,000.00  preference paid + part of the rest
  Common stock's payout                                   $0.00  common shares × per-share part
```

### Call 6: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "6000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $3,000,000.00  preference paid + part of the rest
  Common stock's payout                         $3,000,000.00  common shares × per-share part
```

### Call 7: `equity_waterfall` (the amount raised, $3,000,000, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "3000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                 $3,000,000.00  preference paid + part of the rest
  Common stock's payout                                   $0.00  common shares × per-share part
```

### Call 8: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "3000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $3,000,000.00  preference paid + part of the rest
  Common stock's payout                                 $0.00  common shares × per-share part
```

### Call 9: `equity_waterfall` (the founder's exit, $30,000,000, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "30000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                $12,666,666.02  preference paid + part of the rest
  Common stock's payout                          $17,333,333.98  common shares × per-share part
```

### Call 10: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "30000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                               $8,333,332.53  preference paid + part of the rest
  Common stock's payout                        $21,666,667.47  common shares × per-share part
```

## Expected answer

- Marks: the preference (2x against the template's 1x) Differs, participation Differs, dividends (cumulative)
  Differs, anti-dilution (full ratchet against broad-based weighted average) Differs, the board (two investor seats of
  three against one of three) Differs, redemption Not in the baseline, drag-along and founder vesting Missing. Each
  cites the YC article or template and the matching Feld post, and the answer notes that the baseline is a Series A
  sheet while this is a seed round.
- The 75% is a mismatch: the calculator gives 65.0000%, because the 10% pool is paid for out of the pre-money
  (effective pre-money $7,800,000.00 against $9,000,000.00). It leads the first tier. The investors' 25% is consistent.
- Exit table with both columns and no difference computed: at $6M (the preference owed) common gets $0.00 under the
  sheet and $3,000,000.00 under the baseline; at $12M, $4,333,333.49 against $8,666,666.99; at $30M, $17,333,333.98
  against $21,666,667.47, and under the baseline the seed converts. At $3M common gets $0.00 under both.
- Cumulative dividends, the full ratchet and redemption are quoted with "not modelled: no tool computes this term's
  effect"; the dividend is not folded into the 2x.
- Survivors include, from the next round's lead lens, that a later investor is likely to ask for the same 2x
  participating terms (the YC article: terms set a precedent for later rounds), and from the control lens the
  investors' board majority; each becomes a lawyer question, such as "What does the 2x participating preference pay
  common at our low exit?". No sentence says whether to sign or calls a term off the market.
