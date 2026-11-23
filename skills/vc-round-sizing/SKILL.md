---
name: vc-round-sizing
description: Helps a founder size their own raise before going out to VCs, on the founder's own plan. With the equity calculator's runway_plan tool it works how long each amount lasts on a phased burn plan, in a downside case and with no raise at all, which milestone month each amount's cash reaches with time left to raise the next round, the smallest raise that gets there, and raise now or wait side by side. Ownership comes from the deal_check, round and dilution tools. An adversarial review has a skeptic attack the round story (a milestone with no number, one plan only, no downside) and a refute pass keep only what the founder's material grounds. Use when a founder asks how much should we raise, raise now or wait, what milestone does this buy, how long will this last, what if we miss plan, or pastes a burn plan or use-of-funds slide. Every figure comes from the calculator or the founder; it invents no burn, growth or valuation and gives no recommendation. Not investment advice.
---

# VC round sizing

Helps a founder answer the question a partner asks right after "what do you do": how much are you raising, and what
does it get you to? The skill takes the founder's own plan (cash, a few phases of spend and revenue, the milestones,
the amounts on the table), works every case exactly with the equity calculator, and shows each amount side by side:
how long the money lasts on plan and in a downside, which milestones it reaches with time left to raise the next round,
the smallest raise that would, and what each costs in ownership. It never says which to choose.

The founder is always the user. The skill never plays an investor, never speaks as a named investor or firm, and never
adds a figure the founder did not give: no burn, growth rate, haircut, valuation, milestone or time to raise of its own.

## When to use it

- "How much should we raise?" "Is $3M enough?" "$3M or $4M?" "Raise now or wait?" "What milestone does this buy?"
  "How long will this last?" "How long until we raise again?" "What if we miss plan?" "How long do we survive with no
  new money?"
- A pasted burn or hiring plan, a use-of-funds slide, or a line like "we're raising for 18 months" or "we have six
  months without raising".
