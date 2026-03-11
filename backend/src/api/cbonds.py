"""
API endpoints для работы с Cbonds API.

Документация: https://data.cbonds.info/files/api/API_documentation_eng.pdf

Endpoints:
- POST /cbonds/test-connection — Проверить подключение к Cbonds
- POST /cbonds/session/create — Создать серверную сессию (кеш credentials)
- POST /cbonds/session/clear — Удалить кеш credentials
- POST /cbonds/query — Произвольный запрос к Cbonds API
- POST /cbonds/emission — Получить данные эмиссии по ISIN
- POST /cbonds/emissions/search — Поиск эмиссий с фильтрами
- POST /cbonds/quotes — Котировки участников рынка
- POST /cbonds/nsd-quotes — Справедливая цена НРД
- POST /cbonds/index — Значения индексов
- POST /cbonds/ratings — Рейтинги эмитентов
"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.utils.error_handler import service_endpoint

router = APIRouter()


# ─── Pydantic Models ───────────────────────────────────────────────────────

class CbondsCredentials(BaseModel):
    """Учетные данные Cbonds API."""
    login: str = Field(..., min_length=1, max_length=200, description="Логин Cbonds")
    password: str = Field(..., min_length=1, max_length=200, description="Пароль Cbonds")


class CbondsQuery(BaseModel):
    """Произвольный запрос к Cbonds API."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    operation: str = Field(..., min_length=1, max_length=100, description="Операция (e.g. 'get_emissions')")
    filters: list[dict[str, Any]] | None = Field(None, description="Фильтры [{field, operator, value}]")
    fields: list[str] | None = Field(None, max_length=200, description="Список полей для выборки")
    sorting: list[dict[str, str]] | None = Field(None, description="Сортировка [{field, order}]")
    limit: int = Field(default=100, ge=1, le=1000, description="Записей на страницу")
    offset: int = Field(default=0, ge=0, description="Смещение (кратно limit)")
    lang: str = Field(default="rus", pattern=r"^(rus|eng)$", description="Язык ответа")


class CbondsEmissionRequest(BaseModel):
    """Запрос данных эмиссии по ISIN."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    isin: str = Field(..., min_length=1, max_length=50)
    fields: list[str] | None = Field(None, max_length=200, description="Поля для выборки")


class CbondsEmissionsSearchRequest(BaseModel):
    """Поиск эмиссий с фильтрами."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    filters: list[dict[str, Any]] = Field(..., description="Фильтры [{field, operator, value}]")
    fields: list[str] | None = Field(None, max_length=200)
    sorting: list[dict[str, str]] | None = None
    limit: int = Field(default=100, ge=1, le=1000)


class CbondsQuotesRequest(BaseModel):
    """Запрос котировок."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    isin: str = Field(..., min_length=1, max_length=50)
    date_from: str | None = Field(None, max_length=10, description="Дата начала (YYYYMMDD)")
    date_to: str | None = Field(None, max_length=10, description="Дата конца (YYYYMMDD)")


class CbondsIndexRequest(BaseModel):
    """Запрос значений индекса."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    index_id: str = Field(..., description="ID индекса")
    date_from: str | None = Field(None, max_length=10)
    date_to: str | None = Field(None, max_length=10)


class CbondsRatingsRequest(BaseModel):
    """Запрос рейтингов."""
    login: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=1, max_length=200)
    emitent_id: str | None = Field(None, description="ID эмитента")
    isin: str | None = Field(None, max_length=50)


class SessionRequest(BaseModel):
    """Запрос по session_id."""
    session_id: str = Field(..., description="ID серверной сессии")


class CbondsResponse(BaseModel):
    """Стандартный ответ Cbonds."""
    success: bool
    data: list[dict[str, Any]] = []
    count: int = 0
    total: int = 0
    error: str | None = None
    message: str | None = None


class ConnectionTestResponse(BaseModel):
    """Ответ на проверку подключения."""
    success: bool
    message: str
    login: str | None = None


class SessionResponse(BaseModel):
    """Ответ с session_id."""
    success: bool
    message: str
    session_id: str | None = None
    login: str | None = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/test-connection", response_model=ConnectionTestResponse)
@service_endpoint("Test Connection")
async def test_connection(credentials: CbondsCredentials):
    """Проверить подключение к Cbonds API."""
    from src.services.cbonds_service import test_cbonds_connection

    result = await test_cbonds_connection(credentials.login, credentials.password)
    return ConnectionTestResponse(**result)


