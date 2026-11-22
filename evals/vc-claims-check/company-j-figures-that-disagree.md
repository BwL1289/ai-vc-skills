# Eval 1: Company J, figures that disagree across the deck and the one-pager

A test prompt for the `vc-claims-check` skill. The company is made up. The two tool calls and their excerpts are from
real `equity_calculator deal_check` runs with these inputs. "Expected answer" states the expected behaviour, and
"Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22). A run passes when it makes one
`equity_deal_check` call per document's version of the ask (field order free, money and percents as strings), compares
the other figures as stated, and computes nothing in its own text.

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

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-22, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass.** Two `equity_deal_check` calls with the inputs above, the one-pager's 20% leading as a mismatch, the customer
counts side by side as Contradicted, and MRR and ARR not converted. Short of the expected answer: the MRR line is
Supported on the billing dashboard rather than Needs a source, and the runway attack skipped its refute pass.

> **No: two pairs of figures contradict each other, and one pair can't be compared as written.** The raise, the post-money and the 24 months of runway hold up.
>
> ## What a partner is likely to check first
>
> 1. **Percent sold: the one-pager is wrong.** The calculator puts $2.5M at a $10M post-money at 25.0000% for investors, on a $7.5M pre-money. The deck's "investors get 25%" is consistent. The one-pager's "for 20% of the company" is a mismatch by 5.0000 points. Change the one-pager to 25%. If 20% is the deal you actually want, the raise or the post-money has to change in both documents.
>
> 2. **Customer count: the deck and the one-pager disagree.** The deck says "120 paying customers as of October." and the one-pager says "150 paying customers as of October." That is the same metric for the same month with two counts. Use the number your billing dashboard shows for October in both, and note the date it was read.
>
> 3. **MRR against ARR: not comparable as stated.** "$38k MRR in October" is a monthly figure with a period; "$450k ARR" has no period or definition. I did not convert one into the other, but a partner will annualise the MRR and compare it with $450k. State one figure, in one form, with its month, in both documents, and say how ARR is defined if you keep it.
>
> The skeptic pass ran as a separate subagent and raised the percent sold, the customer count and the runway. No attack was dropped as ungrounded; the runway attack was settled by the calculator.
>
> ## Claims table
>
> | #   | Claim                                                                 | Where                       | Evidence you named | Verdict                                                     | Fix                                                   |
> | --- | --------------------------------------------------------------------- | --------------------------- | ------------------ | ----------------------------------------------------------- | ----------------------------------------------------- |
> | 1   | "for 20% of the company" / "investors get 25%"                        | One-pager ¶4 / Deck slide 9 | None               | **Contradicted**                                            | One-pager to 25%                                      |
> | 2   | "120 paying customers" / "150 paying customers", both "as of October" | Deck slide 5 / One-pager ¶2 | Billing dashboard  | **Contradicted**                                            | Use the dashboard's October count in both             |
> | 3   | "$450k ARR"                                                           | One-pager                   | None               | **Needs a source**                                          | Add its period and definition, or replace it with MRR |
> | 4   | "24 months of runway"                                                 | Deck slide 9                | None               | **Needs a source** (arithmetic consistent)                  | Have the bank balance and spending plan ready         |
> | 5   | "$2.5M at a $10M post-money"                                          | Deck slide 9, One-pager ¶4  | None               | **Needs a source** (arithmetic consistent, documents agree) | Nothing to change in the text                         |
> | 6   | "$38k MRR in October"                                                 | Deck slide 5                | Billing dashboard  | **Supported**                                               | A partner will ask for the dashboard export           |
>
> "Supported" means supported by what you say you can show; I have not seen the dashboard.
>
> ## Deal terms from the calculator
>
> - **Deck figures:** consistent. Investors get 25.0000%, and existing holders keep 75.0000%.
> - **Runway:** consistent. $400k in the bank plus the $2.5M raise, at $120k a month with no revenue, comes to 24.17 months against your stated 24.
> - **One-pager figures:** mismatch. It states 20.0000% where the calculator computes 25.0000%.
>
> [...]
>
> This is not investment, legal or tax advice; have a lawyer review the materials before they go out widely.
