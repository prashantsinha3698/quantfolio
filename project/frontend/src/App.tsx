import { useState, useEffect, useCallback } from 'react';
import { TopBar } from './components/common/TopBar';
import { Sidebar } from './components/common/Sidebar';
import type { NavTab } from './components/common/Sidebar';
import { DashboardOverview } from './components/dashboard/DashboardOverview';
import { PerformanceView } from './components/performance/PerformanceView';
import { RiskView } from './components/risk/RiskView';
import { OptimizationView } from './components/optimization/OptimizationView';
import { RebalanceView } from './components/rebalance/RebalanceView';
import { AssetDetailView } from './components/assets/AssetDetailView';
import { SettingsView } from './components/settings/SettingsView';
import type {
  OptimizationResponse,
  PerformanceResponse,
  PortfolioRequest,
  PortfolioSummaryResponse,
  RebalanceResponse,
  RiskResponse,
} from './types';
import { portfolioApi, API_BASE_URL } from './services/api';
import { AlertCircle, RefreshCw } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [presets, setPresets] = useState<Record<string, PortfolioRequest>>({});
  const [selectedPresetKey, setSelectedPresetKey] = useState<string>('balanced_growth');
  const [currentPortfolio, setCurrentPortfolio] = useState<PortfolioRequest | null>(null);

  // Analytical results state
  const [summary, setSummary] = useState<PortfolioSummaryResponse | null>(null);
  const [performance, setPerformance] = useState<PerformanceResponse | null>(null);
  const [risk, setRisk] = useState<RiskResponse | null>(null);
  const [optimization, setOptimization] = useState<OptimizationResponse | null>(null);
  const [rebalance, setRebalance] = useState<RebalanceResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Load Presets on Mount
  useEffect(() => {
    async function init() {
      try {
        const loadedPresets = await portfolioApi.getPresets();
        setPresets(loadedPresets);
        const defaultKey = Object.keys(loadedPresets)[0] || 'balanced_growth';
        setSelectedPresetKey(defaultKey);
        setCurrentPortfolio(loadedPresets[defaultKey]);
      } catch (err: any) {
        setErrorMessage(`Failed to connect to backend analytics service at ${API_BASE_URL}. If your backend is hosted on Render free tier, please allow up to 45 seconds for cold start.`);
        setIsLoading(false);
      }
    }
    init();
  }, []);

  // Fetch all analytics for the current portfolio
  const fetchAllAnalytics = useCallback(async (portfolio: PortfolioRequest) => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      // Parallel analytical data loading
      const [sumRes, perfRes, riskRes, rebalRes, optRes] = await Promise.all([
        portfolioApi.evaluatePortfolio(portfolio),
        portfolioApi.getPerformance(portfolio),
        portfolioApi.getRisk(portfolio),
        portfolioApi.getRebalance(portfolio),
        portfolioApi.runOptimization(portfolio),
      ]);

      setSummary(sumRes);
      setPerformance(perfRes);
      setRisk(riskRes);
      setRebalance(rebalRes);
      setOptimization(optRes);
    } catch (err: any) {
      setErrorMessage(err.message || 'Analytical processing failed.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Trigger load when current portfolio changes
  useEffect(() => {
    if (currentPortfolio) {
      fetchAllAnalytics(currentPortfolio);
    }
  }, [currentPortfolio, fetchAllAnalytics]);

  const handleSelectPreset = (key: string) => {
    setSelectedPresetKey(key);
    if (presets[key]) {
      setCurrentPortfolio(presets[key]);
    }
  };

  const handleSelectDateRange = (range: string) => {
    if (!currentPortfolio) return;
    const updated = { ...currentPortfolio, date_range: range };
    setCurrentPortfolio(updated);
  };

  const handleRefresh = () => {
    if (currentPortfolio) {
      fetchAllAnalytics(currentPortfolio);
    }
  };

  return (
    <div className="min-h-screen bg-terminal-bg flex flex-col selection:bg-cyan-500/20 selection:text-cyan-200">
      {/* Global Top Bar */}
      {currentPortfolio && (
        <TopBar
          currentPortfolio={currentPortfolio}
          portfolioSummary={summary}
          presets={presets}
          selectedPresetKey={selectedPresetKey}
          onSelectPreset={handleSelectPreset}
          onSelectDateRange={handleSelectDateRange}
          onRefresh={handleRefresh}
          isLoading={isLoading}
          onOpenSettings={() => setActiveTab('settings')}
        />
      )}

      {/* Main Body with Sidebar and Active Content Area */}
      <div className="flex-1 flex flex-col md:flex-row">
        <Sidebar
          activeTab={activeTab}
          onTabChange={setActiveTab}
          rebalanceCount={rebalance?.summary.assets_outside_threshold || 0}
        />

        <main className="flex-1 p-4 sm:p-6 max-w-7xl mx-auto w-full overflow-y-auto">
          {/* Global Error Notice */}
          {errorMessage && (
            <div className="mb-6 p-4 rounded-lg bg-rose-950/40 border border-rose-600/50 flex items-center justify-between text-xs text-rose-200">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                onClick={handleRefresh}
                className="px-3 py-1 rounded bg-rose-600 hover:bg-rose-500 text-white font-semibold transition-colors cursor-pointer"
              >
                Retry
              </button>
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading && !summary && (
            <div className="py-20 text-center space-y-3">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
              <div className="text-sm font-semibold text-slate-300">
                Calculating Quantitative Risk & Performance Analytics...
              </div>
              <div className="text-xs text-slate-500 font-mono">
                Downloading Market Data • Solving SLSQP Efficient Frontier • Estimating VaR
              </div>
            </div>
          )}

          {/* Views */}
          {!isLoading && activeTab === 'overview' && (
            <DashboardOverview
              summary={summary}
              performance={performance}
              risk={risk}
              rebalance={rebalance}
              onNavigateToRebalance={() => setActiveTab('rebalance')}
            />
          )}

          {!isLoading && activeTab === 'performance' && (
            <PerformanceView performance={performance} />
          )}

          {!isLoading && activeTab === 'risk' && <RiskView risk={risk} />}

          {!isLoading && activeTab === 'optimization' && currentPortfolio && (
            <OptimizationView
              currentPortfolio={currentPortfolio}
              optimization={optimization}
              onOptimizationUpdated={(newOpt) => setOptimization(newOpt)}
            />
          )}

          {!isLoading && activeTab === 'rebalance' && (
            <RebalanceView rebalance={rebalance} />
          )}

          {!isLoading && activeTab === 'assets' && (
            <AssetDetailView summary={summary} risk={risk} />
          )}

          {!isLoading && activeTab === 'settings' && <SettingsView />}
        </main>
      </div>
    </div>
  );
}

export default App;
