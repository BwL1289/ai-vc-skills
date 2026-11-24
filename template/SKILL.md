---
name: my-skill-name
description: What the skill does in one sentence. Use when the user asks a concrete trigger question, names a document type, or wants a specific calculation. Say what it does NOT do when another skill does.
---

# My skill name

One paragraph: the job this skill does, and the tool or method it uses to do it exactly.

## When to use it

- The questions or documents that should trigger it, in the user's own words.
- When to hand off to another skill instead.

## Steps

1. What to read or ask for first.
2. Which tool to call, with which inputs: the MCP tool first, the command line only as the fallback. Every number
   comes from a tool or from the document, never from memory.
3. How to check the result before answering.

## Answering

- The shape of the answer: the verdict first, then the numbers, then the assumptions with their sources.
- What to say when an input is missing: ask for it, never guess it.

## Limits

- What the skill does not cover, and that its output is not investment, legal or tax advice.
- When neither the calculator's MCP tool for a call nor its command line runs in the session, say so and give no figure
  in that tool's place: none worked by hand and none from a worked example, a made-up company's result.
