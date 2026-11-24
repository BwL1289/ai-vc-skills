# Eval 1: Company CM, a logo grid, the founder's own axes and a platform answer the material gives

A test prompt for the `vc-competitive-landscape` skill. The company and the names are made up. "Expected answer" states
the expected behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24). A run
passes when it places each named competitor at a level using only the founder's facts, keeps the unverified fact off the
slide, flags the one-company claim, the axis built around the founder's own product and the company at the top of every
axis, draws the 2x2 from the founder's placements by the halves alone, proposes a third axis with its anchors and places
no one on it, drops an objection by quoting the founder's line that answers it, and adds nothing into a score. The
verdict is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or met only in
part, and Fail when two or more are missed; a shortfall against the other points of the expected answer is noted but
does not change the verdict. The recorded run is a Pass with shortfalls, which its grader called partial overall. The
skill was changed after that run (see "Recorded answer").

## Prompt

> Build our competition slide. Company CM plans the day's routes for plumbing firms with two to ten vans. Our
> competitors as we see them. "Product P: dispatch software for plumbing firms with 20 or more vans." (source: their
> pricing page). "Product Q: a job-tracking app many trades use; two prospects told us they tried it for routing."
> (source: those two calls). "Product Q is clunky." (no source). "Suite S, the accounting app every firm we sell to
> already uses, could add scheduling." "Before us, most of our customers planned routes on a whiteboard and by phone."
> (source: our onboarding calls). Why customers pick us: "Firms are live the same afternoon, with no setup call." and
> "We won 6 of the 8 deals where Product P was also in the running." On Suite S: "They have spent ten years on
> invoicing." and "If Suite S ships scheduling, we plug into it and sell the routing on top, as we already do with their
> invoice export." Our slide 6 today shows the three logos under the line "We're the only route planner built for small
> plumbing firms." Our axes: Setup effort, where 1 means a consultant on site and 5 means live the same day; and Fit for
> small crews, where 1 means built for big fleets and 5 means built for two to ten vans. Our placements: us 5 and 5,
> Product P 2 and 1, Product Q 3 and 2.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- "We're the only route planner built for small plumbing firms." is flagged with the no-competitors pattern and survives
  the review. Its fix is a headline built from the founder's own line "Firms are live the same afternoon, with no setup
  call." and the table of all four levels.
- If the platform-risk lens objects that "Suite S, the accounting app every firm we sell to already uses, could add
  scheduling." leaves the slide with no answer for what happens if it does, the refute pass lists it under Dropped,
  answered, quoting the founder's line "If Suite S ships scheduling, we plug into it and sell the routing on top, as we
  already do with their invoice export." with the advice to move it into the speaker note. It is not among the
  survivors.
- "Product Q is clunky." stays on the map labelled unverified and stays off the slide. It drops no objection that asks
  for evidence against Product Q, and the line against Product Q ends with a bracketed ask (`[a deal won against Product
Q, or a customer's words]`).
- The map: Product P at Direct, Product Q at Indirect, Suite S at Adjacent as the platform kind, and the whiteboard and
  phone at Substitutes, each with the problem it solves quoted or a bracketed ask, and each fact with its source as the
  founder gave it. Nothing is added about any of them, and no competitor or platform is named that the founder did not
  name.
- Axes: Setup effort keeps the founder's anchors for 1 and 5 and gets a proposed anchor for 3 for the founder to
  confirm. Fit for small crews is flagged as an axis whose anchors fit the founder's own product alone. At least one
  more axis is proposed to reach three, with its anchors at 1, 3 and 5 stated before any placement and its buyer
  evidence quoted or marked as none given, and every company is `not placed` on it; the skill suggests no placement. The
  halves are stated: 1 and 2 low, 4 and 5 high, 3 on the line.
- The placements table holds the founder's placements as given, and the company at 5 on every axis is flagged. No total,
  average, rank or winner appears.
- The 2x2 uses the founder's two axes and follows the halves alone: Company CM in the high-high quadrant, Product P in
  the low-low quadrant, Product Q on the setup-effort line and in the low half of fit for small crews. Suite S and the
  whiteboard and phone, which the founder did not place, are listed under the grid as `not placed`, never drawn, and
  their placements are open asks. It is flagged as the company alone in the best corner.
- The line against Product P quotes "We won 6 of the 8 deals where Product P was also in the running." as stated; no win
  rate is worked out.
- The platform-risk answer: its first part quotes "They have spent ten years on invoicing." as the founder's view, its
  second part is a bracketed ask, and its third part is the founder's plug-in line. It never says Suite S will not or
  cannot build scheduling.
- The substitutes story starts from "Before us, most of our customers planned routes on a whiteboard and by phone." with
  a bracketed ask for what it cost them.

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass, with shortfalls against the expected answer (its grader called the run partial overall).** It met every clause
of the pass sentence above. It placed Product P at Direct, Product Q at Indirect, Suite S at Adjacent as the platform
kind and the whiteboard and phone at Substitutes, each from the founder's own lines with their sources, and named no
other company. It kept "Product Q is clunky." on the map as unverified and off the slide, where the line against Product
Q ends in a bracketed ask. It flagged the one-company claim with the no-competitors pattern, "Fit for small crews" as an
axis named after the founder's own description, and the company at 5 on both axes, alone in the best corner. It stated
the halves and drew the 2x2 by them alone, with Product Q on the line and Suite S and the whiteboard listed as not
placed. It proposed a 3 anchor for setup effort and a third axis with anchors at 1, 3 and 5 and buyer evidence, placing
no one on it. It dropped one objection by quoting the founder's whiteboard line, and it added nothing into a score.
Short of the expected answer: the objection it dropped is the one the expected answer keeps. The lenses objected to
"We're the only route planner built for small plumbing firms." and the refute pass dropped that objection as answered by
the whiteboard line and the six-of-eight deals line, though the objected line is itself a pattern the skill's table
lists; the answer still flagged the line and replaced it with a new headline. The platform-risk lens never objected that
the slide has no answer if Suite S builds scheduling, so the expected drop that quotes the plug-in line could not
happen; its three platform objections were kept, which the material supports. It also marked the founder's unsourced
six-of-eight count unverified and worded its Product Q ask `[a customer's reason]`. The lenses ran as five subagents and
the refute pass in lean mode, one subagent per lens, since fourteen objections were raised. Since this run the skill
keeps an objection to a line that matches a pattern in its patterns table until the founder replaces that line, whatever
other line would answer it, and quotes that line in the fix. The eval has not been run again.

