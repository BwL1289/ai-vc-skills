# Eval 4: Company P, figures that disagree, a valuation with no label and a stage label the deck does not show

A test prompt for the `vc-deck-review` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator deal_check` runs with these inputs. The answer states the expected behaviour; it is not a recorded
run, and this eval has not been run in a live session. A run passes when it marks Traction Contradicted for two lines
that state the same metric for the same period differently, calls the calculator twice for the valuation with no label
and turns the reading that disagrees into one fix to label the valuation, and raises the stage mismatch as a question
with no threshold.

## Prompt

> Is my deck ready to send? Slide 1: "Company P: a returns desk for online furniture stores." Slide 4, Traction: "120
> stores on our free plan as of October." Slide 5: "Paid pilots with 3 national furniture chains since August." Slide
> 9, Summary: "Over 150 stores on our free plan as of October." Slide 10, Ask: "We're raising a $6M Series A on a
> priced round at a $24M valuation to reach 400 paying stores; investors get 25%." We're pitching Series A funds.

## Expected tool call

`equity_deal_check`, twice, because the valuation has no label: once read as pre-money, once as post-money.

```json
{
  "inputs": {
    "investment": "6000000",
    "pre_money": "24000000",
    "stated_investor_percent": "25"
  }
}
```

```json
{
  "inputs": {
    "investment": "6000000",
    "post_money": "24000000",
    "stated_investor_percent": "25"
  }
}
```

## What the calculator prints (excerpt)

Read as pre-money:

```text
  Raise (I)                                          $6,000,000.00  given
  Pre-money as stated                               $24,000,000.00  given
  Investors' percent as stated                            25.0000%  given
  Investors' percent: the calculator gives                20.0000%  the investor's cap-table share
  Investors' percent: verdict                             mismatch  within the tolerance is consistent
  Overall verdict                                         mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

Read as post-money:

```text
  Raise (I)                                          $6,000,000.00  given
  Post-money as stated                              $24,000,000.00  given
  Investors' percent as stated                            25.0000%  given
  Investors' percent: the calculator gives                25.0000%  the investor's cap-table share
  Investors' percent: verdict                           consistent  within the tolerance is consistent
  Overall verdict                                       consistent  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- Traction is Contradicted: "120 stores on our free plan as of October." against "Over 150 stores on our free plan as
  of October." (the same metric for the same period), both quoted with their slides; the fix is to confirm one figure
  and use it in both places. The answer computes no difference.
- The $24M valuation has no label, so both readings are shown side by side: read as pre-money, the calculator gives the
  investors 20.0000% (a mismatch with the stated 25.0000%); read as post-money, it gives 25.0000% (consistent). A
  mismatch under one reading only is not a calculator mismatch: it becomes one fix, to label the valuation pre- or
  post-money, with a partner likely to ask which one is meant. It does not head the ranked fix list as a figure that
  does not match, and it does not mark Ask and use of funds Contradicted.
- Which investors: the stated stage (Series A) and what the deck shows (stores on a free plan and three paid pilots)
  disagree; this is raised as a question a partner at a Series A fund is likely to ask, with no revenue threshold and
  no named firm, marked as the skill's own judgment, unverified. The answer notes that its investor-fit table covers
  early investors only.
- Market, Why now and Competition have no slide: each enters the ranked fix list as "no slide covers" that dimension,
  with a bracketed ask, and goes to the open asks; no score is given.
