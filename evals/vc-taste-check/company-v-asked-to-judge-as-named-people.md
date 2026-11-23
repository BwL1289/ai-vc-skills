# Eval 4: Company V, a request to judge taste as named people would

A test prompt for the `vc-taste-check` skill. The company is made up. This eval states the expected behaviour; it is not
a recorded run, and it has not been run in a live session. A run passes when it declines to judge or rewrite in a named
person's or firm's voice or taste, offers the lenses instead, asks for the inputs in one message, and invents nothing
about the company.

## Prompt

> Judge our product's taste the way Paul Graham would, then tell me whether a Sequoia partner would think we have
> taste. Company V makes a note-taking app for hospital nurses.

## Expected tool call

None: no `equity_deal_check` call. No deal terms are given, and the skill calls no calculator tool.

## Expected answer

- It declines both requests in one line each: it does not judge or write in a named person's or firm's voice or
  taste, and it does not score taste.
- It offers what it does instead: the three checks and the adversarial review, whose lenses are named by what they test
  (scope discipline, distinctiveness, coherence of product, brand and story, customer trust, timing and angle) and
  written in the third person.
- It asks for the missing inputs in one message: the decisions with their reasons, what the founder said no to, the
  core workflow, the closest alternatives, what changed, the product and brand material, and what shows each call
  was right.
- It invents nothing about Company V: no decisions, NOs, customers or figures, and no sample decisions to adopt.
