"""
Concrete MarketDataProvider using Yahoo Finance (yfinance).
"""
from typing import List, Optional
import pandas as pd
import yfinance as yf

from app.data.base_provider import MarketDataProvider
from app.core.exceptions import MarketDataError, InvalidTickerError
from app.core.logging import logger


class YFinanceProvider(MarketDataProvider):
    """Fetches historical market data using yfinance with corporate actions auto-adjusted."""

    def get_history(
        self,
        tickers: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = "1d",
    ) -> pd.DataFrame:
        clean_tickers = [t.strip().upper() for t in tickers]
        if not clean_tickers:
            raise InvalidTickerError("No tickers provided for market data request.")

        logger.info(f"Downloading data for {clean_tickers} from yfinance (range: {start_date} to {end_date})")

        try:
            raw_data = yf.download(
                tickers=clean_tickers,
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=True,
                progress=False,
                threads=True,
            )
        except Exception as e:
            logger.error(f"yfinance download failed: {e}")
            raise MarketDataError(f"Failed to connect to Yahoo Finance: {e}")

        if raw_data.empty:
            raise MarketDataError(f"Yahoo Finance returned no historical data for tickers: {clean_tickers}")

        # yfinance multi-ticker returns MultiIndex columns: ('Close', 'SPY'), ('Open', 'SPY'), etc.
        # Or if 1 ticker, columns might be 'Close', 'Open', etc.
        prices: pd.DataFrame
        if isinstance(raw_data.columns, pd.MultiIndex):
            if "Close" in raw_data.columns.levels[0]:
                prices = raw_data["Close"]
            else:
                # Fallback to first available top-level column
                top_col = raw_data.columns.levels[0][0]
                prices = raw_data[top_col]
        else:
            if "Close" in raw_data.columns:
                prices = raw_data[["Close"]].copy()
                prices.columns = [clean_tickers[0]]
            else:
                prices = raw_data

        # Ensure columns match clean_tickers
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=clean_tickers[0])

        return prices
