# Eval 2: Company K, the patterns a VC discounts

A test prompt for the `vc-claims-check` skill. The company is made up. This eval states the expected behaviour; it is
not a recorded run. A run passes when each pattern is flagged Will be discounted with its source (or marked
unverified), every fix uses only the founder's facts or a bracketed ask, and no figure is computed.

## Prompt

> Fact-check my deck before Monday. Slide 2: "Company K is an AI-powered scheduling assistant for dental clinics."
> Slide 3: "The global dental market is $40B (industry report); we only need 1% of it." Slide 4: "We have no
> competitors." Slide 6: "$1.2M in revenue from signed letters of intent." Slide 7, Team: "Advisors: a former chief
> dental officer and two well-known SaaS founders. Our CEO is a world-class operator." We can show the signed letters
> of intent. We haven't decided the size of the raise yet.

## Expected tool call

None: no `equity_deal_check` call. The prompt states no deal terms; the size of the raise goes to the open asks.

## Expected answer

- "$1.2M in revenue from signed letters of intent." is Will be discounted (a16z "16 Startup Metrics", items 1 and 2):
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
- The skeptic's top attack is the letters-of-intent line; it is kept as grounded (a discount pattern) and leads the
  answer.
- The close says the answer is not investment advice and that named customers should agree to be named.
