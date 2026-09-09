"""
Portfolio returns calculation and wealth index generator.
"""
from typing import Dict, Union
import numpy as np
import pandas as pd


def compute_portfolio_returns(
    returns_df: pd.DataFrame,
    weights: Union[Dict[str, float], np.ndarray, pd.Series],
) -> pd.Series:
    """
    Computes daily portfolio return series: r_p,t = w^T r_t

    Args:
        returns_df: DataFrame of daily simple returns for each asset.
        weights: Dictionary or array of asset weights.

    Returns:
        pd.Series: Daily portfolio simple returns.
    """
    if isinstance(weights, dict):
        # Align weights with returns DataFrame columns
        aligned_weights = np.array([weights.get(col, 0.0) for col in returns_df.columns])
    elif isinstance(weights, pd.Series):
        aligned_weights = weights.reindex(returns_df.columns).fillna(0.0).values
    else:
        aligned_weights = np.asarray(weights)

    # Normalize weights to sum to 1 if small floating point drift
    weight_sum = np.sum(aligned_weights)
    if weight_sum > 0:
        aligned_weights = aligned_weights / weight_sum

    # Matrix multiplication: (T x N) @ (N,) -> (T,)
    portfolio_daily = returns_df.values @ aligned_weights
    series = pd.Series(portfolio_daily, index=returns_df.index, name="Portfolio_Return")
    return series


def compute_wealth_index(returns_series: pd.Series, initial_capital: float = 1_000_000.0) -> pd.Series:
    """
    Computes cumulative portfolio wealth index:
    W_t = W_0 * prod_{i=1}^t (1 + r_i)
    """
    growth_factors = 1.0 + returns_series
    wealth = initial_capital * growth_factors.cumprod()
    wealth.name = "Portfolio_Wealth"
    return wealth
