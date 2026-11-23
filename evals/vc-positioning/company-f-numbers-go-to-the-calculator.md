# Eval 2: Company F, the ask's numbers go to the calculator

A test prompt for the `vc-positioning` skill. The company is made up. The tool call and the excerpt are from a real
`equity_calculator deal_check` run with these inputs. "Expected answer" states the expected behaviour, and "Recorded
answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-22): the third run of this eval and the first
after the skill fixes the two earlier runs exposed, with the verdict Partial. A run passes when it makes the one tool
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

**Partial: one clause met only in part.** It loaded vc-positioning, made the one `equity_deal_check` call above with
the expected arguments, put the two calculator mismatches at the top of the survivors without a refute pass, kept the
tool's 15.33 months as printed in the rewrites too (it shortens the $12,000,000.00 post-money to "$12M post" twice),
quoted the growth rate as not checked and relayed the runway flag as a common benchmark, not a rule. The third clause is met only in part: its repeatable line says weekly
active users "more than doubled in six months, from 2,000 to 4,500", a comparison that neither the tool nor the founder
made. The survivors table ranks the two calculator rows "Ends the meeting", as the skill's text did when it ran. Two
earlier runs the same day failed. The first loaded vc-deal-math instead: no adversarial review, three calculator calls
and the growth rate worked out by hand. The second loaded vc-positioning but made a second `equity_deal_check` call
that no one asked for, working the 20% back to a pre-money, and rounded the tool's 15.33 months to 15 in the rewrites
and the prep script. After it, step 4 of the skill gained one call per version of the ask and the tool's values as
printed; this run came after that change. The second and third runs came after the skill's description and its "When
to use it" list gained this prompt's opening words, "check our story and our ask", so their routing shows that this
wording now reaches vc-positioning, not that other wordings do.

