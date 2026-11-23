# Eval 5: Company BT, a quarter whose ARR shrank, a churn that matches no basis, and a payback with no parts

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator metrics_check` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the one 3-month call below
with the starting customers' movements in the `cohort_*` fields, leaves the payback out of it, marks the churn
Contradicted because no basis row is consistent, and treats the burn multiple's `not_checked` row as Needs a source,
never as a mismatch.

## Prompt

> Are the metrics in our Q3 investor update ready for our Series A meetings? The update says: "Churn in Q3: 4%."
> "Burn multiple for Q3: 1.8x." "CAC payback: 8 months." Q3 figures (July to September): $200,000 MRR at the start of
> July; over the quarter new customers added $10,000 MRR, upsells $4,000, downgrades $6,000 and cancellations
> $14,000. The customers we had on 1 July account for $3,000 of the upsells, all of the downgrades and all of the
> cancellations. 250 customers at the start of July, 15 lost. Net burn over the quarter was $420,000. We sell
> subscriptions to mid-market companies.

## Expected tool call

`equity_metrics_check`, once, for the update's Q3 figures. The update states its churn and multiple for Q3, so
`period_months` is 3. "CAC payback: 8 months." is left out: no sales and marketing spend was given, and the tool would
refuse the whole call for it.

```json
{
  "inputs": {
    "period_months": 3,
    "recurring_unit": "monthly",
    "starting_recurring": "200000",
    "new_recurring": "10000",
    "expansion_recurring": "4000",
    "contraction_recurring": "6000",
    "churned_recurring": "14000",
    "cohort_expansion_recurring": "3000",
    "cohort_contraction_recurring": "6000",
    "cohort_churned_recurring": "14000",
    "customers_start": 250,
    "customers_lost": 15,
    "net_burn": "420000",
    "customer_segment": "mid_market",
    "stated_churn_percent": "4",
    "stated_burn_multiple": "1.8"
  }
}
```

## What the calculator prints (excerpt)

```text
  Net new ARR                                                $-72,000.00  k·(N + E - C - X)
  Gross revenue retention (3 months)                            90.0000%  (S - C' - X')/S; E', C', X' the starting customers' own when given, else the period's total
  Net revenue retention (3 months)                              91.5000%  (S + E' - C' - X')/S; E', C', X' the starting customers' own when given, else the period's total
  Gross revenue churn (3 months)                                10.0000%  (C' + X')/S; E', C', X' the starting customers' own when given, else the period's total
  Net revenue churn (3 months)                                   8.5000%  (C' + X' - E')/S; E', C', X' the starting customers' own when given, else the period's total
  Logo churn (3 months)                                          6.0000%  customers lost / at the start
  Churn (logo): the deck says                                    4.0000%  given
  Churn (logo): the calculator gives                             6.0000%  customers lost / customers at the start
  Churn (logo): verdict                                         mismatch  within the tolerance, or rounding to the deck's, is consistent
  Churn (gross revenue): the calculator gives                   10.0000%  (C' + X')/S; E', C', X' the starting customers' own when given, else the period's total
  Churn (gross revenue): verdict                                mismatch  within the tolerance, or rounding to the deck's, is consistent
  Churn (net revenue): the calculator gives                      8.5000%  (C' + X' - E')/S; E', C', X' the starting customers' own when given, else the period's total
  Churn (net revenue): verdict                                  mismatch  within the tolerance, or rounding to the deck's, is consistent
  Burn multiple: the deck says                                 1.800000x  given
  Burn multiple: the calculator gives                               none  no multiple: net burn or net new ARR is zero or below
  Burn multiple: verdict                                     not_checked  nothing to check it against, so the overall verdict cannot be consistent
  A VC is likely to ask                           churn_basis_unlabelled  The churn figure names no basis, so it was checked on every basis these figures give; label it logo, gross revenue or net revenue churn
  A VC is likely to ask                        burn_multiple_not_defined  Net new ARR is zero or below in the period, so there is no burn multiple; a stated multiple is not checked, and the overall verdict cannot be consistent
  Overall verdict                                               mismatch  mismatch if any figure is (an unlabelled churn holds when any basis does); else not_checked with none checked or one left unchecked; else consistent
```

## Expected answer

- "Churn in Q3: 4%." is Contradicted: an unlabelled churn that mismatches on every basis the tool checked (logo
  6.0000%, gross revenue 10.0000%, net revenue 8.5000%, the update says 4.0000%). No `stated_*` flag explains it, so it
  leads the ranked fix list with no tier, the founder weighing the gap, and its fix asks `[how the model works this
figure, unrounded]`. `churn_basis_unlabelled` is relayed: name the basis, and show logo and gross revenue churn
  beside net. Each row is relayed as "the update says", not the report's "the deck says".
- "Burn multiple for Q3: 1.8x." gets a `not_checked` row, the calculator giving none: net new ARR is $-72,000.00,
  and `burn_multiple_not_defined` says there is no multiple to check. It is not a calculator mismatch, and no
  `stated_burn_multiple_uses_new_not_net_arr` flag is beside it (the update's 1.8x is not the 3.500000x on new ARR
  only). The fix is the Flags table's: drop the multiple and show net burn and the ARR movement. It is Needs a source,
  with `[how the 1.8x is worked: which burn and which ARR movement]`.
- "CAC payback: 8 months." is Needs a source, left out of the call: `[sales and marketing spend in Q3 and what it
includes]` and `[gross margin in Q3]`. The answer says it can be checked once those are given.
- The starting customers' movements were given, so the `cohort_rule` row reads "the starting customers' own
  expansion, contraction and churn", the report prints the primed formulas, and the tool's retention values (gross 90.0000%, net 91.5000% over the 3 months) may be shown as the
  figures for the slide, with the period beside them.
- Stage expectations (Series A, recurring revenue): the churn, the payback and the burn multiple are Present (quoted).
  ARR and its movement, gross and net revenue retention and logo churn are Missing, on no line of the update; the
  founder gave their parts, so the fix is to show them with the tool's values and the period. CAC, gross margin and
  concentration are Missing, each a bracketed ask.
- No score, no "ready" or "not ready", no firm named as a fit or a voice; nothing is computed, converted or rounded in
  the answer's own text.
