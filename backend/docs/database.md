# 4.4. Слой базы данных

## Обзор

Слой данных реализует **Repository Pattern** поверх Supabase (PostgreSQL + TimescaleDB). Управляет персистентным хранением финансовых данных, результатов расчётов и метаданных файлов.

## Supabase Client

### Инициализация
```python
from supabase import create_client

def get_supabase_client():
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY")
    )
```

Таймаут подключения: 30 секунд. Все репозитории получают клиент через эту фабричную функцию.

## Репозитории

### BondValuationRepository

**Таблица:** `bond_valuations`

**Операции:**
- CRUD с auto-generated timestamps
- Фильтрация по ISIN: `get_by_isin(isin)`
- Date range: `get_by_date_range(start, end)`
- Сортировка: по дате оценки (DESC)

### PortfolioRepository

**Таблица:** `portfolios`

**Особенности:**
- JSONB для гибкой схемы аллокаций
- Simplified CRUD (create, list, get by ID)

```json
{
  "name": "Conservative Portfolio",
  "assets": [
    {"symbol": "SBER", "weight": 0.15},
    {"symbol": "GAZP", "weight": 0.10},
    {"symbol": "OFZ-26238", "weight": 0.30}
  ]
}
```

### CalculationHistoryRepository

**Таблица:** `calculation_history`

**Паттерн:** Append-only аудит (записи создаются, но не модифицируются и не удаляются).

**Типы расчётов:**
- `bond_valuation`
- `swap_pricing`
- `option_pricing`
- `garch_estimation`
- `hmm_analysis`

### MarketDataRepository

**Таблица:** `market_data` (TimescaleDB hypertable)

**Особенности:**
- Upsert по композитному ключу `(ticker, data_type, date)`
- Идемпотентная запись: обновление существующих записей

```python
def create_or_update(self, ticker, data_type, date, data):
    """Upsert с conflict resolution"""
    response = self.client.table("market_data") \
        .upsert(record, on_conflict="ticker,data_type,date") \
        .execute()
```

### FileRepository

**Таблица:** `files`

**Категории файлов:**
- `bond_registry`
- `swap_registry`
- `option_registry`
- `parquet_export`
- `pdf_report`

## TimescaleDB

### Оптимизации для временных рядов
- Chunk-based partitioning (автоматическое)
- Time-based компрессия для исторических данных
- Continuous aggregates для агрегированных метрик
- Оптимизированные range queries по дате

### Пагинация
По умолчанию 100 записей на запрос с настраиваемым лимитом.

## Parquet Export System

### Процесс

```
1. Данные реестра собираются из Pydantic-моделей
2. Конвертация в Pandas DataFrame
3. Сериализация через PyArrow в Parquet
4. Загрузка в Supabase Storage bucket
5. Метаданные сохраняются в FileRepository
```

### Характеристики
- Сжатие: 5-10x vs CSV
- Сохранение типов данных (даты, decimal)
- Встроенная схема метаданных
- Поддержка Pandas, DuckDB, Spark

### Именование файлов
```
files/registries/{type}_registry_{date}.parquet
```

Примеры:
- `files/registries/bond_registry_2026-01-15.parquet`
- `files/registries/swap_registry_2026-01-15.parquet`

## Pydantic модели данных

Type-safe валидация на уровне приложения перед персистентностью:

```python
class BondValuationRecord(BaseModel):
    secid: str
    valuation_date: date
    clean_price: float
    dirty_price: float
    duration: float
    convexity: float
    ytm: float
    day_count: str
    created_at: Optional[datetime] = None
```

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `SUPABASE_URL` | URL проекта Supabase |
| `SUPABASE_ANON_KEY` | Anonymous key для клиента |
| `DATABASE_URL` | PostgreSQL connection string (альтернативно) |
