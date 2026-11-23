# Keeping metrics consistent from one update to the next

Two skills read this file: the vc-current-investor-update skill, which keeps it, and the vc-prospective-investor-update
skill, which reads it in place from `../vc-current-investor-update/references/`. Neither skill keeps a copy. Both
skills' tests check the status words below, so a change here is a change to both.

## Metrics and their definitions

- **Same metrics, same definitions, every time.** A metric the last update reported stays in, whichever way it moved.
  A new metric may be added; a dropped one is said to be dropped, with the reason.
- **A changed definition is announced,** in the metrics and in the Definitions block: the old label and definition,
  the new ones, and, for the period both cover, both values as the founder gives them. Never convert one into the
  other.
- **Name each metric for what it is.** Bookings and letters of intent are not revenue; one-time fees are not recurring
  revenue; GMV is not revenue; "active" needs a definition; churn and burn say gross or net.
- **Per-period figures, with absolutes.** Not cumulative totals in place of a period's figure, and never a percent
  change without the two figures it compares.
- **Growth rates are quoted, never computed.** A growth rate the founder states is quoted with its method (month over
  month, a simple average, compounded) and its period; with no method given, ask for it. Never work one out.

## Metric statuses

Every metric and every figure is set beside the last update's, as stated. Each gets one status. No arithmetic: two
figures are compared as written, and whether one is larger may be said, never by how much.

| Status             | When                                                                                                                                         |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Same               | The same metric, label, definition and form; every period both updates give has the same value                                               |
| Restated           | The same metric, in the same form, for a period both updates give, with a different value                                                    |
| Different form     | The two lines state the metric in different forms (MRR and ARR, a month and a quarter), between the two updates or in two lines of the draft |
| Changed definition | The label or definition differs from the last update's                                                                                       |
| Dropped            | The last update reported it; this draft does not                                                                                             |
| New                | This draft reports it; the last update did not                                                                                               |

A first update has nothing to tie out: every metric is New, and its Definitions block is the one the next update ties
out to.

## The Definitions block

Every metric's definition, word for word the same in every update; a change says so, with both versions.

## Not checked here

Figures no tool here computes stay quoted as stated with "not checked: no tool computes this": growth rates, churn,
retention, recurring revenue built from a month (ARR), unit economics, and the change in cash between the two updates.
For the cash, add the bracketed ask
`[a one-line bridge from the last update's cash to this one's: net burn plus anything else that moved cash]`, since a
reader holding both updates can make that comparison.
