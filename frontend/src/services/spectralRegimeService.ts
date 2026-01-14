/**
 * Сервис для работы с API комплексного анализа скрытых рыночных режимов.
 * 
 * Предоставляет методы для:
 * - Получения списка доступных активов
 * - Загрузки исторических данных
 * - Запуска спектрального анализа режимов
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Asset {
  ticker: string
  name: string
  source: string
}

export interface AssetCategory {
  stocks: Asset[]
  crypto: Asset[]
  commodities: Asset[]
  bonds: Asset[]
  forex: Asset[]
  russia: Asset[]
}

export interface AssetMetadata {
  ticker: string
  start_date: string | null
  end_date: string | null
  n_observations: number
  mean_return: number
  std_return: number
  min_return: number
  max_return: number
  last_price: number | null
}

export interface FetchDataResponse {
  success: boolean
  returns: number[]
  prices: number[]
  metadata: AssetMetadata
}

export interface PoleData {
  index: number
  real: number
  imag: number
  radius: number
  angle: number
}

export interface RegimePoleData {
  regime: number
  real: number
  imag: number
  radius: number
  type: string
}

export interface SpectrumData {
  frequencies: number[]
  amplitude: number[]
  log_amplitude: number[]
  phase: number[]
}

export interface DynamicsData {
  time_series: number[]
  regime_signal: number[]
  regime_energies: number[][]
  entropy: number[]
}

export interface RegimeParams {
  pole: { real: number; imag: number }
  radius: number
  angle: number
  duration: number
  periodicity: number
  intensity: number
  type: string
}

export interface CurrentMetrics {
  regime_index: number
  regime_type: string
  regime_energies: number[]
  entropy: number
  is_stable: boolean
  is_minimum_phase: boolean
  expected_duration_days: number
}

export interface RegimeTimeStats {
  count: number
  percentage: number
}

export interface EntropyStats {
  mean: number
  max: number
  min: number
  std: number
}

export interface AnalysisSummary {
  n_regimes: number
  n_poles: number
  regime_params: { [key: string]: RegimeParams }
  stability: {
    is_stable: boolean
    n_violations: number
    violation_indices: number[]
  }
  minimum_phase: {
    is_minimum_phase: boolean
    n_violations: number
    violations: any[]
  }
  reconstruction: {
    rmse: number
    pct_explained: number
  }
  regime_time_stats: { [key: string]: RegimeTimeStats }
  entropy_stats: EntropyStats
  current_metrics: CurrentMetrics
}

export interface VisualizationData {
  poles: PoleData[]
  regime_poles: RegimePoleData[]
  spectrum: SpectrumData
  dynamics: DynamicsData
  acf: number[]
}

export interface SpectralAnalysisResponse {
  success: boolean
  summary: AnalysisSummary
  visualization: VisualizationData
}

export interface FullAssetAnalysisResponse {
  success: boolean
  asset_metadata: AssetMetadata
  prices: number[]
  returns: number[]
  analysis: {
    summary: AnalysisSummary
    visualization: VisualizationData
  }
}

/**
 * Получить список доступных активов для анализа.
 */
export async function getAvailableAssets(): Promise<{ success: boolean; data: AssetCategory }> {
  const response = await fetch(`${API_BASE}/api/spectral-regime/assets`)
  
  if (!response.ok) {
    throw new Error(`Ошибка получения списка активов: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Загрузить исторические данные актива.
 */
export async function fetchAssetData(
  ticker: string,
  periodDays: number = 252,
  source: string = 'yfinance'
): Promise<FetchDataResponse> {
  const response = await fetch(`${API_BASE}/api/spectral-regime/fetch-data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      ticker,
      period_days: periodDays,
      source
    })
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка загрузки данных: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Запустить анализ спектральных режимов.
 */
export async function analyzeSpectralRegimes(
  returns: number[],
  nPoles: number = 5,
  windowSize: number = 20,
  maxLag?: number
): Promise<SpectralAnalysisResponse> {
  const response = await fetch(`${API_BASE}/api/spectral-regime/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      returns,
      n_poles: nPoles,
      window_size: windowSize,
      max_lag: maxLag
    })
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка анализа: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Загрузить данные актива и выполнить анализ одним запросом.
 */
export async function analyzeAssetRegimes(
  ticker: string,
  periodDays: number = 252,
  nPoles: number = 5,
  windowSize: number = 20
): Promise<FullAssetAnalysisResponse> {
  const params = new URLSearchParams({
    ticker,
    period_days: periodDays.toString(),
    n_poles: nPoles.toString(),
    window_size: windowSize.toString()
  })
  
  const response = await fetch(`${API_BASE}/api/spectral-regime/analyze-asset?${params}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка анализа актива: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить название типа режима на русском.
 */
export function getRegimeTypeName(type: string): string {
  const types: { [key: string]: string } = {
    'Noise': 'Шум',
    'Transient': 'Переходный',
    'Normal': 'Нормальный',
    'Stress': 'Стрессовый',
    'Crisis': 'Кризисный'
  }
  return types[type] || type
}

/**
 * Получить цвет для типа режима.
 */
export function getRegimeTypeColor(type: string): string {
  const colors: { [key: string]: string } = {
    'Noise': '#94a3b8',      // Серый
    'Transient': '#fbbf24',  // Жёлтый
    'Normal': '#4ade80',     // Зелёный
    'Stress': '#f97316',     // Оранжевый
    'Crisis': '#ef4444'      // Красный
  }
  return colors[type] || '#3b82f6'
}

/**
 * Получить цвет для индекса режима.
 */
export function getRegimeColor(index: number): string {
  const colors = [
    '#3b82f6',  // Синий
    '#4ade80',  // Зелёный
    '#f97316',  // Оранжевый
    '#ef4444',  // Красный
    '#a855f7',  // Фиолетовый
    '#06b6d4',  // Бирюзовый
    '#f43f5e',  // Розовый
  ]
  return colors[index % colors.length]
}

/**
 * Форматирование длительности режима.
 */
export function formatDuration(days: number): string {
  if (!isFinite(days) || days <= 0) return 'N/A'
  if (days < 1) return '< 1 дня'
  if (days < 7) return `${days.toFixed(1)} дн.`
  if (days < 30) return `${(days / 7).toFixed(1)} нед.`
  if (days < 365) return `${(days / 30).toFixed(1)} мес.`
  return `${(days / 365).toFixed(1)} лет`
}
