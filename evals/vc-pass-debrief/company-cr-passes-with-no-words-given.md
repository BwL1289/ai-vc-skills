# Eval 2: Company CR, two passes with none of their words given

A test prompt for the `vc-pass-debrief` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it gives no reading, guesses no
reason, drafts no reply, and asks for each pass's words and the other inputs in one message.

## Prompt

> Two VCs passed after our partner meetings. What did they really mean, and can you write the replies? Company CR
> makes payroll software for restaurants.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- It says once that what an investor really meant is not in any text it has, and that it reads only the words of each
  pass.
- It gives no reading, guesses no reason and drafts no reply, since neither pass's words are given.
- It asks in one message for each pass word for word (the email, or the founder's notes from the call, marked as
  notes), who sent it, its date, how far the process got, which passes to answer and whether to ask each for one
  referral.
- It names no fund or person to try next and invents nothing about Company CR.
