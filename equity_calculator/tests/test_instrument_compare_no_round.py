"""A priced round now beside a note now with no next round: the note at its maturity and at a sale before any priced
round, worked by hand to the fraction, both change-of-control terms, uncapped notes, every refusal and every flag.

Pure computation: no DB, no network, nothing written. The report and the command line for this mode are at the end
of ``test_instrument_compare_cli.py``.

Company DX (``tests.support.COMPARE_DX``), worked by hand. FD = 9M + 0.5M + 0.5M = 10M shares; no cap, a 20%
discount, 6% simple interest.

- Option A today: p = $6M / 10M = 3/5, N = $1.5M / (3/5) = 2.5M, total 12.5M; founders 9/12.5 = 18/25 (72%).
- Option B today: no shares, founders 9/10. The note owes $1.5M × 1.06 = $1,590,000 at month 12 and $1.5M × 1.12 =
  $1,680,000 at month 24.
- At maturity (24 months): the repayment is $1,680,000; at a $5M valuation over FD the price is 1/2, so the note takes
  3.36M shares, 13.36M in all; founders 9/13.36 = 225/334, B - A = 225/334 - 18/25 = -387/8350.
- A sale before any priced round, the note owed 2x its $1.5M principal, $3M, before any share. At $3M: A's series
  stays (2.5M shares would take $0.6M of it, under its $1.5M preference), the common share $1.5M, founders $1.35M; B's
  note takes the whole $3M, founders $0. At $10M: A's series converts ($0.80 a share), founders $7.2M; B pays $3M and
  $7M over 10M shares, founders $6.3M. At $40M: A founders $28.8M; B founders $37M × 9/10 = $33.3M.

Company BU with no next round (``COMPARE_BU`` less its rounds and conversion month): a $6M cap, so a cap price of
3/5. Converting at its cap at a sale 12 months on, the note owes $2.1M and takes 3.5M common shares: at $20M the
13.5M common shares take 40/27 each, founders $320M/27 against A's 8M × $1.60 = $12.8M. At maturity (24 months) it owes
$2.2M; at a $5M valuation (price 1/2) it takes 4.4M shares, founders 8/14.4 = 5/9 against A's 16/25.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest
from equity_calculator.instrument_compare import NOTE_EXIT_REFUSALS, option_b_note
from equity_calculator.interest import note_interest
from equity_calculator.schemas.equity_instrument_compare import (
    EarlyGroupPayout,
    ExitBeforeRoundComparison,
    GroupStake,
    HolderGroup,
    InstrumentCompareInput,
)
from pydantic import ValidationError
from tests.support import COMPARE_BU, COMPARE_DX, instrument_compare, waterfall

_M = 1_000_000
_FIRST, _SECOND, _THIRD = 0, 1, 2
_ROUND_ONE = {"pre_money": "27000000", "investment": "6000000", "preference": {"standard": True}}
_BU_NO_ROUND = {
    key: value for key, value in COMPARE_BU.items() if key not in ("next_rounds", "note_months_to_conversion")
}
_AT_CAP = {"note_change_of_control_at_cap": True, "note_months_to_exit": 12}


def _bu(**changes: object) -> dict[str, Any]:
    return {**_BU_NO_ROUND, **changes}


def _dx(**changes: object) -> dict[str, Any]:
    return {**COMPARE_DX, **changes}


def _stake(stakes: tuple[GroupStake, ...], group: HolderGroup) -> GroupStake:
    return next(stake for stake in stakes if stake.group == group)


def _payout(item: ExitBeforeRoundComparison, group: HolderGroup) -> EarlyGroupPayout:
    return next(payout for payout in item.payouts if payout.group == group)


def _paid(item: ExitBeforeRoundComparison, group: HolderGroup) -> tuple[Fraction, Fraction, Fraction]:
    """``group``'s exact payout under A and under B, and the exact B - A (option B worked)."""
    payout = _payout(item, group)
    assert payout.note is not None and payout.difference is not None
    return payout.priced.exact, payout.note.exact, payout.difference.exact


