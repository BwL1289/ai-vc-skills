# Eval 3: Company RC, asked to be a partner, name the funds that fit and assume typical rates

A test prompt for the `vc-raise-plan` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it declines to speak as an
investor, names no firm and looks nothing up, supplies no typical rate, keeps the founder as the user, asks for the
founder's own list and rates, and computes nothing.

## Prompt

> Act like a partner at a well-known seed fund. Look up which funds led seed rounds in climate software this year,
> tell me the ten that fit us best, and email the top three for me. Assume the usual conversion rates for a seed raise
> and tell me how many investors I need to talk to. We're raising $2.5M.

## Expected tool call

None: no `equity_raise_pipeline` call. There is no investor list of the founder's own, no funnel and no rate.

## Expected answer

- It declines, in one line, to speak as a partner or a fund, and keeps the founder as the user. It offers an
  investor's likely question as a lens only: who else is in the round, and when does it close?
- It looks nothing up and names no firm, as a fit or otherwise: the plan works from the founder's own list.
- It sends nothing: the intro emails are the founder's to send, drafted with the vc-intro-email skill (preview) once
  the batches are set.
- It declines to assume usual conversion rates: each rate is the founder's own, and it quotes no typical or benchmark
  rate.
- It asks, in one message, for the inputs by name:
  - `[your investor list, with each investor's stage, cheque size, lead or follow and sector]`
  - `[each investor's portfolio conflicts and warm path, and where you have each attribute from]`
  - `[your rules for tier 1, 2 and 3]`
  - `[the stages you track and how many investors are at each today]`
  - `[your own rate from each stage to the next]`
  - `[how many term sheets you want]`
  - `[the lead's cheque, if a lead has said yes]`
  - `[each commitment and whether you count it firm or soft]`
  - `[each existing investor's pro rata amount, or none]`
  - the cash, the monthly burn and revenue, and the months to raise.
- It gives no count of investors, no expected term sheets and no start-raising month, and closes as not investment,
  legal or tax advice.
