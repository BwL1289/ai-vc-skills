# Eval 2: Company N, competition at four levels and an objection the appendix answers

A test prompt for the `vc-deck-review` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it checks competition at all
four levels without naming a competitor, drops an objection by quoting the founder's own line that answers it, quotes
the SAFE raise's runway unchecked, and invents nothing.

## Prompt

> Tear apart my pitch deck. Slide 1: "Company N: shift scheduling for independent pharmacies, by text message." Slide
> 2, Problem: "Owners build next week's rota by hand every Sunday night." Slide 4, Traction: "Live at 14 pharmacies;
> 11 pay $90 a month." Slide 5, Competition: "There are no direct competitors built for independent pharmacies."
> Slide 6, Team: "Our CEO is a pharmacist who owned two pharmacies for nine years." Slide 7, Ask: "Raising $1.2M on a
> SAFE. 18 months of runway." Slide 8, Appendix: "Our CTO built the scheduling engine at a hospital-staffing
> startup." The one-pager we send with it says: "Most owners still schedule on paper or in a group chat."

## Expected tool call

None: no `equity_deal_check` call. The raise is on a SAFE, which `deal_check` does not model, and no cap or next
priced round is given; as vc-deal-math step 2 says, the answer asks for both before any `equity_round` call.

## Expected answer

- Competition at four levels: Direct quotes "There are no direct competitors built for independent pharmacies." and
  flags the "No competitors" discount pattern; Indirect and Adjacent and platform are missing, each a bracketed ask
  (`[the software your owners already use that could add scheduling]`); Doing nothing is present in the one-pager's
  "Most owners still schedule on paper or in a group chat.", with the fix to put it on slide 5. No competitor is named.
- The team lens objects that "Our CEO is a pharmacist who owned two pharmacies for nine years." leaves no one who
  builds the product on the team slide. The refute pass lists it under Dropped, answered, quoting the founder's line
  "Our CTO built the scheduling engine at a hospital-staffing startup." with the fix to move it from the appendix to
  slide 6. It is not among the survivors.
- "Raising $1.2M on a SAFE." survives the ask lens, with `[the milestone the $1.2M reaches]`. "18 months of runway."
  is quoted and marked "not checked: no tool computes this for a SAFE or note raise"; no runway is worked out.
- The last-slide rule holds: the ask closes the main deck, and the appendix after it does not count.
- Traction is Present, quoted as stated; no revenue is totalled from "11 pay $90 a month".
- Why now and Market have no line to quote: they are open asks, not objections.
