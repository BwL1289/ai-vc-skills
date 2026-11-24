"""The input and result models of every scenario (Pydantic v2, frozen, exact ``Decimal`` in and out).

``equity`` holds the investor and employee scenarios and the tagged ``EquityInput`` / ``EquityResult`` unions, and
re-exports the other modules' names (``equity_pool``, ``equity_round``, ``equity_dilution``, ``equity_vesting``,
``equity_waterfall``, ``equity_deal_check``, ``equity_runway_plan``, ``equity_metrics_check``,
``equity_market_sizing``, ``equity_instrument_compare``, ``equity_pool_plan``); the shared parts live in
``equity_common``.
"""
