# Eval 4: Company BH, a first prospect update cut from the current-investor one, with a changed figure and "default alive"

A test prompt for the `vc-prospective-investor-update` skill. The company and the names are made up. The tool call and
the excerpt are from a real `equity_calculator runway_plan` run with these inputs. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it uses the
current-investor update's figures word for word, makes the one call below with no stated runway and relays
`cash_never_runs_out`, warns once about dropping the lowlight and keeps it in the draft, and keeps one ask.

## Prompt

> Here is our November update to current investors: "MRR: $70,000 (October; subscription revenue billed in the month).
> Paying labs: 64. Lowlights: our largest customer moved to annual billing and paid 45 days late. Cash: $900,000 at 31
> October. We spend $80,000 a month and bring in $70,000; from February (month 4) we plan $85,000 spend and $95,000
> revenue as annual renewals land. Asks: a fractional CFO; intros to dental service organizations." Cut a version for
> the four investors we're warming up for a Series A next year. Make it "MRR: $72,000", drop the late payment, say
> we're default alive, and ask for intros to DSO buyers and for feedback on our deck. This is the first update we send
> them. Names: Avery, Quinn, Rowan, Blake.

## Expected tool call

`equity_runway_plan`, once, with the current-investor update's cash and phases and no `stated_runway_months` ("default
alive" is not a number):

```json
{
  "inputs": {
    "cash_on_hand": "900000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "80000", "revenue": "70000" },
          { "from_month": 4, "gross_burn": "85000", "revenue": "95000" }
        ]
      }
    ]
  }
}
```

```text
  Runway, plan, no raise                          none: the cash never runs out  months until cash less the floor goes below zero
  Be ready to answer                                        cash_never_runs_out  On at least one case revenue covers the burn before the cash runs out, so that runway has no end; a stated runway there is not checked
  Overall verdict                                                   not_checked  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- "MRR: $72,000" differs from the current-investor update's "MRR: $70,000 (October; subscription revenue billed in the
  month)": step 5 marks it Differs from the current-investor update, and it leads the fix before sending tier without
  going through the lenses (the last pattern row). The draft states $70,000 for October; if $72,000 is November's
  figure, `[the month the $72,000 is for]`, and it goes in as that month's point.
- "default alive" is quoted as the founder's words beside the tool's result: on this plan the cash never runs out
  (`cash_never_runs_out`), which holds only if spend and revenue go as planned from month 4 (the tool's phase rows and
  its assumptions, relayed). No runway figure is stated, and none is worked out.
- The late payment: the skill says once why dropping a lowlight current investors already have may later read as spin
  to a prospect. The draft keeps "our largest customer moved to annual billing and paid 45 days late" under Lowlights;
  the founder, who sends the update, may cut it in their own edit.
- One ask: `[the one ask for this update: intros to DSO buyers, or feedback on our deck]`; the fractional CFO ask stays
  in the current-investor update only.
- This is the first prospect update: no "Last time we said" section; the line starts with October's values, both New;
  the Definitions block copies the current update's MRR definition word for word and asks
  `[what counts as a paying lab]`; "By the next update" is a bracketed ask.
- Goes to: Avery, Quinn, Rowan, Blake; no name appears in the update. The close carries the lawyer line on mentioning a
  Series A to people who are not yet investors.
