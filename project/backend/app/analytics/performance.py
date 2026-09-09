"""
Portfolio performance metrics engine: Total Return, CAGR, Volatility, Sharpe, Sortino, Drawdown, Calmar.
"""
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from app.core.config import ANNUALIZATION_FACTOR


def compute_total_return(returns: pd.Series) -> float:
    """Total cumulative return: prod(1 + r_t) - 1"""
    if returns.empty:
        return 0.0
    return float(np.prod(1.0 + returns) - 1.0)


def compute_cagr(returns: pd.Series, periods_per_year: int = ANNUALIZATION_FACTOR) -> float:
    """
    Compound Annual Growth Rate:
    CAGR = (1 + Total_Return)^(252 / T) - 1
    """
    n_days = len(returns)
    if n_days <= 1:
        return 0.0
    tot = compute_total_return(returns)
    if tot <= -1.0:
        return -1.0
    cagr = float(((1.0 + tot) ** (periods_per_year / n_days)) - 1.0)
    return cagr


def compute_annualized_return(returns: pd.Series, periods_per_year: int = ANNUALIZATION_FACTOR) -> float:
    """Arithmetic annualized return: mean(r_t) * 252"""
    if returns.empty:
        return 0.0
    return float(returns.mean() * periods_per_year)


def compute_annualized_volatility(returns: pd.Series, periods_per_year: int = ANNUALIZATION_FACTOR) -> float:
    """Annualized volatility: std(r_t) * sqrt(252)"""
    if len(returns) <= 1:
        return 0.0
    return float(returns.std(ddof=1) * np.sqrt(periods_per_year))


def compute_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.04,
    periods_per_year: int = ANNUALIZATION_FACTOR,
) -> float:
    """
    Annualized Sharpe ratio:
    Sharpe = (Annualized_Return - R_f) / Annualized_Volatility
    """
    ann_vol = compute_annualized_volatility(returns, periods_per_year)
    if ann_vol < 1e-9:
        return 0.0
    ann_ret = compute_annualized_return(returns, periods_per_year)
    return float((ann_ret - risk_free_rate) / ann_vol)


def compute_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.04,
    target_return: float = 0.0,
    periods_per_year: int = ANNUALIZATION_FACTOR,
) -> float:
    """
    Annualized Sortino ratio:
    Sortino = (Annualized_Return - R_f) / Downside_Deviation
    Downside deviation uses daily deviations below target_return.
    """
    if len(returns) <= 1:
        return 0.0
    daily_rf = risk_free_rate / periods_per_year
    downside_diff = returns - daily_rf
    downside_returns = downside_diff[downside_diff < 0.0]

    if len(downside_returns) == 0:
        return 0.0

    # Downside root-mean-square deviation annualized
    downside_std = np.sqrt(np.mean(downside_returns ** 2)) * np.sqrt(periods_per_year)
    if downside_std < 1e-9:
        return 0.0

    ann_ret = compute_annualized_return(returns, periods_per_year)
    return float((ann_ret - risk_free_rate) / downside_std)


def compute_drawdowns(returns: pd.Series) -> Tuple[pd.Series, float]:
    """
    Calculates drawdown time series and maximum drawdown:
    DD_t = W_t / max_{s<=t}(W_s) - 1
    MDD = min(DD_t)
    """
    if returns.empty:
        return pd.Series(dtype=float), 0.0

    wealth = (1.0 + returns).cumprod()
    peak = wealth.cummax()
    drawdown = (wealth - peak) / peak
    drawdown.name = "Drawdown"
    max_dd = float(drawdown.min())
    return drawdown, max_dd


def compute_calmar_ratio(cagr: float, max_drawdown: float) -> float:
    """Calmar ratio: CAGR / abs(MDD)"""
    abs_mdd = abs(max_drawdown)
    if abs_mdd < 1e-6:
        return 0.0
    return float(cagr / abs_mdd)


def compute_drawdown_events(returns: pd.Series, top_n: int = 5) -> List[Dict]:
    """
    Identifies the top drawdown events with Peak Date, Trough Date, Recovery Date,
    Drawdown Magnitude, Drawdown Duration (days), and Recovery Period (days).
    """
    if returns.empty:
        return []

    wealth = (1.0 + returns).cumprod()
    peak = wealth.cummax()
    drawdown = (wealth - peak) / peak

    events = []
    in_drawdown = False
    peak_date = wealth.index[0]
    peak_val = wealth.iloc[0]
    trough_date = wealth.index[0]
    trough_val = wealth.iloc[0]

    for date, val in wealth.items():
        dd = drawdown.loc[date]
        if dd < 0:
            if not in_drawdown:
                in_drawdown = True
                # The peak date was the date of running max prior
                prior_dates = wealth.loc[:date]
                peak_date = prior_dates.idxmax()
                peak_val = wealth.loc[peak_date]
                trough_date = date
                trough_val = val
            else:
                if val < trough_val:
                    trough_val = val
                    trough_date = date
        else:
            if in_drawdown:
                # Recovered!
                recovery_date = date
                mag = float((trough_val - peak_val) / peak_val)
                duration_days = (trough_date - peak_date).days
                recovery_days = (recovery_date - trough_date).days

                events.append({
                    "peak_date": peak_date.strftime("%Y-%m-%d"),
                    "trough_date": trough_date.strftime("%Y-%m-%d"),
                    "recovery_date": recovery_date.strftime("%Y-%m-%d"),
                    "magnitude": mag,
                    "duration_days": max(1, duration_days),
                    "recovery_days": max(1, recovery_days),
                })
                in_drawdown = False

    # Handle ongoing drawdown if still in drawdown at end of series
    if in_drawdown:
        mag = float((trough_val - peak_val) / peak_val)
        duration_days = (trough_date - peak_date).days
        events.append({
            "peak_date": peak_date.strftime("%Y-%m-%d"),
            "trough_date": trough_date.strftime("%Y-%m-%d"),
            "recovery_date": None,
            "magnitude": mag,
            "duration_days": max(1, duration_days),
            "recovery_days": None,
        })

    # Sort by magnitude of loss (most negative first)
    events.sort(key=lambda x: x["magnitude"])
    return events[:top_n]
