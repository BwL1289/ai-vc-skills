# Eval 3: Company U, polish over a generic core

A test prompt for the `vc-taste-check` skill. The company is made up. This eval states the expected behaviour; it is not
a recorded run, and it has not been run in a live session. A run passes when the flags fire on the founder's own lines,
the copying objection survives because the founder's own words ground it, nothing goes in the deck, and no NO is
invented.

## Prompt

> Is our brand generic? Company U sells expense software for small law firms. Homepage: "Seamless, intuitive and
> powerful expense management that empowers modern firms." D1: "We redesigned every screen to feel premium and
> delightful." D2: "We added an AI assistant because every competitor launched one this year." D3: "We keep it
> simple." On what we said no to: "Honestly we said yes to most requests; customers asked for a lot and we built it."

## Expected tool call

None: no `equity_deal_check` call. The prompt states no deal terms, and the skill calls no calculator tool.

## Expected answer

- "Seamless, intuitive and powerful expense management that empowers modern firms." is flagged AI-sounding, with a fix
  that asks for the customer's words for the job; the answer does not say or imply that a model wrote it.
- "We redesigned every screen to feel premium and delightful." is flagged Taste-washed: no cut or trade-off in the
  decisions sits behind it.
- "We added an AI assistant because every competitor launched one this year." is flagged Copycat, and Scope as a
  feature added for a trend. The distinctiveness lens's objection to it survives the refute pass as Kept, because the founder's own line gives other
  companies doing it as the reason; it is not dropped as an outside fact.
- "We keep it simple." is flagged Generic, and "Honestly we said yes to most requests; customers asked for a lot and we
  built it." is flagged Generic: no trade-off was faced. The first open ask is the list of what the founder
  turned down.
- The survivors appear in the ranked table with their quotes. Every decision is placed Not yet; nothing goes in the
  deck. No NO, customer or reason is invented, and no score is given.
