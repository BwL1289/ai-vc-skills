# Eval 1: Company W, how much to raise, $3M or $4M

A test prompt for the `vc-round-sizing` skill. The company is made up. Every tool call and excerpt is from a real
`equity_calculator` run with these inputs. The answer states the expected behaviour; it is not a recorded run, and this
eval has not been run in a live session. A run passes when it makes the five tool calls below (field order free, money
and percents as strings), says whose cash lasts to the milestone month on plan, in the downside and on the lean plan
with the tool's figures, reads the lean plan for $3M only, leaves "$1M ARR" itself not checked, drops the attacks the
founder's material answers, quotes the dilution benchmark only as the tool prints it, gives no recommendation, and
computes nothing in its own text.

## Prompt

> How much should we raise, $3M or $4M, at our $12M pre? We have $500k in the bank. Our plan: months 1-3 we spend
> $120k a month with $10k of revenue, months 4-12 $220k with $25k, and from month 13 $300k with $60k. The milestone
> for the A is "$1M ARR", by month 15, and we allow 6 months to raise the A after that. Downside: revenue comes in at
> half of plan. If we only get $3M, we cut spend to 85% of plan. The founders hold 85% today. We expect the A to sell
> 20% with a new 10% pool.

## Expected tool call

Five calls, in this order.

`equity_runway_plan`, once, with both amounts, the three cases and the milestone:

```json
{
  "inputs": {
    "cash_on_hand": "500000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          {
            "from_month": 1,
            "gross_burn": "120000",
            "revenue": "10000"
          },
          {
            "from_month": 4,
            "gross_burn": "220000",
            "revenue": "25000"
          },
          {
            "from_month": 13,
            "gross_burn": "300000",
            "revenue": "60000"
          }
        ]
      },
      {
        "name": "downside",
        "revenue_percent_of_plan": "50"
      },
      {
        "name": "lean",
        "gross_burn_percent_of_plan": "85"
      }
    ],
    "raises": [
      {
        "amount": "3000000"
      },
      {
        "amount": "4000000"
      }
    ],
    "milestones": [15],
    "months_to_raise": 6
  }
}
```

`equity_deal_check` for $3M, with no burn fields:

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "12000000",
    "holder_percent": "85"
  }
}
```

`equity_deal_check` for $4M:

```json
{
  "inputs": {
    "investment": "4000000",
    "pre_money": "12000000",
    "holder_percent": "85"
  }
}
```

`equity_dilution` for $3M, then the A as the founder expects it:

```json
{
  "inputs": {
    "holder_percent": "85",
    "rounds": [
      {
        "pre_money": "12000000",
        "investment": "3000000"
      },
      {
        "investor_percent": "20",
        "pool_percent": "10"
      }
    ]
  }
}
```

`equity_dilution` for $4M, then the A:

```json
{
  "inputs": {
    "holder_percent": "85",
    "rounds": [
      {
        "pre_money": "12000000",
        "investment": "4000000"
      },
      {
        "investor_percent": "20",
        "pool_percent": "10"
      }
    ]
  }
}
```

## What the calculator prints (excerpt)

The runway plan:

```text
  Plan, phase 3 (month 13 on): revenue a month                                  $60,000.00  given
  Lean, phase 3 (month 13 on): gross burn a month                              $255,000.00  the plan's, scaled by the case's percent
  Runway, plan, no raise                                                       3.87 months  months until cash less the floor goes below zero
  Start raising by, plan, no raise                                            -2.13 months  runway - months to raise
  Runway, plan, raise 1                                                       17.90 months  months until cash less the floor goes below zero
  Runway, plan, raise 2                                                       22.06 months  months until cash less the floor goes below zero
  Runway, downside, raise 1                                                   16.77 months  months until cash less the floor goes below zero
  Runway, downside, raise 2                                                   20.47 months  months until cash less the floor goes below zero
  Runway, lean, raise 1                                                       21.06 months  months until cash less the floor goes below zero
  Milestone 1 (month 15), plan, raise 1: slack                                 2.90 months  runway - the milestone month
  Milestone 1 (month 15), plan, raise 1: verdict                                     short  covered when the runway reaches month 21
  Milestone 1 (month 15), plan, raise 2: slack                                 7.06 months  runway - the milestone month
  Milestone 1 (month 15), plan, raise 2: verdict                                   covered  covered when the runway reaches month 21
  Milestone 1 (month 15), downside, raise 1: slack                             1.77 months  runway - the milestone month
  Milestone 1 (month 15), downside, raise 1: verdict                                 short  covered when the runway reaches month 21
  Milestone 1 (month 15), downside, raise 2: slack                             5.47 months  runway - the milestone month
  Milestone 1 (month 15), downside, raise 2: verdict                                 short  covered when the runway reaches month 21
  Milestone 1 (month 15), lean, raise 1: slack                                 6.06 months  runway - the milestone month
  Milestone 1 (month 15), lean, raise 1: verdict                                   covered  covered when the runway reaches month 21
  Required raise, milestone 1, plan, landing month 0                         $3,745,000.00  smallest raise keeping cash at or above the floor to month 21 (rounded up to the cent)
  Required raise, milestone 1, downside, landing month 0                     $4,142,500.00  smallest raise keeping cash at or above the floor to month 21 (rounded up to the cent)
  Required raise, milestone 1, lean, landing month 0                         $2,989,000.00  smallest raise keeping cash at or above the floor to month 21 (rounded up to the cent)
  Be ready to answer                                               milestone_short_on_plan  A raise does not reach a milestone, with the months to raise, on the plan itself
  Be ready to answer                                      downside_short_where_plan_covers  The cash reaches a milestone on the plan but not on the downside, with the same raise or with none; be ready to say what happens if the plan is missed
  Be ready to answer                                             start_raising_date_passed  With no raise, the plan's runway less the months to raise is already at or past today: on the plan, raising the next round takes longer than the cash lasts
  Be ready to answer                                                     runway_below_band  A raise lasts under 18 months on the plan; be ready to say which milestone it reaches (a common benchmark, not a rule)
  Overall verdict                                                              not_checked  mismatch if any check is; consistent if all are; not_checked with none
