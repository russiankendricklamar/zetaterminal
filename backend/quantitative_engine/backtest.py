import numpy as np
import pandas as pd
import requests
import time
from typing import List, Dict, Any

class Backtester:
    @staticmethod
    def fetch_moex_data(ticker: str, start: str, end: str) -> pd.Series:
        """Загрузка данных с MOEX ISS (Логика из Файла 10)"""
        url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
        all_rows = []
        start_idx = 0
        
        while True:
            params = {'from': start, 'till': end, 'start': start_idx}
            res = requests.get(url, params=params).json()
            rows = res['history']['data']
            if not rows: break
            
            # Индексы колонок TRADEDATE и CLOSE могут меняться, берем из метаданных
            cols = res['history']['columns']
            date_idx, close_idx = cols.index('TRADEDATE'), cols.index('CLOSE')
            
            all_rows.extend([[r[date_idx], r[close_idx]] for r in rows])
            start_idx += len(rows)
            time.sleep(0.1) # Вежливый запрос

        df = pd.DataFrame(all_rows, columns=['Date', 'Close'])
        df['Date'] = pd.to_datetime(df['Date'])
        return df.set_index('Date')['Close'].dropna()

    @classmethod
    def run_backtest(cls, tickers: List[str], weights: np.ndarray, 
                     start: str, end: str, initial_capital: float, 
                     forecast_var_pct: float):
        """
        Основной цикл бэктестинга: расчет реальных потерь vs VaR
        """
        # 1. Сбор данных
        prices = pd.DataFrame({t: cls.fetch_moex_data(t, start, end) for t in tickers})
        prices = prices.ffill().dropna()
        
        # 2. Расчет доходностей портфеля
        returns = prices.pct_change().dropna()
        portfolio_returns = (returns * weights).sum(axis=1)
        portfolio_value = initial_capital * (1 + portfolio_returns).cumprod()
        
        # 3. Анализ пробитий VaR (Файл 10)
        daily_losses_pct = -portfolio_returns * 100
        breaches = daily_losses_pct[daily_losses_pct > forecast_var_pct]
        
        # 4. Формирование метрик
        total_return = (portfolio_value.iloc[-1] / initial_capital - 1) * 100
        max_drawdown = (portfolio_value / portfolio_value.cummax() - 1).min() * 100
        
        return {
            "total_return": float(total_return),
            "max_drawdown": float(max_drawdown),
            "var_breaches": int(len(breaches)),
            "breach_dates": breaches.index.strftime('%Y-%m-%d').tolist(),
            "history": {
                "dates": portfolio_value.index.strftime('%Y-%m-%d').tolist(),
                "values": portfolio_value.values.tolist()
            }
        }