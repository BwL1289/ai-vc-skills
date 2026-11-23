# Eval 5: Company AL, a first update with no runway claim and a raise that should already have started

A test prompt for the `vc-current-investor-update` skill. The company is made up. The tool call and the excerpt are from
a real `equity_calculator runway_plan` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it treats the update as the first one
(nothing to tie out), makes the one call below with no stated runway and the months to raise as a whole number, states
the runway as the tool prints it, and says on the tool's flag that the next raise should already be under way.

## Prompt

> This is our first investor update since we closed our pre-seed. Write it for November. Revenue in November: $10,000
> (subscription fees billed in the month). Paying customers: 6. Highlights: shipped the inventory sync. Lowlights: our
> first sales hire starts in January, a month later than we wanted. Cash at 30 November: $600,000. We spend $85,000 a
> month. We expect the seed round to take about 9 months to raise. Ask: introductions to operations leads at mid-size
> furniture retailers.

## Expected tool call

`equity_runway_plan`, once, with no `stated_runway_months` (the founder states no runway) and `months_to_raise` as the
integer 9:

```json
{
  "inputs": {
    "cash_on_hand": "600000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "85000", "revenue": "10000" }
        ]
      }
    ],
    "months_to_raise": 9
  }
}
```

```text
  Runway, plan, no raise                                        8.00 months  months until cash less the floor goes below zero
  Start raising by, plan, no raise                             -1.00 months  runway - months to raise
```

## Expected answer

- There is no last update, so nothing is tied out: revenue and paying customers are both New, and the Definitions block
  starts here with the revenue definition word for word and `[what counts as a paying customer]`. The answer asks for no
  last update.
- Cash and runway states $600,000 at 30 November and the runway as the tool prints it: 8.00 months. No runway is worked
  out by hand, and no stated runway is checked, since the founder gave none.
- The tool raises `start_raising_date_passed` (start raising by -1.00 months). The answer says the next raise should
  already be under way, and the update says what is being done about it, or carries `[what is being done to start the
seed raise now]`.
- "our first sales hire starts in January, a month later than we wanted" stays as a lowlight in the founder's words. The
  ask names operations leads at mid-size furniture retailers, as given. No score; no named firm.