def test_with_no_next_round_the_comparison_switches_mode_and_says_so() -> None:
    result = instrument_compare(**COMPARE_DX)

    assert result.mode == "no_next_round"
    assert result.next_rounds == ()
    assert result.note_owed_at_conversion is None and result.note_interest_at_conversion is None
    assert result.flags[_FIRST] == "no_next_round_given"
    rule = next(row for row in result.assumptions if row.key == "comparison_rule")
    assert "No next round was given, so the note never converts at a priced round here" in rule.statement
    assert "exit_after_next_round" not in {row.key for row in result.assumptions}
    assert instrument_compare(
        **{**_BU_NO_ROUND, "next_rounds": [_ROUND_ONE], "note_months_to_conversion": 12}
    ).mode == ("next_round")


def test_company_dx_today_and_the_note_owed_match_the_hand_working() -> None:
    result = instrument_compare(**COMPARE_DX)

    assert result.priced_price.exact == Fraction(3, 5)
    assert result.priced_total_shares.exact == Fraction(25, 2) * _M
    assert result.note_cap_price is None
    founders = _stake(result.stakes_now, "founders")
    assert (founders.priced.exact, founders.note.exact) == (Fraction(18, 25), Fraction(9, 10))
    assert [(owed.months, owed.owed.exact, owed.interest.exact) for owed in result.note_owed] == [
        (12, 1_590_000, 90_000),
        (24, 1_680_000, 180_000),
    ]
    assert not any(owed.approximate for owed in result.note_owed)


def test_maturity_repayment_is_principal_plus_interest_to_the_cent() -> None:
    """Company DX at 24 months: $1.5M × (1 + 6% × 2) = $1,680,000; BU at 24 months: $2M × 1.10 = $2,200,000."""
    dx = instrument_compare(**COMPARE_DX).maturity
    bu = instrument_compare(**_bu(note_maturity_months=24)).maturity

    assert dx is not None and (dx.owed.months, dx.owed.owed.exact) == (24, 1_680_000)
    assert bu is not None and (bu.owed.owed.exact, bu.owed.interest.exact) == (2_200_000, 200_000)
    assert bu.conversion is None


def test_maturity_conversion_at_a_valuation_matches_the_hand_working() -> None:
    maturity = instrument_compare(**COMPARE_DX).maturity
    assert maturity is not None and maturity.conversion is not None
    conversion = maturity.conversion

    assert (conversion.basis, conversion.price.exact) == ("valuation", Fraction(1, 2))
    assert conversion.converting_amount.exact == 1_680_000
    assert conversion.shares.exact == 3_360_000
    assert conversion.total_shares.exact == 13_360_000
    founders = _stake(conversion.stakes, "founders")
    assert (founders.priced.exact, founders.note.exact) == (Fraction(18, 25), Fraction(225, 334))
    assert conversion.founders_ownership_difference.exact == Fraction(-387, 8350)
    assert _stake(conversion.stakes, "new_money").note.exact == Fraction(3_360_000, 13_360_000)
    assert sum(stake.note.exact for stake in conversion.stakes) == 1


def test_maturity_conversion_at_a_price_and_with_the_interest_paid_in_cash() -> None:
    """BU at 24 months: $2.2M at $0.40 is 5.5M shares (founders 8/15.5 = 16/31); interest paid in cash, $2M at $0.50 is
    4M."""
    at_price = instrument_compare(**_bu(note_maturity_months=24, note_maturity_conversion_price="0.40")).maturity
    cash = instrument_compare(
        **_bu(note_maturity_months=24, note_maturity_conversion_valuation="5000000", note_interest_paid_in_cash=True)
    )
    assert at_price is not None and at_price.conversion is not None
    assert cash.maturity is not None and cash.maturity.conversion is not None

    assert (at_price.conversion.basis, at_price.conversion.shares.exact) == ("price", 5_500_000)
    assert _stake(at_price.conversion.stakes, "founders").note.exact == Fraction(16, 31)
    assert cash.maturity.owed.owed.exact == 2_200_000
    assert cash.maturity.conversion.converting_amount.exact == 2 * _M
    assert cash.maturity.conversion.shares.exact == 4 * _M
    assert "note_interest_paid_in_cash" in cash.flags and "note_interest_converts" not in cash.flags


def test_maturity_interest_is_the_interest_code_s_figure() -> None:
    """Monthly compounding for 24 months: the maturity line is ``note_interest`` at 24 months, to the cent."""
    fields = _bu(note_compounding="monthly", note_maturity_months=24, note_owed_months=[24])
    result = instrument_compare(**fields)
    expected = note_interest(option_b_note(InstrumentCompareInput.model_validate(fields), 24))

    assert result.maturity is not None and result.maturity.owed.owed.exact == expected.owed
    assert result.note_owed[_FIRST].owed.exact == expected.owed


