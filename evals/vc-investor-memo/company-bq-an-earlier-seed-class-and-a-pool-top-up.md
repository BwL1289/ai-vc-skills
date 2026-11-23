# Eval 5: Company BQ, an earlier Seed class, a pool top-up and no pro forma

A test prompt for the `vc-investor-memo` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator` runs with these inputs, on this repository's calculator. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it makes the four calls
below (field order free, money and percents as strings), takes `common_shares` from the founder's count of issued
common and not from the `existing_holders` row, passes the Seed as its own class at the rank the term sheet gives,
labels every exit value the founder's assumption, and computes nothing in its own text.

## Prompt

> Draft the outcome section of our memo for our champion. The Series A: $5,000,000 at a $20,000,000 pre-money, with
> the pool topped up to 10% before the round; our draft says "the round buys 20%". Cap table: 10,000,000 fully diluted
> shares, of which 7,500,000 are issued common held by the founders, 2,000,000 are Seed preferred (we raised
> $2,000,000, 1x, non-participating) and 500,000 are unissued pool; no options granted, no SAFEs or notes, no pro
> forma yet. The term sheet makes the Series A 1x, non-participating and senior to the Seed. Exits: $6 million if
> things go badly (an acqui-hire), $60 million on plan (a sale to a larger scheduling vendor).

## Expected tool call

Four calls, in this order: `equity_deal_check`, `equity_pool` for whole share counts, then `equity_waterfall` once per
exit value, with `common_shares` 7500000 (the founder's issued common) and the Seed as a second class at rank 2.

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "5000000",
    "pre_money": "20000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money"
  }
}
```

```text
  Investors' share of the cap table                                       20.0000%  N/T
  Investors' percent: verdict                                           consistent  within the tolerance is consistent
```

### Call 2: `equity_pool`

```json
{
  "inputs": {
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "pre_money": "20000000",
    "investment": "5000000",
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "share_rounding": "whole_shares"
  }
}
```

```text
  Shares: existing holders                                    9,500,000           9,500,000  FD - U
  Shares: investor                                            2,714,285           2,500,000  N = I/p
```

### Call 3: `equity_waterfall`, the $6,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "6000000",
    "common_shares": 7500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "5000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      },
      {
        "shares": 2000000,
        "invested": "2000000",
        "preference_multiple": "1",
        "rank": 2,
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $5,000,000.00  preference paid + part of the rest
  Class 2: payout                               $1,000,000.00  preference paid + part of the rest
  Common stock's payout                                 $0.00  common shares × per-share part
```

### Call 4: `equity_waterfall`, the $60,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "60000000",
    "common_shares": 7500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "5000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      },
      {
        "shares": 2000000,
        "invested": "2000000",
        "preference_multiple": "1",
        "rank": 2,
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                              $13,333,330.60  preference paid + part of the rest
  Class 2: payout                               $9,824,561.98  preference paid + part of the rest
  Common stock's payout                        $36,842,107.42  common shares × per-share part
```

## Expected answer

- The round: "the round buys 20%" is consistent with the tool's 20.0000%.
- `common_shares` is the founder's 7,500,000 issued common. The `existing_holders` row of `equity_pool` (9,500,000)
  counts the Seed's 2,000,000 shares too, so it is not used: passing it would count the Seed twice, once as common and
  once as its own class. The Series A class takes the `investor` row (2,714,285); the Seed is its own class with
  $2,000,000 invested at rank 2, since the term sheet makes the Series A senior.
- The outcome table: at $6,000,000, the founder's assumption with "an acqui-hire" quoted, the Series A stays and is
  paid $5,000,000.00 beside $5,000,000 invested; the Seed is paid $1,000,000.00 and common $0.00. At $60,000,000, the
  founder's assumption with "a sale to a larger scheduling vendor" quoted, the Series A converts and is paid
  $13,333,330.60 beside $5,000,000 invested. The `exit_is_shared_amount` row is quoted; no multiple, no fund size.
- The exit if the company wins is a bracketed ask, `[the exit value if the company wins, and why]`.
- No sentence recommends investing; no firm is named; no score.
