# 3.5. Фиксированный доход и оценка облигаций

## Обзор

Модуль реализует DCF-оценку (Discounted Cash Flow) облигаций с поддержкой нескольких day count конвенций, интеграцию с MOEX для получения кривых бескупонных доходностей и инструменты отчётности.

## Bond DCF Engine

### Формула дисконтирования

Чистая цена облигации:
```
P = Σᵢ CFᵢ / (1 + y)^tᵢ
```
где:
- `CFᵢ` — денежный поток (купон или номинал)
- `y` — ставка дисконтирования (годовая)
- `tᵢ` — время до потока в годах (зависит от day count convention)

### Day Count Conventions

| Конвенция | Формула tᵢ | Применение |
|-----------|-----------|------------|
| **Actual/365F** | (actual_days) / 365 | Российский рынок (по умолчанию) |
| **Actual/360** | (actual_days) / 360 | Денежные рынки |
| **Actual/Actual (ISDA)** | Точный подсчёт | Государственные облигации |
| **30/360 (US)** | (360×ΔY + 30×ΔM + ΔD) / 360 | Корпоративные облигации (США) |
| **30E/360** | Европейский 30/360 | Еврооблигации |
| **30E/360 (ISDA)** | ISDA-вариант | Свопы |
| **Actual/Actual (ISMA)** | Точный подсчёт (ISMA) | ISMA-стандарт |

### Метрики

**Yield to Maturity (YTM):**
Решение уравнения `P = Σ CFᵢ / (1 + YTM)^tᵢ` методом Ньютона.

**Macaulay Duration:**
```
D = (1/P) × Σᵢ tᵢ × CFᵢ / (1 + y)^tᵢ
```

**Modified Duration:**
```
D_mod = D / (1 + y/m)
```
где `m` — частота купонов.

**Convexity:**
```
C = (1/P) × Σᵢ tᵢ × (tᵢ + 1/m) × CFᵢ / (1 + y)^tᵢ
```

## Интерфейс оценки (BondValuation.vue)

### Входные данные
- ISIN облигации (например, RU000A10AU99)
- Дата оценки (YYYY-MM-DD)
- Ставка дисконтирования — сценарий 1 (доходность аналога, %)
- Ставка дисконтирования — сценарий 2 (доходность индекса, %)
- Day count convention (выпадающий список)

### Выходные данные
- Чистая и грязная цена для обоих сценариев
- Duration (Macaulay и Modified)
- Convexity
- YTM
- График денежных потоков

## ZCYC Viewer (ZCYCViewer.vue)

### Назначение
Визуализация кривой бескупонных доходностей (КБД) из MOEX ISS API.

### Источник данных
MOEX предоставляет кривую, интерполированную методом **Нельсона-Зигеля**:
```
y(τ) = β₁ + β₂ × [(1 - e^(-τ/λ)) / (τ/λ)] + β₃ × [(1 - e^(-τ/λ)) / (τ/λ) - e^(-τ/λ)]
```

### API Endpoints

| Метод | Endpoint | Назначение |
|-------|----------|------------|
| GET | `/api/zcyc` | Получить кривую на дату |
| POST | `/api/zcyc/interpolate` | Интерполяция для заданного срока |
| GET | `/api/zcyc/dates` | Список доступных дат |
| GET | `/api/zcyc/latest` | Последняя доступная кривая |
| GET | `/api/zcyc/yearyields` | Кривая годовых доходностей |
| POST | `/api/zcyc/discount` | Преобразование в discount curve |

### Fallback-механизм

```
1. Попытка: /engines/stock/zcyc.json (основной MOEX endpoint)
2. Fallback: build_zcyc_from_bonds() — строит кривую из данных ОФЗ
3. Ошибка: предложение сменить дату
```

## Bond Reports

### Vanilla Bond Report (VanillaBondReport.vue)
- Расписание денежных потоков (cashflow schedule)
- YTM, G-spread
- Сравнение с индексами MOEX (AAA, AA, A, BBB)
- Экспорт в Excel/PDF

### Floater Bond Report (FloaterBondReport.vue)
- Формула купона
- Discount Margin (DM) и Quoted Margin (QM)
- Динамика маржи
- Интеграция с forward curve
- Экспорт в Excel/PDF

## Excel Registry

Batch processing через импорт Excel:

| Колонка | Описание |
|---------|----------|
| ISIN | Идентификатор облигации |
| Valuation Date | Дата оценки |
| Discount Yield 1 | Ставка сценария 1 |
| Discount Yield 2 | Ставка сценария 2 |
| Day Count | Конвенция |

Результаты экспортируются в **Parquet** через PyArrow (сжатие 5-10x vs CSV).

## MOEX API Endpoints

| URL | Назначение |
|-----|------------|
| `/iss/engines/stock/zcyc.json` | Кривая КБД |
| `/iss/engines/stock/zcyc/yearyields.json` | Годовые доходности |
| `/iss/history/engines/stock/markets/bonds/` | Исторические цены |
| `/iss/engines/stock/markets/bonds/boards/TQOB/securities` | Список ОФЗ |
