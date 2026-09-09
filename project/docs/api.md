# REST API Specification

The analytics platform exposes RESTful endpoints at `http://127.0.0.1:8000/api`. Interactive OpenAPI documentation is available at `/docs` and `/redoc`.

---

## 1. System Health
### `GET /api/health`
Returns service status, application version, and server timestamp.
```json
{
  "status": "healthy",
  "service": "Financial Portfolio Performance & Risk Analytics",
  "version": "1.0.0",
  "timestamp": "2026-09-09T16:37:06.944205"
}
```

---

## 2. Portfolios
### `GET /api/portfolios/presets`
Returns predefined sample portfolios (Balanced Growth, Tech Innovation, All-Weather Risk Parity).

### `POST /api/portfolios/evaluate`
Accepts a `PortfolioRequest`, retrieves latest market prices, and calculates position market values, current weights, and allocation drift.

**Request Payload:**
```json
{
  "name": "Balanced Growth",
  "initial_capital": 1000000.0,
  "base_currency": "USD",
  "benchmark": "SPY",
  "holdings": [
    { "ticker": "SPY", "quantity": 700, "target_weight": 0.40, "min_weight": 0.0, "max_weight": 0.50 },
    { "ticker": "QQQ", "quantity": 450, "target_weight": 0.25, "min_weight": 0.0, "max_weight": 0.40 },
    { "ticker": "GLD", "quantity": 650, "target_weight": 0.15, "min_weight": 0.0, "max_weight": 0.30 },
    { "ticker": "TLT", "quantity": 1050, "target_weight": 0.10, "min_weight": 0.0, "max_weight": 0.30 },
    { "ticker": "VNQ", "quantity": 1100, "target_weight": 0.10, "min_weight": 0.0, "max_weight": 0.30 }
  ],
  "date_range": "1Y"
}
```

---

## 3. Analytics
### `POST /api/analytics/performance`
Calculates comprehensive portfolio performance metrics, cumulative wealth curves, underwater drawdowns, rolling statistics, and major historical drawdown events.

---

## 4. Risk
### `POST /api/risk/analytics`
Generates 95% and 99% Historical VaR and CVaR, Parametric VaR, Beta, Tracking Error, Covariance Matrix, Pearson Correlation Matrix, and Component Risk Contributions.

---

## 5. Optimization
### `POST /api/optimization/run`
Solves the Minimum Volatility and Maximum Sharpe optimal allocations, and traces the Markowitz Efficient Frontier curve.
Optional query payload field `opt_params`:
```json
{
  "risk_free_rate": 0.04,
  "min_weight": 0.0,
  "max_weight": 0.50,
  "expected_return_method": "historical_mean",
  "frontier_points_count": 35
}
```

---

## 6. Rebalancing
### `POST /api/rebalance/evaluate`
Evaluates allocation drift against the drift threshold (e.g. 5%) and produces prioritized BUY, SELL, and HOLD order recommendations with estimated share quantities and transaction fee drag.
