"""
Rebalancing and trade recommendations API endpoints.
"""
from fastapi import APIRouter

from app.data.collector import MarketDataCollector
from app.rebalance.trades import generate_trades
from app.schemas.portfolio import PortfolioRequest
from app.schemas.rebalance import RebalanceResponse, RebalanceSummary, TradeItem

router = APIRouter(prefix="/rebalance", tags=["Rebalancing"])
collector = MarketDataCollector()


@router.post("/evaluate", response_model=RebalanceResponse)
def evaluate_rebalancing(portfolio: PortfolioRequest):
    tickers = [h.ticker for h in portfolio.holdings]
    target_weights = {h.ticker: h.target_weight for h in portfolio.holdings}

    # 1. Fetch market data for latest prices
    market_data = collector.get_portfolio_market_data(
        tickers=tickers,
        benchmark=portfolio.benchmark,
        date_range=portfolio.date_range,
        start_date=portfolio.start_date,
        end_date=portfolio.end_date,
    )

    latest_prices = market_data.prices.iloc[-1].to_dict()

    # 2. Compute current values
    current_values = {}
    current_prices_clean = {}
    total_val = 0.0

    for h in portfolio.holdings:
        price = float(latest_prices.get(h.ticker, 100.0))
        current_prices_clean[h.ticker] = price
        qty = h.quantity
        if qty <= 0 and price > 0:
            qty = (portfolio.initial_capital * h.target_weight) / price
        val = qty * price
        current_values[h.ticker] = val
        total_val += val

    # 3. Generate trades and summary
    trade_items_raw, summary_raw = generate_trades(
        current_values=current_values,
        target_weights=target_weights,
        current_prices=current_prices_clean,
        drift_threshold=portfolio.rebalance_config.drift_threshold,
        minimum_trade_value=portfolio.rebalance_config.minimum_trade_value,
        transaction_cost_rate=portfolio.rebalance_config.transaction_cost_rate,
    )

    trades = [TradeItem(**t) for t in trade_items_raw]
    summary = RebalanceSummary(**summary_raw)

    return RebalanceResponse(
        summary=summary,
        trades=trades,
    )
