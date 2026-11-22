# Eval 3: Company L, the refute pass keeps only grounded attacks

A test prompt for the `vc-claims-check` skill. The company is made up. This eval states the expected behaviour; it is
not a recorded run. A run passes when the refute pass keeps the attack the material grounds, drops one by quoting the
founder's line that answers it, drops one that rests on an outside fact, and invents nothing on the founder's behalf.

## Prompt

> What will a partner check first? Company L sells inventory software to independent bike shops. Deck, slide 2:
> "Strategic partnership with the largest US bike distributor." Appendix A: "Distributor pilot: unpaid, 3 stores, no
> commitment after the pilot." Slide 4: "62 paying shops, $310 a month each, invoices available." Slide 6: "Our CTO
> led the inventory platform at a national sporting-goods retailer for 6 years." Slide 6 footnote: "Her former manager
> has agreed to take reference calls."

## Expected tool call

None: no `equity_deal_check` call. The prompt states no deal terms.

## Expected answer

- The skeptic's first attack is on "Strategic partnership with the largest US bike distributor." The refute pass
  keeps it as Kept, grounded: Appendix A, quoted as "Distributor pilot: unpaid, 3 stores, no commitment after the
  pilot.", states the relationship differently. The claim is Contradicted, and the fix names it as an unpaid pilot.
  The word largest also needs a source, which goes into the fix.
- An attack on the CTO's credential (a partner will want to confirm the role) is listed under Dropped, answered,
  quoting the founder's line "Her former manager has agreed to take reference calls." The credential is Supported.
- An attack that rests on anything outside the material, such as a claim about the bike market or about the
  distributor, is listed under Dropped, not grounded. The answer adds no market fact of its own.
- "62 paying shops, $310 a month each, invoices available." is Supported by the invoices the founder names. The answer
  does not total the shops' monthly payments.
- The close says the distributor should agree to be named before the deck goes out.
