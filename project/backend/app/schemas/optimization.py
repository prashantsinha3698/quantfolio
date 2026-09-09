"""
Pydantic schemas for portfolio optimization and efficient frontier.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class OptimizationRequest(BaseModel):
    risk_free_rate: float = Field(0.04, ge=0.0, le=0.20, description="Annualized risk-free rate")
    min_weight: float = Field(0.0, ge=0.0, le=1.0, description="Global minimum weight bound")
    max_weight: float = Field(1.0, ge=0.0, le=1.0, description="Global maximum weight bound")
    custom_bounds: Optional[Dict[str, List[float]]] = None
    expected_return_method: str = Field("historical_mean", description="Method: historical_mean, capm")
    target_return: Optional[float] = None
    frontier_points_count: int = Field(30, ge=10, le=100)


class PortfolioAllocationPoint(BaseModel):
    label: str
    expected_return: float
    volatility: float
    sharpe: float
    weights: Dict[str, float]


class FrontierPoint(BaseModel):
    expected_return: float
    volatility: float
    sharpe: float
    weights: Dict[str, float]


class OptimizationResponse(BaseModel):
    current: PortfolioAllocationPoint
    min_volatility: PortfolioAllocationPoint
    max_sharpe: PortfolioAllocationPoint
    target_portfolio: Optional[PortfolioAllocationPoint] = None
    frontier: List[FrontierPoint]
    individual_assets: List[PortfolioAllocationPoint]
    status: str
    iterations: int
    assumptions: Dict[str, str]
