"""
Constrained portfolio optimization engine utilizing SciPy SLSQP.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize

from app.domain.models import OptimizationResult
from app.optimization.objectives import (
    portfolio_expected_return,
    portfolio_variance,
    portfolio_volatility,
    negative_sharpe_ratio,
)
from app.core.logging import logger


class PortfolioOptimizer:
    """Solves constrained Markowitz modern portfolio theory optimization problems."""

    def __init__(
        self,
        tickers: List[str],
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_free_rate: float = 0.04,
    ):
        self.tickers = tickers
        self.expected_returns = expected_returns
        self.cov_matrix = cov_matrix
        self.risk_free_rate = risk_free_rate
        self.n_assets = len(tickers)

    def _get_bounds(
        self,
        min_weight: float = 0.0,
        max_weight: float = 1.0,
        custom_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> List[Tuple[float, float]]:
        bounds = []
        for ticker in self.tickers:
            if custom_bounds and ticker in custom_bounds:
                bounds.append(custom_bounds[ticker])
            else:
                bounds.append((min_weight, max_weight))
        return bounds

    def _get_initial_weights(self) -> np.ndarray:
        """Equal weight starting point."""
        return np.ones(self.n_assets) / self.n_assets

    def optimize_min_volatility(
        self,
        min_weight: float = 0.0,
        max_weight: float = 1.0,
        custom_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> OptimizationResult:
        """Minimizes portfolio variance subject to full investment and asset weight limits."""
        bounds = self._get_bounds(min_weight, max_weight, custom_bounds)
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        init_w = self._get_initial_weights()

        res = minimize(
            fun=portfolio_variance,
            x0=init_w,
            args=(self.cov_matrix,),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-9},
        )

        weights_dict = {t: float(round(w, 5)) for t, w in zip(self.tickers, res.x)}
        ret = portfolio_expected_return(res.x, self.expected_returns)
        vol = portfolio_volatility(res.x, self.cov_matrix)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 1e-9 else 0.0

        return OptimizationResult(
            weights=weights_dict,
            expected_return=float(ret),
            volatility=float(vol),
            sharpe=float(sharpe),
            success=bool(res.success),
            status_message=str(res.message),
            iterations=int(res.nit),
        )

    def optimize_max_sharpe(
        self,
        min_weight: float = 0.0,
        max_weight: float = 1.0,
        custom_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> OptimizationResult:
        """Maximizes the Sharpe ratio (minimizes negative Sharpe) subject to budget and bounds."""
        bounds = self._get_bounds(min_weight, max_weight, custom_bounds)
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
        init_w = self._get_initial_weights()

        res = minimize(
            fun=negative_sharpe_ratio,
            x0=init_w,
            args=(self.expected_returns, self.cov_matrix, self.risk_free_rate),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-9},
        )

        # Fallback to min-vol if max-sharpe fails to converge
        if not res.success:
            logger.warning(f"Max Sharpe solver warning: {res.message}. Retrying from min-vol solution.")
            min_vol_res = self.optimize_min_volatility(min_weight, max_weight, custom_bounds)
            res = minimize(
                fun=negative_sharpe_ratio,
                x0=np.array(list(min_vol_res.weights.values())),
                args=(self.expected_returns, self.cov_matrix, self.risk_free_rate),
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 500, "ftol": 1e-9},
            )

        weights_dict = {t: float(round(w, 5)) for t, w in zip(self.tickers, res.x)}
        ret = portfolio_expected_return(res.x, self.expected_returns)
        vol = portfolio_volatility(res.x, self.cov_matrix)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 1e-9 else 0.0

        return OptimizationResult(
            weights=weights_dict,
            expected_return=float(ret),
            volatility=float(vol),
            sharpe=float(sharpe),
            success=bool(res.success),
            status_message=str(res.message),
            iterations=int(res.nit),
        )

    def optimize_target_return(
        self,
        target_return: float,
        min_weight: float = 0.0,
        max_weight: float = 1.0,
        custom_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> OptimizationResult:
        """Minimizes volatility subject to achieving a specific target expected return."""
        bounds = self._get_bounds(min_weight, max_weight, custom_bounds)
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w: portfolio_expected_return(w, self.expected_returns) - target_return},
        ]
        init_w = self._get_initial_weights()

        res = minimize(
            fun=portfolio_variance,
            x0=init_w,
            args=(self.cov_matrix,),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-9},
        )

        weights_dict = {t: float(round(w, 5)) for t, w in zip(self.tickers, res.x)}
        ret = portfolio_expected_return(res.x, self.expected_returns)
        vol = portfolio_volatility(res.x, self.cov_matrix)
        sharpe = (ret - self.risk_free_rate) / vol if vol > 1e-9 else 0.0

        return OptimizationResult(
            weights=weights_dict,
            expected_return=float(ret),
            volatility=float(vol),
            sharpe=float(sharpe),
            success=bool(res.success),
            status_message=str(res.message),
            iterations=int(res.nit),
        )
