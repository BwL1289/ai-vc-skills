# Eval 1: Company CQ, "does our cap table add up?"

A test prompt for the `vc-cap-table-check` skill. The company is made up. "Expected answer" states the expected
behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on 2026-11-24). Every figure under
"Expected answer" is pasted from what `equity_calculator cap_table_check` printed for these inputs; none is typed by
hand. A run passes when it makes the one tool call below (field order free, percents as strings with the table's
places), leads with the verdict, shows the tie-outs with the tool's figures as printed, names the questions for the
company's lawyer that the flags raise, never says whether a share was validly issued, and computes nothing in its own
text. The verdict is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or met
only in part, and Fail when two or more are missed; a shortfall against the other points of the expected answer is noted
but does not change the verdict. The recorded run is a Pass with shortfalls. The skill was changed after that run (see
"Recorded answer").

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
  Flag                                                                                          over_authorised  A class has issued more shares than the authorised figure given, or the option plan has granted and reserved more than its reserve; ask the company's lawyer whether the charter or the plan was amended to cover them
  Flag                                                                    common_authorised_below_fully_diluted  Authorised common is below the fully diluted shares, all of which would be common once converted or exercised; ask the company's lawyer whether the charter reserves enough common
  Flag                                                                          unconverted_instruments_present  SAFEs or notes are outstanding and hold no shares yet, so every percent here falls when they convert; list them for investors, and ask the company's lawyer to confirm their terms
  Flag                                                                                   departed_holders_share  People who have left hold shares (the lines marked departed); investors often ask about it, and the company's lawyer can say whether any repurchase right or unvested shares were handled
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

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with plugin 0.3.5 loaded from this repository and no user settings. An
earlier run of this eval that day, on plugin 0.3.2, is not recorded. The answer is shown whole.

