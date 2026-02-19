# Frontend — Zeta Terminal

Vue 3 SPA с TypeScript для количественного финансового анализа: 3D-визуализация рыночных режимов, ценообразование деривативов, портфельная оптимизация, анализ облигаций.

## Структура

```
frontend/
├── src/
│   ├── pages/          # Route-level компоненты
│   ├── components/     # Переиспользуемые UI-компоненты
│   ├── services/       # TypeScript API-клиенты
│   ├── stores/         # Pinia state management
│   ├── composables/    # Composition API хуки
│   ├── utils/          # Three.js, HMM утилиты
│   ├── router/         # Vue Router (hash-based)
│   ├── assets/         # Стили, статика
│   └── main.ts         # Точка входа
├── docs/               # Документация
│   ├── architecture.md         # Frontend-архитектура
│   ├── design-system.md        # Liquid Glass дизайн-система
│   ├── navigation-routing.md   # Sidebar, Command Palette
│   ├── portfolio-hmm.md        # HMM, 3D Regime Space
│   ├── market-terminal.md      # Спектральный терминал
│   ├── fixed-income.md         # Облигации, ZCYC
│   ├── derivatives-pricing.md  # Опционы, Vol Surface
│   └── portfolio-optimization.md # GARCH, Monte Carlo, CCMV, HJB
├── vite.config.ts
├── package.json
└── index.html
```

## Установка

```bash
npm install
```

## Конфигурация (.env.local)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Запуск

```bash
npm run dev       # Dev-сервер (Vite HMR)
npm run build     # Production сборка
npm run preview   # Предпросмотр билда
```

Приложение: `http://localhost:5173`

## Ключевые страницы

| Страница | Компонент | Описание |
|----------|-----------|----------|
| Regime Space 3D | `RegimeSpace3D.vue` | HMM + Three.js визуализация |
| Terminal | `Terminal.vue` | Спектральный анализ (Прони) |
| Bond Valuation | `BondValuation.vue` | DCF-оценка облигаций |
| ZCYC Viewer | `ZCYCViewer.vue` | Кривая бескупонных доходностей |
| Option Pricing | `OptionPricing.vue` | 6 моделей (BSM, Heston, VG...) |
| Vol Surface | `VolatilitySurface.vue` | 3D IV поверхность |
| Portfolio | `Portfolio.vue` | Портфельный дашборд |
| CCMV | `CCMVOptimization.vue` | Портфельная оптимизация |
| Monte Carlo | `MonteCarlo.vue` | GBM-симуляция |

## Дизайн-система

"Liquid Glass" — полупрозрачные поверхности с backdrop-blur. Классы: `.glass-card`, `.glass-button`, `.glass-input`, `.glass-table`.

## Документация

Подробная документация — в [docs/](./docs/).
