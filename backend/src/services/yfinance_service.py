"""
Сервис для получения рыночных данных через yfinance.
Поддерживает акции, валюты, индексы, криптовалюты, облигации и товары.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_stock_info(ticker: str) -> Dict[str, Any]:
    """
    Получает информацию об акции.
    
    Args:
        ticker: Тикер акции (например, 'AAPL', 'MSFT', 'SBER.ME')
    
    Returns:
        Словарь с информацией об акции
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Получаем исторические данные
        hist = stock.history(period="1d", interval="1m")
        current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close > 0 else 0
        
        return {
            "ticker": ticker,
            "name": info.get('longName', ticker),
            "symbol": info.get('symbol', ticker),
            "price": float(current_price),
            "previousClose": float(prev_close),
            "change": float(change),
            "changePercent": float(change_percent),
            "volume": int(info.get('volume', 0)),
            "marketCap": int(info.get('marketCap', 0)),
            "peRatio": info.get('trailingPE'),
            "dividendYield": info.get('dividendYield'),
            "sector": info.get('sector'),
            "industry": info.get('industry'),
            "currency": info.get('currency', 'USD'),
            "exchange": info.get('exchange'),
            "country": info.get('country'),
            "website": info.get('website'),
            "description": info.get('longBusinessSummary'),
            "employees": info.get('fullTimeEmployees'),
            "52WeekHigh": info.get('fiftyTwoWeekHigh'),
            "52WeekLow": info.get('fiftyTwoWeekLow'),
            "beta": info.get('beta'),
            "forwardPE": info.get('forwardPE'),
            "priceToBook": info.get('priceToBook'),
            "earningsGrowth": info.get('earningsGrowth'),
            "revenueGrowth": info.get('revenueGrowth')
        }
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
        raise ValueError(f"Не удалось получить данные для {ticker}: {str(e)}")


def get_stock_history(ticker: str, period: str = "1mo", interval: str = "1d") -> List[Dict]:
    """
    Получает исторические данные об акции.
    
    Args:
        ticker: Тикер акции
        period: Период (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Интервал (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
    
    Returns:
        Список словарей с историческими данными
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            return []
        
        hist_reset = hist.reset_index()
        result = []
        for row in hist_reset.itertuples(index=False):
            date_val = row.Date if hasattr(row, 'Date') else row[0]
            result.append({
                "date": date_val.strftime("%Y-%m-%d"),
                "open": float(row.Open),
                "high": float(row.High),
                "low": float(row.Low),
                "close": float(row.Close),
                "volume": int(row.Volume),
                "adjClose": float(row.Close)
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {str(e)}")
        raise ValueError(f"Не удалось получить историю для {ticker}: {str(e)}")


def get_multiple_stocks(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Получает информацию о нескольких акциях одновременно.
    
    Args:
        tickers: Список тикеров
    
    Returns:
        Список словарей с информацией об акциях
    """
    try:
        # Используем yf.download для массовой загрузки
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False)
        
        if data.empty:
            return []
        
        result = []
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Получаем последнюю цену из загруженных данных
                if ticker in data.columns.levels[0] if isinstance(data.columns, pd.MultiIndex) else False:
                    ticker_data = data[ticker] if isinstance(data.columns, pd.MultiIndex) else data
                    current_price = float(ticker_data['Close'].iloc[-1])
                else:
                    hist = stock.history(period="1d")
                    current_price = float(hist['Close'].iloc[-1]) if not hist.empty else 0
                
                prev_close = info.get('previousClose', current_price)
                change = current_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                
                result.append({
                    "ticker": ticker,
                    "name": info.get('longName', ticker),
                    "price": current_price,
                    "previousClose": float(prev_close),
                    "change": float(change),
                    "changePercent": float(change_percent),
                    "volume": int(info.get('volume', 0)),
                    "marketCap": int(info.get('marketCap', 0)),
                    "peRatio": info.get('trailingPE'),
                    "sector": info.get('sector'),
                    "currency": info.get('currency', 'USD')
                })
            except Exception as e:
                logger.warning(f"Error processing {ticker}: {str(e)}")
                continue
        
        return result
    except Exception as e:
        logger.error(f"Error fetching multiple stocks: {str(e)}")
        raise ValueError(f"Не удалось получить данные: {str(e)}")


