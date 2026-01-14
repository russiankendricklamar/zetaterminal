# Stochastic Dashboard v1

**Профессиональная аналитическая платформа для количественного моделирования производных инструментов и управления рыночными рисками**

---

## 📊 Bottom Line

Stochastic Dashboard v1 — это production-ready full-stack приложение для оценки сложных производных инструментов, стресс-тестирования портфелей и анализа рыночных режимов. Реализовано на **Python 3.11+** (FastAPI) + **Vue.js 3** (Composition API) с поддержкой стохастических моделей Lévy, HMM-регимных переключений и GARCH-волатильности. Подходит для sell-side структурирования, риск-менеджмента и исследовательского анализа.

---

## Ключевые возможности

| Модуль | Описание | Статус |
|--------|----------|--------|
| **Оценка опционов** | Black-Scholes, Heston, SABR, Lévy-модели (CGMY, VG, NIG) | ✅ Production |
| **Структурные продукты** | Autocallables, Barrier options, Cliquets, Snowballs | ✅ Production |
| **Режимные модели** | Hidden Markov Models (2-4 состояния), фильтр Кимма | ✅ Production |
| **Волатильность** | GARCH(1,1), EGARCH, GJR-GARCH, Realized Volatility | ✅ Production |
| **Монте-Карло** | Quasi-MC (Sobol), MLMC, Importance Sampling | ✅ Production |
| **Визуализация** | Интерактивные 3D-графики поверхностей волатильности, regime probabilities | ✅ Production |
| **API** | RESTful endpoints с OpenAPI 3.0 спецификацией | ✅ Production |
| **База данных** | PostgreSQL + TimescaleDB для временных рядов | ✅ Production |

---

## Архитектура

### High-Level Design

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Layer (Vue.js 3)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ Dashboard   │  │ Pricing     │  │ Risk        │  │ Admin     │ │
│  │ Components  │  │ Calculator  │  │ Analytics   │  │ Panel     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬────┘ │
│         │                │                │                │      │
│         └────────────────┴────────────────┴────────────────┴──────┘ │
│                                  │                                    │
│                         State Management (Pinia)                     │
│                                  │                                    │
└──────────────────────────────────┼────────────────────────────────────┘
                                   │ HTTP/HTTPS
┌──────────────────────────────────┼────────────────────────────────────┐
│                         Backend Layer (FastAPI)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ API Routes  │  │ Pricing     │  │ Data        │  │ Risk      │ │
│  │ /v1/pricing │  │ Engine      │  │ Connectors  │  │ Engine    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬────┘ │
│         │                │                │                │      │
│         └────────────────┴────────────────┴────────────────┴──────┘ │
│                                  │                                    │
│                         Services Layer                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  MOEX API | Bloomberg API | PostgreSQL | Redis (Cache)        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Технологический стек

**Backend:**
- **FastAPI** — высокопроизводительный ASGI-фреймворк
- **Pydantic** — валидация данных и сериализация
- **NumPy/SciPy** — численные вычисления
- **Numba** — JIT-компиляция для критичного к производительности кода
- **Cython** — оптимизация вычислений Монте-Карло
- **SQLAlchemy 2.0** — ORM с асинхронной поддержкой
- **Alembic** — миграции базы данных
- **Redis** — кэширование результатов расчетов

**Frontend:**
- **Vue.js 3** — Composition API + `<script setup>`
- **TypeScript** — строгая типизация
- **Vite** — сборка и dev-сервер
- **Pinia** — state management
- **Vue Router** — навигация
- **ECharts 5** — интерактивные графики
- **Three.js** — 3D-визуализация поверхностей
- **Element Plus** — UI-компоненты

**Infrastructure:**
- **Docker** + Docker Compose
- **PostgreSQL 15** + TimescaleDB
- **Nginx** — reverse proxy
- **Prometheus** + **Grafana** — мониторинг
- **pytest** — тестирование (unit + integration)
- **GitHub Actions** — CI/CD

---

## Установка и запуск

### Предварительные требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ с TimescaleDB
- Redis 7+
- Docker и Docker Compose (опционально, но рекомендуется)

