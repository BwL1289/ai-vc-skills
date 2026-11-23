"""A founder's traction metrics worked from their parts, each stated figure checked, and flags for what a VC asks.

Notation (``equity_calculator.schemas.equity_metrics_check``): S the recurring revenue at the start of the period,
N new, E expansion, C contraction, X churned, all the period's totals in the recurring unit; k = 12 for a monthly
unit, 1 for an annual one (the only conversion, done here, never by the model). E', C', X' are the starting
customers' own movements when given, else the totals.

- ARR at the start k·S; at the end k·(S + N + E - C - X); net new ARR k·(N + E - C - X); new ARR k·N.
- ARR from the latest month 12·(T - O - U), its run-rate 12·T (T the month's revenue, O one-time, U usage). A stated
  ARR is checked against the movement's ending ARR or the latest month's ARR, whichever it is within the tolerance of
  (the movement's when it is within both or neither, the one worked when only one is); ``arr_basis`` says which.
- Gross revenue retention (S - C' - X')/S, net (S + E' - C' - X')/S; gross revenue churn (C' + X')/S, net
  (C' + X' - E')/S; over the period, never annualised. Logo churn = customers lost / customers at the start.
- CAC: spend / new customers (blended) and spend / paid-channel customers (paid). CAC payback in months:
  spend / (n·m), n the new recurring revenue per month (N, or N/12 for an annual unit) and m the gross margin; on
  revenue only, spend / n.
- Burn multiple: net burn / net new ARR, when both are above 0; on new ARR only, net burn / k·N, worked whenever a
  multiple is stated, to test whether the stated figure used new ARR. Customer concentration: the largest customer's
  revenue / the period's revenue.

Each stated figure becomes one check (a stated churn with no basis one per basis it can be worked on, consistent when
any is; a churn below zero only on net revenue). A stated percent, months or multiple is consistent when it is within
the tolerance (``tolerance_points`` points for a percent, ``tolerance_percent`` of the computed figure for the rest,
the edge included) or when it is the computed figure rounded half away from zero to the places it is typed with
(``12`` against 12.40, ``2`` against 2.4%; ``0.0`` is one place): people write figures rounded to the places they
show. Money is consistent within ``tolerance_percent`` only, since a figure like $1.2M carries no places once typed as
1200000. A stated burn multiple with no multiple to work is ``not_checked``, and the overall verdict is then
``not_checked`` unless a figure is a mismatch, never ``consistent``. The four ``stated_*`` cause flags read a stated
figure's agreement with the other definition by the tolerance alone. ``consistent_beyond_rounding`` names a figure that
holds by the tolerance alone. Flags never change a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import get_args

from equity_calculator.assumptions_metrics_check import metrics_check_assumptions
from equity_calculator.exact import ONE, ZERO, fraction, from_percent, quantity
from equity_calculator.rounding import rounds_to
from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import DealVerdict
from equity_calculator.schemas.equity_metrics_check import (
    ArrBasis,
    ChurnBasis,
    MetricsCheck,
    MetricsCheckInput,
    MetricsCheckKey,
    MetricsCheckResult,
    MetricsFlag,
    payback_band,
)

__all__ = ["compute_metrics_check"]

_MONTHS_PER_YEAR = 12
_ONE_MONTH = 1


@dataclass(frozen=True)
class _Worked:
    """Every metric the inputs can give, as exact fractions (none when its parts were not given)."""

    starting_arr: Fraction | None = None
    ending_arr: Fraction | None = None
    net_new_arr: Fraction | None = None
    new_arr: Fraction | None = None
    month_arr: Fraction | None = None
    run_rate: Fraction | None = None
    ending_over_start: Fraction | None = None
    grr: Fraction | None = None
    nrr: Fraction | None = None
    gross_churn: Fraction | None = None
    net_churn: Fraction | None = None
    logo_churn: Fraction | None = None
    blended_cac: Fraction | None = None
    paid_cac: Fraction | None = None
    payback: Fraction | None = None
    revenue_payback: Fraction | None = None
    burn_multiple: Fraction | None = None
    burn_multiple_on_new: Fraction | None = None
    concentration: Fraction | None = None


def _annual_factor(inputs: MetricsCheckInput) -> int:
    """k: 12 for a monthly recurring unit, 1 for an annual one."""
    return _MONTHS_PER_YEAR if inputs.recurring_unit == "monthly" else 1


def _cohort(given: Decimal | None, total: Decimal) -> Fraction:
    """The starting customers' movement when given, else the period's total."""
    return fraction(total if given is None else given)


def _arr(inputs: MetricsCheckInput) -> dict[str, Fraction | None]:
    """The ARR figures: start, end, net new and new from the movement; the latest month's ARR and run-rate."""
    worked: dict[str, Fraction | None] = {}
    if inputs.starting_recurring is not None:
        factor = _annual_factor(inputs)
        start = fraction(inputs.starting_recurring)
        net_change = (
            fraction(inputs.new_recurring)
            + fraction(inputs.expansion_recurring)
            - fraction(inputs.contraction_recurring)
            - fraction(inputs.churned_recurring)
        )
        worked |= {
            "starting_arr": factor * start,
            "ending_arr": factor * (start + net_change),
            "net_new_arr": factor * net_change,
            "new_arr": factor * fraction(inputs.new_recurring),
        }
        if start > ZERO:
            worked["ending_over_start"] = (start + net_change) / start
    if inputs.month_total_revenue is not None:
        total = fraction(inputs.month_total_revenue)
        recurring = total - fraction(inputs.month_one_time_revenue) - fraction(inputs.month_usage_revenue)
        worked |= {"month_arr": _MONTHS_PER_YEAR * recurring, "run_rate": _MONTHS_PER_YEAR * total}

    return worked


