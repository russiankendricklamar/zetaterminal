"""
Calendar Utils Router — Nager.Date, Russian Calendar

Prefix: /api/calendar
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.services.calendar_utils_service import (
    nager_public_holidays,
    nager_next_holidays,
    nager_is_today_holiday,
    russian_calendar,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/holidays/{country_code}/{year}")
async def holidays(country_code: str, year: int):
    """Public holidays for a country/year (Nager.Date)."""
    try:
        return await nager_public_holidays(country_code.upper(), year)
    except Exception as e:
        logger.error("Calendar operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/next-holidays/{country_code}")
async def next_holidays(country_code: str):
    """Upcoming public holidays (Nager.Date)."""
    try:
        return await nager_next_holidays(country_code.upper())
    except Exception as e:
        logger.error("Calendar operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/is-today-holiday/{country_code}")
async def today_holiday(country_code: str):
    """Check if today is a public holiday (Nager.Date)."""
    try:
        return await nager_is_today_holiday(country_code.upper())
    except Exception as e:
        logger.error("Calendar operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/russia/{year}")
async def russia_calendar(year: int):
    """Russian work/holiday calendar (xmlcalendar.ru)."""
    try:
        return await russian_calendar(year)
    except Exception as e:
        logger.error("Calendar operation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health():
    return {"status": "ok", "service": "calendar"}
