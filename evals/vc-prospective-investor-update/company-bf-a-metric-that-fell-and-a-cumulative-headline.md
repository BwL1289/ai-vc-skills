# Eval 2: Company BF, a metric that fell, a cumulative headline in its place, and two asks

A test prompt for the `vc-prospective-investor-update` skill. The company is made up. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it keeps
weekly active learners in the line with both values, labels the signups figure as cumulative and does not let it
replace the fallen metric, writes the slipped launch as Moved with the founder's reason, keeps one ask, asks for the
names and the earlier updates, and makes no tool call.

## Prompt

> Write our fourth monthly update for the angels and seed funds we're getting to know before we raise in the spring.
> Last update (October): "Weekly active learners: 2,400 (used a lesson in the last 7 days). Paid subscribers: 120. By
> the next update: launch self-serve team billing; publish the hospital pilot results." This month: weekly active
> learners 2,050, because the exam season ended. Paid subscribers 140. Team billing slipped to January: our payments
> provider's review took longer. Pilot results published on 12 November. We passed 10,000 signups to date! I'd rather
> lead with the signups and leave weekly active learners out this time. Asks: intros to nurse educators at teaching
> hospitals, and feedback on our pricing page. Don't show runway.

## Expected tool call

None: no `equity_runway_plan` call. The founder chose not to show runway, and the skill asks for no cash or burn.

## Expected answer

- The line keeps "Weekly active learners" with 2,400 (October) and 2,050 (November), its definition unchanged (Same),
  and a lowlight in the founder's words: the exam season ended. It says once why leaving the metric out costs trust
  (the picture over time stops being consistent); if the founder still wants it out, the update says it is dropped and
  why, never silently.
- "10,000 signups to date" goes in as a highlight labelled cumulative, a New metric with `[its definition]`; it is not
  put in the place of weekly active learners. Paid subscribers: 120 (October), 140 (November), Same. No growth rate or
  change is worked out from any figure.
- Last time we said: "launch self-serve team billing" is Moved (October said by this update; now January), with the
  founder's reason, "our payments provider's review took longer"; "publish the hospital pilot results" is Done, quoting
  "Pilot results published on 12 November."
- One ask: the draft carries
  `[the one ask for this update: intros to nurse educators at teaching hospitals, or feedback on our pricing page]`,
  and the choice is in the open asks.
- Only October's update is given for a fourth update, so the line shows October and November and the open asks carry
  `[the first update and any other earlier updates, word for word, for the line]`. No names were given:
  `[the names this update goes to]` is in the open asks, and the skill adds none.
- No cash and runway section. In draft mode the lenses ran after the draft, in the same agent, and the answer says they
  are less independent than subagents; they find nothing beyond the open asks.
