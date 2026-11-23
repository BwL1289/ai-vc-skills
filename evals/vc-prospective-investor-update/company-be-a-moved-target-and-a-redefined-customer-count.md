# Eval 1: Company BE, a moved target, a redefined customer count and a pilot left half-reported

A test prompt for the `vc-prospective-investor-update` skill. The company and the names are made up. The tool call and
the excerpt are from a real `equity_calculator runway_plan` run with these inputs. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it marks the
customer count Changed definition without comparing the two figures, keeps the moved MRR target and the unreported hire
as findings, drops the definition objection by quoting the draft's own Definitions line, drops the moved enterprise
target by quoting October's update, which already announced the move, makes the one call below and gives its printed
runway under Numbers, and computes nothing in its own text.

## Prompt

> Review my November update to the investors we're warming up for a seed next year. September's update said: "Paying
> customers: 22. MRR: $41,000 (subscription revenue billed in the month). Target: $60,000 MRR by December. Target: 8
> enterprise accounts by December. By the next update: close the two warehouse pilots; hire a head of customer
> success." That was our first update to them. October's said: "Paying customers: 25. MRR: $46,500. We moved the 8
> enterprise accounts target to March: two buyers pushed their budget decisions into the new year. By the next update:
> convert both warehouse pilots to paid; ship the forecasting module." My November draft: "Strong month. Customers
> (paying and pilots): 31. MRR: $49,000. Converted a warehouse pilot to paid. Shipped the forecasting module. On track
> for $60,000 MRR in Q1. On track for 8 enterprise accounts by March. Cash: $1,800,000 at 30 November. Runway: 20
> months. Ask: introductions to operations leaders at third-party logistics firms. Definitions: MRR is subscription
> revenue billed in the month." Notes: "Paying customers: 26. The second warehouse pilot extended to January; they want
> another month of data. We spend $140,000 a month and bring in $49,000. Readers asked last month about our gross
> margin." Goes to: Alex (seed fund), Morgan (angel), Sam (seed fund), Jordan (angel), Alex (seed fund).

## Expected tool call

`equity_runway_plan`, once:

```json
{
  "inputs": {
    "cash_on_hand": "1800000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "140000", "revenue": "49000" }
        ]
      }
    ],
    "stated_runway_months": "20"
  }
}
```

```text
  Runway, plan, no raise                           19.78 months  months until cash less the floor goes below zero
  Runway, no raise: stated                         20.00 months  given
  Runway, no raise: the calculator gives           19.78 months  the plan case's runway
  Runway, no raise: difference                     -0.22 months  computed - stated
  Runway, no raise: verdict                          consistent  within the tolerance is consistent
```

## Expected answer

- The line: paying customers 22 (September), 25 (October), 26 (November, from the notes); MRR $41,000, $46,500 and
  $49,000, each as stated with its month. No change, growth rate or chart appears.
- "Customers (paying and pilots): 31." against "Paying customers: 25." is Changed definition, fix before sending: the
  revised draft keeps "Paying customers: 26" in the line and, if the founder wants the new count, adds it as a new
  metric with its definition. The two figures are never compared. MRR keeps its label and definition: Same, with
  November's value beside October's.
- Moved goalposts, Kept, fix before sending: "Target: $60,000 MRR by December." against "On track for $60,000 MRR in
  Q1." The revised draft names the move in the founder's words with `[why the target moved to Q1]`.
- Last time we said: "convert both warehouse pilots to paid" is Partly done, quoting "Converted a warehouse pilot to
  paid." and "The second warehouse pilot extended to January; they want another month of data."; "ship the forecasting
  module" is Done. September's "hire a head of customer success" was not carried into October's list, so it gets no
  status; the Unreported promise lens raises it (no word anywhere): Kept, worth fixing, with
  `[what happened with the head of customer success hire]`.
- A Changed definitions objection that MRR has no definition is Dropped, answered, quoting "Definitions: MRR is
  subscription revenue billed in the month."
- A Moved goalposts objection on "Target: 8 enterprise accounts by December." against "On track for 8 enterprise
  accounts by March." is Dropped, answered, quoting October's update, the one sent after September's: "We moved the 8
  enterprise accounts target to March: two buyers pushed their budget decisions into the new year." The draft states
  what that line announced, so the founder is not told to name the move again. In the tie-out, October's March target
  is Not yet due. The $60,000 MRR target, which no later update moved, stays Kept.
- Spin: "Strong month." is Kept, worth fixing, and replaced by a plain summary of the founder's facts.
- The readers' gross margin question is an Unreported promise objection, worth fixing, with
  `[gross margin, its definition and period]` in the open asks; no figure is supplied.
- Numbers: 19.78 months, consistent, as the tool prints it; the stated 20 months stands. Goes to: the five names, with
  "Alex (seed fund)" marked as listed twice; no name appears in the update. The close carries the lawyer line on
  mentioning a coming raise.
