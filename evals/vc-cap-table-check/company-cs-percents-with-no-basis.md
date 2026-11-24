# Eval 3: Company CS, a cap table whose percents have no basis

A test prompt for the `vc-cap-table-check` skill. The company is made up. The answer states the expected behaviour; it
is not a recorded run, and this eval has not been run in a live session. The table states percents without saying what
they are a share of, and the founder asks what the SAFE does without giving the next round. A run passes when it makes
no `equity_cap_table_check` call yet, asks in one message for what the table's percents are a share of and for the next
priced round, by name, never picks a basis or a price itself, and computes nothing in its own text.

## Prompt

> Quick one before our board meeting: is this right, and what does our SAFE do to it? Founders 7,000,000 shares (70%),
> employees' options 2,000,000 (20%), pool 1,000,000 (10%). One $750k SAFE at a $9M cap.

## Expected tool call

None: no `equity_cap_table_check` call yet. The tool refuses a stated percent without `stated_percent_basis`, and a
conversion preview needs the next round's pre-money and raise, which the founder has not given.

## Expected answer

- It lists what the table states, word for word: the three lines with their shares and percents, and the SAFE's
  amount and cap.
- It asks, in one message and by name, for what the table's percents are a share of, as the bracketed ask
  `[what the table's percents are a share of: fully diluted or outstanding]`, saying the answer changes which figures
  can be checked, and never picks one because the figures fit it.
- It asks whether the founders' 7,000,000 shares are one line or one per founder, and whether anyone who holds them
  has left.
- It says the SAFE holds no shares until a priced round converts it, and asks for the next priced round the founder
  expects (its pre-money, its raise and any pool top-up) to preview the conversion; it never assumes a price or a
  valuation, and offers to run the tie-out without the preview once the basis is given.
- It gives no percent, total or conversion figure of its own.
