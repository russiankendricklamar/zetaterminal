"""
MOEX ISS Client
Клиент для работы с ISS API Московской Биржи

Основные возможности:
- Получение спецификации инструментов
- История торгов
- Рыночные данные
- Индексы
- Корпоративная информация
- Рейтинги
"""

import requests
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime


class MoexISSClient:
    """
    Клиент для работы с ISS API МосБиржи

    Документация API: https://iss.moex.com/iss/reference/
    """

    BASE_URL = 'https://iss.moex.com/iss'

    def __init__(self, timeout: int = 30):
        """
        Инициализация клиента

        Args:
            timeout: таймаут запросов (сек)
        """
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Базовый метод для выполнения запросов к ISS API

        Args:
            endpoint: путь эндпоинта (без BASE_URL)
            params: параметры запроса

        Returns:
            Словарь с данными (JSON response)
        """
        url = f"{self.BASE_URL}/{endpoint}.json"

        if params is None:
            params = {}

        # Всегда запрашиваем JSON
        params['iss.json'] = 'extended'
        params['iss.meta'] = 'off'  # отключаем метаданные для компактности

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        return data

    def _parse_iss_response(
        self,
        data: Dict,
        table_name: Optional[str] = None
    ) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Парсинг стандартного ISS response в DataFrame

        Args:
            data: JSON response от ISS
            table_name: имя конкретной таблицы (если None - возвращаем все)

        Returns:
            DataFrame или словарь {table_name: DataFrame}
        """
        if not data or len(data) < 2:
            return pd.DataFrame()

        # ISS extended format: [metadata, data]
        # data[1] содержит основные данные
        tables = data[1]

        if table_name:
            if table_name not in tables:
                return pd.DataFrame()

            table_data = tables[table_name]
            if not table_data:
                return pd.DataFrame()

            return pd.DataFrame(table_data)

        # Возвращаем все таблицы
        result = {}
        for name, table_data in tables.items():
            if table_data:
                result[name] = pd.DataFrame(table_data)

        return result

    # =========================================================================
    # SECURITIES: Информация о ценных бумагах
    # =========================================================================

    def get_security_info(self, security: str) -> Dict[str, pd.DataFrame]:
        """
        Получить спецификацию инструмента

        Args:
            security: тикер или ISIN

        Returns:
            Словарь таблиц (description, boards, etc.)

        Example:
            >>> client.get_security_info('GAZP')
        """
        endpoint = f'securities/{security}'
        data = self._request(endpoint)
        return self._parse_iss_response(data)

    def search_securities(
        self,
        query: str,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Поиск ценных бумаг по названию/тикеру

        Args:
            query: поисковый запрос
            limit: максимум результатов

        Returns:
            DataFrame с найденными бумагами
        """
        endpoint = 'securities'
        params = {
            'q': query,
            'limit': limit
        }
        data = self._request(endpoint, params)
        return self._parse_iss_response(data, 'securities')

    # =========================================================================
    # MARKET DATA: Текущие рыночные данные
    # =========================================================================

    def get_market_data(
        self,
        security: str,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получить текущие рыночные данные по инструменту

        Args:
            security: тикер
            engine: торговая система (stock, currency, futures)
            market: рынок (shares, bonds, index)

        Returns:
            DataFrame с текущими данными
        """
        endpoint = f'engines/{engine}/markets/{market}/securities/{security}'
        data = self._request(endpoint)
        tables = self._parse_iss_response(data)

        # Объединяем таблицы marketdata и securities
        if isinstance(tables, dict):
            if 'marketdata' in tables and not tables['marketdata'].empty:
                return tables['marketdata']
            elif 'securities' in tables:
                return tables['securities']

        return pd.DataFrame()

    def get_orderbook(
        self,
        security: str,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получить стакан заявок по инструменту

        Args:
            security: тикер
            engine: торговая система
            market: рынок

        Returns:
            DataFrame со стаканом
        """
        endpoint = f'engines/{engine}/markets/{market}/securities/{security}/orderbook'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'orderbook')

    def get_trades(
        self,
        security: str,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получить последние сделки по инструменту

        Args:
            security: тикер
            engine: торговая система
            market: рынок

        Returns:
            DataFrame со сделками
        """
        endpoint = f'engines/{engine}/markets/{market}/securities/{security}/trades'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'trades')

    # =========================================================================
    # HISTORY: Исторические данные
    # =========================================================================

    def get_security_history(
        self,
        security: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        engine: str = 'stock',
        market: str = 'shares',
        board: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Получить историю торгов инструмента

        Args:
            security: тикер
            start_date: начальная дата (YYYY-MM-DD)
            end_date: конечная дата (YYYY-MM-DD)
            engine: торговая система
            market: рынок
            board: режим торгов (например, TQBR)

        Returns:
            DataFrame с историческими данными
        """
        if board:
            endpoint = f'history/engines/{engine}/markets/{market}/boards/{board}/securities/{security}'
        else:
            endpoint = f'history/engines/{engine}/markets/{market}/securities/{security}'

        params = {}
        if start_date:
            params['from'] = start_date
        if end_date:
            params['till'] = end_date

        # ISS может возвращать данные постранично
        all_data = []
        start = 0

        while True:
            params['start'] = start
            data = self._request(endpoint, params)
            df = self._parse_iss_response(data, 'history')

            if df.empty:
                break

            all_data.append(df)

            # Если строк меньше 100 (дефолтный лимит) - это последняя страница
            if len(df) < 100:
                break

            start += len(df)

        if not all_data:
            return pd.DataFrame()

        result = pd.concat(all_data, ignore_index=True)

        # Преобразуем TRADEDATE в datetime
        if 'TRADEDATE' in result.columns:
            result['TRADEDATE'] = pd.to_datetime(result['TRADEDATE'])

        return result

    def get_index_history(
        self,
        index: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Получить историю индекса (например, IMOEX, RTSI)

        Args:
            index: код индекса (IMOEX, RTSI, etc.)
            start_date: начальная дата
            end_date: конечная дата

        Returns:
            DataFrame с историей индекса
        """
        return self.get_security_history(
            security=index,
            start_date=start_date,
            end_date=end_date,
            engine='stock',
            market='index',
            board='SNDX'
        )

    def get_candles(
        self,
        security: str,
        interval: int = 24,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получить свечи (OHLCV)

        Args:
            security: тикер
            interval: интервал свечи (1, 10, 60, 24, 7, 31 мин/часов)
            start_date: начало
            end_date: конец
            engine: система
            market: рынок

        Returns:
            DataFrame со свечами
        """
        endpoint = f'engines/{engine}/markets/{market}/securities/{security}/candles'

        params = {'interval': interval}
        if start_date:
            params['from'] = start_date
        if end_date:
            params['till'] = end_date

        data = self._request(endpoint, params)
        df = self._parse_iss_response(data, 'candles')

        if not df.empty and 'begin' in df.columns:
            df['begin'] = pd.to_datetime(df['begin'])

        return df

    # =========================================================================
    # INDICES: Индексы
    # =========================================================================

    def get_indices(self) -> pd.DataFrame:
        """
        Получить список всех индексов МосБиржи

        Returns:
            DataFrame с индексами
        """
        endpoint = 'statistics/engines/stock/markets/index/analytics'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'indices')

    def get_index_constituents(self, index: str) -> pd.DataFrame:
        """
        Получить состав индекса

        Args:
            index: код индекса

        Returns:
            DataFrame с составом
        """
        endpoint = f'statistics/engines/stock/markets/index/analytics/{index}'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'analytics')

    # =========================================================================
    # TURNOVERS: Обороты
    # =========================================================================

    def get_turnovers(self, date: Optional[str] = None) -> pd.DataFrame:
        """
        Получить сводные обороты по рынкам за дату

        Args:
            date: дата (YYYY-MM-DD), по умолчанию - сегодня

        Returns:
            DataFrame с оборотами
        """
        endpoint = 'turnovers'
        params = {}
        if date:
            params['date'] = date

        data = self._request(endpoint, params)
        return self._parse_iss_response(data, 'turnovers')

    # =========================================================================
    # CORPORATE INFO: Корпоративная информация (рейтинги, отчётность)
    # =========================================================================

    def get_company_ratings(self, company_id: int) -> pd.DataFrame:
        """
        Получить актуальные рейтинги организации

        Args:
            company_id: ID компании в системе ISS

        Returns:
            DataFrame с рейтингами
        """
        endpoint = f'cci/rating/companies/{company_id}'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'ratings')

    def get_security_ratings(self, security: str) -> pd.DataFrame:
        """
        Получить актуальные рейтинги выпуска

        Args:
            security: ISIN или ID выпуска

        Returns:
            DataFrame с рейтингами
        """
        endpoint = f'cci/rating/securities/{security}'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'ratings')

    def get_company_financials(
        self,
        company_id: int,
        report_type: str = 'msfo-short'
    ) -> pd.DataFrame:
        """
        Получить финансовую отчётность компании

        Args:
            company_id: ID компании
            report_type: тип отчёта (msfo-short, msfo-full, rsbu)

        Returns:
            DataFrame с отчётами
        """
        endpoint = f'cci/accounting/{report_type}/companies/{company_id}/reports'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'reports')

    def get_dividends(self) -> pd.DataFrame:
        """
        Получить информацию о дивидендах

        Returns:
            DataFrame с дивидендами
        """
        endpoint = 'cci/corp-actions/dividends'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'dividends')

    def get_company_dividends(self, company_id: int) -> pd.DataFrame:
        """
        Получить дивиденды конкретной компании

        Args:
            company_id: ID компании

        Returns:
            DataFrame с дивидендами компании
        """
        endpoint = f'cci/corp-actions/dividends'
        params = {'company_id': company_id}
        data = self._request(endpoint, params)
        return self._parse_iss_response(data, 'dividends')

    # =========================================================================
    # REFERENCE DATA: Справочники
    # =========================================================================

    def get_engines(self) -> pd.DataFrame:
        """
        Получить список торговых систем

        Returns:
            DataFrame с торговыми системами
        """
        endpoint = 'engines'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'engines')

    def get_markets(self, engine: str = 'stock') -> pd.DataFrame:
        """
        Получить список рынков торговой системы

        Args:
            engine: торговая система

        Returns:
            DataFrame с рынками
        """
        endpoint = f'engines/{engine}/markets'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'markets')

    def get_boards(
        self,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получить справочник режимов торгов

        Args:
            engine: торговая система
            market: рынок

        Returns:
            DataFrame с режимами торгов
        """
        endpoint = f'engines/{engine}/markets/{market}/boards'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'boards')

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get_trading_dates(
        self,
        engine: str = 'stock',
        market: str = 'shares',
        board: str = 'TQBR'
    ) -> pd.DataFrame:
        """
        Получить доступные торговые даты

        Args:
            engine: торговая система
            market: рынок
            board: режим торгов

        Returns:
            DataFrame с датами
        """
        endpoint = f'history/engines/{engine}/markets/{market}/boards/{board}/dates'
        data = self._request(endpoint)
        return self._parse_iss_response(data, 'dates')


# Вспомогательные утилиты
def format_date(date: Union[str, datetime]) -> str:
    """
    Форматирование даты для ISS API

    Args:
        date: дата (строка YYYY-MM-DD или datetime)

    Returns:
        Строка в формате YYYY-MM-DD
    """
    if isinstance(date, str):
        return date
    return date.strftime('%Y-%m-%d')


# Пример использования
if __name__ == "__main__":
    client = MoexISSClient()

    # 1. Информация о бумаге
    print("=== ИНФОРМАЦИЯ О GAZP ===")
    info = client.get_security_info('GAZP')
    if 'description' in info:
        print(info['description'].head())

    # 2. История торгов
    print("\n=== ИСТОРИЯ ТОРГОВ ===")
    history = client.get_security_history(
        'GAZP',
        start_date='2024-01-01',
        end_date='2024-12-31'
    )
    print(f"Загружено строк: {len(history)}")
    print(history.head())

    # 3. Текущие рыночные данные
    print("\n=== ТЕКУЩИЕ ДАННЫЕ ===")
    market_data = client.get_market_data('GAZP')
    print(market_data.head())

    # 4. История индекса
    print("\n=== ИСТОРИЯ ИНДЕКСА IMOEX ===")
    index_history = client.get_index_history('IMOEX', start_date='2024-01-01')
    print(f"Загружено строк: {len(index_history)}")
    print(index_history.head())
