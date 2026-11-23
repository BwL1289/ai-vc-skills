# Eval 1: Company BM, a memo whose risks section leaves out the biggest risk

A test prompt for the `vc-investor-memo` skill. The company is made up. The tool calls and the excerpts are from real
`equity_calculator` runs with these inputs, on this repository's calculator. "Expected answer" states the expected
behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23), graded Partial: it
met the pass sentence this eval had then, but ran the refute pass as one subagent for all eight objections and
paraphrased the `exit_is_shared_amount` statement. The skill and this pass sentence were changed after that run (see
"Recorded answer"). A run passes when it makes the five calls below (field order free, money and percents as strings),
states the round and the outcome case with the tools' values as printed, labels every exit value the founder's
assumption, quotes the `exit_is_shared_amount` statement word for word under the outcome table, writes the customer
concentration into Top risks, keeps the team objection for the other founders while quoting the deck for the CTO,
gives the flag with its meaning in the fix list and in Numbers, lists the memo's Open questions in full, launches one
refute subagent per objection when it has a subagent tool, and computes nothing in its own text. The other points under
"Expected answer" are expected too; a run that misses one of them is graded Partial.

## Prompt

> Review the memo I drafted for our champion at the seed lead. My draft: "Company BM sells scheduling and billing
> software to physiotherapy clinics. Market: a $40B market. Traction: MRR $40,000 in October, up from $12,000 in
> April. Team: a world-class team. Round: $3,000,000 at a $12,000,000 pre-money, with the pool topped up to 10% before
> the round; the round buys 20%; founders keep 59%; 23 months of runway. Risks: competition from incumbents
> (mitigation: we move faster). Outcome: could be a $1 billion company." Deck, slide 6: "Our CTO built the clinic
> scheduling engine at her last company, used by 2,000 clinics." My notes: "Our largest customer, a 40-location chain,
> is 45% of MRR." Cap table: 10,000,000 fully diluted shares, 500,000 of them the unissued pool, no options granted,
> no SAFEs or notes; the founders hold 8,000,000 and two angels hold the other 1,500,000 as common. Cash $400,000; we
> spend $190,000 a month and bring in $40,000, and plan the same after the raise. No term sheet yet. Exits: $8 million
> if growth stalls (a sale to a billing vendor), $150 million on plan, $1 billion if we become the default system for
> clinics.

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
  beside the $12,000,000 headline, runway 22.67 months; "the round buys 20%", "founders keep 59%" and "23 months" are
  consistent and the memo states the printed figures. The `deal_check` call leaves out `current_monthly_gross_burn` and
  `current_monthly_revenue`, since the founder plans the same burn and revenue after the raise.
- The `pool_in_pre_money_lowers_price` flag, with its meaning from the skill's flag table (over MCP the tool returns the
  code alone), is a question a partner is likely to ask: in the fix list with no tier, after the computed mismatches
  (none here), and in Numbers.
- The waterfall runs on the `equity_pool` counts (9,500,000 common, 2,714,285 for the round, passed as integers), since
  no options are granted; every price and percent in the memo still comes from `equity_deal_check`.
- The outcome table: $8,000,000, $150,000,000 and $1,000,000,000, each "the founder's assumption" with the founder's
  reason quoted; payouts $3,000,000.00 (stays, its preference), $33,333,326.51 and $222,222,176.74 (converts), with no
  column or sentence setting a payout beside the $3,000,000 invested; no multiple, no fund size; directly under the
  table, the `exit_is_shared_amount` statement quoted word for word with its key: "The exit amount is what the
  shareholders share: no debt, fees, escrow, accrued dividends or option exercise cash is taken out first, and
  common_shares counts every common share that takes part (exercised options included; unexercised options take
  nothing)." The waterfall's terms are called the calculator's defaults, since there is no term sheet. "could be a $1
  billion company" becomes an assumption with its reason, not a claim.
