# Stochastic Dashboard v1

**Профессиональная аналитическая платформа для количественного моделирования производных инструментов и управления рыночными рисками**

---

## 📊 Описание

Stochastic Dashboard v1 — это production-ready full-stack приложение для оценки сложных производных инструментов, стресс-тестирования портфелей и анализа рыночных режимов. Реализовано на **Python 3.11+** (FastAPI) + **Vue.js 3** (Composition API) с поддержкой стохастических моделей Lévy, HMM-регимных переключений и GARCH-волатильности.

---

## 🎯 Ключевые возможности

### Оценка инструментов

| Модуль | Описание | Статус |
|--------|----------|--------|
| **Оценка облигаций** | DCF модель с поддержкой реестров, рыночной доходности из MOEX | ✅ Production |
| **Оценка свопов** | IRS, CDS, Basis Swaps с поддержкой реестров | ✅ Production |
| **Оценка форвардов** | FX, Bond, Commodity, Equity, Rate форварды с поддержкой реестров | ✅ Production |
| **Оценка опционов** | Black-Scholes, Heston, SABR, Lévy-модели (CGMY, VG, NIG) | ✅ Production |
| **Структурные продукты** | Autocallables, Barrier options, Cliquets, Snowballs | ✅ Production |

### Аналитика и риск-менеджмент

| Модуль | Описание | Статус |
|--------|----------|--------|
| **Режимные модели** | Hidden Markov Models (2-4 состояния), фильтр Кимма | ✅ Production |
| **Волатильность** | GARCH(1,1), EGARCH, GJR-GARCH, Realized Volatility | ✅ Production |
| **Монте-Карло** | Quasi-MC (Sobol), MLMC, Importance Sampling | ✅ Production |
| **Стресс-тестирование** | Стресс-тесты для портфелей, свопов и опционов | ✅ Production |
| **Греческие параметры** | Delta, Gamma, Vega, Theta, Rho для опционов, свопов и форвардов | ✅ Production |
| **P&L Attribution** | Факторная декомпозиция прибылей и убытков | ✅ Production |
| **Хеджирование** | Регрессионное хеджирование портфелей | ✅ Production |

### Работа с данными

| Модуль | Описание | Статус |
|--------|----------|--------|
| **Реестры** | Загрузка и выгрузка реестров в формате XLSX/XLSM | ✅ Production |
| **Parquet экспорт** | Сохранение реестров в сжатом формате Parquet в Supabase | ✅ Production |
| **Рыночные данные** | Интеграция с MOEX API для получения доходностей | ✅ Production |
| **База данных** | PostgreSQL + TimescaleDB для временных рядов, Supabase для хранения | ✅ Production |

### Визуализация

| Модуль | Описание | Статус |
|--------|----------|--------|
| **Интерактивные графики** | 3D-графики поверхностей волатильности, regime probabilities | ✅ Production |
| **Кривые доходности** | Визуализация кривых бескупонных доходностей (ZCYC) | ✅ Production |
| **Forward Curves** | Построение форвардных кривых | ✅ Production |
| **Volatility Surface** | Поверхности волатильности | ✅ Production |

---

## 🏗️ Архитектура

### High-Level Design

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Layer (Vue.js 3)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │ Dashboard   │  │ Pricing     │  │ Risk        │  │ Reports  │ │
│  │ Components  │  │ Calculator  │  │ Analytics   │  │ Export   │ │
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
│  │ /api/bond   │  │ Engine      │  │ Connectors  │  │ Engine    │ │
│  │ /api/swap   │  │             │  │             │  │           │ │
│  │ /api/forward│  │             │  │             │  │           │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬────┘ │
│         │                │                │                │      │
│         └────────────────┴────────────────┴────────────────┴──────┘ │
│                                  │                                    │
│                         Services Layer                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  MOEX API | Supabase Storage | PostgreSQL | Redis (Cache)    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Технологический стек

