# Eval 8: Company DX, "we hope this is our only round, and we'd rather not offer a cap"

A test prompt for the `vc-deal-math` skill. The company is made up. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24): the fourth run of this eval, and
the first after plugin 0.3.9 changed both skills for the hand-off to this one that the second and third runs missed.
Every figure under "Expected answer" is pasted from what `equity_calculator instrument_compare` printed for these
inputs; none is typed by hand. A run passes when it makes the one tool call below with no next round (field order free,
money and percents as strings), says in words that the comparison runs with no next round, shows these figures side by
side as option A, option B and B - A, never says which option to take, and computes nothing in its own text. The verdict
is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or met only in part, and
Fail when two or more are missed; a shortfall against the other points of the expected answer is noted but does not
change the verdict. The recorded run is a Pass with shortfalls, and its session loaded this skill, the first of the four
runs to do so; the third run, also a Pass, and the second, a Fail, are described under "Recorded answer".

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

Recorded with Claude Code 2.1.331 on 2026-11-24, with plugin 0.3.9 loaded from this repository and no user settings.
This is the fourth run of this eval, made after the hand-off fix the second and third runs led to (below); the first, on
plugin 0.3.2, is not recorded. The answer is shown whole.

**Pass, with shortfalls against the expected answer.** It met every clause of the pass sentence above. The session
loaded this skill: its first tool call loaded vc-deal-math, before it searched for the calculator's tool, and it never
loaded the equity-calculator skill, so this skill's step 7 reached the run, the first of the four runs where it did. It
made the one `equity_instrument_compare` call, its input the same as the expected call, with no `next_rounds` and no
`note_months_to_conversion`, and the tool ran its no-next-round mode. Its first paragraph says in words that the
comparison runs with no next round: "you said this is the only round, so nothing here assumes a later priced round", a
line about the whole comparison; its discount line adds that "with no next round it changes none of these figures". Its
ownership table sets the priced seed, the note and the note minus the priced seed side by side for every group, the
founders, the team, the unissued pool and the new money, right after closing and if the note converts at month 24 (the
founders' 18.0000 and -4.6347 points, the new money's -20.0000 and 5.1497, the team's and the pool's 1.0000 and
-0.2575), where the third run gave the team's and the pool's percents in a sentence with no B - A, and its sale table
does the same for every group at each sale; the note owed at months 12 and 24 is option B's alone, as the tool gives it.
It never says which option to take: its first sentence opens "Neither option is better at every sale price" and goes on
to what the note leaves the founders at each sale, comparing the options without choosing one. Every figure in its text
is one the tool returned or the founder gave: each number in the answer was checked against the tool's result and the
prompt, and none is missing from both. Short of the expected answer: it does not lead with the result's summary but with
a line of its own, then the note owed and the ownership table. It names no flag by its code (`no_next_round_given`,
`note_interest_converts`, `discount_unused_without_round`) and relays none in step 7's words, though it gives each one's
meaning in its own: "nothing here assumes a later priced round", "the conversion includes the $180,000 of interest" and
the discount "only applies at a priced round". It names none of the assumptions `maturity_rule`, `exit_before_any_round`
and `note_discount_rule` and marks none `unverified`, listing its own instead, which match the tool's rules (the 2x on
the principal alone with no interest added, paid before any shareholder; the discount only at a priced round; the
interest converting; the $5M over today's fully diluted shares; the pool paid as if granted). It does not say in one
line what the mode shows: that the note never converts at a priced round here, so the table gives ownership right after
today, the note at its maturity and each sale before any priced round. Its tables drop the cents, and they give the new
money's stake under the note today as "0% (note outstanding, no shares)" rather than to four places. Its lawyer section
hands over who chooses at maturity, the 2x change-of-control wording (interest added to the multiple, or the greater of
2x and converting) and what the maturity shares carry, while whether the interest converts sits under its assumptions;
it asks the lawyer who chooses at maturity but does not say that the note's own terms decide whether it is repaid or
converted. Two lines there make claims the tool did not work, with no figure: the greater of 2x and converting "would
change the $40M row a lot", and if the choice at maturity is the company's "the note behaves very differently". It asks
the founder for nothing more, does not call `equity_deal_check`, says the $5M is measured over today's 10,000,000 fully
diluted shares, pool included, and says the 2x is on the principal only. The session's first line listed the
calculator's server as still starting, with none of its tools; the run found the tool by searching for it by name, a
first search under a shorter name finding nothing, and called it once. Since this run neither skill's text has changed:
the hand-off to this skill fired, and this skill's step 7, which asks to lead with the summary, to say what the mode
shows in one line, to relay each flag in its words and to give the assumptions the answer leans on, and its "Answering"
section, which asks to say plainly which are `unverified`, reached the run and were not followed on those points; how to
make them land is open. The eval has not been run again.

The third run, on plugin 0.3.7 the same day, passed with shortfalls against the expected answer; its session loaded the
equity-calculator skill, never this one, as the first two runs' had, and answered from that skill's own copy of step 7's
rules. It made the same one call, said in its first line that it ran both options "with no next round, so the note never
converts at a priced round here", set the priced seed, the note and the note minus the seed side by side for the
founders' and the investors' ownership and every sale row, never said which option to take and gave no figure of its
own. Short of the expected answer, it too did not lead with the summary, named no flag by its code, named none of the
tool's assumptions and marked none `unverified`, gave the team's and the pool's percents in a sentence with no B - A,
and handed the 2x change-of-control wording and the conversion mechanics to no lawyer by name. After it plugin 0.3.9
changed both skills for the hand-off: this skill's description names weighing a priced round against a note or a SAFE in
its first sentence, the equity-calculator skill's description sends a priced round weighed against a note here, that
skill opens with a line to load this one and answer from step 7, and its own copy of step 7's rules asks for each flag
by its code and each assumption marked `unverified` where the result says so.

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

