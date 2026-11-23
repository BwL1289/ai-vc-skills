---
name: vc-deal-math
description: Helps a founder check the numbers in their own fundraising ask before a VC does, with the equity calculator's deal_check tool. It tests whether the pre-money, post-money and percent sold agree, what the round really does to the founders' ownership once SAFEs, convertible notes and an option-pool top-up are counted, the effective pre-money after the option-pool shuffle, how many months of runway the raise buys at the planned burn, and whether the use-of-funds lines add up to the raise. Use when a founder says check my deck's numbers, is our raise reasonable, what does this round do to my ownership, how much runway does this buy, will a VC question our valuation, or pastes their ask, SAFE stack or use-of-funds slide. Every figure comes from the calculator and the deck's figures are quoted as stated. Not investment, legal or tax advice. For the story and the ask together use vc-positioning. For one scenario on its own (an option pool, vesting, an exit waterfall) use the equity-calculator skill.
---

# VC deal math

Helps a founder see their raise the way a VC will, before the meeting: does the valuation add up, what does the round
really do to the founders' ownership once SAFEs, notes and the option pool are counted, and how long does the money
last. The `equity_deal_check` tool does every calculation exactly and returns each figure the deck states as
consistent or a mismatch, with the difference, plus the questions a VC is likely to ask and the assumptions behind
them. The aim is a deck whose numbers hold up, so the meeting is about the company, not the arithmetic.

## When to use it

- "Check my deck's numbers." "Is our raise reasonable?" "What does this round do to my ownership?"
- "How much runway does this buy?" "Will a VC question our valuation?"
- A pasted ask slide, a SAFE or note list, a cap table summary or a use-of-funds slide.
- Hand off to the equity-calculator skill for a single question with no deck to check: an option pool alone
  (`equity_pool`), SAFE conversion detail (`equity_round`), a stake through later rounds (`equity_dilution`), vesting
  or an exit waterfall.
- Hand off to the vc-round-sizing skill for how much to raise on a phased plan, raise now or wait, or which milestone
  month a raise's cash reaches.

## Steps

1. **List what the deck states, word for word**: the raise, any valuation and whether it is labelled pre- or
   post-money, the percent sold, the founders' percent after the round, the option pool and whether it sits in the
   pre-money, outstanding SAFEs and notes, cash on hand, burn, revenue, the runway claim and the use-of-funds lines.
   Quote each figure as stated; never correct it before the check.
2. **Ask the founder for what is missing, by name, in one message.** Never guess:
   - **Is the new money a priced round, or a SAFE or note?** `deal_check` works the new money as a priced equity
     round. If the founder is raising on a SAFE or a note, do not pass it as `investment`: a SAFE's share is set only
     at the next priced round, and "the safes are not diluted by each other" (Y Combinator's post-money SAFE user
     guide), so `deal_check` would report a correct founders' figure as a mismatch. Say so, and offer `equity_round` instead
     (the equity-calculator skill), with the new SAFE or note as one more instrument and the next priced round the
     founder expects (its size, pre-money and pool target) as the round; say the figures depend on that round.
   - SAFEs, notes or a pool top-up need the fully diluted share count before the round (every share, granted options
     and the unissued pool included) and the unissued pool, as shares (`unissued_pool_shares`) or as a percent of
     the fully diluted shares (`unissued_pool_percent`). If the founder does not have them to hand, offer a stand-in
     of 10,000,000 shares with the pool passed as `unissued_pool_percent`. Use it only on their yes, say so in the
     answer, and quote only percentages and money from that run, never prices or share counts.
   - Each SAFE: amount, post-money cap and/or discount, MFN. Each note: principal, interest rate, months outstanding
     (or issue and conversion dates), simple or compounding interest, cap and/or discount, and what the cap is
     measured against. The calculator reads a note's cap as a pre-money cap over today's fully diluted shares (its
     `note_cap_basis` assumption); if the note says otherwise, say the result does not model that note.
   - A claim about the founders' percent after the round needs their stake today, on the same fully diluted basis:
     pass a share count as `holder_shares` (9,000,000 of 10,000,000 fully diluted shares) or a percent of every fully
     diluted share as `holder_percent`. Never divide the shares yourself. If they give a percent on another basis (of
     issued shares only, say), ask for the share counts.
   - A runway claim needs cash on hand and the planned monthly spend and revenue after the raise. Ask for today's
     spend and revenue too: decks often quote runway on today's burn, and a VC will check it against the plan.
   - Pool timing: if the term sheet or deck does not say, use the pre-money (the usual term sheet), say so, and offer
     to re-run with the pool in the post-money.
