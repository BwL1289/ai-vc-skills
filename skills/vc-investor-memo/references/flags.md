# Flag meanings

The vc-investor-memo skill reads this file when a tool returns a flag; its own "Flags" section links here. A tool's
`flags` holds codes only; over MCP no sentence comes with them. This is what each means for the founder: a question a
partner is likely to ask, never an error, and never a change to a verdict. The skill's test checks that every code
the deal check and the runway plan return has a row here.

## Flags

| Flag                                  | Tool                    | What it means for the founder                                                                 |
| ------------------------------------- | ----------------------- | --------------------------------------------------------------------------------------------- |
| `valuation_back_solved`               | deal check              | No valuation was given, so the post-money was worked from the raise and the percent           |
| `pool_in_pre_money_lowers_price`      | deal check              | The new pool is paid for out of the pre-money, so the effective pre-money and price are lower |
| `pool_in_post_money_dilutes_investor` | deal check              | The pool is counted after the money, so the investor gets less than raise / post-money        |
| `pool_already_large_enough`           | deal check              | The unissued pool already meets the target, so no new pool shares are needed                  |
| `conversions_bought_by_pre_money`     | deal check              | SAFE and note shares come out of the pre-round holders, so their stake falls by more          |
| `discount_beat_cap`                   | deal check              | A discount gave a lower price than the cap                                                    |
| `note_interest_converts`              | deal check              | Note interest converts too, so a note gets more than its principal's worth of shares          |
| `consistent_beyond_rounding`          | deal check, runway plan | A stated percent or runway holds by the tolerance alone, not as the tool's figure rounded     |
| `net_burn_not_positive`               | deal check              | Revenue covers the burn on those figures, so there is no net runway on them                   |
| `current_burn_runway_longer`          | deal check              | Runway on today's burn is longer than on the planned burn                                     |
| `dilution_above_band`                 | deal check              | The investors get more than the tool's dilution benchmark in one round (not a rule)           |
| `runway_below_band`                   | deal check, runway plan | Planned runway is under the tool's runway benchmark (not a rule)                              |
| `cash_never_runs_out`                 | runway plan             | Revenue covers the spend before the cash runs out, so that runway has no end                  |
| `cash_out_before_raise_lands`         | runway plan             | The cash goes below the floor before a later raise lands                                      |
| `milestone_short_on_plan`             | runway plan             | A raise does not reach a milestone, even on the plan                                          |
| `downside_short_where_plan_covers`    | runway plan             | A raise reaches a milestone on the plan but not on the downside                               |
| `covered_without_raise`               | runway plan             | The cash already reaches a milestone with no raise                                            |
| `start_raising_date_passed`           | runway plan             | With the months to raise given, the date to start raising is already at or past today         |
| `no_time_to_raise_given`              | runway plan             | Milestones were checked at their own month, with no time left to raise the next round         |
