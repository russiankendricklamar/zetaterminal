/**
 * DaData Service — Russian company and bank data.
 *
 * Proxied through backend at /api/dadata/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface DaDataCompany {
  inn: string
  ogrn: string
  kpp: string
  name: string
  full_name: string
  short_name: string
  type: string
  status: string
  registration_date: number | null
  okved: string
  okved_type: string
  management_name: string
  management_post: string
  address: string
  capital: number | null
  employees: number | null
}

export interface DaDataCompanyResponse {
  query: string
  companies: DaDataCompany[]
  provider: string
}

export interface DaDataSuggestion {
  inn: string
  ogrn: string
  name: string
  type: string
  status: string
  address: string
}

export interface DaDataSuggestResponse {
  query: string
  suggestions: DaDataSuggestion[]
  provider: string
}

export interface DaDataBank {
  bik: string
  name: string
  full_name: string
  correspondent_account: string
  registration_number: string
  swift: string
  inn: string
  kpp: string
  address: string
  status: string
}

export interface DaDataBankResponse {
  query: string
  banks: DaDataBank[]
  provider: string
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

export async function findCompany(inn: string): Promise<DaDataCompanyResponse> {
  return fetchJson(`${API_BASE}/api/dadata/company/${encodeURIComponent(inn)}`)
}

export async function suggestCompany(query: string, count: number = 10): Promise<DaDataSuggestResponse> {
  return fetchJson(`${API_BASE}/api/dadata/suggest/company?q=${encodeURIComponent(query)}&count=${count}`)
}

export async function findBank(bik: string): Promise<DaDataBankResponse> {
  return fetchJson(`${API_BASE}/api/dadata/suggest/bank?bik=${encodeURIComponent(bik)}`)
}
