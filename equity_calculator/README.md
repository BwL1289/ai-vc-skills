# Equity calculator

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-3fb950"></a>
  <img alt="Python 3.12+" src="https://img.shields.io/badge/python-3.12%2B-3776ab">
  <img alt="Claude Code plugin" src="https://img.shields.io/badge/Claude%20Code-plugin-d97757">
  <img alt="MCP server" src="https://img.shields.io/badge/MCP-server-6e7681">
</p>

The first of the [AI VC skills](../README.md).

Should we trade stock for this, and what does a round do to the cap table? Fourteen scenarios, worked with exact
arithmetic, printed as a report, as JSON, or as a formatted Excel workbook with live formulas. It comes three ways: a
command, `equity_calculator`; an MCP server, `equity_calculator_mcp`, that gives an AI assistant one tool per
scenario; and a Python package, `equity_calculator`. An agent skill in
[`skills/equity-calculator/`](../skills/equity-calculator/SKILL.md), at the repository root, tells an assistant when and
how to use it. The fourteen founder reviews in the root README's [skills table](../README.md#skills), all in preview,
take every figure they work out from these scenarios; four were built around one: `deal_check` for `vc-deal-math`,
`runway_plan` for `vc-round-sizing`, `metrics_check` for `vc-metrics-readiness` and `market_sizing` for
`vc-market-sizing`.