def _retention(inputs: MetricsCheckInput) -> dict[str, Fraction | None]:
    """Gross and net revenue retention and churn on the starting customers' movements, and logo churn."""
    worked: dict[str, Fraction | None] = {}
    if inputs.has_revenue_churn() and inputs.starting_recurring is not None:
        start = fraction(inputs.starting_recurring)
        expansion = _cohort(inputs.cohort_expansion_recurring, inputs.expansion_recurring)
        lost = _cohort(inputs.cohort_contraction_recurring, inputs.contraction_recurring) + _cohort(
            inputs.cohort_churned_recurring, inputs.churned_recurring
        )
        worked |= {
            "grr": (start - lost) / start,
            "nrr": (start + expansion - lost) / start,
            "gross_churn": lost / start,
            "net_churn": (lost - expansion) / start,
        }
    if inputs.has_logo_churn() and inputs.customers_start is not None and inputs.customers_lost is not None:
        worked["logo_churn"] = fraction(inputs.customers_lost) / fraction(inputs.customers_start)

    return worked


def _acquisition(inputs: MetricsCheckInput) -> dict[str, Fraction | None]:
    """Blended and paid CAC, and CAC payback on gross margin and on revenue."""
    worked: dict[str, Fraction | None] = {}
    if inputs.sales_marketing_spend is None:
        return worked

    spend = fraction(inputs.sales_marketing_spend)
    if inputs.customers_new:
        worked["blended_cac"] = spend / fraction(inputs.customers_new)
    if inputs.customers_new_paid:
        worked["paid_cac"] = spend / fraction(inputs.customers_new_paid)
    if inputs.new_recurring > 0:
        monthly_new = fraction(inputs.new_recurring) * _annual_factor(inputs) / _MONTHS_PER_YEAR
        worked["revenue_payback"] = spend / monthly_new
        if inputs.gross_margin_percent is not None:
            worked["payback"] = spend / (monthly_new * from_percent(inputs.gross_margin_percent))

    return worked


