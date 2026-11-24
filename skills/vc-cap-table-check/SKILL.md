---
name: vc-cap-table-check
description: Helps a founder tie out their own cap table before an investor's lawyers do, with the equity calculator's cap_table_check tool. It adds every class up to the fully diluted shares, works each class's and each holder's exact percent and sets it beside the percent the table states (rounding-aware), compares issued with authorised shares, lists the SAFEs and notes not yet converted, and shows the share held by people who have left. On the founder's own next round it previews the conversions, and on their planned rounds it follows the founders' ownership. Use when a founder says check my cap table, does our cap table add up, how much do the founders really own, what do our SAFEs do to the cap table, how much dead equity do we have, or shares a cap table. Every figure comes from the calculator. It never says whether a share was validly issued; it lists the questions for the company's lawyer. Not legal, tax or investment advice.
---

# VC cap table check

Helps a founder see their cap table the way an investor's lawyers will read it in diligence: do the classes add up to
the fully diluted total the table states, does each percent match its shares, is any class past the shares the charter
authorises, which SAFEs and notes are still waiting to convert, and how much of the company is held by people who have
left. The `equity_cap_table_check` tool does every calculation exactly and returns each figure the table states as
consistent or a mismatch, with the difference, plus flags that name what to fix or what to ask the company's lawyer.
The aim is a cap table whose numbers hold up, so diligence is about the company, not the arithmetic. The skill never
rules on whether a share, a grant or a transfer is legally valid.

## When to use it

- "Check my cap table." "Does our cap table add up?" "How much do the founders really own?"
- "What do our SAFEs do to the cap table?" "How much dead equity do we have?"
- A cap table, pasted or exported from a spreadsheet or a cap table tool, or a summary of one in a deck. Any of these
  may come as a file the agent can read in this session.
- Hand off round math (what a priced round, its pool top-up or its SAFEs do to ownership, valuation and runway) to the
  vc-deal-math skill, and a single scenario with no table to check to the equity-calculator skill (`equity_round`,
  `equity_dilution`, `equity_pool`).
- Hand off how big the option pool should be, and what a top-up costs the founders, to the vc-option-pool-plan skill
  (preview, being built); until it is there, `equity_pool` in the equity-calculator skill works the arithmetic.
- Hand off a term sheet to the vc-term-sheet-review skill (preview), and the diligence questions an investor is likely
  to ask about the company to the vc-diligence-questions skill (preview).

## Steps

1. **List what the table states, word for word**: each class (common, each preferred series, options granted, the
   unissued pool, warrants) with its shares and any authorised shares, each holder line with its class, shares and
   percent, the fully diluted total, what the percents are a share of if the table says, the option plan's reserve, and
   each SAFE and note with its terms. Quote each figure as stated; never correct it before the check. Holders are
   numbered, never named, in the tool call: keep the founder's names in the answer only as the founder wrote them.
   When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and list
   what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what was read
   from each. A place you could not read (a slide that is only a picture, a page whose text did not come out, a file
   that opened only in part) is listed as not read and asked for, never filled in from its title or the places around
   it, and a figure is never read off a chart or a picture. Ask only for what you could not read and what the file
   does not show (speaker notes, the figures behind a chart, an input below that it leaves out), and never ask the
   founder to paste what you already read.
2. **Ask the founder for what is missing, by name, in one message.** Never guess:
   - **What the table's percents are a share of**, when it states any and does not say: the fully diluted shares
     (every class, granted options, the unissued pool and warrants included) or the outstanding stock (common and
     preferred only). Ask it as a bracketed ask,
     `[what the table's percents are a share of: fully diluted or outstanding]`. The tool refuses a stated percent
     without `stated_percent_basis`, so make no call with the percents until it is given; never pick one because the
     figures fit it better.
   - Each class's kind and shares, or its holder lines. When a class gives both its shares and holder lines, ask
     whether the listed holders are every holder of the class, and send the answer as `holder_lines` (`complete` or
     `partial`; the tool refuses the class without it). Never build an "everyone else" line by subtracting the listed
     holders from the class's shares: with `partial`, the tool shows the rest itself.
   - Which lines are the founders', and which are held by people who have left (their vested shares, as the table
     shows them; ask whether any unvested shares were bought back). For a co-founder who has left, ask the founder
     whether those shares belong in the founders' share, and never decide it: a line marked both `founder` and
     `departed` counts in the founders' share, the founders' path and the departed holders' share.
   - Authorised shares per class and the option plan's reserve only as the founder's charter and plan give them; with
     none, the tool skips those comparisons, and the answer says they were not checked.
   - Each SAFE: amount, post-money cap and/or discount, MFN. Each note: principal, interest rate, months outstanding
     (or issue and conversion dates), simple or compounding interest, cap and/or discount.
   - **A conversion preview needs the next priced round the founder expects**: its pre-money and raise, and any pool
     top-up. Ask for it; never assume a price or a valuation, and with none run without `conversion_preview`, saying
     the SAFEs and notes stay outside every percent.
   - **The founders' path needs the rounds the founder plans**, each as the percent sold and any new pool, or its
     pre-money and raise. Never invent one. With a conversion preview the path starts from the founders' share after
     that round, so `planned_rounds` holds only the rounds after it: never repeat the next round there, or it is
     counted twice.
