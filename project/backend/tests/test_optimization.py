"""
Unit tests for portfolio optimization and efficient frontier generation.
"""
import numpy as np
import pytest

from app.optimization.optimizer import PortfolioOptimizer


@pytest.fixture
def sample_market_params():
    tickers = ["A", "B", "C", "D"]
    # Expected annual returns
    mu = np.array([0.15, 0.10, 0.08, 0.04])
    # Annualized covariance with varying volatilities and correlations
    vols = np.array([0.22, 0.18, 0.12, 0.06])
    corr = np.array([
        [1.0, 0.6, 0.2, -0.1],
        [0.6, 1.0, 0.1, -0.2],
        [0.2, 0.1, 1.0, 0.3],
        [-0.1, -0.2, 0.3, 1.0],
    ])
    cov = np.outer(vols, vols) * corr
    return tickers, mu, cov


def test_min_volatility_constraints(sample_market_params):
    tickers, mu, cov = sample_market_params
    optimizer = PortfolioOptimizer(tickers, mu, cov, risk_free_rate=0.03)

    result = optimizer.optimize_min_volatility(min_weight=0.0, max_weight=0.60)

    assert result.success is True
    weights = np.array(list(result.weights.values()))

    # Budget constraint: sum(w) == 1.0
    assert pytest.approx(np.sum(weights), abs=1e-4) == 1.0

    # Bounds: 0.0 <= w <= 0.60
    assert np.all(weights >= -1e-6)
    assert np.all(weights <= 0.60 + 1e-4)


def test_max_sharpe_improves_over_equal_weight(sample_market_params):
    tickers, mu, cov = sample_market_params
    rf = 0.03
    optimizer = PortfolioOptimizer(tickers, mu, cov, risk_free_rate=rf)

    # Equal weight portfolio
    eq_w = np.ones(4) / 4.0
    eq_ret = eq_w @ mu
    eq_vol = np.sqrt(eq_w @ cov @ eq_w)
    eq_sharpe = (eq_ret - rf) / eq_vol

    result = optimizer.optimize_max_sharpe(min_weight=0.0, max_weight=1.0)

    assert result.success is True
    # Max Sharpe should be strictly >= equal-weight Sharpe
    assert result.sharpe >= eq_sharpe - 1e-5