**Backend:**
- **FastAPI** — высокопроизводительный ASGI-фреймворк
- **Pydantic** — валидация данных и сериализация
- **NumPy/SciPy** — численные вычисления
- **Pandas** — обработка данных и работа с реестрами
- **PyArrow** — работа с форматом Parquet
- **SQLAlchemy 2.0** — ORM с асинхронной поддержкой
- **Supabase** — хранение файлов и данных

**Frontend:**
- **Vue.js 3** — Composition API + `<script setup>`
- **TypeScript** — строгая типизация
- **Vite** — сборка и dev-сервер
- **Pinia** — state management
- **Vue Router** — навигация
- **Chart.js** — интерактивные графики
- **XLSX** — работа с Excel файлами
- **Three.js** — 3D-визуализация поверхностей

**Infrastructure:**
- **Docker** + Docker Compose
- **PostgreSQL 15** + TimescaleDB
- **Supabase** — хранение файлов и данных
- **Nginx** — reverse proxy
- **GitHub Actions** — CI/CD

---

## 📚 Математические модели

### 1. Оценка облигаций (DCF)

#### Dirty Price (полная стоимость)

$$
P_{\text{dirty}} = \sum_{i=1}^{n} \frac{CF_i}{(1 + r_i)^{t_i}}
$$

где:
- $CF_i$ — денежный поток в момент $t_i$ (купон или номинал)
- $r_i$ — ставка дисконтирования для периода $i$
- $t_i$ — время до платежа $i$ в годах
- $n$ — количество платежей

#### Clean Price (котировочная цена)

$$
P_{\text{clean}} = P_{\text{dirty}} - \text{AI}
$$

#### Накопленный купонный доход (Accrued Interest)

$$
\text{AI} = C \times \frac{D_{\text{accrued}}}{D_{\text{period}}}
$$

где:
- $C$ — размер купона
- $D_{\text{accrued}}$ — количество дней с последнего купона
- $D_{\text{period}}$ — количество дней в купонном периоде

#### Yield to Maturity (YTM)

YTM находится численным методом (Newton–Raphson) из уравнения:

$$
P = \sum_{i=1}^{n} \frac{CF_i}{(1 + \text{YTM})^{t_i}}
$$

#### Macaulay Duration

$$
D_{\text{Macaulay}} = \frac{\sum_{i=1}^{n} t_i \cdot \frac{CF_i}{(1 + r)^{t_i}}}{P_{\text{dirty}}}
$$

#### Modified Duration

$$
D_{\text{Modified}} = \frac{D_{\text{Macaulay}}}{1 + r}
$$

#### Convexity

$$
C = \frac{1}{P_{\text{dirty}} (1 + r)^2} \sum_{i=1}^{n} CF_i \cdot \frac{t_i (t_i + 1)}{(1 + r)^{t_i}}
$$

#### Базисы расчета дней (Day Count Conventions)

**Actual/365F (Fixed):**

$$
\text{Year Fraction} = \frac{\text{Days between dates}}{365}
$$

**Actual/360:**

$$
\text{Year Fraction} = \frac{\text{Days between dates}}{360}
$$

**Actual/Actual (ISDA):**

$$
\text{Year Fraction} = \sum_{k} \frac{\text{Days in year } k}{365 \text{ or } 366}
$$

**30/360 (US):**

$$
\text{Year Fraction} = \frac{360 (Y_2 - Y_1) + 30 (M_2 - M_1) + (D_2 - D_1)}{360}
$$

---

### 2. Оценка свопов (Interest Rate Swaps)

#### Справедливая стоимость свопа

$$
V_{\text{swap}} = V_{\text{fixed}} - V_{\text{floating}}
$$

#### Стоимость фиксированной ноги

$$
V_{\text{fixed}} = N \sum_{i=1}^{n} \frac{C \tau_i}{(1 + r_i)^{t_i}}
$$

где:
- $N$ — номинал
- $C$ — фиксированная ставка
- $\tau_i$ — годовая доля для периода $i$
- $r_i$ — ставка дисконтирования для периода $i$

#### Стоимость плавающей ноги

$$
V_{\text{floating}} = N \left( \frac{1}{(1 + r_1)^{t_1}} - \frac{1}{(1 + r_n)^{t_n}} \right)
$$

