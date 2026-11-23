# Eval 1: Company AM, a run-rate called ARR, net retention that counts new customers, a burn multiple on new ARR

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator metrics_check` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the one tool call below
(field order free, money and percents as strings), leads the ranked fix list with the three mismatches and the flag
that explains each, computes nothing in its own text, and gives no score.

## Prompt

> Are my metrics ready for our Series A? Deck slide 6: "$1.5M ARR. 125% net revenue retention over the last 12
> months. Burn multiple 6.25x over the last 12 months." Over the last 12 months: we started at $80,000 MRR; new customers added $24,000 MRR, upsells $6,000, downgrades
> $2,000 and cancellations $8,000. Last month's revenue was $125,000, of which $25,000 was implementation fees. We
> burned $1.8M net over those 12 months.

## Expected tool call

`equity_metrics_check`, once:

```json
{
  "inputs": {
    "period_months": 12,
    "recurring_unit": "monthly",
    "starting_recurring": "80000",
    "new_recurring": "24000",
    "expansion_recurring": "6000",
    "contraction_recurring": "2000",
    "churned_recurring": "8000",
    "month_total_revenue": "125000",
    "month_one_time_revenue": "25000",
    "net_burn": "1800000",
    "stated_arr": "1500000",
    "stated_nrr_percent": "125",
    "stated_burn_multiple": "6.25"
  }
}
```

## What the calculator prints (excerpt)

```text
  ARR at the end of the period                                             $1,200,000.00  k·(S + N + E - C - X)
  Run-rate (12 x the month's revenue)                                      $1,500,000.00  12·T
  Net new ARR                                                                $240,000.00  k·(N + E - C - X)
  Gross revenue retention (12 months)                                           87.5000%  (S - C - X)/S
  Net revenue retention (12 months)                                             95.0000%  (S + E - C - X)/S
  Burn multiple                                                                7.500000x  net burn / net new ARR
  Burn multiple on new ARR only                                                6.250000x  net burn / new ARR
  ARR: the deck says                                                       $1,500,000.00  given
  ARR: the calculator gives                                                $1,200,000.00  the movement's ending ARR, else the latest month's
  ARR: difference                                                           $-300,000.00  computed - stated
  ARR: verdict                                                                  mismatch  within the tolerance is consistent
  Net revenue retention: the deck says                                         125.0000%  given
  Net revenue retention: the calculator gives                                   95.0000%  (S + E - C - X)/S
  Net revenue retention: difference                                            -30.0000%  computed - stated
  Net revenue retention: verdict                                                mismatch  within the tolerance is consistent
  Burn multiple: the deck says                                                 6.250000x  given
  Burn multiple: the calculator gives                                          7.500000x  net burn / net new ARR
  Burn multiple: difference                                                    1.250000x  computed - stated
  Burn multiple: verdict                                                        mismatch  within the tolerance is consistent
  A VC is likely to ask                                      stated_arr_matches_run_rate  The stated ARR matches the run-rate (12 x the whole month's revenue), not recurring revenue; a VC is likely to recompute ARR without one-time, services and usage fees
  A VC is likely to ask                                  run_rate_includes_non_recurring  The latest month has one-time or usage revenue, so its run-rate is above its ARR; say which figure the document shows
  A VC is likely to ask                                          stated_nrr_includes_new  The stated net retention matches ending over starting recurring revenue, which counts new customers; a VC is likely to ask for the starting customers alone
  A VC is likely to ask                        stated_burn_multiple_uses_new_not_net_arr  The stated burn multiple matches net burn over new ARR only, not over net new ARR after churn and contraction
  A VC is likely to ask                                         burn_multiple_above_band  The burn multiple is at or above 3x; a VC is likely to ask what the spend buys (a benchmark, not a rule)
  Overall verdict                                                               mismatch  mismatch if any figure is (an unlabelled churn holds when any basis does); not_checked with none
```

## Expected answer

- The three mismatches lead the ranked fix list as ends the meeting, not refuted, each with the flag that explains
  it. ARR: the deck says $1,500,000.00, the calculator gives $1,200,000.00; `stated_arr_matches_run_rate` says the
  $1.5M is the run-rate, which counts the $25,000 of implementation fees. Net revenue retention: the deck says
  125.0000%, the calculator gives 95.0000% over the 12 months (gross 87.5000%); `stated_nrr_includes_new` says the
  125% counts new customers. Burn multiple: the deck says 6.250000x, the calculator gives 7.500000x;
  `stated_burn_multiple_uses_new_not_net_arr` says the 6.25x is on new ARR, not net new ARR. The ARR and burn
  multiple fixes use the tool's values; the net revenue retention fix is the bracketed ask for the starting
  customers' movements below, not the tool's 95.0000%, which counts customers won during the 12 months. No fix adds a
  new figure.
- All three metrics are Contradicted. Slide 6 states the 12-month period for the retention and the multiple, so they
  go in the 12-month call.
- `run_rate_includes_non_recurring` is relayed as a question a partner is likely to ask: show the run-rate and ARR,
  each named.
- The period is longer than a month and no starting-customer movements were given, so the answer says the tool's
  `cohort_rule` row applies (retention here includes customers won during the 12 months) and asks
  `[upsells, downgrades and cancellations of the customers you had 12 months ago, alone]`.
- `burn_multiple_above_band` is relayed as a question a partner is likely to ask, with the source and date the
  tool's assumption row gives (Sacks, 2020), said to be a benchmark, not a rule; no other benchmark figure appears.
- Stage expectations (Series A, recurring revenue): ARR, net revenue retention and the burn multiple are Present
  (slide 6). ARR's movement is on no document; the founder gave the parts, so the fix is to show it with the tool's
  values. Gross revenue retention is Missing, with the same ask for the starting customers' movements; the tool's
  87.5000% is shown only as its row, with the `cohort_rule` caveat, never as a figure for the slide. Logo churn, CAC
  and payback, gross margin and concentration are Missing, each a bracketed ask.
- No score, no "ready" or "not ready", no firm named as a fit or a voice (Sacks appears only as the cited source);
  nothing is computed, converted or rounded in the answer's own text.
