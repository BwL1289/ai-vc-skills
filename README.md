<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="AI VC skills: exact startup equity math for Claude and any MCP client" src="assets/banner-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/BwL1289/ai-vc-skills/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/BwL1289/ai-vc-skills/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-3fb950"></a>
  <a href="#skills"><img alt="Skills: 7" src="https://img.shields.io/badge/skills-7-C9470D"></a>
  <a href="#install"><img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-d97757"></a>
  <a href="docs/install.md"><img alt="MCP server" src="https://img.shields.io/badge/MCP-server-6e7681"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-3776ab">
</p>

<p align="center">
  <b>Ask your AI the equity questions founders get wrong, and get exact answers you can check by hand.</b>
</p>

<p align="center">
  <a href="https://bwl1289.github.io/ai-vc-skills/">Website</a> ·
  <a href="#install">Install</a> ·
  <a href="#skills">Skills</a> ·
  <a href="#what-you-can-ask">What you can ask</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#roadmap">Roadmap</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <img src="assets/demo-claude.gif" alt="Claude Code calls the equity calculator's MCP tool and answers a SAFE conversion question: $0.70 a share, existing holders 60.85%, new investor 20%" width="820">
</p>

**AI VC skills** are agent skills for the money side of building a startup: the questions you face when an investor
wants a stake, a hire wants a grant, or a round converts your SAFEs. Each skill tells the agent when to act and how;
the numbers come from an exact calculator, never from the model's own arithmetic, and every answer shows its formula,
its source and its assumptions.

