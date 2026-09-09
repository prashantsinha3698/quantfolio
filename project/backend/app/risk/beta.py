"""
Beta, Jensen's Alpha, and Tracking Error analytics against a benchmark.
"""
from typing import Tuple
import numpy as np
import pandas as pd
from app.core.config import ANNUALIZATION_FACTOR


def compute_beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Computes Capital Asset Pricing Model Beta:
    Beta = Cov(r_p, r_m) / Var(r_m)
    """
    # Align dates
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    if len(aligned) <= 2:
        return 1.0

    p_ret = aligned.iloc[:, 0].values
    m_ret = aligned.iloc[:, 1].values

    benchmark_var = np.var(m_ret, ddof=1)
    if benchmark_var < 1e-12:
        return 1.0

    covariance = np.cov(p_ret, m_ret)[0, 1]
    return float(covariance / benchmark_var)


def compute_alpha(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0.04,
) -> float:
    """
    Jensen's Alpha (annualized):
    Alpha = (R_p - R_f) - Beta * (R_m - R_f)
    """
    beta = compute_beta(portfolio_returns, benchmark_returns)
    p_ann = float(portfolio_returns.mean() * ANNUALIZATION_FACTOR)
    m_ann = float(benchmark_returns.mean() * ANNUALIZATION_FACTOR)

    alpha = (p_ann - risk_free_rate) - beta * (m_ann - risk_free_rate)
    return float(alpha)


def compute_tracking_error(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Tracking Error:
    Standard deviation of excess returns (r_p - r_m) annualized by sqrt(252).
    """
    aligned = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
    if len(aligned) <= 2:
        return 0.0

    excess_returns = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    tracking_err = float(excess_returns.std(ddof=1) * np.sqrt(ANNUALIZATION_FACTOR))
    return tracking_err
