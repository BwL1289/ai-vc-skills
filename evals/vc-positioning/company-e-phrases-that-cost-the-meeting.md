# Eval 1: Company E, the phrases that cost the meeting

A test prompt for the `vc-positioning` skill. The company is made up. This eval states the expected behaviour; it is
not a recorded run. A run passes when it makes no calculator call, runs the adversarial review, keeps the objections
below with the founder's own line quoted, and adds no fact the founder did not give.

## Prompt

> Tighten my pitch before I go out to raise next month. This is how I open: "Company E is an AI-powered platform
> transforming accounting for small businesses. We have no competitors. The small-business accounting market is
> $50B, and we only need 1% of the market to be a $500M company. Our projections are conservative, and we have strong
> traction." We're raising a seed round from angels and seed funds.

## Expected tool call

None: no `equity_deal_check` call. The founder gives no amount, valuation, cash or burn, so there are no ask figures
to check.

## Expected answer

- The adversarial review runs: the attack lenses, each named by what it tests, then a refute pass per objection.
- These objections survive the refute pass, each with the founder's line quoted word for word, why a partner is likely
  to read it as a reason to pass, and a rewrite or the evidence to add:
  - "We have no competitors." (competition and wedge), ranked as ends the meeting.
  - "we only need 1% of the market to be a $500M company" (market and why now).
  - "Company E is an AI-powered platform transforming accounting for small businesses." (clarity and problem).
  - "we have strong traction" with no number (traction and proof).
- None of these is dropped: nothing in the material names an alternative, counts buyers bottom-up, or gives a
  traction figure.
- "Our projections are conservative" is flagged on the say-and-avoid list and labelled unverified.
- It neither confirms nor recomputes the $500M and does not work out 1% of $50B; it asks for who exactly buys, how many
  of them there are, and what each pays.
- The rewrites contain no number, customer or growth claim the founder did not give. Traction is a bracketed ask, such
  as `[paying customers today]`, and competition is `[what customers use today instead]`.
- The team has no line to quote, so it is a gap in the open asks, not an objection.
- The founder names no existing investor, so the prep script gives the substitute branch and asks who it could be.
- No sentence speaks as an investor.