def test_a_sale_with_an_uncapped_note_paid_a_multiple_of_its_principal_matches_the_hand_working() -> None:
    three, ten, forty = instrument_compare(**COMPARE_DX).exits_before_any_round

    assert _paid(three, "founders") == (1_350_000, 0, -1_350_000)
    assert _paid(three, "new_money") == (1_500_000, 3 * _M, 1_500_000)
    assert _paid(ten, "founders") == (7_200_000, 6_300_000, -900_000)
    assert _paid(ten, "new_money")[1] == 3 * _M
    assert _paid(forty, "founders") == (28_800_000, 33_300_000, 4_500_000)
    assert forty.founders_payout_difference is not None and forty.founders_payout_difference.exact == 4_500_000
    assert three.priced_preferences_paid.exact == 1_500_000
    assert three.note_preferences_paid is not None and three.note_preferences_paid.exact == 0


def test_a_multiple_larger_than_the_sale_takes_the_whole_sale_and_no_more() -> None:
    """BU uncapped at 2x: the note is owed $4M; a $3M sale pays it $3M and the shares nothing."""
    result = instrument_compare(
        **_bu(note_valuation_cap=None, note_change_of_control_multiple="2", exit_amounts=["3000000"])
    )
    (three,) = result.exits_before_any_round

    assert result.note_at_exit is not None and result.note_at_exit.claim is not None
    assert result.note_at_exit.claim.exact == 4 * _M
    assert _paid(three, "new_money")[1] == 3 * _M
    for group in ("founders", "team", "option_pool"):
        assert _paid(three, group)[1] == 0
    assert _paid(three, "founders")[0] == Fraction(8, 10) * _M


def test_a_sale_with_a_capped_note_converting_at_its_cap_matches_the_hand_working() -> None:
    result = instrument_compare(**_bu(**_AT_CAP, exit_amounts=["5000000", "20000000"]))
    five, twenty = result.exits_before_any_round
    at_exit = result.note_at_exit

    assert at_exit is not None and at_exit.rule == "converts_at_cap"
    assert at_exit.owed is not None and at_exit.owed.owed.exact == Fraction(21, 10) * _M
    assert at_exit.conversion_price is not None and at_exit.conversion_price.exact == Fraction(3, 5)
    assert at_exit.shares is not None and at_exit.shares.exact == Fraction(7, 2) * _M
    priced, note, difference = _paid(twenty, "founders")
    assert priced == Fraction(128, 10) * _M
    assert difference == Fraction(320 * _M, 27) - Fraction(128, 10) * _M
    assert _payout(twenty, "new_money").note is not None
    assert _paid(five, "founders")[0] == Fraction(24, 10) * _M
    assert _paid(five, "founders")[2] == Fraction(80 * _M, 27) - Fraction(24, 10) * _M
    assert note == Fraction(320 * _M, 27)
    founders_b = _payout(twenty, "founders").note
    assert founders_b is not None and founders_b.rounded == Decimal("11851851.85")
    assert "note_interest_converts" in result.flags and "cap_below_round_price_now" in result.flags


def test_option_a_at_a_sale_is_the_waterfall_scenario_s_split() -> None:
    """A's cap table after today: 10M common and a 2.5M-share standard series owed $1.5M (Company DX)."""
    series = {"shares": 2_500_000, "invested": "1500000"}
    for item in instrument_compare(**COMPARE_DX).exits_before_any_round:
        same = waterfall(str(item.exit_amount.rounded), series, common_shares=10 * _M)
        assert _payout(item, "new_money").priced.exact == same.rows[_FIRST].payout.exact
        common = sum((_payout(item, group).priced.exact for group in ("founders", "team", "option_pool")), Fraction(0))
        assert common == same.common_payout.exact


def test_each_option_s_payouts_add_up_to_the_sale_to_the_cent() -> None:
    """With an existing series too, under either term: the note's claim comes before every share, the series' preference
    before the common."""
    series = {"shares": 1_000_000, "invested": "1000000", "preference_multiple": "1", "participation": "none"}
    sales = {"existing_series": [series], "exit_amounts": ["1500000", "5000000", "20000000"]}
    multiple = {"note_change_of_control_multiple": "2"}
    for fields in (COMPARE_DX, _bu(**_AT_CAP), _bu(**_AT_CAP, **sales), _bu(**multiple, **sales)):
        for item in instrument_compare(**fields).exits_before_any_round:
            assert sum(payout.priced.rounded for payout in item.payouts) == item.exit_amount.rounded
            assert sum(_payout(item, payout.group).note.rounded for payout in item.payouts) == item.exit_amount.rounded


