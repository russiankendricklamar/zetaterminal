"""
Crypto Data Router — CoinGecko, CoinGap

Prefix: /api/crypto-data
"""


from fastapi import APIRouter, Query

from src.services.crypto_data_service import (
    coingap_arbitrage,
    coingecko_coin,
    coingecko_global,
    coingecko_market_chart,
    coingecko_markets,
    coingecko_trending,
)

from src.utils.error_handler import service_endpoint

router = APIRouter()


@router.get("/coingecko/markets")
@service_endpoint("Cg Markets")
async def cg_markets(
    vs_currency: str = Query("usd"),
    per_page: int = Query(100),
    page: int = Query(1),
    order: str = Query("market_cap_desc"),
):
    """Top crypto markets from CoinGecko."""
    return await coingecko_markets(vs_currency, per_page, page, order)
@router.get("/coingecko/coin/{coin_id}")
@service_endpoint("Cg Coin")
async def cg_coin(coin_id: str):
    """Coin details from CoinGecko."""
    return await coingecko_coin(coin_id)
@router.get("/coingecko/coin/{coin_id}/chart")
async def cg_chart(
    coin_id: str,
    vs_currency: str = Query("usd"),
    days: int = Query(30),
):
    """Price history chart from CoinGecko."""
    return await coingecko_market_chart(coin_id, vs_currency, days)
@router.get("/coingecko/trending")
@service_endpoint("Cg Trending")
async def cg_trending():
    """Trending coins from CoinGecko."""
    return await coingecko_trending()
@router.get("/coingecko/global")
async def cg_global():
    """Global crypto market stats."""
    return await coingecko_global()
@router.get("/coingap/arbitrage")
@service_endpoint("Gap Arbitrage")
async def gap_arbitrage():
    """Arbitrage opportunities from CoinGap."""
    return await coingap_arbitrage()
@router.get("/health")
async def health():
    return {"status": "ok", "service": "crypto-data"}
