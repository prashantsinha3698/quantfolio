"""
Correlation matrix and rolling correlation computations.
"""
from typing import Dict, List, Optional
import pandas as pd


def compute_correlation_matrix(returns_df: pd.DataFrame) -> Dict[str, any]:
    """Calculates pairwise Pearson correlation matrix across assets."""
    corr_df = returns_df.corr(method="pearson")
    tickers = list(corr_df.columns)
    matrix = corr_df.round(4).values.tolist()
    return {
        "tickers": tickers,
        "matrix": matrix,
    }


def compute_rolling_correlation(
    series_a: pd.Series,
    series_b: pd.Series,
    windows: List[int] = [20, 60, 126, 252],
) -> Dict[str, List[Dict]]:
    """
    Calculates rolling Pearson correlation between two return series across multiple time horizons.
    """
    results: Dict[str, List[Dict]] = {}

    for w in windows:
        if len(series_a) >= w:
            rolling_series = series_a.rolling(window=w).corr(series_b).dropna()
            points = [
                {"date": d.strftime("%Y-%m-%d"), "correlation": float(round(val, 4))}
                for d, val in rolling_series.items()
            ]
            results[f"{w}d"] = points
        else:
            results[f"{w}d"] = []

    return results
