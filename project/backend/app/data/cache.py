"""
Parquet-based local file caching for historical market data.
"""
import hashlib
import time
from pathlib import Path
from typing import Optional, List
import pandas as pd

from app.core.config import CACHE_DIR, CACHE_TTL_SECONDS
from app.core.logging import logger


class MarketDataCache:
    """Stores and retrieves price DataFrames as Parquet files on local disk."""

    def __init__(self, cache_dir: Path = CACHE_DIR, default_ttl: int = CACHE_TTL_SECONDS):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, tickers: List[str], start_date: Optional[str], end_date: Optional[str]) -> str:
        clean_tickers = sorted([t.strip().upper() for t in tickers])
        raw_key = f"{','.join(clean_tickers)}_{start_date or 'default'}_{end_date or 'default'}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def get(self, tickers: List[str], start_date: Optional[str], end_date: Optional[str]) -> Optional[pd.DataFrame]:
        cache_key = self._generate_key(tickers, start_date, end_date)
        cache_file = self.cache_dir / f"prices_{cache_key}.parquet"

        if not cache_file.exists():
            return None

        # Check TTL
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > self.default_ttl:
            logger.info(f"Cache expired for {tickers} (age: {file_age:.1f}s > {self.default_ttl}s)")
            return None

        try:
            df = pd.read_parquet(cache_file)
            logger.info(f"Cache hit for key {cache_key} ({len(tickers)} tickers, {len(df)} rows)")
            return df
        except Exception as e:
            logger.warning(f"Failed to read cache file {cache_file}: {e}")
            return None

    def set(self, tickers: List[str], start_date: Optional[str], end_date: Optional[str], df: pd.DataFrame) -> None:
        if df.empty:
            return
        cache_key = self._generate_key(tickers, start_date, end_date)
        cache_file = self.cache_dir / f"prices_{cache_key}.parquet"
        try:
            df.to_parquet(cache_file, engine="pyarrow")
            logger.info(f"Saved {len(df)} price observations to cache: {cache_file.name}")
        except Exception as e:
            logger.warning(f"Failed to cache prices to {cache_file}: {e}")
