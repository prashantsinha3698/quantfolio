"""
Unit tests for portfolio performance metrics.
"""
import numpy as np
import pandas as pd
import pytest

from app.analytics.performance import (
    compute_annualized_volatility,
    compute_cagr,
    compute_calmar_ratio,
    compute_drawdown_events,
    compute_drawdowns,
    compute_sharpe_ratio,
    compute_sortino_ratio,
    compute_total_return,
)


def test_total_return_and_cagr():
    # Exactly 252 days with 0.1% daily return
    dates = pd.date_range("2024-01-01", periods=252, freq="B")
    returns = pd.Series([0.001] * 252, index=dates)

    tot = compute_total_return(returns)
    cagr = compute_cagr(returns, periods_per_year=252)

    # 1.001^252 - 1 ~= 0.2863
    expected_tot = (1.001 ** 252) - 1.0
    assert pytest.approx(tot, rel=1e-4) == expected_tot
    assert pytest.approx(cagr, rel=1e-4) == expected_tot


def test_drawdown_calculation():
    # Sequence: 100 -> 120 -> 90 -> 105 -> 130
    # Returns from 100: +20%, -25% (to 90), +16.6667% (to 105), +23.8095% (to 130)
    dates = pd.date_range("2025-01-01", periods=4, freq="B")
    returns = pd.Series([0.20, -0.25, 0.1666667, 0.2380952], index=dates)

    drawdown_series, max_dd = compute_drawdowns(returns)

    # At peak=120, drops to 90 -> loss is (90 - 120)/120 = -30/120 = -0.25 (-25%)
    assert pytest.approx(max_dd, rel=1e-4) == -0.25
    assert pytest.approx(drawdown_series.iloc[1], rel=1e-4) == -0.25


def test_sharpe_and_sortino():
    dates = pd.date_range("2024-01-01", periods=252, freq="B")
    # Alternating positive and zero returns
    returns = pd.Series([0.002, 0.000] * 126, index=dates)

    sharpe = compute_sharpe_ratio(returns, risk_free_rate=0.02)
    sortino = compute_sortino_ratio(returns, risk_free_rate=0.02)

    assert sharpe > 0.0
    assert sortino > 0.0


def test_calmar_ratio():
    cagr = 0.20
    mdd = -0.10
    calmar = compute_calmar_ratio(cagr, mdd)
    assert pytest.approx(calmar, rel=1e-4) == 2.0
