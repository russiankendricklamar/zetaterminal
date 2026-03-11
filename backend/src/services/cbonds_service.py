"""
Сервис для работы с Cbonds API.

Документация: https://data.cbonds.info/files/api/API_documentation_eng.pdf
Каталог операций: https://cbonds.ru/api/catalog/folders/

Формат запроса (POST JSON):
{
    "auth": {"login": "...", "password": "..."},
    "filters": [{"field": "...", "operator": "...", "value": ...}],
    "quantity": {"limit": 1000, "offset": 0},
    "sorting": [{"field": "...", "order": "asc|desc"}],
    "fields": [{"field": "..."}, ...]
}

Ограничения:
- max 1000 записей в ответе
- max 30 запросов в минуту на endpoint
- max 10 000 запросов в сутки на endpoint
- max 1 000 000 записей в общей выборке
"""

import asyncio
import secrets
import time
from typing import Any

import aiohttp

from src.utils.http_client import get_session

# ─── Credential cache (аналог RuData) ──────────────────────────────────────

_SESSION_TTL_SECONDS = 3600
_MAX_CREDENTIAL_CACHE = 100
_credential_cache: dict[str, dict[str, Any]] = {}


def cache_credentials(login: str, password: str) -> str:
    """Cache Cbonds credentials server-side, return session_id."""
    _cleanup_expired()
    if len(_credential_cache) >= _MAX_CREDENTIAL_CACHE:
        oldest = min(_credential_cache, key=lambda k: _credential_cache[k]["cached_at"])
        _credential_cache.pop(oldest, None)
    session_id = secrets.token_hex(32)
    _credential_cache[session_id] = {
        "login": login,
        "password": password,
        "cached_at": time.time(),
    }
    return session_id


def get_cached_credentials(session_id: str) -> dict[str, str] | None:
    """Retrieve cached credentials by session_id."""
    entry = _credential_cache.get(session_id)
    if entry is None:
        return None
    if time.time() - entry["cached_at"] > _SESSION_TTL_SECONDS:
        _credential_cache.pop(session_id, None)
        return None
    return {"login": entry["login"], "password": entry["password"]}


def clear_cached_credentials(session_id: str) -> bool:
    """Remove cached credentials for a session_id."""
    return _credential_cache.pop(session_id, None) is not None


def _cleanup_expired() -> int:
    """Remove expired sessions."""
    now = time.time()
    expired = [
        sid for sid, entry in _credential_cache.items()
        if now - entry["cached_at"] > _SESSION_TTL_SECONDS
    ]
    for sid in expired:
        _credential_cache.pop(sid, None)
    return len(expired)


# ─── Cbonds API Client ─────────────────────────────────────────────────────

