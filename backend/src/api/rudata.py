"""
API endpoints для работы с RuData (Interfax) API.

Endpoints:
- POST /rudata/test-connection - Проверить подключение к RuData
- POST /rudata/query - Выполнить произвольный запрос к RuData
- GET /rudata/bond/{isin} - Получить информацию об облигации
- GET /rudata/bond/{isin}/cashflows - Получить денежные потоки облигации
- POST /rudata/bond/calculate - Рассчитать параметры облигации
- POST /rudata/bonds/search - Поиск облигаций
- GET /rudata/zcyc - Получить кривую бескупонной доходности
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter()


# Pydantic модели

class RuDataCredentials(BaseModel):
    """Учетные данные для RuData API."""
    login: str = Field(..., description="Логин RuData")
    password: str = Field(..., description="Пароль RuData")


class RuDataQuery(BaseModel):
    """Запрос к RuData API."""
    login: str = Field(..., description="Логин RuData")
    password: str = Field(..., description="Пароль RuData")
    path_method: str = Field(..., description="Путь метода API (например, 'Bond/List')")
    body: Dict[str, Any] = Field(default_factory=dict, description="Тело запроса")
    post: bool = Field(default=True, description="Использовать POST метод")
    search_array: Optional[List[str]] = Field(None, description="Массив поиска")
    search_param: str = Field(default="filter", description="Параметр для массива поиска")
    search_field: Optional[str] = Field(None, description="Поле фильтрации")


class BondCalculateRequest(BaseModel):
    """Запрос на расчет параметров облигации."""
    login: str
    password: str
    isin: str
    calc_date: Optional[str] = None
    price: Optional[float] = None


class BondSearchRequest(BaseModel):
    """Запрос на поиск облигаций."""
    login: str
    password: str
    filter: str = Field(..., description="Строка фильтрации")
    fields: Optional[List[str]] = Field(None, description="Список полей для выборки")


class ConnectionTestResponse(BaseModel):
    """Ответ на проверку подключения."""
    success: bool
    message: str
    login: Optional[str] = None


class RuDataResponse(BaseModel):
    """Стандартный ответ RuData."""
    success: bool
    data: List[Dict[str, Any]] = []
    count: int = 0
    columns: Optional[List[str]] = None
    error: Optional[str] = None
    message: Optional[str] = None


@router.post("/test-connection", response_model=ConnectionTestResponse)
async def test_connection(credentials: RuDataCredentials):
    """
    Проверить подключение к RuData API.

    Выполняет авторизацию и возвращает результат.
    """
    try:
        from src.services.rudata_service import test_rudata_connection

        result = await test_rudata_connection(
            login=credentials.login,
            password=credentials.password
        )

        return ConnectionTestResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка проверки подключения: {str(e)}"
        )


@router.post("/query", response_model=RuDataResponse)
async def execute_query(query: RuDataQuery):
    """
    Выполнить произвольный запрос к RuData API.

    Документация методов: https://docs.efir-net.ru/dh2/#/
    """
    try:
        from src.services.rudata_service import fetch_rudata

        result = await fetch_rudata(
            login=query.login,
            password=query.password,
            path_method=query.path_method,
            body_json=query.body,
            post=query.post,
            search_array=query.search_array,
            search_param=query.search_param,
            search_field=query.search_field
        )

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка выполнения запроса: {str(e)}"
        )


@router.post("/bond/info", response_model=RuDataResponse)
async def get_bond_info(credentials: RuDataCredentials, isin: str = Query(..., description="ISIN облигации")):
    """
    Получить информацию об облигации по ISIN.
    """
    try:
        from src.services.rudata_service import get_rudata_service

        service = get_rudata_service(credentials.login, credentials.password)
        result = await service.get_bond_info(isin)

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения информации об облигации: {str(e)}"
        )


@router.post("/bond/cashflows", response_model=RuDataResponse)
async def get_bond_cashflows(credentials: RuDataCredentials, isin: str = Query(..., description="ISIN облигации")):
    """
    Получить денежные потоки (купоны, амортизация) облигации.
    """
    try:
        from src.services.rudata_service import get_rudata_service

        service = get_rudata_service(credentials.login, credentials.password)
        result = await service.get_bond_cashflows(isin)

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения денежных потоков: {str(e)}"
        )


@router.post("/bond/calculate", response_model=RuDataResponse)
async def calculate_bond(request: BondCalculateRequest):
    """
    Рассчитать параметры облигации (доходность, дюрация, и т.д.).
    """
    try:
        from src.services.rudata_service import get_rudata_service

        service = get_rudata_service(request.login, request.password)
        result = await service.calculate_bond(
            isin=request.isin,
            calc_date=request.calc_date,
            price=request.price
        )

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка расчета облигации: {str(e)}"
        )


@router.post("/bonds/search", response_model=RuDataResponse)
async def search_bonds(request: BondSearchRequest):
    """
    Поиск облигаций по фильтру.

    Примеры фильтров:
    - "status = 'В обращении'"
    - "facevalue >= 1000 and currency = 'RUB'"
    - "isin_reg LIKE 'RU%'"
    """
    try:
        from src.services.rudata_service import get_rudata_service

        service = get_rudata_service(request.login, request.password)
        result = await service.search_bonds(
            filter_str=request.filter,
            fields=request.fields
        )

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка поиска облигаций: {str(e)}"
        )


@router.post("/zcyc", response_model=RuDataResponse)
async def get_zcyc(
    credentials: RuDataCredentials,
    date: Optional[str] = Query(None, description="Дата в формате YYYY-MM-DD")
):
    """
    Получить кривую бескупонной доходности (ZCYC) из RuData.
    """
    try:
        from src.services.rudata_service import get_rudata_service

        service = get_rudata_service(credentials.login, credentials.password)
        result = await service.get_zcyc(date=date)

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения ZCYC: {str(e)}"
        )


@router.post("/fintool/reference", response_model=RuDataResponse)
async def get_fintool_reference(
    credentials: RuDataCredentials,
    id: str = Query(..., description="ID финансового инструмента (ISIN, FintoolID)"),
    fields: Optional[List[str]] = Query(None, description="Список полей для выборки")
):
    """
    Получить справочные данные финансового инструмента.
    """
    try:
        from src.services.rudata_service import fetch_rudata

        body: Dict[str, Any] = {'id': id}
        if fields:
            body['fields'] = fields

        result = await fetch_rudata(
            login=credentials.login,
            password=credentials.password,
            path_method='Info/FintoolReferenceData',
            body_json=body
        )

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения справочных данных: {str(e)}"
        )


@router.post("/indicator/list", response_model=RuDataResponse)
async def get_indicator_list(
    credentials: RuDataCredentials,
    filter: Optional[str] = Query(None, description="Строка фильтрации")
):
    """
    Получить список индикаторов.
    """
    try:
        from src.services.rudata_service import fetch_rudata

        body: Dict[str, Any] = {}
        if filter:
            body['filter'] = filter

        result = await fetch_rudata(
            login=credentials.login,
            password=credentials.password,
            path_method='Indicator/List',
            body_json=body
        )

        return RuDataResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения списка индикаторов: {str(e)}"
        )
