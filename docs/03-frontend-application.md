# 3. Frontend-приложение

## Обзор

Клиентское приложение — Vue 3 SPA с TypeScript, развёрнутое на GitHub Pages. Предоставляет интерфейс для всех финансовых инструментов платформы.

## Ключевые страницы

| Страница | Компонент | Назначение |
|----------|-----------|------------|
| Regime Space 3D | `RegimeSpace3D.vue` | Интерактивная 3D-визуализация HMM-режимов |
| Terminal | `Terminal.vue` | Спектральный анализ в стиле терминала |
| Bond Valuation | `BondValuation.vue` | DCF-оценка облигаций |
| ZCYC Viewer | `ZCYCViewer.vue` | Кривая бескупонных доходностей |
| Option Pricing | `OptionPricing.vue` | Ценообразование опционов (6 моделей) |
| Volatility Surface | `VolatilitySurface.vue` | 3D поверхность подразумеваемой волатильности |
| Portfolio | `Portfolio.vue` | Портфельный дашборд с KPI |
| CCMV Optimization | `CCMVOptimization.vue` | CCMV портфельная оптимизация |
| HJB Optimization | `HJBOptimization.vue` | Стохастическое управление |
| Monte Carlo | `MonteCarlo.vue` | Монте-Карло симуляция |
| Swap Valuation | `SwapValuation.vue` | Оценка свопов (IRS, CDS, CCS) |
| Reports | `Reports.vue` | Генерация отчётов |

## Архитектурные слои

```
┌──────────────────────────────────┐
│          Pages (Views)           │  Route-level компоненты
├──────────────────────────────────┤
│         Components               │  Переиспользуемые UI
├──────────────────────────────────┤
│      Composables / Utils         │  Composition API хуки, Three.js
├──────────────────────────────────┤
│         Pinia Stores             │  Реактивное состояние
├──────────────────────────────────┤
│        Service Layer             │  HTTP-клиенты (Axios)
├──────────────────────────────────┤
│       Vue Router (Hash)          │  Клиентская маршрутизация
└──────────────────────────────────┘
```

## Подробные разделы

- [3.1 UI-фреймворк и дизайн-система](./03.1-ui-framework-design-system.md)
- [3.2 Навигация и маршрутизация](./03.2-navigation-routing.md)
- [3.3 Портфельный анализ и HMM](./03.3-portfolio-hmm-regime-detection.md)
- [3.4 Терминал анализа рынка](./03.4-market-analysis-terminal.md)
- [3.5 Фиксированный доход и облигации](./03.5-fixed-income-bond-valuation.md)
- [3.6 Ценообразование деривативов](./03.6-derivatives-pricing.md)
- [3.7 Оптимизация портфеля](./03.7-portfolio-optimization.md)
