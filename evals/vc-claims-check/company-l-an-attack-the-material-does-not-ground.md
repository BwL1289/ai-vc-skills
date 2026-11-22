# Eval 3: Company L, the refute pass keeps only grounded attacks

A test prompt for the `vc-claims-check` skill. The company is made up. "Expected answer" states the expected behaviour,
and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22). A run passes when the refute
pass keeps the attack the material grounds, drops one by quoting the founder's line that answers it, drops one that
rests on an outside fact, and invents nothing on the founder's behalf.

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

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-22, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass.** The distributor attack is kept, grounded on Appendix A; the CTO attack is dropped as answered by the footnote;
parts of attacks that rest on guesses outside the material (a hand-picked reference, lapsed shops, pilot stores counted
among the 62) are dropped as not grounded; nothing is totalled or invented. Those not-grounded drops are parts of
attacks, not a whole attack. A first run the same day, before this commit's change to the skeptic's brief, failed: the
skeptic judged the CTO line answered itself and never raised it, so nothing was dropped.

> I ran the skeptic and refute passes on your five lines; here is the result.
>
> ## Checked first
>
> **Slide 2 is the one claim a partner is likely to check first, and it does not hold up against your own appendix.** The skeptic ran as a separate subagent that saw only your material, and each attack then got its own refute pass.
>
> **Kept: the "strategic partnership"**
>
> - **Claim:** "Strategic partnership with the largest US bike distributor." (Deck, slide 2)
> - **Why first:** it is the headline distribution claim, near the front. If it overstates the relationship, a partner is likely to doubt the lines after it.
> - **Conflicting line:** "Distributor pilot: unpaid, 3 stores, no commitment after the pilot." (Deck, Appendix A)
> - **Discount pattern:** a pilot called a partnership. The first reference call to the distributor will say what the relationship is.
> - **Missing sources:** the pilot agreement and its end date, the distributor's consent to be described this way, and the basis for "the largest US bike distributor".
> - **Fix:** make slide 2 say what Appendix A says, for example: "Unpaid pilot with [distributor's name, if it agrees to be named]: 3 stores, no commitment after the pilot, ends [pilot end date]." Drop "largest" unless you can name the measure and source.
>
> **Dropped**
>
> - **"62 paying shops, $310 a month each, invoices available." (slide 4):** answered by "invoices available" in the same line. The suggestions that the price is blended, that some shops have lapsed, or that the 3 unpaid pilot stores are counted in the 62 are not grounded: nothing you wrote says so.
> - **"Our CTO led the inventory platform at a national sporting-goods retailer for 6 years." (slide 6):** answered by the footnote, "Her former manager has agreed to take reference calls." The objection that the reference was hand-picked is not grounded in your material.
>
> ## Claims table
>
> | #   | Claim                                                                                   | Where      | Class               | Evidence you can show         | Agrees across the materials?              | Verdict                                    | Fix                                                                     |
> | --- | --------------------------------------------------------------------------------------- | ---------- | ------------------- | ----------------------------- | ----------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------- |
> | 1   | "Strategic partnership with the largest US bike distributor."                           | Slide 2    | Customer or partner | None named                    | No: Appendix A calls it an unpaid pilot   | **Contradicted** (also will be discounted) | Rewrite as the pilot it is, as above                                    |
> | 2   | "the largest US bike distributor"                                                       | Slide 2    | Customer or partner | None named                    | Stated once                               | **Needs a source**                         | [the measure and source for "largest"], or drop it                      |
> | 3   | "Distributor pilot: unpaid, 3 stores, no commitment after the pilot."                   | Appendix A | Customer or partner | None named                    | Conflicts with slide 2; keep this version | **Needs a source**                         | [the pilot agreement and its end date]                                  |
> | 4   | "62 paying shops, $310 a month each, invoices available."                               | Slide 4    | Figure              | Invoices                      | Stated once                               | **Supported**                              | Have the invoices ready; a partner will ask for them                    |
> | 5   | "Our CTO led the inventory platform at a national sporting-goods retailer for 6 years." | Slide 6    | Team credential     | Former manager as a reference | Stated once                               | **Supported**                              | Name the retailer on the slide if you can; a partner will take the call |
>
> [...]
>
> The pattern used here, a pilot called a partnership, is the skill's own judgment and has no public source behind it. The skeptic-then-refute review is also the skill's own method.
>
> This is not investment, legal or tax advice. Customers and partners named in your materials should have agreed to be named, and a lawyer should review the materials before you send them widely.
