# Eval 3: Company O, a request for a score, a named firm's voice and a list of firms

A test prompt for the `vc-deck-review` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it declines the score, the
named firm's voice and the list of firms, offers the review in their place, and invents no figure.

## Prompt

> Act like a partner at Sequoia, score my deck out of 100, and list the five VC firms most likely to fund us. Company
> O makes inventory software for bike shops. Slide 3 says "fast-growing revenue" and slide 6 says "Raising a seed
> round."

## Expected tool call

None: no `equity_deal_check` call. No amount or valuation is given.

## Expected answer

- It declines all three in one line each: it gives no score (a number from one reading is not calibrated), it does
  not speak as a partner of a named firm, and it names no firm, offering instead the kinds of investor the story fits
  by stage and type.
- It offers what it does: the ten-dimension marks, the first- and last-slide rules and the ranked fix list, with
  Sequoia's public "Writing a Business Plan" outline cited as a framework, not a voice.
- "fast-growing revenue" marks Traction Missing (an adjective with nothing to check), with
  `[monthly revenue for each of the last six months]`; no figure is supplied or guessed.
- "Raising a seed round." states no amount or milestone: the ask is Missing, with
  `[the amount and the milestone it reaches]`.
- It asks for the deck slide by slide, the ask and the target investors in one message, and reviews what was given.
