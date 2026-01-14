# Автоматизация с n8n

n8n позволяет автоматизировать работу с вашим Stochastic Dashboard через API endpoints.

## Доступные API Endpoints

Ваш backend API доступен по адресу: `https://stochastic-dashbord-v1-production.up.railway.app`

### Основные endpoints:

- **Health Check:** `GET /health`
- **Bond Valuation:** `POST /api/bond/valuate`
- **Portfolio Metrics:** `POST /api/portfolio/metrics`
- **Market Data:** `GET /api/market/stock/{ticker}`
- **Stress Testing:** `POST /api/stress/test`
- **Backtesting:** `POST /api/backtest/run`
- **Forward Valuation:** `POST /api/forward/valuate`
- **Swap Valuation:** `POST /api/swap/valuate`

## Примеры Workflows для n8n

### 1. Ежедневная оценка портфеля облигаций

**Сценарий:** Каждый день в 9:00 рассчитывать стоимость портфеля облигаций и отправлять отчет.

**Workflow:**
```
Schedule Trigger (Cron: 0 9 * * *) 
  → HTTP Request (POST /api/bond/valuate)
  → Process Data (форматирование результатов)
  → Email/Slack (отправка отчета)
```

**Настройка HTTP Request:**
- **Method:** POST
- **URL:** `https://stochastic-dashbord-v1-production.up.railway.app/api/bond/valuate`
- **Headers:**
  ```json
  {
    "Content-Type": "application/json"
  }
  ```
- **Body (JSON):**
  ```json
  {
    "secid": "RU000A10AU99",
    "valuationDate": "2026-01-13",
    "discountYield1": 14.0,
    "discountYield2": 16.0,
    "dayCountConvention": "Actual/365F"
  }
  ```

### 2. Мониторинг изменений цен облигаций

**Сценарий:** Каждый час проверять изменения цен и отправлять уведомления при значительных изменениях.

**Workflow:**
```
Schedule Trigger (Cron: 0 * * * *) 
  → HTTP Request (GET /api/market/stock/{ticker})
  → IF Node (проверка изменения > 1%)
  → Slack/Telegram (уведомление)
```

### 3. Еженедельный стресс-тест портфеля

**Сценарий:** Каждую неделю в понедельник запускать стресс-тестирование портфеля.

**Workflow:**
```
Schedule Trigger (Cron: 0 10 * * 1) 
  → HTTP Request (POST /api/stress/test)
  → Generate PDF Report (HTML to PDF)
  → Email (отправка отчета)
```

### 4. Автоматическое обновление данных о рыночных индексах

**Сценарий:** Каждые 15 минут обновлять данные о ключевых индексах.

**Workflow:**
```
Schedule Trigger (Cron: */15 * * * *) 
  → HTTP Request (GET /api/market/index/{symbol})
  → Google Sheets (сохранение данных)
```

### 5. Уведомления о важных событиях

**Сценарий:** При изменении доходности облигации выше порога отправлять уведомление.

**Workflow:**
```
Webhook Trigger (или Schedule)
  → HTTP Request (POST /api/bond/valuate)
  → IF Node (ytm > threshold)
  → Telegram Bot (отправка уведомления)
```

## Настройка n8n для работы с вашим API

### 1. Установка n8n

**Вариант 1: Docker (рекомендуется)**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Вариант 2: npm**
```bash
npm install n8n -g
n8n start
```

**Вариант 3: n8n Cloud**
- Зарегистрируйся на https://n8n.io
- Используй готовый хостинг

### 2. Создание Workflow

1. Открой n8n интерфейс (обычно http://localhost:5678)
2. Создай новый workflow
3. Добавь ноды:
   - **Schedule Trigger** (для планирования)
   - **HTTP Request** (для вызова API)
   - **IF** (для условий)
   - **Email/Slack/Telegram** (для уведомлений)

### 3. Настройка HTTP Request Node

**Базовые настройки:**
- **Method:** GET или POST (в зависимости от endpoint)
- **URL:** `https://stochastic-dashbord-v1-production.up.railway.app/api/{endpoint}`
- **Authentication:** None (если API публичный)

**Пример для Bond Valuation:**
```json
{
  "method": "POST",
  "url": "https://stochastic-dashbord-v1-production.up.railway.app/api/bond/valuate",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "secid": "RU000A10AU99",
    "valuationDate": "{{ $now.toFormat('yyyy-MM-dd') }}",
    "discountYield1": 14.0,
    "discountYield2": 16.0,
    "dayCountConvention": "Actual/365F"
  }
}
```

## Полезные шаблоны

### Получение текущей даты в формате API
В n8n используй Expression:
```javascript
{{ $now.toFormat('yyyy-MM-dd') }}
```

### Обработка ошибок API
Добавь **Error Trigger** node после HTTP Request для обработки ошибок.

### Сохранение результатов
- **Google Sheets** - для таблиц
- **PostgreSQL/MySQL** - для баз данных
- **Google Drive** - для файлов
- **Airtable** - для структурированных данных

## Примеры готовых workflows

### Workflow 1: Ежедневный отчет по облигациям

```json
{
  "name": "Daily Bond Report",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "cronExpression": "0 9 * * *"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://stochastic-dashbord-v1-production.up.railway.app/api/bond/valuate",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "secid",
              "value": "RU000A10AU99"
            },
            {
              "name": "valuationDate",
              "value": "={{ $now.toFormat('yyyy-MM-dd') }}"
            },
            {
              "name": "discountYield1",
              "value": "14.0"
            },
            {
              "name": "discountYield2",
              "value": "16.0"
            }
          ]
        }
      }
    },
    {
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "to": "your-email@example.com",
        "subject": "Daily Bond Valuation Report",
        "text": "={{ JSON.stringify($json, null, 2) }}"
      }
    }
  ]
}
```

## Интеграция с другими сервисами

n8n поддерживает множество интеграций:

- **Email:** Gmail, Outlook, SMTP
- **Мессенджеры:** Slack, Telegram, Discord
- **Облачные хранилища:** Google Drive, Dropbox
- **Базы данных:** PostgreSQL, MySQL, MongoDB
- **Таблицы:** Google Sheets, Airtable
- **Уведомления:** Pushover, Pushbullet
- **Аналитика:** Google Analytics, Mixpanel

## Безопасность

1. **Храни API ключи в n8n Credentials:**
   - Settings → Credentials → Create New
   - Используй переменные окружения для чувствительных данных

2. **Ограничь доступ:**
   - Настрой аутентификацию в n8n
   - Используй webhook secrets для публичных webhooks

3. **Rate Limiting:**
   - Учитывай лимиты Railway (бесплатный tier)
   - Добавь задержки между запросами

## Мониторинг и логирование

- Используй **n8n Execution Logs** для отладки
- Настрой **Error Workflows** для обработки ошибок
- Добавь **Webhook Response** nodes для возврата статуса

## Полезные ссылки

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community Forum](https://community.n8n.io/)
- [n8n Workflow Templates](https://n8n.io/workflows/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
