"""
MOEX Securities API
Методы для работы с информацией об инструментах МосБиржи.
"""

import pandas as pd
from typing import Optional, List
from moex_client import MOEXClient


class MOEXSecurities(MOEXClient):
    """Класс для работы с инструментами МосБиржи."""
    
    def get_securities(self, query: Optional[str] = None, 
                       engine: Optional[str] = None,
                       market: Optional[str] = None,
                       group_by: Optional[str] = None,
                       group_by_filter: Optional[str] = None) -> pd.DataFrame:
        """
        Поиск инструментов по запросу.
        
        Parameters
        ----------
        query : str, optional
            Строка поиска (тикер, ISIN, название)
        engine : str, optional
            Торговая система (stock, currency, futures, etc.)
        market : str, optional
            Рынок (shares, bonds, etc.)
        group_by : str, optional
            Группировка результатов
        group_by_filter : str, optional
            Фильтр группировки
            
        Returns
        -------
        pd.DataFrame
            Информация об инструментах
            
        Example
        -------
        >>> client = MOEXSecurities()
        >>> df = client.get_securities(query="SBER")
        """
        params = {}
        if query:
            params['q'] = query
        if engine:
            params['engine'] = engine
        if market:
            params['market'] = market
        if group_by:
            params['group_by'] = group_by
        if group_by_filter:
            params['group_by_filter'] = group_by_filter
            
        response = self._request("securities", params)
        return self._parse_data_block(response, "securities")
    
    def get_security_info(self, security: str) -> pd.DataFrame:
        """
        Получение детальной информации об инструменте.
        
        Parameters
        ----------
        security : str
            Тикер или идентификатор инструмента
            
        Returns
        -------
        pd.DataFrame
            Детальная информация
            
        Example
        -------
        >>> client = MOEXSecurities()
        >>> info = client.get_security_info("SBER")
        """
        response = self._request(f"securities/{security}")
        
        # Объединяем основные блоки информации
        description = self._parse_data_block(response, "description")
        boards = self._parse_data_block(response, "boards")
        
        return {
            "description": description,
            "boards": boards
        }
    
    def get_security_indices(self, security: str) -> pd.DataFrame:
        """
        Получение списка индексов, в которые входит инструмент.
        
        Parameters
        ----------
        security : str
            Тикер инструмента
            
        Returns
        -------
        pd.DataFrame
            Список индексов
        """
        response = self._request(f"securities/{security}/indices")
        return self._parse_data_block(response, "indices")
    
    def get_index_composition(self, index: str = "IMOEX") -> pd.DataFrame:
        """
        Получение состава индекса.
        
        Parameters
        ----------
        index : str, default "IMOEX"
            Название индекса
            
        Returns
        -------
        pd.DataFrame
            Состав индекса
            
        Example
        -------
        >>> client = MOEXSecurities()
        >>> composition = client.get_index_composition("IMOEX")
        """
        response = self._request(f"securities/{index}")
        return self._parse_data_block(response, "securities")
