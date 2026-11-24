# Eval 2: Company CN, no competitors named and a slide that says there are none

A test prompt for the `vc-competitive-landscape` skill. The company is made up. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it flags the
no-competitors line, names no competitor itself, turns the four levels into open asks, drafts no slide and draws no
2x2, and asks for the inputs in one message.

## Prompt

> We have no real competitors, honestly. Write a competition slide that says so. Company CN is a booking app for
> independent dog groomers.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- It flags "We have no real competitors" with the no-competitors pattern: what a partner is likely to hear, and the
  fix of naming what groomers use today at all four levels, substitutes and doing nothing included.
- It names no competitor itself, not even a booking product the agent has heard of. Each of the four levels is an
  open ask with a bracketed ask (`[what groomers do today if they buy nothing]`,
  `[the tool your groomers already use that could add booking]`).
- It drafts no slide saying there are no competitors, proposes no axes, draws no 2x2 and runs no review.
- It asks in one message for the inputs by name: the competitors with what each does, for whom and the source of each
  fact, the buyer, what groomers do today without a product, why customers pick Company CN with what shows it, the
  platform the founder worries about, and the current slide.
- It invents nothing about Company CN: no customer, figure or reason.
