"""
Crypto Data Router — CoinGecko, CoinGap

Prefix: /api/crypto-data
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.services.crypto_data_service import (
    coingap_arbitrage,
    coingecko_coin,
    coingecko_global,
    coingecko_market_chart,
    coingecko_markets,
    coingecko_trending,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/coingecko/markets")
async def cg_markets(
    vs_currency: str = Query("usd"),
    per_page: int = Query(100),
    page: int = Query(1),
    order: str = Query("market_cap_desc"),
):
    """Top crypto markets from CoinGecko."""
    try:
        return await coingecko_markets(vs_currency, per_page, page, order)
    except Exception as e:
        logger.error("CoinGecko markets failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/coingecko/coin/{coin_id}")
async def cg_coin(coin_id: str):
    """Coin details from CoinGecko."""
    try:
        return await coingecko_coin(coin_id)
    except Exception as e:
        logger.error("CoinGecko coin details failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/coingecko/coin/{coin_id}/chart")
async def cg_chart(
    coin_id: str,
    vs_currency: str = Query("usd"),
    days: int = Query(30),
):
    """Price history chart from CoinGecko."""
    try:
        return await coingecko_market_chart(coin_id, vs_currency, days)
    except Exception as e:
        logger.error("CoinGecko market chart failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/coingecko/trending")
async def cg_trending():
    """Trending coins from CoinGecko."""
    try:
        return await coingecko_trending()
    except Exception as e:
        logger.error("CoinGecko trending failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/coingecko/global")
async def cg_global():
    """Global crypto market stats."""
    try:
        return await coingecko_global()
    except Exception as e:
        logger.error("CoinGecko global stats failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/coingap/arbitrage")
async def gap_arbitrage():
    """Arbitrage opportunities from CoinGap."""
    try:
        return await coingap_arbitrage()
    except Exception as e:
        logger.error("CoinGap arbitrage failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-data"}
