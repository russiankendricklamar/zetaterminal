/**
 * Сервис для работы с многомерной HMM моделью анализа рыночных режимов.
 */

import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface FitRequest {
  data?: number[][]
  asset_names?: string[]
  bank_reg_number?: string
  n_regimes?: number
  auto_optimize?: boolean
  criterion?: 'aic' | 'bic' | 'aicc'
  max_iterations?: number
  tol?: number
  random_state?: number
  period_days?: number
}

export interface FitResponse {
  success: boolean
  n_regimes: number
  n_assets: number
  n_samples: number
  asset_names: string[]
  log_likelihood_history: number[]
  iterations: number
  message: string
}

export interface PredictResponse {
  states: number[]
  probabilities: number[][]
  time_indices: number[]
}

export interface RegimeStatistics {
  regime: number
  mean: number[]
  covariance: number[][]
  correlation: number[][]
  volatility_per_asset: number[]
  transition_probs: number[]
  persistence: number
  duration_days: number | null
  frequency: number
  days_in_regime: number
  asset_names: string[]
}

export interface RegimeStatisticsResponse {
  statistics: RegimeStatistics[]
}

export interface RegimeAtTimeResponse {
  time_index: number
  regime_probabilities: number[]
  most_likely_regime: number
  confidence: number
  entropy: number
}

export interface ChartDataPoint {
  price: number
  regime: number
  vol: number
  time_index: number
}

export interface ChartDataResponse {
  success: boolean
  data: ChartDataPoint[]
  n_samples: number
  n_regimes: number
  asset_names: string[]
}

/**
 * Обучение многомерной HMM модели.
 */
export async function fitModel(request: FitRequest): Promise<FitResponse> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/fit`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request)
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка обучения модели: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Предсказать наиболее вероятные состояния.
 */
export async function predictStates(data?: number[][]): Promise<PredictResponse> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/predict`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({ data: data || null })
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка предсказания: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить статистику режимов.
 */
export async function getRegimeStatistics(): Promise<RegimeStatisticsResponse> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/statistics`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения статистики: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить информацию о режиме в момент времени.
 */
export async function getRegimeAtTime(t: number): Promise<RegimeAtTimeResponse> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/regime-at-time?t=${t}`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения информации о режиме: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить матрицу переходов.
 */
export async function getTransitionMatrix(): Promise<{ success: boolean; transition_matrix: number[][]; n_regimes: number }> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/transition-matrix`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения матрицы переходов: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить данные для визуализации.
 */
export async function getChartData(): Promise<ChartDataResponse> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/chart-data`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения данных для графиков: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Симулировать будущие траектории.
 */
export async function simulateTrajectories(nSteps: number = 100): Promise<{ trajectories: number[][]; n_steps: number; n_assets: number }> {
  const response = await fetch(`${API_BASE}/api/multivariate-hmm/simulate`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({ n_steps: nSteps })
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка симуляции: ${response.status}`)
  }
  
  return response.json()
}
