# Eval 5: Company BU, "a priced round now or a note now"

A test prompt for the `vc-deal-math` skill. The company is made up. The answer states the expected behaviour; it is not
a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted from
what `equity_calculator instrument_compare` printed for these inputs; none is typed by hand. A run passes when it makes
the one tool call below (field order free, money and percents as strings), shows these figures side by side as option
A, option B and B - A, never says which option to take, and computes nothing in its own text.

## Prompt

> We need $2M and can't decide: a priced seed at $8M pre on standard terms, or a convertible note with a $6M cap, a 20%
> discount and 5% simple interest, which we'd expect to convert in about 12 months. Cap table today: 8,000,000 founder
> shares, 1,000,000 for the team (granted options) and a 1,000,000 unissued pool; no other investors. For the next
> round we're planning on $6M at a $27M pre, but it could be as little as $2M at a $9M pre; both standard terms. Show
> us what each does if we later sell for $5M, $20M or $100M.

## Expected tool call

`equity_instrument_compare`, once:

```json
{
  "inputs": {
    "founder_shares": 8000000,
    "team_shares": 1000000,
    "unissued_pool_shares": 1000000,
    "investment": "2000000",
    "priced_pre_money": "8000000",
    "priced_preference": { "standard": true },
    "note_valuation_cap": "6000000",
    "note_discount_percent": "20",
    "note_interest_rate_percent": "5",
    "note_compounding": "simple",
    "note_months_to_conversion": 12,
    "next_rounds": [
      {
        "pre_money": "27000000",
        "investment": "6000000",
        "preference": { "standard": true }
      },
      {
        "pre_money": "9000000",
        "investment": "2000000",
        "preference": { "standard": true }
      }
    ],
    "exit_amounts": ["5000000", "20000000", "100000000"]
  }
}
```

## What the calculator prints (excerpt)

```text
  Today: price per share                                                                $0.800000                                    p = V/(FD + converted + new pool)
  Note owed when it converts                                                                          $2,100,000.00                  principal + interest, to the cent
  Note's cap price                                                                                        $0.600000                  cap / FD
  Today: founders                                                                        64.0000%          80.0000%        16.0000%  group's shares / total shares
  Next round 1: price per share                                                         $2.160000         $2.000000                  p = V/(each option's shares + converted + new pool)
  Next round 1: B's note: converts at                                                                     $0.600000                  its cap price, the lower
  Next round 1: B's note: shares                                                                          3,500,000                  amount converting / price
  Next round 1: founders                                                                 52.3636%          48.4848%        -3.8788%  group's shares / total shares
  Next round 1: exit $5,000,000.00: founders                                                $0.00             $0.00           $0.00  the waterfall, every preference honoured
  Next round 1: exit $5,000,000.00: preferences paid                                $5,000,000.00     $5,000,000.00                  classes that stay
  Next round 1: exit $20,000,000.00: founders                                       $8,960,000.00     $8,296,296.29    $-663,703.70  the waterfall, every preference honoured
  Next round 1: exit $20,000,000.00: preferences paid                               $6,000,000.00     $6,000,000.00                  classes that stay
  Next round 1: exit $100,000,000.00: founders                                     $52,363,636.36    $48,484,848.49  $-3,878,787.88  the waterfall, every preference honoured
  Next round 1: exit $100,000,000.00: preferences paid                                      $0.00             $0.00                  classes that stay
  Next round 2: price per share                                                         $0.720000         $0.637500                  p = V/(each option's shares + converted + new pool)
  Next round 2: B's note: converts at                                                                     $0.510000                  its discount price, the lower
  Next round 2: B's note: shares                                                                      4,117,647.059                  amount converting / price
  Next round 2: founders                                                                 52.3636%          46.3636%        -6.0000%  group's shares / total shares
  Next round 2: exit $5,000,000.00: founders                                          $800,000.00       $720,000.00     $-80,000.00  the waterfall, every preference honoured
  Next round 2: exit $5,000,000.00: preferences paid                                $4,000,000.00     $4,100,000.00                  classes that stay
  Next round 2: exit $20,000,000.00: founders                                      $10,472,727.27     $9,272,727.27  $-1,200,000.00  the waterfall, every preference honoured
  Next round 2: exit $20,000,000.00: preferences paid                                       $0.00             $0.00                  classes that stay
  Next round 2: exit $100,000,000.00: founders                                     $52,363,636.36    $46,363,636.36  $-6,000,000.00  the waterfall, every preference honoured
  Next round 2: exit $100,000,000.00: preferences paid                                      $0.00             $0.00                  classes that stay
  Flag                                                                  cap_below_round_price_now                                    The note's cap price is below option A's price per share today: at its cap the note buys shares for less than option A's investors pay today
  Flag                                                                       note_converts_at_cap                                    In at least one next round the note converts at its cap price
  Flag                                                                  note_converts_at_discount                                    In at least one next round the note converts at its discount price, which is below its cap price there
  Flag                                                                     note_interest_converts                                    The note's interest converts too, so it gets shares for more than the raise
  Flag                                                                         maturity_not_given                                    No maturity was given for the note: what happens if the next round comes late is in the note's own terms, not modelled here
  Flag                                                        next_round_below_priced_round_price                                    A next round prices below option A's price today, a down round for option A's investors: any anti-dilution adjustment in their terms is not modelled here
```

## Expected answer

- It asks for nothing more: the founder gave both sets of terms, the next rounds and the exits, and said the terms are
  standard, so `{"standard": true}` goes in for each series. It assumes no maturity and says none was given.
- Today: the founders own 64.0000% under the priced round and 80.0000% under the note, which has no shares until the
  next round (it will owe $2,100,000.00 then; its cap price is $0.600000 against the priced round's $0.800000).
- Next round 1 ($6M at $27M pre): the note converts at its cap price, $0.600000, into 3,500,000 shares; the founders
  end at 52.3636% (A) and 48.4848% (B), -3.8788% for B. At the exits the founders get $0.00 and $0.00 at $5M (the
  preferences take all $5,000,000.00), $8,960,000.00 and $8,296,296.29 at $20M ($-663,703.70), and $52,363,636.36 and
  $48,484,848.49 at $100M ($-3,878,787.88).
- Next round 2 ($2M at $9M pre): the note converts at its discount price, $0.510000, into 4,117,647.059 shares; the
  founders end at 52.3636% (A) and 46.3636% (B), -6.0000% for B. At the exits the founders get $800,000.00 and
  $720,000.00 at $5M, $10,472,727.27 and $9,272,727.27 at $20M, and $52,363,636.36 and $46,363,636.36 at $100M. The
  round prices at $0.720000 for A, below A's $0.800000 today.
- Each flag with the meaning the report prints: `cap_below_round_price_now`, `note_converts_at_cap`,
  `note_converts_at_discount`, `note_interest_converts`, `maturity_not_given` and
  `next_round_below_priced_round_price` (a down round for A's investors; any anti-dilution in their terms is not
  modelled).
- The assumptions it leans on, each named `unverified` where the result says so: `note_price_rule`, `series_terms`
  (the note's shares carry the next round's terms with a preference on the $2.1M converted), `maturity_rule` and
  `exit_after_next_round`.
- It never picks an option or calls one better for the founders, and it hands the note's maturity and what happens at
  it, the preference and anti-dilution wording and the conversion mechanics to their lawyer.
- It does not call `equity_deal_check`, and it adds, subtracts or divides none of the tool's figures in its own text.
