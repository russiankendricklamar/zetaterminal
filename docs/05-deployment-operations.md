# 5. Деплой и операции

## Архитектура деплоя

Двухкомпонентная модель с независимым деплоем:

```
┌──────────────────┐          ┌──────────────────┐
│  GitHub Pages    │  HTTPS   │    Railway       │
│  (Frontend)      │ ◄──────► │    (Backend)     │
│  Vue.js SPA      │          │    FastAPI        │
└──────┬───────────┘          └──────┬───────────┘
       │                             │
       │ gh-pages branch             │ Railway deploy
       │                             │
       └───── GitHub Actions ────────┘
                    │
              push to main
```

## CI/CD Pipelines

### Frontend (`.github/workflows/pages.yml`)

**Триггер:** push в main / manual dispatch

```yaml
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
        working-directory: ./frontend
      - run: npm run build
        working-directory: ./frontend
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
      - uses: peaceiris/actions-gh-pages@v4
        with:
          publish_dir: ./frontend/dist
```

### Backend (`.github/workflows/deploy-backend.yml`)

**Триггер:** push в main с path filter `backend/**`

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bervProject/railway-deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
```

Path filtering сокращает ненужные деплои и расход Railway.

## Конфигурация сборки

### Vite (frontend/vite.config.ts)

```typescript
export default defineConfig({
  base: '/stochastic-dashbord-v1/',    // GitHub Pages path
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

**Стратегия code splitting:**
- **vendor** — Vue-экосистема, загружается сразу
- **charts** — Chart.js, lazy-load при навигации на страницу с графиками
- **pdf** — html2pdf, lazy-load при экспорте

### Backend Runtime

**runtime.txt:**
```
python-3.11.0
```

**Procfile:**
```
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

**start.sh:**
```bash
#!/bin/bash
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

## Хостинг

### GitHub Pages (Frontend)

| Настройка | Значение |
|-----------|----------|
| Source | gh-pages branch |
| URL | `russiankendricklamar.github.io/stochastic-dashbord-v1/` |
| Routing | Hash-based (`#/`) |
| Base path | `/stochastic-dashbord-v1/` |
| 404 handling | `404.html` → hash redirect |

### Railway (Backend)

| Настройка | Значение |
|-----------|----------|
| Process | Uvicorn ASGI |
| Host | `0.0.0.0` |
| Port | `$PORT` (Railway-assigned) |
| CORS | `CORS_ORIGINS` env var |
| Health check | Auto HTTP GET / 30s interval |
| Restart | 3 consecutive failures → restart |

### Supabase (Database)

| Компонент | Назначение |
|-----------|------------|
| PostgreSQL | Основное хранилище |
| TimescaleDB | Временные ряды |
| Storage | Parquet файлы |

## Переменные окружения

### GitHub Secrets

| Переменная | Используется в |
|-----------|---------------|
| `VITE_API_BASE_URL` | Frontend build |
| `RAILWAY_TOKEN` | Backend deploy |

### Railway Dashboard

| Переменная | Назначение |
|-----------|------------|
| `PORT` | Порт (auto) |
| `DATABASE_URL` | PostgreSQL |
| `SUPABASE_URL` | Supabase URL |
| `SUPABASE_ANON_KEY` | Supabase key |
| `CORS_ORIGINS` | Разрешённые origins |
| + API keys | 15+ ключей внешних API |

## Мониторинг

### Frontend
Нет встроенного мониторинга. Возможна интеграция с Sentry/LogRocket.

### Backend (Railway)
- Real-time логи
- CPU/memory метрики
- Request statistics
- Health checks (30s interval)

## Rollback

### Frontend
1. Revert коммита в `gh-pages` branch
2. Или: сменить source branch в GitHub Pages на предыдущий коммит

### Backend
1. Railway Dashboard → Deployments
2. Найти предыдущий успешный деплой
3. Нажать "Rollback"
4. Трафик мгновенно переключается на предыдущий контейнер

## Логирование

### Backend
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Bond valuation: {secid} on {date}")
logger.error(f"External API error: {str(e)}")
```

Логи доступны в Railway Dashboard в real-time.
