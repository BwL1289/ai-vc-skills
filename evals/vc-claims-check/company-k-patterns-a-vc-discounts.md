# Eval 2: Company K, the patterns a VC discounts

A test prompt for the `vc-claims-check` skill. The company is made up. "Expected answer" states the expected behaviour,
and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22). A run passes when each
pattern is flagged Will be discounted with its source (or marked unverified), every fix uses only the founder's facts or
a bracketed ask, and no figure is computed. The verdict is Pass when every clause of that sentence is met, Partial when
exactly one clause is missed or met only in part, and Fail when two or more are missed; a shortfall against the other
points of the expected answer is noted but does not change the verdict.

## Prompt

> Fact-check my deck before Monday. Slide 2: "Company K is an AI-powered scheduling assistant for dental clinics."
> Slide 3: "The global dental market is $40B (industry report); we only need 1% of it." Slide 4: "We have no
> competitors." Slide 6: "$1.2M in revenue from signed letters of intent." Slide 7, Team: "Advisors: a former chief
> dental officer and two well-known SaaS founders. Our CEO is a world-class operator." We can show the signed letters
> of intent. We haven't decided the size of the raise yet.

## Expected tool call

None: no `equity_deal_check` call. The prompt states no deal terms; the size of the raise goes to the open asks.

## Expected answer

- "$1.2M in revenue from signed letters of intent." is Will be discounted (a16z "16 Startup Metrics", item 1):
  letters of intent are not revenue. The evidence the founder can show, the letters, supports that they exist, not
  that they are revenue. The fix names the letters of intent for what they are, with their own figure as stated.
- "The global dental market is $40B (industry report); we only need 1% of it." is Will be discounted (YC seven
  questions, 2; YC seed fundraising guide): top-down only. The answer does not work out 1% of $40B. The fix is a
  bottom-up size from the founder's own figures, as bracketed asks: `[number of clinics you can sell to]`,
  `[what each pays a year]`. It also asks for the report's publisher and year.
- "We have no competitors." is Will be discounted, with the fix to name the alternatives in the four groups (marked
  unverified as a grouping), including clinics doing it by phone or by hand. It names no competitor itself.
- "AI-powered scheduling assistant" is Will be discounted, marked unverified, with an ask: what the model does that
  the product could not do without it.
- The advisors line and "world-class operator" are Will be discounted (YC seed deck guide; YC "How to Apply"), with
  asks for one specific achievement for the CEO and what each advisor does for the company.
- The skeptic's top attack is the letters-of-intent line; it is kept as grounded (a discount pattern) even though
  the founder can show the letters, and it leads the answer under Checked first, never under Dropped.
- The close says the answer is not investment advice and that named customers should agree to be named.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-22, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Partial: one clause met only in part.** The letters of intent lead under Checked first; the market size, no
competitors, the advisors and the world-class operator are Will be discounted; no 1% is worked out. The first clause is
missed for one pattern: the AI-powered line came back Needs a source, not Will be discounted, because the pattern then
applied only where the product would work the same without a model, which the founder's text cannot settle. Since this
run the pattern is an AI-powered label with nothing that says what the model does; the eval has not been run again.

> Nothing in the deck contradicts itself, but five of the six claims use wording a partner is likely to discount, and the sixth needs evidence. I checked only your wording and the evidence you named: I haven't seen the letters of intent and looked nothing up, so this doesn't say whether any claim is true.
>
> ## Checked first
>
> An independent skeptic pass (run as a subagent) picked these three, and a separate refute pass kept all of them.
>
> 1. **Slide 6: "$1.2M in revenue from signed letters of intent."** This is your only traction figure, and it calls letters of intent revenue. Showing the signed letters proves they exist, not that the money was earned. A partner is likely to ask whether they are binding and what has been invoiced or paid.
>
>    - **Fix:** "Signed letters of intent: $1.2M `[number of clinics, period covered, binding or not]`. Revenue to date: `[figure and period]`."
>
> 2. **Slide 4: "We have no competitors."** This reads as either the need isn't real or you haven't looked. The deck also never says what clinics use for scheduling today.
>
>    - **Fix:** replace it with what your clinics use now: `[the same kind of product]`, `[practice software that could add this]`, `[front-desk staff doing it by hand]`, and why the clinics that signed would switch.
>
> 3. **Slide 3: "The global dental market is $40B (industry report); we only need 1% of it."** There are three problems in this one line:
>    - **No source:** "(industry report)" names no publisher or date.
>    - **Top-down only:** "we only need 1%" never narrows to who will buy.
>    - **Wrong scope:** it sizes the whole dental market, not what clinics spend on scheduling.
>    - **Fix:** cut the 1% line and build the number bottom-up: `[number of clinics you can reach]`, `[price per clinic per year]`. Keep the $40B only as a cross-check, with `[publisher, year, definition]`.
>
> **Dropped:** one part of the second attack, that Slide 2 implies clinics already get scheduling done somehow. The deck never says that, so it was not grounded.
>
> ## Claims table
>
> Each claim appears once in one document, so there is nothing to disagree across materials.
>
> | #   | Claim                                                                        | Where   | Class            | Evidence you can show                   | Verdict            | Fix                                                                                                                              |
> | --- | ---------------------------------------------------------------------------- | ------- | ---------------- | --------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
> | 1   | "$1.2M in revenue from signed letters of intent."                            | Slide 6 | Figure           | Signed letters of intent                | Will be discounted | As above                                                                                                                         |
> | 2   | "We have no competitors."                                                    | Slide 4 | Competition      | None named                              | Will be discounted | As above                                                                                                                         |
> | 3   | "The global dental market is $40B (industry report); we only need 1% of it." | Slide 3 | Market size      | "industry report", no publisher or date | Will be discounted | As above                                                                                                                         |
> | 4   | "Advisors: a former chief dental officer and two well-known SaaS founders."  | Slide 7 | Team credential  | None named                              | Will be discounted | Put founders first. List an advisor only with `[name]` and `[what they do for the company]`, and confirm they agree to be named. |
> | 5   | "Our CEO is a world-class operator."                                         | Slide 7 | Team credential  | None named                              | Will be discounted | Replace the adjective with one checkable achievement: `[role, company, result]`.                                                 |
> | 6   | "Company K is an AI-powered scheduling assistant for dental clinics."        | Slide 2 | Technology claim | None named                              | Needs a source     | Say `[what the model does that the product could not do without it]` and `[what shows it]`, or drop "AI-powered".                |
>
> [...]
>
> This is not investment, legal or tax advice. Have a lawyer review the deck before it goes out widely, and make sure every clinic and advisor you name has agreed to be named.
