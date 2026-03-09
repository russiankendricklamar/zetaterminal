# 4.4. Слой базы данных

## Обзор

Слой данных реализует **Repository Pattern** поверх SQLAlchemy async ORM с Neon PostgreSQL. Управляет персистентным хранением финансовых данных, результатов расчётов и метаданных файлов.

## SQLAlchemy Client

### Инициализация
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/zetaterminal")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

Таблицы создаются автоматически при старте через `init_db()` в FastAPI lifespan.

## ORM-модели (sa_models.py)

5 моделей: `BondValuation`, `Portfolio`, `CalculationHistory`, `MarketDataDaily`, `FileRecord`.

## Репозитории

### BondValuationRepository

**Таблица:** `bond_valuations`

**Операции:**
- CRUD с auto-generated timestamps
- Фильтрация по SECID: `get_by_secid(secid)`
- Date range: `get_by_date_range(start, end)`
- Сортировка: по дате оценки (DESC)

### PortfolioRepository

**Таблица:** `portfolios`

**Особенности:**
- JSON для гибкой схемы аллокаций
- Simplified CRUD (create, list, get by ID)

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

**Таблица:** `market_data_daily`

**Особенности:**
- Upsert по композитному ключу `(ticker, data_type, date)`
- Идемпотентная запись: обновление существующих записей

### FileRepository

**Таблица:** `file_records`

**Категории файлов:**
- `bond_registry`
- `swap_registry`
- `option_registry`
- `parquet_export`
- `pdf_report`

## Parquet Export System

### Процесс
```
1. Данные реестра собираются из Pydantic-моделей
2. Конвертация в Pandas DataFrame
3. Сериализация через PyArrow в Parquet
4. Сохранение на локальный диск (exports/)
5. Метаданные сохраняются в FileRepository
```

### Именование файлов
```
exports/registries/{type}_registry_{date}.parquet
```

## Переменные окружения

| Переменная | Описание |
|-----------|----------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |
| `API_KEY` | API authentication key |
