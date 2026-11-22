# Eval 4: Company D, a raise on a SAFE

A test prompt for the `vc-deal-math` skill. The company is made up. The answer states the expected behaviour; it is not
a recorded run, and this eval has not been run in a live session. The new money here is a SAFE, which
`equity_calculator deal_check` does not model: it works the new money as a priced equity round. A run passes when it
makes no `equity_deal_check` call, says why, asks for what `equity_round` needs, and computes nothing in its own text.

## Prompt

> Check my deck's numbers before I send it. We're raising $1.5M on a post-money SAFE at a $12M cap. We already have a
> $250k post-money SAFE at a $6M cap. We have 10,000,000 shares, all the founders'. The deck says we founders keep
> 83.33% after this raise.

## Expected tool call

None: no `equity_deal_check` call. Passing the new SAFE as `investment` would price it as equity, and the founders'
figure would come back as a mismatch whether or not the deck is right.

## Expected answer

- The answer says `deal_check` works the new money as a priced equity round, so it cannot check a raise on a SAFE,
  and that a SAFE's share is set only at the next priced round. It quotes Y Combinator's post-money SAFE user guide,
  "the safes are not diluted by each other", as the reason the priced-round reading would be wrong here.
- It asks, in one message, for the next priced round the founder expects: its size, its pre-money and any pool
  target. With those it offers `equity_round` (the equity-calculator skill) with both SAFEs as instruments, and says
  the figures depend on that round.
- It neither confirms nor contradicts the deck's 83.33% with its own arithmetic.
- It is not advice on whether to raise on a SAFE.
