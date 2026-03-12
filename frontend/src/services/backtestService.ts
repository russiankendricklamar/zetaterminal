/**
 * Сервис для работы с бэктестингом портфеля
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

// Используем относительный путь для работы с Vite proxy
const API_BASE_URL = getApiBaseUrl();

export interface BacktestRequest {
  mu: number[];
  cov_matrix: number[][];
  initial_capital?: number;
  risk_free_rate: number;
  gamma: number;
  horizon_years?: number;
  n_steps?: number;
  asset_names?: string[];
  n_paths?: number;
  seed?: number;
}

export interface BacktestMetrics {
  total_return: number;
  cagr: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  drawdowns: Array<{
    period: string;
    amount: number;
    recovery: string;
  }>;
  monthly_returns: { [year: string]: { [month: number]: number } };
  total_trades: number;
  win_rate: number;
  profit_factor: number;
  avg_profit: number;
  avg_loss: number;
  hold_time: number;
  equity_curve: number[];
  dates: string[];
}

export interface BacktestResponse {
  metrics: BacktestMetrics;
  equity_curve: number[];
  benchmark_curve: number[];
  dates: string[];
  optimal_weights: number[];
  portfolio_stats: {
    optimal_weights: number[];
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
    risk_free_rate: number;
    gamma: number;
  };
  monte_carlo_stats: {
    mean_final: number;
    median_final: number;
    std_final: number;
    min_final: number;
    max_final: number;
    var_95: number;
    cvar_95: number;
    var_99: number;
    cvar_99: number;
    mean_max_drawdown: number;
    mean_return: number;
    median_return: number;
    std_return: number;
    sharpe_ratio: number;
  };
}

/**
 * Выполняет бэктест портфеля
 */
export const runPortfolioBacktest = async (request: BacktestRequest): Promise<BacktestResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/backtest/run`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

/**
 * Проверка здоровья бэктестинга сервиса
 */
export const checkBacktestHealth = async (): Promise<{ status: string; service: string }> => {
  const response = await fetch(`${API_BASE_URL}/api/backtest/health`, { headers: getApiHeaders() });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
};


// ── Historical Backtest ─────────────────────────────────────────────────────

export interface HistoricalBacktestRequest {
  historical_prices: number[][];
  asset_names?: string[];
  rebalance_frequency?: 'daily' | 'weekly' | 'monthly' | 'quarterly';
  strategy_type?: 'equal_weight' | 'min_variance' | 'risk_parity' | 'max_sharpe' | 'custom';
  initial_weights?: number[];
  lookback_window?: number;
  transaction_cost_bps?: number;
  risk_free_rate?: number;
  initial_capital?: number;
}

export interface HistoricalBacktestResponse {
  equity_curve: number[];
  benchmark_curve: number[];
  dates: string[];
  metrics: BacktestMetrics & {
    calmar_ratio: number;
    sortino_ratio: number;
    information_ratio: number;
  };
  weights_history: number[][];
  asset_names: string[];
  n_rebalances: number;
  total_transaction_cost: number;
  transaction_cost_pct: number;
  strategy_type: string;
  rebalance_frequency: string;
}

export const runHistoricalBacktest = async (
  request: HistoricalBacktestRequest,
): Promise<HistoricalBacktestResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/backtest/historical`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
};


// ── Walk-Forward Optimization ───────────────────────────────────────────────

export interface WalkForwardRequest {
  historical_prices: number[][];
  asset_names?: string[];
  in_sample_window?: number;
  out_of_sample_window?: number;
  optimization_method?: 'min_variance' | 'risk_parity' | 'max_sharpe';
  step_size?: number;
  transaction_cost_bps?: number;
  risk_free_rate?: number;
  initial_capital?: number;
}

export interface WalkForwardWindowMetric {
  window: number;
  is_start: number;
  is_end: number;
  oos_start: number;
  oos_end: number;
  is_sharpe: number;
  oos_sharpe: number;
  oos_return: number;
  oos_vol: number;
  weights: number[];
}

export interface WalkForwardResponse {
  oos_equity_curve: number[];
  dates: string[];
  metrics: BacktestMetrics & {
    calmar_ratio: number;
    sortino_ratio: number;
  };
  per_window_metrics: WalkForwardWindowMetric[];
  aggregated_stats: {
    n_windows: number;
    avg_is_sharpe: number;
    avg_oos_sharpe: number;
    degradation_ratio: number;
    total_oos_return: number;
  };
  asset_names: string[];
  optimization_method: string;
  in_sample_window: number;
  out_of_sample_window: number;
}

export const runWalkForwardOptimization = async (
  request: WalkForwardRequest,
): Promise<WalkForwardResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/backtest/walk-forward`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return await response.json();
};
