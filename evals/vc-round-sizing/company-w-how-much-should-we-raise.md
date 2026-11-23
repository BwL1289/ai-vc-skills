# Eval 1: Company W, how much to raise, $3M or $4M

A test prompt for the `vc-round-sizing` skill. The company is made up. Every tool call and excerpt is from a real
`equity_calculator` run with these inputs. "Expected answer" states the expected behaviour, and "Recorded answer" is an
excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when it makes the five tool calls below and
no other (field order free, money and percents as strings), says whose cash lasts to the milestone month on plan, in
the downside and on the lean plan with the tool's figures, reads the lean plan for $3M only, leaves "$1M ARR" itself not
checked, runs the refute pass on every attack, quotes the dilution benchmark only as the tool prints it, gives no
recommendation, and computes nothing in its own text. The verdict is Pass when every clause of that sentence is met,
Partial when exactly one clause is missed or met only in part, and Fail when two or more are missed; a shortfall against
the other points of the expected answer is noted but does not change the verdict.

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
  Required raise, milestone 1, plan, landing month 0                         $3,745,000.00  smallest raise keeping cash at or above the floor to month 21
  Required raise, milestone 1, downside, landing month 0                     $4,142,500.00  smallest raise keeping cash at or above the floor to month 21
  Required raise, milestone 1, lean, landing month 0                         $2,989,000.00  smallest raise keeping cash at or above the floor to month 21
  Be ready to answer                                               milestone_short_on_plan  A raise does not reach a milestone, with the months to raise, on the plan itself
  Be ready to answer                                      downside_short_where_plan_covers  A raise reaches a milestone on the plan but not on the downside; be ready to say what happens if the plan is missed
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
- The no-raise row comes first: 3.87 months, start raising by -2.13 months as printed (never "already passed"), with
  the `start_raising_date_passed` flag and its meaning from the skill's flag table.
- Ownership: $3M sells 20.0000% and leaves the founders 68.0000%; $4M sells 25.0000% and leaves 63.7500%. After the A
  as the founder expects it, 47.6000% and 44.6250%.
- The dilution benchmark is quoted only as the tool prints it (Dilution benchmark 25.0000%, its `dilution_band` row,
  source unverified); 25.0000% is not above it, so no flag. No benchmark figure of the skill's own appears.
- Flags, one line each with its meaning from the skill's flag table: `milestone_short_on_plan`,
  `downside_short_where_plan_covers`, `start_raising_date_passed`, `runway_below_band` (a common benchmark, not a rule,
  quoting the tool's `runway_band` row, and asking which milestone $3M reaches rather than calling it short).
- It runs only the founder's three cases, in the one `equity_runway_plan` call: no case merges the downside's revenue
  cut into the lean plan, and the open asks ask whether spend would also be cut in the downside.
- No figure in the text is a gap or a difference worked by hand: no amount said to fall short of or clear the required
  raise by some sum, and no difference in points between the two options' stakes; each pair of tool values sits side
  by side.
- The calculator's short milestones head the review as computed facts, with no tier, and are not refuted. The skeptic's
  strongest kept attack quotes "$1M ARR" beside the plan's "from month 13 $300k with $60k", with the pattern "A revenue
  milestone with no monthly figure" (unverified); an attack on the revenue path under "Revenue in the plan rising with
  no evidence named" may also be kept. An attack that asserts the downside misses the revenue milestone, which no tool
  computes, is Dropped, not grounded.
- The refute pass runs on every attack, one subagent per attack launched in one message, and each attack carries its
  verdict. If the skeptic raises an attack under "No downside case" or "One amount only, no plan for a smaller raise",
  it is Dropped, answered, quoting "Downside: revenue comes in at half of plan" or "If we only get $3M, we cut spend to
  85% of plan": the material supplies what those patterns say is missing, so no kept attack rests on either. The
  answer says whether the skeptic ran as a subagent.
- No recommendation: it says what $4M buys on plan and not in the downside, and lists what would have to be true for
  either amount to work, in the founder's terms. It closes as not investment, legal or tax advice.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Fail: four clauses missed.** It made the five expected calls with the expected arguments, quoted the tool's runways,
slacks and required raises, left "$1M ARR" unconverted and unchecked, and left out the $4M lean rows. But it made a
sixth call that merged the downside's revenue cut into the lean plan and put that case in the founder's tables; it never
ran the refute pass (only the skeptic ran as a subagent, and no attack carried a verdict); it never quoted the dilution
benchmark; and it computed six figures in its own text: the gaps between each amount and the required raise, and the
difference in points between the two options' stakes. It also left out the flags, the -2.13 months start-raising value
and Sources, and opened with a verdict of its own. Since this run the skill bans any gap or difference stated by hand,
forbids merging two cases or a second runway plan call, makes the answer's eleven items required headings, launches one
refute subagent per attack in a single message, and carries the deal check's flag meanings; the eval now expects the
open ask about cutting spend in the downside, and drops an answered attack only when the skeptic raises it.

> **Neither amount is safe as planned: $4M covers the milestone plus your 6 months only if revenue hits plan, and $3M covers it only with the 85% cut and revenue on plan, with about $11k to spare.** In your downside, both fall short. This shows what each amount buys on your figures; it is not a recommendation or investment advice.
>
> [...]
>
> | Option         | Case         | Runway (months) | Covered to month 21? | Slack after month 15 | Start raising the A by |
> | -------------- | ------------ | --------------- | -------------------- | -------------------- | ---------------------- |
> | No raise       | Plan         | 3.87            | Short                | -11.13               | already passed         |
> | [...]          |              |                 |                      |                      |                        |
> | $3M, 85% spend | Half revenue | 19.28           | Short                | 4.28                 | month 13.28            |
>
> [...]
>
> - **$3M:** at full spend it is $745,000 short of the plan requirement, so it only works with the cut. With the cut it clears by $11,000, and it fails if revenue also halves.
> - **$4M:** it clears the plan requirement by $255,000 but is $142,500 short in your downside, with 5.47 months to raise the A instead of 6.
> - **The "85% spend, half revenue" row** is my combination of your two statements; you did not say whether you would cut spend in the downside.
>
> [...]
>
> The extra $1M costs the founders 4.25 points now and 2.975 points after the A. [...]
>
> An independent skeptic pass on your text raised three points, and all three stand:
>
> [...]
>
> 2. **"Downside: revenue comes in at half of plan."** The milestone is a revenue milestone, so your own downside misses it at month 15. [...]
