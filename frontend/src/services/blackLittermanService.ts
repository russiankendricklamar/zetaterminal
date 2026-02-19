/**
 * Сервис для работы с Black-Litterman оптимизацией портфеля
 */

import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export interface BLView {
  assets: number[]
  weights: number[]
  expected_return: number
  confidence: number
}

export interface BlackLittermanRequest {
  cov_matrix: number[][]
  market_weights: number[]
  views: BLView[]
  tau: number
  delta: number
  risk_free_rate: number
  max_weight: number
  asset_names?: string[]
}

export interface BLViewImpact {
  view_index: number
  view_return: number
  confidence: number
  affected_assets: string[]
  weight_shift: number
}

export interface BlackLittermanResponse {
  optimal_weights: number[]
  equilibrium_weights: number[]
  equilibrium_returns: number[]
  posterior_returns: number[]
  posterior_cov: number[][]
  risk_contributions: number[]
  views_impact: BLViewImpact[]
  portfolio_stats: {
    expected_return: number
    volatility: number
    sharpe_ratio: number
    num_positions: number
  }
  equilibrium_stats: {
    expected_return: number
    volatility: number
    sharpe_ratio: number
  }
  parameters: {
    tau: number
    delta: number
    risk_free_rate: number
    max_weight: number
    num_views: number
  }
  asset_names: string[]
  timestamp: string
}

export const optimizeBlackLitterman = async (
  request: BlackLittermanRequest
): Promise<BlackLittermanResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/black-litterman/optimize`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Black-Litterman Optimization Failed:', error)
    throw error
  }
}

export const checkBLHealth = async (): Promise<{ status: string; service: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/black-litterman/health`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Black-Litterman Health Check Failed:', error)
    throw error
  }
}
