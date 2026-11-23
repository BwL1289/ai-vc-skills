# Eval 2: Company AH, a restated figure, a changed definition and a pilot the draft leaves out

A test prompt for the `vc-current-investor-update` skill. The company is made up. The tool call and the excerpt are from
a real `equity_calculator runway_plan` run with these inputs. The answer states the expected behaviour; it is not a
recorded run, and this eval has not been run in a live session. A run passes when it marks September MRR Restated, the
active-user line Changed definition and the customer count Dropped without converting or adding up anything, judges the
founder's draft as given and so keeps the Missing bad news objection about the pilot, drops the one about churn by
quoting the draft's own lowlight, and quotes the growth rate and the cash change unchecked.

## Prompt

> Review my November update before I send it. Last update (October) said: "MRR: $41,800 (September). Active users
> (logged in during the last 30 days): 2,140. Paying customers: 41. Cash: $2,550,000. Next month: convert the
> grocery-chain pilot to a paid contract." My draft: "Another strong month! MRR: September $40,900, October $43,500
> (+6%). Weekly active users: 1,310. Highlights: launched the Android app; 3 new customers. Lowlights: lost 2 small
> customers to a cheaper tool. Cash: $2,400,000. Net burn: $120,000 a month (spend $160,000, cash collected $40,000).
> Runway: 20 months. Asks: intros to heads of operations at regional grocers." My notes for the month: "Grocery pilot:
> they paused the decision until January."

## Expected tool call

`equity_runway_plan`, once:

```json
{
  "inputs": {
    "cash_on_hand": "2400000",
    "cases": [
      {
        "name": "plan",
        "phases": [
          { "from_month": 1, "gross_burn": "160000", "revenue": "40000" }
        ]
      }
    ],
    "stated_runway_months": "20"
  }
}
```

```text
  Runway, plan, no raise                           20.00 months  months until cash less the floor goes below zero
  Runway, no raise: rounds to the deck's "20"               yes  the computed figure, rounded half away from zero to the places the deck writes, is the deck's
  Runway, no raise: verdict                          consistent  within the tolerance, or rounding to the deck's, is consistent
```

## Expected answer

- Tie-out table: MRR for September is Restated ("MRR: $41,800 (September)." against "September $40,900"), fix before
  sending, with `[why September MRR changed since the October update]` beside the figure. "Active users (logged in
  during the last 30 days): 2,140." against "Weekly active users: 1,310." is Changed definition: the two are not
  compared; the fix gives the 30-day figure for October `[active users, logged in during the last 30 days, October]` and
  announces the weekly metric with its definition. "Paying customers: 41." is Dropped, fix before sending: the draft
  gives "3 new customers" and "lost 2 small customers" but no count, and no count is worked out from them; the fix puts
  the line back with `[paying customers now, counted as in the last update]`. Cash is quoted both times with "not
  checked: no tool computes this" and the bridge ask.
- Missing bad news, Kept, fix before sending: the last update's "Next month: convert the grocery-chain pilot to a paid
  contract." has no line in the founder's draft, while the notes say "Grocery pilot: they paused the decision until
  January." The reader pass judges the founder's draft as given, so the line the revised draft adds as a lowlight does
  not answer the objection; it stays in the ranked fix list.
- Missing bad news on churn is Dropped, answered, quoting "Lowlights: lost 2 small customers to a cheaper tool."
- Spin: "Another strong month!" is Kept as worth fixing, replaced by a summary of the founder's facts.
- "(+6%)" is quoted with "not checked: no tool computes this" and the ask to name its method and which September figure
  it uses. No growth rate, difference or conversion appears.
- Runway: 20.00 months, consistent, as the tool prints it. The answer says the founder's "cash collected $40,000" was
  passed as revenue, as their own net-burn line uses it, and the open asks include `[the date of the $2,400,000 cash
figure]`.
