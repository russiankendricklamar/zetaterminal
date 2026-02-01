/**
 * Сервис для работы с рыночными данными через yfinance API
 */

// В dev режиме используем относительные пути для работы через Vite proxy
// В production используем переменную окружения
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

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
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/stock/${ticker}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch stock info:', error);
    throw error;
  }
};

/**
 * Получает исторические данные об акции
 */
export const getStockHistory = async (
  ticker: string,
  period: string = '1mo',
  interval: string = '1d'
): Promise<StockHistoryPoint[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/stock/history`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ticker, period, interval }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch stock history:', error);
    throw error;
  }
};

/**
 * Получает информацию о нескольких акциях одновременно
 */
export const getMultipleStocks = async (tickers: string[]): Promise<StockInfo[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/stocks/multiple`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tickers }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch multiple stocks:', error);
    throw error;
  }
};

/**
 * Получает курс валютной пары
 */
export const getCurrencyRate = async (base: string, quote: string = 'USD'): Promise<CurrencyRate> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/currency/${base}/${quote}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch currency rate:', error);
    throw error;
  }
};

/**
 * Получает информацию о криптовалюте
 */
export const getCryptoInfo = async (symbol: string): Promise<CryptoInfo> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/crypto/${symbol}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch crypto info:', error);
    throw error;
  }
};

/**
 * Получает информацию об индексе
 */
export const getIndexInfo = async (symbol: string): Promise<IndexInfo> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/index/${symbol}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch index info:', error);
    throw error;
  }
};

/**
 * Получает список популярных тикеров из различных индексов и бирж
 */
export const getPopularTickers = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/tickers/popular`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch popular tickers:', error);
    throw error;
  }
};

/**
 * Получает список популярных криптовалют
 */
export const getPopularCryptos = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/market/crypto/popular`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch popular cryptos:', error);
    throw error;
  }
};

// MOEX ISS API interfaces
export interface MOEXStock {
  SECID: string;
  SHORTNAME: string;
  SECNAME: string;
  PREVPRICE: number;
  LAST: number;
  CHANGE: number;
  LASTTOPREVPRICE: number;
  VOLTODAY: number;
  VALTODAY: number;
  MARKETCAP?: number;
  BOARDID: string;
}

export interface MOEXStockInfo {
  ticker: string;
  name: string;
  symbol: string;
  price: number;
  previousClose: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  currency: string;
  exchange: string;
  country: string;
}

/**
 * Получает список всех акций с Московской биржи (MOEX ISS API)
 * Документация: https://iss.moex.com/iss/reference/
 */
export const getMOEXStocks = async (): Promise<MOEXStockInfo[]> => {
  try {
    // Получаем данные с MOEX ISS API - акции из основного режима торгов (TQBR)
    const response = await fetch(
      'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json?iss.meta=off&iss.only=securities,marketdata&securities.columns=SECID,SHORTNAME,SECNAME,PREVPRICE,BOARDID&marketdata.columns=SECID,LAST,CHANGE,LASTTOPREVPRICE,VOLTODAY,VALTODAY',
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`MOEX API error: ${response.status}`);
    }

    const data = await response.json();

    // Парсим данные из формата MOEX ISS
    const securities = data.securities?.data || [];
    const marketdata = data.marketdata?.data || [];

    // Создаем мапу marketdata по SECID для быстрого поиска
    const marketdataMap = new Map<string, any[]>();
    marketdata.forEach((row: any[]) => {
      marketdataMap.set(row[0], row);
    });

    const stocks: MOEXStockInfo[] = [];

    securities.forEach((sec: any[]) => {
      const secid = sec[0];
      const shortname = sec[1];
      const secname = sec[2];
      const prevprice = sec[3];

      const md = marketdataMap.get(secid);
      if (md && md[1]) { // Только если есть цена
        const last = md[1] || prevprice;
        const change = md[2] || 0;
        const changePercent = md[3] || 0;
        const volume = md[4] || 0;
        const valtoday = md[5] || 0;

        stocks.push({
          ticker: secid,
          name: secname || shortname,
          symbol: secid,
          price: last,
          previousClose: prevprice || last,
          change: change,
          changePercent: changePercent,
          volume: volume,
          marketCap: valtoday * 100, // Приблизительная оценка
          currency: 'RUB',
          exchange: 'MOEX',
          country: 'Russia',
        });
      }
    });

    return stocks;
  } catch (error) {
    console.error('Failed to fetch MOEX stocks:', error);
    throw error;
  }
};

/**
 * Получает список акций со СПБ Биржи
 * Примечание: СПБ Биржа не имеет открытого API, поэтому возвращаем список известных тикеров
 */
export const getSPBStocks = async (): Promise<string[]> => {
  // Популярные иностранные акции, торгующиеся на СПБ Бирже
  return [
    // Технологии США
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'AMD', 'INTC',
    'QCOM', 'AVGO', 'ORCL', 'ADBE', 'CRM', 'CSCO', 'IBM',
    // Финансы
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'V', 'MA', 'PYPL',
    // Потребительские товары
    'WMT', 'HD', 'KO', 'PEP', 'NKE', 'MCD', 'SBUX', 'PG', 'DIS',
    // Здравоохранение
    'JNJ', 'PFE', 'MRK', 'ABBV', 'UNH', 'LLY',
    // Энергетика
    'XOM', 'CVX', 'COP',
    // Промышленность
    'BA', 'CAT', 'GE', 'HON', 'MMM',
    // Телекоммуникации
    'T', 'VZ', 'TMUS',
    // Китай
    'BABA', 'JD', 'BIDU', 'NIO', 'XPEV', 'LI',
  ];
};

/**
 * Получает все тикеры MOEX для добавления в список
 */
export const getMOEXTickers = async (): Promise<string[]> => {
  try {
    const stocks = await getMOEXStocks();
    return stocks.map(s => s.ticker + '.ME');
  } catch (error) {
    console.error('Failed to get MOEX tickers:', error);
    // Возвращаем статический список в случае ошибки
    return [
      'SBER.ME', 'GAZP.ME', 'LKOH.ME', 'ROSN.ME', 'GMKN.ME', 'YNDX.ME',
      'MGNT.ME', 'VTBR.ME', 'TATN.ME', 'NVTK.ME', 'SNGS.ME', 'ALRS.ME',
      'MTSS.ME', 'TRNFP.ME', 'PLZL.ME', 'POLY.ME', 'CHMF.ME', 'NLMK.ME',
      'MAGN.ME', 'MOEX.ME', 'AFLT.ME', 'RTKM.ME', 'FEES.ME', 'HYDR.ME',
      'IRAO.ME', 'PIKK.ME', 'PHOR.ME', 'RUAL.ME', 'SIBN.ME', 'FIVE.ME',
    ];
  }
};
