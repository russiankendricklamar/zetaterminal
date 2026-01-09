export enum OrderSide {
  BUY = 'BUY',
  SELL = 'SELL'
}

export enum OrderType {
  LIMIT = 'LIMIT',
  MARKET = 'MARKET'
}

export interface Candle {
  time: string; // ISO string or time label
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OrderBookItem {
  price: number;
  amount: number;
  total: number;
}

export interface Trade {
  id: string;
  price: number;
  amount: number;
  time: string;
  side: OrderSide;
}

export interface Position {
  symbol: string;
  size: number;
  entryPrice: number;
  markPrice: number;
  pnl: number;
  pnlPercent: number;
  side: OrderSide;
}

export interface AIAnalysisResult {
  trend: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  reasoning: string;
  keyLevels: { support: number; resistance: number };
}

export interface AssetInfo {
    name: string;
    symbol: string;
    price: string;
    change: string;
    cap?: string;
    vol?: string;
    category?: string;
    region?: string;
    country?: string;
    sector?: string;
    high24h?: string;
    low24h?: string;
}

export interface SearchResult {
    id: string;
    label: string;
    type: 'asset' | 'command';
    code?: string; // e.g. "TOP" or "BTC"
    description?: string;
}
