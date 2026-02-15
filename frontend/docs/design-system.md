# 3.1. UI-фреймворк и дизайн-система

## Дизайн-система "Liquid Glass"

Визуальная система построена на **Tailwind CSS 3.4.1** с кастомными CSS-переменными, реализующими эстетику "жидкого стекла" — полупрозрачные поверхности с backdrop-blur и световыми акцентами.

## CSS-токены

### Glass-эффекты
```css
.glass-card {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(40px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.glass-button {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.2s ease;
}

.glass-input {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(10px);
}

.glass-table {
  background: rgba(255, 255, 255, 0.02);
  border-collapse: separate;
  border-spacing: 0;
}
```

### Типографика

| Элемент | Размер | Вес | Spacing |
|---------|--------|-----|---------|
| Section titles | 28px | 700 | -0.01em |
| Card headers | 12px uppercase | 600 | 0.05em |
| Body text | 13px | 400-500 | normal |
| Mono (числа, даты) | 13px | 400 | normal |

### Цветовая палитра

```css
:root {
  --accent-blue: rgba(59, 130, 246, 1);
  --accent-green: rgba(34, 197, 94, 1);
  --accent-red: rgba(239, 68, 68, 1);
  --accent-orange: rgba(249, 115, 22, 1);
  --text-primary: rgba(255, 255, 255, 0.87);
  --text-secondary: rgba(255, 255, 255, 0.6);
  --text-muted: rgba(255, 255, 255, 0.38);
  --bg-primary: #0a0a0f;
  --bg-card: rgba(255, 255, 255, 0.03);
}
```

## Переиспользуемые компоненты

### Glass Cards
Контейнеры содержимого с полупрозрачным фоном и blur-эффектом.

### Glass Buttons
Интерактивные элементы с hover-состоянием и transition.

### Glass Inputs
Поля ввода в стилистике стеклянных поверхностей.

### Glass Tables
Таблицы данных с полупрозрачными строками.

### ScrubInput
Интерактивный числовой input с возможностью drag-изменения значения (горизонтальное перетаскивание).

## Адаптивные breakpoints

| Breakpoint | Ширина | Layout |
|-----------|--------|--------|
| Desktop | >1200px | 4-колоночные grid'ы |
| Laptop | 1024-1200px | 2-3 колонки |
| Tablet | 768-1024px | 1 колонка |
| Mobile | <480px | Стек, минимальные отступы |

## Мобильные оптимизации

- Уменьшенный blur (12px вместо 40px на десктопе)
- Скрытые ambient-анимации
- Минимальная высота кнопок 44px (touch target)
- Полноширинные формы
- Collapsible секции
- Swipe-жесты для закрытия sidebar

## Фоновые эффекты (MainLayout)

```
┌──────────────────────────────────┐
│  Animated gradient orbs (z: 1)   │  Плавающие градиентные сферы
│  SVG noise overlay (z: 2)        │  Текстурный шум
│  Content area                    │  Основное содержимое
│  Dynamic Island (z: 1000)        │  Плавающий индикатор задач
│  Sidebar (z: 1100+)              │  Навигационное меню
└──────────────────────────────────┘
```

## Анимации

- **Transition**: 0.2s ease для hover-состояний
- **Gradient orbs**: Медленное floating-движение (CSS keyframes)
- **Page transitions**: Vue `<Transition>` с fade-эффектом
- **Loading states**: Пульсирующий скелетон-placeholder
