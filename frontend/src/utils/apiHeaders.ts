import { persistSet, persistRemove, persistClearAll } from '@/utils/persistentStorage'

const ACCESS_TOKEN_KEY = 'zeta_access_token'
const REFRESH_TOKEN_KEY = 'zeta_refresh_token'

export function getApiHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

export function setTokens(accessToken: string, refreshToken: string): void {
  persistSet('zeta_access_token', accessToken)
  persistSet('zeta_refresh_token', refreshToken)
}

export function getRefreshToken(): string {
  return localStorage.getItem(REFRESH_TOKEN_KEY) || ''
}

export function clearTokens(): void {
  persistClearAll()
}

// Backward-compatible wrappers
export function getApiKey(): string {
  return localStorage.getItem(ACCESS_TOKEN_KEY) || ''
}

export function setApiKey(key: string): void {
  if (key) {
    persistSet('zeta_access_token', key)
  } else {
    persistRemove('zeta_access_token')
  }
}

export function setAccessToken(token: string): void {
  persistSet('zeta_access_token', token)
}
