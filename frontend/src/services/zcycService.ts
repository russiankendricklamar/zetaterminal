/**
 * Сервис для работы с кривой бескупонных доходностей (КБД) из MOEX ISS API.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ZCYCPoint {
  term: number
  value: number
}

export interface ZCYCResponse {
  status: string
  date: string
  data: ZCYCPoint[]
  count: number
  min_term: number
  max_term: number
  min_rate: number
  max_rate: number
  mean_rate: number
  error?: string
}

export interface InterpolateResponse {
  term: number
  value: number
  method: string
  interpolated: boolean
}

/**
 * Получить кривую бескупонных доходностей на указанную дату.
 */
export async function getZCYC(date?: string): Promise<ZCYCResponse> {
  const params = new URLSearchParams()
  if (date) {
    params.append('date', date)
  }
  
  const url = `${API_BASE}/api/zcyc${params.toString() ? '?' + params.toString() : ''}`
  
  const response = await fetch(url)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения кривой: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Интерполировать доходность для заданного срока.
 */
export async function interpolateZCYC(
  term: number,
  method: 'linear' | 'nelson_siegel' = 'linear',
  date?: string
): Promise<InterpolateResponse> {
  const params = new URLSearchParams({
    term: term.toString(),
    method
  })
  
  if (date) {
    params.append('date', date)
  }
  
  const response = await fetch(`${API_BASE}/api/zcyc/interpolate?${params.toString()}`, {
    method: 'POST'
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка интерполяции: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить список доступных дат.
 */
export async function getAvailableDates(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/zcyc/dates`)
  
  if (!response.ok) {
    throw new Error(`Ошибка получения списка дат: ${response.status}`)
  }
  
  const data = await response.json()
  return data.dates || []
}
