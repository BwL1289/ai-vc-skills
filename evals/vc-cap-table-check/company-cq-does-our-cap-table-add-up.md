# Eval 1: Company CQ, "does our cap table add up?"

A test prompt for the `vc-cap-table-check` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted
from what `equity_calculator cap_table_check` printed for these inputs; none is typed by hand. A run passes when it
makes the one tool call below (field order free, percents as strings with the table's places), leads with the verdict,
shows the tie-outs with the tool's figures as printed, names the questions for the company's lawyer that the flags
raise, never says whether a share was validly issued, and computes nothing in its own text.

## Prompt

> Here's our cap table before it goes into the data room. Does it add up? Common: Founder A 4,500,000 (45.00%),
> Founder B 3,500,000 (35.00%), our first engineer, who left last year, 250,000 vested (2.50%); 8,000,000 common
> authorised. Seed preferred 1,000,000 (10.00%), 1,000,000 authorised. Options granted 500,000 (5.00%), unissued pool
> 250,000 (2.50%); the plan reserves 750,000. Warrants from our bank 100,000 (1.00%). Total fully diluted: 10,000,000.
> We also have a $1M post-money SAFE at a $12M cap. The percents are of fully diluted.

## Expected tool call

`equity_cap_table_check`, once:

```json
{
  "inputs": {
    "classes": [
      {
        "kind": "common",
        "authorised_shares": 8000000
      },
      {
        "kind": "preferred",
        "shares": 1000000,
        "authorised_shares": 1000000,
        "stated_percent": "10.00"
      },
      {
        "kind": "options_granted",
        "shares": 500000,
        "stated_percent": "5.00"
      },
      {
        "kind": "options_unissued",
        "shares": 250000,
        "stated_percent": "2.50"
      },
      {
        "kind": "warrants",
        "shares": 100000,
        "stated_percent": "1.00"
      }
    ],
    "holders": [
      {
        "share_class": 1,
        "shares": 4500000,
        "stated_percent": "45.00",
        "founder": true
      },
      {
        "share_class": 1,
        "shares": 3500000,
        "stated_percent": "35.00",
        "founder": true
      },
      {
        "share_class": 1,
        "shares": 250000,
        "stated_percent": "2.50",
        "departed": true
      }
    ],
    "stated_fully_diluted_shares": 10000000,
    "stated_percent_basis": "fully_diluted",
    "option_plan_reserve": 750000,
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "1000000",
        "valuation_cap": "12000000"
      }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Fully diluted shares (FD)                                                                          10,100,000  every class
  Holder line 1 (class 1, common): of fully diluted                                                    44.5545%  shares/FD
  Class 1 (common): authorised left                                                                    -250,000  authorised - shares (below 0: over)
  Authorised common left over FD                                                                     -2,100,000  authorised common - FD
  Departed holders: of fully diluted                                                                    2.4752%  departed lines' shares/FD
  Fully diluted shares: the table says                                                               10,000,000  given
  Fully diluted shares: difference                                                                      100,000  computed - stated
  Fully diluted shares: verdict                                                                        mismatch  consistent only when equal
  Holder line 1 (class 1, common) percent: the table says                                              45.0000%  given
  Holder line 1 (class 1, common) percent: the calculator gives                                        44.5545%  shares/FD
  Holder line 1 (class 1, common) percent: rounds to the table's "45.00"                                     no  the computed figure, rounded half away from zero to the places the table writes, is the table's
  Holder line 1 (class 1, common) percent: verdict                                                     mismatch  within the tolerance, or rounding to the table's, is consistent
  Holder line 2 (class 1, common) percent: the calculator gives                                        34.6535%  shares/FD
  Holder line 2 (class 1, common) percent: verdict                                                     mismatch  within the tolerance, or rounding to the table's, is consistent
  Class 5 (warrants) percent: the calculator gives                                                      0.9901%  shares/FD
  Class 5 (warrants) percent: verdict                                                                  mismatch  within the tolerance, or rounding to the table's, is consistent
  Percent column, line by line: the table says                                                        101.0000%  given
  Percent column, line by line: what rounding explains                                                  0.0350%  half the last place of each
  Percent column, line by line: verdict                                                                mismatch  a gap within what rounding explains, plus the tolerance for each, is consistent
  Flag                                                                                      percents_do_not_sum  The stated percents cannot all be roundings of shares that add up to 100%: a line is missing, counted twice, or on another basis; find it before the table goes to an investor
  Flag                                                                                          over_authorised  A class has issued more shares than the authorised figure given, or the option plan has granted and reserved more than its reserve; ask the company's lawyer whether the charter or the plan was amended, as shares past the authorised number may not be validly issued
  Flag                                                                    common_authorised_below_fully_diluted  Authorised common is below the fully diluted shares, all of which would be common once converted or exercised; ask the company's lawyer whether the charter reserves enough common
  Flag                                                                          unconverted_instruments_present  SAFEs or notes are outstanding and hold no shares yet, so every percent here falls when they convert; list them for investors, and ask the company's lawyer to confirm their terms
  Flag                                                                                   departed_holders_share  People who have left hold shares (the departed holders' line above); investors often ask about it, and the company's lawyer can say whether any repurchase right or unvested shares were handled
  Overall verdict                                                                                      mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- It leads with the verdict: the figures the table states do not all match. The classes add up to 10,100,000 fully
  diluted shares, not the table's 10,000,000 (a difference of 100,000), and every percent misses at the two places it
  is written with: Founder A holds 44.5545%, not 45.00%, and Founder B 34.6535%, not 35.00%.
- It shows the tie-outs table (the table says, the calculator gives, the difference, consistent or not) with the
  tool's figures as printed, and says the percent column, read line by line, adds up to 101.0000%, past the 0.0350%
  that rounding can explain (`percents_do_not_sum`). It does not guess which line is wrong: it asks the founder to
  find the line that is missing, counted twice or on another basis, as the flag says.
- It says common has 250,000 shares past its authorised 8,000,000 (`over_authorised`) and authorised common is
  2,100,000 short of the fully diluted shares (`common_authorised_below_fully_diluted`), and asks, as questions for
  the company's lawyer, whether the charter was amended to authorise them and whether it reserves enough common. It
  never says the shares were or were not validly issued.
- It gives the departed engineer's share as 2.4752% of the fully diluted shares (`departed_holders_share`) and asks
  whether any unvested shares were bought back; it lists the SAFE as outstanding (`unconverted_instruments_present`)
  and says no percent counts it until a priced round converts it, offering a preview at the next round the founder
  expects, never at an assumed price.
- It quotes the assumptions it leans on: `fully_diluted_basis`, `preferred_as_converted` and `legal_validity`.
