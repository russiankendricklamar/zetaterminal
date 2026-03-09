const STORAGE_KEY = 'zeta_backend_url'
const PRODUCTION_URL = 'https://zetaterminal.onrender.com'
const BUILD_TIME_DEFAULT = import.meta.env.VITE_API_BASE_URL || PRODUCTION_URL

export function getApiBaseUrl(): string {
  const override = localStorage.getItem(STORAGE_KEY)
  return override !== null ? override : BUILD_TIME_DEFAULT
}

export function setApiBaseUrl(url: string): void {
  url ? localStorage.setItem(STORAGE_KEY, url) : localStorage.removeItem(STORAGE_KEY)
}

export function isTauri(): boolean {
  return '__TAURI_INTERNALS__' in window
}
