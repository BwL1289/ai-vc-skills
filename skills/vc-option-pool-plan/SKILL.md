---
name: vc-option-pool-plan
description: Helps a founder size the option pool their own hiring plan needs until the next round and set it beside the pool a term sheet asks for, with the equity calculator's pool_plan tool. It works the round both ways, the plan's pool and the requested one, each created in the pre-money, and shows the price per share, the effective pre-money after the option-pool shuffle, the founders' ownership and the pool left ungranted at the next round, with the requested pool less the plan's, then one evidence line for the pool conversation built only from the founder's plan. Use when a founder says the term sheet asks for a 15% pool, is this pool too big, how big a pool do we need, what does the pool cost us, size our option pool from our hiring plan, or the VC wants a bigger pool. Every figure comes from the calculator or the founder, and it never says which pool to accept. Not investment, legal or tax advice. For the whole term sheet use vc-term-sheet-review; for how much to raise use vc-round-sizing.
---

# VC option pool plan

Helps a founder answer the pool ask in a term sheet with their own hiring plan. A term sheet often asks for an option
pool of some percent of the shares after the round, created in the pre-money, so the existing holders (the founders
among them) pay for it and the effective pre-money falls below the headline. The founder's plan says how much of a
pool the hires until the next round actually take. The `equity_pool_plan` tool works the round both ways, exactly: at
the pool the plan needs and at the pool requested, with the requested column less the plan's for every figure. The
founder sees what the ask costs in their own numbers and walks into the conversation with one line of evidence built
from their plan. A VC's view is only a lens here: a partner is likely to ask how the pool was sized, and the plan is
the founder's answer. The skill never says which pool to accept.

## When to use it

- "The term sheet asks for a 15% pool." "Is this pool too big?" "How big a pool do we need?" "What does the pool cost
  us?" "Size our option pool from our hiring plan." "The VC wants a bigger pool."
- The founder's hiring plan (roles, start months, grants) and the term sheet's pool clause, typed in or as files.
  Either may come as a file the agent can read in this session.
- Hand off:
  - The whole term sheet (every term against a standard one, an exit waterfall, questions for the lawyer): the
    vc-term-sheet-review skill (preview).
  - How much to raise and how long it lasts on the plan: the vc-round-sizing skill.
  - A deck's ask checked before a VC reads it (valuation labels, the SAFE stack, percent sold, runway): the
    vc-deal-math skill.
  - One scenario on its own (a pool with the pool in the post-money, SAFEs and notes converting in the round, what one
    hire is worth): the equity-calculator skill (`equity_pool`, `equity_round`, `equity_employee`).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess, and never fill a gap with a typical figure.
When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and list
what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what was read
from each. A place you could not read (a slide that is only a picture, a page whose text did not come out, a file that
opened only in part) is listed as not read and asked for, never filled in from its title or the places around it, and a
figure is never read off a chart or a picture. Ask only for what you could not read and what the file does not show
(speaker notes, the figures behind a chart, an input below that it leaves out), and never ask the founder to paste what
you already read. When the founder cannot answer now, do not wait for them: go on with what was given (a call or step
that waits for an input still waits), invent nothing in a gap's place, and list each ask in brackets under **Needs from
the founder**, the open asks under that name; a live drill waits for the founder.

1. **Today's shares:** the fully diluted shares before the round (every share, granted options and the unissued pool
   included) and the unissued pool today (`0` for none). The founders' own shares, if the founder wants their
   ownership line.
2. **The term sheet's round:** the pre-money, the investment, and the pool it asks for, word for word from the clause.
   The tool reads that percent as the unissued pool after the round, of every post-round share, created in the
   pre-money. If the clause counts granted options in it, asks for an increase of some percent, or puts the pool in the
   post-money, ask what it means rather than pass it: a post-money pool goes to `equity_pool` (the equity-calculator
   skill), which works that timing.
3. **SAFEs and notes:** any that convert in this round. `equity_pool_plan` does not convert them, so its price and
   totals would leave them out: say so, and offer `equity_round` (the equity-calculator skill) or the
   vc-term-sheet-review skill (preview) for the round with them converted.
4. **The hiring plan until the next round:** each hire's role, start month (whole months from today, 0 for now) and
   grant, in shares or as a percent of the fully diluted shares after this round, every hire the same way. Grants
   still owed to people already on the team (a promised grant, a refresh) come out of the same pool: ask for them as
   rows too. A hire with no grant size ("five engineers") is asked for; never supply a typical grant. What one hire is
   worth to the company goes to `equity_employee` (the equity-calculator skill).
5. **The next round:** the month, from today, the founder expects to raise it. Hires starting after it are left out.

