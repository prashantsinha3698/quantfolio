"""
Value at Risk (VaR) computation: Historical Simulation and Parametric Normal methods.
"""
from typing import Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm


def compute_historical_var(
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
    portfolio_value: float = 1_000_000.0,
    horizon_days: int = 1,
) -> Tuple[float, float]:
    """
    Historical Simulation Value at Risk:
    Takes actual historical returns, sorts daily losses, and computes the empirical quantile:
    VaR_alpha = -Quantile(r_p, 1 - alpha) * sqrt(horizon)

    Returns:
        (var_percentage, var_dollar)
    """
    if portfolio_returns.empty:
        return 0.0, 0.0

    # 1 - alpha quantile of returns (e.g. 0.05 quantile for 95% confidence)
    quantile_level = 1.0 - confidence_level
    quantile_return = float(np.percentile(portfolio_returns, quantile_level * 100))

    # Loss is positive if returns are negative
    var_pct = -quantile_return * np.sqrt(horizon_days)
    var_dollar = var_pct * portfolio_value

    return float(var_pct), float(var_dollar)


def compute_parametric_var(
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
    portfolio_value: float = 1_000_000.0,
    horizon_days: int = 1,
) -> Tuple[float, float]:
    """
    Parametric (Variance-Covariance) Value at Risk:
    Assumes portfolio returns follow a normal distribution.
    VaR_alpha = -(mu_daily + z_{1-alpha} * sigma_daily) * sqrt(horizon) * V

    Returns:
        (var_percentage, var_dollar)
    """
    if len(portfolio_returns) <= 1:
        return 0.0, 0.0

    mu_daily = float(portfolio_returns.mean())
    sigma_daily = float(portfolio_returns.std(ddof=1))

    # z critical value for standard normal
    # For alpha = 0.95 -> norm.ppf(0.05) ~ -1.64485
    z_score = norm.ppf(1.0 - confidence_level)

    var_pct = -(mu_daily + z_score * sigma_daily) * np.sqrt(horizon_days)
    var_dollar = var_pct * portfolio_value

    return float(var_pct), float(var_dollar)
