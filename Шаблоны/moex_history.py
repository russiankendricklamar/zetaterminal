"""
MOEX Historical Data API
Методы для получения исторических данных по инструментам.
"""

import pandas as pd
from typing import Optional, Union
from datetime import datetime, date
from moex_client import MOEXClient


class MOEXHistory(MOEXClient):
    """Класс для работы с историческими данными МосБиржи."""
    
    def get_history(self, 
                   security: str,
                   engine: str = "stock",
                   market: str = "shares",
                   board: Optional[str] = None,
                   start_date: Optional[Union[str, date, datetime]] = None,
                   end_date: Optional[Union[str, date, datetime]] = None,
                   interval: int = 24) -> pd.DataFrame:
        """
        Получение исторических данных по инструменту.
        
        Parameters
        ----------
        security : str
            Тикер инструмента
        engine : str, default "stock"
            Торговая система (stock, currency, futures)
        market : str, default "shares"
            Рынок (shares, bonds, index, etc.)
        board : str, optional
            Режим торгов (TQBR, TQTF, etc.)
        start_date : str, date, datetime, optional
            Дата начала периода (формат YYYY-MM-DD)
        end_date : str, date, datetime, optional
            Дата окончания периода
        interval : int, default 24
            Интервал свечи (1, 10, 60, 24, 7, 31, 4)
            
        Returns
        -------
        pd.DataFrame
            Исторические данные (OPEN, CLOSE, HIGH, LOW, VALUE, VOLUME)
        """
        params = {}
        
        if start_date:
            if isinstance(start_date, (date, datetime)):
                start_date = start_date.strftime("%Y-%m-%d")
            params['from'] = start_date
            
        if end_date:
            if isinstance(end_date, (date, datetime)):
                end_date = end_date.strftime("%Y-%m-%d")
            params['till'] = end_date
        
        params['interval'] = interval
        
        if board:
            endpoint = f"history/engines/{engine}/markets/{market}/boards/{board}/securities/{security}"
        else:
            endpoint = f"history/engines/{engine}/markets/{market}/securities/{security}"
        
        df = self._fetch_all_pages(endpoint, params, "history")
        
        if not df.empty:
            if 'TRADEDATE' in df.columns:
                df['TRADEDATE'] = pd.to_datetime(df['TRADEDATE'])
            
            numeric_cols = ['OPEN', 'LOW', 'HIGH', 'CLOSE', 'VALUE', 'VOLUME']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_candles(self,
                   security: str,
                   engine: str = "stock",
                   market: str = "shares",
                   start_date: Optional[Union[str, date, datetime]] = None,
                   end_date: Optional[Union[str, date, datetime]] = None,
                   interval: int = 60) -> pd.DataFrame:
        """
        Получение свечей (OHLCV) для инструмента.
        """
        params = {'interval': interval}
        
        if start_date:
            if isinstance(start_date, (date, datetime)):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
            params['from'] = start_date
            
        if end_date:
            if isinstance(end_date, (date, datetime)):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
            params['till'] = end_date
        
        endpoint = f"engines/{engine}/markets/{market}/securities/{security}/candles"
        df = self._fetch_all_pages(endpoint, params, "candles")
        
        if not df.empty:
            if 'begin' in df.columns:
                df['begin'] = pd.to_datetime(df['begin'])
            if 'end' in df.columns:
                df['end'] = pd.to_datetime(df['end'])
            
            numeric_cols = ['open', 'close', 'high', 'low', 'value', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
