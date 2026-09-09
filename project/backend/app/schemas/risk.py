"""
Pydantic schemas for risk analytics, VaR/CVaR, and correlation.
"""
from pydantic import BaseModel
from typing import List, Dict, Optional


class RiskKPIs(BaseModel):
    annualized_volatility: float
    historical_var_95: float
    historical_var_99: float
    historical_var_95_dollar: float
    historical_var_99_dollar: float
    parametric_var_95: float
    parametric_var_99: float
    parametric_var_95_dollar: float
    parametric_var_99_dollar: float
    historical_cvar_95: float
    historical_cvar_99: float
    historical_cvar_95_dollar: float
    historical_cvar_99_dollar: float
    beta: float
    tracking_error: float
    skewness: float
    kurtosis: float


class RiskContributionItem(BaseModel):
    ticker: str
    weight: float
    marginal_risk_contribution: float
    component_risk_contribution: float
    percentage_risk_contribution: float  # Percentage of total risk (sums to ~100%)


class CorrelationMatrix(BaseModel):
    tickers: List[str]
    matrix: List[List[float]]


class CovarianceMatrix(BaseModel):
    tickers: List[str]
    matrix: List[List[float]]


class RollingVolPoint(BaseModel):
    date: str
    vol_20d: Optional[float] = None
    vol_60d: Optional[float] = None
    vol_126d: Optional[float] = None
    vol_252d: Optional[float] = None


class RiskResponse(BaseModel):
    kpis: RiskKPIs
    risk_contributions: List[RiskContributionItem]
    correlation: CorrelationMatrix
    covariance: CovarianceMatrix
    rolling_volatility: List[RollingVolPoint]
    assumptions: Dict[str, str]
