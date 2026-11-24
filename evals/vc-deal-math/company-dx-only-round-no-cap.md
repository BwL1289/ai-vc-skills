# Eval 8: Company DX, "we hope this is our only round, and we'd rather not offer a cap"

A test prompt for the `vc-deal-math` skill. The company is made up. The answer states the expected behaviour; it is not
a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted from
what `equity_calculator instrument_compare` printed for these inputs; none is typed by hand. A run passes when it makes
the one tool call below with no next round (field order free, money and percents as strings), says in words that the
comparison runs with no next round, shows these figures side by side as option A, option B and B - A, never says which
option to take, and computes nothing in its own text.

## Prompt

> We're raising $1.5M and we hope it's the only round we ever raise. We'd rather not put a cap on a note. Option one is
> a priced seed at $6M pre on standard terms. Option two is a convertible note with no cap, a 20% discount and 6% simple
> interest, maturing in 24 months: if we haven't raised again by then it's repaid or it converts at a $5M valuation,
> and if we're bought before that the note holders get 2x their principal. Cap table today: 9,000,000 founder shares,
> 500,000 for the team (granted options) and a 500,000 unissued pool; no other investors. Show us what the note owes at
> 12 and 24 months, and what each option does if we sell for $3M, $10M or $40M before raising again.

## Expected tool call

`equity_instrument_compare`, once:

```json
{
  "inputs": {
    "founder_shares": 9000000,
    "team_shares": 500000,
    "unissued_pool_shares": 500000,
    "investment": "1500000",
    "priced_pre_money": "6000000",
    "priced_preference": { "standard": true },
    "note_discount_percent": "20",
    "note_interest_rate_percent": "6",
    "note_compounding": "simple",
    "note_owed_months": [12, 24],
    "note_maturity_months": 24,
    "note_maturity_conversion_valuation": "5000000",
    "note_change_of_control_multiple": "2",
    "exit_amounts": ["3000000", "10000000", "40000000"]
  }
}
```

## What the calculator prints (excerpt)

```text
  Summary, today: founders                                                               72.0000%          90.0000%        18.0000%  as the Today lines below
  Summary, today: new money                                                              20.0000%           0.0000%       -20.0000%  as the Today lines below; B's note holds no shares until it converts
  Summary, at B's maturity conversion: founders                                          72.0000%          67.3653%        -4.6347%  A as today; B as the maturity lines below
  Summary, at B's maturity conversion: new money                                         20.0000%          25.1497%         5.1497%  A as today; B as the maturity lines below
  Summary, sale before any round, $3,000,000.00: founders' payout                   $1,350,000.00             $0.00  $-1,350,000.00  as the sale's lines below
  Summary, sale before any round, $10,000,000.00: founders' payout                  $7,200,000.00     $6,300,000.00    $-900,000.00  as the sale's lines below
  Summary, sale before any round, $40,000,000.00: founders' payout                 $28,800,000.00    $33,300,000.00   $4,500,000.00  as the sale's lines below
  Mode                                                                              no next round     no next round                  no next round given: the note is never converted at a priced round here; ownership today, the note at its maturity on its own terms, and each exit as a sale before any priced round
  Today: price per share                                                                $0.600000                                    p = V/(FD + converted + new pool)
  Note owed at month 12                                                                               $1,590,000.00                  principal + interest, to the cent
  Note owed at month 24                                                                               $1,680,000.00                  principal + interest, to the cent
  Today: founders                                                                        72.0000%          90.0000%        18.0000%  group's shares / total shares
  At maturity (month 24): note owed                                                                   $1,680,000.00                  principal + interest, to the cent; repaid if its terms say so
  At maturity (month 24): converts at                                                                     $0.500000                  the maturity valuation / FD
  At maturity (month 24): note's shares                                                                   3,360,000                  amount converting / price
  At maturity (month 24): founders                                                       72.0000%          67.3653%        -4.6347%  group's shares / total shares (A: right after today)
  At a sale: note's claim                                                                             $3,000,000.00                  the multiple x the principal, paid before any share, up to the sale
  Sale before any round, $3,000,000.00: founders                                    $1,350,000.00             $0.00  $-1,350,000.00  the waterfall, every preference honoured; B's note on its own term
  Sale before any round, $3,000,000.00: new money                                   $1,500,000.00     $3,000,000.00   $1,500,000.00  the waterfall, every preference honoured; B's note on its own term
  Sale before any round, $10,000,000.00: founders                                   $7,200,000.00     $6,300,000.00    $-900,000.00  the waterfall, every preference honoured; B's note on its own term
  Sale before any round, $40,000,000.00: founders                                  $28,800,000.00    $33,300,000.00   $4,500,000.00  the waterfall, every preference honoured; B's note on its own term
  Flag                                                                        no_next_round_given                                    No next round was given, so the note never converts at a priced round here: the comparison shows ownership today, the note at its maturity on its own terms, and each exit as a sale before any priced round
  Flag                                                                     note_interest_converts                                    The note's interest converts too, so it gets shares for more than the raise
  Flag                                                              discount_unused_without_round                                    The note's discount comes off a priced round's price, and no next round is given: it changes no figure here
```

## Expected answer

- It asks for nothing more: the founder gave both sets of terms, the note's maturity and what happens then, its term at
  a sale, the months to show and the sale values, and said the priced terms are standard, so `{"standard": true}`
  goes in. It passes no cap and no next round, as the founder said.
- It leads with the result's summary, before the side-by-side table: the founders' and the new money's ownership
  today and at B's maturity conversion, and the founders' payout at each sale before any round, under A, B and B - A,
  each as printed.
- It passes no `next_rounds` and no `note_months_to_conversion`, and it says in words that the comparison runs with no
  next round (`no_next_round_given`): the note never converts at a priced round here, so the table shows ownership
  right after today, the note at its maturity and each sale before any priced round.
- It passes the $5M as `note_maturity_conversion_valuation`, saying the tool takes it over today's 10,000,000 fully
  diluted shares, and "2x their principal" as `note_change_of_control_multiple`, the multiple of the principal alone.
- Today: the founders own 72.0000% under the priced round and 90.0000% under the note, which has no shares while it
  is outstanding; the note owes $1,590,000.00 at month 12 and $1,680,000.00 at month 24.
- At maturity (month 24): the repayment is $1,680,000.00; converting at $0.500000 a share, the note takes 3,360,000
  shares, and the founders own 67.3653% against 72.0000% under the priced round (-4.6347%). It says the note's own
  terms decide which happens, and the tool shows both.
- At a sale before any priced round the note's claim is $3,000,000.00, paid before any share. At $3M the founders get
  $1,350,000.00 (A) and $0.00 (B), as the claim takes the whole sale; at $10M $7,200,000.00 and $6,300,000.00
  ($-900,000.00); at $40M $28,800,000.00 and $33,300,000.00 ($4,500,000.00).
- Each flag with its meaning in step 7's words: `no_next_round_given`, `note_interest_converts` and
  `discount_unused_without_round` (the note's discount comes off a priced round's price, so with no next round it
  changes no figure).
- The assumptions it leans on, each named `unverified` where the result says so: `maturity_rule`,
  `exit_before_any_round` (the multiple is of the principal alone, paid before any share and never more than the sale)
  and `note_discount_rule`.
- It never picks an option or calls one better for the founders, and it hands the note's maturity and what happens at
  it, its change-of-control wording and the conversion mechanics to their lawyer.
- It does not call `equity_deal_check`, and it adds, subtracts or divides none of the tool's figures in its own text.
