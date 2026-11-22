# Eval 2: Company F, the ask's numbers go to the calculator

A test prompt for the `vc-positioning` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator deal_check` run with these inputs. "Expected answer" states the expected behaviour, and "Recorded
answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22). A run passes when it makes the one tool
call below (field order free, money and percents as strings), puts the calculator's mismatches at the top of the
surviving objections, and computes nothing in its own text. The verdict is Pass when every clause of that sentence is
met, Partial when exactly one clause is missed or met only in part, and Fail when two or more are missed; a shortfall
against the other points of the expected answer is noted but does not change the verdict.

## Prompt

> Check our story and our ask. Company F helps truck fleets pay their drivers the same day. We're raising a $2M priced
> seed at a $10M pre-money for 20% of the company. We have $300k in the bank and no revenue yet, and we don't plan
> any revenue in the next 18 months. We spend $150k a month today and plan to keep spending $150k a month after the
> raise. The deck says 18 months of runway. Weekly active users went from 2,000 to 4,500 over the last six months,
> which is 15% a month.

## Expected tool call

`equity_deal_check`, once:

```json
{
  "inputs": {
    "investment": "2000000",
    "pre_money": "10000000",
    "stated_investor_percent": "20",
    "cash_on_hand": "300000",
    "planned_monthly_gross_burn": "150000",
    "planned_monthly_revenue": "0",
    "current_monthly_gross_burn": "150000",
    "current_monthly_revenue": "0",
    "stated_runway_months": "18"
  }
}
```

## What the calculator prints (excerpt)

```text
  Post-money valuation                                 $12,000,000.00  V + I
  Investors' percent: the deck says                          20.0000%  given
  Investors' percent: the calculator gives                   16.6667%  the investor's cap-table share
  Investors' percent: difference                             -3.3333%  computed - stated
  Investors' percent: verdict                                mismatch  within the tolerance is consistent
  Runway: the deck says                                  18.00 months  given
  Runway: the calculator gives                           15.33 months  (cash + I)/net burn, planned (else current)
  Runway: difference                                     -2.67 months  computed - stated
  Runway: verdict                                            mismatch  within the tolerance is consistent
  A VC is likely to ask                             runway_below_band  Planned runway is under 18 months; a VC is likely to ask whether the raise reaches the next milestone (a common benchmark, not a rule)
  Overall verdict                                            mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

## Expected answer

- The two calculator mismatches lead the surviving objections, ranked as ends the meeting and not put through the
  refute pass: the deck's 20% against the calculator's 16.6667% (a $12,000,000.00 post-money), and the deck's 18.00
  months against 15.33 months. Each quotes the deck's figure as stated and gives the tool's value.
- Through the MCP tool, the investors' share comes back as the fraction 0.166667 and the difference as -0.033333; the
  answer shows them as 16.6667% and -3.3333% by moving the decimal point two places, the form the report prints, and
  rounds neither.
- The `runway_below_band` flag is relayed as a question a partner is likely to ask, a common benchmark and not a rule.
- "15% a month" is quoted as stated and marked "not checked: no tool computes this". The answer neither confirms,
  corrects nor annualizes it.
- The ask lens's objection about what the $2M reaches survives, because the material names no milestone; the evidence
  to add is a bracketed ask, such as `[the milestone the $2M reaches]`.
- Every percent, valuation and month figure in the answer comes from the tool or is quoted from the prompt.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-22, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Fail: two clauses missed.** It loaded vc-positioning, put the two calculator mismatches at the top of the survivors
and quoted the growth rate unchecked, but it missed two clauses: it made a second `equity_deal_check` call that no one
asked for, working the 20% back to a pre-money, and its own text rounds the tool's 15.33 months to 15 in the rewrites
and the prep script. Since this run, step 4 of the skill asks for one call per version of the ask and the tool's values
as printed; the eval has not been run again. A first run the same day, before this commit's skill changes, loaded
vc-deal-math instead: no adversarial review, three calculator calls and the growth rate worked out by hand, also a fail.
This run came after the skill's description and its "When to use it" list gained this prompt's opening words, "check our
story and our ask", so its routing shows that this wording now reaches vc-positioning, not that other wordings do.

