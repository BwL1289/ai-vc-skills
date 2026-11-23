# Eval 2: Company R, a runway answer the calculator checks

A test prompt for the `vc-partner-meeting` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator deal_check` and `equity_calculator runway_plan` runs with these inputs. "Expected answer" states the
expected behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run
passes when it makes the two tool calls below (field order free, money and percents as strings), puts the runway
mismatch at the head of the kept questions without refuting it, checks the runway with no raise with the calculator,
and computes nothing in its own text. The verdict is Pass when every clause of that sentence is met, Partial when
exactly one clause is missed or met only in part, and Fail when two or more are missed. The recorded run is graded
against the pass sentence this eval had then, which asked for one `equity_deal_check` call and the runway with no raise
quoted as not checked, where it now asks for the second call and that runway checked with the calculator. It is a
Partial against that sentence; it made neither of those two, so against today's sentence it would be a Fail. The skill
and this pass sentence were changed after that run (see "Recorded answer").

## Prompt

> Prep me for my partner meeting at a seed fund on Tuesday; the partner was a finance executive before investing. One
> message, please. We're raising a $2M priced seed at an $8M pre-money for 20% of the company. We have $500k in the
> bank, spend $80k a month today and plan to spend $120k a month after the raise; no revenue yet. The deck says the
> round gives us 24 months of runway. Without the raise we have about 6 months. One-liner: "Company R schedules
> home-care nurses for agencies." My answer to "how long does the money last?": "Two years, comfortably."

## Expected tool call

Two calls.

`equity_deal_check`, once (`current_monthly_revenue` and `planned_monthly_revenue` as `"0"` may be added, since the founder says there is no revenue yet; no other key):

```json
{
  "inputs": {
    "investment": "2000000",
    "pre_money": "8000000",
    "stated_investor_percent": "20",
    "cash_on_hand": "500000",
    "planned_monthly_gross_burn": "120000",
    "current_monthly_gross_burn": "80000",
    "stated_runway_months": "24"
  }
}
```

`equity_runway_plan`, once, for the runway with no raise, on today's spend:

```json
{
  "inputs": {
    "cash_on_hand": "500000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          {
            "from_month": 1,
            "gross_burn": "80000",
            "revenue": "0"
          }
        ]
      }
    ],
    "stated_runway_months": "6"
  }
}
```

## What the calculator prints (excerpt)

The deal check, as the command line prints it (a tool call returns the same values as JSON: fractions such as
0.200000, and each flag as its bare code):

```text
  Planned monthly gross burn                                       $120,000.00  given
  Net runway, planned burn                                        20.83 months  (cash + I)/net burn
  Net runway, today's burn                                        31.25 months  (cash + I)/net burn
  Investors' percent: the calculator gives                            20.0000%  the investor's cap-table share
  Investors' percent: verdict                                       consistent  within the tolerance, or rounding to the deck's, is consistent
  Runway: the deck says                                           24.00 months  given
  Runway: the calculator gives                                    20.83 months  (cash + I)/net burn, planned (else current)
  Runway: difference                                              -3.17 months  computed - stated
  Runway: verdict                                                     mismatch  within the tolerance, or rounding to the deck's, is consistent
  A VC is likely to ask                             current_burn_runway_longer  Runway on today's burn is longer than on the planned burn; say which one the deck uses, as a VC will check it against the planned spend
```

The runway plan:

```text
  Runway, plan, no raise                          6.25 months  months until cash less the floor goes below zero
  Runway, no raise: stated                        6.00 months  given
  Runway, no raise: the calculator gives          6.25 months  the plan case's runway
  Runway, no raise: difference                    0.25 months  computed - stated
  Runway, no raise: verdict                          mismatch  within the tolerance is consistent
