"""
ISS MOEX API Client
Клиент для работы с API Московской Биржи (ISS)

Документация: https://iss.moex.com/iss/reference/
"""

import requests
import pandas as pd
from typing import Optional, Dict, List, Union
from datetime import datetime, timedelta
import time


class MoexISSClient:
    """
    Клиент для работы с Information & Statistical Server (ISS) Московской Биржи
    """

    BASE_URL = "https://iss.moex.com/iss"

    def __init__(self, lang: str = 'ru', timeout: int = 30):
        """
        Инициализация клиента

        Args:
            lang: язык ответа ('ru' или 'en')
            timeout: таймаут запросов в секундах
        """
        self.lang = lang
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'MOEX-ISS-Python-Client/1.0'})

    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Базовый метод для выполнения HTTP-запросов

        Args:
            endpoint: относительный путь API (например, '/securities/GAZP')
            params: параметры запроса

        Returns:
            Словарь с данными ответа
        """
        if params is None:
            params = {}

        # Добавляем язык и формат
        params['lang'] = self.lang
        params['iss.json'] = 'extended'  # расширенный JSON формат

        url = f"{self.BASE_URL}{endpoint}.json"

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Ошибка запроса к {url}: {e}")

    def _parse_columns(self, data: List, columns: List[str]) -> pd.DataFrame:
        """
        Преобразование данных ISS в DataFrame

        Args:
            data: массив данных из ISS
            columns: список названий колонок

        Returns:
            DataFrame с данными
        """
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=columns)

        # Конвертация дат
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        for col in date_cols:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass

        return df

    # ========== SECURITIES ==========

    def get_security_info(self, security: str) -> Dict[str, pd.DataFrame]:
        """
        Получение информации о ценной бумаге

        Args:
            security: тикер или ISIN (например, 'GAZP' или 'RU0007661625')

        Returns:
            Словарь с таблицами: description, boards, aggregates
        """
        response = self._request(f'/securities/{security}')

        result = {}
        for table_name in ['description', 'boards', 'aggregates']:
            if table_name in response[1]:
                table_data = response[1][table_name]
                columns = table_data['columns']
                data = table_data['data']
                result[table_name] = self._parse_columns(data, columns)

        return result

    def search_securities(self, query: str, limit: int = 100) -> pd.DataFrame:
        """
        Поиск ценных бумаг по запросу

        Args:
            query: поисковый запрос (тикер, название, ISIN)
            limit: максимальное количество результатов

        Returns:
            DataFrame с результатами поиска
        """
        response = self._request('/securities', params={'q': query, 'limit': limit})

        if 'securities' in response[1]:
            table_data = response[1]['securities']
            return self._parse_columns(table_data['data'], table_data['columns'])

        return pd.DataFrame()

    # ========== HISTORY (Исторические данные) ==========

    def get_security_history(
        self,
        security: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        engine: str = 'stock',
        market: str = 'shares',
        board: str = 'TQBR'
    ) -> pd.DataFrame:
        """
        Получение исторических котировок ценной бумаги

        Args:
            security: тикер (например, 'GAZP')
            start_date: начальная дата (YYYY-MM-DD), по умолчанию - год назад
            end_date: конечная дата (YYYY-MM-DD), по умолчанию - сегодня
            engine: торговая система ('stock', 'currency', 'futures')
            market: рынок ('shares', 'bonds', 'index')
            board: режим торгов ('TQBR', 'TQCB', 'TQOB')

        Returns:
            DataFrame с историческими данными
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        endpoint = f'/history/engines/{engine}/markets/{market}/boards/{board}/securities/{security}'

        all_data = []
        start = 0

        while True:
            params = {
                'from': start_date,
                'till': end_date,
                'start': start
            }

            response = self._request(endpoint, params)

            if 'history' in response[1]:
                table_data = response[1]['history']
                df = self._parse_columns(table_data['data'], table_data['columns'])

                if df.empty:
                    break

                all_data.append(df)

                # Проверка на наличие следующей страницы
                if 'history.cursor' in response[1]:
                    cursor = response[1]['history.cursor']['data']
                    if cursor and cursor[0][1] >= cursor[0][2]:  # INDEX >= TOTAL
                        break
                    start += 100
                else:
                    break
            else:
                break

            time.sleep(0.1)  # Rate limiting

        if all_data:
            return pd.concat(all_data, ignore_index=True)

        return pd.DataFrame()

    def get_market_candles(
        self,
        security: str,
        interval: int = 24,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получение свечей (OHLCV данных)

        Args:
            security: тикер
            interval: интервал в минутах (1, 10, 60, 24, 7, 31, 4)
            start_date: начальная дата
            end_date: конечная дата
            engine: торговая система
            market: рынок

        Returns:
            DataFrame со свечами
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        endpoint = f'/engines/{engine}/markets/{market}/securities/{security}/candles'

        params = {
            'from': start_date,
            'till': end_date,
            'interval': interval
        }

        response = self._request(endpoint, params)

        if 'candles' in response[1]:
            table_data = response[1]['candles']
            return self._parse_columns(table_data['data'], table_data['columns'])

        return pd.DataFrame()

    # ========== ENGINES (Текущие данные рынка) ==========

    def get_market_data(
        self,
        security: Optional[str] = None,
        engine: str = 'stock',
        market: str = 'shares'
    ) -> pd.DataFrame:
        """
        Получение текущих рыночных данных

        Args:
            security: тикер (если None - все бумаги рынка)
            engine: торговая система
            market: рынок

        Returns:
            DataFrame с рыночными данными
        """
        if security:
            endpoint = f'/engines/{engine}/markets/{market}/securities/{security}'
        else:
            endpoint = f'/engines/{engine}/markets/{market}/securities'

        response = self._request(endpoint)

        if 'securities' in response[1] or 'marketdata' in response[1]:
            # Объединяем securities и marketdata
            result_df = pd.DataFrame()

            if 'securities' in response[1]:
                sec_data = response[1]['securities']
                result_df = self._parse_columns(sec_data['data'], sec_data['columns'])

            if 'marketdata' in response[1]:
                mkt_data = response[1]['marketdata']
                mkt_df = self._parse_columns(mkt_data['data'], mkt_data['columns'])

                if not result_df.empty and not mkt_df.empty:
                    # Объединяем по SECID
                    result_df = pd.merge(result_df, mkt_df, on='SECID', how='left', suffixes=('', '_mkt'))
                elif mkt_df.empty:
                    result_df = mkt_df

            return result_df

        return pd.DataFrame()

    def get_orderbook(
        self,
        security: str,
        engine: str = 'stock',
        market: str = 'shares',
        board: str = 'TQBR'
    ) -> Dict[str, pd.DataFrame]:
        """
        Получение стакана заявок

        Args:
            security: тикер
            engine: торговая система
            market: рынок
            board: режим торгов

        Returns:
            Словарь с таблицами: bids (покупки), offers (продажи)
        """
        endpoint = f'/engines/{engine}/markets/{market}/boards/{board}/securities/{security}/orderbook'

        response = self._request(endpoint)

        result = {}
        for table_name in ['orderbook']:
            if table_name in response[1]:
                table_data = response[1][table_name]
                df = self._parse_columns(table_data['data'], table_data['columns'])

                # Разделяем на биды и офферы
                if not df.empty and 'BUYSELL' in df.columns:
                    result['bids'] = df[df['BUYSELL'] == 'B'].copy()
                    result['offers'] = df[df['BUYSELL'] == 'S'].copy()

        return result

    # ========== INDICES (Индексы) ==========

    def get_index_data(self, index_name: str = 'IMOEX') -> Dict[str, pd.DataFrame]:
        """
        Получение данных по индексу

        Args:
            index_name: название индекса (IMOEX, RTSI, MOEXOG и др.)

        Returns:
            Словарь с таблицами данных индекса
        """
        response = self._request(f'/securities/{index_name}')

        result = {}
        for table_name in ['description', 'boards', 'indices']:
            if table_name in response[1]:
                table_data = response[1][table_name]
                result[table_name] = self._parse_columns(table_data['data'], table_data['columns'])

        return result

    def get_index_history(
        self,
        index_name: str = 'IMOEX',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Исторические значения индекса

        Args:
            index_name: название индекса
            start_date: начальная дата
            end_date: конечная дата

        Returns:
            DataFrame с историей индекса
        """
        return self.get_security_history(
            security=index_name,
            start_date=start_date,
            end_date=end_date,
            engine='stock',
            market='index',
            board='SNDX'
        )

    # ========== STATISTICS ==========

    def get_turnovers(self, engine: str = 'stock', date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение оборотов по рынкам

        Args:
            engine: торговая система
            date: дата (по умолчанию - последняя доступная)

        Returns:
            DataFrame с оборотами
        """
        endpoint = f'/engines/{engine}/turnovers'
        params = {}
        if date:
            params['date'] = date

        response = self._request(endpoint, params)

        if 'turnovers' in response[1]:
            table_data = response[1]['turnovers']
            return self._parse_columns(table_data['data'], table_data['columns'])

        return pd.DataFrame()

    # ========== CORPORATE ACTIONS ==========

    def get_dividends(self, security: Optional[str] = None) -> pd.DataFrame:
        """
        Получение информации о дивидендах

        Args:
            security: тикер (если None - все бумаги)

        Returns:
            DataFrame с информацией о дивидендах
        """
        endpoint = '/cci/corp-actions/dividends'
        response = self._request(endpoint)

        if 'dividends' in response[1]:
            table_data = response[1]['dividends']
            df = self._parse_columns(table_data['data'], table_data['columns'])

            if security and not df.empty:
                df = df[df['secid'] == security].copy()

            return df

        return pd.DataFrame()

    def get_coupons(self, security: Optional[str] = None) -> pd.DataFrame:
        """
        Получение информации о купонах облигаций

        Args:
            security: тикер облигации

        Returns:
            DataFrame с купонными выплатами
        """
        endpoint = '/cci/corp-actions/coupons'
        response = self._request(endpoint)

        if 'coupons' in response[1]:
            table_data = response[1]['coupons']
            df = self._parse_columns(table_data['data'], table_data['columns'])

            if security and not df.empty:
                df = df[df['secid'] == security].copy()

            return df

        return pd.DataFrame()

    # ========== RATINGS ==========

    def get_company_ratings(self, company_id: Optional[int] = None) -> pd.DataFrame:
        """
        Получение рейтингов компании

        Args:
            company_id: ID компании в системе NSD

        Returns:
            DataFrame с рейтингами
        """
        if company_id:
            endpoint = f'/cci/rating/companies/{company_id}'
        else:
            endpoint = '/cci/rating/companies'

        response = self._request(endpoint)

        # Ищем первую доступную таблицу
        for key in response[1]:
            if isinstance(response[1][key], dict) and 'data' in response[1][key]:
                table_data = response[1][key]
                return self._parse_columns(table_data['data'], table_data['columns'])

        return pd.DataFrame()


# Примеры использования
if __name__ == "__main__":
    client = MoexISSClient()

    # Пример 1: Информация о ценной бумаге
    info = client.get_security_info('GAZP')
    print("\n=== ИНФОРМАЦИЯ О ГАЗПРОМЕ ===")
    print(info['description'])

    # Пример 2: Исторические котировки
    history = client.get_security_history('GAZP', start_date='2025-01-01', end_date='2026-01-01')
    print(f"\n=== ИСТОРИЧЕСКИЕ ДАННЫЕ: {len(history)} записей ===")
    print(history.head())

    # Пример 3: Текущие рыночные данные
    market_data = client.get_market_data('GAZP')
    print("\n=== ТЕКУЩИЕ РЫНОЧНЫЕ ДАННЫЕ ===")
    print(market_data)
