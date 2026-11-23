# Eval 1: Company BE, a moved target, a redefined customer count and a pilot left half-reported

A test prompt for the `vc-prospective-investor-update` skill. The company and the names are made up. The tool call and
the excerpt are from a real `equity_calculator runway_plan` run with these inputs. "Expected answer" states the expected
behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when
it marks the customer count Changed definition without comparing the two figures, keeps the moved MRR target and the
unreported hire as findings, keeps no objection to the MRR definition or to the moved enterprise target (one a lens
raises is dropped by quoting the draft's own Definitions line, or October's update, which already announced the move),
makes the one call below and gives its printed runway under Numbers, and computes nothing in its own text. The verdict
is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or met only in part, and
Fail when two or more are missed; a shortfall against the other points of the expected answer is noted but does not
change the verdict. The recorded run is graded against the pass sentence this eval had then, which asked for two drops
where it now asks that neither objection is kept: the definition objection dropped by quoting the Definitions line, and
the moved enterprise target dropped by quoting October's update. It is a Fail against that sentence: no lens raised
either objection, so neither was dropped, and its fix list compared the two customer counts. Against today's sentence
only that comparison falls short, so it would be a Partial. The skill and this pass sentence were changed after that
run (see "Recorded answer").

## Prompt

> Review my November update to the investors we're warming up for a seed next year. September's update said: "Paying
> customers: 22. MRR: $41,000 (subscription revenue billed in the month). Target: $60,000 MRR by December. Target: 8
> enterprise accounts by December. By the next update: close the two warehouse pilots; hire a head of customer
> success." That was our first update to them. October's said: "Paying customers: 25. MRR: $46,500. We moved the 8
> enterprise accounts target to March: two buyers pushed their budget decisions into the new year. By the next update:
> convert both warehouse pilots to paid; ship the forecasting module." My November draft: "Strong month. Customers
> (paying and pilots): 31. MRR: $49,000. Converted a warehouse pilot to paid. Shipped the forecasting module. On track
> for $60,000 MRR in Q1. On track for 8 enterprise accounts by March. Cash: $1,800,000 at 30 November. Runway: 20
> months. Ask: introductions to operations leaders at third-party logistics firms. Definitions: MRR is subscription
> revenue billed in the month." Notes: "Paying customers: 26. The second warehouse pilot extended to January; they want
> another month of data. We spend $140,000 a month and bring in $49,000. Readers asked last month about our gross
> margin." Goes to: Alex (seed fund), Morgan (angel), Sam (seed fund), Jordan (angel), Alex (seed fund).

## Expected tool call

`equity_runway_plan`, once:

```json
{
  "inputs": {
    "cash_on_hand": "1800000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "140000", "revenue": "49000" }
        ]
      }
    ],
    "stated_runway_months": "20"
  }
}
```

```text
  Runway, plan, no raise                           19.78 months  months until cash less the floor goes below zero
  Runway, no raise: stated                         20.00 months  given
  Runway, no raise: the calculator gives           19.78 months  the plan case's runway
  Runway, no raise: difference                     -0.22 months  computed - stated
  Runway, no raise: rounds to the deck's "20"               yes  the computed figure, rounded half away from zero to the places the deck writes, is the deck's
  Runway, no raise: verdict                          consistent  within the tolerance, or rounding to the deck's, is consistent
```

## Expected answer

- The line: paying customers 22 (September), 25 (October), 26 (November, from the notes); MRR $41,000, $46,500 and
  $49,000, each as stated with its month. No change, growth rate or chart appears.
- "Customers (paying and pilots): 31." against "Paying customers: 25." is Changed definition, fix before sending: the
  revised draft keeps "Paying customers: 26" in the line and, if the founder wants the new count, adds it as a new
  metric with its definition. The two figures are never compared, not even as larger or smaller. MRR keeps its label
  and definition: Same, with November's value beside October's.
- Moved goalposts, Kept, fix before sending: "Target: $60,000 MRR by December." against "On track for $60,000 MRR in
  Q1." The revised draft names the move in the founder's words with `[why the target moved to Q1]`.
- Last time we said: "convert both warehouse pilots to paid" is Partly done, quoting "Converted a warehouse pilot to
  paid." and "The second warehouse pilot extended to January; they want another month of data."; "ship the forecasting
  module" is Done. September's "hire a head of customer success" was not carried into October's list, so it gets no
  status; the Unreported promise lens raises it (no word anywhere): Kept, worth fixing, with
  `[what happened with the head of customer success hire]`.
- A Changed definitions objection that MRR has no definition, if a lens raises it, is Dropped, answered, quoting
  "Definitions: MRR is subscription revenue billed in the month." It is never Kept.
- A Moved goalposts objection on "Target: 8 enterprise accounts by December." against "On track for 8 enterprise
  accounts by March.", if a lens raises it, is Dropped, answered, quoting October's update, the one sent after
  September's: "We moved the 8 enterprise accounts target to March: two buyers pushed their budget decisions into the
  new year." The draft states what that line announced, so the founder is not told to name the move again. Whether or
  not a lens raises either objection, MRR is Same in the tie-out and October's March target is Not yet due. The $60,000
  MRR target, which no later update moved, stays Kept.
- Spin: "Strong month." is Kept, worth fixing, and replaced by a plain summary of the founder's facts.
- The readers' gross margin question is an Unreported promise objection, worth fixing or fix before sending (the tier
  is a judgment), with `[gross margin, its definition and period]` in the open asks; no figure is supplied.
- The tie-out has a row only for each metric and each of October's items, each with one status. The revised draft adds
  no definition or lowlight the founder did not give: a missing definition is a bracketed ask, and the moved $60,000
  target is named under "Last time we said". The four lenses run as subagents, then one refute subagent per objection,
  the refute subagents launched in one message; the answer says how many ran.
