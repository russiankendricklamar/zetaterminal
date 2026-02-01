"""
Сервис для работы с RuData (Interfax) API.

Основан на RudataExtractor, адаптирован для FastAPI.
Документация API: https://docs.efir-net.ru/dh2/#/
"""

import asyncio
from typing import Optional, Iterable, Union, Dict, Any, List
from datetime import datetime
import aiohttp
import pandas as pd


class RuDataService:
    """
    Сервис для выгрузки данных из RuData (EFIR).

    Ограничения API:
    - Не более 5 запросов в секунду
    - pageSize не более 300 (используем 100 для совместимости)
    - В фильтре не более 100 элементов за раз
    """

    API_URL = 'https://dh2.efir-net.ru/v2/'

    def __init__(
        self,
        login: str,
        password: str,
        max_pagesize: int = 100,
        max_array: int = 100,
        multi: bool = True
    ):
        self._login = login
        self._password = password
        self._max_pagesize = max_pagesize
        self._max_array = max_array
        self._max_requests = 5 if multi else 1
        self._request_wait = 1.0 if multi else 0.2
        self._token: Optional[str] = None
        self._token_expires: Optional[datetime] = None

    async def _get_token(self, session: aiohttp.ClientSession) -> Optional[str]:
        """Получить токен авторизации."""
        url = f"{self.API_URL}Account/Login"
        body = {
            'login': self._login,
            'password': self._password
        }

        try:
            async with session.post(url, json=body, headers={'Content-Type': 'application/json'}) as response:
                if response.ok:
                    data = await response.json()
                    return data.get('token')
                else:
                    return None
        except Exception:
            return None

    async def _do_request(
        self,
        session: aiohttp.ClientSession,
        path: str,
        body: dict,
        token: str,
        method: str = 'POST'
    ) -> Union[dict, list, str]:
        """Выполнить запрос к API."""
        url = f"{self.API_URL}{path}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        try:
            async with session.request(method, url, json=body, headers=headers) as response:
                if response.ok:
                    return await response.json()
                return f"{response.status} {response.reason}"
        except Exception as e:
            return str(e)

    async def test_connection(self) -> Dict[str, Any]:
        """Проверить подключение к RuData API."""
        async with aiohttp.ClientSession() as session:
            token = await self._get_token(session)

            if token:
                return {
                    'success': True,
                    'message': 'Успешное подключение к RuData API',
                    'login': self._login
                }
            else:
                return {
                    'success': False,
                    'message': 'Ошибка авторизации. Проверьте логин и пароль.',
                    'login': self._login
                }

    async def extract_data(
        self,
        path_method: str,
        body_json: dict,
        post: bool = True,
        search_array: Optional[Iterable] = None,
        search_param: str = 'filter',
        search_field: Optional[str] = None,
        keep_duplicates: bool = False
    ) -> Dict[str, Any]:
        """
        Извлечь данные из RuData API.

        Args:
            path_method: Путь метода API (например, 'Bond/CalculateBondMulti')
            body_json: Тело запроса
            post: Использовать POST (иначе GET)
            search_array: Массив поиска (если больше 100 элементов)
            search_param: Параметр для массива поиска
            search_field: Поле фильтрации (если search_param == 'filter')
            keep_duplicates: Сохранять дубликаты

        Returns:
            dict с ключами: success, data, count, error
        """
        # Нормализуем путь
        if path_method.startswith('/'):
            path_method = path_method[1:]
        if path_method.startswith('v2/'):
            path_method = path_method[3:]

        async with aiohttp.ClientSession() as session:
            token = await self._get_token(session)
            if not token:
                return {
                    'success': False,
                    'data': [],
                    'count': 0,
                    'error': 'Ошибка авторизации'
                }

            results: List[dict] = []

            try:
                if search_array is None:
                    # Простая выгрузка без массива поиска
                    results = await self._extract_simple(
                        session, token, path_method, body_json, post
                    )
                else:
                    # Выгрузка с массивом поиска
                    if search_param == 'filter' and search_field is None:
                        return {
                            'success': False,
                            'data': [],
                            'count': 0,
                            'error': "search_field обязателен при search_param='filter'"
                        }

                    results = await self._extract_with_array(
                        session, token, path_method, body_json, post,
                        search_array, search_param, search_field
                    )

                if not results:
                    return {
                        'success': True,
                        'data': [],
                        'count': 0,
                        'message': 'Данные не найдены'
                    }

                # Преобразуем в DataFrame для обработки
                df = pd.DataFrame(results)

                if not keep_duplicates:
                    try:
                        df = df.drop_duplicates()
                    except TypeError:
                        pass  # Некоторые типы не поддерживают drop_duplicates

                df = df.replace([r'\r', r'\n'], [' ', ' '], regex=True)

                return {
                    'success': True,
                    'data': df.to_dict(orient='records'),
                    'count': len(df),
                    'columns': df.columns.tolist()
                }

            except Exception as e:
                return {
                    'success': False,
                    'data': [],
                    'count': 0,
                    'error': str(e)
                }

    async def _extract_simple(
        self,
        session: aiohttp.ClientSession,
        token: str,
        path: str,
        body: dict,
        post: bool
    ) -> List[dict]:
        """Простая выгрузка без массива поиска."""
        results = []
        body = body.copy()
        body['pageNum'] = 1
        body['pageSize'] = self._max_pagesize
        body['pager'] = {'page': 1, 'size': self._max_pagesize}

        prev_container = None

        while True:
            tasks = []
            for _ in range(self._max_requests):
                tasks.append(
                    self._do_request(
                        session, path, body.copy(), token,
                        method='POST' if post else 'GET'
                    )
                )
                body['pageNum'] += 1
                body['pager']['page'] += 1

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            should_break = False
            for response in responses:
                if isinstance(response, str):
                    # Ошибка
                    should_break = True
                    break

                if isinstance(response, dict):
                    results.append(response)
                    should_break = True
                    break

                if isinstance(response, list):
                    if response == prev_container:
                        # Цикличная выгрузка
                        should_break = True
                        break

                    prev_container = response
                    results.extend(response)

                    if len(response) < self._max_pagesize:
                        should_break = True
                        break

            if should_break:
                break

            await asyncio.sleep(self._request_wait)

        return results

    async def _extract_with_array(
        self,
        session: aiohttp.ClientSession,
        token: str,
        path: str,
        body: dict,
        post: bool,
        search_array: Iterable,
        search_param: str,
        search_field: Optional[str]
    ) -> List[dict]:
        """Выгрузка с массивом поиска."""
        results = []
        search_list = list(search_array)
        filter_orig = body.get(search_param, '')

        # Разбиваем массив на чанки
        for i in range(0, len(search_list), self._max_array):
            chunk = tuple(search_list[i:i + self._max_array])

            chunk_body = body.copy()

            if search_param == 'filter':
                chunk_str = str(chunk).replace(',', '') if len(chunk) == 1 else str(chunk)
                if filter_orig:
                    chunk_body[search_param] = f"{filter_orig} AND {search_field} IN {chunk_str}"
                else:
                    chunk_body[search_param] = f"{search_field} IN {chunk_str}"
            else:
                chunk_body[search_param] = list(chunk)

            chunk_results = await self._extract_simple(
                session, token, path, chunk_body, post
            )
            results.extend(chunk_results)

            await asyncio.sleep(self._request_wait)

        return results

    # Удобные методы для типовых запросов

    async def get_bond_info(self, isin: str) -> Dict[str, Any]:
        """Получить информацию о облигации по ISIN."""
        return await self.extract_data(
            'Info/FintoolReferenceData',
            {'id': isin}
        )

    async def get_bond_cashflows(self, isin: str) -> Dict[str, Any]:
        """Получить денежные потоки облигации."""
        return await self.extract_data(
            'Bond/Coupons',
            {'filter': f"isin_reg = '{isin}'"}
        )

    async def calculate_bond(
        self,
        isin: str,
        calc_date: Optional[str] = None,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Рассчитать параметры облигации."""
        body = {'id': isin}
        if calc_date:
            body['calcDate'] = calc_date
        if price is not None:
            body['price'] = price

        return await self.extract_data(
            'Bond/Calculate',
            body
        )

    async def search_bonds(
        self,
        filter_str: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Поиск облигаций по фильтру."""
        body: Dict[str, Any] = {'filter': filter_str}
        if fields:
            body['fields'] = fields

        return await self.extract_data(
            'Bond/List',
            body
        )

    async def get_zcyc(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Получить кривую бескупонной доходности."""
        body = {}
        if date:
            body['date'] = date

        return await self.extract_data(
            'Info/ZCYC',
            body
        )


# Глобальный экземпляр сервиса (будет инициализирован при первом использовании)
_rudata_instance: Optional[RuDataService] = None


def get_rudata_service(login: str, password: str) -> RuDataService:
    """Получить экземпляр сервиса RuData."""
    global _rudata_instance

    if _rudata_instance is None or _rudata_instance._login != login:
        _rudata_instance = RuDataService(login=login, password=password)

    return _rudata_instance


async def test_rudata_connection(login: str, password: str) -> Dict[str, Any]:
    """Проверить подключение к RuData."""
    service = RuDataService(login=login, password=password)
    return await service.test_connection()


async def fetch_rudata(
    login: str,
    password: str,
    path_method: str,
    body_json: dict,
    **kwargs
) -> Dict[str, Any]:
    """Выполнить запрос к RuData API."""
    service = get_rudata_service(login, password)
    return await service.extract_data(path_method, body_json, **kwargs)