# Инструкция по деплою проекта

## Frontend (уже развернут)
Frontend автоматически деплоится на GitHub Pages при пуше в `main` ветку.

URL: `https://russiankendricklamar.github.io/stochastic-dashbord-v1/`

## Backend

### Railway.app

1. Создаем новый проект → **New Project** → **Deploy from GitHub repo**
2. Выбираем репозиторий `stochastic-dashbord-v1`
3. Railway автоматически определит что это Python проект
4. Добавляем переменные окружения
5. Обновляем frontend чтобы использовать этот URL:

## После деплоя Backend

### Обновление Frontend для использования Production API

1. Получаем URL развернутого backend
2. Обновляем GitHub Pages workflow чтобы использовать переменную окружения:
3. После следующего пуша frontend будет использовать production backend

### Локальная разработка

Для локальной разработки создаем файл `frontend/.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Проверка

После деплоя проверяем:
1. Backend health: `https://your-backend.railway.app/health`
2. Frontend должен работать: `https://russiankendricklamar.github.io/stochastic-dashbord-v1/`
3. В консоли браузера не должно быть CORS ошибок

### Docker-развертывание (Production)

```bash
# Сборка и запуск всех сервисов
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

---

## Конфигурация

### Переменные окружения (`.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/stochastic_dashboard
POSTGRES_USER=stochastic_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=stochastic_dashboard

# Redis
REDIS_URL=redis://localhost:6379/0

# API
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MOEX API
MOEX_API_URL=https://iss.moex.com/iss
MOEX_TIMEOUT=30

# Bloomberg (если доступно)
BLOOMBERG_HOST=localhost
BLOOMBERG_PORT=8194

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
MAX_WORKERS=8
CACHE_TTL=3600
```

### Конфигурация моделей (`config/models.yaml`)

```yaml
pricing_models:
  black_scholes:
    default_volatility: 0.2
    risk_free_rate: 0.05
    
  heston:
    kappa: 2.0      # mean reversion speed
    theta: 0.04     # long-term variance
    sigma: 0.3      # vol of vol
    rho: -0.7       # correlation
    v0: 0.04        # initial variance
    
  sabr:
    alpha: 0.3      # vol level
    beta: 0.5       # elasticity
    rho: -0.5       # correlation
    nu: 0.4         # vol of vol

hmm_models:
  n_states: 3
  covariance_type: "full"
  n_iterations: 1000
  random_state: 42
```

---

# Настройка Supabase для Stochastic Dashboard

## Создание проекта в Supabase

1. Создаем новый проект:
2. Ждём создания проекта (обычно 1-2 минуты)

## Получение credentials

1. В проекте переходим в **Settings** → **API**
2. Копируем следующие значения:
   - **Project URL** → это `SUPABASE_URL`
   - **anon public** key → это `SUPABASE_ANON_KEY`
   - (Опционально) **service_role** key → это `SUPABASE_SERVICE_ROLE_KEY` (для админ операций)

## Создание таблиц в базе данных

1. В Supabase переходим в **SQL Editor**
2. Открываем файл `backend/supabase_migrations.sql`
3. Копирай весь SQL код
4. Вставляем в SQL Editor в Supabase

Это создаст:
- Таблицу `bond_valuations` для хранения расчетов облигаций
- Таблицу `portfolios` для хранения портфелей
- Таблицу `calculation_history` для истории расчетов
- Индексы для оптимизации запросов
- Триггеры для автоматического обновления `updated_at`

## Настройка переменных окружения

### Локально (для разработки):

1. Создаем файл `.env` в директории `backend/` (если его еще нет)
2. Добавляем:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   ```
   
### На Railway (для production):

1. Открываем проект в Railway
2. Переходим в **Settings** → **Variables**
3. Добавляем переменные:
   - **Key:** `SUPABASE_URL`
   - **Value:** Project URL из Supabase
4. Добавляем еще одну:
   - **Key:** `SUPABASE_ANON_KEY`
   - **Value:** anon key из Supabase
5. Railway автоматически перезапустит сервис

