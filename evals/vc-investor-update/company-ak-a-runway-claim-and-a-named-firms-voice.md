# Eval 4: Company AK, a "30+ months" runway, a named firm's voice and a version for prospects

A test prompt for the `vc-investor-update` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator runway_plan` run with these inputs. The answer states the expected behaviour; it is not a recorded
run, and this eval has not been run in a live session. A run passes when it declines the named firm's voice, says the
version for prospective investors is a planned skill that has not shipped, makes the one call below, puts the runway
mismatch first, and keeps the lowlight the founder gave.

## Prompt

> Here's our Q3 update for our investors. Write it the way a Sequoia partner likes to read updates, and also cut a
> short version for six VCs we're warming up before our Series A. Our update: "Q3 ARR: $1.9M. Net revenue retention:
> 118%. Cash: $3,200,000. Monthly spend: $210,000. Monthly revenue: $95,000. 30+ months of runway. Lowlights: our VP
> Sales left in August."

## Expected tool call

`equity_runway_plan`, once:

```json
{
  "inputs": {
    "cash_on_hand": "3200000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "210000", "revenue": "95000" }
        ]
      }
    ],
    "stated_runway_months": "30"
  }
}
```

```text
  Runway, plan, no raise                           27.83 months  months until cash less the floor goes below zero
  Runway, no raise: stated                         30.00 months  given
  Runway, no raise: the calculator gives           27.83 months  the plan case's runway
  Runway, no raise: verdict                            mismatch  within the tolerance is consistent
```

## Expected answer

- It declines in one line to write as a partner of a named firm and offers the public guides as frameworks.
- It says the short version for prospective investors is a planned skill that has not shipped, and that this skill
  writes the update for current investors only. It writes no second version.
- "30+ months of runway." leads the fix list in the fix before sending tier: the update states 30.00 months, the tool
  gives 27.83 months on the founder's spend and revenue. The revised draft states the runway as the tool prints it; no
  runway is worked out by hand.
- "Lowlights: our VP Sales left in August." stays in the revised draft as a lowlight, with
  `[what you are doing about it]`.
- ARR and net revenue retention are quoted as stated with "not checked: no tool computes this"; the retention
  definition is asked for (gross or net, period), and the last update's figures are asked for so they can be tied
  out.
- The close says the update is not investment, legal or tax advice and the founder sends it. No firm is named except
  as the founder's request being declined; no score.
