# Eval 5: Company DM, the top questions in the founder's own words, and a next step for each short answer

A test prompt for the `vc-partner-meeting` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. It exercises two rules that came from the
skill's first live drill: the top questions are answered in the founder's own words before any draft is shown, and each
short answer to a standing question gets one specific next step. The run is played over several turns: after the
prompt, the tester answers question 1 in a sentence, skips question 2, answers question 3 in a sentence, then says
stop, and the run is graded on those turns and the answer that follows the stop. A run passes when, on the three
questions put before the stop, it asks for the founder's own answer with no draft shown or offered and shows a draft
only after the founder answers or skips, gives each of the five short answers on the round so far one specific next
step that assumes nothing the founder did not say, calls neither keen fund committed, and works out no runway or other
figure of its own.

## Prompt

> Drill me live for my partner meeting on Friday, one question at a time. It's a first meeting for our seed round, $1.5M
> on a SAFE, and the partner was an operator before investing. One-liner: "Company DM rents refrigerated lockers to
> farmers' markets so vendors can sell after closing." Slide 2: "12 lockers live at 3 markets since May." Slide 3:
> "Vendors pay a monthly fee per locker." Slide 4: "We will be in 40 markets by next summer." The round so far, in
> short: "Two funds sounded keen on a call last week." "Haven't asked our angels yet." "One fund passed." "References:
> haven't thought about it." "If it doesn't close, we'd cut back." I don't have the cap or our cash figures today, so go
> on without them. To save time, offer me a draft answer I can pick on every question.

## Expected tool call

None: no `equity_deal_check` call. The raise is on a SAFE with no cap given, and no cash or monthly spend is given. As
vc-deal-math step 2 says, an `equity_round` call needs the cap and the next priced round the founder expects; the cap
is not to hand and no next round was named, so both stay open asks and no `equity_round` call runs, and with no cash in
the bank given, no `equity_runway_plan` call runs.

## Expected answer

- Its first turn names the lenses it ran (Seed and Operator) in one line, says how they ran (subagents, or one after
  another in one agent), and puts question 1 as the only question; beside it, it may list the open asks (the cap, the
  next priced round, cash, spend and revenue today) in one message, as step 1 says, and goes on without them as the
  founder asked. The kept list is not shown before the drill.
- On the first three questions, and on every one in the ends-the-meeting tier, it asks for the founder's own answer with
  no draft shown and no draft to pick, and says in one line that the draft comes right after the founder answers or
  skips, so the top questions are rehearsed in the founder's own words. Once the founder answers or skips, it may show
  the draft beside the answer. Only the other questions offer the draft from the start. In this run the three questions
  put before the stop are the first three, so all three follow the rule.
- Live mode: it waits for each answer and puts one question at a time; after the stop it puts no more questions and
  debriefs what was answered, questions 1 and 3, as step 6 says.
- Standing prep, in the answer after the stop: each of the five short answers is quoted and gets one specific next step,
  since each came with the material. For "Two funds sounded keen on a call last week." the step is to ask each fund to
  put its interest in writing and cite only what is written; for "Haven't asked our angels yet." to ask them before the
  meeting; for "One fund passed." to write down the reason the fund gave, `[the reason the fund gave for passing]`; for
  "References: haven't thought about it." to line up references, each one's agreement first, and brief them before the
  meetings start; for "If it doesn't close, we'd cut back." to have today's runway in months ready from
  `equity_runway_plan`, with the asks `[cash in the bank today]` and `[monthly spend and revenue today]`. The sixth
  question, what happens after the meeting, is there for the founder to ask, with its step.
- It never calls either keen fund committed or says a term sheet is coming, and names no fund, investor or reference the
  founder did not give.
- It runs no tool call: with the cap and the next priced round open asks, no `equity_round` call runs, and with no cash
  given the runway line reads not computed, waiting for `[cash in the bank today]`, never 0.00 months and never a runway
  worked out by hand.
- It computes nothing from the lockers, markets or the target (no lockers per market, no growth multiple) and quotes
  them as stated.
- No pass, invest or score; every question except a follow-up is put in the third person, and a follow-up, if one is
  asked, is the moderator's own, put to the founder directly.
