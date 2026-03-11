/**
 * Service for the GARCH-Conditional VaR/CVaR Risk Engine API.
 */
import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API_BASE_URL = getApiBaseUrl()

// ---------- Request Types ----------

export type VaRMethod = 'parametric' | 'historical' | 'monte_carlo'
export type GarchModel = 'garch_11' | 'gjr_garch' | 'egarch' | 'ewma'

export interface VaRRequest {
  returns: number[]
  method?: VaRMethod
  confidence?: number
  horizon?: number
  portfolio_value?: number
  n_simulations?: number
  use_garch?: boolean
  garch_model?: GarchModel
}

export interface RiskReportRequest {
  returns: number[]
  confidence?: number
  horizon?: number
  portfolio_value?: number
  n_simulations?: number
  use_garch?: boolean
  garch_model?: GarchModel
  returns_matrix?: number[][]
  weights?: number[]
}

// ---------- Response Types ----------

export interface VaRResult {
  method: VaRMethod
  confidence: number
  horizon: number
  portfolio_value: number
  use_garch: boolean
  garch_model: string | null
  var: number
  cvar: number
  volatility?: number
  z_score?: number
  var_quantile?: number
  cvar_quantile?: number
  n_tail_obs?: number
  mean_pnl?: number
  std_pnl?: number
  n_simulations?: number
  percentile_5?: number
  percentile_95?: number
}

export interface ComponentVaRResult {
  total_var: number
  marginal_var: number[]
  component_var: number[]
  pct_contribution: number[]
  portfolio_volatility: number
}

export interface RiskReportResult {
  confidence: number
  horizon: number
  portfolio_value: number
  use_garch: boolean
  parametric: VaRResult
  historical: VaRResult
  monte_carlo: VaRResult
  component_var?: ComponentVaRResult
}

// ---------- API Functions ----------

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api/risk${path}`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export const calculateVaR = (request: VaRRequest): Promise<VaRResult> =>
  post<VaRResult>('/var', request)

export const getRiskReport = (request: RiskReportRequest): Promise<RiskReportResult> =>
  post<RiskReportResult>('/report', request)
