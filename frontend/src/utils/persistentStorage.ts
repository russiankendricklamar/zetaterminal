/**
 * Persistent storage abstraction.
 *
 * Problem: Tauri's WKWebView (macOS) may clear localStorage between app restarts.
 * Solution: On desktop, mirror all auth-critical keys to tauri-plugin-store (disk-backed).
 *
 * Strategy (hybrid):
 *   - Reads:  always from localStorage (sync, zero-latency).
 *   - Writes: localStorage + Tauri Store (async fire-and-forget).
 *   - Init:   load Tauri Store → populate localStorage (restores tokens on cold start).
 *
 * In browser mode, this is a no-op wrapper around localStorage.
 */

import { isTauri } from '@/utils/apiBase'

const STORE_FILE = 'auth.json'

/** Keys that must survive app restarts */
const PERSISTED_KEYS = [
  'zeta_access_token',
  'zeta_refresh_token',
  'zeta_auth_user',
] as const

type PersistedKey = (typeof PERSISTED_KEYS)[number]

interface TauriStore {
  get: <T>(key: string) => Promise<T | null>
  set: (key: string, value: unknown) => Promise<void>
  delete: (key: string) => Promise<boolean>
  save: () => Promise<void>
}

let _store: TauriStore | null = null
let _initPromise: Promise<void> | null = null

async function loadStore(): Promise<TauriStore> {
  const { load } = await import('@tauri-apps/plugin-store')
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return await load(STORE_FILE, { autoSave: false } as any) as unknown as TauriStore
}

/**
 * Initialize persistent storage. Must be called once at app startup.
 * In browser mode, resolves immediately.
 */
export function initPersistentStorage(): Promise<void> {
  if (!isTauri()) return Promise.resolve()
  if (_initPromise) return _initPromise

  _initPromise = _doInit()
  return _initPromise
}

async function _doInit(): Promise<void> {
  try {
    _store = await loadStore()

    // Restore persisted keys into localStorage
    for (const key of PERSISTED_KEYS) {
      const value = await _store.get<string>(key)
      if (value !== null && value !== undefined) {
        localStorage.setItem(key, value)
      }
    }
  } catch {
    // Store unavailable — fall back to localStorage only
    _store = null
  }
}

/**
 * Write a persisted key. Updates both localStorage and Tauri Store.
 */
export function persistSet(key: PersistedKey, value: string): void {
  localStorage.setItem(key, value)

  if (_store) {
    _store.set(key, value).then(() => _store?.save()).catch(() => {})
  }
}

/**
 * Remove a persisted key from both storages.
 */
export function persistRemove(key: PersistedKey): void {
  localStorage.removeItem(key)

  if (_store) {
    _store.delete(key).then(() => _store?.save()).catch(() => {})
  }
}

/**
 * Clear all persisted auth keys.
 */
export function persistClearAll(): void {
  for (const key of PERSISTED_KEYS) {
    persistRemove(key)
  }
}
