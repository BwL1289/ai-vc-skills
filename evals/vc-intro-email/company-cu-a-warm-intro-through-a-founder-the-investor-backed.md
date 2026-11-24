# Eval 1: Company CU, a warm intro through a founder the investor backed

A test prompt for the `vc-intro-email` skill. The company and the people are made up. "Expected answer" states the
expected behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24). A run
passes when it drafts the note to the connector with the forwardable blurb, the cold email and two follow-ups from the
founder's material only, quotes every figure exactly as given, flags the hype word, adds no fact about the investor, and
sends nothing. The verdict is Pass when every clause of that sentence is met, Partial when exactly one clause is missed
or met only in part, and Fail when two or more are missed; a shortfall against the other points of the expected answer
is noted but does not change the verdict. The recorded run is a Pass with one shortfall, which its grader called partial
overall; the skill was not changed after it.

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
- The cold email's and the follow-ups' address lines are `[the investor's email, from you]`, the note to Sam's is
  `[the connector's email, from you]`, and the blurb has none. No other investor is named or hinted at, and nothing is
  sent.

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass, with a shortfall against the expected answer (its grader called the run partial overall).** It met every clause
of the pass sentence above. It drafted the note to Sam with the forwardable blurb under it, the cold email and the two
follow-ups from the founder's material only; quoted "$38k MRR in October" and "22 paying clinics" exactly, with no
yearly figure, no rounding and no figure per clinic; dropped "revolutionary" as a hype word and said what the product
does in plain words; added nothing about Jordan or Fund F beyond the founder's line, looking nothing up; and sent
nothing. Its only tool call loaded the skill. Each draft has the one ask, the first follow-up asks for one new fact in
brackets, and the second gives an easy no and offers occasional updates, with no interval suggested. Short of the
expected answer: the note offers Sam the check instead of asking for it ("If you'd rather check with Jordan first that
the intro is welcome, please do."), where the expected answer has the note ask Sam to check with Jordan first. Its
address lines name Sam and Jordan (`[Sam's email, from you]`) rather than the connector and the investor, which comes to
the same. The skill already says the note asks for that check, so this run led to no change in it, and the eval has not
been run again.

> Drafts are below. Two things differ from what you gave me: I dropped "revolutionary" from the one-liner, and I left Sam out of the cold email until Sam agrees to be named.
>
> ## Note to Sam (blurb goes under it)
>
> **To:** [Sam's email, from you] > **Subject:** Intro to Jordan at Fund F?
>
> Hi Sam,
>
> Would you be open to introducing me to Jordan at Fund F? Jordan led the seed of a clinic-software company and wrote that small practices are underserved, which is exactly who we sell to.
>
> If you'd rather check with Jordan first that the intro is welcome, please do. I've put a blurb below that you can forward as it stands.
>
> Thanks,
> Ana
>
> ## Forwardable blurb
>
> **Subject:** Company CU (front desk for dental clinics) / Jordan, Fund F
>
> Hi Jordan,
>
> I'm Ana, CEO of Company CU. Sam and I were in the same accelerator batch.
>
> Company CU is the front desk for dental clinics: online booking, reminders and payments in one inbox. We had $38k MRR in October and 22 paying clinics, per our October update.
>
> I'm writing to you because you led the seed of a clinic-software company and wrote that small practices are underserved. Those practices are our customers.
>
> Would you have 30 minutes for a call?
>
> [deck link, if you send one]
>
> Ana
> CEO, Company CU
>
> [...]
>
> ## Follow-up 2 (the last one)
>
> **To:** [Jordan's email, from you] > **Subject:** Re: Front desk for dental clinics: $38k MRR in October
>
> Hi Jordan,
>
> [One line of news, if you have it.]
>
> If Company CU isn't a fit for Fund F right now, a one-word "no" is fine and I won't write again. If you'd rather watch from a distance, I'm happy to send you a short update now and then. And if a 30-minute call works, I'd welcome it.
>
> Ana
> CEO, Company CU
>
> ## Reader pass
>
> These are my own judgment of how a busy investor is likely to skim the drafts.
>
> | Line                                                   | What an investor is likely to read in it                 | What I did                                                                                                            |
> | ------------------------------------------------------ | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
> | "the revolutionary front desk" (one-pager)             | A hype word with nothing they can check.                 | Dropped the word; the rest of your one-liner is intact. Worth changing in the one-pager too, since Jordan may see it. |
> | "22 paying clinics"                                    | A count with no date.                                    | Attributed it to the October update; give me an as-of date if you have one.                                           |
> | "wrote that small practices are underserved"           | A fair reason to write, but only if it matches the post. | Kept your paraphrase. Check it against the blog before sending, since Jordan will know what they wrote.               |
> | "Sam and I were in the same accelerator batch" (blurb) | Fine in the blurb, because Sam is the one forwarding it. | Kept there, but left out of the cold email, where it would use Sam's name without their intro.                        |
>
> [...]
>
> The timing of the follow-ups is your call. None of the emails mentions a raise; if you add one, have a lawyer look before it goes to someone you don't know. This is not investment, legal or tax advice.
