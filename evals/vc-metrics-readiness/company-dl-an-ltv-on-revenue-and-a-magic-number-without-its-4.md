# Eval 6: Company DL, an LTV on revenue alone and a magic number without its 4

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator metrics_check` run with these inputs. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24). A run passes when it makes the
one one-month call below with the founder's ARPA, contribution margin, churn basis, growth, margin and basis and the two
quarters, works none of the four figures by hand, leads with the LTV and magic number mismatches and the flag that
explains each, and sets no line against the Rule of 40, LTV/CAC or the magic number. The verdict is Pass when every
clause of that sentence is met, Partial when exactly one clause is missed or met only in part, and Fail when two or more
are missed; a shortfall against the other points of the expected answer is noted but does not change the verdict. The
recorded run is a Pass with shortfalls. The skill was changed after that run (see "Recorded answer").

## Prompt

> Is the efficiency slide in our Series A deck ready? Slide 9 says: "LTV $100k." "LTV/CAC 10x." "Rule of 40: 35%
> (70% revenue growth, -35% EBITDA margin)." "Magic number 0.2." Last month we started at $200,000 MRR; new
> customers added $20,000 MRR, upsells $2,000, downgrades $1,000 and cancellations $3,000. We won 25 customers, 10
> of them from paid ads, on $150,000 of sales and marketing spend. Gross margin is 80% and contribution margin 60%
> (after hosting, support and payment costs). The average account pays $2,000 a month, and our LTV divides by
> monthly gross revenue churn. Revenue was $510,000 in Q2 and $600,000 in Q3, with $450,000 of sales and marketing
> spend in Q2.

## Expected tool call

`equity_metrics_check`, once. The LTV divides by a monthly churn, so `period_months` is 1; the growth, the margin
and the two quarters are the founder's own figures and go in as given. Each stated multiple and percent is text with
the slide's places.

```json
{
  "inputs": {
    "period_months": 1,
    "recurring_unit": "monthly",
    "starting_recurring": "200000",
    "new_recurring": "20000",
    "expansion_recurring": "2000",
    "contraction_recurring": "1000",
    "churned_recurring": "3000",
    "customers_new": 25,
    "customers_new_paid": 10,
    "sales_marketing_spend": "150000",
    "gross_margin_percent": "80",
    "arpa": "2000",
    "contribution_margin_percent": "60",
    "ltv_churn_basis": "gross_revenue",
    "revenue_growth_percent": "70",
    "profit_margin_percent": "-35",
    "profit_margin_basis": "ebitda",
    "quarter_revenue": "600000",
    "prior_quarter_revenue": "510000",
    "prior_quarter_sales_marketing_spend": "450000",
    "stated_ltv": "100000",
    "stated_ltv_to_cac": "10",
    "stated_rule_of_40_percent": "35",
    "stated_magic_number": "0.2"
  }
}
```

## What the calculator prints (excerpt)

```text
  Gross revenue churn (1 month)                                             2.0000%  (C + X)/S
  CAC, blended                                                            $6,000.00  spend / new customers
  CAC, paid                                                              $15,000.00  spend / new customers from paid channels
  CAC payback (gross margin)                                            9.38 months  spend/(new monthly recurring·margin)
  LTV (contribution margin)                                              $60,000.00  ARPA × the period's units × margin / gross revenue churn
  LTV on revenue alone                                                  $100,000.00  ARPA × the period's units / gross revenue churn
  LTV on gross margin                                                    $80,000.00  ARPA × the period's units × gross margin / gross revenue churn
  LTV/CAC                                                                10.000000x  LTV / blended CAC
  LTV/CAC on revenue alone                                               16.666667x  LTV on revenue / CAC
  Rule of 40 (growth + EBITDA margin)                                      35.0000%  revenue growth + margin, as given
  Magic number (on revenue)                                               0.800000x  4·(quarter revenue - prior quarter's) / prior quarter's spend
  Magic number without the 4                                              0.200000x  (quarter revenue - prior quarter's) / prior quarter's spend
  LTV: the deck says                                                    $100,000.00  given
  LTV: the calculator gives                                              $60,000.00  ARPA × the period's units × margin / gross revenue churn
  LTV: difference                                                       $-40,000.00  computed - stated
  LTV: verdict                                                             mismatch  within the tolerance is consistent
  LTV/CAC: the deck says                                                 10.000000x  given
  LTV/CAC: the calculator gives                                          10.000000x  LTV / blended CAC
  LTV/CAC: rounds to the deck's "10"                                            yes  the computed figure, rounded half away from zero to the places the deck writes, is the deck's
  LTV/CAC: verdict                                                       consistent  within the tolerance, or rounding to the deck's, is consistent
  Rule of 40: the deck says                                                35.0000%  given
  Rule of 40: the calculator gives                                         35.0000%  revenue growth + margin, as given
  Rule of 40: rounds to the deck's "35"                                         yes  the computed figure, rounded half away from zero to the places the deck writes, is the deck's
  Rule of 40: verdict                                                    consistent  within the tolerance, or rounding to the deck's, is consistent
  Magic number: the deck says                                             0.200000x  given
  Magic number: the calculator gives                                      0.800000x  4·(quarter revenue - prior quarter's) / prior quarter's spend
  Magic number: difference                                                0.600000x  computed - stated
  Magic number: rounds to the deck's "0.2"                                       no  the computed figure, rounded half away from zero to the places the deck writes, is the deck's
  Magic number: verdict                                                    mismatch  within the tolerance, or rounding to the deck's, is consistent
  A VC is likely to ask                          stated_ltv_uses_revenue_not_margin  A stated LTV or LTV/CAC matches the figure on revenue alone, with no margin taken out; a VC is likely to recompute it on margin
  A VC is likely to ask                          stated_magic_number_not_annualised  The stated magic number matches the quarter's revenue change over the prior quarter's spend without the 4 that annualises it; a VC is likely to recompute it with the 4
  Overall verdict                                                          mismatch  mismatch if any figure is (an unlabelled churn holds when any basis does); else not_checked with none checked or one left unchecked; else consistent
```

## Expected answer

- The two mismatches lead the ranked fix list ahead of the tiers, with no tier, not refuted, each with the flag that
  explains it. LTV: the slide says $100,000.00, the calculator gives $60,000.00 on the 60.0000% contribution
  margin; `stated_ltv_uses_revenue_not_margin` says the slide's figure is LTV on revenue alone ($100,000.00), with
  no margin taken out. The fix restates it at the tool's $60,000.00. Magic number: the slide says 0.200000x, the
  calculator gives 0.800000x; `stated_magic_number_not_annualised` says the 0.2 is the quarter's revenue change
  over the prior quarter's spend without the 4 (0.200000x). The fix restates it at 0.800000x, or labels the slide's
  figure quarterly. Both metrics are Contradicted.
- "LTV/CAC 10x." is Supported: the calculator gives 10.000000x on blended CAC, and the row says it rounds to the
  slide's "10". The answer relays the tool's other row, LTV/CAC on revenue alone 16.666667x, to say the slide's ratio
  is on margin while its LTV is not, so the two lines agree only once the LTV is restated; it works no ratio from the
  slide's $100k by hand.
- "Rule of 40: 35% (70% revenue growth, -35% EBITDA margin)." is Supported: the calculator gives 35.0000% (growth +
  EBITDA margin), rounding to the slide's "35", the margin named, so no `rule_of_40_margin_basis_unlabelled` flag
  is raised. The answer sets no line against it, says the tool sets none, and never says whether it clears 40.
- No benchmark is set for LTV, LTV/CAC, the Rule of 40 or the magic number, and none is set against any of them by
  eye. The `ltv_rule`, `rule_of_40_rule` and `magic_number_rule` assumption rows are named with the sources the
  tool's rows give: a16z's item 5, paraphrased, for LTV on contribution margin over one month's churn, and the rest
  unverified.
- Stage expectations (Series A, recurring revenue): LTV, LTV/CAC, the Rule of 40 and the magic number are on slide 9.
  ARR and its movement, gross and net revenue retention, CAC and payback and gross margin are Missing from the slide;
  the founder gave their parts, so the fix is to show them with the tool's values (gross revenue churn 2.0000% for
  the month, blended CAC $6,000.00, paid CAC $15,000.00, payback 9.38 months on gross margin). Logo churn, the burn
  multiple and concentration are Missing, each a bracketed ask (`[customers at the start of the month and customers
lost]`, `[net burn last month]`, `[the largest customer's revenue last month]`).
- No score, no "ready" or "not ready", no firm named as a fit or a voice; nothing is computed, converted or rounded
  in the answer's own text.

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with plugin 0.3.5 loaded from this repository and no user settings. An
earlier run of this eval that day, on plugin 0.3.2, is not recorded. The answer is shown whole.

**Pass, with shortfalls against the expected answer.** It met every clause of the pass sentence above. It made the one
one-month `equity_metrics_check` call, its input the same as the expected call, and no other; every figure in the answer
is one the tool printed ($60,000.00, $100,000.00, $80,000.00, 10.000000x, 16.666667x, 35.0000%, 0.800000, 0.200000),
none worked by hand; it led with the LTV and magic number mismatches, each with the flag that explains it in plain words
(the LTV worked on revenue, not margin; the magic number missing the four that annualises it); and it set no line
against the Rule of 40, LTV/CAC or the magic number, saying the calculator sets none. Its lenses ran together in one
subagent and its refute pass in another, which the answer said is less independent. Short of the expected answer: it
gave the magic number mismatch a tier ("Minor (understates)"), where the expected answer has both mismatches with no
tier; there is no metrics table with a verdict per metric, so Contradicted and Supported never appear, and LTV/CAC and
the Rule of 40 are ranked as weakening the slide instead of Supported; neither flag code
(`stated_ltv_uses_revenue_not_margin`, `stated_magic_number_not_annualised`), none of the assumption rows (`ltv_rule`,
`rule_of_40_rule`, `magic_number_rule`) and not a16z's item 5 behind the LTV is named; and blended CAC, paid CAC and
gross margin are not listed as missing stage expectations. The skill's rule that an understated figure goes in the minor
tier at most named ARR, retention, churn, CAC, payback, burn multiple and concentration, not the magic number, and the
run read the slide's 0.2 below the tool's 0.8 as an understatement. Since this run the skill says that a mismatch a flag
explains as another definition, a magic number without its 4 among them, is no understatement, whichever way it errs,
and keeps no tier. The eval has not been run again.

> **Slide 9 has two figures that do not hold up as written: the LTV and the magic number.** The other two lines check out against your own parts. I can't give a readiness verdict, but these are the fixes, in order.
>
> ## The biggest fixes
>
> 1. **"LTV $100k." is worked on revenue, not margin.** On your 60% contribution margin and monthly gross revenue churn, the calculator gives $60,000.00, a difference of -$40,000.00. Your $100k matches its revenue-only figure, $100,000.00 (on gross margin it is $80,000.00).
> 2. **"LTV/CAC 10x." only works with the $60,000 LTV.** The calculator gives 10.000000x on the contribution-margin LTV over a blended CAC of $6,000.00. With the slide's own $100k it gives 16.666667x, so the two lines on the slide use two different LTVs.
> 3. **"Magic number 0.2." is missing the four that annualises it.** From Q2 and Q3 revenue and Q2 spend, the calculator gives 0.800000; 0.200000 is the unannualised quarterly figure. Here the slide understates you.
>
> ## Ranked fix list
>
> | #   | Tier                                          | Line                                                         | Why a partner reads it that way                                                                                         | Fix                                                                                                           |
> | --- | --------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
> | 1   | None, you weigh the gap (calculator mismatch) | "LTV $100k."                                                 | LTV on revenue sets too high a ceiling on acquisition spend, and the slide names no margin or churn basis.              | "LTV $60k (60% contribution margin, monthly gross revenue churn)".                                            |
> | 2   | Minor (understates)                           | "Magic number 0.2."                                          | A quarterly change set against a ratio usually read annualised looks low.                                               | "Magic number 0.8 (Q3 vs Q2 revenue, Q2 S&M spend)", or label 0.2 as quarterly.                               |
> | 3   | Weakens                                       | "LTV/CAC 10x."                                               | It is blended only. Paid CAC is $15,000.00 against blended $6,000.00, and a partner will ask whether paid growth works. | Show both CACs and say what the $150,000 includes. `[is $150,000 all sales and marketing cost, or ads only?]` |
> | 4   | Weakens                                       | "Rule of 40: 35% (70% revenue growth, -35% EBITDA margin)."  | The sum is right (35.0000%) and the margin is named, but neither figure has a period.                                   | Add the period. `[period for the 70% growth and the -35% EBITDA margin]`                                      |
> | 5   | Weakens                                       | Slide 9 as a whole                                           | For a Series A with recurring revenue, a fund usually expects more than these four ratios (see below).                  | Add the missing metrics from the calculator's values.                                                         |
> | 6   | Minor                                         | "Revenue was $510,000 in Q2 and $600,000 in Q3" (your notes) | The magic number rests on it, and it does not say recurring or total.                                                   | `[are the Q2 and Q3 figures recurring or total revenue?]`                                                     |
>
> One objection was dropped: that the LTV's churn has no parts. Your notes answer it ("downgrades $1,000 and cancellations $3,000"), but put the basis beside the figure on the slide.
>
> ## What the calculator gives from your parts
>
> These cover last month only and are not annualised.
>
> | Metric                      | Calculator value                   | On the slide?                                                         |
> | --------------------------- | ---------------------------------- | --------------------------------------------------------------------- |
> | Ending ARR                  | $2,616,000.00 (from $2,400,000.00) | Missing                                                               |
> | Net new ARR                 | $216,000.00 (new ARR $240,000.00)  | Missing                                                               |
> | Gross revenue retention     | 98.0000%                           | Missing                                                               |
> | Net revenue retention       | 99.0000%                           | Missing                                                               |
> | Gross revenue churn         | 2.0000%                            | Missing                                                               |
> | Net revenue churn           | 1.0000%                            | Missing                                                               |
> | CAC payback on gross margin | 9.38 months (7.50 on revenue only) | Missing                                                               |
> | Logo churn                  | Not computed                       | Missing `[customers at start of month, customers lost]`               |
> | Burn multiple               | Not computed                       | Missing `[net burn for the month]`                                    |
> | Concentration               | Not computed                       | Missing `[largest customer's revenue and total revenue, same period]` |
>
> Retention uses the month's totals, which is exact only if no customer won during the month also moved. The calculator sets no benchmark for LTV/CAC, the Rule of 40 or the magic number, so I have not rated any of them. Its Rule of 40 and magic number definitions are common ones with no source read behind them.
>
> ## Open asks
>
> - `[which month "last month" is]`
> - `[is $150,000 all sales and marketing cost, or ads only?]`
> - `[period for the 70% growth and the -35% EBITDA margin]`
> - `[are the Q2 and Q3 figures recurring or total revenue?]`
> - `[customers at start of month, customers lost]`
> - `[net burn for the month]`
> - `[largest customer's revenue and total revenue, same period]`
> - `[customer segment: small business, mid-market or enterprise]`, which sets the payback benchmark question
>
> ## How this was run
>
> The attack lenses ran in one subagent and the refute pass in another, to keep cost down. That is less independent than one subagent per lens and per objection; say so if you want the full pass. I saw no billing or ledger data, and a partner will ask for it.
>
> This is not investment, legal, tax or accounting advice. The figures should match your books before the deck goes out.
