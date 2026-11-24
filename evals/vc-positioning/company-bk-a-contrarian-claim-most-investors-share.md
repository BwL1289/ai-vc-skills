# Eval 5: Company BK, a "contrarian" insight most investors already hold

A test prompt for the `vc-positioning` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. The founder's slide calls a trend most investors
already expect a contrarian insight, and the founder's own competition slide shows others acting on it. A run passes
when the Is it really contrarian? lens objects to the slide-2 line as a view most investors already hold, that
objection survives the refute pass, and the answer writes no contrarian belief the founder did not state, asking for
one once with the two prompts instead.

## Prompt

> What do we believe that others don't? I want our contrarian slide to hold up before we pitch seed funds next month.
> Opening line: "Company BK writes claim reports for independent insurance adjusters." Slide 2, Our contrarian insight:
> "Insurance claims work is moving from paper to software." Slide 3, Problem: "An adjuster spends more time writing
> each claim report than inspecting the damage." Slide 4, Competition: "Every large insurer now runs claims on its own
> software, and four funded startups sell claims software to insurers." Slide 5, Team: "Our CEO worked 9 years as an
> independent adjuster; our CTO built document tools at a legal-software company."

## Expected tool call

None: no `equity_deal_check` call. No ask figures are given, so the ask is an open ask, not a calculator call.

## Expected answer

- The Is it really contrarian? lens objects to the slide-2 line, quoted word for word, "Insurance claims work is moving
  from paper to software.": a partner is likely to read it as a trend most investors already expect, not a belief most
  of them would reject, and the founder's own slide 4, "Every large insurer now runs claims on its own software, and
  four funded startups sell claims software to insurers.", shows others already acting on it. The line also names no
  one who disagrees and no evidence that it is right.
- That objection survives the refute pass. No other line of the material names anyone who rejects the belief or says
  why they are wrong, and the slide-4 line supports the objection rather than answering it. The refute pass judges it
  on a partner's likely reading of the line and does not drop it as resting on an outside fact.
- Row 12 is marked Needs work, quoting the slide-2 line. The Contrarian insight block quotes that line as stated and
  lists the lens's surviving objection.
- The answer writes no contrarian belief the founder did not state. No rewrite claims, for instance, that independent
  adjusters rather than insurers are the real buyer, or that report writing is the part of claims work others ignore,
  though slides 3 and 5 might seem to point there. Any rewrite uses only the founder's lines and leaves the belief
  itself as the bracketed ask `[the belief about this market that most investors would reject today, in one sentence]`.
- It asks once, in one message, with the two prompts: what the founder believes about this market that most investors
  would reject, and what they saw first-hand (the CEO's 9 years as an independent adjuster is the place to look) that
  others have not. The prompts are one item in the open asks, with the bracketed ask, and the Contrarian insight block
  points to it rather than asking again. It says not every good company needs a contrarian story, so cutting the slide
  is an option.
- "9 years" and "four funded startups" are quoted as stated; nothing is computed. The missing ask, metrics and
  market go to the open asks.
- It invents nothing about Company BK: no customers, pilots, figures or market size. The lens is named by its test and
  writes in the third person, never as a named investor.