- Hand off:
  - The ask's arithmetic (valuation labels, the pool shuffle, the SAFE stack, a deck's percent sold): the vc-deal-math
    skill.
  - The story and the say-and-avoid list: the vc-positioning skill. Each claim's evidence, and figures that disagree
    across documents: the vc-claims-check skill.
  - One scenario on its own (a pool, a SAFE's conversion, a stake through later rounds): the equity-calculator skill.
  - Whether the metrics are ready for the next round (ARR, retention, churn, CAC payback, burn multiple): the
    vc-metrics-readiness skill (preview).

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess, and never fill a gap with a typical figure.

1. **Cash and the plan:** cash in the bank today, and the monthly plan as a few phases (from which month, gross
   spend, revenue). Three to five phases is plenty; a detailed model is not needed.
2. **Milestones:** what the round must reach, each as a month from today and a result a next-round investor could
   check (a number, a launch, a count of paying customers), in the founder's words. A revenue milestone in other terms
   than the plan (ARR, a year's revenue) also needs the revenue a month it stands for, in the founder's words; never
   convert it by hand.
3. **Raise options:** each amount to compare; when the money would land (now, or after waiting some months); the
   instrument (priced round, SAFE or note); any valuation or cap quoted or asked for; the founders' stake today. A
   valuation for a later raise is the founder's assumption and is labelled so.
4. **Downside, and a lean plan if any:** what the founder believes could go wrong, as a percent of planned revenue
   and/or spend, or as its own phases; and, if they would cut back on a smaller raise, that lean plan and the amount
   it is for.
5. **Time to raise and reserve:** how many months the founder allows to raise the next round once the milestone is
   hit, and any cash the plan must never spend (the `cash_floor`).

A missing input becomes a named gap, written as a bracketed ask: `[months you allow to raise the next round]`. With no
time to raise given, run anyway and say every milestone was checked at its bare month (the tool's
`no_time_to_raise_given` flag). With no downside given, run the plan alone and ask for one; never pick a percent.

## Steps

Without a subagent tool, run the skeptic (Adversarial review) first, before step 1, as "How to run it" says.

1. **Quote first.** List what the founder states, word for word: the ask, instrument and valuation, cash, burn,
   revenue, any runway claim, the use-of-funds lines, the milestones. Do not tidy or correct them yet.
2. **Ask for what is missing** (Inputs), in one message.
3. **Call `equity_runway_plan` once,** with every option, every case and every milestone; make no second call unless
   the founder asks for another case. Each case is exactly one the founder stated (the plan, their downside, their
   lean plan): never merge two (the downside's revenue percent into the lean plan, say) and never add one. When it is
   unclear whether the founder would also cut spend in the downside, that is an open ask,
   `[would you cut spend in the downside, and to what?]`, not a case. The no-raise row is always worked; do not add it
   as an option. Send money and percents as strings:

   ```json
   {
     "inputs": {
       "cash_on_hand": "500000",
       "cases": [
         {
           "name": "plan",
           "phases": [
             { "from_month": 1, "gross_burn": "120000", "revenue": "10000" },
             { "from_month": 4, "gross_burn": "220000", "revenue": "25000" },
             { "from_month": 13, "gross_burn": "300000", "revenue": "60000" }
           ]
         },
         { "name": "downside", "revenue_percent_of_plan": "50" }
       ],
       "raises": [{ "amount": "3000000" }, { "amount": "4000000" }],
       "milestones": [15],
       "months_to_raise": 6
     }
   }
   ```

   The same plan from the command line, `equity_calculator runway_plan`:

   ```
   equity_calculator runway_plan --cash-on-hand 500000 --phase "from-month=1 gross-burn=120000 revenue=10000" --phase "from-month=4 gross-burn=220000 revenue=25000" --phase "from-month=13 gross-burn=300000 revenue=60000" --downside-revenue-percent 50 --raise "amount=3000000" --raise "amount=4000000" --milestone 15 --months-to-raise 6
   ```

   Part of what it prints (Company W, made up):

   ```text
     Runway, plan, no raise                                                       3.87 months  months until cash less the floor goes below zero
     Start raising by, plan, no raise                                            -2.13 months  runway - months to raise
     Runway, plan, raise 1                                                       17.90 months  months until cash less the floor goes below zero
     Runway, plan, raise 2                                                       22.06 months  months until cash less the floor goes below zero
     Runway, downside, raise 1                                                   16.77 months  months until cash less the floor goes below zero
     Runway, downside, raise 2                                                   20.47 months  months until cash less the floor goes below zero
     Milestone 1 (month 15), plan, raise 1: verdict                                     short  covered when the runway reaches month 21
     Milestone 1 (month 15), plan, raise 2: slack                                 7.06 months  runway - the milestone month
     Milestone 1 (month 15), plan, raise 2: verdict                                   covered  covered when the runway reaches month 21
     Milestone 1 (month 15), downside, raise 1: verdict                                 short  covered when the runway reaches month 21
     Milestone 1 (month 15), downside, raise 2: verdict                                 short  covered when the runway reaches month 21
     Required raise, milestone 1, plan, landing month 0                         $3,745,000.00  smallest raise keeping cash at or above the floor to month 21
     Required raise, milestone 1, downside, landing month 0                     $4,142,500.00  smallest raise keeping cash at or above the floor to month 21
   ```

   $4M's cash lasts to month 15 with six months to raise on plan, but not in the downside; $3M's lasts on neither.

   The other fields, each only when the founder gives it:

   - A waiting option's `lands_month`, in whole months from today (`lands-month=` inside `--raise`). Left out, the
     money lands today, and a waiting option reads as raising now.
   - A reserve in `cash_floor` (`--cash-floor`); never subtract it from the cash by hand.
   - A lean plan as a third case named `lean`, with its own phases or `gross_burn_percent_of_plan` and
     `revenue_percent_of_plan` (`--lean-phase`, `--lean-gross-burn-percent`, `--lean-revenue-percent`). The tool works
     every case for every option, so a lean plan for the smaller raise also prints rows for the larger one: read the
     lean rows only for the option the founder ties the plan to, and say so.

   What a milestone verdict says: only that the cash lasts to the milestone month plus the months to raise (the tool's
   `milestone_rule` row). Slack is the runway less the milestone month, so a milestone is covered only when the slack
   is at least the months to raise; "short" beside a positive slack is no contradiction. Whether the plan reaches the
   milestone's own figure is quoted as stated and not checked by these calls: an ARR target is checked by the
   vc-metrics-readiness skill (`equity_metrics_check` works ARR out from monthly recurring revenue), and the open asks
   ask for the monthly recurring revenue it stands for; a customer count or a launch is quoted with "not checked: no
   tool computes this". A revenue milestone the founder gives as revenue a month is set beside the tool's phase revenue row for
   that month, both as printed; one in other terms is never converted by hand, and its monthly figure goes to the
   open asks.

4. **Ownership per option,** with the tools that already do it:
   - A priced round: `equity_deal_check` with the option's amount, its valuation and the founders' stake today
     (`holder_percent`), and no burn fields, so the runway comes only from `equity_runway_plan` and the answer never
     shows two runway figures.
   - A SAFE or note: `equity_round`, with the next priced round the founder expects. With none, the SAFE's share is
     "not computed: set at the next priced round", as the vc-deal-math skill says; never pass a SAFE as `investment`.
     The tool's `fully_diluted_shares` counts every share before the round, granted options and the unissued pool
     included, and leaves SAFEs and notes out. Some cap tables count SAFEs and notes in their fully diluted total; ask
     which way the founder's does, and pass the tool its own basis. If the founder's total counts them, ask for the
     total without them, `[fully diluted shares before the round, SAFEs and notes left out]`; never subtract the SAFE
     or note shares yourself.
   - Through the next round: `equity_dilution`, with this round and the next as the founder expects it.
   - A code in an ownership tool's `flags` means what this skill's Ownership flags table says (the tool returns codes
     only); a benchmark one is quoted with the tool's own assumption row and its source. Take only the meaning from
     that table: the figure comes from the tool's `dilution_band` or `runway_band` row as printed, never from the
     table's text. Whenever `equity_deal_check` ran, its `dilution_band` row is quoted with its source, flag or not.
5. **Deck claims.** "We have N months without raising" goes in the top-level `stated_runway_months`. A raise's runway
   claim goes in that option's `stated_runway_months`, with `stated_runway_from` set to `landing` when the deck counts
   from the close of a later raise. Use-of-funds lines go in that option's `use_of_funds`. Each comes back consistent,
   a mismatch, or not checked: a runway claim gets no check row when the cash never runs out (`cash_never_runs_out`)
   or runs out before a later raise lands (`cash_out_before_raise_lands`), and the answer lists it as not checked.
   Quote the deck's figure; never correct it by hand.
6. **Raise now or wait** (when asked). The waiting option carries its `lands_month`. Put the options side by side in
   tool values: runway per case, the cash above the floor when the waiting option's money lands, whether cash runs out
   first (`cash_out_before_raise_lands`), each option's ownership. Then list what has to be true for waiting to work, in
   the founder's terms: the valuation they assume, the revenue the plan needs by then, the raise closing in the month
   named. No recommendation.
7. **Run the adversarial review** (below).
8. **Check before answering.** Scan the whole draft, tables, asks and the skeptic's relayed text included, for any
   figure that is in neither a tool result nor the founder's text: a difference, a total, a gap, a remainder or "points"
   counts, and goes. Every case is one the founder named, from one `equity_runway_plan` call. Every code in each
   result's `flags` appears once, with its table meaning. The no-raise row shows `start_raising_by` as printed, a
   negative value included. Every attack quotes a founder line word for word and carries its refute verdict; nothing
   speaks as an investor; no figure, milestone or assumption is the skill's own; the close is item 11's sentence as
   written. Never work out how two of the founder's figures relate (a difference, a sum, a ratio or multiple, a share
   left over, "doubled") in a rewrite, a line or a table cell unless the founder's material states it or a tool returned
   it; quote both figures as stated instead ("from 2,000 to 4,500", never "more than doubled").

Tool values: use each value's `rounded` with its unit; never round again or recompute. A value whose unit is
`fraction` is shown as a percent by moving the decimal point of its `rounded` value two places right, keeping every
digit (0.166667 is 16.6667%), which is what the command line's report prints; a change of notation, not a calculation.
Money keeps its cents: 3745000.00 is $3,745,000.00, never $3.7M or $3,745,000; 0.680000 is 68.0000%, never 68%.
Months to raise and slack are never added or subtracted by hand: the tool gives `target_month`, `slack_months`,
`runway_from_landing` and `start_raising_by`. Never state the gap between an option's amount and a required raise,
or between two options' runways or stakes ("short by $X", "clears it by $Y", "N points more"), or what a founder's
percent leaves over (85% of plan never becomes "the other 15%"): show both values side by side and let the founder
compare.

## Adversarial review

The tool says which amounts reach which months. A partner also asks whether the milestone is worth reaching and the
plan believable. A skeptic attacks the round story; a refute pass keeps an attack only when the founder's material
grounds it.

### The skeptic

Its brief:

- You find the reasons a partner is likely to doubt that this amount buys this milestone. Write in the third person
  ("a partner is likely to doubt this because ..."); you are not an investor and do not speak as one, named or not.
- Read only the founder's material given here and the pattern list. Bring in no outside fact about the company, its
  market or its competitors, and do no arithmetic.
- Return at most three attacks, strongest first. For each: the founder's line, quoted word for word; why a partner is
  likely to doubt it; and the evidence that would answer it, or the pattern it matches.
- A doubt you cannot tie to a line the founder wrote is not an attack: list it apart as a question to the founder.
- Do not judge whether another line of the material answers an attack: raise it anyway, however short the material,
  and the refute pass decides. Return "nothing found" only when no line of the material gives an attack worth a
  partner's time.

**How to run it.** With a subagent tool (in Claude Code, the Agent or Task tool), run the skeptic as a subagent,
however short the material, given only the founder's material, the brief above and the Pattern column below. Without
one, run it before step 1 and write its attacks down in full; never revise them after the tool results are in. Say in
the answer which way it ran.

**Calculator results do not go through the review.** A milestone the tool marks short, a runway or use-of-funds
mismatch, a cash-out before the money lands: each is a computed fact, listed ahead of the kept attacks with no tier,
never refuted: how much a gap hurts depends on its size, which the founder weighs. A runway mismatch whose claim is
below the tool's figure understates it: the founder may keep the claim or state the tool's figure, and it is listed
last among the computed facts, as minor at most.

### Check the quotes

Drop any attack whose quoted line is not in the founder's material word for word (spacing aside) as not grounded.
Questions to the founder go to the open asks.

### The refute pass

Each attack gets its own pass. With a subagent tool, launch a subagent per attack, all in a single message, each given
only the material, that one attack, the Pattern column and this brief; never put two attacks in one subagent. Only
without a subagent tool, take the attacks one at a time in the same agent and decide each before reading the next.
Say in the answer which way the refute pass ran.

- You decide whether one attack is grounded in the founder's material. Write in the third person; you are not an
  investor. Use only the material; bring in no outside fact, and do no arithmetic.
- An attack that asserts a result no tool computed (that a case misses a revenue milestone, say) is Dropped, not
  grounded; its doubt goes to the open asks as a question to the founder.
- The patterns below are of two kinds.
  - **Something said:** "Runway that ends at the milestone month", "Runway quoted on today's burn while the plan
    hires", "A monthly revenue milestone above the plan's revenue a month then", "Detailed multi-year financials
    at seed" and "A large share of the company sold in the round". An attack that matches one of these is Kept,
    grounded even when the material shows evidence: evidence shows the thing is there, not that it escapes the
    pattern.
  - **Something missing:** every other row (no milestone named, no plan for a smaller raise, no number, date or check,
    no evidence named, no downside case, a revenue milestone with no monthly figure). One applies only while the
    material lacks that thing. When another line supplies it, the attack is Dropped, answered, quoting that line.
- Return one verdict, quoting the founder's line word for word where it needs one:
  - **Kept, grounded:** the attack rests on the material: a missing number, date or source, or a pattern that applies.
  - **Dropped, answered:** another line of the material gives what the attack asks for, including the thing a
    pattern of something missing names, and no pattern of something said applies. Quote it, and say whether it should
    move earlier where a partner will see it.
  - **Dropped, not grounded:** the attack rests on an outside fact, or the quoted line does not say what it claims.
- When you cannot decide, return Kept. The pass invents nothing on the founder's behalf.

### Patterns

Signals, not rules. A row marked unverified has no public source its authors read; say so when you use it.

| Pattern                                                                   | Why a partner is likely to doubt it                 | Fix                                                                            | Source                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Raising for N months" with no milestone named                            | Months of runway say how long, not what for         | Name the milestone the money reaches, with its month                           | Unverified: this skill's own judgment. The YC seed fundraising guide calls "raising for N months" a "great answer"; it backs only the fix (the amount "must be tied to a believable plan", sized to the next "fundable" milestone) |
| One amount only, no plan for a smaller raise                              | No answer when the round comes in light             | Show the smaller amount with its own (lean) plan and what it still reaches     | YC seed fundraising guide ("create multiple plans assuming different amounts raised")                                                                                                                                              |
| A milestone with no number, date or check ("product-market fit", "scale") | Nothing the next investor could check               | A result with a number and a month, in the founder's terms                     | Unverified                                                                                                                                                                                                                         |
| Revenue in the plan rising with no evidence named                         | The plan's runway rests on revenue not yet earned   | Name what backs it (signed contracts, pipeline by stage), or show the downside | Unverified                                                                                                                                                                                                                         |
| No downside case                                                          | No answer to what happens if the plan slips         | The founder's own downside, run through the tool                               | Unverified                                                                                                                                                                                                                         |
| A revenue milestone with no monthly figure (ARR beside revenue a month)   | Nothing shows the plan reaches the result it is for | Give the revenue a month the milestone stands for, beside the plan's phase     | Unverified                                                                                                                                                                                                                         |
| A monthly revenue milestone above the plan's revenue a month then         | The plan does not reach the milestone it raises for | Change the plan, the milestone or its month, and run the tool again            | Unverified                                                                                                                                                                                                                         |
| Runway that ends at the milestone month                                   | No time left to raise on the result                 | Allow months to raise after the milestone; show the tool's slack               | Unverified                                                                                                                                                                                                                         |
| Runway quoted on today's burn while the plan hires                        | The deck's months will not survive the hiring plan  | Quote the plan case's runway from the tool                                     | Unverified                                                                                                                                                                                                                         |
| Detailed multi-year financials at seed                                    | Precision the stage cannot support                  | A few phases and the two or three assumptions that drive them                  | YC seed fundraising guide (its list of things not to do: "Create detailed financials"); "multi-year", "at seed" and the reason are this skill's own, unverified                                                                    |
| A large share of the company sold in the round                            | A large stake gone early                            | Be ready to say why; show the smaller option beside it                         | The `dilution_band` row of `equity_deal_check`, quoted as it prints (its source: unverified)                                                                                                                                       |

## Flags

The result's `flags` holds codes only; this is what each means for the founder. A flag is a question to prepare for,
never an error, and never changes a verdict.

| Flag                               | What it means for the founder                                                       | What to change or prepare                                                      |
| ---------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `cash_never_runs_out`              | On that case, revenue covers spend before the cash goes, so there is no runway end. | Say so; a partner will check the revenue that makes it true.                   |
| `cash_out_before_raise_lands`      | Waiting runs the cash below the floor before the money arrives.                     | That option needs bridge money or an earlier close; show it.                   |
| `milestone_short_on_plan`          | An amount does not reach a milestone, with time to raise, even on plan.             | See the tool's required raise, move the milestone, or name a lean plan.        |
| `downside_short_where_plan_covers` | The plan reaches the milestone; the founder's downside does not.                    | Be ready to say what you would cut, and when you would know.                   |
| `covered_without_raise`            | Cash on hand already reaches a milestone on some case.                              | Say what the raise buys beyond it.                                             |
| `start_raising_date_passed`        | On cash alone, raising should already have started, given the months to raise.      | Say when the raise started or will close; quote this meaning, not advice.      |
| `no_time_to_raise_given`           | Milestones were checked at their bare month, with no time to raise after them.      | Give the months you allow, and re-run.                                         |
| `runway_below_band`                | An amount's plan runway ends before the top of the tool's runway band.              | A common benchmark, not a rule: quote the tool's `runway_band` row and source. |

A benchmark flag asks which milestone the amount reaches: say that, and never present it as a shortfall ("short of
the benchmark", "just under it"); the tool's `runway_band` row says what the band means.

## Ownership flags

`equity_deal_check` also returns codes only; this is what each means for the founder. A benchmark flag quotes its band
only from the tool's `dilution_band` or `runway_band` row.

| Flag                                  | What it means for the founder                                                                       | What to change or prepare                                                    |
| ------------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `valuation_back_solved`               | No valuation was given, so the post-money was worked from the raise and the percent.                | Label the valuation pre- or post-money; a partner will ask which it is.      |
| `pool_in_pre_money_lowers_price`      | The new pool is paid for out of the pre-money, so the effective pre-money and price are below it.   | Show the effective pre-money beside the headline.                            |
| `pool_in_post_money_dilutes_investor` | The pool is counted after the money, so the investor gets less than raise / post-money.             | Expect a partner to ask to move the pool into the pre-money.                 |
| `pool_already_large_enough`           | The unissued pool already meets the target, so no new pool shares are needed.                       | Say so; a partner may still ask for a bigger target.                         |
| `conversions_bought_by_pre_money`     | SAFE and note shares come out of the pre-round holders, so their stake falls by more than the sale. | Show ownership with the SAFEs and notes converted.                           |
| `discount_beat_cap`                   | A discount gave a lower price than the cap.                                                         | Model that instrument at its discount price.                                 |
| `note_interest_converts`              | Note interest converts too, so a note gets more than its principal's worth of shares.               | Count the interest in the cap table.                                         |
| `net_burn_not_positive`               | Revenue covers the burn on those figures, so there is no net runway on it.                          | The runway comes from `equity_runway_plan` here; say so.                     |
| `current_burn_runway_longer`          | Runway on today's burn is longer than on the planned burn.                                          | The runway comes from `equity_runway_plan` here; say which burn a deck uses. |
| `runway_below_band`                   | Planned net runway is under the tool's runway band.                                                 | Say which milestone the raise reaches (a common benchmark, not a rule).      |
| `dilution_above_band`                 | The investors get more than the tool's dilution band in one round.                                  | Be ready to say why so much is sold (a common benchmark, not a rule).        |

## Answering

Lead with what each amount buys, then the ownership, then what will be doubted. Use the tool's printed values only.
The eleven items below are required headings, in this order; write "none" under one that has nothing. No headline
verdict of the skill's own opens the answer.

1. **What each amount buys,** one line per option in the tool's words: plan runway, downside runway, each milestone
   covered or short with its slack, and the tool's required raise per milestone, on plan and in the downside, beside
   the amount, with no gap worked between them. No word the tool does not print about an option ("safe", "works",
   "fails", "only works", "needs to"). A lean plan's runway, verdict and required raise go on the line of the option
   the founder ties it to, and nowhere else; one line says the lean rows for the other amounts are left out because
   the founder ties the lean plan to that amount. `milestone_short_on_plan` counts the plan case only, so a smaller
   raise can carry it while its lean rows cover the milestone: quote both. Each milestone's own figure is quoted as
   stated and not checked: an ARR target with the vc-metrics-readiness skill named as where it is checked, a customer
   count or a launch with "not checked: no tool computes this".
2. **Table:** Option, Case, Runway, Milestone (month), Covered?, Slack, Start raising by. The no-raise row first, its
   start raising by as printed (a negative value stays negative, never "already passed").
3. **Ownership per option:** percent sold and the founders' stake after, from `equity_deal_check`; after the next
   round from `equity_dilution`; a SAFE's share from `equity_round`, or "not computed: set at the next priced round".
   The options' values side by side; never their difference.
4. **Raise now or wait,** when asked: the side-by-side, then what has to be true for each, in the founder's terms.
   No recommendation.
5. **Deck claims:** each runway and use-of-funds check, the deck's figure and the tool's, consistent or a mismatch.
6. **Adversarial review:** three parts: the calculator's short milestones, mismatches and cash-outs first, as
   computed facts; then each skeptic attack with its refute verdict (Kept, grounded; Dropped, answered; Dropped, not
   grounded) and the founder's line quoted, the kept ones (at most three) with the doubt and the fix, then
   **Dropped,** one line each with why; then one sentence on how each pass ran ("The skeptic ran as a subagent" or
   "inline, before step 1"; the refute pass as one subagent per attack, or one at a time in this agent), which says
   whether the skeptic ran as a subagent.
7. **Flags,** one line per code in each result's `flags`, with its meaning from the tables above. A benchmark (the
   runway band, the dilution band) is quoted only from the tool's own assumption row, with the source that row gives;
   never as a figure of the skill's own. Whenever `equity_deal_check` ran, its `dilution_band` row is quoted here.
8. **Assumptions** the answer leans on, quoted from the result with their sources: phases are flat inside, the raise
   lands at once, no fees or interest, and a milestone is covered when the cash lasts to its month plus the months to
   raise (`milestone_rule`); the months to raise and every case are the founder's.
9. **Open asks:** every bracketed gap and every question from the skeptic, in one list.
10. **Sources,** and which points rest on an unverified source.
11. **Close:** this is not investment, legal or tax advice, and the skill does not recommend raising now or waiting
    or how much to raise; an accountant should check the plan's cash figures and a lawyer the instrument.

## Sources

- Y Combinator, "A guide to seed fundraising": https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising.
  Read in full by this repository's authors. Quoted here: the amount "must be tied to a believable plan"; "create
  multiple plans assuming different amounts raised"; and its list of things not to do ("Create detailed
  financials"). Its "How Much to Raise?" section also calls "raising for N months" a "great answer", so this skill
  never cites it for doubting that answer. No date was seen on the guide, which is older (it names Imagine K12, and
  one of its footnotes links to a 2016 address of the original). Its figure for how long a raise
  lasts reaches the answer only through the calculator's `runway_band` and `milestone_rule` assumption rows, quoted
  as the tool prints them, never as the skill's own number. Its figures for how much of the company to sell are not
  quoted: the `dilution_band` row of `equity_deal_check` gives its own source. Its rule of thumb for spend per
  engineer is never used to fill in a founder's burn.

Not read, so unverified and never quoted: any data on time between rounds or months to raise, and stage-by-stage
round sizes. The pattern rows marked unverified, the skeptic and refute method, and the plan-and-downside layout are
this skill's own judgment, unverified.

## Limits

- Not investment, legal or tax advice. The skill does not recommend raising now or waiting, how much to raise, or
  from whom; it shows what each option buys on the founder's own plan.
- It never invents a burn, revenue path, growth rate, downside haircut, valuation, time to raise or milestone. Each
  is the founder's; a gap stays a bracketed ask.
- It never role-plays or speaks as a named investor, firm or author. Asked to "be" one, it offers the YC seed
  fundraising guide's framework, as a framework, and the skeptic's review, and keeps the founder as the user.
- No arithmetic outside the equity calculator's tools: no months added, runways subtracted or amounts divided by hand,
  and no gap to a required raise or difference between two options stated, in prose, a table or an ask.
- It never builds a case the founder did not state, by merging two of theirs or by a second call.
- The plan is a model: spend and revenue are flat inside each phase, the raise lands at once, and fees, interest and
  late payments are left out. Say so beside the results.
- The review predicts what a partner is likely to doubt; a real partner may doubt other things.
- It works from the founder's text and sends nothing anywhere.
