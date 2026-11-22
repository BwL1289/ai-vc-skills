# Eval 2: Company F, the ask's numbers go to the calculator

A test prompt for the `vc-positioning` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator deal_check` run with these inputs; the rest states the expected behaviour and is not a recorded
run. A run passes when it makes the one tool call below (field order free, money and percents as strings), puts the
calculator's mismatches at the top of the surviving objections, and computes nothing in its own text.

## Prompt

> Check our story and our ask. Company F helps truck fleets pay their drivers the same day. We're raising a $2M priced
> seed at a $10M pre-money for 20% of the company. We have $300k in the bank and no revenue yet, and we don't plan
> any revenue in the next 18 months. We spend $150k a month today and plan to keep spending $150k a month after the
> raise. The deck says 18 months of runway. Weekly active users went from 2,000 to 4,500 over the last six months,
> which is 15% a month.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "2000000",
    "pre_money": "10000000",
    "stated_investor_percent": "20",
    "cash_on_hand": "300000",
    "planned_monthly_gross_burn": "150000",
    "planned_monthly_revenue": "0",
    "current_monthly_gross_burn": "150000",
    "current_monthly_revenue": "0",
    "stated_runway_months": "18"
  }
}
```

## What the calculator prints (excerpt)

```text
  Post-money valuation                                 $12,000,000.00  V + I
  Investors' percent: the deck says                          20.0000%  given
  Investors' percent: the calculator gives                   16.6667%  the investor's cap-table share
  Investors' percent: difference                             -3.3333%  computed - stated
  Investors' percent: verdict                                mismatch  within the tolerance is consistent
  Runway: the deck says                                  18.00 months  given
  Runway: the calculator gives                           15.33 months  (cash + I)/net burn, planned (else current)
  Runway: difference                                     -2.67 months  computed - stated
  Runway: verdict                                            mismatch  within the tolerance is consistent
  A VC is likely to ask                             runway_below_band  Planned runway is under 18 months; a VC is likely to ask whether the raise reaches the next milestone (a common benchmark, not a rule)
  Overall verdict                                            mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The two calculator mismatches lead the surviving objections, ranked as ends the meeting and not put through the
  refute pass: the deck's 20% against the calculator's 16.6667% (a $12,000,000.00 post-money), and the deck's 18.00
  months against 15.33 months. Each quotes the deck's figure as stated and gives the tool's value.
- Through the MCP tool, the investors' share comes back as the fraction 0.166667 and the difference as -0.033333; the
  answer shows them as 16.6667% and -3.3333% by moving the decimal point two places, the form the report prints, and
  rounds neither.
- The `runway_below_band` flag is relayed as a question a partner is likely to ask, a common benchmark and not a rule.
- "15% a month" is quoted as stated and marked "not checked: no tool computes this". The answer neither confirms,
  corrects nor annualizes it.
- The ask lens's objection about what the $2M reaches survives, because the material names no milestone; the evidence
  to add is a bracketed ask, such as `[the milestone the $2M reaches]`.
- Every percent, valuation and month figure in the answer comes from the tool or is quoted from the prompt.
