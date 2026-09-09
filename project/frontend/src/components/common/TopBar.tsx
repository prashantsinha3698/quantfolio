import React from 'react';
import { RefreshCw, Sliders } from 'lucide-react';
import type { PortfolioRequest, PortfolioSummaryResponse } from '../../types';

interface TopBarProps {
  currentPortfolio: PortfolioRequest;
  portfolioSummary: PortfolioSummaryResponse | null;
  presets: Record<string, PortfolioRequest>;
  selectedPresetKey: string;
  onSelectPreset: (key: string) => void;
  onSelectDateRange: (range: string) => void;
  onRefresh: () => void;
  isLoading: boolean;
  onOpenSettings: () => void;
}

const DATE_RANGES = ['1M', '3M', '6M', 'YTD', '1Y', '3Y', '5Y', 'MAX'];

export const TopBar: React.FC<TopBarProps> = ({
  currentPortfolio,
  portfolioSummary,
  presets,
  selectedPresetKey,
  onSelectPreset,
  onSelectDateRange,
  onRefresh,
  isLoading,
  onOpenSettings,
}) => {
  return (
    <header className="bg-terminal-subtle border-b border-terminal-border px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 sticky top-0 z-40">
      {/* Left: Product branding & Portfolio Preset Selector */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-gradient-to-tr from-cyan-600 to-emerald-500 flex items-center justify-center shadow-inner">
            <span className="text-white font-bold text-sm tracking-wider font-mono">QP</span>
          </div>
          <div>
            <div className="text-sm font-bold text-white tracking-wide flex items-center gap-1.5">
              QUANTFOLIO
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-cyan-950/60 border border-cyan-800 text-cyan-400">
                PRO
              </span>
            </div>
            <div className="text-[10px] text-slate-400">Analytics & Risk Terminal</div>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-800 hidden sm:block" />

        {/* Portfolio Selector dropdown */}
        <div className="flex items-center gap-1.5">
          <label className="text-xs text-slate-400 hidden md:inline">Portfolio:</label>
          <select
            value={selectedPresetKey}
            onChange={(e) => onSelectPreset(e.target.value)}
            className="bg-terminal-card border border-terminal-border text-xs text-slate-200 rounded px-2.5 py-1.5 font-medium hover:border-slate-600 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            {Object.keys(presets).map((key) => (
              <option key={key} value={key}>
                {presets[key].name} ({presets[key].holdings.map((h) => h.ticker).join(', ')})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Center/Right: Date range toggles, Data Status, Refresh */}
      <div className="flex items-center flex-wrap gap-2 sm:gap-3 ml-auto">
        {/* Date Range Selector Pills */}
        <div className="flex items-center bg-terminal-card border border-terminal-border rounded p-0.5">
          {DATE_RANGES.map((range) => {
            const active = (currentPortfolio.date_range || '1Y') === range;
            return (
              <button
                key={range}
                onClick={() => onSelectDateRange(range)}
                className={`text-[11px] font-mono px-2 py-1 rounded transition-colors ${
                  active
                    ? 'bg-cyan-600/30 text-cyan-300 font-bold border border-cyan-500/40'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {range}
              </button>
            );
          })}
        </div>

        {/* Data Source Status Badge */}
        {portfolioSummary && (
          <div className="hidden lg:flex items-center gap-1.5 text-xs px-2.5 py-1 rounded bg-terminal-card border border-terminal-border">
            <span
              className={`w-2 h-2 rounded-full ${
                portfolioSummary.is_demo ? 'bg-amber-400 animate-pulse' : 'bg-emerald-400'
              }`}
            />
            <span className="text-[11px] font-mono text-slate-300">
              {portfolioSummary.is_demo ? 'DEMO DATA' : 'MARKET DATA'}
            </span>
            <span className="text-[10px] text-slate-500 border-l border-slate-700 pl-1.5">
              {portfolioSummary.last_updated}
            </span>
          </div>
        )}

        {/* Refresh button */}
        <button
          onClick={onRefresh}
          disabled={isLoading}
          title="Refresh market data and recalculate analytics"
          className="flex items-center gap-1 text-xs bg-terminal-card border border-terminal-border text-slate-300 hover:text-white hover:border-slate-600 px-2.5 py-1.5 rounded transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>

        {/* Settings button */}
        <button
          onClick={onOpenSettings}
          title="Model settings and formula reference"
          className="p-1.5 bg-terminal-card border border-terminal-border text-slate-400 hover:text-white hover:border-slate-600 rounded transition-colors cursor-pointer"
        >
          <Sliders className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