**Pass, with shortfalls against the expected answer.** It met every clause of the pass sentence above. It made the one
`equity_cap_table_check` call, its input the same as the expected call, and no other; it led with the verdict ("No, it
does not add up: 9 of the 9 figures the table states do not match."); its tie-outs table sets the table's figure beside
the tool's, with the difference, for the fully diluted total, every stated percent and the percent column's total, each
percent the tool's fraction with its decimal point moved; it put to the company's lawyer the questions the flags raise
(an amendment raising the authorised common, enough common reserved, the departed engineer's unvested shares, the SAFE's
terms); it said the check is arithmetic only and never said whether a share was validly issued; and every figure in it
is one the tool returned. Short of the expected answer: it half-guessed the wrong line ("The gap is 100,000 shares, and
your warrants line is 100,000."), where the expected answer guesses none: no figure is worked out there, so the last
clause holds, but the match relates two figures as the skill's limits rule out. It paraphrased the assumptions, with
neither their keys (`fully_diluted_basis`, `preferred_as_converted`, `legal_validity`) nor their sources; the percent
column's row trims the tool's digits (100.00% for 100.0000%, 0.035 for 0.0350%); and its SAFE paragraph, close to the
expected answer, says every percent falls when the SAFE converts and a preview needs the founder's next round, but not
in so many words that no percent counts it until a priced round converts it. The session's first line listed the
calculator's server as still starting, with none of its tools; the run found the tool by searching for it by name, as
the skill says, and called it once. Since this run the skill's limits say never to say or hint which line is wrong, not
even when a difference the tool prints equals one line's shares, and its answering steps name each assumption by its
key, with its source. The eval has not been run again.

> **No, it does not add up: 9 of the 9 figures the table states do not match.** The classes add up to 10,100,000 fully diluted shares, not the 10,000,000 stated, so every percent is slightly overstated and the percent column totals 101.00%.
>
> The gap is 100,000 shares, and your warrants line is 100,000. Check whether the 10,000,000 total was built before the warrants were added; that is a question for you, not something the check can tell.
>
> ## Tie-outs
>
> | Figure                | The table says | The calculator gives | Difference                                  | Consistent? |
> | --------------------- | -------------- | -------------------- | ------------------------------------------- | ----------- |
> | Fully diluted shares  | 10,000,000     | 10,100,000           | 100,000                                     | No          |
> | Founder A             | 45.00%         | 44.5545%             | -0.4455 pts                                 | No          |
> | Founder B             | 35.00%         | 34.6535%             | -0.3465 pts                                 | No          |
> | First engineer (left) | 2.50%          | 2.4752%              | -0.0248 pts                                 | No          |
> | Seed preferred        | 10.00%         | 9.9010%              | -0.0990 pts                                 | No          |
> | Options granted       | 5.00%          | 4.9505%              | -0.0495 pts                                 | No          |
> | Unissued pool         | 2.50%          | 2.4752%              | -0.0248 pts                                 | No          |
> | Warrants              | 1.00%          | 0.9901%              | -0.0099 pts                                 | No          |
> | Percent column total  | 101.00%        | 100.00%              | -1.00 pts (rounding explains at most 0.035) | No          |
>
> ## What the table adds up to
>
> - **Fully diluted:** 10,100,000 shares.
> - **Outstanding (common and preferred):** 9,250,000 shares.
> - **Common:** 8,250,000 shares from the three holder lines, 81.6832% of fully diluted.
> - **Founders together:** 79.2079% of fully diluted.
> - **Departed holders (dead equity):** 2.4752% of fully diluted.
>
> ## Authorised shares
>
> | Item                               | Issued or needed | Authorised | Left                   |
> | ---------------------------------- | ---------------- | ---------- | ---------------------- |
> | Common                             | 8,250,000        | 8,000,000  | **-250,000 (over)**    |
> | Seed preferred                     | 1,000,000        | 1,000,000  | 0                      |
> | Option plan (granted and unissued) | 750,000          | 750,000    | 0                      |
> | Common against fully diluted       | 10,100,000       | 8,000,000  | **-2,100,000 (short)** |
>
> The common overage is the more serious finding. Your three common lines add up to more common than the 8,000,000 you say the charter authorises.
>
> ## Outstanding SAFE
>
> There is one, a $1,000,000 post-money SAFE at a $12,000,000 cap. It holds no shares yet, so it sits outside every percent above, and all of them fall when it converts. I did not model the conversion because that needs the priced round you expect.
>
> ## Flags
>
> - **Percents do not sum:** the stated percents cannot all be roundings of shares that add up to 100%. A line is missing, counted twice, or on another basis.
> - **Over authorised:** common has issued more than the authorised figure you gave.
> - **Authorised common below fully diluted:** everything would be common once converted or exercised, and 8,000,000 does not cover it.
> - **Unconverted instrument:** list the SAFE for investors alongside the table.
> - **Departed holder's shares:** investors often ask about these.
>
> ## Questions for your lawyer
>
> 1. Is the 8,000,000 common figure the charter as filed, or was an amendment raising it filed?
> 2. Does the charter reserve enough common for the preferred conversion, the options, and the warrants?
> 3. Does the seed preferred still convert one to one?
> 4. Were the option grants approved, and does the 750,000 reserve cover them?
> 5. For the engineer who left, were unvested shares bought back or cancelled, and does the company keep any right to repurchase the 250,000?
> 6. Are the warrant terms (shares, exercise price, expiry) and the SAFE terms as listed, and are any other SAFEs or notes outstanding?
>
> ## Assumptions
>
> - Preferred counts one common share per share, and warrants count as fully exercised. Both are unverified; your charter and the warrant decide.
> - Authorised figures are the ones you gave; I did not read the charter.
> - Percents are checked with zero tolerance beyond rounding to two places.
> - This checks arithmetic only, not whether any share or grant is legally valid. It is not legal, tax or investment advice.
>
> ## Needs from the founder
>
> - [Which is right: the 10,000,000 total or the line items, and were warrants meant to be in the total?] Once you correct it, I can re-run the check.
> - [Next priced round you expect: pre-money, raise amount, any pool top-up] With that I can show what the SAFE conversion does to each line.
