const API_KEY_STORAGE_KEY = 'zeta_api_key'

export function getApiHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  const apiKey = localStorage.getItem(API_KEY_STORAGE_KEY)
  if (apiKey) {
    headers['X-API-Key'] = apiKey
  }
  return headers
}

export function getApiKey(): string {
  return localStorage.getItem(API_KEY_STORAGE_KEY) || ''
}

export function setApiKey(key: string): void {
  if (key) {
    localStorage.setItem(API_KEY_STORAGE_KEY, key)
  } else {
    localStorage.removeItem(API_KEY_STORAGE_KEY)
  }
}
