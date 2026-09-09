import React from 'react';
import { MetricCard } from '../common/MetricCard';
import { PlotlyChart } from '../common/PlotlyChart';
import { RiskResponse } from '../../types';
import { Info } from 'lucide-react';

interface RiskViewProps {
  risk: RiskResponse | null;
}

export const RiskView: React.FC<RiskViewProps> = ({ risk }) => {
  if (!risk) {
    return <div className="p-8 text-center text-slate-400">Loading risk analytics...</div>;
  }

  const kpis = risk.kpis;

  // Correlation Heatmap Plotly Data
  const heatmapData: Plotly.Data[] = [
    {
      z: risk.correlation.matrix,
      x: risk.correlation.tickers,
      y: risk.correlation.tickers,
      type: 'heatmap',
      colorscale: [
        [0.0, '#1e3a8a'],  // Blue for negative correlation
        [0.5, '#0f172a'],  // Dark for zero
        [1.0, '#06b6d4'],  // Cyan for high correlation
      ],
      zmin: -0.5,
      zmax: 1.0,
      hoverongaps: false,
    },
  ];

  // Risk Contribution Horizontal Bar Data
  const rcData: Plotly.Data[] = [
    {
      y: risk.risk_contributions.map((r) => r.ticker),
      x: risk.risk_contributions.map((r) => r.weight * 100),
      type: 'bar',
      name: 'Portfolio Weight (%)',
      orientation: 'h',
      marker: { color: '#334155' },
    },
    {
      y: risk.risk_contributions.map((r) => r.ticker),
      x: risk.risk_contributions.map((r) => r.percentage_risk_contribution * 100),
      type: 'bar',
      name: 'Risk Contribution (%)',
      orientation: 'h',
      marker: { color: '#06b6d4' },
    },
  ];

  // Rolling Multi-Horizon Volatility Data
  const validRolling = risk.rolling_volatility.filter((p) => p.vol_60d !== null);
  const rollingVolData: Plotly.Data[] = [
    {
      x: validRolling.map((p) => p.date),
      y: validRolling.map((p) => (p.vol_20d ? p.vol_20d * 100 : null)),
      type: 'scatter',
      mode: 'lines',
      name: '20-Day Vol (%)',
      line: { color: '#f59e0b', width: 1.2 },
    },
    {
      x: validRolling.map((p) => p.date),
      y: validRolling.map((p) => (p.vol_60d ? p.vol_60d * 100 : null)),
      type: 'scatter',
      mode: 'lines',
      name: '60-Day Vol (%)',
      line: { color: '#06b6d4', width: 1.8 },
    },
    {
      x: validRolling.map((p) => p.date),
      y: validRolling.map((p) => (p.vol_252d ? p.vol_252d * 100 : null)),
      type: 'scatter',
      mode: 'lines',
      name: '252-Day Vol (%)',
      line: { color: '#8b5cf6', width: 1.5, dash: 'dot' },
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Risk KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          label="95% Hist. VaR (1-Day)"
          value={`$${kpis.historical_var_95_dollar.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          subtext={`${(kpis.historical_var_95 * 100).toFixed(2)}% of capital`}
          highlight="amber"
          tooltip="Estimated 1-day threshold loss exceeded on only 5% of historical trading days."
        />
        <MetricCard
          label="95% Hist. CVaR"
          value={`$${kpis.historical_cvar_95_dollar.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          subtext={`${(kpis.historical_cvar_95 * 100).toFixed(2)}% Expected Shortfall`}
          highlight="rose"
          tooltip="Expected average loss on days when the loss breaches the 95% VaR threshold."
        />
        <MetricCard
          label="99% Hist. VaR (1-Day)"
          value={`$${kpis.historical_var_99_dollar.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          subtext={`${(kpis.historical_var_99 * 100).toFixed(2)}% of capital`}
          tooltip="Estimated 1-day threshold loss at 99% confidence level."
        />
        <MetricCard
          label="95% Parametric VaR"
          value={`$${kpis.parametric_var_95_dollar.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          subtext={`${(kpis.parametric_var_95 * 100).toFixed(2)}% (Normal Model)`}
          tooltip="Variance-covariance VaR assuming normally distributed returns."
        />
        <MetricCard
          label="Portfolio Beta"
          value={kpis.beta.toFixed(2)}
          subtext="Benchmark Sensitivity"
          tooltip="Covariance with benchmark divided by benchmark variance."
        />
        <MetricCard
          label="Tracking Error"
          value={`${(kpis.tracking_error * 100).toFixed(2)}%`}
          subtext="Annualized Dispersion"
          tooltip="Standard deviation of excess returns relative to benchmark."
        />
      </div>

      {/* Correlation Heatmap & Risk Contribution Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Correlation Heatmap */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
          <div className="mb-2">
            <h3 className="text-sm font-semibold text-white">Asset Correlation Matrix</h3>
            <p className="text-xs text-slate-400">Pairwise Pearson correlation between portfolio assets</p>
          </div>
          <div className="h-[280px]">
            <PlotlyChart
              data={heatmapData}
              layout={{
                margin: { l: 50, r: 20, t: 20, b: 50 },
              }}
            />
          </div>
        </div>

        {/* Risk Contribution vs Weight */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
          <div className="mb-2">
            <h3 className="text-sm font-semibold text-white">Risk Contribution vs Allocation</h3>
            <p className="text-xs text-slate-400">Comparing asset portfolio weight with its component risk contribution</p>
          </div>
          <div className="h-[280px]">
            <PlotlyChart
              data={rcData}
              layout={{
                barmode: 'group',
                xaxis: { title: { text: 'Percentage (%)' }, ticksuffix: '%' },
                margin: { l: 60, r: 20, t: 20, b: 40 },
              }}
            />
          </div>
        </div>
      </div>

      {/* Multi-Horizon Rolling Volatility */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="mb-2">
          <h3 className="text-sm font-semibold text-white">Multi-Horizon Rolling Volatility</h3>
          <p className="text-xs text-slate-400">20-day, 60-day, and 252-day annualized volatility regimes</p>
        </div>
        <div className="h-[260px]">
          <PlotlyChart
            data={rollingVolData}
            layout={{
              yaxis: { title: { text: 'Volatility (%)' }, ticksuffix: '%' },
              xaxis: { title: { text: 'Date' } },
            }}
          />
        </div>
      </div>

      {/* Methodological Transparency Note */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4 flex gap-3.5">
        <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
          <div className="font-semibold text-white">Risk Model Assumptions & Interpretations</div>
          <p>
            • <strong>Historical VaR:</strong> Computed empirically from sorted sample returns without assuming a normal distribution. Captures fat tails and skewness.
          </p>
          <p>
            • <strong>Parametric VaR:</strong> Assumes a standard Gaussian distribution ($Z_{0.05} = -1.645$). Useful as an analytical baseline, but can underestimate extreme tail events.
          </p>
          <p>
            • <strong>Expected Shortfall (CVaR):</strong> A sub-additive coherent risk measure averaging losses beyond the VaR threshold, answering: <em>"If a tail loss occurs, how severe is the average loss?"</em>
          </p>
        </div>
      </div>
    </div>
  );
};
