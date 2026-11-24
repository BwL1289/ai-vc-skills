# Eval 1: Company CQ, three passes, three reasons and a come-back bar

A test prompt for the `vc-pass-debrief` skill. The company, the funds and the people are made up. The answer states
the expected behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when
it quotes each pass word for word, groups the passes by the reason given, labels every reading unverified, maps each
reason to its skill, lists the come-back bar beside the founder's figure without working out the gap, and drafts three
replies that each ask for at most one referral and send nothing.

## Prompt

> Three funds passed on our seed this month. What do they mean, what should we change, and can you draft replies? We
> want to ask each for one referral. P1, from Morgan at Birchline Capital, 3 November: "Thanks for the time. We'd want
> to see more revenue traction before we lean in." P2, from Alex at Quayside Partners, 10 November: "Really enjoyed
> it. We're not sure the market is big enough for a venture outcome." P3, from Robin at Tallow Ventures, 17 November:
> "Too early for us. Come back when you're at $1M ARR." "Our ARR is $400k as of October." Company CQ sells inventory
> software to craft breweries.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- Each pass is quoted word for word as P1 to P3, with who sent it and its date, as the investor's own words.
- The groups: "We'd want to see more revenue traction before we lean in." under Traction; "We're not sure the market
  is big enough for a venture outcome." under Market; "Too early for us." under Stage or timing, read both ways (a fund
  that invests later, or traction below this fund's bar). Each group lists its pass by number.
- Every reading is labelled unverified. None says what Morgan, Alex or Robin meant or thinks.
- What to fix: Traction to the vc-metrics-readiness skill, Market to the vc-market-sizing skill, Stage or timing to
  the come-back list. No market size is worked out and no fund math appears.
- Come back when: "Come back when you're at $1M ARR." beside "Our ARR is $400k as of October." both as stated, with a
  check-again date left for the founder. No gap, share of the way there or month to reach it is worked out.
- Three replies, one per pass, each thanking the investor without arguing with the reason, keeping the door open
  (the reply to P3 says the founder will write when the bar is met, if the founder agrees), and asking for at most one
  referral. No other fund is named or hinted at, and nothing is sent.
- No fund or person is suggested to try next.