@router.post("/session/create", response_model=SessionResponse)
@service_endpoint("Create Session")
async def create_session(credentials: CbondsCredentials):
    """Проверить подключение и кешировать credentials на сервере."""
    from src.services.cbonds_service import cache_credentials, test_cbonds_connection

    result = await test_cbonds_connection(credentials.login, credentials.password)

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
@service_endpoint("Clear Session")
async def clear_session(request: SessionRequest):
    """Удалить кешированные credentials."""
    from src.services.cbonds_service import clear_cached_credentials

    removed = clear_cached_credentials(request.session_id)
    return {"success": True, "removed": removed}


@router.post("/query", response_model=CbondsResponse)
@service_endpoint("Execute Query")
async def execute_query(query: CbondsQuery):
    """
    Произвольный запрос к Cbonds API.

    Операции: get_emissions, get_mpquotes, get_nsd_quotes,
    get_tradings_realtime, get_index_value, get_emitent_ratings, get_auctions.

    Фильтры: [{"field": "isin_code", "operator": "eq", "value": "RU000A0..."}]
    Операторы: eq, ne, lt, le, gt, ge, in, ni, bw, bn, ew, en, cn, nc, nu, nn
    """
    from src.services.cbonds_service import fetch_cbonds

    result = await fetch_cbonds(
        login=query.login,
        password=query.password,
        operation=query.operation,
        filters=query.filters,
        fields=query.fields,
        sorting=query.sorting,
        limit=query.limit,
        offset=query.offset,
        lang=query.lang,
    )

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )


@router.post("/emission", response_model=CbondsResponse)
@service_endpoint("Get Emission")
async def get_emission(request: CbondsEmissionRequest):
    """Получить справочные данные эмиссии по ISIN."""
    from src.services.cbonds_service import get_cbonds_service

    service = get_cbonds_service(request.login, request.password)
    result = await service.get_emission_by_isin(request.isin, request.fields)

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )


@router.post("/emissions/search", response_model=CbondsResponse)
@service_endpoint("Search Emissions")
async def search_emissions(request: CbondsEmissionsSearchRequest):
    """
    Поиск эмиссий с произвольными фильтрами.

    Примеры фильтров:
    - [{"field": "isin_code", "operator": "eq", "value": "RU000A0JXQS3"}]
    - [{"field": "country_id", "operator": "eq", "value": "2"}, {"field": "currency_id", "operator": "eq", "value": "1"}]
    - [{"field": "maturity_date", "operator": "ge", "value": "20260101"}]
    """
    from src.services.cbonds_service import get_cbonds_service

    service = get_cbonds_service(request.login, request.password)
    result = await service.search_emissions(
        filters=request.filters,
        fields=request.fields,
        sorting=request.sorting,
        limit=request.limit,
    )

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )


@router.post("/quotes", response_model=CbondsResponse)
@service_endpoint("Get Quotes")
async def get_quotes(request: CbondsQuotesRequest):
    """Получить котировки от участников рынка."""
    from src.services.cbonds_service import get_cbonds_service

    service = get_cbonds_service(request.login, request.password)
    result = await service.get_quotes(
        isin=request.isin,
        date_from=request.date_from,
        date_to=request.date_to,
    )

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )


@router.post("/nsd-quotes", response_model=CbondsResponse)
@service_endpoint("Get NSD Quotes")
async def get_nsd_quotes(request: CbondsQuotesRequest):
    """Получить справедливую цену НРД (NSD Price Center)."""
    from src.services.cbonds_service import get_cbonds_service

    service = get_cbonds_service(request.login, request.password)
    result = await service.get_nsd_quotes(
        isin=request.isin,
        date_from=request.date_from,
        date_to=request.date_to,
    )

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )


@router.post("/index", response_model=CbondsResponse)
@service_endpoint("Get Index Value")
async def get_index_value(request: CbondsIndexRequest):
    """Получить значения индекса (IFX-Cbonds, Cbonds-CBI и др.)."""
    from src.services.cbonds_service import get_cbonds_service

    service = get_cbonds_service(request.login, request.password)
    result = await service.get_index_value(
        index_id=request.index_id,
        date_from=request.date_from,
        date_to=request.date_to,
    )

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )


@router.post("/ratings", response_model=CbondsResponse)
@service_endpoint("Get Ratings")
async def get_ratings(request: CbondsRatingsRequest):
    """Получить кредитные рейтинги эмитента или эмиссии."""
    from src.services.cbonds_service import get_cbonds_service

    service = get_cbonds_service(request.login, request.password)
    result = await service.get_emitent_ratings(
        emitent_id=request.emitent_id,
        isin=request.isin,
    )

    return CbondsResponse(
        success=result.get("success", False),
        data=result.get("items", []),
        count=result.get("count", 0),
        total=result.get("total", 0),
        error=result.get("error"),
    )