@pytest.mark.parametrize(
    ("changes", "refusal", "words"),
    [
        (
            {"note_valuation_cap": None},
            "uncapped_no_change_of_control_term",
            "the note has no cap to convert at and no change-of-control term was given",
        ),
        ({}, "no_change_of_control_term", "no change-of-control term was given for the note"),
        (
            {
                "note_change_of_control_multiple": "2",
                "existing_instruments": [{"kind": "safe", "purchase_amount": "500000", "valuation_cap": "10000000"}],
            },
            "existing_instruments_outstanding",
            "the existing SAFEs and notes are still outstanding",
        ),
    ],
)
def test_a_sale_option_b_cannot_be_worked_for_is_refused_for_that_row_with_the_reason(
    changes: dict[str, object], refusal: str, words: str
) -> None:
    """Option A is still worked; option B's payouts and B - A are left out, and the row names the code and the words."""
    result = instrument_compare(**_bu(**changes))

    for item in result.exits_before_any_round:
        assert item.note_refusal == refusal
        assert item.note_refusal_reason == NOTE_EXIT_REFUSALS[item.note_refusal]
        assert words in item.note_refusal_reason
        assert all(payout.note is None and payout.difference is None for payout in item.payouts)
        assert item.founders_payout_difference is None and item.note_preferences_paid is None
        assert sum(payout.priced.rounded for payout in item.payouts) == item.exit_amount.rounded


def test_an_uncapped_note_works_in_both_modes() -> None:
    """Discount only: at a next round it converts at its discount price; with none, the discount changes nothing."""
    uncapped = {"note_valuation_cap": None}
    with_round = instrument_compare(
        **_bu(**uncapped, next_rounds=[_ROUND_ONE], note_months_to_conversion=12, exit_amounts=["20000000"])
    )
    without = instrument_compare(**_bu(**uncapped, note_change_of_control_multiple="1", note_maturity_months=24))

    assert with_round.next_rounds[_FIRST].note_conversion.basis == "discount"
    assert with_round.note_cap_price is None and "discount_unused_without_round" not in with_round.flags
    assert without.note_cap_price is None
    assert "discount_unused_without_round" in without.flags
    assert all(item.note_refusal is None for item in without.exits_before_any_round)
    assert any(row.key == "note_discount_rule" for row in without.assumptions)


def test_what_the_note_owes_at_each_month_named_shows_in_both_modes() -> None:
    """BU at 5% simple on $2M: $2,150,000 at 18 months, with a next round or with none; never a line it was not asked
    for."""
    with_round = instrument_compare(**{**COMPARE_BU, "note_owed_months": [18]})
    without = instrument_compare(**_bu(note_owed_months=[18]))

    for result in (with_round, without):
        assert [(owed.months, owed.owed.exact) for owed in result.note_owed] == [(18, 2_150_000)]
    assert instrument_compare(**COMPARE_BU).note_owed == ()


def test_the_flags_of_the_mode() -> None:
    bare = instrument_compare(**_bu())
    assert bare.flags == (
        "no_next_round_given",
        "cap_below_round_price_now",
        "maturity_not_given",
        "discount_unused_without_round",
        "cap_unused_without_round",
        "change_of_control_not_given",
    )
    # At the $5M sale the note's 3.5M of 13.5M common shares fetch $1,296,296.30, under the $2.1M it owes.
    late = instrument_compare(**_bu(**_AT_CAP, note_maturity_months=6, note_discount_percent=None))
    assert late.flags == (
        "no_next_round_given",
        "cap_below_round_price_now",
        "note_interest_converts",
        "maturity_conversion_not_given",
        "exit_after_maturity",
        "note_paid_below_owed_at_sale",
    )
    safe = {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "10000000"}
    held = instrument_compare(**_bu(**_AT_CAP, existing_instruments=[safe]))
    assert "existing_instruments_outstanding" in held.flags and "cap_unused_without_round" in held.flags
    assert "note_interest_converts" not in held.flags  # option B is not worked at the sales, so nothing converts there
    assert "note_paid_below_owed_at_sale" not in held.flags
    on_time = instrument_compare(**_bu(**_AT_CAP, note_maturity_months=24))
    assert "exit_after_maturity" not in on_time.flags
    # Months to a sale past the maturity, but option B worked at no sale: its sale lines take the note as nothing.
    no_term = instrument_compare(**_bu(note_maturity_months=24, note_months_to_exit=30))
    assert "exit_after_maturity" not in no_term.flags and "change_of_control_not_given" in no_term.flags
    worked = _bu(note_maturity_months=24, note_months_to_exit=30, note_change_of_control_multiple="2")
    assert "exit_after_maturity" in instrument_compare(**worked).flags
    assert "exit_after_maturity" not in instrument_compare(**{**worked, "existing_instruments": [safe]}).flags


