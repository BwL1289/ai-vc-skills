---
name: vc-term-sheet-review
description: Helps a founder understand a VC term sheet before the lawyer call. It explains each term in plain words, sets it beside a published standard-and-clean Series A term sheet, and marks it as matching that baseline, differing from it, or not covered by it, with the source. The economics run on the equity calculator, never by hand - the valuation and the option-pool shuffle with deal_check and pool, the founders' ownership after the round, and an exit waterfall at several exits, low ones included, beside a 1x non-participating baseline when the preference differs. An adversarial review reads the terms the way the next round's lead, an acquirer, the team and the board will, and a refute pass drops every objection the sheet itself answers. It ends with questions for the lawyer. Use when a founder says review my term sheet, what does this term mean, is this term sheet standard, what do I get at a low exit, or what is the liquidation preference doing. Never says whether to sign. Not legal, tax or investment advice.
---

# VC term sheet review

Helps a founder read a term sheet they have been offered before they sit down with their lawyer. Each term is
explained in plain words and set beside a public baseline, Y Combinator's standard and clean Series A term sheet,
marked as matching it, differing from it, or not covered by it. The money is worked by the equity calculator: what
the valuation really pays for once the option pool is counted, what the founders own after the round, and who gets
what at several exit values, low ones included, under the sheet's terms and, when the sheet's preference differs, under
a 1x non-participating baseline.
Independent lenses then read the sheet the way the next round's lead, an acquirer, the team and the board will, a
refute pass drops what the sheet itself answers, and the survivors become questions for the founder's lawyer.

The founder is always the user. The skill never says whether to sign, never plays an investor, never speaks as a
named investor, firm or law firm, never calls a term "market" on its own say, and never adds a term, figure or fact
the founder did not give. It always tells the founder to have a lawyer review the sheet.

## When to use it

- "Review my term sheet." "What does this term mean?" "Is this term sheet standard?" "What do I get at a $20M
  exit?" "What is the liquidation preference doing?" "What should I ask my lawyer about this term sheet?"
- "Should we take this term sheet?": run the review and say, in one line, that whether to sign is the founder's call
  with their lawyer.
- "Is this term sheet standard?": never answer yes or no. Say which terms match the YC baseline, which differ and which
  it does not cover, each from the marks table, and that "standard" here means only that baseline.
- A pasted term sheet, a summary of its key terms, or a term sheet file the agent can read in this session, with or
  without the pro forma cap table that came with it.
- Hand off:
  - Before any term sheet, checking the ask in a deck: the vc-deal-math skill. One equity scenario with no term
    sheet (a pool alone, vesting, one waterfall): the equity-calculator skill.
  - A SAFE or a convertible note offered on its own, with no priced round: not a term sheet this skill reviews. Its
    conversion goes to `equity_round` as vc-deal-math step 2 says, once the founder gives the next priced round they
    expect; explain its terms in plain words and send the founder to their lawyer.
  - The story and the say-and-avoid list for the next round: the vc-positioning skill. Claims in a deck: the
    vc-claims-check skill. The deck as a whole: the vc-deck-review skill (preview).
  - How much to raise and what it buys: the vc-round-sizing skill (preview).
  - Diligence after the term sheet, with a data-room checklist: the vc-diligence-questions skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess.

1. The term sheet, every term word for word, in its own order and with its own headings (or the key terms, each
   quoted), and whether the text is the whole sheet. Figures are quoted as the sheet states them.
2. The round: the amount, the valuation and whether the sheet labels it pre- or post-money, the option pool target
   and whether the sheet counts it in the valuation, and any SAFEs or notes that convert (amount, cap, discount).
3. The cap table today: the fully diluted shares (every share, granted options and the unissued pool included), the
   unissued pool, the founders' shares, any earlier preferred classes (shares, amount invested, preference,
   participation, seniority), and whether granted options should count as exercised in an exit. The pro forma cap
   table, if the founder has one, is the best source for every share count.
