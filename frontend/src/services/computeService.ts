/**
 * Сервис для работы с вычислительными задачами
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface GARCHRequest {
  returns: number[];
  omega?: number;
  alpha?: number;
  beta?: number;
  initial_variance?: number;
}

export interface GARCHResponse {
  result: {
    variances: number[];
    volatilities: number[];
    residuals: number[];
    parameters: {
      omega: number;
      alpha: number;
      beta: number;
    };
    long_term_volatility: number;
    mean_variance: number;
    mean_volatility: number;
  };
  status: string;
  timestamp: string;
}

/**
 * Вычисляет GARCH(1,1) модель волатильности
 */
export const calculateGARCH = async (request: GARCHRequest): Promise<GARCHResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/compute/garch`, {
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
    console.error('GARCH Calculation Failed:', error);
    throw error;
  }
};