3. **Call `equity_cap_table_check`** with the founder's figures, percents as JSON strings with exactly the places the
   table writes (`"45.00"` for "45.00%"), share counts as integers, and `founder` and `departed` as `true`. Company CQ
   (made up) as an example:

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

   The same check from the command line (`equity_calculator cap_table_check --help` lists every flag):

   ```
   equity_calculator cap_table_check --share-class "kind=common authorised-shares=8000000" --share-class "kind=preferred shares=1000000 authorised-shares=1000000 stated-percent=10.00" --share-class "kind=options_granted shares=500000 stated-percent=5.00" --share-class "kind=options_unissued shares=250000 stated-percent=2.50" --share-class "kind=warrants shares=100000 stated-percent=1.00" --holder "share-class=1 shares=4500000 stated-percent=45.00 founder" --holder "share-class=1 shares=3500000 stated-percent=35.00 founder" --holder "share-class=1 shares=250000 stated-percent=2.50 departed" --stated-fully-diluted-shares 10000000 --stated-percent-basis fully_diluted --option-plan-reserve 750000 --safe "1000000 valuation-cap=12000000"
   ```

   and an excerpt of what it prints:

   ```text
     Class 1 (common): authorised left                                                                    -250,000  authorised - shares (below 0: over)
     Fully diluted shares (FD)                                                                          10,100,000  every class
     Holder line 1 (class 1, common): of fully diluted                                                    44.5545%  shares/FD
     Departed holders: of fully diluted                                                                    2.4752%  departed lines' shares/FD
     Fully diluted shares: the table says                                                               10,000,000  given
     Fully diluted shares: verdict                                                                        mismatch  consistent only when equal
     Holder line 1 (class 1, common) percent: the table says                                              45.0000%  given
     Holder line 1 (class 1, common) percent: the calculator gives                                        44.5545%  shares/FD
     Holder line 1 (class 1, common) percent: verdict                                                     mismatch  within the tolerance, or rounding to the table's, is consistent
     Percent column, line by line: the table says                                                        101.0000%  given
     Percent column, line by line: verdict                                                                mismatch  a gap within what rounding explains, plus the tolerance for each, is consistent
     Flag                                                                                      percents_do_not_sum  The stated percents cannot all be roundings of shares that add up to 100%: a line is missing, counted twice, or on another basis; find it before the table goes to an investor
     Flag                                                                                          over_authorised  A class has issued more shares than the authorised figure given, or the option plan has granted and reserved more than its reserve; ask the company's lawyer whether the charter or the plan was amended to cover them
     Flag                                                                    common_authorised_below_fully_diluted  Authorised common is below the fully diluted shares, all of which would be common once converted or exercised; ask the company's lawyer whether the charter reserves enough common
     Flag                                                                          unconverted_instruments_present  SAFEs or notes are outstanding and hold no shares yet, so every percent here falls when they convert; list them for investors, and ask the company's lawyer to confirm their terms
     Flag                                                                                   departed_holders_share  People who have left hold shares (the lines marked departed); investors often ask about it, and the company's lawyer can say whether any repurchase right or unvested shares were handled
     Overall verdict                                                                                      mismatch  mismatch if any check is; consistent if all are; not_checked with none
   ```

4. **A refusal is the answer for those inputs**: relay the tool's reason and ask for what it names (a stated percent
   with no basis, a class with shares and holder lines and no word on whether the lines are every holder, a holder
   line in a class that is not there, a preview with no SAFE or note). Never work around it.
5. **Follow-ups go to tools too**: a corrected table by re-running `equity_cap_table_check`; a priced round's full
   effect to the vc-deal-math skill; a pool top-up to the vc-option-pool-plan skill, or `equity_pool` until it is
   there.

## Answering

Lead with the verdict, then the tie-outs, then the flags and the questions for the lawyer, then the assumptions. Use
the tool's printed values (`rounded` with its unit, or the exact fraction when precision matters); never round again or
recompute. A value whose unit is `fraction` is a share of the whole: show it as a percent by moving the decimal point of
its `rounded` value two places to the right, keeping every digit (0.445545 is 44.5545%), which is what the command
line's report prints. That is a change of notation, not a calculation.

1. **Verdict.** "All N figures the table states are consistent", "M of N figures the table states do not match", or,
   for `not_checked`, "The table states no figure the calculator could check; here is what it adds up to."
2. **Tie-outs table:** "The table says", "The calculator gives", "Difference", "Consistent?", one row per check: the
   fully diluted total, each class total against its holder lines (where they are every holder, or add up to more),
   each stated percent, and each percent column's total against 100% with what rounding can explain.
