# Eval 1: Company AC, a cap table the deck misstates

A test prompt for the `vc-diligence-questions` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator deal_check` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it makes the one tool call below
(field order free, money and percents as strings, share counts as whole numbers), puts the founders' mismatch first
among the ranked questions without refuting it, relays the two flag codes in the tool's words, quotes the founders'
percent today and the cap table's own sum as not checked, marks the cap table Contradicted in the data-room checklist,
and computes nothing in its own text. A field passed at its default value (here `pool_timing`) may be left out.

## Prompt

> A partner asked for our data room after Tuesday's first meeting; get me ready for diligence. Company AC makes
> inspection software for elevator maintenance firms. We're raising a $3M priced seed at a $12M pre-money, and
> investors get 20%. The deck says "Founders own 75% today." and "Founders keep 60% after the round." Cap table:
> founders 6,000,000 shares; granted options 800,000; unissued pool 700,000; an angel's common 500,000; 8,000,000
> fully diluted, the SAFE not counted. One SAFE: $500k at an $8M post-money cap. The term sheet tops the pool up to 10%
> after the round, in the pre-money. Documents we have: the cap table spreadsheet, the signed SAFE, the term sheet, our
> incorporation documents.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "12000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 8000000,
    "unissued_pool_shares": 700000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "500000",
        "valuation_cap": "8000000"
      }
    ],
    "holder_shares": 6000000,
    "stated_holder_percent": "60"
  }
}
```

## What the calculator prints (excerpt)

```text
  After: holder group                                                        53.6170%  h·kept
  After: SAFE 1                                                               4.7660%  shares/T
  After: option pool                                                         10.0000%  (U + P)/T
  Investors' percent: the calculator gives                                   20.0000%  the investor's cap-table share
  Investors' percent: verdict                                              consistent  within the tolerance is consistent
  Holder group's percent after: the deck says                                60.0000%  given
  Holder group's percent after: the calculator gives                         53.6170%  h·(share every pre-round share keeps)
  Holder group's percent after: difference                                   -6.3830%  computed - stated
  Holder group's percent after: verdict                                      mismatch  within the tolerance is consistent
  A VC is likely to ask                                pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
  A VC is likely to ask                               conversions_bought_by_pre_money  SAFE and note shares come out of the pre-round holders, not the new investor, so their stake falls by more than the percent sold; a VC reads the cap table this way
  Overall verdict                                                            mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The founders' mismatch leads the ranked list as stops the process, in Financials and cap table, and is not put
  through the refute pass: "Founders keep 60% after the round." (the tool prints 60.0000%, given) against the tool's
  53.6170%, a difference of -6.3830%. The `conversions_bought_by_pre_money` and `pool_in_pre_money_lowers_price`
  codes are relayed in the tool's words as the reasons a partner is likely to give. The draft answer uses only the
  tool's figure, asks the founder to correct the deck line, and brackets
  `[the pro forma cap table after the round, from your lawyer]`.
- "Founders own 75% today." is quoted and marked "not checked: no tool adds up a cap table"; so is whether the four
  holder rows add up to the fully diluted total. No division or sum of shares appears.
- The investors' percent is consistent (20.0000%) and is not raised.
- Step 2 asks nothing about the fully diluted basis, since the prompt states the SAFE is not counted.
- Data room: the cap table (FIN-D2) is Contradicted (the deck against the tool); the signed SAFE and the term sheet
  (FIN-D3) and the incorporation documents (LEG-D1) are Ready as named, with the note that a partner will open them;
  the work assignments (LEG-D2), the founders' stock agreements (LEG-D3) and the disputes list (LEG-D4) are Missing,
  each with a bracketed ask, and so are the founder bios (TEAM-D1), the product walkthrough (PROD-D1) and the
  executive summary (FIN-D1). These are the core set, the pre-seed rows. No document on the list and no kept question
  points to a seed row, so the seed rows are named once, in one line, as "if asked", and none is marked Missing; no
  Series A row is listed.
- The area prep list for Financials and cap table cites CAP-1 to CAP-4 by ID; for Legal, LEGAL-2 to LEGAL-5.
- No arithmetic in its own text beyond the tool's values; no score and no readiness percentage.
