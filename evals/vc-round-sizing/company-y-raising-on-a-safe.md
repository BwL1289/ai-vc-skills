# Eval 3: Company Y, raising on a SAFE, with two runway claims

A test prompt for the `vc-round-sizing` skill. The company is made up. Every tool call and excerpt is from a real
`equity_calculator` run with these inputs. The answer states the expected behaviour; it is not a recorded run, and this
eval has not been run in a live session. A run passes when it makes the one tool call below (field order free, money
and percents as strings), checks both runway claims, the one with no raise and the deck's, puts both mismatches first
without refuting them, runs the skeptic and refute pass after them, asks for a downside case without picking a percent,
leaves the SAFE's share not computed, and makes no `equity_deal_check` call.

## Prompt

> We're raising $1.5M on a post-money SAFE at a $12M cap; the deck says this gives us 24 months. Without it we have
> about 4 months. Cash is $300k. We spend $90k a month for months 1-3, then $160k a month with $10k of revenue. The
> milestone is month 12, and we allow 6 months to raise the seed after it.

## Expected tool call

`equity_runway_plan`, once:

```json
{
  "inputs": {
    "cash_on_hand": "300000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          {
            "from_month": 1,
            "gross_burn": "90000"
          },
          {
            "from_month": 4,
            "gross_burn": "160000",
            "revenue": "10000"
          }
        ]
      }
    ],
    "raises": [
      {
        "amount": "1500000",
        "stated_runway_months": "24"
      }
    ],
    "milestones": [12],
    "months_to_raise": 6,
    "stated_runway_months": "4"
  }
}
```

The "about 4 months" goes in the top-level `stated_runway_months`; the deck's 24 months in the raise's. No
`equity_deal_check` call: a SAFE is not a priced `investment`.

## What the calculator prints (excerpt)

```text
  Runway with no raise as stated                                    4.00 months  given
  Raise 1: runway as stated                                        24.00 months  given, counted from today
  Runway, plan, no raise                                            3.20 months  months until cash less the floor goes below zero
  Runway, plan, raise 1                                            13.20 months  months until cash less the floor goes below zero
  Milestone 1 (month 12), plan, raise 1: slack                      1.20 months  runway - the milestone month
  Milestone 1 (month 12), plan, raise 1: verdict                          short  covered when the runway reaches month 18
  Required raise, milestone 1, plan, landing month 0              $2,220,000.00  smallest raise keeping cash at or above the floor to month 18 (rounded up to the cent)
  Runway, no raise: stated                                          4.00 months  given
  Runway, no raise: the calculator gives                            3.20 months  the plan case's runway
  Runway, no raise: difference                                     -0.80 months  computed - stated
  Runway, no raise: verdict                                            mismatch  within the tolerance is consistent
  Runway, raise 1: stated                                          24.00 months  given
  Runway, raise 1: the calculator gives                            13.20 months  the plan case's runway
  Runway, raise 1: difference                                     -10.80 months  computed - stated
  Runway, raise 1: verdict                                             mismatch  within the tolerance is consistent
  Be ready to answer                                    milestone_short_on_plan  A raise does not reach a milestone, with the months to raise, on the plan itself
  Be ready to answer                                  start_raising_date_passed  With no raise, the plan's runway less the months to raise is already at or past today: on the plan, raising the next round takes longer than the cash lasts
  Be ready to answer                                          runway_below_band  A raise lasts under 18 months on the plan; be ready to say which milestone it reaches (a common benchmark, not a rule)
  Overall verdict                                                      mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- Both runway claims are mismatches, listed first and not refuted: with no raise, "about 4 months" (4.00 months as
  stated) against 3.20 months; with the SAFE, the deck's 24.00 months against 13.20 months, a difference of -10.80
  months.
- The milestone is short: 1.20 months of slack past month 12; the tool covers it only when the runway reaches month 18. The tool's required raise is $2,220,000.00; the answer quotes it and does not suggest raising it.
- No downside was given, so the plan runs alone and the open asks ask for a downside case; the answer picks no
  percent of its own.
- Adversarial review, after the two computed mismatches: the skeptic's kept attacks, each with a founder line quoted
  word for word, for example "the deck says this gives us 24 months" under "No downside case", or "The milestone is
  month 12" under "A milestone with no number, date or check"; then Dropped, one line each. The answer says whether
  the skeptic ran as a subagent.
- The SAFE's share is "not computed: set at the next priced round". The answer offers `equity_round` once the founder
  names that round; it does not pass the SAFE to `equity_deal_check`.
- Flags, one line each: `milestone_short_on_plan`, `start_raising_date_passed`, `runway_below_band` (a common
  benchmark, not a rule, quoting the tool's `runway_band` row).
- No recommendation. It closes as not investment, legal or tax advice.
