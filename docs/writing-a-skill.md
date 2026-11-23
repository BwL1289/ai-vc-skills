# Writing a skill

A skill is a folder in `skills/` holding a `SKILL.md`: YAML frontmatter, then Markdown instructions the agent follows.
Start from [`template/SKILL.md`](../template/SKILL.md).

## Anatomy

```
skills/<skill-name>/
├── SKILL.md          required: frontmatter + instructions (under 500 lines)
└── references/       optional: long material the instructions link to, loaded only when needed
```

```
┌──────────────────────────────────────────────────────────┐
│ SKILL.md                                                 │
│ ┌─ frontmatter ────────────────────────────────────────┐ │
│ │ name: <skill-name>        same as the folder         │ │
│ │ description: what it does + when to use it           │ │
│ └──────────────────────────────────────────────────────┘ │
│ When to use it   → the questions that trigger it         │
│ Steps            → which tool, which inputs, in order    │
│ Answering        → verdict, numbers, assumptions         │
│ Limits           → what it does not cover; not advice    │
└──────────────────────────────────────────────────────────┘
```

## The frontmatter

- `name`: lowercase letters, digits and single hyphens, at most 64 characters, the same as the folder.
- `description`: at most 1,024 characters, no `<` or `>`. It is the only part the agent sees before it decides to load
  the skill, so say what the skill does and list the questions and documents that should trigger it, in the words
  users type ("Should we take this term sheet?", "what does the SAFE convert at").

`python scripts/validate_skills.py` checks both, and that the README's skills table links the folder.

## The rules every skill here follows

1. **Numbers come from tools.** Call the `equity_calculator` MCP tools (or the command) for every figure; never let
   the model do arithmetic in its head. Quote figures from a user's document as the document states them.
2. **Ask, never guess.** A missing input is asked for, by name.
3. **Show the working.** Answer with the verdict, then the numbers, then the assumptions and their sources.
4. **Frameworks, not people.** A review lens is a named framework (YC's application questions, a standard term-sheet
   checklist), never an imitation of a named investor or firm.
5. **Not advice.** Say what a lawyer or accountant should check; never present investment, legal or tax advice as fact.
6. **Nothing leaves the machine.** A skill never sends a user's document to any service.
7. **The founder is the user.** A skill answers a founder's question; an investor's view is a lens a review applies,
   never the role the skill plays.

## Testing a skill by hand

Install the plugin from your clone (`/plugin marketplace add ./`, then `/plugin install ai-vc-skills@ai-vc-skills`),
start a new session, and ask the questions from your description. The skill should load on its own and every number
should come from a tool call you can see.
