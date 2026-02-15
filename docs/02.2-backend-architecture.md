# 2.2. Backend-архитектура

## Обзор

Backend построен на **FastAPI** с чёткой слоистой архитектурой: API-роутеры → Сервисный слой → Репозитории → База данных.

## Структура файлов

```
backend/src/
├── main.py                 # FastAPI приложение, CORS, lifecycle
├── api/                    # Роутеры (15+ модулей)
│   ├── bond.py
│   ├── swap.py
│   ├── forward.py
│   ├── compute.py
│   ├── multivariate_hmm.py
│   ├── spectral_regime.py
│   ├── zcyc.py
│   ├── rudata.py
│   ├── database.py
│   ├── portfolio.py
│   ├── backtest.py
│   ├── stress.py
│   ├── ccmv.py
│   ├── hjb.py
│   ├── market_data.py
│   ├── market_feeds.py
│   ├── macro_data.py
│   ├── crypto_data.py
│   ├── news_ai.py
│   ├── calendar_utils.py
│   ├── security_tools.py
│   └── platform_services.py
├── services/               # Бизнес-логика
│   ├── bond_pricing.py     # DCF, YTM, Duration, Convexity (~1470 строк)
│   ├── bond_service.py     # Оркестрация оценки облигаций
│   ├── compute_service.py  # GARCH(1,1)
│   ├── multivariate_hmm_service.py  # HMM (~888 строк)
│   ├── spectral_regime_service.py   # Спектральный анализ
│   ├── ccmv_service.py     # CCMV оптимизация (MIQP)
│   ├── hjb_service.py      # Мертон + Монте-Карло
│   ├── swap_service.py     # Свопы (IRS, CDS, CCS)
│   ├── forward_service.py  # Форварды
│   ├── portfolio_service.py
│   ├── backtest_service.py
│   ├── zcyc_service.py     # КБД из MOEX
│   ├── rudata_service.py   # RuData/Interfax API
│   ├── yfinance_service.py # Yahoo Finance
│   ├── crypto_data_service.py   # CoinGecko, CoinGap
│   ├── macro_data_service.py    # FRED, ECB, CBR
│   ├── market_feeds_service.py  # Alpha Vantage, Twelve Data, Polygon
│   ├── news_ai_service.py      # NewsAPI, Currents, HuggingFace
│   ├── cache_service.py    # In-memory TTL кеш
│   └── ...
├── database/
│   └── repositories.py     # Repository pattern (265 строк)
└── utils/
    └── http_client.py       # Shared aiohttp session singleton
```

## FastAPI-приложение (main.py)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.http_client import close_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_session()  # Закрытие shared HTTP-сессии

app = FastAPI(
    title="Zeta Terminal API",
    description="Backend API для Zeta Terminal",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Сервисный слой

### Паттерны

**Stateful-сервисы** — хранят конфигурацию и credentials:
- `RuDataService` — кеширование API-токенов, rate limiting

**Stateless-сервисы** — чистые вычислительные функции:
- `ComputeService` — GARCH расчёты
- `SpectralRegimeAnalyzer` — спектральный анализ

### Ключевые сервисы

| Сервис | Файл | Назначение |
|--------|------|------------|
| Bond Pricing | `bond_pricing.py` | DCF, YTM, Duration, Convexity |
| GARCH | `compute_service.py` | Условная волатильность |
| HMM | `multivariate_hmm_service.py` | Режимы рынка |
| Spectral | `spectral_regime_service.py` | Метод Прони, ACF |
| CCMV | `ccmv_service.py` | Портфельная оптимизация |
| HJB | `hjb_service.py` | Мертон + Монте-Карло |

## Repository Pattern

Классы в `database/repositories.py` обеспечивают единообразный CRUD:

| Репозиторий | Таблица | Особенности |
|-------------|---------|-------------|
| `BondValuationRepository` | bond_valuations | Фильтрация по ISIN, date range |
| `PortfolioRepository` | portfolios | JSONB для аллокаций |
| `CalculationHistoryRepository` | calculation_history | Append-only аудит |
| `MarketDataRepository` | market_data | Upsert по (ticker, type, date) |
| `FileRepository` | files | Метаданные Parquet-экспортов |

**Стандартные операции**:
- `create(record)` — вставка с auto-timestamp
- `get_by_id(id)` — получение по ID
- `update(id, record)` — обновление с `updated_at`
- `delete(id)` — удаление

## Shared HTTP Session

Все async-сервисы используют единый `aiohttp.ClientSession`:

```python
# utils/http_client.py
connector = aiohttp.TCPConnector(
    limit=100,           # Макс. соединений
    limit_per_host=10,   # Макс. на хост
    ttl_dns_cache=300,   # DNS-кеш 5 минут
)
timeout = aiohttp.ClientTimeout(total=30, connect=10)
```

Сессия закрывается при shutdown FastAPI через `lifespan`.

## In-Memory Cache

```python
# services/cache_service.py
MAX_CACHE_SIZE = 2000   # Максимум записей

def cache_set(key, value, ttl_seconds=300):
    if len(_cache) >= MAX_CACHE_SIZE:
        _evict_expired()   # Удаление истёкших
    if len(_cache) >= MAX_CACHE_SIZE:
        # LRU — удаление самой старой записи
        oldest = min(_cache, key=lambda k: _cache[k][1])
        del _cache[oldest]
    _cache[key] = (value, time.time() + ttl_seconds)
```

## Обработка ошибок

| Слой | Ответственность | HTTP-коды |
|------|-----------------|-----------|
| Pydantic | Автоматическая валидация | 422 |
| API-роутер | HTTPException | 400, 404, 500 |
| Сервис | Структурированные ответы ошибок | — |
| Репозиторий | Ошибки БД | 500 |

```python
# Типичный API-роутер
@router.post("/valuate")
async def valuate_bond(request: BondValuationRequest):
    try:
        result = await asyncio.to_thread(calculate_bond_valuation, ...)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

## Конфигурация

| Переменная | Назначение | Где используется |
|-----------|------------|------------------|
| `CORS_ORIGINS` | Разрешённые origins | main.py |
| `DATABASE_URL` | PostgreSQL строка подключения | repositories.py |
| `SUPABASE_URL` | Supabase project URL | repositories.py |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | repositories.py |
| `PORT` | Порт сервера (Railway) | start.sh |
