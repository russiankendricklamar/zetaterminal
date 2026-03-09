/**
 * Сервис для работы с RuData (Interfax) API.
 *
 * Документация API: https://docs.efir-net.ru/dh2/#/
 */

import { getApiHeaders } from '@/utils/apiHeaders'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

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

// Server-side session management (no localStorage credential storage)

export interface SessionResponse {
  success: boolean
  message: string
  session_id?: string
  login?: string
}

// Session ID is kept in memory only (cleared on page refresh)
let _sessionId: string | null = null
let _sessionLogin: string | null = null

/**
 * Authenticate with RuData and cache credentials server-side.
 * Returns session info; stores session_id in memory.
 */
export async function createSession(credentials: RuDataCredentials): Promise<SessionResponse> {
  const response = await fetch(`${API_BASE}/api/rudata/session/create`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify(credentials)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  const result: SessionResponse = await response.json()

  if (result.success && result.session_id) {
    _sessionId = result.session_id
    _sessionLogin = result.login ?? credentials.login
  }

  return result
}

/**
 * Get the current server-side session ID (memory-only).
 */
export function getSessionId(): string | null {
  return _sessionId
}

/**
 * Get the login associated with the current session.
 */
export function getSessionLogin(): string | null {
  return _sessionLogin
}

/**
 * Check if a server session is active.
 */
export function hasActiveSession(): boolean {
  return _sessionId !== null
}

/**
 * Clear the server-side session and local reference.
 */
export async function clearSession(): Promise<void> {
  if (_sessionId) {
    try {
      await fetch(`${API_BASE}/api/rudata/session/clear`, {
        method: 'POST',
        headers: getApiHeaders(),
        body: JSON.stringify({ session_id: _sessionId })
      })
    } catch {
      // Best-effort cleanup
    }
  }
  _sessionId = null
  _sessionLogin = null
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

  /**
   * Create a session on the server, caching credentials server-side.
   */
  async createSession(): Promise<SessionResponse> {
    return createSession(this.credentials)
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

  /**
   * Clear the server-side session.
   */
  async clearSession(): Promise<void> {
    return clearSession()
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
  createSession,
  getSessionId,
  getSessionLogin,
  hasActiveSession,
  clearSession,
  RuDataClient
}
