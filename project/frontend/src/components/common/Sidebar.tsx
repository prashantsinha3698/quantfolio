import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  ShieldAlert,
  SlidersHorizontal,
  Scale,
  PieChart,
  BookOpen,
} from 'lucide-react';

export type NavTab =
  | 'overview'
  | 'performance'
  | 'risk'
  | 'optimization'
  | 'rebalance'
  | 'assets'
  | 'settings';

interface NavItem {
  id: NavTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  rebalanceCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  rebalanceCount = 0,
}) => {
  const navItems: NavItem[] = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'risk', label: 'Risk Analytics', icon: ShieldAlert },
    { id: 'optimization', label: 'Optimization', icon: SlidersHorizontal },
    {
      id: 'rebalance',
      label: 'Rebalancing',
      icon: Scale,
      badge: rebalanceCount > 0 ? `${rebalanceCount}` : undefined,
    },
    { id: 'assets', label: 'Holdings Analysis', icon: PieChart },
    { id: 'settings', label: 'Model & Formulas', icon: BookOpen },
  ];

  return (
    <aside className="w-full md:w-56 bg-terminal-subtle border-r border-terminal-border flex md:flex-col shrink-0 overflow-x-auto md:overflow-y-auto">
      <div className="flex md:flex-col p-2 gap-1 w-full">
        <div className="hidden md:block px-3 py-2 text-[10px] uppercase font-mono tracking-wider text-slate-500 font-semibold">
          Analytics Terminal
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id as NavTab)}
              className={`flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
                isActive
                  ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="ml-2 px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="mt-auto hidden md:block p-3 m-2 rounded bg-terminal-card border border-terminal-border text-[11px] text-slate-400">
        <div className="font-semibold text-slate-300 mb-1">Quantitative Engine</div>
        <div>Markowitz SLSQP Optimization + Historical & Parametric VaR</div>
      </div>
    </aside>
  );
};
