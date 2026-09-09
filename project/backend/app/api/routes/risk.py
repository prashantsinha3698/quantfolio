"""
Risk analytics API endpoints: VaR, CVaR, Beta, Covariance, Correlation, Risk Contributions.
"""
from fastapi import APIRouter
import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew

from app.analytics.performance import compute_annualized_volatility
from app.analytics.returns import compute_portfolio_returns
from app.data.collector import MarketDataCollector
from app.risk.beta import compute_beta, compute_tracking_error
from app.risk.correlation import compute_correlation_matrix
from app.risk.covariance import CovarianceEstimator
from app.risk.cvar import compute_historical_cvar
from app.risk.risk_contribution import compute_risk_contributions
from app.risk.var import compute_historical_var, compute_parametric_var
from app.schemas.portfolio import PortfolioRequest
from app.schemas.risk import (
    CorrelationMatrix,
    CovarianceMatrix,
    RiskContributionItem,
    RiskKPIs,
    RiskResponse,
    RollingVolPoint,
)

router = APIRouter(prefix="/risk", tags=["Risk"])
collector = MarketDataCollector()


@router.post("/analytics", response_model=RiskResponse)
def get_risk_analytics(portfolio: PortfolioRequest):
    tickers = [h.ticker for h in portfolio.holdings]
    target_weights = {h.ticker: h.target_weight for h in portfolio.holdings}

    # 1. Fetch market data
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
    capital = portfolio.initial_capital
    horizon = portfolio.risk_config.var_horizon_days

    # 3. VaR & CVaR
    h_var_95_pct, h_var_95_dlr = compute_historical_var(p_returns, 0.95, capital, horizon)
    h_var_99_pct, h_var_99_dlr = compute_historical_var(p_returns, 0.99, capital, horizon)

    p_var_95_pct, p_var_95_dlr = compute_parametric_var(p_returns, 0.95, capital, horizon)
    p_var_99_pct, p_var_99_dlr = compute_parametric_var(p_returns, 0.99, capital, horizon)

    h_cvar_95_pct, h_cvar_95_dlr = compute_historical_cvar(p_returns, 0.95, capital, horizon)
    h_cvar_99_pct, h_cvar_99_dlr = compute_historical_cvar(p_returns, 0.99, capital, horizon)

    # 4. Volatility, Beta, Distribution statistics
    ann_vol = compute_annualized_volatility(p_returns)
    beta = compute_beta(p_returns, b_returns)
    tracking_err = compute_tracking_error(p_returns, b_returns)
    sk = float(skew(p_returns))
    kt = float(kurtosis(p_returns))

    kpis = RiskKPIs(
        annualized_volatility=float(round(ann_vol, 4)),
        historical_var_95=float(round(h_var_95_pct, 4)),
        historical_var_99=float(round(h_var_99_pct, 4)),
        historical_var_95_dollar=float(round(h_var_95_dlr, 2)),
        historical_var_99_dollar=float(round(h_var_99_dlr, 2)),
        parametric_var_95=float(round(p_var_95_pct, 4)),
        parametric_var_99=float(round(p_var_99_pct, 4)),
        parametric_var_95_dollar=float(round(p_var_95_dlr, 2)),
        parametric_var_99_dollar=float(round(p_var_99_dlr, 2)),
        historical_cvar_95=float(round(h_cvar_95_pct, 4)),
        historical_cvar_99=float(round(h_cvar_99_pct, 4)),
        historical_cvar_95_dollar=float(round(h_cvar_95_dlr, 2)),
        historical_cvar_99_dollar=float(round(h_cvar_99_dlr, 2)),
        beta=float(round(beta, 4)),
        tracking_error=float(round(tracking_err, 4)),
        skewness=float(round(sk, 4)),
        kurtosis=float(round(kt, 4)),
    )

    # 5. Risk contribution
    rc_raw = compute_risk_contributions(market_data.returns, target_weights)
    rc_items = [RiskContributionItem(**item) for item in rc_raw]

    # 6. Correlation & Covariance matrices
    corr_data = compute_correlation_matrix(market_data.returns)
    corr_matrix = CorrelationMatrix(tickers=corr_data["tickers"], matrix=corr_data["matrix"])

    cov_raw = CovarianceEstimator.sample_covariance(market_data.returns, annualized=True)
    cov_raw, _ = CovarianceEstimator.stabilize_covariance(cov_raw)
    cov_matrix = CovarianceMatrix(
        tickers=list(market_data.returns.columns),
        matrix=np.round(cov_raw, 6).tolist(),
    )

    # 7. Rolling volatility across windows
    rolling_vol_points: list[RollingVolPoint] = []
    v20 = p_returns.rolling(20).std() * np.sqrt(252)
    v60 = p_returns.rolling(60).std() * np.sqrt(252)
    v126 = p_returns.rolling(126).std() * np.sqrt(252)
    v252 = p_returns.rolling(252).std() * np.sqrt(252)

    for d in p_returns.index:
        d_str = d.strftime("%Y-%m-%d")
        rolling_vol_points.append(
            RollingVolPoint(
                date=d_str,
                vol_20d=float(round(v20.loc[d], 4)) if pd.notna(v20.loc[d]) else None,
                vol_60d=float(round(v60.loc[d], 4)) if pd.notna(v60.loc[d]) else None,
                vol_126d=float(round(v126.loc[d], 4)) if pd.notna(v126.loc[d]) else None,
                vol_252d=float(round(v252.loc[d], 4)) if pd.notna(v252.loc[d]) else None,
            )
        )

    return RiskResponse(
        kpis=kpis,
        risk_contributions=rc_items,
        correlation=corr_matrix,
        covariance=cov_matrix,
        rolling_volatility=rolling_vol_points,
        assumptions={
            "var_horizon": f"{horizon} day(s)",
            "confidence_levels": "95% and 99%",
            "annualization_factor": "252 trading days",
            "parametric_distribution": "Standard Gaussian normal distribution",
            "cvar_definition": "Conditional tail expectation (mean of losses exceeding VaR threshold)",
        },
    )
