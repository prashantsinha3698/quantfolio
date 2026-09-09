"""
Custom domain and analytical exceptions for the portfolio platform.
"""

class PortfolioAnalyticsError(Exception):
    """Base exception for all portfolio analytics errors."""
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MarketDataError(PortfolioAnalyticsError):
    """Raised when external market data retrieval fails or returns invalid responses."""
    pass


class InvalidTickerError(MarketDataError):
    """Raised when one or more tickers cannot be found or are invalid."""
    pass


class InsufficientDataError(MarketDataError):
    """Raised when historical observations are too few for statistical significance."""
    pass


class PortfolioValidationError(PortfolioAnalyticsError):
    """Raised when portfolio configurations violate domain constraints (e.g. weights sum != 1)."""
    pass


class OptimizationError(PortfolioAnalyticsError):
    """Raised when numerical portfolio optimization fails."""
    pass


class InfeasibleConstraintsError(OptimizationError):
    """Raised when optimization constraints cannot be satisfied."""
    pass
