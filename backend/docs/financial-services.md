# 4.2. Сервисы финансовой аналитики

## Обзор

Backend реализует вычислительные сервисы для количественного финансового анализа: GARCH, спектральный анализ, HMM и bond pricing.

## Bond Pricing Engine (`bond_pricing.py`, ~1470 строк)

### DCF-оценка
```python
def calculate_dcf_price(cashflows, dates, valuation_date, yield_rate, day_count_convention):
    """
    P = Σ CF_i / (1 + y)^t_i
    t_i зависит от day count convention
    """
```

### Метрики

**YTM (Yield to Maturity):**
Численное решение через метод Ньютона.

**Macaulay Duration:**
```
D = (1/P) × Σ t_i × CF_i / (1 + y)^t_i
```

**Modified Duration:**
```
D_mod = D / (1 + y/m)
```

**Convexity:**
```
C = (1/P) × Σ t_i × (t_i + 1/m) × CF_i / (1 + y)^t_i
```

### Оптимизации
- `.iterrows()` заменено на `.itertuples()` и `.to_dict('records')` (10-100x ускорение)
- Векторизированные NumPy-операции

## GARCH Volatility Service (`compute_service.py`)

### Модель GARCH(1,1)
```python
def calculate_garch(returns, omega=0.000025, alpha=0.082, beta=0.893):
    """
    σ²_t = ω + α × ε²_{t-1} + β × σ²_{t-1}

    Используются raw returns (не стандартизированные остатки)
    по Bollerslev (1986).
    """
    # Начальная дисперсия = long-run variance
    variance = omega / (1 - alpha - beta)

    for t in range(len(returns)):
        variance = omega + alpha * returns[t-1]**2 + beta * variance
        variances[t] = variance
```

### Валидация
- α + β < 1 (стационарность)
- Variance floor (предотвращение нулевой дисперсии)
- Начальная дисперсия = ω / (1 - α - β)

### Выходные данные
- Условные дисперсии (массив)
- Условные волатильности (√дисперсий)
- Стандартизированные остатки
- Параметры модели
- Long-term volatility

### Сложность
O(T), где T — длина временного ряда.

## Spectral Regime Service (`spectral_regime_service.py`)

### SpectralRegimeAnalyzer

Декомпозирует рыночную динамику на полюса методом Прони через ACF.

### Алгоритм

```
1. ACF-вычисление с максимальным лагом
2. Построение Ганкелевой матрицы из ACF
3. Eigendecomposition (np.linalg.eig)
4. Извлечение полюсов
5. Иерархическая кластеризация (scipy.cluster.hierarchy)
6. Классификация режимов по |λ_k|
```

### Классификация полюсов

| |λ_k| | Режим |
|-------|-------|
| < 0.5 | Шум |
| 0.5 - 0.8 | Слабый тренд |
| 0.8 - 0.95 | Умеренный тренд |
| 0.95 - 0.999 | Сильный тренд |
| ≥ 0.999 | Кризис |

### Динамический анализ

Скользящее окно:
- Вычисление режимных энергий на каждом шаге
- Расчёт энтропии Шеннона для неопределённости
- Временная линия переходов

### Сложность
- Прони: O(H³), H = max_lag
- Кластеризация: O(M² log M), M = кол-во полюсов
- Динамический анализ: O(T × K × W)

## HMM Service (`multivariate_hmm_service.py`, ~888 строк)

### Мультивариантные гауссовские эмиссии

Три измерения: returns, volatility, liquidity.

### Реализованные алгоритмы

**Baum-Welch (EM):**
Оценка параметров HMM через итеративный EM-алгоритм.

**Viterbi:**
Нахождение наиболее вероятной последовательности состояний через динамическое программирование.

**Forward-Backward:**
Вычисление сглаженных апостериорных вероятностей.

### Нормализация
Исправлено: `if sum > 0` вместо `/(sum + 1e-10)` (7 мест).

## CCMV Service (`ccmv_service.py`)

### MIQP через CVXPy

Решение задачи Mixed-Integer Quadratic Programming:
```
min  w'Σw - γ × μ'w
s.t. Σ wᵢ = 1
     0 ≤ wᵢ ≤ w̄
     Σ zᵢ ≤ Δ  (binary: zᵢ ∈ {0,1})
     wᵢ ≤ w̄ × zᵢ
```

### Валидация PSD
Ковариационная матрица проверяется через `eigvalsh`:
```python
eigenvalues = np.linalg.eigvalsh(cov_matrix)
if np.min(eigenvalues) < -1e-8:
    cov_matrix += (abs(min_eig) + 1e-6) * np.eye(n)
```

## HJB Service (`hjb_service.py`)

### Задача Мертона + Монте-Карло

Оптимальная аллокация:
```
π* = (μ - r) / (γ × σ²)
```

### Sharpe Ratio
Исправлено: `(R - Rf) / σ` вместо `R / σ` (3 места).

## Зависимости

| Библиотека | Использование |
|-----------|---------------|
| NumPy | Линейная алгебра, eigendecomposition |
| SciPy | Ганкелева матрица, кластеризация, оптимизация |
| Pandas | Временные ряды, DataFrames |
| CVXPy | MIQP оптимизация |
| yfinance | Исторические рыночные данные |

## Валидация и устойчивость

- Минимум 50 наблюдений для спектрального анализа
- NaN/Inf проверки
- Численная регуляризация
- Защита от деления на ноль
- Cross-validation против известных решений
