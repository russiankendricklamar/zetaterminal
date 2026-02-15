# 1. Обзор системы

## Назначение

Zeta Terminal — платформа для количественного финансового анализа, включающая:

- **Ценообразование деривативов** — опционы (Black-Scholes, Heston, VG, CGMY), свопы, форварды
- **Управление рисками** — VaR, CVaR, стресс-тестирование, сценарный анализ
- **Определение рыночных режимов** — Hidden Markov Models (HMM), спектральный анализ (метод Прони)
- **Оптимизация портфелей** — CCMV (MIQP), HJB (стохастическое управление), Markowitz
- **Анализ фиксированного дохода** — DCF-оценка облигаций, кривые бескупонных доходностей (КБД)
- **Волатильность** — GARCH(1,1), поверхности подразумеваемой волатильности

## Высокоуровневая архитектура

```
┌─────────────────────────┐     HTTPS/JSON     ┌─────────────────────────┐
│     Frontend (SPA)      │ ◄──────────────────►│    Backend (API)        │
│  Vue 3 + TypeScript     │                     │  FastAPI + Python       │
│  GitHub Pages           │                     │  Railway                │
└─────────┬───────────────┘                     └──────────┬──────────────┘
          │                                                │
          │ Hash-routing                                   │ REST APIs
          │ Three.js / ECharts                             ├── MOEX ISS
          │ Pinia stores                                   ├── RuData/Interfax
          │                                                ├── Yahoo Finance
          │                                                ├── CoinGecko
          │                                                └── Supabase (PostgreSQL)
```

Система реализует **decoupled client-server архитектуру**: Vue.js SPA (Single Page Application) общается с Python FastAPI backend через HTTP/HTTPS.

## Ключевые модули (по важности)

| Модуль | Вес | Описание |
|--------|-----|----------|
| 3D Regime Space | 47.68 | HMM-анализ рыночных режимов с Three.js визуализацией |
| Zeta Terminal | 18.54 | Спектральный анализ режимов (метод Прони) |
| ZCYC Viewer | 14.22 | Визуализация кривой бескупонных доходностей |
| Documentation | 12.81 | KaTeX-формулы и LaTeX-рендеринг |
| CCMV/HJB Optimization | 9.12 | Портфельная оптимизация |

## Математические модели

### Ценообразование
- **Bond DCF** — дисконтирование денежных потоков (Actual/365F, Actual/360, 30/360)
- **Black-Scholes-Merton** — европейские опционы с аналитическими формулами
- **Heston** — стохастическая волатильность (FFT/полуаналитический метод)
- **Variance Gamma (VG)** — процесс Леви с гамма-субординатором
- **CGMY** — обобщённый процесс Леви
- **Merton Jump Diffusion** — диффузия с пуассоновскими скачками
- **Bates** — Heston + скачки
- **SABR** — стохастический α-β-ρ

### Статистические модели
- **GARCH(1,1)** — условная гетероскедастичность: `σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}`
- **HMM (2-4 состояния)** — Baum-Welch (EM), Viterbi, Forward-Backward
- **Спектральный анализ** — метод Прони, ACF-декомпозиция, кластеризация полюсов

### Оптимизация
- **CCMV** — Cluster-based Constrained Mean-Variance (MIQP через CVXPy)
- **HJB** — Hamilton-Jacobi-Bellman (стохастическое управление + Монте-Карло)
- **Markowitz** — классическая mean-variance оптимизация

## Структура проекта

```
zetaterminal/
├── frontend/
│   └── src/
│       ├── pages/              # Страницы (Route-level компоненты)
│       ├── components/         # Переиспользуемые UI-компоненты
│       ├── services/           # TypeScript API-клиенты
│       ├── stores/             # Pinia state management
│       ├── composables/        # Composition API утилиты
│       ├── utils/              # Three.js, HMM утилиты
│       ├── router/             # Vue Router конфигурация
│       ├── assets/             # Стили и статика
│       └── main.ts             # Точка входа
├── backend/
│   └── src/
│       ├── api/                # FastAPI роутеры (15+)
│       ├── services/           # Бизнес-логика
│       ├── database/           # Репозитории (Supabase)
│       ├── utils/              # Shared HTTP-клиент, кеш
│       └── main.py             # FastAPI приложение
├── .github/workflows/          # CI/CD пайплайны
└── docs/                       # Документация
```

## Внешние API (38 интеграций)

| Группа | API | Назначение |
|--------|-----|------------|
| Рынок | yfinance, Alpha Vantage, Twelve Data, Polygon.io | Котировки, исторические данные |
| Макро | FRED, ECB/Frankfurter, CBR, SEC EDGAR, OpenFIGI | Макроэкономические данные |
| Крипто | CoinGecko, CoinGap | Криптовалютные рынки, арбитраж |
| Новости | NewsAPI, Currents, HuggingFace | Новостная аналитика |
| Рус. облигации | RuData (Interfax), MOEX ISS | КБД, данные облигаций |

## Безопасность

- **Credentials**: переменные окружения на backend, base64-обфускация в localStorage на frontend
- **CORS**: настраивается через `CORS_ORIGINS` (по умолчанию `*`)
- **Валидация**: Pydantic на backend, TypeScript интерфейсы на frontend

## Деплой

| Компонент | Хостинг | URL |
|-----------|---------|-----|
| Frontend | GitHub Pages | `russiankendricklamar.github.io/zetaterminal/` |
| Backend | Railway | `backend-production.up.railway.app` |
| Database | Supabase | PostgreSQL + TimescaleDB + Storage |