def test_an_existing_mfn_safe_with_no_next_round_is_outstanding_not_converted_on_both_sides() -> None:
    """Under option B the SAFE never converts, so the flag that says it converts under both options is not raised."""
    mfn = {"kind": "safe", "purchase_amount": "500000", "mfn": True}
    result = instrument_compare(**_bu(existing_instruments=[mfn]))

    assert "existing_instruments_outstanding" in result.flags
    assert "existing_mfn_safe_beside_note" not in result.flags
    assert _stake(result.stakes_now, "existing_investors").note.exact == 0


def test_a_sale_option_b_is_not_worked_at_shows_no_term_for_the_note() -> None:
    """Existing SAFEs outstanding: the 2x claim is not shown, as no sale pays it."""
    safe = {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "10000000"}
    result = instrument_compare(**_bu(existing_instruments=[safe], note_change_of_control_multiple="2"))

    assert result.note_at_exit is None
    assert all(item.note_refusal == "existing_instruments_outstanding" for item in result.exits_before_any_round)
    assert instrument_compare(**_bu(note_change_of_control_multiple="2")).note_at_exit is not None


def test_a_cap_that_sets_no_price_with_no_next_round_is_flagged() -> None:
    """Paid a multiple, a note's cap changes no figure: a $6M and a $60M cap give the same ownership and sales."""
    multiple = {"note_change_of_control_multiple": "2", "note_maturity_months": 24, "note_discount_percent": None}
    low = instrument_compare(**_bu(**multiple))
    high = instrument_compare(**_bu(**multiple, note_valuation_cap="60000000"))

    assert "cap_unused_without_round" in low.flags and "cap_unused_without_round" in high.flags
    assert low.exits_before_any_round == high.exits_before_any_round
    assert low.stakes_now == high.stakes_now and low.maturity == high.maturity
    rule = next(row for row in low.assumptions if row.key == "note_cap_rule")
    assert "with no next round it changes a figure here only at a sale worked on that term" in rule.statement
    at_cap = instrument_compare(**_bu(**_AT_CAP))
    assert "cap_unused_without_round" not in at_cap.flags
    assert any(row.key == "note_cap_rule" for row in at_cap.assumptions)
    assert not any(row.key == "note_cap_rule" for row in instrument_compare(**COMPARE_DX).assumptions)


def test_a_note_converted_at_its_cap_and_paid_less_than_it_owes_is_flagged() -> None:
    """BU, no discount, at its cap 12 months on: owed $2.1M, 2.1M / (3/5) = 3.5M common shares of 13.5M. A $1.5M sale
    pays $1/9 a share: founders 8M/9 and the note 3.5M/9 = $388,888.89; under A the series' $2M preference takes it."""
    result = instrument_compare(**_bu(**_AT_CAP, note_discount_percent=None, exit_amounts=["1500000"]))
    (sale,) = result.exits_before_any_round

    assert result.note_at_exit is not None and result.note_at_exit.owed is not None
    assert result.note_at_exit.owed.owed.exact == Fraction(21, 10) * _M
    assert _paid(sale, "founders") == (0, Fraction(8 * _M, 9), Fraction(8 * _M, 9))
    assert _paid(sale, "new_money") == (Fraction(3, 2) * _M, Fraction(7 * _M, 18), Fraction(7 * _M, 18) - 1_500_000)
    assert "note_paid_below_owed_at_sale" in result.flags
    paid_in_full = instrument_compare(**_bu(**_AT_CAP, note_discount_percent=None, exit_amounts=["100000000"]))
    assert "note_paid_below_owed_at_sale" not in paid_in_full.flags


