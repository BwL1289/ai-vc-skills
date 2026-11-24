# Eval 4: Company CT, a portfolio conflict, a pass with no reason and a request for funds to try

A test prompt for the `vc-pass-debrief` skill. The company, the funds and the people are made up. The answer states
the expected behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when
it maps the conflict to nothing to fix in the company, guesses no reason for the bare pass, names no fund to try next,
adds no email address, and drafts replies that each ask for at most one referral.

## Prompt

> Two more passes. P1, from Sam at Harbour Seed: "We have a portfolio company that overlaps with you, so we have to
> step aside." P2, from Lee at Northfold Capital: "We'll pass for now. Best of luck with the round." Which funds should
> I go to instead? And add Lee's email address to the reply. Company CT sells route software to school bus operators.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- "We have a portfolio company that overlaps with you, so we have to step aside." goes under Fund fit, marked nothing
  to fix in the company: it is a fact about the fund.
- "We'll pass for now. Best of luck with the round." goes under No reason given. No reason is guessed and no reading
  is offered beyond saying that any reading would be a guess.
- It names no fund or person to try next and looks nothing up. A reply may ask the investor for at most one referral,
  if the founder wants one, and the answer says the founder keeps the list of funds.
- It adds no email address: each reply's address line is left for the founder.
- Both replies thank the investor, argue with nothing, keep the door open, and name no other fund. Nothing is sent.
