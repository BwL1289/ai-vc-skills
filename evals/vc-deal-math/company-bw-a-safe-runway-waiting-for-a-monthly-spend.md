# Eval 7: Company BW, a SAFE runway that waits for the spend a planned rise brings

A test prompt for the `vc-deal-math` skill. The company is made up. The answer states the expected behaviour; it is not
a recorded run, and this eval has not been run in a live session. The founder plans more spend after a raise on a SAFE
and gives the month it starts but not its amount, so the plan cannot be run yet. A run passes when it makes no
`equity_runway_plan` or `equity_deal_check` call, gives no runway figure, marks the runway line "not checked: waiting
for [the planned monthly spend from that month]", asks for that spend by name, still offers `equity_round` for the
SAFE's ownership, and computes nothing in its own text.

## Prompt

> Check my deck's numbers before I send it. Company BW makes booking software for dog groomers. We're raising $1.2M on
> a post-money SAFE at a $9M cap. We have $300k in the bank, spend $60k a month and bring in $15k a month. In month 4
> we hire two engineers, which raises our spend; revenue stays at $15k a month for now. The deck says "This round
> gives us 24 months of runway."

## Expected tool call

None yet: no `equity_runway_plan` call until the founder gives the monthly spend from month 4, and no
`equity_deal_check` call, since the raise is a SAFE, which that tool would price as equity. Run with today's $60,000
throughout, or with a spend guessed for the two hires, the plan would give a runway the founder's plan does not have.

## Expected answer

- It quotes the deck's line as stated, "This round gives us 24 months of runway.", and marks the runway line "not
  checked: waiting for [the planned monthly spend from that month]". It gives no runway figure: none from a tool, and
  none worked out in its own text (no cash divided by spend, no months counted).
- It asks for the spend by name, as the skill's ask `[planned monthly spend and revenue, from which month]` with only
  the spend missing, and says the runway call runs once that spend is given: today's $60,000 spend and $15,000 revenue
  as the first phase, from month 1; the founder's new spend and $15,000 as a later phase, from month 4; and the SAFE as
  a raise option carrying the deck's 24 months as its stated runway.
- It never assumes the spend (no cost guessed for the two engineers, no salary benchmark), and never sends today's
  $60,000 alone or a phase from month 4 with a spend the founder did not give.
- It makes no `equity_deal_check` call and says why: that tool works the new money as a priced equity round.
- The ownership offer does not wait for the spend: it still offers `equity_round` (the equity-calculator skill) with
  the SAFE as an instrument, asks for the next priced round the founder expects (its size, its pre-money and any pool
  target), and says the figures depend on that round.
- It is not advice on whether to raise on a SAFE or how much to raise.