#### DV01 (Dollar Duration)

$$
\text{DV01} = -\frac{\partial V}{\partial r} \times 0.0001
$$

#### Duration

$$
D = -\frac{1}{V} \frac{\partial V}{\partial r}
$$

---

### 3. Оценка форвардов

#### Cost-of-Carry модель

$$
F = S e^{(r - q - c) T}
$$

где:
- $F$ — форвардная цена
- $S$ — спотовая цена
- $r$ — безрисковая ставка
- $q$ — дивидендная доходность (для акций) или convenience yield (для товаров)
- $c$ — стоимость хранения
- $T$ — время до экспирации

#### Валютный форвард

$$
F = S \frac{1 + r_d T}{1 + r_f T}
$$

где:
- $r_d$ — ставка по базовой валюте
- $r_f$ — ставка по котируемой валюте

#### Форвард на облигацию

$$
F = (S - I) e^{r T} + \text{AI}_{\text{delivery}}
$$

где:
- $I$ — приведенная стоимость купонов до экспирации
- $\text{AI}_{\text{delivery}}$ — накопленный купонный доход на дату поставки

#### Стоимость форвардного контракта

$$
V = (F - K) e^{-r T}
$$

где $K$ — цена исполнения форварда

---

### 4. Стохастические модели волатильности

#### Модель Хестона (Heston, 1993)

$$
\begin{aligned}
dS_t &= r S_t dt + \sqrt{v_t} S_t dW_t^S \\
dv_t &= \kappa (\theta - v_t) dt + \sigma \sqrt{v_t} dW_t^v \\
\langle dW_t^S, dW_t^v \rangle &= \rho dt
\end{aligned}
$$

**Параметры:**
- $\kappa$ — скорость среднего возврата волатильности
- $\theta$ — долгосрочный уровень волатильности
- $\sigma$ — волатильность волатильности
- $\rho$ — корреляция между ценой и волатильностью

#### Модель SABR

$$
\begin{aligned}
dF_t &= \alpha_t F_t^\beta dW_t^1 \\
d\alpha_t &= \nu \alpha_t dW_t^2 \\
\langle dW_t^1, dW_t^2 \rangle &= \rho dt
\end{aligned}
$$

---

### 5. Модели скачков (Lévy)

#### Модель Variance Gamma (VG)

$$
X(t; \sigma, \nu, \theta) = \theta G(t; \nu) + \sigma W(G(t; \nu))
$$

**Характеристическая функция:**

$$
\phi_{VG}(u) = \left(1 - i u \theta \nu + \frac{1}{2} \sigma^2 \nu u^2\right)^{-t / \nu}
$$

#### Модель CGMY

$$
\phi_{CGMY}(u) = \exp \big( t C \Gamma(-Y) [ (M - i u)^Y - M^Y + (G + i u)^Y - G^Y ] \big)
$$

---

### 6. Hidden Markov Models для рыночных режимов

Используется дискретная HMM с $N$ скрытыми состояниями $S_t \in \{1, \dots, N\}$ и наблюдаемыми доходностями $r_t$.

- Матрица переходов: $A = [a_{ij}]$, где $a_{ij} = P(S_t = j \mid S_{t-1} = i)$
- Начальное распределение: $\pi_i = P(S_0 = i)$
- Плотности наблюдений: $f(r_t \mid S_t = i)$, обычно гауссовские или t‑распределения

Оценка параметров: Baum–Welch (EM), декодирование — Витерби, сглаживание вероятностей режимов — forward–backward.

---

### 7. GARCH модели волатильности

#### GARCH(1,1)

$$
\begin{aligned}
r_t &= \mu + \epsilon_t, \quad \epsilon_t = \sigma_t z_t, \quad z_t \sim \mathcal{N}(0,1) \\
\sigma_t^2 &= \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2
\end{aligned}
$$

#### EGARCH

$$
\log(\sigma_t^2) = \omega + \alpha \left( \frac{|\epsilon_{t-1}|}{\sigma_{t-1}} - \sqrt{\frac{2}{\pi}} \right) + \gamma \frac{\epsilon_{t-1}}{\sigma_{t-1}} + \beta \log(\sigma_{t-1}^2)
$$

