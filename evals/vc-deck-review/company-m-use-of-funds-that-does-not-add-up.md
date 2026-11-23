# Eval 1: Company M, a deck whose use of funds does not add up

A test prompt for the `vc-deck-review` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator deal_check` run with these inputs. The answer states the expected behaviour; it is not a recorded
run, and this eval has not been run in a live session. A run passes when it makes the one tool call below (field order
free, money and percents as strings), puts the calculator's mismatch at the top of the ranked fix list, applies the
first- and last-slide rules, and computes nothing in its own text.

## Prompt

> Review my deck before I send it to seed funds on Monday. Slide 1: "Company M. Reimagining freight for a new era."
> Slide 2, Problem: "Small freight brokers lose hours every day re-keying load details from emails into their
> systems." Slide 3, Solution: "Company M reads load emails and fills the broker's system automatically." Slide 4,
> Traction: "38 brokers paying $500 a month as of October; 9 in June." Slide 5, Team: "Our CEO ran operations at a
> 200-truck brokerage for six years; our CTO built document parsing at a payments company." Slide 6, The ask: "We're
> raising a $4M priced seed at a $16M post-money; investors get 25%. Use of funds: 50% engineering, 30% sales, 15%
> operations. 25 months of runway." Slide 7: "Thank you! Questions?" We have $500k in the bank and spend $120k a month
> today with $20k of monthly revenue; after the raise we plan to spend $200k a month, with revenue staying at $20k.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "4000000",
    "post_money": "16000000",
    "stated_investor_percent": "25",
    "cash_on_hand": "500000",
    "planned_monthly_gross_burn": "200000",
    "planned_monthly_revenue": "20000",
    "current_monthly_gross_burn": "120000",
    "current_monthly_revenue": "20000",
    "stated_runway_months": "25",
    "use_of_funds": [
      { "percent": "50" },
      { "percent": "30" },
      { "percent": "15" }
    ]
  }
}
```

## What the calculator prints (excerpt)

```text
  Post-money valuation                                          $16,000,000.00  V + I
  Use of funds: total                                            $3,800,000.00  every line
  Use of funds: share of the raise                                    95.0000%  total/I
  Investors' percent: verdict                                       consistent  within the tolerance is consistent
  Runway: verdict                                                   consistent  within the tolerance is consistent
  Use of funds total: the deck says                                   95.0000%  given
  Use of funds total: the calculator gives                           100.0000%  against the raise (or 100%)
  Use of funds total: difference                                       5.0000%  computed - stated
  Use of funds total: verdict                                         mismatch  within the tolerance is consistent
  A VC is likely to ask                             current_burn_runway_longer  Runway on today's burn is longer than on the planned burn; say which one the deck uses, as a VC will check it against the planned spend
  Overall verdict                                                     mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The calculator's mismatch heads the ranked fix list, ahead of the tiers, as a figure that does not match
  (computed), not refuted and given no tier: the use-of-funds lines add up to 95.0000% of the raise ($3,800,000.00),
  not 100.0000%. The fix is a bracketed ask,
  `[where the rest of the raise goes]`; the answer does not guess the missing line. Dimension 10, Ask and use of funds,
  is marked Contradicted.
- The 25% and the 25 months are consistent; the `current_burn_runway_longer` flag is relayed as a question a partner
  is likely to ask: say which burn the 25 months uses.
- First slide: "Reimagining freight for a new era." fails the first-slide rule (it does not say what the company
  does). The fix moves the founder's own slide-3 line, "Company M reads load emails and fills the broker's system
  automatically.", onto slide 1.
- Last slide: "Thank you! Questions?" is not an ask; the deck is being sent ahead, so the ask on slide 6 should close
  it. The ask lens's objection that "We're raising a $4M priced seed at a $16M post-money; investors get 25%." names
  no milestone survives, with `[the milestone the $4M reaches]`.
- Why now, Market and Competition are Missing (no slide); each enters the ranked fix list as "no slide covers" that
  dimension, with its bracketed ask, and stays an open ask; the four competition levels are four bracketed asks. The
  skill names no competitor.
- Traction is Present, quoted as stated; the answer works out no revenue from "38 brokers paying $500 a month".
- This eval does not grade the marks of Problem, Solution, Product, Business model and Team.
- Which investors: the story reads as a seed story (a product in use and early numbers), matching the founder's
  target, marked as the skill's own judgment, unverified. No firm is named and no score is given.
