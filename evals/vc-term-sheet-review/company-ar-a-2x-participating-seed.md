# Eval 2: Company AR, a 2x participating seed with terms the calculator does not model

A test prompt for the `vc-term-sheet-review` skill. The company is made up. The tool calls and their excerpts are real
calculator output for these inputs. "Expected answer" states the expected behaviour, and "Recorded answer" is an
excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23), graded Partial: it met this pass sentence, but ran the
lenses and the refute pass in its own agent though it had a subagent tool. The skill and this eval were changed after
that run (see "Recorded answer"). A run passes when it marks the valuation's label, the preference, participation,
dividends, anti-dilution, board and redemption terms Differs or Not in the baseline with their sources, marks no term
Missing (the founder has not said the text is the whole sheet), reports the founders' 75%
as a mismatch, runs every exit under the sheet's terms and under the 1x non-participating baseline with no difference
computed, quotes the not-modelled terms with the fixed string, and says nothing about whether to sign.

## Prompt

> Is this seed term sheet standard? "$3,000,000 Series Seed at a $9,000,000 pre-money valuation; investors own 25%
> fully diluted. Option pool: 10% post-closing, included in the pre-money. Liquidation Preference: 2x, fully
> participating. Dividends: 8% cumulative. Anti-dilution: full ratchet. Board: two Investor designees and one Founder.
> Redemption: at the option of the Investors after five years." Our three founders hold all 6,000,000 shares, there is
> no pool yet and no SAFE or note. We think we keep 75%. An acquirer floated $30M last month: what would we get?

## Expected tool call

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "9000000",
    "stated_investor_percent": "25",
    "fully_diluted_shares": 6000000,
    "target_pool_percent": "10",
    "holder_shares": 6000000,
    "stated_holder_percent": "75"
  }
}
```

```text
  Post-money valuation                                                $12,000,000.00  V + I
  Effective pre-money                                                  $7,800,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  Investors' percent: verdict                                             consistent  within the tolerance is consistent
  Holder group's percent after: the calculator gives                        65.0000%  h·(share every pre-round share keeps)
  Holder group's percent after: verdict                                     mismatch  within the tolerance is consistent
  A VC is likely to ask                               pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
```

### Call 2: `equity_pool`

```json
{
  "inputs": {
    "fully_diluted_shares": 6000000,
    "pre_money": "9000000",
    "investment": "3000000",
    "target_pool_percent": "10",
    "share_rounding": "whole_shares"
  }
}
```

```text
  Shares: existing holders                                    6,000,000           6,000,000  FD - U
  Shares: investor                                            2,307,692           2,000,000  N = I/p
