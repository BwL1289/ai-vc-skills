# Eval 1: Company A, "check my deck's numbers"

A test prompt for the `vc-deal-math` skill. The company is made up. Every figure under "Expected answer" is pasted
from what `equity_calculator deal_check` printed for these inputs; none is typed by hand. A run passes when it makes
the one tool call below (field order free, money and percents as strings), gives these figures, and computes nothing
in its own text.

## Prompt

> Check my deck's numbers before I send it out. We're raising $3M at a $12M pre-money and the deck says investors get
> 20%. We'll create a 10% option pool, and the term sheet puts it in the pre-money. The deck also says the raise gives
> us 24 months of runway. We have 8,000,000 shares, all the founders', no pool yet, $400k in the bank, and we plan to
> burn $180k a month after the raise.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "12000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 8000000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "holder_percent": "100",
    "cash_on_hand": "400000",
    "planned_monthly_gross_burn": "180000",
    "stated_runway_months": "24"
  }
}
```

## What the calculator prints (excerpt)

```text
  Effective pre-money                                               $10,500,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  Price per share (p)                                                    $1.312500  the round's price
  After: holder group                                                     70.0000%  h·kept
  After: option pool                                                      10.0000%  (U + P)/T
  After: investors                                                        20.0000%  N/T
  Pre-money pays for: new pool                                       $1,500,000.00  P·p (pool in the pre-money)
  Net runway, planned burn                                            18.89 months  (cash + I)/net burn
  Investors' percent: verdict                                           consistent  within the tolerance is consistent
  Runway: the deck says                                               24.00 months  given
  Runway: the calculator gives                                        18.89 months  (cash + I)/net burn, planned (else current)
  Runway: difference                                                  -5.11 months  computed - stated
  Runway: verdict                                                         mismatch  within the tolerance is consistent
  Overall verdict                                                         mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- Verdict `mismatch`: of the two figures the deck states, the investors' 20% is consistent and the 24-month runway
  is not.
- The 20% holds because the pool sits in the pre-money; the answer says so.
- Runway: the deck says 24.00 months, the calculator gives 18.89 months on the planned burn, a difference of -5.11
  months. The answer tells the founder to fix the slide or say which burn the 24 months assumed.
- What the round does: founders 70.0000%, pool 10.0000%, investors 20.0000%, price $1.312500. The pool in the
  pre-money prices the founders' shares at an effective pre-money of $10,500,000.00, and $1,500,000.00 of the
  pre-money pays for the new pool.
- One question a VC is likely to ask, from the flag `pool_in_pre_money_lowers_price`: the effective pre-money is below
  the headline. No runway-band or dilution flag appears.
- The answer quotes the pool-timing and runway assumptions with their sources (`unverified (standard arithmetic)` for
  runway) and gives no advice on whether to take the round.
