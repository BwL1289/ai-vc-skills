# Eval 4: Company RD, pro rata larger than the room the lead and the firm commitments leave

A test prompt for the `vc-raise-plan` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. Every figure under "Expected answer" is pasted
from what `equity_calculator raise_pipeline` printed for these inputs; none is typed by hand. A run passes when it
makes the one tool call below (field order free, money and percents as strings), quotes the allocation left below zero
and `pro_rata_exceeds_left` as printed, never counts the soft commitments, leaves the pro rata and the round size to
the founder, asks for no investor list (the question is about coverage alone), and computes nothing in its own text.

## Prompt

> How much of the round is left? We're raising $2M; our lead is in for $1.2M, one angel has signed for $300k (firm),
> and two more angels said maybe $200k each (soft). Both our existing investors want their full pro rata, $300k each.
> Funnel: 12 first meetings and 3 partner meetings; on our numbers a quarter of first meetings reach a partner meeting
> and 40% of partner meetings give a term sheet. We want 2 term sheets. $800k in the bank, $100k a month burn, no
> revenue yet, and 5 months to raise.

## Expected tool call

`equity_raise_pipeline`, once:

```json
{
  "inputs": {
    "round_size": "2000000",
    "lead_cheque": "1200000",
    "commitments": [
      { "amount": "300000", "kind": "firm" },
      { "amount": "200000", "kind": "soft" },
      { "amount": "200000", "kind": "soft" }
    ],
    "pro_rata": ["300000", "300000"],
    "stages": [
      { "name": "First meeting", "investors": 12, "rate_percent": "25" },
      { "name": "Partner meeting", "investors": 3, "rate_percent": "40" }
    ],
    "term_sheets_wanted": 2,
    "runway": {
      "cash_on_hand": "800000",
      "phases": [{ "from_month": 1, "gross_burn": "100000" }],
      "months_to_raise": 5
    }
  }
}
```

## What the calculator prints (excerpt)

```text
  Soft commitments, never counted (S)                                        $400,000.00  the soft commitments, shown on their own
  Pro rata (P)                                                               $600,000.00  every pro rata amount
  Room after the lead and the firm commitments                               $500,000.00  R - L - F
  Allocation left                                                           $-100,000.00  R - L - F - P; below 0, more is counted than the round holds
  Expected term sheets from today's funnel (E)                                      2.40  the sum of each stage's investors × its rate to a term sheet; an expectation from the founder's rates, not a forecast
  More first-stage targets needed beyond today's funnel                                0  ceiling((W - E) / the conversion); 0 when E >= W
  Start raising by (the runway plan's)                                       3.00 months  runway with no raise - months to raise, in months from today
  Flag                                                      soft_commitments_not_counted  At least one commitment is soft: soft commitments are shown on their own line and never counted against the round
  Flag                                                             pro_rata_exceeds_left  The lead's cheque and the firm commitments fit in the round, but the pro rata is larger than the room they leave: the allocation left is below zero
```

## Expected answer

- Coverage, as printed: the room after the lead and the firm commitment $500,000.00, the pro rata $600,000.00, and
  the allocation left $-100,000.00; the soft $400,000.00 is shown apart and never counted, so it does not make the
  gap larger or smaller.
- `pro_rata_exceeds_left` in its words from the flag table: the lead's cheque and the firm commitment fit in the
  round, but the pro rata is larger than the room they leave. It quotes the printed figures and works out no gap of
  its own.
- It leaves the choice to the founder: how much pro rata to take is the founder's and the existing investors' to
  settle, with the founder's lawyer, and a larger round is a question for the vc-round-sizing skill (preview). It
  suggests no amount to cut and no investor to drop.
- The funnel, as printed: on the founder's own rates today's funnel is expected to give 2.40 term sheets, an
  expectation and not a forecast, against the 2 wanted, and 0 more first-stage targets are needed; the start-raising
  month is month 3.
- The question is about coverage alone, so it asks for no investor list, tier rules or batch inputs before the call;
  it offers the tiers, the batches and the tracker after the coverage.
- `soft_commitments_not_counted` with its meaning, and the assumptions it leans on, each `unverified` where the
  result says so: `allocation_rule` and `pro_rata_rule` (each pro rata amount counted in full).
- It closes as not investment, legal or tax advice, and adds, subtracts or divides none of the tool's or the founder's
  figures in its own text.
