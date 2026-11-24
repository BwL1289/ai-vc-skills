# Eval 1: Company CP, "the term sheet asks for a 15% pool"

A test prompt for the `vc-option-pool-plan` skill. The company is made up. "Expected answer" states the expected
behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24). Every figure under
"Expected answer" is pasted from what `equity_calculator pool_plan` printed for these inputs; none is typed by hand. A
run passes when it makes the one tool call below (field order free, money and percents as strings), shows the plan, the
requested pool and the difference side by side as printed, writes one evidence line from the founder's plan, never says
which pool to accept, and computes nothing in its own text. The verdict is Pass when every clause of that sentence is
met, Partial when exactly one clause is missed or met only in part, and Fail when two or more are missed; a shortfall
against the other points of the expected answer is noted but does not change the verdict. The recorded run is a Pass
with shortfalls, which its grader called partial overall. The skill was changed after that run (see "Recorded answer").

## Prompt

> Our term sheet is $4M at a $16M pre-money, and it asks for "an available option pool of 15% of the fully diluted
> capitalization after the financing, included in the pre-money valuation". We have 10,000,000 fully diluted shares
> today, 1,000,000 of them unissued pool, and the two founders hold 7,000,000; no SAFEs or notes, and no grants owed
> to anyone already on the team. We expect to raise
> the next round in month 18. Hiring plan: a founding engineer in month 1 (400,000 shares), senior engineers in months
> 4 and 6 (250,000 each), a head of sales in month 9 (350,000), a designer in month 12 (150,000) and a VP of
> engineering in month 24 (500,000). Is 15% more than we need?

## Expected tool call

`equity_pool_plan`, once:

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
      { "role": "Founding engineer", "start_month": 1, "grant_shares": 400000 },
      { "role": "Senior engineer", "start_month": 4, "grant_shares": 250000 },
      { "role": "Senior engineer", "start_month": 6, "grant_shares": 250000 },
      { "role": "Head of sales", "start_month": 9, "grant_shares": 350000 },
      { "role": "Designer", "start_month": 12, "grant_shares": 150000 },
      { "role": "VP engineering", "start_month": 24, "grant_shares": 500000 }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Hire 6: VP engineering, from month 24                           500,000                                                left out: starts after month 18, the next round
  Shares the counted grants take                                1,400,000                   1,400,000                    G: the counted grants added up
  Target pool after the round (t)                                10.7692%                    15.0000%           4.2308%  plan: G·V/((V + I)(FD - U + G)), the pool holding exactly G; requested: given
  New pool shares (P)                                             400,000               1,076,923.077       676,923.077  (t·FD - (1 - r)U)/(1 - r - t), 0 when not positive: the pool scenario's
  Price per share (p)                                           $1.538462                   $1.444444        $-0.094017  V/(FD + P)
  Ownership: existing holders                                    69.2308%                    65.0000%          -4.2308%  shares / T
  Ownership: founders                                            53.8462%                    50.5556%          -3.2906%  F / T (founders are among the existing holders)
  Pool left ungranted at the next round                                 0                 676,923.077       676,923.077  U + P - the counted grants' shares; below 0, the pool runs short before the next round
  Effective pre-money                                      $13,846,153.85              $13,000,000.00      $-846,153.85  (FD - U)·p: the holders' shares at the round price
  Flag                                     hires_after_next_round_ignored                                                1 hire starts after month 18 and is left out of the plan: the next round's own pool would cover it
  Flag                                               requested_above_plan                                                The requested pool is larger than the plan's: the difference column shows what the larger pool does to the price, the effective pre-money and who owns what
