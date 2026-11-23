# Eval 3: Company C, "is our raise reasonable"

A test prompt for the `vc-deal-math` skill. The company is made up. The answer states the expected behaviour; it is not
a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted from
what `equity_calculator deal_check` printed for these inputs; none is typed by hand. A run passes when it makes the one
tool call below (field order free, money and percents as strings), gives these figures, and computes nothing in its own
text.

## Prompt

> Is our raise reasonable, or will a VC pick holes in it? $2.5M seed at a $10M pre-money. The deck says we founders keep
> 80% and the raise gives us about 24 months of runway. Use of funds: 50% engineering, 30% go-to-market, 20% G&A. We
> have 8,000,000 shares, all ours. One convertible note: $500k, 6% simple interest, 18 months outstanding, an $8M cap,
> 20% discount. $300k in the bank. Today we spend $120k a month with $20k of
> revenue; after the raise we plan $210k a month with $35k of revenue.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "2500000",
    "pre_money": "10000000",
    "fully_diluted_shares": 8000000,
    "instruments": [
      {
        "kind": "note",
        "principal": "500000",
        "interest_rate_percent": "6",
        "months_outstanding": 18,
        "compounding": "simple",
        "valuation_cap": "8000000",
        "discount_percent": "20"
      }
    ],
    "holder_percent": "100",
    "stated_holder_percent": "80",
    "cash_on_hand": "300000",
    "planned_monthly_gross_burn": "210000",
    "planned_monthly_revenue": "35000",
    "current_monthly_gross_burn": "120000",
    "current_monthly_revenue": "20000",
    "stated_runway_months": "24",
    "use_of_funds": [
      {
        "percent": "50"
      },
      {
        "percent": "30"
      },
      {
        "percent": "20"
      }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Price per share (p)                                                            $1.164844  the round's price
  After: holder group                                                             74.5500%  h·kept
  After: Note 1                                                                    5.4500%  shares/T
  After: investors                                                                20.0000%  N/T
  Net burn, planned burn                                                       $175,000.00  gross burn - revenue
  Gross runway, planned burn                                                  13.33 months  (cash + I)/gross burn
  Net runway, planned burn                                                    16.00 months  (cash + I)/net burn
  Gross runway, today's burn                                                  23.33 months  (cash + I)/gross burn
  Net runway, today's burn                                                    28.00 months  (cash + I)/net burn
  Use of funds: line 1                                                       $1,250,000.00  as given, or percent·I
  Use of funds: line 2                                                         $750,000.00  as given, or percent·I
  Use of funds: line 3                                                         $500,000.00  as given, or percent·I
  Use of funds: total                                                        $2,500,000.00  every line
  Holder group's percent after: the deck says                                     80.0000%  given
  Holder group's percent after: the calculator gives                              74.5500%  h·(share every pre-round share keeps)
  Holder group's percent after: difference                                        -5.4500%  computed - stated
  Holder group's percent after: verdict                                           mismatch  within the tolerance, or rounding to the deck's, is consistent
  Runway: the deck says                                                       24.00 months  given
  Runway: the calculator gives                                                16.00 months  (cash + I)/net burn, planned (else current)
  Runway: difference                                                          -8.00 months  computed - stated
  Runway: verdict                                                                 mismatch  within the tolerance, or rounding to the deck's, is consistent
  Use of funds total: verdict                                                   consistent  within the tolerance is consistent
  A VC is likely to ask                                    conversions_bought_by_pre_money  SAFE and note shares come out of the pre-round holders, not the new investor, so their stake falls by more than the percent sold; a VC reads the cap table this way
  A VC is likely to ask                                                  discount_beat_cap  A discount gave a lower price than the cap, so a cap-only conversion in the deck would be wrong
  A VC is likely to ask                                             note_interest_converts  Note interest converts too, so a note gets more than its principal's worth of shares; count it in the cap table
  A VC is likely to ask                                         current_burn_runway_longer  Runway on today's burn is longer than on the planned burn; say which one the deck uses, as a VC will check it against the planned spend
  A VC is likely to ask                                                  runway_below_band  Planned runway is under 18 months; a VC is likely to ask whether the raise reaches the next milestone (a common benchmark, not a rule)
  Overall verdict                                                                 mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- Verdict `mismatch`: the use of funds adds up to 100% of the raise; the founders' 80% and the 24-month runway do
  not hold.
- Founders: the deck says 80.0000%, the calculator gives 74.5500%, a difference of -5.4500%. The note holds 5.4500%
  and the seed investors 20.0000%.
- The note converts $545,000.00 ($45,000.00 of it interest) at its discount price, $0.931875, not its cap price,
  $1.000000 (from the result's `round`); the round price is $1.164844.
- Runway: the deck says 24.00 months, the calculator gives 16.00 months on the planned net burn of $175,000.00, a
  difference of -8.00 months. Planned gross is 13.33 months; on today's burn, net is 28.00 and gross 23.33 months. The
  answer points out that the deck's figure sits near today's gross-burn line, without computing anything itself.
- Use of funds: $1,250,000.00, $750,000.00 and $500,000.00, 100% of the raise.
- Questions a VC is likely to ask, one per flag: `conversions_bought_by_pre_money`, `discount_beat_cap`,
  `note_interest_converts`, `current_burn_runway_longer` and `runway_below_band`. The last is a common benchmark, not a
  rule (18 months, source `unverified`), and the answer says benchmarks vary by sector, stage and year.
- "Reasonable" is answered as whether the numbers hold up and which questions to prepare for, never as advice to raise
  or not. The answer notes the note's interest was taken as simple because the founder said so (the calculator's
  default is yearly compounding), and that the $8M cap was read as a pre-money cap over today's 8,000,000 fully
  diluted shares (the `note_cap_basis` assumption), which the founder should confirm against the note.
