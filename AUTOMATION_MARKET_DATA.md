# Автоматизация загрузки рыночных данных

## Варианты автоматизации

### 1. n8n Workflow (Рекомендуется)

Создай workflow в n8n:

```
Schedule Trigger (Cron: 0 9 * * *) 
  → HTTP Request (POST /api/market-data/fetch-daily)
  → IF Node (проверка успешности)
  → Email/Slack (уведомление об ошибках)
```

**Настройка HTTP Request:**
- **Method:** POST
- **URL:** `https://stochastic-dashbord-v1-production.up.railway.app/api/market-data/fetch-daily`
- **Authentication:** None (или добавь API key если нужно)

### 2. Cron Job (Linux/Mac)

Добавь в crontab:
```bash
# Каждый день в 9:00
0 9 * * * cd /path/to/project/backend && python scripts/fetch_market_data.py >> logs/market_data.log 2>&1
```

### 3. GitHub Actions (если нужно)

Создай `.github/workflows/daily-market-data.yml`:
```yaml
name: Fetch Daily Market Data

on:
  schedule:
    - cron: '0 9 * * *'  # Каждый день в 9:00 UTC
  workflow_dispatch:

jobs:
  fetch-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Fetch market data
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        run: |
          cd backend
          python scripts/fetch_market_data.py
```

### 4. Railway Cron Job (через API endpoint)

Создай API endpoint для запуска через HTTP запрос (уже есть в `api/market_data.py`).

Затем используй внешний сервис для планирования (например, cron-job.org или n8n).

## Настройка скрипта

1. Отредактируй список тикеров в `scripts/fetch_market_data.py`:
   ```python
   TICKERS = {
       "stocks": ["SBER.ME", "GAZP.ME", ...],
       "currencies": ["USDRUB=X", ...],
       "indices": ["IMOEX.ME", ...]
   }
   ```

2. Установи переменные окружения:
   ```bash
   export SUPABASE_URL=your-url
   export SUPABASE_ANON_KEY=your-key
   ```

3. Запусти вручную для теста:
   ```bash
   cd backend
   python scripts/fetch_market_data.py
   ```

## Мониторинг

- Проверяй таблицу `market_data_daily` в Supabase
- Настрой уведомления об ошибках (Email/Slack/Telegram)
- Добавь логирование в файл
