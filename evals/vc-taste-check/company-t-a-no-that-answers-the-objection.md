# Eval 1: Company T, a NO that answers the objection

A test prompt for the `vc-taste-check` skill. The company is made up. This eval states the expected behaviour; it is not
a recorded run, and it has not been run in a live session. A run passes when the refute pass drops an objection by
quoting the founder's own line that gives the reason for a cut, places a clear decision in the deck with its slide and a
removed feature in the meeting, and invents nothing on the founder's behalf.

## Prompt

> Which decisions should I show investors? Company T makes shift scheduling for home-care agencies. Core workflow: "A
> coordinator fills a missed shift from a phone in under five minutes." D1: "We removed the reporting dashboard in
> June, three months after launch." Why D1: "Coordinators told us they export to spreadsheets for reports anyway, and
> the dashboard took a third of our build time." Evidence for D1: "11 of 12 pilot agencies kept using the app after we
> removed the dashboard in June." D2: "We said no to a chat assistant inside the app, because coordinators fill shifts
> while driving and need one tap, not a conversation." Evidence for D2: "A judgment before data; we will know it was
> right if coordinators keep filling shifts without calling the office." D3: "Our brand voice is plain and calm,
> written for coordinators at 6 a.m."

## Expected tool call

None: no `equity_deal_check` call. The prompt states no deal terms, and the skill calls no calculator tool.

## Expected answer

- A scope-discipline objection to "We removed the reporting dashboard in June, three months after launch." (the line
  gives no reason) is listed under Dropped, answered, quoting the founder's line "Coordinators told us they export to
  spreadsheets for reports anyway, and the dashboard took a third of our build time." The pass says that line should
  sit next to D1.
- D1 is placed In the meeting, as the story of a feature removed after launch.
- D2 is Clear on all three checks with no flag: its Trust mark rests on the founder's honest label of a judgment before
  data and how they will know. Its why-we-built-it line uses only the founder's reason and is placed in the deck on the
  product or solution slide; it may be marked the repeatable line.
- "11 of 12 pilot agencies kept using the app after we removed the dashboard in June." is quoted as stated, never
  turned into a percent, and named as a claim a partner may check (the vc-claims-check skill).
- D3 names no NO, so the open asks ask what brand tactic or tone the founder turned down; no NO is invented for it.
- No decision is added, no score is given, and the word taste does not appear in the why-we-built-it lines.
