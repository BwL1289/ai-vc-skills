# Eval 3: Company AO, a marketplace with an "ARR" figure it does not explain

A test prompt for the `vc-metrics-readiness` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it makes no calculator
call, asks what the $3M is, says ARR does not apply to a marketplace without recurring revenue, and computes no take
and no annual figure.

## Prompt

> Check my ARR before our seed meetings. Our deck says "$3M ARR". We're a marketplace for used lab equipment: buyers
> spent $250,000 through us last month and we take 12%.

## Expected tool call

None: no `equity_metrics_check` call. The founder gives no recurring revenue and no month's revenue as booked; what
buyers spent is GMV, not revenue, and working the take from the 12% would be the model's own arithmetic.

## Expected answer

- "$3M ARR" is Needs a source: `[what the $3M is (GMV, revenue as booked, or another figure) and over which period]`.
  The answer says ARR is a recurring-revenue measure and that marketplaces state size as a run-rate (a16z "16 More"
  (2)), and that if the $3M comes from GMV, the GMV-called-revenue pattern applies (a16z "16 Startup Metrics" (6)).
  The fix: GMV and revenue on separate lines, each with its period.
- The answer computes nothing: not $250,000 times 12, not the 12% take, no annual figure. It offers to run
  `equity_metrics_check` for a run-rate once `[last month's revenue as booked]` is given.
- Stage expectations use the seed row and the marketplace row: GMV and revenue on separate lines, a run-rate on the
  latest month or quarter, the take as the founder states it, revenue month by month, its growth and net burn, each
  Present (quoted) or Missing (a bracketed ask); no thresholds.
- No score; no firm named as a fit or a voice.
