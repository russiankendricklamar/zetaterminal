/**
 * Service for GARCH volatility modeling API.
 */
import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API_BASE_URL = getApiBaseUrl()

// ---------- Request Types ----------

export interface GarchFitRequest {
  returns: number[]
  model?: 'garch_11' | 'gjr_garch' | 'egarch' | 'ewma'
  params?: Record<string, number>
  initial_variance?: number
}

export interface GarchForecastRequest {
  returns: number[]
  model?: 'garch_11' | 'gjr_garch' | 'egarch' | 'ewma'
  params?: Record<string, number>
  n_steps?: number
  confidence_levels?: number[]
}

export interface DCCRequest {
  returns_matrix: number[][]
  univariate_model?: string
  univariate_params?: Record<string, number>[]
  dcc_params?: { a: number; b: number }
  n_steps?: number
}

export interface DiagnosticsRequest {
  returns: number[]
}

// ---------- Response Types ----------

export interface GarchFitResult {
  model: string
  params: Record<string, number>
  variances: number[]
  volatilities: number[]
  residuals: number[]
  log_likelihood: number
  persistence?: number
  long_run_variance?: number | null
  n_params: number
  n_obs: number
}

export interface ForecastResult {
  forecasts: number[]
  forecast_volatilities: number[]
  annualized_volatilities: number[]
  confidence_intervals: Record<string, number[]>
  term_structure: number[]
  current_vol: number
  forecast_vol: number
  long_run_vol: number | null
  n_steps: number
}

export interface GarchForecastResponse {
  fit: GarchFitResult
  forecast: ForecastResult
}

export interface ModelRanking {
  model: string
  log_likelihood: number
  n_params: number
  aic: number
  bic: number
  persistence?: number
}

export interface DiagnosticsResponse {
  comparison: {
    rankings: ModelRanking[]
    best_aic: string
    best_bic: string
  }
  diagnostics: {
    ljung_box: {
      statistic: number
      p_value: number
      lags: number
      reject_h0: boolean
    }
    arch_lm: {
      statistic: number
      p_value: number
      r_squared: number
      lags: number
      reject_h0: boolean
    }
  }
  best_model: GarchFitResult
}

// ---------- API Functions ----------

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/api/garch${path}`, {
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

export const fitGarch = (request: GarchFitRequest): Promise<GarchFitResult> =>
  post<GarchFitResult>('/fit', request)

export const forecastGarch = (request: GarchForecastRequest): Promise<GarchForecastResponse> =>
  post<GarchForecastResponse>('/forecast', request)

export const fitDCC = (request: DCCRequest): Promise<Record<string, unknown>> =>
  post<Record<string, unknown>>('/dcc', request)

export const garchDiagnostics = (request: DiagnosticsRequest): Promise<DiagnosticsResponse> =>
  post<DiagnosticsResponse>('/diagnostics', request)
