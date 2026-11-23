# Eval 2: Company AN, a churn figure with no basis, a payback the deck and the model state differently, and a burn the update defines

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The tool calls and the excerpts are from
real `equity_calculator metrics_check` runs with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes one call per document that
states a figure the tool checks, marks the payback Contradicted from the deck's call, marks the deck's churn Will be
discounted with the tool's three bases, and drops the burn objection as answered by the update's line.

## Prompt

> Do my metrics match across the deck, the model and the update? Deck slide 5: "Monthly churn: 2%. CAC payback: 7.2
> months. Burn: $40k a month." Model, KPI tab, October: "CAC payback 9.6 months (gross-margin adjusted)." October
> update: "Net revenue churn was 2% in October." and "Net burn in October was $40k: spend less customer collections."
> October figures: 400 customers at the start, 12 lost, 45 new (20 from paid ads); $50,000 MRR at the start, $5,000
> new, $500 expansion, $500 downgrades, $1,000 cancelled; $36,000 sales and marketing spend; 75% gross margin. We sell
> to small businesses.

## Expected tool call

`equity_metrics_check`, three times: once per document, each with the October parts and only that document's stated
figures. The burn lines go to no call: the tool checks no stated burn. The deck's call:

```json
{
  "inputs": {
    "period_months": 1,
    "recurring_unit": "monthly",
    "starting_recurring": "50000",
    "new_recurring": "5000",
    "expansion_recurring": "500",
    "contraction_recurring": "500",
    "churned_recurring": "1000",
    "customers_start": 400,
    "customers_lost": 12,
    "customers_new": 45,
    "customers_new_paid": 20,
    "sales_marketing_spend": "36000",
    "gross_margin_percent": "75",
    "customer_segment": "smb",
    "stated_churn_percent": "2",
    "stated_cac_payback_months": "7.2"
  }
}
```

What the calculator prints for the deck (excerpt):

```text
  Gross revenue churn (1 month)                                           3.0000%  (C + X)/S
  Net revenue churn (1 month)                                             2.0000%  (C + X - E)/S
  Logo churn (1 month)                                                    3.0000%  customers lost / at the start
  CAC, blended                                                            $800.00  spend / new customers
  CAC, paid                                                             $1,800.00  spend / new customers from paid channels
  CAC payback (gross margin)                                          9.60 months  spend/(new monthly recurring·margin)
  CAC payback (revenue only)                                          7.20 months  spend/new monthly recurring
  Churn (logo): the deck says                                             2.0000%  given
  Churn (logo): the calculator gives                                      3.0000%  customers lost / customers at the start
  Churn (logo): difference                                                1.0000%  computed - stated
  Churn (logo): verdict                                                  mismatch  within the tolerance is consistent
  Churn (gross revenue): the deck says                                    2.0000%  given
  Churn (gross revenue): the calculator gives                             3.0000%  (C + X)/S
  Churn (gross revenue): difference                                       1.0000%  computed - stated
  Churn (gross revenue): verdict                                         mismatch  within the tolerance is consistent
  Churn (net revenue): the deck says                                      2.0000%  given
  Churn (net revenue): the calculator gives                               2.0000%  (C + X - E)/S
  Churn (net revenue): difference                                         0.0000%  computed - stated
  Churn (net revenue): verdict                                         consistent  within the tolerance is consistent
  CAC payback: the deck says                                          7.20 months  given
  CAC payback: the calculator gives                                   9.60 months  spend/(new monthly recurring·margin), or on revenue with no margin
  CAC payback: difference                                             2.40 months  computed - stated
  CAC payback: verdict                                                   mismatch  within the tolerance is consistent
  A VC is likely to ask                                    churn_basis_unlabelled  The churn figure names no basis, so it was checked on every basis these figures give; label it logo, gross revenue or net revenue churn
  A VC is likely to ask                        stated_payback_not_margin_adjusted  The stated payback matches the revenue-only payback, not the payback on gross margin; Bessemer measures it after gross margin, so a VC may recompute it that way
  Overall verdict                                                        mismatch  mismatch if any figure is (an unlabelled churn holds when any basis does); not_checked with none
```

The model's call:

