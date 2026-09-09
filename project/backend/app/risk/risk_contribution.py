"""
Component Risk Contribution and Marginal Risk Decomposition.
"""
from typing import Dict, List
import numpy as np
import pandas as pd
from app.risk.covariance import CovarianceEstimator


def compute_risk_contributions(
    returns_df: pd.DataFrame,
    weights_dict: Dict[str, float],
) -> List[Dict[str, float]]:
    """
    Decomposes portfolio volatility into individual asset contributions:
    - Marginal Risk Contribution: MRC_i = (Sigma @ w)_i / sigma_p
    - Component Risk Contribution: RC_i = w_i * MRC_i
    - Percentage Risk Contribution: PRC_i = RC_i / sigma_p
    Mathematical invariant: sum(PRC_i) == 1.0 (100%)
    """
    tickers = list(returns_df.columns)
    n = len(tickers)
    if n == 0:
        return []

    # Align weights array
    w = np.array([weights_dict.get(t, 0.0) for t in tickers], dtype=float)
    if w.sum() > 0:
        w = w / w.sum()

    cov_matrix = CovarianceEstimator.sample_covariance(returns_df, annualized=True)
    cov_matrix, _ = CovarianceEstimator.stabilize_covariance(cov_matrix)

    # Portfolio annualized variance & volatility
    port_variance = float(w @ cov_matrix @ w)
    port_vol = np.sqrt(max(port_variance, 1e-12))

    # Marginal Risk Contribution vector: (Sigma @ w) / sigma_p
    marginal_rc = (cov_matrix @ w) / port_vol

    # Component Risk Contribution vector: w * MRC
    component_rc = w * marginal_rc

    # Percentage Risk Contribution vector: RC / sigma_p
    percent_rc = component_rc / port_vol

    items = []
    for idx, ticker in enumerate(tickers):
        items.append({
            "ticker": ticker,
            "weight": float(round(w[idx], 4)),
            "marginal_risk_contribution": float(round(marginal_rc[idx], 4)),
            "component_risk_contribution": float(round(component_rc[idx], 4)),
            "percentage_risk_contribution": float(round(percent_rc[idx], 4)),
        })

    return items
