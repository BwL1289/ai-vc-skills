# Eval 5: Company BS, a runway the SAFE does not reach and a total that counts a SAFE

A test prompt for the `vc-diligence-questions` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator runway_plan` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the one tool call below
(field order free, money as strings), makes no `equity_deal_check` call, puts the runway mismatch first among the
ranked questions without refuting it, asks for the fully diluted total without the SAFE instead of subtracting it,
keeps the data room to the seed stage's core set, and computes nothing in its own text.

## Prompt

> A seed fund starts diligence next week; prep me. Company BS sells scheduling software to physiotherapy clinics.
> We're raising $1.5M on a SAFE at a $10M post-money cap. The deck says "The raise gives us 36 months of runway." We
> have $200k in the bank, spend $70k a month and bring in $10k a month. Cap table: 9,000,000 shares fully diluted, our
> earlier $300k SAFE counted in. Documents we have: the deck, the cap table spreadsheet, the signed SAFE, our
> incorporation documents.

## Expected tool call

`equity_runway_plan`, once, with the raise as the raise option and the deck's runway as that option's own stated
runway. No `equity_deal_check` call: the raise is a SAFE, which is not passed as `investment`, and the answer asks for
the next priced round the founder expects before any `equity_round` call.

```json
{
  "inputs": {
    "cash_on_hand": "200000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          {
            "from_month": 1,
            "gross_burn": "70000",
            "revenue": "10000"
          }
        ]
      }
    ],
    "raises": [
      {
        "amount": "1500000",
        "stated_runway_months": "36"
      }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Runway, raise 1: stated                          36.00 months  given
  Runway, raise 1: the calculator gives            28.33 months  the plan case's runway
  Runway, raise 1: difference                      -7.67 months  computed - stated
  Runway, raise 1: verdict                             mismatch  within the tolerance is consistent
  Overall verdict                                      mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The runway mismatch heads the ranked list, ahead of the tiers and with no tier, in Financials and cap table, and is
  not put through the refute pass: "The raise gives us 36 months of runway." (the tool prints 36.00 months, given)
  against the tool's 28.33 months, a difference of -7.67 months. The claim is above the computed runway, so the
  understated-runway exception does not apply. The tool returns no flag, so none is relayed. The draft answer uses
  only the tool's figure, asks for `[the corrected deck line]`, and names the monthly cash plan (FIN-D5) as what to put
  in the data room, with `[the monthly cash plan, with and without the raise]`; it never says the deck was corrected.
- The founder's fully diluted total counts the SAFE, so step 2 asks for
  `[fully diluted shares before the round, SAFEs and notes left out]` and passes no share count to any tool; no
  share figure is subtracted or divided.
- Data room: the cap table spreadsheet (FIN-D2), the signed SAFE (FIN-D3) and the incorporation documents (LEG-D1)
  are Ready as named, with the note that a partner will open them; the founder bios (TEAM-D1), the product
  walkthrough (PROD-D1), the executive summary (FIN-D1), the work assignments (LEG-D2), the founders' stock
  agreements (LEG-D3) and the disputes list (LEG-D4) are Missing, each with a bracketed ask. The monthly cash plan
  (FIN-D5) is Missing too, because the runway question's draft answer names it. Every other seed row, the operating
  plan and the budget (FIN-D4, FIN-D6) among them, is named once, in one line, as "if asked".
- No runway, burn or share figure is worked out in its own text beyond the tool's values; no score and no readiness
  percentage.
