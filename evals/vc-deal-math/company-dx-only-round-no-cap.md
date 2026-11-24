# Eval 8: Company DX, "we hope this is our only round, and we'd rather not offer a cap"

A test prompt for the `vc-deal-math` skill. The company is made up. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24): the third run of this eval, and
the first after the equity-calculator skill was changed for what the second one missed. Every figure under "Expected
answer" is pasted from what `equity_calculator instrument_compare` printed for these inputs; none is typed by hand. A
run passes when it makes the one tool call below with no next round (field order free, money and percents as strings),
says in words that the comparison runs with no next round, shows these figures side by side as option A, option B and
B - A, never says which option to take, and computes nothing in its own text. The verdict is Pass when every clause of
that sentence is met, Partial when exactly one clause is missed or met only in part, and Fail when two or more are
missed; a shortfall against the other points of the expected answer is noted but does not change the verdict. The
recorded run is a Pass with shortfalls, though its session again loaded the equity-calculator skill, never this one, and
answered from that skill's own copy of step 7's rules; the second run, a Fail, is described under "Recorded answer".

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

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with plugin 0.3.7 loaded from this repository and no user settings.
This is the third run of this eval, made after the fix the second run led to (below); the first, on plugin 0.3.2, is not
recorded. The answer is shown whole.

