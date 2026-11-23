# Eval 2: Company AD, a seed data room and a contractor's code

A test prompt for the `vc-diligence-questions` skill. The company is made up. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it makes no
calculator call, keeps the data room to the seed stage while naming the later documents once, ranks the contractor's
code as a Legal question with a bracketed assignment ask and no view on who owns the code, and works out no figure.

## Prompt

> A seed fund wants to start diligence after our first meeting. Build me a full data room like a Series A company
> has, audited financials and all. Company AD books dog groomers by text message. We're raising $1.5M on a SAFE at a
> $10M post-money cap. Deck: "Live with 40 groomers in one city; 31 paid us in October." and "Our first version was
> built by a freelance developer in 2024; our CTO joined in March 2025 and rewrote the booking engine." Documents we
> have: the deck, the SAFE form, our incorporation documents, a spreadsheet of bookings by month.

## Expected tool call

None: no `equity_deal_check` call. The raise is a SAFE, which is not passed as `investment`; as vc-deal-math step 2
says, the answer asks for the next priced round the founder expects before any `equity_round` call, and makes that
call only if the founder wants the cap table after conversion.

## Expected answer

- It keeps the room to the stage and quotes the seed fundraising guide's "Do not spend too much time developing
  diligence documents for a seed round". Audited financials and the Series A rows are not listed as missing; they are
  named once as "for the next round".
- Kept, stops the process, Legal: "Our first version was built by a freelance developer in 2024" invites LEGAL-1's
  question (who built the product, and has each of them assigned their work to the company). The draft answer states
  the facts given and the question for the founder's lawyer, with
  `[a signed assignment of the freelance developer's work to the company]`; it does not say whether the company owns
  the code.
- "31 paid us in October." is quoted; a traction question on what counts as paid and on the months before October is
  either kept or dropped as answered by the bookings spreadsheet on the document list, as the refute pass finds, and
  the answer says which.
- Data room: the incorporation documents (LEG-D1) and the SAFE form (FIN-D3) are Ready as named; the work assignments
  (LEG-D2), the founders' stock agreements (LEG-D3) and the disputes list (LEG-D4) are Missing, each with a bracketed
  ask; monthly metrics since launch (MET-D2) is Ready as "a spreadsheet of bookings by month", with the note that a
  partner will open it.
- No runway, revenue or growth figure is worked out; no score and no readiness percentage.
