/**
 * Сервис для работы с рыночными данными через yfinance API
 */

import { getApiHeaders } from '@/utils/apiHeaders'
import { getApiBaseUrl } from '@/utils/apiBase'

// В dev режиме используем относительные пути для работы через Vite proxy
// В production используем переменную окружения
const API_BASE_URL = getApiBaseUrl();

export interface StockInfo {
  ticker: string;
  name: string;
  symbol: string;
  price: number;
  previousClose: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  peRatio?: number;
  dividendYield?: number;
  sector?: string;
  industry?: string;
  currency: string;
  exchange?: string;
  country?: string;
  website?: string;
  description?: string;
  employees?: number;
  '52WeekHigh'?: number;
  '52WeekLow'?: number;
  beta?: number;
  forwardPE?: number;
  priceToBook?: number;
  earningsGrowth?: number;
  revenueGrowth?: number;
}

export interface StockHistoryPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  adjClose: number;
}

export interface CurrencyRate {
  base: string;
  quote: string;
  rate: number;
  previousRate: number;
  change: number;
  changePercent: number;
  timestamp: string;
}

export interface CryptoInfo {
  symbol: string;
  name: string;
  price: number;
  previousClose: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
  circulatingSupply?: number;
  totalSupply?: number;
  '24hHigh': number;
  '24hLow': number;
}

export interface IndexInfo {
  symbol: string;
  name: string;
  price: number;
  previousClose: number;
  change: number;
  changePercent: number;
  volume: number;
}

/**
 * Получает информацию об акции
 */
export const getStockInfo = async (ticker: string): Promise<StockInfo> => {
    const response = await fetch(`${API_BASE_URL}/api/market/stock/${ticker}`, {
      method: 'GET',
      headers: getApiHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает исторические данные об акции
 */
export const getStockHistory = async (
  ticker: string,
  period: string = '1mo',
  interval: string = '1d'
): Promise<StockHistoryPoint[]> => {
    const response = await fetch(`${API_BASE_URL}/api/market/stock/history`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({ ticker, period, interval }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает информацию о нескольких акциях одновременно
 */
export const getMultipleStocks = async (tickers: string[]): Promise<StockInfo[]> => {
    const response = await fetch(`${API_BASE_URL}/api/market/stocks/multiple`, {
      method: 'POST',
      headers: getApiHeaders(),
      body: JSON.stringify({ tickers }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает курс валютной пары
 */
export const getCurrencyRate = async (base: string, quote: string = 'USD'): Promise<CurrencyRate> => {
    const response = await fetch(`${API_BASE_URL}/api/market/currency/${base}/${quote}`, {
      method: 'GET',
      headers: getApiHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает информацию о криптовалюте
 */
export const getCryptoInfo = async (symbol: string): Promise<CryptoInfo> => {
    const response = await fetch(`${API_BASE_URL}/api/market/crypto/${symbol}`, {
      method: 'GET',
      headers: getApiHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает информацию об индексе
 */
export const getIndexInfo = async (symbol: string): Promise<IndexInfo> => {
    const response = await fetch(`${API_BASE_URL}/api/market/index/${symbol}`, {
      method: 'GET',
      headers: getApiHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает список популярных тикеров из различных индексов и бирж
 */
export const getPopularTickers = async (): Promise<string[]> => {
    const response = await fetch(`${API_BASE_URL}/api/market/tickers/popular`, {
      method: 'GET',
      headers: getApiHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};

/**
 * Получает список популярных криптовалют
 */
export const getPopularCryptos = async (): Promise<string[]> => {
    const response = await fetch(`${API_BASE_URL}/api/market/crypto/popular`, {
      method: 'GET',
      headers: getApiHeaders(),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
};