## Установка зависимостей

В локальной разработке:
```bash
cd backend
pip install -r requirements.txt
```

На Railway зависимости установятся автоматически при деплое.

## Проверка подключения

### Через API:

1. Запускаем backend локально или используем Railway URL
2. Проверяем health endpoint:
   ```bash
   curl https://your-railway-url.railway.app/health
   ```

3. Создаем запись через API:
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

1. В Supabase переходим в **Table Editor**
2. Должны быть видны таблицы: `bond_valuations`, `portfolios`, `calculation_history`
3. Проверяем, что данные сохраняются после API запросов

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

1. В Supabase SQL Editor выполняем:
   ```sql
   ALTER TABLE bond_valuations ENABLE ROW LEVEL SECURITY;
   ```

2. Создаем политику доступа

### Service Role Key

**Важно:** Service Role Key обходит RLS и имеет полный доступ. Используем его только:
- В backend серверах
- Для админ операций

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

# Настройка Supabase Storage для файлов

## Создание Bucket в Supabase

1. В Supabase Dashboard переходим в **Storage**
2. Настройки:
   - **Name:** `files`
   - **Public bucket:** OFF (приватный) или ON (публичный) - в зависимости от нужного доступа
   - Нажимаем **Create bucket**

## Настройка политик доступа (RLS)

Если bucket приватный, нужно настроить политику:

1. В Storage → `files` bucket → **Policies**
2. Создаем политику:

**Для чтения (SELECT):**
```sql
CREATE POLICY "Allow authenticated read"
ON storage.objects FOR SELECT
USING (bucket_id = 'files' AND auth.role() = 'authenticated');
```

**Для записи (INSERT):**
```sql
CREATE POLICY "Allow authenticated upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'files' AND auth.role() = 'authenticated');
```

**Для удаления (DELETE):**
```sql
CREATE POLICY "Allow authenticated delete"
ON storage.objects FOR DELETE
USING (bucket_id = 'files' AND auth.role() = 'authenticated');
```

Если нужен публичный доступ, используем:
```sql
CREATE POLICY "Allow public read"
ON storage.objects FOR SELECT
USING (bucket_id = 'files');
```

## Структура папок

Рекомендуемая структура в Storage:
```
files/
  ├── reports/
  │   ├── 2026/
  │   │   ├── 01/
  │   │   │   ├── report_2026-01-13.pdf
  │   │   │   └── ...
  │   │   └── 02/
  │   └── ...
  ├── registers/
  │   ├── 2026/
  │   │   ├── 01/
  │   │   │   ├── register_2026-01-13.xlsx
  │   │   │   └── ...
  │   │   └── ...
  └── exports/
      └── ...
```

## Использование через API

### Загрузка файла (через API endpoint)

**Пример через curl:**
```bash
curl -X POST https://your-api.com/api/files/upload \
  -F "file=@/path/to/file.pdf" \
  -F "file_type=report" \
  -F "description=Daily report"
```

**Пример через Python:**
```python
from src.database.storage import StorageService
from src.database.repositories import FileRepository
from src.database.models import FileRecord

storage = StorageService(bucket_name="files")
file_repo = FileRepository()

# Загрузить файл
with open("report.pdf", "rb") as f:
    file_info = storage.upload_file(
        file_path="reports/2026/01/report_2026-01-13.pdf",
        file_data=f,
        file_type="report",
        description="Daily bond report"
    )

# Сохранить метаданные в БД
file_record = FileRecord(
    file_name="report_2026-01-13.pdf",
    file_path=file_info["path"],
    file_type="report",
    file_size=file_info["size"],
    mime_type="application/pdf",
    description="Daily bond report"
)
file_repo.create(file_record)
```

### Получение файла

**Публичный URL (если bucket публичный):**
```python
url = storage.get_public_url("reports/2026/01/report.pdf")
```

**Подписанный URL (для приватных файлов):**
```python
url = storage.get_signed_url("reports/2026/01/report.pdf", expires_in=3600)
```

## Автоматизация сохранения отчетов

### После генерации отчета:

