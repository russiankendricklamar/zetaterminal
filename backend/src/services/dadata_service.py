"""
DaData Service — Russian company and bank data.

Suggestions API: https://suggestions.dadata.ru/suggestions/api/4_1/rs
"""

import os
from typing import Optional, Dict, Any, List

from src.services.cache_service import cache_get, cache_set, make_cache_key
from src.utils.http_client import get_session

DADATA_TOKEN = os.getenv("DADATA_API_TOKEN", "")
DADATA_SECRET = os.getenv("DADATA_SECRET_KEY", "")
DADATA_BASE = "https://suggestions.dadata.ru/suggestions/api/4_1/rs"


def _dadata_headers() -> Dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if DADATA_TOKEN:
        headers["Authorization"] = f"Token {DADATA_TOKEN}"
    return headers


async def dadata_find_company(inn: str) -> Dict[str, Any]:
    """Find company by INN/OGRN."""
    key = make_cache_key("dadata", "company", inn)
    cached = cache_get(key)
    if cached is not None:
        return cached

    session = await get_session()
    async with session.post(
        f"{DADATA_BASE}/findById/party",
        json={"query": inn},
        headers=_dadata_headers(),
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    suggestions = data.get("suggestions", [])
    companies = []
    for s in suggestions:
        d = s.get("data", {})
        address = d.get("address", {})
        companies.append({
            "inn": d.get("inn", ""),
            "ogrn": d.get("ogrn", ""),
            "kpp": d.get("kpp", ""),
            "name": s.get("value", ""),
            "full_name": d.get("name", {}).get("full_with_opf", ""),
            "short_name": d.get("name", {}).get("short_with_opf", ""),
            "type": d.get("type", ""),
            "status": d.get("state", {}).get("status", ""),
            "registration_date": d.get("state", {}).get("registration_date"),
            "okved": d.get("okved", ""),
            "okved_type": d.get("okved_type", ""),
            "management_name": d.get("management", {}).get("name", "") if d.get("management") else "",
            "management_post": d.get("management", {}).get("post", "") if d.get("management") else "",
            "address": address.get("value", "") if address else "",
            "capital": d.get("capital", {}).get("value") if d.get("capital") else None,
            "employees": d.get("employee_count"),
        })

    result = {"query": inn, "companies": companies, "provider": "dadata"}
    cache_set(key, result, ttl_seconds=3600)
    return result


async def dadata_suggest_company(query: str, count: int = 10) -> Dict[str, Any]:
    """Suggest companies by name or partial INN."""
    key = make_cache_key("dadata", "suggest_company", query, count)
    cached = cache_get(key)
    if cached is not None:
        return cached

    session = await get_session()
    async with session.post(
        f"{DADATA_BASE}/suggest/party",
        json={"query": query, "count": count},
        headers=_dadata_headers(),
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    suggestions = []
    for s in data.get("suggestions", []):
        d = s.get("data", {})
        suggestions.append({
            "inn": d.get("inn", ""),
            "ogrn": d.get("ogrn", ""),
            "name": s.get("value", ""),
            "type": d.get("type", ""),
            "status": d.get("state", {}).get("status", ""),
            "address": d.get("address", {}).get("value", "") if d.get("address") else "",
        })

    result = {"query": query, "suggestions": suggestions, "provider": "dadata"}
    cache_set(key, result, ttl_seconds=600)
    return result


async def dadata_find_bank(bik: str) -> Dict[str, Any]:
    """Find bank by BIK."""
    key = make_cache_key("dadata", "bank", bik)
    cached = cache_get(key)
    if cached is not None:
        return cached

    session = await get_session()
    async with session.post(
        f"{DADATA_BASE}/findById/bank",
        json={"query": bik},
        headers=_dadata_headers(),
    ) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)

    banks = []
    for s in data.get("suggestions", []):
        d = s.get("data", {})
        banks.append({
            "bik": d.get("bic", ""),
            "name": s.get("value", ""),
            "full_name": d.get("name", {}).get("payment", ""),
            "correspondent_account": d.get("correspondent_account", ""),
            "registration_number": d.get("registration_number", ""),
            "swift": d.get("swift", ""),
            "inn": d.get("inn", ""),
            "kpp": d.get("kpp", ""),
            "address": d.get("address", {}).get("value", "") if d.get("address") else "",
            "status": d.get("state", {}).get("status", ""),
        })

    result = {"query": bik, "banks": banks, "provider": "dadata"}
    cache_set(key, result, ttl_seconds=3600)
    return result