```json
{
  "inputs": {
    "period_months": 1,
    "recurring_unit": "monthly",
    "starting_recurring": "50000",
    "new_recurring": "5000",
    "expansion_recurring": "500",
    "contraction_recurring": "500",
    "churned_recurring": "1000",
    "customers_start": 400,
    "customers_lost": 12,
    "customers_new": 45,
    "customers_new_paid": 20,
    "sales_marketing_spend": "36000",
    "gross_margin_percent": "75",
    "customer_segment": "smb",
    "stated_cac_payback_months": "9.6"
  }
}
```

What the calculator prints for the model (excerpt):

```text
  CAC payback (gross margin)                                 9.60 months  spend/(new monthly recurring·margin)
  CAC payback (revenue only)                                 7.20 months  spend/new monthly recurring
  CAC payback: the deck says                                 9.60 months  given
  CAC payback: the calculator gives                          9.60 months  spend/(new monthly recurring·margin), or on revenue with no margin
  CAC payback: difference                                    0.00 months  computed - stated
  CAC payback: verdict                                        consistent  within the tolerance is consistent
  Overall verdict                                             consistent  mismatch if any figure is (an unlabelled churn holds when any basis does); not_checked with none
```

The update's call:

```json
{
  "inputs": {
    "period_months": 1,
    "recurring_unit": "monthly",
    "starting_recurring": "50000",
    "new_recurring": "5000",
    "expansion_recurring": "500",
    "contraction_recurring": "500",
    "churned_recurring": "1000",
    "customers_start": 400,
    "customers_lost": 12,
    "customers_new": 45,
    "customers_new_paid": 20,
    "sales_marketing_spend": "36000",
    "gross_margin_percent": "75",
    "customer_segment": "smb",
    "stated_churn_percent": "2",
    "stated_churn_basis": "net_revenue"
  }
}
```

What the calculator prints for the update (excerpt):

```text
  Net revenue churn (1 month)                                    2.0000%  (C + X - E)/S
  Churn (net revenue): the deck says                             2.0000%  given
  Churn (net revenue): the calculator gives                      2.0000%  (C + X - E)/S
  Churn (net revenue): difference                                0.0000%  computed - stated
  Churn (net revenue): verdict                                consistent  within the tolerance is consistent
  Overall verdict                                             consistent  mismatch if any figure is (an unlabelled churn holds when any basis does); not_checked with none
```

## Expected answer

- The deck's payback leads the ranked fix list as ends the meeting: the deck says 7.20 months, the calculator gives
  9.60 months on gross margin, a difference of 2.40 months, and `stated_payback_not_margin_adjusted` says the 7.2 is
  the revenue-only payback (7.20 months). The model's 9.6 is consistent (9.60 months). CAC payback is Contradicted,
  with the fix to state the model's figure and its basis on the slide.
- "Monthly churn: 2%." is not a calculator mismatch, because one basis row is consistent: it matches net revenue
  churn (2.0000%) only, while logo churn and gross revenue churn are 3.0000%. It is Will be discounted under the
  pattern table's row for "Churn" with no basis (a16z "16 Startup Metrics" (11)), and `churn_basis_unlabelled` is relayed. The fix:
  label it net revenue churn and show logo and gross revenue churn beside it. The update's "Net revenue churn was 2%
  in October." is consistent in its own call, yet it does not drop the objection, because it matches the "Net revenue
  churn shown alone" pattern.
- The burn-and-efficiency lens's objection that "Burn: $40k a month." does not say net or gross is listed under
  Dropped, answered, quoting "Net burn in October was $40k: spend less customer collections.", with the fix to put
  that definition beside the figure on the slide.
- No `payback_above_band` flag fires, so no benchmark figure appears in the answer.
- `blended_cac_only` is not raised (the paid split was given); both CACs are shown as the tool printed them, $800.00
  blended and $1,800.00 paid.
- Check rows from the model's and the update's calls are relayed as "the model says" and "the update says", never
  as the report's "the deck says": the model says 9.60 months, the deck says 7.20 months.
- The prompt gives no stage of the raise and no business model, so the open asks include `[the stage of this raise
and the business model]`, and stage expectations wait for the answer.
- No figure is converted or computed by the model; no score; no firm named as a fit or a voice.
