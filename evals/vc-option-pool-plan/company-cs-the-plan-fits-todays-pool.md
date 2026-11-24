# Eval 4: Company CS, grants as percents that fit today's pool

A test prompt for the `vc-option-pool-plan` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is
pasted from what `equity_calculator pool_plan` printed for these inputs; none is typed by hand. A run passes when it
makes the one tool call below with every grant as a percent, says the plan needs no top-up because today's pool holds
it, quotes the plan's pool after the round from the option pool line rather than its target line, shows the requested
pool's top-up and difference as printed, and never says which pool to accept.

## Prompt

> We're raising $3M at a $12M pre-money and the lead wants a 15% pool after the round, in the pre-money. We have
> 10,000,000 fully diluted shares, 1,500,000 of them an unissued pool. Our plan until the next round in month 15:
> a backend engineer (month 2) and a frontend engineer (month 3) at 1% each, a support lead in month 6 at 0.5%, a
> head of product in month 10 at 2%, and a head of finance in month 20 at 1%. Grants are percents of the fully diluted
> shares after this round. Do we even need a top-up?

## Expected tool call

`equity_pool_plan`, once:

```json
{
  "inputs": {
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 1500000,
    "pre_money": "12000000",
    "investment": "3000000",
    "requested_pool_percent": "15",
    "next_round_month": 15,
    "hires": [
      { "role": "Backend engineer", "start_month": 2, "grant_percent": "1" },
      { "role": "Frontend engineer", "start_month": 3, "grant_percent": "1" },
      { "role": "Support lead", "start_month": 6, "grant_percent": "0.5" },
      { "role": "Head of product", "start_month": 10, "grant_percent": "2" },
      { "role": "Head of finance", "start_month": 20, "grant_percent": "1" }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Hire 5: Head of finance, from month 20                          1.0000%                                                left out: starts after month 15, the next round
  Shares the counted grants take                                  562,500                 588,461.538                    the counted grants' percents of this column's T
  Target pool after the round (t)                                 4.5000%                    15.0000%          10.5000%  plan: the counted grants' percents added up; requested: given
  New pool shares (P)                                                   0                 461,538.462       461,538.462  (t·FD - (1 - r)U)/(1 - r - t), 0 when not positive: the pool scenario's
  Price per share (p)                                           $1.200000                   $1.147059        $-0.052941  V/(FD + P)
  Ownership: existing holders                                    68.0000%                    65.0000%          -3.0000%  shares / T
  Ownership: option pool                                         12.0000%                    15.0000%           3.0000%  shares / T
  Pool left ungranted at the next round                           937,500               1,373,076.923       435,576.923  U + P - the counted grants' shares; below 0, the pool runs short before the next round
  Effective pre-money                                      $10,200,000.00               $9,750,000.00      $-450,000.00  (FD - U)·p: the holders' shares at the round price
  Unissued pool already meets it                                      yes                          no                    then P = 0: no top-up
  Flag                                     hires_after_next_round_ignored                                                1 hire starts after month 15 and is left out of the plan: the next round's own pool would cover it
  Flag                                             plan_fits_current_pool                                                The plan's grants fit in today's unissued pool, so the plan needs no top-up
  Flag                                               requested_above_plan                                                The requested pool is larger than the plan's: the difference column shows what the larger pool does to the price, the effective pre-money and who owns what
```

## Expected answer

- It asks for nothing more: every grant is given the same way, as a percent of the shares after this round, and the
  15% is the unissued pool after the round in the pre-money. It passes no `founder_shares`, as none was given, and
  says the founders' own line needs their share count.
- `plan_fits_current_pool` in its words: the four hires counted by month 15 take 562,500 shares (4.5000% as their
  target), which today's 1,500,000-share pool holds, so the plan needs no top-up (0 new pool shares). It quotes the
  plan's pool after the round from the option pool line, 12.0000%, today's pool kept whole, and says its 4.5000% is
  the plan's target, not the pool after the round.
- The requested column as printed: 461,538.462 new pool shares, the price $1.147059 against $1.200000 ($-0.052941),
  the existing holders 65.0000% against 68.0000% (-3.0000%), the effective pre-money $9,750,000.00 against
  $10,200,000.00 ($-450,000.00), and 1,373,076.923 shares ungranted at the next round against 937,500.
- The head of finance in month 20 is left out (`hires_after_next_round_ignored`).
- One evidence line from the founder's plan and those figures only: the hires until month 15 fit in today's pool with
  no top-up, and the 15% asked for sets the effective pre-money at $9,750,000.00 against $10,200,000.00.
- It never says which pool to accept, proposes no pool figure of its own and quotes no typical pool size; it closes
  as not investment, legal or tax advice.
- It adds, subtracts or divides none of the tool's figures in its own text.
