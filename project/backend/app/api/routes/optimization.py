"""
Portfolio optimization and efficient frontier API endpoints.
"""
from typing import Optional
from fastapi import APIRouter
import numpy as np

from app.data.collector import MarketDataCollector
from app.optimization.efficient_frontier import generate_efficient_frontier
from app.optimization.expected_returns import ExpectedReturnsEstimator
from app.risk.covariance import CovarianceEstimator
from app.schemas.optimization import (
    FrontierPoint,
    OptimizationRequest,
    OptimizationResponse,
    PortfolioAllocationPoint,
)
from app.schemas.portfolio import PortfolioRequest

router = APIRouter(prefix="/optimization", tags=["Optimization"])
collector = MarketDataCollector()


class OptimizationRunPayload(PortfolioRequest):
    opt_params: Optional[OptimizationRequest] = None


@router.post("/run", response_model=OptimizationResponse)
def run_portfolio_optimization(payload: OptimizationRunPayload):
    portfolio = payload
    opt_params = payload.opt_params or OptimizationRequest()

    tickers = [h.ticker for h in portfolio.holdings]
    current_weights = {h.ticker: h.target_weight for h in portfolio.holdings}

    # 1. Fetch market data
    market_data = collector.get_portfolio_market_data(
        tickers=tickers,
        benchmark=portfolio.benchmark,
        date_range=portfolio.date_range,
        start_date=portfolio.start_date,
        end_date=portfolio.end_date,
    )

    # 2. Expected returns vector
    if opt_params.expected_return_method == "capm":
        exp_returns = ExpectedReturnsEstimator.capm(
            returns_df=market_data.returns,
            benchmark_returns=market_data.benchmark_returns,
            risk_free_rate=opt_params.risk_free_rate,
        )
    else:
        exp_returns = ExpectedReturnsEstimator.historical_mean(market_data.returns)

    # 3. Covariance matrix and stabilization
    cov_matrix = CovarianceEstimator.sample_covariance(market_data.returns, annualized=True)
    cov_matrix, was_stabilized = CovarianceEstimator.stabilize_covariance(cov_matrix)

    # 4. Generate Efficient Frontier, Min-Vol, and Max-Sharpe portfolios
    frontier_data = generate_efficient_frontier(
        tickers=tickers,
        expected_returns=exp_returns,
        cov_matrix=cov_matrix,
        current_weights=current_weights,
        risk_free_rate=opt_params.risk_free_rate,
        min_weight=opt_params.min_weight,
        max_weight=opt_params.max_weight,
        n_points=opt_params.frontier_points_count,
    )

    current_pt = PortfolioAllocationPoint(**frontier_data["current"])
    min_vol_pt = PortfolioAllocationPoint(**frontier_data["min_volatility"])
    max_sharpe_pt = PortfolioAllocationPoint(**frontier_data["max_sharpe"])
    frontier_pts = [FrontierPoint(**pt) for pt in frontier_data["frontier"]]
    assets_pts = [PortfolioAllocationPoint(**pt) for pt in frontier_data["individual_assets"]]

    return OptimizationResponse(
        current=current_pt,
        min_volatility=min_vol_pt,
        max_sharpe=max_sharpe_pt,
        target_portfolio=None,
        frontier=frontier_pts,
        individual_assets=assets_pts,
        status="Optimal solution found using SciPy SLSQP constrained solver",
        iterations=len(frontier_pts),
        assumptions={
            "expected_returns_model": opt_params.expected_return_method,
            "covariance_stabilization": "Regularized PSD" if was_stabilized else "Standard Sample",
            "risk_free_rate": f"{opt_params.risk_free_rate * 100:.2f}%",
            "weight_bounds": f"[{opt_params.min_weight * 100:.0f}%, {opt_params.max_weight * 100:.0f}%]",
            "budget_constraint": "sum(weights) = 1.0 (long-only, no leverage)",
        },
    )
