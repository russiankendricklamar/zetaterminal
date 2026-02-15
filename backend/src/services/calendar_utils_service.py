"""
Calendar Utils Service — Nager.Date, Russian Calendar (xmlcalendar.ru)

Public holiday data and work calendar information.
"""

import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import aiohttp

from src.services.cache_service import cache_get, cache_set, make_cache_key

NAGER_BASE = "https://date.nager.at/api/v3"
XMLCAL_BASE = "https://xmlcalendar.ru/data/ru"


# ─── Nager.Date ───────────────────────────────────────────────────────────────

async def nager_public_holidays(country_code: str, year: int) -> List[Dict[str, Any]]:
    """Get public holidays for a country and year."""
    key = make_cache_key("nager", "holidays", country_code, year)
    cached = cache_get(key)
    if cached is not None:
        return cached

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{NAGER_BASE}/PublicHolidays/{year}/{country_code}") as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    holidays = []
    for h in data:
        holidays.append({
            "date": h.get("date", ""),
            "localName": h.get("localName", ""),
            "name": h.get("name", ""),
            "countryCode": h.get("countryCode", ""),
            "fixed": h.get("fixed", False),
            "global": h.get("global", True),
            "types": h.get("types", []),
        })

    cache_set(key, holidays, ttl_seconds=86400)
    return holidays


async def nager_next_holidays(country_code: str) -> List[Dict[str, Any]]:
    """Get upcoming public holidays."""
    key = make_cache_key("nager", "next", country_code)
    cached = cache_get(key)
    if cached is not None:
        return cached

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{NAGER_BASE}/NextPublicHolidays/{country_code}") as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)

    cache_set(key, data, ttl_seconds=86400)
    return data


async def nager_is_today_holiday(country_code: str) -> Dict[str, Any]:
    """Check if today is a public holiday."""
    key = make_cache_key("nager", "today", country_code)
    cached = cache_get(key)
    if cached is not None:
        return cached

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{NAGER_BASE}/IsTodayPublicHoliday/{country_code}") as resp:
            # 200 = today is a holiday, 204 = not a holiday
            result = {"is_holiday": resp.status == 200, "country_code": country_code}

    cache_set(key, result, ttl_seconds=3600)
    return result


# ─── Russian Calendar (xmlcalendar.ru) ────────────────────────────────────────

async def russian_calendar(year: int) -> Dict[str, Any]:
    """Get Russian work/holiday calendar for a given year.

    Day types from xmlcalendar.ru:
      t=1: holiday
      t=2: pre-holiday (shortened work day)
      t=3: transferred work day
    """
    key = make_cache_key("rucal", year)
    cached = cache_get(key)
    if cached is not None:
        return cached

    url = f"{XMLCAL_BASE}/{year}/calendar.xml"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            text = await resp.text()

    root = ET.fromstring(text)
    days = []
    type_map = {"1": "holiday", "2": "preholiday", "3": "work_transfer"}

    for month_el in root.findall(".//month"):
        month_num = month_el.attrib.get("m", "")
        for day_el in month_el.findall("day"):
            d_str = day_el.attrib.get("d", "")
            t_str = day_el.attrib.get("t", "1")
            holiday_name = day_el.attrib.get("h", "")

            # Format as YYYY-MM-DD
            if "." in d_str:
                mm, dd = d_str.split(".")
            else:
                mm = month_num.zfill(2)
                dd = d_str.zfill(2)

            days.append({
                "date": f"{year}-{mm.zfill(2)}-{dd.zfill(2)}",
                "type": type_map.get(t_str, "holiday"),
                "type_code": int(t_str) if t_str.isdigit() else 1,
                "name": holiday_name,
            })

    result = {
        "year": year,
        "country": "RU",
        "days": days,
        "total_holidays": sum(1 for d in days if d["type"] == "holiday"),
        "total_preholidays": sum(1 for d in days if d["type"] == "preholiday"),
        "provider": "xmlcalendar",
    }
    cache_set(key, result, ttl_seconds=86400)
    return result
