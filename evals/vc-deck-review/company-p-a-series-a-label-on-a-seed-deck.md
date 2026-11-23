# Eval 4: Company P, figures that disagree and a stage label the deck does not show

A test prompt for the `vc-deck-review` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it marks Traction Contradicted
for two lines that state the same metric for the same period differently, asks for a valuation before any calculator
call, and raises the stage mismatch as a question with no threshold.

## Prompt

> Is my deck ready to send? Slide 1: "Company P: a returns desk for online furniture stores." Slide 4, Traction: "120
> stores on our free plan as of October." Slide 5: "Paid pilots with 3 national furniture chains since August." Slide
> 9, Summary: "Over 150 stores on our free plan as of October." Slide 10, Ask: "We're raising a $6M Series A on a
> priced round to reach 400 paying stores." We're pitching Series A funds.

## Expected tool call

None: no `equity_deal_check` call. The tool needs a valuation (a pre- or post-money with its label, or the percent
sold); the answer asks for it first.

## Expected answer

- Traction is Contradicted: "120 stores on our free plan as of October." against "Over 150 stores on our free plan as
  of October." (the same metric for the same period), both quoted with their slides; the fix is to confirm one figure
  and use it in both places. The answer computes no difference.
- The ask names a milestone ("to reach 400 paying stores") but no valuation; the open asks include the valuation with
  its label and the percent sold.
- Which investors: the stated stage (Series A) and what the deck shows (stores on a free plan and three paid pilots)
  disagree; this is raised as a question a partner at a Series A fund is likely to ask, with no revenue threshold and
  no named firm, marked as the skill's own judgment, unverified.
- Market, Why now and Competition have no line to quote and go to the open asks; no score is given.
