"""
Unit tests for drift evaluation and trade generation.
"""
import pytest
from app.rebalance.drift import calculate_allocation_drift
from app.rebalance.trades import generate_trades


def test_drift_calculation_and_status():
    current_weights = {"SPY": 0.48, "QQQ": 0.22, "TLT": 0.30}
    target_weights = {"SPY": 0.40, "QQQ": 0.25, "TLT": 0.35}

    reports = calculate_allocation_drift(current_weights, target_weights, drift_threshold=0.05)
    lookup = {r["ticker"]: r for r in reports}

    # SPY drift: 0.48 - 0.40 = +0.08 (+8% > 5% threshold -> action_required)
    assert pytest.approx(lookup["SPY"]["drift"], rel=1e-4) == 0.08
    assert lookup["SPY"]["drift_status"] == "action_required"

    # QQQ drift: 0.22 - 0.25 = -0.03 (-3% between 2.5% and 5% -> warning)
    assert pytest.approx(lookup["QQQ"]["drift"], rel=1e-4) == -0.03
    assert lookup["QQQ"]["drift_status"] == "warning"


def test_generate_trades_buy_sell_classification():
    current_values = {"SPY": 480_000.0, "QQQ": 220_000.0, "TLT": 300_000.0}  # Total 1,000,000
    target_weights = {"SPY": 0.40, "QQQ": 0.25, "TLT": 0.35}
    prices = {"SPY": 480.0, "QQQ": 440.0, "TLT": 100.0}

    trades, summary = generate_trades(
        current_values=current_values,
        target_weights=target_weights,
        current_prices=prices,
        drift_threshold=0.05,
        minimum_trade_value=1000.0,
    )
    trade_map = {t["ticker"]: t for t in trades}

    # SPY target = 400,000; current = 480,000 -> SELL 80,000
    assert trade_map["SPY"]["action"] == "SELL"
    assert pytest.approx(trade_map["SPY"]["trade_value"], rel=1e-4) == -80000.0

    # QQQ target = 250,000; current = 220,000 -> BUY 30,000
    assert trade_map["QQQ"]["action"] == "BUY"
    assert pytest.approx(trade_map["QQQ"]["trade_value"], rel=1e-4) == 30000.0

    # Summary checks
    assert summary["rebalance_required"] is True
    assert summary["assets_outside_threshold"] == 1  # SPY has 8% drift > 5%
