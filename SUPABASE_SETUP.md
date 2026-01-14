# Настройка Supabase для Stochastic Dashboard

## Шаг 1: Создание проекта в Supabase

1. Перейди на https://supabase.com
2. Зарегистрируйся или войди в аккаунт
3. Создай новый проект:
   - **Name:** stochastic-dashboard (или любое другое)
   - **Database Password:** создай надежный пароль (сохрани его!)
   - **Region:** выбери ближайший регион
   - Нажми **Create new project**

4. Дождись создания проекта (обычно 1-2 минуты)

## Шаг 2: Получение credentials

1. В проекте перейди в **Settings** → **API**
2. Скопируй следующие значения:
   - **Project URL** → это `SUPABASE_URL`
   - **anon public** key → это `SUPABASE_ANON_KEY`
   - (Опционально) **service_role** key → это `SUPABASE_SERVICE_ROLE_KEY` (для админ операций)

## Шаг 3: Создание таблиц в базе данных

1. В Supabase перейди в **SQL Editor**
2. Открой файл `backend/supabase_migrations.sql`
3. Скопируй весь SQL код
4. Вставь в SQL Editor в Supabase
5. Нажми **Run** (или F5)

Это создаст:
- Таблицу `bond_valuations` для хранения расчетов облигаций
- Таблицу `portfolios` для хранения портфелей
- Таблицу `calculation_history` для истории расчетов
- Индексы для оптимизации запросов
- Триггеры для автоматического обновления `updated_at`

## Шаг 4: Настройка переменных окружения

### Локально (для разработки):

1. Создай файл `.env` в директории `backend/` (если его еще нет)
2. Добавь:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```

### На Railway (для production):

1. Открой проект в Railway
2. Перейди в **Settings** → **Variables**
3. Добавь переменные:
   - **Key:** `SUPABASE_URL`
   - **Value:** твой Project URL из Supabase
4. Добавь еще одну:
   - **Key:** `SUPABASE_ANON_KEY`
   - **Value:** твой anon key из Supabase
5. Railway автоматически перезапустит сервис

## Шаг 5: Установка зависимостей

В локальной разработке:
```bash
cd backend
pip install -r requirements.txt
```

На Railway зависимости установятся автоматически при деплое.

## Шаг 6: Проверка подключения

### Через API:

1. Запусти backend локально или используй Railway URL
2. Проверь health endpoint:
   ```bash
   curl https://your-railway-url.railway.app/health
   ```

3. Попробуй создать запись через API:
   ```bash
   curl -X POST https://your-railway-url.railway.app/api/db/bond-valuations \
     -H "Content-Type: application/json" \
     -d '{
       "secid": "RU000A10AU99",
       "valuation_date": "2026-01-13",
       "discount_yield1": 14.0,
       "discount_yield2": 16.0,
       "dirty_price": 1000.50,
       "clean_price": 995.20,
       "ytm": 14.5,
       "duration": 5.2
     }'
   ```

### Через Supabase Dashboard:

1. В Supabase перейди в **Table Editor**
2. Должны быть видны таблицы: `bond_valuations`, `portfolios`, `calculation_history`
3. Проверь, что данные сохраняются после API запросов

## Доступные API Endpoints

После настройки доступны следующие endpoints:

### Bond Valuations:
- `POST /api/db/bond-valuations` - создать запись
- `GET /api/db/bond-valuations` - получить все записи
- `GET /api/db/bond-valuations/{id}` - получить по ID
- `GET /api/db/bond-valuations?secid=RU000A10AU99` - получить по ISIN
- `GET /api/db/bond-valuations?start_date=2026-01-01&end_date=2026-01-31` - получить по датам
- `PUT /api/db/bond-valuations/{id}` - обновить запись
- `DELETE /api/db/bond-valuations/{id}` - удалить запись

### Portfolios:
- `POST /api/db/portfolios` - создать портфель
- `GET /api/db/portfolios` - получить все портфели
- `GET /api/db/portfolios/{id}` - получить портфель по ID

### Calculation History:
- `POST /api/db/calculation-history` - сохранить историю расчета
- `GET /api/db/calculation-history` - получить историю
- `GET /api/db/calculation-history?calculation_type=bond` - получить по типу

## Интеграция с существующими endpoints

Можно автоматически сохранять результаты расчетов в БД. Например, в `bond.py`:

```python
from src.database.repositories import BondValuationRepository, CalculationHistoryRepository
from src.database.models import BondValuationRecord, CalculationHistory
import time

@router.post("/valuate", response_model=Dict[str, Any])
async def valuate_bond(request: BondValuationRequest):
    start_time = time.time()
    
    # Выполняем расчет
    result = calculate_bond_valuation(...)
    
    # Сохраняем в БД
    bond_repo = BondValuationRepository()
    history_repo = CalculationHistoryRepository()
    
    # Сохраняем результат расчета
    bond_record = BondValuationRecord(
        secid=request.secid,
        valuation_date=request.valuationDate,
        discount_yield1=request.discountYield1,
        discount_yield2=request.discountYield2,
        dirty_price=result["scenario1"]["dirtyPrice"],
        clean_price=result["scenario1"]["cleanPrice"],
        ytm=result["scenario1"]["ytmPercent"],
        duration=result["scenario1"]["duration"],
        modified_duration=result["scenario1"].get("modifiedDuration"),
        convexity=result["scenario1"].get("convexity")
    )
    bond_repo.create(bond_record)
    
    # Сохраняем в историю
    execution_time = (time.time() - start_time) * 1000
    history_record = CalculationHistory(
        calculation_type="bond",
        input_data=request.model_dump(),
        result_data=result,
        execution_time_ms=execution_time
    )
    history_repo.create(history_record)
    
    return result
```

## Безопасность

### Row Level Security (RLS)

По умолчанию RLS отключен. Если нужно включить:

1. В Supabase SQL Editor выполни:
   ```sql
   ALTER TABLE bond_valuations ENABLE ROW LEVEL SECURITY;
   ```

2. Создай политики доступа (примеры в `supabase_migrations.sql`)

### Service Role Key

**Важно:** Service Role Key обходит RLS и имеет полный доступ. Используй его только:
- В backend серверах
- Для админ операций
- Никогда не используй в frontend!

## Мониторинг и аналитика

В Supabase Dashboard доступны:
- **Table Editor** - просмотр и редактирование данных
- **SQL Editor** - выполнение SQL запросов
- **Database** → **Reports** - аналитика использования
- **Logs** - логи запросов

## Полезные ссылки

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