class CbondsService:
    """
    Клиент для Cbonds API (ws2.cbonds.info).

    Операции:
    - get_emissions        — справочные данные эмиссий (ISIN, купон, даты, номинал)
    - get_mpquotes         — котировки от участников рынка
    - get_nsd_quotes       — справедливая цена НРД (NSD Price Center)
    - get_tradings_realtime — внутридневные котировки
    - get_index_value      — значения индексов
    - get_index_types      — типы индексов
    - get_emitent_ratings  — рейтинги эмитентов
    - get_auctions         — аукционы
    """

    BASE_URL = "https://ws2.cbonds.info/services/json"
    MAX_LIMIT = 1000
    MAX_PAGES = 100  # safety limit

    def __init__(self, login: str, password: str):
        self._login = login
        self._password = password

    def _auth_block(self) -> dict[str, str]:
        return {"login": self._login, "password": self._password}

    async def _request(
        self,
        operation: str,
        filters: list[dict[str, Any]] | None = None,
        fields: list[str] | None = None,
        sorting: list[dict[str, str]] | None = None,
        limit: int = 1000,
        offset: int = 0,
        lang: str = "rus",
    ) -> dict[str, Any]:
        """
        Execute a single request to Cbonds API.

        Args:
            operation: API operation name (e.g. 'get_emissions')
            filters: List of filter dicts [{"field": ..., "operator": ..., "value": ...}]
            fields: List of field names to return
            sorting: List of sort dicts [{"field": ..., "order": "asc|desc"}]
            limit: Records per page (max 1000)
            offset: Page offset (must be multiple of limit)
            lang: Language ('rus' or 'eng')
        """
        url = f"{self.BASE_URL}/{operation}/?lang={lang}"

        body: dict[str, Any] = {
            "auth": self._auth_block(),
            "quantity": {"limit": min(limit, self.MAX_LIMIT), "offset": offset},
        }

        if filters:
            body["filters"] = filters
        if fields:
            body["fields"] = [{"field": f} for f in fields]
        if sorting:
            body["sorting"] = sorting

        session = await get_session()
        try:
            async with session.post(
                url,
                json=body,
                headers={"Content-Type": "application/json"},
            ) as response:
                if response.status == 403:
                    return {"success": False, "error": "Ошибка авторизации (403)", "items": [], "total": 0}
                if response.status == 301:
                    return {"success": False, "error": "Требуется HTTPS (301)", "items": [], "total": 0}
                if not response.ok:
                    text = await response.text()
                    return {"success": False, "error": f"{response.status}: {text[:200]}", "items": [], "total": 0}

                data = await response.json()

                # Cbonds wraps errors as strings or dicts with error info
                if isinstance(data, str):
                    return {"success": False, "error": data, "items": [], "total": 0}

                return {
                    "success": True,
                    "items": data.get("items", []),
                    "count": data.get("count", 0),
                    "total": data.get("total", 0),
                    "limit": data.get("limit", limit),
                    "offset": data.get("offset", offset),
                }

        except aiohttp.ClientError as e:
            return {"success": False, "error": str(e), "items": [], "total": 0}

    async def fetch_all(
        self,
        operation: str,
        filters: list[dict[str, Any]] | None = None,
        fields: list[str] | None = None,
        sorting: list[dict[str, str]] | None = None,
        lang: str = "rus",
        max_records: int = 10000,
    ) -> dict[str, Any]:
        """
        Fetch all pages for an operation (auto-pagination).

        Returns combined items from all pages.
        """
        all_items: list[dict] = []
        offset = 0
        limit = self.MAX_LIMIT

        for _ in range(self.MAX_PAGES):
            result = await self._request(
                operation=operation,
                filters=filters,
                fields=fields,
                sorting=sorting,
                limit=limit,
                offset=offset,
                lang=lang,
            )

            if not result["success"]:
                if all_items:
                    # Return what we have so far
                    break
                return result

            items = result["items"]
            all_items.extend(items)

            total = result["total"]

            # Stop conditions
            if len(all_items) >= total:
                break
            if len(all_items) >= max_records:
                break
            if len(items) < limit:
                break

            offset += limit
            await asyncio.sleep(0.1)  # rate limit protection

        return {
            "success": True,
            "data": all_items,
            "count": len(all_items),
            "total": result.get("total", len(all_items)),
        }

    # ─── Convenience methods ────────────────────────────────────────────

    async def test_connection(self) -> dict[str, Any]:
        """Test connection by requesting 1 emission record."""
        result = await self._request("get_emissions", limit=1)
        if result["success"]:
            return {
                "success": True,
                "message": "Успешное подключение к Cbonds API",
                "login": self._login,
            }
        return {
            "success": False,
            "message": f"Ошибка подключения: {result.get('error', 'unknown')}",
            "login": self._login,
        }

    async def get_emission_by_isin(
        self,
        isin: str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get bond reference data by ISIN."""
        return await self._request(
            "get_emissions",
            filters=[{"field": "isin_code", "operator": "eq", "value": isin}],
            fields=fields,
        )

    async def get_emissions_by_isins(
        self,
        isins: list[str],
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get bond reference data for multiple ISINs."""
        return await self._request(
            "get_emissions",
            filters=[{"field": "isin_code", "operator": "in", "value": ";".join(isins)}],
            fields=fields,
        )

    async def get_quotes(
        self,
        isin: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Get market participant quotes for a bond."""
        filters: list[dict[str, Any]] = [
            {"field": "isin_code", "operator": "eq", "value": isin},
        ]
        if date_from:
            filters.append({"field": "date", "operator": "ge", "value": date_from})
        if date_to:
            filters.append({"field": "date", "operator": "le", "value": date_to})

        return await self._request("get_mpquotes", filters=filters)

    async def get_nsd_quotes(
        self,
        isin: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Get NSD Price Center fair price estimates."""
        filters: list[dict[str, Any]] = [
            {"field": "isin_code", "operator": "eq", "value": isin},
        ]
        if date_from:
            filters.append({"field": "date", "operator": "ge", "value": date_from})
        if date_to:
            filters.append({"field": "date", "operator": "le", "value": date_to})

        return await self._request("get_nsd_quotes", filters=filters)

    async def get_index_value(
        self,
        index_id: int | str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any]:
        """Get index values (e.g. IFX-Cbonds, Cbonds-CBI)."""
        filters: list[dict[str, Any]] = [
            {"field": "id", "operator": "eq", "value": str(index_id)},
        ]
        if date_from:
            filters.append({"field": "date", "operator": "ge", "value": date_from})
        if date_to:
            filters.append({"field": "date", "operator": "le", "value": date_to})

        return await self._request("get_index_value", filters=filters)

    async def get_emitent_ratings(
        self,
        emitent_id: int | str | None = None,
        isin: str | None = None,
    ) -> dict[str, Any]:
        """Get issuer/emission credit ratings."""
        filters: list[dict[str, Any]] = []
        if emitent_id:
            filters.append({"field": "emitent_id", "operator": "eq", "value": str(emitent_id)})
        if isin:
            filters.append({"field": "isin_code", "operator": "eq", "value": isin})

        return await self._request("get_emitent_ratings", filters=filters)

    async def search_emissions(
        self,
        filters: list[dict[str, Any]],
        fields: list[str] | None = None,
        sorting: list[dict[str, str]] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Search emissions with custom filters."""
        return await self._request(
            "get_emissions",
            filters=filters,
            fields=fields,
            sorting=sorting,
            limit=limit,
        )

    async def get_emissions_updated_since(
        self,
        date: str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get emissions updated since a date (format: YYYYMMDD)."""
        return await self.fetch_all(
            "get_emissions",
            filters=[{"field": "updating_date", "operator": "ge", "value": date}],
            fields=fields,
        )


# ─── Module-level helpers ───────────────────────────────────────────────────

def get_cbonds_service(login: str, password: str) -> CbondsService:
    """Create a new CbondsService instance."""
    return CbondsService(login=login, password=password)


async def test_cbonds_connection(login: str, password: str) -> dict[str, Any]:
    """Test Cbonds API connection."""
    service = CbondsService(login=login, password=password)
    return await service.test_connection()


async def fetch_cbonds(
    login: str,
    password: str,
    operation: str,
    filters: list[dict[str, Any]] | None = None,
    fields: list[str] | None = None,
    sorting: list[dict[str, str]] | None = None,
    limit: int = 1000,
    offset: int = 0,
    lang: str = "rus",
) -> dict[str, Any]:
    """Execute a Cbonds API request."""
    service = get_cbonds_service(login, password)
    return await service._request(
        operation=operation,
        filters=filters,
        fields=fields,
        sorting=sorting,
        limit=limit,
        offset=offset,
        lang=lang,
    )
