# 3.2. Навигация и маршрутизация

## Vue Router

### Конфигурация
```typescript
const router = createRouter({
  history: createWebHashHistory(),  // Hash-based для GitHub Pages
  routes: [
    { path: '/', component: Home },
    { path: '/portfolio', component: Portfolio, meta: { layout: 'main' } },
    { path: '/terminal', component: Terminal },
    { path: '/regime-space', component: RegimeSpace3D, meta: { layout: 'main' } },
    { path: '/bond-valuation', component: BondValuation, meta: { layout: 'main' } },
    { path: '/zcyc', component: ZCYCViewer, meta: { layout: 'main' } },
    { path: '/pricing/options', component: OptionPricing, meta: { layout: 'main' } },
    { path: '/volatility-surface', component: VolatilitySurface, meta: { layout: 'main' } },
    { path: '/monte-carlo', component: MonteCarlo, meta: { layout: 'main' } },
    // ...и другие маршруты
  ]
})
```

### Навигационный guard
```typescript
router.beforeEach((to) => {
  document.title = `${to.meta?.title || to.name} — Stochastic Dashboard`
})
```

### 404 Redirect (GitHub Pages)
`public/404.html` перехватывает прямые URL и конвертирует в hash-маршруты:
```html
<script>
  // /portfolio → /#/portfolio
  const path = window.location.pathname
  window.location.replace('/#' + path)
</script>
```

## Sidebar (Sidebar.vue)

648 строк. Иерархическое меню навигации с группами:

| Группа | Страницы |
|--------|----------|
| Portfolio Analytics | Portfolio, CCMV, HJB |
| Risk Management | Monte Carlo, Stress Testing |
| Market Regimes | Regime Space 3D, Terminal |
| Fixed Income | Bond Valuation, ZCYC Viewer |
| Options | Option Pricing, Volatility Surface |
| Swaps | Swap Valuation, Swap Greeks |
| Forwards | Forward Valuation |
| Bond Reports | Vanilla Bond Report, Floater Report |

### Функции
- Expandable/collapsible группы
- Glass morphism стилизация
- Свёрнутый/развёрнутый режим
- Touch-жесты (swipe-to-close на мобильных)
- Активная подсветка текущего маршрута

## Command Palette (CommandPalette.vue)

663 строки. Глобальная навигация по клавише:

### Активация
- **macOS**: `⌘K` (Cmd+K)
- **Windows/Linux**: `Ctrl+K`

### Возможности
- Real-time fuzzy search по 100+ командам
- Клавиатурная навигация (↑↓ стрелки, Enter, Esc)
- Route metadata-driven список команд
- Мгновенный переход к любой странице

### Структура
```
┌───────────────────────────────┐
│  🔍 Поиск...                  │  Input с autofocus
├───────────────────────────────┤
│  ▸ Portfolio Analytics        │  Группа
│    Portfolio Dashboard        │  Команда
│    CCMV Optimization          │  Команда
│  ▸ Market Regimes             │  Группа
│    Regime Space 3D            │  Команда
│    ...                        │
└───────────────────────────────┘
```

## Breadcrumbs

Автоматически генерируются из `route.name`:
```
Dashboard > Portfolio > CCMV Optimization
```

Отображаются uppercase в header MainLayout.
