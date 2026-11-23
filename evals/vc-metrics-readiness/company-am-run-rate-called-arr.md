# Eval 1: Company AM, a run-rate called ARR, net retention that counts new customers, a burn multiple on new ARR

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator metrics_check` run with these inputs. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when it makes the
one tool call below (field order free, money and percents as strings), runs the five lenses as subagents, leads the
ranked fix list with the three mismatches and the flag that explains each, computes nothing in its own text, and gives
no score. The verdict is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or
met only in part, and Fail when two or more are missed; a shortfall against the other points of the expected answer is
noted but does not change the verdict.

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
  A VC is likely to ask                                          stated_nrr_includes_new  The stated net retention matches ending over starting recurring revenue, which counts revenue from customers who were not there at the start (new customers, or their expansion); a VC is likely to ask for the starting customers alone
  A VC is likely to ask                        stated_burn_multiple_uses_new_not_net_arr  The stated burn multiple matches net burn over new ARR only, not over net new ARR after churn and contraction
  A VC is likely to ask                                         burn_multiple_above_band  The burn multiple is at or above 3x; a VC is likely to ask what the spend buys (a benchmark, not a rule)
  Overall verdict                                                               mismatch  mismatch if any figure is (an unlabelled churn holds when any basis does); else not_checked with none checked or one left unchecked; else consistent
```

## Expected answer

- The three mismatches lead the ranked fix list ahead of the tiers, with no tier, not refuted, each with the flag that
  explains it. ARR: the deck says $1,500,000.00, the calculator gives $1,200,000.00; `stated_arr_matches_run_rate` says
  the $1.5M is the run-rate, which counts the $25,000 of implementation fees. Net revenue retention: the deck says
  125.0000%, the calculator gives 95.0000% over the 12 months (gross 87.5000%); `stated_nrr_includes_new` says the 125%
  counts new customers. Burn multiple: the deck says 6.250000x, the calculator gives 7.500000x;
  `stated_burn_multiple_uses_new_not_net_arr` says the 6.25x is on new ARR, not net new ARR. The ARR and burn multiple
  fixes use the tool's values; the net revenue retention fix is the bracketed ask for the starting customers' movements
  below, not the tool's 95.0000%, which counts customers won during the 12 months. No fix adds a new figure.
- All three metrics are Contradicted. Slide 6 states the 12-month period for the retention and the multiple, so they
  go in the 12-month call.
- `run_rate_includes_non_recurring` is relayed as a question a partner is likely to ask: show the run-rate and ARR,
  each named.
- Every tool value keeps the digits the report prints (95.0000%, 7.500000x, $1,200,000.00), never trimmed or
  abbreviated.
- The period is longer than a month and no starting-customer movements were given, so the answer says the tool's
  `cohort_rule` row applies (retention here includes customers won during the 12 months) and asks
  `[upsells, downgrades and cancellations of the customers you had 12 months ago, alone]`.
- `burn_multiple_above_band` is relayed as a question a partner is likely to ask, with the source and date the
  tool's assumption row gives (Sacks, 2020), said to be a benchmark, not a rule, and only for the tool's 7.500000x:
  the deck's 6.25x is never set against the benchmark. No other benchmark figure appears.
- Stage expectations (Series A, recurring revenue): ARR, net revenue retention and the burn multiple are Present
  (slide 6). ARR's movement is Missing, on no document; the founder gave the parts, so the fix is to show it with the
  tool's values. Gross revenue retention is Missing, with the same ask for the starting customers' movements; the tool's
  87.5000% is shown only as its row, with the `cohort_rule` caveat, never as a figure for the slide. Logo churn, CAC
  and payback, gross margin and concentration are Missing, each a bracketed ask.
- The five lenses run as subagents (Revenue definitions, Retention and churn, Acquisition and payback, Burn and
  efficiency, Stage fit), then one refute subagent per objection, the refute subagents launched in one message. The
  ranked fix list has a Lens column, and the answer lists each lens with what it returned, "nothing found" included.
- No score, no "ready" or "not ready", no firm named as a fit or a voice (Sacks appears only as the cited source);
  nothing is computed, converted or rounded in the answer's own text.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository. The answer is trimmed;
[...] marks each cut.

