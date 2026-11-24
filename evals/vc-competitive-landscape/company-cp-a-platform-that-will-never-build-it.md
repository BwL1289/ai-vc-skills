# Eval 4: Company CP, a platform the founder says will never build it and an unverified tip

A test prompt for the `vc-competitive-landscape` skill. The company and the names are made up. The answer states the
expected behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it
flags the guess about the platform's plans, never writes that the platform will not build it, keeps the unverified tip
off the slide and lets it drop no objection, leaves the empty levels as asks without naming anyone, and draws the 2x2
from the founder's placements by the halves alone.

## Prompt

> Map our competitors and draft the slide; the question I dread is what happens if TillSuite builds this. Company CP
> sends stock alerts to independent bookshops. "TillSuite is the till system most of our shops already use." Shops
> told us: "TillSuite's stock screen is a list, not a warning." "Instead of us, shops check their shelves by hand on
> Monday mornings." (source: our first ten shop visits). My answer on TillSuite so far: "TillSuite will never build
> this, they're too big to care about bookshops." Also: "TillSuite has no plans for alerts." (a friend there told me;
> unverified). Our axes: Warning before a shelf runs out, where 1 means none and 5 means a same-day alert; and Setup
> for one shop, where 1 means a week of help and 5 means done alone in an hour. Our placements: us 5 and 4, TillSuite
> 1 and 5, checking shelves by hand 1 and 5.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- "TillSuite will never build this, they're too big to care about bookshops." is flagged as a guess about another
  company's plans. The platform-risk answer never says TillSuite will not or cannot build alerts, and gives the
  founder's reasons as the founder's view, or a bracketed ask for them.
- "TillSuite has no plans for alerts." stays on the map labelled unverified and stays off the slide. If the
  platform-risk lens objects that the founder gives no reason TillSuite has not built alerts, that line does not drop
  the objection: a fact marked unverified never answers an objection that asks for evidence, so it stays Kept with a
  bracketed ask for the founder's reasons.
- The map: TillSuite at Adjacent as the platform kind, quoting "TillSuite is the till system most of our shops
  already use.", and checking shelves by hand at Substitutes, quoting "Instead of us, shops check their shelves by hand
  on Monday mornings." with its source. Direct and Indirect are empty, each a bracketed ask, never a name the agent
  supplies.
- The platform-risk answer's second part may quote "TillSuite's stock screen is a list, not a warning." as the
  founder's evidence of the gap today, with a bracketed ask for what the company would still have if TillSuite added
  alerts; its third part is a bracketed ask, since the founder gives no plan for that case.
- The 2x2 follows the halves alone: Company CP in the high-high quadrant, and TillSuite and checking shelves by hand
  in the quadrant low on warning and high on setup. No total, average, rank or winner appears.
- The substitutes story and an `Instead of` line come from the founder's Monday-morning line, with a bracketed ask for
  what checking by hand costs a shop.
- No competitor or platform is named that the founder did not name, and nothing is added about TillSuite.