3. **Call `equity_deal_check`** with every stated figure. Send money and percents as strings:

   ```json
   {
     "inputs": {
       "investment": "3000000",
       "pre_money": "12000000",
       "stated_investor_percent": "20",
       "fully_diluted_shares": 8000000,
       "target_pool_percent": "10",
       "pool_timing": "pre_money",
       "holder_percent": "100",
       "cash_on_hand": "400000",
       "planned_monthly_gross_burn": "180000",
       "stated_runway_months": "24"
     }
   }
   ```

   The same check from the command line:

   ```
   equity_calculator deal_check --investment 3000000 --pre-money 12000000 --stated-investor-percent 20 --fully-diluted-shares 8000000 --target-pool-percent 10 --holder-percent 100 --cash-on-hand 400000 --planned-monthly-gross-burn 180000 --stated-runway-months 24
   ```

   Part of what it prints (Company A, a made-up seed deck: $3M at $12M pre for 20%, a 10% pool in the pre-money,
   $400k in the bank and a planned $180k a month, with a 24-month runway claim):

   ```text
     Effective pre-money                                               $10,500,000.00  (FD - U)·p: the pre-round holders' shares at the round price
     After: holder group                                                     70.0000%  h·kept
     Pre-money pays for: new pool                                       $1,500,000.00  P·p (pool in the pre-money)
     Investors' percent: verdict                                           consistent  within the tolerance is consistent
     Runway: the deck says                                               24.00 months  given
     Runway: the calculator gives                                        18.89 months  (cash + I)/net burn, planned (else current)
     Runway: difference                                                  -5.11 months  computed - stated
     Runway: verdict                                                         mismatch  within the tolerance is consistent
     Overall verdict                                                         mismatch  mismatch if any check is; consistent if all are; not_checked with none
   ```

   The 20% holds, but the 24 months does not: the raise and the cash last 18.89 months at the planned burn. The pool
   in the pre-money also means the founders' shares are priced at $10,500,000.00, not the $12M headline.

4. **A valuation with no label** ("$2M at $10M"): call twice, once as `pre_money` and once as `post_money`, show both
   readings side by side, and tell the founder that a VC will ask which one is meant.
5. **Read the result before answering**: `verdict`, every row in `checks`, every code in `flags`, `runway`,
   `pre_money_split` and `assumptions`. A refusal or tool error is the answer for those inputs: relay its reason and
   what to change.
6. **Follow-ups the founder asks for go to tools too**: a different pool size or timing, or a smaller raise, by
   re-running `equity_deal_check`; the next round's effect with `equity_dilution`; a full exit split with
   `equity_waterfall`.

## Answering

Lead with the verdict, then the table, then the questions, then the assumptions. Use the tool's printed values
(`rounded` with its unit, or the exact fraction when precision matters); never round again or recompute. A value whose
unit is `fraction` is a share of the whole: show it as a percent by moving the decimal point of its `rounded` value two
places to the right, keeping every digit (0.166667 is 16.6667%), which is what the command line's report prints. That
is a change of notation, not a calculation.

1. **Verdict.** "All N figures the deck states are consistent", "M of N figures the deck states do not match", or,
   for `not_checked`, "The calculator could check none of the deck's figures; here is what the round does." A runway
   claim is not checked when revenue covers every burn given (the `net_burn_not_positive` flag): say that claim could
   not be checked, and why.
2. **Checks table:** "The deck says", "The calculator gives", "Difference", "Consistent?", one row per check.
3. **What the round does to you.** Ownership after the round: the founders, existing holders, each SAFE or note, the
   pool, the new investor. Also the share of their stake every pre-round share keeps, the effective pre-money against
   the headline, and what the pre-money pays for. When SAFEs or notes convert, present the pre-money split line by
   line rather than one effective pre-money: the tool's effective pre-money also leaves out the converted shares and
   the unissued pool already there, so it is lower than the pre-money less the new pool that a VC may quote.