def _efficiency(inputs: MetricsCheckInput, net_new_arr: Fraction | None) -> dict[str, Fraction | None]:
    """The burn multiple (and on new ARR only, to test a stated one) and customer concentration."""
    worked: dict[str, Fraction | None] = {}
    if inputs.net_burn is not None and net_new_arr is not None:
        burn = fraction(inputs.net_burn)
        if burn > ZERO and net_new_arr > ZERO:
            worked["burn_multiple"] = burn / net_new_arr
        new_arr = _annual_factor(inputs) * fraction(inputs.new_recurring)
        if burn > ZERO and new_arr > ZERO and inputs.stated_burn_multiple is not None:
            worked["burn_multiple_on_new"] = burn / new_arr
    if inputs.largest_customer_revenue is not None and inputs.period_revenue is not None:
        worked["concentration"] = fraction(inputs.largest_customer_revenue) / fraction(inputs.period_revenue)

    return worked


def _work(inputs: MetricsCheckInput) -> _Worked:
    """Every metric the inputs give."""
    arr = _arr(inputs)

    return _Worked(
        **arr,
        **_retention(inputs),
        **_acquisition(inputs),
        **_efficiency(inputs, arr.get("net_new_arr")),
    )


def _check(
    key: MetricsCheckKey,
    unit: EquityUnit,
    written: Decimal,
    computed: Fraction,
    tolerance: Fraction,
    basis: ChurnBasis | None = None,
) -> MetricsCheck:
    """One check of the figure as ``written`` (percent points for a fraction): consistent within ``tolerance`` of the
    computed figure (the edge included) or, for a percent, months or multiple, when it is the computed figure rounded
    to the places it is typed with (``within_rounding``)."""
    stated = from_percent(written) if unit == "fraction" else fraction(written)
    difference = computed - stated
    rounds = rounds_to(written, unit, computed)

    return MetricsCheck(
        key=key,
        basis=basis,
        stated=quantity(unit, stated),
        computed=quantity(unit, computed),
        difference=quantity(unit, difference),
        verdict="consistent" if abs(difference) <= tolerance or rounds else "mismatch",
        within_rounding=rounds,
    )


def _within(stated: Fraction, other: Fraction | None, tolerance: Fraction) -> bool:
    """Whether ``stated`` sits within ``tolerance`` of ``other`` (the edge included)."""
    return other is not None and abs(other - stated) <= tolerance


def _checked_arr(inputs: MetricsCheckInput, worked: _Worked) -> tuple[ArrBasis, Fraction] | None:
    """The ARR a stated ARR is checked against, and which one: of the movement's ending ARR and the latest month's,
    the first a stated ARR is within ``tolerance_percent`` of, else the first worked (the movement's); none when
    neither is worked. With no stated ARR it is the first worked."""
    candidates: tuple[tuple[ArrBasis, Fraction | None], ...] = (
        ("movement", worked.ending_arr),
        ("month", worked.month_arr),
    )
    worked_arrs: list[tuple[ArrBasis, Fraction]] = [(basis, value) for basis, value in candidates if value is not None]
    if not worked_arrs:
        return None
    if inputs.stated_arr is not None:
        stated = fraction(inputs.stated_arr)
        relative = from_percent(inputs.tolerance_percent)
        for basis, value in worked_arrs:
            if _within(stated, value, relative * value):
                return basis, value

    return worked_arrs[0]


def _churn_rows(inputs: MetricsCheckInput, worked: _Worked, points: Fraction) -> list[MetricsCheck]:
    """A stated churn on its basis, or one row per basis the inputs can work when it has none."""
    if inputs.stated_churn_percent is None:
        return []

    written = inputs.stated_churn_percent
    by_basis: dict[ChurnBasis, Fraction | None] = {
        "logo": worked.logo_churn,
        "gross_revenue": worked.gross_churn,
        "net_revenue": worked.net_churn,
    }
    wanted = inputs.stated_churn_basis
    rows = []
    for basis, computed in by_basis.items():
        # A churn below zero can only be net revenue churn: it is never checked on a basis that cannot go below 0.
        if written < 0 and basis != "net_revenue":
            continue
        if computed is not None and wanted in (basis, "unlabelled"):
            rows.append(_check("churn", "fraction", written, computed, points, basis))

    return rows