**Partial: one clause missed.** It made the one call above with the expected inputs, led the ranked fix list with the
three mismatches, each with the flag that explains it, computed nothing and gave no score. The lenses did not run as
subagents: the session had the Task tool, yet the transcript holds no subagent call, and the answer says the lenses ran
in the main agent. Short of the expected answer: the three mismatches sit in the top tier; the fix list has no Lens
column and no lens result beyond the mismatches; tool values are trimmed or abbreviated ("95%", "7.5x", "$1.2M ARR");
the deck's 6.25x is set against the 3x benchmark by eye; two flags are relayed as statements, not questions; the
`cohort_rule` row is never named; the Missing stage rows carry no bracketed ask; and the retention rule is credited to
Bessemer, though the tool's row marks it as the tool's own unverified judgment. Since this run the skill opens its
Steps by running the lenses and the refute pass as subagents whenever the tool is there, puts the calculator's
mismatches ahead of the tiers with no tier, keeps every digit of a tool value, relays a benchmark flag only for the
value it was raised on, asks for each flag as a question with its fix, names the `cohort_rule` row, puts each Missing
row's ask in the row, and takes each assumption's source from the tool's row; the eval has not been run again.

> All three figures on slide 6 fail the check against the parts you gave me: each one matches a looser definition than the one its label claims. I can't give a ready/not-ready verdict, but these are the lines a partner is likely to test first.
>
> [...]
>
> ## Ranked fix list
>
> All three are calculator mismatches explained by a definition flag, so all sit in the top tier.
>
> | Rank | Tier             | The line (slide 6)                                   | Why a partner reads it that way                                                                                                       | Fix                                                                                                                                                                               |
> | ---- | ---------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | 1    | Ends the meeting | "$1.5M ARR"                                          | It equals the run-rate of $1,500,000.00, and last month includes $25,000 of one-time implementation fees. ARR excludes one-time fees. | State "$1.2M ARR", and show the "$1.5M revenue run-rate" on its own line if you want it.                                                                                          |
> | 2    | Ends the meeting | "125% net revenue retention over the last 12 months" | New-customer revenue is growth, not retention. Without it, the calculator gives 95% net and 87.5% gross.                              | Restate on the starting customers only, and show gross retention beside it. First I need `[upsells, downgrades and cancellations from the customers you had 12 months ago only]`. |
> | 3    | Ends the meeting | "Burn multiple 6.25x over the last 12 months"        | It uses new ARR of $288,000.00 rather than net new ARR of $240,000.00, which flatters efficiency.                                     | State 7.5x: $1.8M net burn over $240,000.00 net new ARR.                                                                                                                          |
>
> [...]
>
> **On the burn multiple:** both 6.25x and 7.5x are above the 3x benchmark the calculator uses (David Sacks, "The Burn Multiple", 2020). [...] That is a benchmark, not a rule, but be ready to say why the burn is that high.
>
> Nothing was dropped: no line of your material answers these three objections. I ran the review lenses myself rather than as independent subagents, so they are less independent than they would be.
>
> [...]
>
> - **Flags:**
>   - The stated ARR agrees with the run-rate, not with recurring revenue.
>   - The month has one-time revenue, so run-rate and ARR differ.
>   - The stated net retention counts new customers.
>   - The stated burn multiple uses new ARR, not net new ARR.
>   - The burn multiple is above the 3x benchmark.
> - **Assumption on ARR:** it excludes "one-time fees, professional service fees, and any variable usage fees" (a16z, "16 More Startup Metrics", 2015).
> - **Assumption on retention:** leaving new customers out follows Bessemer's definitions (2021); naming their inclusion as a mistake is the tool's own unverified judgment.
>
> [...]
>
> ## Stage expectations (Series A, recurring revenue)
>
> | Metric                                            | Status                                     |
> | ------------------------------------------------- | ------------------------------------------ |
> | ARR                                               | Present, mislabelled ("$1.5M ARR")         |
> | ARR movement (new, expansion, contraction, churn) | Missing from the slide; you have the parts |
> | Net revenue retention                             | Present, wrong basis                       |
> | Gross revenue retention                           | Missing                                    |
> | [...]                                             |                                            |
>
> [...]
>
> This is not investment, legal, tax or accounting advice. How revenue is recognised is a question for your accountant, and the figures should match your books before the deck goes out.
