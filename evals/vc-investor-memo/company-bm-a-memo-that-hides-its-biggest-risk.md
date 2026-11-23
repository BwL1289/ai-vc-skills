# Eval 1: Company BM, a memo whose risks section leaves out the biggest risk

A test prompt for the `vc-investor-memo` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator` runs with these inputs, on this repository's calculator. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it makes the five calls
below (field order free, money and percents as strings), states the round and the outcome case with the tools' values as
printed, labels every exit value the founder's assumption, writes the customer concentration into Top risks, drops the
team objection by quoting the deck, and computes nothing in its own text.

## Prompt

> Review the memo I drafted for our champion at the seed lead. My draft: "Company BM sells scheduling and billing
> software to physiotherapy clinics. Market: a $40B market. Traction: MRR $40,000 in October, up from $12,000 in
> April. Team: a world-class team. Round: $3,000,000 at a $12,000,000 pre-money, with the pool topped up to 10% before
> the round; the round buys 20%; founders keep 59%; 23 months of runway. Risks: competition from incumbents
> (mitigation: we move faster). Outcome: could be a $1 billion company." Deck, slide 6: "Our CTO built the clinic
> scheduling engine at her last company, used by 2,000 clinics." My notes: "Our largest customer, a 40-location chain,
> is 45% of MRR." Cap table: 10,000,000 fully diluted shares, 500,000 of them the unissued pool, no options granted,
> no SAFEs or notes; the founders hold 8,000,000 and two angels hold the other 1,500,000 as common. Cash $400,000; we
> spend $190,000 a month and bring in $40,000. No term sheet yet. Exits: $8 million if growth stalls (a sale to a
> billing vendor), $150 million on plan, $1 billion if we become the default system for clinics.

## Expected tool call

Five calls, in this order: `equity_deal_check`, `equity_pool`, then `equity_waterfall` once per exit value.

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "3000000",
    "pre_money": "12000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "holder_shares": 8000000,
    "stated_holder_percent": "59",
    "cash_on_hand": "400000",
    "planned_monthly_gross_burn": "190000",
    "planned_monthly_revenue": "40000",
    "stated_runway_months": "23"
  }
}
```

```text
  Investors' share of the cap table                                         20.0000%  N/T
  Effective pre-money                                                 $10,500,000.00  (FD - U)·p: the pre-round holders' shares at the round price
  Holder group's percent after: the calculator gives                        58.9474%  h·(share every pre-round share keeps)
  Holder group's percent after: verdict                                   consistent  within the tolerance is consistent
  Runway: the calculator gives                                          22.67 months  (cash + I)/net burn, planned (else current)
  Runway: verdict                                                         consistent  within the tolerance is consistent
  A VC is likely to ask                               pool_in_pre_money_lowers_price  The new pool is paid for out of the pre-money, so the effective pre-money and the price per share are below the headline; a VC prices it this way
  Overall verdict                                                         consistent  mismatch if any check is; consistent if all are; not_checked with none
```

### Call 2: `equity_pool`

```json
{
  "inputs": {
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "pre_money": "12000000",
    "investment": "3000000",
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "share_rounding": "whole_shares"
  }
}
```

```text
  Shares: existing holders                                    9,500,000           9,500,000  FD - U
  Shares: investor                                            2,714,285           2,500,000  N = I/p
```

### Call 3: `equity_waterfall`, the $8,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "8000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "3000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: choice                                       stays  converts only when that pays strictly more
  Class 1: payout if it stays                   $3,000,000.00  the others' choices held
  Class 1: payout                               $3,000,000.00  preference paid + part of the rest
```

### Call 4: `equity_waterfall`, the $150,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "150000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "3000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                              $33,333,326.51  preference paid + part of the rest
```

### Call 5: `equity_waterfall`, the $1,000,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "1000000000",
    "common_shares": 9500000,
    "classes": [
      {
        "shares": 2714285,
        "invested": "3000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none"
      }
    ]
  }
}
```

```text
  Class 1: choice                                    converts  converts only when that pays strictly more
  Class 1: payout                             $222,222,176.74  preference paid + part of the rest
```

## Expected answer

- The round section uses the tool's values: founders 58.9474% after the round, the effective pre-money $10,500,000.00
  beside the $12,000,000 headline (the `pool_in_pre_money_lowers_price` flag as a question a partner is likely to ask),
  runway 22.67 months; "the round buys 20%", "founders keep 59%" and "23 months" are consistent and the memo states the
  printed figures.
- The waterfall runs on the `equity_pool` counts (9,500,000 common, 2,714,285 for the round, passed as integers), since
  no options are granted; every price and percent in the memo still comes from `equity_deal_check`.
- The outcome table: $8,000,000, $150,000,000 and $1,000,000,000, each "the founder's assumption" with the founder's
  reason quoted; payouts $3,000,000.00 (stays, its preference), $33,333,326.51 and $222,222,176.74 (converts), each
  beside $3,000,000 invested; no multiple, no fund size; the `exit_is_shared_amount` row quoted; the waterfall's terms
  called the calculator's defaults, since there is no term sheet. "could be a $1 billion company" becomes an assumption
  with its reason, not a claim.
- Dissent, Kept: Risks left out, quoting "Our largest customer, a 40-location chain, is 45% of MRR."; the revised Top
  risks carries it in the founder's words with `[what is being done about it, and what shows it]`. Kept: "we move
  faster" as a mitigation that names no action under way. Kept: "a $40B market" with no basis (the market pattern), with
  `[who buys, how many, what each pays]`.
- Dissent, Dropped, answered by slide 6, "Our CTO built the clinic scheduling engine at her last company, used by 2,000
  clinics.": the Team lens's objection to "a world-class team". The memo's Team section is to carry that line.
- "MRR $40,000 in October, up from $12,000 in April" is quoted; no growth rate is worked out.
- No sentence recommends investing; no firm is named; no score.