4. Exit values to look at: one low, one the founder thinks likely, one hoped for, in their own figures.
5. What the founder believes the round does ("we keep 75%"), so the calculator can check it.
6. The stage of the round and anything the founder already knows they care about (board control, a sale soon).

A missing input does not stop the review. It becomes a named gap in the answer, never a plausible figure. A
missing share count means the waterfall is not run, said plainly; it is never estimated.

## The baseline and the marks

The baseline is Y Combinator's standard and clean Series A term sheet (the template and the article beside it,
which says it "substantively reflect[s] what we see most often"). It is a Series A sheet: say so when the round is a
seed round, and keep the comparison. Each term gets one mark:

- **Matches:** the sheet says what the baseline cell says; the sheet's line is quoted beside the cell.
- **Differs:** the sheet says something else; quote both and say which way it moves money or control, citing the
  row's source. "Differs" is a fact about two texts, never a verdict on the term.
- **Not in the baseline:** the baseline has no such term (redemption, pay-to-play, warrants). Say what it does, cite
  the row's source, and make it a lawyer question.
- **Missing:** the founder has said the text is the whole sheet, the baseline has the term, and the sheet is silent
  (no drag-along, no vesting line). A lawyer question.

When the founder pasted only some terms, or has not said the text is the whole sheet, a baseline term the text leaves
out gets no mark: it goes to the open asks as "not in what was pasted", with a request for the whole sheet. Only a
term the baseline has can be Missing. Founder vesting, which the baseline leaves blank to negotiate, is Differs when
the sheet fills it in and Missing when a whole sheet is silent on it.

The Baseline column below summarises the YC template in this skill's own words and leaves the template's amounts and
rates out on purpose; it is not a quotation, and the answer never presents it as one.

## The terms

Each row: the term, what it does in plain words, what the baseline says, how its effect is worked, and the sources
behind the row. "Feld" is Brad Feld and Jason Mendelson's term sheet series (2005): say its date when a founder
leans on it.

| Term                                                               | What it does                                                                                                                  | Baseline (YC template)                                                                           | Worked by                          | Source                                                       |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------- | ------------------------------------------------------------ |
| Amount and valuation                                               | How much comes in and at what price; whether the valuation is pre- or post-money                                              | A post-money valuation that includes the option pool                                             | `equity_deal_check`                | YC template; Feld "Price"                                    |
| Option pool                                                        | Shares set aside for hires; inside the valuation it lowers the founders' real price                                           | Pool sized as a percent of the post-closing fully diluted shares, inside the valuation           | `equity_deal_check`, `equity_pool` | YC template; Feld "Price"                                    |
| Liquidation preference                                             | What preferred stock takes back first in a sale or wind-down                                                                  | 1x                                                                                               | `equity_waterfall`                 | YC template and article; Feld "Liquidation Preference"       |
| Participation                                                      | Whether preferred takes its preference and a share of the rest too, or chooses one                                            | Non-participating                                                                                | `equity_waterfall`                 | YC template and article; Feld "Liquidation Preference"       |
| Seniority                                                          | Whether a later series is paid before earlier ones or beside them                                                             | One Series A; SAFEs and notes convert into shadow series                                         | `equity_waterfall` (rank)          | YC template; Feld "Liquidation Preference"                   |
| Dividends                                                          | A yearly percent owed to preferred; cumulative ones add to the preference                                                     | Non-cumulative, only when the board declares them                                                | not modelled                       | YC template and article; Feld "Dividends"                    |
| Conversion                                                         | When preferred becomes common, by choice or automatically                                                                     | At the holder's option; automatic at an IPO or by a preferred majority; 1-to-1                   | `equity_waterfall` (1-to-1 only)   | YC template; Feld "Conversion"                               |
| Anti-dilution                                                      | How the conversion price moves if a later round is priced lower                                                               | Broad-based weighted average                                                                     | not modelled                       | YC template; Feld "Anti-Dilution"                            |
| Protective provisions                                              | Actions that need the preferred holders' consent                                                                              | A short list; the vetoes on a new financing and on a sale matter most                            | none (text)                        | YC template and article note 2; Feld "Protective Provisions" |
| Board                                                              | Who holds the seats, and so who can replace the CEO                                                                           | Lead investor 1 seat, common majority 2                                                          | none (text)                        | YC template and article; Feld "Board of Directors"           |
| Operational approvals                                              | An investor director's consent for budgets, hiring, a pivot                                                                   | Not in the template                                                                              | none (text)                        | YC article                                                   |
| Drag-along                                                         | Who can force every holder to vote for a sale                                                                                 | Needs the board, a preferred majority and a common majority                                      | none (text)                        | YC template; Feld "Drag Along"                               |
| Founder vesting                                                    | Whether founders' shares re-vest, with any credit for time served and any acceleration                                        | Founders: left blank to negotiate; employees: 4 years monthly with a 1-year cliff                | `equity_vesting` on request        | YC template; Feld "Vesting"                                  |
| Pro rata, first refusal, co-sale, information, registration rights | Investors' rights to buy into later rounds and to see information; a multiple on the right to buy is the part to check (Feld) | "Standard" rights                                                                                | none (text)                        | YC template; Feld "Right of First Refusal"                   |
| Redemption                                                         | Investors can make the company buy their shares back                                                                          | Not in the template                                                                              | not modelled                       | Feld "Redemption Rights"                                     |
| Pay-to-play                                                        | Investors who skip a later round lose rights                                                                                  | Not in the template                                                                              | not modelled                       | Feld "Pay-to-Play"                                           |
| Warrants                                                           | Extra shares for the investor beyond the price paid                                                                           | Not in the template                                                                              | not modelled                       | YC article; Feld "Price"                                     |
| No-shop and conditions                                             | What binds now (the no-shop, fees) and what must happen before closing                                                        | A 30-day binding no-shop; everything else non-binding; company pays the lead's capped legal fees | none (text)                        | YC template; Feld "Conditions Precedent"                     |

