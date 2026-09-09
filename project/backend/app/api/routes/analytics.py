"""
Performance analytics API endpoints.
"""
from fastapi import APIRouter
import numpy as np
import pandas as pd

from app.analytics.performance import (
    compute_annualized_return,
    compute_annualized_volatility,
    compute_cagr,
    compute_calmar_ratio,
    compute_drawdown_events,
    compute_drawdowns,
    compute_sharpe_ratio,
    compute_sortino_ratio,
    compute_total_return,
)
from app.analytics.returns import compute_portfolio_returns, compute_wealth_index
from app.data.collector import MarketDataCollector
from app.risk.beta import compute_alpha, compute_beta, compute_tracking_error
from app.schemas.analytics import (
    DrawdownEvent,
    PerformanceKPIs,
    PerformanceResponse,
    RollingMetricPoint,
    TimeSeriesPoint,
)
from app.schemas.portfolio import PortfolioRequest

router = APIRouter(prefix="/analytics", tags=["Analytics"])
collector = MarketDataCollector()


@router.post("/performance", response_model=PerformanceResponse)
def get_performance_analytics(portfolio: PortfolioRequest):
    tickers = [h.ticker for h in portfolio.holdings]
    target_weights = {h.ticker: h.target_weight for h in portfolio.holdings}

    # 1. Fetch normalized market data
    market_data = collector.get_portfolio_market_data(
        tickers=tickers,
        benchmark=portfolio.benchmark,
        date_range=portfolio.date_range,
        start_date=portfolio.start_date,
        end_date=portfolio.end_date,
    )

    # 2. Portfolio return series
    p_returns = compute_portfolio_returns(market_data.returns, target_weights)
    b_returns = market_data.benchmark_returns

    # 3. Wealth and Drawdown series
    p_wealth = compute_wealth_index(p_returns, portfolio.initial_capital)
    b_wealth = compute_wealth_index(b_returns, portfolio.initial_capital)
    p_dd, p_mdd = compute_drawdowns(p_returns)
    b_dd, b_mdd = compute_drawdowns(b_returns)

    # 4. KPIs
    p_tot = compute_total_return(p_returns)
    p_cagr = compute_cagr(p_returns)
    p_ann_ret = compute_annualized_return(p_returns)
    p_ann_vol = compute_annualized_volatility(p_returns)
    p_sharpe = compute_sharpe_ratio(p_returns, risk_free_rate=0.04)
    p_sortino = compute_sortino_ratio(p_returns, risk_free_rate=0.04)
    p_calmar = compute_calmar_ratio(p_cagr, p_mdd)
    pos_pct = float((p_returns > 0).mean() * 100)

    b_tot = compute_total_return(b_returns)
    b_cagr = compute_cagr(b_returns)
    b_vol = compute_annualized_volatility(b_returns)
    b_sharpe = compute_sharpe_ratio(b_returns, risk_free_rate=0.04)

    beta = compute_beta(p_returns, b_returns)
    alpha = compute_alpha(p_returns, b_returns, risk_free_rate=0.04)
    te = compute_tracking_error(p_returns, b_returns)

    kpis = PerformanceKPIs(
        total_return=float(round(p_tot, 4)),
        annualized_return=float(round(p_ann_ret, 4)),
        cagr=float(round(p_cagr, 4)),
        annualized_volatility=float(round(p_ann_vol, 4)),
        daily_volatility=float(round(float(p_returns.std(ddof=1)), 4)),
        sharpe_ratio=float(round(p_sharpe, 4)),
        sortino_ratio=float(round(p_sortino, 4)),
        max_drawdown=float(round(p_mdd, 4)),
        calmar_ratio=float(round(p_calmar, 4)),
        positive_days_pct=float(round(pos_pct, 2)),
        benchmark_total_return=float(round(b_tot, 4)),
        benchmark_cagr=float(round(b_cagr, 4)),
        benchmark_volatility=float(round(b_vol, 4)),
        benchmark_sharpe=float(round(b_sharpe, 4)),
        alpha=float(round(alpha, 4)),
        beta=float(round(beta, 4)),
        tracking_error=float(round(te, 4)),
    )

    # 5. Time series points
    ts_points: list[TimeSeriesPoint] = []
    # Downsample if series is very long (keep all if <= 756 days)
    for date in p_returns.index:
        d_str = date.strftime("%Y-%m-%d")
        ts_points.append(
            TimeSeriesPoint(
                date=d_str,
                portfolio_return=float(round(p_returns.loc[date], 5)),
                benchmark_return=float(round(b_returns.loc[date], 5)),
                portfolio_wealth=float(round(p_wealth.loc[date], 2)),
                benchmark_wealth=float(round(b_wealth.loc[date], 2)),
                portfolio_drawdown=float(round(p_dd.loc[date], 4)),
                benchmark_drawdown=float(round(b_dd.loc[date], 4)),
            )
        )

    # 6. Drawdown events
    dd_events_raw = compute_drawdown_events(p_returns, top_n=5)
    dd_events = [DrawdownEvent(**ev) for ev in dd_events_raw]

    # 7. Rolling metrics (60-day rolling vol & return)
    rolling_points: list[RollingMetricPoint] = []
    p_vol_roll = p_returns.rolling(window=60).std() * np.sqrt(252)
    b_vol_roll = b_returns.rolling(window=60).std() * np.sqrt(252)
    p_ret_roll = p_returns.rolling(window=60).mean() * 252

    for d in p_vol_roll.dropna().index:
        rolling_points.append(
            RollingMetricPoint(
                date=d.strftime("%Y-%m-%d"),
                portfolio_vol=float(round(p_vol_roll.loc[d], 4)),
                benchmark_vol=float(round(b_vol_roll.loc[d], 4)),
                portfolio_return_rolling=float(round(p_ret_roll.loc[d], 4)),
            )
        )

    return PerformanceResponse(
        kpis=kpis,
        time_series=ts_points,
        major_drawdowns=dd_events,
        rolling_metrics=rolling_points,
        assumptions={
            "annualization_days": "252 trading days",
            "risk_free_rate": "4.00% annualized",
            "benchmark": portfolio.benchmark,
            "data_source": market_data.source,
            "period": f"{market_data.start_date} to {market_data.end_date}",
        },
    )
