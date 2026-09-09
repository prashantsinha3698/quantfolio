"""
Abstract base class for market data providers.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd


class MarketDataProvider(ABC):
    """
    Abstract interface for historical market data retrieval.
    Decouples analytical engines from specific data vendors (yfinance, Polygon, Bloomberg, etc.).
    """

    @abstractmethod
    def get_history(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Retrieve adjusted close prices for the requested tickers over the date range.

        Returns:
            pd.DataFrame: DataFrame indexed by Timestamp, with columns corresponding to tickers.
        """
        pass
