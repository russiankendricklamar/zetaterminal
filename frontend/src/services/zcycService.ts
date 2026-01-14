/**
 * Сервис для работы с кривой бескупонных доходностей (КБД) из MOEX ISS API.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }))
      throw new Error(error.detail || `Ошибка получения кривой: ${response.status}`)
    }
    
    return response.json()
  } catch (error: any) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error(`Не удалось подключиться к серверу. Убедитесь, что бэкенд запущен на ${API_BASE}`)
    }
    throw error
  }
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

/**
 * Получить максимальные даты для кривой ZCYC.
 */
export async function getMaxDates(engine: string = 'stock') {
  const response = await fetch(`${API_BASE}/api/zcyc/maxdates?engine=${engine}`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения максимальных дат: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить кривую годовых доходностей (yearyields) для указанной даты.
 */
export async function getYearYields(date?: string, engine: string = 'stock') {
  const params = new URLSearchParams({ engine })
  if (date) {
    params.append('date', date)
  }
  
  const response = await fetch(`${API_BASE}/api/zcyc/yearyields?${params.toString()}`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения кривой доходностей: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить диапазон доступных дат для yearyields.
 */
export async function getYearYieldsDates(date?: string, engine: string = 'stock') {
  const params = new URLSearchParams({ engine })
  if (date) {
    params.append('date', date)
  }
  
  const response = await fetch(`${API_BASE}/api/zcyc/yearyields/dates?${params.toString()}`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения диапазона дат: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Получить последнюю доступную кривую доходностей.
 */
export async function getLatestCurve(engine: string = 'stock') {
  const response = await fetch(`${API_BASE}/api/zcyc/latest?engine=${engine}`)
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка получения последней кривой: ${response.status}`)
  }
  
  return response.json()
}

/**
 * Преобразовать кривую доходностей в discount curve.
 */
export async function curveToDiscount(
  data: Array<Record<string, any>>,
  colTerm: string = 'period',
  colYield: string = 'value'
) {
  const response = await fetch(`${API_BASE}/api/zcyc/discount?col_term=${colTerm}&col_yield=${colYield}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `Ошибка преобразования кривой: ${response.status}`)
  }
  
  return response.json()
}
