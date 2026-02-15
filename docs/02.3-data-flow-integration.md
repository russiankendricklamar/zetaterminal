# 2.3. Потоки данных и интеграция

## Паттерны потоков данных

Система реализует четыре основных паттерна:

### 1. External API → Service → Repository → DB
Персистентное хранение рыночных данных.
```
Yahoo Finance → yfinance_service → MarketDataRepository → Supabase
```

### 2. External API → Service → Direct Response
Realtime-запросы без кеширования.
```
MOEX ISS → zcyc_service → JSON Response → Frontend
```

### 3. Frontend → Backend → Computation → Response
Тяжёлые вычисления (GARCH, HMM, DCF).
```
Vue Component → computeService.ts → POST /api/compute/garch → compute_service.py → JSON
```

### 4. Bulk Export → Parquet → Supabase Storage
Экспорт реестров в колоночный формат.
```
Registry Data → PyArrow → .parquet → Supabase Storage Bucket
```

## Пример: ZCYC (кривая бескупонных доходностей)

```
1. ZCYCViewer.vue вызывает zcycService.ts
2. GET /api/zcyc?date=2026-01-15
3. FastAPI роутер валидирует дату через Pydantic
4. zcyc_service.fetch_zcyc_from_moex() вызывает MOEX ISS API
5. Ответ MOEX трансформируется в стандартную структуру
6. JSON возвращается клиенту:
   {
     "status": "ok",
     "date": "2026-01-15",
     "data": [{"term": 0.25, "value": 13.52}, ...],
     "count": 12,
     "min_term": 0.083,
     "max_term": 30.0,
     "min_rate": 13.45,
     "max_rate": 14.82,
     "mean_rate": 14.12
   }
7. Компонент рендерит кривую через ECharts
```

### ZCYC Fallback Chain
```
1. Попытка: MOEX /engines/stock/zcyc.json
2. Fallback (404): build_zcyc_from_bonds() — строит кривую из ОФЗ
3. Если и облигации недоступны: ошибка с рекомендацией сменить дату
```

## Пример: RuData интеграция

```
1. Settings.vue сохраняет credentials (base64) в localStorage
2. Запрос передаёт credentials с каждым вызовом (stateless backend)
3. rudata_service.py получает Bearer-токен через login/password
4. API-вызовы с rate limiting: 5 req/sec, max 100 items per filter
5. Автоматическое разбиение больших массивов на батчи по 100
6. Задержка 1.0 секунда между батчами
```

## Интеграция с внешними API

| API | Аутентификация | Rate Limit | Назначение |
|-----|---------------|------------|------------|
| MOEX ISS | Не требуется | HTTP throttling | КБД, данные облигаций |
| RuData/Interfax | Bearer token | 5 req/sec, 100 items | Справочные данные облигаций |
| Yahoo Finance | Через библиотеку | Library-managed | Исторические цены |
| CoinGecko | API key (опционально) | 50 req/min (free) | Крипто-рынки |
| Alpha Vantage | API key | 5 req/min (free) | Котировки акций |
| FRED | API key | 120 req/min | Макроэкономика (США) |
| NewsAPI | API key | 100 req/day (free) | Новости |

## Обработка ошибок (по слоям)

| Слой | Ответственность | Стратегия |
|------|-----------------|-----------|
| **Service** | Ошибки сети, HTTP статусы | try-catch, fallback |
| **Component** | Пользовательские алерты | Красные glass-карточки |
| **Backend API** | Валидация Pydantic | HTTPException (400/422/500) |
| **External API** | Retry, fallback | Альтернативные источники |

## Credential Management

### Frontend (Settings.vue)
```
Логин/пароль → base64 encode → localStorage
localStorage → base64 decode → Передача с каждым запросом
```

### Backend
```
Environment variables → os.getenv()
RuData: per-request token → не кешируется на сервере
```

> **Важно**: base64 — обфускация, не шифрование. Предназначено для dev/testing.

## Кеширование

### Backend In-Memory Cache
- TTL-based с автоочисткой
- Макс. 2000 записей, LRU-вытеснение
- Используется для CoinGecko (120с), новостей (300с), глобальных метрик

### Рекомендации по кешированию

| Данные | Рекомендуемый TTL | Обоснование |
|--------|-------------------|-------------|
| ZCYC кривая | 24 часа | Обновляется раз в день |
| Справочные данные облигаций | 7 дней | Редко меняются |
| Исторические цены | Бессрочно | Неизменяемые |
| Real-time котировки | 60 секунд | Динамичные данные |
