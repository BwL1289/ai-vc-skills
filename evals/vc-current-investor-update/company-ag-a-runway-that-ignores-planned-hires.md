# Eval 1: Company AG, a monthly update whose runway ignores the planned hires

A test prompt for the `vc-current-investor-update` skill. The company is made up. The tool calls and the excerpts are
from real `equity_calculator runway_plan` runs with these inputs. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when it makes the
two calls below (field order free, money as strings), states the runway as the tool prints it, ties out last month's
two "next month" items as lowlights in the founder's words, and computes nothing in its own text. The verdict is Pass
when every clause of that sentence is met, Partial when exactly one clause is missed or met only in part, and Fail when
two or more are missed; a shortfall against the other points of the expected answer is noted but does not change the
verdict.

## Prompt

> Write our October investor update. Last month's update said: "Highlights: signed our 12th paying clinic. Next month:
> hire two engineers and launch the scheduling add-on. Runway: 15 months." This month: 14 paying clinics; MRR $22,000,
> which we report for the first time (recurring subscription revenue billed in the month). We hired one engineer, not
> two; the second candidate declined. The scheduling add-on slipped to December because of a billing bug. Cash at 31
> October: $1,100,000. We spend $95,000 a month and bring in $22,000; from month 4 (February), with the two hires, we
> plan to spend $120,000 a month with $30,000 of revenue. Runway: 15 months. Ask: introductions to practice managers at
> multi-site dental groups.

## Expected tool call

`equity_runway_plan`, twice. First the plan:

```json
{
  "inputs": {
    "cash_on_hand": "1100000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "95000", "revenue": "22000" },
          { "from_month": 4, "gross_burn": "120000", "revenue": "30000" }
        ]
      }
    ],
    "stated_runway_months": "15"
  }
}
```

```text
  Runway, plan, no raise                           12.79 months  months until cash less the floor goes below zero
  Runway, no raise: stated                         15.00 months  given
  Runway, no raise: the calculator gives           12.79 months  the plan case's runway
  Runway, no raise: difference                     -2.21 months  computed - stated
  Runway, no raise: verdict                            mismatch  within the tolerance is consistent
```

Then today's spend held flat, because the plan changes the burn and the claim is a mismatch:

```json
{
  "inputs": {
    "cash_on_hand": "1100000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "95000", "revenue": "22000" }
        ]
      }
    ],
    "stated_runway_months": "15"
  }
}
```

```text
  Runway, plan, no raise                           15.07 months  months until cash less the floor goes below zero
  Runway, no raise: verdict                          consistent  within the tolerance is consistent
```

## Expected answer

- The draft's Cash and runway section states $1,100,000 at 31 October and the runway as the tool prints it: 12.79 months
  on the plan with the two hires, 15.07 months at today's spend held flat. "Runway: 15 months" does not appear as the
  update's figure.
- The calculator's mismatch leads the fix list ahead of the tiers, with no tier. The update states the runway the last
  update gave, so that entry names the pattern "The same runway figure two updates running" and says it is unverified.
  The answer computes no runway itself and explains no gap with a division.
- Tie-out: "hire two engineers" and "launch the scheduling add-on" each get a lowlight in the founder's words ("We hired
  one engineer, not two; the second candidate declined." and "The scheduling add-on slipped to December because of a
  billing bug."). Paying clinics: 12 in the last update, 14 now, both quoted, status Same (a count given as an event and
  one given as a level), with one ask whether any clinic left; the last update's words are not recast, and no growth is
  worked out. MRR is New (the last update gave none) and carries its definition.
