# Eval 2: Company RB, a stage with no rate and a commitment with no mark

A test prompt for the `vc-raise-plan` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it makes no call, asks in one
message for the missing rate and the commitment's mark by name as bracketed asks, fills neither with a typical figure
or a guess, and, as the question is about coverage alone, asks for no investor list, tier rules or batch inputs.

## Prompt

> We're raising a $3M seed with no lead yet. One angel is in for $200k. This is our first round, so there are no
> existing investors and no pro rata. Funnel today: 25 intro asks, 6 first meetings, 1 partner meeting. In my
> experience 40% of intro asks become first meetings and 25% of first meetings get to a partner meeting; I've never
> had a partner meeting turn into a term sheet before, so just use whatever is typical. We want 2 term sheets. $900k
> in the bank, $110k a month burn and $10k of revenue, 5 months to raise. How many more investors do we need, and
> when do we start?

## Expected tool call

None: no `equity_raise_pipeline` call. The partner-meeting stage has no rate of the founder's own, and the angel's
$200k is not marked firm or soft.

## Expected answer

- It lists what the founder gave, word for word: a $3M seed, no lead, an angel in for $200k, a first round with no
  existing investors and no pro rata, 25 intro asks, 6 first meetings, 1 partner meeting, 40% and 25% as the
  founder's own rates, 2 term sheets wanted, $900k in the bank, $110k a month burn, $10k of revenue and 5 months to
  raise.
- It asks, in one message, for the two missing inputs by name:
  `[your own rate from a partner meeting to a term sheet]` (the founder's best estimate is the founder's own figure)
  and `[soft or firm, for the angel's $200k]`.
- It declines to use a typical rate: every rate is the founder's, and a benchmark goes in only when the founder gives
  one with its source, so the skill supplies no typical conversion rate.
- It does not decide whether the angel's $200k is firm or soft.
- The question is about coverage alone, so it asks for no investor list, tier rules or batch inputs; it may offer the
  tiers, the batches and the tracker once the coverage is worked.
- It gives no expected term sheets, no targets needed and no start-raising month, and makes no call until both inputs
  are given.
