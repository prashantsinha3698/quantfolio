import React from 'react';
import { BookOpen } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const formulas = [
    {
      name: 'Portfolio Daily Return',
      formula: 'r_{p,t} = \\sum_{i=1}^N w_i \\cdot r_{i,t} = \\mathbf{w}^T \\mathbf{r}_t',
      explanation: 'Weighted sum of asset daily simple returns under static or time-varying weights.',
      assumptions: 'Daily simple returns with full reinvestment; weights sum to 1.0.',
    },
    {
      name: 'Compound Annual Growth Rate (CAGR)',
      formula: 'CAGR = (1 + R_{total})^{252 / T} - 1',
      explanation: 'Geometric annualized growth rate normalized for standard 252 trading days.',
      assumptions: 'Compounding frequency matches standard business day calendar.',
    },
    {
      name: 'Annualized Volatility',
      formula: '\\sigma_{ann} = \\sigma_d \\times \\sqrt{252}',
      explanation: 'Sample standard deviation of daily returns scaled by square root of 252 trading days.',
      assumptions: 'Assumes returns are identically and independently distributed (i.i.d.).',
    },
    {
      name: 'Sharpe Ratio',
      formula: 'Sharpe = \\frac{R_{p,ann} - R_f}{\\sigma_{p,ann}}',
      explanation: 'Excess return earned per unit of total risk above the risk-free rate (default 4.0%).',
      assumptions: 'Risk-free rate is constant; total risk captured by volatility.',
    },
    {
      name: 'Sortino Ratio',
      formula: 'Sortino = \\frac{R_{p,ann} - R_f}{\\sigma_{downside}}',
      explanation: 'Penalizes only downside return deviations below the target benchmark / risk-free rate.',
      assumptions: 'Upside volatility is beneficial and not penalized.',
    },
    {
      name: 'Maximum Drawdown (MDD)',
      formula: 'MDD = \\min_{t} \\left( \\frac{W_t}{\\max_{s \\le t} W_s} - 1 \\right)',
      explanation: 'Largest peak-to-trough drop in portfolio wealth before a new high-water mark is reached.',
      assumptions: 'Calculated along the continuous wealth trajectory.',
    },
    {
      name: 'Historical Value at Risk (VaR)',
      formula: 'VaR_\\alpha = -\\text{Quantile}_{1-\\alpha}(r_p) \\times \\text{Value} \\times \\sqrt{h}',
      explanation: 'Empirical quantile loss at confidence level alpha (e.g. 95% or 99%) over horizon h.',
      assumptions: 'Historical return distribution represents future probability distribution.',
    },
    {
      name: 'Historical Expected Shortfall (CVaR)',
      formula: 'CVaR_\\alpha = \\mathbb{E}[L \\mid L \\ge VaR_\\alpha]',
      explanation: 'Average loss given that the loss breaches the VaR threshold.',
      assumptions: 'Coherent risk measure capturing severe tail risk.',
    },
    {
      name: 'Percentage Risk Contribution (PRC)',
      formula: 'PRC_i = \\frac{w_i \\cdot (\\Sigma \\mathbf{w})_i}{\\sigma_p^2}',
      explanation: 'Component percentage of total portfolio volatility contributed by asset i.',
      assumptions: 'Mathematical invariant: \\sum_{i=1}^N PRC_i = 100\\%.',
    },
    {
      name: 'Allocation Drift & Trade',
      formula: 'Drift_i = w_{current,i} - w_{target,i}, \\quad Trade_i = V \\cdot (w_{target,i} - w_{current,i})',
      explanation: 'Difference between current holding weight and target allocation, generating buy/sell orders.',
      assumptions: 'Threshold triggers rebalancing when |Drift| exceeds threshold (default 5.0%).',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-terminal-card border border-terminal-border rounded-lg p-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded bg-cyan-950/60 border border-cyan-800 text-cyan-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Quantitative Methodology & Formulas</h2>
            <p className="text-xs text-slate-400">
              Mathematical specifications and operational assumptions implemented across all analytics engines
            </p>
          </div>
        </div>
      </div>

      {/* Formula Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {formulas.map((item, idx) => (
          <div key={idx} className="bg-terminal-card border border-terminal-border rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between text-xs font-semibold text-cyan-300">
              <span>{item.name}</span>
              <span className="text-slate-500 font-mono">#{idx + 1}</span>
            </div>
            <div className="p-2.5 bg-slate-900/90 rounded border border-slate-800 font-mono text-xs text-slate-200 overflow-x-auto">
              {item.formula}
            </div>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">{item.explanation}</p>
            <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-800/80">
              <span className="font-semibold text-slate-400">Assumptions:</span> {item.assumptions}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
