# Quantitative Formulas Reference & Specifications

This document defines the exact mathematical formulations, operational interpretations, assumptions, and edge-case behaviors implemented in the **Financial Portfolio Performance & Risk Analytics Platform**.

---

## 1. Asset & Portfolio Returns

### Simple Daily Return
$$r_{i,t} = \frac{P_{i,t} - P_{i,t-1}}{P_{i,t-1}} = \frac{P_{i,t}}{P_{i,t-1}} - 1$$
- **Interpretation:** Percentage capital gain/loss of asset $i$ from trading day $t-1$ to $t$.
- **Assumptions:** Adjusted close prices account for corporate actions (splits, dividend adjustments).
- **Edge cases:** If $P_{i,t-1} \le 0$, flagged by data validator.

### Portfolio Daily Return
$$r_{p,t} = \mathbf{w}^T \mathbf{r}_t = \sum_{i=1}^{N} w_i r_{i,t}$$
- **Interpretation:** Daily return of the aggregate portfolio under weight vector $\mathbf{w}$.
- **Invariant:** Long-only portfolio weights satisfy $\sum_{i=1}^N w_i = 1.0$ and $w_i \ge 0$.

---

## 2. Performance Metrics

### Total Cumulative Return
$$R_{total} = \prod_{t=1}^{T} (1 + r_{p,t}) - 1$$
- **Interpretation:** Overall return over the entire investment window.

### Compound Annual Growth Rate (CAGR)
$$CAGR = (1 + R_{total})^{\frac{252}{T}} - 1$$
- **Interpretation:** Constant annual growth rate that yields the final portfolio value from initial capital.
- **Convention:** Scaled by 252 business days per calendar year.

### Annualized Volatility
$$\sigma_{ann} = \sigma_d \times \sqrt{252} = \sqrt{\frac{1}{T-1} \sum_{t=1}^T (r_{p,t} - \bar{r}_p)^2} \times \sqrt{252}$$
- **Assumptions:** Returns are identically and independently distributed across trading days.

### Sharpe Ratio
$$\text{Sharpe} = \frac{R_{p,ann} - R_f}{\sigma_{p,ann}}$$
- **Interpretation:** Excess return earned above the risk-free rate per unit of total risk.
- **Default:** $R_f = 4.00\%$ annualized.

### Sortino Ratio
$$\text{Sortino} = \frac{R_{p,ann} - R_f}{\sigma_{downside}}, \quad \sigma_{downside} = \sqrt{\frac{1}{T} \sum_{t=1}^T \min(0, r_{p,t} - r_{f,daily})^2} \times \sqrt{252}$$
- **Interpretation:** Penalizes only harmful downside volatility below the daily risk-free threshold.

### Maximum Drawdown (MDD) & Wealth Index
$$W_t = W_0 \prod_{s=1}^t (1 + r_{p,s})$$
$$DD_t = \frac{W_t}{\max_{s \le t} W_s} - 1, \quad MDD = \min_{t} (DD_t)$$
- **Interpretation:** Largest historical capital loss from peak to trough.
- **Diagnostics:** Tracks Peak Date, Trough Date, Recovery Date, and Recovery Duration (days).

### Calmar Ratio
$$\text{Calmar} = \frac{CAGR}{|MDD|}$$
- **Interpretation:** Annualized growth relative to maximum historical drawdown risk.

---

## 3. Risk Analytics

### Covariance & Positive Semi-Definiteness (PSD)
$$\Sigma = \frac{1}{T-1} (R - \bar{R})^T (R - \bar{R}) \times 252$$
- **Robustness:** Verified via eigenvalue decomposition $\lambda_i \ge 0$.
- **Regularization:** If min eigenvalue $< 10^{-7}$, regularized via diagonal shrinkage:
  $$\Sigma_{shrunk} = (1 - \lambda)\Sigma + \lambda \text{diag}(\Sigma)$$

