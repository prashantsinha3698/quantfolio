"""
Normalizes prices across trading calendars and generates clean return series.
"""
from typing import Tuple
import numpy as np
import pandas as pd


class MarketDataNormalizer:
    """Synchronizes pricing calendars and generates simple and log return series."""

    @staticmethod
    def normalize(prices: pd.DataFrame, max_ffill_days: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Args:
            prices: Raw validated price DataFrame
            max_ffill_days: Max consecutive business days to forward-fill across holidays/halts

        Returns:
            clean_prices: Synchronized price DataFrame
            simple_returns: Daily simple returns (P_t / P_{t-1} - 1)
            log_returns: Daily log returns (ln(P_t / P_{t-1}))
        """
        # Forward fill small gaps (e.g. international market holidays, different calendar schedules)
        filled_prices = prices.ffill(limit=max_ffill_days)

        # Drop any remaining unfillable rows (e.g. before initial asset inception)
        clean_prices = filled_prices.dropna()

        # Compute simple daily returns
        simple_returns = clean_prices.pct_change().dropna()

        # Compute log returns
        log_returns = np.log(clean_prices / clean_prices.shift(1)).dropna()

        return clean_prices, simple_returns, log_returns
