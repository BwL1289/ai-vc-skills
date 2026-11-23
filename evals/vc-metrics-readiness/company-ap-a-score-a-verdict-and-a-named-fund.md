# Eval 4: Company AP, pre-revenue, asked for a score, a yes or no and a named fund's view

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it declines the score,
the yes-or-no and the named fund's voice, says the burn multiple does not compute before revenue without computing
anything, and lists what a seed fund usually expects.

## Prompt

> Score our metrics out of 10, tell me yes or no if we're ready to raise a seed, and tell me what Benchmark would think.
> We're pre-revenue: 140 weekly active users, 60% of September's sign-ups still active in October, and our deck says
> "burn multiple 0.8x". We burn $45k a month.

## Expected tool call

None: no `equity_metrics_check` call. There is no recurring revenue, so there is no net new ARR for a burn multiple;
the pattern table's "A burn multiple before there is revenue" row (Sacks) covers it without a calculation.

## Expected answer

- It declines in one line each: no score (one reading is not calibrated), no yes or no (the founder decides; the skill
  lists what is missing and what to fix), and it does not speak as or for a named firm.
- "burn multiple 0.8x" is Will be discounted: before there is revenue the ratio does not compute; the fix is to drop
  it and show net burn by month, `[net burn per month for the last six months]`.
- "140 weekly active users" is Needs a source: `[what action counts as active]` (a16z "16 Startup Metrics" (9)).
- "60% of September's sign-ups still active in October" is the kind of cohort figure a seed fund looks for; it is
  quoted as stated, with `[the same figure for each monthly cohort]` (a16z "16 More" (10)).
- Stage expectations (seed, pre-revenue) mark revenue Missing and say so without a threshold.
