# Platform Architecture Document

## 1. Architectural Philosophy
The **Financial Portfolio Performance & Risk Analytics Platform** is designed as a layered, modular monolith emphasizing **mathematical correctness, numerical stability, testability, and high information density**.

Financial calculation logic is strictly decoupled from presentation:
```text
Portfolio Configuration
        ↓
Data Acquisition & Caching (yfinance + Parquet)
        ↓
Data Validation & Normalization
        ↓
Time-Series & Returns Engine (Pandas / NumPy)
        ↓
┌───────────────────────┬───────────────────────┐
▼                       ▼                       ▼
Performance Engine      Risk Engine      Portfolio Analytics
└───────────────────────┼───────────────────────┘
                        ▼
               Optimization Engine (SciPy SLSQP)
                        ▼
               Rebalancing Engine
                        ▼
               FastAPI REST Layer
                        ▼
           React / TS / Plotly Quant Terminal
```

---

## 2. Layer Specifications

### 2.1 Domain Layer (`backend/app/domain/`)
- Pure Python dataclasses: `Holding`, `PortfolioConfig`, `RiskConfig`, `RebalanceConfig`, `MarketData`, `OptimizationResult`, `TradeRecommendation`.
- Defines entities and business rules without external framework dependencies.

### 2.2 Market Data & Ingestion (`backend/app/data/`)
- `MarketDataProvider` abstract protocol.
- `YFinanceProvider`: Implements auto-adjusted close price downloads.
- `DemoMarketDataProvider`: Synthetic geometric Brownian motion generator with cross-asset correlations, guaranteeing zero downtime and test reproducibility.
- `MarketDataCache`: PyArrow Parquet caching with SHA-256 keys and TTL expiration.
- `MarketDataValidator`: Ensures strictly positive prices, monotonic timestamp ordering, duplicate elimination, and calendar alignment.
- `MarketDataNormalizer`: Generates aligned simple return matrices ($P_t / P_{t-1} - 1$) and log returns.

### 2.3 Analytics & Risk Engine (`backend/app/analytics/` & `backend/app/risk/`)
- **Returns:** Portfolio vector multiplication $r_{p,t} = \mathbf{w}^T \mathbf{r}_t$.
- **Performance:** Total return, CAGR, annualized volatility, Sharpe ratio, Sortino ratio, wealth series, drawdown curve, and top drawdown events.
- **Risk:**
  - Covariance matrix with positive semi-definite (PSD) eigenvalue validation and diagonal shrinkage.
  - Pairwise correlation matrix and rolling multi-horizon volatility (20D, 60D, 126D, 252D).
  - Historical VaR & CVaR (Expected Shortfall) at 95% and 99% levels.
  - Parametric Gaussian VaR.
  - Beta, Jensen's Alpha, and Tracking Error.
  - Component Risk Contribution ($\sum PRC_i = 100\%$).

### 2.4 Optimization Engine (`backend/app/optimization/`)
- Constrained non-linear optimization using `scipy.optimize.minimize(method='SLSQP')`.
- Budget constraint: $\sum w_i = 1.0$.
- Bound constraints: $w_{min} \le w_i \le w_{max}$.
- Objectives: Minimum Volatility ($\mathbf{w}^T \Sigma \mathbf{w}$), Maximum Sharpe Ratio ($-\frac{\mathbf{w}^T \mu - R_f}{\sqrt{\mathbf{w}^T \Sigma \mathbf{w}}}$).
- Efficient frontier generator tracing target returns from min-vol to max return.

### 2.5 Rebalancing Engine (`backend/app/rebalance/`)
- Drift calculation: $D_i = w_{current, i} - w_{target, i}$.
- Multi-tier drift classification: normal, warning, action required.
- Trade generation: $Trade_i = V \cdot (w_{target, i} - w_{current, i})$.
- Filtering by minimum trade size and calculation of transaction cost drag.

### 2.6 REST API Layer (`backend/app/api/`)
- FastAPI endpoints with Pydantic request/response validation.
- JSON error responses with domain exception handling.

### 2.7 Frontend Application (`frontend/src/`)
- Vite + React 19 + TypeScript + Tailwind CSS.
- Plotly.js for interactive quantitative financial charts.
- Dark terminal fintech visual design with high contrast, tabular typography, and accessible UI indicators.
