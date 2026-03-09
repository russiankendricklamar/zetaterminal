/**
 * Admin panel API service.
 */
import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API = () => getApiBaseUrl()

function getAdminHeaders(): Record<string, string> {
  const headers = getApiHeaders()
  try {
    const raw = localStorage.getItem('zeta_auth_user')
    if (raw) {
      const user = JSON.parse(raw)
      if (user.username) {
        headers['X-Username'] = user.username
      }
    }
  } catch { /* ignore */ }
  return headers
}

// ── Interfaces ──────────────────────────────────────────────────────────────

export interface AdminUser {
  id: number
  username: string
  domain_handle: string
  email: string
  display_name: string | null
  role: string
  status: string
  invite_code: string
  created_at: string
  activated_at: string | null
}

export interface ServiceHealth {
  name: string
  url?: string
  status: string
  http_status?: number | null
  response_ms: number
  error?: string
}

export interface HealthResponse {
  services: ServiceHealth[]
  checked_at: number
}

export interface RequestRecord {
  request_id: string
  method: string
  path: string
  status_code: number
  duration_ms: number
  client_ip: string
  timestamp: number
}

export interface ActiveRequest {
  request_id: string
  method: string
  path: string
  client_ip: string
  elapsed_ms: number
}

export interface ErrorRecord {
  request_id: string
  method: string
  path: string
  status_code: number
  error: string
  traceback_short: string
  client_ip: string
  timestamp: number
}

export interface SystemInfo {
  python_version: string
  platform: string
  uptime_seconds: number
  db_pool: {
    size: number
    checked_in: number
    checked_out: number
    overflow: number
  }
  memory_mb: number
}

export interface IpBanRecord {
  id: number
  ip_address: string
  reason: string | null
  banned_by: string | null
  created_at: string
}

// ── API calls ───────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const resp = await fetch(`${API()}/api/admin${path}`, {
    headers: getAdminHeaders(),
    ...options,
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: `HTTP ${resp.status}` }))
    throw new Error(err.detail || `HTTP ${resp.status}`)
  }
  return resp.json()
}

export const fetchUsers = (): Promise<AdminUser[]> =>
  apiFetch('/users')

export const updateUserStatus = (userId: number, status: string): Promise<{ id: number; username: string; status: string }> =>
  apiFetch(`/users/${userId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status }),
  })

export const updateUserRole = (userId: number, role: string): Promise<{ id: number; username: string; role: string }> =>
  apiFetch(`/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  })

export const fetchHealth = (): Promise<HealthResponse> =>
  apiFetch('/health')

export const fetchRequests = (params?: {
  limit?: number
  status_code?: number
  path_contains?: string
}): Promise<RequestRecord[]> => {
  const qs = new URLSearchParams()
  if (params?.limit) qs.set('limit', String(params.limit))
  if (params?.status_code) qs.set('status_code', String(params.status_code))
  if (params?.path_contains) qs.set('path_contains', params.path_contains)
  const query = qs.toString()
  return apiFetch(`/requests${query ? `?${query}` : ''}`)
}

export const fetchActiveRequests = (): Promise<ActiveRequest[]> =>
  apiFetch('/requests/active')

export const cancelRequest = (requestId: string): Promise<{ cancelled: boolean }> =>
  apiFetch(`/requests/${requestId}/cancel`, { method: 'POST' })

export const fetchErrors = (limit = 50): Promise<ErrorRecord[]> =>
  apiFetch(`/errors?limit=${limit}`)

export const fetchSystemInfo = (): Promise<SystemInfo> =>
  apiFetch('/system')

export const kickUser = (userId: number): Promise<{ id: number; username: string; kicked: boolean }> =>
  apiFetch(`/users/${userId}/kick`, { method: 'POST' })

export const banUser = (userId: number): Promise<{ id: number; username: string; status: string; banned: boolean }> =>
  apiFetch(`/users/${userId}/ban`, { method: 'POST' })

export const fetchIpBans = (): Promise<IpBanRecord[]> =>
  apiFetch('/ip-bans')

export const createIpBan = (ip_address: string, reason?: string): Promise<{ ip_address: string; banned: boolean }> =>
  apiFetch('/ip-ban', {
    method: 'POST',
    body: JSON.stringify({ ip_address, reason }),
  })

export const deleteIpBan = (ip: string): Promise<{ ip_address: string; unbanned: boolean }> =>
  apiFetch(`/ip-ban/${encodeURIComponent(ip)}`, { method: 'DELETE' })

export const fetchUserIpInfo = (userId: number): Promise<{ user_id: number; username: string; last_ip: string | null }> =>
  apiFetch(`/users/${userId}/ip-info`)
