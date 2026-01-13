# Инструкция по деплою проекта

## Frontend (уже развернут)
Frontend автоматически деплоится на GitHub Pages при пуше в `main` ветку.

URL: `https://russiankendricklamar.github.io/stochastic-dashbord-v1/`

## Backend - Варианты деплоя

### Вариант 1: Railway (Рекомендуется - самый простой)

1. Зарегистрируйся на [Railway.app](https://railway.app) через GitHub
2. Создай новый проект → **New Project** → **Deploy from GitHub repo**
3. Выбери репозиторий `stochastic-dashbord-v1`
4. Railway автоматически определит что это Python проект
5. В настройках проекта:
   - **Root Directory**: `/backend`
   - **Start Command**: `python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11`

6. Добавь переменные окружения (Settings → Variables):
   ```
   CORS_ORIGINS=https://russiankendricklamar.github.io,http://localhost:5173
   PORT=8000
   ```

7. После деплоя скопируй URL (например: `https://your-app.railway.app`)

8. Обнови frontend чтобы использовать этот URL:
   - В GitHub → Settings → Secrets and variables → Actions
   - Добавь новый секрет: `VITE_API_BASE_URL` = `https://your-app.railway.app`
   - Обнови workflow `pages.yml` чтобы использовать эту переменную при билде

### Вариант 2: Render

1. Зарегистрируйся на [Render.com](https://render.com) через GitHub
2. Создай новый **Web Service**
3. Подключи репозиторий `stochastic-dashbord-v1`
4. Настройки:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: `Python 3`
   - **Plan**: Free (или Hobby $7/мес)

5. Добавь Environment Variables:
   ```
   CORS_ORIGINS=https://russiankendricklamar.github.io,http://localhost:5173
   ```

6. После деплоя скопируй URL (например: `https://stochastic-backend.onrender.com`)

### Вариант 3: Fly.io

1. Установи flyctl: `curl -L https://fly.io/install.sh | sh`
2. Зарегистрируйся: `fly auth signup`
3. В директории `backend/` создай `fly.toml`:
   ```toml
   app = "stochastic-backend"
   primary_region = "ams"

   [build]

   [http_service]
     internal_port = 8000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0
     processes = ["app"]

   [[services]]
     protocol = "tcp"
     internal_port = 8000

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```

4. Задеплой: `fly deploy`

## После деплоя Backend

### Обновление Frontend для использования Production API

1. Получи URL развернутого backend (например: `https://your-backend.railway.app`)

2. Обнови GitHub Pages workflow чтобы использовать переменную окружения:

   Файл: `.github/workflows/pages.yml`
   ```yaml
   - name: Build
     working-directory: ./frontend
     run: npm run build
     env:
       VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
   ```

3. В GitHub → Settings → Secrets and variables → Actions:
   - Добавь новый секрет: `VITE_API_BASE_URL` = `https://your-backend.railway.app`

4. После следующего пуша frontend будет использовать production backend

### Локальная разработка

Для локальной разработки создай файл `frontend/.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Проверка

После деплоя проверь:
1. Backend health: `https://your-backend.railway.app/health`
2. Frontend должен работать: `https://russiankendricklamar.github.io/stochastic-dashbord-v1/`
3. В консоли браузера не должно быть CORS ошибок
