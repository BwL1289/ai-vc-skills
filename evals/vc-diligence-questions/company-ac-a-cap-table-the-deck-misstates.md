# Eval 1: Company AC, a cap table the deck misstates

A test prompt for the `vc-diligence-questions` skill. The company is made up. The tool call and the excerpt are from a
real `equity_calculator deal_check` run with these inputs. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when it makes the
one tool call below (field order free, money and percents as strings, share counts as whole numbers), puts the founders'
mismatch first among the ranked questions without refuting it, relays the two flag codes with their meanings from the
skill's flag table, quotes the founders' percent today and the cap table's own sum as not checked, marks the cap table
Contradicted in the data-room checklist, and computes nothing in its own text. The verdict is Pass when every clause of
that sentence is met, Partial when exactly one clause is missed or met only in part, and Fail when two or more are
missed; a shortfall against the other points of the expected answer is noted but does not change the verdict. A field
passed at its default value (here `pool_timing`) may be left out. The recorded run is graded against the pass sentence
this eval had then, which asked for the two flag codes "in the tool's words" where it now asks for their meanings from
the skill's flag table. It is a Fail: it explained the flags in its own words and said what the deck's percents were
made of. It would be a Fail against today's sentence too. The skill was changed after that run (see "Recorded answer").

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
  After: holder group                                                             53.6170%  h·kept
  After: SAFE 1                                                                    4.7660%  shares/T
  After: option pool                                                              10.0000%  (U + P)/T
  Investors' percent: the calculator gives                                        20.0000%  the investor's cap-table share
  Investors' percent: verdict                                                   consistent  within the tolerance, or rounding to the deck's, is consistent
  Holder group's percent after: the deck says                                     60.0000%  given
  Holder group's percent after: the calculator gives                              53.6170%  h·(share every pre-round share keeps)
  Holder group's percent after: difference                                        -6.3830%  computed - stated
  Holder group's percent after: verdict                                           mismatch  within the tolerance, or rounding to the deck's, is consistent
  A VC is likely to ask                                     pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
  A VC is likely to ask                                    conversions_bought_by_pre_money  SAFE and note shares come out of the pre-round holders, not the new investor, so their stake falls by more than the percent sold; a VC reads the cap table this way
  Overall verdict                                                                 mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The founders' mismatch heads the ranked list, ahead of the tiers and with no tier, in Financials and cap table, and
  is not put through the refute pass: "Founders keep 60% after the round." (the tool prints 60.0000%, given) against
  the tool's 53.6170%, a difference of -6.3830%. The `conversions_bought_by_pre_money` and
  `pool_in_pre_money_lowers_price` codes are relayed with their meanings from the skill's flag table (over MCP the
  tool returns the codes alone) as the reasons a partner is likely to give. The draft answer uses only the tool's
  figure, then asks for `[the corrected deck line]` and `[the pro forma cap table after the round, from your lawyer]`;
  it never says the deck was corrected or that a pro forma is in the data room.
- "Founders own 75% today." is quoted and marked "not checked: no tool adds up a cap table"; so is whether the four
  holder rows add up to the fully diluted total. No sentence says what the deck's 75% or 60% is made of or how the
  deck reached it; where a question needs that, the draft asks
  `[how the deck's figure was worked out, and on what basis]`. No division or sum of shares appears.
- The investors' percent is consistent (20.0000%). A lens question on it that survives the refute pass is minor at
  most, and its draft quotes the tool's value and the assumption row it rests on, never stating the assumption as what
  the term sheet says.
- Step 2 asks nothing about the fully diluted basis, since the prompt states the SAFE is not counted.
- Data room: the cap table (FIN-D2) is Contradicted (the deck against the tool); the signed SAFE and the term sheet
  (FIN-D3) and the incorporation documents (LEG-D1) are Ready as named, with the note that a partner will open them;
  the work assignments (LEG-D2), the founders' stock agreements (LEG-D3) and the disputes list (LEG-D4) are Missing,
  each with a bracketed ask, and so are the founder bios (TEAM-D1), the product walkthrough (PROD-D1) and the
  executive summary (FIN-D1). These are the core set, the pre-seed rows. No document on the list points to a seed row.
  A seed row is listed only when a kept question's draft names it as the row that settles that question (a question
  on the 800,000 granted options may name the option plan, FIN-D8, and the approvals, LEG-D5), and then it is Missing
  with its bracketed ask; every other seed row is named once, in one line, as "if asked", each by its ID, never as
  Missing; no Series A row is listed.
