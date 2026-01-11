/**
 * Сервис для работы с бэктестингом портфеля
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
  try {
    const response = await fetch(`${API_BASE_URL}/api/backtest/run`, {
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
    console.error('Backtest Failed:', error);
    throw error;
  }
};

/**
 * Проверка здоровья бэктестинга сервиса
 */
export const checkBacktestHealth = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/backtest/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Backtest Health Check Failed:', error);
    throw error;
  }
};
