/**
 * Crypto Data Service — CoinGecko, CoinGap
 *
 * Proxied through backend at /api/crypto-data/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface CoinMarket {
  id: string
  symbol: string
  name: string
  image: string
  current_price: number
  market_cap: number
  market_cap_rank: number
  total_volume: number
  high_24h: number
  low_24h: number
  price_change_24h: number
  price_change_percentage_24h: number
  price_change_percentage_1h_in_currency?: number
  price_change_percentage_7d_in_currency?: number
  sparkline_in_7d?: { price: number[] }
}

export interface CoinDetails {
  id: string
  symbol: string
  name: string
  description: string
  image: string
  market_data: Record<string, unknown>
  market_cap_rank: number
  genesis_date: string
  provider: string
}

export interface MarketChart {
  coin_id: string
  vs_currency: string
  prices: [number, number][]
  market_caps: [number, number][]
  total_volumes: [number, number][]
  provider: string
}

export interface GlobalStats {
  active_cryptocurrencies: number
  markets: number
  total_market_cap: Record<string, number>
  total_volume: Record<string, number>
  market_cap_percentage: Record<string, number>
  market_cap_change_percentage_24h_usd: number
  provider: string
}

export interface ArbitrageOpportunity {
  [key: string]: unknown
}

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

export async function getCoinGeckoMarkets(
  vsCurrency: string = 'usd',
  perPage: number = 100,
  page: number = 1
): Promise<CoinMarket[]> {
  return fetchJson(`${API_BASE}/api/crypto-data/coingecko/markets?vs_currency=${vsCurrency}&per_page=${perPage}&page=${page}`)
}

export async function getCoinDetails(coinId: string): Promise<CoinDetails> {
  return fetchJson(`${API_BASE}/api/crypto-data/coingecko/coin/${encodeURIComponent(coinId)}`)
}

export async function getCoinChart(
  coinId: string,
  vsCurrency: string = 'usd',
  days: number = 30
): Promise<MarketChart> {
  return fetchJson(`${API_BASE}/api/crypto-data/coingecko/coin/${encodeURIComponent(coinId)}/chart?vs_currency=${vsCurrency}&days=${days}`)
}

export async function getTrendingCoins(): Promise<Record<string, unknown>> {
  return fetchJson(`${API_BASE}/api/crypto-data/coingecko/trending`)
}

export async function getGlobalStats(): Promise<GlobalStats> {
  return fetchJson(`${API_BASE}/api/crypto-data/coingecko/global`)
}

export async function getArbitrageOpportunities(): Promise<ArbitrageOpportunity[]> {
  return fetchJson(`${API_BASE}/api/crypto-data/coingap/arbitrage`)
}
