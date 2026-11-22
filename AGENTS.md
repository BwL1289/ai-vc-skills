# AGENTS.md

Instructions for AI coding agents working on this repository. Humans: see [CONTRIBUTING.md](CONTRIBUTING.md).

## What this repository is

AI VC skills: agent skills for the money side of building a startup, shipped as one Claude Code plugin. Skills live in
`skills/<name>/SKILL.md`; the exact math lives in the `equity_calculator` Python package, which the skills call through
its command or its MCP server.

## Layout

| Path                         | What it is                                                                                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `skills/<name>/SKILL.md`     | One agent skill per folder; the folder name is the skill's `name`.                                                                                                                                |
| `evals/<skill>/*.md`         | Test prompts for a skill: the expected tool call and answer. Calculator calls and excerpts are real output; each file says whether its answer is a recorded run or states the expected behaviour. |
| `template/SKILL.md`          | The starting point for a new skill.                                                                                                                                                               |
| `equity_calculator/`         | The Python package: scenarios, command, workbook, MCP server, tests.                                                                                                                              |
| `.claude-plugin/`            | `marketplace.json` (the marketplace) and `plugin.json` (the one plugin).                                                                                                                          |
| `scripts/validate_skills.py` | Checks every skill's frontmatter and that the README lists it.                                                                                                                                    |
| `docs/`                      | Install guide per client, how to write a skill, and the one-page website GitHub Pages serves (`index.html` and its assets; every file the page uses lives here).                                  |

## Rules

- Every number a skill gives comes from a tool or from the user's document, never from the model's own arithmetic.
- A skill never presents investment, legal or tax advice as fact, never speaks as a named investor or firm, and never
  sends a user's document anywhere.
- Keep `SKILL.md` under 500 lines; move long reference material to files beside it and link them.
- A new skill gets a row in the README's skills table (the validator checks) and a line in CHANGELOG.md.
- Use underscores in Python names and hyphens only in skill names and command-line flags (README, "Names").

## Before you finish

```
python scripts/validate_skills.py
pre-commit run --all-files
pytest
claude plugin validate .
```
