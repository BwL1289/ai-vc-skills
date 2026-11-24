# Eval 5: Company BK, a "contrarian" insight most investors already hold

A test prompt for the `vc-positioning` skill. The company is made up. "Expected answer" states the expected behaviour,
and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24). The founder's slide calls a
trend most investors already expect a contrarian insight, and the founder's own competition slide shows others acting on
it. A run passes when the Is it really contrarian? lens objects to the slide-2 line as a view most investors already
hold, that objection survives the refute pass, and the answer writes no contrarian belief the founder did not state,
asking for one once with the two prompts instead. The verdict is Pass when every clause of that sentence is met, Partial
when exactly one clause is missed or met only in part, and Fail when two or more are missed; a shortfall against the
other points of the expected answer is noted but does not change the verdict. The recorded run is a Pass with
shortfalls. The skill was changed after that run (see "Recorded answer").

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

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with plugin 0.3.5 loaded from this repository and no user settings. An
earlier run of this eval that day, on plugin 0.3.2, is not recorded. The answer is trimmed; [...] marks each cut.

**Pass, with shortfalls against the expected answer.** It met every clause of the pass sentence above. The Is it really
contrarian? lens objected to the slide-2 line, quoted word for word, as a trend reworded that few investors would reject
and that names no one who disagrees; five of the seven lenses raised it. That objection survived the refute pass and
heads the survivors, tiered as ending the meeting. The answer wrote no contrarian belief: its rewrite is the bracketed
ask `[the belief about this market that most investors would reject today, in one sentence]`, and it asked for one once,
with the two prompts, each of which appears once in the answer. Seven lens subagents ran, and with ten objections, past
the eight above which lean mode may apply, the refute pass ran one subagent per lens, which the answer said. Short of
the expected answer: the refute pass dropped as not grounded a second objection, the one quoting slide 4, on the ground
that slide 4 says nothing about the insight being contrarian, where the expected answer has slide 4 support the
objection; the surviving objection never cites slide 4, though the answer's opening line leans on it. There is no
dimension table, so row 12 is never marked Needs work, and no open asks section: the two prompts sit in the Contrarian
insight block, and the bracketed belief ask appears three times. A steer in that block ("Everyone funded sells to
insurers, you serve independent adjusters", "If your real belief lives in that gap, state it") states no belief but
leans toward the kind the expected answer rules out, and the ask in the second survivor's row assumes what no slide
says. The missing raise ask is never named, and there is no prep script, no Lens column and no link beside the sources.
Since this run the refute brief says that a line showing others already acting on a belief stated as contrarian supports
the objection that most investors hold it, so that objection is never dropped as not grounded because its quoted line
does not name the belief. The eval has not been run again.

> **Slide 2 will not hold up as written.** "Insurance claims work is moving from paper to software" is a belief most seed investors already hold, and your own slide 4 shows every large insurer and four funded startups acting on it.
>
> I ran seven independent review lenses over your five lines, then tested each objection against your own text. I only saw these five lines, so slides you did not paste may already answer some of the gaps.
>
> ## Biggest issues
>
> 1. **Slide 2 is consensus, not contrarian.** Five of the seven lenses raised this independently. Nothing in the deck names who disagrees with the belief or why they are wrong.
> 2. **Slide 4 names a funded field but not why it leaves you room.** Your text draws the split itself (they sell "to insurers", you serve "independent insurance adjusters") but never says why that gap exists or will last.
> 3. **Slide 3 has no measurement behind it.** It is the one line that sounds like first-hand knowledge, yet it carries no hours, sample or source, and nothing ties it to the CEO's 9 years.
>
> ## Objections that survived
>
> | #   | Tier             | Your line                                                                                                             | Why a partner is likely to read it that way                                                             | Evidence to add                                                                                                                        |
> | --- | ---------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
> | 1   | Ends the meeting | "Insurance claims work is moving from paper to software."                                                             | A trend investors already expect, labelled as contrarian.                                               | `[the belief about this market that most investors would reject today, in one sentence]` and `[who disagrees, and why they are wrong]` |
> | 2   | Ends the meeting | "Every large insurer now runs claims on its own software, and four funded startups sell claims software to insurers." | A crowded field with no stated reason you win, and no reason those players will not add report writing. | `[why insurer software and the four startups do not serve independent adjusters, with evidence]`                                       |
> | 3   | Weakens          | "An adjuster spends more time writing each claim report than inspecting the damage."                                  | A claim with no measurement.                                                                            | `[hours per claim writing vs. inspecting, with source]` or `[what the CEO saw in 9 years that shows this]`                             |
> | 4   | Weakens          | "Company BK writes claim reports for independent insurance adjusters."                                                | "Writes" could mean a human service, a template tool or software that drafts reports.                   | `[product form: service, template tool or drafting software]`                                                                          |
> | 5   | Weakens          | Same line                                                                                                             | Names the user but not the buyer, the count or the price.                                               | `[who pays: adjuster, their firm or the insurer]`, `[number of independent adjusters, with source]`, `[price]`                         |
> | 6   | Weakens          | Same line                                                                                                             | No stage, usage or revenue figure in the lines given.                                                   | `[adjusters using it, reports written, revenue, each with its period]`                                                                 |
> | 7   | Weakens          | "Our CEO worked 9 years as an independent adjuster; our CTO built document tools at a legal-software company."        | Tenure and a job description, not an achievement.                                                       | `[CEO: claims handled or a concrete outcome]`, `[CTO: the specific tool shipped and how it carries over]`                              |
> | 8   | Weakens          | "Insurance claims work is moving from paper to software."                                                             | As a "why now" it names no trigger and no date.                                                         | `[what changed for independent adjusters, and when]`                                                                                   |
> | 9   | Minor            | Opening line                                                                                                          | A narrow first market with no stated way to widen.                                                      | `[next customer group after independent adjusters]`                                                                                    |
>
> **Dropped:** one objection, that slide 4 by itself undercuts the contrarian claim. The check ruled that slide 4 says nothing about the insight; the point survives inside objection 1 instead.
>
> The second-stage check ran once per lens, not once per objection, which is less independent. I can run the full pass if you want it.
>
> ## Contrarian insight
>
> - **As stated:** "Insurance claims work is moving from paper to software."
> - **Verdict:** most investors already hold it, and no evidence for it is shown.
> - **Rewrite:** I will not write the belief for you; one you did not state would be invented. It has to come from you: `[the belief about this market that most investors would reject today, in one sentence]`.
>
> Two prompts to find it:
>
> - What do you believe about this market that most investors would reject?
> - What did you see first-hand that others have not?
>
> Your own slides hold the raw material. Everyone funded sells to insurers, you serve independent adjusters, and your CEO was one for 9 years. If your real belief lives in that gap, state it, say who disagrees, and put the CEO's first-hand evidence beside it.
>
> Not every good company needs a contrarian story. Dropping the label and using slide 2 as a plain "why now" with a trigger and a date is a legitimate choice.
>
> [...]
>
> The who-disagrees and evidence tests are this review's own framing, and the pre-pitch test has no public source behind it. This is not investment or legal advice.
