const STORAGE_KEY = 'zeta_backend_url'
const PRODUCTION_URL = 'https://zeta-terminal-backend.onrender.com'
const BUILD_TIME_DEFAULT = import.meta.env.VITE_API_BASE_URL || PRODUCTION_URL

// Allowed backend hosts (dev override only)
const ALLOWED_HOSTS = [
  'localhost',
  '127.0.0.1',
  'zeta-terminal-backend.onrender.com',
]

function isAllowedUrl(raw: string): boolean {
  try {
    const parsed = new URL(raw)
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return false
    return ALLOWED_HOSTS.includes(parsed.hostname)
  } catch {
    return false
  }
}

export function getApiBaseUrl(): string {
  if (import.meta.env.DEV) {
    const override = localStorage.getItem(STORAGE_KEY)
    if (override !== null && isAllowedUrl(override)) return override
  }
  return BUILD_TIME_DEFAULT
}

export function setApiBaseUrl(url: string): boolean {
  if (!url) {
    localStorage.removeItem(STORAGE_KEY)
    return true
  }
  if (!isAllowedUrl(url)) return false
  localStorage.setItem(STORAGE_KEY, url)
  return true
}

export function isTauri(): boolean {
  return '__TAURI_INTERNALS__' in window
}
