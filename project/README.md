# Financial Portfolio Performance & Risk Analytics Platform

An institutional-grade quantitative portfolio performance, risk analytics, mathematical optimization, and rebalancing platform built with a Python FastAPI analytics engine and a React / TypeScript / Tailwind CSS / Plotly analytical dashboard.

---

## Key Capabilities

### 1. Portfolio Performance Analytics
- **Return Metrics:** Total Return, Compound Annual Growth Rate (CAGR), Annualized Arithmetic Return, Daily Return Time-Series.
- **Risk-Adjusted Metrics:** Annualized Sharpe Ratio ($R_f = 4.0\%$), Sortino Ratio (downside semivariance), Calmar Ratio ($CAGR / |MDD|$).
- **Drawdown Analysis:** Running high-water mark wealth curve, Maximum Drawdown (MDD), underwater drawdown chart, and Historical Drawdown Events table detailing peak dates, trough dates, recovery dates, magnitude, and duration in days.
- **Benchmark Comparisons:** Cumulative wealth comparison, Alpha, Beta, Tracking Error against configurable benchmarks (e.g. `SPY`, `QQQ`).

### 2. Quantitative Risk Engine
- **Value at Risk (VaR):**
  - **Historical Simulation VaR** at 95% and 99% confidence levels (empirical percentile losses).
  - **Parametric Gaussian VaR** using standard normal distribution assumptions ($Z_{0.05} = -1.645$).
- **Expected Shortfall (CVaR):** Conditional tail expectation measuring average losses exceeding the VaR threshold.
- **Correlation & Covariance:** Pairwise Pearson correlation heatmap and sample covariance matrix with positive semi-definite (PSD) eigenvalue verification and diagonal shrinkage.
- **Component Risk Contribution:** Decomposes total portfolio volatility into marginal ($MRC_i$) and component ($RC_i$) risk contributions, verifying $\sum PRC_i = 100\%$.
- **Multi-Horizon Rolling Volatility:** 20-day, 60-day, 126-day, and 252-day dynamic risk regimes.

### 3. Mathematical Portfolio Optimization
- **SciPy SLSQP Constrained Solver:** Enforces full investment budget constraints ($\sum w_i = 1.0$) and individual asset bounds ($w_{min} \le w_i \le w_{max}$).
- **Minimum Volatility Portfolio:** Minimizes portfolio variance $\mathbf{w}^T \Sigma \mathbf{w}$.
- **Maximum Sharpe Ratio Portfolio:** Maximizes risk-adjusted excess return $\frac{\mathbf{w}^T \mu - R_f}{\sqrt{\mathbf{w}^T \Sigma \mathbf{w}}}$.
- **Markowitz Efficient Frontier:** Traces Pareto optimal allocations across discrete target returns, displaying Current Portfolio, Min Vol, Max Sharpe, and individual asset coordinates.

### 4. Actionable Rebalancing Engine
- **Drift Detection:** Tracks $D_i = w_{current, i} - w_{target, i}$ and categorizes status into `normal`, `warning`, and `action_required`.
- **Trade Generation:** Calculates target dollar amounts ($V \cdot w_{target, i}$), delta trade values, order directions (`BUY`, `SELL`, `HOLD`), and estimated share counts.
- **Execution Filters:** Filters small transactions below a minimum trade size (e.g. $1,000) and models proportional transaction cost drag.

---

## Technology Stack

- **Backend:** Python 3.14, FastAPI, Pandas, NumPy, SciPy (SLSQP), yfinance, PyArrow, Pydantic v2, Pytest.
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Plotly.js (`plotly.js-dist-min`), Lucide React.
- **Data Persistence & Caching:** Local Apache Arrow Parquet caching with SHA-256 keys.

---

## Directory Structure

```text
project/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── core/                    # Settings, exceptions, logging
│   │   ├── domain/                  # Pure domain models (dataclasses)
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── data/                    # yfinance provider, demo generator, cache, validator
│   │   ├── analytics/               # Returns, performance, drawdown, CAGR
│   │   ├── risk/                    # VaR, CVaR, covariance PSD, correlation, beta, risk contribution
│   │   ├── optimization/            # SciPy SLSQP optimizer, efficient frontier
│   │   ├── rebalance/               # Allocation drift, trade generation, costs
│   │   └── api/routes/              # REST endpoint routers
│   └── tests/                       # Complete Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── components/              # AppShell, TopBar, MetricCard, PlotlyChart, Views
│   │   ├── services/api.ts          # Centralized typed HTTP client
│   │   ├── types/index.ts           # TypeScript interfaces
│   │   ├── App.tsx                  # Root state & navigation
│   │   └── index.css                # Tailwind base & tabular typography
│   └── package.json
├── data/
│   └── cache/                       # Parquet cached market data files
├── docs/
│   ├── architecture.md              # System design & data pipeline
│   ├── formulas.md                  # Complete mathematical specifications
│   ├── api.md                       # REST API endpoint documentation
│   └── decisions.md                 # Architectural Decision Records (ADRs)
├── requirements.txt                 # Pinned Python dependencies
└── README.md
```

---

## Quickstart & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node v25)
- npm

### 2. Backend Setup
```bash
cd project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend API server (runs at http://127.0.0.1:8000)
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### 3. Frontend Setup
```bash
cd project/frontend

# Install dependencies
npm install

# Start Vite development server (runs at http://127.0.0.1:5173)
npm run dev
```

---

## Testing

### Run Backend Quantitative Test Suite
```bash
cd project
.\.venv\Scripts\python -m pytest backend/tests -v
```
All 22 unit & integration tests verify:
- Invariant: Long-only weight bounds and budget constraint $\sum w_i = 1.0$.
- Invariant: Total risk contributions sum to 100% ($\sum PRC_i \approx 1.0$).
- Invariant: Covariance positive semi-definiteness via eigenvalue verification.
- Invariant: Expected Shortfall (CVaR) is strictly $\ge$ Value at Risk (VaR).
- Total Return, CAGR, Sharpe, Sortino, Drawdown, and Calmar ratios.
- Drift calculations and BUY/SELL/HOLD classification.

### Build Frontend Production Bundle
```bash
cd project/frontend
node ./node_modules/vite/bin/vite.js build
```

---

## Financial Disclaimer
This application is an educational and quantitative research tool. All calculations, optimizations, and rebalancing recommendations are model-based research estimates and do not constitute personalized investment, financial, or tax advice. Past historical performance does not guarantee future results.
