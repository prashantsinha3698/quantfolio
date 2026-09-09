"""
Unit tests for risk metrics, VaR/CVaR, covariance stabilization, and risk contributions.
"""
import numpy as np
import pandas as pd
import pytest

from app.risk.beta import compute_beta
from app.risk.correlation import compute_correlation_matrix
from app.risk.covariance import CovarianceEstimator
from app.risk.cvar import compute_historical_cvar
from app.risk.risk_contribution import compute_risk_contributions
from app.risk.var import compute_historical_var, compute_parametric_var


def test_covariance_psd_stabilization():
    # Construct a non-positive semi-definite matrix
    bad_matrix = np.array([
        [1.0, 0.9, 0.9],
        [0.9, 1.0, 0.9],
        [0.9, 0.9, 0.5],  # Ill-conditioned
    ])
    stabilized, was_stabilized = CovarianceEstimator.stabilize_covariance(bad_matrix)
    is_psd = CovarianceEstimator.is_positive_semi_definite(stabilized)
    assert is_psd is True


def test_correlation_diagonal():
    np.random.seed(42)
    returns = pd.DataFrame(np.random.normal(0, 0.01, size=(100, 3)), columns=["A", "B", "C"])
    corr_data = compute_correlation_matrix(returns)
    matrix = np.array(corr_data["matrix"])

    # Diagonal must be 1.0
    for i in range(3):
        assert pytest.approx(matrix[i, i], rel=1e-4) == 1.0


def test_var_and_cvar_relation():
    np.random.seed(42)
    returns = pd.Series(np.random.normal(0.0005, 0.015, 1000))
    capital = 1_000_000.0

    h_var_pct, h_var_dlr = compute_historical_var(returns, confidence_level=0.95, portfolio_value=capital)
    h_cvar_pct, h_cvar_dlr = compute_historical_cvar(returns, confidence_level=0.95, portfolio_value=capital)

    # Invariant: CVaR (Expected Shortfall) must be >= VaR
    assert h_cvar_pct >= h_var_pct
    assert h_cvar_dlr >= h_var_dlr


def test_beta_calculation():
    # Create benchmark and portfolio with known relation: r_p = 1.5 * r_m + noise
    np.random.seed(42)
    m_ret = pd.Series(np.random.normal(0.001, 0.01, 500))
    p_ret = 1.5 * m_ret + pd.Series(np.random.normal(0.0, 0.001, 500))

    beta = compute_beta(p_ret, m_ret)
    assert pytest.approx(beta, rel=0.05) == 1.5


def test_risk_contribution_invariant():
    """
    Fundamental quantitative invariant:
    Sum of percentage risk contributions across assets must equal 100% (1.0).
    """
    np.random.seed(42)
    returns_df = pd.DataFrame(
        np.random.normal(0.0005, 0.015, size=(252, 4)),
        columns=["SPY", "QQQ", "GLD", "TLT"],
    )
    weights = {"SPY": 0.40, "QQQ": 0.30, "GLD": 0.15, "TLT": 0.15}

    rc_items = compute_risk_contributions(returns_df, weights)
    prc_sum = sum(item["percentage_risk_contribution"] for item in rc_items)

    assert pytest.approx(prc_sum, rel=1e-3) == 1.0
