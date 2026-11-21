<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="AI VC skills: exact startup equity math for Claude and any MCP client" src="assets/banner-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-3fb950"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-3776ab">
  <a href="#claude-code"><img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-d97757"></a>
  <a href="#any-mcp-client"><img alt="MCP server" src="https://img.shields.io/badge/MCP-server-6e7681"></a>
</p>

<p align="center">
  <b>Ask your AI assistant the equity questions founders get wrong, and get exact answers you can check by hand.</b>
</p>

<p align="center">
  <img src="assets/demo.gif" alt="The investor test in a terminal: selling 7% for a 10% gain says accept, for a 5% gain says reject" width="820">
</p>

Agent skills for the money side of building a startup. The first is the **equity calculator**: Paul Graham's equity
equation, the option-pool shuffle, SAFEs and notes converting in a priced round, dilution, vesting and exit
waterfalls, worked as exact fractions. Claude calls it instead of doing the arithmetic in its head, and every answer
shows how each line is computed and which assumptions it rests on.

## Install

### Claude Code

```
/plugin marketplace add BwL1289/ai-vc-skills
/plugin install equity-calculator@ai-vc-skills
```

That adds the agent skill and the MCP server. The server starts with [`uvx`](https://docs.astral.sh/uv/), so install
uv first if you do not have it.

### Any MCP client

<details>
<summary>Claude Desktop, Cursor and other MCP clients</summary>

Install the package with its MCP server (Python 3.12 or later):

```
pip install "equity_calculator[mcp] @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
```

Then add the server to the client's MCP settings:

```json
{
  "mcpServers": {
    "equity_calculator": { "command": "equity_calculator_mcp" }
  }
}
```

In Claude Code without the plugin: `claude mcp add equity_calculator -- equity_calculator_mcp`.

</details>

### Command line and Python

<details>
<summary>pip, or a clone to work on it</summary>

```
pip install "equity_calculator @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
```

The command and the library need only Pydantic and openpyxl; add `[mcp]` for the server. From a clone:

```
git clone https://github.com/BwL1289/ai-vc-skills
cd ai-vc-skills
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e "./equity_calculator[mcp,dev]"
```

</details>

## What you can ask

Once the plugin is installed, ask in plain words:

- "An investor wants 7% and says the deal makes the company 10% more valuable. Should we take it?"
- "We have 10M shares, a $1M post-money SAFE capped at $8M, and we're raising $3M at $12M pre with the pool topped
  up to 10%. What does the SAFE convert at, and who owns what?"
- "How much equity is a hire worth if they make the company 25% more valuable?"
- "The Series A sells 20% and adds a 10% pool. What's left of my 30%?"
- "We sell for $50M. The investors put in $10M for 25% of the shares, with a 1x non-participating preference. Who
  gets what?"
- "How much of a 4-year grant with a 1-year cliff has vested at month 30?"

```mermaid
flowchart LR
  Q["Your question"] --> C["Claude, or any MCP client"]
  C -->|"the skill picks the scenario"| T["equity_calculator tool"]
  T --> X["Exact fractions"]
  X --> R["Report with every formula and source"]
```

## Skills

| Skill                                                                      | Status    | What it does                                                                     |
| -------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------- |
| [`equity-calculator`](equity_calculator/skills/equity-calculator/SKILL.md) | Available | Seven equity scenarios, worked exactly, with the formulas and sources shown.     |
| More AI VC skills                                                          | Planned   | Reviews in the style of a venture firm: pitch decks, term sheets, due diligence. |

## The equity calculator

| Scenario    | The question it answers                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| `investor`  | An investor wants n of the company. Is the deal worth it?                                                    |
| `employee`  | How much of the company is a hire worth at most, and what would Paul Graham's rule of thumb offer?           |
| `pool`      | A round asks for a bigger option pool. What is the real price per share, and who owns what afterwards?       |
| `round`     | A priced round converts post-money SAFEs and convertible notes. At what price, and who owns what afterwards? |
| `dilution`  | A holder owns h of the company. What is left after a series of rounds?                                       |
| `vesting`   | How much of a grant has vested at a given month, and what is it worth above the strike?                      |
| `waterfall` | The company is sold. Who gets what, with preferences paid by rank and each preferred class free to convert?  |

It runs four ways, all from the same model:

| Way        | How                                                                                                  |
| ---------- | ---------------------------------------------------------------------------------------------------- |
| Command    | `equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10`                            |
| Workbook   | Add `--xlsx deal.xlsx` to a command: an `.xlsx` whose investor verdict re-works when a cell changes. |
| MCP server | `equity_calculator_mcp`: one tool per scenario, for Claude or any MCP client.                        |
| Python     | `from equity_calculator.scenarios import compute`                                                    |

Every number is worked as an exact fraction and shown rounded once (one case aside: a note's interest over a part
period, which is marked approximate). Every result says how each line is computed and lists the assumptions it rests
on, with their sources.

### Quick start

Paul Graham's example from "The Equity Equation": selling 7% for a 10% better outcome.

```
equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10
```

Among the lines it prints:

```
  Value ratio R             1.023000x  (1 - n)·m: what the holders keep vs. before
  Break-even multiplier m*  1.075269x  1/(1 - n)
  Verdict                      accept  accept: R > 1; break_even: R = 1; reject: R < 1
```

Add `--json` for the whole result as JSON, or `--xlsx investor.xlsx` to write the workbook too.
`equity_calculator --help` lists the scenarios and `equity_calculator investor --help` the flags of one.

From Python:

```python
from decimal import Decimal

from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import InvestorInput

result = compute(InvestorInput(equity_percent=Decimal("7"), outcome_multiplier=Decimal("1.10")))
print(result.verdict, result.value_ratio.exact)  # accept 1023/1000
```

The [package README](equity_calculator/README.md) has the rest: every flag, the MCP tools and other clients, the agent
skill, the workbook, the limits and a worked example for each scenario.

### The formulas in brief

- **Investor** (Paul Graham). Sell n of the company for a deal that multiplies its average outcome by m, and the
  holders keep R = (1 - n)·m of what the whole company was worth before. Accept when R > 1. The break-even multiplier
  is m\* = 1/(1 - n): selling 7% breaks even at 1.0753x.
- **Employee** (Paul Graham). A hire who makes the average outcome i times what it was is worth at most
  n = (i - 1)/i of the company.
- **Option pool.** A pool topped up before the round is paid for by the existing holders: with a target t, a
  pre-money V and an investment I, their shares are worth V - t(V + I) at the round price, not V.
- **SAFEs and notes** (Y Combinator's post-money SAFE). Each converts at the lower of its cap price and the round
  price less its discount, the one that gives it more shares.
- **Dilution.** Each round k that sells `n_k` and adds a pool `p_k` leaves a holder `h_k = h_(k-1)·(1 - n_k - p_k)`.
- **Vesting** (Sam Altman's 4 years with a 1-year cliff by default). Nothing before the cliff, then G·min(s, T)/T of a
  grant of G shares after s of T months.
- **Waterfall.** Preferences are paid by rank, the rest is shared per share, and each preferred class converts to
  common exactly when that pays it strictly more.

Each formula, its sources and the points no source settles (marked `unverified` in every result) are in
[The formulas](equity_calculator/README.md#the-formulas).

## What is in the repository

| Path                                                                   | What it is                                                                                        |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| [`equity_calculator/`](equity_calculator/)                             | The equity calculator: code, tests, MCP server, agent skill, plugin manifest and its full guide.  |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)   | The Claude Code marketplace that lists this repository's plugins.                                 |
| `assets/`                                                              | The banner and the demo GIF on this page.                                                         |
| `pyproject.toml`                                                       | Settings for the whole repository: the dev tools (`dev` group), ruff, isort, pytest and coverage. |
| `.pre-commit-config.yaml`                                              | The hooks every commit runs (see [Working on the repository](#working-on-the-repository)).        |
| [`.github/pull_request_template.md`](.github/pull_request_template.md) | The checklist every pull request starts with.                                                     |
| [`LICENSE`](LICENSE)                                                   | MIT.                                                                                              |

## Names

<details>
<summary>Why most names use underscores and two keep hyphens</summary>

Every name uses underscores, the repository's style: the folder `equity_calculator/`, the pip package
`equity_calculator`, the commands `equity_calculator` and `equity_calculator_mcp`, and the MCP server name
`equity_calculator`. Two things keep hyphens:

- The agent skill and the Claude Code plugin are `equity-calculator`. The skill is in
  [`equity_calculator/skills/equity-calculator/`](equity_calculator/skills/equity-calculator/SKILL.md). The Agent
  Skills format allows only lowercase letters, digits and hyphens in a skill's name, and the folder must carry the
  same name.
- Command-line flags, such as `--equity-percent`.

The first version used hyphens (`equity-calculator`, `equity-calculator-mcp`). Those names are gone. Installing the
new version over the first one changes nothing, because pip reads both names as the same package at the same version.
If you installed the first version, remove it and its MCP server first, then install and register again with the
lines above:

```
pip uninstall equity-calculator
claude mcp remove equity-calculator
```

The repository was called `opensource-content` until November 2026; GitHub redirects the old address.

</details>

## Working on the repository

<details>
<summary>Set-up, commit hooks and tests</summary>

Set up a clone as in [Command line and Python](#command-line-and-python), then add the tools and the commit hooks:

```
python -m pip install -U pip   # dependency groups need pip 25.1 or later
pip install --group dev
pre-commit install
pre-commit run --all-files
```

The hooks are ruff (lint, with fixes) and ruff-format, isort, pyupgrade, prettier for Markdown, YAML and JSON, and
pre-commit's standard checks (trailing whitespace, merge conflicts, valid YAML, TOML and JSON, and others), plus a few
pattern checks such as no `eval`.

Run the tests from the repository root:

```
pytest
```

That runs the calculator's tests with branch coverage of the `equity_calculator` package; the coverage report is
printed and written to `htmlcov/`. Coverage counts the package only when it is installed with `pip install -e`, as
above. The tests need no network. Inside the repository they write only the coverage files, pytest's cache and
Python bytecode, all git-ignored; everything else goes under pytest's temporary folder.
`cd equity_calculator && pytest` runs the same tests with the package's own settings and no coverage.

To try the plugin from a clone, add the clone as a marketplace in Claude Code:
from inside the clone, `/plugin marketplace add ./`, then `/plugin install equity-calculator@ai-vc-skills`.

The calculator's folder:

```
equity_calculator/
  pyproject.toml           the package: name, dependencies, the two commands
  README.md                the full guide
  LICENSE                  MIT, the same as the repository's
  .claude-plugin/          the Claude Code plugin manifest and icon
  .mcp.json                the MCP server the plugin starts
  src/equity_calculator/   the code: scenarios, command, workbook, MCP server
  tests/                   the tests
  skills/equity-calculator/SKILL.md   the agent skill
```

Every pull request starts from [the template](.github/pull_request_template.md): say what kind of change it is, and
run `pre-commit run --all-files` before asking for review.

</details>

## History

The repository started in October 2024 with `src/equity_equation`, a script that worked Paul Graham's investor test.
In November 2026 it grew into the equity calculator, which works the same test exactly and adds the six other
scenarios, and became the home of the AI VC skills. The original script is at
[`src/equity_equation/` in commit 8748071](https://github.com/BwL1289/ai-vc-skills/tree/87480719db0871c6b467a16437919d1df84055ed/src/equity_equation).

## License and credits

MIT, see [LICENSE](LICENSE).

The calculator implements:

- Paul Graham, ["The Equity Equation"](https://paulgraham.com/equity.html), July 2007: the investor and employee
  tests, the salary rule of thumb and the dilution step.
- Sam Altman, ["Employee Equity"](https://blog.samaltman.com/employee-equity), April 2014: grants measured against the
  fully diluted shares, and the 4-year schedule with a 1-year cliff.
- Y Combinator's post-money SAFE forms and its Post-Money Safe User Guide,
  [ycombinator.com/documents](https://www.ycombinator.com/documents): the SAFE conversion rules.

Everything else (option pools, notes, preferred stock, the finer vesting terms) is standard arithmetic, marked
`unverified` in each result's assumptions.
