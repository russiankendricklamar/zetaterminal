/**
 * Сервис для работы с HJB оптимизацией портфеля
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface HJBRequest {
  mu: number[];
  cov_matrix: number[][];
  risk_free_rate: number;
  gamma: number;
  asset_names?: string[];
  monte_carlo?: {
    initial_capital?: number;
    horizon_years?: number;
    n_paths?: number;
    n_steps?: number;
    random_seed?: number;
  };
}

export interface HJBResponse {
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
  timestamp: string;
}

/**
 * Выполняет HJB оптимизацию портфеля
 */
export const optimizeHJBPortfolio = async (request: HJBRequest): Promise<HJBResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/hjb/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('HJB Optimization Failed:', error);
    throw error;
  }
};

/**
 * Проверка здоровья HJB сервиса
 */
export const checkHJBHealth = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/hjb/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('HJB Health Check Failed:', error);
    throw error;
  }
};
