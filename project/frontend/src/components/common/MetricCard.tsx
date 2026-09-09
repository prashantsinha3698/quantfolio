import React from 'react';
import { HelpCircle, TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  tooltip?: string;
  highlight?: 'cyan' | 'emerald' | 'amber' | 'rose' | 'default';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  trend,
  trendValue,
  tooltip,
  highlight = 'default',
  className = '',
}) => {
  const getBorderHighlight = () => {
    switch (highlight) {
      case 'cyan':
        return 'border-t-2 border-t-cyan-500';
      case 'emerald':
        return 'border-t-2 border-t-emerald-500';
      case 'amber':
        return 'border-t-2 border-t-amber-500';
      case 'rose':
        return 'border-t-2 border-t-rose-500';
      default:
        return 'border-t border-t-slate-800';
    }
  };

  return (
    <div
      className={`bg-terminal-card border border-terminal-border rounded-lg p-4 shadow-sm relative overflow-hidden group ${getBorderHighlight()} ${className}`}
    >
      <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5 font-medium">
        <span>{label}</span>
        {tooltip && (
          <div className="relative group/tooltip">
            <HelpCircle className="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 cursor-pointer" />
            <div className="absolute right-0 top-5 w-48 p-2 bg-slate-900 border border-slate-700 text-slate-300 text-[11px] rounded shadow-xl opacity-0 group-hover/tooltip:opacity-100 transition-opacity z-50 pointer-events-none">
              {tooltip}
            </div>
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-xl sm:text-2xl font-bold tracking-tight text-white font-mono tabular-nums">
          {value}
        </span>
        {trendValue && (
          <span
            className={`inline-flex items-center text-xs font-semibold px-1.5 py-0.5 rounded font-mono ${
              trend === 'up'
                ? 'text-emerald-400 bg-emerald-950/40 border border-emerald-800/50'
                : trend === 'down'
                ? 'text-rose-400 bg-rose-950/40 border border-rose-800/50'
                : 'text-slate-400 bg-slate-800'
            }`}
          >
            {trend === 'up' && <TrendingUp className="w-3 h-3 mr-0.5" />}
            {trend === 'down' && <TrendingDown className="w-3 h-3 mr-0.5" />}
            {trendValue}
          </span>
        )}
      </div>

      {subtext && <div className="text-[11px] text-slate-500 mt-1 font-sans">{subtext}</div>}
    </div>
  );
};
