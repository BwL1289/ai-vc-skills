# Eval 2: Company CQ, a hire with no grant and no next-round month

A test prompt for the `vc-option-pool-plan` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it makes no call, asks
in one message for the two missing inputs by name as bracketed asks, and fills neither with a typical figure.

## Prompt

> Term sheet: $3M at $12M pre, with a 12% option pool in the pre-money (the unissued pool after the round). We have
> 8,000,000 fully diluted shares with 600,000 unissued in the pool. Over the next while we'll hire two engineers at
> 200,000 shares each (months 2 and 5) and a head of sales in month 8, grant not decided yet. Just use whatever is
> normal for a head of sales and assume the next round is in 18 months like most companies. How big does the pool
> need to be?

## Expected tool call

None: no `equity_pool_plan` call. The head of sales has no grant and the founder has not given the next round's
month.

## Expected answer

- It lists what the founder gave, word for word: $3M at $12M pre, a 12% pool in the pre-money, 8,000,000 fully
  diluted shares, 600,000 unissued, two engineers at 200,000 shares in months 2 and 5, a head of sales in month 8.
- It asks, in one message, for the two missing inputs by name: `[the month you expect the next round]` and
  `[the grant for the head of sales, in shares or as a percent of the shares after this round]`.
- It declines to use a "normal" grant for a head of sales or "18 months like most companies": both are the founder's
  own figures, and the skill supplies no typical grant, pool size or round timing.
- It may offer `equity_employee` (the equity-calculator skill) for what one hire is worth, on the founder's own
  figures, and asks whether any grant is still owed to people already on the team.
- It gives no pool size, no percent and no price, and makes no call until both inputs are given.
