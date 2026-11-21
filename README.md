# opensource-content

Open-source code, one project per folder. Today there is one project: the **equity calculator**, which works the
questions founders ask about stock with exact arithmetic. Should we sell 7% for this deal? What does a bigger option
pool do to the price per share? How do our SAFEs convert in the next round? Who gets what when the company is sold?
It answers as a command, an Excel workbook with live formulas, an MCP server that an AI assistant can call, and a
Python library.

## What is in the repository

| Path                                                                   | What it is                                                                                                                                                      |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`equity_calculator/`](equity_calculator/)                             | The equity calculator, a Python package of its own: code, tests, MCP server, agent skill and the [full guide](equity_calculator/README.md).                     |
| [`src/main.py`](src/main.py)                                           | Runs the calculator's command (`python3 src/main.py --help`) once it is installed, or says how to install it.                                                   |
| [`src/equity_equation/`](src/equity_equation/)                         | Where the original `equity_equation` script lived. It now points to the calculator; the script is in the git history (see [History](#history)).                 |
| [`src/utils/`](src/utils/)                                             | The small `Constants` enum the original script used. Nothing imports it now.                                                                                    |
| `pyproject.toml`, `setup.cfg`                                          | Settings for the whole repository: ruff, isort, pytest and coverage.                                                                                            |
| `.pre-commit-config.yaml`                                              | The hooks every commit runs (see [Working on the repository](#working-on-the-repository)).                                                                      |
| `.pre-commit-hooks.yaml`                                               | Hook definitions in pre-commit's hook-repository format (pre-commit's standard checks plus ruff). The hooks that run are the ones in `.pre-commit-config.yaml`. |
| `dev_requirements.txt`                                                 | The tools for working on the repository: pre-commit, pytest-cov and ruff.                                                                                       |
| [`.github/pull_request_template.md`](.github/pull_request_template.md) | The checklist every pull request starts with.                                                                                                                   |
| [`LICENSE`](LICENSE)                                                   | MIT.                                                                                                                                                            |

## The equity calculator

Seven scenarios, each with its own subcommand and MCP tool:

| Scenario    | The question it answers                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| `investor`  | An investor wants n of the company. Is the deal worth it?                                                    |
| `employee`  | How much of the company is a hire worth at most, and what would Paul Graham's rule of thumb offer?           |
| `pool`      | A round asks for a bigger option pool. What is the real price per share, and who owns what afterwards?       |
| `round`     | A priced round converts post-money SAFEs and convertible notes. At what price, and who owns what afterwards? |
| `dilution`  | A holder owns h of the company. What is left after a series of rounds?                                       |
| `vesting`   | How much of a grant has vested at a given month, and what is it worth above the strike?                      |
| `waterfall` | The company is sold. Who gets what, with preferences paid by rank and each preferred class free to convert?  |

Every number is worked as an exact fraction and shown rounded once (one case aside: a note's interest over a part
period, which is marked approximate). Every result says how each line is computed and lists the assumptions it rests
on, with their sources, so you can check it by hand.

### Install

Python 3.12 or later. From GitHub, with the MCP server:

```
pip install "equity_calculator[mcp] @ git+https://github.com/BwL1289/opensource-content#subdirectory=equity_calculator"
```

Leave out `[mcp]` for the command and the library alone; they need only Pydantic and openpyxl.

Or from a clone, which is also how to work on it:

```
git clone https://github.com/BwL1289/opensource-content
cd opensource-content
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e "./equity_calculator[mcp,dev]"
```

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

To let Claude Code call it, register the MCP server:

```
claude mcp add equity_calculator -- equity_calculator_mcp
```

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

## Names

Every name uses underscores, like the rest of the repository (`src/equity_equation`): the folder
`equity_calculator/`, the pip package `equity_calculator`, the commands `equity_calculator` and
`equity_calculator_mcp`, and the MCP server name `equity_calculator`. Two things keep hyphens:

- The agent skill is `equity-calculator`, in
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

## Working on the repository

Set up a clone as in [Install](#install), then add the tools and the commit hooks:

```
pip install -r dev_requirements.txt
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

The calculator's folder:

```
equity_calculator/
  pyproject.toml           the package: name, dependencies, the two commands
  README.md                the full guide
  LICENSE                  MIT, the same as the repository's
  src/equity_calculator/   the code: scenarios, command, workbook, MCP server
  tests/                   the tests
  skills/equity-calculator/SKILL.md   the agent skill
```

Every pull request starts from [the template](.github/pull_request_template.md): say what kind of change it is, and
run `pre-commit run --all-files` before asking for review.

## History

The repository started in 2024 with `src/equity_equation`, a script that worked Paul Graham's investor test. In
November 2026 it grew into the equity calculator, which works the same test exactly and adds the six other
scenarios. The original script is at
[`src/equity_equation/` in commit 8748071](https://github.com/BwL1289/opensource-content/tree/87480719db0871c6b467a16437919d1df84055ed/src/equity_equation).

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
