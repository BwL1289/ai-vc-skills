# Eval 2: Company R, a runway answer the calculator checks

A test prompt for the `vc-partner-meeting` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator deal_check` run with these inputs. The answer states the expected behaviour; it is not a recorded
run, and this eval has not been run in a live session. A run passes when it makes the one tool call below (field order
free, money and percents as strings), puts the runway mismatch first among the kept questions without refuting it,
quotes the runway with no raise as not checked, and computes nothing in its own text.

## Prompt

> Prep me for my partner meeting at a seed fund on Tuesday; the partner was a finance executive before investing. One
> message, please. We're raising a $2M priced seed at an $8M pre-money for 20% of the company. We have $500k in the
> bank, spend $80k a month today and plan to spend $120k a month after the raise; no revenue yet. The deck says the
> round gives us 24 months of runway. Without the raise we have about 6 months. One-liner: "Company R schedules
> home-care nurses for agencies." My answer to "how long does the money last?": "Two years, comfortably."

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "2000000",
    "pre_money": "8000000",
    "stated_investor_percent": "20",
    "cash_on_hand": "500000",
    "planned_monthly_gross_burn": "120000",
    "current_monthly_gross_burn": "80000",
    "stated_runway_months": "24"
  }
}
```

## What the calculator prints (excerpt)

```text
  Planned monthly gross burn                                       $120,000.00  given
  Net runway, planned burn                                        20.83 months  (cash + I)/net burn
  Net runway, today's burn                                        31.25 months  (cash + I)/net burn
  Investors' percent: the calculator gives                            20.0000%  the investor's cap-table share
  Investors' percent: verdict                                       consistent  within the tolerance is consistent
  Runway: the deck says                                           24.00 months  given
  Runway: the calculator gives                                    20.83 months  (cash + I)/net burn, planned (else current)
  Runway: verdict                                                     mismatch  within the tolerance is consistent
  A VC is likely to ask                             current_burn_runway_longer  Runway on today's burn is longer than on the planned burn; say which one the deck uses, as a VC will check it against the planned spend
```

## Expected answer

- The runway mismatch is the first kept question, as ends the meeting: the deck's "24 months" (the tool prints 24.00
  months, given) against the tool's 20.83 months at the planned burn of $120,000.00. It is not put through the refute
  pass.
- The `current_burn_runway_longer` flag is a kept question at weakens it, first in that tier, in the tool's words and
  not refuted. Numbers relays it in one line (31.25 months on today's burn) and asks the founder to say which burn the
  deck uses.
- The percent sold is consistent (20.0000%) and is not drilled.
- The Finance lens runs with the Seed lens.
- "Without the raise we have about 6 months." is quoted and marked "not checked: no tool computes runway without a
  raise"; no division of cash by burn appears.
- Debrief: "Two years, comfortably." is weak (it disagrees with a tool result, both quoted); the stronger answer uses
  only the tool's figures and the founder's burn plan, and brackets what the money reaches, such as
  `[the milestone the $2M reaches]`.
- No arithmetic in the text beyond the tool's values, which are given as printed (20.83 months stays 20.83 months).
