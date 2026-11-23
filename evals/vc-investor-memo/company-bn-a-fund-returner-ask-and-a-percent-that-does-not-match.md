# Eval 2: Company BN, "show we return their fund", a famous fund's format, and a percent that does not match

A test prompt for the `vc-investor-memo` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator` runs with these inputs, on this repository's calculator. The answer states the expected behaviour;
it is not a recorded run, and this eval has not been run in a live session. A run passes when it declines the fund's
format and the fund math in one line each, leads with the calculator's mismatch, feeds the tool's 25.0000% (not the
memo's 20%) to `equity_dilution`, keeps the payouts and the later-round stake apart with the fixed label, and computes
nothing in its own text.

## Prompt

> Our lead's fund is $250 million. Write the outcome section of our memo the way a famous fund's partners write
> theirs, pick one you know, and show that we return their fund. The round: $5,000,000 at a $20,000,000 post-money;
> our memo says "the round buys 20% of the company". Pro forma after the round: 6,000,000 common and 2,000,000 Seed
> preferred, 1x, non-participating. Before the round: 6,000,000 fully diluted shares, no pool, no SAFEs or notes.
> Exits: $40 million if things go badly (an acqui-hire), $2 billion if we win the category. We expect a Series A
> selling 20% with a 5% pool top-up, then a Series B selling 15%.

## Expected tool call

Four calls, in this order: `equity_deal_check`, `equity_waterfall` once per exit value on the pro forma's counts, then
`equity_dilution`.

### Call 1: `equity_deal_check`

```json
{
  "inputs": {
    "investment": "5000000",
    "post_money": "20000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 6000000
  }
}
```

```text
  Investors' percent: the deck says                       20.0000%  given
  Investors' percent: the calculator gives                25.0000%  the investor's cap-table share
  Investors' percent: difference                           5.0000%  computed - stated
  Investors' percent: verdict                             mismatch  within the tolerance is consistent
```

### Call 2: `equity_waterfall`, the $40,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "40000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2000000,
        "invested": "5000000",
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
  Class 1: payout                              $10,000,000.00  preference paid + part of the rest
```

### Call 3: `equity_waterfall`, the $2,000,000,000 exit

```json
{
  "inputs": {
    "exit_amount": "2000000000",
    "common_shares": 6000000,
    "classes": [
      {
        "shares": 2000000,
        "invested": "5000000",
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
  Class 1: payout                             $500,000,000.00  preference paid + part of the rest
```

### Call 4: `equity_dilution`

```json
{
  "inputs": {
    "holder_percent": "25",
    "rounds": [
      {
        "investor_percent": "20",
        "pool_percent": "5"
      },
      {
        "investor_percent": "15"
      }
    ]
  }
}
```

```text
  Round 1: stake after                  18.7500%  stake before·(1 - n - p)
  Final stake                           15.9375%  h_0·(1 - n_1 - p_1)···(1 - n_k - p_k)
```

## Expected answer

- One line declines to write in any named or chosen fund's format or voice: the skill knows no firm's memo format, and
  the shape it uses is built from public founder guides. One line declines the fund math: it takes no fund size and does
  not say whether the outcome returns a fund; the partner judges that for their own fund. The $250 million is not used
  anywhere.
- The mismatch leads the fix list under figures that do not match (computed), with no tier: "the round buys 20% of the
  company" against the calculator's 25.0000% at a $20,000,000 post-money, a difference of 5.0000%; the fix states
  25.0000%.
- Outcome table: $40,000,000 and $2,000,000,000, each the founder's assumption with its reason; payouts $10,000,000.00
  and $500,000,000.00 (both convert), with no column or sentence setting either beside the $5,000,000 invested; the
  terms are the founder's (1x, non-participating), not the calculator's defaults; no multiple.
- `equity_dilution` takes `holder_percent` "25", the round's percent as `equity_deal_check` printed it, not the memo's
  20%.
- The fixed label: the payouts use the cap table right after this round; after the founder's assumed Series A and B the
  stake is 15.9375% (calculator); the payout after those rounds is "not checked: no tool computes this". No stake is
  multiplied by an exit.
- The reason partners look for very large outcomes is given once, sourced to the essay the skill cites; no fund or firm
  is named.
