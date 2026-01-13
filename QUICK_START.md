# Быстрый старт - Развертывание проекта

## Текущая ситуация

✅ **Frontend** уже развернут на GitHub Pages и работает  
❌ **Backend** нужно развернуть отдельно (GitHub Pages не может хостить Python серверы)

## Решение: Развернуть Backend на Railway (5 минут)

### Шаг 1: Регистрация на Railway
1. Перейди на https://railway.app
2. Нажми **Login with GitHub**
3. Авторизуйся через GitHub

### Шаг 2: Создание проекта
1. В Railway нажми **New Project**
2. Выбери **Deploy from GitHub repo**
3. Выбери репозиторий `stochastic-dashbord-v1`
4. Railway автоматически начнет деплой

### Шаг 3: Настройка
1. После начала деплоя, в настройках проекта:
   - Найди секцию **Settings** → **Deploy**
   - В поле **Root Directory** укажи: `backend`
   - Railway автоматически определит Python и установит зависимости

2. Переменные окружения (Settings → Variables):
   ```
   CORS_ORIGINS=https://russiankendricklamar.github.io,http://localhost:5173
   ```

### Шаг 4: Получение URL
1. После успешного деплоя (обычно 2-3 минуты)
2. В разделе **Settings** → **Networking** → **Public Domain**
3. Нажми **Generate Domain** или используй предоставленный
4. Скопируй URL (например: `https://stochastic-backend-production.up.railway.app`)

### Шаг 5: Подключение Frontend к Backend
1. В GitHub перейди в твой репозиторий
2. **Settings** → **Secrets and variables** → **Actions**
3. Нажми **New repository secret**
4. Имя: `VITE_API_BASE_URL`
5. Значение: URL твоего backend из Railway (например: `https://stochastic-backend-production.up.railway.app`)
6. Нажми **Add secret**

### Шаг 6: Обновление Frontend
1. Сделай любой коммит и пуш (или просто пустой коммит):
   ```bash
   git commit --allow-empty -m "Trigger frontend rebuild with new API URL"
   git push origin main
   ```

2. GitHub Actions автоматически пересоберет frontend с новым API URL

### Готово! ✅

Теперь:
- Frontend доступен: `https://russiankendricklamar.github.io/stochastic-dashbord-v1/`
- Backend доступен: `https://your-backend.railway.app`
- Они связаны между собой и все расчеты работают!

## Проверка работы

1. Открой frontend в браузере
2. Открой DevTools (F12) → Console
3. Попробуй выполнить любой расчет
4. В Network tab должны быть запросы к твоему Railway backend (не ошибки CORS)

## Важно

- Railway бесплатный tier дает 500 часов в месяц (достаточно для разработки)
- Backend будет "засыпать" после неактивности на бесплатном плане (первый запрос после сна займет 30-60 секунд)
- Для production лучше использовать платный план ($5/мес) или Render с бесплатным планом

## Альтернативы Railway

Если Railway не подходит, есть другие варианты (см. DEPLOYMENT.md):
- **Render.com** - бесплатный tier, немного медленнее
- **Fly.io** - больше контроля, но сложнее настройка
- **Heroku** - платный, но очень надежный
