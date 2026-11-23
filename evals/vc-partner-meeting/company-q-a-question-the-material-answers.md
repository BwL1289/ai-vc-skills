# Eval 1: Company Q, a question the founder's material already answers

A test prompt for the `vc-partner-meeting` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. A run passes when the refute pass moves a
question to the quick-rehearsal list by quoting the founder's own line that answers it, keeps the one the material
cannot answer, debriefs each pasted answer with a stronger one built only from the founder's material, and never
speaks as an investor.

## Prompt

> Run a mock partner meeting for our seed round; I'll paste everything in one message. The partner came from
> product. One-liner: "Company Q turns warehouse pick lists into voice instructions for pickers." Slide 2: "Pickers
> today read paper lists or handheld screens." Slide 3: "Live in 3 warehouses since June; pick errors fell from 2.1%
> to 0.6% at the first site over 8 weeks." Slide 4: "Our moat is our AI." Slide 5: "Raising $1.2M on a SAFE to reach
> 15 paying warehouses." Answers I expect to give: "Why do they come back? Because pickers love it." and "Who else
> does this? Nobody does voice for small warehouses."

## Expected tool call

None: no `equity_deal_check` call. The raise is on a SAFE with no cap given. As vc-deal-math step 2 says, the skill
asks for the cap and the next priced round the founder expects before any `equity_round` call.

## Expected answer

- It names the lenses it ran (Seed and Product) in one line, and says how they ran (subagents, or one after another
  in one agent).
- A Product lens question on whether anyone wants this, raised on the one-liner, is listed under Dropped, answered,
  quoting "Live in 3 warehouses since June; pick errors fell from 2.1% to 0.6% at the first site over 8 weeks." as the
  line to lead with. It goes to the quick-rehearsal list, not the hard drill.
- Kept: a question on "Our moat is our AI." (what the model does that the product could not do without it), with a
  bracketed ask. No pasted answer matches it, so it is marked "not rehearsed".
- Debrief: "Because pickers love it." is weak (no figure where the question asks for one); the stronger answer leads
  with the slide-3 line and brackets the missing figure, such as
  `[share of pickers using it each shift, last 8 weeks]`. "Nobody does voice for small warehouses." is weak (a phrase the vc-positioning skill flags); the stronger
  answer names the alternatives from "Pickers today read paper lists or handheld screens."
- It computes nothing from the error rates (no relative reduction) and quotes them as stated.
- The standing prep questions are listed with bracketed asks, since the material says nothing about the round so far.
- No pass, invest or score; every question is put in the third person.
