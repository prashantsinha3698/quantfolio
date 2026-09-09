import React, { useState } from 'react';
import { PlotlyChart } from '../common/PlotlyChart';
import type { OptimizationResponse, PortfolioRequest } from '../../types';
import { portfolioApi } from '../../services/api';
import { Sliders, Play, CheckCircle2, AlertCircle } from 'lucide-react';

interface OptimizationViewProps {
  currentPortfolio: PortfolioRequest;
  optimization: OptimizationResponse | null;
  onOptimizationUpdated: (result: OptimizationResponse) => void;
}

export const OptimizationView: React.FC<OptimizationViewProps> = ({
  currentPortfolio,
  optimization,
  onOptimizationUpdated,
}) => {
  const [riskFreeRate, setRiskFreeRate] = useState(0.04);
  const [minWeight, setMinWeight] = useState(0.0);
  const [maxWeight, setMaxWeight] = useState(0.5);
  const [expectedReturnMethod, setExpectedReturnMethod] = useState('historical_mean');
  const [isRunning, setIsRunning] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleRunOptimization = async () => {
    setIsRunning(true);
    setErrorMsg(null);
    try {
      const res = await portfolioApi.runOptimization(currentPortfolio, {
        risk_free_rate: riskFreeRate,
        min_weight: minWeight,
        max_weight: maxWeight,
        expected_return_method: expectedReturnMethod,
        frontier_points_count: 35,
      });
      onOptimizationUpdated(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Optimization solver failed');
    } finally {
      setIsRunning(false);
    }
  };

  if (!optimization) {
    return <div className="p-8 text-center text-slate-400">Loading optimization workstation...</div>;
  }

  // Efficient Frontier Plotly Series
  const frontier = optimization.frontier;
  const current = optimization.current;
  const minVol = optimization.min_volatility;
  const maxSharpe = optimization.max_sharpe;
  const individualAssets = optimization.individual_assets;

  const frontierPlotData: Plotly.Data[] = [
    // 1. Frontier line
    {
      x: frontier.map((p) => p.volatility * 100),
      y: frontier.map((p) => p.expected_return * 100),
      type: 'scatter',
      mode: 'lines',
      name: 'Efficient Frontier',
      line: { color: '#06b6d4', width: 2.5 },
    },
    // 2. Individual Assets
    {
      x: individualAssets.map((a) => a.volatility * 100),
      y: individualAssets.map((a) => a.expected_return * 100),
      text: individualAssets.map((a) => a.label),
      type: 'scatter',
      mode: 'markers+text',
      textposition: 'top center',
      name: 'Individual Assets',
      marker: { color: '#64748b', size: 8 },
    },
    // 3. Current Portfolio
    {
      x: [current.volatility * 100],
      y: [current.expected_return * 100],
      type: 'scatter',
      mode: 'markers',
      name: 'Current Portfolio',
      marker: { color: '#38bdf8', size: 14, symbol: 'diamond' },
    },
    // 4. Minimum Volatility
    {
      x: [minVol.volatility * 100],
      y: [minVol.expected_return * 100],
      type: 'scatter',
      mode: 'markers',
      name: 'Minimum Volatility',
      marker: { color: '#10b981', size: 14, symbol: 'circle' },
    },
    // 5. Maximum Sharpe
    {
      x: [maxSharpe.volatility * 100],
      y: [maxSharpe.expected_return * 100],
      type: 'scatter',
      mode: 'markers',
      name: 'Maximum Sharpe',
      marker: { color: '#a855f7', size: 16, symbol: 'star' },
    },
  ];

  const tickers = Object.keys(current.weights);

  return (
    <div className="space-y-6">
      {/* Research Workstation Header & Parameter Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Controls Sidebar */}
        <div className="bg-terminal-card border border-terminal-border rounded-lg p-4 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-white border-b border-terminal-border pb-2.5">
            <Sliders className="w-4 h-4 text-cyan-400" />
            Optimization Parameters
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1">Expected Return Model</label>
              <select
                value={expectedReturnMethod}
                onChange={(e) => setExpectedReturnMethod(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1.5 focus:border-cyan-500 focus:outline-none"
              >
                <option value="historical_mean">Historical Annualized Mean</option>
                <option value="capm">CAPM Risk-Adjusted Model</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Risk-Free Rate (Rf)</label>
              <input
                type="number"
                step="0.005"
                min="0"
                max="0.15"
                value={riskFreeRate}
                onChange={(e) => setRiskFreeRate(parseFloat(e.target.value) || 0)}
                className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1.5 font-mono focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-slate-400 mb-1">Min Weight</label>
                <input
                  type="number"
                  step="0.05"
                  min="0"
                  max="0.5"
                  value={minWeight}
                  onChange={(e) => setMinWeight(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1.5 font-mono focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-slate-400 mb-1">Max Weight</label>
                <input
                  type="number"
                  step="0.05"
                  min="0.2"
                  max="1.0"
                  value={maxWeight}
                  onChange={(e) => setMaxWeight(parseFloat(e.target.value) || 1)}
                  className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded px-2.5 py-1.5 font-mono focus:border-cyan-500 focus:outline-none"
                />
              </div>
            </div>

            <button
              onClick={handleRunOptimization}
              disabled={isRunning}
              className="w-full mt-2 flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-600 to-emerald-600 hover:from-cyan-500 hover:to-emerald-500 text-white font-semibold py-2 px-4 rounded transition-all shadow-md active:scale-98 disabled:opacity-50 cursor-pointer"
            >
              <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : ''}`} />
              {isRunning ? 'Optimizing SLSQP...' : 'Run Optimization'}
            </button>

            {errorMsg && (
              <div className="flex items-center gap-1.5 text-xs text-rose-400 bg-rose-950/40 border border-rose-800 p-2 rounded">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </div>
        </div>

        {/* Efficient Frontier Chart Area */}
        <div className="lg:col-span-3 bg-terminal-card border border-terminal-border rounded-lg p-4">
          <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
            <div>
              <h3 className="text-sm font-semibold text-white">Markowitz Efficient Frontier</h3>
              <p className="text-xs text-slate-400">Risk/return Pareto optimal allocations solved via SciPy SLSQP</p>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Solved: {optimization.status}</span>
            </div>
          </div>
          <div className="h-[340px]">
            <PlotlyChart
              data={frontierPlotData}
              layout={{
                xaxis: { title: { text: 'Annualized Volatility (%)' }, ticksuffix: '%' },
                yaxis: { title: { text: 'Expected Return (%)' }, ticksuffix: '%' },
              }}
            />
          </div>
        </div>
      </div>

      {/* Side-by-Side Allocation Comparison Table */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="mb-3">
          <h3 className="text-sm font-semibold text-white">Portfolio Allocation Comparison</h3>
          <p className="text-xs text-slate-400">Current holdings vs Minimum Volatility vs Maximum Sharpe alternatives</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-900/80 text-slate-400 border-b border-terminal-border">
              <tr>
                <th className="py-2.5 px-3">Metric / Asset</th>
                <th className="py-2.5 px-3 text-right">Current Portfolio</th>
                <th className="py-2.5 px-3 text-right text-emerald-400 font-bold">Min Volatility</th>
                <th className="py-2.5 px-3 text-right text-purple-400 font-bold">Max Sharpe</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr className="bg-slate-900/20 font-bold">
                <td className="py-2 px-3 text-slate-300 font-sans">Expected Annual Return</td>
                <td className="py-2 px-3 text-right">{(current.expected_return * 100).toFixed(2)}%</td>
                <td className="py-2 px-3 text-right text-emerald-400">{(minVol.expected_return * 100).toFixed(2)}%</td>
                <td className="py-2 px-3 text-right text-purple-400">{(maxSharpe.expected_return * 100).toFixed(2)}%</td>
              </tr>
              <tr className="bg-slate-900/20 font-bold">
                <td className="py-2 px-3 text-slate-300 font-sans">Annualized Volatility</td>
                <td className="py-2 px-3 text-right">{(current.volatility * 100).toFixed(2)}%</td>
                <td className="py-2 px-3 text-right text-emerald-400">{(minVol.volatility * 100).toFixed(2)}%</td>
                <td className="py-2 px-3 text-right text-purple-400">{(maxSharpe.volatility * 100).toFixed(2)}%</td>
              </tr>
              <tr className="bg-slate-900/20 font-bold border-b border-slate-700">
                <td className="py-2 px-3 text-slate-300 font-sans">Sharpe Ratio</td>
                <td className="py-2 px-3 text-right">{current.sharpe.toFixed(2)}</td>
                <td className="py-2 px-3 text-right text-emerald-400">{minVol.sharpe.toFixed(2)}</td>
                <td className="py-2 px-3 text-right text-purple-400">{maxSharpe.sharpe.toFixed(2)}</td>
              </tr>

              {/* Per-Asset Weights */}
              {tickers.map((ticker) => {
                const currW = (current.weights[ticker] || 0) * 100;
                const minVolW = (minVol.weights[ticker] || 0) * 100;
                const maxSharpeW = (maxSharpe.weights[ticker] || 0) * 100;

                return (
                  <tr key={ticker} className="hover:bg-slate-900/40">
                    <td className="py-2 px-3 font-bold text-white">{ticker}</td>
                    <td className="py-2 px-3 text-right text-slate-300">{currW.toFixed(1)}%</td>
                    <td className="py-2 px-3 text-right text-emerald-300">{minVolW.toFixed(1)}%</td>
                    <td className="py-2 px-3 text-right text-purple-300">{maxSharpeW.toFixed(1)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
