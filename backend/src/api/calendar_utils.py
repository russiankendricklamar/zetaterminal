"""
Calendar Utils Router — Nager.Date, Russian Calendar

Prefix: /api/calendar
"""


from fastapi import APIRouter, HTTPException

from src.services.calendar_utils_service import (
    nager_is_today_holiday,
    nager_next_holidays,
    nager_public_holidays,
    russian_calendar,
)

from src.utils.error_handler import service_endpoint

router = APIRouter()


@router.get("/holidays/{country_code}/{year}")
@service_endpoint("Holidays")
async def holidays(country_code: str, year: int):
    """Public holidays for a country/year (Nager.Date)."""
    return await nager_public_holidays(country_code.upper(), year)
    """Upcoming public holidays (Nager.Date)."""
    return await nager_next_holidays(country_code.upper())
    """Check if today is a public holiday (Nager.Date)."""
    return await nager_is_today_holiday(country_code.upper())
    """Russian work/holiday calendar (xmlcalendar.ru)."""
    return await russian_calendar(year)
    return {"status": "ok", "service": "calendar"}
