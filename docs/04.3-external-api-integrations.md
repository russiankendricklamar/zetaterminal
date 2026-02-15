# 4.3. Интеграция с внешними API

## Обзор

Система интегрирует **38 внешних API** через 5 сервисных групп. Все async-сервисы используют shared `aiohttp.ClientSession` с connection pooling.

## Основные источники данных

### MOEX ISS API

**Base URL:** `https://iss.moex.com/iss`

**Аутентификация:** не требуется (публичный API)

**Endpoints:**

| URL | Назначение |
|-----|------------|
| `/engines/stock/zcyc.json` | Кривая бескупонных доходностей (КБД) |
| `/engines/stock/zcyc/yearyields.json` | Годовые доходности |
| `/history/engines/stock/markets/bonds/` | Исторические цены облигаций |
| `/engines/stock/markets/bonds/boards/TQOB/securities` | Список ОФЗ |

**Rate Limiting:** стандартный HTTP throttling

**Fallback:**
```
1. /engines/stock/zcyc.json (основной)
2. build_zcyc_from_bonds() (при 404 — строит кривую из ОФЗ)
3. Ошибка с рекомендацией сменить дату
```

### RuData/Interfax API

**Base URL:** `https://dh2.efir-net.ru/v2/`

**Аутентификация:** Bearer token (login/password → token)

**Rate Limiting:**
- 5 requests/second
- 100 items max per filter
- 1.0 секунда задержки между батчами
- Автоматическое разбиение массивов >100 на батчи

**Реализация (`rudata_service.py`):**
```python
class RuDataService:
    async def _get_token(self, session, login, password):
        """Получение Bearer-токена"""
        ...

    async def _extract_simple(self, session, endpoint, filters):
        """Пагинированная выгрузка с rate limiting"""
        ...

    async def _extract_with_array(self, session, endpoint, array_values):
        """Выгрузка с разбиением массива >100 на батчи"""
        ...
```

**Credential management:**
- Frontend: base64-обфускация в localStorage (Settings.vue)
- Backend: per-request credentials (stateless)

### Yahoo Finance

**Библиотека:** `yfinance` (≥0.2.0)

**Назначение:** исторические OHLCV-данные для спектрального анализа и HMM

**Rate Limiting:** library-managed (автоматическое)

**Lookback:** 2 года по умолчанию

## Группы API-сервисов

### Market Feeds (`market_feeds_service.py`)

| API | Назначение | Ключ |
|-----|------------|------|
| Alpha Vantage | Котировки акций, forex | `ALPHA_VANTAGE_API_KEY` |
| Twelve Data | Real-time данные, технический анализ | `TWELVE_DATA_API_KEY` |
| Polygon.io | Агрегированные рыночные данные | `POLYGON_API_KEY` |

### Macro Data (`macro_data_service.py`)

| API | Назначение | Ключ |
|-----|------------|------|
| FRED | Макроэкономика США (ставки, GDP, CPI) | `FRED_API_KEY` |
| ECB/Frankfurter | Курсы валют ЕЦБ | Не требуется |
| CBR | Курсы валют ЦБ РФ | Не требуется |
| SEC EDGAR | Отчёты компаний (10-K, 10-Q) | User-Agent header |
| OpenFIGI | Маппинг финансовых идентификаторов | `OPENFIGI_API_KEY` |

### Crypto Data (`crypto_data_service.py`)

| API | Назначение | Ключ |
|-----|------------|------|
| CoinGecko | Крипто-рынки, графики, trending | `COINGECKO_API_KEY` |
| CoinGap | Арбитражные возможности | `COINGAP_API_KEY` |

**Кеширование CoinGecko:**
- Markets: 120s (fallback: 600s)
- Coin details: 120s
- Chart: 120s
- Trending: 300s
- Global stats: 120s

### News & AI (`news_ai_service.py`)

| API | Назначение | Ключ |
|-----|------------|------|
| NewsAPI | Финансовые новости | `NEWS_API_KEY` |
| Currents API | Альтернативные новости | `CURRENTS_API_KEY` |
| HuggingFace | NLP (sentiment analysis) | `HUGGINGFACE_API_KEY` |

### Platform Services (`platform_services_service.py`)

| API | Назначение | Ключ |
|-----|------------|------|
| Mailcheck | Email-валидация | Не требуется |
| SendGrid | Email отправка | `SENDGRID_API_KEY` |
| Twilio | SMS | `TWILIO_*` |
| Cloudinary | Хранение изображений | `CLOUDINARY_*` |
| VirusTotal | Проверка безопасности | `VIRUSTOTAL_API_KEY` |

## Shared HTTP Session

Все async-сервисы используют singleton-сессию:

```python
# utils/http_client.py
connector = aiohttp.TCPConnector(
    limit=100,           # Макс. соединений
    limit_per_host=10,   # Макс. на хост
    ttl_dns_cache=300,   # DNS-кеш 5 минут
)
timeout = aiohttp.ClientTimeout(total=30, connect=10)
```

## In-Memory Cache

```python
# services/cache_service.py
MAX_CACHE_SIZE = 2000
# TTL-based кеш с LRU eviction
```

| Данные | TTL |
|--------|-----|
| CoinGecko markets | 120s |
| CoinGecko trending | 300s |
| CoinGap arbitrage | 60s |
| News | 300s |
| Macro data | 300s |

## Обработка ошибок

| Ситуация | Стратегия |
|----------|-----------|
| Network timeout | `aiohttp.ClientTimeout(total=30)` → exception |
| HTTP 429 (rate limit) | Fallback на кешированные данные |
| HTTP 404 (MOEX ZCYC) | Fallback на build_zcyc_from_bonds() |
| Invalid credentials | `{success: false, message: 'Ошибка авторизации'}` |
| API unavailable | Возврат пустого массива / кешированных данных |

## Переменные окружения

| Переменная | API |
|-----------|-----|
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage |
| `TWELVE_DATA_API_KEY` | Twelve Data |
| `POLYGON_API_KEY` | Polygon.io |
| `FRED_API_KEY` | FRED |
| `COINGECKO_API_KEY` | CoinGecko |
| `COINGAP_API_KEY` | CoinGap |
| `NEWS_API_KEY` | NewsAPI |
| `CURRENTS_API_KEY` | Currents |
| `HUGGINGFACE_API_KEY` | HuggingFace |
| `SENDGRID_API_KEY` | SendGrid |
| `VIRUSTOTAL_API_KEY` | VirusTotal |
