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
  row). "$1M ARR" itself is quoted as stated and not checked: an ARR target is the vc-metrics-readiness skill's to check
  (`equity_metrics_check`, from monthly recurring revenue), never "no tool computes this", and the open asks ask for the
  monthly recurring revenue it stands for. The answer does not convert ARR to a month by hand.
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

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings. This
is the second run, made after the fixes the first run led to (below). The answer is trimmed; [...] marks each cut.

**Partial: one clause met only in part.** It made the five calls below with the expected arguments and no other, ran
only the founder's three cases, quoted the tool's runways, slacks and required raises with their cents, read the lean
plan for $3M only and said why, and left "$1M ARR" not checked. Its review led with the computed short milestones and
no tier, ran the skeptic and then one refute subagent per attack in a single message, and struck the skeptic's claim
that the downside misses the milestone as a result no tool computed. It quoted the dilution band as the tool prints it,
gave each flag its meaning from the skill's table, printed -2.13 as the start-raising value, used the eleven headings
and gave no recommendation. It computed one figure in its own text: its second attack, relayed from the skeptic, asks
what "the other 15%" of spend is for, a remainder of the founder's 85% that neither the founder nor the tool gave. Of
the other points, it did not name its first attack's pattern and did not list in one place what would have to be true
for each amount. Since this run the skill names a remainder of a founder's percent among the figures an answer never
states, and its check before answering covers the skeptic's text it relays; an ARR milestone, which this run called
something no tool computes, is now named as the vc-metrics-readiness skill's to check. The skill has not been run
again.

The first run, on the same version and day, failed with four clauses missed. It made a sixth call that merged the
downside's revenue cut into the lean plan and put that case in the founder's tables; it never ran the refute pass; it
never quoted the dilution benchmark; and it computed six figures in its own text: the gaps between each amount and the
required raise, and the difference in points between the two options' stakes ("The extra $1M costs the founders 4.25
points now"). It also left out the flags and the -2.13 start-raising value, and opened with a verdict of its own
("Neither amount is safe as planned"). After it the skill banned any gap or difference stated by hand, forbade merging
two cases or a second runway plan call, made the answer's eleven items required headings, launched one refute subagent
per attack in a single message, and carried the deal check's flag meanings; this eval gained the open ask about cutting
spend in the downside, and drops an answered attack only when the skeptic raises it.

> The numbers are all in; here is what each amount buys on your plan. Every figure below is from the equity calculator or your own message.
>
> ## 1. What each amount buys
>
> - **$3M, full plan:** runway 17.90 months on plan and 16.77 in the downside. The month-15 milestone is short in both cases (slack 2.90 and 1.77 months, against your 6 months to raise).
> - **$3M, your lean plan (spend at 85%):** runway 21.06 months, milestone covered, slack 6.06 months. The required raise on the lean plan is $2,989,000.00, beside your $3,000,000.00.
> - [...]
>
> The lean rows for $4M and for no raise are left out because you tie the lean plan to $3M.
>
> ## 2. Table
>
> | Option   | Case | Runway (months) | Milestone (month) | Covered? | Slack (months) | Start raising by (month) |
> | -------- | ---- | --------------- | ----------------- | -------- | -------------- | ------------------------ |
> | No raise | plan | 3.87            | 15                | short    | -11.13         | -2.13                    |
> | [...]    |      |                 |                   |          |                |                          |
> | $3M      | lean | 21.06           | 15                | covered  | 6.06           | 15.06                    |
>
> [...]
>
> 2. **"If we only get $3M, we cut spend to 85% of plan."**
>    - Doubt: the line does not say what is cut, or whether revenue and the milestone month survive the cut. The lean case above keeps revenue at 100% of plan because you stated no change. A partner is likely to ask what the other 15% of spend is for if revenue arrives without it.
>
> [...]
>
> - The skeptic's remark that the milestone is "presumably missed" in the downside was struck as a result no tool computed. It moves to the open asks.
>
> **Dropped:** none.
>
> The skeptic ran as a subagent, and the refute pass ran as one subagent per attack.
>
> ## 7. Flags
>
> - `milestone_short_on_plan`: $3M does not reach the milestone with time to raise, even on plan. This flag counts the plan case only; the $3M lean row covers it.
> - [...]
> - `start_raising_date_passed`: on cash alone, raising should already have started, given your 6 months to raise.
