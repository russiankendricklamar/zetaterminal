/**
 * Market Feeds Service — Alpha Vantage, Twelve Data, Polygon.io
 *
 * Proxied through backend at /api/market-feeds/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

// ─── Types ───────────────────────────────────────────────────────────────────

export interface QuoteData {
  symbol: string
  price: number
  open: number
  high: number
  low: number
  volume: number
  change: number
  change_percent?: string
  percent_change?: number
  previous_close: number
  latest_trading_day?: string
  name?: string
  exchange?: string
  datetime?: string
  provider: string
}

export interface OhlcvBar {
  date?: string
  timestamp?: number
  open: number
  high: number
  low: number
  close: number
  volume: number
  vwap?: number
  num_transactions?: number
}

export interface TimeSeriesData {
  symbol?: string
  ticker?: string
  interval?: string
  series: OhlcvBar[]
  provider: string
}

export interface FxRate {
  from: string
  to: string
  rate: number
  last_refreshed: string
  provider: string
}

export interface TechnicalPoint {
  date: string
  [key: string]: string | number
}

export interface TechnicalData {
  symbol: string
  indicator: string
  interval: string
  time_period: number
  data: TechnicalPoint[]
  provider: string
}

export interface TickerDetails {
  ticker?: string
  name?: string
  market?: string
  locale?: string
  primary_exchange?: string
  type?: string
  currency_name?: string
  market_cap?: number
  provider: string
}

export interface OptionsContract {
  ticker: string
  contracts: Record<string, unknown>[]
  provider: string
}

export interface PolygonNewsArticle {
  id: string
  title: string
  author: string
  published_utc: string
  article_url: string
  tickers: string[]
  description: string
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

// ─── Alpha Vantage ───────────────────────────────────────────────────────────

export async function getAlphaVantageQuote(symbol: string): Promise<QuoteData> {
  return fetchJson(`${API_BASE}/api/market-feeds/alpha-vantage/quote?symbol=${encodeURIComponent(symbol)}`)
}

export async function getAlphaVantageTimeSeries(
  symbol: string,
  interval: string = 'daily',
  outputsize: string = 'compact'
): Promise<TimeSeriesData> {
  return fetchJson(`${API_BASE}/api/market-feeds/alpha-vantage/time-series?symbol=${encodeURIComponent(symbol)}&interval=${interval}&outputsize=${outputsize}`)
}

export async function getAlphaVantageForex(from: string, to: string): Promise<FxRate> {
  return fetchJson(`${API_BASE}/api/market-feeds/alpha-vantage/forex?from=${from}&to=${to}`)
}

export async function getAlphaVantageTechnicals(
  symbol: string,
  indicator: string = 'SMA',
  interval: string = 'daily',
  timePeriod: number = 20,
  seriesType: string = 'close'
): Promise<TechnicalData> {
  return fetchJson(`${API_BASE}/api/market-feeds/alpha-vantage/technicals?symbol=${encodeURIComponent(symbol)}&indicator=${indicator}&interval=${interval}&time_period=${timePeriod}&series_type=${seriesType}`)
}

// ─── Twelve Data ─────────────────────────────────────────────────────────────

export async function getTwelveDataQuote(symbol: string): Promise<QuoteData> {
  return fetchJson(`${API_BASE}/api/market-feeds/twelve-data/quote?symbol=${encodeURIComponent(symbol)}`)
}

export async function getTwelveDataTimeSeries(
  symbol: string,
  interval: string = '1day',
  outputsize: number = 30
): Promise<TimeSeriesData> {
  return fetchJson(`${API_BASE}/api/market-feeds/twelve-data/time-series?symbol=${encodeURIComponent(symbol)}&interval=${interval}&outputsize=${outputsize}`)
}

export async function getTwelveDataForexPairs(): Promise<Array<{ symbol: string; currency_group: string; currency_base: string; currency_quote: string }>> {
  return fetchJson(`${API_BASE}/api/market-feeds/twelve-data/forex-pairs`)
}

// ─── Polygon.io ──────────────────────────────────────────────────────────────

export async function getPolygonTickerDetails(ticker: string): Promise<TickerDetails> {
  return fetchJson(`${API_BASE}/api/market-feeds/polygon/ticker/${encodeURIComponent(ticker)}`)
}

export async function getPolygonAggregates(
  ticker: string,
  from: string,
  to: string,
  timespan: string = 'day',
  multiplier: number = 1
): Promise<TimeSeriesData> {
  return fetchJson(`${API_BASE}/api/market-feeds/polygon/aggs/${encodeURIComponent(ticker)}?from=${from}&to=${to}&timespan=${timespan}&multiplier=${multiplier}`)
}

export async function getPolygonOptionsChain(
  ticker: string,
  expirationDate?: string,
  strikePrice?: number,
  contractType?: string,
  limit: number = 50
): Promise<OptionsContract> {
  let url = `${API_BASE}/api/market-feeds/polygon/options/${encodeURIComponent(ticker)}?limit=${limit}`
  if (expirationDate) url += `&expiration_date=${expirationDate}`
  if (strikePrice) url += `&strike_price=${strikePrice}`
  if (contractType) url += `&contract_type=${contractType}`
  return fetchJson(url)
}

export async function getPolygonNews(ticker?: string, limit: number = 20): Promise<PolygonNewsArticle[]> {
  let url = `${API_BASE}/api/market-feeds/polygon/news?limit=${limit}`
  if (ticker) url += `&ticker=${encodeURIComponent(ticker)}`
  return fetchJson(url)
}
