# Eval 1: Company M, a deck whose use of funds does not add up

A test prompt for the `vc-deck-review` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator deal_check` run with these inputs. "Expected answer" states the expected behaviour, and "Recorded
answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when it makes the one tool
call below (field order free, money and percents as strings), puts the calculator's mismatch at the top of the ranked
fix list, applies the first- and last-slide rules, and computes nothing in its own text. The verdict is Pass when
every clause of that sentence is met, Partial when exactly one clause is missed or met only in part, and Fail when two
or more are missed; a shortfall against the other points of the expected answer is noted but does not change the
verdict. The recorded run is a Pass with two shortfalls, which its grader called partial overall: it made up the
flag's question and gave no "no slide covers" rows. Both were fixed in the skill after it.

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
  is likely to ask: say which burn the 25 months uses. Over MCP the tool returns the code only; the question comes
  from the skill's Calculator flags table, which says what the excerpt's command-line line prints beside the code.
- First slide: "Reimagining freight for a new era." fails the first-slide rule (it does not say what the company
  does). The fix moves the founder's own slide-3 line, "Company M reads load emails and fills the broker's system
  automatically.", onto slide 1.
- Last slide: "Thank you! Questions?" is not an ask; the deck is being sent ahead, so the ask on slide 6 should close
  it. The ask lens's no-milestone objection on slide 6 survives, quoting either slide-6 line ("We're raising a $4M
  priced seed at a $16M post-money; investors get 25%." or "25 months of runway."), with a bracketed milestone ask
  such as `[the milestone the $4M reaches]`.
- Why now, Market and Competition are Missing (no slide); each enters the ranked fix list as "no slide covers" that
  dimension, its own row even where a lens objection on another line touches it, with its bracketed ask, and stays an
  open ask; the four competition levels are missing, each a bracketed ask in the open asks (Doing nothing may instead
  quote slide 2's line word for word, marked implied). The skill names no competitor.
- Traction is Present, quoted as stated; the answer works out no revenue from "38 brokers paying $500 a month".
- This eval does not grade the marks of Problem, Solution, Product, Business model and Team.
- Which investors: the story reads as a seed story (a product in use and early numbers), matching the founder's
  target, marked as the skill's own judgment, unverified. No firm is named and no score is given.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass, with two shortfalls against the expected answer (its grader called the run partial overall).** It made the one
`equity_deal_check` call above, put the use-of-funds mismatch at the head of the ranked fix list with no tier, applied
the first- and last-slide rules, and computed nothing in its own text: no revenue was worked out from "38 brokers paying
$500 a month". Short of the expected answer: it relayed the `current_burn_runway_longer` flag with a question it made
up ("what the extra spend buys") rather than "say which burn the 25 months uses", since the MCP result carries the
code only and the skill pointed to vc-deal-math's flag table without loading it; and Why now, Market and Competition
got no "no slide covers" rows, folded into lens objections on other lines, with the direct and indirect competition
asks missing from the open asks. Smaller points: the first-slide fix left the ranked list once its objection was
dropped as answered, the Doing nothing level paraphrases slide 2, the headline shortens 95.0000% to 95%, and the
investor fit calls seed funds "the right kind of investor". The milestone objection was raised on the other slide-6
line, which the expected answer now accepts. Since this run the skill carries each flag's meaning itself (Calculator
flags), gives each uncovered dimension, failed slide rule and move fix its own row, lists every missing competition
level's ask, quotes a level word for word or marks it implied, keeps the tool's digits in the headline, and never calls
a kind of investor right; the eval has not been run again.

> # Deck review: Company M
>
> The deck is not ready to send: the use-of-funds lines don't add up to the raise, and the ask buys time without naming what it reaches. The equity calculator checked the ask, seven independent lenses attacked the deck, and each objection was then tested against your own material.
>
> ## The biggest fixes
>
> 1. **Slide 6: the use of funds adds up to 95%, not 100%.** The calculator totals your three lines at $3,800,000.00 against a $4,000,000 raise.
> 2. **Slide 6: the ask names 25 months, not a milestone, and your plan has revenue flat at $20k.** A partner will read 30% for sales with no revenue growth as a raise that buys time only.
> 3. **No slide says how many small freight brokers exist.** With no market, competition or why-now slide, a partner cannot tell if this is venture-sized.
>
> ## Ranked fix list
>
> | Rank | Tier                                 | Slide | Lens                        | The deck's line                                                                                              | Why a partner reads it that way                                                                                                       | Fix                                                                                                                               |
> | ---- | ------------------------------------ | ----- | --------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
> | 1    | Figures that do not match (computed) | 6     | Calculator                  | "Use of funds: 50% engineering, 30% sales, 15% operations."                                                  | The lines total 95.0000% ($3,800,000.00); the difference is 5.0000% of the raise. An unchecked sum casts doubt on every other figure. | Add `[the missing 5% line]` or correct the three shares.                                                                          |
> | 2    | Ends the meeting                     | 6     | Opening and close; Ask      | "25 months of runway."                                                                                       | It is a duration, not a destination. Nothing says what makes the next round raisable.                                                 | Add `[the broker count, monthly revenue or product milestone the $4M reaches, and the month]`.                                    |
> | 3    | Ends the meeting                     | 6     | Traction and business model | "Use of funds: 50% engineering, 30% sales, 15% operations."                                                  | Your note says "revenue staying at $20k" after the raise. That will come out with the model, and it undercuts slide 4's growth.       | State `[planned broker count or revenue after the raise, by date]`. If flat revenue is only a cautious runway assumption, say so. |
> | 4    | Ends the meeting                     | 2, 4  | Market and why now          | "Small freight brokers lose hours every day…" and "38 brokers paying $500 a month as of October; 9 in June." | The buyer is named but never defined or counted. The 38 could be the start of a large market or most of a niche.                      | Add a market slide: `[definition of "small", number of such brokers, with source and date]`.                                      |
> | 5    | Weakens it                           | 3     | Competition                 | "Company M reads load emails and fills the broker's system automatically."                                   | The product sits on a system someone else owns. That vendor could add the feature and controls access.                                | Add a competition slide: `[which systems you fill, how you connect, why the vendor won't build it]`.                              |
> | 6    | Weakens it                           | 1     | Market and why now          | "Company M. Reimagining freight for a new era."                                                              | "A new era" promises a why-now the deck never gives.                                                                                  | Add `[what changed, with date and source]`, or cut the phrase.                                                                    |
>
> [...]
>
> **Dropped**
>
> - **Slide 1 doesn't say what the company does** (Opening and close; Problem and solution): answered by slide 3, "Company M reads load emails and fills the broker's system automatically." Move that line to slide 1 in place of the tagline.
>
> [...]
>
> ## Competition at four levels
>
> | Level                 | What the deck says                | Ask                                                            |
> | --------------------- | --------------------------------- | -------------------------------------------------------------- |
> | Direct                | Missing                           | `[Who sells the same thing to small brokers, and why you win]` |
> | Indirect              | Missing                           | `[Other ways brokers get load details into their systems]`     |
> | Adjacent and platform | Missing                           | `[The system your buyer already uses that could add this]`     |
> | Doing nothing         | Slide 2 implies re-keying by hand | `[What hand entry costs a broker against $500 a month]`        |
>
> [...]
>
> - **Flag, `current_burn_runway_longer`:** at today's burn the same cash lasts 45.00 months net. A partner is likely to ask what the extra spend buys, which is the same gap as fix 2.
>
> [...]
>
> ## Which investors the story fits
>
> This is a judgment, unverified. A product in use with early numbers ("38 brokers paying $500 a month as of October; 9 in June") reads as a seed story, so seed funds are the right kind of investor. It fits larger firms that also do seed less well, because "25 months of runway" names no milestone that makes the next round possible. A sector fund would look for the freight shift that "a new era" claims but never states.
>
> [...]
