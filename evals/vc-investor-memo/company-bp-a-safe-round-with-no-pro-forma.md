# Eval 4: Company BP, a SAFE round with no pro forma, a runway that does not hold, and paid pilots

A test prompt for the `vc-investor-memo` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator` runs with these inputs, on this repository's calculator. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it routes the SAFE to
`equity_round` and the runway to `equity_runway_plan`, runs no waterfall and says why in the fixed words, quotes the
memo's 12.5% beside the tool's values without a verdict, feeds the SAFE's own row (not the investor row) to
`equity_dilution` with only the Series B, drops the pilots objection by quoting the founder's notes, and computes
nothing in its own text.

## Prompt

> Draft the memo for our champion. We're raising $2,000,000 on post-money SAFEs at a $16,000,000 cap; our draft says
> "SAFE investors own 12.5%". We expect a Series A in about 18 months: $8,000,000 at a $32,000,000 pre-money with the
> pool topped up to 10%, then a Series B selling 15%. Cap table: 10,000,000 fully diluted shares, 500,000 of them
> unissued pool, no other SAFEs or notes. Cash $600,000; we spend $150,000 a month and bring in $20,000. Draft: "The
> round gives us 24 months of runway." Traction: "three hospital systems in pilots". Notes: "All three pilots are paid,
> $25,000 each, signed in Q3." Exit on plan: $300 million.

## Expected tool call

Three calls: `equity_round` with the Series A the founder expects, `equity_runway_plan` with the SAFE money as cash
only, and `equity_dilution` from the SAFE's own row with only the Series B. No `equity_pool` or `equity_waterfall`
call.

### Call 1: `equity_round`

```json
{
  "inputs": {
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "pre_money": "32000000",
    "investment": "8000000",
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "2000000",
        "valuation_cap": "16000000"
      }
    ]
  }
}
```

```text
  SAFE 1: shares                           1,428,571.429  a / conversion price
  Capped SAFEs' share of C (sigma)              12.5000%  sum of a/K over SAFEs on their cap
  Ownership: SAFE 1                              9.1503%  shares / T
  Ownership: investor                           20.0000%  shares / T
```

### Call 2: `equity_runway_plan`

```json
{
  "inputs": {
    "cash_on_hand": "600000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          {
            "from_month": 1,
            "gross_burn": "150000",
            "revenue": "20000"
          }
        ]
      }
    ],
    "raises": [
      {
        "amount": "2000000",
        "stated_runway_months": "24"
      }
    ]
  }
}
```

```text
  Runway, plan, raise 1                            20.00 months  months until cash less the floor goes below zero
  Runway, raise 1: stated                          24.00 months  given
  Runway, raise 1: the calculator gives            20.00 months  the plan case's runway
  Runway, raise 1: difference                      -4.00 months  computed - stated
  Runway, raise 1: rounds to the deck's "24"                 no  the computed figure, rounded half away from zero to the places the deck writes, is the deck's
  Runway, raise 1: verdict                             mismatch  within the tolerance, or rounding to the deck's, is consistent
```

### Call 3: `equity_dilution`

`holder_percent` is the "Ownership: SAFE 1" row of call 1, not "Ownership: investor"; `rounds` holds only the Series B,
since call 1 already counted the Series A.

```json
{
  "inputs": {
    "holder_percent": "9.1503",
    "rounds": [
      {
        "investor_percent": "15"
      }
    ]
  }
}
```

```text
  Stake before the first round           9.1503%  given
  Round 1: new investors' share (n)     15.0000%  given
  Final stake                            7.7778%  h_0·(1 - n_1 - p_1)···(1 - n_k - p_k)
```

## Expected answer

- The runway mismatch leads the fix list under figures that do not match (computed), with no tier: "24 months of runway"
  against 20.00 months; the memo states 20.00 months.
- The round: "SAFE investors own 12.5%" is quoted beside the tool's 12.5000% (the capped SAFEs' share of company
  capitalization at conversion) and 9.1503% after the Series A the founder expects, labelled the founder's assumption,
  with no verdict; the fix asks the founder to say which of the two the memo means.
- The outcome case: "not run: a SAFE or note holds no shares until the priced round it converts in, so this round has
  no payout to show"; the $300,000,000 exit is listed as the founder's assumption with `[why $300 million]`; no payout
  is worked out. In the fixed SAFE wording of step 7, the stake is 9.1503% after the Series A the founder expects and
  7.7778% after the Series B the founder expects, each as printed and labelled the founder's assumption; what it pays
  at an exit is not checked.
- Dissent, Dropped, answered by the notes, "All three pilots are paid, $25,000 each, signed in Q3.": the Traction lens's
  objection that "three hospital systems in pilots" shows no paying customer. The memo is to carry that line. No total
  of the three pilots is worked out.
- No recommendation; no score; no firm named.