- Dissent, Kept: Risks left out, quoting "Our largest customer, a 40-location chain, is 45% of MRR."; the revised Top
  risks carries it in the founder's words with `[what is being done about it, and what shows it]`. Kept: "we move
  faster" as a mitigation that names no action under way. Kept: "a $40B market" with no basis (the market pattern), with
  `[who buys, how many, what each pays]`.
- Dissent, Kept, answered only in part: the Team lens's objection to "a world-class team". Slide 6, "Our CTO built the
  clinic scheduling engine at her last company, used by 2,000 clinics.", answers it for the CTO alone, and "the founders
  hold 8,000,000" names more than one founder. The memo's Team section is to carry the slide 6 line, and the objection
  stays for the other founders as `[one specific achievement for each other founder, and their role]`. Its Fix cell
  says it is answered in part and quotes the slide 6 line with its place.
- The fix list quotes the 45% as stated; it never restates a figure in words ("nearly half").
- The memo's Open questions section lists its own bracketed asks in full; a pointer to the answer's Open asks does not
  pass, since the memo is handed on alone.
- With a subagent tool, the five lenses run as subagents launched in one message, and the refute pass as one subagent
  per objection that survived the quote check, launched in one message; one subagent deciding several objections, even
  one at a time, does not pass. The answer says how both ran.
- "MRR $40,000 in October, up from $12,000 in April" is quoted; no growth rate is worked out.
- No sentence recommends investing; no firm or investor is named as a voice, as the lead, or inside the memo (the
  Sources citations the skill prescribes are excepted); no score.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Partial.** It made the five calls with the expected arguments (plus today's burn and revenue, equal to the plan),
used every figure as the tool printed it, labelled the exits the founders' assumptions with their reasons, called the
terms the calculator's defaults, ranked the customer concentration first and wrote it into Top risks, kept "we move
faster" as an intention, carried the slide 6 line with a bracket for the other founders, and quoted the MRR line with
no growth rate. The five lenses ran as subagents launched together. It fell short in five places. The refute pass ran
as one subagent deciding all eight objections. It paraphrased the `exit_is_shared_amount` statement in Numbers instead
of quoting it under the table. It gave the flag only in Numbers, because the skill put flags in the fix list in one
place and in Numbers in another. Its memo's Open questions pointed to the answer's list, which the champion would not
receive. Its fix list turned the founder's 45% into "nearly half". Since this run the skill launches one refute
subagent per objection in a single message, quotes the statement word for word with its key under the table, puts
each flag in both places with its meaning from a flag table, lists the memo's Open questions in full, says in a Fix
cell when an objection is answered in part, and leaves out today's burn and revenue when they equal the plan. The eval
has not been run again.

> **Biggest fixes**
>
> 1. **The memo leaves out its biggest risk.** Your notes say "Our largest customer, a 40-location chain, is 45% of MRR." The draft's only risk is incumbents, so a partner who finds this in diligence will read it as concealed, and that costs your champion credibility.
>
> [...]
>
> - The payouts above use the cap table right after this round, before any later round.
> - The unissued pool takes no part in a sale, so the payout is not the 20% times the exit.
> - [The basis for each exit value: the revenue or clinic count each case assumes.]
>
> **Open questions**
>
> - See the open asks below.
>
> [...]
>
> | 1 | Sinks the case | Traction; Top risks | Traction and evidence; Risks left out; Market and why now; Round and outcome | "Our largest customer, a 40-location chain, is 45% of MRR." (your notes, left out) | Nearly half the headline figure is one account, and the memo names neither the risk nor a mitigation. | State it in Traction and Top risks; add the contract term, renewal date and MRR without the chain. |
>
> [...]
>
> The five lenses ran as separate subagents. The refute pass ran as one subagent deciding the eight objections one at a time, not one subagent per objection; it kept all eight.
>
> [...]
>
> - **A partner is likely to ask:** the new pool is paid for out of the pre-money, so the effective pre-money ($10,500,000.00) and the price per share are below the headline.
>
> [...]
>
> - The exit amount is what shareholders share, with no debt, fees or escrow taken out first.