Built from the original `equity_equation` script this repository started with (it is in the git history, at
[`src/equity_equation/` in commit 8748071](https://github.com/BwL1289/ai-vc-skills/tree/87480719db0871c6b467a16437919d1df84055ed/src/equity_equation))
and the essay it implements. That script's own TODO
list asked for Pydantic models and cell formatting (percent, numbers); both are here, along with the employee formula
and the option-pool shuffle.

| Scenario             | The question it answers                                                                                                                                                                                                     |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `investor`           | An investor wants n of the company. Is the deal worth it, given what it does to the company's average outcome?                                                                                                              |
| `employee`           | How much of the company is a hire worth at most, and what would Paul Graham's rule of thumb offer?                                                                                                                          |
| `pool`               | A priced round asks for a bigger option pool. What is the real price per share, how many new shares are made, and who owns what afterwards?                                                                                 |
| `round`              | A priced round converts post-money SAFEs and convertible notes. At what price does each convert, what is the round price, and who owns what afterwards?                                                                     |
| `dilution`           | A holder owns h of the company. What is left after a series of rounds, each selling a stake and adding a pool?                                                                                                              |
| `vesting`            | How much of a grant has vested at a given month, with a cliff, a termination and acceleration, and what is it worth above the strike?                                                                                       |
| `waterfall`          | A company is sold. Who gets what, with preferences paid by rank and each preferred class choosing to convert or not?                                                                                                        |
| `deal_check`         | A founder's raise as a VC will read it: do the valuation, percent sold, ownership after the round and runway the deck states agree with the arithmetic?                                                                     |
| `runway_plan`        | How long does each raise last on a founder's phased plan and a downside, which milestones does it reach with time to raise the next round, and how much is needed to get there?                                             |
| `metrics_check`      | A founder's traction metrics as a VC will recompute them: do the ARR, retention, churn, CAC payback and burn multiple the deck states agree with their parts?                                                               |
| `market_sizing`      | A founder's market built bottom-up: TAM, SAM and SOM from customers and price, the deck's figures checked, a top-down cross-check, and which assumption moves it most?                                                      |
| `instrument_compare` | A founder choosing between a priced round now and a convertible note now: who owns what after today and after each next round, and who gets what at each exit, A beside B with B - A, never a pick?                         |
| `pool_plan`          | A term sheet asks for an option pool. How big a pool does the founder's hiring plan to the next round need, and what does each pool do to the price, the effective pre-money and who owns what, side by side, never a pick? |
| `raise_pipeline`     | A founder planning a raise: how much of the round is left after the lead, the firm commitments and pro rata, how many term sheets the funnel is expected to give on the founder's own rates, and when to start raising?     |

## Install

In Claude Code, as a plugin (every skill and the MCP server, started with [`uvx`](https://docs.astral.sh/uv/)):

```
/plugin install ai-vc-skills --marketplace BwL1289/ai-vc-skills
```

On Claude Code before 2.1.275, add the marketplace first: `/plugin marketplace add BwL1289/ai-vc-skills`, then
`/plugin install ai-vc-skills@ai-vc-skills`.

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

| Tool                                                                                                                                                                                                                                                                                              | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `equity_investor`, `equity_employee`, `equity_pool`, `equity_round`, `equity_dilution`, `equity_vesting`, `equity_waterfall`, `equity_deal_check`, `equity_runway_plan`, `equity_metrics_check`, `equity_market_sizing`, `equity_instrument_compare`, `equity_pool_plan`, `equity_raise_pipeline` | One per scenario, read-only. It takes one argument, `inputs`, holding that scenario's fields (the names `--json` shows under `inputs`), and returns exactly the text `equity_calculator <scenario> --json` prints.                                                                                                                                                                                                                                                                                                                                                  |
| `equity_workbook`                                                                                                                                                                                                                                                                                 | Only when the server runs with `--output-dir DIR`. It works any scenario (`inputs` with its `scenario` tag) and writes the workbook as a new `.xlsx` file in DIR. `file_name` must be a bare name with no control, format or surrogate character; a name that would land outside DIR, an existing file and a link are refused, and so is an answer too large for a workbook cell (no file is made). While saving, the Excel library also writes and deletes a short-lived file in the system's temporary folder (`TMPDIR` if set), so that folder must be writable. |

An input the model refuses, or a valid one with no answer (a round with no positive price, say), comes back as a tool
error that says why. The SDK checks the arguments itself and passes the validation library's text through
unchanged, so a list with one bad item also carries an untrue line saying the list is too short (for a market's one
segment: "Tuple should have at least 1 item after validation, not 0"); the first line names the real reason, and the
command line leaves that extra line out. Money and percents are best sent as JSON strings (`"7"`, `"1.10"`, `"8000000"`): a JSON number
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

[`skills/equity-calculator/SKILL.md`](../skills/equity-calculator/SKILL.md), at the repository root, is an agent skill: it tells an assistant
which scenario answers which question, how to run it with the command or the MCP tools, the formulas and their
sources, and to quote the labelled assumptions with every answer. In Claude Code, copy the folder to
`~/.claude/skills/` (every project) or to a project's `.claude/skills/`. The skill alone keeps a hyphen,
`equity-calculator`, in its name and folder: the Agent Skills format allows only lowercase letters, digits and
hyphens in a skill's name, and the folder must carry the same name.

The other skills, the founder reviews, are listed in the root README's [skills table](../README.md#skills), each in
preview until it has been checked on real decks and meetings.

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
- **YC seed guide**: Y Combinator, ["A guide to seed fundraising"](https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising),
  read in full on 22 November 2026; the page shows no date, and its round sizes are old. The runway plan quotes two
  of its lines word for word in its assumptions: for a startup that will need a follow-on round, the guide says to
  raise enough to reach the next "fundable" milestone, "which will usually be 12 to 18 months later", and founders
  raise "for N months (usually 12-18)". The runway band's default of 18 months is the top of that range (a
  benchmark, not a rule); the time left to raise the next round is ours, unverified.
- **Metrics**: the metrics check quotes five public pages word for word in its assumptions, each read in full on
  23 November 2026, text only (charts, images and embedded slides not seen): a16z's
  ["16 Startup Metrics"](https://a16z.com/16-startup-metrics/) (21 August 2015) for churn and CAC, and
  ["16 More Startup Metrics"](https://a16z.com/16-more-startup-metrics/) (23 September 2015) for ARR and customer
  concentration; Bessemer Venture Partners'
  ["Scaling to $100 Million"](https://www.bvp.com/atlas/scaling-to-100-million) (21 September 2021) for gross and
  net retention, CAC payback on gross margin and its payback targets by customer segment (under 12, 18 and 24
  months; its data is Bessemer's own cloud portfolio, not a random sample); David Sacks's
  ["The Burn Multiple"](https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200) (23 April 2020) for the
  multiple, its 3x line and the multiple approaching 0 as burn reaches 0; and David Skok's ["SaaS Metrics 2.0"](https://www.forentrepreneurs.com/saas-metrics-2/)
  (no date on the page) for net revenue churn above 2% a month. The three lines are benchmarks, not rules: each
  raises a question, never an error, and each is an input. The period rule, the cohort rule, leaving new customers
  out of retention, the exact payback formula and the tolerances are unverified.
- **Market size**: the market sizing quotes two Y Combinator pages word for word in its assumptions:
  ["How to Pitch Your Company"](https://www.ycombinator.com/library/4b-how-to-pitch-your-company)
  (the YC pitch guide; no date on the page; read in full on 23 November 2026), for building the market from customers
  and price, its method for "creating a new product or space (like Slack)" ("you can estimate the number of customers
  that would want your product and approximate how much you could charge them"), for a price that covers more than a
  year (its example device's "lifecycle ... is two years") and for preferring bottom-up to top-down. The page's own
  bottom-up is a different build ("With bottom up you figure out where comparable products are sold, how many of them
  are sold, and what % of those sales you could take."), so its preference is quoted beside that sentence, and calling
  customers times price bottom-up is common usage, unverified; and the seed guide's
  glossary (the YC seed guide above), for TAM as "the estimated total revenue available for the product(s) you are selling", which is why a
  take rate below 100% counts only the share of the spend the company keeps. Neither page defines SAM or SOM, so
  those rules, the population check, the sensitivity and break-even rule, the straight-line year (price × 12 / the
  months covered: the pitch guide gives the two-year lifecycle, not the division), the straight-line path to SOM and
  the tolerance are unverified. No figure comes from the calculator: every count, price and share is the founder's.
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

### Deal check (YC for post = pre + raise; the rest unverified)

A founder's ask is the raise I and at least one valuation figure: a pre-money, a post-money, or the percent sold. The
new money is worked as a priced equity round; a raise on a SAFE or note is not modelled here (a SAFE's share is set at
the next priced round, so `round` with that round's terms works it).

1. **Which valuation sets V.** The first given of pre-money, post-money (V = post - I) and stated percent
   (V = I/percent - I, true only with the pool in the pre-money) sets the pre-money; any other figure given is checked
   against it. Post-money = V + I, from YC's Post-Money Safe User Guide: "$2 million at a $10 million pre-money
   valuation ... the same as saying ... $2 million at a $12 million post-money valuation".
2. **The round.** With SAFEs or notes, the `round` scenario works the cap table; with only a pool top-up, the `pool`
   scenario at the deal's pool timing; with neither, the investor holds I/(V + I). The result carries the nested
   round or pool result whole.
3. **Ownership.** Every pre-round share keeps FD/T of its stake (T the shares after the round), or V/(V + I) with no
   share counts; a holder group's stake after is h × that, with h given as a percent of FD or as a share count
   (h = shares/FD, so no one divides by hand). The unissued pool U is given as shares or as a percent of FD that
   comes to whole shares. The effective pre-money is (FD - U) × price, the pre-round holders' shares at the round
   price, the same definition as the pool scenario; with SAFEs or notes it also leaves out the converted shares, so
   it sits below the pre-money less the new pool. The pre-money is split into what it pays for: those holders'
   shares, the unissued pool already there, the new pool (pool in the pre-money) and the SAFE and note shares; the
   four add up to V, rounded to the cent by largest remainder, so the existing holders' part can differ by a cent from
   the effective pre-money rounded on its own.
4. **Runway.** For the planned and today's burn, each given: net burn = gross burn - revenue, gross runway =
   (cash + I)/gross burn and net runway = (cash + I)/net burn, none when the net burn is not positive. A runway
   claim is checked against the planned net runway, else today's (no plan given, or revenue covering the planned
   burn); when revenue covers every burn given, it is not checked. No fees, the whole raise lands at once.
5. **Use of funds.** Amount lines are added up and checked against I; percent lines are turned into dollars of I,
   split to the cent, and their total checked against 100%.
6. **Checks.** A stated percent within 0.5 percentage points of the computed one is consistent, and a stated money or
   months figure within 2% of it (both inputs; the edge counts as consistent). A stated investors' percent, holder
   group's percent or runway is also consistent, whatever the tolerance, when it is the computed figure rounded half
   away from zero to the places it is written with, since people write figures rounded to the places they show: a
   stated `12` months holds a computed 11.5 up to, but not including, 12.5 (12.40 holds, though 0.4 months is past 2%
   of it), `12.0` holds 11.95 up to 12.05, and `17` holds 16.6667% sold (16.5 up to 17.5) while `20` does not. Its row
   shows the figure as typed, since those places decide it, and says whether it is that rounding
   (`rounds to the deck's "12"`, yes or no); send each as text, with the places the deck writes (`metrics_check`'s
   rule, from one shared helper). The post-money keeps the tolerance alone, since a round money figure typed in full
   carries no places, and so does the use-of-funds total, a sum of the lines, not a figure typed as one. The verdict
   is `mismatch` if any check is, `consistent` if all are, and `not_checked` when no stated figure could be checked:
   none was stated, or the only one was a runway claim with revenue covering every burn.
7. **Flags** are questions a VC is likely to ask, never errors, and never change the verdict:
   `valuation_back_solved`, `pool_in_pre_money_lowers_price`, `pool_in_post_money_dilutes_investor`,
   `pool_already_large_enough`, `conversions_bought_by_pre_money`, `discount_beat_cap`, `note_interest_converts`,
   `consistent_beyond_rounding` (a stated percent or runway consistent by the tolerance alone, not the computed figure
   rounded to its places, such as `16.5` against 16.6667%, so a VC recomputing gets another figure),
   `net_burn_not_positive`, `current_burn_runway_longer`, and two benchmark flags, `runway_below_band` (planned
   runway under 18 months) and `dilution_above_band` (more than 25% sold in one round). The two benchmarks are
   inputs, and each is a common benchmark, not a rule: no source was read that fixes either.

A refusal names the fields: no valuation, a post-money not above the raise, SAFEs, notes or a pool target without the
fully diluted shares, a stated holder percent without the holder's stake before, the holder's stake or the unissued
pool given both ways, a holder share count or pool percent without the fully diluted shares, a pool percent that is
not a whole number of shares, a holder group larger than the shares held outside the unissued pool, a runway claim or
a revenue without its burn, use-of-funds lines that mix amounts and percents, a percent with no valuation and the pool
in the post-money, and a pre-money worked from the post-money or the percent that no decimal holds exactly (1/7 of a
dollar, say) or that falls outside the calculator's bounds, when SAFEs, notes or a pool top-up need it as an input to
the nested round.

### Runway plan (YC seed guide for the milestone rule and the band; the rest unverified)

Cash only: a founder's plan, its cases and the raises to compare, with no valuation, instrument or ownership (those
are `deal_check`, `round` and `dilution`). Time t is in elapsed months from today.

1. **Phases.** A phase starting in month a covers t from a - 1 until the next phase starts; the last runs on. Net burn
   n = gross burn - revenue, flat within a phase. The cumulative net burn S(t) is continuous and piecewise linear.
   A downside or lean case is its own phases, or the plan's with revenue × R/100 and gross burn × G/100 (each 100
   when left out); the percents are the founder's, with no default.
2. **Cash.** A = cash on hand - the floor (cash kept in the bank). A raise of I landing after L whole months adds I
   at t = L (with L = 0, from the start): cash(t) = A - S(t) before L and A + I - S(t) from L on. No fees, interest or
   collection lag; the whole raise lands at once.
3. **Runway** R = the first t at which cash(t) goes below zero, worked segment by segment (breakpoints at the phase
   starts and at L), with no month-by-month loop. Cash that touches zero and then holds or rises has not run out, and
   cash exactly at zero as the money lands survives. When the last phase's net burn is not positive and the cash has
   not run out by then, there is no R. A row with no raise is always worked (option 0), on every case. With a later
   raise the result also gives whether the cash ran out before it landed (R is then the no-raise runway), the cash
   above the floor just before it lands, and R - L.
4. **Milestones.** With T = month + `months_to_raise` (the month alone when that is not given), a milestone is covered
   when R ≥ T or there is no R; the slack is R - month, and start raising by is R - `months_to_raise`. The rule
   follows the YC seed guide's "next “fundable” milestone" (for a startup that will need a follow-on round); the
   months to raise are the founder's, and leaving them is ours, unverified.
5. **Required raise.** For each case, milestone and landing month (0 and every option's): I\* = max(0, the peak of
   S(t) - A over t from L to T), the peak of a piecewise-linear function falling at a breakpoint or an end. There is
   none when S(t) > A somewhere from 0 to the earlier of L and T: the cash runs out before the money lands. An
   option landing at L covers the milestone exactly when its amount is at least I\*; the tests check that on random
   plans. The amount shown is I\* rounded up to the next cent, never down, so raising the printed figure always
   covers; the exact I\* is in the JSON.
6. **Checks.** A stated runway with no raise is checked against the plan's no-raise runway; each option's stated
   runway against its plan runway from today, or less L when it counts from landing; within 2% of the computed one
   (an input, the edge included) is consistent. A stated runway is also consistent, whatever the tolerance, when it is
   that computed figure rounded half away from zero to the places it is written with (`deal_check`'s rule, from the
   same shared helper): a stated `12` holds a computed 12.40 though 0.4 months is past 2% of it, and `12.0` does not.
   Its row shows the figure as typed and says whether it is that rounding (`rounds to the deck's "12"`, yes or no);
   send each as text, with the places the founder writes. Each option's use-of-funds lines are checked against its
   amount as `deal_check` checks them (one shared helper, the same tolerances), with the tolerance alone: the total is
   a sum of the lines, not a figure typed as one. With no R, a runway claim is not checked, and neither is a runway
   counted from landing when the cash runs out before the money lands (there is no R - L; the stated line says so and
   `cash_out_before_raise_lands` fires). The verdict is `deal_check`'s rule.
7. **Flags**, never errors: `cash_never_runs_out`, `cash_out_before_raise_lands`, `milestone_short_on_plan` (a raise
   short on the plan; the no-raise row does not count), `downside_short_where_plan_covers` (a milestone covered on
   the plan and short on the downside for the same row, the no-raise row included: with a raise or with none),
   `covered_without_raise`, `start_raising_date_passed` (the
   no-raise plan runway less the months to raise is at or before today), `no_time_to_raise_given`, and
   `runway_below_band` (a raise lasting under 18 months on the plan, from today; an input, and a benchmark, not a
   rule: 18 is the top of the YC seed guide's "raising for N months (usually 12-18)", so a raise inside 12 to 18 is
   within the guide's range and the flag is a question, not a shortfall), and `consistent_beyond_rounding` (a stated
   runway consistent by the tolerance alone, not the computed runway rounded to its places, such as `12.5` against
   12.62 months, so a reader recomputing gets another figure).

A refusal names the field: a first case that is not the plan, a plan given as percents, a case named twice, a case
with both phases and a percent or neither, phases that do not start at month 1 or do not move later, a floor above the
cash, a milestone given twice, use-of-funds lines that mix amounts and percents, and every list over its cap.

### Metrics check (a16z, Bessemer, Sacks and Skok for the definitions and benchmarks; the rest unverified)

A founder's own figures for one period of P months (1 to 36): every flow (the recurring revenue movement, customers,
spend, burn, revenue) covers that one period. Recurring revenue is monthly (k = 12) or annual (k = 1), as the founder
gives it; the calculator never converts a quarter to a year or compounds a rate.

1. **ARR.** With S at the start, N new, E expansion, C contraction and X churned: ARR at the start k·S, at the end
   k·(S + N + E - C - X), net new ARR k·(N + E - C - X), new ARR k·N. From the latest month's revenue T, of which O
   is one-time and U usage: ARR 12·(T - O - U), and the run-rate 12·T, which is not ARR (a16z: ARR "should exclude
   one-time fees, professional service fees, and any variable usage fees"). A stated ARR is checked against the
   movement's ending ARR, or the latest month's ARR when no movement is given. With both given, it is consistent
   within `tolerance_percent` of either, and the report says which it was checked against: the month's when it is
   within the tolerance of the month's alone, else the movement's. When the two differ by more than
   `tolerance_percent`, `arr_movement_and_month_disagree` says the founder's two sets of parts disagree, whatever the
   verdict.
2. **Retention and churn.** Gross revenue retention (S - C' - X')/S and net (S + E' - C' - X')/S, where E', C' and
   X' are the starting customers' own movements when given and the period's totals otherwise (Bessemer for the
   definitions; leaving new customers out is ours, unverified). Gross revenue churn = 1 - GRR, net revenue churn =
   1 - NRR (below zero when expansion outruns losses), logo churn = customers lost / customers at the start (a16z,
   stated per month; over a longer period it is ours). None is annualised. Once a starting-customers figure is given,
   the report prints the primed formula, and the `cohort_rule` row names which movements were the starting
   customers' own and which fell back to the period's total.
3. **Acquisition.** Blended CAC = spend / new customers; paid CAC = spend / customers from paid channels (a16z). CAC
   payback = spend / (new monthly recurring revenue × gross margin) in months, and the revenue-only payback leaves
   the margin out (Bessemer measures payback on gross margin; the formula is unverified). With no gross margin, the
   revenue-only payback is a floor under the margin one (a margin is at most 100%), so the payback benchmark is set
   against it: at or above the band it is flagged; below it the benchmark is not applied, and its row says so.
4. **Efficiency.** Burn multiple = net burn / net new ARR (Sacks), none when either is zero or less. Sacks gives no
   ratio before revenue and says the multiple "should also approach 0 over time" as burn reaches 0; working none at
   zero burn, and none for a negative burn or net new ARR, is ours (unverified). On new ARR alone it is worked
   whenever a multiple is stated, to test whether the stated figure used new ARR. Concentration = the largest
   customer's revenue / the period's revenue (a16z), with no benchmark.
5. **Checks.** Each stated figure is checked with `deal_check`'s tolerances (0.5 points for a percent, 2% of the
   computed value for the rest, each an input, the edge included); a mismatch whose difference shows as equal to the
   tolerance says it is just over it. A stated percent, months or multiple is also consistent, whatever the
   tolerance, when it is the computed figure rounded half away from zero to the places it is written with, since
   people write figures rounded to the places they show: a stated `12` months holds a computed 11.5 up to, but not
   including, 12.5 (12.40 holds, though 0.4 months is past 2% of it; 12.5 rounds to 13), `12.0` holds 11.95 up to
   12.05, and a monthly churn stated as `2` (2%) holds 2.4% but not 2.6%. Its row shows the figure as typed, since
   those places decide it, and says whether it is that rounding (`rounds to the deck's "12"`, yes or no). Money keeps
   the tolerance alone and has no such row, since a figure like $1.2M
   carries no places once typed as 1200000. A stated churn with a basis is checked on that basis; with none, on
   every basis the inputs allow, and it holds when any does; a churn below zero is checked only as net revenue churn,
   and rounds away from zero as a positive figure does (-1.55% is -2 to no places and -1.6 to one). A stated gross retention
   above 100% is checked like any other figure: a mismatch unless it is within the tolerance of the computed figure
   or its rounding (100.4% against 99.95% is consistent). A stated zero keeps the places it is written with for the
   rounding, so `0.0` holds -0.05 to 0.05 and `0` holds -0.5 to 0.5, both ends left out; send each stated percent,
   months or multiple as text, with the places the document writes. A stated payback is checked on gross margin when
   one is given. A stated burn multiple with no multiple to work (step 4) comes back
   `not_checked`, with no computed figure. The verdict: mismatch if any figure is, else not_checked if none was
   checked or one was left unchecked, else consistent.
6. **Flags**, never errors. Beside a mismatch, the likely cause: `stated_arr_matches_run_rate`,
   `stated_nrr_includes_new` (ending over starting recurring revenue), `stated_payback_not_margin_adjusted` and
   `stated_burn_multiple_uses_new_not_net_arr` (also beside a multiple left unchecked), each only when the stated
   figure lands within tolerance of that other definition (the tolerance alone: the rounding rule of step 5 decides a
   verdict, never a cause; the run-rate one also only when the latest month has one-time or usage revenue).
   `consistent_beyond_rounding`: a figure consistent by the tolerance alone, not the computed figure
   rounded to its places, such as a monthly churn of 1.7% against 2.1%, so a VC recomputing gets another figure. With
   or without a mismatch:
   `arr_movement_and_month_disagree` (step 1), `run_rate_includes_non_recurring` (the latest month has one-time
   or usage revenue), `expansion_hides_churn` (revenue was lost, but net revenue churn is at or below zero),
   `churn_basis_unlabelled` (a stated churn with no basis; below zero it says it was checked as net revenue churn
   alone), `blended_cac_only` (no paid-channel count),
   `payback_not_margin_adjusted` (no gross margin), `burn_multiple_not_defined` (net new ARR at or below zero) and
   `no_net_burn` (a net burn at or below zero); each of these two says the overall verdict cannot be consistent only
   when a multiple is stated. The benchmarks, each an input: `payback_above_band` (at or above
   Bessemer's target for the customer segment, under 12 months for SMB, 18 for mid-market and 24 for enterprise, or
   the founder's own band), `burn_multiple_above_band` (3x or more, Sacks) and `net_revenue_churn_above_band` (above
   2% in a one-month period, Skok; not asked over a longer period, since nothing is compounded).

A refusal names the field: a churn below zero on a basis that cannot go there (logo or gross revenue churn, or no
recurring revenue to work net revenue churn on), customers lost above customers at the start (only those there at
the start count; customers won and lost inside the period are left out), a movement or cohort figure without
`starting_recurring`, contraction and churn above
everything the period had (the start, new and expansion, so ARR at the end is never below 0), a cohort figure above
its total, the starting customers' contraction and churn above the start (each the period's total when its `cohort_*`
figure is not given, so retention is never below 0), the latest month's parts without its total or above it, customers lost or
paid-channel customers without or above their total, the largest customer without or above the period's revenue, a
stated figure without what it needs to be checked, and a churn basis without a stated churn or its inputs.

### Market sizing (YC's pitch guide for customers × price and the seed guide for TAM as revenue; the rest unverified)

A founder's own segments, up to 8: for each, the buying customers, the price of one unit and the months it covers
(not given, or null, is read as 12, a yearly price, which the report marks as not given and flags, and the result's
echoed `inputs` keep as null, so feeding them back keeps the flag; 1 for a monthly price, 24 for a two-year device),
the units one customer buys, the take rate (100% by
default; a marketplace's or a payments company's fee), the serviceable percent (100% by default) and the SOM, as the
customers to win (preferred) or a share of the serviceable customers to win, never both.

1. **Per segment.** Annual revenue from one customer = price × 12 / the months covered × units × take rate. TAM =
   customers × that; the gross spend (before the take rate) is shown apart. SAM customers = customers × serviceable
   percent, SAM = SAM customers × annual revenue from one. SOM customers = the customers to win, or SAM customers ×
   the share to win; SOM = SOM customers × annual revenue from one.
2. **Totals.** Each is the sum of the segments; SAM as a share of TAM, SOM as a share of SAM and, with today's
   annual revenue, SOM over it. With today's customers and a horizon in years, the new customers a year to reach SOM
   are a straight line, (SOM customers - today's) / years; no growth rate is compounded.
3. **Top-down cross-check.** Each top-down figure's comparable part (the figure × the share that matches the
   founder's definition) is set beside the bottom-up TAM or SAM: the bottom-up as a share of it and the difference.
   It never sets the market size or the verdict (YC's pitch guide prefers its bottom-up, comparable products' sales,
   to top-down; that the preference carries over to customers × price is unverified).
4. **Checks.** A stated TAM, SAM or SOM is checked with `deal_check`'s 2% relative tolerance (an input, the edge
   included). The verdict is mismatch if any is, not_checked with none.
5. **Sensitivity.** Each row works one field of one segment (`customers`, `price`, `units_per_customer`, the three
   percents or `obtainable_customers`) at each of the founder's values, the rest at base, and gives the SOM low,
   high and swing. Every total is linear in one field, so the value at which SOM reaches the plan's target, and TAM
   or SAM the first top-down figure's comparable part (only the first: a second or third figure gets the cross-check
   of step 3, no break-even), is exact: x\* = x0·(T - the other segments' total) / this segment's total. It is
   `does_not_move` when the field is not a factor of that total (tested first, so it is reported even when the
   target is already met); `met_without_it` when the target is reached with the field at its base (the other segments
   alone reach it, or, for the plan's target, the base SOM is already at or above it), with no value; and `out_of_range` when the segment would be refused at that value (a percent above 100,
   more customers to win than it can serve, fewer customers than today's, or a number outside the size every input
   has: at least 1e-15 and under 1e16), the value still given. The top-down break-even is a cross-check, not a
   target.
6. **Flags**, never errors: `price_period_defaulted` (a segment left out the months its price covers, so the price
   was read as a yearly one; a monthly price left out makes that segment 12 times too small),
   `segments_exceed_population` (the segments' customers add up to more than the population they come from: a buyer
   counted twice), `bottom_up_above_top_down` (above a top-down figure's comparable part), `sam_equals_tam` (no
   serviceable percent below 100), `som_not_given` (a segment with no SOM, so no SOM total), `som_as_percent_only`,
   `som_from_zero_customers`, `som_below_customers_today`, `no_horizon_given`, `som_below_target` (the SOM total is
   below the plan's target) and `som_target_out_of_reach` (the SOM is below the target, and no sensitivity row
   reaches it at a value its segment can take: at least one row would need a value out of range and none reaches it
   exactly).

A refusal names the field: a SOM given both ways, today's customers above the buying customers, customers to win
above the serviceable customers, a stated SOM or a target with a segment that has no SOM, and a sensitivity row past
the last segment, on a SOM field the segment does not give, repeated, or with a value the segment would refuse.

### Priced round now vs a note now (the round's and the waterfall's rules; the comparison's own unverified)

The same raise I two ways, from today's cap table by holder group: the founders, the team (granted options and the
team's common), the unissued pool U, the existing preferred series, and any SAFEs and notes outstanding. Today's fully
diluted shares FD = founders + team + U + the existing series' shares. Every price comes from the round code above
and every exit from the waterfall code; nothing is worked a second way.

1. **Option A, today.** A priced round of I at the founder's pre-money V on FD, with any pool top-up and the
   existing SAFEs and notes converting in it, exactly as `round` works it: p = V/(FD + converted + new pool), new
   money's shares N = I/p.
2. **Option B, today.** No shares: the note is outstanding, its principal I now and, when it converts, what the note
   interest rules above say it owes (principal plus interest, to the cent, or the principal alone when the interest is
   paid in cash). Its cap price is the cap over FD.
3. **Each next round, the same for both.** The founder gives its pre-money, raise, any pool top-up and its series'
   terms. Each next round is an alternative for the one round after today, worked from today's cap table, never after
   the one before. A prices it on A's shares after today (exact, often fractional) with nothing left to convert. B prices it
   on FD with the existing SAFEs and notes (each existing note that many months older) and its note converting at the
   lower of its cap price and its discount price (the round price × (1 - discount)); with neither it takes the round
   price.
4. **Each exit, after each next round.** The waterfall splits each option's cap table: the existing series as given;
   option A's new money and every converted SAFE or note on the series terms of the round they convert in, owed their
   multiple of the amount converted; the next round's investors on its terms. The founders, the team and (by default)
   the pool are common. A series' terms are the founder's: `standard` (1x, non-participating) only when the founder
   says the terms are standard, else the multiple and participation given; rank 1 unless given.
5. **Side by side.** Ownership is each group's shares over the total. Each option's payouts are split to the cent by
   largest remainder, so they add up to the exit; every B - A is the exact difference, rounded once, so it can differ
   by a cent from the difference of the two rounded payouts.
6. **Flags**, never a pick: `cap_below_round_price_now` (the note's cap price is below A's price today),
   `note_converts_at_cap`, `note_converts_at_discount`, `note_converts_at_round_price` (the price the note took in
   at least one next round), `note_interest_converts`, `note_interest_paid_in_cash` (B pays the interest in cash at
   conversion: it is in no payout line, and A pays none), `maturity_not_given`, `converts_after_maturity` (the
   maturity comes before the months to conversion: only compared, never modelled),
   `next_round_below_priced_round_price` (a down round for A's investors; no anti-dilution is applied),
   `priced_round_below_existing_series_price` (A's price today is below what an existing series paid per share, its
   amount invested over its shares: a down round for that series; no anti-dilution is applied) and
   `existing_mfn_safe_beside_note` (an existing MFN SAFE converts on the terms given for it under both options; whether
   it may take B's note's cap or discount is in the SAFE's own terms, not modelled).

No next round is refused (`no_next_round_given`: the note converts only at one), and so is a comparison with no
exit. An exit before the next round, while the note is outstanding, is not modelled.

### Pool plan (the option-pool shuffle above; the plan's own conventions unverified)

The pool a term sheet asks for, t_req, beside the pool the founder's hiring plan needs until the next round, t_plan,
both created in the pre-money and both worked by the option-pool shuffle's own code (the pool in the pre-money,
above), so no formula of the shuffle is worked a second way.

| Symbol | Meaning                                                                                                  |
| ------ | -------------------------------------------------------------------------------------------------------- |
| FD, U  | every share before the round, the unissued pool U included                                               |
| V, I   | pre-money valuation, investment                                                                          |
| G      | the grants of the hires starting on or before the next round's month, in shares                          |
| t_plan | the plan's target: the share of every post-round share that G takes on the plan column's own cap table   |
| t_req  | the term sheet's requested pool: the unissued pool after the round, as a share of every post-round share |

With the pool in the pre-money, the shuffle's new pool P gives a price p = V/(FD + P) and a total of
T = (FD + P)·(V + I)/V shares, so the pool after the round is t = (U + P)·V/((FD + P)(V + I)). t_plan is the grants'
share of the plan column's own total, G/T. When the grants do not fit in today's pool (G > U), the plan's pool holds
exactly them, U + P = G, so P = G - U and FD + P = FD - U + G; when they fit (G ≤ U), P = 0 and FD + P = FD:

- **grants in shares**: t_plan = G·V/((V + I)(FD - U + G)) with a top-up, and G·V/((V + I)·FD) when the grants fit
  in today's pool. Put back into the shuffle's P = (t·FD - (1 - r)·U)/(1 - r - t) with r = I/(V + I), the first gives
  P = G - U again, and the second a needed P that is not positive (t·FD = G·(1 - r) ≤ U·(1 - r)), so P = 0. The tests
  check that on exact fractions and on seeded random inputs, and that the same plan given in shares and as percents
  of the same total gives the same t_plan.
- **grants as percents of the post-round fully diluted shares**: t_plan is their sum, and each column's grants take
  that sum of its own total T. A plan that gives some grants in shares and some as percents is refused
  (`grants_mixed_units`): a percent of shares not yet priced cannot be added to a count of shares.

When the grants fit in today's pool (G ≤ U), the shuffle's needed new pool is not positive, so P = 0, p = V/FD and
today's pool is kept whole (`plan_fits_current_pool`); the plan's pool is then not cut below U, and the pool after the
round (the option pool's ownership line) is today's pool's share, not t_plan. Each column then gives the shuffle's
table: P, p, the investor's shares N = I/p, T, who owns what (the founders too, F/T, when `--founder-shares` is
given), the pool left ungranted at the next round (U + P less the grants' shares, negative when the pool runs short
before it) and the effective pre-money (FD - U)·p, which is V - t(V + I) when the column tops the pool up (P > 0) and
(FD - U)·V/FD when it does not. Every difference is requested - plan of the exact values, rounded once.

Flags, never a pick: `no_hires_before_next_round`, `hires_after_next_round_ignored` (a hire starting after the next
round's month is left out: the next round's own pool would cover it), `plan_fits_current_pool`,
`requested_met_by_current_pool` (today's pool already meets t_req), `requested_above_plan` and
`requested_below_plan`. No hire is refused (`no_hiring_plan_given`), and so are percents of the counted hires adding
up to V/(V + I) or more, which leave no positive price.

### Raise pipeline (unverified arithmetic; the start-raising month is the runway plan's)

A founder's round, the commitments and pro rata against it, and the founder's own funnel of investors. Every amount,
count and rate is the founder's; nothing is assumed or looked up, and no investor is named.

| Symbol | Meaning                                                                                 |
| ------ | --------------------------------------------------------------------------------------- |
| R      | the round size                                                                          |
| L      | the lead's cheque (0 when none is given)                                                |
| F, S   | the firm and the soft commitments, each as the founder marks it                         |
| P      | every pro rata amount, counted in full                                                  |
| n_k    | the investors at stage k today, each counted once, at the furthest stage it has reached |
| r_k    | the founder's rate from stage k to the next (from the last stage, to a term sheet)      |
| W      | the term sheets the founder wants                                                       |

**Allocation.** The room after the lead and the firm commitments is R - L - F and the allocation left is
R - L - F - P. S is summed and shown on its own line, never counted. Below zero, one cause is named:
`oversubscribed` when L + F > R (the lead and the firm commitments alone are over the round), else
`pro_rata_exceeds_left` when L + F ≤ R < L + F + P; `fully_allocated` when the allocation left is exactly zero.

**Funnel.** With q*k = r_k·r*(k+1)···r*last, the rate to a term sheet from stage k, the conversion is q_1 and the
expected term sheets are E = Σ n_k·q_k: walked stage by stage, e_1 = n_1, e_k = n_k + e*(k-1)·r\_(k-1), and
E = e_last·r_last. With every investor at the first stage, E = n_1·q_1, the targets times the product of the rates.
E is an expectation from the founder's own rates (each investor moving on independently), not a forecast. The targets
needed from an empty funnel are T = ceiling(W/q_1), the more needed beyond today's M = ceiling((W - E)/q_1), floored
at 0, and the investors needed at stage k ceiling(W/q_k). A stage with no rate is refused (`stage_rate_missing`); a
benchmark rate goes in only with the founder's source (`rate_basis: benchmark`, `benchmark_source`), and is flagged.

**Timing.** With cash, the phases and the months to raise, the start-raising month is the `runway_plan` scenario's own
row for the plan with no raise: its runway less the months to raise, in months from today. Its flags
`cash_never_runs_out` and `start_raising_date_passed` come through. Cash and phases with no months to raise are
refused (`no_months_to_raise_given`).

Flags, never a pick: `no_lead_cheque_given`, `soft_commitments_not_counted`, `oversubscribed`,
`pro_rata_exceeds_left`, `fully_allocated`, `no_funnel_given`, `benchmark_rates_given`, `funnel_short_of_wanted`
(E < W), `no_runway_given`, `cash_never_runs_out` and `start_raising_date_passed`. A commitment not marked soft or firm
is refused (`commitment_kind_missing`), and so are term sheets wanted with no funnel (`no_funnel_given`) and a funnel
with no term sheets wanted (`no_term_sheet_count_given`).

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

**Checking a raise (Company B, made up).** An $8M Series A at $32M pre ($40M post) for 20%, two post-money SAFEs ($1M
at a $10M cap, $1.5M at a $15M cap), a pool topped up to 10% in the pre-money, and founders at 90% of 10M fully
diluted shares, 400,000 of them the unissued pool. The deck says the founders keep 72%:

```
equity_calculator deal_check --investment 8000000 --pre-money 32000000 --post-money 40000000 \
    --stated-investor-percent 20 --fully-diluted-shares 10000000 --unissued-pool-shares 400000 \
    --target-pool-percent 10 --safe "1000000 valuation-cap=10000000" --safe "1500000 valuation-cap=15000000" \
    --holder-percent 90 --stated-holder-percent 72
  Price per share (p)                                                            $2.314050  the round's price
  Effective pre-money                                                       $22,214,876.03  (FD - U)·p: the pre-round holders' shares at the round price
  After: holder group                                                             52.0661%  h·kept
  After: SAFE 1                                                                    7.2314%  shares/T
  After: SAFE 2                                                                    7.2314%  shares/T
  After: option pool                                                              10.0000%  (U + P)/T
  After: investors                                                                20.0000%  N/T
  Share of their stake every pre-round share keeps                                57.8512%  FD/T, or V/(V + I) with no share counts
  Pre-money pays for: SAFE and note shares                                   $5,785,123.97  converted shares·p
  Post-money: verdict                                                           consistent  within the tolerance is consistent
  Investors' percent: verdict                                                   consistent  within the tolerance, or rounding to the deck's, is consistent
  Holder group's percent after: the deck says                                     72.0000%  given
  Holder group's percent after: the calculator gives                              52.0661%  h·(share every pre-round share keeps)
  Holder group's percent after: difference                                       -19.9339%  computed - stated
  Holder group's percent after: verdict                                           mismatch  within the tolerance, or rounding to the deck's, is consistent
  Overall verdict                                                                 mismatch  mismatch if any check is; consistent if all are; not_checked with none
```

The post-money and the 20% hold; the 72% does not. It counts only the new investors' 20% against the founders, and
leaves out the SAFEs and the pool top-up, both paid for out of the pre-money: every pre-round share keeps 57.8512% of
its stake. The report also flags
`pool_in_pre_money_lowers_price` and `conversions_bought_by_pre_money` as what a VC is likely to ask about.

**How long a raise lasts (Company W, made up).** $500k in the bank; months 1 to 3 spend $120k a month with $10k of
revenue, months 4 to 12 spend $220k with $25k, and from month 13 $300k with $60k. The downside has half the revenue.
$3M or $4M raised now; the milestone is month 15, with 6 months to raise the next round:

```
equity_calculator runway_plan --cash-on-hand 500000 --phase "from-month=1 gross-burn=120000 revenue=10000" \
    --phase "from-month=4 gross-burn=220000 revenue=25000" --phase "from-month=13 gross-burn=300000 revenue=60000" \
    --downside-revenue-percent 50 --raise "amount=3000000" --raise "amount=4000000" --milestone 15 --months-to-raise 6
  Runway, plan, no raise                                                       3.87 months  months until cash less the floor goes below zero
  Start raising by, plan, no raise                                            -2.13 months  runway - months to raise
  Runway, plan, raise 1                                                       17.90 months  months until cash less the floor goes below zero
  Runway, plan, raise 2                                                       22.06 months  months until cash less the floor goes below zero
  Runway, downside, no raise                                                   3.75 months  months until cash less the floor goes below zero
  Runway, downside, raise 1                                                   16.77 months  months until cash less the floor goes below zero
  Runway, downside, raise 2                                                   20.47 months  months until cash less the floor goes below zero
  Milestone 1 (month 15), plan, raise 1: verdict                                     short  covered when the runway reaches month 21
  Milestone 1 (month 15), plan, raise 2: verdict                                   covered  covered when the runway reaches month 21
  Milestone 1 (month 15), downside, raise 1: verdict                                 short  covered when the runway reaches month 21
  Milestone 1 (month 15), downside, raise 2: verdict                                 short  covered when the runway reaches month 21
  Required raise, milestone 1, plan, landing month 0                         $3,745,000.00  smallest raise keeping cash at or above the floor to month 21 (rounded up to the cent)
  Required raise, milestone 1, downside, landing month 0                     $4,142,500.00  smallest raise keeping cash at or above the floor to month 21 (rounded up to the cent)
```

With no raise the cash lasts 3.87 months, so the next raise is already late. $3M lasts 17.90 months, short of month
21; $4M lasts 22.06 months on the plan but 20.47 on the downside, short there too. The smallest raise that reaches
month 21 now is $3,745,000.00 on the plan and $4,142,500.00 on the downside. The report also flags
`milestone_short_on_plan`, `downside_short_where_plan_covers`, `start_raising_date_passed` and `runway_below_band`.

**Traction a VC will recompute (Company AM, made up).** Over 12 months, monthly recurring revenue went from $80k
to $100k: $24k new, $6k expansion, $2k downgrades and $8k cancelled. Last month's revenue was $125k, $25k of it
implementation fees, and the net burn was $1.8M. The deck says $1.5M ARR, 125% net revenue retention and a 6.25x
burn multiple:

```
equity_calculator metrics_check --period-months 12 --starting-recurring 80000 --new-recurring 24000 \
    --expansion-recurring 6000 --contraction-recurring 2000 --churned-recurring 8000 \
    --month-total-revenue 125000 --month-one-time-revenue 25000 --net-burn 1800000 \
    --stated-arr 1500000 --stated-nrr-percent 125 --stated-burn-multiple 6.25
  ARR at the end of the period                                                   $1,200,000.00  k·(S + N + E - C - X)
  Run-rate (12 x the month's revenue)                                            $1,500,000.00  12·T
  Gross revenue retention (12 months)                                                 87.5000%  (S - C - X)/S
  Net revenue retention (12 months)                                                   95.0000%  (S + E - C - X)/S
  Burn multiple                                                                      7.500000x  net burn / net new ARR
  Burn multiple on new ARR only                                                      6.250000x  net burn / new ARR
  ARR: verdict                                                                        mismatch  within the tolerance is consistent
  Net revenue retention: verdict                                                      mismatch  within the tolerance, or rounding to the deck's, is consistent
  Burn multiple: verdict                                                              mismatch  within the tolerance, or rounding to the deck's, is consistent
  Overall verdict                                                                     mismatch  mismatch if any figure is (an unlabelled churn holds when any basis does); else not_checked with none checked or one left unchecked; else consistent
```

ARR is 12 × $100k = $1,200,000; the $1.5M is the run-rate, with the fees in it. Net revenue retention is 95%, not
125%: the 125% is ending over starting recurring revenue, which counts the new customers. The burn multiple is
7.5x on net new ARR; the deck's 6.25x divides by new ARR alone, before churn and downgrades. The report also flags
`stated_arr_matches_run_rate`, `run_rate_includes_non_recurring`, `stated_nrr_includes_new`,
`stated_burn_multiple_uses_new_not_net_arr` and `burn_multiple_above_band` as what a VC is likely to ask about.

**A market built bottom-up (Company AW, made up).** Software for vet clinics: 18,000 independent clinics at $400 a
month, 60% of them reachable today, 900 to win and 45 customers now; and 400 multi-site groups, 15 locations each at
$300 a location a month, 50% reachable, 10% of those to win and 2 customers now. An analyst's figure of $2.1B a
year matches the founder's definition for 40% of it. The plan needs $8M a year from this market in 5 years, today's
revenue is $324k a year (its 47 customers at its own prices), and the deck says the TAM is $120M. The founder's own ranges: price $300 to $500, clinics to
win 600 to 1,200, the groups' share 5% to 15%:

```
equity_calculator market_sizing \
    --segment "customers=18,000 price=400 price-period-months=1 serviceable-percent=60 obtainable-customers=900 customers-today=45" \
    --segment "customers=400 price=300 price-period-months=1 units-per-customer=15 serviceable-percent=50 obtainable-percent=10 customers-today=2" \
    --top-down "amount=2,100,000,000 comparable-percent=40" --som-years 5 --annual-revenue-today 324000 \
    --som-target 8000000 --stated-tam 120000000 \
    --sensitivity "field=price segment=1 values=300/500" --sensitivity "field=obtainable-customers segment=1 values=600/1,200" \
    --sensitivity "field=obtainable-percent segment=2 values=5/15"
  Segment 1: annual revenue per customer                                         $4,800.00  price × 12 / months covered × units × take rate
  Segment 2: annual revenue per customer                                        $54,000.00  price × 12 / months covered × units × take rate
  Total TAM                                                                $108,000,000.00  sum of the segments
  Total SAM                                                                 $62,640,000.00  sum of the segments
  Total SOM customers                                                                  920  sum of the segments
  Total SOM                                                                  $5,400,000.00  sum of the segments
  SOM share of SAM                                                                 8.6207%  total SOM / total SAM
  SOM / annual revenue today                                                    16.666667x  total SOM / annual revenue today
  Segment 1: new customers a year to SOM                                               171  (SOM customers - customers today) / years, a straight line
  Top-down 1: comparable part                                              $840,000,000.00  figure × share matching
  Top-down 1: bottom-up as a share of it                                          12.8571%  bottom-up TAM / comparable part (a cross-check)
  TAM: verdict                                                                    mismatch  within the tolerance is consistent
  Sensitivity 1: SOM swing                                                   $2,160,000.00  SOM high - SOM low
  Sensitivity 2: SOM swing                                                   $2,880,000.00  SOM high - SOM low
  Sensitivity 3: SOM swing                                                   $1,080,000.00  SOM high - SOM low
  Sensitivity 1: segment 1 price at SOM = $8,000,000.00                        $640.740741  base × (target - other segments' SOM) / this segment's SOM
  Sensitivity 2: segment 1 customers to win at SOM = $8,000,000.00                1,441.67  base × (target - other segments' SOM) / this segment's SOM
  Sensitivity 3: segment 2 share to win at SOM = $8,000,000.00                    34.0741%  base × (target - other segments' SOM) / this segment's SOM
  Overall verdict                                                                 mismatch  mismatch if any stated figure is; not_checked with none; a top-down figure never counts
```

The TAM is $108,000,000.00, not the deck's $120M (a mismatch past the 2% tolerance), and the SOM is $5,400,000.00
from 920 customers, 8.6207% of SAM and 16.666667x today's revenue: short of the $8M the plan needs, so the report
flags `som_below_target`, and
`som_as_percent_only` for the groups' 10%. The top-down figure is a cross-check only: the bottom-up TAM is 12.8571% of
its comparable part. Of the three ranges, the clinics to win move SOM the most ($2,880,000.00 from low to high);
reaching $8M on one assumption alone would take a $640.740741 monthly price, about 1,442 clinics (1,441.67 rounded;
4325/3 exactly), or winning 34.0741% of the serviceable groups (about 68 of the 200, 17.04% of all 400).

**A priced round now or a note now (Company BU, made up).** 8,000,000 founder shares, 1,000,000 for the team and a
1,000,000-share unissued pool, raising $2,000,000. Option A prices it at an $8,000,000 pre-money on standard terms
(the founder said so). Option B is a note with a $6,000,000 cap, a 20% discount and 5% simple interest, converting in
12 months. The founder expects the next round to raise $6,000,000 at a $27,000,000 pre-money, then a sale for $5M,
$20M or $100M:

```
equity_calculator instrument_compare --founder-shares 8,000,000 --team-shares 1,000,000 \
    --unissued-pool-shares 1,000,000 --investment 2,000,000 --priced-pre-money 8,000,000 --priced-preference standard \
    --note-valuation-cap 6,000,000 --note-discount-percent 20 --note-interest-rate-percent 5 --note-compounding simple \
    --note-months-to-conversion 12 --next-round "pre-money=27000000 investment=6000000 standard" \
    --exit 5,000,000 --exit 20,000,000 --exit 100,000,000
  Today: price per share                                                      $0.800000                                    p = V/(FD + converted + new pool)
  Note owed when it converts                                                                $2,100,000.00                  principal + interest, to the cent
  Note's cap price                                                                              $0.600000                  cap / FD
  Today: founders                                                              64.0000%          80.0000%        16.0000%  group's shares / total shares
  Next round 1: price per share                                               $2.160000         $2.000000                  p = V/(each option's shares + converted + new pool)
  Next round 1: B's note: converts at                                                           $0.600000                  its cap price, the lower
  Next round 1: B's note: shares                                                                3,500,000                  amount converting / price
  Next round 1: founders                                                       52.3636%          48.4848%        -3.8788%  group's shares / total shares
  Next round 1: exit $5,000,000.00: founders                                      $0.00             $0.00           $0.00  the waterfall, every preference honoured
  Next round 1: exit $5,000,000.00: new money                             $1,250,000.00     $1,296,296.30      $46,296.30  the waterfall, every preference honoured
  Next round 1: exit $5,000,000.00: preferences paid                      $5,000,000.00     $5,000,000.00                  classes that stay
  Next round 1: exit $20,000,000.00: founders                             $8,960,000.00     $8,296,296.29    $-663,703.70  the waterfall, every preference honoured
  Next round 1: exit $20,000,000.00: new money                            $2,800,000.00     $3,629,629.63     $829,629.63  the waterfall, every preference honoured
  Next round 1: exit $20,000,000.00: next round's investors               $6,000,000.00     $6,000,000.00           $0.00  the waterfall, every preference honoured
  Next round 1: exit $100,000,000.00: founders                           $52,363,636.36    $48,484,848.49  $-3,878,787.88  the waterfall, every preference honoured
  Flag                                                        cap_below_round_price_now                                    The note's cap price is below option A's price per share today: at its cap the note buys shares for less than option A's investors pay today
  Flag                                                             note_converts_at_cap                                    In at least one next round the note converts at its cap price
  Flag                                                           note_interest_converts                                    The note's interest converts too, so it gets shares for more than the raise
  Flag                                                               maturity_not_given                                    No maturity was given for the note: what happens if the next round comes late is in the note's own terms, not modelled here
```

Right after today the founders hold 64% in A and 80% in B, as the note has no shares yet. At the next round the note
converts its $2.1M at its $0.60 cap price (below A's $0.80 today) into 3,500,000 shares, so the founders end at
48.4848% in B against 52.3636% in A, 3.8788 points fewer (-32/825 exactly). At a $5M sale both options pay the
founders nothing: the preferences ($8M in A, $8.1M in B) take it all. At $20M the founders get $8,960,000.00 in A and
$8,296,296.29 in B ($8,296,296.30 on its own; the cent goes elsewhere by largest remainder), $663,703.70 less; at
$100M everyone converts and the payouts follow ownership. The report never says which to take.

**A pool sized from the hiring plan (Company CP, made up).** 10,000,000 fully diluted shares, 1,000,000 of them an
unissued pool and 7,000,000 the founders'; raising $4,000,000 at a $16,000,000 pre-money, and the term sheet asks for
a 15% pool. The founder plans five hires before the next round in month 18 (400,000, 250,000, 250,000, 350,000 and
150,000 shares: G = 1,400,000) and a sixth in month 24:

```
equity_calculator pool_plan --fully-diluted-shares 10,000,000 --unissued-pool-shares 1,000,000 \
    --founder-shares 7,000,000 --pre-money 16,000,000 --investment 4,000,000 --requested-pool-percent 15 \
    --next-round-month 18 --hire "Founding engineer: start-month=1 grant-shares=400000" \
    --hire "Senior engineer: start-month=4 grant-shares=250000" --hire "Senior engineer: start-month=6 grant-shares=250000" \
    --hire "Head of sales: start-month=9 grant-shares=350000" --hire "Designer: start-month=12 grant-shares=150000" \
    --hire "VP engineering: start-month=24 grant-shares=500000"
  Hire 6: VP engineering, from month 24                           500,000                                                left out: starts after month 18, the next round
  Shares the counted grants take                                1,400,000                   1,400,000                    G: the counted grants added up
  Target pool after the round (t)                                10.7692%                    15.0000%           4.2308%  plan: G·V/((V + I)(FD - U + G)), the pool holding exactly G; requested: given
  New pool shares (P)                                             400,000               1,076,923.077       676,923.077  (t·FD - (1 - r)U)/(1 - r - t), 0 when not positive: the pool scenario's
  Price per share (p)                                           $1.538462                   $1.444444        $-0.094017  V/(FD + P)
  Ownership: founders                                            53.8462%                    50.5556%          -3.2906%  F / T (founders are among the existing holders)
  Pool left ungranted at the next round                                 0                 676,923.077       676,923.077  U + P - the counted grants' shares; below 0, the pool runs short before the next round
  Effective pre-money                                      $13,846,153.85              $13,000,000.00      $-846,153.85  (FD - U)·p: the holders' shares at the round price
  Flag                                     hires_after_next_round_ignored                                                1 hire starts after month 18 and is left out of the plan: the next round's own pool would cover it
  Flag                                               requested_above_plan                                                The requested pool is larger than the plan's: the difference column shows what the larger pool does to the price, the effective pre-money and who owns what
```

The plan's pool is t_plan = 1,400,000 × 16,000,000/(20,000,000 × 10,400,000) = 7/65, about 10.7692%: a top-up of
P = G - U = 400,000 shares at $20/13 a share. The requested 15% creates 1,076,923.077 new shares (14,000,000/13
exactly) at $13/9 a share, so the effective pre-money falls from $13,846,153.85 to $13,000,000.00, $846,153.85 lower
(11,000,000/13 exactly), and the founders hold 50.5556% instead of 53.8462% (91/180 against 7/13). At the next round
676,923.077 of the requested pool is still ungranted. The report never says which pool to accept.

**A raise pipeline (Company RA, made up).** A $4,000,000 round with a $2,500,000 lead cheque, $500,000 of firm and
$500,000 of soft commitments and one $400,000 pro rata. The founder's funnel: 40 investors with an intro asked (half
reach a first meeting, on the founder's own rate), 10 at a first meeting (30% go on to a partner meeting) and 2 at a
partner meeting (25% give a term sheet); the founder wants 3 term sheets. $1,200,000 in the bank burning $150,000 a
month on $30,000 of revenue, and 6 months allowed to raise:

```
equity_calculator raise_pipeline --round-size 4,000,000 --lead-cheque 2,500,000 --commitment "500000 kind=firm" \
    --commitment "250000 kind=soft" --commitment "250000 kind=soft" --pro-rata 400000 \
    --stage "Intro asked: investors=40 rate-percent=50" --stage "First meeting: investors=10 rate-percent=30" \
    --stage "Partner meeting: investors=2 rate-percent=25" --term-sheets-wanted 3 --cash-on-hand 1,200,000 \
    --phase "from-month=1 gross-burn=150000 revenue=30000" --months-to-raise 6
  Soft commitments, never counted (S)                                        $500,000.00  the soft commitments, shown on their own
  Room after the lead and the firm commitments                             $1,000,000.00  R - L - F
  Allocation left                                                            $600,000.00  R - L - F - P; below 0, more is counted than the round holds
  Stage 3, Partner meeting: needed here for 3 term sheets                             12  ceiling(W / the rate to a term sheet from here)
  Conversion, first stage to a term sheet                                        3.7500%  the product of every rate
  Expected term sheets from today's funnel (E)                                      2.75  the sum of each stage's investors × its rate to a term sheet; an expectation from the founder's rates, not a forecast
  First-stage targets needed, from an empty funnel                                    80  ceiling(W / the conversion)
  More first-stage targets needed beyond today's funnel                                7  ceiling((W - E) / the conversion); 0 when E >= W
  Runway with no raise (the runway plan's)                                  10.00 months  months until cash less the floor goes below zero, on the plan
  Start raising by (the runway plan's)                                       4.00 months  runway with no raise - months to raise, in months from today
  Flag                                                      soft_commitments_not_counted  At least one commitment is soft: soft commitments are shown on their own line and never counted against the round
  Flag                                                            funnel_short_of_wanted  On the founder's rates, today's funnel is expected to give fewer than the 3 term sheets wanted: see the more targets needed line
```

The lead and the firm commitment leave $1,000,000 of room, and the pro rata takes $400,000 of it: $600,000 is left to
allocate. The soft $500,000 is shown and never counted. The conversion is 1/2 × 3/10 × 1/4 = 3/80, and today's funnel
is expected to give E = 40 × 3/80 + 10 × 3/40 + 2 × 1/4 = 11/4 = 2.75 term sheets on those rates, short of 3: from an
empty funnel 3 term sheets need 80 first-stage targets, and today's funnel needs 7 more. The cash lasts 10 months
($1,200,000 / $120,000) with no raise, so with 6 months to raise the founder starts by month 4. The report never says
whom to pitch.

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
equity_calculator deal_check --investment I [--pre-money V] [--post-money P] [--stated-investor-percent X]
    [--fully-diluted-shares FD [--unissued-pool-shares U | --unissued-pool-percent UP] [--target-pool-percent T]
    [--pool-timing pre_money|post_money] [--safe "TERMS" | --note "TERMS"]...]
    [(--holder-percent H | --holder-shares HS) [--stated-holder-percent S]] [--cash-on-hand C]
    [--planned-monthly-gross-burn B [--planned-monthly-revenue R]]
    [--current-monthly-gross-burn B [--current-monthly-revenue R]] [--stated-runway-months M]
    [--use-of-funds AMOUNT|PCT%]... [--tolerance-points P] [--tolerance-percent Q]
    [--dilution-band-percent D] [--runway-band-months M]
equity_calculator runway_plan --cash-on-hand C [--cash-floor F] --phase "TERMS"...
    [--downside-phase "TERMS"... | [--downside-revenue-percent R] [--downside-gross-burn-percent G]]
    [--lean-phase "TERMS"... | [--lean-revenue-percent R] [--lean-gross-burn-percent G]]
    [--raise "TERMS"]... [--raise-use-of-funds "N AMOUNT|PCT%"]... [--milestone M]... [--months-to-raise T]
    [--stated-runway-months S] [--tolerance-points P] [--tolerance-percent Q] [--runway-band-months B]
equity_calculator metrics_check --period-months P [--recurring-unit monthly|annual]
    [--starting-recurring S [--new-recurring N] [--expansion-recurring E] [--contraction-recurring C]
    [--churned-recurring X] [--cohort-expansion-recurring E] [--cohort-contraction-recurring C]
    [--cohort-churned-recurring X]] [--month-total-revenue T [--month-one-time-revenue O]
    [--month-usage-revenue U]] [--customers-start S [--customers-lost L]] [--customers-new N
    [--customers-new-paid P]] [--sales-marketing-spend M [--gross-margin-percent G]] [--net-burn B]
    [--largest-customer-revenue L --period-revenue R] [--stated-arr A] [--stated-nrr-percent N]
    [--stated-grr-percent G] [--stated-churn-percent C [--stated-churn-basis BASIS]] [--stated-cac C]
    [--stated-cac-payback-months M] [--stated-burn-multiple X] [--stated-concentration-percent C]
    [--tolerance-points P] [--tolerance-percent Q] [--customer-segment smb|mid_market|enterprise]
    [--payback-band-months B] [--burn-multiple-band X] [--net-revenue-churn-band-percent C]
equity_calculator market_sizing --segment "TERMS"... [--top-down "TERMS"]... [--sensitivity "TERMS"]...
    [--population N] [--annual-revenue-today R] [--som-years Y] [--som-target T] [--stated-tam A]
    [--stated-sam A] [--stated-som A] [--tolerance-percent Q]
equity_calculator instrument_compare --founder-shares F --team-shares T --unissued-pool-shares U
    [--existing-series "TERMS"]... [--existing-safe "TERMS" | --existing-note "TERMS"]... --investment I
    --priced-pre-money V [--priced-target-pool-percent T] [--priced-pool-timing pre_money|post_money]
    --priced-preference "TERMS" [--note-valuation-cap K] [--note-discount-percent D]
    --note-interest-rate-percent R --note-compounding simple|annual|monthly [--note-stub-rule RULE]
    --note-months-to-conversion M [--note-maturity-months M] [--note-interest-paid-in-cash]
    --next-round "TERMS"... --exit E... [--pool-at-exit as_common|left_out]
equity_calculator pool_plan --fully-diluted-shares FD --unissued-pool-shares U [--founder-shares F]
    --pre-money V --investment I --requested-pool-percent T --next-round-month M --hire "ROLE: TERMS"...
equity_calculator raise_pipeline --round-size R [--lead-cheque L] [--commitment "AMOUNT kind=soft|firm"]...
    [--pro-rata A]... [--stage "NAME: TERMS"]... [--term-sheets-wanted W] [--cash-on-hand C [--cash-floor F]
    --phase "TERMS"... --months-to-raise M]
```

`deal_check` needs `--investment` and at least one of `--pre-money`, `--post-money` and `--stated-investor-percent`.
Its `--safe` and `--note` take the same terms as `round`'s. `--holder-shares` gives the holder group as a share count
of FD instead of `--holder-percent`, and `--unissued-pool-percent` gives the unissued pool as a percent of FD instead of
`--unissued-pool-shares`. Each `--use-of-funds` is one line of the deck's use of
funds, an amount (`1250000`) or a percent of the raise (`50%`), all lines the same kind. Give each stated percent and
the stated runway with the places the deck writes (`--stated-runway-months 18` for "18 months", not `18.0`), since a
figure that is the computed one rounded to those places is consistent.

`runway_plan` needs `--cash-on-hand` and at least one `--phase`, the plan's, the first starting at month 1. A downside
or a lean case is its own `--downside-phase` / `--lean-phase` items or the percents of the plan's revenue and gross
burn, not both. Each `--raise` is one option to compare, and each `--raise-use-of-funds` is one line of the raise it
names by number (`1` is the first `--raise`), an amount or a percent of that raise. `--milestone` is a month from
today; `--stated-runway-months` is the runway stated with no raise.

`metrics_check` needs `--period-months`, the one period every flow figure covers. Each part is the founder's own
figure: recurring revenue in the unit `--recurring-unit` names (monthly by default), customers as whole numbers,
and `--net-burn` positive when cash goes out (`--net-burn=-50000` for a cash-generative period, with `=` because
argparse reads a lone negative number as a flag). Give only what the document shows, each stated percent, months or
multiple with the places the document writes (`--stated-cac-payback-months 12` for "12 months", not `12.0`), since a
figure that is the computed one rounded to those places is consistent; each stated figure is checked when its parts
are there, and `--stated-churn-basis` (`logo`, `gross_revenue`, `net_revenue` or
`unlabelled`) says which churn the document means. A net revenue churn below zero goes in the same way:
`--stated-churn-percent -3` reads as a number, but `-3%` needs the `=` form, `--stated-churn-percent=-3%`. A stated retention or churn figure is checked over
`--period-months` and never annualised, so give the period the document's figure covers (1 for a monthly churn, 12
for an annual NRR) and run once per period when the document mixes them. A stated CAC is checked as blended CAC.

`market_sizing` needs at least one `--segment`, one group of buying customers with no overlap between groups. Each
count, price and share is the founder's own figure: a price is given with the months it covers
(`price-period-months=1` for a monthly price, 24 for a two-year device) and never turned into a year by hand, and
`take-rate-percent` is the share of the customers' spend the company keeps (a marketplace's fee). The SOM is
`obtainable-customers` (preferred) or `obtainable-percent` of the serviceable customers, not both. `--top-down` is a
cross-check only, compared with the bottom-up TAM unless `compare-to=sam`. Each `--sensitivity` names one field of
one segment by number (`1` is the first `--segment`) and its values, split on `/` (a comma there separates
thousands). `--population` is the population the segments are drawn from, to catch a buyer counted twice;
`--som-target` is the annual revenue the plan needs from this market; `--stated-som` and `--som-target` need a SOM in
every segment.

`instrument_compare` needs today's founder shares, the team's shares and the unissued pool (`0` for none: today's
fully diluted shares are built from them), the raise, option A's pre-money and series terms, option B's
interest rate, compounding and months until it converts, at least one `--next-round` (with none it is refused,
`no_next_round_given`, as the note converts only at a next round) and at least one `--exit`. Each `--next-round` is
an alternative for the one round after today, worked from today, never after the one before. Every term is the
founder's own figure: `--priced-preference standard` (and `standard` in a `--next-round`) only when the founder says
the terms are standard, 1x non-participating; otherwise give the multiple and participation. `--existing-series` takes
`--class`'s terms with `preference-multiple=` and `participation=` always given (that series' own terms; rank is 1
unless given), and `--existing-safe` and `--existing-note` take `--safe`'s and `--note`'s, an existing note with
`months-outstanding=` as of today (dates are refused) and `compounding=` always given. `--note-maturity-months` is
only compared with the months to conversion; nothing at maturity is modelled. `--pool-at-exit left_out` gives the pool
nothing at an exit.

`pool_plan` needs the fully diluted shares before the round, the unissued pool (`0` for none), the pre-money, the
raise, the term sheet's requested pool and the month the next round is expected (1 to 120 months from today), and at
least one `--hire` (with none it is refused, `no_hiring_plan_given`). Each `--hire` is the role in the founder's words
(letters, digits, spaces and `. , & / ( ) ' - + #`, starting with a letter or a digit, at most 40 characters), a
colon, then its terms. Every grant is given the same way, all in shares or all as percents of the post-round fully
diluted shares; a hire starting after `--next-round-month` is shown and left out. `--founder-shares`, when given, adds
the founders' ownership line. Every figure is the founder's own.

`raise_pipeline` needs the round size. Each `--commitment` is an amount and `kind=soft` or `kind=firm`, as the founder
marks it (with no kind it is refused, `commitment_kind_missing`); each `--pro-rata` is one existing investor's amount.
Each `--stage` is the stage's name in the founder's words (the same characters as a hire's role, plus `:`), a colon,
then `investors=N` (whole investors at that stage today) and `rate-percent=P` (the founder's rate to the next stage;
from the last stage, to a term sheet), in the funnel's order; `rate-basis=benchmark benchmark-source=TEXT` marks a
rate the founder took from a benchmark, the source running to the end of the stage. `--term-sheets-wanted` goes with
the stages. `--cash-on-hand`, `--cash-floor`, each `--phase` (the same terms as `runway_plan`'s) and
`--months-to-raise` give the start-raising month. Every figure is the founder's own.

`round` needs at least one `--safe` or `--note`, `dilution` at least one `--round` and `waterfall` at least one
`--class`. Each repeated flag is one instrument, round, class, phase, raise, segment, top-down figure, sensitivity
row or hire, given as one quoted string of `key=value` terms and
bare flags in any order, after the amount for a SAFE, the principal for a note or the role and a colon for a hire,
which comes first:

| Flag                  | Terms                                                                                                                                                                                                                                                                                       |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--safe`              | `AMOUNT [valuation-cap=X] [discount-percent=D] [mfn]`                                                                                                                                                                                                                                       |
| `--note`              | `PRINCIPAL interest-rate-percent=R (months-outstanding=M \| issue-date=YYYY-MM-DD conversion-date=YYYY-MM-DD) [compounding=simple\|annual\|monthly] [stub-rule=simple\|fractional_power] [day-count=actual_365\|actual_360] [valuation-cap=X] [discount-percent=D] [interest-paid-in-cash]` |
| `--round`             | `(investor-percent=N \| pre-money=V investment=I) [pool-percent=P]`                                                                                                                                                                                                                         |
| `--class`             | `shares=S invested=I [preference-multiple=M] [rank=K] [participation=none\|full\|capped] [cap-multiple=C]` (a cap only with `capped`)                                                                                                                                                       |
| `--phase`             | `from-month=M gross-burn=G [revenue=R]` (also `--downside-phase` and `--lean-phase`)                                                                                                                                                                                                        |
| `--raise`             | `amount=I [lands-month=L] [stated-runway-months=M [stated-runway-from=today\|landing]]` (a basis with no stated runway is refused)                                                                                                                                                          |
| `--segment`           | `customers=N price=P [price-period-months=M] [units-per-customer=U] [take-rate-percent=R] [serviceable-percent=S] [obtainable-percent=O \| obtainable-customers=C] [customers-today=T]`                                                                                                     |
| `--top-down`          | `amount=A [comparable-percent=C] [compare-to=tam\|sam]`                                                                                                                                                                                                                                     |
| `--sensitivity`       | `field=F segment=K values=V1/V2/...` (F one of `customers`, `price`, `units-per-customer`, `take-rate-percent`, `serviceable-percent`, `obtainable-percent`, `obtainable-customers`; 1 to 4 values)                                                                                         |
| `--priced-preference` | `standard [rank=K]` or `preference-multiple=M participation=none\|full\|capped [cap-multiple=C] [rank=K]`                                                                                                                                                                                   |
| `--next-round`        | `pre-money=V investment=I [target-pool-percent=T] [pool-timing=pre_money\|post_money]` and the series' terms as `--priced-preference` takes them                                                                                                                                            |
| `--hire`              | `ROLE: start-month=M (grant-shares=S \| grant-percent=P)`: the role and a colon first, the grant in shares or as a percent of the post-round fully diluted shares                                                                                                                           |

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
most 50 SAFEs and notes, a dilution at most 20 rounds, a waterfall at most 12 preferred classes, ranked 1 to 12, and a
deal check at most 50 SAFEs and notes and 20 use-of-funds lines. A runway plan takes at most 3 cases (the plan, a
downside and a lean case) of at most 12 phases, 6 raises of at most 20 use-of-funds lines each, and 10 milestones;
its months are at most 600 and its months to raise at most 60. A metrics check covers one period of 1 to 36
months, and its customer counts are whole numbers below 1e16. A market size takes at most 8 segments, 3 top-down
figures and 6 sensitivity rows of 1 to 4 values each; a price covers at most 120 months and the SOM horizon is 1 to
20 years. A comparison takes at most 6 existing series, 4 existing SAFEs and notes, 4 next rounds and 6 exits; its
note converts within 600 months, an existing note's months plus those included. A pool plan takes at most 40 hires,
each starting within 120 months, and its next round comes within the same. A raise pipeline takes at most 40
commitments, 20 pro rata amounts and 8 stages of at most 10,000 investors each, and at most 100 term sheets wanted;
its runway takes the runway plan's limits.
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

There is one sheet per scenario (`Investor`, `Employee`, `Pool`, `Convertibles` for the round, `Dilution`, `Vesting`,
`Waterfall`, `Deal check`, `Runway plan`, `Metrics check`, `Market sizing`, `Priced vs note`, `Pool plan` or
`Raise pipeline`):

- Row 1 is a bold header, frozen in place: `Line`, one value column (two for the pool, one per timing) and
  `How it is computed`.
- Every value cell holds the model's display rounding as a number, under its unit's format (a live investor
  sheet's inputs excepted, below). Fractions use `0.00%`,
  money `"$"#,##0`, a price per share `"$"#,##0.000000`, shares `#,##0`, customer counts `#,##0.00`, multipliers `0.0000"x"` and months
  `0.00" months"`.
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
  ownership and post-money (pool and round), the stake lost in all (dilution), vested in all and the grant (vesting), the total paid out
  (waterfall), the pre-money split and use-of-funds totals (deal check), each raise's use-of-funds total (runway plan), and a market size's totals across its segments (customers, gross spend, TAM, SAM and SOM). A live total adds the rounded cells, so it can differ from the model's exact total in the last place
  kept: a cent on the investor's post-money, a thousandth of a share on the pool's total shares, 0.000001 on its total
  ownership. The number formats hide that difference.
- The pool's and the round's value rows, the waterfall's payouts, a deal check's pre-money split and percent
  use-of-funds lines, and a market size's segment figures (to the cent, or a hundredth of a customer) are rounded by
  largest remainder, so they add up to their rounded total exactly. A segment's buying customers line shows that
  rounding too: when it is not the typed count (0.335 shows 0.34 in one segment and 0.33 in the next), its
  how-column says "given, shown rounded so the segments add up to the total".
- Verdict cells are coloured by conditional formatting: green for accept, grant and in the money, amber for break
  even and at the money, red for reject, no grant and underwater. A deal check's, a runway plan's, a metrics check's and a market size's verdicts are
  green for consistent, red for mismatch and amber for not checked; a runway plan's milestones are green when covered and red
  when short. A waterfall choice is blue when the class converts
  and grey when it stays: neither is good or bad. The investor verdict recolours itself when an input changes;
  elsewhere, typing a different verdict recolours the cell.
- The assumptions follow two rows below, under their own bold header: `Assumption`, `Setting`, `Statement` and
  `Source`.
- Column widths are set so labels and formulas are readable without resizing.

## Exactness

Inside, every number is a `Fraction`. Inputs arrive as `Decimal` (the models refuse NaN and infinity, and hold every
number to the limits above) and share counts as plain integers (a bool, a float or a numeric string is refused, never
read as a count). The output carries both the exact fraction and a `Decimal` rounded half away from zero at a fixed
number of places (12.125 months prints 12.13, the figure the rounding test of a document's stated figure gives too):
6 places for ratios and prices, 2 for money and months, 3 for shares. Three exceptions: a market's unit price
the founder typed (a segment's price, a sensitivity base or value) is shown exactly, to the cent at least, with no
trailing zeros past it ($400.00, $0.0075, $0.00000125, $0.3333333); a break-even price, which is worked, shows
the fewest places from 2 that give the same figure as 6 (a price under $0.00001 keeps two significant digits, up to 15
places); and a runway plan's required raise is rounded up to the cent, so the amount shown always covers. Rounding is
integer arithmetic. No step reads or sets the global decimal context, so a caller's `decimal.localcontext()` cannot
change a result, and the note stub's private context sets every field, so a changed `decimal.DefaultContext` cannot
either.

One step is not exact: a note with `stub-rule=fractional_power` (the default) and a stub left over raises its growth
to a fractional power, which has no exact rational value. It is computed in a private 50-digit decimal context, then
rounded to the cent like every note's amount, and its assumption says it is approximate. A note with
`stub-rule=simple` or `compounding=simple` stays exact, and one that ran a whole number of periods has no stub, so it
compounds exactly under either stub rule.

Verdicts, checks and flags use the exact values, never the rounded ones shown. So a line can look as if it contradicts
the verdict beside it: a runway of 17.996 months prints as 18.00 months beside a flag for a raise lasting under 18,
and a difference of 0.50004 points prints as 0.5000% beside a 0.5-point tolerance and the verdict mismatch. A deck that
copies a figure printed from an exact half (a runway of 12.125 months, printed 12.13) is consistent, and its difference
line prints -0.01 months beside two equal figures: the exact difference, -0.005 months, is half a hundredth, rounded
away from zero like every figure. The exact fraction of each is in the JSON.

Each number shown is its own exact value rounded once. So rounded parts can miss a rounded total by one in the last
place shown: in the report, a thousandth of a share or 0.0001% beside a total line. The pool's and the round's value
rows, the waterfall's payouts and a deal check's pre-money split and percent use-of-funds lines are the exception,
split to the cent by largest remainder.

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

The `deal_check` scenario adds these, each only when the input uses it, then the nested round's or pool's own rows
(above) that it does not already list:

| Key                   | Default                                                                                                                              | How to change it                            | Source                                                |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- | ----------------------------------------------------- |
| `post_money_rule`     | post-money = V + I                                                                                                                   | fixed                                       | YC (the Post-Money Safe User Guide)                   |
| `valuation_order`     | pre-money, then post-money, then the stated percent                                                                                  | give one valuation figure                   | unverified                                            |
| `back_solve`          | post-money = I / percent                                                                                                             | give a pre- or post-money                   | unverified (standard arithmetic)                      |
| `holder_scaling`      | h × the share of the stake every pre-round share keeps                                                                               | fixed                                       | unverified                                            |
| `effective_pre_money` | (FD - U) × price                                                                                                                     | fixed                                       | unverified                                            |
| `runway_rule`         | (cash + I) / monthly burn, net and gross                                                                                             | fixed                                       | unverified (standard arithmetic)                      |
| `runway_band`         | 18 months                                                                                                                            | `--runway-band-months`                      | unverified (a common benchmark, not a rule)           |
| `tolerance`           | 0.5 points; 2% relative; a stated percent or runway that is the computed figure rounded to its places also holds; one flag beside it | `--tolerance-points`, `--tolerance-percent` | unverified (the rounding test is standard arithmetic) |
| `dilution_band`       | 25%                                                                                                                                  | `--dilution-band-percent`                   | unverified (a common benchmark, not a rule)           |
| `use_of_funds_rule`   | the lines add up to the raise                                                                                                        | fixed                                       | unverified                                            |

The `runway_plan` scenario adds these, each only when the input uses it:

| Key                   | Default                                                                                                                | How to change it                            | Source                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------------------------------------- |
| `runway_rule`         | cash on hand less the floor, plus the raise, run down by the phased net burn                                           | `--cash-floor`                              | unverified (standard arithmetic)                                            |
| `phase_rule`          | a phase runs until the next starts; the last runs on                                                                   | fixed                                       | unverified (a modelling choice)                                             |
| `landing_rule`        | the whole raise lands at once, after its whole months                                                                  | `lands-month=`                              | unverified (a modelling choice)                                             |
| `derived_case_rule`   | the plan's phases scaled by the case's percents                                                                        | give the case its own phases                | unverified (a modelling choice)                                             |
| `milestone_rule`      | covered when the cash lasts to the month plus the months to raise                                                      | `--months-to-raise`                         | YC seed guide ("next “fundable” milestone"); the months to raise unverified |
| `required_raise_rule` | the smallest raise keeping cash at or above the floor to the target                                                    | fixed                                       | unverified (standard arithmetic)                                            |
| `tolerance`           | 0.5 points; 2% relative; a stated runway that is the computed one rounded to its places also holds; one flag beside it | `--tolerance-points`, `--tolerance-percent` | unverified (the rounding test is standard arithmetic)                       |
| `runway_band`         | 18 months                                                                                                              | `--runway-band-months`                      | YC seed guide ("usually 12-18"; 18 is its top; a benchmark, not a rule)     |
| `use_of_funds_rule`   | the lines add up to the raise                                                                                          | fixed                                       | unverified                                                                  |

The `metrics_check` scenario adds these, each only when the input uses it:

| Key                      | Default                                                                                                                                                          | How to change it                              | Source                                                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `period_rule`            | every flow is for the one period; nothing annualised or compounded                                                                                               | `--period-months`                             | unverified (a modelling choice)                                                                                             |
| `arr_rule`               | ARR = k × recurring revenue (the movement's); ARR from the latest month = 12 × its recurring revenue; run-rate = 12 × its whole revenue: only the figures worked | `--recurring-unit`                            | a16z ("16 More Startup Metrics", item 2)                                                                                    |
| `retention_rule`         | GRR = (S - C - X)/S; NRR = (S + E - C - X)/S; new customers left out (primed, C' and so on, once a starting-customers figure is given)                           | fixed                                         | Bessemer for the definitions; leaving new customers out unverified                                                          |
| `cohort_rule`            | the period's totals; with `--cohort-*` figures, which movements are the starting customers' own and which are totals                                             | the `--cohort-*` figures                      | unverified (a modelling choice)                                                                                             |
| `churn_rule`             | logo, gross and net revenue churn over the period                                                                                                                | fixed                                         | a16z ("16 Startup Metrics", item 11; per month)                                                                             |
| `cac_rule`               | blended = spend / new customers; paid = spend / paid-channel customers                                                                                           | fixed                                         | a16z ("16 Startup Metrics", item 8)                                                                                         |
| `payback_rule`           | spend / (new monthly recurring revenue × gross margin)                                                                                                           | `--gross-margin-percent`                      | Bessemer (on gross margin); the formula unverified                                                                          |
| `burn_multiple_rule`     | net burn / net new ARR; none at or below zero, a stated one not checked                                                                                          | fixed                                         | Sacks (the formula, no ratio before revenue, and approaching 0 as burn reaches 0); working none at zero or below unverified |
| `concentration_rule`     | largest customer / the period's revenue; no benchmark                                                                                                            | fixed                                         | a16z ("16 More Startup Metrics", item 14)                                                                                   |
| `tolerance`              | 0.5 points; 2% relative; a percent, months or multiple that is the computed figure rounded to its places also holds; one flag beside it                          | `--tolerance-points`, `--tolerance-percent`   | unverified (the rounding test is standard arithmetic)                                                                       |
| `payback_band`           | the segment's target: 12, 18 or 24 months; with no margin, set against the revenue-only payback as a floor                                                       | `--customer-segment`, `--payback-band-months` | Bessemer (a benchmark, not a rule)                                                                                          |
| `burn_multiple_band`     | 3x                                                                                                                                                               | `--burn-multiple-band`                        | Sacks (a benchmark, not a rule)                                                                                             |
| `net_revenue_churn_band` | 2% a month, one-month periods only                                                                                                                               | `--net-revenue-churn-band-percent`            | Skok (a benchmark, not a rule)                                                                                              |

The `market_sizing` scenario adds these: `bottom_up_rule`, `annual_rule` and `sam_rule` always, the rest only when
the input uses them:

| Key                | Default                                                                    | How to change it                       | Source                                                                     |
| ------------------ | -------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------------------------- |
| `bottom_up_rule`   | TAM = customers × annual revenue from one customer, per segment, summed    | fixed                                  | YC pitch guide (question 2)                                                |
| `annual_rule`      | annual price = price × 12 / the months it covers; no growth or churn       | `price-period-months=`                 | YC pitch guide (the two-year lifecycle); the straight-line year unverified |
| `revenue_rule`     | TAM = the customers' spend × the take rate (only below 100%)               | `take-rate-percent=`                   | YC seed guide (glossary: TAM)                                              |
| `sam_rule`         | SAM = TAM × the serviceable percent; 100% when none is given               | `serviceable-percent=`                 | unverified (common usage)                                                  |
| `som_rule`         | SOM = the customers to win × annual revenue from one; a straight-line path | `obtainable-customers=`, `--som-years` | unverified (common usage)                                                  |
| `top_down_rule`    | a top-down figure is a cross-check only                                    | fixed                                  | YC pitch guide (question 2)                                                |
| `population_rule`  | the segments' customers at most the population                             | `--population`                         | unverified (standard arithmetic)                                           |
| `sensitivity_rule` | one field of one segment at a time, the rest at base                       | fixed                                  | unverified (standard arithmetic)                                           |
| `tolerance`        | 2% relative                                                                | `--tolerance-percent`                  | unverified                                                                 |

The `instrument_compare` scenario carries the round's rows (the SAFE rows when an existing SAFE converts, the note
rows, `converted_shares_in_pre_money`, `tie_rule`, `fractional_shares`, `search`) and the waterfall's rows, and adds
these (`standard_preference` only when a series is given as standard):

| Key                         | Default                                                                                     | How to change it                                  | Source                                      |
| --------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------- | ------------------------------------------- |
| `pool_timing`               | each round's own: option A's today and each next round's                                    | `--priced-pool-timing`, `pool-timing=`            | unverified                                  |
| `comparison_rule`           | the same raise, next rounds and exits both ways; never a pick                               | fixed                                             | method                                      |
| `note_outstanding_today`    | option B issues no shares until the next round                                              | fixed                                             | unverified (notes have no standard form)    |
| `note_price_rule`           | the lower of cap price (cap / FD) and discount price; the round price with neither          | `--note-valuation-cap`, `--note-discount-percent` | unverified (notes have no standard form)    |
| `note_interest_terms`       | the founder's rate, compounding and months, rounded to the cent                             | the `--note-*` interest flags                     | the founder's terms                         |
| `maturity_rule`             | the maturity is only compared with the months to conversion                                 | `--note-maturity-months`                          | unverified (the note's own terms decide)    |
| `exit_after_next_round`     | every exit follows the next round                                                           | fixed                                             | method                                      |
| `existing_instruments_rule` | existing SAFEs and notes convert at the first priced round: today's in A, the next one in B | fixed                                             | unverified (each instrument's terms decide) |
| `series_terms`              | converted shares take their round's series terms, a preference on the amount converted      | fixed                                             | unverified (shadow series vary by deal)     |
| `series_rank`               | rank 1 when not given                                                                       | `rank=`                                           | method                                      |
| `standard_preference`       | 1x, non-participating, used only where the founder said standard                            | `--priced-preference`, a `--next-round`'s terms   | unverified                                  |
| `pool_at_exit`              | the pool takes part as common                                                               | `--pool-at-exit left_out`                         | method                                      |
| `money_split`               | largest remainder within each option                                                        | fixed                                             | display convention                          |
| `difference_rounding`       | B - A of the exact values, rounded once                                                     | fixed                                             | display convention                          |

The `pool_plan` scenario carries the pool's `target_pool`, `price_basis` and `money_split` rows word for word, and
these:

| Key                 | Default                                                                                             | How to change it                                        | Source                                    |
| ------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | ----------------------------------------- |
| `pool_timing`       | both columns create the pool in the pre-money                                                       | fixed (the `pool` scenario works the post-money timing) | unverified (common term-sheet practice)   |
| `plan_pool`         | the plan's pool holds exactly the grants to the next round, U + P = G; no top-up when they fit in U | fixed                                                   | unverified (this calculator's convention) |
| `next_round_cutoff` | a hire starting on or before the next round's month counts                                          | `--next-round-month`                                    | unverified                                |
| `grant_unit`        | every grant in shares, or every grant as a percent of the post-round fully diluted shares           | each `--hire`'s grant                                   | unverified                                |
| `share_rounding`    | exact fractions of shares                                                                           | fixed                                                   | unverified                                |
| `difference`        | requested - plan of the exact values, rounded once; neither column is a recommendation              | fixed                                                   | display convention                        |

The `raise_pipeline` scenario has these rows, each only when its input is given, and with cash and burn the runway
plan's own rows (`runway_rule`, `phase_rule`, ...) word for word after them:

| Key                    | Default                                                                     | How to change it                       | Source                                    |
| ---------------------- | --------------------------------------------------------------------------- | -------------------------------------- | ----------------------------------------- |
| `allocation_rule`      | left = R - L - firm - pro rata; a soft commitment shown, never counted      | each `--commitment`'s `kind=`          | unverified (standard arithmetic)          |
| `pro_rata_rule`        | each pro rata amount counted in full                                        | `--pro-rata`                           | unverified (a planning convention)        |
| `stage_counting`       | each investor counted once, at the furthest stage it has reached            | fixed                                  | unverified (a modelling choice)           |
| `expected_term_sheets` | E = Σ investors × the rate to a term sheet from their stage; not a forecast | fixed                                  | unverified (expected values)              |
| `rate_basis`           | every rate the founder's own                                                | `rate-basis=benchmark` with its source | the founder                               |
| `targets_needed`       | each count needed rounded up to whole investors                             | fixed                                  | unverified (standard arithmetic)          |
| `start_raising_rule`   | the runway plan's runway with no raise less the months to raise             | `--months-to-raise`                    | unverified (the runway plan's arithmetic) |

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
