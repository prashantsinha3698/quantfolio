"""
Unit tests for returns computation and portfolio aggregation.
"""
import numpy as np
import pandas as pd
import pytest

from app.analytics.returns import compute_portfolio_returns, compute_wealth_index


def test_portfolio_returns_aggregation():
    # 3 assets, 4 periods
    dates = pd.date_range("2025-01-01", periods=4, freq="B")
    returns_df = pd.DataFrame(
        {
            "A": [0.01, -0.02, 0.03, 0.00],
            "B": [0.02, 0.01, -0.01, 0.04],
            "C": [0.00, 0.03, 0.02, -0.01],
        },
        index=dates,
    )
    weights = {"A": 0.50, "B": 0.30, "C": 0.20}

    port_ret = compute_portfolio_returns(returns_df, weights)

    # Manual expected:
    # t0: 0.5*0.01 + 0.3*0.02 + 0.2*0.00 = 0.005 + 0.006 + 0.000 = 0.011
    # t1: 0.5*(-0.02) + 0.3*(0.01) + 0.2*(0.03) = -0.01 + 0.003 + 0.006 = -0.001
    assert pytest.approx(port_ret.iloc[0], rel=1e-5) == 0.011
    assert pytest.approx(port_ret.iloc[1], rel=1e-5) == -0.001


def test_wealth_index_growth():
    dates = pd.date_range("2025-01-01", periods=3, freq="B")
    returns_series = pd.Series([0.10, -0.10, 0.05], index=dates)

    wealth = compute_wealth_index(returns_series, initial_capital=1000.0)

    # 1000 * 1.10 = 1100
    # 1100 * 0.90 = 990
    # 990 * 1.05 = 1039.5
    assert pytest.approx(wealth.iloc[0], rel=1e-5) == 1100.0
    assert pytest.approx(wealth.iloc[1], rel=1e-5) == 990.0
    assert pytest.approx(wealth.iloc[2], rel=1e-5) == 1039.5
