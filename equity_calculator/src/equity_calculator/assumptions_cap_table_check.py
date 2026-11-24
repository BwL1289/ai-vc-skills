"""The labelled assumptions of a cap table check, each with its source, merged with the nested round's and dilution's.

Only the fully diluted measure has a source read in full here (Sam Altman's "Employee Equity", which measures grants
as a share of the fully diluted shares). How preferred, warrants and options count, that SAFEs and notes stay out
until they convert, the tolerance and the rounding test are marked unverified: each is a convention a lawyer or the
company's own documents settle. Legal validity is never checked, and the last of the cap table's own rows says so;
the nested round's and dilution's rows follow it. A row appears only when the input uses it.
"""

from __future__ import annotations

from equity_calculator.assumptions import ALTMAN_FULLY_DILUTED_SOURCE, UNVERIFIED
from equity_calculator.schemas.equity_cap_table_check import CapTableCheckInput, PathStart
from equity_calculator.schemas.equity_common import EquityAssumption

__all__ = ["cap_table_check_assumptions"]

_LAWYER = f"{UNVERIFIED} (the company's charter and plan decide; a question for its lawyer)"
_WARRANT_LAWYER = f"{UNVERIFIED} (the warrant decides; a question for the company's lawyer)"


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _count_rows(inputs: CapTableCheckInput) -> list[EquityAssumption]:
    """What the fully diluted shares count, and how each kind of class is counted in them."""
    kinds = {item.kind for item in inputs.classes}
    rows = [
        _assumption(
            "fully_diluted_basis",
            "every class: common, preferred, options granted, the unissued pool, warrants",
            "The fully diluted shares are every class's shares added up, the unissued pool included; each class's "
            "and holder line's share is its shares over that total.",
            ALTMAN_FULLY_DILUTED_SOURCE,
        ),
        _assumption(
            "class_shares",
            "the class's stated shares, else its holder lines' sum",
            "A class with stated shares counts those; a class without counts its holder lines. With both, the "
            "founder says whether the lines are every holder of the class: complete lines are checked against the "
            "stated shares; partial ones leave the rest shown as shares in no line, and are checked only when they "
            "add up to more. The lines are never used in the stated shares' place.",
            "method",
        ),
    ]
    if "preferred" in kinds:
        rows.append(
            _assumption(
                "preferred_as_converted",
                "one common share per preferred share",
                "Each preferred share counts as one share of common, as if converted at one to one. A series whose "
                "conversion price has moved (an anti-dilution adjustment, a split) converts into a different number.",
                _LAWYER,
            )
        )
    if "warrants" in kinds:
        rows.append(
            _assumption(
                "warrants_as_exercised",
                "one share per warrant share, as if exercised",
                "Each warrant share counts as one share, exercised in full, whatever its exercise price.",
                _WARRANT_LAWYER,
            )
        )
    if inputs.stated_percent_basis == "outstanding":
        rows.append(
            _assumption(
                "outstanding_basis",
                "common and preferred only",
                "On the outstanding basis a stated percent is a share of the issued stock (common and preferred), "
                "with options, the pool and warrants left out.",
                f"{UNVERIFIED} (the founder named this basis)",
            )
        )

    return rows


def _path_row(path_from: PathStart) -> EquityAssumption:
    """Where the founders' path starts and what it converts."""
    if path_from == "conversion_preview":
        return _assumption(
            "founder_path",
            "the founders' share after the conversion preview, times each round's share kept",
            "The founders' path starts from their holder lines' share after the conversion preview's round, the "
            "SAFEs and notes converted in it, and keeps 1 - n - p of it in each planned round, as the dilution "
            "scenario works it. The planned rounds are the rounds after the preview; one that repeats it is counted "
            "twice.",
            UNVERIFIED,
        )

    return _assumption(
        "founder_path",
        "the founders' share of the fully diluted shares, times each round's share kept",
        "The founders' path starts from their holder lines over today's fully diluted shares and keeps 1 - n - p of "
        "it in each planned round, as the dilution scenario works it. It converts no SAFE or note; a conversion "
        "preview would start it after the next round, with them converted.",
        UNVERIFIED,
    )


def _check_rows(inputs: CapTableCheckInput, checked: bool, path_from: PathStart | None) -> list[EquityAssumption]:
    """The tolerance (when anything was checked), the authorised-share comparisons, the instruments and the path."""
    rows = []
    if checked:
        rows.append(
            _assumption(
                "tolerance",
                f"{inputs.tolerance_points} points",
                "A stated percent is consistent when it is the computed figure rounded half away from zero to the "
                "places it is written with, or within this many percentage points of it. The stated percents' total "
                "is consistent when its gap from 100% is no more than half a unit in the last place of each percent "
                "added (the most their rounding can explain), plus the tolerance for each. A share count is "
                "consistent only when it is equal. A flag names a figure consistent by the tolerance alone.",
                f"{UNVERIFIED} (the rounding test is standard arithmetic)",
            )
        )
    if any(item.authorised_shares is not None for item in inputs.classes) or inputs.option_plan_reserve is not None:
        rows.append(
            _assumption(
                "authorised_shares",
                "issued against authorised, class by class",
                "Each class's issued shares are set against the authorised shares the founder gives for it, the "
                "option plan's granted and unissued options against its reserve, and authorised common against the "
                "fully diluted shares, each of which would be common once converted or exercised. The authorised "
                "figures are the founder's; the charter's are not read. Options already exercised and shares already "
                "issued under the plan are not counted against its reserve here, so what is left is not room to "
                "grant; the plan's records say what has been used.",
                _LAWYER,
            )
        )
    if inputs.instruments:
        rows.append(
            _assumption(
                "instruments_outside",
                "SAFEs and notes are not in the fully diluted shares",
                "An unconverted SAFE or note holds no shares until a priced round converts it, so it is listed with "
                "its amount and left out of every percent. Only a conversion preview, at a round the founder gives, "
                "converts it.",
                UNVERIFIED,
            )
        )
    if path_from is not None:
        rows.append(_path_row(path_from))
    rows.append(
        _assumption(
            "legal_validity",
            "not checked",
            "The check works the arithmetic of the figures given. Whether a share was validly issued, a grant "
            "approved, a vesting schedule or a transfer allowed is for the company's lawyer; the report flags what "
            "to ask, never rules on it.",
            "method",
        )
    )

    return rows


def cap_table_check_assumptions(
    inputs: CapTableCheckInput, checked: bool, nested: tuple[EquityAssumption, ...], path_from: PathStart | None
) -> tuple[EquityAssumption, ...]:
    """The cap table check's rows (the path's where a path was worked, from ``path_from``), then the nested round's
    and dilution's rows whose key is not already listed."""
    rows = [*_count_rows(inputs), *_check_rows(inputs, checked, path_from)]
    keys = {row.key for row in rows}
    merged: list[EquityAssumption] = []
    for row in nested:
        if row.key not in keys:
            keys.add(row.key)
            merged.append(row)

    return (*rows, *merged)