A missing input becomes a named gap, written as a bracketed ask: `[the month you expect the next round]`,
`[the grant for the head of sales, in shares or as a percent of the shares after this round]`. Make no call until every
input above is given. The plan holds exactly the founder's grants: it adds no buffer for hires not in the plan unless
the founder gives one as a row of its own, with the founder's own figure.

## Steps

1. **List what the term sheet and the plan state, word for word**: the pre-money, the investment, the pool clause, and
   each hire's role, start month and grant. Quote each figure as stated; never correct it before the call.
2. **Ask for what is missing, by name, in one message** (the inputs above), and make no call until it is given.
3. **Call `equity_pool_plan`** with the founder's figures. Send money and percents as strings, share counts and months
   as whole numbers:

   ```json
   {
     "inputs": {
       "fully_diluted_shares": 10000000,
       "unissued_pool_shares": 1000000,
       "founder_shares": 7000000,
       "pre_money": "16000000",
       "investment": "4000000",
       "requested_pool_percent": "15",
       "next_round_month": 18,
       "hires": [
         {
           "role": "Founding engineer",
           "start_month": 1,
           "grant_shares": 400000
         },
         {
           "role": "Senior engineer",
           "start_month": 4,
           "grant_shares": 250000
         },
         {
           "role": "Senior engineer",
           "start_month": 6,
           "grant_shares": 250000
         },
         { "role": "Head of sales", "start_month": 9, "grant_shares": 350000 },
         { "role": "Designer", "start_month": 12, "grant_shares": 150000 },
         { "role": "VP engineering", "start_month": 24, "grant_shares": 500000 }
       ]
     }
   }
   ```

   The same call from the command line:

   ```
   equity_calculator pool_plan --fully-diluted-shares 10000000 --unissued-pool-shares 1000000 --founder-shares 7000000 --pre-money 16000000 --investment 4000000 --requested-pool-percent 15 --next-round-month 18 --hire "Founding engineer: start-month=1 grant-shares=400000" --hire "Senior engineer: start-month=4 grant-shares=250000" --hire "Senior engineer: start-month=6 grant-shares=250000" --hire "Head of sales: start-month=9 grant-shares=350000" --hire "Designer: start-month=12 grant-shares=150000" --hire "VP engineering: start-month=24 grant-shares=500000"
   ```

   Part of what it prints (Company CP, made up: $4M at a $16M pre-money with a 15% pool asked for, five hires before
   the next round in month 18 and a sixth in month 24):

   ```text
     Target pool after the round (t)                                10.7692%                    15.0000%           4.2308%  plan: G·V/((V + I)(FD - U + G)), the pool holding exactly G; requested: given
     New pool shares (P)                                             400,000               1,076,923.077       676,923.077  (t·FD - (1 - r)U)/(1 - r - t), 0 when not positive: the pool scenario's
     Price per share (p)                                           $1.538462                   $1.444444        $-0.094017  V/(FD + P)
     Ownership: founders                                            53.8462%                    50.5556%          -3.2906%  F / T (founders are among the existing holders)
     Pool left ungranted at the next round                                 0                 676,923.077       676,923.077  U + P - the counted grants' shares; below 0, the pool runs short before the next round
     Effective pre-money                                      $13,846,153.85              $13,000,000.00      $-846,153.85  (FD - U)·p: the holders' shares at the round price
     Flag                                     hires_after_next_round_ignored                                                1 hire starts after month 18 and is left out of the plan: the next round's own pool would cover it
     Flag                                               requested_above_plan                                                The requested pool is larger than the plan's: the difference column shows what the larger pool does to the price, the effective pre-money and who owns what
   ```

   The plan's five hires take a 10.7692% pool after the round; the 15% asked for sets the effective pre-money (the
   existing holders' shares at the round price) at $13,000,000.00 rather than $13,846,153.85, and leaves 676,923.077
   shares ungranted when the next round comes.

4. **Read the result before answering**: both columns' `cap_table`, `target_pool`, `grant_shares`,
   `pool_left_at_next_round` and `founders_ownership`, every figure in `requested_minus_plan`, `hires_counted`,
   `hires_left_out`, every code in `flags`, and `assumptions`. When `plan_fits_current_pool` holds, the plan's pool
   after the round is today's pool, kept whole (its `Ownership: option pool` line), not its target line: quote both. A
   refusal or a tool error is the answer for those inputs: relay its reason and what to change
   (`no_hiring_plan_given`: ask for the plan; `grants_mixed_units`: ask for every grant the same way).
5. **Write the evidence line**, one sentence for the pool conversation, from the founder's plan and the tool's figures
   as printed, and nothing else: the hires counted until the next round's month (by role, from the founder's plan),
   the plan's target pool, and the case the result shows:

   - the requested pool above the plan's (`requested_above_plan`, with a top-up): the effective pre-money in each
     column and the requested pool's shares still ungranted at the next round, as printed;
   - today's pool holding the plan's grants (`plan_fits_current_pool`): say the plan needs no top-up, and quote what
     the requested pool does as printed;
   - the requested pool's shares left below zero: say the ask falls short of the plan before the next round, with the
     printed shortfall. Never leave this case out.

   The line never proposes a pool figure of its own, never says which pool to accept, and names no other company's
   pool.

