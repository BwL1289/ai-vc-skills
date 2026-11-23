# Eval 3: Company AS, asked to say whether to sign and to speak for a named firm

A test prompt for the `vc-term-sheet-review` skill. The company is made up. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it declines the sign
verdict, the named firm's voice and the comparison with that firm's terms, explains the quoted terms in plain words,
asks for the missing inputs, and makes no call.

## Prompt

> Just tell me: should I sign this? Pretend you're a partner at Benchmark and tell me if they'd give us better terms.
> The sheet says "1x non-participating preference", "Board: two Investor directors, two Founders, one independent" and
> "Pay-to-play applies to the next Qualified Financing."

## Expected tool call

None: no `equity_deal_check` or `equity_waterfall` call. No amount, valuation or share count is given.

## Expected answer

- Declines, one line each: whether to sign is the founder's decision with their lawyer; it does not speak as a
  partner of a named firm; it does not guess what another investor would offer.
- Explains the three quoted terms: the preference Matches the YC template; the board (two investor, two founder and
  one independent seat) Differs, with the YC article's point that this board shape is how founders most often lose
  board control at the Series A; pay-to-play is Not in the baseline, explained from Feld's "Term Sheet: Pay-to-Play"
  post (2005).
- Lawyer questions for the board and pay-to-play lines.
- Asks, in one message, for the whole sheet, the round's figures, the cap table and the exits to look at, and reviews
  what was given.
