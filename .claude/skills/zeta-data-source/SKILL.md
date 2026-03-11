---
name: zeta-data-source
description: Integrate a new external data source (market data, API, feed) following zetaterminal async patterns. Use when connecting to new APIs, adding data providers, or building data ingestion pipelines.
---

# Zeta Terminal — New Data Source Integration

## Existing Sources (reference patterns)

| Source | File | Pattern |
|--------|------|---------|
| MOEX ISS | `services/zcyc_service.py` | REST + aiohttp, public API, no auth |
| RuData/Interfax | `services/rudata_service.py` | REST + rate limiting (5 req/s), auth token |
| Yahoo Finance | `services/spectral_regime_service.py` | `yfinance` library, sync wrapped in `to_thread` |

## Service Template

`backend/src/services/{source}_service.py`:

```python
"""
{Source Name} data service.

API docs: {url}
Rate limits: {X req/s}
Auth: {method}
"""
import logging
import aiohttp
from typing import Any

logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://api.example.com"
TIMEOUT = aiohttp.ClientTimeout(total=30)
MAX_RETRIES = 3


class {Source}Service:
    """Async client for {Source} API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._session = aiohttp.ClientSession(
                base_url=BASE_URL,
                headers=headers,
                timeout=TIMEOUT,
            )
        return self._session

    async def fetch_data(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Fetch data from {Source}.

        Parameters
        ----------
        params : dict
            Query parameters.

        Returns
        -------
        dict with keys: data, metadata

        Raises
        ------
        ValueError
            If API returns an error or invalid data.
        RuntimeError
            If connection fails after retries.
        """
        session = await self._get_session()

        for attempt in range(MAX_RETRIES):
            try:
                async with session.get("/endpoint", params=params) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error("{Source} API error %d: %s", resp.status, text)
                        if resp.status == 429:  # Rate limited
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise ValueError(f"{Source} API returned {resp.status}")

                    data = await resp.json()
                    return self._parse_response(data)
            except aiohttp.ClientError as e:
                logger.error("{Source} connection error (attempt %d): %s", attempt + 1, e)
                if attempt == MAX_RETRIES - 1:
                    raise RuntimeError(f"{Source} unavailable after {MAX_RETRIES} retries") from e

    def _parse_response(self, raw: dict) -> dict[str, Any]:
        """Parse and validate API response."""
        # Transform to standard format
        return {
            "data": raw,
            "metadata": {
                "source": "{source}",
                "timestamp": datetime.now(datetime.UTC).isoformat(),
            }
        }

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
```

## Router Pattern

```python
@router.get("/api/{source}/fetch")
async def fetch_data(
    param: str = Query(..., description="Query parameter"),
):
    service = {Source}Service(api_key=os.environ.get("{SOURCE}_API_KEY"))
    try:
        result = await service.fetch_data({"param": param})
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail="Data source unavailable") from e
    finally:
        await service.close()
```

## Data Source Priorities (Aladdin Data Platform roadmap)

| Source | Data | Priority |
|--------|------|----------|
| **CBR (ЦБ РФ)** | Ключевая ставка, инфляция, денежная масса | P1 |
| **FRED** | US macro (GDP, CPI, Fed Funds Rate) | P1 |
| **Binance** | Crypto prices, order book | P2 |
| **MOEX ISS (расширение)** | Акции, фьючерсы, индексы | P1 |
| **Finam** | Исторические данные российских акций | P2 |

## Checklist Before Done

- [ ] Async client with `aiohttp` (not `requests`)
- [ ] Retry logic with exponential backoff
- [ ] Rate limiting respected (429 handling)
- [ ] API key from `os.environ`, never hardcoded
- [ ] Timeout configured (`aiohttp.ClientTimeout`)
- [ ] Session cleanup (`close()` method)
- [ ] Response parsed into standard format (`data` + `metadata`)
- [ ] Router with proper error handling (400/503)
- [ ] API docs URL in docstring
- [ ] `ruff check` passes
