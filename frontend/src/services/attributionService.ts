/**
 * Attribution Service - Brinson-Fachler and Factor-based P&L attribution.
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API_BASE_URL = getApiBaseUrl()

// -- Request Types ------------------------------------------------------------

export interface BrinsonRequest {
  portfolio_weights: number[]
  benchmark_weights: number[]
  portfolio_returns: number[]
  benchmark_returns: number[]
  sector_names?: string[]
}

export interface FactorAttributionRequest {
  portfolio_returns: number[]
  factor_returns: number[][]
  factor_names?: string[]
  portfolio_value?: number
}

// -- Response Types -----------------------------------------------------------

export interface BrinsonSector {
  name: string
  portfolio_weight: number
  benchmark_weight: number
  portfolio_return: number
  benchmark_return: number
  allocation_effect: number
  selection_effect: number
  interaction_effect: number
  total_effect: number
}

export interface BrinsonTotals {
  allocation: number
  selection: number
  interaction: number
  excess_return: number
  decomposition_total: number
  verification_error: number
}

export interface BrinsonResult {
  sectors: BrinsonSector[]
  totals: BrinsonTotals
  portfolio_return: number
  benchmark_return: number
  n_sectors: number
}

export interface FactorResult {
  factors: Array<{
    name: string
    beta: number
    mean_return: number
    cumulative_contribution: number
    pnl_contribution: number
    period_contributions: number[]
    factor_volatility: number
  }>
  alpha: number
  alpha_annualized: number
  alpha_pnl: number
  r_squared: number
  adjusted_r_squared: number
  residual_std: number
  residual_pnl: number
  total_factor_pnl: number
  total_pnl: number
  explained_pnl: number
  unexplained_pnl: number
  n_observations: number
  n_factors: number
  portfolio_value: number
  betas: number[]
  factor_names: string[]
}

export interface AttributionResponse<T> {
  result: T
  timestamp: string
}

// -- API Calls ----------------------------------------------------------------

export async function runBrinsonAttribution(
  params: BrinsonRequest,
): Promise<BrinsonResult> {
  const response = await fetch(`${API_BASE_URL}/api/attribution/brinson`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Attribution request failed' }))
    throw new Error(err.detail || `HTTP ${response.status}`)
  }
  const data: AttributionResponse<BrinsonResult> = await response.json()
  return data.result
}

export async function runFactorAttribution(
  params: FactorAttributionRequest,
): Promise<FactorResult> {
  const response = await fetch(`${API_BASE_URL}/api/attribution/factor`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(params),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Factor attribution request failed' }))
    throw new Error(err.detail || `HTTP ${response.status}`)
  }
  const data: AttributionResponse<FactorResult> = await response.json()
  return data.result
}
