"""
Efficient Frontier multi-point generation and portfolio comparison engine.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np

from app.optimization.objectives import portfolio_expected_return, portfolio_volatility
from app.optimization.optimizer import PortfolioOptimizer


def generate_efficient_frontier(
    tickers: List[str],
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    current_weights: Dict[str, float],
    risk_free_rate: float = 0.04,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
    n_points: int = 30,
) -> Dict[str, any]:
    """
    Generates a structured efficient frontier curve by solving for the minimum volatility
    at multiple target return levels between the minimum-volatility portfolio and the
    maximum feasible return.
    """
    optimizer = PortfolioOptimizer(
        tickers=tickers,
        expected_returns=expected_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )

    # 1. Min Volatility Portfolio
    min_vol_res = optimizer.optimize_min_volatility(min_weight, max_weight)

    # 2. Max Sharpe Portfolio
    max_sharpe_res = optimizer.optimize_max_sharpe(min_weight, max_weight)

    # 3. Current Portfolio Metrics
    curr_w = np.array([current_weights.get(t, 0.0) for t in tickers], dtype=float)
    if curr_w.sum() > 0:
        curr_w = curr_w / curr_w.sum()
    curr_ret = portfolio_expected_return(curr_w, expected_returns)
    curr_vol = portfolio_volatility(curr_w, cov_matrix)
    curr_sharpe = (curr_ret - risk_free_rate) / curr_vol if curr_vol > 1e-9 else 0.0

    current_point = {
        "label": "Current Portfolio",
        "expected_return": float(round(curr_ret, 4)),
        "volatility": float(round(curr_vol, 4)),
        "sharpe": float(round(curr_sharpe, 4)),
        "weights": {t: float(round(w, 4)) for t, w in zip(tickers, curr_w)},
    }

    min_vol_point = {
        "label": "Minimum Volatility",
        "expected_return": float(round(min_vol_res.expected_return, 4)),
        "volatility": float(round(min_vol_res.volatility, 4)),
        "sharpe": float(round(min_vol_res.sharpe, 4)),
        "weights": min_vol_res.weights,
    }

    max_sharpe_point = {
        "label": "Maximum Sharpe",
        "expected_return": float(round(max_sharpe_res.expected_return, 4)),
        "volatility": float(round(max_sharpe_res.volatility, 4)),
        "sharpe": float(round(max_sharpe_res.sharpe, 4)),
        "weights": max_sharpe_res.weights,
    }

    # 4. Individual assets performance points
    individual_assets = []
    for i, t in enumerate(tickers):
        single_w = np.zeros(len(tickers))
        single_w[i] = 1.0
        a_vol = portfolio_volatility(single_w, cov_matrix)
        a_ret = float(expected_returns[i])
        a_sharpe = (a_ret - risk_free_rate) / a_vol if a_vol > 1e-9 else 0.0
        individual_assets.append({
            "label": t,
            "expected_return": float(round(a_ret, 4)),
            "volatility": float(round(a_vol, 4)),
            "sharpe": float(round(a_sharpe, 4)),
            "weights": {t: 1.0},
        })

    # 5. Frontier points
    min_ret = min_vol_res.expected_return
    max_ret = float(np.max(expected_returns))

    frontier_points = []
    if max_ret > min_ret:
        target_returns = np.linspace(min_ret, max_ret, n_points)
        for target in target_returns:
            pt = optimizer.optimize_target_return(target, min_weight, max_weight)
            if pt.success:
                frontier_points.append({
                    "expected_return": float(round(pt.expected_return, 4)),
                    "volatility": float(round(pt.volatility, 4)),
                    "sharpe": float(round(pt.sharpe, 4)),
                    "weights": pt.weights,
                })

    # Ensure min vol and max sharpe are included
    if not frontier_points:
        frontier_points = [
            {
                "expected_return": min_vol_point["expected_return"],
                "volatility": min_vol_point["volatility"],
                "sharpe": min_vol_point["sharpe"],
                "weights": min_vol_point["weights"],
            },
            {
                "expected_return": max_sharpe_point["expected_return"],
                "volatility": max_sharpe_point["volatility"],
                "sharpe": max_sharpe_point["sharpe"],
                "weights": max_sharpe_point["weights"],
            },
        ]

    # Sort frontier points by volatility
    frontier_points.sort(key=lambda x: x["volatility"])

    return {
        "current": current_point,
        "min_volatility": min_vol_point,
        "max_sharpe": max_sharpe_point,
        "frontier": frontier_points,
        "individual_assets": individual_assets,
    }
