# Eval 3: Company AY, one percent of a big market

A test prompt for the `vc-market-sizing` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. A run passes when it makes no tool call,
names the top-down-only pattern, asks for the bottom-up inputs in one message, and works out no share of the
analyst's figure.

## Prompt

> Our TAM is $50B (an analyst report on global logistics software); we only need 1% of it. Is that credible?

## Expected tool call

None: no `equity_market_sizing` call. There is no segment yet: no buyer, count or price to build from.

## Expected answer

- It quotes the founder's line, "Our TAM is $50B (an analyst report on global logistics software); we only need 1% of
  it.", and says it matches the first pattern: a market size from an analyst figure only, or "if we get 1% of it".
- It quotes the YC pitch guide's reason: "I prefer the bottom up method because it helps you avoid a common top down
  pitfall, which is not narrowing down the customer enough".
- It works out no share of the $50B and states no figure for 1% of it.
- It asks, in one message, for the bottom-up inputs: who buys, as segments, and how many there are with the source;
  what each pays and the months the price covers; the share it can serve today; the customers it plans to win, by
  when, with customers today and the channel; and the report's publisher, year and definition, so the $50B can be
  used as a cross-check.
- It says the review and the call run once those inputs are in, runs no review in this turn, and closes with not
  investment, legal or tax advice.
