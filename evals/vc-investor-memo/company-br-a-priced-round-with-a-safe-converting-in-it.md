# Eval 6: Company BR, a priced round with a SAFE converting in it

A test prompt for the `vc-investor-memo` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator` runs with these inputs, on this repository's calculator; the founder's pro forma is the
calculator's converted share counts in whole shares. The answer states the expected behaviour; it is not a recorded
run, and this eval has not been run in a live session. A run passes when it passes the SAFE to `equity_deal_check` as
`instruments`, leads with the founders' percent that does not match, runs the waterfall on the pro forma's counts with
the SAFE as its own class and not in `common_shares`, and computes nothing in its own text.

## Prompt

> Draft the memo for our champion. The Series A: $4,000,000 at a $16,000,000 pre-money, with the pool topped up to 10%
> before the round. A $1,000,000 post-money SAFE at an $8,000,000 cap converts in it. Our draft says "founders keep
> 62%". Cap table before the round: 10,000,000 fully diluted shares, not counting the SAFE; the founders hold
> 8,000,000, angels hold 1,000,000 as common, and 1,000,000 is unissued pool; no options granted. Pro forma from our
> lawyer: 9,000,000 common, 1,428,571 SAFE preferred, 2,979,591 Series A preferred, 1,489,795 pool. Both preferred
> classes are 1x, non-participating and pari passu. Exit on plan: $100 million.

## Expected tool call

Two calls: `equity_deal_check` with the SAFE in `instruments`, then `equity_waterfall` at the plan exit on the pro
forma's counts.

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "4000000",
    "pre_money": "16000000",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 1000000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "holder_shares": 8000000,
    "stated_holder_percent": "62",
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "1000000",
        "valuation_cap": "8000000"
      }
    ]
  }
}
```

```text
  SAFEs and notes                                                                   1  given
  After: SAFE 1                                                               9.5890%  shares/T
  Holder group's percent after: the calculator gives                         53.6986%  h·(share every pre-round share keeps)
  Holder group's percent after: difference                                   -8.3014%  computed - stated
  Holder group's percent after: verdict                                      mismatch  within the tolerance is consistent
  A VC is likely to ask                               conversions_bought_by_pre_money  SAFE and note shares come out of the pre-round holders, not the new investor, so their stake falls by more than the percent sold; a VC reads the cap table this way
```

### Call 2: `equity_waterfall`, the $100,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "100000000",
    "common_shares": 9000000,
    "classes": [
      {
        "shares": 2979591,
        "invested": "4000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      },
      {
        "shares": 1428571,
        "invested": "1000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      }
    ]
  }
}
```

```text
  Common shares                                     9,000,000  given
  Class 1: payout                              $22,222,218.08  preference paid + part of the rest
  Class 2: choice                                    converts  converts only when that pays strictly more
  Class 2: payout                              $10,654,487.92  preference paid + part of the rest
  Common stock's payout                        $67,123,294.00  common shares × per-share part
```

## Expected answer

- The founders' percent leads the fix list under figures that do not match (computed), with no tier: "founders keep
  62%" against the tool's 53.6986% (difference -8.3014%); the memo states 53.6986%. Left out of `instruments`, the
  SAFE would not be counted and the founders' percent would come out too high.
- The `conversions_bought_by_pre_money` flag goes into the fix list as a question a partner is likely to ask, in the
  tool's words.
- The waterfall runs on the pro forma's counts: `common_shares` 9,000,000, the SAFE's 1,428,571 shares as their own
  class with $1,000,000 invested, never part of `common_shares`, and the Series A's 2,979,591 shares with $4,000,000
  invested, both at rank 1 as the founder states them.
- The outcome table: $100,000,000, the founder's assumption with `[why $100 million]`; the Series A's payout
  $22,222,218.08 beside $4,000,000 invested, and the SAFE class's $10,654,487.92 beside $1,000,000; no multiple, no
  fund size.
- No sentence recommends investing; no firm is named; no score.