- The ask names the practice managers at multi-site dental groups, as given. The Definitions block holds the MRR
  definition word for word, and no definition the founder did not give (the runway's is a bracketed ask). No score; no
  named firm.
- The draft comes first, with no status line or headline before it, and is labelled October with a bracketed `[year]`.
  The four lenses run as subagents, then one refute subagent per objection, all launched in one message; the answer says
  how many ran.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from a pinned copy of this repository. The
answer is trimmed; [...] marks each cut.

**Pass.** It made the two calls below with the expected inputs, stated 12.79 months on the plan and 15.07 months at
today's spend held flat as the tool prints them, wrote both "next month" items as lowlights in the founder's words, and
computed nothing. Short of the expected answer: the pattern for the same runway two updates running is never named;
paying clinics came back Different form, not Same, while the draft recasts the last update as "the 12 we reported"; the
four lenses ran as subagents but the refute pass ran in the main agent; a status line and a headline come before the
draft; the subject line adds a year the founder never gave; and the Definitions block carries a runway definition of
the skill's own. Since this run the skill names the pattern when the stated runway repeats the last update's, the
shared rules file makes a count given as an event and one given as a level of the same thing Same, Stage B launches one
refute subagent per objection in a single message, draft mode opens with the draft, and a year or definition the
founder did not give is a bracketed ask; the eval has not been run again.

> Still working: the runway check and four independent reader lenses are done; here is the finished draft and what they found.
>
> **Your "Runway: 15 months" does not hold on your own plan.** With the February step-up to $120,000 spend and $30,000 revenue, the calculator gives 12.79 months from 31 October. The 15 only holds if today's spend and revenue stay flat (15.07 months). The draft states both and leaves bracketed gaps where only you have the facts.
>
> ## Draft, ready to copy
>
> **Subject: [Company name]: October 2026 investor update**
>
> [...]
>
> **Lowlights**
>
> - Hiring: we said we would hire two engineers. We hired one; the second candidate declined. Our plan still has both hires in place from February. [what happens next on the second hire, and the new target date]
> - Scheduling add-on: we said it would launch in October. It has slipped to December because of a billing bug. [what the bug is, whether it affected any clinic's invoices or the $22,000, and what is being done]
> - Runway: 12.79 months on our plan, against the 15 months we reported last month. [one sentence: did last month's 15 months count the February step-up in spend]
>
> [...]
>
> **Cash and runway**
>
> - Cash: $1,100,000 at 31 October. [one-line bridge from last month's cash to this: net burn plus anything else that moved cash]
> - Today: spend (gross burn) $95,000 a month, revenue $22,000 a month. [confirm the $22,000 billed is also what was collected]
> - Plan: from February, with the two hires, spend $120,000 a month and revenue $30,000 a month. [what the $30,000 rests on: signed clinics, the add-on, or a target]
> - Runway on this plan, with no raise: 12.79 months from 31 October.
> - With today's spend and revenue held flat: 15.07 months.
>
> [...]
>
> **Definitions**
>
> - Paying clinics: [what counts as a paying clinic, and the date it is counted at]
> - MRR: recurring subscription revenue billed in the month.
> - Spend: gross burn. Runway: months until cash reaches zero on the plan above, with no raise.
>
> ## Reader pass
>
> Four lenses ran as independent subagents on my first draft. I judged the refute step myself rather than with separate subagents, so it is less independent. Nothing was dropped, because your notes do not answer any of these; the draft above is already revised for each.
>
> | Rank | Tier               | Section         | Lens                                   | The line (quoted)                   | Why an investor is likely to read it that way                                                                                                                                                      | Fix                                                                                            |
> | ---- | ------------------ | --------------- | -------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
> | 1    | Fix before sending | Cash and runway | Calculator                             | "Runway: 15 months" (your notes)    | The plan gives 12.79 months, so the figure is a mismatch.                                                                                                                                          | State 12.79 on plan and 15.07 held flat (done).                                                |
> | 2    | Fix before sending | Cash and runway | Missing bad news, Definitions, Tie-out | "Last month we reported 15 months." | The drop from 15 sat at the bottom of the cash section with no explanation. It reads as a quiet correction. The flat figure, 15.07, is also larger than last month's 15 after a month of spending. | Moved to Summary and Lowlights; needs your sentence on last month's basis and the cash bridge. |
>
> [...]
>
> ## Tie-out to last month
>
> | Item                        | Last update said                | This update says                      | Status                                     |
> | --------------------------- | ------------------------------- | ------------------------------------- | ------------------------------------------ |
> | Paying clinics              | "signed our 12th paying clinic" | "14 paying clinics"                   | Different form until you confirm the count |
> | MRR                         | not reported                    | "$22,000"                             | New                                        |
> | Runway                      | "Runway: 15 months"             | 12.79 months on plan; 15.07 held flat | Mismatch with your stated 15               |
> | Promise: hire two engineers | "hire two engineers"            | "We hired one engineer, not two"      | Missed, reported                           |
> | Promise: scheduling add-on  | "launch the scheduling add-on"  | "slipped to December"                 | Missed, reported                           |
>
> ## Numbers
>
> - **Plan, no raise:** stated 15.00 months, calculator 12.79 months, difference -2.21 months, verdict mismatch. No flags.
> - **Today's spend held flat:** stated 15.00 months, calculator 15.07 months, difference 0.07 months, verdict consistent. No flags.
>
> [...]
>
> This is not investment, legal or tax advice. You send the update; I have sent nothing.
