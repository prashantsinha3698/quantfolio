import React from 'react';
import { MetricCard } from '../common/MetricCard';
import { PlotlyChart } from '../common/PlotlyChart';
import type { RebalanceResponse } from '../../types';
import { AlertTriangle, CheckCircle, ArrowDownRight, ArrowUpRight, Minus, AlertOctagon } from 'lucide-react';

interface RebalanceViewProps {
  rebalance: RebalanceResponse | null;
}

export const RebalanceView: React.FC<RebalanceViewProps> = ({ rebalance }) => {
  if (!rebalance) {
    return <div className="p-8 text-center text-slate-400">Loading rebalancing analysis...</div>;
  }

  const { summary, trades, disclaimer } = rebalance;

  // Grouped Bar Chart: Current vs Target
  const chartData: Plotly.Data[] = [
    {
      x: trades.map((t) => t.ticker),
      y: trades.map((t) => t.current_weight * 100),
      name: 'Current Allocation (%)',
      type: 'bar',
      marker: { color: '#3b82f6' },
    },
    {
      x: trades.map((t) => t.ticker),
      y: trades.map((t) => t.target_weight * 100),
      name: 'Target Allocation (%)',
      type: 'bar',
      marker: { color: '#06b6d4' },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Rebalance Status Header */}
      <div
        className={`p-4 rounded-lg border flex flex-wrap items-center justify-between gap-4 ${
          summary.rebalance_required
            ? 'bg-amber-950/30 border-amber-500/40 text-amber-200'
            : 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200'
        }`}
      >
        <div className="flex items-center gap-3">
          <div
            className={`p-2.5 rounded-md ${
              summary.rebalance_required ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'
            }`}
          >
            {summary.rebalance_required ? (
              <AlertTriangle className="w-6 h-6" />
            ) : (
              <CheckCircle className="w-6 h-6" />
            )}
          </div>
          <div>
            <h2 className="text-base font-bold text-white">
              {summary.rebalance_required ? 'Rebalancing Action Recommended' : 'Portfolio Within Drift Tolerance'}
            </h2>
            <p className="text-xs text-slate-300">
              {summary.rebalance_required
                ? `${summary.assets_outside_threshold} asset(s) exceed the ${(summary.drift_threshold * 100).toFixed(1)}% absolute drift threshold.`
                : `All assets remain within the ${(summary.drift_threshold * 100).toFixed(1)}% drift threshold.`}
            </p>
          </div>
        </div>

        <div className="text-right text-xs font-mono">
          <div className="text-slate-400">Total Trade Turnover</div>
          <div className="text-base font-bold text-white">
            ${summary.total_turnover_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricCard
          label="Drift Threshold"
          value={`${(summary.drift_threshold * 100).toFixed(1)}%`}
          subtext="Tolerance Window"
        />
        <MetricCard
          label="Breached Assets"
          value={summary.assets_outside_threshold}
          highlight={summary.assets_outside_threshold > 0 ? 'amber' : 'emerald'}
          subtext="Need Rebalancing"
        />
        <MetricCard
          label="Estimated Buys"
          value={`$${summary.total_buy_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          highlight="emerald"
        />
        <MetricCard
          label="Estimated Sells"
          value={`$${summary.total_sell_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          highlight="rose"
        />
      </div>

      {/* Current vs Target Allocation Comparison Chart */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="mb-2">
          <h3 className="text-sm font-semibold text-white">Current vs Target Allocation Drift</h3>
          <p className="text-xs text-slate-400">Comparison of active weights versus target mandate</p>
        </div>
        <div className="h-[260px]">
          <PlotlyChart
            data={chartData}
            layout={{
              barmode: 'group',
              yaxis: { title: { text: 'Allocation (%)' }, ticksuffix: '%' },
            }}
          />
        </div>
      </div>

      {/* Actionable Trade Recommendations Table */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-white">Actionable Trade Recommendations</h3>
          <p className="text-xs text-slate-400">Ranked by absolute allocation drift and transaction magnitude</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-terminal-border">
              <tr>
                <th className="py-2.5 px-3">Priority</th>
                <th className="py-2.5 px-3">Asset</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3 text-right">Current %</th>
                <th className="py-2.5 px-3 text-right">Target %</th>
                <th className="py-2.5 px-3 text-right">Drift</th>
                <th className="py-2.5 px-3 text-right">Trade Value ($)</th>
                <th className="py-2.5 px-3 text-right">Est. Shares</th>
                <th className="py-2.5 px-3 font-sans">Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {trades.map((trade) => {
                const isBuy = trade.action === 'BUY';
                const isSell = trade.action === 'SELL';
                const isHold = trade.action === 'HOLD';

                return (
                  <tr key={trade.ticker} className="hover:bg-slate-900/40 transition-colors">
                    <td className="py-2.5 px-3 text-slate-500 font-bold">#{trade.priority}</td>
                    <td className="py-2.5 px-3 font-bold text-white">{trade.ticker}</td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold ${
                          isBuy
                            ? 'bg-emerald-950/60 border border-emerald-600 text-emerald-400'
                            : isSell
                            ? 'bg-rose-950/60 border border-rose-600 text-rose-400'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {isBuy && <ArrowUpRight className="w-3.5 h-3.5" />}
                        {isSell && <ArrowDownRight className="w-3.5 h-3.5" />}
                        {isHold && <Minus className="w-3.5 h-3.5" />}
                        {trade.action}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-300">{(trade.current_weight * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 text-right text-slate-400">{(trade.target_weight * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 text-right">
                      <span
                        className={`font-bold ${
                          trade.drift_status === 'action_required'
                            ? 'text-amber-400'
                            : trade.drift_status === 'warning'
                            ? 'text-amber-300/70'
                            : 'text-slate-400'
                        }`}
                      >
                        {trade.drift >= 0 ? '+' : ''}{(trade.drift * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td
                      className={`py-2.5 px-3 text-right font-bold ${
                        isBuy ? 'text-emerald-400' : isSell ? 'text-rose-400' : 'text-slate-400'
                      }`}
                    >
                      {trade.trade_value >= 0 ? '+' : '-'}${Math.abs(trade.trade_value).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-200">
                      {trade.estimated_shares > 0 ? trade.estimated_shares.toLocaleString() : '—'}
                    </td>
                    <td className="py-2.5 px-3 font-sans text-slate-300 text-[11px]">{trade.reason}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Financial Disclaimer */}
      <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-md text-[11px] text-slate-500 flex items-center gap-2">
        <AlertOctagon className="w-4 h-4 shrink-0 text-slate-600" />
        <span>{disclaimer}</span>
      </div>
    </div>
  );
};
