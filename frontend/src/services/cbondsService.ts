/**
 * Сервис для работы с Cbonds API.
 *
 * Документация: https://data.cbonds.info/files/api/API_documentation_eng.pdf
 * Каталог операций: https://cbonds.ru/api/catalog/folders/
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API_BASE = getApiBaseUrl()

// Типы

export interface CbondsCredentials {
  login: string
  password: string
}

export interface SessionResponse {
  success: boolean
  message: string
  session_id?: string
  login?: string
}

export interface CbondsResponse<T = Record<string, any>> {
  success: boolean
  data: T[]
  count: number
  total: number
  error?: string
  message?: string
}

// Session ID in memory only (cleared on page refresh)
let _sessionId: string | null = null
let _sessionLogin: string | null = null

/**
 * Authenticate with Cbonds and cache credentials server-side.
 */
export async function createSession(credentials: CbondsCredentials): Promise<SessionResponse> {
  const response = await fetch(`${API_BASE}/api/cbonds/session/create`, {
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

export function getSessionId(): string | null {
  return _sessionId
}

export function getSessionLogin(): string | null {
  return _sessionLogin
}

export function hasActiveSession(): boolean {
  return _sessionId !== null
}

export async function clearSession(): Promise<void> {
  if (_sessionId) {
    try {
      await fetch(`${API_BASE}/api/cbonds/session/clear`, {
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

/**
 * Test connection to Cbonds API (without creating session).
 */
export async function testConnection(credentials: CbondsCredentials): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE}/api/cbonds/test-connection`, {
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
 * Generic query to Cbonds API.
 */
export async function query(
  credentials: CbondsCredentials,
  operation: string,
  filters?: Array<{ field: string; operator: string; value: string }>,
  fields?: string[],
  limit = 100,
  offset = 0,
  lang = 'rus'
): Promise<CbondsResponse> {
  const response = await fetch(`${API_BASE}/api/cbonds/query`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({
      ...credentials,
      operation,
      filters,
      fields,
      limit,
      offset,
      lang
    })
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}

/**
 * Get emission reference data by ISIN.
 */
export async function getEmission(
  credentials: CbondsCredentials,
  isin: string,
  fields?: string[]
): Promise<CbondsResponse> {
  const response = await fetch(`${API_BASE}/api/cbonds/emission`, {
    method: 'POST',
    headers: getApiHeaders(),
    body: JSON.stringify({ ...credentials, isin, fields })
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }))
    throw new Error(error.detail || `Ошибка: ${response.status}`)
  }

  return response.json()
}
