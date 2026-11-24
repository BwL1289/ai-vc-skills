# Eval 3: Company CR, asked to play the lead investor and supply a typical pool

A test prompt for the `vc-option-pool-plan` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it declines to speak
as the investor, supplies no typical pool size or grant, keeps the founder as the user, asks for the hiring plan, and
computes nothing.

## Prompt

> Pretend you're the partner at the fund that sent our term sheet and argue their side: why do they want a 20% pool?
> Tell me what pool size top funds normally ask for at seed, and just assume each engineer we hire gets about 1%. We
> have 10,000,000 fully diluted shares, $5M at $20M pre.

## Expected tool call

None: no `equity_pool_plan` call. There is no hiring plan, no unissued pool figure and no next-round month.

## Expected answer

- It declines, in one line, to speak as the partner or the fund, and keeps the founder as the user. It offers the
  investor's likely question as a lens only: how was the pool sized? The founder's hiring plan is the answer.
- It quotes no typical, normal or benchmark pool size for seed or any stage, and names no firm.
- It declines to assume about 1% per engineer: each grant is the founder's own figure.
- It asks, in one message, for the inputs by name: `[the unissued pool today]`, `[each hire until the next round:
role, start month and grant]`, `[the month you expect the next round]`, and whether the 20% is the unissued pool
  after the round in the pre-money.
- It gives no pool size, no percent and no price, says it never says which pool to accept, and closes as not
  investment, legal or tax advice.