```

## Expected answer

- It asks for nothing more: the clause says the pool is the available (unissued) pool after the financing, in the
  pre-money, which is how the tool reads `requested_pool_percent`; there are no SAFEs or notes to convert and no grants
  owed to the team.
- The side-by-side, as printed: the target pool 10.7692% (plan) against 15.0000% (requested), 4.2308% in the
  difference column; new pool shares 400,000 against 1,076,923.077; the price per share $1.538462 against $1.444444
  ($-0.094017); the founders 53.8462% against 50.5556% (-3.2906%); the pool left ungranted at the next round 0 against
  676,923.077; the effective pre-money $13,846,153.85 against $13,000,000.00 ($-846,153.85).
- The hires: five counted by month 18 (1,400,000 shares of grants), and the VP of engineering in month 24 left out,
  with `hires_after_next_round_ignored` in its words (the next round's own pool would cover that hire).
- One evidence line from the founder's plan and those figures only, for example: "Our hires until the next round in
  month 18 (a founding engineer, two senior engineers, a head of sales and a designer) take a 10.7692% pool after the
  round; at the 15% asked for, the effective pre-money is $13,000,000.00 against $13,846,153.85 on our plan, and
  676,923.077 shares are still ungranted when the next round comes."
- `requested_above_plan` with its meaning from the flag table, and the assumptions it leans on, each named
  `unverified` where the result says so: `pool_timing`, `plan_pool` and `next_round_cutoff`.
- It never says which pool to accept, proposes no pool figure of its own and quotes no typical pool size; it closes
  as not investment, legal or tax advice, with the pool clause's meaning for the founder's lawyer to confirm.
- It adds, subtracts or divides none of the tool's figures in its own text.

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with the plugin loaded from this repository and no user settings. This
is the second attempt, made minutes after the first, which reached an out-of-date build of the calculator's server with
no `equity_pool_plan` and is not graded: it tried the command line (not allowed in that session), then built the plan
and difference columns from the skill's worked example, "the calculator's reference output for these same inputs, which
I did not re-run". The answer is shown whole.

**Pass, with shortfalls against the expected answer (its grader called the run partial overall).** It met every clause
of the pass sentence above. It made the one `equity_pool_plan` call with the expected arguments and no other; it showed
the plan, the requested pool and the difference side by side with every cell as the tool printed it, adding the existing
holders' and the option pool's rows from the same result; it wrote one evidence line from the founder's plan and the
tool's figures; it never said which pool to accept; and it computed nothing in its own text. One cell is borderline: the
investor's row reads "none" in the difference column, where the tool prints no difference, a comparison of two equal
printed values that gives no figure. It also counted the five hires and left out the VP of engineering as the result
lists them. Short of the expected answer: it named neither flag code (`hires_after_next_round_ignored`,
`requested_above_plan`) and none of the assumptions' keys, and it never said `unverified`, though the result marks the
pool's timing, the plan's pool and the next round's cut-off so; it gave their meanings in its own words only, where the
skill's answering steps already ask for each code and each mark. Since this run, when neither the tool nor its command
line runs, the skill says so and gives no figure, never one from its worked example. The eval has not been run again.

> **Yes, on your plan: the five hires before month 18 take a 10.7692% pool after the round, against the 15% the term sheet asks for.** The extra 4.2308 points come out of the existing holders, because the pool is created in the pre-money.
>
> |                                                 | Plan: hires to month 18 | Term sheet: 15% pool | Requested − plan |
> | ----------------------------------------------- | ----------------------- | -------------------- | ---------------- |
> | Target pool after the round                     | 10.7692%                | 15.0000%             | 4.2308%          |
> | New pool shares                                 | 400,000                 | 1,076,923.077        | 676,923.077      |
> | Price per share                                 | $1.538462               | $1.444444            | −$0.094017       |
> | Founders' ownership                             | 53.8462%                | 50.5556%             | −3.2906%         |
> | Existing holders' ownership (founders included) | 69.2308%                | 65.0000%             | −4.2308%         |
> | Option pool's ownership                         | 10.7692%                | 15.0000%             | 4.2308%          |
> | Investor's ownership                            | 20.0000%                | 20.0000%             | none             |
> | Pool left ungranted at the next round           | 0                       | 676,923.077          | 676,923.077      |
> | Effective pre-money                             | $13,846,153.85          | $13,000,000.00       | −$846,153.85     |
>
> **The hires**
>
> - **Counted (1,400,000 shares):** founding engineer in month 1 (400,000), senior engineers in months 4 and 6 (250,000 each), head of sales in month 9 (350,000) and designer in month 12 (150,000).
> - **Left out:** the VP of engineering in month 24 (500,000) starts after the next round, so that round's own pool would cover the grant.
>
> **Evidence line for the pool conversation**
>
> "Our plan to the next round in month 18 is five hires (a founding engineer, two senior engineers, a head of sales and a designer) taking 1,400,000 shares, which is a 10.7692% pool after the financing. At 15% the effective pre-money is $13,000,000.00 rather than $13,846,153.85, and 676,923.077 pool shares are still ungranted when the next round comes."
>
> **What the comparison leans on**
>
> - **No buffer:** the plan column holds exactly your five grants, so it ends at zero. An unplanned hire, a refresh grant, a larger offer to close a candidate, or the VP of engineering arriving early would all need more pool.
> - **Month 18 cut-off:** if the next round slips to month 24 or later, the VP's 500,000 shares would also come out of this pool.
> - **Clause reading:** I read "available option pool of 15%" as the unissued pool after the round, as a share of all post-round shares, created in the pre-money. Your lawyer should confirm that reading and how the round counts the pool.
> - **Share rounding:** share counts are exact fractions; a real cap table rounds to whole shares, which moves a figure by a share or a cent.
>
> This is not investment, legal or tax advice, and it does not say which pool to accept.