6. **Follow-ups go to tools too**: a different pool asked for, or a changed plan, by re-running `equity_pool_plan`; the
   pool in the post-money with `equity_pool`; SAFEs and notes converting in the round with `equity_round`.

## Flags

The result's `flags` holds codes only; this table is what each one means for the founder. The text report prints the
same meaning beside each flag; the MCP result does not. None says which pool to accept.

| Flag                             | What it means for the founder                                                                                  | What to prepare                                                                        |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `no_hires_before_next_round`     | No hire in the plan starts on or before the next round's month, so the plan needs no pool before it.           | Check the start months and the next round's month with the founder.                    |
| `hires_after_next_round_ignored` | At least one hire starts after the next round's month and is left out of the plan's pool.                      | Be ready to say that the next round's own pool would cover those hires.                |
| `plan_fits_current_pool`         | The plan's grants fit in today's unissued pool, so the plan needs no top-up; today's pool is kept whole.       | Show the plan's grants against today's unissued pool.                                  |
| `requested_met_by_current_pool`  | Today's unissued pool already meets the requested percent, so the term sheet's pool needs no top-up either.    | Quote both columns as printed; the requested column then makes no new pool shares.     |
| `requested_above_plan`           | The requested pool's target is above the plan's.                                                               | Show the difference column: the price, the effective pre-money and who owns what.      |
| `requested_below_plan`           | The requested pool's target is below the plan's; the pool left line shows whether the plan's grants still fit. | When the pool left is below zero, say the ask runs short of the plan before the round. |

## Answering

Lead with the side-by-side, then the hires, then the evidence line. Use the tool's printed values (`rounded` with its
unit, or the exact fraction when precision matters); never round again or recompute. A value whose unit is `fraction`
is a share of the whole: show it as a percent by moving the decimal point of its `rounded` value two places to the
right, keeping every digit (0.107692 is 10.7692%), which is what the command line's report prints. That is a change of
notation, not a calculation.

1. **Side by side:** a table with "Plan: hires to the next round", "Term sheet: requested pool" and "Requested -
   plan", one row each for the target pool, the new pool shares, the price per share, the founders' ownership (when
   given), the existing holders' and the option pool's ownership, the pool left ungranted at the next round and the
   effective pre-money, every cell as the tool printed it.
2. **The hires:** each hire, counted or left out, as the result lists them, and the counted grants' shares.
3. **The evidence line** from step 5.
4. **Flags,** one line per code in `flags`, with its meaning from the table above.
5. **Assumptions** the answer leans on, quoted from the result with their sources: the pool in the pre-money in both
   columns (`pool_timing`), the plan's pool holding exactly the counted grants (`plan_pool`), the next round's month
   as the cut-off (`next_round_cutoff`), and the grant unit. Say plainly that each is `unverified` where the result
   says so.
6. **Open asks:** every bracketed gap still open.
7. **Close:** this is not investment, legal or tax advice, and the skill does not say which pool to accept; the
   founder's lawyer should confirm what the pool clause means and how the round counts the pool.

## Limits

- Not investment, legal or tax advice. It never says which pool to accept, never proposes a counter figure of its
  own, and never says what a company is worth.
- No arithmetic outside the calculator's tools. Never work out how two of the founder's figures relate (a difference,
  a sum, a ratio or multiple, a share left over, "doubled") in a rewrite, a line or a table cell unless the founder's
  material states it or a tool returned it; quote both figures as stated instead ("from 2,000 to 4,500", never "more
  than doubled"). The requested pool less the plan's comes from the tool's difference column only.
- When neither `equity_pool_plan` nor its command line runs in the session, say so and give no figure in its place:
  never one from the worked example in step 3, which is one made-up company's result, not the founder's.
- Every grant, start month and share count is the founder's. It never supplies a typical grant, a typical pool size
  or a buffer, and it quotes no benchmark pool size: none is applied.
- It never role-plays or speaks as a named investor or firm, and never names a firm as a fit. Asked to "be" the
  investor, it says in one line that it keeps the founder as the user, and offers the investor's likely question (how
  was the pool sized?) as a lens, answered by the founder's plan.
- It works the pool in the pre-money only, and converts no SAFE or note: those go to `equity_pool` and
  `equity_round` (the equity-calculator skill).
- Shares are exact fractions; a real cap table rounds to whole shares, which moves a figure by a share or a cent.
- It works from the founder's text and files the agent can read in this session, looks nothing up, and sends nothing
  anywhere.
