import React, { useState } from 'react';
import { MetricCard } from '../common/MetricCard';
import type { PortfolioSummaryResponse, RiskResponse } from '../../types';

interface AssetDetailViewProps {
  summary: PortfolioSummaryResponse | null;
  risk: RiskResponse | null;
}

export const AssetDetailView: React.FC<AssetDetailViewProps> = ({ summary, risk }) => {
  const [selectedTicker, setSelectedTicker] = useState<string>(
    summary?.holdings[0]?.ticker || 'SPY'
  );

  if (!summary) {
    return <div className="p-8 text-center text-slate-400">Loading asset details...</div>;
  }

  const holdings = summary.holdings;
  const currentHolding = holdings.find((h) => h.ticker === selectedTicker) || holdings[0];

  const riskContrib = risk?.risk_contributions.find((r) => r.ticker === selectedTicker);

  // Correlation with other assets
  let correlationRows: { ticker: string; correlation: number }[] = [];
  if (risk) {
    const assetIdx = risk.correlation.tickers.indexOf(selectedTicker);
    if (assetIdx !== -1) {
      correlationRows = risk.correlation.tickers.map((ticker, idx) => ({
        ticker,
        correlation: risk.correlation.matrix[assetIdx][idx],
      }));
    }
  }

  return (
    <div className="space-y-6">
      {/* Asset Selector Pills */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 bg-terminal-card border border-terminal-border rounded-lg">
        {holdings.map((h) => (
          <button
            key={h.ticker}
            onClick={() => setSelectedTicker(h.ticker)}
            className={`px-3 py-1.5 rounded text-xs font-mono font-bold transition-all cursor-pointer ${
              selectedTicker === h.ticker
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            {h.ticker}
          </button>
        ))}
      </div>

      {/* Selected Asset Header & Key Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          label="Current Price"
          value={`$${currentHolding.current_price.toFixed(2)}`}
          subtext="Per Share (USD)"
          highlight="cyan"
        />
        <MetricCard
          label="Position Value"
          value={`$${currentHolding.market_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
          subtext={`${currentHolding.quantity.toLocaleString()} Shares`}
        />
        <MetricCard
          label="Current Weight"
          value={`${(currentHolding.current_weight * 100).toFixed(1)}%`}
          subtext={`Target: ${(currentHolding.target_weight * 100).toFixed(1)}%`}
        />
        <MetricCard
          label="Allocation Drift"
          value={`${currentHolding.drift >= 0 ? '+' : ''}${(currentHolding.drift * 100).toFixed(1)}%`}
          highlight={Math.abs(currentHolding.drift) > 0.05 ? 'amber' : 'default'}
        />
        <MetricCard
          label="Risk Contribution"
          value={riskContrib ? `${(riskContrib.percentage_risk_contribution * 100).toFixed(1)}%` : '—'}
          subtext="Share of Volatility"
          highlight="emerald"
        />
        <MetricCard
          label="Marginal Risk"
          value={riskContrib ? `${riskContrib.marginal_risk_contribution.toFixed(3)}` : '—'}
          subtext="d(Sigma)/d(Weight)"
        />
      </div>

      {/* Correlation with Other Portfolio Assets */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-white">
            {selectedTicker} Correlation with Portfolio Holdings
          </h3>
          <p className="text-xs text-slate-400">Linear co-movement coefficient with peer assets</p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {correlationRows.map((item) => (
            <div
              key={item.ticker}
              className={`p-3 rounded border text-center font-mono ${
                item.ticker === selectedTicker
                  ? 'bg-slate-900/80 border-slate-700'
                  : 'bg-terminal-subtle border-terminal-border'
              }`}
            >
              <div className="text-xs font-bold text-slate-300">{item.ticker}</div>
              <div
                className={`text-sm font-bold mt-1 ${
                  item.correlation > 0.6
                    ? 'text-cyan-400'
                    : item.correlation < 0
                    ? 'text-rose-400'
                    : 'text-slate-200'
                }`}
              >
                {item.correlation.toFixed(2)}
              </div>
              <div className="text-[10px] text-slate-500 font-sans mt-0.5">
                {item.correlation > 0.7
                  ? 'Strong Positive'
                  : item.correlation < 0
                  ? 'Diversifier'
                  : 'Moderate'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