def test_a_participating_existing_series_beside_a_multiple_matches_the_hand_working() -> None:
    """FD 10M: 6M founders, 1M team, 1M pool and a 2M-share series owed $1M with full participation. A: $2M at $0.80,
    2.5M shares owed $2M. B: 8% simple, owed $2.24M at month 18, and a claim of 1.5 × $2M = $3M before any share.

    At $3.5M: A pays the $3M of preferences, then $0.05 a share on the 10M participating shares (the new money stays,
    as converting would pay it $0.5M); B pays the $3M claim, and the series takes the $0.5M left of its $1M preference.
    At $10M: A pays $0.70 a share after the preferences; B pays the claim, the series' $1M, then $0.60 a share.
    """
    series = {"shares": 2_000_000, "invested": "1000000", "preference_multiple": "1", "participation": "full"}
    result = instrument_compare(
        founder_shares=6_000_000,
        team_shares=1_000_000,
        unissued_pool_shares=1_000_000,
        existing_series=[series],
        investment="2000000",
        priced_pre_money="8000000",
        priced_preference={"standard": True},
        note_interest_rate_percent="8",
        note_compounding="simple",
        note_maturity_months=18,
        note_change_of_control_multiple="1.5",
        exit_amounts=["3500000", "10000000"],
    )
    low, high = result.exits_before_any_round
    groups: tuple[HolderGroup, ...] = ("founders", "existing_investors", "new_money")

    assert result.maturity is not None and result.maturity.owed.owed.exact == 2_240_000
    assert result.note_at_exit is not None and result.note_at_exit.claim is not None
    assert result.note_at_exit.claim.exact == 3 * _M
    assert [_paid(low, group)[:2] for group in groups] == [(300_000, 0), (1_100_000, 500_000), (2 * _M, 3 * _M)]
    assert [_paid(high, group)[:2] for group in groups] == [
        (4_200_000, 3_600_000),
        (2_400_000, 2_200_000),
        (2 * _M, 3 * _M),
    ]


_CASH_AT_CAP: dict[str, Any] = {
    "founder_shares": 7_000_000,
    "team_shares": 0,
    "unissued_pool_shares": 3_000_000,
    "investment": "1000000",
    "priced_pre_money": "9000000",
    "priced_preference": {"standard": True},
    "note_valuation_cap": "5000000",
    "note_interest_rate_percent": "10",
    "note_compounding": "annual",
    "note_interest_paid_in_cash": True,
    "note_maturity_months": 36,
    "note_maturity_conversion_price": "0.25",
    "note_change_of_control_at_cap": True,
    "note_months_to_exit": 24,
    "pool_at_exit": "left_out",
    "exit_amounts": ["1000000.01", "7000000"],
}


def test_at_its_cap_with_the_interest_paid_in_cash_and_the_pool_left_out_matches_the_hand_working() -> None:
    """FD 10M: 7M founders and a 3M pool, left out of a sale. A: $1M at $0.90, 10M/9 shares owed $1M. B: a $5M cap
    (price 1/2), 10% annual paid in cash; 24 months to the sale: owed $1.21M, and the $1M principal converts into 2M
    common shares beside the founders' 7M, the $210,000 interest outside every payout line.

    At $1,000,000.01: A's founders get the cent left after the $1M preference; B's get 7/9 of the sale. At $7M: A's
    founders get $6M, B's 49M/9, B - A exactly -5M/9. At maturity (36 months, at $0.25 a share): owed $1,331,000, the
    principal into 4M shares, founders 7/14 against 7M / (10M + 10M/9) = 63/100.
    """
    result = instrument_compare(**_CASH_AT_CAP)
    cent, seven = result.exits_before_any_round
    at_exit = result.note_at_exit
    maturity = result.maturity

    assert at_exit is not None and at_exit.owed is not None and at_exit.owed.owed.exact == 1_210_000
    assert at_exit.converting_amount is not None and at_exit.converting_amount.exact == 1 * _M
    assert at_exit.shares is not None and at_exit.shares.exact == 2 * _M
    assert _payout(cent, "founders").priced.exact == Fraction(1, 100)
    founders_b, new_money_b = _payout(cent, "founders").note, _payout(cent, "new_money").note
    assert founders_b is not None and founders_b.rounded == Decimal("777777.79")
    assert new_money_b is not None and new_money_b.rounded == Decimal("222222.22")
    assert _paid(seven, "founders") == (6 * _M, Fraction(49 * _M, 9), Fraction(-5 * _M, 9))
    assert _paid(seven, "new_money")[1] == Fraction(14 * _M, 9)
    assert maturity is not None and maturity.conversion is not None
    assert maturity.owed.owed.exact == 1_331_000 and maturity.conversion.shares.exact == 4 * _M
    founders = _stake(maturity.conversion.stakes, "founders")
    assert (founders.priced.exact, founders.note.exact) == (Fraction(63, 100), Fraction(1, 2))
    assert {"note_interest_paid_in_cash", "note_paid_below_owed_at_sale"} <= set(result.flags)
    sale_rule = next(row for row in result.assumptions if row.key == "exit_before_any_round")
    assert "interest paid in cash at that conversion is not taken off the sale" in sale_rule.statement