4. **Runway:** each burn case's net and gross runway, and which one the claim was checked against: the planned net
   runway, else today's when revenue covers the planned burn.
5. **What a VC is likely to ask**, one line per flag, in plain words, with how to fix the deck or prepare the answer
   (the flag table below). A flag is a question to be ready for, never an error. The two benchmark flags (dilution above 25%, runway under
   18 months) are common benchmarks, not rules: say so, say they vary by sector, stage and year, and quote the source
   the tool's assumption row gives, which today is `unverified`.
6. **Assumptions:** quote the ones the answer leans on, with their sources. Say plainly which are `unverified` and how
   to change a default (pool timing, note compounding, the tolerances, the two benchmarks).
7. **Close** with what a lawyer or accountant should confirm before the deck goes out: the actual cap table, the SAFE
   and note documents, the term sheet's pool wording.

## Flags

The result's `flags` holds codes only; this table is what each one means for the founder. The text report prints the
same meaning beside each flag.

| Flag                                  | What it means for the founder                                                                                   | What to change or prepare                                                                      |
| ------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `valuation_back_solved`               | No valuation was given, so the post-money was worked from the raise and the percent.                            | Label the valuation pre- or post-money in the deck; a VC will ask which it is.                 |
| `pool_in_pre_money_lowers_price`      | The new pool is paid for out of the pre-money, so the effective pre-money and the price are below the headline. | Expect a VC to price it this way; show the effective pre-money beside the headline.            |
| `pool_in_post_money_dilutes_investor` | The pool is counted after the money, so the investor gets less than raise / post-money.                         | Expect a VC to ask to move the pool into the pre-money; show what that does to the founders.   |
| `pool_already_large_enough`           | The unissued pool already meets the target, so no new pool shares are needed.                                   | Say so in the deck; a VC may still ask for a bigger target.                                    |
| `conversions_bought_by_pre_money`     | SAFE and note shares come out of the pre-round holders, so their stake falls by more than the percent sold.     | Show ownership with the SAFEs and notes converted, as a VC reads the cap table.                |
| `discount_beat_cap`                   | A discount gave a lower price than the cap.                                                                     | Model that instrument at its discount price; a cap-only conversion in the deck would be wrong. |
| `note_interest_converts`              | Note interest converts too, so a note gets more than its principal's worth of shares.                           | Count the interest in the cap table.                                                           |
| `net_burn_not_positive`               | Revenue covers the burn on those figures, so there is no net runway on it.                                      | A runway claim is checked on the other burn's net runway; with none, it is not checked.        |
| `current_burn_runway_longer`          | Runway on today's burn is longer than on the planned burn.                                                      | Say which burn the deck's runway uses; a VC will check it against the planned spend.           |
| `runway_below_band`                   | Planned net runway is under the runway benchmark (18 months by default).                                        | Be ready to say whether the raise reaches the next milestone (a common benchmark, not a rule). |
| `dilution_above_band`                 | The investors get more than the dilution benchmark (25% by default) in one round.                               | Be ready to say why so much is sold (a common benchmark, not a rule).                          |

## Limits

- No arithmetic outside the calculator's tools. A figure outside the deal terms (a growth rate, a market size, unit
  economics) is quoted as stated with "not checked: no tool computes this", and no what-if the founder did not ask for
  is run.
- It checks the arithmetic of the figures the founder gives. It does not read a deck file, a cap table file or a term
  sheet; the founder's text is the input, and nothing is sent anywhere. A term sheet goes to the vc-term-sheet-review
  skill.
- It is not investment, legal or tax advice, and it does not say whether to take a round or what a company is worth.
- It works the new money as a priced equity round. A raise on a SAFE or note is not modelled by `deal_check`; step 2
  routes it to `equity_round` with the next priced round the founder expects.
- Benchmarks are common benchmarks, not rules. Quote one only as the tool's assumption rows give it, with the source
  they name, or as `unverified` when they name none.
- It uses named public frameworks (Y Combinator's post-money SAFE user guide, the option-pool shuffle, runway on net
  burn), never the voice or opinion of a named investor or firm.
- Shares are exact fractions; a real cap table rounds to whole shares, which moves figures by a share or a cent.
- Use-of-funds lines are checked only for adding up to the raise. No sourced benchmark for how a raise should split by
  category was found, so none is applied.
