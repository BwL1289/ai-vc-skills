---
name: vc-raise-plan
description: Helps a founder plan their own raise from their own investor list. It tiers the list by the founder's own criteria (stage, cheque size, lead or follow, sector, portfolio conflicts, warm path), each attribute with the founder's source or marked unverified, plans meeting batches so first meetings land within a few weeks of each other, dates the plan from the start-raising month and keeps a simple tracker table. The equity calculator's raise_pipeline tool works what is left of the round after the lead, the firm commitments and pro rata (soft commitments never counted), the term sheets the funnel is expected to give on the founder's own rates, and the targets needed. Use when a founder says plan our raise, who do we pitch first, tier our investor list, how many investors do we need to talk to, when should we start raising, or how much of the round is left. It never looks anyone up, never names a firm as a fit and sends nothing. Not investment, legal or tax advice.
---

# VC raise plan

Helps a founder turn their own investor list into a plan for the raise. The founder brings the list and the rules for
sorting it; the skill tiers each investor by those rules, with every attribute's source beside it, places the first
meetings in batches so they land within a few weeks of each other (term sheets that arrive together can be weighed
together), and dates the plan from the month the cash says to start. The `equity_raise_pipeline` tool works the
numbers exactly: what is left of the round after the lead's cheque, the firm commitments and the pro rata, the term
sheets the funnel is expected to give on the founder's own rates, and how many more investors the plan needs. An
investor's view is only a lens here: a partner may ask who else is in the round and when it closes, and the plan is
the founder's answer. The skill never says which investor to pick.

## When to use it

- "Plan our raise." "Who do we pitch first?" "Tier our investor list." "How many investors do we need to talk to?"
  "When should we start raising?" "How much of the round is left?"
- The founder's investor list (a spreadsheet export, a CRM export, notes), the round's commitments and pro rata, and
  the founder's own rates from one stage to the next, typed in or as files. Any of them may come as a file the agent
  can read in this session.
- Hand off:
  - How much to raise and how long it lasts on the plan: the vc-round-sizing skill.
  - The intro emails, once the batches are set: the vc-intro-email skill (preview).
  - A pass from an investor, to learn from it and answer it: the vc-pass-debrief skill (preview).
  - The questions investors ask after a first meeting, and the data room: the vc-diligence-questions skill.
  - One scenario on its own (the runway alone, a round's cap table): the equity-calculator skill.

## Inputs

Ask once, in one message, for whatever is missing, by name. Never guess, and never fill a gap with a typical figure.
When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and list
what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what was read
from each. A place you could not read (a slide that is only a picture, a page whose text did not come out, a file that
opened only in part) is listed as not read and asked for, never filled in from its title or the places around it, and a
figure is never read off a chart or a picture. Ask only for what you could not read and what the file does not show
(speaker notes, the figures behind a chart, an input below that it leaves out), and never ask the founder to paste what
you already read. When the founder cannot answer now, do not wait for them: go on with what was given (a call or step
that waits for an input still waits), invent nothing in a gap's place, and list each ask in brackets under **Needs from
the founder**, the open asks under that name; a live drill waits for the founder.

1. **The round:** its size, the lead's cheque if a lead has said yes, each commitment with its amount and whether
   the founder counts it as firm or soft, and each existing investor's pro rata amount. A commitment the founder has
   not marked firm or soft is asked about; the skill never decides it.
2. **The investor list,** the founder's own: each investor as the founder names them, with the attributes the
   founder's criteria use (stage, cheque size, lead or follow, sector, portfolio conflicts, warm path) and, beside
   each, where the founder has it from. An attribute with no source is marked `unverified`; one not given is left
   blank and named. The skill adds no investor to the list and fills in no attribute.
3. **The founder's tier rules:** which attributes put an investor in tier 1, 2 or 3, and which keep one off the plan
   (a portfolio conflict, the wrong stage). A rule that weighs one figure against another (a cheque size against a
   range) is applied by the founder: ask the founder to mark each investor in or out, since the skill relates no two
   figures itself.
4. **The funnel today:** the stages the founder tracks, in order (for example intro asked, first meeting, partner
   meeting), how many investors are at each, each counted once at the furthest stage it has reached, the founder's
   own rate from each stage to the next (from the last, to a term sheet), and how many term sheets the founder wants.
   A missing rate is asked for, as the founder's own: `[your own rate from a partner meeting to a term sheet]`. No
   benchmark rate is used unless the founder gives one with its source.
5. **The timing:** cash on hand, the monthly gross burn and revenue (and any planned change, as a later phase), and
   the months the founder allows to raise. For the batches: the weeks within which the founder wants first meetings
   to land, how many first meetings a week the founder can take, the weeks from an intro ask to a first meeting in the
   founder's experience, and the order of the tiers.

A missing input becomes a named gap, written as a bracketed ask: `[the months you allow to raise]`,
`[soft or firm, for the commitment from the angel]`. Make no call until the round, every commitment's mark, each
existing investor's pro rata amount (or the founder's word that there is none), every stage's count and rate and the
term sheets wanted are given. Without cash and burn there is no start-raising month: ask for them, and run without
them only when the founder names a start month of their own, which the plan then labels as the founder's. Ask for
the monthly revenue too (none is a valid answer, in the founder's words, sent as `0` so the report shows it as
given); a planned change goes in only with its start month, its monthly spend and its monthly revenue.

