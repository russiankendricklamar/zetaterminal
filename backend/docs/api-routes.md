# 4.1. Структура API-роутеров

## Обзор

Backend предоставляет **15+ роутеров**, организованных по финансовым доменам. Каждый роутер валидирует входные данные через Pydantic и делегирует вычисления сервисному слою.

## Полная таблица эндпоинтов

### Bond Router (`/api/bond`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/valuate` | DCF-оценка облигации для двух сценариев |
| GET | `/market-yield` | Рыночная доходность из MOEX |

**Request (POST /valuate):**
```json
{
  "secid": "RU000A10AU99",
  "valuationDate": "2026-01-15",
  "discountYield1": 12.5,
  "discountYield2": 13.0,
  "dayCountConvention": "Actual/365F"
}
```

### Swap Router (`/api/swap`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/valuate` | Оценка IRS/CDS/CCS свопа |

### Forward Router (`/api/forward`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/valuate` | Оценка форвардного контракта |

### Compute Router (`/api/compute`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/garch` | GARCH(1,1) волатильность |
| POST | `/statistics` | Описательная статистика |
| GET | `/health` | Проверка работоспособности |

### Multivariate HMM Router (`/api/multivariate-hmm`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/chart-data` | Данные для визуализации HMM |
| GET | `/transition-matrix` | Матрица перехода между режимами |

### Spectral Regime Router (`/api/spectral-regime`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/analyze` | Анализ массива доходностей |
| POST | `/analyze-asset` | Загрузка данных + анализ |
| GET | `/available-assets` | Список доступных активов |

### ZCYC Router (`/api/zcyc`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/zcyc` | Кривая бескупонных доходностей |
| POST | `/zcyc/interpolate` | Интерполяция для заданного срока |
| GET | `/zcyc/dates` | Доступные даты |
| GET | `/zcyc/latest` | Последняя кривая |
| GET | `/zcyc/yearyields` | Годовые доходности |
| GET | `/zcyc/yearyields/dates` | Диапазон дат yearyields |
| GET | `/zcyc/maxdates` | Максимальные даты |
| POST | `/zcyc/discount` | Преобразование в discount curve |

### RuData Router (`/api/rudata`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/test-connection` | Тест подключения к RuData |
| POST | `/query` | Запрос данных облигаций |

### Database Router (`/api/database`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/export/registry/parquet` | Экспорт реестра в Parquet |

### Portfolio Router (`/api/portfolio`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Получить все портфели |
| POST | `/create` | Создать портфель |

### Backtest Router (`/api/backtest`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/run` | Запуск бэктеста |

### Stress Router (`/api/stress`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/test` | Стресс-тестирование |

### CCMV Router (`/api/ccmv`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/optimize` | CCMV-оптимизация портфеля |

### HJB Router (`/api/hjb`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/solve` | Решение HJB уравнения |

### Market Data Router (`/api/market-data`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/fetch` | Получить рыночные данные |

### Дополнительные роутеры

| Префикс | Назначение |
|---------|------------|
| `/api/market-feeds` | Alpha Vantage, Twelve Data, Polygon.io |
| `/api/macro-data` | FRED, ECB, CBR, SEC EDGAR |
| `/api/crypto-data` | CoinGecko, CoinGap |
| `/api/news-ai` | NewsAPI, Currents, HuggingFace |
| `/api/calendar-utils` | Торговые календари |
| `/api/security-tools` | VirusTotal, HIBP |
| `/api/platform-services` | Email, SMS, Cloudinary |

## Валидация (Pydantic)

Все входные данные автоматически валидируются:

```python
class BondValuationRequest(BaseModel):
    secid: str = Field(..., description="ISIN облигации")
    valuationDate: str = Field(..., description="Дата оценки (YYYY-MM-DD)")
    discountYield1: float = Field(..., description="Ставка сценария 1 (%)")
    discountYield2: float = Field(..., description="Ставка сценария 2 (%)")
    dayCountConvention: Optional[str] = Field(None)
```

Невалидный запрос → `422 Unprocessable Entity` с деталями ошибки.

## HTTP-коды ответов

| Код | Назначение |
|-----|------------|
| 200 | Успешный запрос |
| 400 | Невалидные параметры |
| 404 | Ресурс не найден |
| 422 | Ошибка валидации Pydantic |
| 500 | Серверная ошибка |
