# Calculator flags

The vc-partner-meeting skill reads this file when a tool returns a mismatch or a flag; its own "Calculator flags"
section links here. Where each mismatch and flag goes in the drill comes first; then, since a tool call returns each
flag as a bare code, what each code means, as a question a partner is likely to ask.

## Where the calculator's mismatches and flags go

The calculator's mismatches and flags from step 3 do not go through the lenses. Each mismatch row heads the kept
questions, ahead of the tiers, quoting the figure as the founder states it with the tool's value as the reason. It
carries no tier: how much a gap hurts depends on its size, which the founder weighs. One exception: a runway claim below
the computed runway understates it, so it does not head the drill; the founder may keep it or state the printed runway,
and it goes in the minor tier at most. A percent sold or use-of-funds total below the tool's figure is still a mismatch.
Each flag is added as weakens it, with its meaning from the tables below. Neither goes through the quote check or the
refute pass: the calculator computed it, and its quote is the tool's row.

## What each flag code means

| Flag (`equity_deal_check`)            | What a partner is likely to ask                                                                                  |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `valuation_back_solved`               | No valuation was given, so the post-money was worked from the raise: pre- or post-money?                         |
| `pool_in_pre_money_lowers_price`      | The new pool is paid for out of the pre-money, as a VC prices it: does the deck show the effective pre-money?    |
| `pool_in_post_money_dilutes_investor` | The pool is counted after the money, so the investor gets less: will you move it into the pre?                   |
| `pool_already_large_enough`           | The unissued pool already meets the target: is the target big enough for the hiring plan?                        |
| `conversions_bought_by_pre_money`     | SAFE and note shares come out of the existing holders: what do you own once they convert?                        |
| `discount_beat_cap`                   | A discount gave a lower price than the cap: is the cap table modelled at that price?                             |
| `note_interest_converts`              | Note interest converts too: is the interest counted in the cap table?                                            |
| `consistent_beyond_rounding`          | A stated percent or runway holds only by the tolerance: will the deck quote the figure a partner recomputes?     |
| `net_burn_not_positive`               | Revenue covers the burn on those figures, so there is no net runway on it: which burn does the runway claim use? |
| `current_burn_runway_longer`          | Runway on today's burn is longer than on the planned burn: which burn does the runway claim use?                 |
| `runway_below_band`                   | Planned net runway is under the tool's runway band: which milestone does the raise reach?                        |
| `dilution_above_band`                 | The investors get more than the tool's dilution band in one round: why sell that much?                           |

From `equity_runway_plan`, with no milestone, months to raise or landing month here, only `cash_never_runs_out`,
`runway_below_band` and `consistent_beyond_rounding` come back; a milestone the founder names brings the rest.

| Flag (`equity_runway_plan`)        | What a partner is likely to ask                                                                               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `cash_never_runs_out`              | Revenue covers spend before the cash runs out, so the runway has no end: what revenue makes that true?        |
| `cash_out_before_raise_lands`      | The cash goes below the floor before a later raise lands: what carries the company to the close?              |
| `milestone_short_on_plan`          | A raise does not reach a milestone, with time to raise after it, even on plan: which milestone does it reach? |
| `downside_short_where_plan_covers` | The plan reaches a milestone and the downside does not: what would you cut, and when would you know?          |
| `covered_without_raise`            | The cash already reaches a milestone with no raise: what does the raise buy beyond it?                        |
| `start_raising_date_passed`        | On the cash alone, with the months to raise given, raising should already have started: when will it close?   |
| `no_time_to_raise_given`           | Milestones were checked at their own month, with no time left to raise: how long will the next raise take?    |
| `runway_below_band`                | A raise's plan runway is under the tool's runway band: which milestone does it reach?                         |
| `consistent_beyond_rounding`       | A stated runway holds only by the tolerance: will the deck quote the runway a partner recomputes?             |
