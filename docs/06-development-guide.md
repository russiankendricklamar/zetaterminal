# 6. Руководство разработчика

## Требования

| Компонент | Минимальная версия |
|-----------|-------------------|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |
| PostgreSQL | 15+ (опционально) |

## Быстрый старт

### 1. Клонирование

```bash
git clone https://github.com/russiankendricklamar/stochastic-dashbord-v1.git
cd stochastic-dashbord-v1
```

### 2. Backend

```bash
cd backend

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# или: venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла
cat > .env << 'EOF'
CORS_ORIGINS=http://localhost:5173
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key
DATABASE_URL=your_postgresql_url

# API ключи (опционально)
ALPHA_VANTAGE_API_KEY=
FRED_API_KEY=
COINGECKO_API_KEY=
NEWS_API_KEY=
EOF

# Запуск
uvicorn src.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend

# Установка зависимостей
npm install

# Создание .env.local
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Запуск dev-сервера
npm run dev
```

Приложение доступно по адресу `http://localhost:5173`.

### 4. Проверка

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs` (Swagger UI)
- Health: `http://localhost:8000/health`

## Стек технологий

### Почему Vue 3?

- **Composition API** — лучшая переиспользуемость логики через composables
- **TypeScript** — нативная поддержка
- **Reactivity system** — granular обновления DOM
- **Ecosystem** — Pinia, Vue Router, DevTools

### Почему FastAPI?

- **Async/await** — нативная асинхронность для I/O-bound задач
- **Pydantic** — автоматическая валидация и OpenAPI-документация
- **Производительность** — один из самых быстрых Python-фреймворков
- **Type hints** — IDE-поддержка, автодополнение

### Почему Supabase?

- **PostgreSQL** — мощная реляционная БД
- **TimescaleDB** — оптимизация для временных рядов
- **Storage** — Parquet файлы
- **Client SDK** — простой Python/JS клиент

## State Management (Pinia)

### Паттерн

```typescript
// stores/portfolioStore.ts
import { defineStore } from 'pinia'

export const usePortfolioStore = defineStore('portfolio', {
  state: () => ({
    assets: [],
    metrics: null,
    loading: false
  }),
  getters: {
    totalValue: (state) => state.assets.reduce((sum, a) => sum + a.value, 0),
    sharpe: (state) => state.metrics?.sharpe ?? 0
  },
  actions: {
    async fetchPortfolio() {
      this.loading = true
      try {
        const data = await portfolioService.getPortfolio()
        this.assets = data.assets
        this.metrics = data.metrics
      } finally {
        this.loading = false
      }
    }
  }
})
```

### Использование в компоненте

```vue
<script setup lang="ts">
import { usePortfolioStore } from '@/stores/portfolioStore'

const store = usePortfolioStore()
onMounted(() => store.fetchPortfolio())
</script>
```

## Стилизация и дизайн-токены

### Tailwind CSS конфигурация

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        accent: '#22c55e',
        danger: '#ef4444',
      },
      backdropBlur: {
        glass: '40px',
      }
    }
  }
}
```

### Принципы стилизации

1. **Utility-first** — Tailwind классы в шаблонах
2. **Glass morphism** — `.glass-card`, `.glass-button`, `.glass-input`
3. **Dark theme** — основной режим
4. **Responsive** — Tailwind breakpoints (`sm`, `md`, `lg`)
5. **Mono font** — для числовых значений и кода

## Конвенции кода

### Frontend
- `<script setup>` syntax (Composition API)
- TypeScript over JavaScript
- Tailwind utilities over custom CSS
- Composables для переиспользуемой логики
- Services для API-вызовов
- Stores для глобального состояния

### Backend
- Type hints на всех функциях
- Pydantic models для request/response
- Service layer для бизнес-логики
- Repository pattern для данных
- `asyncio.to_thread()` для sync I/O

### Git
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Язык: русский в UI, английский в коде/API

## Отладка

### Vue DevTools
- Инспекция иерархии компонентов
- Отладка Pinia stores
- Timeline событий

### Vite HMR
Hot Module Replacement сохраняет состояние при обновлении компонентов.

### API status
Заголовок приложения показывает статус подключения к backend и задержку.

### FastAPI Swagger
`http://localhost:8000/docs` — интерактивная документация всех API.

## Скрипты

### Frontend

| Скрипт | Назначение |
|--------|------------|
| `npm run dev` | Dev-сервер (Vite HMR) |
| `npm run build` | Production сборка |
| `npm run preview` | Предпросмотр production билда |
| `npm run type-check` | TypeScript проверка |

### Backend

| Команда | Назначение |
|---------|------------|
| `uvicorn src.main:app --reload` | Dev-сервер с auto-reload |
| `uvicorn src.main:app` | Production сервер |
| `pip install -r requirements.txt` | Установка зависимостей |

## Структура imports

### Frontend
```typescript
import { ref, computed, onMounted } from 'vue'          // Vue core
import { usePortfolioStore } from '@/stores/...'         // Stores
import { calculateGarch } from '@/services/...'          // API clients
import { useRegimeSpace3D } from '@/composables/...'     // Composables
```

### Backend
```python
from fastapi import APIRouter, HTTPException              # Framework
from pydantic import BaseModel, Field                     # Validation
from src.services.bond_pricing import calculate_dcf       # Business logic
from src.database.repositories import BondValuationRepo   # Data access
from src.utils.http_client import get_session             # HTTP client
```

## Лицензия и дисклеймер

**MIT License** — исключительно для исследовательских и образовательных целей.

**Допущения:**
- No-arbitrage, perfect markets, стандартные risk-neutral pricing assumptions
- Результаты чувствительны к качеству входных данных и калибровке параметров
- Требуется независимая валидация перед production использованием
