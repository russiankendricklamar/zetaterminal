import { getApiHeaders, setApiKey } from '@/utils/apiHeaders'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

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

export async function register(data: RegisterRequest): Promise<RegisterResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Registration failed' }))
    throw new Error(err.detail || 'Registration failed')
  }
  return res.json()
}

export async function activate(code: string): Promise<ActivateResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/activate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Activation failed' }))
    throw new Error(err.detail || 'Activation failed')
  }
  return res.json()
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
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
  const res = await fetch(`${API_BASE_URL}/api/auth/users`, {
    headers: getApiHeaders(),
  })
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
