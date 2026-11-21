"""The investor sheet's live formulas, written, read back and worked the way a spreadsheet works them.

File output only: no DB, no network. Each test writes a workbook under pytest's temporary directory and reads it back
with openpyxl. A small evaluator below works the written formulas in binary floating point, as Excel and LibreOffice
do, so the tests check what a spreadsheet would show: the verdict it computes agrees with the model's exact verdict,
break even included, and editing one input cell re-works the test.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from equity_calculator.investor_live import spreadsheet_agrees
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity import InvestorResult
from equity_calculator.workbook import save_workbook
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from tests.support import employee, investor

_SEED = 20261121
_RANDOM_CASES = 400
_TOKEN = re.compile(
    r"\s*(?:(?P<number>\d+(?:\.\d+)?)|(?P<cell>[A-Z]+\d+)|(?P<name>[A-Z]+)(?=\()"
    r'|"(?P<text>[^"]*)"|(?P<op>[-+*/()=<>,]))'
)
_CENT = Fraction(1, 100)
_HALF_MILLIONTH = Fraction(1, 2 * 10**6)
_RATIO_TOLERANCE = Fraction(1, 10**9)


@dataclass
class _Spreadsheet:
    """One read-back sheet, worked like a spreadsheet: numbers as binary floats, formulas evaluated on demand."""

    page: Worksheet
    edits: dict[str, float] = field(default_factory=dict)

    def value(self, coordinate: str) -> float | str:
        if coordinate in self.edits:
            return self.edits[coordinate]
        raw = self.page[coordinate].value
        if isinstance(raw, str) and raw.startswith("="):
            return _Formula(raw[1:], self).evaluate()
        if isinstance(raw, str):
            return raw
        return float(Decimal(str(raw)))


@dataclass
class _Formula:
    """A recursive-descent reader for the formulas the workbook writes: + - * /, comparisons, IF and ROUND."""

    text: str
    sheet: _Spreadsheet
    tokens: list[tuple[str, str]] = field(init=False)
    at: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self.tokens = []
        position = 0
        while position < len(self.text):
            match = _TOKEN.match(self.text, position)
            assert match is not None and match.lastgroup is not None, self.text[position:]
            self.tokens.append((match.lastgroup, match.group(match.lastgroup)))
            position = match.end()

    def evaluate(self) -> float | str:
        result = self._comparison()
        assert self.at == len(self.tokens), self.text
        return result

    def _peek(self) -> str:
        return self.tokens[self.at][1] if self.at < len(self.tokens) else ""

    def _take(self, expected: str | None = None) -> tuple[str, str]:
        token = self.tokens[self.at]
        assert expected is None or token[1] == expected, (self.text, expected, token)
        self.at += 1
        return token

    def _comparison(self) -> float | str:
        left = self._additive()
        if self._peek() in ("=", ">", "<"):
            operator = self._take()[1]
            right = self._additive()
            assert isinstance(left, float) and isinstance(right, float)
            return float({"=": left == right, ">": left > right, "<": left < right}[operator])
        return left

    def _additive(self) -> float | str:
        value = self._multiplicative()
        while self._peek() in ("+", "-"):
            operator = self._take()[1]
            right = self._multiplicative()
            assert isinstance(value, float) and isinstance(right, float)
            value = value + right if operator == "+" else value - right
        return value

    def _multiplicative(self) -> float | str:
        value = self._unary()
        while self._peek() in ("*", "/"):
            operator = self._take()[1]
            right = self._unary()
            assert isinstance(value, float) and isinstance(right, float)
            value = value * right if operator == "*" else value / right
        return value

    def _unary(self) -> float | str:
        if self._peek() == "-":
            self._take()
            value = self._unary()
            assert isinstance(value, float)
            return -value
        return self._primary()

    def _primary(self) -> float | str:
        kind, text = self._take()
        if kind == "number":
            return float(text)
        if kind == "text":
            return text
        if kind == "cell":
            return self.sheet.value(text)
        if kind == "name":
            return self._call(text)
        assert text == "(", (self.text, text)
        value = self._comparison()
        self._take(")")
        return value

    def _call(self, name: str) -> float | str:
        self._take("(")
        arguments = [self._comparison()]
        while self._peek() == ",":
            self._take()
            arguments.append(self._comparison())
        self._take(")")
        if name == "IF":
            condition, when_true, when_false = arguments
            return when_true if condition else when_false
        assert name == "ROUND", name
        number, places = arguments
        assert isinstance(number, float) and isinstance(places, float)
        # Excel's ROUND rounds half away from zero on the number's shortest decimal form.
        exponent = Decimal(1).scaleb(-int(places))
        return float(Decimal(repr(number)).quantize(exponent, rounding=ROUND_HALF_UP))


def _read_back(tmp_path: Path, result: InvestorResult) -> tuple[_Spreadsheet, dict[str, int]]:
    sheet = sheet_for(result)
    target = tmp_path / "investor.xlsx"
    save_workbook(target, (sheet,))
    page = load_workbook(target)[sheet.title]
    return _Spreadsheet(page), {line.key: row for row, line in enumerate(sheet.lines, start=2)}


def test_every_derived_investor_line_is_a_live_formula_over_its_inputs(tmp_path: Path) -> None:
    """With the amounts and a holder: the stake, R, m*, g*, the verdict and the holder's lines are all formulas.

    The formulas are written out here rather than read from the layout, so a formula that names the wrong line fails.
    """
    sheet, rows = _read_back(
        tmp_path, investor(pre_money="8000000", investment="2000000", outcome_multiplier="1.3", holder_percent="50")
    )
    cell = {key: f"B{row}" for key, row in rows.items()}
    n, m, r = cell["equity_sold"], cell["outcome_multiplier"], cell["value_ratio"]
    h, v, i = cell["holder_before"], cell["pre_money"], cell["investment"]
    expected = {
        "equity_sold": f"={i}/({v}+{i})",
        "post_money": f"=SUM({v}:{i})",
        "value_ratio": f"=(1-{n})*{m}",
        "break_even_multiplier": f"=1/(1-{n})",
        "break_even_growth": f"={n}/(1-{n})",
        "verdict": f'=IF(ROUND({r}-1,12)>0,"accept",IF(ROUND({r}-1,12)=0,"break_even","reject"))',
        "holder_after": f"={h}*(1-{n})",
        "holder_value_before": f"={h}*{v}",
        "holder_value_after": f'={cell["holder_value_before"]}*{r}',
    }
    written = {key: sheet.page[coordinate].value for key, coordinate in cell.items()}

    assert {key: value for key, value in written.items() if str(value).startswith("=")} == expected
    assert sheet.value(cell["verdict"]) == "accept"


def test_a_stake_given_as_a_percent_is_an_input_cell_not_a_formula(tmp_path: Path) -> None:
    """Without the amounts the stake is given, so it is the number to edit; R and the verdict still follow it."""
    sheet, rows = _read_back(tmp_path, investor(equity_percent="7", outcome_multiplier="1.10"))

    assert sheet.page[f"B{rows['equity_sold']}"].value == pytest.approx(0.07)
    assert sheet.page[f"B{rows['outcome_multiplier']}"].value == pytest.approx(1.1)
    assert str(sheet.page[f"B{rows['verdict']}"].value).startswith("=IF(")


def test_editing_the_multiplier_flips_the_verdict(tmp_path: Path) -> None:
    """7% for a 10% gain is accepted; edit the one multiplier cell to 1.05 and the sheet rejects, as the model does."""
    sheet, rows = _read_back(tmp_path, investor(equity_percent="7", outcome_multiplier="1.10"))
    multiplier, verdict, ratio = (f"B{rows[key]}" for key in ("outcome_multiplier", "verdict", "value_ratio"))

    assert sheet.value(verdict) == "accept"
    sheet.edits[multiplier] = 1.05
    assert sheet.value(verdict) == "reject"
    assert sheet.value(ratio) == pytest.approx(0.9765)
    assert investor(equity_percent="7", outcome_multiplier="1.05").verdict == "reject"


def test_editing_an_amount_re_works_the_stake_and_the_verdict(tmp_path: Path) -> None:
    """From the amounts, a bigger investment sells more of the company: 2M on 8M breaks even at 1.25, 2.5M rejects."""
    sheet, rows = _read_back(tmp_path, investor(pre_money="8000000", investment="2000000", outcome_multiplier="1.25"))
    investment, stake, verdict = (f"B{rows[key]}" for key in ("investment", "equity_sold", "verdict"))

    assert sheet.value(verdict) == "break_even"
    sheet.edits[investment] = 2500000.0
    assert sheet.value(stake) == pytest.approx(2.5 / 10.5)
    assert sheet.value(verdict) == "reject"


_BREAK_EVEN_AND_EDGE_CASES: list[dict[str, str]] = [
    {"equity_percent": "7", "outcome_multiplier": "1.10"},
    {"equity_percent": "7", "outcome_multiplier": "1.05"},
    {"equity_percent": "20", "outcome_multiplier": "1.25"},
    {"equity_percent": "50", "outcome_multiplier": "2"},
    {"equity_percent": "0.0001", "outcome_multiplier": "1.000001"},
    {"equity_percent": "0.0001", "outcome_multiplier": "1.000002"},
    {"pre_money": "2000000", "investment": "1000000", "outcome_multiplier": "1.5"},
    {"pre_money": "9000000", "investment": "1000000", "outcome_multiplier": "1.111111"},
    {"pre_money": "8000000", "investment": "2000000", "outcome_multiplier": "1.25", "holder_percent": "62.5"},
    {"equity_percent": "33.3333", "outcome_multiplier": "1.499999", "holder_percent": "10"},
    # Finer than the sheet displays: the inputs are held at full precision, so the formulas see what was given.
    {"equity_percent": "20.00004", "outcome_multiplier": "1.25"},
    {"equity_percent": "20", "growth_percent": "25.00001"},
    {"equity_percent": "0.00000001", "outcome_multiplier": "1"},
    {"pre_money": "1000000000", "investment": "1000000", "outcome_multiplier": "1.1", "holder_percent": "12.345678"},
]

# Inputs a spreadsheet's floating point cannot work to the model's answer: R within 10^-11 of 1 without being 1 (the
# first two), and a stake so close to 100% that 1 - n loses its digits (the last). Their sheets hold the model's values.
_STATIC_CASES: list[dict[str, str]] = [
    {"pre_money": "40242254.04", "investment": "1683574.94", "outcome_multiplier": "1.041836"},
    {"pre_money": "36744646.63", "investment": "48974146.90", "outcome_multiplier": "2.332824"},
    {"equity_percent": "99.9999999", "outcome_multiplier": "2000000000"},
]


def _random_cases() -> list[dict[str, str]]:
    """Seeded inputs: percents to 4 or 7 places, multipliers to 6, money to cents, holder stakes to 6 places."""
    draw = random.Random(_SEED)
    cases: list[dict[str, str]] = []
    for index in range(_RANDOM_CASES):
        multiplier = f"{draw.randint(500_000, 3_000_000) / 1_000_000:.6f}"
        holder = {"holder_percent": f"{draw.randint(1, 100_000_000) / 1_000_000:.6f}"} if index % 3 == 0 else {}
        if index % 4 == 1:
            stake = {"equity_percent": f"{draw.randint(1, 999_999) / 10_000:.4f}"}
        elif index % 4 == 3:
            stake = {"equity_percent": f"{draw.randint(1, 999_999_999) / 10_000_000:.7f}"}
        else:
            stake = {
                "pre_money": f"{draw.randint(100_000_00, 100_000_000_00) / 100:.2f}",
                "investment": f"{draw.randint(10_000_00, 50_000_000_00) / 100:.2f}",
            }
        cases.append({**stake, "outcome_multiplier": multiplier, **holder})
    return cases


def _is_live(sheet: _Spreadsheet, rows: dict[str, int]) -> bool:
    return str(sheet.page[f"B{rows['verdict']}"].value).startswith("=")


@pytest.mark.parametrize("fields", _BREAK_EVEN_AND_EDGE_CASES + _STATIC_CASES + _random_cases())
def test_the_spreadsheets_verdict_agrees_with_the_exact_model(tmp_path: Path, fields: dict[str, str]) -> None:
    """Worked in floating point from the written cells, the verdict is the model's and every number is within its
    display rounding: half a millionth on R and the holder's stake after, half a cent on the dollar values. On a live
    sheet R is also within one part in a billion.
    """
    result = investor(**fields)
    sheet, rows = _read_back(tmp_path, result)

    assert sheet.value(f"B{rows['verdict']}") == result.verdict, fields
    computed_ratio = Fraction(sheet.value(f"B{rows['value_ratio']}"))
    ratio_tolerance = _RATIO_TOLERANCE if _is_live(sheet, rows) else _HALF_MILLIONTH
    assert abs(computed_ratio - result.value_ratio.exact) <= ratio_tolerance, fields
    holder = result.holder
    if holder is not None:
        stake_after = Fraction(sheet.value(f"B{rows['holder_after']}"))
        assert abs(stake_after - holder.stake_after.exact) <= _HALF_MILLIONTH, fields
    if holder is not None and holder.value_after is not None:
        value_after = Fraction(sheet.value(f"B{rows['holder_value_after']}"))
        assert abs(value_after - holder.value_after.exact) <= _CENT / 2, fields


def test_inputs_finer_than_the_display_stay_live_at_full_precision(tmp_path: Path) -> None:
    """20.00004% is written as 0.2000004, not the 20.0000% it displays as, so the sheet rejects as the model does."""
    sheet, rows = _read_back(tmp_path, investor(equity_percent="20.00004", outcome_multiplier="1.25"))

    assert _is_live(sheet, rows)
    assert sheet.page[f"B{rows['equity_sold']}"].value == pytest.approx(0.2000004, abs=1e-15)
    assert sheet.value(f"B{rows['verdict']}") == "reject"


@pytest.mark.parametrize("fields", _STATIC_CASES)
def test_inputs_floating_point_cannot_decide_get_the_models_values(tmp_path: Path, fields: dict[str, str]) -> None:
    """No formula at all on such a sheet: every cell is the model's display rounding and the verdict is its own."""
    result = investor(**fields)
    sheet, rows = _read_back(tmp_path, result)

    assert not spreadsheet_agrees(result)
    assert not any(str(sheet.page[f"B{row}"].value).startswith("=") for key, row in rows.items() if key != "post_money")
    assert sheet.page[f"B{rows['verdict']}"].value == result.verdict


def test_only_the_investor_sheet_carries_line_formulas() -> None:
    """The employee sheet keeps the model's values: its verdicts stay as written (only totals are live elsewhere)."""
    sheet = sheet_for(employee(gain_percent="20", offered_percent="7"))

    assert not any(line.formula for line in sheet.lines)
