# Eval 1: Company CP, "the term sheet asks for a 15% pool"

A test prompt for the `vc-option-pool-plan` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is
pasted from what `equity_calculator pool_plan` printed for these inputs; none is typed by hand. A run passes when it
makes the one tool call below (field order free, money and percents as strings), shows the plan, the requested pool
and the difference side by side as printed, writes one evidence line from the founder's plan, never says which pool
to accept, and computes nothing in its own text.

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
