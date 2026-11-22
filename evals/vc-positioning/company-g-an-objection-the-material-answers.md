# Eval 3: Company G, an objection the founder's material already answers

A test prompt for the `vc-positioning` skill. The company is made up. "Expected answer" states the expected behaviour,
and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22). A run passes when the refute
pass drops an objection by quoting the founder's own line that answers it, keeps the one the material cannot answer, and
invents nothing on the founder's behalf.

## Prompt

> Stress-test our pitch before I meet our lead seed investor on Thursday. Opening line: "Company G gives hospital
> pharmacies one screen for drug shortages, and early traction is strong." Slide 3, Traction: "Paid pilots at 4
> hospitals since March, $2,000 a month each; 3 of the 4 renewed for a year in September." Slide 4, Why now: "Since
> last year the main shortage list is published as a daily data feed, so shortages can be tracked automatically."
> Slide 5, Competition: "Today pharmacists use spreadsheets and phone calls; two inventory vendors show shortages in a
> monthly report." Slide 6, Team: "Our CEO ran pharmacy purchasing at a 600-bed hospital for 8 years; our CTO built
> the data pipeline at a health-data startup." Slide 7, Ask: "We're raising $1.5M on a SAFE.
> That gives us 18 months of runway."

## Expected tool call

None: no `equity_deal_check` call. The raise is on a SAFE, which `deal_check` does not model, and no cap is given. As
the vc-deal-math skill says, it asks for the cap and the next priced round the founder expects before any
`equity_round` call. No tool checks the runway claim on a SAFE raise either.

## Expected answer

- The traction lens's objection to "early traction is strong" (a claim with no number) is listed under Dropped,
  answered, quoting the founder's own line "Paid pilots at 4 hospitals since March, $2,000 a month each; 3 of the 4
  renewed for a year in September." It does not appear among the survivors.
- The say-and-avoid list may still suggest moving that slide-3 line into the opening, using only the founder's own
  figures; it does not add or total any number (no monthly revenue worked out from the pilots).
- Any objection that the why-now or competition lines answer is dropped the same way, quoting the slide-4 or slide-5
  line.
- "We're raising $1.5M on a SAFE." survives (the ask and milestones), because nothing in the material says what the
  $1.5M reaches; the evidence to add is a bracketed ask, such as `[the milestones the $1.5M reaches]`.
- "That gives us 18 months of runway." is quoted as stated and marked "not checked: no tool computes this for a SAFE
  or note raise". The answer works out no runway from any figure.
- The market has no line to quote, so it is a gap in the open asks, not an objection.
- The prep script is filled in for the lead seed investor and brings the top survivors to the session.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-22, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass.** Six lens subagents and eight refute subagents ran; the refute pass dropped the traction objection by quoting
slide 3, the SAFE's runway is not checked, and no pilot revenue is totalled. Short of the expected answer: the why-now
objection was dropped although its judge called it a close call (the skill says to keep it), the market became a
survivor rather than an open ask, and the prep script hedges on who the lead is.

> I ran the stress test: six independent skeptical lenses attacked the pitch, then a separate pass tested each objection against your own slides. Six objections survived and two were dropped; none is rated as ending the meeting.
>
> ## The three to fix before Thursday
>
> 1. **Slide 5 makes you look like a feature.** You say two inventory vendors already show shortages, and the only difference you name is monthly versus daily.
> 2. **The fourth hospital is unexplained.** With four customers, a partner is likely to assume it churned.
> 3. **No new customer since March.** The renewals show retention, but nothing shows you can win a fifth hospital.
>
> ## Surviving objections
>
> | Rank | Tier    | Lens                | Your line                                                                                                  | Why a partner reads it that way                                                                                                    | Evidence to add                                                                                                                                 |
> | ---- | ------- | ------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
> | 1    | Weakens | Competition; Market | "two inventory vendors show shortages in a monthly report."                                                | Incumbents are already inside the hospital, and the feed on slide 4 is published, so going daily looks like a short step for them. | [what your screen does that a vendor's report would not do even if daily] and [whether the renewing hospitals already use one of those vendors] |
> | 2    | Weakens | Traction; Ask       | "3 of the 4 renewed for a year in September."                                                              | One unexplained non-renewal is a large share of the evidence, and silence reads as the obvious risk left out.                      | [the fourth hospital's status, its stated reason, and what you changed as a result]                                                             |
> | 3    | Weakens | Traction            | "Paid pilots at 4 hospitals since March, $2,000 a month each; 3 of the 4 renewed for a year in September." | The customer count reads as flat to down, because no hospital is named as added since March.                                       | [hospitals signed or in contracting since March, with dates]                                                                                    |
> | 4    | Weakens | Ask                 | "We're raising $1.5M on a SAFE. That gives us 18 months of runway."                                        | Runway is a duration, not a milestone, so a partner cannot judge whether you will be fundable at the next round.                   | [the hospital count, revenue level or product state at month 18] and [use of funds]                                                             |
> | 5    | Weakens | Market              | "Paid pilots at 4 hospitals since March, $2,000 a month each; 3 of the 4 renewed for a year in September." | This is the only price on a buyer, set against an uncounted number of buyers.                                                      | [how many hospital pharmacies fit, with a source] and [the price you expect beyond the pilot rate]                                              |
> | 6    | Minor   | Ask                 | "We're raising $1.5M on a SAFE."                                                                           | The instrument is named without terms; a lead often sets them, but have your view ready.                                           | [valuation cap, discount if any, and whether it is post-money]                                                                                  |
>
> ## Dropped objections
>
> - **"early traction is strong" has no number** (phrase scan): answered by slide 3, "Paid pilots at 4 hospitals since March, $2,000 a month each; 3 of the 4 renewed for a year in September." Move those figures into the opening line in place of the adjective.
> - **The why-now is open to everyone** (Market; Competition): answered by slide 6, "Our CEO ran pharmacy purchasing at a 600-bed hospital for 8 years; our CTO built the data pipeline at a health-data startup." The judge called this a close call, because the deck never says the vendors lack that experience. Reference the CEO's experience on slide 4; the part still open is objection 1.
>
> The Clarity lens and the Team lens found nothing.
>
> [...]
>
> ## Numbers
>
> - **"$1.5M on a SAFE" and "18 months of runway":** not checked. No tool computes runway for a SAFE raise, and with no cap or discount given the conversion could not be run either.
> - **"4 hospitals", "$2,000 a month", "3 of the 4":** quoted as stated, not checked.
> - **"since March", "in September", "since last year":** these carry no year, so put the years on the slides.
>
> [...]
>
> ## Prep session
>
> I do not know whether this lead has already committed or is still deciding. If you have another existing investor or a founder who recently raised a seed, take 45 minutes with them by Tuesday; a substitute who does not know your history can only guess at items 4 and 5.
>
> 1. Before any slides, ask them to say in one sentence what Company G does, and compare it with your one-liner.
> 2. Give the pitch and ask them to stop you at the first line they would discount.
> 3. Ask for the three questions they expect first. If the inventory vendors or the fourth hospital come up, rehearse those answers out loud.
> 4. Ask whether "$1.5M, 18 months, [milestone]" holds up and matches what they have seen in your updates.
> 5. Ask what they would say if a new investor called them about the company, and how they would describe it in an intro email.
>
> [...]
>
> This review predicts likely objections from your text; a real partner may raise others. It is not investment, legal or tax advice. Have a lawyer review materials before you send them widely, and make sure any hospital you name has agreed to be named.
