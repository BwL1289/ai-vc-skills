# Eval 3: Company G, an objection the founder's material already answers

A test prompt for the `vc-positioning` skill. The company is made up. This eval states the expected behaviour; it is
not a recorded run. A run passes when the refute pass drops an objection by quoting the founder's own line that
answers it, keeps the one the material cannot answer, and invents nothing on the founder's behalf.

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
  or note raise". The answer works out no runway and asks for nothing it would need to.
- The market has no line to quote, so it is a gap in the open asks, not an objection.
- The prep script is filled in for the lead seed investor and brings the top survivors to the session.
