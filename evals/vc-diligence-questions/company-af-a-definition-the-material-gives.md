# Eval 4: Company AF, a definition the material already gives

A test prompt for the `vc-diligence-questions` skill. The company is made up. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it drops the
active-customer question as answered by the founder's own definition line and moves it to the have-it-ready list,
keeps the recurring-revenue and retention questions with bracketed asks, marks the metrics rows of the data room by
the document list, and converts or computes no metric.

## Prompt

> Prep me for Series A diligence; one message. Company AF makes warranty-claims software for appliance retailers.
> Deck: "ARR: $1.2M (October bookings x 12)." and "Active customer: a retailer that filed at least one claim in the
> month." and "Monthly active customers: 210 in October." One-pager: "Net revenue retention 118% over the last 12
> months." Documents we have: monthly metrics since launch, invoices, the cap table.

## Expected tool call

None: no `equity_deal_check` call. The prompt gives no figures of the ask.

## Expected answer

- The Traction and metrics lens asks how an active customer is counted, on "Monthly active customers: 210 in
  October." Dropped, answered: "Active customer: a retailer that filed at least one claim in the month." gives the
  definition, so the question goes to the have-it-ready list with that line as the answer to point to.
- Kept, stops the process or slows it, Traction and metrics: "ARR: $1.2M (October bookings x 12)." A month's bookings
  times twelve is not recurring revenue, as the metrics guide in the skill's Sources says. The draft answer names the
  metric for what it is and brackets `[recurring revenue for October, one-time fees excluded]`; it computes nothing.
- Kept, slows it: "Net revenue retention 118% over the last 12 months." has no definition or cohort table behind it,
  `[net revenue retention, last 12 months, as you define it, with the cohort table]`.
- Data room: retention by monthly cohort (MET-D4) and the metric definitions sheet (MET-D1) are Missing; monthly
  metrics since launch (MET-D2) and invoices and contracts (MET-D5) are Ready as named.
- No conversion between ARR and MRR, no growth figure, no score and no readiness percentage. The ARR and retention
  lines are quoted as stated, with the vc-metrics-readiness skill named as the one that checks them against their
  parts.
