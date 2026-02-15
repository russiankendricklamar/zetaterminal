# Stochastic Dashboard v1

Платформа для количественного финансового анализа: оценка деривативов, управление рисками, определение рыночных режимов, оптимизация портфелей и анализ инструментов с фиксированным доходом.

## Содержание документации

| # | Раздел | Описание |
|---|--------|----------|
| 1 | [Обзор системы](./01-overview.md) | Архитектура, стек технологий, ключевые модули |
| 2 | [Архитектура](./02-architecture.md) | Общая архитектура системы |
| 2.1 | [Frontend-архитектура](./02.1-frontend-architecture.md) | Vue 3, маршрутизация, состояние, дизайн-система |
| 2.2 | [Backend-архитектура](./02.2-backend-architecture.md) | FastAPI, сервисный слой, репозитории |
| 2.3 | [Потоки данных и интеграция](./02.3-data-flow-integration.md) | Паттерны обмена данными, внешние API |
| 3 | [Frontend-приложение](./03-frontend-application.md) | Обзор клиентского приложения |
| 3.1 | [UI-фреймворк и дизайн-система](./03.1-ui-framework-design-system.md) | Tailwind CSS, Liquid Glass, адаптивность |
| 3.2 | [Навигация и маршрутизация](./03.2-navigation-routing.md) | Vue Router, Sidebar, Command Palette |
| 3.3 | [Портфельный анализ и HMM](./03.3-portfolio-hmm-regime-detection.md) | HMM, 3D-визуализация, корреляции |
| 3.4 | [Терминал анализа рынка](./03.4-market-analysis-terminal.md) | Спектральный анализ, метод Прони |
| 3.5 | [Фиксированный доход и облигации](./03.5-fixed-income-bond-valuation.md) | DCF, КБД, день-счёт конвенции |
| 3.6 | [Ценообразование деривативов](./03.6-derivatives-pricing.md) | Опционы, поверхность волатильности, свопы |
| 3.7 | [Оптимизация портфеля](./03.7-portfolio-optimization.md) | GARCH, Монте-Карло, стресс-тесты, CCMV, HJB |
| 4 | [Backend-сервисы](./04-backend-services.md) | Обзор серверной части |
| 4.1 | [Структура API-роутеров](./04.1-api-router-structure.md) | 15+ роутеров, эндпоинты, валидация |
| 4.2 | [Сервисы финансовой аналитики](./04.2-financial-analytics-services.md) | Bond Pricing, Spectral, GARCH, HMM |
| 4.3 | [Интеграция с внешними API](./04.3-external-api-integrations.md) | MOEX, RuData, Yahoo Finance |
| 4.4 | [Слой базы данных](./04.4-database-layer.md) | Supabase, репозитории, Parquet |
| 5 | [Деплой и операции](./05-deployment-operations.md) | CI/CD, хостинг, мониторинг |
| 6 | [Руководство разработчика](./06-development-guide.md) | Локальная настройка, стек, стилизация |

## Быстрый старт

```bash
# Frontend
cd frontend && npm install && npm run dev

# Backend
cd backend && pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Стек технологий

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Frontend | Vue.js + TypeScript | 3.4.15 |
| Сборка | Vite | 5.0.8 |
| 3D-графика | Three.js | 0.182.0 |
| Графики | ECharts / Chart.js | 6.0.0 / 4.4.1 |
| Backend | FastAPI + Python | ≥0.104.0 |
| Вычисления | NumPy / SciPy / Pandas | ≥1.24 / ≥1.11 / ≥2.0 |
| Оптимизация | CVXPy | ≥1.3.0 |
| База данных | Supabase (PostgreSQL) | — |
| Хостинг | GitHub Pages + Railway | — |

## Лицензия

MIT License. Исключительно для исследовательских и образовательных целей.