> The review is done: two of the deck's own numbers disagree with each other, and the story has no stated buyer or milestone.
>
> ## The biggest issues
>
> 1. **The ask does not add up.** $2M at a $10M pre-money sells 16.6667% of the company, not 20% (post-money is $12,000,000.00).
> 2. **The runway claim does not add up.** $300k in the bank plus the $2M raise at $150k a month is 15.33 months, not 18, a gap of 2.67 months.
> 3. **The round reaches nothing a partner can name.** There is no revenue for 18 months, no named milestone, and spend is unchanged, so the money appears to run out before any test of whether anyone pays.
>
> ## Adversarial review
>
> Six lenses attacked the text as independent subagents, and a separate pass judged each objection against your own words. The two calculator rows were not put through the refute pass, because the calculator computed them.
>
> ### Survivors
>
> | Rank | Tier             | Lens                                   | Your line                                                                                      | Why a partner reads it that way                                                                                                                                                            | Rewrite or evidence to add                                                                                                                                   |
> | ---- | ---------------- | -------------------------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
> | 1    | Ends the meeting | Calculator                             | "a $2M priced seed at a $10M pre-money for 20% of the company"                                 | The three figures cannot all be true: the computed share is 16.6667%, a difference of -3.3333 points.                                                                                      | Say "$2M at a $10M pre-money, $12M post, 16.6667% of the company", or change the raise or the valuation and rerun the check.                                 |
> | 2    | Ends the meeting | Calculator; the ask and milestones     | "The deck says 18 months of runway."                                                           | The stated cash, raise and burn give 15.33 months. That is also below the 18-month mark partners commonly ask about, and it ends before your no-revenue period does.                       | State 15.33 months, or change the burn or the raise and rerun the check.                                                                                     |
> | 3    | Ends the meeting | All except team                        | "no revenue yet, and we don't plan any revenue in the next 18 months"                          | Nothing says who pays or how the company makes money. The round is spent with no test of willingness to pay and no other milestone that makes the next round raisable.                     | `[who pays and what they pay for]`, `[why no revenue for 18 months]`, `[the milestone this round reaches, if not revenue]`                                   |
> | 4    | Weakens it       | Clarity; market; traction; competition | "Company F helps truck fleets pay their drivers the same day."                                 | "Helps" could mean payroll software, a payments product or an advance of money. The line names no customer (fleet or driver), no alternative, no insight and no reason this is the moment. | `[what the product is]`, `[who the customer is]`, `[what fleets do today instead]`, `[what changed to make this possible now]`                               |
> | 5    | Weakens it       | Clarity; market; traction              | "Weekly active users went from 2,000 to 4,500 over the last six months, which is 15% a month." | This is your only traction figure and it has a period but no definition. A partner cannot map "users" to fleets, payouts or buyers.                                                        | `[who a user is: driver, fleet or fleet staff]`, `[what action counts as active]`, `[number of fleets live]`, `[payouts and dollar volume, with the period]` |
> | 6    | Weakens it       | The ask and milestones                 | "We spend $150k a month today and plan to keep spending $150k a month after the raise."        | Identical spend before and after reads as buying time, not progress. No hire, launch or pilot is named.                                                                                    | `[what the $2M funds that you cannot do today]`, `[where the $150k a month goes, by line]`                                                                   |
> | 7    | Weakens it       | Competition and wedge                  | "truck fleets"                                                                                 | This is a whole category, not a chosen first market.                                                                                                                                       | `[which fleets first: size, freight type or geography]`, `[how many such fleets exist, with the source]`                                                     |
>
> ### Dropped
>
> None. Your text answered no objection, because each one is about something the text does not yet contain. The team lens returned nothing because there is no line about the founders; that is listed under open asks.
>
> [...]
>
> ## Say and avoid
>
> | Your line                                                        | What a partner is likely to hear           | Say instead                                                                                                | Source                                     |
> | ---------------------------------------------------------------- | ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
> | "We're raising a $2M priced seed…" with no milestone after it    | They cannot tell what the money buys.      | "We're raising $2M to reach `[milestone]` by `[date]`."                                                    | YC seed deck guide; YC seven questions (7) |
> | "we don't plan any revenue in the next 18 months" with no reason | The obvious risk is left out.              | "We don't charge until `[condition]` because `[reason]`; the risk is `[risk]` and we test it by `[test]`." | YC "How to Apply"                          |
> | "The deck says 18 months"                                        | You do not own the figure.                 | "This gives us 15.33 months at $150k a month."                                                             | Calculator result                          |
> | "Weekly active users" with no definition                         | A usage count that may hide the real unit. | "`[N]` drivers at `[N]` fleets received a same-day payout last week."                                      | a16z "16 Startup Metrics"                  |
>
> ## Numbers
>
> **`equity_deal_check` verdict: mismatch.**
>
> | Figure         | Deck states  | Calculator   | Difference     | Verdict  |
> | -------------- | ------------ | ------------ | -------------- | -------- |
> | Investor share | 20.0000%     | 16.6667%     | -3.3333 points | Mismatch |
> | Runway         | 18.00 months | 15.33 months | -2.67 months   | Mismatch |
>
> - **Post-money:** $12,000,000.00. Existing holders keep 83.3333% before any option pool, SAFEs or notes, none of which you mentioned.
> - **Runway assumptions:** the whole raise lands at once, there are no fees, and burn stays at $150,000.00 with zero revenue. Current and planned burn give the same 15.33 months.
> - **Flag:** runway is below the 18-month band. That is a common benchmark, not a rule.
> - **"15% a month":** not checked, because no tool here computes growth rates. A partner will test it against 2,000 and 4,500 over six months, so confirm it yourself before it goes in the deck.
>
> [...]
>
> ## Tightened narrative
>
> **One-liner options** (each needs one fact from you):
>
> - "Company F is `[payroll software / a payments product / a pay advance]` that lets truck fleets pay drivers the same day."
> - "Truck fleets use Company F to pay drivers the same day instead of `[how they are paid today]`."
>
> **30-second version:**
>
> > Company F is `[what it is]` for `[which fleets]`. Today drivers wait `[how long]` to be paid, which costs fleets `[cost]`. Weekly active `[drivers / fleets]` grew from 2,000 to 4,500 over the last six months, across `[N]` fleets. We don't charge yet because `[reason]`; `[who]` will pay `[what]` once `[condition]`. We're raising $2M at a $10M pre-money, $12M post, for 16.6667% of the company. With $300k in the bank that gives us 15.33 months at $150k a month to reach `[milestone]`.
>
> **Repeatable line:** "Truck fleets use Company F to pay drivers the same day, and weekly active `[drivers]` more than doubled in six months, from 2,000 to 4,500."
>
> [...]
>
> This is not investment, legal or tax advice. Have a lawyer review fundraising materials before they are sent widely, and get agreement from any customer you name in the deck.
