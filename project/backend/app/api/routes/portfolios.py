"""
Portfolio configuration and presets endpoints.
"""
from datetime import datetime
from typing import List, Dict
from fastapi import APIRouter
from app.data.collector import MarketDataCollector
from app.schemas.portfolio import (
    HoldingInput,
    HoldingResponse,
    PortfolioRequest,
    PortfolioSummaryResponse,
)

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])
collector = MarketDataCollector()

PRESET_PORTFOLIOS: Dict[str, PortfolioRequest] = {
    "balanced_growth": PortfolioRequest(
        name="Balanced Growth",
        initial_capital=1_000_000.0,
        base_currency="USD",
        benchmark="SPY",
        holdings=[
            HoldingInput(ticker="SPY", quantity=700, target_weight=0.40, min_weight=0.0, max_weight=0.50),
            HoldingInput(ticker="QQQ", quantity=450, target_weight=0.25, min_weight=0.0, max_weight=0.40),
            HoldingInput(ticker="GLD", quantity=650, target_weight=0.15, min_weight=0.0, max_weight=0.30),
            HoldingInput(ticker="TLT", quantity=1050, target_weight=0.10, min_weight=0.0, max_weight=0.30),
            HoldingInput(ticker="VNQ", quantity=1100, target_weight=0.10, min_weight=0.0, max_weight=0.30),
        ],
        date_range="1Y",
    ),
    "tech_heavy": PortfolioRequest(
        name="Tech Innovation & Growth",
        initial_capital=1_000_000.0,
        base_currency="USD",
        benchmark="QQQ",
        holdings=[
            HoldingInput(ticker="QQQ", quantity=800, target_weight=0.40, min_weight=0.1, max_weight=0.60),
            HoldingInput(ticker="AAPL", quantity=1500, target_weight=0.25, min_weight=0.0, max_weight=0.40),
            HoldingInput(ticker="MSFT", quantity=600, target_weight=0.20, min_weight=0.0, max_weight=0.35),
            HoldingInput(ticker="NVDA", quantity=1200, target_weight=0.15, min_weight=0.0, max_weight=0.30),
        ],
        date_range="1Y",
    ),
    "all_weather": PortfolioRequest(
        name="All-Weather Risk Parity",
        initial_capital=1_000_000.0,
        base_currency="USD",
        benchmark="SPY",
        holdings=[
            HoldingInput(ticker="SPY", quantity=500, target_weight=0.30, min_weight=0.0, max_weight=0.50),
            HoldingInput(ticker="TLT", quantity=4200, target_weight=0.40, min_weight=0.1, max_weight=0.60),
            HoldingInput(ticker="GLD", quantity=650, target_weight=0.15, min_weight=0.0, max_weight=0.30),
            HoldingInput(ticker="BND", quantity=2000, target_weight=0.15, min_weight=0.0, max_weight=0.30),
        ],
        date_range="1Y",
    ),
}


@router.get("/presets")
def get_presets():
    """Returns curated portfolio presets for instant demonstration and analysis."""
    return PRESET_PORTFOLIOS


@router.post("/evaluate", response_model=PortfolioSummaryResponse)
def evaluate_portfolio(portfolio: PortfolioRequest):
    """
    Evaluates current holdings, fetches latest prices, calculates current market value and drift.
    """
    tickers = [h.ticker for h in portfolio.holdings]
    market_data = collector.get_portfolio_market_data(
        tickers=tickers,
        benchmark=portfolio.benchmark,
        date_range=portfolio.date_range,
        start_date=portfolio.start_date,
        end_date=portfolio.end_date,
    )

    latest_prices = market_data.prices.iloc[-1].to_dict()

    holding_responses: List[HoldingResponse] = []
    total_market_val = 0.0

    for h in portfolio.holdings:
        price = float(latest_prices.get(h.ticker, 100.0))
        # If quantity was 0, default quantity from target weight and initial capital
        qty = h.quantity
        if qty <= 0 and price > 0:
            qty = (portfolio.initial_capital * h.target_weight) / price

        val = qty * price
        total_market_val += val
        holding_responses.append(
            HoldingResponse(
                ticker=h.ticker,
                quantity=float(round(qty, 2)),
                current_price=float(round(price, 2)),
                market_value=float(round(val, 2)),
                current_weight=0.0,  # Will normalize after total
                target_weight=h.target_weight,
                min_weight=h.min_weight,
                max_weight=h.max_weight,
                drift=0.0,
            )
        )

    # Calculate actual current weights and drift
    for hr in holding_responses:
        if total_market_val > 0:
            hr.current_weight = float(round(hr.market_value / total_market_val, 4))
            hr.drift = float(round(hr.current_weight - hr.target_weight, 4))

    return PortfolioSummaryResponse(
        name=portfolio.name,
        base_currency=portfolio.base_currency,
        benchmark=portfolio.benchmark,
        initial_capital=portfolio.initial_capital,
        current_value=float(round(total_market_val, 2)),
        cash_value=0.0,
        holdings=holding_responses,
        data_source=market_data.source,
        is_demo=market_data.is_demo,
        last_updated=datetime.now().strftime("%b %d, %Y %H:%M"),
        data_quality_warnings=market_data.data_quality_warnings,
    )
