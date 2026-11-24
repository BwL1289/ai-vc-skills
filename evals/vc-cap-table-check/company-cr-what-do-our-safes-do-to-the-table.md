# Eval 2: Company CR, "what do our SAFEs do to the cap table?"

A test prompt for the `vc-cap-table-check` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted
from what `equity_calculator cap_table_check` printed for these inputs; none is typed by hand. The founder counts only
the two remaining founders as founders, so the departed co-founder's line is marked `departed` only (with both marks it
would count in the founders' share and path too). A run passes when it makes the one tool call below (field order free,
money and percents as strings), says the preview rests on the founder's own next round, shows the founders' path from
their share after that round through the two rounds planned after it, gives the departed co-founder's share as printed,
and computes nothing in its own text.

## Prompt

> Our cap table: me 5,000,000 common (50%), my co-founder 3,000,000 (30%), our third co-founder who left 500,000 vested
> (5%; count just the two of us as founders), 1,000,000 options granted and a 500,000 unissued pool; percents are of
> fully diluted. We have two post-money SAFEs: $1M at a $10M cap, and $500k at an $8M cap with a 20% discount. We expect
> to raise $4M at an $18M pre-money next. After that we plan a round selling 20% with a 5% new pool, then another
> selling 20%. What do the SAFEs do to us, and where do we end up?

## Expected tool call

`equity_cap_table_check`, once:

```json
{
  "inputs": {
    "classes": [
      {
        "kind": "common"
      },
      {
        "kind": "options_granted",
        "shares": 1000000
      },
      {
        "kind": "options_unissued",
        "shares": 500000
      }
    ],
    "holders": [
      {
        "share_class": 1,
        "shares": 5000000,
        "stated_percent": "50",
        "founder": true
      },
      {
        "share_class": 1,
        "shares": 3000000,
        "stated_percent": "30",
        "founder": true
      },
      {
        "share_class": 1,
        "shares": 500000,
        "stated_percent": "5",
        "departed": true
      }
    ],
    "stated_percent_basis": "fully_diluted",
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "1000000",
        "valuation_cap": "10000000"
      },
      {
        "kind": "safe",
        "purchase_amount": "500000",
        "valuation_cap": "8000000",
        "discount_percent": "20"
      }
    ],
    "conversion_preview": {
      "pre_money": "18000000",
      "investment": "4000000"
    },
    "planned_rounds": [
      {
        "investor_percent": "20",
        "pool_percent": "5"
      },
      {
        "investor_percent": "20"
      }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Fully diluted shares (FD)                                                                 10,000,000  every class
  Founders' lines: of fully diluted                                                           80.0000%  founder lines' shares/FD
  Departed holders: of fully diluted                                                           5.0000%  departed lines' shares/FD
  SAFEs and notes: amount                                                                $1,500,000.00  before interest
  Holder line 1 (class 1, common) percent: verdict                                          consistent  within the tolerance, or rounding to the table's, is consistent
  Next round: price per share                                                                $1.507500  the round scenario's price
  SAFE 1: converts at                                                                        $0.837500  cap
  SAFE 1: shares                                                                         1,194,029.851  amount converting/price
  SAFE 2: converts at                                                                        $0.670000  cap
  SAFE 2: shares                                                                           746,268.657  amount converting/price
  After: Class 1 (common)                                                                     58.2443%  shares/T
  After: Class 2 (options granted)                                                             6.8523%  shares/T
  After: option pool                                                                           3.4261%  the round's pool/T
  After: SAFE 1                                                                                8.1818%  shares/T
  After: SAFE 2                                                                                5.1136%  shares/T
  After: new investors                                                                        18.1818%  shares/T
  After: founders' lines                                                                      54.8182%  shares/T
  After: departed holders                                                                      3.4261%  shares/T
  Founders' path: after the next round (the preview)                                          54.8182%  the preview's founders' lines (shares/T)
  Founders' path: round 1 keeps                                                               75.0000%  1 - n - p
  Founders' path: after round 1                                                               41.1136%  before × kept
  Founders' path: round 2 keeps                                                               80.0000%  1 - n - p
  Founders' path: after round 2                                                               32.8909%  before × kept
  Founders' path: after the last round                                                        32.8909%  after the preview × every kept
  Flag                                                                 unconverted_instruments_present  SAFEs or notes are outstanding and hold no shares yet, so every percent here falls when they convert; list them for investors, and ask the company's lawyer to confirm their terms
  Flag                                                                          departed_holders_share  People who have left hold shares (the lines marked departed); investors often ask about it, and the company's lawyer can say whether any repurchase right or unvested shares were handled
  Overall verdict                                                                           consistent  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- It says the stated percents tie out (the overall verdict is consistent) and that the founders' lines hold 80.0000%
  of the 10,000,000 fully diluted shares today, with the $1,500,000.00 of SAFEs outstanding and in no percent yet.
- It shows the preview at the founder's own next round, $4,000,000 at an $18,000,000 pre-money: the round price is
  $1.507500, both SAFEs convert at their caps ($0.837500 and $0.670000), and the founders' lines hold 54.8182% after
  it, the departed co-founder 3.4261% and the new investors 18.1818%. It says these figures rest on that round, which
  the founder gave, and would change with another.
- It shows the founders' path as printed: it starts after the founder's next round, from the founders' 54.8182% with
  both SAFEs converted, then 41.1136% after the first planned round and 32.8909% after the second. It says the two
  planned rounds are the ones after the next round, so that round is counted once, and it works out no figure of the
  path by hand.
- It gives the departed co-founder's 5.0000% of the fully diluted shares today (`departed_holders_share`) and asks, as
  a question for the company's lawyer, whether any unvested shares were bought back and whether the company keeps a
  right to buy back what is held.
- It hands the size of the next round's pool to the vc-option-pool-plan skill and the round's wider effect to the
  vc-deal-math skill.
