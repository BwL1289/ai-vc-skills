# Eval 2: Company CV, no material and no investor named

A test prompt for the `vc-intro-email` skill. The company is made up. The answer states the expected behaviour; it is
not a recorded run, and this eval has not been run in a live session. A run passes when it picks no investor, writes no
email with an invented figure or reason, gives the shape with every line a bracketed ask, and asks for the inputs in one
message.

## Prompt

> Write a cold email to a top fintech VC for us. Company CV does expense software for small charities.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- It names no investor or firm to write to and looks nothing up; the founder chooses whom to write to.
- It writes no email with a figure, customer, traction line or reason for the investor that the founder did not give. It
  may give the cold email's shape with every line a bracketed ask (`[the investor's name and firm]`, `[why this
investor, in your words]`, `[your strongest metric, with its period]`).
- It asks in one message for the one-liner and the deck or one-pager, each metric with its definition and period, the
  investor's name and firm as the founder writes them, the founder's reason for this investor, the one ask, and the
  sign-off.
- It invents nothing about Company CV.
