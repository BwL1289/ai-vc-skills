# Eval 1: Company RA, "plan our raise" from the founder's own list

A test prompt for the `vc-raise-plan` skill. The company is made up, and so is every investor on its list. "Expected
answer" states the expected behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on
2026-11-24). Every figure under "Expected answer" is pasted from what `equity_calculator raise_pipeline` printed for
these inputs; none is typed by hand. A run passes when it makes the one tool call below (field order free, money and
percents as strings), tiers the founder's list by the founder's rules with every attribute's source or `unverified`,
places the batches from the printed start-raising month, keeps the tracker, never names a firm as a fit and computes
nothing in its own text. The verdict is Pass when every clause of that sentence is met, Partial when exactly one clause
is missed or met only in part, and Fail when two or more are missed; a shortfall against the other points of the
expected answer is noted but does not change the verdict. The recorded run is a Partial. The skill was changed after
that run (see "Recorded answer").

## Prompt

> Plan our raise. We're raising $4M and Fund A has said yes to lead with $2.5M. Our angel has committed $500k and
> signed, so that one's firm; two angels said "probably $250k each", which I'd call soft. Our seed investor has pro
> rata of $400k and wants all of it. Our tracker today: 40 intro asks out, 10 first meetings, 2 partner meetings.
> From our last raise, about half of intro asks turned into a first meeting, 30% of first meetings into a partner
> meeting and a quarter of partner meetings into a term sheet. We want 3 term sheets. We have $1.2M in the bank,
> burn $150k a month on $30k of revenue, and I'd give the raise 6 months. Today is month 0.
>
> New names to tier (none contacted yet):
>
> - Fund B: seed, leads, cheque fits our lead size, devtools, no conflict, warm path through a founder they backed
>   (from that founder).
> - Fund C: seed, leads, cheque fits, infrastructure, no conflict, no warm path (stage and cheque from their site,
>   checked last week).
> - Fund D: seed, leads, cheque fits, devtools, backs a direct competitor (from their portfolio page, I checked).
> - Fund E: seed, follows only, follow-size cheque, devtools, no conflict, warm path through our advisor.
> - Fund F: seed, leads, cheque fits, devtools, no conflict, no warm path (I think they do seed; not sure).
> - Angel G: seed, follows, small cheque, devtools, no conflict, warm path through our angel.
> - Fund H: Series A only, leads, devtools (from their site).
>
> My rules: tier 1 leads at seed in devtools with a warm path and no conflict; tier 2 leads at seed with no warm path
> or outside devtools; tier 3 follows. Anyone with a portfolio conflict, or not at seed, stays off the plan. I want
> first meetings within 3 weeks, I can take 3 a week, an intro takes about 2 weeks to become a first meeting, and I
> go tier 1 first, then 2, then 3.

## Expected tool call

`equity_raise_pipeline`, once:

```json
{
  "inputs": {
    "round_size": "4000000",
    "lead_cheque": "2500000",
    "commitments": [
      { "amount": "500000", "kind": "firm" },
      { "amount": "250000", "kind": "soft" },
      { "amount": "250000", "kind": "soft" }
    ],
    "pro_rata": ["400000"],
    "stages": [
      { "name": "Intro asked", "investors": 40, "rate_percent": "50" },
      { "name": "First meeting", "investors": 10, "rate_percent": "30" },
      { "name": "Partner meeting", "investors": 2, "rate_percent": "25" }
    ],
    "term_sheets_wanted": 3,
    "runway": {
      "cash_on_hand": "1200000",
      "phases": [
        { "from_month": 1, "gross_burn": "150000", "revenue": "30000" }
      ],
      "months_to_raise": 6
    }
  }
}
```

## What the calculator prints (excerpt)

