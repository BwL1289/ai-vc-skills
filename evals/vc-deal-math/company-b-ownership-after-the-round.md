# Eval 2: Company B, "what does this round do to my ownership"

A test prompt for the `vc-deal-math` skill. The company is made up. The answer states the expected behaviour; it is not
a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted from
what `equity_calculator deal_check` printed for these inputs; none is typed by hand. A run passes when it makes the one
tool call below (field order free, money and percents as strings), gives these figures, and computes nothing in its own
text.

## Prompt

> What does this round do to my ownership? Series A: $8M at a $32M pre ($40M post), investors get 20%. We founders own
> 90% today, so the deck says we keep 72%. Cap table: 9,000,000 founder shares, 600,000 granted options, 400,000
> unissued pool, 10,000,000 fully diluted. Two post-money SAFEs are outstanding: $1M at a $10M cap and $1.5M at a $15M
> cap. The term sheet tops the pool up to 10% unissued after the round, in the pre-money.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "8000000",
    "pre_money": "32000000",
    "post_money": "40000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 400000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "1000000",
        "valuation_cap": "10000000"
      },
      {
        "kind": "safe",
        "purchase_amount": "1500000",
        "valuation_cap": "15000000"
      }
    ],
    "holder_percent": "90",
    "stated_holder_percent": "72"
  }
}
```

## What the calculator prints (excerpt)

```text
  Price per share (p)                                                       $2.314050  the round's price
  Effective pre-money                                                  $22,214,876.03  (FD - U)·p: the pre-round holders' shares at the round price
  After: existing holders                                                    55.5372%  (FD - U)/T
  After: holder group                                                        52.0661%  h·kept
  After: SAFE 1                                                               7.2314%  shares/T
  After: SAFE 2                                                               7.2314%  shares/T
  After: option pool                                                         10.0000%  (U + P)/T
  After: investors                                                           20.0000%  N/T
  Share of their stake every pre-round share keeps                           57.8512%  FD/T, or V/(V + I) with no share counts
  Pre-money pays for: existing holders' shares                         $22,214,876.03  (FD - U)·p, to the cent so the parts add up to V
  Pre-money pays for: unissued pool already there                         $925,619.83  U·p
  Pre-money pays for: new pool                                          $3,074,380.17  P·p (pool in the pre-money)
  Pre-money pays for: SAFE and note shares                              $5,785,123.97  converted shares·p
  Pre-money pays for: total                                            $32,000,000.00  V
  Post-money: verdict                                                      consistent  within the tolerance is consistent
  Investors' percent: verdict                                              consistent  within the tolerance is consistent
  Holder group's percent after: the deck says                                72.0000%  given
  Holder group's percent after: the calculator gives                         52.0661%  h·(share every pre-round share keeps)
  Holder group's percent after: difference                                  -19.9339%  computed - stated
  Holder group's percent after: verdict                                      mismatch  within the tolerance is consistent
  Overall verdict                                                            mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- It asks whether the founder's 10,000,000 fully diluted shares leave the two SAFEs out, as the tool's count does
  (every share before the round, granted options and the unissued pool included, SAFEs and notes left out), and says
  the figures stand only on that basis. It subtracts no SAFE shares itself.
- Verdict `mismatch`: the post-money and the investors' 20% are consistent; the founders' 72% is not.
- Founders: the deck says 72.0000%, the calculator gives 52.0661%, a difference of -19.9339%. The answer explains that
  the 72% leaves out the two SAFEs converting and the pool top-up, both paid for out of the pre-money, and that a VC
  will read the cap table this way.
- After the round: existing holders (founders and granted options) 55.5372%, SAFE 1 7.2314%, SAFE 2 7.2314%, pool
  10.0000%, investors 20.0000%. Every pre-round share keeps 57.8512% of its stake.
- Price $2.314050; both SAFEs convert at their caps ($0.800000 and $1.200000 a share, from the result's `round`).
- What the $32M pre-money pays for: the pre-round holders' shares $22,214,876.03 (the effective pre-money), the
  unissued pool already there $925,619.83, the new pool $3,074,380.17 and the SAFE shares $5,785,123.97, which add up
  to $32,000,000.00.
- Questions a VC is likely to ask: `pool_in_pre_money_lowers_price` and `conversions_bought_by_pre_money`.
- The answer does not say the SAFE holders keep their percent through the Series A (a post-money SAFE's cap is
  post-SAFEs, not post-Series A).