- The area prep list for Financials and cap table cites CAP-1 to CAP-4 by ID; for Legal, LEGAL-2 to LEGAL-5.
- No arithmetic in its own text beyond the tool's values; no score and no readiness percentage. The answer closes with
  the skill's fixed closing sentence.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings, when
this eval asked for the two flag codes "in the tool's words". The answer is trimmed; [...] marks each cut.

**Fail, against the pass sentence this eval had then: two clauses missed.** It made the one call with the expected
arguments, put the founders' mismatch first without refuting it, quoted "Founders own 75% today." and the cap table's
own sum as not checked, and marked the cap table Contradicted; it also ran the six lenses as parallel subagents and then
one refute subagent per lens question. It missed two clauses. It relayed the two flag codes with meanings in its own
words, not the tool's, since over MCP the tool returned the codes alone. And it computed in its own text: it said what
the deck's two percents were made of ("The 75% is founders' shares over the 8,000,000 fully diluted total"), which is
division done in its own head. Against today's sentence the same two clauses are missed, the first because its meanings
are not the skill's flag table's. Short of the expected answer as well: its draft for the mismatch said the deck had
been corrected and a pro forma was in the data room, though the founder named neither, and it marked three seed rows
Missing because its own drafts named them. Since this run the skill forbids saying what a stated percent is made of,
gives a mismatch's draft a fixed shape, carries a meaning for every flag code, and lists a seed row only when a draft
names it as the row that settles the question, which this eval now accepts. The eval has not been run again.

> **Fix the deck before you open the data room.** "Founders keep 60% after the round." does not survive your own cap table: the calculator gives the founders 53.6170% after the round, 6.3830 points lower. The signed SAFE and the pool top-up both come out of the existing holders, and the 60% counts neither. [...]
>
> ## Ranked questions
>
> | #   | Tier              | Area                            | Your line                            | The question                                                                 | What settles it                                                                                   |
> | --- | ----------------- | ------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
> | 1   | Stops the process | Financials and cap table; Legal | "Founders keep 60% after the round." | What does the cap table look like after this round? (ASK-7)                  | A pro forma cap table with the SAFE converted and the pool topped up, and the deck line corrected |
> | 2   | Slows it          | Financials and cap table; Legal | "Founders own 75% today."            | On what basis is "today" stated, and why does it leave out the SAFE? (CAP-1) | The cap table with its basis stated and a SAFE row; the deck line relabelled                      |
>
> [...]
>
> ## Draft answers
>
> Bracketed items are facts only you can supply.
>
> 1. **After-round ownership.** "Our deck's 60% was wrong and we have corrected it. With the $500k SAFE converting at its $8M post-money cap and the pool topped up to 10% in the pre-money, the founders hold 53.6170% after the round. New investors hold 20.0000%, the SAFE holder 4.7660% and the pool 10.0000%. The pro forma is in the data room." Data room: FIN-D2.
> 2. **75% today.** "The 75% is founders' shares over the 8,000,000 fully diluted total, which leaves the SAFE out. [State the figure with the SAFE counted, or relabel the line 'before SAFE conversion'.]" Data room: FIN-D2.
>
> [...]
>
> | LEG-D5 Approvals for every share, option and SAFE | Records behind each row | Missing | [board and stockholder approvals] |
> | FIN-D8 Option plan and grant list | Options granted and promised | Missing | [the plan and the list] |
> | MKT-D1 Source of the buyer count | Who buys and how many | Missing | [the count and its source] |
>
> [...]
>
> - **Flag `pool_in_pre_money_lowers_price`:** the new pool is made inside the pre-money valuation, before the round. Of the $12M, $561,702.13 pays for the new pool and $938,297.87 for the existing unissued pool.
> - **Flag `conversions_bought_by_pre_money`:** the pre-money buys every converted SAFE share; $714,893.62 of the $12M pays for the SAFE's shares.
