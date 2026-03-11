/**
 * Session manager — auto-restore, auto-refresh, and session keep-alive.
 *
 * On app mount:
 * 1. If a refresh token exists, silently restore the session (get new access token).
 *    This also warms up the backend (replaces the /health warmup).
 * 2. Schedule periodic token refresh before the access token expires.
 *
 * The user stays logged in for up to 30 days without re-entering credentials.
 */

import { getRefreshToken, clearTokens } from '@/utils/apiHeaders'
import { refreshTokenPair } from '@/utils/tokenRefresher'

const REFRESH_INTERVAL_MS = 25 * 60 * 1000 // 25 min (access token lives 30 min)

let _refreshTimer: ReturnType<typeof setInterval> | null = null
let _restorePromise: Promise<boolean> | null = null
let _restored = false

/**
 * Try to restore the session using the stored refresh token.
 * Returns true if the session was restored, false otherwise.
 * Safe to call multiple times — deduplicates concurrent calls
 * and skips if already restored in this session.
 */
export function restoreSession(): Promise<boolean> {
  if (_restored) return Promise.resolve(true)
  if (_restorePromise) return _restorePromise

  _restorePromise = _doRestore().finally(() => {
    _restorePromise = null
  })
  return _restorePromise
}

async function _doRestore(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  const newAccessToken = await refreshTokenPair()
  if (!newAccessToken) {
    clearTokens()
    return false
  }

  _restored = true
  startAutoRefresh()
  return true
}

/**
 * Start periodic token refresh. Called after successful login or restore.
 */
export function startAutoRefresh(): void {
  stopAutoRefresh()
  _refreshTimer = setInterval(async () => {
    const result = await refreshTokenPair()
    if (!result) {
      stopAutoRefresh()
    }
  }, REFRESH_INTERVAL_MS)
}

/**
 * Stop periodic token refresh. Called on logout.
 */
export function stopAutoRefresh(): void {
  if (_refreshTimer) {
    clearInterval(_refreshTimer)
    _refreshTimer = null
  }
  _restored = false
}

/**
 * Check if the user has a potentially valid session (tokens exist).
 */
export function hasSession(): boolean {
  return !!getRefreshToken()
}