```

### Call 3: `equity_waterfall` (the post-money, $12,000,000, under the sheet's terms; whichever waterfall runs first prints the preference owed)

```json
{
  "inputs": {
    "exit_amount": "12000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                 $7,666,666.51  preference paid + part of the rest
  Common stock's payout                           $4,333,333.49  common shares × per-share part
```

### Call 4: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "12000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                               $3,333,333.01  preference paid + part of the rest
  Common stock's payout                         $8,666,666.99  common shares × per-share part
```

### Call 5: `equity_waterfall` (that preference owed, $6,000,000, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "6000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                 $6,000,000.00  preference paid + part of the rest
  Common stock's payout                                   $0.00  common shares × per-share part
```

### Call 6: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "6000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $3,000,000.00  preference paid + part of the rest
  Common stock's payout                         $3,000,000.00  common shares × per-share part
```

### Call 7: `equity_waterfall` (the amount raised, $3,000,000, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "3000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                 $3,000,000.00  preference paid + part of the rest
  Common stock's payout                                   $0.00  common shares × per-share part
```

### Call 8: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "3000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout                               $3,000,000.00  preference paid + part of the rest
  Common stock's payout                                 $0.00  common shares × per-share part
```

### Call 9: `equity_waterfall` (the founder's exit, $30,000,000, under the sheet's terms)

```json
{
  "inputs": {
    "exit_amount": "30000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "2",
        "participation": "full"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                        $6,000,000.00  multiple × invested
  Class 1: choice                                         stays  converts only when that pays strictly more
  Class 1: payout                                $12,666,666.02  preference paid + part of the rest
  Common stock's payout                          $17,333,333.98  common shares × per-share part
```

### Call 10: `equity_waterfall` (the same exit under the 1x non-participating baseline)

```json
{
  "inputs": {
    "exit_amount": "30000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2307692,
        "invested": "3000000",
        "preference_multiple": "1",
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: preference owed                      $3,000,000.00  multiple × invested
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                               $8,333,332.53  preference paid + part of the rest
  Common stock's payout                        $21,666,667.47  common shares × per-share part
```

## Expected answer

- Marks: amount and valuation Differs on the label (the sheet's pre-money against the template's post-money, with
  the pool's place quoted, "included in the pre-money", in that row or in the option pool row), the preference (2x
  against the template's 1x) Differs, participation Differs, dividends (cumulative) Differs, anti-dilution (full ratchet against broad-based weighted average) Differs,
  the board (two investor seats of three against one of three) Differs, redemption Not in the baseline. Each cites the
  YC article or template and the matching Feld post, and the answer notes that the baseline is a Series A sheet while
  this is a seed round. The founder has not said the text is the whole sheet, so no term is marked Missing:
  conversion, protective provisions, drag-along, founder vesting, the investor rights and the no-shop and conditions
  go to the open asks as not in what was pasted, with a request for the whole sheet.
- The 75% is a mismatch: the calculator gives 65.0000%, because the 10% pool is paid for out of the pre-money
  (effective pre-money $7,800,000.00 against $9,000,000.00). It heads the list, ahead of the tiers, with no tier. The
  investors' 25% is consistent.
- Exit table with both columns and no difference computed: at $6M (the preference owed) common gets $0.00 under the
  sheet and $3,000,000.00 under the baseline; at $12M, $4,333,333.49 against $8,666,666.99; at $30M, $17,333,333.98
  against $21,666,667.47, and under the baseline the seed converts. At $3M common gets $0.00 under both. Participation
  is explained with the waterfall's own fields; the investors' 25% is never set beside the $30M exit's remainder.
- Cumulative dividends, the full ratchet and redemption are quoted with "not modelled: no tool computes this term's
  effect"; the dividend is not folded into the 2x.
- Survivors include, from the next round's lead lens, that a later lead investor is likely to ask to match
  "Liquidation Preference: 2x, fully participating", grounded in that line alone, and from the control lens the
  investors' board majority; each becomes a lawyer question, such as "What does the 2x participating preference pay
  common at our low exit?". No sentence says whether to sign or calls a term off the market.
- With a subagent tool, the four lenses run as subagents launched in one message, then one refute subagent per
  objection that survived the quote check; the answer gives a refute verdict for every such objection, Kept ones
  included.
- Asked whether the sheet is standard, it gives no yes or no: it says which terms match the baseline, differ or are
  not in it, from the marks table, and gives no count of terms that the table does not give. Every lawyer question
  uses only periods and amounts that the sheet or the founder gave (the sheet gives five years for redemption).

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Partial.** It met every clause of the pass sentence above: all ten calls with the expected arguments, every figure
as the tool printed it, the marks with their sources, no term marked Missing, the 75% as a mismatch, both columns of
the exit table with no difference computed, the not-modelled terms with the fixed string, and nothing on whether to
sign. It was graded Partial on two expected points: it ran the four lenses and the refute pass in its own agent
although it had a subagent tool, and its preference mark did not cite a precedent point from the YC article that the
skill never mentions (that point is no longer expected, since no one has read the article for it). It also quoted the
pool's place in the option pool row (now accepted), counted "five of the seven lines" where its own table marks six,
opened with a bare "no", asked about a three-year period the sheet never gave, and set the investors' 25% beside the
$30M exit's remainder. Since this run the skill puts the subagent path first, asks for a refute verdict per objection,
answers "is it standard?" from the marks table with no yes or no, takes every count from that table, keeps lawyer
questions to the sheet's own periods, and explains participation with the waterfall's own fields. The eval has not
been run again.

> This is a plain-words reading to prepare for your lawyer, not legal, tax or investment advice; whether to sign is your call with them.
>
> **Short answer:** no. Against Y Combinator's "standard and clean" Series A term sheet (a Series A baseline, used here for a seed round), five of the seven lines differ or are not in it at all. You would keep 65%, not 75%. At a $30M sale after this round closes, the three founders together would get $17,333,333.98, before any accrued dividends, which the calculator does not model.
>
> [...]
>
> | Exit            | Where it comes from    | Series Seed's choice              | Series Seed gets | Founders get (this sheet) | Founders get (1x non-participating) |
> | --------------- | ---------------------- | --------------------------------- | ---------------- | ------------------------- | ----------------------------------- |
> | $3,000,000      | Amount raised          | Keeps preference                  | $3,000,000.00    | $0.00                     | $0.00                               |
> | $6,000,000      | The 2x preference owed | Keeps preference                  | $6,000,000.00    | $0.00                     | $3,000,000.00                       |
> | $12,000,000     | Post-money             | Keeps preference and participates | $7,666,666.51    | $4,333,333.49             | $8,666,666.99                       |
> | **$30,000,000** | The offer you named    | Keeps preference and participates | $12,666,666.02   | **$17,333,333.98**        | $21,666,667.47                      |
>
> At $30M the investors' 25% takes $6M first, then a pro rata share of the remaining $24M. Under the baseline they would convert to common instead.
>
> [...]
>
> I ran the four lenses and the refute pass myself in one pass, so they are less independent than separate reviewers would be. Nothing in the seven lines answers any objection, so none was dropped.
>
> [...]
>
> 3. Do the 8% cumulative dividends add to the liquidation preference, compound, or get paid in shares? What is owed after three and five years?
