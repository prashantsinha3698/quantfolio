import React, { useState } from 'react';
import { MetricCard } from '../common/MetricCard';
import { PlotlyChart } from '../common/PlotlyChart';
import type { PerformanceResponse } from '../../types';

interface PerformanceViewProps {
  performance: PerformanceResponse | null;
}

export const PerformanceView: React.FC<PerformanceViewProps> = ({ performance }) => {
  const [showBenchmark, setShowBenchmark] = useState(true);

  if (!performance) {
    return <div className="p-8 text-center text-slate-400">Loading performance data...</div>;
  }

  const kpis = performance.kpis;
  const ts = performance.time_series;

  // Cumulative Return Growth Chart
  const growthData: Plotly.Data[] = [
    {
      x: ts.map((p) => p.date),
      y: ts.map((p) => (p.portfolio_wealth / ts[0].portfolio_wealth - 1) * 100),
      type: 'scatter',
      mode: 'lines',
      name: 'Portfolio Return (%)',
      line: { color: '#06b6d4', width: 2.5 },
    },
  ];

  if (showBenchmark) {
    growthData.push({
      x: ts.map((p) => p.date),
      y: ts.map((p) => (p.benchmark_wealth / ts[0].benchmark_wealth - 1) * 100),
      type: 'scatter',
      mode: 'lines',
      name: 'Benchmark Return (%)',
      line: { color: '#94a3b8', width: 1.5, dash: 'dot' },
    });
  }

  // Drawdown Underwater Chart
  const drawdownData: Plotly.Data[] = [
    {
      x: ts.map((p) => p.date),
      y: ts.map((p) => p.portfolio_drawdown * 100),
      type: 'scatter',
      mode: 'lines',
      name: 'Drawdown (%)',
      fill: 'tozeroy',
      fillcolor: 'rgba(244, 63, 94, 0.15)',
      line: { color: '#f43f5e', width: 1.8 },
    },
  ];

  // Rolling Volatility Chart
  const rollingVolData: Plotly.Data[] = [
    {
      x: performance.rolling_metrics.map((p) => p.date),
      y: performance.rolling_metrics.map((p) => p.portfolio_vol * 100),
      type: 'scatter',
      mode: 'lines',
      name: 'Portfolio 60D Vol (%)',
      line: { color: '#10b981', width: 2 },
    },
    {
      x: performance.rolling_metrics.map((p) => p.date),
      y: performance.rolling_metrics.map((p) => p.benchmark_vol * 100),
      type: 'scatter',
      mode: 'lines',
      name: 'Benchmark 60D Vol (%)',
      line: { color: '#64748b', width: 1.5, dash: 'dash' },
    },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <MetricCard
          label="Total Return"
          value={`${(kpis.total_return * 100).toFixed(1)}%`}
          highlight={kpis.total_return >= 0 ? 'emerald' : 'rose'}
          trend={kpis.total_return >= 0 ? 'up' : 'down'}
          trendValue={`${(kpis.total_return * 100).toFixed(1)}%`}
        />
        <MetricCard
          label="CAGR"
          value={`${(kpis.cagr * 100).toFixed(1)}%`}
          subtext="Annualized Return"
        />
        <MetricCard
          label="Volatility"
          value={`${(kpis.annualized_volatility * 100).toFixed(1)}%`}
          subtext="Annualized StDev"
        />
        <MetricCard
          label="Sharpe Ratio"
          value={kpis.sharpe_ratio.toFixed(2)}
          highlight="cyan"
          subtext="Rf = 4.0%"
        />
        <MetricCard
          label="Sortino Ratio"
          value={kpis.sortino_ratio.toFixed(2)}
          subtext="Downside Risk Adjusted"
        />
        <MetricCard
          label="Max Drawdown"
          value={`${(kpis.max_drawdown * 100).toFixed(1)}%`}
          highlight="rose"
          subtext="Peak-to-Trough Loss"
        />
        <MetricCard
          label="Calmar Ratio"
          value={kpis.calmar_ratio.toFixed(2)}
          subtext="CAGR / |MDD|"
        />
      </div>

      {/* Main Cumulative Growth Chart */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div>
            <h3 className="text-sm font-semibold text-white">Cumulative Return (% Growth)</h3>
            <p className="text-xs text-slate-400">Total return trajectory against benchmark</p>
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-1.5 text-xs text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={showBenchmark}
                onChange={(e) => setShowBenchmark(e.target.checked)}
                className="rounded border-slate-700 text-cyan-500 focus:ring-0 cursor-pointer"
              />
              Show Benchmark
            </label>
          </div>
        </div>
        <div className="h-[320px]">
          <PlotlyChart
            data={growthData}
            layout={{
              yaxis: { title: { text: 'Cumulative Return (%)' }, ticksuffix: '%' },
              xaxis: { title: { text: 'Date' } },
            }}
          />
        </div>
      </div>

      {/* Drawdown & Rolling Volatility Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Underwater Drawdown */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-white mb-1">Underwater Drawdown</h3>
          <p className="text-xs text-slate-400 mb-2">Historical decline from previous high-water mark</p>
          <div className="h-[240px]">
            <PlotlyChart
              data={drawdownData}
              layout={{
                yaxis: { title: { text: 'Drawdown (%)' }, ticksuffix: '%', range: [Math.min(kpis.max_drawdown * 100 * 1.1, -5), 1] },
              }}
            />
          </div>
        </div>

        {/* Rolling Volatility */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-white mb-1">Rolling 60-Day Annualized Volatility</h3>
          <p className="text-xs text-slate-400 mb-2">Dynamic risk regimes over time</p>
          <div className="h-[240px]">
            <PlotlyChart
              data={rollingVolData}
              layout={{
                yaxis: { title: { text: 'Volatility (%)' }, ticksuffix: '%' },
              }}
            />
          </div>
        </div>
      </div>

      {/* Major Drawdown Events Table */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-white">Historical Drawdown Events</h3>
          <p className="text-xs text-slate-400">Deepest historical declines with peak, trough, and recovery periods</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 font-mono border-b border-terminal-border">
              <tr>
                <th className="py-2.5 px-3">#</th>
                <th className="py-2.5 px-3">Peak Date</th>
                <th className="py-2.5 px-3">Trough Date</th>
                <th className="py-2.5 px-3">Recovery Date</th>
                <th className="py-2.5 px-3 text-right">Magnitude</th>
                <th className="py-2.5 px-3 text-right">Duration (Days)</th>
                <th className="py-2.5 px-3 text-right">Recovery (Days)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {performance.major_drawdowns.map((event, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-2.5 px-3 text-slate-500 font-bold">{idx + 1}</td>
                  <td className="py-2.5 px-3 text-slate-200">{event.peak_date}</td>
                  <td className="py-2.5 px-3 text-rose-300">{event.trough_date}</td>
                  <td className="py-2.5 px-3 text-emerald-400">
                    {event.recovery_date || <span className="text-amber-400 font-sans italic">In Progress</span>}
                  </td>
                  <td className="py-2.5 px-3 text-right font-bold text-rose-400">
                    {(event.magnitude * 100).toFixed(2)}%
                  </td>
                  <td className="py-2.5 px-3 text-right text-slate-300">{event.duration_days} d</td>
                  <td className="py-2.5 px-3 text-right text-slate-400">
                    {event.recovery_days ? `${event.recovery_days} d` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