def _checks(inputs: MetricsCheckInput, worked: _Worked) -> tuple[MetricsCheck, ...]:
    """One check per stated figure (a churn with no basis one per basis), in ``MetricsCheckKey``'s order.

    The validator made sure each stated figure has its parts, except a burn multiple with no multiple to check (net
    burn or net new ARR at or below zero), which gets a ``not_checked`` row (no computed figure) and a flag.
    """
    points = from_percent(inputs.tolerance_points)
    relative = from_percent(inputs.tolerance_percent)
    checks: list[MetricsCheck] = []
    arr = _checked_arr(inputs, worked)
    if inputs.stated_arr is not None and arr is not None:
        _, against = arr
        checks.append(_check("arr", "money", inputs.stated_arr, against, relative * against))
    percents: tuple[tuple[MetricsCheckKey, Decimal | None, Fraction | None], ...] = (
        ("nrr", inputs.stated_nrr_percent, worked.nrr),
        ("grr", inputs.stated_grr_percent, worked.grr),
    )
    for key, stated, computed in percents:
        if stated is not None and computed is not None:
            checks.append(_check(key, "fraction", stated, computed, points))
    checks += _churn_rows(inputs, worked, points)
    payback = worked.payback if worked.payback is not None else worked.revenue_payback
    relatives: tuple[tuple[MetricsCheckKey, EquityUnit, Decimal | None, Fraction | None], ...] = (
        ("cac", "money", inputs.stated_cac, worked.blended_cac),
        ("cac_payback", "months", inputs.stated_cac_payback_months, payback),
        ("burn_multiple", "multiplier", inputs.stated_burn_multiple, worked.burn_multiple),
    )
    for key, unit, stated, computed in relatives:
        if stated is not None and computed is not None:
            checks.append(_check(key, unit, stated, computed, relative * computed))
        elif key == "burn_multiple" and stated is not None:
            checks.append(MetricsCheck(key=key, stated=quantity(unit, fraction(stated)), verdict="not_checked"))
    if inputs.stated_concentration_percent is not None and worked.concentration is not None:
        written = inputs.stated_concentration_percent
        checks.append(_check("concentration", "fraction", written, worked.concentration, points))

    return tuple(checks)


def _mismatched(checks: tuple[MetricsCheck, ...], key: MetricsCheckKey, *, or_unchecked: bool = False) -> bool:
    """Whether the stated figure ``key`` was checked and is a mismatch (or, with ``or_unchecked``, was not checked)."""
    wrong = ("mismatch", "not_checked") if or_unchecked else ("mismatch",)
    return any(check.key == key and check.verdict in wrong for check in checks)


def _definition_flags(
    inputs: MetricsCheckInput, worked: _Worked, checks: tuple[MetricsCheck, ...]
) -> list[MetricsFlag]:
    """The four ``stated_*`` flags: a mismatch that agrees with the named wrong definition instead, within the
    tolerance of it (the tolerance alone: the rounding rule decides verdicts, not causes)."""
    points = from_percent(inputs.tolerance_points)
    relative = from_percent(inputs.tolerance_percent)
    flags: list[MetricsFlag] = []
    run_rate, month_arr = worked.run_rate, worked.month_arr
    if inputs.stated_arr is not None and _mismatched(checks, "arr") and run_rate is not None and month_arr is not None:
        # Only a month with one-time or usage revenue has a run-rate apart from its ARR. A stated ARR within the
        # tolerance of the month's own ARR never gets here: it is consistent, checked against that ARR.
        stated = fraction(inputs.stated_arr)
        if run_rate != month_arr and _within(stated, run_rate, relative * run_rate):
            flags.append("stated_arr_matches_run_rate")
    if inputs.stated_nrr_percent is not None and _mismatched(checks, "nrr"):
        if _within(from_percent(inputs.stated_nrr_percent), worked.ending_over_start, points):
            flags.append("stated_nrr_includes_new")
    if (
        inputs.stated_cac_payback_months is not None
        and worked.payback is not None
        and worked.revenue_payback is not None
        and _mismatched(checks, "cac_payback")
    ):
        revenue = worked.revenue_payback
        if _within(fraction(inputs.stated_cac_payback_months), revenue, relative * revenue):
            flags.append("stated_payback_not_margin_adjusted")
    on_new = worked.burn_multiple_on_new
    # Also beside a multiple left unchecked: with churn above new sales there is no net-new multiple at all, and a
    # stated one that matches net burn over new ARR is exactly the mistake this flag names.
    if (
        inputs.stated_burn_multiple is not None
        and on_new is not None
        and _mismatched(checks, "burn_multiple", or_unchecked=True)
    ):
        if _within(fraction(inputs.stated_burn_multiple), on_new, relative * on_new):
            flags.append("stated_burn_multiple_uses_new_not_net_arr")

    return flags


