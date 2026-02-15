/**
 * Macro Data Service — FRED, Frankfurter (ECB), Bank of Russia, SEC EDGAR, OpenFIGI
 *
 * Proxied through backend at /api/macro-data/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// ─── Types ───────────────────────────────────────────────────────────────────

export interface FredObservation {
  date: string
  value: number | null
}

export interface FredSeriesData {
  series_id: string
  count: number
  observations: FredObservation[]
  provider: string
}

export interface FredSeriesInfo {
  id: string
  title: string
  frequency: string
  units: string
  observation_start: string
  observation_end: string
  popularity: number
}

export interface FredSearchResult {
  query: string
  series: FredSeriesInfo[]
  provider: string
}

export interface EcbRates {
  base: string
  date: string
  rates: Record<string, number>
  provider: string
}

export interface EcbHistoricalRates {
  base: string
  start_date: string
  end_date: string
  rates: Record<string, Record<string, number>>
  provider: string
}

export interface CbrRate {
  num_code: string
  char_code: string
  nominal: number
  name: string
  value: number
  vunit_rate: number
}

export interface CbrDailyRates {
  date: string
  rates: CbrRate[]
  provider: string
}

export interface CbrKeyRate {
  current_rate: number
  history: Array<{ date: string; rate: number }>
  provider: string
}

export interface SecFiling {
  form: string
  filing_date: string
  description: string
  accession_number: string
}

export interface SecCompanyFilings {
  cik: string
  name: string
  tickers: string[]
  exchanges: string[]
  sic: string
  sic_description: string
  filings: SecFiling[]
  provider: string
}

export interface SecCompanyFacts {
  cik: string
  entity_name: string
  facts: Record<string, unknown>
  provider: string
}

export interface OpenFigiJob {
  idType: string
  idValue: string
  exchCode?: string
  micCode?: string
  currency?: string
}

export interface OpenFigiResult {
  data?: Array<{
    figi: string
    name: string
    ticker: string
    exchCode: string
    compositeFIGI: string
    securityType: string
    marketSector: string
  }>
  error?: string
}

// ─── Helper ──────────────────────────────────────────────────────────────────

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

// ─── FRED ────────────────────────────────────────────────────────────────────

export async function getFredSeries(
  seriesId: string,
  limit: number = 100,
  sortOrder: string = 'desc',
  observationStart?: string,
  observationEnd?: string
): Promise<FredSeriesData> {
  let url = `${API_BASE}/api/macro-data/fred/series?series_id=${encodeURIComponent(seriesId)}&limit=${limit}&sort_order=${sortOrder}`
  if (observationStart) url += `&observation_start=${observationStart}`
  if (observationEnd) url += `&observation_end=${observationEnd}`
  return fetchJson(url)
}

export async function searchFredSeries(query: string, limit: number = 20): Promise<FredSearchResult> {
  return fetchJson(`${API_BASE}/api/macro-data/fred/search?q=${encodeURIComponent(query)}&limit=${limit}`)
}

// ─── Frankfurter (ECB) ──────────────────────────────────────────────────────

export async function getEcbLatestRates(base: string = 'EUR'): Promise<EcbRates> {
  return fetchJson(`${API_BASE}/api/macro-data/ecb/latest?base=${base}`)
}

export async function getEcbHistoricalRates(
  base: string = 'EUR',
  start: string = '2024-01-01',
  end?: string,
  symbols?: string
): Promise<EcbHistoricalRates> {
  let url = `${API_BASE}/api/macro-data/ecb/history?base=${base}&start=${start}`
  if (end) url += `&end=${end}`
  if (symbols) url += `&symbols=${symbols}`
  return fetchJson(url)
}

// ─── Bank of Russia ─────────────────────────────────────────────────────────

export async function getCbrRates(): Promise<CbrDailyRates> {
  return fetchJson(`${API_BASE}/api/macro-data/cbr/rates`)
}

export async function getCbrKeyRate(): Promise<CbrKeyRate> {
  return fetchJson(`${API_BASE}/api/macro-data/cbr/key-rate`)
}

// ─── SEC EDGAR ──────────────────────────────────────────────────────────────

export async function getSecFilings(cik: string): Promise<SecCompanyFilings> {
  return fetchJson(`${API_BASE}/api/macro-data/sec/filings/${encodeURIComponent(cik)}`)
}

export async function getSecCompanyFacts(cik: string): Promise<SecCompanyFacts> {
  return fetchJson(`${API_BASE}/api/macro-data/sec/company-facts/${encodeURIComponent(cik)}`)
}

// ─── OpenFIGI ───────────────────────────────────────────────────────────────

export async function mapOpenFigi(jobs: OpenFigiJob[]): Promise<OpenFigiResult[]> {
  return postJson(`${API_BASE}/api/macro-data/openfigi/map`, jobs)
}
