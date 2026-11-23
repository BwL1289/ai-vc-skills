# Calculator flags

The vc-partner-meeting skill reads this file when a tool returns a flag; its own "Calculator flags" section links here.
A tool call returns each flag as a bare code; this is what each code means, as a question a partner is likely to ask.

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

From `equity_runway_plan` (no milestone, months to raise or landing month here), three codes can come back:
`cash_never_runs_out` (revenue covers spend first: what revenue makes that true?), `runway_below_band` (a raise's plan
runway is under the tool's runway band: which milestone?) and `consistent_beyond_rounding` (its row above).