def _rounding_flags(checks: tuple[MetricsCheck, ...]) -> list[MetricsFlag]:
    """A stated percent, months or multiple consistent by the tolerance alone: not the computed figure rounded to its
    own places, so a VC recomputing gets another figure. A churn with no basis counts as one figure: it is a rounding
    when any of its rows is. (A rounding is always consistent, so no mismatch is one.)"""
    flags: list[MetricsFlag] = []
    keys = dict.fromkeys(check.key for check in checks if check.within_rounding is not None)
    for key in keys:
        rows = [check for check in checks if check.key == key and check.within_rounding is not None]
        rounds = any(check.within_rounding for check in rows)
        holds = any(check.verdict == "consistent" for check in rows)
        if holds and not rounds:
            flags.append("consistent_beyond_rounding")

    return flags


def _band_flags(inputs: MetricsCheckInput, worked: _Worked) -> list[MetricsFlag]:
    """The three benchmark questions: payback at or above its band, the multiple at or above its band, and one
    month's net revenue churn above its band."""
    flags: list[MetricsFlag] = []
    band = payback_band(inputs)
    # With no gross margin, the revenue-only payback is a floor under the payback on gross margin (a margin is at
    # most 100%), so one already at or above the band shows the payback on gross margin is too.
    payback = worked.payback if worked.payback is not None else worked.revenue_payback
    if band is not None and payback is not None and payback >= fraction(band):
        flags.append("payback_above_band")
    if worked.burn_multiple is not None and worked.burn_multiple >= fraction(inputs.burn_multiple_band):
        flags.append("burn_multiple_above_band")
    churn = worked.net_churn
    if inputs.period_months == _ONE_MONTH and churn is not None:
        if churn > from_percent(inputs.net_revenue_churn_band_percent):
            flags.append("net_revenue_churn_above_band")

    return flags


def _flags(inputs: MetricsCheckInput, worked: _Worked, checks: tuple[MetricsCheck, ...]) -> tuple[MetricsFlag, ...]:
    """Every flag that holds, in ``MetricsFlag``'s order."""
    found = set(_definition_flags(inputs, worked, checks)) | set(_band_flags(inputs, worked))
    found |= set(_rounding_flags(checks))
    if inputs.month_total_revenue is not None and (inputs.month_one_time_revenue > 0 or inputs.month_usage_revenue > 0):
        found.add("run_rate_includes_non_recurring")
    movement, month = worked.ending_arr, worked.month_arr
    if movement is not None and month is not None:
        if not _within(month, movement, from_percent(inputs.tolerance_percent) * abs(movement)):
            found.add("arr_movement_and_month_disagree")
    if worked.gross_churn is not None and worked.net_churn is not None:
        if worked.gross_churn > ZERO and worked.net_churn <= ZERO:
            found.add("expansion_hides_churn")
    if inputs.stated_churn_percent is not None and inputs.stated_churn_basis == "unlabelled":
        found.add("churn_basis_unlabelled")
    if worked.blended_cac is not None and inputs.customers_new_paid is None:
        found.add("blended_cac_only")
    if worked.revenue_payback is not None and worked.payback is None:
        found.add("payback_not_margin_adjusted")
    if inputs.net_burn is not None:
        if worked.net_new_arr is not None and worked.net_new_arr <= ZERO:
            found.add("burn_multiple_not_defined")
        if inputs.net_burn <= 0:
            found.add("no_net_burn")

    return tuple(flag for flag in _FLAG_ORDER if flag in found)


