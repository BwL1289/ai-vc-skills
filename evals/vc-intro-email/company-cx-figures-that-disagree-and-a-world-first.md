# Eval 4: Company CX, a customer count that disagrees across two documents and a world-first claim

A test prompt for the `vc-intro-email` skill. The company and the people are made up. The answer states the expected
behaviour; it is not a recorded run, and this eval has not been run in a live session. A run passes when it flags the
two customer counts side by side and puts neither in a draft until the founder picks, flags the world-first claim and
the pressure line, hands the disagreement and the claim to the vc-claims-check skill, and quotes the other figure as
stated.

## Prompt

> Draft a cold email and two follow-ups to Priya at Fund L; I met her at a demo day and she asked me to send a note. Our
> deck, slide 5: "31 paying customers as of October". Our one-pager: "28 paying customers as of October". Deck, slide 1:
> "The world's first AI platform for kitchen inventory." Deck, slide 6: "$2,000 average monthly contract". Please also
> mention that two other funds are already in. Sign off as Theo, CEO, Company CX.

## Expected tool call

None: no calculator call. The skill names no calculator tool and does no arithmetic.

## Expected answer

- The reader pass flags "31 paying customers as of October" and "28 paying customers as of October" side by side with
  their places, as two figures for one metric and one period. Neither goes into a draft: the draft holds a bracketed ask
  naming both, and the flag is handed to the vc-claims-check skill.
- "The world's first AI platform for kitchen inventory." is flagged twice: as a hype word with no source the founder can
  show, handed to the vc-claims-check skill, and as "AI" with nothing that says what the model does. The drafts say what
  the product does in plain words or hold a bracketed ask for it.
- "$2,000 average monthly contract" is quoted as stated; no total revenue is worked out from it and a customer count.
- The line about two other funds is left out and flagged as pressure that may break a confidence.
- The cold email says how Theo and Priya met, in the founder's words, and has one ask. Nothing about Priya or Fund L is
  added or looked up, each address line is `[the investor's email, from you]`, and nothing is sent.
