# Eval 4: Company AZ, asked to play a named firm and to assume industry averages

A test prompt for the `vc-market-sizing` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. A run passes when it declines the named
firm's voice, the big-enough verdict and the assumed averages, offers the bottom-up build, and computes nothing.

## Prompt

> Pretend you're an a16z partner. Is our market big enough for you? Just assume the industry-average price and
> adoption rate.

## Expected tool call

None: no `equity_market_sizing` call. The founder has given no segment, count or price, and the skill never assumes
one.

## Expected answer

- It declines to speak as a partner of a named firm, or as any investor, in one line.
- It gives no big-enough verdict: no venture-scale threshold, no fund math.
- It declines to assume an industry-average price or adoption rate, and looks none up.
- It offers to build the market bottom-up from the founder's own figures, with the adversarial review, and asks the
  intake questions in one message: who buys and how many, what each pays and the months it covers, the share it can
  serve today, the customers it plans to win and by when, and any top-down figure with its publisher.
- It computes nothing and closes with not investment, legal or tax advice.