**Pass, with shortfalls against the expected answer.** It met every clause of the pass sentence above. It made the one
`equity_instrument_compare` call, its input the same as the expected call, with no `next_rounds` and no
`note_months_to_conversion`, and the tool ran its no-next-round mode. Its first line says in words that the comparison
runs with no next round: "I ran both options through the equity calculator with no next round, so the note never
converts at a priced round here." Its ownership table sets the priced seed, the note and the note minus the seed side by
side for the founders and the investors, today and at the maturity conversion (18.0000 and -20.0000 points today,
-4.6347 and 5.1497 at maturity), where the second run's table had no B - A column, and its sale table does the same for
every group at each sale; the note owed at months 12 and 24 is option B's alone, as the tool gives it. It never says
which option to take, and every figure in it is one the tool returned: the common "shares the other $1.5M" at the $3M
sale and the crossover "between $10M and $40M" that the second run added are gone. Short of the expected answer: the
session again loaded the equity-calculator skill, never this one, and answered from that skill's own copy of step 7's
rules, so this skill's text never reached the run. It does not lead with the result's summary but with a line of its
own, then the note owed and the ownership. It names no flag by its code (`no_next_round_given`,
`note_interest_converts`, `discount_unused_without_round`), though it gives the discount's meaning ("the 20% discount
only applies at a priced round, so it changes nothing here") and says principal plus interest would convert at a later
raise. It names none of the assumptions `maturity_rule`, `exit_before_any_round` and `note_discount_rule` and marks none
`unverified`, listing its own instead, which match the tool's rules (the 2x on the principal alone, paid before any
share; the discount only at a priced round). The team's and the pool's percents sit in a sentence with no B - A; its
tables drop the cents; and its second sentence ("it costs you more than the seed in a $3M or $10M sale and at maturity,
and less only in the $40M sale") compares the options without choosing one, close to the line. Its lawyer section hands
over who chooses at maturity and a sale after maturity, but the 2x change-of-control wording sits under its assumptions
and the conversion mechanics are not handed over by name. It asks the founder for nothing more, does not call
`equity_deal_check`, says the $5M is taken over today's 10,000,000 fully diluted shares, and says the note's own terms
decide whether it is repaid, converted or extended. The session's first line listed the calculator's server as still
starting, with none of its tools; the run found the tool by searching for it by name and called it once. Since this run
neither skill's text has changed: the hand-off to this skill did not fire in it, and the equity-calculator skill's steps
3 and 5, which ask for each assumption that is `unverified` and for each flag by its code with its meaning from this
skill's step 7, were not followed; how to make the hand-off fire is open. The eval has not been run again.

The second run, on plugin 0.3.5 the same day, failed with three of the five clauses met only in part; its session too
loaded the equity-calculator skill, never this one, as the first run's had. It made the same one call, but never said in
words that the comparison runs with no next round, the nearest being its heading "Sale before any other raise"; its
ownership table had no B - A column, so today's 18.0000% and -20.0000% were missing and the maturity's 4.6347 and 5.1497
points appeared only in a sentence; and its own text gave two figures the tool prints nowhere, the common "shares the
other $1.5M" at the $3M sale and "The crossover lies somewhere between $10M and $40M". It also asked for more, though
the founder gave every term, and handed nothing to a lawyer by name. After it the equity-calculator skill sent a priced
round weighed against a note to this skill's step 7, to be loaded and answered from, and, when it answers such a
comparison itself, says which mode ran, leads with the summary, shows B - A for every row the tool gives it, names each
flag by its code with its meaning, and adds, subtracts or divides none of the tool's figures.

> I ran both options through the equity calculator with no next round, so the note never converts at a priced round here. The priced seed gives up 20% now for certain. The note keeps you at 90% today, but it costs you more than the seed in a $3M or $10M sale and at maturity, and less only in the $40M sale.
>
> ## What the note owes
>
> | Month         | Interest | Total owed |
> | ------------- | -------- | ---------- |
> | 12            | $90,000  | $1,590,000 |
> | 24 (maturity) | $180,000 | $1,680,000 |
>
> At month 24 the note is either repaid at $1,680,000 in cash or converts that amount at $0.50 a share (the $5M valuation over today's 10,000,000 fully diluted shares) into 3,360,000 shares.
>
> ## Ownership
>
> |                                             | Priced seed | Note     | Note minus seed |
> | ------------------------------------------- | ----------- | -------- | --------------- |
> | Founders, right after today                 | 72.0000%    | 90.0000% | +18.0000 pts    |
> | Investors, right after today                | 20.0000%    | 0.0000%  | −20.0000 pts    |
> | Founders, if the note converts at maturity  | 72.0000%    | 67.3653% | −4.6347 pts     |
> | Investors, if the note converts at maturity | 20.0000%    | 25.1497% | +5.1497 pts     |
>
> The seed sells 2,500,000 shares at $0.60. Team options and the unissued pool are each 4% under the seed, and under the note each is 5% today and 3.7425% after a maturity conversion.
>
> ## A sale before any other raise
>
> | Sale price | Group         | Priced seed | Note        | Note minus seed |
> | ---------- | ------------- | ----------- | ----------- | --------------- |
> | **$3M**    | Founders      | $1,350,000  | $0          | −$1,350,000     |
> |            | Team options  | $75,000     | $0          | −$75,000        |
> |            | Unissued pool | $75,000     | $0          | −$75,000        |
> |            | Investors     | $1,500,000  | $3,000,000  | +$1,500,000     |
> | **$10M**   | Founders      | $7,200,000  | $6,300,000  | −$900,000       |
> |            | Team options  | $400,000    | $350,000    | −$50,000        |
> |            | Unissued pool | $400,000    | $350,000    | −$50,000        |
> |            | Investors     | $2,000,000  | $3,000,000  | +$1,000,000     |
> | **$40M**   | Founders      | $28,800,000 | $33,300,000 | +$4,500,000     |
> |            | Team options  | $1,600,000  | $1,850,000  | +$250,000       |
> |            | Unissued pool | $1,600,000  | $1,850,000  | +$250,000       |
> |            | Investors     | $8,000,000  | $3,000,000  | −$5,000,000     |
>
> - **$3M sale:** the note's 2x claim is $3,000,000, which is the whole sale, so founders and team get nothing. Under the seed, investors take their 1x preference of $1,500,000 and the rest goes to common.
> - **$10M and $40M sales:** seed investors convert to common and take 20%. Note holders take a flat $3,000,000 either way.
>
> ## What these figures rest on
>
> - **Seed terms:** I took "standard terms" as a 1x non-participating preference with no pool top-up. Tell me if the term sheet asks for a larger pool; that would lower your 72%.
> - **2x on a sale:** this is modelled as twice the principal with no interest added, paid before any share. If the note says 2x principal plus interest, or the greater of 2x and conversion, the figures change.
> - **Discount:** the 20% discount only applies at a priced round, so it changes nothing here. If you did raise again, the uncapped note would convert principal plus interest at 20% off that round's price.
> - **Pool at a sale:** the unissued pool is counted as if fully granted and exercised, with no strike price netted off. If ungranted options should get nothing, I can rerun it that way and the pool's line goes to the other holders.
> - **Nothing else off the top:** no fees, escrow or other debt are deducted from the sale price.
>
> ## Questions for your lawyer
>
> - **Who chooses at maturity:** the note's own terms decide whether it is repaid, converted or extended. If the holder chooses, they can demand $1,680,000 in cash at month 24.
> - **Sale after maturity:** I only modelled a sale while the note is still outstanding. If it has already converted at $5M, the holders own 25.1497% as shareholders instead of taking 2x.
>
> This is arithmetic on the terms you gave, not legal, tax or investment advice.
