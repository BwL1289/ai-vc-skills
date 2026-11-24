"""``cap_table_check``: a founder's cap table checked against itself, worked by exact fractions.

Company CQ (made up, ``tests.support.CAP_TABLE_CQ``) states percents worked on 10,000,000 shares before its 100,000
warrants: every percent is off at two places, the column adds up to 101.00%, common is issued past its authorised
shares, and a departed hire holds 250,000 shares. Company CR (``CAP_TABLE_CR``) is clean, with two SAFEs converted in
the founder's next round and the founders followed from it through two planned rounds. Every expected fraction is
worked by hand (CR's founders after the preview: 8,000,000 of the 22,000,000/(603/400) shares after it, 603/1100).
No DB, no network.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import get_args

import pytest
from equity_calculator.errors import RoundHasNoPrice
from equity_calculator.round import compute_round
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_cap_table_check import (
    CapCheck,
    CapTableCheckInput,
    CapTableCheckResult,
    CapTableFlag,
)
from equity_calculator.schemas.equity_round import RoundInput
from pydantic import ValidationError
from tests.support import CAP_TABLE_CQ, CAP_TABLE_CR, cap_table_check

# Company CR's founders after the preview (603/1100), then after its two planned rounds (kept 3/4, then 4/5).
_CR_AFTER_PREVIEW = Fraction(603, 1100)
_CR_PATH = [Fraction(1809, 4400), Fraction(1809, 5500)]

_FD_CQ = 10_100_000
_OUTSTANDING_CQ = 9_250_000
# Half a hundredth of a point, as a fraction of the whole, for each of CQ's seven percents typed to two places.
_HALF_HUNDREDTH_POINT = Fraction(1, 20_000)
_SEVEN = 7

# Three holders of a third each and nothing else: what rounding to each written place makes of 100%.
_THIRDS = {
    "classes": [{"kind": "common"}],
    "holders": [
        {"share_class": 1, "shares": 1_000_000, "stated_percent": "33.33", "founder": True},
        {"share_class": 1, "shares": 1_000_000, "stated_percent": "33.33", "founder": True},
        {"share_class": 1, "shares": 1_000_000, "stated_percent": "33.33"},
    ],
    "stated_percent_basis": "fully_diluted",
}
# A plain table: 6,000,000 and 3,000,000 common and a 1,000,000 unissued pool, every percent exact.
_PLAIN = {
    "classes": [{"kind": "common"}, {"kind": "options_unissued", "shares": 1_000_000, "stated_percent": "10"}],
    "holders": [
        {"share_class": 1, "shares": 6_000_000, "stated_percent": "60", "founder": True},
        {"share_class": 1, "shares": 3_000_000, "stated_percent": "30"},
    ],
    "stated_percent_basis": "fully_diluted",
}


# One common class stating its 8,000,000 shares and listing two holder lines (5,000,000 and 2,000,000), beside a
# 1,000,000 unissued pool: whether the lines are every holder of it is the founder's word, never assumed.
_LISTED = {
    "classes": [{"kind": "common", "shares": 8_000_000}, {"kind": "options_unissued", "shares": 1_000_000}],
    "holders": [
        {"share_class": 1, "shares": 5_000_000, "founder": True},
        {"share_class": 1, "shares": 2_000_000, "departed": True},
    ],
}
# A note and a SAFE converted in a preview whose pool target is counted in the post-money.
_NOTE_AND_SAFE = {
    "classes": [{"kind": "common"}, {"kind": "options_unissued", "shares": 500_000}],
    "holders": [{"share_class": 1, "shares": 6_000_000, "founder": True}, {"share_class": 1, "shares": 2_000_000}],
    "instruments": [
        {
            "kind": "note",
            "principal": "500000",
            "interest_rate_percent": "8",
            "months_outstanding": 12,
            "compounding": "simple",
            "valuation_cap": "5000000",
        },
        {"kind": "safe", "purchase_amount": "1000000", "valuation_cap": "10000000"},
    ],
    "conversion_preview": {
        "pre_money": "20000000",
        "investment": "5000000",
        "target_pool_percent": "10",
        "pool_timing": "post_money",
    },
}


def _with(base: dict[str, object], **fields: object) -> dict[str, object]:
    return {**base, **fields}


def _listed(holder_lines: str, shares: int = 8_000_000, **fields: object) -> dict[str, object]:
    """``_LISTED`` with its common class's shares and the founder's word on its holder lines."""
    common = {"kind": "common", "shares": shares, "holder_lines": holder_lines}
    return _with(_LISTED, classes=[common, {"kind": "options_unissued", "shares": 1_000_000}], **fields)


def _classes_stating(*percents: str) -> dict[str, object]:
    """Three common classes of 6,000,000, 3,000,000 and 1,000,000 shares, each stating a percent of fully diluted."""
    shares = (6_000_000, 3_000_000, 1_000_000)
    classes = [
        {"kind": "common", "shares": count, "stated_percent": percent}
        for count, percent in zip(shares, percents, strict=True)
    ]
    return {"classes": classes, "stated_percent_basis": "fully_diluted"}


def _check(result: CapTableCheckResult, key: str, index: int | None = None) -> CapCheck:
    return next(check for check in result.checks if check.key == key and check.index == index)


def test_company_cq_adds_its_classes_to_the_fully_diluted_shares() -> None:
    result = cap_table_check(**CAP_TABLE_CQ)

    assert result.fully_diluted_shares.exact == _FD_CQ
    assert result.outstanding_shares.exact == _OUTSTANDING_CQ
    common, preferred, granted, pool, warrants = result.classes
    assert common.shares.exact == 8_250_000 and common.holder_shares is not None
    assert common.fully_diluted_fraction.exact == Fraction(165, 202)
    assert common.outstanding_fraction is not None and common.outstanding_fraction.exact == Fraction(33, 37)
    assert preferred.fully_diluted_fraction.exact == Fraction(10, 101)
    assert granted.outstanding_fraction is None and pool.outstanding_fraction is None
    assert warrants.fully_diluted_fraction.exact == Fraction(1, 101)
    assert sum(row.fully_diluted_fraction.exact for row in result.classes) == 1


def test_each_holder_line_is_its_shares_over_the_fully_diluted_and_the_outstanding_shares() -> None:
    result = cap_table_check(**CAP_TABLE_CQ)

    first, second, departed = result.holders
    assert first.fully_diluted_fraction.exact == Fraction(45, 101)
    assert first.outstanding_fraction is not None and first.outstanding_fraction.exact == Fraction(18, 37)
    assert second.fully_diluted_fraction.exact == Fraction(35, 101)
    assert departed.departed and not departed.founder
    assert result.founders_fraction is not None and result.founders_fraction.exact == Fraction(80, 101)
    assert result.departed_fraction is not None and result.departed_fraction.exact == Fraction(5, 202)


def test_the_table_s_total_is_checked_only_by_equality() -> None:
    check = _check(cap_table_check(**CAP_TABLE_CQ), "fully_diluted_total")

    assert check.stated.exact == 10_000_000 and check.computed.exact == _FD_CQ
    assert check.difference.exact == 100_000
    assert check.verdict == "mismatch" and check.within_rounding is None


def test_a_percent_typed_to_two_places_is_off_when_its_rounding_differs() -> None:
    result = cap_table_check(**CAP_TABLE_CQ)
    first = _check(result, "holder_percent", 1)

    assert first.computed.exact == Fraction(45, 101)
    assert first.stated.exact == Fraction(45, 100)
    assert first.difference.exact == Fraction(45, 101) - Fraction(45, 100)
    assert first.within_rounding is False and first.verdict == "mismatch"
    assert [check.verdict for check in result.checks if check.key.endswith("_percent")] == ["mismatch"] * 7


def test_the_percent_column_read_line_by_line_adds_up_to_101_percent() -> None:
    check = _check(cap_table_check(**CAP_TABLE_CQ), "line_percent_total")

    assert check.stated.exact == Fraction(101, 100)
    assert check.difference.exact == Fraction(-1, 100)
    assert check.rounding_allowance is not None
    assert check.rounding_allowance.exact == _SEVEN * _HALF_HUNDREDTH_POINT
    assert check.verdict == "mismatch" and check.within_rounding is False


def test_company_cq_raises_every_flag_its_table_holds_in_order() -> None:
    result = cap_table_check(**CAP_TABLE_CQ)

    assert result.flags == (
        "percents_do_not_sum",
        "over_authorised",
        "common_authorised_below_fully_diluted",
        "unconverted_instruments_present",
        "departed_holders_share",
    )
    assert result.verdict == "mismatch"
    assert set(result.flags) <= set(get_args(CapTableFlag))


def test_issued_shares_are_set_against_the_authorised_shares_and_the_plan_s_reserve() -> None:
    result = cap_table_check(**CAP_TABLE_CQ)
    common, preferred, *_ = result.classes

    assert common.authorised_headroom is not None and common.authorised_headroom.exact == -250_000
    assert common.over_authorised is True and preferred.over_authorised is False
    assert result.plan_reserve is not None and result.plan_reserve.headroom.exact == 0
    assert result.plan_reserve.over_authorised is False
    assert result.common_reserve is not None and result.common_reserve.headroom.exact == -2_100_000
    assert result.common_reserve.short is True


def test_an_option_plan_past_its_reserve_is_over_authorised() -> None:
    result = cap_table_check(**_with(CAP_TABLE_CQ, option_plan_reserve=700_000))

    assert result.plan_reserve is not None and result.plan_reserve.headroom.exact == -50_000
    assert result.plan_reserve.over_authorised is True
    assert "over_authorised" in result.flags


def test_thirds_written_to_two_places_add_up_within_what_rounding_explains() -> None:
    result = cap_table_check(**_THIRDS)
    check = _check(result, "line_percent_total")

    assert check.stated.exact == Fraction(9_999, 10_000)
    assert check.verdict == "consistent" and check.within_rounding is True
    assert all(item.verdict == "consistent" for item in result.checks)
    assert "percents_do_not_sum" not in result.flags


def test_a_class_s_stated_total_is_used_and_complete_holder_lines_are_checked_against_it() -> None:
    short = cap_table_check(**_listed("complete"))
    held = cap_table_check(**_listed("complete", shares=7_000_000))
    check = _check(short, "class_shares", 1)

    assert short.classes[0].shares.exact == 8_000_000 and short.fully_diluted_shares.exact == 9_000_000
    assert check.stated.exact == 8_000_000 and check.computed.exact == 7_000_000
    assert check.difference.exact == -1_000_000 and check.verdict == "mismatch"
    assert short.classes[0].unlisted_shares is None and "holder_lines_exceed_class" not in short.flags
    assert short.founders_fraction is not None and short.founders_fraction.exact == Fraction(5, 9)
    assert _check(held, "class_shares", 1).verdict == "consistent" and held.verdict == "consistent"


def test_partial_holder_lines_leave_the_rest_in_no_line_and_are_not_checked() -> None:
    result = cap_table_check(**_listed("partial"))

    assert result.checks == () and result.verdict == "not_checked"
    common = result.classes[0]
    assert common.holder_shares is not None and common.holder_shares.exact == 7_000_000
    assert common.unlisted_shares is not None and common.unlisted_shares.exact == 1_000_000
    assert result.founders_fraction is not None and result.founders_fraction.exact == Fraction(5, 9)
    assert result.departed_fraction is not None and result.departed_fraction.exact == Fraction(2, 9)


def test_a_partial_class_s_own_percent_stands_for_it_in_the_percent_column() -> None:
    holders = [
        {"share_class": 1, "shares": 5_000_000, "stated_percent": "50", "founder": True},
        {"share_class": 1, "shares": 2_000_000, "stated_percent": "20"},
    ]
    classes = [
        {"kind": "common", "shares": 9_000_000, "stated_percent": "90", "holder_lines": "partial"},
        {"kind": "options_unissued", "shares": 1_000_000, "stated_percent": "10"},
    ]
    result = cap_table_check(classes=classes, holders=holders, stated_percent_basis="fully_diluted")

    # Read line by line, the two lines' 70% would stand for the class's 90%: a column short by what no line lists.
    assert [check.key for check in result.checks if check.key.endswith("_total")] == ["class_percent_total"]
    assert result.verdict == "consistent" and "percents_do_not_sum" not in result.flags


@pytest.mark.parametrize("holder_lines", ["complete", "partial"])
def test_holder_lines_past_their_class_leave_out_every_founders_and_departed_figure(holder_lines: str) -> None:
    preview = {
        "instruments": [{"kind": "safe", "purchase_amount": "500000", "valuation_cap": "10000000"}],
        "conversion_preview": {"pre_money": "18000000", "investment": "4000000"},
        "planned_rounds": [{"investor_percent": "20"}],
    }
    result = cap_table_check(**_listed(holder_lines, shares=6_000_000, **preview))
    check = _check(result, "class_shares", 1)

    assert check.computed.exact == 7_000_000 and check.verdict == "mismatch"
    assert result.flags[0] == "holder_lines_exceed_class"
    assert "path_leaves_out_instruments" not in result.flags and "departed_holders_share" in result.flags
    assert result.founders_fraction is None and result.departed_fraction is None
    assert result.preview is not None and result.preview.founders_after is None
    assert result.preview.departed_after is None
    assert result.founder_path is None and result.classes[0].unlisted_shares is None
    keys = [row.key for row in result.assumptions]
    assert "founder_path" not in keys and "dilution_rule" not in keys


def test_a_line_marked_founder_and_departed_counts_in_both_shares_and_the_path() -> None:
    holders = [
        {"share_class": 1, "shares": 6_000_000, "founder": True},
        {"share_class": 1, "shares": 4_000_000, "founder": True, "departed": True},
    ]
    result = cap_table_check(classes=[{"kind": "common"}], holders=holders, planned_rounds=[{"investor_percent": "20"}])

    assert result.founders_fraction is not None and result.founders_fraction.exact == 1
    assert result.departed_fraction is not None and result.departed_fraction.exact == Fraction(2, 5)
    assert result.founder_path is not None and result.founder_path.final.exact == Fraction(4, 5)


def test_the_outstanding_basis_checks_stock_percents_against_the_issued_stock() -> None:
    stock = {
        "classes": [{"kind": "common"}, {"kind": "options_unissued", "shares": 1_000_000}],
        "holders": [
            {"share_class": 1, "shares": 6_000_000, "stated_percent": "66.67", "founder": True},
            {"share_class": 1, "shares": 3_000_000, "stated_percent": "33.33"},
        ],
        "stated_percent_basis": "outstanding",
    }
    result = cap_table_check(**stock)

    assert _check(result, "holder_percent", 1).computed.exact == Fraction(2, 3)
    assert all(check.verdict == "consistent" for check in result.checks)
    assert _check(result, "line_percent_total").verdict == "consistent"


def test_a_percent_held_only_by_the_tolerance_is_flagged() -> None:
    holders = [
        {"share_class": 1, "shares": 6_000_000, "stated_percent": "60.40", "founder": True},
        {"share_class": 1, "shares": 3_000_000, "stated_percent": "30"},
    ]
    result = cap_table_check(**_with(_PLAIN, holders=holders, tolerance_points="0.5"))
    check = _check(result, "holder_percent", 1)

    assert check.verdict == "consistent" and check.within_rounding is False
    assert "consistent_beyond_rounding" in result.flags


def test_three_classes_stating_exact_percents_add_up_within_their_whole_point_rounding() -> None:
    result = cap_table_check(**_classes_stating("60", "30", "10"))
    check = _check(result, "class_percent_total")

    assert check.stated.exact == 1 and check.difference.exact == 0
    assert check.rounding_allowance is not None and check.rounding_allowance.exact == Fraction(3, 200)
    assert check.verdict == "consistent" and check.within_rounding is True
    assert result.verdict == "consistent" and result.flags == ()


def test_thirds_written_as_whole_points_add_up_to_99_within_what_rounding_explains() -> None:
    thirds = {"classes": [{"kind": "common", "shares": 1, "stated_percent": "33"}] * 3}
    result = cap_table_check(**thirds, stated_percent_basis="fully_diluted")
    check = _check(result, "class_percent_total")

    assert check.stated.exact == Fraction(99, 100) and check.difference.exact == Fraction(1, 100)
    assert all(item.verdict == "consistent" and item.within_rounding is True for item in result.checks)


def test_a_class_column_adding_up_to_105_percent_cannot_be_roundings() -> None:
    result = cap_table_check(**_classes_stating("60", "30", "15"))
    check = _check(result, "class_percent_total")

    assert check.stated.exact == Fraction(21, 20) and check.verdict == "mismatch"
    assert _check(result, "class_percent", 3).verdict == "mismatch"
    assert result.flags == ("percents_do_not_sum",) and result.verdict == "mismatch"


def test_a_table_with_nothing_stated_is_not_checked() -> None:
    result = cap_table_check(classes=[{"kind": "common", "shares": 1_000_000}])

    assert result.checks == () and result.verdict == "not_checked"
    assert result.flags == () and result.founders_fraction is None


def test_the_preview_is_the_round_scenario_worked_on_the_cap_table() -> None:
    result = cap_table_check(**CAP_TABLE_CR)
    preview = result.preview
    direct = compute_round(
        RoundInput.model_validate(
            {
                "fully_diluted_shares": 10_000_000,
                "unissued_pool_shares": 500_000,
                "pre_money": "18000000",
                "investment": "4000000",
                "instruments": CAP_TABLE_CR["instruments"],
            }
        )
    )

    assert preview is not None and preview.round == direct
    total = direct.total_shares.exact
    assert preview.founders_after is not None and preview.founders_after.exact == Fraction(8_000_000) / total
    assert preview.departed_after is not None and preview.departed_after.exact == Fraction(500_000) / total
    assert preview.stake_kept.exact == Fraction(10_000_000) / total
    assert [row.kind for row in preview.classes] == ["common", "options_granted"]
    parts = [
        *(row.fraction_after.exact for row in preview.classes),
        preview.option_pool_after.exact,
        *(row.fraction_after.exact for row in preview.instruments),
        preview.investors_after.exact,
    ]
    assert sum(parts) == 1


def test_the_preview_converts_a_note_with_its_interest_and_tops_the_pool_up_after_the_round() -> None:
    preview = cap_table_check(**_NOTE_AND_SAFE).preview
    direct = compute_round(
        RoundInput.model_validate(
            {
                "fully_diluted_shares": 8_500_000,
                "unissued_pool_shares": 500_000,
                "pre_money": "20000000",
                "investment": "5000000",
                "target_pool_percent": "10",
                "pool_timing": "post_money",
                "instruments": _NOTE_AND_SAFE["instruments"],
            }
        )
    )

    assert preview is not None and preview.round == direct
    note = direct.conversions[0]
    assert note.accrued_interest is not None and note.accrued_interest.exact == 40_000
    assert note.converting_amount.exact == 540_000
    assert note.conversion_price.exact == Fraction(10, 17) and note.shares.exact == 918_000
    assert direct.new_pool_shares.exact > 0 and direct.pool_already_large_enough is False
    assert preview.instruments[0].shares == note.shares


def test_with_a_preview_the_founders_path_starts_after_it() -> None:
    result = cap_table_check(**CAP_TABLE_CR)
    path = result.founder_path

    assert result.preview is not None and result.preview.founders_after is not None
    assert result.preview.founders_after.exact == _CR_AFTER_PREVIEW
    assert path is not None and path.starts_from == "conversion_preview"
    assert path.start.exact == _CR_AFTER_PREVIEW
    assert [kept.exact for kept in path.kept] == [Fraction(3, 4), Fraction(4, 5)]
    assert path.post_money == (None, None)
    assert [stake.exact for stake in path.stakes] == _CR_PATH
    assert path.final.exact == _CR_PATH[-1]


def test_without_a_preview_the_founders_path_starts_today_and_flags_the_instruments() -> None:
    result = cap_table_check(**_with(CAP_TABLE_CR, conversion_preview=None))
    path = result.founder_path

    assert path is not None and path.starts_from == "today" and path.start.exact == Fraction(4, 5)
    assert [stake.exact for stake in path.stakes] == [Fraction(3, 5), Fraction(12, 25)]
    assert result.flags[-1] == "path_leaves_out_instruments"
    statement = next(row.statement for row in result.assumptions if row.key == "founder_path")
    assert "It converts no SAFE or note" in statement


def test_the_path_publishes_each_round_s_kept_share_never_a_made_up_holder_s_stake() -> None:
    result = cap_table_check(
        classes=[{"kind": "common"}, {"kind": "options_unissued", "shares": 2_000_000}],
        holders=[{"share_class": 1, "shares": 8_000_000, "founder": True}],
        planned_rounds=[{"pre_money": "18000000", "investment": "4000000"}],
    )
    path = result.founder_path

    assert path is not None and path.kept[0].exact == Fraction(9, 11)
    assert path.post_money[0] is not None and path.post_money[0].exact == 22_000_000
    assert path.final.exact == Fraction(36, 55)
    assert "dilution" not in result.model_dump()["founder_path"]
    assert "dilution_rule" in [row.key for row in result.assumptions]


def test_company_cr_is_consistent_and_flags_what_it_leaves_open() -> None:
    result = cap_table_check(**CAP_TABLE_CR)

    assert result.verdict == "consistent"
    assert result.flags == ("unconverted_instruments_present", "departed_holders_share")
    assert result.instruments_amount is not None and result.instruments_amount.exact == 1_500_000


def test_the_nested_rows_join_the_assumptions_once_each_after_legal_validity() -> None:
    rows = cap_table_check(**CAP_TABLE_CR).assumptions
    keys = [row.key for row in rows]

    assert len(keys) == len(set(keys))
    assert {"fully_diluted_basis", "legal_validity", "safe_price_rule", "dilution_rule"} <= set(keys)
    assert keys.index("legal_validity") < keys.index("company_capitalization") < keys.index("dilution_rule")
    assert "after the conversion preview" in rows[keys.index("founder_path")].setting
    assert "preferred_as_converted" not in keys
    assert "preferred_as_converted" in [row.key for row in cap_table_check(**CAP_TABLE_CQ).assumptions]


def test_a_warrant_s_count_is_the_warrant_s_question_and_the_reserve_is_not_room_to_grant() -> None:
    rows = {row.key: row for row in cap_table_check(**CAP_TABLE_CQ).assumptions}

    warrant_source = "unverified (the warrant decides; a question for the company's lawyer)"
    assert rows["warrants_as_exercised"].source == warrant_source
    assert "not counted against its reserve here" in rows["authorised_shares"].statement


def test_a_preview_with_no_price_raises_the_round_s_error() -> None:
    no_price = _with(
        CAP_TABLE_CR,
        instruments=[{"kind": "safe", "purchase_amount": "250000", "discount_percent": "50"}],
        conversion_preview={"pre_money": "1000000", "investment": "1000000", "target_pool_percent": "25"},
    )

    with pytest.raises(RoundHasNoPrice):
        compute(CapTableCheckInput.model_validate(no_price))


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        (_with(_PLAIN, stated_percent_basis=None), "a stated_percent needs stated_percent_basis"),
        (
            {"classes": [{"kind": "common", "shares": 10}], "stated_percent_basis": "fully_diluted"},
            "stated_percent_basis is given, but no class",
        ),
        (
            _with(_PLAIN, stated_percent_basis="outstanding"),
            "on the outstanding basis only common and preferred lines have a percent",
        ),
        (
            _with(_PLAIN, holders=[{"share_class": 3, "shares": 10}]),
            "holders item 1 names share_class 3, past the last of the 2 given",
        ),
        (_with(_PLAIN, holders=[{"share_class": 2, "shares": 10}]), "holders item 1 is in the unissued pool"),
        ({"classes": [{"kind": "common"}]}, "classes item 1 gives neither shares nor a holder line"),
        (
            {"classes": [{"kind": "common", "shares": 10}], "option_plan_reserve": 5},
            "option_plan_reserve needs an options_granted or options_unissued class",
        ),
        (
            {"classes": [{"kind": "common", "shares": 10}], "planned_rounds": [{"investor_percent": "20"}]},
            "planned_rounds needs at least one holder line marked founder",
        ),
        (
            _with(_PLAIN, conversion_preview={"pre_money": "8000000", "investment": "2000000"}),
            "conversion_preview needs at least one SAFE or note",
        ),
        (
            {"classes": [{"kind": "options_granted", "shares": 10, "authorised_shares": 20}]},
            "authorised_shares is for a common or preferred class",
        ),
        ({"classes": [{"kind": "common", "shares": 0}]}, "no class holds a share"),
        (
            {
                "classes": [{"kind": "common", "shares": 0, "stated_percent": "0"}, {"kind": "warrants", "shares": 5}],
                "stated_percent_basis": "outstanding",
            },
            "the outstanding basis needs common or preferred shares",
        ),
        (
            {
                "classes": [{"kind": "options_unissued", "shares": 10}],
                "instruments": [{"kind": "safe", "purchase_amount": "100", "valuation_cap": "1000"}],
                "conversion_preview": {"pre_money": "8000000", "investment": "2000000"},
            },
            "conversion_preview needs a class that holds shares besides the unissued pool",
        ),
        (_LISTED, "classes item 1 gives both shares and holder lines: say with holder_lines whether"),
        (
            _with(_PLAIN, classes=[{"kind": "common", "holder_lines": "complete"}, {"kind": "options_unissued"}]),
            "classes item 1 gives holder_lines, which is only for a class with both shares and holder lines",
        ),
        (_listed("some"), "Input should be 'complete' or 'partial'"),
        (
            _with(
                CAP_TABLE_CR,
                conversion_preview={"pre_money": "8000000", "investment": "2000000", "target_pool_percent": "80"},
            ),
            "target_pool_percent",
        ),
        (_with(_PLAIN, holders=[{"share_class": "1", "shares": 10}]), "Input should be a valid integer"),
        (
            _with(_PLAIN, holders=[{"share_class": 1, "shares": 10, "founder": "yes"}]),
            "Input should be a valid boolean",
        ),
        (_with(_PLAIN, holders=[{"share_class": 1, "shares": 0}]), "Input should be greater than 0"),
        ({"classes": []}, "at least 1 item"),
    ],
)
def test_a_table_that_cannot_be_checked_is_refused_saying_why(fields: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError) as caught:
        CapTableCheckInput.model_validate(fields)

    assert message in str(caught.value)


def test_a_stated_percent_keeps_the_places_it_is_typed_with() -> None:
    inputs = CapTableCheckInput.model_validate(CAP_TABLE_CQ)

    assert inputs.holders[0].stated_percent == Decimal("45.00")
    assert str(inputs.holders[0].stated_percent) == "45.00"
