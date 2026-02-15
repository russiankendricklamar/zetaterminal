/**
 * Сервис для работы с метриками портфеля
 */

import { getApiHeaders } from '@/utils/apiHeaders'

// Используем относительный путь для работы с Vite proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface Position {
  symbol: string;
  name: string;
  price: number;
  dayChange: number;
  notional: number;
  allocation: number;
  targetAllocation: number;
  color?: string;
}

export interface PortfolioMetricsRequest {
  positions: Position[];
  risk_free_rate?: number;
  market_return?: number;
  market_volatility?: number;
}

export interface PortfolioMetricsResponse {
  total_pnl: number;
  nav: number;
  annual_return: number;
  daily_return: number;
  volatility: number;
  var_95: number;
  var_95_daily: number;
  var_95_percent: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  beta: number;
  alpha: number;
  skew: number;
  max_drawdown: number;
  diversification: number;
  avg_correlation: number;
  risk_free_rate: number;
  num_positions: number;
  status: string;
  timestamp: string;
}

/**
 * Вычисляет метрики портфеля
 */
export const calculatePortfolioMetrics = async (
  request: PortfolioMetricsRequest
): Promise<PortfolioMetricsResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/portfolio/metrics`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Portfolio Metrics Calculation Failed:', error);
    throw error;
  }
};
