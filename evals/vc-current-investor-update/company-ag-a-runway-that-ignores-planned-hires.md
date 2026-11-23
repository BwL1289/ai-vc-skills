# Eval 1: Company AG, a monthly update whose runway ignores the planned hires

A test prompt for the `vc-current-investor-update` skill. The company is made up. The tool calls and the excerpts are
from real `equity_calculator runway_plan` runs with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the two calls below (field
order free, money as strings), states the runway as the tool prints it, ties out last month's two "next month" items as
lowlights in the founder's words, and computes nothing in its own text.

## Prompt

> Write our October investor update. Last month's update said: "Highlights: signed our 12th paying clinic. Next month:
> hire two engineers and launch the scheduling add-on. Runway: 15 months." This month: 14 paying clinics; MRR $22,000,
> which we report for the first time (recurring subscription revenue billed in the month). We hired one engineer, not
> two; the second candidate declined. The scheduling add-on slipped to December because of a billing bug. Cash at 31
> October: $1,100,000. We spend $95,000 a month and bring in $22,000; from month 4 (February), with the two hires, we
> plan to spend $120,000 a month with $30,000 of revenue. Runway: 15 months. Ask: introductions to practice managers at
> multi-site dental groups.

## Expected tool call

`equity_runway_plan`, twice. First the plan:

```json
{
  "inputs": {
    "cash_on_hand": "1100000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "95000", "revenue": "22000" },
          { "from_month": 4, "gross_burn": "120000", "revenue": "30000" }
        ]
      }
    ],
    "stated_runway_months": "15"
  }
}
```

```text
  Runway, plan, no raise                           12.79 months  months until cash less the floor goes below zero
  Runway, no raise: stated                         15.00 months  given
  Runway, no raise: the calculator gives           12.79 months  the plan case's runway
  Runway, no raise: difference                     -2.21 months  computed - stated
  Runway, no raise: verdict                            mismatch  within the tolerance is consistent
```

Then today's spend held flat, because the plan changes the burn and the claim is a mismatch:

```json
{
  "inputs": {
    "cash_on_hand": "1100000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "95000", "revenue": "22000" }
        ]
      }
    ],
    "stated_runway_months": "15"
  }
}
```

```text
  Runway, plan, no raise                           15.07 months  months until cash less the floor goes below zero
  Runway, no raise: verdict                          consistent  within the tolerance is consistent
```

## Expected answer

- The draft's Cash and runway section states $1,100,000 at 31 October and the runway as the tool prints it: 12.79 months
  on the plan with the two hires, 15.07 months at today's spend held flat. "Runway: 15 months" does not appear as the
  update's figure.
- The calculator's mismatch leads the fix list in the fix before sending tier; the same runway figure two updates
  running is named as a pattern (unverified). The answer computes no runway itself and explains no gap with a division.
- Tie-out: "hire two engineers" and "launch the scheduling add-on" each get a lowlight in the founder's words ("We hired
  one engineer, not two; the second candidate declined." and "The scheduling add-on slipped to December because of a
  billing bug."). Paying clinics: 12 in the last update, 14 now, both quoted, status Same; no growth is worked out. MRR
  is New (the last update gave none) and carries its definition.
- The ask names the practice managers at multi-site dental groups, as given. The Definitions block holds the MRR
  definition word for word. No score; no named firm.