3. **What the table adds up to:** the fully diluted and outstanding shares, each class's and each holder line's
   percent, a partial class's shares in no holder line as printed, the founders' share, and the departed holders'
   share of the fully diluted shares.
4. **Authorised shares:** each class's shares against its authorised shares and what is left (below 0 when over), the
   option plan against its reserve, authorised common against the fully diluted shares; or "not checked: no
   authorised figure given".
5. **Outstanding SAFEs and notes,** each with its amount and terms and their total. With a preview, every line after
   the founder's next round, the price and each instrument's conversion price and basis, said to rest on that round;
   with a path, the founders' share where it starts and after each planned round, as printed. With a preview the
   path starts after the preview's round, its SAFEs and notes converted; without one it starts today and leaves them
   out (`path_leaves_out_instruments`), and the answer says so.
6. **Flags**, one line each in the words of the table below. A flag is a question to settle, never a ruling.
7. **Questions for the lawyer**, from the section below, only those the result raises, each as a question.
8. **Assumptions:** quote the ones the answer leans on with their sources. Say plainly which are `unverified` and how
   to change a default (the basis, the tolerance).

## Flags

The result's `flags` holds codes only; this table is what each `cap_table_check` flag means for the founder. The text
report prints the same meaning beside each flag; the MCP result does not.

| Flag                                    | What it means for the founder                                                                       | What to change or ask                                                                       |
| --------------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `holder_lines_exceed_class`             | Holder lines add up to more than their class's shares; founders' figures and the path are left out. | Ask which is right, the lines or the class's shares, and re-run with the corrected figure.  |
| `percents_do_not_sum`                   | A column of stated percents cannot be roundings of shares that add up to 100%.                      | Find the line that is missing, counted twice or on another basis before the table goes out. |
| `consistent_beyond_rounding`            | A stated percent holds by the tolerance alone, not as the tool's figure rounded to its places.      | Quote the tool's figure; an investor recomputing gets it.                                   |
| `over_authorised`                       | A class has issued more than the authorised shares given, or the plan more than its reserve.        | Ask the company's lawyer whether the charter or the plan was amended to cover them.         |
| `common_authorised_below_fully_diluted` | Authorised common is below the fully diluted shares, all of which would be common once converted.   | Ask the company's lawyer whether the charter reserves enough common.                        |
| `unconverted_instruments_present`       | SAFEs or notes are outstanding and hold no shares yet, so every percent falls when they convert.    | List them for investors; a preview at the founder's next round shows one conversion.        |
| `departed_holders_share`                | People who have left hold shares (dead equity).                                                     | Ask the company's lawyer whether any repurchase right or unvested shares were handled.      |
| `path_leaves_out_instruments`           | The path starts today and converts no SAFE or note, so it shows more than the founders would keep.  | Ask for the next round and re-run with it as the preview; the path then starts after it.    |

## Questions for the lawyer

The tool checks arithmetic. These are the questions its result can raise that only the company's lawyer can settle;
ask the ones the flags and the table call for, and never answer them yourself:

- Is every class within the authorised shares in the charter as filed, and was any amendment that raised them filed?
- Does each preferred series still convert one to one, or has an adjustment changed its conversion?
- Were the option grants approved, and does the plan's reserve cover the options granted and unissued?
- For each person who has left: were their unvested shares bought back or cancelled, and does the company keep any
  right to buy back what they hold?
- Are the SAFEs and notes as listed (cap, discount, MFN, interest, maturity), and are any others outstanding?
- Are the warrants' terms (shares, exercise price, expiry) as listed?

## Limits

- No arithmetic outside the calculator's tools, and no what-if the founder did not ask for. Never work out how two of
  the founder's figures relate (a difference, a sum, a ratio or multiple, a share left over, "doubled") in a rewrite, a
  line or a table cell unless the founder's material states it or a tool returned it; quote both figures as stated
  instead ("from 2,000 to 4,500", never "more than doubled").
- It never says whether a share, a grant, a vesting schedule or a transfer is legally valid, and never says whether to
  accept a term or a request: the tool flags the questions, and the company's lawyer answers them.
- It checks the arithmetic of the figures the founder gives, pasted or in a file the agent can read in this session. It
  opens no folder of files, reads no figure off a chart or a picture, and sends nothing anywhere.
- Preferred counts one common share per share and warrants as exercised, as the tool's assumptions say; a series whose
  conversion has been adjusted is a question for the lawyer, not modelled.
- SAFEs and notes convert only in a preview at a round the founder gives; with none, they are listed and left out.
- It is not investment, legal or tax advice. It uses named public frameworks (the fully diluted measure, the round and
  dilution arithmetic of the equity calculator), never the voice or opinion of a named investor or firm.
- Shares are exact fractions; a real cap table rounds converted shares to whole shares, which moves figures by a share.
