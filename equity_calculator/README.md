# Equity calculator

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-3fb950"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-3776ab">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-d97757">
  <img alt="MCP server" src="https://img.shields.io/badge/MCP-server-6e7681">
</p>

The first of the [AI VC skills](../README.md).

Should we trade stock for this, and what does a round do to the cap table? Seven scenarios, worked with exact
arithmetic, printed as a report, as JSON, or as a formatted Excel workbook with live formulas. It comes three ways: a
command, `equity_calculator`; an MCP server, `equity_calculator_mcp`, that gives an AI assistant one tool per
scenario; and a Python package, `equity_calculator`. An agent skill in
[`skills/equity-calculator/`](skills/equity-calculator/SKILL.md) tells an assistant when and how to use it.

Built from the original `equity_equation` script this repository started with (it is in the git history, at
[`src/equity_equation/` in commit 8748071](https://github.com/BwL1289/ai-vc-skills/tree/87480719db0871c6b467a16437919d1df84055ed/src/equity_equation))
and the essay it implements. That script's own TODO
list asked for Pydantic models and cell formatting (percent, numbers); both are here, along with the employee formula
and the option-pool shuffle.

| Scenario    | The question it answers                                                                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `investor`  | An investor wants n of the company. Is the deal worth it, given what it does to the company's average outcome?                                          |
| `employee`  | How much of the company is a hire worth at most, and what would Paul Graham's rule of thumb offer?                                                      |
| `pool`      | A priced round asks for a bigger option pool. What is the real price per share, how many new shares are made, and who owns what afterwards?             |
| `round`     | A priced round converts post-money SAFEs and convertible notes. At what price does each convert, what is the round price, and who owns what afterwards? |
| `dilution`  | A holder owns h of the company. What is left after a series of rounds, each selling a stake and adding a pool?                                          |
| `vesting`   | How much of a grant has vested at a given month, with a cliff, a termination and acceleration, and what is it worth above the strike?                   |
| `waterfall` | A company is sold. Who gets what, with preferences paid by rank and each preferred class choosing to convert or not?                                    |

## Install

In Claude Code, as a plugin (the agent skill and the MCP server, started with [`uvx`](https://docs.astral.sh/uv/)):

```
/plugin install equity-calculator --marketplace BwL1289/ai-vc-skills
```

On Claude Code before 2.1.275, add the marketplace first: `/plugin marketplace add BwL1289/ai-vc-skills`, then
`/plugin install equity-calculator@ai-vc-skills`.

As a Python package, Python 3.12 or later. From GitHub, with the MCP server:

```
pip install "equity_calculator[mcp] @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
```

Or from a clone:

```
git clone https://github.com/BwL1289/ai-vc-skills
cd ai-vc-skills/equity_calculator
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e '.[mcp,dev]'
```

The `mcp` extra adds the MCP server and `dev` adds the test tools; leave both out for the command and the library
alone, which need only Pydantic and openpyxl.

## Quick start

```
equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10
Investor test (Paul Graham, "The Equity Equation"): is the stake worth what the deal adds?
  Line                          Value  How it is computed
  Equity sold (n)             7.0000%  given
  Outcome multiplier (m)    1.100000x  given
  Value ratio R             1.023000x  (1 - n)·m: what the holders keep vs. before
  Break-even multiplier m*  1.075269x  1/(1 - n)
  Break-even growth g*        7.5269%  n/(1 - n) = m* - 1
  Verdict                      accept  accept: R > 1; break_even: R = 1; reject: R < 1
Assumptions:
  - outcome_multiplier = the deal's whole effect: m is the deal's whole effect on the company's average outcome, the investor's cash included; a round that adds only its cash at a fair price has m = (V + I)/V = 1/(1 - n) and breaks even. Source: Paul Graham, "The Equity Equation", paulgraham.com/equity.html (July 2007): "improves your average outcome enough that the (100 - n)% you have left is worth more than the whole company was before".
  - break_even_verdict = R = 1 is break even, not accept: Accept needs R > 1 strictly; R exactly 1 is its own verdict. Source: Paul Graham, "The Equity Equation", paulgraham.com/equity.html (July 2007): "if the company merely breaks even on the deal, there's no reason to do it" (said of hires; the same test).
```

Add `--json` for the whole result as JSON (every number as its exact fraction and its rounded value) or
`--xlsx investor.xlsx` to write the workbook as well. `equity_calculator --help` lists the scenarios and
`equity_calculator <scenario> --help` their flags; [Using it](#using-it) below has them all. From Python:

```python
from decimal import Decimal

from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import InvestorInput

result = compute(InvestorInput(equity_percent=Decimal("7"), outcome_multiplier=Decimal("1.10")))
print(result.verdict, result.value_ratio.exact)  # accept 1023/1000
```

## MCP server

`equity_calculator_mcp` serves the calculator over MCP on stdio, so an AI assistant can work a scenario exactly
instead of doing the arithmetic itself.

| Tool                                                                                                                         | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `equity_investor`, `equity_employee`, `equity_pool`, `equity_round`, `equity_dilution`, `equity_vesting`, `equity_waterfall` | One per scenario, read-only. It takes one argument, `inputs`, holding that scenario's fields (the names `--json` shows under `inputs`), and returns exactly the text `equity_calculator <scenario> --json` prints.                                                                                                                                                                                                                                                                                                                                                  |
| `equity_workbook`                                                                                                            | Only when the server runs with `--output-dir DIR`. It works any scenario (`inputs` with its `scenario` tag) and writes the workbook as a new `.xlsx` file in DIR. `file_name` must be a bare name with no control, format or surrogate character; a name that would land outside DIR, an existing file and a link are refused, and so is an answer too large for a workbook cell (no file is made). While saving, the Excel library also writes and deletes a short-lived file in the system's temporary folder (`TMPDIR` if set), so that folder must be writable. |

An input the model refuses, or a valid one with no answer (a round with no positive price, say), comes back as a tool
error that says why. Money and percents are best sent as JSON strings (`"7"`, `"1.10"`, `"8000000"`): a JSON number
with a decimal point reaches the server as a binary float, which keeps about 15 digits. Without `--output-dir` the
server writes nothing at all, and its own code never reads the network or a database. From the environment that code
takes only `HOME`, to expand a leading `~` in `--output-dir`. The MCP SDK under it (`mcp` 1.28.1) also reads `FASTMCP_*`
variables, in any letter case, and a `.env` file in the folder the server starts in. No value there changes this
server's settings, but three things stop it at start-up: a `.env` the server has no permission to read, or that is not
valid text in the system's encoding (UTF-8 on most systems); any value of `FASTMCP_DEPENDENCIES` that is not valid
JSON, an empty one included; and a non-empty value that is not valid JSON (a bare word, say) in
`FASTMCP_TRANSPORT_SECURITY__ALLOWED_HOSTS` or `FASTMCP_TRANSPORT_SECURITY__ALLOWED_ORIGINS`.

In Claude Code:

```
claude mcp add equity_calculator -- equity_calculator_mcp
claude mcp add equity_calculator -- equity_calculator_mcp --output-dir ~/equity-workbooks
```

The second form adds the workbook tool. In a client that reads an `mcpServers` file, such as Claude Desktop:

```json
{
  "mcpServers": {
    "equity_calculator": {
      "command": "equity_calculator_mcp",
      "args": ["--output-dir", "/path/to/equity-workbooks"]
    }
  }
}
```

Leave out `args` for a server that writes nothing. If the client cannot find `equity_calculator_mcp`, give the full
path to it: it is in the `bin` folder of the environment it was installed into (`which equity_calculator_mcp`).

## Agent skill

[`skills/equity-calculator/SKILL.md`](skills/equity-calculator/SKILL.md) is an agent skill: it tells an assistant
which scenario answers which question, how to run it with the command or the MCP tools, the formulas and their
sources, and to quote the labelled assumptions with every answer. In Claude Code, copy the folder to
`~/.claude/skills/` (every project) or to a project's `.claude/skills/`. The skill alone keeps a hyphen,
`equity-calculator`, in its name and folder: the Agent Skills format allows only lowercase letters, digits and
hyphens in a skill's name, and the folder must carry the same name.

## Sources

- **PG**: Paul Graham, ["The Equity Equation"](https://paulgraham.com/equity.html), July 2007. Source of the
  investor test, the employee formula, the salary rule of thumb, and the dilution step: each round leaves "the
  (100 - n)% you have left".
- **Altman**: Sam Altman, ["Employee Equity"](https://blog.samaltman.com/employee-equity), 18 April 2014. Grants are
  measured as "what percentage of the fully-diluted shares", which is the basis the pool scenario prices on, and
  "The standard at startups is 4 years with a 1-year cliff", the vesting scenario's default schedule.
- **YC**: Y Combinator's three current post-money SAFE forms (valuation cap; discount; MFN), from
  [ycombinator.com/documents](https://www.ycombinator.com/documents), downloaded as Word files and read on
  18 November 2026. The SAFE rules below (Company Capitalization, the Safe Price, the "greater of" conversion, the
  Discount Price, MFN) are quoted from them word for word in each result's assumptions. YC has no current form with
  both a cap and a discount, so the rule for a SAFE with both (the lower price wins) is marked unverified. YC's
  Post-Money Safe User Guide (version 1.2, February 2023) works a round's price per share in an example: the
  pre-money valuation over the fully diluted shares after the SAFEs convert plus the pool increase.
- **Pre-money SAFEs are not supported.** YC's page has no current pre-money SAFE form; the user guide works one
  pre-money Safe Price only as an example, not as a form's definitions, so they are left out.
- **Unverified**: neither essay covers option pools, convertible notes, preferred stock or the finer vesting terms,
  and YC's forms do not fix a round's own terms. The pool rules, notes in the round's price, every note convention
  (cap basis, interest, day count, rounding), every waterfall term (ranks, 1:1 conversion, participation, caps), and
  the vesting conventions past Altman's schedule (monthly steps, termination, acceleration, intrinsic value) are
  standard arithmetic, and each result marks them `unverified` in its assumptions.

## The formulas

<details>
<summary>Every formula, with its sources and what no source settles</summary>

### Investor test (PG)

PG's test is that you should trade n of the company "if what you trade it for improves your average outcome enough that
the (100 - n)% you have left is worth more than the whole company was before".

| Symbol                    | Meaning                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------ |
| n                         | the stake sold, a fraction (7% is 0.07)                                                                |
| m                         | what the deal multiplies the company's average outcome by, the investor's cash included (1.10 is +10%) |
| R = (1 - n)·m             | what the holders keep, measured against the whole company before                                       |
| m\* = 1/(1 - n)           | the break-even multiplier                                                                              |
| g\* = n/(1 - n) = m\* - 1 | the break-even growth                                                                                  |

The verdict is **accept** when R > 1, **break_even** when R = 1, and **reject** when R < 1. From amounts, the stake is
n = I/(V + I), where V is the pre-money valuation and I the investment. If you give a holder's stake h, the holder
owns h(1 - n) after the round. Their value goes from h·V to h(1 - n)·m·V, so R > 1 exactly when the holder ends up
richer; the tests check this on random inputs.

### Employee test (PG)

If i is the company's average outcome with the hire, the hire is worth n = (i - 1)/i (PG: "Which means n = (i -
1)/i"), and the inverse is i = 1/(1 - n). A hire with i < 1 lowers the outcome and gets the verdict **no_grant**, a
verdict rather than an error. When i = 1 the verdict is **break_even**, and when i > 1 it is **grant**.

PG's rule of thumb for an offer, labelled as a rule of thumb in every output, only runs when you give `--annual-cost`
and `--valuation`:

| Line                     | Formula                                                                |
| ------------------------ | ---------------------------------------------------------------------- |
| stock cost of the salary | annual cost × cost years (PG: "multiply the annual rate by about 1.5") |
| stake the salary costs   | stock cost / valuation                                                 |
| retail stake             | n/(1 + margin) (PG's 50% "profit" is "subtract a third")               |
| offer                    | retail stake - stake the salary costs, floored at 0                    |

### Option-pool shuffle (unverified arithmetic)

| Symbol        | Meaning                                                                                                                                  |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| FD            | every share before the round, the unissued pool included                                                                                 |
| U             | the unissued pool before the round                                                                                                       |
| V, I          | pre-money valuation, investment                                                                                                          |
| t             | the target: the unissued pool's share of the fully diluted shares after the round                                                        |
| r = I/(V + I) | the investment's share of V + I: the investor's stake after the round with the pool in the pre-money (less with the pool added after it) |

**Pool in the pre-money** (the usual term sheet, and the default):

- P = (t·FD - (1 - r)·U)/(1 - r - t) new pool shares.
- p = (V - t(V + I))/(FD - U), which equals V/(FD + P).
- If P ≤ 0, the unissued pool already meets the target, so P = 0 and p = V/FD.

**Pool in the post-money**: p = V/FD and P = max(0, (t(FD + N) - U)/(1 - t)).

In both cases the investor gets N = I/p shares and the total is T = FD + P + N. Post-money is T·p. The effective
pre-money, (FD - U)·p, is what the existing holders' shares are worth at the round price. With the pool in the
pre-money, that comes to V - t(V + I): the new pool is paid for out of the holders' valuation. A target with
t ≥ 1 - r, and any denominator that is not positive, is refused with a message naming the flags.

Both pool timings are always computed side by side. `--pool-timing` only picks which one is "this deal".

### SAFEs and notes in a priced round (YC for the SAFE rules; the rest unverified)

The round takes the pool scenario's FD, U, V, I and t, plus up to 50 SAFEs and notes. Each one converts an amount a:
a SAFE's purchase amount, or a note's principal plus its accrued interest (the principal alone with
`interest-paid-in-cash`). K is its valuation cap and d its discount (0 when it has none).

Each instrument converts at the lower of two prices, which is the greater number of shares (YC: "convert into the
greater of"):

- its **cap price**: K/C for a SAFE, where C is the Company Capitalization (YC: the Safe Price "equal to the
  Post-Money Valuation Cap divided by the Company Capitalization"); K/FD for a note, whose cap is taken as a pre-money
  cap on the pre-round shares (unverified: notes have no standard form);
- its **other price**: the round price times 1 - d (YC: the Discount Price), or the round price itself with no
  discount.

A SAFE needs a cap or a discount, unless it is MFN. An MFN SAFE converts on the terms it is given (the ones it took
from a later instrument); with neither it converts at the round price. Which later instrument's terms it may take is
not worked out here.

C counts every pre-round share (FD, the unissued pool included) and every converting share, but not the pool
increase made for the round (YC: "any increase to the Unissued Option Pool in connection with the Equity Financing
will only be included to the extent that the number of Promised Options exceeds the Unissued Option Pool"; no
options are taken as promised beyond the old pool). With each capped instrument placed on its cap or its other
price, three sums describe the conversions:

| Symbol                         | Meaning                                                                |
| ------------------------------ | ---------------------------------------------------------------------- |
| sigma = Σ a/K                  | over the SAFEs on their cap: their share of C (each gets a·C/K shares) |
| F = Σ a·FD/K                   | over the notes on their cap: their shares                              |
| D = Σ a/(1 - d)                | over every instrument at its other price: their shares are D/p         |
| C = (FD + F + D/p)/(1 - sigma) | the Company Capitalization                                             |

The pre-money valuation buys every pre-round share, every converted share and, with the pool in the pre-money, the
new pool (for SAFEs, the worked example in YC's Post-Money Safe User Guide; notes converting the same way are
unverified). That gives the round price p:

- **Pool in the pre-money** (the default): p = (V - t(V + I) - D/(1 - sigma)) / ((FD + F)/(1 - sigma) - U) and
  P = t(V + I)/p - U. If P ≤ 0, the unissued pool already meets the target, so P = 0 and
  p = (V(1 - sigma) - D)/(FD + F).
- **Pool in the post-money**: p = (V(1 - sigma) - D)/(FD + F) and P = max(0, (t(C + N) - U)/(1 - t)).

The investor gets N = I/p shares, the total is T = C + P + N, and post-money is T·p. Which price each instrument
takes depends on p, and p on which price each takes. So the search starts with every capped instrument on its cap,
prices the round, and keeps an instrument on its cap exactly when its cap price is at most its other price (a tie
takes the cap; the shares are the same either way), until a pass changes nothing. It takes at most one pass more
than there are capped instruments. A round that has not settled by then is refused rather than guessed.

The round is also refused, with a message naming the flag or instrument, when: a SAFE has neither cap nor discount
(and is not MFN); a SAFE's purchase amount is not below its cap; U is not below FD; t is not below V/(V + I) (the
new pool would take the whole pre-money valuation); the capped SAFEs' Σ a/K reaches 1; the instruments converting off their cap take the whole
pre-money valuation (no positive price); or a note gives both or neither of `months-outstanding` and the two dates.

### Note interest (unverified)

With P the principal, r the yearly rate and y the years outstanding (months/12, or the actual days between the issue
and conversion dates over 365, or 360 with `day-count=actual_360`):

| Terms                                                                                                            | Amount owed                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `compounding=annual` (n = 1, the default) or `monthly` (n = 12), with `stub-rule=fractional_power` (the default) | P(1 + r/n)^(w + s): the growth raised to the fractional number of periods, w whole periods and the stub s (the part of a period left) |
| the same with `stub-rule=simple`                                                                                 | P(1 + r/n)^w·(1 + (r/n)·s): the w whole periods compound, the stub earns simple interest                                              |
| `compounding=simple`                                                                                             | P(1 + r·y)                                                                                                                            |

The amount owed is rounded to the cent, half-even, before it converts. A fractional power has no exact rational
value, so it is computed in a private 50-digit decimal context and marked approximate: a note that names neither term
and has a stub left over (18 months, say) is approximate by default. A note that ran a whole number of periods (24
months, yearly or monthly) has no stub, s = 0: both rules then give the exact P(1 + r/n)^w, and nothing is marked
approximate.

### Dilution through rounds (PG; the pool term unverified)

A holder who owns `h_0` keeps, after each round k, `h_k = h_(k-1)·(1 - n_k - p_k)`. `n_k` is the stake the round sells
(given, or n = I/(V + I) from its pre-money and investment) and `p_k` the new pool's share after the round. The holder
buys nothing in any round. Each round must leave something, n + p < 100%. The result shows each round's stake kept, the
stake after, the stake lost, the stake lost in all, the final stake, and the share of the first stake kept.

### Vesting (Altman's schedule; the rest unverified)

A grant of G shares vests over T months (48 by default) with a cliff (12 months by default). At month m, with e the
termination month (if any) and s = min(m, e) the months served:

- on schedule: 0 when s is below the cliff, else G·min(s, T)/T;
- acceleration vests a percent of what is still unvested (or of the whole grant, with `--acceleration-base grant`)
  at the month it fires. `single_trigger` fires at the change of control, when the holder was not terminated before
  it; `double_trigger` fires at the termination, when that is at or after the change of control. The accelerated
  shares come off the end of the schedule, so vested = min(G, on schedule + accelerated);
- a termination stops vesting, and the unvested shares are forfeited;
- with `--strike-price`, the exercise cost is vested × strike; with `--common-price` too, the spread is
  max(0, common - strike) and the intrinsic value is vested × spread. The common price against the strike is shown
  as **in_the_money**, **at_the_money** or **underwater**.

`--share-rounding whole_shares` rounds the vested count down to a whole share.

### Exit waterfall (unverified)

E is what the shareholders share at the exit (nothing is taken out ahead of them). Each preferred class has shares,
an amount invested, a preference multiple (1 by default), a rank (1 is paid first; 1 by default) and a participation
(`none` by default, `full` or `capped`).

1. Each class that stays owed its preference, multiple × invested. Ranks are paid most senior first, and a rank
   short of money is paid pro rata to what each class in it is owed.
2. The rest R is shared per share among the common shares, the classes that converted (one common share for each
   preferred share) and the participating classes. A `capped` class stops at cap-multiple × invested, its preference
   included; what it would have taken past its cap is shared among the others.
3. Each class converts exactly when that pays it strictly more than staying, the other classes' choices held fixed;
   a tie stays and keeps its preference. The search starts with no class converting and visits the classes in the
   order given; it stops after a pass that changes nothing, at most one pass more than there are classes. A
   waterfall that has not settled by then is refused rather than guessed. When terms allow more than one settled
   set of choices, this is the one the search reaches first; the tests compare it with every one of the 2^k sets.

The money is rounded to the cent by largest remainder, so the payouts add up to E exactly.

</details>

## Worked examples

**PG's YC example.** Selling 7% for a 10% better outcome:

```
equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10
  Value ratio R             1.023000x  (1 - n)·m: what the holders keep vs. before
  Break-even multiplier m*  1.075269x  1/(1 - n)
  Break-even growth g*        7.5269%  n/(1 - n) = m* - 1
  Verdict                      accept  accept: R > 1; break_even: R = 1; reject: R < 1
```

At m = 1.05 it is a reject. Selling 50% for m = 2 breaks even. PG's Sequoia example (30%, "1/.7 = 1.43") accepts at
m = 1.43 and rejects at m = 1.428.

**PG's hire.** A hire who adds 20%, costs $60k a year and joins at a $2M valuation, with a 50% margin:

```
equity_calculator employee --gain-percent 20 --annual-cost 60000 --valuation 2000000 --margin-percent 50
  Break-even stake n                             16.6667%  (i - 1)/i, floored at 0
  Stake the salary costs                          4.5000%  stock cost / valuation
  Retail stake                                   11.1111%  n/(1 + margin)
  Rule-of-thumb offer                             6.6111%  retail - salary's stake, floored at 0
```

PG's own numbers are 16.7%, 4.5%, 11.1% and "an offer of 6.6%".

**The pool shuffle.** 10M fully diluted shares, 0.5M of them unissued pool, an $8M pre-money, $2M invested and a 10%
target:

|                           | Pool in the pre-money | Pool in the post-money |
| ------------------------- | --------------------- | ---------------------- |
| New pool shares P         | 857,142.857           | 833,333.333            |
| Price per share p         | $0.736842             | $0.800000              |
| Investor's shares N       | 2,714,285.714         | 2,500,000              |
| Holders / pool / investor | 70% / 10% / 20%       | 71.25% / 10% / 18.75%  |
| Effective pre-money       | $7,000,000            | $7,600,000             |

With 2M of the 10M already unissued, the pool meets the target without new shares. Then P = 0, p = $0.80, N = 2.5M and
T = 12.5M, so the holders own 64%, the pool 16% and the investor 20%.

**Two SAFEs in a priced round.** 10M fully diluted shares (0.5M unissued pool), a $16M pre-money, $4M invested, a 10%
pool target in the pre-money, and two SAFEs: $500k on a $5M cap and $1M on a $10M cap:

```
equity_calculator round --fully-diluted-shares 10000000 --unissued-pool-shares 500000 --pre-money 16000000 \
    --investment 4000000 --target-pool-percent 10 \
    --safe "500000 valuation-cap=5000000" --safe "1000000 valuation-cap=10000000"
```

sigma = 0.5/5 + 1/10 = 20%, so C = 10M/0.8 = 12.5M. The SAFEs convert at $0.40 and $0.80, 1,250,000 shares each.
p = (16M - 0.1·20M)/(12.5M - 0.5M) = $1.166667, P = 1,214,285.714 and N = 3,428,571.429, so T = 17,142,857.143 and
post-money is $20,000,000.00. One pass settles it.

| Holder            | Shares        | Ownership | Value at p     |
| ----------------- | ------------- | --------- | -------------- |
| Existing holders  | 9,500,000     | 55.4167%  | $11,083,333.34 |
| SAFE 1 ($5M cap)  | 1,250,000     | 7.2917%   | $1,458,333.33  |
| SAFE 2 ($10M cap) | 1,250,000     | 7.2917%   | $1,458,333.33  |
| Option pool       | 1,714,285.714 | 10.0000%  | $2,000,000.00  |
| Investor          | 3,428,571.429 | 20.0000%  | $4,000,000.00  |

Give SAFE 2 a $40M cap and a 20% discount instead (`--safe "1000000 valuation-cap=40000000 discount-percent=20"`):
its cap price, $3.257399, is above its discount price, $0.950785, so it converts at the discount. That takes 2 passes
and gives p = $1.188482, SAFE 1 7.2971% and SAFE 2 6.2500%.

**A note.** 10M fully diluted shares (no pool), a $10M pre-money, $2M invested, no pool target, and a $500k note at
8% for 18 months with a $6M cap (`--note "500000 interest-rate-percent=8 months-outstanding=18
valuation-cap=6000000"`). It names neither term, so it compounds yearly with a fractional-power stub: it owes
500,000·1.08^1.5 = $561,184.46 (marked approximate), $61,184.46 of interest, which converts at the cap price
$6M/10M = $0.60: 935,307.433 shares. C = 10,935,307.433 and p = $0.914469. The existing holders own 76.2058%, the
note 7.1276% and the investor 16.6667%. The same note with `stub-rule=simple` owes $561,600.00 (a year compounded,
the half-year stub simple), with `compounding=simple` $560,000.00 ($60,000 of simple interest), and with
`compounding=monthly` $563,523.97 (18 whole months, so exact).

**Dilution.** A holder with 50% through three rounds, each `investor-percent` / `pool-percent`: 20/10, 20/5, 15/0:

| Round | Stake kept (1 - n - p) | Stake after | Stake lost |
| ----- | ---------------------- | ----------- | ---------- |
| 1     | 70%                    | 35.0000%    | 15.0000%   |
| 2     | 75%                    | 26.2500%    | 8.7500%    |
| 3     | 85%                    | 22.3125%    | 3.9375%    |

The stake lost in all is 27.6875%, and 44.6250% of the first stake is kept.

**Vesting.** A 48,000-share grant on the default 4 years with a 1-year cliff has nothing vested at month 11, 12,000
at month 12 and 30,000 at month 30. At month 30 with a $0.50 strike and $2 common, exercising costs $15,000.00, the
spread is $1.50 and the intrinsic value is $45,000.00: **in_the_money**. A single trigger of 50% at a change of
control in month 24 adds 12,000 (half of the 24,000 unvested then), so 36,000 (75%) are vested at month 24. A double
trigger of 100% with a termination in month 24, after a change of control in month 20, vests all 48,000.

**The waterfall.** 7M common shares; class A has 2M shares and $5M invested, class B 1M shares and $10M invested,
both 1x non-participating:

| Exit, terms                    | A                                           | B                                | Common         | Passes |
| ------------------------------ | ------------------------------------------- | -------------------------------- | -------------- | ------ |
| $50M, one rank                 | converts: $8,888,888.89 ($4.444444 a share) | stays: $10,000,000.00            | $31,111,111.11 | 2      |
| $12M, B at rank 1, A at rank 2 | stays: $2,000,000.00                        | stays: $10,000,000.00            | $0.00          | 1      |
| $40M, A capped at 3x           | stays: $10,555,555.56                       | stays: $10,000,000.00            | $19,444,444.44 | 1      |
| $70M, A capped at 3x           | stays at its cap: $15,000,000.00            | stays: $10,000,000.00            | $45,000,000.00 | 1      |
| $100M, A capped at 3x          | converts: $20,000,000.00                    | ties at $10,000,000.00 and stays | $70,000,000.00 | 2      |

## Using it

```
equity_calculator investor (--equity-percent N | --pre-money V --investment I)
    (--outcome-multiplier M | --growth-percent G) [--holder-percent H]
equity_calculator employee (--outcome-multiplier I | --gain-percent G) [--offered-percent O]
    [--annual-cost C --valuation V] [--margin-percent M] [--cost-years Y]
equity_calculator pool --fully-diluted-shares FD [--unissued-pool-shares U] --pre-money V --investment I
    --target-pool-percent T [--pool-timing pre_money|post_money] [--share-rounding exact|whole_shares]
equity_calculator round --fully-diluted-shares FD [--unissued-pool-shares U] --pre-money V --investment I
    [--target-pool-percent T] [--pool-timing pre_money|post_money] [--safe "TERMS"]... [--note "TERMS"]...
equity_calculator dilution --holder-percent H --round "TERMS"...
equity_calculator vesting --grant-shares G [--total-months T] [--cliff-months C] --month M
    [--strike-price S] [--common-price P] [--termination-month E]
    [--acceleration none|single_trigger|double_trigger] [--acceleration-percent A]
    [--acceleration-base unvested|grant] [--change-of-control-month M] [--share-rounding exact|whole_shares]
equity_calculator waterfall --exit-amount E --common-shares S --class "TERMS"...
```

`round` needs at least one `--safe` or `--note`, `dilution` at least one `--round` and `waterfall` at least one
`--class`. Each repeated flag is one instrument, round or class, given as one quoted string of `key=value` terms and
bare flags in any order, after the amount for a SAFE or the principal for a note, which comes first:

| Flag      | Terms                                                                                                                                                                                                                                                                                       |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--safe`  | `AMOUNT [valuation-cap=X] [discount-percent=D] [mfn]`                                                                                                                                                                                                                                       |
| `--note`  | `PRINCIPAL interest-rate-percent=R (months-outstanding=M \| issue-date=YYYY-MM-DD conversion-date=YYYY-MM-DD) [compounding=simple\|annual\|monthly] [stub-rule=simple\|fractional_power] [day-count=actual_365\|actual_360] [valuation-cap=X] [discount-percent=D] [interest-paid-in-cash]` |
| `--round` | `(investor-percent=N \| pre-money=V investment=I) [pool-percent=P]`                                                                                                                                                                                                                         |
| `--class` | `shares=S invested=I [preference-multiple=M] [rank=K] [participation=none\|full\|capped] [cap-multiple=C]` (a cap only with `capped`)                                                                                                                                                       |

A note that names no `compounding` compounds `annual`, and one that names no `stub-rule` uses `fractional_power`.
An unknown term, a term given twice, or a value that is not a number is refused, naming the flag.

Every scenario also takes `--json`, which prints the whole result model instead of the report, and `--xlsx PATH`,
which also writes the workbook. Numbers may carry `$`, `_` and commas that separate thousands (`$8,000,000`): one to
three digits, not starting with 0, then groups of exactly three. A comma in that place is always read as thousands, so
`1,250` is 1250 and `1,050` is 1050, even where a decimal comma was meant: nothing can tell the two apart. Any other
comma, such as `7,5`, `0,500` or `8,00,000`, is refused rather than read as a bigger number. A percent may carry `%`.
A negative percent with `%` needs `=`, as in `--growth-percent=-10%`, because argparse reads a lone `-10%` as a flag;
`--growth-percent -10` works as it is.

Spaces around a number are trimmed, and `$` and `_` are dropped wherever they appear, so `7_000_000` is 7000000.
Full-width digits (`５０`) and Arabic-Indic digits (`٥٠`) are read as the digits they are, the same way Python reads
them. The comma rule holds in every script: a first group that starts with a full-width or Arabic-Indic zero, such as
`０,５００`, is refused like `0,500`.

The exit code is 0 on success. It is 1 when the inputs are refused, with each reason on its own line naming the flag:
a value out of range, or a missing either-or choice such as `investor --equity-percent 7` with no multiplier, or
`--annual-cost` without `--valuation`. A number outside the limits below is refused the same way
(`--pre-money: a nonzero number here is at least 1e-15 and under 1e16 in size (got 1E+999999999)`). It is also 1 when
valid inputs have no answer, with a plain message: a round with no positive price (`the SAFEs and notes converting off
their cap take the whole pre-money valuation: no positive price`), a round whose conversions do not settle, or a
waterfall whose choices do not settle. It is 1 too when the `--xlsx` file cannot be written, or when the answer
holds a value of 1e300 or more in size, too large for a workbook cell (`--xlsx: the answer holds a value of 1E+300 or
more in size, ...`); no file or folder is written then. The printed report and `--json` do not check that size
(see Limits). It is 2 when argparse
rejects an argument: not a number, a comma that does not separate thousands, number text over 100 characters, a term
string it cannot read, or a flag argparse itself requires, such as `pool` without `--pre-money`.

The command's own code reads no network, database or environment variable (Python's standard library reads a
few, such as `COLUMNS` to wrap the help, none of which changes a number). Its one output file is `--xlsx`, and it
creates any folders on its path that do not exist yet; while saving, the Excel library also writes and deletes a
short-lived file in the system's temporary folder (`TMPDIR` if set), so that folder must be writable.
From Python, `equity_calculator.scenarios.compute(inputs)` takes any
`equity_calculator.schemas.equity` input model and returns its result. On valid inputs with no answer it raises an
`equity_calculator.errors.EquityComputeError` (a `ValueError`): `RoundHasNoPrice`, `ConversionDidNotSettle` or
`NoConversionEquilibrium`. `equity_calculator.result_range.check_result_range(result)` raises `ResultOutOfRange`, another
`EquityComputeError`, when any value in a result is 1e300 or more in size.

In JSON, every quantity is `{"unit", "exact", "rounded"}`. `exact` is the exact fraction as `"a/b"` (a whole number
as `"a"`) and `rounded` is the display value as a decimal string.

## Limits

Every decimal input has at most 28 significant digits, trailing zeros included, and a nonzero value at least 1e-15
and under 1e16 in size. A share count is a whole number below 1e16. Number text is at most 100 characters. A round takes at
most 50 SAFEs and notes, a dilution at most 20 rounds, and a waterfall at most 12 preferred classes, ranked 1 to 12.
A note runs at most 600 months, or at most 18,262 days (about 50 years) between its dates; a vesting schedule, its
cliff and every month asked about are at most 600 months. These limits keep every exact step small: the largest
inputs compute in well under a second, and a value like `1e999999999` is refused at once instead of tying up the
process.

Bounded inputs can still give an enormous answer. SAFEs whose discounted amounts use up all but a sliver of the
pre-money leave a price per share near zero: with nine such SAFEs the largest values reach about 1.8e321 to 3.9e322
(by how they are set), past Excel's largest number (9.99999999999999E+307), where openpyxl would write a blank cell
that an `=SUM` reads as zero. So no value of 1e300 or more in size
(`equity_calculator.result_range.RESULT_LIMIT`) reaches a workbook: the workbook writer refuses such an answer, so
`--xlsx` and the MCP server's `equity_workbook` tool make no file. The printed report, `--json` and the MCP scenario
tools do not check it.

## The Excel workbook

There is one sheet per scenario (`Investor`, `Employee`, `Pool`, `Convertibles` for the round, `Dilution`, `Vesting`
or `Waterfall`):

- Row 1 is a bold header, frozen in place: `Line`, one value column (two for the pool, one per timing) and
  `How it is computed`.
- Every value cell holds the model's display rounding as a number, under its unit's format (a live investor
  sheet's inputs excepted, below). Fractions use `0.00%`,
  money `"$"#,##0`, a price per share `"$"#,##0.000000`, shares `#,##0` and multipliers `0.0000"x"`.
- The investor sheet is live: its inputs (the stake, or the pre-money and the investment; the outcome multiplier; a
  holder's stake) are numbers held at full precision, with the display format doing the rounding, and every line
  worked from them is a formula over those cells: the stake from the amounts `I/(V + I)`, R `(1 - n)·m`, m\*
  `1/(1 - n)`, g\* `n/(1 - n)`, the holder's stake after and dollar values, and the verdict,
  `=IF(ROUND(R-1,12)>0,"accept",IF(ROUND(R-1,12)=0,"break_even","reject"))`. Change the multiplier from 1.10 to 1.05
  on a 7% stake and the verdict turns from a green accept to a red reject.
- A spreadsheet works those formulas in binary floating point. Rounding R - 1 to 12 places keeps an exact break even
  reading break even. Before writing the sheet, the calculator works the same formulas the same way and keeps them only
  when every number lands within the display rounding of the exact answer and the verdict is the model's. When it
  does not (an R within 10^-11 of 1 without being 1, or a stake so close to 100% that 1 - n loses its digits), the
  sheet holds the model's values instead, as the other sheets do. The tests check both kinds of sheet, on break-even
  cases and on seeded random inputs.
- Formula cells are worked out by the spreadsheet when it opens the file (Excel and LibreOffice do); a viewer that
  does not calculate, such as a file preview or openpyxl's `data_only` read, shows them empty.
- Totals are live `=SUM` formulas, so editing a part re-totals: the investor's post-money, total shares, total
  ownership and post-money (pool and round), the stake lost in all (dilution), vested in all and the grant (vesting), and the total paid out
  (waterfall). A live total adds the rounded cells, so it can differ from the model's exact total in the last place
  kept: a cent on the investor's post-money, a thousandth of a share on the pool's total shares, 0.000001 on its total
  ownership. The number formats hide that difference.
- The pool's and the round's value rows, and the waterfall's payouts, are rounded to the cent by largest remainder,
  so they add up to their rounded total exactly.
- Verdict cells are coloured by conditional formatting: green for accept, grant and in the money, amber for break
  even and at the money, red for reject, no grant and underwater. A waterfall choice is blue when the class converts
  and grey when it stays: neither is good or bad. The investor verdict recolours itself when an input changes;
  elsewhere, typing a different verdict recolours the cell.
- The assumptions follow two rows below, under their own bold header: `Assumption`, `Setting`, `Statement` and
  `Source`.
- Column widths are set so labels and formulas are readable without resizing.

## Exactness

Inside, every number is a `Fraction`. Inputs arrive as `Decimal` (the models refuse NaN and infinity, and hold every
number to the limits above) and share counts as plain integers (a bool, a float or a numeric string is refused, never
read as a count). The output carries both the exact fraction and a `Decimal` rounded half-even at a fixed number of
places: 6 places for ratios and prices, 2 for money, 3 for shares. Rounding is integer arithmetic. No step reads or
sets the global decimal context, so a caller's `decimal.localcontext()` cannot change a result, and the note stub's
private context sets every field, so a changed `decimal.DefaultContext` cannot either.

One step is not exact: a note with `stub-rule=fractional_power` (the default) and a stub left over raises its growth
to a fractional power, which has no exact rational value. It is computed in a private 50-digit decimal context, then
rounded to the cent like every note's amount, and its assumption says it is approximate. A note with
`stub-rule=simple` or `compounding=simple` stays exact, and one that ran a whole number of periods has no stub, so it
compounds exactly under either stub rule.

Each number shown is its own exact value rounded once. So rounded parts can miss a rounded total by one in the last
place shown: in the report, a thousandth of a share or 0.0001% beside a total line. The pool's and the round's value
rows and the waterfall's payouts are the exception, split to the cent by largest remainder.

## Assumptions

<details>
<summary>Every assumption a result can list, with its sources</summary>

Every result lists the assumptions it rests on, with the setting it used and its source. They appear in the report,
in the JSON and in the workbook.

| Key                  | Default                                                        | How to change it                                      | Source                                     |
| -------------------- | -------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------ |
| `outcome_multiplier` | m is the deal's whole effect, cash included                    | fixed (the definition of m)                           | PG                                         |
| `break_even_verdict` | R = 1 is break even, not accept                                | fixed                                                 | PG ("no reason to do it")                  |
| `stake_from_amounts` | n = I/(V + I)                                                  | give `--equity-percent` instead                       | unverified                                 |
| `holder_value`       | value before = h·V (shown with `--holder-percent` and amounts) | fixed                                                 | unverified                                 |
| `grant_rule`         | i ≤ 1 grants nothing; the stake is floored at 0                | fixed                                                 | PG                                         |
| `cost_years`         | 1.5                                                            | `--cost-years`                                        | PG                                         |
| `valuation`          | the valuation given                                            | `--valuation` (PG suggests the last post-money)       | PG, note 2                                 |
| `margin`             | 0%                                                             | `--margin-percent` (PG's example uses 50)             | PG                                         |
| `offer_floor`        | an offer below 0 is shown as 0, flagged                        | fixed                                                 | unverified                                 |
| `pool_timing`        | `pre_money`                                                    | `--pool-timing post_money` (both are always computed) | unverified                                 |
| `target_pool`        | unissued pool after the round                                  | fixed                                                 | unverified                                 |
| `price_basis`        | fully diluted                                                  | fixed                                                 | unverified; Altman's fully-diluted measure |
| `share_rounding`     | `exact` (fractional shares)                                    | `--share-rounding whole_shares`                       | unverified                                 |
| `money_split`        | largest remainder                                              | fixed                                                 | display convention                         |

With `whole_shares`, the new pool and the investor's shares are rounded down at the exact price, and the cash that
did not convert is reported. This convention is unverified: some term sheets round differently.

The `round` scenario adds these (SAFE rows only with a SAFE, the MFN row only with an MFN SAFE, note rows only with a
note); it also carries `pool_timing` (default `pre_money`, `--pool-timing post_money`) and `money_split`:

| Key                             | Default                                                                        | How to change it                | Source                                  |
| ------------------------------- | ------------------------------------------------------------------------------ | ------------------------------- | --------------------------------------- |
| `company_capitalization`        | FD + every converting share, no pool increase                                  | fixed                           | YC                                      |
| `promised_options`              | none beyond the old pool                                                       | fixed                           | unverified                              |
| `safe_price_rule`               | the lower of cap price and discount price                                      | fixed                           | YC (one term each); unverified for both |
| `mfn`                           | the terms given, else the round price                                          | give the SAFE the terms it took | YC (MFN form)                           |
| `note_cap_basis`                | a pre-money cap over FD                                                        | fixed                           | unverified                              |
| `note_interest`                 | yearly compounding with a fractional-power stub, unless the note names its own | `compounding=`, `stub-rule=`    | unverified                              |
| `day_count`                     | actual days over 365                                                           | `day-count=actual_360`          | unverified                              |
| `interest_rounding`             | to the cent, half-even                                                         | fixed                           | unverified                              |
| `interest_conversion`           | accrued interest converts                                                      | `interest-paid-in-cash`         | unverified                              |
| `converted_shares_in_pre_money` | V buys every pre-round and converted share                                     | fixed                           | YC guide's example; notes unverified    |
| `tie_rule`                      | a tie takes the cap                                                            | fixed                           | display convention                      |
| `fractional_shares`             | exact                                                                          | fixed                           | unverified                              |
| `search`                        | from every cap, at most one pass more than the capped instruments              | fixed                           | method                                  |

The `dilution` and `vesting` scenarios add these:

| Key                     | Default                                           | How to change it                   | Source                           |
| ----------------------- | ------------------------------------------------- | ---------------------------------- | -------------------------------- |
| `dilution_rule`         | `h_k = h_(k-1)·(1 - n - p)`                       | fixed                              | PG; the pool term unverified     |
| `pool_basis`            | the new pool's share after the round              | fixed                              | unverified                       |
| `no_participation`      | the holder buys nothing                           | fixed                              | unverified                       |
| `stake_from_amounts`    | n = I/(V + I) (only for a round given by amounts) | give `investor-percent=` instead   | unverified                       |
| `schedule`              | 48 months, 12-month cliff, monthly after it       | `--total-months`, `--cliff-months` | Altman; monthly steps unverified |
| `termination`           | vesting stops; the unvested shares are forfeited  | fixed                              | unverified                       |
| `share_rounding`        | `exact`                                           | `--share-rounding whole_shares`    | unverified                       |
| `acceleration_base`     | the unvested shares                               | `--acceleration-base grant`        | unverified                       |
| `acceleration_order`    | off the end of the schedule                       | fixed                              | unverified                       |
| `double_trigger_window` | any termination at or after the change of control | fixed                              | unverified                       |
| `intrinsic_value`       | vested × max(0, common - strike)                  | fixed                              | unverified                       |

The acceleration rows appear only with acceleration, and `intrinsic_value` only with a strike price: the row also says
how the exercise cost is worked, which a strike alone gives; the value itself needs a common price too. The `waterfall`
scenario adds these (participation and cap rows only when a class uses them), every one unverified, since no source
was read for preferred-stock terms:

| Key                            | Default                                                      | How to change it                  |
| ------------------------------ | ------------------------------------------------------------ | --------------------------------- |
| `exit_is_shared_amount`        | nothing ahead of the shareholders                            | give E net of anything paid first |
| `preference_order`             | rank 1 first; pro rata within a rank                         | `rank=` per class                 |
| `conversion_one_to_one`        | 1 common share per preferred share                           | fixed                             |
| `convert_when_strictly_better` | a tie stays                                                  | fixed                             |
| `best_response_search`         | from none converting, at most one pass more than the classes | fixed                             |
| `participation`                | the preference, then a per-share part of the rest            | `participation=full` or `capped`  |
| `cap_includes_preference`      | cap-multiple × invested, the preference included             | `cap-multiple=`                   |

</details>

## Tests

```
pip install -e '.[mcp,dev]'
pytest
```

The tests need no network. They work PG's examples and the worked examples in this file (each command above that
shows its output is run, and every line shown must appear in what it prints), check the formulas' properties on seeded
random inputs, compare the waterfall with every possible set of conversion choices, read the workbooks back with
openpyxl, run the command as a child process, and drive the MCP server both in process and over stdio. Apart from
pytest's cache and Python bytecode, they write only under pytest's temporary folder.

## License

MIT, see [LICENSE](LICENSE).
