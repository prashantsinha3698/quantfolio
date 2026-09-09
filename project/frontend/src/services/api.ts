/**
 * API service layer communicating with the FastAPI analytics backend.
 */
import type {
  OptimizationResponse,
  PerformanceResponse,
  PortfolioRequest,
  PortfolioSummaryResponse,
  RebalanceResponse,
  RiskResponse,
} from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/$/, '');

async function postJson<T>(endpoint: string, data: any): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorDetail = 'API request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.message || errJson.error || JSON.stringify(errJson);
    } catch {
      errorDetail = `${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const portfolioApi = {
  async getPresets(): Promise<Record<string, PortfolioRequest>> {
    const res = await fetch(`${API_BASE_URL}/portfolios/presets`);
    if (!res.ok) throw new Error('Failed to load portfolio presets');
    return res.json();
  },

  async evaluatePortfolio(portfolio: PortfolioRequest): Promise<PortfolioSummaryResponse> {
    return postJson<PortfolioSummaryResponse>('/portfolios/evaluate', portfolio);
  },

  async getPerformance(portfolio: PortfolioRequest): Promise<PerformanceResponse> {
    return postJson<PerformanceResponse>('/analytics/performance', portfolio);
  },

  async getRisk(portfolio: PortfolioRequest): Promise<RiskResponse> {
    return postJson<RiskResponse>('/risk/analytics', portfolio);
  },

  async runOptimization(portfolio: PortfolioRequest, optParams?: any): Promise<OptimizationResponse> {
    const payload = {
      ...portfolio,
      opt_params: optParams,
    };
    return postJson<OptimizationResponse>('/optimization/run', payload);
  },

  async getRebalance(portfolio: PortfolioRequest): Promise<RebalanceResponse> {
    return postJson<RebalanceResponse>('/rebalance/evaluate', portfolio);
  },

  async checkHealth(): Promise<{ status: string; service: string; version: string }> {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.json();
  }
};
