import { getApiHeaders, setApiKey } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

const API_BASE_URL = getApiBaseUrl()

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface RegisterResponse {
  username: string
  domain_handle: string
  status: string
  message: string
}

export interface ActivateRequest {
  code: string
}

export interface ActivateResponse {
  username: string
  status: string
  message: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  username: string
  domain_handle: string
  role: string
  api_key: string
}

export interface UserInfo {
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

const AUTH_USER_KEY = 'zeta_auth_user'

const MAX_RETRIES = 2
const RETRY_DELAY_MS = 3000

function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError && String(error.message).toLowerCase().includes('load failed')) {
    return true
  }
  if (error instanceof TypeError && String(error.message).toLowerCase().includes('failed to fetch')) {
    return true
  }
  return false
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function fetchWithRetry(
  url: string,
  options: RequestInit,
  fallbackDetail: string,
): Promise<Response> {
  let lastError: unknown
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(url, options)
      return res
    } catch (error: unknown) {
      lastError = error
      if (isNetworkError(error) && attempt < MAX_RETRIES) {
        await delay(RETRY_DELAY_MS)
        continue
      }
      break
    }
  }
  if (isNetworkError(lastError)) {
    throw new Error('Сервер запускается, попробуйте через несколько секунд')
  }
  throw new Error(fallbackDetail)
}

export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  const res = await fetchWithRetry(
    `${API_BASE_URL}/api/auth/register`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    },
    'Registration failed',
  )
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }))
    throw new Error(err.detail || 'Registration failed')
  }
  return res.json()
}

export async function activate(code: string): Promise<ActivateResponse> {
  const res = await fetchWithRetry(
    `${API_BASE_URL}/api/auth/activate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    },
    'Activation failed',
  )
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Activation failed' }))
    throw new Error(err.detail || 'Activation failed')
  }
  return res.json()
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await fetchWithRetry(
    `${API_BASE_URL}/api/auth/login`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    },
    'Login failed',
  )
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Login failed' }))
    throw new Error(err.detail || 'Login failed')
  }
  const result: LoginResponse = await res.json()
  setApiKey(result.api_key)
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify({
    username: result.username,
    domain_handle: result.domain_handle,
    role: result.role,
  }))
  return result
}

export async function fetchUsers(): Promise<UserInfo[]> {
  const res = await fetchWithRetry(
    `${API_BASE_URL}/api/auth/users`,
    { headers: getApiHeaders() },
    'Failed to fetch users',
  )
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to fetch users' }))
    throw new Error(err.detail || 'Failed to fetch users')
  }
  return res.json()
}

export function getAuthUser(): { username: string; domain_handle: string; role: string } | null {
  const raw = localStorage.getItem(AUTH_USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function logout(): void {
  setApiKey('')
  localStorage.removeItem(AUTH_USER_KEY)
}

export function isAdmin(): boolean {
  const user = getAuthUser()
  return user?.role === 'admin'
}