> Neither option is better at every sale price: on your figures the note leaves the founders with less at a $3M or $10M sale and more at a $40M sale. All figures are from the equity calculator, and you said this is the only round, so nothing here assumes a later priced round.
>
> ## What the note owes
>
> | Month         | Interest | Owed       |
> | ------------- | -------- | ---------- |
> | 12            | $90,000  | $1,590,000 |
> | 24 (maturity) | $180,000 | $1,680,000 |
>
> At month 24 the note is either repaid $1,680,000 in cash or converts. Converting at the $5M valuation means $0.50 a share, against $0.60 in the priced seed, so the $1,680,000 becomes 3,360,000 shares.
>
> ## Ownership
>
> |                                                | Priced seed | Note                             | Note minus priced |
> | ---------------------------------------------- | ----------- | -------------------------------- | ----------------- |
> | **Founders, right after closing**              | 72.0000%    | 90.0000%                         | +18.0000 pts      |
> | Team (granted options)                         | 4.0000%     | 5.0000%                          | +1.0000 pts       |
> | Unissued pool                                  | 4.0000%     | 5.0000%                          | +1.0000 pts       |
> | New money                                      | 20.0000%    | 0% (note outstanding, no shares) | −20.0000 pts      |
> | **Founders, if the note converts at month 24** | 72.0000%    | 67.3653%                         | −4.6347 pts       |
> | Team                                           | 4.0000%     | 3.7425%                          | −0.2575 pts       |
> | Unissued pool                                  | 4.0000%     | 3.7425%                          | −0.2575 pts       |
> | New money                                      | 20.0000%    | 25.1497%                         | +5.1497 pts       |
>
> The 90% under the note lasts only while the note is outstanding. If it converts at maturity, the investor ends up with 25.1497% instead of the seed's 20%.
>
> ## A sale before maturity
>
> | Sale price | Who           | Priced seed | Note        | Note minus priced |
> | ---------- | ------------- | ----------- | ----------- | ----------------- |
> | **$3M**    | **Founders**  | $1,350,000  | $0          | −$1,350,000       |
> |            | Team          | $75,000     | $0          | −$75,000          |
> |            | Unissued pool | $75,000     | $0          | −$75,000          |
> |            | Investor      | $1,500,000  | $3,000,000  | +$1,500,000       |
> | **$10M**   | **Founders**  | $7,200,000  | $6,300,000  | −$900,000         |
> |            | Team          | $400,000    | $350,000    | −$50,000          |
> |            | Unissued pool | $400,000    | $350,000    | −$50,000          |
> |            | Investor      | $2,000,000  | $3,000,000  | +$1,000,000       |
> | **$40M**   | **Founders**  | $28,800,000 | $33,300,000 | +$4,500,000       |
> |            | Team          | $1,600,000  | $1,850,000  | +$250,000         |
> |            | Unissued pool | $1,600,000  | $1,850,000  | +$250,000         |
> |            | Investor      | $8,000,000  | $3,000,000  | −$5,000,000       |
>
> - **$3M sale:** the note's 2x claim is $3,000,000, which is the whole sale price, so founders and team get nothing. Under the seed, the investor takes the 1x preference of $1,500,000 and the rest goes to common.
> - **$10M sale:** the seed investor converts and takes 20%, which is $2,000,000. The note holder takes a flat $3,000,000 off the top.
> - **$40M sale:** the note holder's payout stays at $3,000,000, while the seed investor's 20% is worth $8,000,000.
>
> ## What the figures assume
>
> - **Seed terms:** I read "standard terms" as a 1x non-participating preference with no pool top-up. A top-up inside the $6M pre-money would lower the founders' seed figures.
> - **Interest at maturity:** the conversion includes the $180,000 of interest. If your note converts principal only, the investor's share is smaller.
> - **$5M valuation:** it is measured over today's 10,000,000 fully diluted shares, pool included.
> - **2x on a sale:** it is 2x principal only, with no interest added, and paid before any shareholder.
> - **Discount:** the 20% discount only applies at a priced round, so with no next round it changes none of these figures.
> - **Unissued pool:** it is paid as if fully granted and exercised. If those 500,000 shares are still ungranted at a sale, their line goes to the other holders instead.
> - **Sale timing:** the sale rows assume the sale happens before month 24. Nothing else comes off the price first (fees, escrow, other debt).
>
> ## Questions for your lawyer
>
> - **Who chooses at maturity?** If the holder can demand the $1,680,000 in cash, a company that hopes never to raise again has to have it on hand. If the choice is yours, the note behaves very differently.
> - **Is the sale payout exactly 2x principal?** Some notes add interest to the multiple, or give the holder the greater of 2x and converting. The second version would change the $40M row a lot.
> - **What do the maturity shares carry?** I counted only the shares. If they come with a liquidation preference, a sale after month 24 looks different from the table.
>
> This is arithmetic on your stated terms, not investment, legal or tax advice.