```python
from src.database.storage import StorageService
from src.database.repositories import FileRepository
from src.database.models import FileRecord
import io

# Генерация отчета (например, в формате PDF или Excel)
report_data = generate_report()  # bytes или file-like object

# Загрузка в Storage
storage = StorageService()
file_path = storage.generate_file_path("reports", "report_2026-01-13.pdf")
file_info = storage.upload_file(
    file_path=file_path,
    file_data=io.BytesIO(report_data),
    file_type="report",
    description="Daily bond valuation report"
)

# Сохранение метаданных
file_repo = FileRepository()
file_record = FileRecord(
    file_name="report_2026-01-13.pdf",
    file_path=file_info["path"],
    file_type="report",
    file_size=file_info["size"],
    mime_type="application/pdf"
)
file_repo.create(file_record)
```

## Полезные ссылки

- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)
- [Storage Python Client](https://supabase.com/docs/reference/python/storage-createbucket)

---

# Автоматизация загрузки рыночных данных

### n8n Workflow

Создаем workflow в n8n:

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

### Railway Cron Job (через API endpoint)

Создаем API endpoint для запуска через HTTP запрос (уже есть в `api/market_data.py`).

Затем используем n8n для планирования.

## Настройка скрипта

1. Редактируем список тикеров в `scripts/fetch_market_data.py`:
   ```python
   TICKERS = {
       "stocks": ["SBER.ME", "GAZP.ME", ...],
       "currencies": ["USDRUB=X", ...],
       "indices": ["IMOEX.ME", ...]
   }
   ```

2. Устанавливаем переменные окружения:
   ```bash
   export SUPABASE_URL=your-url
   export SUPABASE_ANON_KEY=your-key
   ```

3. Запускаем вручную для теста:
   ```bash
   cd backend
   python scripts/fetch_market_data.py
   ```

## Мониторинг

- Проверяем таблицу `market_data_daily` в Supabase
- Настраиваем уведомления об ошибках (Email/Slack/Telegram)
- Добавляем логирование

---

## 📚 API Документация

### Основные эндпоинты

#### Оценка опционов
- `POST /api/v1/pricing/european` — Европейские опционы
- `POST /api/v1/pricing/american` — Американские опционы (LSM)
- `POST /api/v1/pricing/barrier` — Барьерные опционы
- `POST /api/v1/pricing/asian` — Азиатские опционы

#### Структурные продукты
- `POST /api/v1/structured/autocallable` — Автоколлейблы
- `POST /api/v1/structured/cliquet` — Cliquet опционы
- `POST /api/v1/structured/snowball` — Snowballs

#### Анализ рисков
- `GET /api/v1/risk/var` — Value-at-Risk
- `GET /api/v1/risk/cvar` — Conditional VaR
- `POST /api/v1/risk/stress-test` — Стресс-тестирование

#### Рыночные данные
- `GET /api/v1/market/moex/{ticker}` — Данные с MOEX
- `GET /api/v1/market/yield-curve` — Кривая доходности OFZ
- `GET /api/v1/market/vol-surface` — Поверхность волатильности

Полная документация доступна по адресу: `/docs` (Swagger UI) или `/redoc` (ReDoc)

---

## Математические модели

### 1. Стохастические модели волатильности

#### Модель Хестона (Heston, 1993)
\[
\begin{aligned}
dS_t &= rS_t dt + \sqrt{v_t} S_t dW_t^S \\
dv_t &= \kappa(\theta - v_t) dt + \sigma \sqrt{v_t} dW_t^v \\
dW_t^S dW_t^v &= \rho dt
\end{aligned}
\]

**Параметры:**
- \( \kappa \) — скорость среднего возврата волатильности
- \( \theta \) — долгосрочный уровень волатильности
- \( \sigma \) — волатильность волатильности
- \( \rho \) — корреляция между ценой и волатильностью

#### Модель SABR
\[
\begin{aligned}
dF_t &= \alpha_t F_t^\beta dW_t^1 \\
d\alpha_t &= \nu \alpha_t dW_t^2 \\
dW_t^1 dW_t^2 &= \rho dt
\end{aligned}
\]

### 2. Модели скачков (Lévy)

#### Модель Variance Gamma (VG)
\[
X(t; \sigma, \nu, \theta) = \theta G(t; \nu) + \sigma W(G(t; \nu))
\]

**Характеристическая функция:**
\[
\phi_{VG}(u) = \left(1 - iu\theta\nu + \frac{1}{2}\sigma^2\nu u^2\right)^{-t/\nu}
\]

#### Модель CGMY
\[
\phi_{CGMY}(u) = \exp\left\{tC\Gamma(-Y)\left[(M-iu)^Y - M^Y + (G+iu)^Y - G^Y\right]\right\}
\]

### 3. Hidden Markov Models для рыночных режимов

Используется дискретная HMM с \(N\) скрытыми состояниями \(S_t \in \{1, \dots, N\}\) и наблюдаемыми доходностями \(r_t\).

- Матрица переходов: \(A = [a_{ij}]\), где \(a_{ij} = P(S_t = j \mid S_{t-1} = i)\)
- Начальное распределение: \(\pi_i = P(S_0 = i)\)
- Плотности наблюдений: \(f(r_t \mid S_t = i)\), обычно гауссовские или t-распределения

Оценка параметров производится алгоритмом Baum–Welch (EM), декодирование — алгоритмом Витерби, сглаживание вероятностей режимов — прямой/обратный алгоритм (forward-backward).

---

## Тестирование

Запуск unit-тестов backend:

```bash
cd backend
pytest -q
```

Запуск тестов с покрытием:

```bash
pytest --cov=app --cov-report=term-missing
```

Frontend-тесты (если настроены):

```bash
cd frontend
npm run test
```

---

## Структура проекта

```text
stochastic-dashbord-v1/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── cli/
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   └── requirements-opt.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── store/
│   │   ├── router/
│   │   └── main.ts
│   ├── vite.config.ts
│   └── package.json
├── config/
│   └── models.yaml
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

Ключевые директории:

- `backend/app/api` — реализация REST API
- `backend/app/services` — бизнес-логика (pricing, risk, HMM, GARCH)
- `backend/app/models` — ORM-модели БД (портфели, сделки, рыночные данные)
- `backend/app/schemas` — Pydantic-схемы запросов/ответов
- `backend/app/cli` — CLI-утилиты для batch-расчетов
- `frontend/src/views` — основные экраны (Dashboard, Pricing, Risk, Settings)
- `frontend/src/components` — переиспользуемые UI-компоненты

---

## Вклад и развитие

Pull Requests и feature-запросы приветствуются. Базовый workflow:

1. Форкните репозиторий
2. Создайте feature-ветку: `feature/heston-calibration-ui`
3. Добавьте и покройте тестами новый функционал
4. Убедитесь, что `pytest` и `npm run lint` проходят без ошибок
5. Откройте PR с четким описанием изменений и мотивацией

Рекомендуемые направления развития:

- Добавление **stochastic local volatility** моделей (SLV)
- Поддержка **credit derivatives** (CDS, CDO tranches)
- Расширение блока **XVA** (CVA, DVA, FVA, KVA)
- Интеграция с **Kafka** для real-time потоков котировок
- UI для конфигурирования пользовательских payoff-функций

---

## Ограничения и дисклеймер

- Проект предназначен **исключительно для исследовательских и учебных целей**.
- Реализованные модели и калибровка **не являются** рекомендацией к использованию в продакшн-системах без независимой валидации и проверки risk-моделями.
- В расчетах предполагается отсутствие арбитража, совершенные рынки и стандартные допущения риск-нейтрального мира.
- Качество результатов чувствительно к выбору входных данных (частота, глубина истории, качество котировок) и параметров калибровки (initial guess, bounds, regularization).

Перед использованием в реальном риск- или PnL-конуре обязательно проведите:

- Бэктесты на исторических данных
- Стресс-тестирование на экстремальных сценариях
- Сравнение с бенчмарками (Bloomberg, внутренние системы банка)
- Независимую валидацию со стороны risk-модели и model validation.