```text
  Soft commitments, never counted (S)                                        $500,000.00  the soft commitments, shown on their own
  Room after the lead and the firm commitments                             $1,000,000.00  R - L - F; the value when run, not a live formula
  Allocation left                                                            $600,000.00  R - L - F - P; below 0, more is counted than the round holds; the value when run, not a live formula
  Conversion, first stage to a term sheet                                        3.7500%  the product of every rate
  Expected term sheets from today's funnel (E)                                      2.75  the sum of each stage's investors × its rate to a term sheet; an expectation from the founder's rates, not a forecast
  First-stage targets needed, from an empty funnel                                    80  ceiling(W / the conversion)
  More first-stage targets needed beyond today's funnel                                7  ceiling((W - E) / the conversion); 0 when E >= W
  Runway with no raise (the runway plan's)                                  10.00 months  months until cash less the floor goes below zero, on the plan
  Start raising by (the runway plan's)                                       4.00 months  runway with no raise - months to raise, in months from today
  Flag                                                      soft_commitments_not_counted  At least one commitment is soft: soft commitments are shown on their own line and never counted against the round
  Flag                                                            funnel_short_of_wanted  On the founder's rates, today's funnel is expected to give fewer than the 3 term sheets wanted: see the more targets needed line
```

## Expected answer

- Coverage, as printed: the room after the lead and the firm commitment $1,000,000.00, the allocation left
  $600,000.00, the soft $500,000.00 shown apart and never counted; on the founder's own rates today's funnel is
  expected to give 2.75 term sheets, an expectation and not a forecast, against the 3 wanted; 80 first-stage targets
  from an empty funnel and 7 more beyond today's; start raising by month 4.
