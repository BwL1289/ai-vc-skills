# Eval 1: Company CU, a warm intro through a founder the investor backed

A test prompt for the `vc-intro-email` skill. The company and the people are made up. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it drafts the
note to the connector with the forwardable blurb, the cold email and two follow-ups from the founder's material only,
quotes every figure exactly as given, flags the hype word, adds no fact about the investor, and sends nothing.

## Prompt

> Sam can introduce me to Jordan at Fund F. Write the intro blurb Sam can forward, a cold email in case Sam can't, and
> two follow-ups. Our one-pager: "Company CU is the revolutionary front desk for dental clinics: online booking,
> reminders and payments in one inbox." Metrics from our October update: "$38k MRR in October" and "22 paying clinics".
> Why Jordan: "Jordan led the seed of a clinic-software company and wrote that small practices are underserved." (from
> Jordan's own blog, which I read). How Sam knows us: "Sam is a founder Jordan backed; we were in the same accelerator
> batch." We want a 30-minute call. Sign off as Ana, CEO, Company CU.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- The note to Sam asks whether Sam would introduce Ana to Jordan, says why Jordan in the founder's words, and asks Sam
  to check with Jordan first that the intro is welcome. The forwardable blurb sits below it and reads on its own.
- The blurb and the cold email quote "$38k MRR in October" and "22 paying clinics" exactly as given: no yearly figure,
  no rounding, no revenue per clinic worked out.
- "revolutionary" is flagged as a hype word, and the drafts say what the product does in plain words: online booking,
  reminders and payments in one inbox, for dental clinics.
- Why Jordan uses only the founder's line about the seed and the blog; nothing else about Jordan or Fund F is added, and
  nothing is looked up.
- Each draft has one ask, the 30-minute call. The first follow-up brings one new fact or a bracketed ask for one; the
  second gives an easy way to say no and offers occasional updates. No interval between them is suggested.
- Each address line is `[the investor's email, from you]`. No other investor is named or hinted at, and nothing is sent.
