# 2. Архитектура

## Обзор

Stochastic Dashboard реализует **decoupled client-server архитектуру** с чётким разделением ответственности:

- **Frontend** — UI, маршрутизация, 3D-визуализация, состояние приложения
- **Backend** — вычисления, персистентность данных, интеграция с внешними API

Коммуникация — REST API через HTTPS с JSON-пейлоадами.

## Диаграмма взаимодействия

```
┌──────────────┐    HTTP/JSON    ┌──────────────┐    SQL/REST     ┌──────────────┐
│   Vue.js     │ ──────────────► │   FastAPI    │ ──────────────► │  Supabase    │
│   Frontend   │ ◄────────────── │   Backend    │ ◄────────────── │  PostgreSQL  │
└──────┬───────┘                 └──────┬───────┘                 └──────────────┘
       │                                │
       │ Pinia Stores                   │ External APIs
       │ Three.js Renderer              ├── MOEX ISS
       │ ECharts                        ├── RuData/Interfax
       │ Vue Router                     ├── Yahoo Finance
       │                                ├── CoinGecko/CoinGap
       │                                ├── Alpha Vantage
       │                                ├── FRED / ECB / CBR
       │                                └── NewsAPI / HuggingFace
```

## Стек технологий

### Frontend

| Технология | Версия | Назначение |
|-----------|--------|------------|
| Vue.js | 3.4.15 | Реактивный фреймворк |
| TypeScript | 5.3.3 | Типизация |
| Vite | 5.0.8 | Сборка и HMR |
| Vue Router | 4.6.4 | Маршрутизация (hash-based) |
| Pinia | 2.1.7 | Управление состоянием |
| Three.js | 0.182.0 | 3D-визуализация |
| Chart.js | 4.4.1 | 2D-графики |
| ECharts | 6.0.0 | Продвинутые графики |
| KaTeX | 0.16.27 | LaTeX-рендеринг формул |
| XLSX | 0.18.5 | Excel I/O |
| Tailwind CSS | 3.4.1 | Утилитарные стили |
| Axios | 1.6.5 | HTTP-клиент |

### Backend

| Технология | Версия | Назначение |
|-----------|--------|------------|
| FastAPI | ≥0.104.0 | ASGI-фреймворк с OpenAPI |
| Uvicorn | ≥0.24.0 | ASGI-сервер |
| Pydantic | ≥2.0.0 | Валидация данных |
| NumPy | ≥1.24.0 | Линейная алгебра, статистика |
| Pandas | ≥2.0.0 | DataFrames, временные ряды |
| SciPy | ≥1.11.0 | Оптимизация, кластеризация |
| PyArrow | ≥14.0.0 | Parquet I/O |
| CVXPy | ≥1.3.0 | Выпуклая оптимизация (MIQP) |
| Supabase | ≥2.0.0 | PostgreSQL + Storage клиент |
| aiohttp | ≥3.9.0 | Async HTTP-клиент |
| yfinance | ≥0.2.0 | Yahoo Finance данные |

## Структура API-роутеров

| Префикс | Модуль | Ключевые маршруты |
|---------|--------|-------------------|
| `/api/bond` | bond.py | `POST /valuate`, `GET /market-yield` |
| `/api/swap` | swap.py | `POST /valuate` |
| `/api/forward` | forward.py | `POST /valuate` |
| `/api/compute` | compute.py | `POST /garch`, `POST /statistics` |
| `/api/multivariate-hmm` | multivariate_hmm.py | `GET /chart-data`, `GET /transition-matrix` |
| `/api/spectral-regime` | spectral_regime.py | `POST /analyze`, `GET /available-assets` |
| `/api/zcyc` | zcyc.py | `GET /zcyc`, `POST /interpolate`, `GET /dates` |
| `/api/rudata` | rudata.py | `POST /test-connection`, `POST /query` |
| `/api/database` | database.py | `POST /export/registry/parquet` |
| `/api/portfolio` | portfolio.py | `GET /`, `POST /create` |
| `/api/backtest` | backtest.py | `POST /run` |
| `/api/stress` | stress.py | `POST /test` |
| `/api/ccmv` | ccmv.py | `POST /optimize` |
| `/api/hjb` | hjb.py | `POST /solve` |
| `/api/market-data` | market_data.py | `GET /fetch` |

## Поток запроса

```
1. Компонент вызывает TypeScript-сервис
2. Сервис отправляет HTTP-запрос через Axios (JSON)
3. FastAPI роутер валидирует через Pydantic
4. Сервисный слой выполняет бизнес-логику
5. Репозиторий обращается к Supabase (опционально)
6. Ответ JSON возвращается клиенту
7. Компонент обновляет реактивное состояние
```

## Архитектурные решения

### Hash-based маршрутизация
GitHub Pages — статический файловый сервер без server-side routing. Hash-routing (`#/portfolio`) обеспечивает клиентскую маршрутизацию без серверной конфигурации.

### Repository Pattern
Чёткое разделение ответственности: API-роутеры → Сервисы → Репозитории → БД. Упрощает тестирование и замену реализации хранилища.

### Parquet для экспорта
Сжатие 5-10x vs CSV, сохранение типов данных, поддержка Pandas/DuckDB.

### Сервисный слой
API-роутеры — тонкие контроллеры для валидации. Бизнес-логика изолирована в сервисах для переиспользования и тестируемости.

### Async/Await
Финансовые API часто имеют rate limits и высокую задержку. Async I/O позволяет обрабатывать множество запросов конкурентно без блокировки потоков.

### Shared HTTP Session
Все async-сервисы используют singleton `aiohttp.ClientSession` с connection pooling (limit=100, ttl_dns=300s) для эффективного переиспользования соединений.
