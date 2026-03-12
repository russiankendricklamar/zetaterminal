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

from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from src.middleware.rate_limit import limiter
from src.utils.error_handler import service_endpoint

router = APIRouter()


# Pydantic модели

class RuDataCredentials(BaseModel):
    """Учетные данные для RuData API."""
    login: str = Field(..., min_length=1, max_length=200, description="Логин RuData")
    password: str = Field(..., min_length=1, max_length=200, description="Пароль RuData")


class RuDataQuery(BaseModel):
    """Запрос к RuData API."""
    login: str = Field(..., min_length=1, max_length=200, description="Логин RuData")
    password: str = Field(..., min_length=1, max_length=200, description="Пароль RuData")
    path_method: str = Field(..., min_length=1, max_length=200, description="Путь метода API (например, 'Bond/List')")
    body: dict[str, Any] = Field(default_factory=dict, description="Тело запроса")
    post: bool = Field(default=True, description="Использовать POST метод")
    search_array: list[str] | None = Field(None, max_length=1000, description="Массив поиска")
    search_param: str = Field(default="filter", max_length=100, description="Параметр для массива поиска")
    search_field: str | None = Field(None, max_length=200, description="Поле фильтрации")


class BondCalculateRequest(BaseModel):
    """Запрос на расчет параметров облигации."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    isin: str = Field(..., min_length=1, max_length=50)
    calc_date: str | None = Field(None, max_length=20)
    price: float | None = None


class BondSearchRequest(BaseModel):
    """Запрос на поиск облигаций."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    filter: str = Field(..., min_length=1, max_length=2000, description="Строка фильтрации")
    fields: list[str] | None = Field(None, max_length=100, description="Список полей для выборки")


class ConnectionTestResponse(BaseModel):
    """Ответ на проверку подключения."""
    success: bool
    message: str
    login: str | None = None


class RuDataResponse(BaseModel):
    """Стандартный ответ RuData."""
    success: bool
    data: list[dict[str, Any]] = []
    count: int = 0
    columns: list[str] | None = None
    error: str | None = None
    message: str | None = None


class SessionResponse(BaseModel):
    """Ответ с session_id после кеширования credentials."""
    success: bool
    message: str
    session_id: str | None = None
    login: str | None = None


class SessionRequest(BaseModel):
    """Запрос по session_id."""
    session_id: str = Field(..., description="ID серверной сессии")


@router.post("/session/create", response_model=SessionResponse)
@limiter.limit("20/minute")
@service_endpoint("Create Session")
async def create_session(request: Request, credentials: RuDataCredentials):
    """
    Проверить подключение к RuData API и кешировать credentials на сервере.

    Возвращает session_id для последующих запросов без передачи логина/пароля.
    """
    from src.services.rudata_service import cache_credentials, test_rudata_connection

    result = await test_rudata_connection(
        login=credentials.login,
        password=credentials.password
    )

    if result.get("success"):
        session_id = cache_credentials(credentials.login, credentials.password)
        return SessionResponse(
            success=True,
            message=result.get("message", "Подключено"),
            session_id=session_id,
            login=credentials.login,
        )

    return SessionResponse(
        success=False,
        message=result.get("message", "Ошибка авторизации"),
        login=credentials.login,
    )

@router.post("/session/clear")
@limiter.limit("20/minute")
@service_endpoint("Clear Session")
async def clear_session(request: Request, session_req: SessionRequest):
    """Удалить кешированные credentials по session_id."""
    from src.services.rudata_service import clear_cached_credentials

    removed = clear_cached_credentials(session_req.session_id)
    return {"success": True, "removed": removed}


@router.post("/test-connection", response_model=ConnectionTestResponse)
@limiter.limit("20/minute")
@service_endpoint("Test Connection")
async def test_connection(request: Request, credentials: RuDataCredentials):
    """
    Проверить подключение к RuData API.

    Выполняет авторизацию и возвращает результат.
    """
    from src.services.rudata_service import test_rudata_connection

    result = await test_rudata_connection(
        login=credentials.login,
        password=credentials.password
    )

    return ConnectionTestResponse(**result)

