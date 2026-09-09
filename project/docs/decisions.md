# Architectural Decision Records (ADRs)

## ADR 1: Abstraction of Market Data Layer
- **Status:** Accepted
- **Context:** Hard-coding `yfinance` direct calls throughout analytical code creates fragile vendor lock-in and prevents testing in offline/sandboxed environments.
- **Decision:** Define `MarketDataProvider` abstract base class. Implement `YFinanceProvider` for live/historical data, `DemoMarketDataProvider` for offline development and synthetic tests, and `MarketDataCollector` for cache orchestration.
- **Consequences:** Analytical engines are completely isolated from network protocols, API changes, and vendor rate limits.

---

## ADR 2: Parquet-Based Caching Layer
- **Status:** Accepted
- **Context:** Re-downloading multi-year historical time-series repeatedly causes slow responsiveness and risks rate-limiting.
- **Decision:** Use Apache Arrow Parquet (`pyarrow`) for local tabular caching. Keys are SHA-256 hashes of sorted tickers and normalized date bounds with a configurable TTL (default 24 hours).
- **Consequences:** Drastically reduced network traffic; fast sub-second response times on subsequent analytical runs.

---

## ADR 3: Covariance Regularization & PSD Stabilization
- **Status:** Accepted
- **Context:** Sample covariance matrices computed from assets with differing volatilities or short observation histories may possess small negative eigenvalues or high condition numbers, causing numerical optimization failure in SciPy.
- **Decision:** Validate positive semi-definiteness via eigenvalue decomposition. If the minimum eigenvalue is below $10^{-7}$, clamp negative eigenvalues and apply diagonal shrinkage towards sample variance:
  $$\Sigma_{shrunk} = (1 - \lambda)\Sigma + \lambda \text{diag}(\Sigma)$$
- **Consequences:** Guarantees optimization convergence without distorting asset correlation profiles.

---

## ADR 4: Separation of Optimization and Rebalancing
- **Status:** Accepted
- **Context:** An optimization recommendation is an analytical model output; it should never silently overwrite the investor's intended strategic target weights.
- **Decision:** Maintain `Target Allocation`, `Current Allocation`, and `Optimized Allocation` as three distinct concepts. The rebalancing engine calculates drift strictly against the user's defined target weights, while the optimization workstation provides an independent research view.
- **Consequences:** Prevents unexpected asset reallocations and provides full transparency for decision-making.

---

## ADR 5: Dark Quantitative Terminal UI Aesthetics
- **Status:** Accepted
- **Context:** Quantitative financial workflows require high information density, clear contrast, and minimal visual distraction.
- **Decision:** Implement a near-black slate/graphite theme (`#080c14`, `#111827`, `#141d30`) with monospace tabular numbers for financial figures and subtle cyan/emerald/rose accents. Avoid cartoonish fintech gradients or low-density cards.
- **Consequences:** Delivers an institutional-grade, Bloomberg-inspired workstation feel.
