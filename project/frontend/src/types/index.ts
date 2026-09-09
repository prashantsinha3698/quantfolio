export interface HoldingInput {
  ticker: string;
  quantity: number;
  target_weight: number;
  min_weight: number;
  max_weight: number;
}

export interface HoldingResponse {
  ticker: string;
  quantity: number;
  current_price: number;
  market_value: number;
  current_weight: number;
  target_weight: number;
  min_weight: number;
  max_weight: number;
  drift: number;
}

export interface RiskConfig {
  confidence_level: number;
  var_horizon_days: number;
  lookback_days: number;
}

export interface RebalanceConfig {
  drift_threshold: number;
  minimum_trade_value: number;
  transaction_cost_rate: number;
}

export interface PortfolioRequest {
  name: string;
  initial_capital: number;
  base_currency: string;
  benchmark: string;
  holdings: HoldingInput[];
  risk_config?: RiskConfig;
  rebalance_config?: RebalanceConfig;
  date_range?: string;
  start_date?: string;
  end_date?: string;
}

export interface PortfolioSummaryResponse {
  name: string;
  base_currency: string;
  benchmark: string;
  initial_capital: number;
  current_value: number;
  cash_value: number;
  holdings: HoldingResponse[];
  data_source: string;
  is_demo: boolean;
  last_updated: string;
  data_quality_warnings: string[];
}

export interface PerformanceKPIs {
  total_return: number;
  annualized_return: number;
  cagr: number;
  annualized_volatility: number;
  daily_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown: number;
  calmar_ratio: number;
  positive_days_pct: number;
  benchmark_total_return: number;
  benchmark_cagr: number;
  benchmark_volatility: number;
  benchmark_sharpe: number;
  alpha: number;
  beta: number;
  tracking_error: number;
}

export interface TimeSeriesPoint {
  date: string;
  portfolio_return: number;
  benchmark_return: number;
  portfolio_wealth: number;
  benchmark_wealth: number;
  portfolio_drawdown: number;
  benchmark_drawdown: number;
}

export interface DrawdownEvent {
  peak_date: string;
  trough_date: string;
  recovery_date?: string;
  magnitude: number;
  duration_days: number;
  recovery_days?: number;
}

export interface RollingMetricPoint {
  date: string;
  portfolio_vol: number;
  benchmark_vol: number;
  portfolio_return_rolling: number;
}

export interface PerformanceResponse {
  kpis: PerformanceKPIs;
  time_series: TimeSeriesPoint[];
  major_drawdowns: DrawdownEvent[];
  rolling_metrics: RollingMetricPoint[];
  assumptions: Record<string, string>;
}

export interface RiskKPIs {
  annualized_volatility: number;
  historical_var_95: number;
  historical_var_99: number;
  historical_var_95_dollar: number;
  historical_var_99_dollar: number;
  parametric_var_95: number;
  parametric_var_99: number;
  parametric_var_95_dollar: number;
  parametric_var_99_dollar: number;
  historical_cvar_95: number;
  historical_cvar_99: number;
  historical_cvar_95_dollar: number;
  historical_cvar_99_dollar: number;
  beta: number;
  tracking_error: number;
  skewness: number;
  kurtosis: number;
}

export interface RiskContributionItem {
  ticker: string;
  weight: number;
  marginal_risk_contribution: number;
  component_risk_contribution: number;
  percentage_risk_contribution: number;
}

export interface CorrelationMatrix {
  tickers: string[];
  matrix: number[][];
}

export interface CovarianceMatrix {
  tickers: string[];
  matrix: number[][];
}

export interface RollingVolPoint {
  date: string;
  vol_20d?: number;
  vol_60d?: number;
  vol_126d?: number;
  vol_252d?: number;
}

export interface RiskResponse {
  kpis: RiskKPIs;
  risk_contributions: RiskContributionItem[];
  correlation: CorrelationMatrix;
  covariance: CovarianceMatrix;
  rolling_volatility: RollingVolPoint[];
  assumptions: Record<string, string>;
}

export interface PortfolioAllocationPoint {
  label: string;
  expected_return: number;
  volatility: number;
  sharpe: number;
  weights: Record<string, number>;
}

export interface FrontierPoint {
  expected_return: number;
  volatility: number;
  sharpe: number;
  weights: Record<string, number>;
}

export interface OptimizationResponse {
  current: PortfolioAllocationPoint;
  min_volatility: PortfolioAllocationPoint;
  max_sharpe: PortfolioAllocationPoint;
  target_portfolio?: PortfolioAllocationPoint;
  frontier: FrontierPoint[];
  individual_assets: PortfolioAllocationPoint[];
  status: string;
  iterations: number;
  assumptions: Record<string, string>;
}

export interface TradeItem {
  ticker: string;
  current_weight: number;
  target_weight: number;
  drift: number;
  drift_status: 'normal' | 'warning' | 'action_required';
  current_value: number;
  target_value: number;
  trade_value: number;
  action: 'BUY' | 'SELL' | 'HOLD';
  priority: number;
  current_price: number;
  estimated_shares: number;
  reason: string;
}

export interface RebalanceSummary {
  rebalance_required: boolean;
  drift_threshold: number;
  assets_outside_threshold: number;
  total_buy_value: number;
  total_sell_value: number;
  total_turnover_value: number;
  estimated_transaction_cost: number;
  transaction_cost_rate: number;
}

export interface RebalanceResponse {
  summary: RebalanceSummary;
  trades: TradeItem[];
  disclaimer: string;
}