@router.post("/query", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Execute Query")
async def execute_query(request: Request, query: RuDataQuery):
    """
    Выполнить произвольный запрос к RuData API.

    Документация методов: https://docs.efir-net.ru/dh2/#/
    """
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

@router.post("/bond/info", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Get Bond Info")
async def get_bond_info(request: Request, credentials: RuDataCredentials, isin: str = Query(..., description="ISIN облигации")):
    """
    Получить информацию об облигации по ISIN.
    """
    from src.services.rudata_service import get_rudata_service

    service = get_rudata_service(credentials.login, credentials.password)
    result = await service.get_bond_info(isin)

    return RuDataResponse(**result)

@router.post("/bond/cashflows", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Get Bond Cashflows")
async def get_bond_cashflows(request: Request, credentials: RuDataCredentials, isin: str = Query(..., description="ISIN облигации")):
    """
    Получить денежные потоки (купоны, амортизация) облигации.
    """
    from src.services.rudata_service import get_rudata_service

    service = get_rudata_service(credentials.login, credentials.password)
    result = await service.get_bond_cashflows(isin)

    return RuDataResponse(**result)

@router.post("/bond/calculate", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Calculate Bond")
async def calculate_bond(request: Request, calc_req: BondCalculateRequest):
    """
    Рассчитать параметры облигации (доходность, дюрация, и т.д.).
    """
    from src.services.rudata_service import get_rudata_service

    service = get_rudata_service(calc_req.login, calc_req.password)
    result = await service.calculate_bond(
        isin=calc_req.isin,
        calc_date=calc_req.calc_date,
        price=calc_req.price
    )

    return RuDataResponse(**result)

@router.post("/bonds/search", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Search Bonds")
async def search_bonds(request: Request, search_req: BondSearchRequest):
    """
    Поиск облигаций по фильтру.

    Примеры фильтров:
    - "status = 'В обращении'"
    - "facevalue >= 1000 and currency = 'RUB'"
    - "isin_reg LIKE 'RU%'"
    """
    from src.services.rudata_service import get_rudata_service

    service = get_rudata_service(search_req.login, search_req.password)
    result = await service.search_bonds(
        filter_str=search_req.filter,
        fields=search_req.fields
    )

    return RuDataResponse(**result)

@router.post("/zcyc", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Get Zcyc")
async def get_zcyc(
    request: Request,
    credentials: RuDataCredentials,
    date: str | None = Query(None, description="Дата в формате YYYY-MM-DD")
):
    """
    Получить кривую бескупонной доходности (ZCYC) из RuData.
    """
    from src.services.rudata_service import get_rudata_service

    service = get_rudata_service(credentials.login, credentials.password)
    result = await service.get_zcyc(date=date)

    return RuDataResponse(**result)

@router.post("/fintool/reference", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Get Fintool Reference")
async def get_fintool_reference(
    request: Request,
    credentials: RuDataCredentials,
    id: str = Query(..., description="ID финансового инструмента (ISIN, FintoolID)"),
    fields: list[str] | None = Query(None, description="Список полей для выборки")
):
    """
    Получить справочные данные финансового инструмента.
    """
    from src.services.rudata_service import fetch_rudata

    body: dict[str, Any] = {'id': id}
    if fields:
        body['fields'] = fields

    result = await fetch_rudata(
        login=credentials.login,
        password=credentials.password,
        path_method='Info/FintoolReferenceData',
        body_json=body
    )

    return RuDataResponse(**result)

@router.post("/indicator/list", response_model=RuDataResponse)
@limiter.limit("20/minute")
@service_endpoint("Get Indicator List")
async def get_indicator_list(
    request: Request,
    credentials: RuDataCredentials,
    filter: str | None = Query(None, description="Строка фильтрации")
):
    """
    Получить список индикаторов.
    """
    from src.services.rudata_service import fetch_rudata

    body: dict[str, Any] = {}
    if filter:
        body['filter'] = filter

    result = await fetch_rudata(
        login=credentials.login,
        password=credentials.password,
        path_method='Indicator/List',
        body_json=body
    )

    return RuDataResponse(**result)
