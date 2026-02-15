# Backend API — Stochastic Dashboard

FastAPI-бэкенд для количественного финансового анализа: DCF-оценка облигаций, GARCH, HMM, спектральный анализ, оптимизация портфелей (CCMV/HJB), интеграция с 38 внешними API.

## Структура

```
backend/
├── src/
│   ├── api/            # FastAPI роутеры (15+ модулей)
│   ├── services/       # Бизнес-логика и вычисления
│   ├── database/       # Repository pattern (Supabase)
│   └── utils/          # Shared HTTP-клиент, кеш
├── docs/               # Документация
│   ├── architecture.md       # Архитектура бэкенда
│   ├── api-routes.md         # Все API endpoints
│   ├── financial-services.md # Bond Pricing, GARCH, Spectral, HMM
│   ├── external-apis.md      # 38 внешних API интеграций
│   ├── database.md           # Supabase, репозитории, Parquet
│   └── data-flow.md          # Потоки данных
├── requirements.txt
├── runtime.txt         # Python 3.11.0
├── Procfile            # Railway deployment
├── start.sh            # Startup script
└── .env.example
```

## Установка

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
pip install -r requirements.txt
```

## Конфигурация (.env)

```env
CORS_ORIGINS=http://localhost:5173
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
DATABASE_URL=your_postgresql_url

# API-ключи (опционально)
ALPHA_VANTAGE_API_KEY=
FRED_API_KEY=
COINGECKO_API_KEY=
NEWS_API_KEY=
```

## Запуск

```bash
uvicorn src.main:app --reload --port 8000
```

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Ключевые сервисы

| Сервис | Файл | Назначение |
|--------|------|------------|
| Bond Pricing | `bond_pricing.py` | DCF, YTM, Duration, Convexity |
| GARCH | `compute_service.py` | Условная волатильность |
| HMM | `multivariate_hmm_service.py` | Режимы рынка (2-4 состояния) |
| Spectral | `spectral_regime_service.py` | Метод Прони, ACF |
| CCMV | `ccmv_service.py` | Портфельная оптимизация (MIQP) |
| HJB | `hjb_service.py` | Мертон + Монте-Карло |

## Документация

Подробная документация — в [docs/](./docs/).
