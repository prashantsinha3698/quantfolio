"""
High-level MarketDataCollector coordinating caching, data providers, validation, and normalization.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import pandas as pd

from app.core.exceptions import MarketDataError
from app.core.logging import logger
from app.data.cache import MarketDataCache
from app.data.demo_provider import DemoMarketDataProvider
from app.data.normalizer import MarketDataNormalizer
from app.data.validator import MarketDataValidator
from app.data.yfinance_provider import YFinanceProvider
from app.domain.models import MarketData


def resolve_date_range(
    date_range: Optional[str] = "1Y",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[str, str]:
    """Translates common period tags (1M, 3M, 6M, YTD, 1Y, 3Y, 5Y, MAX) into YYYY-MM-DD bounds."""
    now = datetime.now()
    end_str = end_date if end_date else now.strftime("%Y-%m-%d")

    if start_date:
        return start_date, end_str

    tag = (date_range or "1Y").upper()
    if tag == "1M":
        start_dt = now - timedelta(days=30)
    elif tag == "3M":
        start_dt = now - timedelta(days=90)
    elif tag == "6M":
        start_dt = now - timedelta(days=180)
    elif tag == "YTD":
        start_dt = datetime(now.year, 1, 1)
    elif tag == "1Y":
        start_dt = now - timedelta(days=365)
    elif tag == "3Y":
        start_dt = now - timedelta(days=365 * 3)
    elif tag == "5Y":
        start_dt = now - timedelta(days=365 * 5)
    elif tag == "MAX":
        start_dt = now - timedelta(days=365 * 10)
    else:
        start_dt = now - timedelta(days=365)

    return start_dt.strftime("%Y-%m-%d"), end_str


class MarketDataCollector:
    """Orchestrates market data fetching, caching, validation, and alignment."""

    def __init__(self, cache: Optional[MarketDataCache] = None):
        self.cache = cache or MarketDataCache()
        self.yf_provider = YFinanceProvider()
        self.demo_provider = DemoMarketDataProvider()

    def get_portfolio_market_data(
        self,
        tickers: List[str],
        benchmark: str = "SPY",
        date_range: Optional[str] = "1Y",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_demo: bool = False,
    ) -> MarketData:
        start_s, end_s = resolve_date_range(date_range, start_date, end_date)
        all_tickers = sorted(list(set([t.strip().upper() for t in tickers + [benchmark]])))

        raw_prices: Optional[pd.DataFrame] = None
        source = "yfinance"
        is_demo = False
        warnings: List[str] = []

        def is_usable(df: Optional[pd.DataFrame]) -> bool:
            if df is None or df.empty:
                return False
            # If any ticker column is entirely NaN
            if df.isna().all().any():
                return False
            # Check if sufficient non-NaN rows exist
            valid_rows = df.dropna(how="all").shape[0]
            if valid_rows < 15:
                return False
            # Check if forward-filled data has sufficient complete rows
            if df.ffill(limit=5).dropna().shape[0] < 10:
                return False
            return True

        # 1. Check local cache first (unless demo forced)
        if not force_demo:
            cached_prices = self.cache.get(all_tickers, start_s, end_s)
            if is_usable(cached_prices):
                raw_prices = cached_prices

        # 2. Fetch from yfinance if not cached
        if raw_prices is None and not force_demo:
            try:
                fetched_prices = self.yf_provider.get_history(all_tickers, start_s, end_s)
                if is_usable(fetched_prices):
                    raw_prices = fetched_prices
                    self.cache.set(all_tickers, start_s, end_s, raw_prices)
                else:
                    logger.warning("External market data contained all-NaN columns or insufficient rows; using demo data.")
                    warnings.append("External market data incomplete for requested period; switched to calibrated demo data.")
                    raw_prices = None
            except Exception as e:
                logger.warning(f"Yahoo Finance acquisition failed ({e}); falling back to demo data engine.")
                warnings.append(f"External market data unavailable ({str(e)}). Using calibrated demo market data.")
                raw_prices = None

        # 3. Fallback to Demo provider if needed or forced
        if raw_prices is None or force_demo:
            raw_prices = self.demo_provider.get_history(all_tickers, start_s, end_s)
            source = "demo_fixture"
            is_demo = True
            if not warnings:
                warnings.append("Operating in Demo Data Mode with realistic asset calibrations.")

        # 4. Validate data
        validated_prices, val_warnings = MarketDataValidator.validate(raw_prices, all_tickers)
        warnings.extend(val_warnings)

        # 5. Normalize prices and returns
        clean_prices, simple_returns, _ = MarketDataNormalizer.normalize(validated_prices)

        # 6. Separate asset prices from benchmark
        asset_tickers = [t for t in tickers if t in clean_prices.columns]
        benchmark_col = benchmark if benchmark in clean_prices.columns else clean_prices.columns[0]

        asset_prices = clean_prices[asset_tickers]
        asset_returns = simple_returns[asset_tickers]
        benchmark_prices = clean_prices[benchmark_col]
        benchmark_returns = simple_returns[benchmark_col]

        return MarketData(
            prices=asset_prices,
            returns=asset_returns,
            benchmark_prices=benchmark_prices,
            benchmark_returns=benchmark_returns,
            start_date=clean_prices.index[0].strftime("%Y-%m-%d"),
            end_date=clean_prices.index[-1].strftime("%Y-%m-%d"),
            source=source,
            is_demo=is_demo,
            data_quality_warnings=warnings,
        )
