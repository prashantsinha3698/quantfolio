"""
Market data validator for integrity, date ordering, positive prices, and gaps.
"""
from typing import List, Tuple
import pandas as pd
from app.core.exceptions import InsufficientDataError, MarketDataError
from app.core.logging import logger


class MarketDataValidator:
    """Validates raw pricing time-series and surfaces data-quality diagnostics."""

    @staticmethod
    def validate(df: pd.DataFrame, expected_tickers: List[str]) -> Tuple[pd.DataFrame, List[str]]:
        warnings: List[str] = []

        if df.empty:
            raise MarketDataError("Market data provider returned an empty dataset.")

        # Ensure DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception as e:
                raise MarketDataError(f"Failed to parse dates in price series: {e}")

        # Check sorting
        if not df.index.is_monotonic_increasing:
            logger.info("Sorting price index in chronological order.")
            df = df.sort_index()

        # Deduplicate dates
        if df.index.duplicated().any():
            dup_count = df.index.duplicated().sum()
            warnings.append(f"Removed {dup_count} duplicate timestamp(s) from price series.")
            df = df[~df.index.duplicated(keep="last")]

        # Check missing tickers
        missing_tickers = [t for t in expected_tickers if t not in df.columns]
        if missing_tickers:
            warnings.append(f"No price history found for tickers: {', '.join(missing_tickers)}")

        # Check for non-positive prices
        numeric_df = df.select_dtypes(include=["number"])
        if (numeric_df <= 0).any().any():
            warnings.append("Detected non-positive price values; replacing invalid prices with NaN.")
            df[numeric_df <= 0] = pd.NA

        # Missing values check
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                pct = (count / len(df)) * 100
                if pct > 30.0:
                    warnings.append(f"Ticker {col} has {pct:.1f}% missing price observations.")
                else:
                    logger.debug(f"Ticker {col} has {count} missing observations ({pct:.1f}%).")

        # Insufficient observations check
        valid_rows = df.dropna(how="all").shape[0]
        if valid_rows < 15:
            raise InsufficientDataError(
                f"Insufficient historical data: found only {valid_rows} observations, minimum required is 15."
            )

        return df, warnings
