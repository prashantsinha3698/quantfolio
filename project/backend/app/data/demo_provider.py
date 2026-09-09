"""
Realistic demo market data provider for offline development, tests, and demonstration.
Generates correlated geometric Brownian motion series calibrated to typical asset characteristics.
"""
from datetime import datetime, timedelta
from typing import List, Optional
import numpy as np
import pandas as pd

from app.data.base_provider import MarketDataProvider
from app.core.logging import logger

# Calibrated annual parameters: (expected_annual_return, annual_volatility, initial_price)
ASSET_CALIBRATION = {
    "SPY": (0.12, 0.16, 560.0),
    "QQQ": (0.16, 0.22, 480.0),
    "GLD": (0.08, 0.14, 230.0),
    "TLT": (0.03, 0.15, 95.0),
    "VNQ": (0.07, 0.19, 88.0),
    "AAPL": (0.15, 0.23, 225.0),
    "MSFT": (0.15, 0.21, 440.0),
    "NVDA": (0.28, 0.42, 120.0),
    "BND": (0.04, 0.06, 73.0),
    "IWM": (0.10, 0.21, 215.0),
}


class DemoMarketDataProvider(MarketDataProvider):
    """Generates realistic synthetic price series calibrated to real-world asset metrics."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def get_history(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        logger.info(f"Using DemoMarketDataProvider for tickers: {tickers}")
        np.random.seed(self.seed)

        # Determine date range
        end_dt = datetime.now() if not end_date else pd.to_datetime(end_date)
        if start_date:
            start_dt = pd.to_datetime(start_date)
        else:
            start_dt = end_dt - timedelta(days=756)

        # Generate business days
        date_range = pd.date_range(start=start_dt, end=end_dt, freq="B")
        n_days = len(date_range)
        if n_days < 20:
            date_range = pd.date_range(end=end_dt, periods=100, freq="B")
            n_days = len(date_range)

        dt = 1.0 / 252.0
        n_assets = len(tickers)

        # Base correlation structure (stocks correlate with stocks, negative/low with bonds, etc.)
        corr_matrix = np.full((n_assets, n_assets), 0.35)
        np.fill_diagonal(corr_matrix, 1.0)

        for i, t1 in enumerate(tickers):
            for j, t2 in enumerate(tickers):
                if i != j:
                    if ("TLT" in (t1, t2) or "BND" in (t1, t2)) and not ("TLT" in (t1, t2) and "BND" in (t1, t2)):
                        corr_matrix[i, j] = -0.15
                    elif "QQQ" in (t1, t2) and "SPY" in (t1, t2):
                        corr_matrix[i, j] = 0.88
                    elif "GLD" in (t1, t2):
                        corr_matrix[i, j] = 0.10

        # Ensure positive semi-definite correlation
        eigval, eigvec = np.linalg.eigh(corr_matrix)
        eigval = np.maximum(eigval, 1e-4)
        corr_matrix = eigvec @ np.diag(eigval) @ eigvec.T
        d = np.sqrt(np.diag(corr_matrix))
        corr_matrix = corr_matrix / np.outer(d, d)

        # Cholesky decomposition
        try:
            L = np.linalg.cholesky(corr_matrix)
        except np.linalg.LinAlgError:
            L = np.eye(n_assets)

        # Generate correlated shocks
        uncorrelated_shocks = np.random.normal(0, 1, size=(n_days, n_assets))
        correlated_shocks = uncorrelated_shocks @ L.T

        prices_dict = {}
        for idx, ticker in enumerate(tickers):
            mu, sigma, s0 = ASSET_CALIBRATION.get(ticker, (0.09, 0.18, 100.0))
            # GBM formulation: S_t = S_0 * exp(cumsum((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z_t))
            drift = (mu - 0.5 * (sigma ** 2)) * dt
            diffusion = sigma * np.sqrt(dt) * correlated_shocks[:, idx]
            log_returns = drift + diffusion
            price_path = s0 * np.exp(np.cumsum(log_returns))
            prices_dict[ticker] = price_path

        df = pd.DataFrame(prices_dict, index=date_range)
        df.index.name = "Date"
        return df
