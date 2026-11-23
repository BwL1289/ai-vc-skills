# Eval 2: Company T, a NO that answers the objection

A test prompt for the `vc-taste-check` skill. The company is made up. "Expected answer" states the expected behaviour,
and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.330 on 2026-11-23). A run passes when it puts the
founder's reason for the cut beside D1, drops any objection the founder's material answers by quoting the line that
answers it, places each decision by the skill's rules (a minor survivor moves nothing; a kept objection that ends the
meeting or weakens it holds a decision at Not yet and is named there), and invents nothing on the founder's behalf. The
verdict is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or met only in
part, and Fail when two or more are missed. The recorded run is graded against the pass sentence this eval had then,
which asked for an objection dropped by quoting the founder's reason for the cut, a clear decision placed in the deck
with its slide and the removed feature in the meeting, and nothing invented. It is a Fail against that sentence: nothing
was dropped, and D1 was not placed in the meeting nor D2 in the deck. Against today's sentence it misses only the
placement clause, so it would be a Partial. The skill and this pass sentence were changed after that run (see "Recorded
answer").

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

- If a lens objects to "We removed the reporting dashboard in June, three months after launch." because the line gives
  no reason, the objection is listed under Dropped, answered, quoting the founder's line "Coordinators told us they
  export to spreadsheets for reports anyway, and the dashboard took a third of our build time." Raised or not, that
  reason sits next to D1, in its why-we-built-it line or the decisions table.
- D1 is placed In the meeting, as the story of a feature removed after launch, unless an objection that ends the
  meeting or weakens it survives on D1. A minor survivor, such as one about the evidence line, leaves D1 in the
  meeting with its bracketed ask beside the line.
- D2 is Clear on all three checks with no flag: its Trust mark rests on the founder's honest label of a judgment before
  data and how they will know. Its why-we-built-it line uses only the founder's reason; it may be marked the repeatable
  line. It is placed in the deck on the product or solution slide when no objection above minor survives on it.
  Otherwise it is Not yet, naming every kept objection on it: the prompt says nothing of what turning down the chat
  assistant cost, and the core workflow's "under five minutes" sits beside D2's "one tap", so a lens may keep either.
  A customer-trust objection that nothing shows the call was right, if a lens raises one, is listed under Dropped,
  answered, quoting "A judgment before data; we will know it was right if coordinators keep filling shifts without
  calling the office."
- An objection that only says an input is missing (what changed, the closest alternatives, the material) goes to the
  open asks as a gap and is never kept against D2.
- An objection that a decision copies another product or follows what the market does, if a lens raises one, is
  listed under Dropped, not grounded: the prompt names no other product and gives no one else doing it as a reason.
  The answer adds no product or market fact of its own.
- "11 of 12 pilot agencies kept using the app after we removed the dashboard in June." is quoted as stated, never
  turned into a percent, and named as a claim a partner may check (the vc-claims-check skill). The answer never says
  what the agency that did not keep using the app did; an ask about it uses the founder's own terms.
- D3 names no NO, so the open asks ask what brand tactic or tone the founder turned down; no NO is invented for it.
  D3 is placed Not yet, with naming what it turned down as the fix that would move it.
- No decision is added, no score is given, and the word taste does not appear in the why-we-built-it lines.

## Recorded answer

Recorded with Claude Code 2.1.330 on 2026-11-23, with the plugin loaded from this repository and no user settings, when
this eval expected an objection dropped by quoting D1's reason, D1 in the meeting and D2 in the deck. The answer is
trimmed; [...] marks each cut.

**Fail, against the pass sentence this eval had then: two clauses missed.** It ran the five lenses and five refute
passes as subagents, put the founder's reason beside D1 in its why-we-built-it line, said that D2's own label answers a
"no data" objection, invented no decision, figure or product, quoted "11 of 12" as stated, and asked what voice D3
turned down. It missed the drop: no lens objected to D1's missing reason, since the reason was in the material every
lens read, so no objection was dropped by quoting it. It missed the placements: one minor objection held D1 at Not yet,
and D2 was Not yet too. The run's reviewer graded it Partial and traced the misses to this eval and to two loose rules
in the skill rather than to the model. Against today's sentence, which puts the reason beside D1, asks for a drop only
of an objection the material answers and places each decision by the skill's rules, it misses one clause, so it would be
a Partial: the minor objection moved D1, and D2's Not yet named two of the three objections kept on it, the third only
saying that the founder had not said what changed. Since this run a minor survivor no longer moves a decision, an
objection that only says an input is missing goes to the open asks, the lenses get no list of what was not provided, a
figure line is never turned into what it leaves over, and every Not yet names each kept objection on it; this eval's
drop and placement points are now conditional. The eval has not been run again.

> **Short answer:** as written, none of the three is ready to show yet. D2 (the chat assistant no) is one fact away from the deck, D1 (the dashboard cut) is two facts away from being your meeting story, and D3 (brand voice) should be left out until it names something you turned down.
>
> Five independent review lenses attacked your lines, and a separate pass tested each objection against your own words. All five objections survived and none was dropped.
>
> [...]
>
> | Rank  | Tier       | Lens                             | Your line                                                                            | Why a partner is likely to read it that way                                                                     | Evidence to add                                                                                                   |
> | ----- | ---------- | -------------------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
> | [...] |            |                                  |                                                                                      |                                                                                                                 |                                                                                                                   |
> | 4     | Weakens it | Timing and angle                 | Same D2 line                                                                         | Nothing in the list says what changed to make this the moment. This is a missing input more than a fault in D2. | `[what changed for agencies or coordinators that makes this possible or needed now]`                              |
> | 5     | Minor      | Scope discipline, Customer trust | "11 of 12 pilot agencies kept using the app after we removed the dashboard in June." | It shows agencies tolerated the cut, not that the cut paid off. The twelfth agency is unexplained.              | `[why the twelfth agency stopped, and whether it was the dashboard]`, `[what the reclaimed build time went into]` |
>
> [...]
>
> | #   | Decision                                                                 | Said no to              | Clarity | Usefulness | Trust | Flags | Placement                                            |
> | --- | ------------------------------------------------------------------------ | ----------------------- | ------- | ---------- | ----- | ----- | ---------------------------------------------------- |
> | D1  | "We removed the reporting dashboard in June, three months after launch." | The reporting dashboard | Clear   | Clear      | Clear | None  | Not yet; in the meeting once objection 5 is answered |
>
> [...]
