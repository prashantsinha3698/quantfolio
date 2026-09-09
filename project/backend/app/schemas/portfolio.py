"""
Pydantic schemas for portfolio configuration, validation, and serialization.
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict


class HoldingInput(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=15, description="Asset ticker symbol, e.g. SPY")
    quantity: float = Field(0.0, ge=0.0, description="Number of shares held")
    target_weight: float = Field(..., ge=0.0, le=1.0, description="Target portfolio weight (0.0 to 1.0)")
    min_weight: float = Field(0.0, ge=0.0, le=1.0, description="Minimum allowable weight in optimization")
    max_weight: float = Field(1.0, ge=0.0, le=1.0, description="Maximum allowable weight in optimization")

    @field_validator("ticker")
    @classmethod
    def clean_ticker(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_bounds(self):
        if self.min_weight > self.max_weight:
            raise ValueError(f"min_weight ({self.min_weight}) cannot exceed max_weight ({self.max_weight}) for {self.ticker}")
        if self.target_weight < self.min_weight or self.target_weight > self.max_weight:
            # We allow target_weight outside bounds with a relaxed check, but warn or ensure valid bounds
            pass
        return self


class RiskConfigSchema(BaseModel):
    confidence_level: float = Field(0.95, ge=0.80, le=0.999, description="VaR / CVaR confidence level, e.g. 0.95 or 0.99")
    var_horizon_days: int = Field(1, ge=1, le=252, description="VaR loss horizon in days")
    lookback_days: int = Field(756, ge=60, le=2520, description="Lookback window in trading days")


class RebalanceConfigSchema(BaseModel):
    drift_threshold: float = Field(0.05, ge=0.005, le=0.50, description="Absolute weight drift threshold to trigger rebalancing")
    minimum_trade_value: float = Field(1000.0, ge=0.0, description="Minimum dollar trade amount to avoid small transactions")
    transaction_cost_rate: float = Field(0.0010, ge=0.0, le=0.05, description="Proportional transaction cost rate (e.g. 0.0010 = 10 bps)")


class PortfolioRequest(BaseModel):
    name: str = Field("Balanced Growth", min_length=1, max_length=100)
    initial_capital: float = Field(1_000_000.0, gt=0.0, description="Portfolio initial capital in USD")
    base_currency: str = Field("USD", min_length=3, max_length=3)
    benchmark: str = Field("SPY", min_length=1, max_length=15)
    holdings: List[HoldingInput] = Field(..., min_length=1, description="List of portfolio holdings")
    risk_config: RiskConfigSchema = Field(default_factory=RiskConfigSchema)
    rebalance_config: RebalanceConfigSchema = Field(default_factory=RebalanceConfigSchema)
    date_range: Optional[str] = Field("1Y", description="Predefined range: 1M, 3M, 6M, YTD, 1Y, 3Y, 5Y, MAX")
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    @field_validator("benchmark")
    @classmethod
    def clean_benchmark(cls, v: str) -> str:
        return v.strip().upper()

    @model_validator(mode="after")
    def validate_holdings(self):
        tickers = [h.ticker for h in self.holdings]
        if len(tickers) != len(set(tickers)):
            raise ValueError("Duplicate tickers detected in holdings list")

        total_target = sum(h.target_weight for h in self.holdings)
        if not (0.98 <= total_target <= 1.02):
            raise ValueError(f"Target weights must sum to approximately 1.0 (currently {total_target:.4f})")
        return self


class HoldingResponse(BaseModel):
    ticker: str
    quantity: float
    current_price: float
    market_value: float
    current_weight: float
    target_weight: float
    min_weight: float
    max_weight: float
    drift: float


class PortfolioSummaryResponse(BaseModel):
    name: str
    base_currency: str
    benchmark: str
    initial_capital: float
    current_value: float
    cash_value: float
    holdings: List[HoldingResponse]
    data_source: str
    is_demo: bool
    last_updated: str
    data_quality_warnings: List[str] = []