def get_currency_rate(base: str, quote: str = "USD") -> Dict[str, Any]:
    """
    Получает курс валютной пары.
    
    Args:
        base: Базовая валюта (например, 'EUR', 'RUB')
        quote: Котируемая валюта (по умолчанию 'USD')
    
    Returns:
        Словарь с информацией о курсе
    """
    try:
        # yfinance использует формат BASE-QUOTE=X для валют
        if base == quote:
            return {
                "base": base,
                "quote": quote,
                "rate": 1.0,
                "change": 0.0,
                "changePercent": 0.0
            }
        
        ticker_str = f"{base}{quote}=X"
        currency = yf.Ticker(ticker_str)
        hist = currency.history(period="2d")
        
        if hist.empty:
            raise ValueError(f"Не удалось получить данные для {ticker_str}")
        
        current_rate = float(hist['Close'].iloc[-1])
        prev_rate = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_rate
        change = current_rate - prev_rate
        change_percent = (change / prev_rate * 100) if prev_rate > 0 else 0
        
        return {
            "base": base,
            "quote": quote,
            "rate": current_rate,
            "previousRate": prev_rate,
            "change": change,
            "changePercent": change_percent,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching currency rate {base}/{quote}: {str(e)}")
        raise ValueError(f"Не удалось получить курс {base}/{quote}: {str(e)}")


def get_crypto_info(symbol: str) -> Dict[str, Any]:
    """
    Получает информацию о криптовалюте.
    
    Args:
        symbol: Символ криптовалюты (например, 'BTC-USD', 'ETH-USD')
    
    Returns:
        Словарь с информацией о криптовалюте
    """
    try:
        crypto = yf.Ticker(symbol)
        info = crypto.info
        hist = crypto.history(period="1d")
        
        if hist.empty:
            raise ValueError(f"Не удалось получить данные для {symbol}")
        
        current_price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close > 0 else 0
        
        return {
            "symbol": symbol,
            "name": info.get('longName', symbol),
            "price": current_price,
            "previousClose": prev_close,
            "change": change,
            "changePercent": change_percent,
            "volume": int(hist['Volume'].iloc[-1]),
            "marketCap": info.get('marketCap'),
            "circulatingSupply": info.get('circulatingSupply'),
            "totalSupply": info.get('totalSupply'),
            "24hHigh": float(hist['High'].iloc[-1]),
            "24hLow": float(hist['Low'].iloc[-1])
        }
    except Exception as e:
        logger.error(f"Error fetching crypto info for {symbol}: {str(e)}")
        raise ValueError(f"Не удалось получить данные для {symbol}: {str(e)}")


def get_index_info(symbol: str) -> Dict[str, Any]:
    """
    Получает информацию об индексе.
    
    Args:
        symbol: Символ индекса (например, '^GSPC' для S&P 500, '^DJI' для Dow Jones)
    
    Returns:
        Словарь с информацией об индексе
    """
    try:
        index = yf.Ticker(symbol)
        info = index.info
        hist = index.history(period="1d")
        
        if hist.empty:
            raise ValueError(f"Не удалось получить данные для {symbol}")
        
        current_price = float(hist['Close'].iloc[-1])
        prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
        change = current_price - prev_close
        change_percent = (change / prev_close * 100) if prev_close > 0 else 0
        
        return {
            "symbol": symbol,
            "name": info.get('longName', symbol),
            "price": current_price,
            "previousClose": prev_close,
            "change": change,
            "changePercent": change_percent,
            "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0
        }
    except Exception as e:
        logger.error(f"Error fetching index info for {symbol}: {str(e)}")
        raise ValueError(f"Не удалось получить данные для {symbol}: {str(e)}")


def search_ticker(query: str, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Поиск тикеров по запросу.
    
    Args:
        query: Поисковый запрос
        exchange: Биржа (опционально, например, 'NASDAQ', 'NYSE', 'MOEX')
    
    Returns:
        Список найденных тикеров
    """
    try:
        # yfinance не имеет встроенного поиска, используем альтернативный подход
        # Можно использовать yfinance search или внешние API
        # Для простоты возвращаем пустой список, но можно интегрировать с другими сервисами
        return []
    except Exception as e:
        logger.error(f"Error searching ticker: {str(e)}")
        return []


def get_popular_tickers() -> List[str]:
    """
    Возвращает список популярных тикеров из различных индексов и бирж.
    Включает S&P 500, NASDAQ 100, Dow Jones, и другие популярные акции.
    
    Returns:
        Список тикеров
    """
    # S&P 500 основные компоненты
    sp500_tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'UNH',
        'JNJ', 'V', 'PG', 'JPM', 'MA', 'HD', 'CVX', 'MRK', 'ABBV', 'PEP',
        'COST', 'AVGO', 'TMO', 'WMT', 'DIS', 'ACN', 'ADBE', 'NFLX', 'CRM', 'NKE',
        'LIN', 'DHR', 'VZ', 'ABT', 'PM', 'TXN', 'NEE', 'BMY', 'RTX', 'HON',
        'UPS', 'QCOM', 'AMGN', 'LOW', 'INTU', 'SPGI', 'AXP', 'BKNG', 'GE', 'SYK',
        'C', 'BLK', 'DE', 'ADI', 'TJX', 'GILD', 'ISRG', 'VRTX', 'ZTS', 'ADP',
        'MMC', 'CME', 'CDNS', 'APH', 'KLAC', 'SNPS', 'FTNT', 'MCHP', 'NXPI', 'CTSH',
        'ANSS', 'CDW', 'FAST', 'PAYX', 'WDAY', 'TEAM', 'ZM', 'DOCN', 'CRWD', 'NET',
        'DDOG', 'ZS', 'OKTA', 'SNOW', 'PLTR', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'RIVN',
        'LCID', 'NIO', 'XPEV', 'LI', 'BYDDY', 'BABA', 'TCEHY', 'JD', 'BIDU', 'PDD',
        'NIO', 'XPEV', 'LI', 'TSM', 'ASML', 'SAP', 'SIEGY', 'MBGYY', 'BMWYY', 'VWAGY',
        'TTE', 'LVMUY', 'LRLCY', 'SNY', 'EADSY', 'NSRGY', 'NVS', 'RHHBY', 'UBS', 'UL',
        'AZN', 'SHEL', 'BP', 'GSK', 'VOD', 'DEO', 'TM', 'SONY', 'SFTBY', 'NTDOY',
        'HMC', 'NSANY', 'SSNLF', 'HXSCL', 'LGEAF', 'RELIANCE.BSE', 'TCS.BSE', 'INFY', 'SHOP', 'RY',
        'CNI', 'BHP', 'RIO', 'CMWAY'
    ]
    
    # NASDAQ 100 дополнительные
    nasdaq_tickers = [
        'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'AMAT', 'LRCX', 'KLAC', 'MCHP', 'SWKS',
        'QRVO', 'NXPI', 'ON', 'WOLF', 'ALGM', 'DIOD', 'POWI', 'SLAB', 'SITM', 'CRUS',
        'OLED', 'OLED', 'OLED', 'OLED', 'OLED', 'OLED', 'OLED', 'OLED', 'OLED', 'OLED'
    ]
    
    # Дополнительные популярные акции
    additional_tickers = [
        'XOM', 'COP', 'SLB', 'HAL', 'MPC', 'VLO', 'PSX', 'OXY', 'DVN', 'FANG',
        'EOG', 'MRO', 'APA', 'CTRA', 'PR', 'MTDR', 'SM', 'NOV', 'FTI', 'NBR',
        'CAT', 'DE', 'CMI', 'PCAR', 'AGCO', 'TEX', 'ALG', 'ASTE', 'AOS', 'ARCB',
        'CHRW', 'EXPD', 'JBHT', 'KNX', 'ODFL', 'R', 'RXO', 'TFII', 'WERN', 'XPO',
        'NEE', 'DUK', 'SO', 'AEP', 'SRE', 'ES', 'ETR', 'FE', 'PEG', 'AEE',
        'ED', 'EIX', 'XEL', 'WEC', 'CMS', 'CNP', 'ATO', 'LNT', 'NI', 'PNW',
        'PLD', 'EQR', 'SPG', 'WELL', 'VICI', 'PSA', 'EXPI', 'AMT', 'CCI', 'EQIX',
        'FCX', 'NEM', 'SCCO', 'AA', 'CENX', 'KALU', 'CSTM', 'ZEUS', 'ATI', 'X',
        'STLD', 'NUE', 'CMC', 'RS', 'CLF', 'MT', 'TX', 'GGB', 'SID', 'VALE'
    ]
    
    # Российские акции (MOEX)
    russian_tickers = [
        'SBER.ME', 'GAZP.ME', 'LKOH.ME', 'GMKN.ME', 'YNDX.ME', 'ROSN.ME', 'NVTK.ME',
        'TATN.ME', 'ALRS.ME', 'MGNT.ME', 'MOEX.ME', 'POLY.ME', 'CHMF.ME', 'PLZL.ME',
        'VTBR.ME', 'SNGS.ME', 'MTSS.ME', 'TRNFP.ME', 'RTKM.ME', 'AFKS.ME', 'FIVE.ME',
        'PHOR.ME', 'HYDR.ME', 'IRAO.ME', 'FEES.ME', 'SNGSP.ME', 'AFLT.ME', 'PIKK.ME',
        'LSRG.ME', 'UPRO.ME', 'NLMK.ME'
    ]
    
    # Европейские акции
    european_tickers = [
        'ASML', 'UL', 'DEO', 'GSK', 'VOD', 'SAP', 'SIEGY', 'MBGYY', 'BMWYY', 'VWAGY',
        'ALIZY', 'TTE', 'LVMUY', 'LRLCY', 'SNY', 'EADSY', 'NSRGY', 'NVS', 'RHHBY', 'UBS',
        'ING', 'UNLY', 'BP', 'SHEL', 'AZN'
    ]
    
    # Азиатские акции
    asian_tickers = [
        'TM', 'SONY', 'SFTBY', 'NTDOY', 'HMC', 'NSANY', 'SSNLF', 'HXSCL', 'LGEAF',
        'BABA', 'TCEHY', 'JD', 'BIDU', 'PNGAY', 'IDCBY', 'CICHY', 'BYDDY', 'NIO',
        'XPEV', 'LI', 'TSM', 'RELIANCE.BSE', 'TCS.BSE', 'INFY'
    ]
    
    # Объединяем все списки и убираем дубликаты
    all_tickers = list(set(
        sp500_tickers + nasdaq_tickers + additional_tickers + 
        russian_tickers + european_tickers + asian_tickers
    ))
    
    return sorted(all_tickers)


def get_popular_cryptos() -> List[str]:
    """
    Возвращает список популярных криптовалют.
    Формат тикеров для yfinance: SYMBOL-USD (например, BTC-USD, ETH-USD)
    
    Returns:
        Список тикеров криптовалют в формате SYMBOL-USD
    """
    # Топ криптовалюты по капитализации
    top_cryptos = [
        'BTC-USD', 'ETH-USD', 'BNB-USD', 'SOL-USD', 'XRP-USD', 'USDT-USD', 'USDC-USD',
        'ADA-USD', 'DOGE-USD', 'AVAX-USD', 'SHIB-USD', 'TON-USD', 'DOT-USD', 'TRX-USD',
        'LINK-USD', 'MATIC-USD', 'NEAR-USD', 'ICP-USD', 'LTC-USD', 'UNI-USD', 'ATOM-USD',
        'ETC-USD', 'XLM-USD', 'INJ-USD', 'APT-USD', 'OP-USD', 'ARB-USD', 'FIL-USD',
        'IMX-USD', 'HBAR-USD', 'VET-USD', 'MKR-USD', 'THETA-USD', 'RNDR-USD', 'ALGO-USD',
        'AAVE-USD', 'GRT-USD', 'EGLD-USD', 'SAND-USD', 'MANA-USD', 'AXS-USD', 'EOS-USD',
        'FLOW-USD', 'XTZ-USD', 'CHZ-USD', 'QNT-USD', 'GALA-USD', 'FTM-USD', 'ROSE-USD',
        'KLAY-USD', 'CRV-USD', 'LRC-USD', 'ZEC-USD', 'DASH-USD', 'ENJ-USD', 'BAT-USD',
        'ZIL-USD', 'IOTA-USD', 'WAVES-USD', 'ONT-USD', 'ZEN-USD', 'STORJ-USD', 'OMG-USD',
        'SNX-USD', 'COMP-USD', 'YFI-USD', 'SUSHI-USD', '1INCH-USD', 'BAL-USD', 'CVX-USD',
        'FRAX-USD', 'LDO-USD', 'RPL-USD', 'RETH-USD', 'STETH-USD', 'DAI-USD', 'TUSD-USD',
        'BUSD-USD', 'USDP-USD', 'GUSD-USD', 'HUSD-USD', 'PAXG-USD', 'WBTC-USD', 'RENBTC-USD',
        'BCH-USD', 'BSV-USD', 'BTG-USD', 'XMR-USD', 'ZEN-USD', 'DCR-USD', 'RVN-USD',
        'XEM-USD', 'SC-USD', 'BTT-USD', 'WIN-USD', 'TRX-USD', 'BTT-USD', 'JST-USD',
        'SUN-USD', 'NFT-USD', 'PEOPLE-USD', 'LRC-USD', 'ANT-USD', 'REP-USD', 'CVC-USD',
        'POWR-USD', 'MANA-USD', 'SAND-USD', 'GALA-USD', 'AXS-USD', 'ENJ-USD', 'FLOW-USD',
        'IMX-USD', 'APE-USD', 'RARE-USD', 'SUPER-USD', 'ALICE-USD', 'TLM-USD', 'CHR-USD',
        'MAGIC-USD', 'GMT-USD', 'GFT-USD', 'HOOK-USD', 'HFT-USD', 'BLUR-USD', 'PEPE-USD',
        'FLOKI-USD', 'BONK-USD', 'WIF-USD', 'MEME-USD', 'MYRO-USD', 'POPCAT-USD', 'MEW-USD',
        'FET-USD', 'AGIX-USD', 'OCEAN-USD', 'RNDR-USD', 'TAO-USD', 'AI-USD', 'OLAS-USD',
        'ARKM-USD', 'GLM-USD', 'NMR-USD', 'CTXC-USD', 'DBC-USD', 'VXV-USD', 'COTI-USD',
        'CRO-USD', 'KCS-USD', 'HT-USD', 'OKB-USD', 'FTT-USD', 'LEO-USD', 'GT-USD',
        'BNX-USD', 'MX-USD', 'DYDX-USD', 'GMX-USD', 'GNS-USD', 'PERP-USD', 'VELA-USD',
        'ILV-USD', 'ATLAS-USD', 'POLIS-USD', 'MAGIC-USD', 'GMT-USD', 'GFT-USD', 'HOOK-USD',
        'HFT-USD', 'BLUR-USD', 'PEPE-USD', 'FLOKI-USD', 'BONK-USD', 'WIF-USD', 'MEME-USD',
        'MYRO-USD', 'POPCAT-USD', 'MEW-USD', 'FET-USD', 'AGIX-USD', 'OCEAN-USD', 'RNDR-USD',
        'TAO-USD', 'AI-USD', 'OLAS-USD', 'ARKM-USD', 'GLM-USD', 'NMR-USD', 'CTXC-USD',
        'DBC-USD', 'VXV-USD', 'COTI-USD', 'CRO-USD', 'KCS-USD', 'HT-USD', 'OKB-USD',
        'FTT-USD', 'LEO-USD', 'GT-USD', 'BNX-USD', 'MX-USD', 'DYDX-USD', 'GMX-USD',
        'GNS-USD', 'PERP-USD', 'VELA-USD', 'ILV-USD', 'ATLAS-USD', 'POLIS-USD'
    ]
    
    # Убираем дубликаты и сортируем
    unique_cryptos = list(set(top_cryptos))
    
    return sorted(unique_cryptos)