Never quote a share of deals that use a term: no figure from a market survey appears in the answer. Cooley's Q2 2026
Venture Financing Report says liquidation-preference structures "remained favorable to companies"; quote those
words, with the report and its date, when a founder asks whether a 1x non-participating preference is still usual.

## Steps

With a subagent tool (in Claude Code, the Agent or Task tool), step 6 spawns the four lens subagents in one message,
however short the sheet, then one refute subagent per objection that survives the quote check, as "How to run the
lenses" says; the one-agent order below is only for a client with no subagent tool. Without a subagent tool, take the
steps in this order: 1, 3, 4, 5, then Stage A of the adversarial review (as "How to run the lenses" says), then 2,
then the rest of 6. The lenses need the calculator's output but must not see the marks.

The tools return JSON. The field names below are the JSON's; the command line's report prints the same values under
the labels given in parentheses.

1. **Quote the sheet.** List every term word for word with its heading, in the sheet's order. Do not tidy it.
2. **Explain and mark each term** against the table above: what it does in plain words, the baseline cell from the
   table, the mark, the source. A term the table does not hold is explained in plain words, marked Not in the
   baseline, and made a lawyer question; say the explanation is this skill's own reading, unverified.
3. **The round's arithmetic.** Send money and percents as strings (a stated percent or runway with the document's own
   places, since one that is the tool's figure rounded to them is consistent); one call per figure, never a figure
   from one tool matched by eye against another.
   - `equity_deal_check` (from the command line, `equity_calculator deal_check`): the amount, the valuation with its
     label (a valuation with no label: call twice, once as `pre_money` and once as `post_money`), the pool target and
     its timing, every SAFE and note as `instruments`, the founders' shares as `holder_shares`, and every figure the
     founder believes as `stated_investor_percent` or `stated_holder_percent`. Its `effective_pre_money`
     ("Effective pre-money"), `holder_ownership_after` ("After: holder group"), `investor_ownership`, `checks`,
     `flags` and `verdict` are the figures for the price, the founders' ownership and any belief that does not hold.
     With two readings, show both side by side. Only a check that is a mismatch under every reading is the
     calculator's mismatch; a mismatch under one reading only is not: it becomes one lawyer question, to have the
     sheet say pre- or post-money, quoting both readings in the tool's values.
   - Fully diluted shares, for the tool, count every share before the round, granted options and the unissued pool
     included and SAFEs and notes excluded. Some cap tables count SAFEs and notes in their fully diluted total; ask
     which way the founder's does, and pass the tool its own basis. If the founder's total counts them, ask the
     founder for the total without them, as a bracketed ask,
     `[fully diluted shares before the round, SAFEs and notes left out]`, and leave every cap-table field out of the
     call until they give it; never subtract the SAFE or note shares yourself.
   - `equity_pool`, only when no SAFE or note converts and the sheet sets a pool target: the same round with
     `share_rounding` set to `whole_shares` and the same `pool_timing` as `equity_deal_check`. It returns two tables,
     `pool_in_pre_money` and `pool_in_post_money`, each with its own `rows`. The one that matches the sheet's pool
     timing is the deal (`inputs.pool_timing` names it; the report marks its column "(this deal)"): take the whole
     share counts the waterfall needs from that table's `rows` only. The other table is the what-if (what moving the
     pool would change). It holds the pre-money fixed, so its price and post-money are not the sheet's: quote its
     `post_money` ("Post-money (every share at p)") and `price_per_share` ("Price per share (p)") beside its investor
     ownership, and say the sheet's own post-money stays as stated. Its `pre_money` is `equity_deal_check`'s
     `pre_money` ("Pre-money valuation (V)"), passed on, never subtracted by hand. A whole share count prints as
     `2307692.000`; pass it as the integer `2307692` (notation, not rounding).
   - A tool value whose unit is `fraction` is a share of the whole. Show it as a percent by moving the decimal point
     of its `rounded` value two places to the right, keeping every digit (0.166667 is 16.6667%), which is what the
     command line's report prints. That is a change of notation, not a calculation; never round it.
   - `equity_dilution`, only when the founder asks what a later round they expect does to their stake:
     `holder_percent` is `equity_deal_check`'s `holder_ownership_after` ("After: holder group") shown as a percent,
     and each round's `investor_percent` and `pool_percent` are the founder's own figures for that round, never
     assumed. Its `final_stake` ("Final stake") is the founders' stake after it.
   - `equity_vesting`, only when the founder asks how much of their shares would be vested at a month they name
     under the sheet's founder vesting: `grant_shares`, `total_months`, `cliff_months`, `acceleration` and
     `acceleration_percent` as the sheet and the founder state them, `acceleration_base` `grant` when the sheet's
     percent is of the whole grant, and `month` as the founder names it. With acceleration, also
     `change_of_control_month`, the month of the sale the founder names; for a double trigger, also
     `termination_month`, the month the founder names for being let go, without which the acceleration never fires.
     A month the founder has not named is never picked: say "not run: name the month of the sale" (or "of the
     termination") and ask for it. A founder who says they stay on after the sale has no termination month: leave
     `termination_month` out and say the double trigger does not fire. Credit for time served has no tool input:
     quote it with "not modelled: no tool computes this term's effect", run no vesting call for that grant, never
     shift a month by hand, and make it a lawyer question.
4. **The waterfall,** `equity_waterfall`, one call per exit value:
   - `common_shares`: the issued common that takes part in a sale (the founders' shares, other issued common, and
     granted options only when the founder says to count them as exercised). The unissued pool takes nothing. Take
     the count from the pro forma cap table or a count of issued common the founder states. The `existing_holders`
     row of `equity_pool` (every share but the unissued pool, so earlier preferred shares too) serves only when there
     are no granted options (or the founder says to count them all as exercised) and no earlier preferred class;
     otherwise take issued common from the pro forma or the founder's count, or the earlier class is counted twice.
     Never add or subtract shares yourself.
   - `classes`: the new series with its `shares` from the pro forma or from the `investor` row of the `equity_pool`
     table that matches the sheet's pool timing (`pool_in_pre_money` when the pool is inside the valuation),
     `invested`, `preference_multiple`, `participation` (`none`, `full`, or `capped` with `cap_multiple`) and `rank`;
     then each earlier preferred class with its own terms. Seniority: every class at rank 1 when the sheet says pari
     passu or is silent (say so); the new series at rank 1 and earlier ones at 2 when the sheet stacks them.
   - When SAFEs or notes convert, the calculator's converted shares are fractional and `equity_waterfall` takes whole
     shares; when the sheet sets no pool target, `equity_pool` does not run (it takes no 0% target) and no other tool
     gives the new series' whole share count. In either case run the waterfall only with the pro forma cap table's
     counts. Without them, say "not run: the waterfall needs whole share counts; send the pro forma cap table" and
     ask for it; never divide the amount by the price yourself.
   - Exit values, each named with where it comes from: the amount raised as the sheet states it; the post-money (as
     the sheet states it, or `equity_deal_check`'s `post_money`); the new series' preference owed, as the first
     waterfall run gives it (`rows[0].preference_owed`, "Class 1: preference owed"), when it differs from the amount
     raised; and every exit the founder named. Never an exit value you worked out ("half the post-money", the point
     where the investor converts).
   - When the sheet's preference differs from the baseline (a multiple above 1x, or any participation), run each exit
     a second time with the new series at `preference_multiple` 1 and `participation` `none`, every other input the
     same, as the baseline column. Run no other what-if unless the founder asks.
   - Read each result: every row's `converts` (true: it converts; false: it stays), its `payout`, and
     `common_payout` ("Common stock's payout"). When the founders hold every common share that takes part, the
     common payout is the founders' payout; otherwise give the common payout and its per-share part and say "not
     checked: no tool splits the common payout by holder".
   - Explain participation only with the row's own fields (`preference_paid`, `residual_share`, `payout`). Never set
     the round's ownership percent beside the waterfall's `residual`: the unissued pool takes nothing in a sale, so a
     class's share of the rest is not its cap-table percent.
5. **Terms the calculator does not model.** Cumulative dividends, anti-dilution, redemption, pay-to-play, warrants,
   conversion thresholds, management carve-outs, credit for time served on founder vesting, and debt, fees or
   escrow taken out of a sale are quoted with
   "not modelled: no tool computes this term's effect", and the waterfall's `exit_is_shared_amount` and
   `conversion_one_to_one` assumptions are quoted beside the exit table. Never fold one into another input (a
   dividend into `preference_multiple`, a ratchet into the share count).
6. **Run the adversarial review** (next section): attack, check the quotes, refute, rank.
7. **Write the lawyer questions:** one per Differs, Not in the baseline and Missing mark, one per surviving
   objection, and one per mismatch from `equity_deal_check`, each tied to the sheet's line, grouped as Economics,
   Control and Process. A question asks; it never recommends and never proposes a trade ("What does the 2x
   participating preference pay common at our low exit?" is a question; "push back on the 2x" and "ask for a lower
   valuation in return" are not).
8. **Check before answering.** Every quote is in the sheet or the founder's material word for word; every figure is
   quoted as stated or comes from a tool; a count of terms is a figure too, taken from the marks table or left out;
   lawyer questions use only the periods and amounts the sheet or the founder gave; no sentence says to sign or not to
   sign, says what a term "should" be, or speaks as an investor; every source named is in the Sources list; the
   answer gives a refute verdict for every objection that reached the refute pass; the answer says to get a lawyer.

## Adversarial review

The marks say how the sheet differs from a clean one; this review says what those terms will cost later, when the
next round's lead, an acquirer or the board reads them. Independent lenses attack, a second pass judges each
objection using only the founder's material, and only what that material does not answer reaches the founder.

### Stage A: attack

Each lens tests one thing and is named by it. The lenses are frameworks, never people: none is a named investor,
firm or lawyer, and none speaks in the first person.

| Lens                  | What it tests                                                                                                                                                                       |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The next round's lead | Terms a later investor is likely to ask to match, or to ask existing investors to drop: preference multiple, participation, seniority, separate class votes, rights with a multiple |
| An acquirer           | What makes a sale harder or splits the price away from common: the preference stack at the exit values run, consent and drag-along thresholds, redemption, acceleration             |
| The team and the pool | What employees and founders take at low exits (from the tool output given), the pool's size and timing, vesting and acceleration                                                    |
| Control               | Board seats, protective provisions, operational approvals, conditions to close, and what binds before signing                                                                       |

Every lens gets the same brief, with its own name and test filled in:

- You test one thing: the lens's name and what it tests. Write in the third person ("a later lead investor is
  likely to ask ..."); you are not an investor, acquirer or lawyer and do not speak as one, named or not.
- Read only what you are given: the term sheet, the founder's answers and the calculator's printed output. Bring in
  no outside fact about the company, the investor or the market, and do no arithmetic.
- Return at most three objections, strongest first. For each: the sheet's line, quoted word for word with its
  heading; why that reader is likely to object to it; and how much it costs (a later deal is likely to stall on it,
  a later deal is likely to ask about it, or minor).
- An objection you cannot tie to a line of the sheet is not an objection. List it apart as a gap, worded as a
  question.
- Do not judge whether another line of the sheet answers an objection: raise it anyway, however short the material;
  the refute pass decides. Return "nothing found" only when no line of the sheet gives this lens an objection worth
  the founder's time. Say nothing about whether to sign.

**How to run the lenses.** With a subagent tool (in Claude Code, the Agent or Task tool), run the lenses as
parallel subagents, however short the material, all launched in one message, each given only the sheet, the
founder's answers, the calculator's output and its lens brief: not
the marks, not this skill's other sections, not another lens's output. Without one, run them one after another after
step 5 and before step 2 (no mark exists yet), write each lens's objections down in full before reading the next
brief, and never revise an earlier list. Lenses run this way are less independent than subagents, and the same agent
then judges them, so the answer says so.

**The calculator's mismatches** from step 3 do not go through the lenses: each heads the survivors, ahead of the
tiers, quoting the founder's belief with the tool's value and difference. It is computed, not argued, and not refuted.
It carries no tier: how much a gap hurts depends on its size and on the term, which the founder weighs. It leads
because the founder's own figure for the round is wrong, which matters before anything else; it is not a prediction
about a later deal. A question to label the valuation (a mismatch under one reading only) is not a calculator
mismatch.

### Check the quotes

Before Stage B, check every objection's quote against the sheet. A quote not there word for word (spacing and line
breaks aside) is dropped as not grounded. Merge two lenses' objections to the same line and keep both lens names.
Gaps go to the open asks.

### Stage B: refute

Each objection gets its own refute pass. With a subagent tool, launch one subagent per objection in a single message;
never put two objections in one subagent. Give each one the sheet, the founder's answers, the calculator's output,
that one objection, the baseline column of the terms table, and everything from "The refute brief:" to the end of
this stage, and nothing else. Without one, decide the objections
one at a time against the same brief.

The refute brief:

- You decide whether the sheet itself answers one objection; you argue neither side. Write in the third person; you
  are not an investor, acquirer or lawyer and do not speak as one.
- Use only what you are given. Bring in no outside fact about the company, the investor or the market, and do no
  arithmetic.
- How a later investor, an acquirer or a board is likely to read a line is not an outside fact: judge whether the
  sheet answers that reading.
- A line that differs from the baseline never answers an objection.
- Return one verdict from the three below, quoting the line word for word where it needs one. When you cannot decide,
  return Kept.

The verdicts:

- **Dropped, answered:** a line of the sheet other than the objected line supplies the specific thing the objection
  says is missing (a carve-out, a common-majority vote on a sale). Quote it with its heading.
- **Dropped, not grounded:** the quoted line does not say what the objection claims, or the objection rests on an
  outside fact.
- **Kept:** neither holds. What the founder would need to know becomes a lawyer question.

The refute pass invents nothing: no term, side letter, promise or argument the founder did not give. An answering
line that is not in the sheet word for word, or that is the objected line itself, does not drop the objection.

### Rank what survives

Three tiers, most costly first: **a later deal is likely to stall on it**, **a later deal is likely to ask about
it**, **minor**. The calculator's mismatches head the list, ahead of the tiers, under **figures that do not match
(computed)**, with no tier. Within a tier, an objection raised by more than one lens comes first. The tier is a judgment, not a probability, and never a recommendation: no percentages, no score,
no "do not sign". Each survivor becomes a lawyer question in step 7.

## Answering

Lead with the reminder, then the terms, then the money, then what a later reader will object to.

1. **First:** this is a plain-words reading to prepare for the lawyer, not legal, tax or investment advice; whether to
   sign, and on what changes, is for the founder with their lawyer. One line, no verdict.
2. **The terms,** as a table: Term, The sheet says (quoted), In plain words, Baseline (YC template, this skill's
   summary), Mark, Source.
3. **The money:**
   - `equity_deal_check`: the headline valuation beside the effective pre-money, the founders' percent after, the
     pool, each SAFE or note, and every mismatch with the founder's belief in the tool's values; each flag as its code
     with its meaning from the flag table below (over MCP the tool returns the code alone).
   - The pool counted in the pre-money beside the post-money, from `equity_pool`, when it ran: the what-if column's
     investor ownership with its own price and post-money, saying it holds the pre-money fixed.
   - **Exit table:** Exit value, Where it comes from, the new series' choice, its payout, the common payout under the
     sheet, the common payout under the baseline (when run). Compute no difference between columns.
   - When the founder asked: the founders' stake after the later round they named, from `equity_dilution`, and the
     shares vested at the month they named, from `equity_vesting`, each in the tool's values.
   - Every not-modelled term with its string, and the waterfall's assumptions the table leans on.
4. **What a later investor, acquirer or board is likely to object to:** survivors as a table: Rank, Tier, Lens, The
   sheet's line (quoted), Why that reader objects; the figures that do not match (computed) first, with no tier.
   Then **Refute verdicts:** one line for every objection that reached the refute pass, Kept ones included, each with
   its verdict, and for a Dropped one why it fell. Say how the lenses and the refute pass ran (as subagents, one
   refute subagent per objection); when the lenses ran in one agent, say they are less independent than separate
   subagents.
5. **Questions for your lawyer,** numbered, under Economics, Control and Process.
6. **Open asks:** every gap, in one list, with the baseline terms not in what was pasted.
7. **Sources:** the ones used, with links and dates, and which explanations are this skill's own, unverified.
8. **Close:** have a lawyer who works on startup and venture financings review the sheet before signing; ask them
   which parts bind on signing (the sheet itself says, often the no-shop and fees); this is not legal, tax or
   investment advice.

## Flags

`equity_deal_check`'s `flags` holds codes only; over MCP no sentence comes with them (the command line prints one
beside each). This is what each means for the founder: a question a later reader is likely to ask, never an error.

| Flag                                  | What it means for the founder                                                                                   |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `valuation_back_solved`               | No valuation was given, so the post-money was worked from the raise and the percent: the sheet should say which |
| `pool_in_pre_money_lowers_price`      | The new pool is paid for out of the pre-money, so the effective pre-money and the price are below the headline  |
| `pool_in_post_money_dilutes_investor` | The pool is counted after the money, so the investor gets less than raise / post-money                          |
| `pool_already_large_enough`           | The unissued pool already meets the target, so no new pool shares are needed                                    |
| `conversions_bought_by_pre_money`     | SAFE and note shares come out of the pre-round holders, so their stake falls by more than the percent sold      |
| `discount_beat_cap`                   | A discount gave a lower price than the cap, so a cap-only conversion would be wrong                             |
| `note_interest_converts`              | Note interest converts too, so a note gets more than its principal's worth of shares                            |
| `consistent_beyond_rounding`          | A stated percent or runway holds by the tolerance alone, not as the tool's figure rounded to its own places     |
| `net_burn_not_positive`               | Revenue covers the burn on those figures, so there is no net runway on them                                     |
| `current_burn_runway_longer`          | Runway on today's burn is longer than on the planned burn                                                       |
| `runway_below_band`                   | Planned runway is under the tool's runway benchmark (a common benchmark, not a rule)                            |
| `dilution_above_band`                 | The investors get more than the tool's dilution benchmark in one round (a common benchmark, not a rule)         |

## Sources

- Y Combinator, "A standard and clean Series A term sheet" (Jason Kwon and Aaron Harris):
  https://www.ycombinator.com/library/4P-a-standard-and-clean-series-a-term-sheet
- Y Combinator, "Series A Term Sheet Template" (the page and its Word document):
  https://www.ycombinator.com/series_a_term_sheet
- Brad Feld and Jason Mendelson, the term sheet series on Feld Thoughts (2005):
  - "Term Sheet: Price": https://feld.com/archives/2005/01/term-sheet-price/
  - "Term Sheet: Liquidation Preference": https://feld.com/archives/2005/01/term-sheet-liquidation-preference/
  - "Term Sheet: Board of Directors": https://feld.com/archives/2005/01/term-sheet-board-of-directors/
  - "Term Sheet: Protective Provisions": https://feld.com/archives/2005/01/term-sheet-protective-provisions/
  - "Term Sheet: Drag Along": https://feld.com/archives/2005/02/term-sheet-drag-along/
  - "Term Sheet – Anti-Dilution": https://feld.com/archives/2005/03/term-sheet-anti-dilution/
  - "Term Sheet: Pay-to-Play": https://feld.com/archives/2005/03/term-sheet-pay-to-play/
  - "Term Sheet: Redemption Rights": https://feld.com/archives/2005/03/term-sheet-redemption-rights/
  - "Term Sheet: Dividends": https://feld.com/archives/2005/03/term-sheet-dividends/
  - "Term Sheet: Conversion": https://feld.com/archives/2005/04/term-sheet-conversion/
  - "Term Sheet: Conditions Precedent to Financing":
    https://feld.com/archives/2005/04/term-sheet-conditions-precedent-to-financing/
  - "Term Sheet – Vesting": https://feld.com/archives/2005/05/term-sheet-vesting/
  - "Term Sheet: Right of First Refusal": https://feld.com/archives/2005/06/term-sheet-right-of-first-refusal/
- Cooley, "Q2 2026 Venture Financing Report" (17 August 2026), the web page (the PDF was not read):
  https://www.cooley.com/news/insight/2026/2026-08-17-q2-2026-venture-financing-report

The Feld series is from 2005 and written by investors; use it to explain what a term does, never as today's
practice, and never repeat its worked figures. The YC baseline is one accelerator's view of a clean Series A, not a
survey. The lenses, the tiers, the marks and every plain-words explanation of a term the table does not hold are this
skill's own, unverified. The two-stage review (attack, then refute with the founder's own material) is this
repository's own method.

## Limits

- Not legal, tax or investment advice. It never says whether to sign, whether a term is acceptable, or what to
  counter-offer; it says how a term differs from a cited baseline and what to ask a lawyer.
- No number of its own: every figure is quoted from the sheet or comes from a tool. No market-survey percentages, no
  "most deals", no exit value or breakpoint it worked out.
- Not modelled by any tool here: cumulative dividends, anti-dilution, redemption, pay-to-play, warrants, conversion
  thresholds, carve-outs, credit for time served on founder vesting, and debt or fees ahead of shareholders in a
  sale. They are explained and quoted, never estimated.
- It never role-plays or speaks as a named investor, firm or law firm, and does no investor research: it does not
  say whether a named investor offers better terms.
- The adversarial review predicts likely objections from the sheet's text; a real investor or acquirer may raise
  others.
- It works from the founder's text and sends nothing anywhere.
