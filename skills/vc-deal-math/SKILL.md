---
name: vc-deal-math
description: Helps a founder check the numbers in their own fundraising ask before a VC does, with the equity calculator's deal_check tool. It tests whether the pre-money, post-money and percent sold agree, what the round really does to the founders' ownership once SAFEs, convertible notes and an option-pool top-up are counted, the effective pre-money after the option-pool shuffle, how many months of runway the raise buys at the planned burn, and whether the use-of-funds lines add up to the raise. Use when a founder says check my deck's numbers, is our raise reasonable, what does this round do to my ownership, how much runway does this buy, will a VC question our valuation, or pastes their ask, SAFE stack or use-of-funds slide. Every figure comes from the calculator and the deck's figures are quoted as stated. Not investment, legal or tax advice. For one scenario on its own (an option pool, vesting, an exit waterfall) use the equity-calculator skill.
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

## Steps

1. **List what the deck states, word for word**: the raise, any valuation and whether it is labelled pre- or
   post-money, the percent sold, the founders' percent after the round, the option pool and whether it sits in the
   pre-money, outstanding SAFEs and notes, cash on hand, burn, revenue, the runway claim and the use-of-funds lines.
   Quote each figure as stated; never correct it before the check.
2. **Ask the founder for what is missing, by name, in one message.** Never guess:
   - SAFEs, notes or a pool top-up need the fully diluted share count before the round (every share, granted options
     and the unissued pool included) and the unissued pool. If the founder does not have them to hand, offer a
     stand-in of 10,000,000 shares with the pool as its percent of that. Use it only on their yes, say so in the
     answer, and quote only percentages and money from that run, never prices or share counts.
   - Each SAFE: amount, post-money cap and/or discount, MFN. Each note: principal, interest rate, months outstanding
     (or issue and conversion dates), simple or compounding interest, cap and/or discount.
   - A claim about the founders' percent after the round needs their share of the company today, on the same fully
     diluted basis (9,000,000 of 10,000,000 shares is 90). If they give it on another basis, ask for the share counts.
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
6. **Follow-ups go to tools too**: a different pool size or timing, or a smaller raise, by re-running
   `equity_deal_check`; the next round's effect with `equity_dilution`; a full exit split with `equity_waterfall`.

## Answering

Lead with the verdict, then the table, then the questions, then the assumptions. Use the tool's printed values
(`rounded` with its unit, or the exact fraction when precision matters); never round again or recompute.

1. **Verdict.** "All N figures the deck states are consistent", "M of N figures the deck states do not match", or
   "The deck states nothing the calculator can check; here is what the round does."
2. **Checks table:** "The deck says", "The calculator gives", "Difference", "Consistent?", one row per check.
3. **What the round does to you.** Ownership after the round: the founders, existing holders, each SAFE or note, the
   pool, the new investor. Also the share of their stake every pre-round share keeps, the effective pre-money against
   the headline, and what the pre-money pays for.
4. **Runway:** each burn case's net and gross runway, and which one the claim was checked against.
5. **What a VC is likely to ask**, one line per flag, in plain words, with how to fix the deck or prepare the answer.
   A flag is a question to be ready for, never an error. The two benchmark flags (dilution above 25%, runway under
   18 months) are common benchmarks, not rules: say so, say they vary by sector, stage and year, and quote the source
   the tool's assumption row gives, which today is `unverified`.
6. **Assumptions:** quote the ones the answer leans on, with their sources. Say plainly which are `unverified` and how
   to change a default (pool timing, note compounding, the tolerances, the two benchmarks).
7. **Close** with what a lawyer or accountant should confirm before the deck goes out: the actual cap table, the SAFE
   and note documents, the term sheet's pool wording.

## Limits

- It checks the arithmetic of the figures the founder gives. It does not read a deck file, a cap table file or a term
  sheet; the founder's text is the input, and nothing is sent anywhere.
- It is not investment, legal or tax advice, and it does not say whether to take a round or what a company is worth.
- Benchmarks are common benchmarks, not rules. Quote one only as the tool's assumption rows give it, with the source
  they name, or as `unverified` when they name none.
- It uses named public frameworks (Y Combinator's post-money SAFE user guide, the option-pool shuffle, runway on net
  burn), never the voice or opinion of a named investor or firm.
- Shares are exact fractions; a real cap table rounds to whole shares, which moves figures by a share or a cent.
- Use-of-funds lines are checked only for adding up to the raise. No sourced benchmark for how a raise should split by
  category was found, so none is applied.
