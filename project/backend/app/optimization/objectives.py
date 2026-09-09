"""
Objective functions for SciPy portfolio optimization.
"""
import numpy as np


def portfolio_variance(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Annualized portfolio variance: w^T Sigma w"""
    return float(weights @ cov_matrix @ weights)


def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """Annualized portfolio volatility: sqrt(w^T Sigma w)"""
    var = weights @ cov_matrix @ weights
    return float(np.sqrt(max(var, 1e-12)))


def portfolio_expected_return(weights: np.ndarray, expected_returns: np.ndarray) -> float:
    """Expected annualized portfolio return: w^T mu"""
    return float(weights @ expected_returns)


def negative_sharpe_ratio(
    weights: np.ndarray,
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.04,
) -> float:
    """
    Negative Sharpe ratio for minimization:
    - (w^T mu - R_f) / sqrt(w^T Sigma w)
    """
    port_ret = float(weights @ expected_returns)
    port_vol = float(np.sqrt(max(weights @ cov_matrix @ weights, 1e-12)))
    if port_vol < 1e-9:
        return 0.0
    return -(port_ret - risk_free_rate) / port_vol
