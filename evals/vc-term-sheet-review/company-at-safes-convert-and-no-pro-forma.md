# Eval 4: Company AT, SAFEs convert and there is no pro forma cap table

A test prompt for the `vc-term-sheet-review` skill. The company is made up. The tool call and its excerpt are real
calculator output for these inputs. The answer states the expected behaviour; it is not a recorded run, and this eval
has not been run in a live session. A run passes when it makes the one call below, reports the founders' 70% as a
mismatch, asks which way the founder's cap table counts fully diluted shares, runs no waterfall and says why, and asks
for the pro forma cap table.

## Prompt

> Our Series A term sheet: "$10,000,000 at a $40,000,000 pre-money valuation; option pool 10% post-closing, in the
> pre-money; 1x non-participating; outstanding SAFEs convert into shadow series." The SAFEs are $1,000,000 at a
> $10,000,000 post-money cap and $1,500,000 at a $15,000,000 post-money cap. We have 10,000,000 fully diluted shares:
> founders 9,500,000, unissued pool 500,000. We think the founders keep 70%. What happens at a $25M sale?

## Expected tool call

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "10000000",
    "pre_money": "40000000",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "target_pool_percent": "10",
    "holder_shares": 9500000,
    "stated_holder_percent": "70",
    "instruments": [
      {
        "kind": "safe",
        "purchase_amount": "1000000",
        "valuation_cap": "10000000"
      },
      {
        "kind": "safe",
        "purchase_amount": "1500000",
        "valuation_cap": "15000000"
      }
    ]
  }
}
```

```text
  Effective pre-money                                                  $27,708,333.33  (FD - U)·p: the pre-round holders' shares at the round price
  After: SAFE 1                                                               7.2917%  shares/T
  After: SAFE 2                                                               7.2917%  shares/T
  Holder group's percent after: the calculator gives                         55.4167%  h·(share every pre-round share keeps)
  Holder group's percent after: verdict                                      mismatch  within the tolerance is consistent
```

## Expected answer

- The 70% is a mismatch (55.4167%), explained by the pool and both SAFEs being paid for out of the pre-money (the
  `conversions_bought_by_pre_money` and `pool_in_pre_money_lowers_price` flags, each with its meaning from the skill's
  flag table); it heads the list, ahead of the tiers, with no tier. Each SAFE ends at 7.2917%.
- It asks whether the founder's 10,000,000 fully diluted shares leave the SAFEs out, as the tool's count does (every
  share before the round, the unissued pool included and SAFEs and notes excluded), and says the call stands only on
  that basis; if they count the SAFEs, it asks for the total without them and never subtracts the SAFE shares itself.
- No `equity_pool` call (SAFEs convert) and no `equity_waterfall` call: "not run: the waterfall needs whole share
  counts; send the pro forma cap table". The $25M sale is not estimated.
- Amount and valuation Differs on the label (the sheet's pre-money against the template's post-money, with the pool's
  place quoted: "in the pre-money"). The shadow-series line Matches the baseline cell (SAFEs and notes convert into
  shadow series); the lawyer questions include each shadow series' preference and seniority, which the waterfall will
  need once the pro forma arrives.
- The founder quoted only some terms and has not said it is the whole sheet, so no term is marked Missing; the
  baseline terms not in what was pasted go to the open asks, with a request for the whole sheet.
