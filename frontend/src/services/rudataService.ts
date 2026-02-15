/**
 * Сервис для работы с RuData (Interfax) API.
 *
 * Документация API: https://docs.efir-net.ru/dh2/#/
 */

import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Типы

export interface RuDataCredentials {
  login: string
  password: string
}

export interface ConnectionTestResponse {
  success: boolean
  message: string
  login?: string
}

export interface RuDataResponse<T = Record<string, any>> {
  success: boolean
  data: T[]
  count: number
  columns?: string[]
  error?: string
  message?: string
}

export interface RuDataQuery {
  login: string
  password: string
  path_method: string
  body?: Record<string, any>
  post?: boolean
  search_array?: string[]
  search_param?: string
  search_field?: string
}

export interface BondCalculateRequest {
  login: string
  password: string
  isin: string
  calc_date?: string
  price?: number
}

export interface BondSearchRequest {
  login: string
  password: string
  filter: string
  fields?: string[]
}

// Хранение credentials в localStorage

const STORAGE_KEY = 'rudata_credentials'

export function saveCredentials(credentials: RuDataCredentials): void {
  // Сохраняем в base64 для минимальной обфускации
  const encoded = btoa(JSON.stringify(credentials))
  localStorage.setItem(STORAGE_KEY, encoded)
}

export function loadCredentials(): RuDataCredentials | null {
  const encoded = localStorage.getItem(STORAGE_KEY)
  if (!encoded) return null

  try {
    return JSON.parse(atob(encoded))
  } catch {
    return null
  }
}

export function clearCredentials(): void {
  localStorage.removeItem(STORAGE_KEY)
}

// API функции

/**
 * Проверить подключение к RuData API.
 */
export async function testConnection(credentials: RuDataCredentials): Promise<ConnectionTestResponse> {
  const response = await fetch(`${API_BASE}/api/rudata/test-connection`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(credentials)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}

/**
 * Выполнить произвольный запрос к RuData API.
 */
export async function executeQuery<T = Record<string, any>>(
  query: RuDataQuery
): Promise<RuDataResponse<T>> {
  const response = await fetch(`${API_BASE}/api/rudata/query`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({
      ...query,
      body: query.body || {},
      post: query.post ?? true,
      search_param: query.search_param || 'filter'
    })
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка запроса: ${response.status}`)
  }

  return response.json()
}

/**
 * Получить информацию об облигации по ISIN.
 */
export async function getBondInfo(
  credentials: RuDataCredentials,
  isin: string
): Promise<RuDataResponse> {
  const response = await fetch(`${API_BASE}/api/rudata/bond/info?isin=${encodeURIComponent(isin)}`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(credentials)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}

/**
 * Получить денежные потоки облигации.
 */
export async function getBondCashflows(
  credentials: RuDataCredentials,
  isin: string
): Promise<RuDataResponse> {
  const response = await fetch(`${API_BASE}/api/rudata/bond/cashflows?isin=${encodeURIComponent(isin)}`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(credentials)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}

/**
 * Рассчитать параметры облигации.
 */
export async function calculateBond(request: BondCalculateRequest): Promise<RuDataResponse> {
  const response = await fetch(`${API_BASE}/api/rudata/bond/calculate`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка расчета: ${response.status}`)
  }

  return response.json()
}

/**
 * Поиск облигаций по фильтру.
 */
export async function searchBonds(request: BondSearchRequest): Promise<RuDataResponse> {
  const response = await fetch(`${API_BASE}/api/rudata/bonds/search`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка поиска: ${response.status}`)
  }

  return response.json()
}

/**
 * Получить кривую бескупонной доходности (ZCYC) из RuData.
 */
export async function getZCYC(
  credentials: RuDataCredentials,
  date?: string
): Promise<RuDataResponse> {
  const params = new URLSearchParams()
  if (date) {
    params.append('date', date)
  }

  const url = `${API_BASE}/api/rudata/zcyc${params.toString() ? '?' + params.toString() : ''}`

  const response = await fetch(url, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(credentials)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}

/**
 * Получить справочные данные финансового инструмента.
 */
export async function getFintoolReference(
  credentials: RuDataCredentials,
  id: string,
  fields?: string[]
): Promise<RuDataResponse> {
  const params = new URLSearchParams({ id })
  if (fields) {
    fields.forEach(f => params.append('fields', f))
  }

  const response = await fetch(`${API_BASE}/api/rudata/fintool/reference?${params.toString()}`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(credentials)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}

/**
 * Класс-обертка для удобной работы с RuData API.
 */
export class RuDataClient {
  private credentials: RuDataCredentials

  constructor(credentials: RuDataCredentials) {
    this.credentials = credentials
  }

  static fromStorage(): RuDataClient | null {
    const credentials = loadCredentials()
    if (!credentials) return null
    return new RuDataClient(credentials)
  }

  async testConnection(): Promise<ConnectionTestResponse> {
    return testConnection(this.credentials)
  }

  async query<T = Record<string, any>>(
    pathMethod: string,
    body: Record<string, any> = {},
    options: Partial<Omit<RuDataQuery, 'login' | 'password' | 'path_method' | 'body'>> = {}
  ): Promise<RuDataResponse<T>> {
    return executeQuery<T>({
      ...this.credentials,
      path_method: pathMethod,
      body,
      ...options
    })
  }

  async getBondInfo(isin: string): Promise<RuDataResponse> {
    return getBondInfo(this.credentials, isin)
  }

  async getBondCashflows(isin: string): Promise<RuDataResponse> {
    return getBondCashflows(this.credentials, isin)
  }

  async calculateBond(isin: string, calcDate?: string, price?: number): Promise<RuDataResponse> {
    return calculateBond({
      ...this.credentials,
      isin,
      calc_date: calcDate,
      price
    })
  }

  async searchBonds(filter: string, fields?: string[]): Promise<RuDataResponse> {
    return searchBonds({
      ...this.credentials,
      filter,
      fields
    })
  }

  async getZCYC(date?: string): Promise<RuDataResponse> {
    return getZCYC(this.credentials, date)
  }

  async getFintoolReference(id: string, fields?: string[]): Promise<RuDataResponse> {
    return getFintoolReference(this.credentials, id, fields)
  }

  // Сохранить credentials
  save(): void {
    saveCredentials(this.credentials)
  }
}

// Экспорт по умолчанию
export default {
  testConnection,
  executeQuery,
  getBondInfo,
  getBondCashflows,
  calculateBond,
  searchBonds,
  getZCYC,
  getFintoolReference,
  saveCredentials,
  loadCredentials,
  clearCredentials,
  RuDataClient
}
