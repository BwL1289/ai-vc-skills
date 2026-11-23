# Eval 2: Company X, raise now or wait six months

A test prompt for the `vc-round-sizing` skill. The company is made up. Every tool call and excerpt is from a real
`equity_calculator` run with these inputs. The answer states the expected behaviour; it is not a recorded run, and this
eval has not been run in a live session. A run passes when it makes the three tool calls below (field order free, money
and percents as strings), sets the waiting option's `lands_month`, sets the two options side by side in tool values,
labels the later valuation as the founder's assumption, lists what has to be true for waiting to work, runs the
adversarial review after the computed results, and gives no recommendation.

## Prompt

> Raise $2M now at $8M pre, or wait six months and raise $3M at $15M pre? Cash is $1.2M. Plan: months 1-6 we spend
> $150k a month with $30k of revenue, months 7-12 $200k with $50k, from month 13 $260k with $80k. The milestone is
> month 18, and we allow 6 months to raise after it. Downside: revenue at 60% of plan. Founders hold 70%.

## Expected tool call

Three calls, in this order.

`equity_runway_plan`, once, with the waiting option's money landing after 6 months:

```json
{
  "inputs": {
    "cash_on_hand": "1200000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          {
            "from_month": 1,
            "gross_burn": "150000",
            "revenue": "30000"
          },
          {
            "from_month": 7,
            "gross_burn": "200000",
            "revenue": "50000"
          },
          {
            "from_month": 13,
            "gross_burn": "260000",
            "revenue": "80000"
          }
        ]
      },
      {
        "name": "downside",
        "revenue_percent_of_plan": "60"
      }
    ],
    "raises": [
      {
        "amount": "2000000"
      },
      {
        "amount": "3000000",
        "lands_month": 6
      }
    ],
    "milestones": [18],
    "months_to_raise": 6
  }
}
```

`equity_deal_check` for raising now, with no burn fields:

```json
{
  "inputs": {
    "investment": "2000000",
    "pre_money": "8000000",
    "holder_percent": "70"
  }
}
```

`equity_deal_check` for waiting, at the founder's assumed $15M pre:

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "15000000",
    "holder_percent": "70"
  }
}
```

## What the calculator prints (excerpt)

The runway plan:

```text
  Raise 2: lands after                                                         6.00 months  whole months from today
  Runway, plan, raise 1                                                       20.78 months  months until cash less the floor goes below zero
  Runway, plan, raise 2                                                       26.33 months  months until cash less the floor goes below zero
  Ran out before the money lands, plan, raise 2                                         no  cash below the floor before month 6 ends
  Cash above the floor when it lands, plan, raise 2                            $480,000.00  before the raise
  Runway, downside, raise 1                                                   18.55 months  months until cash less the floor goes below zero
  Runway, downside, raise 2                                                   23.26 months  months until cash less the floor goes below zero
  Milestone 1 (month 18), plan, raise 1: verdict                                     short  covered when the runway reaches month 24
  Milestone 1 (month 18), plan, raise 2: verdict                                   covered  covered when the runway reaches month 24
  Milestone 1 (month 18), downside, raise 1: slack                             0.55 months  runway - the milestone month
  Milestone 1 (month 18), downside, raise 1: verdict                                 short  covered when the runway reaches month 24
  Milestone 1 (month 18), downside, raise 2: verdict                                 short  covered when the runway reaches month 24
  Required raise, milestone 1, plan, landing month 0                         $2,580,000.00  smallest raise keeping cash at or above the floor to month 24 (rounded up to the cent)
  Required raise, milestone 1, plan, landing month 6                         $2,580,000.00  smallest raise keeping cash at or above the floor to month 24 (rounded up to the cent)
  Required raise, milestone 1, downside, landing month 0                     $3,156,000.00  smallest raise keeping cash at or above the floor to month 24 (rounded up to the cent)
  Required raise, milestone 1, downside, landing month 6                     $3,156,000.00  smallest raise keeping cash at or above the floor to month 24 (rounded up to the cent)
  Be ready to answer                                               milestone_short_on_plan  A raise does not reach a milestone, with the months to raise, on the plan itself
  Be ready to answer                                      downside_short_where_plan_covers  The cash reaches a milestone on the plan but not on the downside, with the same raise or with none; be ready to say what happens if the plan is missed
```

The two deal checks, now then wait:

```text
  Dilution benchmark                                      25.0000%  given
  Investors' headline share                               20.0000%  I/(V + I)
  After: holder group                                     56.0000%  h·kept
```

```text
  Dilution benchmark                                      25.0000%  given
  Investors' headline share                               16.6667%  I/(V + I)
  After: holder group                                     58.3333%  h·kept
```

## Expected answer

- Side by side. Now: 20.78 months on plan and 18.55 months in the downside, short of month 18 with time to raise on
  both (0.55 months of slack in the downside). Wait: 26.33 months on plan, covered, and 23.26 months in the downside, short. The cash does not run out before
  the waiting option's money lands; $480,000.00 is left above the floor then (on plan).
- The tool's required raise is $2,580,000.00 on plan and $3,156,000.00 in the downside, the same whether it lands
  now or after 6 months.
- Ownership: now sells 20.0000% and leaves the founders 56.0000%; waiting sells 16.6667% and leaves 58.3333%, at a
  $15M pre that is the founder's assumption and is labelled so.
- What has to be true for waiting to work, in the founder's terms: a $15M pre six months from now, the plan's
  revenue through month 6, and the raise closing in month 6. Each is listed, none is judged likely or unlikely.
- Flags: `milestone_short_on_plan` and `downside_short_where_plan_covers`, each in the tool's words. No
  `cash_out_before_raise_lands`.
- Adversarial review: the calculator's short milestones first, not refuted; then the skeptic's kept attacks, each with
  a founder line quoted word for word, for example "The milestone is month 18" under "A milestone with no number, date
  or check"; then Dropped, one line each, including an attack under "No downside case", Dropped, answered, quoting
  "Downside: revenue at 60% of plan". The answer says whether the skeptic ran as a subagent.
- No recommendation to raise now or wait. It closes as not investment, legal or tax advice.