### Pairwise Pearson Correlation
$$\rho_{ij} = \frac{\text{Cov}(r_i, r_j)}{\sigma_i \sigma_j}$$

### Historical Value at Risk (VaR)
$$\text{VaR}_\alpha = -\text{Quantile}_{1-\alpha}(r_p) \times V \times \sqrt{h}$$
- **Interpretation:** Non-parametric empirical loss threshold for confidence $\alpha$ (e.g. 95% or 99%) over horizon $h$.

### Parametric Normal Value at Risk
$$\text{VaR}_\alpha^{param} = -(\mu_d + z_{1-\alpha} \sigma_d) \times V \times \sqrt{h}$$
- **Assumptions:** Gaussian standard distribution ($z_{0.05} = -1.64485$, $z_{0.01} = -2.32635$).

### Historical Expected Shortfall (CVaR)
$$\text{CVaR}_\alpha = \mathbb{E}[L \mid L \ge \text{VaR}_\alpha] \times \sqrt{h}$$
- **Interpretation:** Expected tail loss on days when losses breach the VaR threshold.

### Capital Asset Pricing Model Beta & Jensen's Alpha
$$\beta = \frac{\text{Cov}(r_p, r_m)}{\text{Var}(r_m)}, \quad \alpha_{ann} = (R_{p,ann} - R_f) - \beta (R_{m,ann} - R_f)$$

### Tracking Error
$$TE = \text{StDev}(r_p - r_m) \times \sqrt{252}$$

### Component & Percentage Risk Contribution
$$\text{Marginal Risk Contribution (MRC)}_i = \frac{(\Sigma \mathbf{w})_i}{\sigma_p}$$
$$\text{Component Risk Contribution (RC)}_i = w_i \times \text{MRC}_i$$
$$\text{Percentage Risk Contribution (PRC)}_i = \frac{\text{RC}_i}{\sigma_p}$$
- **Mathematical Invariant:** $\sum_{i=1}^N \text{PRC}_i = 100\%$.

---

## 4. Portfolio Optimization

### Minimum Volatility
$$\min_{\mathbf{w}} \mathbf{w}^T \Sigma \mathbf{w} \quad \text{s.t.} \quad \sum_{i=1}^N w_i = 1, \quad w_{min} \le w_i \le w_{max}$$

### Maximum Sharpe Ratio
$$\min_{\mathbf{w}} -\frac{\mathbf{w}^T \mu - R_f}{\sqrt{\mathbf{w}^T \Sigma \mathbf{w}}} \quad \text{s.t.} \quad \sum_{i=1}^N w_i = 1, \quad w_{min} \le w_i \le w_{max}$$

### Efficient Frontier
$$\min_{\mathbf{w}} \mathbf{w}^T \Sigma \mathbf{w} \quad \text{s.t.} \quad \mathbf{w}^T \mu = R_{target}, \quad \sum_{i=1}^N w_i = 1, \quad w_{min} \le w_i \le w_{max}$$
Traced for $R_{target} \in [R_{min\_vol}, \max(\mu_i)]$.

---

## 5. Rebalancing Engine

### Allocation Drift
$$Drift_i = w_{current, i} - w_{target, i}$$
- Status:
  - Normal: $|Drift_i| \le 0.5 \times \text{Threshold}$
  - Warning: $0.5 \times \text{Threshold} < |Drift_i| \le \text{Threshold}$
  - Action Required: $|Drift_i| > \text{Threshold}$

### Desired Trade Value & Direction
$$Trade_i = V_{portfolio} \times (w_{target, i} - w_{current, i})$$
- Action:
  - $Trade_i > 0$ and $|Trade_i| \ge \text{MinTradeSize} \implies \text{BUY}$
  - $Trade_i < 0$ and $|Trade_i| \ge \text{MinTradeSize} \implies \text{SELL}$
  - Otherwise $\implies \text{HOLD}$