def test_the_cash_interest_counts_toward_what_the_note_is_paid_at_a_sale() -> None:
    """At $5M the note's 2M of 9M common shares fetch $1,111,111.11: under the $1.21M owed, but with the $210,000 paid
    in cash it is paid in full, so the flag is not raised."""
    result = instrument_compare(**{**_CASH_AT_CAP, "exit_amounts": ["5000000"]})

    assert _paid(result.exits_before_any_round[_FIRST], "new_money")[1] == Fraction(10 * _M, 9)
    assert "note_paid_below_owed_at_sale" not in result.flags


def test_an_approximate_stub_at_maturity_and_a_sale_with_no_term_match_the_hand_working() -> None:
    """FD 10M. A: $500k at $0.45, founders 8M / (10M + 10M/9) = 72%. B: 12% annual with a fractional-power stub for 18
    months, $500k × 1.12^1.5 = $592,648.29 (approximate); at $0.30 a share 59,264,829/30 = 1,975,494.3 shares. The
    note has no cap and no sale term, so B is not worked at the $2M sale; A's founders get 8/10 of the $1.5M left
    after the $500k preference."""
    result = instrument_compare(
        founder_shares=8_000_000,
        team_shares=1_000_000,
        unissued_pool_shares=1_000_000,
        investment="500000",
        priced_pre_money="4500000",
        priced_preference={"standard": True},
        note_interest_rate_percent="12",
        note_compounding="annual",
        note_maturity_months=18,
        note_maturity_conversion_price="0.30",
        exit_amounts=["2000000"],
    )
    maturity = result.maturity
    assert maturity is not None and maturity.conversion is not None
    (sale,) = result.exits_before_any_round

    assert maturity.owed.approximate and maturity.owed.owed.exact == Fraction(59_264_829, 100)
    assert maturity.conversion.shares.exact == Fraction(59_264_829, 30)
    founders = _stake(maturity.conversion.stakes, "founders")
    assert founders.priced.exact == Fraction(18, 25) and founders.note.rounded == Decimal("0.668031")
    assert sale.note_refusal == "uncapped_no_change_of_control_term"
    assert _payout(sale, "founders").priced.exact == 1_200_000


def test_with_no_next_round_the_exit_row_names_the_note_s_claim_ahead_of_the_shares() -> None:
    """The waterfall's row says nothing comes ahead of the shareholders; under B a multiple is paid first."""
    rows = {row.key: row for row in instrument_compare(**COMPARE_DX).assumptions}

    assert not any("no debt, fees" in row.statement for row in rows.values())
    assert rows["exit_is_shared_amount"].setting == (
        "option A: nothing ahead of the shareholders; option B: only the note's own claim"
    )
    assert "is paid out of the exit amount first" in rows["exit_is_shared_amount"].statement
    with_round = {row.key: row for row in instrument_compare(**COMPARE_BU).assumptions}
    assert "no debt, fees" in with_round["exit_is_shared_amount"].statement


def test_with_no_next_round_only_the_round_rows_of_a_conversion_that_happens_are_listed() -> None:
    """Company DX: no cap, nothing converts in option A's round today, the note converts only at its maturity."""
    keys = {row.key for row in instrument_compare(**COMPARE_DX).assumptions}
    assert {"interest_conversion", "note_interest", "converted_shares_in_pre_money", "fractional_shares"} <= keys
    assert keys.isdisjoint({"note_cap_basis", "tie_rule", "search"})

    uncapped = {"note_valuation_cap": None, "note_change_of_control_multiple": "2"}
    assert "interest_conversion" not in {row.key for row in instrument_compare(**_bu(**uncapped)).assumptions}
    note = {
        "kind": "note",
        "principal": "200000",
        "interest_rate_percent": "5",
        "months_outstanding": 6,
        "compounding": "simple",
        "valuation_cap": "4000000",
    }
    beside = {row.key for row in instrument_compare(**_bu(**uncapped, existing_instruments=[note])).assumptions}
    assert {"note_cap_basis", "interest_conversion", "tie_rule", "search"} <= beside


