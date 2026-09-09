"""
Expected return estimation models: Historical Mean, Median, and CAPM.
"""
from typing import Optional
import numpy as np
import pandas as pd
from app.core.config import ANNUALIZATION_FACTOR


class ExpectedReturnsEstimator:
    """Calculates expected annualized return vector mu for portfolio assets."""

    @staticmethod
    def historical_mean(returns_df: pd.DataFrame) -> np.ndarray:
        """Annualized arithmetic mean of historical daily returns: mu = mean(r) * 252"""
        daily_mean = returns_df.mean().values
        return daily_mean * ANNUALIZATION_FACTOR

    @staticmethod
    def capm(
        returns_df: pd.DataFrame,
        benchmark_returns: pd.Series,
        risk_free_rate: float = 0.04,
        market_equity_risk_premium: float = 0.06,
    ) -> np.ndarray:
        """
        Capital Asset Pricing Model (CAPM) expected returns:
        E[R_i] = R_f + beta_i * (E[R_m] - R_f)
        """
        aligned = returns_df.join(benchmark_returns, how="inner").dropna()
        m_ret = aligned.iloc[:, -1].values
        var_m = np.var(m_ret, ddof=1)

        expected_returns = []
        for col in returns_df.columns:
            a_ret = aligned[col].values
            if var_m > 1e-12:
                beta = np.cov(a_ret, m_ret)[0, 1] / var_m
            else:
                beta = 1.0
            er = risk_free_rate + beta * market_equity_risk_premium
            expected_returns.append(er)

        return np.array(expected_returns)
