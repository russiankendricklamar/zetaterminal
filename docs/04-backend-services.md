# 4. Backend-сервисы

## Обзор

Серверная часть построена на FastAPI и обеспечивает:
- Финансовые вычисления (DCF, GARCH, HMM, Spectral, CCMV, HJB)
- Интеграцию с 38 внешними API
- Персистентность данных через Supabase
- Экспорт реестров в Parquet

## Архитектура сервисного слоя

```
API Router (валидация)
    ↓
Service Layer (бизнес-логика)
    ↓
Repository (CRUD) ──────── External APIs (данные)
    ↓
Database (Supabase PostgreSQL)
```

## Подробные разделы

- [4.1 Структура API-роутеров](./04.1-api-router-structure.md) — 15+ роутеров, эндпоинты, Pydantic-схемы
- [4.2 Сервисы финансовой аналитики](./04.2-financial-analytics-services.md) — Bond Pricing, GARCH, Spectral, HMM
- [4.3 Интеграция с внешними API](./04.3-external-api-integrations.md) — MOEX, RuData, Yahoo Finance, CoinGecko
- [4.4 Слой базы данных](./04.4-database-layer.md) — Supabase, репозитории, Parquet