> Your competition slide is drafted below, but three things on it would not survive a partner's questions yet. Five independent lenses attacked your material and a second pass tested each objection against your own lines; 13 of 14 survived, all in the "weakens it" tier.
>
> [...]
>
> **Dropped**
>
> - Coverage and Substitutes, on the slide 6 line: "the only" reads as a founder who has not looked, with substitutes left out. Dropped, answered by "Before us, most of our customers planned routes on a whiteboard and by phone." and by the eight deals against Product P. Both lines now sit on the slide draft, and the "only" headline is gone.
>
> **How it ran:** the lenses ran as separate subagents. With more than eight objections, the refute pass ran one subagent per lens, which is less independent than one per objection. Ask if you want the full pass.
>
> ## The map
>
> | #   | Competitor           | Level                                        | The problem it solves                                               | Your facts                                                                | Source                                           |
> | --- | -------------------- | -------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------ |
> | C1  | Product P            | Direct                                       | "dispatch software for plumbing firms with 20 or more vans"         | "We won 6 of the 8 deals where Product P was also in the running."        | Their pricing page; the deal count is unverified |
> | C2  | Product Q            | Indirect                                     | "a job-tracking app many trades use"                                | "two prospects told us they tried it for routing"; "Product Q is clunky." | Those two calls; "clunky" is unverified          |
> | C3  | Suite S              | Adjacent (a platform the buyer already uses) | "the accounting app every firm we sell to already uses"             | "could add scheduling"; "They have spent ten years on invoicing."         | Unverified                                       |
> | C4  | Whiteboard and phone | Substitute                                   | "most of our customers planned routes on a whiteboard and by phone" | —                                                                         | Your onboarding calls                            |
>
> [...]
>
> ## Axes
>
> On every axis, 1 and 2 are the low half, 4 and 5 the high half, and 3 sits on the line.
>
> | Axis                                                   | 1                      | 3                                                                           | 5                               | Buyer evidence                                                                  |
> | ------------------------------------------------------ | ---------------------- | --------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------- |
> | Setup effort (yours)                                   | A consultant on site   | Proposed, for you to confirm: the firm sets it up itself after a setup call | Live the same day               | None given: [a buyer saying setup decided it]                                   |
> | Fit for small crews (yours)                            | Built for big fleets   | Not given                                                                   | Built for two to ten vans       | "We won 6 of the 8 deals where Product P was also in the running." (unverified) |
> | Route planning done for the firm (proposed third axis) | Tracks jobs; no routes | The firm plans routes by hand inside the tool                               | The tool plans the day's routes | "two prospects told us they tried it for routing"                               |
>
> [...]
>
> ## The platform-risk answer (Suite S)
>
> 1. **Why it has not (your view):** "They have spent ten years on invoicing." [your reason this has kept them from scheduling]
> 2. **What a feature would lack:** your view is that routing would remain to "sell on top". [what their scheduling would lack against your routing, and what shows it]
> 3. **If it does:** "If Suite S ships scheduling, we plug into it and sell the routing on top, as we already do with their invoice export." [the terms of that export today]
>
> ## The competition slide (draft, slide 6)
>
> **Headline:** Small plumbing firms pick us because they are live the same afternoon, with no setup call.
>
> [...]
>
> Product Q sits on the line between the two lower quadrants. Not placed: Suite S, whiteboard and phone.
>
> [...]
>
> ## Patterns a partner is likely to discount
>
> | Your line                                                      | Pattern                                   | What a partner is likely to hear                            | Fix                                                       |
> | -------------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------- |
> | "We're the only route planner built for small plumbing firms." | "The only company that"                   | The founder has not looked                                  | Replaced by the headline and four-level table             |
> | "shows the three logos"                                        | Logo grid with no reason                  | A list, not an answer                                       | The "why customers pick us" column                        |
> | "us 5 and 5"                                                   | Alone in the best corner; 5 on every axis | Axes picked for the position; placements nobody could check | Evidence per placement; the third axis; a weak spot owned |
> | "Fit for small crews … 5 means built for two to ten vans"      | Axis named after your own description     | Built so only you can top it                                | The proposed rename                                       |
> | Both axes, with no 3                                           | Missing anchors                           | Nothing to check in the middle                              | Confirm or rewrite the 3 anchors                          |
> | Slide 6 has no whiteboard                                      | Substitutes left out                      | Has not looked at what buyers do today                      | Now a row on the slide                                    |
> | "Product Q is clunky."                                         | Weakness with no source                   | Runs a competitor down                                      | Left off the slide                                        |
>
> [...]
>
> This is not investment, legal or tax advice. The competitor facts are yours to check before the deck goes out, and a lawyer should review comparative claims about named competitors before the deck is sent widely or published.
