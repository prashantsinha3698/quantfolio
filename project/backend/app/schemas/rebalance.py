"""
Pydantic schemas for rebalancing evaluation and trade recommendations.
"""
from pydantic import BaseModel, Field
from typing import List, Dict


class TradeItem(BaseModel):
    ticker: str
    current_weight: float
    target_weight: float
    drift: float
    drift_status: str  # "normal", "warning", "action_required"
    current_value: float
    target_value: float
    trade_value: float
    action: str  # "BUY", "SELL", "HOLD"
    priority: int
    current_price: float
    estimated_shares: int
    reason: str


class RebalanceSummary(BaseModel):
    rebalance_required: bool
    drift_threshold: float
    assets_outside_threshold: int
    total_buy_value: float
    total_sell_value: float
    total_turnover_value: float
    estimated_transaction_cost: float
    transaction_cost_rate: float


class RebalanceResponse(BaseModel):
    summary: RebalanceSummary
    trades: List[TradeItem]
    disclaimer: str = (
        "Informational Research Output: Model-based rebalancing analysis only. "
        "Does not constitute personalized financial or investment advice."
    )
