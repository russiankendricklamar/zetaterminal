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
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
}

export function getRefreshToken(): string {
  return localStorage.getItem(REFRESH_TOKEN_KEY) || ''
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

// Backward-compatible wrappers
export function getApiKey(): string {
  return localStorage.getItem(ACCESS_TOKEN_KEY) || ''
}

export function setApiKey(key: string): void {
  if (key) {
    localStorage.setItem(ACCESS_TOKEN_KEY, key)
  } else {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
  }
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}