> Two of your ask's numbers don't agree with each other, and a partner will find both in the first minute: the round sells 16.6667%, not 20%, and it buys 15.33 months of runway, not 18.
>
> ## The biggest issues
>
> 1. **Percent sold.** $2M on a $10M pre-money is a $12,000,000.00 post-money, so the investor gets 16.6667%, not the 20% you state.
> 2. **Runway.** $300k in the bank plus the $2M raise at $150k a month is 15.33 months, which is 2.67 months short of the deck's 18.
> 3. **No revenue and no milestone in its place.** You plan no revenue for the whole period the round funds, and nothing says who will pay or what the money proves.
>
> ## Numbers
>
> The calculator's verdict on the ask is **mismatch**.
>
> | Figure                              | You state    | Calculator   | Difference     | Verdict  |
> | ----------------------------------- | ------------ | ------------ | -------------- | -------- |
> | Percent sold                        | 20.0000%     | 16.6667%     | -3.3333 points | Mismatch |
> | Runway at $150k a month, no revenue | 18.00 months | 15.33 months | -2.67 months   | Mismatch |
>
> - **Fixing the percent:** pick one pair. Either keep the $10M pre-money and say 16.6667%, or keep 20% for $2M, which the calculator works back to an $8,000,000.00 pre-money and a $10,000,000.00 post-money. "$10M" and "20%" together suggest the $10M may be a post-money figure labelled as pre-money.
> - **Runway assumptions:** the calculator assumes the whole raise lands at once, no fees, and burn stays flat. It also flags 15.33 months as below an 18-month benchmark, which is a common question and not a rule.
> - **No pool or SAFEs counted:** you gave no option pool, SAFEs or notes, so the 16.6667% is the headline figure only.
> - **Growth rate, not checked:** no tool computes "2,000 to 4,500 over the last six months, which is 15% a month". A partner will test whether the endpoints and the monthly rate agree, so say whether the 15% is compounded or an average, and confirm it before it goes out.
>
> ## Adversarial review
>
> Six lenses ran as independent subagents, and each objection then got its own refute pass against your material.
>
> | Rank | Tier             | Lens                                        | Your line                                                               | Why a partner reads it that way                                                                            | Rewrite or evidence to add                                                                                                                               |
> | ---- | ---------------- | ------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | 1    | Ends the meeting | Calculator                                  | "a $2M priced seed at a $10M pre-money for 20% of the company"          | The three figures cannot all be true; the computed share is 16.6667%.                                      | State one consistent set (see Numbers).                                                                                                                  |
> | 2    | Ends the meeting | Calculator                                  | "The deck says 18 months of runway."                                    | Cash plus the raise at the stated spend gives 15.33 months.                                                | Say 15 months, or change the raise or spend so 18 is true.                                                                                               |
> | 3    | Ends the meeting | Clarity, Market, Traction, Competition, Ask | "no revenue yet, and we don't plan any revenue in the next 18 months"   | The round buys no evidence that anyone will pay, and nothing names what will make the next round raisable. | `[who pays and how you charge]`, `[the milestone this round reaches instead of revenue]`, `[any paid pilot or pricing test]`                             |
> | 4    | Weakens it       | Clarity, Market, Traction, Competition      | "Weekly active users went from 2,000 to 4,500 over the last six months" | It has a period but no definition, and your customer is the fleet, not the user.                           | `[who counts as a user and what makes one active]`, `[number of fleets behind the 4,500]`, `[share of users in the largest few fleets]`                  |
> | 5    | Weakens it       | Clarity, Market, Competition                | "Company F helps truck fleets pay their drivers the same day."          | It gives an outcome but not the kind of company, the problem today, the alternative, or a first segment.   | `[payroll software, payments rail or wage advance]`, `[how drivers are paid today and what the delay costs]`, `[first segment: fleet size, type, count]` |
> | 6    | Weakens it       | Traction, Ask                               | "plan to keep spending $150k a month after the raise"                   | The money reads as paying for the status quo, with the amount chosen for duration and not for an outcome.  | `[use of funds by line]`, `[why this milestone needs $2M]`                                                                                               |
>
> **Dropped**
>
> - **Runway attributed to the deck, not owned by the founder (Ask lens):** not grounded, because that line is you describing the deck to me, not the deck's wording. The other half of that objection, runway with no destination, is merged into row 6.
>
> **Nothing found**
>
> - **Team lens:** your material has no line about the founders, so there was nothing to object to. That is a gap, listed under open asks.
>
> [...]
>
> ## Say and avoid
>
> | Your line                                                         | What a partner is likely to hear     | Say instead                                                                                           | Source                                     |
> | ----------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------------ |
> | "We're raising a $2M priced seed" with no milestone after it      | Cannot tell what the money buys      | "We're raising $2M to reach `[milestone]` by `[date]`."                                               | YC seed deck guide; YC seven questions (7) |
> | "we don't plan any revenue in the next 18 months", with no reason | The obvious risk, left unexplained   | "We are not charging until `[condition]` because `[reason]`; `[who]` pays after that."                | YC "How to Apply"                          |
> | "18 months of runway"                                             | A figure that fails a one-line check | "15 months of runway at $150k a month."                                                               | Calculator                                 |
> | "Weekly active users" with no definition                          | Usage, not adoption by a buyer       | "`[N]` fleets; `[drivers or staff]` who `[action]` each week went from 2,000 to 4,500 in six months." | a16z "16 Startup Metrics"                  |
>
> [...]
>
> ## Prep script
>
> Run this with an existing investor about 45 minutes before any outside meeting. If you have none, use a founder who recently raised a seed, and treat their answers on items 5 and 7 as guesses.
>
> [...]
>
> This is not investment, legal or tax advice. Have a lawyer review the materials before you send them widely.
