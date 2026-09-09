"""
Application configuration and runtime settings.
"""
from pathlib import Path
from typing import List
import os

# Base Directories
APP_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Cache & Data storage
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Quantitative Assumptions & Defaults
DEFAULT_RISK_FREE_RATE: float = float(os.getenv("DEFAULT_RISK_FREE_RATE", "0.04"))
DEFAULT_BENCHMARK: str = os.getenv("DEFAULT_BENCHMARK", "SPY")
ANNUALIZATION_FACTOR: int = 252  # Standard trading days per year in US equity markets
CALENDAR_DAYS: int = 365
CACHE_TTL_SECONDS: int = 86400  # 24 hours

# API Configuration
API_V1_PREFIX: str = "/api"
PROJECT_NAME: str = "Financial Portfolio Performance & Risk Analytics"
VERSION: str = "1.0.0"

# CORS configuration
CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