#### GJR-GARCH

$$
\sigma_t^2 = \omega + (\alpha + \gamma I_{t-1}) \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2
$$

где $I_{t-1} = 1$, если $\epsilon_{t-1} < 0$, иначе $I_{t-1} = 0$.

---

## 📄 Работа с реестрами

### Формат реестра для облигаций

Реестр должен содержать следующие колонки:

#### Обязательные поля:

| Колонка | Описание | Пример | Тип данных |
|---------|----------|--------|------------|
| **ISIN** | ISIN облигации | RU000A10AU99 | Текст |
| **Дата оценки** | Дата оценки в формате YYYY-MM-DD | 2024-01-15 | Дата |

#### Режим 1: Два сценария

| Колонка | Описание | Пример | Тип данных |
|---------|----------|--------|------------|
| **Y аналога (%)** | Ставка дисконтирования для сценария 1 | 14.0 | Число |
| **Y индекса (%)** | Ставка дисконтирования для сценария 2 | 16.0 | Число |

#### Режим 2: Рыночная доходность из MOEX

| Колонка | Описание | Пример | Тип данных |
|---------|----------|--------|------------|
| **Рыночная доходность (%)** | Рыночная доходность (можно оставить пустым для автозагрузки) | 15.5 | Число |

#### Опциональные поля:

| Колонка | Описание | Пример | Тип данных |
|---------|----------|--------|------------|
| **Активность рынка** | Активность рынка (high/medium/low/unknown) | medium | Текст |
| **Базис расчета** | Базис расчета дней | Actual/365F | Текст |

### Поддерживаемые форматы

- **XLSX** — стандартный формат Excel
- **XLSM** — Excel с макросами (для облигаций)

### Функции работы с реестрами

1. **Загрузка реестра** — загрузка Excel файла с данными
2. **Расчет всех активов** — автоматический расчет для всех записей в реестре
3. **Выгрузка результатов** — экспорт результатов в XLSX
4. **Сохранение в Parquet** — сохранение реестра в сжатом формате Parquet в Supabase Storage

### Получение рыночной доходности из MOEX

Система автоматически получает рыночную доходность облигаций из MOEX ISS API на указанную дату оценки. Если данные недоступны на точную дату, используется ближайшая доступная дата.

---

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ с TimescaleDB (опционально)
- Supabase аккаунт (для хранения файлов)

### Backend

```bash
cd backend
pip install -r requirements.txt

# Создать .env файл
cp env.example .env
# Отредактировать .env с вашими настройками

# Запустить сервер
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install

# Создать .env.local
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# Запустить dev сервер
npm run dev
```

### Docker

```bash
docker-compose up -d --build
```

---

## ⚙️ Конфигурация