```

## Expected answer

- The runway mismatch heads the kept questions, ahead of the tiers and with no tier: the deck's "24 months" (the tool
  prints 24.00 months, given) against the tool's 20.83 months at the planned burn of $120,000.00, a difference of
  -3.17 months (restating it as 3.17 months short of the claim puts the tool's sign into words and computes nothing). It is
  not put through the refute pass.
- The `current_burn_runway_longer` flag is a kept question at weakens it, first in that tier, with its meaning from
  the skill's calculator flags table, since the tool call returns the code only, and not refuted. Numbers relays it
  in one line (31.25 months on today's burn) and asks the founder to say which burn the deck uses.
- The percent sold is consistent (20.0000%) and is not drilled.
- The Finance lens runs with the Seed lens.
- "Without the raise we have about 6 months." is checked with `equity_runway_plan` on today's spend: 6.25 months
  against 6.00 months stated, a mismatch. The claim is below the tool's figure, so it understates: it goes in the minor
  tier at most, and the founder may keep it or say 6.25 months. No division of cash by burn appears.
- Debrief: "Two years, comfortably." is weak (it disagrees with a tool result, both quoted); the reason for the gap is
  a bracketed ask, such as `[what the deck's 24 months assumes]`, never an argument about which assumptions would make
  24 months true. The stronger answer uses only the tool's figures and the founder's burn plan, and brackets what the
  money reaches, such as `[the milestone the $2M reaches]`.
- The hardest three and the kept table put each question in the third person ("A partner is likely to ask ..."); the
  calculator's rows are marked as from the calculator and not refuted, and any count of questions that survived the
  refute pass counts only the lens questions.
- No arithmetic in the text beyond the tool's values, which are given as printed (20.83 months stays 20.83 months):
  no difference between the founder's two burn figures appears anywhere, in a table cell or a bracketed ask included.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings, when
this eval expected one `equity_deal_check` call and the runway with no raise quoted as not checked. The answer is
trimmed; [...] marks each cut.

**Partial, against the pass sentence this eval had then: one clause missed.** It made the one call then expected, put
the runway mismatch first without refuting it, relayed the flag and quoted the runway with no raise as not checked, as
the skill then said. But a bracketed ask in its table states "$40k", the difference between the founder's two burn
figures, which neither the founder nor the tool gave; its debrief also argues which assumptions would make the deck's 24
months true. Against today's sentence it also misses the second call and the calculator check of the runway with no
raise, three clauses in all, so it would be a Fail. Since this run the skill sends the runway with no raise to
`equity_runway_plan`, counts bracketed asks, table cells and debrief notes in its no-arithmetic check, leaves the reason
for a disagreement as a bracketed ask, carries each flag's meaning in a table of its own (the tool call returned the
bare code), puts a mismatch ahead of the tiers with no tier, and writes the hardest three in the third person; this eval
now expects the second call. The eval has not been run again.

> **The deck's 24 months does not match your own numbers.** $500k in the bank plus the $2M, at $120k a month with no revenue, lasts 20.83 months, which is 3.17 months short of the claim. [...]
>
> [...]
>
> | Rank  | Tier             | Lens                            | Your line                                                                                  | Question a partner is likely to ask                                                                     | What you need ready                                                          |
> | ----- | ---------------- | ------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
> | 1     | Ends the meeting | Calculator (also Seed, Finance) | "The deck says the round gives us 24 months of runway." Calculator: 20.83 months, mismatch | Walk me through 24 months from the cash, the $2M and $120k a month. Where does "comfortably" come from? | [what the deck's 24 assumes: a spend ramp, revenue, or an error]             |
> | [...] |                  |                                 |                                                                                            |                                                                                                         |                                                                              |
> | 5     | Weakens it       | Finance                         | "plan to spend $120k a month after the raise"                                              | What does the extra spend buy, what if the plan slips, and what do you cut first?                       | [what the added $40k a month pays for; a downside runway; the order of cuts] |
>
> [...]
>
> The 24 sits between the two calculator figures, so it can only be right if the deck assumes a gradual ramp or some revenue. [...]
>
> [...]
>
> - **Runway without the raise:** "about 6 months" is quoted as you stated it; not checked, because no tool computes runway without a raise.