- The tiers, by the founder's rules, each attribute with its source or `unverified`: Fund B tier 1; Fund C tier 2
  (outside devtools, no warm path); Fund F tier 2, its stage `unverified` (the founder is not sure); Fund E and
  Angel G tier 3; Fund D off the plan (a portfolio conflict, from the founder's check of the portfolio page); Fund H
  off the plan (not at seed). Fund B's warm path is sourced to the founder it backed; Fund E's and Angel G's warm
  paths and every attribute the founder gave with no source are `unverified`.
- The batches, the window opening at month 4 as printed, the latest start on the founder's plan (the founder may name
  an earlier month, labelled as the founder's), weeks numbered from there and no calendar date worked out:
  week 1 holds Fund B, Fund C and Fund F (tier 1, then tier 2, at most 3 a week); week 2 holds Fund E and Angel G;
  each batch's intro asks go out 2 weeks before its week.
- A tracker table with one row per investor on the plan: investor, tier, warm path with its source, batch and week,
  intro asked, first meeting, partner meeting, term sheet or pass, next step, every outcome cell empty until the
  founder reports it, the intro emails handed to the vc-intro-email skill (preview).
- `soft_commitments_not_counted` and `funnel_short_of_wanted` with their meanings from the flag table; it quotes the
  7 more targets needed and the five investors the rules tier, both as stated, and leaves whom to add to the founder.
- The assumptions it leans on, each `unverified` where the result says so: `allocation_rule`, `pro_rata_rule`,
  `stage_counting`, `expected_term_sheets`, `rate_basis` (the founder's own rates) and `start_raising_rule`.
- It looks no investor up, adds none to the list, corrects no attribute, names no firm as a fit and sends nothing; it
  closes as not investment, legal or tax advice.
- It adds, subtracts or divides none of the tool's or the founder's figures in its own text.

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with the plugin loaded from this repository and no user settings. This
is the second attempt, made minutes after the first, which reached an out-of-date build of the calculator's server with
no `equity_raise_pipeline` and is not graded: with no tool, it presented the skill's worked example's figures as "the
calculator's printed output for these exact inputs, taken from its reference example". The answer is trimmed; [...]
marks each cut.

**Partial: one clause met only in part.** It made the one `equity_raise_pipeline` call with the expected arguments and
no other, and quoted every figure as the tool printed it. It tiered the founder's list by the founder's rules, quoting
the rule that placed each investor: Fund B in tier 1, Fund C in tier 2, Fund F in tier 2 provisionally with its stage
`unverified`, Fund E and Angel G in tier 3, and Fund D and Fund H off the plan for the portfolio conflict and the stage.
It kept the tracker, one row per investor with its next step handed to the vc-intro-email skill, named no firm as a fit
and computed nothing in its own text. The batches clause is met only in part: it placed the five investors in tier
order, at most three a week, with their intro asks two weeks before their week, but numbered the weeks "from when you
open the window" rather than from month 4, and proposed a start of its own ("I recommend now, not month 4") that the
founder never named. Read strictly, two more clauses would be met only in part, which would make the run a Fail: the
attributes with no source carry one blanket line saying they are `unverified` rather than the mark in each cell, and two
lines set the founder's figures against each other in words ("The soft angels nearly fill the room"; "far more than 3 a
week for 3 weeks holds"). Its one use of "fit" is about cheque size against the room left. Short of the expected answer:
it gave no Flags section, so neither `soft_commitments_not_counted` nor `funnel_short_of_wanted` is named though both
meanings are given, it did not quote the start-raising rule among the assumptions, and it added one of its own ("no cash
floor"). Since this run the skill never proposes an earlier start month of its own, keeping every week's label from the
printed month until the founder names one, and when neither the tool nor its command line runs it says so and gives no
figure, never one from its worked example. The eval has not been run again.

> **You have $600,000.00 of the $4M left to allocate, and today's funnel is expected to give 2.75 term sheets against the 3 you want.** You need 7 more intro asks to close that gap, and this list adds 5 names that pass your rules. The cash says to start raising by month 4 at the latest.
>
> ## Coverage
>
> | Line                                       | Value           |
> | ------------------------------------------ | --------------- |
> | Round                                      | $4,000,000.00   |
> | Fund A lead cheque                         | $2,500,000.00   |
> | Firm commitments (signed angel)            | $500,000.00     |
> | Room after the lead and firm commitments   | $1,000,000.00   |
> | Seed investor pro rata, counted in full    | $400,000.00     |
> | **Allocation left**                        | **$600,000.00** |
> | Soft commitments (two angels), not counted | $500,000.00     |
>
> [...]
>
> The 2.75 is an expectation from your own rates, not a forecast; the term sheets that arrive can be more or fewer.
>
> ## Tiers
>
> | Investor | Stage                                    | Lead or follow | Cheque            | Sector         | Conflict                                             | Warm path                                          | Tier               | Rule that placed it                                          |
> | -------- | ---------------------------------------- | -------------- | ----------------- | -------------- | ---------------------------------------------------- | -------------------------------------------------- | ------------------ | ------------------------------------------------------------ |
> | Fund B   | seed                                     | leads          | fits lead size    | devtools       | none                                                 | yes, via a founder they backed (from that founder) | **1**              | "leads at seed in devtools with a warm path and no conflict" |
> | Fund C   | seed (their site, checked last week)     | leads          | fits (their site) | infrastructure | none                                                 | none                                               | **2**              | "leads at seed with no warm path or outside devtools"        |
> | Fund F   | seed, `unverified` ("I think… not sure") | leads          | fits              | devtools       | none                                                 | none                                               | **2, provisional** | Same tier 2 rule, if the stage holds                         |
> | Fund E   | seed                                     | follows only   | follow-size       | devtools       | none                                                 | yes, via your advisor                              | **3**              | "tier 3 follows"                                             |
> | Angel G  | seed                                     | follows        | small             | devtools       | none                                                 | yes, via your angel                                | **3**              | "tier 3 follows"                                             |
> | Fund D   | seed                                     | leads          | fits              | devtools       | **backs a direct competitor** (their portfolio page) | not given                                          | **Off plan**       | "Anyone with a portfolio conflict… stays off the plan"       |
> | Fund H   | **Series A only** (their site)           | leads          | not given         | devtools       | not given                                            | not given                                          | **Off plan**       | "…or not at seed, stays off the plan"                        |
>
> Attributes with no source beside them are `unverified`: you stated them but did not say where they come from. I looked no one up.
>
> ## Batches and tracker
>
> All five fit inside your 3-week window at 3 first meetings a week, in your tier order. Weeks are numbered from when you open the window, and intro asks go out 2 weeks before each meeting week.
>
> [...]
>
> **When to open the window:** I recommend now, not month 4. Month 4 is the latest start your cash allows, and you already have a lead yes and 40 intro asks out, which will not hold for four months. The month is your call.
>
> ## Things to resolve before sending
>
> [...]
>
> - **The soft angels nearly fill the room:** their $500,000.00 sits against the $600,000.00 left. If both firm up, there is little space for Fund E or Angel G, so ask whether either has firmed and I will re-run.
>
> [...]
>
> This is not investment, legal or tax advice. I contacted no one, and I am not saying which investor to pick.
