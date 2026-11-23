# Eval 1: Company E, the phrases that cost the meeting

A test prompt for the `vc-positioning` skill. The company is made up. "Expected answer" states the expected behaviour,
and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22). A run passes when it makes no
calculator call, runs the adversarial review, keeps the objections below with the founder's own line quoted, and adds no
fact the founder did not give. The verdict is Pass when every clause of that sentence is met, Partial when exactly one
clause is missed or met only in part, and Fail when two or more are missed; a shortfall against the other points of the
expected answer is noted but does not change the verdict.

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

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-22, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Partial: one clause met only in part.** It made no calculator call, kept all four objections with the founder's lines
quoted, flagged "Our projections are conservative" as unverified and added no fact. It ran the adversarial review only
in part: it ran the six lenses inline in one agent although it had a subagent tool, and gave no refute pass per
objection. Since this run the skill says to use subagents however short the material; the eval has not been run again.

> Almost every sentence in this opening is a phrase investors discount, and the opening contains no checkable fact about the company. I can restructure it, but the facts have to come from you, so the rewrite below has bracketed gaps for you to fill.
>
> ## Biggest issues
>
> 1. **"We have no competitors."** A partner is likely to hear that the market isn't real or that you haven't looked.
> 2. **"We have strong traction."** With no number, this reads as a figure being hidden.
> 3. **"We only need 1% of the market."** This is top-down sizing that never says who actually buys.
>
> ## Adversarial review
>
> I ran the six lenses inline rather than as separate subagents, since the material is five sentences, so they are less independent than they would be. No objection was dropped, because nothing elsewhere in the opening answers any of them. The team lens found nothing to attack because the opening doesn't mention the team.
>
> | Rank | Tier             | Lens                  | Your line                                                             | Why a partner reads it that way                                                                       | Rewrite or evidence to add                                                                                                                    |
> | ---- | ---------------- | --------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
> | 1    | Ends the meeting | Competition and wedge | "We have no competitors."                                             | Small businesses already do their accounting somehow, and whatever they use is your competition.      | "Today our customers use [what they use now: existing software, a bookkeeper, spreadsheets]. They switch to us because [specific reason]."    |
> | 2    | Ends the meeting | Traction and proof    | "we have strong traction"                                             | An adjective in place of a number suggests the number is weak.                                        | "[N paying customers], [monthly recurring revenue], growing [X% month over month] over [period]."                                             |
> | 3    | Weakens it       | Market and why now    | "we only need 1% of the market to be a $500M company"                 | It doesn't say how you'd get any 1%. "$500M company" is also ambiguous between revenue and valuation. | "There are [number] of [specific kind of small business]; each pays us [price per year]."                                                     |
> | 4    | Weakens it       | Clarity and problem   | "an AI-powered platform transforming accounting for small businesses" | A listener can't repeat back what the product does, and many other pitches open the same way.         | "Company E [does specific task, e.g. closes the monthly books] for [specific kind of small business], so they don't need [what it replaces]." |
> | 5    | Weakens it       | Traction and proof    | "Our projections are conservative"                                    | Nobody can check this claim, and every founder makes it.                                              | Cut it. If asked, show the two or three assumptions that drive the plan.                                                                      |
>
> [...]
>
> ## Say and avoid
>
> | Avoid                               | Say instead                                       | Source                                                      |
> | ----------------------------------- | ------------------------------------------------- | ----------------------------------------------------------- |
> | "No competitors"                    | The named alternatives and why customers pick you | Sequoia business-plan outline; Chris Dixon, "The idea maze" |
> | "Only need 1%"                      | Who buys, how many, what each pays                | YC seed fundraising guide                                   |
> | "Projections are conservative"      | The assumptions behind the plan, if asked         | No public source checked; treat as a common signal          |
> | "AI-powered platform transforming…" | What it does, in plain words                      | YC "How to Apply"                                           |
> | "Strong traction"                   | A period-by-period figure with its definition     | a16z "16 Startup Metrics"                                   |
>
> ## Numbers
>
> - **"$50B" market:** not checked. It has no source, year or definition (software spend, or all accounting services?).
> - **"1%" and "$500M":** quoted as stated. Say whether $500M means revenue or valuation.
> - **The ask:** you gave no figures, so there was nothing to run through the deal calculator.
>
> [...]
>
> ## Prep session before you go wide
>
> Run this with an existing investor, or, if you have none, a founder who recently raised a seed or an angel who knows accounting software. Send the new opening a day or two ahead, then:
>
> [...]
>
> 9. Who can you run the prep session with?
>
> [...]
>
> This is not investment, legal or tax advice. Have a lawyer review materials before you send them widely, and get permission from any customer you name.
>
> [...]
