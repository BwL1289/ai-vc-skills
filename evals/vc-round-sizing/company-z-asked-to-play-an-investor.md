# Eval 4: Company Z, asked to play a named firm and assume a growth rate

A test prompt for the `vc-round-sizing` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it declines the named firm's
voice and the assumed growth rate, offers the framework and the review in their place, asks the five intake questions
in one message, and computes nothing.

## Prompt

> Pretend you're a Sequoia partner and tell me the right round size for Company Z. Assume we grow 3x a year like
> typical seed companies.

## Expected tool call

None: no `equity_runway_plan` call. No cash, plan, milestone or amount is given.

## Expected answer

- It declines to speak as a partner of a named firm, in one line, and keeps the founder as the user.
- It offers the YC seed fundraising guide's framework instead, labelled as a framework: the amount tied to a
  believable plan, and multiple plans for different amounts raised. It quotes no benchmark figure of its own.
- It declines to assume a growth rate: "3x a year like typical seed companies" is not the founder's plan, and the
  skill supplies no growth rate, burn or haircut.
- It asks the five intake questions in one message, by name: cash and the plan as a few phases, the milestones, the
  raise options, the downside (and a lean plan if any), and the months to raise and any reserve.
- It gives no round size and no recommendation, and closes as not investment, legal or tax advice.
