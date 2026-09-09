import React from 'react';
import { MetricCard } from '../common/MetricCard';
import { PlotlyChart } from '../common/PlotlyChart';
import type { PerformanceResponse, PortfolioSummaryResponse, RebalanceResponse, RiskResponse } from '../../types';
import { AlertTriangle, ArrowRight } from 'lucide-react';

interface DashboardOverviewProps {
  summary: PortfolioSummaryResponse | null;
  performance: PerformanceResponse | null;
  risk: RiskResponse | null;
  rebalance: RebalanceResponse | null;
  onNavigateToRebalance: () => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  summary,
  performance,
  risk,
  rebalance,
  onNavigateToRebalance,
}) => {
  if (!summary || !performance) {
    return (
      <div className="p-8 text-center text-slate-400 animate-pulse">
        Loading portfolio analytics...
      </div>
    );
  }

  const kpis = performance.kpis;
  const holdings = summary.holdings;

  // Portfolio vs Benchmark Growth Plotly Data
  const growthData = [
    {
      x: performance.time_series.map((p) => p.date),
      y: performance.time_series.map((p) => p.portfolio_wealth),
      type: 'scatter' as const,
      mode: 'lines' as const,
      name: `${summary.name} ($)`,
      line: { color: '#06b6d4', width: 2.2 },
    },
    {
      x: performance.time_series.map((p) => p.date),
      y: performance.time_series.map((p) => p.benchmark_wealth),
      type: 'scatter' as const,
      mode: 'lines' as const,
      name: `Benchmark: ${summary.benchmark} ($)`,
      line: { color: '#64748b', width: 1.5, dash: 'dot' as const },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Rebalance Warning Banner */}
      {rebalance && rebalance.summary.rebalance_required && (
        <div className="bg-amber-950/40 border border-amber-500/40 rounded-lg p-3.5 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-amber-500/20 text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-amber-200">
                Rebalancing Required — {rebalance.summary.assets_outside_threshold} asset(s) outside drift threshold
              </div>
              <div className="text-xs text-amber-300/80">
                Estimated turnover: ${rebalance.summary.total_turnover_value.toLocaleString()} across{' '}
                {rebalance.trades.filter((t) => t.action !== 'HOLD').length} rebalancing orders.
              </div>
            </div>
          </div>
          <button
            onClick={onNavigateToRebalance}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors shrink-0 cursor-pointer"
          >
            Review Trades <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Top Executive KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          label="Portfolio Value"
          value={`$${summary.current_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          subtext={`Initial: $${summary.initial_capital.toLocaleString()}`}
          highlight="cyan"
          tooltip="Current aggregate market value of all active holdings."
        />
        <MetricCard
          label="Total Return"
          value={`${(kpis.total_return * 100).toFixed(1)}%`}
          trend={kpis.total_return >= 0 ? 'up' : 'down'}
          trendValue={`${kpis.total_return >= 0 ? '+' : ''}${(kpis.total_return * 100).toFixed(1)}%`}
          highlight={kpis.total_return >= 0 ? 'emerald' : 'rose'}
          tooltip="Cumulative portfolio return over the selected date range."
        />
        <MetricCard
          label="CAGR"
          value={`${(kpis.cagr * 100).toFixed(1)}%`}
          subtext="Annualized Growth"
          tooltip="Compound Annual Growth Rate normalized for 252 trading days per year."
        />
        <MetricCard
          label="Sharpe Ratio"
          value={kpis.sharpe_ratio.toFixed(2)}
          subtext={`Bench: ${kpis.benchmark_sharpe.toFixed(2)}`}
          highlight={kpis.sharpe_ratio >= 1.0 ? 'emerald' : 'default'}
          tooltip="Risk-adjusted excess return per unit of total volatility (Rf = 4.0%)."
        />
        <MetricCard
          label="Annual Volatility"
          value={`${(kpis.annualized_volatility * 100).toFixed(1)}%`}
          subtext={`Bench: ${(kpis.benchmark_volatility * 100).toFixed(1)}%`}
          tooltip="Annualized standard deviation of daily simple returns."
        />
        <MetricCard
          label="Max Drawdown"
          value={`${(kpis.max_drawdown * 100).toFixed(1)}%`}
          highlight="rose"
          tooltip="Largest peak-to-trough historical capital decline."
        />
      </div>

      {/* Main Growth Chart Card */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h3 className="text-sm font-semibold text-white">Portfolio Growth vs Benchmark</h3>
            <p className="text-xs text-slate-400">Cumulative wealth progression on $1,000,000 initial capital</p>
          </div>
          <div className="text-xs font-mono text-slate-400">
            Alpha: <span className="text-emerald-400 font-bold">{kpis.alpha >= 0 ? '+' : ''}{(kpis.alpha * 100).toFixed(2)}%</span>
            {' '}| Beta: <span className="text-cyan-400 font-bold">{kpis.beta.toFixed(2)}</span>
          </div>
        </div>
        <div className="h-[340px]">
          <PlotlyChart
            data={growthData}
            layout={{
              yaxis: { title: { text: 'Value ($)' }, tickprefix: '$' },
              xaxis: { title: { text: 'Date' } },
            }}
          />
        </div>
      </div>

      {/* Grid: Allocation & Risk Contribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Allocation vs Target */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Asset Allocation</h3>
              <p className="text-xs text-slate-400">Current Weight vs Target Allocation</p>
            </div>
          </div>
          <div className="space-y-3">
            {holdings.map((h) => {
              const currPct = h.current_weight * 100;
              const targPct = h.target_weight * 100;
              const driftPct = h.drift * 100;
              return (
                <div key={h.ticker} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-white w-12">{h.ticker}</span>
                      <span className="text-slate-400 text-[11px]">${h.market_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                    </div>
                    <div className="flex items-center gap-2 font-mono">
                      <span className="text-slate-200">{currPct.toFixed(1)}%</span>
                      <span className="text-slate-500">/ {targPct.toFixed(1)}%</span>
                      <span
                        className={`text-[11px] font-semibold ${
                          Math.abs(driftPct) > 5 ? 'text-amber-400' : 'text-slate-400'
                        }`}
                      >
                        ({driftPct >= 0 ? '+' : ''}{driftPct.toFixed(1)}%)
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden flex">
                    <div
                      className="bg-cyan-500 h-full rounded-full transition-all"
                      style={{ width: `${Math.min(100, currPct)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Risk Contribution */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-sm font-semibold text-white">Risk Contribution Decomposition</h3>
              <p className="text-xs text-slate-400">Component share of total portfolio volatility (sums to 100%)</p>
            </div>
          </div>
          {risk ? (
            <div className="space-y-3">
              {risk.risk_contributions.map((rc) => {
                const prcPct = rc.percentage_risk_contribution * 100;
                return (
                  <div key={rc.ticker} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-white w-12">{rc.ticker}</span>
                        <span className="text-slate-400 text-[11px]">Weight: {(rc.weight * 100).toFixed(1)}%</span>
                      </div>
                      <div className="font-mono text-cyan-300 font-semibold">{prcPct.toFixed(1)}% Risk</div>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(100, Math.max(0, prcPct))}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-xs text-slate-500 py-8 text-center">Loading risk breakdown...</div>
          )}
        </div>
      </div>
    </div>
  );
};
