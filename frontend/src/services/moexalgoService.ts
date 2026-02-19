/**
 * MOEX ISS Service — Russian stock market data.
 *
 * Proxied through backend at /api/moexalgo/*
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface MoexSecurity {
  secid: string
  name: string
  isin: string
  lot_size: number
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
}

export interface MoexSecuritiesResponse {
  board: string
  market: string
  engine: string
  securities: MoexSecurity[]
  provider: string
}

export interface MoexCandle {
  open: number | null
  close: number | null
  high: number | null
  low: number | null
  volume: number | null
  begin: string
  end: string
}

export interface MoexCandlesResponse {
  ticker: string
  board: string
  interval: number
  candles: MoexCandle[]
  provider: string
}

export interface MoexOrderbookResponse {
  ticker: string
  board: string
  bids: Array<{ price: number; quantity: number }>
  asks: Array<{ price: number; quantity: number }>
  provider: string
}

export interface MoexTradesResponse {
  ticker: string
  board: string
  trades: Array<{
    trade_no: number
    time: string
    price: number
    quantity: number
    value: number
    side: string
  }>
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

export async function getMoexSecurities(
  board: string = 'TQBR',
  market: string = 'shares',
  engine: string = 'stock',
  limit: number = 100
): Promise<MoexSecuritiesResponse> {
  return fetchJson(`${API_BASE}/api/moexalgo/securities?board=${board}&market=${market}&engine=${engine}&limit=${limit}`)
}

export async function getMoexCandles(
  ticker: string,
  board: string = 'TQBR',
  interval: number = 24,
  from?: string,
  till?: string,
  limit: number = 100
): Promise<MoexCandlesResponse> {
  let url = `${API_BASE}/api/moexalgo/candles/${encodeURIComponent(ticker)}?board=${board}&interval=${interval}&limit=${limit}`
  if (from) url += `&from=${from}`
  if (till) url += `&till=${till}`
  return fetchJson(url)
}

export async function getMoexOrderbook(ticker: string, board: string = 'TQBR'): Promise<MoexOrderbookResponse> {
  return fetchJson(`${API_BASE}/api/moexalgo/orderbook/${encodeURIComponent(ticker)}?board=${board}`)
}

export async function getMoexTrades(ticker: string, board: string = 'TQBR', limit: number = 50): Promise<MoexTradesResponse> {
  return fetchJson(`${API_BASE}/api/moexalgo/trades/${encodeURIComponent(ticker)}?board=${board}&limit=${limit}`)
}

export async function getMoexIndex(indexId: string = 'IMOEX', limit: number = 100): Promise<Record<string, unknown>> {
  return fetchJson(`${API_BASE}/api/moexalgo/index/${encodeURIComponent(indexId)}?limit=${limit}`)
}

export async function getMoexFuturesOI(ticker: string): Promise<Record<string, unknown>> {
  return fetchJson(`${API_BASE}/api/moexalgo/futures/oi/${encodeURIComponent(ticker)}`)
}