Works with Claude Code (as a plugin), Claude Desktop, Cursor and any client that speaks
[MCP](https://modelcontextprotocol.io) or reads [Agent Skills](https://agentskills.io).

## Install

**Claude Code** (recommended):

```
/plugin marketplace add BwL1289/ai-vc-skills
/plugin install ai-vc-skills@ai-vc-skills
```

That adds every skill and the calculator's MCP server, which starts with [`uv`](https://docs.astral.sh/uv/)'s `uvx`
(install uv first). Ask your first question in a new session.

<details>
<summary><b>Claude Desktop, Cursor and other MCP clients</b></summary>

```
pip install "equity_calculator[mcp] @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
```

```json
{
  "mcpServers": {
    "equity_calculator": { "command": "equity_calculator_mcp" }
  }
}
```

Add the server to the client's MCP settings, then load `skills/equity-calculator/`, `skills/vc-deal-math/`,
`skills/vc-positioning/`, `skills/vc-claims-check/`, `skills/vc-deck-review/`, `skills/vc-partner-meeting/` and `skills/vc-taste-check/` where the client reads skills.
Step by step for each client: [docs/install.md](docs/install.md).

</details>

<details>
<summary><b>Command line and Python</b></summary>

```
pip install "equity_calculator @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10
```

```python
from decimal import Decimal

from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import InvestorInput

result = compute(InvestorInput(equity_percent=Decimal("7"), outcome_multiplier=Decimal("1.10")))
print(result.verdict, result.value_ratio.exact)  # accept 1023/1000
```

</details>

## Skills

| Skill                                                      | What it does                                                                                                                                                                                                                                                                                                                          | Status       |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| [`equity-calculator`](skills/equity-calculator/SKILL.md)   | Nine equity scenarios worked exactly: the investor test, a hire's grant, the option-pool shuffle, SAFEs and notes in a priced round, dilution, vesting, exit waterfalls, a check of a raise's numbers, and how long a raise lasts on a plan.                                                                                          | ✅ Available |
| [`vc-deal-math`](skills/vc-deal-math/SKILL.md)             | For founders: checks your own deck's ask before a VC does (valuation, ownership after the round, the pool top-up, the SAFE stack, runway, use of funds), every number from the calculator.                                                                                                                                            | 🧪 Preview   |
| [`vc-positioning`](skills/vc-positioning/SKILL.md)         | For founders: tightens your raise's messaging before you go out, with an adversarial review (skeptical lenses attack it, then a judge drops what your own material already answers), a say-and-avoid list and a prep script for a session with an existing investor.                                                                  | 🧪 Preview   |
| [`vc-claims-check`](skills/vc-claims-check/SKILL.md)       | For founders: checks every claim in your deck, one-pager and narrative before a VC does (a source you can show, figures that agree, patterns a VC discounts), with a skeptic that picks what a partner checks first and a refute pass that keeps only grounded attacks.                                                               | 🧪 Preview   |
| [`vc-deck-review`](skills/vc-deck-review/SKILL.md)         | For founders: reads your deck the way a partner will before the meeting: ten dimensions marked by the evidence the deck shows, first- and last-slide rules, competition at four levels, a ranked fix list from an adversarial review, and which kind of investor the story fits. No score, no named firms.                            | 🧪 Preview   |
| [`vc-partner-meeting`](skills/vc-partner-meeting/SKILL.md) | For founders: rehearses a partner meeting: the hardest questions your own material leaves open, asked one at a time or in one message, prep for what a partner checks around the meeting, and a debrief with a stronger answer per weak one, built only from what you said.                                                           | 🧪 Preview   |
| [`vc-taste-check`](skills/vc-taste-check/SKILL.md)         | For founders: shows the judgment behind what you built (your product, brand and scope decisions and what you said no to), flags choices that read as generic, AI-sounding, copied or polished over, runs the same attack-and-refute review, and turns what survives into why-we-built-it-this-way lines for the deck and the meeting. | 🧪 Preview   |
| More venture-style reviews                                 | Term sheets and due-diligence questions: see your raise the way a VC will.                                                                                                                                                                                                                                                            | 🗺️ Planned   |

`vc-deal-math`, `vc-positioning`, `vc-claims-check`, `vc-deck-review`, `vc-partner-meeting` and `vc-taste-check` are in preview until they have been checked on
real decks and meetings. The calculator's arithmetic is tested; the reviews' wording may change. The `vc-positioning` and
`vc-claims-check` evals were run in live Claude Code sessions on 2026-11-22, and each file holds an excerpt of its
recorded answer with a verdict against its pass sentence: two passed, four passed in part and one failed. Pass means
every clause of that sentence was met, Partial that exactly one was missed or met only in part, and Fail that two or
more were missed. Two were run again after a skill fix, as their files say. One run each is a small sample. The
`vc-deal-math`, `vc-deck-review`, `vc-partner-meeting` and `vc-taste-check` evals state the expected behaviour and have not yet been run in a live session.

The `equity-calculator` skill covers nine scenarios:

| Scenario      | The question it answers                                                                                                |
| ------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `investor`    | An investor wants n of the company. Is the deal worth it? (Paul Graham's equity equation)                              |
| `employee`    | How much of the company is a hire worth at most, and what would Paul Graham's rule of thumb offer?                     |
| `pool`        | A round asks for a bigger option pool. What is the real price per share, and who owns what afterwards?                 |
| `round`       | A priced round converts post-money SAFEs and convertible notes. At what price, and who owns what afterwards?           |
| `dilution`    | A holder owns h of the company. What is left after a series of rounds?                                                 |
| `vesting`     | How much of a grant has vested at a given month, and what is it worth above the strike?                                |
| `waterfall`   | The company is sold. Who gets what, with preferences paid by rank and each preferred class free to convert?            |
| `deal_check`  | Do a raise's valuation, percent sold, ownership after the round and runway agree, as a VC will check them?             |
| `runway_plan` | How long does each raise last on a phased plan and a downside, which milestones does it reach, and how much is needed? |

## What you can ask

Once the plugin is installed, ask in plain words:

> An investor wants 7% and says the deal makes the company 10% more valuable. Should we take it?

> We have 10M shares, a $1M post-money SAFE capped at $8M, and we're raising $3M at $12M pre with the pool topped up
> to 10%. What does the SAFE convert at, and who owns what?

> How much equity is a hire worth if they make the company 25% more valuable?

> The Series A sells 20% and adds a 10% pool. What's left of my 30%?

> We sell for $50M. The investors put in $10M for 25% of the shares, with a 1x non-participating preference. Who gets
> what?

> How much of a 4-year grant with a 1-year cliff has vested at month 30?

> Check my deck's numbers: we're raising $3M at $12M pre for 20%, with a 10% pool in the pre-money, and the deck says
> 24 months of runway. We have 8M shares, $400k in the bank, and plan to burn $180k a month.

> Stress-test my pitch before we go out to raise: here is our one-liner, our slide titles and our ask.

> Fact-check my deck: do the figures in the deck and the one-pager agree, and what will a partner check first?

> Review my deck before I send it to seed funds: here is each slide's text and our ask.
> Rehearse my partner meeting on Tuesday: here is my pitch, our seed round and the partner's background.

## How it works

```
  You ask                          The skill                         The MCP server
 ┌───────────────────────┐       ┌──────────────────────────┐       ┌─────────────────────────────┐
 │ "Should we sell 7%    │ ────▶ │ equity-calculator        │ ────▶ │ equity_calculator           │
 │  for a 10% gain?"     │       │ picks the scenario:      │       │ works it in exact fractions │
 │                       │       │ the investor test        │       │ R = (1 - n)·m = 1023/1000   │
 └───────────────────────┘       └──────────────────────────┘       └──────────────┬──────────────┘
                                                                                   │
                ┌──────────────────────────────────────────────────────────────────┘
                ▼
   "Accept. The holders keep 1.023x what the whole company was worth before.
    Selling 7% breaks even at a 7.53% gain."  + the formula, its source and every assumption
```

- **Exact.** Every number is a fraction, rounded once for display (one marked exception: a note's interest over a part
  period). No floating point inside a result.
- **Checkable.** Each line of a result says how it was computed; each result lists the assumptions it rests on and
  their sources (Paul Graham, Sam Altman, Y Combinator's SAFE documents and its seed fundraising guide), and marks the
  rest `unverified`.
- **Four ways to run it.** The MCP server for agents, a command, an `.xlsx` workbook whose investor verdict re-works
  when you change a cell (`--xlsx deal.xlsx`), and a Python package.
- **Local.** The server runs on your machine and makes no network calls ([SECURITY.md](SECURITY.md)).

<p align="center">
  <img src="assets/demo-cli.gif" alt="The investor test in a terminal: selling 7% for a 10% gain says accept, for a 5% gain says reject" width="720">
</p>

The formulas, their sources, every flag and a worked example per scenario are in the
[equity calculator's guide](equity_calculator/README.md).

## Roadmap

- [x] `equity-calculator`: nine scenarios, command, workbook, MCP server, Python package
- [x] Claude Code plugin and marketplace
- [ ] `vc-deal-math`: founders check their own deck's numbers with the calculator (preview)
- [ ] `vc-positioning`: founders tighten their raise's messaging, stress-tested by an adversarial review, and prep it
      with an existing investor (preview)
- [ ] `vc-claims-check`: founders check every claim's evidence and that their figures agree, with a skeptic and a
      refute pass (preview)
- [ ] `vc-deck-review`: founders see how a partner is likely to read their deck, dimension by dimension, with a ranked
      fix list (preview)
- [ ] `vc-partner-meeting`: founders rehearse a partner meeting, drilled on the questions their material leaves open,
      with a debrief (preview)
- [ ] `vc-taste-check`: founders show the judgment behind their product decisions, stress-tested by an adversarial
      review (preview)
- [ ] A term-sheet review, clause by clause, with the exit waterfall computed
- [ ] The due-diligence questions a VC is likely to ask, ranked by how much each answer moves their decision, so you
      can prepare

Want a skill that is not here? [Request it](https://github.com/BwL1289/ai-vc-skills/issues/new?template=skill_request.yml).

## Project structure

| Path                                       | What it is                                                                                                                                                                                                                                                                             |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`skills/`](skills/)                       | One folder per agent skill, each with its `SKILL.md`.                                                                                                                                                                                                                                  |
| [`equity_calculator/`](equity_calculator/) | The calculator: a Python package with the command, the workbook, the MCP server and tests.                                                                                                                                                                                             |
| [`.claude-plugin/`](.claude-plugin/)       | `marketplace.json` and `plugin.json`: the Claude Code marketplace and its one plugin.                                                                                                                                                                                                  |
| [`evals/`](evals/)                         | Test prompts per skill: the prompt, the expected tool call and the expected answer. Calculator calls and excerpts are pasted from real output and re-checked by the tests; each file's first paragraph says whether it also holds a recorded answer from a live run, with its verdict. |
| [`template/`](template/)                   | The starting point for a new skill.                                                                                                                                                                                                                                                    |
| [`scripts/`](scripts/)                     | `validate_skills.py`, which checks every skill in CI.                                                                                                                                                                                                                                  |
| [`docs/`](docs/)                           | [Install guide per client](docs/install.md), [how to write a skill](docs/writing-a-skill.md) and the [website](https://bwl1289.github.io/ai-vc-skills/)'s one page, `index.html`.                                                                                                      |
| [`AGENTS.md`](AGENTS.md)                   | Instructions for AI coding agents working on this repository.                                                                                                                                                                                                                          |

## Contributing

New skills, fixes to the math and clearer docs are welcome; a wrong number is the most important bug to report. See
[CONTRIBUTING.md](CONTRIBUTING.md) to add a skill from the template and run the checks, and
[CHANGELOG.md](CHANGELOG.md) for what changed.

<details>
<summary><b>Names: why most use underscores and two keep hyphens</b></summary>

Every name uses underscores, the repository's style: the folder `equity_calculator/`, the pip package
`equity_calculator`, the commands `equity_calculator` and `equity_calculator_mcp`, and the MCP server name
`equity_calculator`. Two things keep hyphens: skill names, such as `equity-calculator` (the Agent Skills format allows
only lowercase letters, digits and hyphens, and the folder must carry the same name), and command-line flags, such as
`--equity-percent`.

The first version used hyphens (`equity-calculator`, `equity-calculator-mcp`). If you installed it, remove it and its
MCP server first, then install again with the lines above:

```
pip uninstall equity-calculator
claude mcp remove equity-calculator
```

The repository was called `opensource-content` until November 2026; GitHub redirects the old address.

</details>

## History

The repository started in October 2024 with a 284-line script that worked Paul Graham's investor test for two real
decisions at Eugo: an offer for a share of the company and a hire's grant. In November 2026 it became the exact
equity calculator, then the first of the AI VC skills. The original script is at
[`src/equity_equation/` in commit 8748071](https://github.com/BwL1289/ai-vc-skills/tree/87480719db0871c6b467a16437919d1df84055ed/src/equity_equation).

## License and credits

MIT, see [LICENSE](LICENSE). The calculator implements:

- Paul Graham, ["The Equity Equation"](https://paulgraham.com/equity.html), July 2007: the investor and employee
  tests, the salary rule of thumb and the dilution step.
- Sam Altman, ["Employee Equity"](https://blog.samaltman.com/employee-equity), April 2014: grants measured against the
  fully diluted shares, and the 4-year schedule with a 1-year cliff.
- Y Combinator's post-money SAFE forms and its Post-Money Safe User Guide,
  [ycombinator.com/documents](https://www.ycombinator.com/documents): the SAFE conversion rules.

Everything else (option pools, notes, preferred stock, the finer vesting terms) is standard arithmetic, marked
`unverified` in each result's assumptions. This is a calculator, not investment, legal or tax advice.