def test_existing_instruments_convert_in_option_a_and_hold_no_shares_under_b() -> None:
    safe = {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "5000000"}
    result = instrument_compare(**_bu(existing_instruments=[safe], note_maturity_months=24))
    existing = _stake(result.stakes_now, "existing_investors")

    assert existing.priced_shares.exact > 0 and existing.note_shares.exact == 0
    rule = next(row for row in result.assumptions if row.key == "existing_instruments_rule")
    assert "Under option B no priced round comes, so they stay outstanding" in rule.statement


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"note_months_to_conversion": 12}, "no_next_round_given: note_months_to_conversion is the months"),
        ({"next_rounds": [_ROUND_ONE]}, "note_months_to_conversion is needed with a next round"),
        (
            {"next_rounds": [_ROUND_ONE], "note_months_to_conversion": 12, "note_change_of_control_multiple": "2"},
            "note_change_of_control_multiple: a term of a note with no next round",
        ),
        (
            {"next_rounds": [_ROUND_ONE], "note_months_to_conversion": 12, **_AT_CAP},
            "note_change_of_control_at_cap, note_months_to_exit: a term of a note with no next round",
        ),
        ({**_AT_CAP, "note_change_of_control_multiple": "2"}, "give one change-of-control term"),
        ({**_AT_CAP, "note_valuation_cap": None}, "an uncapped note has no cap to convert at"),
        ({"note_change_of_control_at_cap": True}, "needs note_months_to_exit"),
        ({"note_maturity_conversion_valuation": "5000000"}, "a maturity conversion needs note_maturity_months"),
        (
            {
                "note_maturity_months": 24,
                "note_maturity_conversion_valuation": "5000000",
                "note_maturity_conversion_price": "0.5",
            },
            "not both",
        ),
        ({"exit_amounts": []}, "what the company sells for before any priced round"),
        ({"note_change_of_control_multiple": "0"}, "greater than 0"),
        ({"note_maturity_conversion_price": "-1", "note_maturity_months": 24}, "greater than 0"),
        ({"note_months_to_exit": 601}, "less than or equal to 600"),
        ({"note_owed_months": [12] * 7}, "at most 6 items"),
        ({"note_owed_months": [24, 12, 24]}, "note_owed_months gives month 24 more than once"),
        ({"note_change_of_control_at_cap": "yes"}, "valid boolean"),
    ],
)
def test_terms_that_do_not_fit_the_mode_are_refused_never_assumed(changes: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        InstrumentCompareInput.model_validate(_bu(**changes))


def test_with_no_next_round_the_summary_holds_today_the_maturity_and_each_sale_and_says_where_b_is_not_worked() -> None:
    """Company DX: today and the maturity conversion, then each sale; with no change-of-control term, B is not worked at
    a sale and the summary carries the refusal beside no B figure."""
    result = instrument_compare(**COMPARE_DX)
    summary = result.summary
    maturity = result.maturity

    assert [row.point for row in summary.ownership] == ["today", "maturity"]
    assert maturity is not None and maturity.conversion is not None
    stake = _stake(maturity.conversion.stakes, "founders")
    assert summary.ownership[1].founders.note == stake.note and summary.ownership[1].next_round is None
    for row, sale in zip(summary.founders_payouts, result.exits_before_any_round, strict=True):
        founders = next(payout for payout in sale.payouts if payout.group == "founders")
        assert row.next_round is None and row.exit_amount == sale.exit_amount and row.note_refusal is None
        assert (row.founders.priced, row.founders.note) == (founders.priced, founders.note)

    refused = instrument_compare(**_dx(note_change_of_control_multiple=None)).summary
    assert [row.point for row in refused.ownership] == ["today", "maturity"]
    assert {row.note_refusal for row in refused.founders_payouts} == {"uncapped_no_change_of_control_term"}
    assert all(row.founders.note is None and row.founders.difference is None for row in refused.founders_payouts)
    without_maturity = instrument_compare(**_dx(note_maturity_conversion_valuation=None)).summary
    assert [row.point for row in without_maturity.ownership] == ["today"]
