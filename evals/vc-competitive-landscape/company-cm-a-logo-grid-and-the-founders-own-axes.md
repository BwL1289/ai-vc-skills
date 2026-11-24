# Eval 1: Company CM, a logo grid, the founder's own axes and a platform answer the material gives

A test prompt for the `vc-competitive-landscape` skill. The company and the names are made up. The answer states the
expected behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it
places each named competitor at a level using only the founder's facts, keeps the unverified fact off the slide, flags
the one-company claim, the axis built around the founder's own product and the company at the top of every axis, draws
the 2x2 from the founder's placements by the halves alone, proposes a third axis with its anchors and places no one on
it, drops an objection by quoting the founder's line that answers it, and adds nothing into a score.

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
