/**
 * Сервис для работы с CCMV оптимизацией портфеля
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface CCMVRequest {
  R: number[][];  // Матрица доходностей (time_steps x num_assets)
  mu: number[];  // Ожидаемые доходности активов
  cov_matrix: number[][];  // Ковариационная матрица
  Delta: number;  // Максимальное количество активов
  bar_w: number;  // Максимальный вес на актив
  gamma: number;  // Коэффициент неприятия риска
  method?: 'delta' | 'alpha';  // Метод оптимизации
  asset_names?: string[];  // Названия активов
}

export interface CCMVCluster {
  assets: string[];
  asset_indices: number[];
  delta_k: number;
  alpha_k: number;
  weights: number[];
}

export interface CCMVResponse {
  optimal_weights: number[];
  clusters: CCMVCluster[];
  portfolio_stats: {
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
    objective_value: number;
  };
  method: string;
  Delta: number;
  gamma: number;
  bar_w: number;
  timestamp: string;
}

/**
 * Выполняет CCMV оптимизацию портфеля
 */
export const optimizeCCMVPortfolio = async (request: CCMVRequest): Promise<CCMVResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ccmv/optimize`, {
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
    console.error('CCMV Optimization Failed:', error);
    throw error;
  }
};

/**
 * Проверка здоровья CCMV сервиса
 */
export const checkCCMVHealth = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ccmv/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('CCMV Health Check Failed:', error);
    throw error;
  }
};
