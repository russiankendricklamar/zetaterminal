/**
 * ETF Data Service — Russian ETFs via MOEX, international via yfinance.
 *
 * Proxied through backend at /api/etf/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface EtfItem {
  ticker: string
  name: string
  isin: string
  currency: string
  prev_price: number | null
  last: number | null
  open: number | null
  high: number | null
  low: number | null
  volume: number | null
  value: number | null
  change: number | null
  change_pct: number | null
  update_time: string
  market: string
}

export interface EtfListResponse {
  etfs: EtfItem[]
  count: number
  provider: string
}

export interface EtfCandle {
  open: number | null
  close: number | null
  high: number | null
  low: number | null
  volume: number | null
  begin: string
  end: string
}

export interface EtfCandlesResponse {
  ticker: string
  interval: number
  candles: EtfCandle[]
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

export async function getEtfList(): Promise<EtfListResponse> {
  return fetchJson(`${API_BASE}/api/etf/list`)
}

export async function getEtfCandles(
  ticker: string,
  interval: number = 24,
  from?: string,
  till?: string,
  limit: number = 100
): Promise<EtfCandlesResponse> {
  let url = `${API_BASE}/api/etf/candles/${encodeURIComponent(ticker)}?interval=${interval}&limit=${limit}`
  if (from) url += `&from=${from}`
  if (till) url += `&till=${till}`
  return fetchJson(url)
}

export async function getPopularInternationalEtfs(): Promise<{ tickers: string[] }> {
  return fetchJson(`${API_BASE}/api/etf/popular-international`)
}
