"""
Pydantic schemas for portfolio performance analytics.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict


class PerformanceKPIs(BaseModel):
    total_return: float
    annualized_return: float
    cagr: float
    annualized_volatility: float
    daily_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    positive_days_pct: float
    benchmark_total_return: float
    benchmark_cagr: float
    benchmark_volatility: float
    benchmark_sharpe: float
    alpha: float
    beta: float
    tracking_error: float


class TimeSeriesPoint(BaseModel):
    date: str
    portfolio_return: float
    benchmark_return: float
    portfolio_wealth: float
    benchmark_wealth: float
    portfolio_drawdown: float
    benchmark_drawdown: float


class DrawdownEvent(BaseModel):
    peak_date: str
    trough_date: str
    recovery_date: Optional[str] = None
    magnitude: float
    duration_days: int
    recovery_days: Optional[int] = None


class RollingMetricPoint(BaseModel):
    date: str
    portfolio_vol: float
    benchmark_vol: float
    portfolio_return_rolling: float


class PerformanceResponse(BaseModel):
    kpis: PerformanceKPIs
    time_series: List[TimeSeriesPoint]
    major_drawdowns: List[DrawdownEvent]
    rolling_metrics: List[RollingMetricPoint]
    assumptions: Dict[str, str]