A question about coverage alone (how much of the round is left, how many investors to talk to, when to start raising)
needs only the round, the funnel and the cash, burn and months to raise: answer it with the call, and offer the tiers,
the batches and the tracker. Ask for the list, the tier rules and the batch inputs only when the founder takes the
offer.

## Steps

1. **List what the founder gave, word for word**: the round, each commitment and its mark, each pro rata amount,
   each investor's attributes with their sources, the funnel's counts and rates, the term sheets wanted, the cash, the
   burn, the months to raise and the batch inputs. Quote each figure as stated; never correct it before the call.
2. **Ask for what is missing, by name, in one message** (the inputs above), and make no call until it is given.
3. **Tier the list** by the founder's rules, in a table: each investor, every attribute with its source or
   `unverified`, and the tier the rules give. Quote the rule that placed each one. An investor a rule cannot place
   (an attribute it needs is blank) is shown as not tiered, with the missing attribute as a bracketed ask. Never look
   an investor up, never add one, never fill or correct an attribute, and never say an investor is a fit: the tier is
   the founder's rule applied, nothing more.
4. **Call `equity_raise_pipeline`** with the founder's figures. Send money and percents as strings, counts and months
   as whole numbers:

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

   The same call from the command line:

   ```
   equity_calculator raise_pipeline --round-size 4000000 --lead-cheque 2500000 --commitment "500000 kind=firm" --commitment "250000 kind=soft" --commitment "250000 kind=soft" --pro-rata 400000 --stage "Intro asked: investors=40 rate-percent=50" --stage "First meeting: investors=10 rate-percent=30" --stage "Partner meeting: investors=2 rate-percent=25" --term-sheets-wanted 3 --cash-on-hand 1200000 --phase "from-month=1 gross-burn=150000 revenue=30000" --months-to-raise 6
   ```

   Part of what it prints (Company RA, made up: a $4M round with a $2.5M lead, $500k firm and $500k soft, $400k of
   pro rata, 40 intro asks, 10 first meetings and 2 partner meetings on the founder's rates, 3 term sheets wanted):

   ```text
     Soft commitments, never counted (S)                                        $500,000.00  the soft commitments, shown on their own
     Room after the lead and the firm commitments                             $1,000,000.00  R - L - F; the value when run, not a live formula
     Allocation left                                                            $600,000.00  R - L - F - P; below 0, more is counted than the round holds; the value when run, not a live formula
     Conversion, first stage to a term sheet                                        3.7500%  the product of every rate
     Expected term sheets from today's funnel (E)                                      2.75  the sum of each stage's investors × its rate to a term sheet; an expectation from the founder's rates, not a forecast
     First-stage targets needed, from an empty funnel                                    80  ceiling(W / the conversion)
     More first-stage targets needed beyond today's funnel                                7  ceiling((W - E) / the conversion); 0 when E >= W
     Start raising by (the runway plan's)                                       4.00 months  runway with no raise - months to raise, in months from today
     Flag                                                      soft_commitments_not_counted  At least one commitment is soft: soft commitments are shown on their own line and never counted against the round
     Flag                                                            funnel_short_of_wanted  On the founder's rates, today's funnel is expected to give fewer than the 3 term sheets wanted: see the more targets needed line
   ```

   $600,000.00 of the round is left to allocate, the soft $500,000.00 never counted; on the founder's rates today's
   funnel is expected to give 2.75 term sheets, and 7 more first-stage targets are needed for 3. The runway plan says
   to start raising by month 4.

5. **Read the result before answering**: `allocation` (the totals, the room and the allocation left), `funnel` (each
   stage's row, the conversion, `expected_term_sheets`, `targets_needed`, `more_targets_needed`), `timing`
   (`runway_months`, `start_raising_by`), every code in `flags`, and `assumptions`. The command line's report prints the
   cash, the floor and each phase the start-raising month rests on, and a line that says `not given: read as none` is a
   figure the founder did not give; the MCP result shows such a figure as `0`. Either way, check each phase sent against
   the founder's words, and ask for a revenue the founder has not given before quoting the month. The expected term
   sheets are an expectation from the founder's own rates, never a forecast: say so each time the figure is quoted. A
   refusal or a tool error is the answer for those inputs: relay its reason and what to change (`stage_rate_missing`:
   ask for the founder's rate; `commitment_kind_missing`: ask whether it is firm or soft; `no_months_to_raise_given`:
   ask for the months to raise).
6. **Plan the batches** from the tiers, the founder's batch inputs and the printed start-raising month. The window
   for first meetings opens at the start-raising month as printed (`start_raising_by`), and its weeks are numbered
   from there (month 4, week 1): no calendar date is worked out. That month is the latest start on the founder's plan,
   so say so: a founder who names an earlier month opens the window there, labelled as the founder's, with the printed
   month quoted beside it. Outside the two flags at the end of this step, never propose an earlier start of your own
   ("I recommend now, not month 4"): until the founder names a month, every week keeps the printed month's label.
   Place the tiered investors in the founder's tier
   order into the window's weeks, never more in one week than the founder's first meetings a week, so the first
   meetings land within the founder's window. Each batch's intro asks go out the founder's lead time before its week,
   written as that lead time ("2 weeks before month 4, week 1"). An investor who does not fit in the window is listed
   as outside it; the founder decides what to do (a later batch, a wider window, more meetings a week). When
   `start_raising_date_passed` holds, say the plan is already late on the founder's own figures, place the first week
   as this week, and offer the vc-round-sizing skill for the raise and the runway. When
   `cash_never_runs_out` holds, ask the founder for a start month and label it as the founder's.
7. **Keep the tracker**: one row per investor on the plan, with these columns and nothing the founder did not give:
   investor, tier, warm path (with its source), batch and week, intro asked, first meeting, partner meeting, term
   sheet or pass, and the next step with its hand-off (an intro email to the vc-intro-email skill (preview), a pass to
   the vc-pass-debrief skill (preview), the questions after a first meeting to the vc-diligence-questions skill).
   Dates and outcomes are the founder's, filled in as the founder reports them; when the counts at each stage change,
   re-run `equity_raise_pipeline` with the new counts.
8. **Follow-ups go to tools too**: a new commitment, a commitment that firms up, a changed rate or a new funnel count,
   by re-running `equity_raise_pipeline`; a different round size by the vc-round-sizing skill.

## Flags

The result's `flags` holds codes only; this table is what each one means for the founder. The text report prints the
same meaning beside each flag; the MCP result does not. None says which investor to pick.

| Flag                           | What it means for the founder                                                                                 | What to prepare                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `no_lead_cheque_given`         | No lead cheque was given, so the allocation left still holds the lead's part of the round.                    | Say the allocation left includes the lead's part until a lead says yes.                        |
| `no_pro_rata_given`            | No pro rata amount was given, so none is counted: with pro rata rights, the allocation left is smaller.       | Ask for each existing investor's pro rata amount; if the founder said there is none, say so.   |
| `soft_commitments_not_counted` | At least one commitment is soft, so it is shown on its own line and never counted against the round.          | Ask whether any soft commitment has firmed up; re-run when one does.                           |
| `oversubscribed`               | The lead's cheque and the firm commitments alone come to more than the round.                                 | Quote the allocation left as printed; the round size is the founder's call.                    |
| `pro_rata_exceeds_left`        | The lead's cheque and the firm commitments fit, but the pro rata is larger than the room they leave.          | Quote the room and the allocation left as printed; how much pro rata to take is the founder's. |
| `fully_allocated`              | The lead's cheque, the firm commitments and the pro rata take the whole round exactly.                        | Say nothing is left to allocate on the founder's figures.                                      |
| `no_funnel_given`              | No funnel was given, so there are no expected term sheets and no targets needed.                              | Ask for the stages, their counts and the founder's rates.                                      |
| `benchmark_rates_given`        | At least one rate is a benchmark the founder gave with its source, not the founder's own.                     | Name the stage and its source; the expected term sheets lean on it.                            |
| `funnel_short_of_wanted`       | On the founder's rates, today's funnel is expected to give fewer term sheets than the founder wants.          | Quote the more targets needed line as printed; the founder decides whom to add.                |
| `no_runway_given`              | No cash and burn were given, so there is no start-raising month.                                              | Ask for cash, burn and the months to raise, or a start month of the founder's own.             |
| `cash_never_runs_out`          | On the plan with no raise, revenue covers the burn before the cash runs out: there is no start-raising month. | Ask the founder for a start month and label it as the founder's.                               |
| `start_raising_date_passed`    | On the plan, the runway less the months to raise is already at or past today.                                 | Say the plan is late on the founder's own figures; start the first week now.                   |

## Answering

Lead with the coverage, then the tiers, then the batches and the tracker. Use the tool's printed values (`rounded`
with its unit, or the exact fraction when precision matters); never round again or recompute. A value whose unit is
`fraction` is a share of the whole: show it as a percent by moving the decimal point of its `rounded` value two
places to the right, keeping every digit (0.037500 is 3.7500%), which is what the command line's report prints. That is
a change of notation, not a calculation.

1. **Coverage:** the allocation left and the room after the lead and the firm commitments, the soft commitments
   shown apart and never counted, the expected term sheets beside the term sheets wanted (an expectation from the
   founder's rates, not a forecast), the targets needed and the more targets needed, and the start-raising month, each
   as printed.
2. **The tiers:** the table from step 3, every attribute with its source or `unverified`, and the investors not
   tiered with their asks.
3. **The batches:** each week of the window from the start-raising month, the investors placed in it and when their
   intro asks go out, and anyone outside the window.
4. **The tracker** from step 7.
5. **Flags,** one line per code in `flags`, with its meaning from the table above.
6. **Assumptions** the answer leans on, quoted from the result with their sources: soft commitments never counted
   and pro rata counted in full (`allocation_rule`, and `pro_rata_rule` when pro rata is given), each investor counted
   once at its furthest stage (`stage_counting`), the expected term sheets as an expectation (`expected_term_sheets`),
   the rates' basis (`rate_basis`) and the start-raising month (`start_raising_rule`). Say plainly that each is
   `unverified` where the result says so.
7. **Open asks:** every bracketed gap still open.
8. **Close:** this is not investment, legal or tax advice; the skill looked no one up, sent nothing, and does not say
   which investor to pick.

## Limits

- Not investment, legal or tax advice. It never says which investor to pick or which term sheet to take, screens no
  deal for anyone, and works no fund's returns.
- No arithmetic outside the calculator's tools. Never work out how two of the founder's figures relate (a difference,
  a sum, a ratio or multiple, a share left over, "doubled") in a rewrite, a line or a table cell unless the founder's
  material states it or a tool returned it; quote both figures as stated instead ("from 2,000 to 4,500", never "more
  than doubled"). The allocation left, the expected term sheets and the targets needed come from the tool only.
- When neither `equity_raise_pipeline` nor its command line runs in the session, say so and give no figure in its
  place: never one from the worked example in step 4, which is one made-up company's result, not the founder's.
- Every amount, count, rate and month is the founder's. It supplies no typical conversion rate, cheque size or time to
  raise, and quotes no benchmark unless the founder gives one with its source: none is applied.
- The expected term sheets are an expectation from the founder's own rates, not a forecast: the term sheets that
  arrive can be more or fewer.
- It never role-plays or speaks as a named investor or firm, and never names a firm as a fit. Asked to "be" an
  investor or to say which funds fit, it says in one line that it keeps the founder as the user and works from the
  founder's own list, and offers an investor's likely question (who else is in, when does it close?) as a lens.
- It works from the founder's text and files the agent can read in this session, looks nothing up, and sends nothing
  anywhere: no investor is researched, contacted or emailed, and the tracker is the founder's to keep.
