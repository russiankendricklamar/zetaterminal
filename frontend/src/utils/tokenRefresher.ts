/**
 * Low-level token refresh primitive.
 *
 * Shared by sessionManager (auto-refresh) and authService (manual refresh).
 * Avoids circular dependencies by not importing from authService.
 */

import { getRefreshToken, setTokens } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'
import { appFetch } from '@/utils/tauriFetch'

/**
 * Exchange the stored refresh token for a new access + refresh token pair.
 * Returns the new access token, or null if refresh failed.
 */
export async function refreshTokenPair(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return null

  try {
    const res = await appFetch(`${getApiBaseUrl()}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!res.ok) return null
    const data = await res.json()
    setTokens(data.access_token, data.refresh_token)
    return data.access_token
  } catch {
    return null
  }
}