```

The two deal checks, $3M then $4M:

```text
  Dilution benchmark                                      25.0000%  given
  Investors' headline share                               20.0000%  I/(V + I)
  After: holder group                                     68.0000%  h·kept
```

```text
  Dilution benchmark                                      25.0000%  given
  Investors' headline share                               25.0000%  I/(V + I)
  After: holder group                                     63.7500%  h·kept
```

The two dilution runs, $3M then $4M:

```text
  Round 1: stake after                         68.0000%  stake before·(1 - n - p)
  Round 2: stake after                         47.6000%  stake before·(1 - n - p)
```

```text
  Round 1: stake after                         63.7500%  stake before·(1 - n - p)
  Round 2: stake after                         44.6250%  stake before·(1 - n - p)
```

## Expected answer

- What each amount buys: $3M lasts 17.90 months on plan and 16.77 months in the downside, and is short of month 15
  with time to raise on both (slack 2.90 months on plan and 1.77 months in the downside; the tool covers it only when
  the runway reaches month 21, since slack counts from month 15). On the founder's lean plan, which is for $3M, it
  lasts 21.06 months, covered with 6.06 months of slack. $4M lasts 22.06 months on plan, covered with 7.06 months of
  slack, and 20.47 months in the downside, short. The lean rows the tool prints for $4M are left out, and the answer
  says why: the lean plan is the founder's plan for $3M.
- `milestone_short_on_plan` counts the plan case only: the answer quotes it beside $3M's covered lean verdict and does
  not drop either.
- A covered verdict says only that the cash lasts to month 15 plus 6 months to raise (the tool's `milestone_rule`
  row). "$1M ARR" itself is quoted as stated, "not checked: no tool computes this", and the open asks ask for the
  revenue a month the plan needs by month 15 for it. The answer does not convert ARR to a month by hand.
- The tool's required raise to reach month 15 with 6 months to raise is $3,745,000.00 on plan, $4,142,500.00 in the
  downside and $2,989,000.00 on the lean plan. The answer quotes them and does not round them to a nicer number.
- The no-raise row comes first: 3.87 months, start raising by -2.13 months, with the `start_raising_date_passed` flag
  in the tool's words.
- Ownership: $3M sells 20.0000% and leaves the founders 68.0000%; $4M sells 25.0000% and leaves 63.7500%. After the A
  as the founder expects it, 47.6000% and 44.6250%.
- The dilution benchmark is quoted only as the tool prints it (Dilution benchmark 25.0000%, its `dilution_band` row,
  source unverified); 25.0000% is not above it, so no flag. No benchmark figure of the skill's own appears.
- Flags, one line each: `milestone_short_on_plan`, `downside_short_where_plan_covers`, `start_raising_date_passed`,
  `runway_below_band` (a common benchmark, not a rule, quoting the tool's `runway_band` row).
- The calculator's short milestones head the review and are not refuted. The skeptic's strongest kept attack quotes
  "$1M ARR" beside the plan's "from month 13 $300k with $60k", with the pattern "A revenue milestone with no monthly
  figure" (unverified); an attack on the revenue path under "Revenue in the plan rising with no evidence named" may
  also be kept.
- Dropped, answered: an attack under "No downside case", quoting "Downside: revenue comes in at half of plan", and one
  under "One amount only, no plan for a smaller raise", quoting "If we only get $3M, we cut spend to 85% of plan". The
  material supplies what those patterns say is missing. The answer says whether the skeptic ran as a subagent.
- No recommendation: it says what $4M buys on plan and not in the downside, and lists what would have to be true for
  either amount to work, in the founder's terms. It closes as not investment, legal or tax advice.
