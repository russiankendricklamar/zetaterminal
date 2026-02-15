/**
 * Сервис для работы со стресс-тестированием портфеля
 */

import { getApiHeaders } from '@/utils/apiHeaders'

// Используем относительный путь для работы с Vite proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export interface StressScenario {
  name: string;
  key: string;
  type: 'return_shock' | 'volatility_shock' | 'correlation_shock';
  return_multiplier?: number;
  volatility_multiplier?: number;
  correlation_multiplier?: number;
  seed?: number;
}

export interface StressTestRequest {
  mu: number[];
  cov_matrix: number[][];
  initial_capital?: number;
  risk_free_rate: number;
  gamma: number;
  scenarios: StressScenario[];
  asset_names?: string[];
  n_paths?: number;
  seed?: number;
}

export interface StressScenarioResult {
  scenario_name: string;
  metrics: {
    mean_final: number;
    median_final: number;
    mean_return: number;
    median_return: number;
    std_return: number;
    sharpe: number;
    var_95: number;
    var_99: number;
    cvar_95: number;
    cvar_99: number;
    loss_var_95: number;
    loss_var_99: number;
    loss_cvar_95: number;
    loss_cvar_99: number;
    mean_max_dd: number;
    worst_dd: number;
    prob_loss: number;
    prob_loss_50: number;
  };
  optimal_weights: number[];
  portfolio_stats: {
    optimal_weights: number[];
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
    risk_free_rate: number;
    gamma: number;
  };
  monte_carlo?: {
    paths: number[][];
    median_path: number[];
    q05_path: number[];
    q95_path: number[];
    t_grid: number[];
    stats: {
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
  };
  T_years: number;
  n_paths: number;
}

export interface StressTestResponse {
  results: { [key: string]: StressScenarioResult };
  baseline: {
    initial_capital: number;
    risk_free_rate: number;
    gamma: number;
    n_assets: number;
    asset_names: string[];
  };
}

/**
 * Выполняет стресс-тестирование портфеля
 */
export const runStressTests = async (request: StressTestRequest): Promise<StressTestResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stress/test`, {
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
    console.error('Stress Test Failed:', error);
    throw error;
  }
};

/**
 * Проверка здоровья стресс-тестирования сервиса
 */
export const checkStressHealth = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stress/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Stress Health Check Failed:', error);
    throw error;
  }
};
