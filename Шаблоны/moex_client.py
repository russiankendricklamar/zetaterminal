"""
MOEX ISS API Client
Базовый клиент для работы с информационно-статистическим сервером (ISS) МосБиржи.

Документация API: https://iss.moex.com/iss/reference/
"""

import requests
import pandas as pd
from typing import Optional, Dict, List, Union
from datetime import datetime, date
import time


class MOEXClient:
    """Клиент для работы с ISS API МосБиржи."""
    
    BASE_URL = "https://iss.moex.com/iss"
    
    def __init__(self, timeout: int = 30, retries: int = 3, delay: float = 0.5):
        """
        Инициализация клиента.
        
        Parameters
        ----------
        timeout : int
            Таймаут запроса в секундах
        retries : int
            Количество повторных попыток при ошибке
        delay : float
            Задержка между запросами (секунды)
        """
        self.timeout = timeout
        self.retries = retries
        self.delay = delay
        self.session = requests.Session()
        
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Базовый метод для выполнения запросов к API.
        
        Parameters
        ----------
        endpoint : str
            Эндпоинт API (без базового URL)
        params : dict, optional
            Параметры запроса
            
        Returns
        -------
        dict
            JSON-ответ от API
        """
        url = f"{self.BASE_URL}/{endpoint}.json"
        
        if params is None:
            params = {}
        
        for attempt in range(self.retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.retries - 1:
                    raise Exception(f"Ошибка запроса после {self.retries} попыток: {e}")
                time.sleep(self.delay * (attempt + 1))
                
    def _parse_data_block(self, data: Dict, block_name: str) -> pd.DataFrame:
        """
        Парсинг блока данных из ответа ISS.
        
        Parameters
        ----------
        data : dict
            JSON-ответ от ISS
        block_name : str
            Название блока данных (например, 'securities', 'marketdata')
            
        Returns
        -------
        pd.DataFrame
            Данные в виде DataFrame
        """
        if block_name not in data:
            return pd.DataFrame()
        
        block = data[block_name]
        if 'data' not in block or 'columns' not in block:
            return pd.DataFrame()
            
        df = pd.DataFrame(block['data'], columns=block['columns'])
        return df
    
    def _fetch_all_pages(self, endpoint: str, params: Optional[Dict] = None, 
                         block_name: str = None) -> pd.DataFrame:
        """
        Получение всех страниц данных с пагинацией.
        
        Parameters
        ----------
        endpoint : str
            Эндпоинт API
        params : dict, optional
            Параметры запроса
        block_name : str, optional
            Название блока данных для парсинга
            
        Returns
        -------
        pd.DataFrame
            Объединённые данные со всех страниц
        """
        if params is None:
            params = {}
        
        params['start'] = 0
        all_data = []
        
        while True:
            response = self._request(endpoint, params)
            
            # Автоопределение имени блока, если не задано
            if block_name is None:
                # Берём первый блок, который не является метаданными
                for key in response.keys():
                    if key not in ['history.cursor']:
                        block_name = key
                        break
            
            df = self._parse_data_block(response, block_name)
            
            if df.empty:
                break
                
            all_data.append(df)
            
            # Проверка наличия следующей страницы
            cursor = response.get('history.cursor', {})
            if not cursor.get('data'):
                break
                
            cursor_df = pd.DataFrame(cursor['data'], columns=cursor['columns'])
            if cursor_df.empty or cursor_df.iloc[0]['INDEX'] + cursor_df.iloc[0]['PAGESIZE'] >= cursor_df.iloc[0]['TOTAL']:
                break
                
            params['start'] += len(df)
        
        if not all_data:
            return pd.DataFrame()
            
        return pd.concat(all_data, ignore_index=True)
    
    def close(self):
        """Закрытие сессии."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
