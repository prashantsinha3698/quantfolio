"""
Conditional Value at Risk (CVaR) / Expected Shortfall engine.
"""
from typing import Tuple
import numpy as np
import pandas as pd


def compute_historical_cvar(
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
    portfolio_value: float = 1_000_000.0,
    horizon_days: int = 1,
) -> Tuple[float, float]:
    """
    Historical Expected Shortfall (CVaR):
    Measures the expected loss given that the loss exceeds the VaR threshold.
    CVaR = Mean(losses | losses >= VaR_threshold)

    Returns:
        (cvar_percentage, cvar_dollar)
    """
    if portfolio_returns.empty:
        return 0.0, 0.0

    # Losses are negative returns
    losses = -portfolio_returns.values
    quantile_level = confidence_level * 100.0
    var_threshold = float(np.percentile(losses, quantile_level))

    tail_losses = losses[losses >= var_threshold]
    if len(tail_losses) == 0:
        cvar_pct = var_threshold
    else:
        cvar_pct = float(np.mean(tail_losses))

    # Scale for horizon
    cvar_pct = cvar_pct * np.sqrt(horizon_days)
    cvar_dollar = cvar_pct * portfolio_value

    return float(cvar_pct), float(cvar_dollar)
