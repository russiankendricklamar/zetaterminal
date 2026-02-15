# 2.1. Frontend-архитектура

## Обзор

Frontend — Vue 3 SPA с TypeScript, собираемое Vite. Использует Composition API (`<script setup>`), hash-based маршрутизацию и Pinia для state management.

## Структура файлов

```
frontend/src/
├── main.ts                     # Точка входа: createApp, plugins
├── App.vue                     # Корневой компонент
├── router/
│   └── index.ts                # Определения маршрутов
├── components/
│   ├── Layout/
│   │   ├── MainLayout.vue      # Основной layout с glass-эффектом
│   │   └── Sidebar.vue         # Навигационное меню (648 строк)
│   ├── common/                 # Переиспользуемые UI-компоненты
│   └── CommandPalette.vue      # ⌘K навигация (663 строки)
├── pages/                      # Route-level компоненты
│   ├── RegimeSpace3D.vue       # HMM 3D-визуализация
│   ├── Terminal.vue            # Спектральный терминал
│   ├── BondValuation.vue       # DCF-оценка облигаций
│   ├── OptionPricing.vue       # Ценообразование опционов
│   ├── MonteCarlo.vue          # Монте-Карло симуляция
│   ├── Portfolio.vue           # Портфельный дашборд
│   ├── VolatilitySurface.vue   # 3D поверхность IV
│   ├── CCMVOptimization.vue    # CCMV оптимизация (~3600 строк)
│   ├── HJBOptimization.vue     # HJB оптимизация
│   ├── ZCYCViewer.vue          # Кривая бескупонных доходностей
│   ├── VanillaBondReport.vue   # Отчёт по vanilla-облигациям
│   ├── FloaterBondReport.vue   # Отчёт по плавающим облигациям
│   └── ...
├── services/                   # TypeScript API-клиенты
│   ├── bondService.ts
│   ├── computeService.ts
│   ├── multivariateHmmService.ts
│   ├── spectralRegimeService.ts
│   ├── zcycService.ts
│   ├── ccmvService.ts
│   ├── hjbService.ts
│   └── ...
├── stores/                     # Pinia stores
├── composables/                # Composition API хуки
│   ├── useRegimeSpace3D.ts     # Three.js рендерер режимов
│   └── ...
├── utils/                      # Утилиты (Three.js, HMM)
└── assets/
    └── styles/
        └── main.css            # Дизайн-токены, glass-эффекты
```

## Маршрутизация

### Конфигурация
Используется `createWebHashHistory()` — все маршруты с префиксом `#/`:

```typescript
import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [...]
})
```

### Категории маршрутов
- **Без layout**: `/`, `/docs`, `/terminal`, `/profile`
- **MainLayout**: Большинство страниц приложения
- **Вложенные**: `/pricing/options/*`, `/forwards/*`, `/stress/swaps`

### Navigation Guard
Обновляет `document.title` из route metadata через `beforeEach`.

### 404 Redirect
`public/404.html` конвертирует традиционные пути в hash-маршруты для GitHub Pages.

## State Management (Pinia)

Реактивные stores управляют:
- **Portfolio** — активы, аллокации, метрики риска
- **Theme** — тёмный/светлый режим
- **Tasks** — фоновые вычисления
- **Swap Registry** — реестр свопов

Паттерн использования:
```typescript
const store = usePortfolioStore()
store.initTheme()
```

## Сервисный слой (API-клиенты)

Все TypeScript-сервисы следуют единому паттерну:

1. Читают `VITE_API_BASE_URL` из окружения
2. Определяют TypeScript-интерфейсы для request/response
3. Обрабатывают ошибки сети и HTTP
4. Предоставляют convenience-методы для API-вызовов

```typescript
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function calculateGarch(params: GarchRequest): Promise<GarchResponse> {
  const response = await axios.post(`${API_BASE}/api/compute/garch`, params)
  return response.data
}
```

## Конфигурация сборки (Vite)

```typescript
// vite.config.ts
export default defineConfig({
  base: '/zetaterminal/',   // GitHub Pages
  build: {
    target: 'esnext',
    minify: 'terser',
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia', 'axios'],
          charts: ['chart.js'],
          pdf: ['html2pdf.js']
        }
      }
    }
  }
})
```

**Code splitting**: vendor (Vue-экосистема), charts (Chart.js, lazy-load), pdf (html2pdf, lazy-load).

## Переменные окружения

| Переменная | Описание | Тип |
|-----------|----------|-----|
| `VITE_API_BASE_URL` | URL бэкенда | Build-time |

Переменные с `VITE_` префиксом встраиваются в production-бандл при сборке.

## Глобальные компоненты

| Компонент | Назначение |
|-----------|------------|
| `App.vue` | Корневой компонент |
| `CommandPalette.vue` | ⌘K/Ctrl+K навигация, fuzzy search |
| `TaskWidget.vue` | Индикатор фоновых задач |
| `MainLayout.vue` | Glass-design обёртка |
| `Sidebar.vue` | Иерархическое меню навигации |
| `ScrubInput.vue` | Draggable числовой input |

## Z-Index слои (MainLayout)

| Слой | Z-Index | Содержимое |
|------|---------|------------|
| Background | 1-2 | Анимированные gradient orbs, SVG noise |
| Content | relative | `<router-view>` с прокруткой |
| Dynamic Island | 1000 | Плавающий индикатор задач |
| Sidebar | 1100+ | Навигация с swipe-жестами |
