# Stochastic Dashboard v1

**Профессиональная аналитическая платформа для количественного моделирования производных инструментов и управления рыночными рисками**

---

## 📊 Bottom Line

Stochastic Dashboard v1 — это production-ready full-stack приложение для оценки сложных производных инструментов, стресс-тестирования портфелей и анализа рыночных режимов. Реализовано на **Python 3.11+** (FastAPI) + **Vue.js 3** (Composition API) с поддержкой стохастических моделей Lévy, HMM-регимных переключений и GARCH-волатильности. Подходит для sell-side структурирования, риск-менеджмента и исследовательского анализа.

---

## 🎯 Ключевые возможности

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

## 🏗️ Архитектура

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

## 📦 Установка и запуск

### Предварительные требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ с TimescaleDB
- Redis 7+
- Docker и Docker Compose (опционально, но рекомендуется)

### Локальная установка (Development)

#### 1. Клонирование репозитория

```bash
git clone https://github.com/russiankendricklamar/stochastic-dashbord-v1.git
cd stochastic-dashbord-v1
```

#### 2. Backend setup

```bash
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Установка дополнительных библиотек для оптимизации
pip install -r requirements-opt.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env (см. раздел Configuration)

# Запуск миграций
alembic upgrade head

# Запуск сервера разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: `http://localhost:8000`
Документация OpenAPI: `http://localhost:8000/docs`

#### 3. Frontend setup

```bash
cd frontend

# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev
```

Frontend будет доступен по адресу: `http://localhost:5173`

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

## ⚙️ Конфигурация

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

## 🚀 Быстрый старт

### Пример 1: Оценка европейского колл-опциона (Black-Scholes)

```python
import requests

# Через Python
response = requests.post(
    "http://localhost:8000/api/v1/pricing/european",
    json={
        "spot_price": 100.0,
        "strike_price": 105.0,
        "time_to_maturity": 1.0,
        "risk_free_rate": 0.05,
        "volatility": 0.2,
        "option_type": "call"
    }
)

price = response.json()
print(f"Option Price: {price['price']:.4f}")
print(f"Greeks: {price['greeks']}")
```

### Пример 2: Моделирование автоколлейбла (Monte-Carlo)

```bash
# Используя CLI
python -m app.cli.price_autocallable \
  --spot 100 \
  --barrier 80 \
  --coupon 0.08 \
  --maturity 3 \
  --simulations 100000 \
  --model heston
```

### Пример 3: Анализ рыночных режимов (HMM)

```python
import pandas as pd
from app.services.hmm import MarketRegimeDetector

# Загрузка исторических данных
data = pd.read_csv("data/ofz_prices.csv", index_col=0, parse_dates=True)

# Обучение модели
detector = MarketRegimeDetector(n_states=3)
detector.fit(data['returns'].values.reshape(-1, 1))

# Предсказание текущего режима
current_regime = detector.predict_latest()
print(f"Current Market Regime: {current_regime}")
```

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

## 🔬 Математические модели

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

## 🧪 Тестирование

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

## 🛠️ Структура проекта

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

## 🤝 Вклад и развитие

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

## ⚠️ Ограничения и дисклеймер

- Проект предназначен **исключительно для исследовательских и учебных целей**.
- Реализованные модели и калибровка **не являются** рекомендацией к использованию в продакшн-системах без независимой валидации и проверки risk-моделями.
- В расчетах предполагается отсутствие арбитража, совершенные рынки и стандартные допущения риск-нейтрального мира.
- Качество результатов чувствительно к выбору входных данных (частота, глубина истории, качество котировок) и параметров калибровки (initial guess, bounds, regularization).

Перед использованием в реальном риск- или PnL-конуре обязательно проведите:

- Бэктесты на исторических данных
- Стресс-тестирование на экстремальных сценариях
- Сравнение с бенчмарками (Bloomberg, внутренние системы банка)
- Независимую валидацию со стороны risk-модели и model validation.