- Numbers: 19.78 months, consistent, as the tool prints it; the stated 20 months stands. Goes to: the five names, with
  "Alex (seed fund)" marked as listed twice; no name appears in the update. The close carries the lawyer line on
  mentioning a coming raise.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository, when this eval asked for
the definition objection and the moved enterprise target each dropped by quoting the founder's own line. The answer is
trimmed; [...] marks each cut.

**Fail, against the pass sentence this eval had then: two clauses missed and one met only in part.** It made the one
call above, gave 19.78 months under Numbers as the tool prints it, kept the moved $60,000 MRR target and the head of
customer success hire as findings, and computed nothing. It missed both drops that sentence asked for: no lens raised an
objection to the MRR definition or to the moved enterprise target, so neither was dropped by quoting the Definitions
line or October's update (the tie-out shows MRR Same and the March target Not yet due). It marked the customer count
Changed definition, but its fix list compares the two counts ("a wider count shows a larger number"), so that clause is
met only in part. Today's sentence asks only that neither objection is kept, which the run met, so against today's
sentence it would be a Partial. Short of the expected answer: the refute pass ran as one subagent for all six
objections; the tie-out gives statuses to two September items and two statuses to one metric; the revised draft adds a
runway definition and a lowlight the founder never wrote; the gross margin question was ranked fix before sending. Since
this run the lens brief, the refute brief and the fix list never set figures under different definitions side by side,
Stage B launches one refute subagent per objection in a single message, the tie-out has rows only for the last update's
items with one status each, and a definition or lowlight the founder did not give is a bracketed ask. This eval now
accepts either tier for the gross margin question and asks for the two Dropped entries only when a lens raises them; it
has not been run again.

> **Don't send this draft as written.** Three lines will cost you trust with anyone who kept the September and October updates. The cash and runway lines hold up.
>
> ## Biggest fixes
>
> 1. **Customer count relabelled.** "Customers (paying and pilots): 31" replaces "Paying customers" (22, then 25) without saying so. Your notes say paying customers are 26, and that figure is not in the draft.
> 2. **$60,000 MRR target moved silently.** September said "by December"; the draft says "On track for $60,000 MRR in Q1" and never names the move. October named the enterprise move openly, so the contrast shows.
> 3. **Second warehouse pilot missing.** October promised "convert both warehouse pilots to paid"; the draft says "Converted a warehouse pilot to paid" and leaves out the extension to January.
>
> ## Revised draft
>
> [...]
>
> **The line**
>
> | Metric                                         | September    | October      | November |
> | ---------------------------------------------- | ------------ | ------------ | -------- |
> | Paying customers                               | 22           | 25           | 26       |
> | MRR                                            | $41,000      | $46,500      | $49,000  |
> | Customers (paying and pilots), new this update | not reported | not reported | 31       |
>
> [...]
>
> **Lowlights**
>
> - The second warehouse pilot did not convert this month; it runs to January.
> - $60,000 MRR will not land in December; the target is now Q1.
>
> [...]
>
> **Definitions**
>
> - MRR is subscription revenue billed in the month.
> - Paying customers: [definition, to repeat word for word in every update].
> - Customers (paying and pilots): [definition, or cut this row].
> - Runway: cash divided by monthly spend less monthly revenue, both held flat.
>
> ## Reader pass
>
> The four lenses ran as parallel subagents. The refute pass ran as one subagent deciding the six objections one at a time, which is less independent than one subagent each. All six were kept and none dropped.
>
> | Rank  | Tier               | Section           | Lens                                       | The line                                      | Why an investor reads it that way                                                                                    | Fix                                                                 |
> | ----- | ------------------ | ----------------- | ------------------------------------------ | --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
> | 1     | Fix before sending | The line          | Spin, Changed definitions                  | "Customers (paying and pilots): 31."          | The series they were following is gone and a wider count shows a larger number. It reads as changing the scoreboard. | Restore "Paying customers: 26"; keep 31 only as a new, defined row. |
> | 2     | Fix before sending | Last time we said | Spin, Moved goalposts, Changed definitions | "On track for $60,000 MRR in Q1."             | Same figure, later date, labelled "on track". It reads as a miss being hidden.                                       | Name the move: old date, new date, and the reason.                  |
> | [...] |                    |                   |                                            |                                               |                                                                                                                      |                                                                     |
> | 5     | Worth fixing       | Last time we said | Moved goalposts, Unreported promise        | "hire a head of customer success" (September) | Two updates have passed without a word on it.                                                                        | One line on what happened.                                          |
> | [...] |                    |                   |                                            |                                               |                                                                                                                      |                                                                     |
>
> ## Tie-out
>
> | Metric or item                       | The last update said                                 | This draft says                                | Status                                       |
> | ------------------------------------ | ---------------------------------------------------- | ---------------------------------------------- | -------------------------------------------- |
> | Paying customers                     | "Paying customers: 25."                              | "Customers (paying and pilots): 31."           | Changed definition; paying customers dropped |
> | MRR                                  | "MRR: $46,500."                                      | "MRR: $49,000."                                | Same                                         |
> | [...]                                |                                                      |                                                |                                              |
> | 8 enterprise accounts                | "We moved the 8 enterprise accounts target to March" | "On track for 8 enterprise accounts by March." | Not yet due                                  |
> | [...]                                |                                                      |                                                |                                              |
> | Head of customer success (September) | not mentioned in October                             | not mentioned                                  | No word                                      |
> | [...]                                |                                                      |                                                |                                              |
>
> ## Numbers
>
> - **Runway:** you stated 20.00 months; the calculator gives 19.78 months, a difference of -0.22 months. Its verdict is consistent, so "20 months" may stay. It raised no flags.
>
> [...]
