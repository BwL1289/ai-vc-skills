# Eval 1: Company CQ, three passes, three reasons and a come-back bar

A test prompt for the `vc-pass-debrief` skill. The company, the funds and the people are made up. "Expected answer"
states the expected behaviour, and "Recorded answer" is an excerpt of a recorded run (Claude Code 2.1.331 on
2026-11-24). A run passes when it quotes each pass word for word, groups the passes by the reason given, labels every
reading unverified, maps each reason to its skill, lists the come-back bar beside the founder's figure without working
out the gap, and drafts three replies that each ask for at most one referral and send nothing. The verdict is Pass when
every clause of that sentence is met, Partial when exactly one clause is missed or met only in part, and Fail when two
or more are missed; a shortfall against the other points of the expected answer is noted but does not change the
verdict. The recorded run is a Pass with one shortfall against the expected answer. The skill was changed after that run
(see "Recorded answer").

## Prompt

> Three funds passed on our seed this month. What do they mean, what should we change, and can you draft replies? We
> want to ask each for one referral. P1, from Morgan at Fund B, 3 November: "Thanks for the time. We'd want to see more
> revenue traction before we lean in." P2, from Alex at Fund Q, 10 November: "Really enjoyed it. We're not sure the
> market is big enough for a venture outcome." P3, from Robin at Fund T, 17 November: "Too early for us. Come back when
> you're at $1M ARR." "Our ARR is $400k as of October." Company CQ sells inventory software to craft breweries.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- Each pass is quoted word for word as P1 to P3, with who sent it and its date, as the investor's own words.
- The groups: "We'd want to see more revenue traction before we lean in." under Traction; "We're not sure the market is
  big enough for a venture outcome." under Market; "Too early for us." under Stage or timing, read both ways (a fund
  that invests later, or traction below this fund's bar). Each group lists its pass by number.
- Every reading is labelled unverified. None says what Morgan, Alex or Robin meant or thinks.
- What to fix: Traction to the vc-metrics-readiness skill, Market to the vc-market-sizing skill, Stage or timing to the
  come-back list. No market size is worked out and no fund math appears.
- Come back when: "Come back when you're at $1M ARR." beside "Our ARR is $400k as of October." both as stated, with a
  check-again date left for the founder. No gap, share of the way there or month to reach it is worked out.
- Three replies, one per pass, each thanking the investor without arguing with the reason, keeping the door open (the
  reply to P3 says the founder will write when the bar is met, if the founder agrees), and asking for at most one
  referral. No other fund is named or hinted at, and nothing is sent.
- No fund or person is suggested to try next.

## Recorded answer

Recorded with Claude Code 2.1.331 on 2026-11-24, with the plugin loaded from this repository and no user settings. The
answer is trimmed; [...] marks each cut.

**Pass: it met every clause.** It quoted each pass word for word with who sent it and when, under a heading that calls
the words the investor's; grouped the passes as Traction (P1), Market (P2) and Stage or timing (P3), reading P3 both
ways; labelled every reading unverified and said none is what the investor meant; mapped traction to the
vc-metrics-readiness skill, the market to the vc-market-sizing skill and the stage to the come-back list; set Robin's
"$1M ARR" bar beside "$400k as of October" with no gap worked out and the check-again date left to the founder; and
drafted three replies, each with one referral ask, sending nothing. Its only tool call loaded the skill. Short of the
expected answer: the reply to P2, whose pass names no come-back condition, thanks Alex and asks for one referral but has
no line that keeps the door open, while the reply to P1 offers occasional updates the founder never said they want to
send (the answer lists that as an open ask). It also set "$400k as of October" beside Morgan's "more revenue traction",
which names no measure, with the measure left as a bracketed ask. Since this run the skill closes a reply that has no
come-back condition to quote and no update the founder wants to offer with one line that keeps the door open and
promises nothing, and offers no update the founder did not ask to send. The eval has not been run again.

> # Pass debrief: Company CQ, three passes in November
>
> ## The pattern
>
> Each pass gives a different reason, so no reason group is named by more than one pass:
>
> - **Traction:** P1
> - **Market:** P2
> - **Stage or timing:** P3
>
> [...]
>
> ## The passes
>
> | #   | Who            | Date        | How far it got | The words (the investor's, as you pasted them)                                      | Group           |
> | --- | -------------- | ----------- | -------------- | ----------------------------------------------------------------------------------- | --------------- |
> | P1  | Morgan, Fund B | 3 November  | `[not given]`  | "Thanks for the time. We'd want to see more revenue traction before we lean in."    | Traction        |
> | P2  | Alex, Fund Q   | 10 November | `[not given]`  | "Really enjoyed it. We're not sure the market is big enough for a venture outcome." | Market          |
> | P3  | Robin, Fund T  | 17 November | `[not given]`  | "Too early for us. Come back when you're at $1M ARR."                               | Stage or timing |
>
> ## What they may mean
>
> The text does not show what any of these investors really meant; only they could say. These are common readings, all unverified.
>
> [...]
>
> ## Come back when
>
> | Pass | Who            | The condition (quoted)                    | What it measures          | Your figure now                          | Check again                                           |
> | ---- | -------------- | ----------------------------------------- | ------------------------- | ---------------------------------------- | ----------------------------------------------------- |
> | P3   | Robin, Fund T  | "Come back when you're at $1M ARR."       | ARR                       | "$400k as of October" `[ARR definition]` | `[when you want to check]`                            |
> | P1   | Morgan, Fund B | "more revenue traction before we lean in" | Revenue; no measure given | "$400k as of October"                    | `[what would count: your own measure, or ask Morgan]` |
>
> [...]
>
> **P2, to Alex at Fund Q**
>
> > Hi Alex,
> >
> > Thank you for the time, and for telling us plainly what gave you pause. Understood on the market size question. One ask, and feel free to say no: is there one person, a founder or an investor, you think we should be talking to? Either way, I appreciate the candour.
> >
> > Best,
> > [Your name]
>
> **P3, to Robin at Fund T**
>
> > Hi Robin,
> >
> > Thanks for the time, and for giving us a clear bar. Understood that it's too early for you; I'll write when we're at $1M ARR. One ask in the meantime, and no problem if not: is there one person, a founder or an investor, you think we should talk to?
> >
> > Best,
> > [Your name]
>
> [...]
>
> This is not investment, legal or tax advice. I've sent nothing; the replies are yours to edit and send.