### Переменные окружения (`.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/stochastic_dashboard

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# MOEX API
MOEX_API_URL=https://iss.moex.com/iss
MOEX_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
```

---

## 📡 API Endpoints

### Оценка облигаций

- `POST /api/bond/valuate` — оценка облигации
- `GET /api/bond/market-yield?secid={isin}&date={date}` — получение рыночной доходности из MOEX

### Оценка свопов

- `POST /api/swap/valuate` — оценка свопа

### Оценка форвардов

- `POST /api/forward/valuate` — оценка форварда

### Работа с реестрами

- `POST /api/db/export/registry/parquet` — экспорт реестра в Parquet

### Полная документация

Доступна по адресу: `/docs` (Swagger UI) или `/redoc` (ReDoc)

---

## 📊 Доступные страницы

### Оценка инструментов

- **Справедливая стоимость облигаций** (`/bond-valuation`) — DCF оценка с поддержкой реестров
- **Оценка справедливой стоимости СВОПов** (`/valuation/swaps`) — оценка IRS, CDS, Basis Swaps
- **Forward Valuation** (`/valuation/forwards`) — оценка форвардных контрактов
- **Справедливая стоимость опционов** (`/pricing/options`) — Black-Scholes, Heston, SABR и др.

### Аналитика

- **Доходность облигаций** (`/fixed-income`) — анализ доходности
- **Кривая бескупонных доходностей** (`/zcyc-viewer`) — визуализация ZCYC
- **Рыночные режимы** (`/regimes`) — HMM анализ
- **HMM Аналитика** (`/regime-details`) — детальный анализ режимов
- **Volatility Surface** (`/analytics/volatility`) — поверхности волатильности
- **Факторная декомпозиция P&L** (`/analytics/pnl`) — анализ прибылей и убытков

### Риск-менеджмент

- **Стресс-тестирование** (`/stress`) — стресс-тесты портфелей
- **Стресс-тестирование Свопов** (`/stress/swaps`) — стресс-тесты свопов
- **Греческие параметры** (`/greeks`) — Delta, Gamma, Vega и др.
- **Греки СВОПов** (`/swap-greeks`) — чувствительность свопов
- **Greeks Dashboard** (`/forwards/greeks`) — греки форвардов
- **Регрессионное хеджирование** (`/hedging`) — хеджирование портфелей

### Инструменты

- **Forward Curve Builder** (`/forwards/curve`) — построение форвардных крив
- **Basis Analysis** (`/forwards/basis`) — анализ базиса
- **Сравнение моделей ценообразования** (`/pricing/options/models`) — сравнение моделей
- **Анализ чувствительности (Greeks)** (`/pricing/options/greeks`) — анализ греков опционов
- **Портфель опционов** (`/pricing/options/portfolio`) — управление портфелем опционов
- **CCMV Оптимизация** (`/CCMVoptimization`) — оптимизация портфеля

### Портфель и отчеты

- **Портфель** (`/portfolio`) — управление портфелем
- **Monte Carlo** (`/monte-carlo`) — симуляции Монте-Карло
- **Бэктестинг** (`/backtest`) — тестирование стратегий
- **Отчёты** (`/reports`) — генерация отчетов
- **Отчет об оценке облигаций** (`/bond-report`) — отчеты по облигациям

---

## 💾 Хранение данных

### Supabase Storage

Реестры и отчеты сохраняются в Supabase Storage в сжатом формате Parquet:

```
files/
  ├── registries/
  │   └── {registry_type}_registry_{date}.parquet
  ├── reports/
  │   └── {report_type}_{date}.pdf
  └── exports/
      └── {export_type}_{date}.parquet
```

### Преимущества Parquet

- **Эффективное сжатие** (обычно в 5-10 раз меньше чем CSV)
- **Быстрые запросы** (читает только нужные колонки)
- **Поддержка типов данных** (сохраняет типы, даты, etc.)

---

## 🔧 Разработка

### Структура проекта

```text
stochastic-dashbord-v1/
├── backend/
│   ├── src/
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Бизнес-логика
│   │   ├── database/     # Работа с Supabase
│   │   └── main.py       # Точка входа
│   ├── bond_pricing.py   # Модуль оценки облигаций
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Страницы приложения
│   │   ├── components/   # UI компоненты
│   │   ├── services/     # API клиенты
│   │   └── router/       # Маршрутизация
│   └── package.json
└── README.md
```

### Тестирование

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты (если настроены)
cd frontend
npm run test
```

---

## 📝 Лицензия

Проект предназначен **исключительно для исследовательских и учебных целей**.

---

## ⚠️ Ограничения и дисклеймер

- Реализованные модели и калибровка **не являются** рекомендацией к использованию в продакшн-системах без независимой валидации
- В расчетах предполагается отсутствие арбитража, совершенные рынки и стандартные допущения риск-нейтрального мира
- Качество результатов чувствительно к выбору входных данных и параметров калибровки

Перед использованием в реальном риск- или PnL-контуре обязательно проведите:
- Бэктесты на исторических данных
- Стресс-тестирование на экстремальных сценариях
- Сравнение с бенчмарками
- Независимую валидацию со стороны risk-модели

---

## 🔗 Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js 3 Documentation](https://vuejs.org/)
- [Supabase Documentation](https://supabase.com/docs)
- [MOEX ISS API](https://www.moex.com/a2193)
