# Eval 1: Company J, figures that disagree across the deck and the one-pager

A test prompt for the `vc-claims-check` skill. The company is made up. The two tool calls and their excerpts are from
real `equity_calculator deal_check` runs with these inputs; the rest states the expected behaviour and is not a
recorded run. A run passes when it makes one `equity_deal_check` call per document's version of the ask (field order
free, money and percents as strings), compares the other figures as stated, and computes nothing in its own text.

## Prompt

> Do my numbers agree? Deck, slide 9 (Ask): "Raising $2.5M at a $10M post-money; investors get 25%. This gives us 24
> months of runway." One-pager, paragraph 4: "We're raising $2.5M at a $10M post-money for 20% of the company." Deck,
> slide 5 (Traction): "120 paying customers as of October." One-pager, paragraph 2: "150 paying customers as of
> October." Deck, slide 5 also says "$38k MRR in October", and the one-pager says "$450k ARR". We have $400k in the
> bank and plan to spend $120k a month after the raise; the 24 months counts no revenue at all, to be safe. Our
> billing dashboard shows the customer count and MRR.

## Expected tool call

`equity_deal_check`, twice: once with the deck's figures, once with the one-pager's. The deck's call:

```json
{
  "inputs": {
    "investment": "2500000",
    "post_money": "10000000",
    "stated_investor_percent": "25",
    "cash_on_hand": "400000",
    "planned_monthly_gross_burn": "120000",
    "planned_monthly_revenue": "0",
    "stated_runway_months": "24"
  }
}
```

What the calculator prints for the deck (excerpt):

```text
  Pre-money valuation (V)                            $7,500,000.00  post-money - I (worked from it)
  Net runway, planned burn                            24.17 months  (cash + I)/net burn
  Investors' percent: the deck says                       25.0000%  given
  Investors' percent: the calculator gives                25.0000%  the investor's cap-table share
  Investors' percent: verdict                           consistent  within the tolerance is consistent
  Runway: the deck says                               24.00 months  given
  Runway: the calculator gives                        24.17 months  (cash + I)/net burn, planned (else current)
  Runway: verdict                                       consistent  within the tolerance is consistent
  Overall verdict                                       consistent  mismatch if any check is; consistent if all are; not_checked with none
```

The one-pager's call:

```json
{
  "inputs": {
    "investment": "2500000",
    "post_money": "10000000",
    "stated_investor_percent": "20"
  }
}
```

What the calculator prints for the one-pager (excerpt):

```text
  Investors' percent: the deck says                       20.0000%  given
  Investors' percent: the calculator gives                25.0000%  the investor's cap-table share
  Investors' percent: difference                           5.0000%  computed - stated
  Investors' percent: verdict                             mismatch  within the tolerance is consistent
  Overall verdict                                         mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The one-pager's "20% of the company" is Contradicted: the calculator gives 25.0000% for $2.5M at a $10M post-money,
  a difference of 5.0000%. It is a kept attack that skips the refute pass, and it leads the answer. The fix is to state
  the deck's 25% in the one-pager once the founder confirms which is meant.
- The deck's "investors get 25%" and "24 months of runway" pass the arithmetic (consistent; 24.17 months on the
  planned burn with no revenue, as the founder stated). The answer says the runway check counts no revenue because the
  founder said so.
- "120 paying customers as of October" and "150 paying customers as of October" are quoted side by side with their
  places and marked Contradicted. No difference is computed. The fix asks the founder to confirm one figure against
  the billing dashboard and use it in both documents.
- "$38k MRR in October" and "$450k ARR" are not compared: one is monthly and one yearly, and the skill converts
  neither. Both are Needs a source, with an ask to state one figure, in one form, with its period. If the skeptic
  attacks this pair, the refute pass keeps the attack as a missing source, not a conflict, so the verdict stays Needs
  a source and is never Contradicted.
- Through the MCP tool, the one-pager's computed share comes back as the fraction 0.250000 and the difference as
  0.050000; the answer shows them as 25.0000% and 5.0000% by moving the decimal point two places, the form the report
  prints, and rounds neither.
- Every percent, valuation and month figure in the answer comes from the tool or is quoted from the prompt.