_FLAG_ORDER: tuple[MetricsFlag, ...] = get_args(MetricsFlag)


def _verdict(checks: tuple[MetricsCheck, ...]) -> DealVerdict:
    """``not_checked`` with no check; else each stated figure is consistent when any of its rows is (an unlabelled
    churn has one row per basis), not checked when its only row is, and a mismatch otherwise. The verdict is
    ``mismatch`` if any figure is one, else ``not_checked`` if any figure went unchecked, else ``consistent``."""
    if not checks:
        return "not_checked"

    keys = dict.fromkeys(check.key for check in checks)
    outcomes = set()
    for key in keys:
        rows = [row.verdict for row in checks if row.key == key]
        if "consistent" in rows:
            outcomes.add("consistent")
        elif all(verdict == "not_checked" for verdict in rows):
            outcomes.add("not_checked")
        else:
            outcomes.add("mismatch")
    if "mismatch" in outcomes:
        return "mismatch"
    return "not_checked" if "not_checked" in outcomes else "consistent"


def _optional(unit: EquityUnit, value: Fraction | None) -> EquityQuantity | None:
    return None if value is None else quantity(unit, value)


def compute_metrics_check(inputs: MetricsCheckInput) -> MetricsCheckResult:
    """The metrics worked exactly from their parts, each stated figure's verdict, the flags and the assumptions."""
    worked = _work(inputs)
    checks = _checks(inputs, worked)
    band = payback_band(inputs)
    arr = _checked_arr(inputs, worked)

    return MetricsCheckResult(
        inputs=inputs,
        starting_arr=_optional("money", worked.starting_arr),
        ending_arr=_optional("money", worked.ending_arr),
        net_new_arr=_optional("money", worked.net_new_arr),
        new_arr=_optional("money", worked.new_arr),
        month_arr=_optional("money", worked.month_arr),
        run_rate=_optional("money", worked.run_rate),
        arr_basis=None if arr is None else arr[0],
        gross_revenue_retention=_optional("fraction", worked.grr),
        net_revenue_retention=_optional("fraction", worked.nrr),
        gross_revenue_churn=_optional("fraction", worked.gross_churn),
        net_revenue_churn=_optional("fraction", worked.net_churn),
        logo_churn=_optional("fraction", worked.logo_churn),
        logo_retention=None if worked.logo_churn is None else quantity("fraction", ONE - worked.logo_churn),
        blended_cac=_optional("money", worked.blended_cac),
        paid_cac=_optional("money", worked.paid_cac),
        cac_payback_months=_optional("months", worked.payback),
        revenue_payback_months=_optional("months", worked.revenue_payback),
        burn_multiple=_optional("multiplier", worked.burn_multiple),
        burn_multiple_on_new_arr=_optional("multiplier", worked.burn_multiple_on_new),
        concentration=_optional("fraction", worked.concentration),
        payback_band_months=None
        if band is None or (worked.payback is None and worked.revenue_payback is None)
        else quantity("months", fraction(band)),
        checks=checks,
        flags=_flags(inputs, worked, checks),
        verdict=_verdict(checks),
        assumptions=metrics_check_assumptions(inputs, bool(checks), _used(worked)),
    )


def _used(worked: _Worked) -> frozenset[str]:
    """Which metrics were worked, so the assumptions list only the rules a result rests on."""
    return frozenset(name for name, value in vars(worked).items() if value is not None)
