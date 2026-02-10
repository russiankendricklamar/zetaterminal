// Knowledge Base Data - Full Documentation
// Contains all formulas, explanations, and features

export interface KnowledgeItem {
  id: string
  code: string
  title: string
  category: string
  description: string
  formula?: string
  formulaExplanation?: string
  features: string[]
  howToUse?: string[]
  path?: string
  relatedItems?: string[]
}

export interface Category {
  id: string
  name: string
  description: string
  color: string
  longDescription: string
}

export const categories: Category[] = [
  {
    id: 'options',
    name: 'ОПЦИОНЫ',
    description: 'Ценообразование опционов, греки, модели волатильности',
    color: '#22c55e',
    longDescription: 'Раздел посвящён ценообразованию опционов с использованием классических и современных моделей: Black-Scholes, Heston, Merton, SABR. Включает расчёт греков (чувствительностей) и анализ портфеля опционов.'
  },
  {
    id: 'bonds',
    name: 'ОБЛИГАЦИИ',
    description: 'Оценка облигаций, дюрация, кривые доходности',
    color: '#3b82f6',
    longDescription: 'Инструменты для оценки облигаций методом дисконтированных денежных потоков, расчёта дюрации, выпуклости, DV01. Поддержка фиксированных и плавающих купонов, интеграция с MOEX.'
  },
  {
    id: 'swaps',
    name: 'СВОПЫ И ФОРВАРДЫ',
    description: 'IRS, CDS, форварды, базисный анализ',
    color: '#f59e0b',
    longDescription: 'Оценка процентных свопов (IRS), кредитных дефолтных свопов (CDS), валютных свопов и форвардных контрактов. Анализ базиса и построение форвардных кривых.'
  },
  {
    id: 'risk',
    name: 'РИСК-МЕНЕДЖМЕНТ',
    description: 'VaR, стресс-тесты, хеджирование',
    color: '#ef4444',
    longDescription: 'Комплексный анализ рисков портфеля: Value-at-Risk, Expected Shortfall, стресс-тестирование. Инструменты для построения хеджей и атрибуции P&L.'
  },
  {
    id: 'simulation',
    name: 'СИМУЛЯЦИИ',
    description: 'Monte Carlo, бэктестинг, сценарии',
    color: '#8b5cf6',
    longDescription: 'Стохастическое моделирование с использованием Monte Carlo симуляций на основе геометрического броуновского движения. Бэктестинг торговых стратегий.'
  },
  {
    id: 'regimes',
    name: 'РЕЖИМЫ РЫНКА',
    description: 'HMM, спектральный анализ, переходы',
    color: '#06b6d4',
    longDescription: 'Определение рыночных режимов с помощью скрытых марковских моделей (HMM). Анализ матриц переходов, стационарных распределений и спектральных свойств.'
  },
  {
    id: 'portfolio',
    name: 'ПОРТФЕЛЬ',
    description: 'Оптимизация, аллокация, метрики',
    color: '#ec4899',
    longDescription: 'Управление портфелем активов: оптимизация по Марковицу, HJB-оптимизация, расчёт Sharpe Ratio, анализ диверсификации и корреляций.'
  },
  {
    id: 'terminal',
    name: 'ТЕРМИНАЛ',
    description: 'Потоковые данные, количественный анализ',
    color: '#f97316',
    longDescription: 'Торговый терминал с потоковыми данными в реальном времени. Продвинутые 3D-визуализации: поверхности волатильности, фазовое пространство, модели ликвидности.'
  }
]

export const items: KnowledgeItem[] = [
  // ═══════════════════════════════════════════════════════════════
  // ОПЦИОНЫ - OPTIONS
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'bsm',
    code: 'BSM',
    title: 'Модель Блэка-Шоулза',
    category: 'options',
    path: '/pricing/options',
    description: 'Классическая модель ценообразования европейских опционов, разработанная Фишером Блэком и Майроном Шоулзом в 1973 году. Предполагает логнормальное распределение цены базового актива и постоянную волатильность.',
    formula: 'C = S₀·N(d₁) - K·e^(-rT)·N(d₂)',
    formulaExplanation: `Где:
• C — цена колл-опциона
• S₀ — текущая цена базового актива
• K — страйк (цена исполнения)
• r — безрисковая ставка
• T — время до экспирации (в годах)
• N(x) — функция стандартного нормального распределения
• d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
• d₂ = d₁ - σ√T
• σ — волатильность базового актива

Для пут-опциона: P = K·e^(-rT)·N(-d₂) - S₀·N(-d₁)`,
    features: [
      'Расчёт цены Call и Put опционов',
      'Поддержка дивидендной доходности',
      'Расчёт всех греков (Δ, Γ, ν, Θ, ρ)',
      'Implied Volatility калькулятор',
      'Batch-расчёт из Excel'
    ],
    howToUse: [
      'Введите параметры: S₀ (цена актива), K (страйк), T (срок), r (ставка), σ (волатильность)',
      'Выберите тип опциона: Call или Put',
      'Нажмите "Рассчитать" для получения цены и греков',
      'Используйте IV калькулятор для определения подразумеваемой волатильности по рыночной цене'
    ],
    relatedItems: ['greeks', 'heston', 'volsurf']
  },
  {
    id: 'heston',
    code: 'HEST',
    title: 'Модель Хестона',
    category: 'options',
    path: '/pricing/options/models',
    description: 'Модель стохастической волатильности, где волатильность сама является случайным процессом. Позволяет воспроизводить "улыбку волатильности" и эффект левериджа.',
    formula: 'dSₜ = μSₜdt + √Vₜ·Sₜ·dW₁\ndVₜ = κ(θ - Vₜ)dt + ξ√Vₜ·dW₂',
    formulaExplanation: `Система стохастических дифференциальных уравнений:

• Sₜ — цена базового актива
• Vₜ — мгновенная дисперсия (σ² = V)
• μ — дрифт цены актива
• κ — скорость возврата волатильности к среднему
• θ — долгосрочный уровень дисперсии
• ξ — волатильность волатильности (vol of vol)
• ρ — корреляция между dW₁ и dW₂ (обычно отрицательная)
• dW₁, dW₂ — коррелированные винеровские процессы

Условие Феллера: 2κθ > ξ² гарантирует V > 0`,
    features: [
      'Стохастическая волатильность',
      'Воспроизведение улыбки волатильности',
      'Эффект левериджа (отрицательная корреляция)',
      'Mean-reversion волатильности',
      'Калибровка на рыночные данные'
    ],
    howToUse: [
      'Задайте базовые параметры опциона (S, K, T, r)',
      'Настройте параметры Хестона: V₀, κ, θ, ξ, ρ',
      'Сравните цену с BSM для оценки влияния стохастической волатильности',
      'Используйте для pricing опционов с длинными сроками'
    ],
    relatedItems: ['bsm', 'sabr', 'volsurf']
  },
  {
    id: 'greeks',
    code: 'GREEK',
    title: 'Греки опционов',
    category: 'options',
    path: '/option-greeks-analyzer',
    description: 'Греки — это частные производные цены опциона по различным параметрам. Они показывают чувствительность цены к изменению входных параметров и используются для управления рисками.',
    formula: 'Δ = ∂C/∂S, Γ = ∂²C/∂S², ν = ∂C/∂σ, Θ = ∂C/∂t, ρ = ∂C/∂r',
    formulaExplanation: `Основные греки для BSM:

• Delta (Δ) = N(d₁) для Call, N(d₁)-1 для Put
  Изменение цены опциона при изменении базового актива на $1

• Gamma (Γ) = N'(d₁) / (S·σ·√T)
  Скорость изменения дельты, "выпуклость" опциона

• Vega (ν) = S·√T·N'(d₁)
  Чувствительность к изменению волатильности на 1%

• Theta (Θ) = -S·N'(d₁)·σ/(2√T) - r·K·e^(-rT)·N(d₂)
  Временной распад, потеря стоимости за 1 день

• Rho (ρ) = K·T·e^(-rT)·N(d₂) для Call
  Чувствительность к изменению процентной ставки`,
    features: [
      'Расчёт всех 5 основных греков',
      'P&L сценарный анализ',
      'Матрица чувствительности (ΔS × Δσ)',
      'Декомпозиция P&L по грекам',
      'Визуализация профиля греков'
    ],
    howToUse: [
      'Введите параметры опциона или выберите из портфеля',
      'Просмотрите значения греков в карточках KPI',
      'Используйте сценарный анализ для оценки P&L при изменении S или σ',
      'Изучите матрицу чувствительности для понимания рисков'
    ],
    relatedItems: ['bsm', 'portfolio-greeks', 'hedging']
  },
  {
    id: 'merton',
    code: 'MERT',
    title: 'Модель Мертона (Jump Diffusion)',
    category: 'options',
    path: '/pricing/options/models',
    description: 'Расширение модели Блэка-Шоулза с добавлением скачков цены (jumps). Позволяет моделировать резкие движения рынка и "толстые хвосты" распределения доходностей.',
    formula: 'dSₜ = (μ - λk)Sₜdt + σSₜdWₜ + Sₜ(e^J - 1)dNₜ',
    formulaExplanation: `Компоненты модели:

• dWₜ — стандартное броуновское движение
• dNₜ — пуассоновский процесс с интенсивностью λ
• J — размер скачка, J ~ N(μⱼ, σⱼ²)
• k = E[e^J - 1] = e^(μⱼ + σⱼ²/2) - 1
• λ — среднее количество скачков в год

Цена опциона вычисляется как сумма:
C = Σₙ (e^(-λT)(λT)ⁿ/n!) · BSM(Sₙ, σₙ)

где σₙ² = σ² + nσⱼ²/T`,
    features: [
      'Моделирование скачков цены',
      'Толстые хвосты распределения',
      'Калибровка интенсивности скачков',
      'Сравнение с BSM',
      'Распределение размера скачков'
    ],
    howToUse: [
      'Задайте параметры диффузии (σ) и скачков (λ, μⱼ, σⱼ)',
      'Сравните цену с BSM для оценки премии за скачки',
      'Используйте для опционов на активы с редкими резкими движениями'
    ],
    relatedItems: ['bsm', 'bates', 'variance-gamma']
  },
  {
    id: 'sabr',
    code: 'SABR',
    title: 'Модель SABR',
    category: 'options',
    path: '/volatility-surface',
    description: 'Stochastic Alpha Beta Rho — модель для описания динамики улыбки волатильности. Широко используется на рынках процентных ставок и валют.',
    formula: 'dFₜ = σₜ·Fₜ^β·dW₁\ndσₜ = α·σₜ·dW₂',
    formulaExplanation: `Параметры модели SABR:

• F — форвардная цена
• σ — стохастическая волатильность
• α — vol-of-vol (волатильность волатильности)
• β — эластичность (0 ≤ β ≤ 1)
  - β = 0: нормальная модель
  - β = 1: логнормальная модель
• ρ — корреляция между F и σ

Формула Хагана для implied volatility:
σᵢₘₚ(K) ≈ α·[...] · [1 + (ε₁ + ε₂)T]

где коэффициенты зависят от α, β, ρ и F/K`,
    features: [
      'Калибровка на рыночную улыбку',
      'Интерполяция между страйками',
      'Динамика улыбки во времени',
      'Применение для swaptions и caps',
      'Параметр β для контроля скошенности'
    ],
    howToUse: [
      'Загрузите рыночные котировки опционов',
      'Запустите калибровку для нахождения α, β, ρ',
      'Используйте для интерполяции IV между страйками',
      'Экстраполируйте улыбку на нестандартные страйки'
    ],
    relatedItems: ['volsurf', 'heston', 'swaptions']
  },
  {
    id: 'volsurf',
    code: 'VOLSURF',
    title: 'Поверхность волатильности',
    category: 'options',
    path: '/volatility-surface',
    description: '3D-визуализация подразумеваемой волатильности как функции страйка и времени до экспирации. Отражает рыночные ожидания будущей волатильности.',
    formula: 'IV = f(K/S, T)',
    formulaExplanation: `Поверхность волатильности описывает:

• Улыбка (Smile): IV выше для OTM опционов
  - Вызвана толстыми хвостами распределения
  - Отражает страх рынка перед резкими движениями

• Скос (Skew): асимметрия улыбки
  - Negative skew: IV(Put OTM) > IV(Call OTM)
  - Характерен для акций (crash risk)

• Временная структура: изменение IV с T
  - Обычно убывает с ростом T (term structure)
  - Инверсия при ожидании событий

Монейность: m = ln(K/F) / (σ√T)
ATM: m = 0, OTM Put: m < 0, OTM Call: m > 0`,
    features: [
      '3D интерактивная визуализация',
      'Построение по разным моделям',
      'Wireframe и solid режимы',
      'Анимация вращения',
      'Экспорт данных'
    ],
    howToUse: [
      'Выберите модель построения (BSM, Heston, SABR, Local Vol)',
      'Загрузите рыночные котировки из Excel',
      'Изучите форму улыбки и скоса',
      'Вращайте поверхность для анализа структуры'
    ],
    relatedItems: ['sabr', 'heston', 'bsm']
  },
  {
    id: 'portfolio-options',
    code: 'OPTPF',
    title: 'Портфель опционов',
    category: 'options',
    path: '/option-portfolio',
    description: 'Управление портфелем опционных позиций с агрегированием греков, анализом P&L и оценкой рисков.',
    formula: 'Δₚ = Σᵢ nᵢ·Δᵢ, Γₚ = Σᵢ nᵢ·Γᵢ, ...',
    formulaExplanation: `Агрегирование греков портфеля:

• Портфельная Delta: Δₚ = Σ (количество × Δ каждой позиции)
• Портфельная Gamma: Γₚ = Σ (количество × Γ)
• Портфельная Vega: νₚ = Σ (количество × ν)
• Портфельная Theta: Θₚ = Σ (количество × Θ)

P&L декомпозиция:
ΔP&L ≈ Δ·ΔS + ½Γ·(ΔS)² + ν·Δσ + Θ·Δt

Нетто-позиция определяет направленность:
• Δₚ > 0: лонг по рынку
• Γₚ > 0: выигрыш от волатильности
• Θₚ < 0: временной распад (платим)`,
    features: [
      'Агрегированные греки портфеля',
      'P&L по каждой позиции',
      'Анализ монейности',
      'Группировка по экспирациям',
      'Нетто-греки портфеля'
    ],
    howToUse: [
      'Добавьте опционные позиции в портфель',
      'Просмотрите агрегированные греки',
      'Оцените P&L при сценарных изменениях',
      'Идентифицируйте риски (gamma risk, vega risk)'
    ],
    relatedItems: ['greeks', 'hedging', 'pnl-attr']
  },

  // ═══════════════════════════════════════════════════════════════
  // ОБЛИГАЦИИ - BONDS
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'bond-valuation',
    code: 'BOND',
    title: 'Оценка облигаций (DCF)',
    category: 'bonds',
    path: '/bond-valuation',
    description: 'Оценка облигаций методом дисконтированных денежных потоков. Рассчитывается приведённая стоимость всех будущих купонов и номинала.',
    formula: 'P = Σᵢ CFᵢ/(1+y)^tᵢ + N/(1+y)^T',
    formulaExplanation: `Формула приведённой стоимости:

P = Σ [C/(1+y)^tᵢ] + N/(1+y)^T

Где:
• P — грязная цена облигации (Dirty Price)
• C — купонный платёж
• N — номинал (обычно 100 или 1000)
• y — доходность к погашению (YTM)
• tᵢ — время до i-го купона (в годах)
• T — время до погашения

Чистая цена = Грязная цена - НКД
НКД = C × (дней с последнего купона / дней в купонном периоде)

YTM находится итеративно (Newton-Raphson):
P(y) = Market Price`,
    features: [
      'Расчёт грязной и чистой цены',
      'Накопленный купонный доход (НКД)',
      'Доходность к погашению (YTM)',
      'Интеграция с MOEX ISS API',
      'Batch-расчёт из Excel'
    ],
    howToUse: [
      'Введите ISIN или выберите облигацию из списка',
      'Система загрузит параметры с MOEX',
      'Укажите дату оценки и кривую доходности',
      'Получите цену, YTM и аналитику'
    ],
    relatedItems: ['duration', 'zcyc', 'convexity']
  },
  {
    id: 'duration',
    code: 'DUR',
    title: 'Дюрация и DV01',
    category: 'bonds',
    path: '/bond-valuation',
    description: 'Дюрация — мера процентного риска облигации, показывающая чувствительность цены к изменению доходности. DV01 — изменение цены при сдвиге ставки на 1 б.п.',
    formula: 'D = -1/P · dP/dy = Σ(tᵢ·PVᵢ)/P',
    formulaExplanation: `Виды дюрации:

• Дюрация Маколея:
  Dₘ = Σ[tᵢ · CFᵢ/(1+y)^tᵢ] / P
  Средневзвешенный срок денежных потоков

• Модифицированная дюрация:
  Dₘₒₐ = Dₘ / (1 + y/m)
  где m — частота купонов в год

• Dollar Duration (DV01):
  DV01 = Dₘₒₐ × P × 0.0001
  Изменение цены при росте ставки на 1 б.п.

Приближение изменения цены:
ΔP ≈ -Dₘₒₐ × P × Δy

Для большей точности добавляем выпуклость:
ΔP ≈ -Dₘₒₐ × P × Δy + ½ × Convexity × P × (Δy)²`,
    features: [
      'Дюрация Маколея',
      'Модифицированная дюрация',
      'DV01 (PVBP)',
      'Эффективная дюрация',
      'Key Rate Duration'
    ],
    howToUse: [
      'Загрузите облигацию по ISIN',
      'Просмотрите показатели в карточках метрик',
      'Используйте DV01 для оценки риска позиции',
      'Сравните дюрации для выбора облигаций'
    ],
    relatedItems: ['bond-valuation', 'convexity', 'hedging']
  },
  {
    id: 'convexity',
    code: 'CONV',
    title: 'Выпуклость (Convexity)',
    category: 'bonds',
    path: '/bond-valuation',
    description: 'Выпуклость — вторая производная цены по доходности. Улучшает оценку изменения цены при больших движениях ставок.',
    formula: 'Convexity = 1/P · d²P/dy² = Σ[tᵢ(tᵢ+1)·PVᵢ] / [P·(1+y)²]',
    formulaExplanation: `Выпуклость описывает кривизну зависимости P(y):

Convexity = [Σ tᵢ(tᵢ+1)·CFᵢ/(1+y)^tᵢ] / [P·(1+y)²]

Свойства:
• Convexity > 0 для обычных облигаций
• Чем больше Convexity, тем лучше для инвестора
• При росте ставок — меньше потери
• При падении ставок — больше прибыль

Полная формула изменения цены:
ΔP/P ≈ -Dₘₒₐ·Δy + ½·Convexity·(Δy)²

Пример: D = 5, C = 30, Δy = +1%
ΔP/P ≈ -5×0.01 + 0.5×30×0.0001 = -4.85%
(без convexity было бы -5%)`,
    features: [
      'Расчёт выпуклости',
      'Dollar Convexity',
      'Сравнение облигаций',
      'Сценарный анализ',
      'Визуализация P(y)'
    ],
    howToUse: [
      'Выберите облигацию для анализа',
      'Сравните Convexity разных бумаг',
      'Используйте для оценки риска при больших движениях ставок'
    ],
    relatedItems: ['duration', 'bond-valuation']
  },
  {
    id: 'zcyc',
    code: 'ZCYC',
    title: 'Кривая бескупонной доходности',
    category: 'bonds',
    path: '/zcyc-viewer',
    description: 'Zero-Coupon Yield Curve — кривая доходности, построенная по бескупонным инструментам. Отражает временную структуру процентных ставок.',
    formula: 'P(T) = e^(-r(T)·T) или P(T) = 1/(1+r(T))^T',
    formulaExplanation: `Построение ZCYC:

1. Bootstrapping из рыночных инструментов:
   - Короткие сроки: денежный рынок (RUONIA, депозиты)
   - Средние: свопы (IRS)
   - Длинные: гос. облигации

2. Discount Factor:
   DF(T) = e^(-r(T)·T) для непрерывного начисления
   DF(T) = 1/(1+r(T))^T для дискретного

3. Forward Rate:
   f(t₁,t₂) = [r(t₂)·t₂ - r(t₁)·t₁] / (t₂-t₁)

4. Интерполяция:
   - Linear (простая)
   - Cubic Spline (гладкая)
   - Nelson-Siegel (параметрическая)

MOEX публикует G-Curve (ОФЗ) ежедневно`,
    features: [
      'Загрузка с MOEX ISS API',
      'Историческое сравнение',
      'Статистика кривой',
      '3D визуализация',
      'Forward rates'
    ],
    howToUse: [
      'Выберите дату для загрузки кривой',
      'Сравните с историческими данными',
      'Изучите форму кривой (нормальная/инвертированная)',
      'Используйте для дисконтирования денежных потоков'
    ],
    relatedItems: ['bond-valuation', 'swap-val', 'forward-curve']
  },
  {
    id: 'floater',
    code: 'FRN',
    title: 'Облигации с плавающим купоном',
    category: 'bonds',
    path: '/floater-bond-report',
    description: 'Floating Rate Notes — облигации с купоном, привязанным к референсной ставке (RUONIA, SOFR). Имеют низкую процентную чувствительность.',
    formula: 'Coupon = Reference Rate + Spread',
    formulaExplanation: `Механика FRN:

Купон = Референсная ставка + Спред

• Референсные ставки:
  - RUONIA (Россия)
  - SOFR (США)
  - EURIBOR (Еврозона)
  - SONIA (Великобритания)

• Спред фиксирован на весь срок
• Купон пересчитывается каждый период

Особенности оценки:
• Дюрация ≈ время до следующего reset
• Цена близка к номиналу в дату reset
• Основной риск — кредитный (spread risk)

Dirty Price = PV(будущих купонов) + PV(номинала)
где купоны прогнозируются через forward rates`,
    features: [
      'Прогноз купонов через forwards',
      'Spread analysis',
      'Reset mechanics',
      'Сравнение с fixed-rate',
      'RUONIA интеграция'
    ],
    howToUse: [
      'Введите ISIN флоатера',
      'Просмотрите текущий и прогнозные купоны',
      'Оцените spread risk',
      'Сравните с фиксированными облигациями'
    ],
    relatedItems: ['bond-valuation', 'zcyc', 'swap-val']
  },

  // ═══════════════════════════════════════════════════════════════
  // СВОПЫ И ФОРВАРДЫ - SWAPS & FORWARDS
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'irs',
    code: 'IRS',
    title: 'Процентные свопы (IRS)',
    category: 'swaps',
    path: '/valuation/swaps',
    description: 'Interest Rate Swap — контракт обмена фиксированных платежей на плавающие. Используется для хеджирования процентного риска.',
    formula: 'NPV = PV(Fixed Leg) - PV(Floating Leg)',
    formulaExplanation: `Структура IRS:

• Fixed Leg: платим/получаем фиксированную ставку K
  PV_fixed = K × Σ[Δtᵢ × DF(tᵢ)] × Notional

• Floating Leg: получаем/платим плавающую ставку
  PV_float = Σ[Fᵢ × Δtᵢ × DF(tᵢ)] × Notional
  где Fᵢ — forward rate

Par Swap Rate (справедливая фикс. ставка):
K* = [1 - DF(T)] / Σ[Δtᵢ × DF(tᵢ)]

DV01 свопа:
DV01 ≈ Σ[Δtᵢ × DF(tᵢ)] × Notional × 0.0001

Payer Swap: платим fixed, получаем float
Receiver Swap: получаем fixed, платим float`,
    features: [
      'Расчёт NPV и DV01',
      'Par rate калькулятор',
      'Payer / Receiver свопы',
      'Multi-currency support',
      'Batch valuation'
    ],
    howToUse: [
      'Задайте notional, maturity, fixed rate',
      'Выберите floating leg (RUONIA, MOSPRIME)',
      'Рассчитайте NPV и risk metrics',
      'Используйте для хеджирования bond portfolio'
    ],
    relatedItems: ['cds', 'forward-val', 'duration']
  },
  {
    id: 'cds',
    code: 'CDS',
    title: 'Кредитные дефолтные свопы',
    category: 'swaps',
    path: '/valuation/swaps',
    description: 'Credit Default Swap — страховка от дефолта. Покупатель платит премию, продавец компенсирует потери при дефолте.',
    formula: 'Spread × RPV01 = (1-R) × Σ[q(tᵢ)·DF(tᵢ)]',
    formulaExplanation: `Компоненты CDS:

• Premium Leg (платежи покупателя):
  PV_premium = Spread × RPV01
  RPV01 = Σ[Δtᵢ × DF(tᵢ) × Q(tᵢ)]
  Q(tᵢ) — вероятность выживания до tᵢ

• Protection Leg (выплата при дефолте):
  PV_protection = (1-R) × Σ[q(tᵢ) × DF(tᵢ)]
  q(tᵢ) = Q(tᵢ₋₁) - Q(tᵢ) — вероятность дефолта
  R — Recovery Rate (обычно 40%)

Par Spread (справедливый spread):
S* = (1-R) × Σ[q(tᵢ)·DF(tᵢ)] / RPV01

Hazard Rate (интенсивность дефолта):
λ ≈ Spread / (1-R)`,
    features: [
      'Расчёт NPV',
      'Par spread calculator',
      'Implied default probability',
      'Recovery rate sensitivity',
      'Hazard rate curve'
    ],
    howToUse: [
      'Введите reference entity и notional',
      'Укажите spread и recovery rate',
      'Рассчитайте справедливую стоимость',
      'Оцените вероятность дефолта'
    ],
    relatedItems: ['irs', 'credit-risk', 'bond-valuation']
  },
  {
    id: 'forward-val',
    code: 'FWD',
    title: 'Форвардные контракты',
    category: 'swaps',
    path: '/valuation/forwards',
    description: 'Форвард — соглашение о покупке/продаже актива в будущем по фиксированной цене. Применяется для хеджирования и спекуляций.',
    formula: 'F = S × e^((r-q)T) или F = S × (1+r)^T / (1+q)^T',
    formulaExplanation: `Форвардная цена по типам активов:

• Акции без дивидендов:
  F = S × e^(rT)

• Акции с дивидендной доходностью q:
  F = S × e^((r-q)T)

• Валюта (Covered Interest Parity):
  F = S × (1+r_domestic)^T / (1+r_foreign)^T

• Товары (cost-of-carry):
  F = S × e^((r+c-y)T)
  c — storage cost, y — convenience yield

• Облигации:
  F = (S - PV(coupons)) × e^(rT)

Стоимость существующего форварда:
V = (F_new - K) × e^(-rT) × Notional`,
    features: [
      'Pricing всех типов форвардов',
      'Валютные форварды',
      'Commodity forwards',
      'Bond forwards',
      'Mark-to-market'
    ],
    howToUse: [
      'Выберите тип базового актива',
      'Введите spot price, rates, maturity',
      'Получите forward price',
      'Оцените стоимость существующей позиции'
    ],
    relatedItems: ['basis', 'forward-curve', 'irs']
  },
  {
    id: 'basis',
    code: 'BASIS',
    title: 'Базисный анализ',
    category: 'swaps',
    path: '/basis-analysis',
    description: 'Базис — разница между форвардной и спотовой ценой. Анализ базиса важен для понимания стоимости хеджирования и арбитражных возможностей.',
    formula: 'Basis = F - S = S × (e^((r-q)T) - 1)',
    formulaExplanation: `Компоненты базиса:

Basis = Forward Price - Spot Price

Для финансовых активов:
Basis ≈ S × (r - q) × T
• r — безрисковая ставка
• q — дивидендная доходность

Для товаров:
Basis = S × (r + c - y) × T
• c — storage costs
• y — convenience yield

Типы базиса:
• Contango: F > S (basis > 0) — норма для финансов
• Backwardation: F < S (basis < 0) — commodity markets

Annualized Basis:
Basis% = (F/S - 1) × (365/T)

Используется для:
• Оценки стоимости хеджа
• Cash-and-carry арбитража
• Rollover analysis`,
    features: [
      'Basis calculation',
      'Annualized carry cost',
      'Contango/Backwardation',
      'Historical basis tracking',
      'Roll analysis'
    ],
    howToUse: [
      'Выберите актив и форвардный срок',
      'Сравните basis для разных экспираций',
      'Оцените стоимость roll-over',
      'Идентифицируйте арбитражные возможности'
    ],
    relatedItems: ['forward-val', 'forward-curve', 'hedging']
  },

  // ═══════════════════════════════════════════════════════════════
  // РИСК-МЕНЕДЖМЕНТ - RISK MANAGEMENT
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'var',
    code: 'VAR',
    title: 'Value at Risk (VaR)',
    category: 'risk',
    path: '/greeks',
    description: 'VaR — максимальные потери портфеля за период с заданной вероятностью. Ключевая метрика рыночного риска.',
    formula: 'VaR_α = -μ + σ × Φ⁻¹(α)',
    formulaExplanation: `Методы расчёта VaR:

1. Параметрический (Variance-Covariance):
   VaR = Portfolio × σ × z_α × √T
   • z_α — квантиль нормального распределения
   • z_95% = 1.645, z_99% = 2.326
   • Предполагает нормальность returns

2. Исторический:
   VaR = -Percentile(returns, 1-α)
   • Берём α-квантиль реальных returns
   • Не требует допущений о распределении

3. Monte Carlo:
   • Генерируем N сценариев
   • VaR = -Percentile(simulated P&L, 1-α)

Пример: VaR 95% = $1M означает:
"С вероятностью 95% потери за день не превысят $1M"
или "5% дней потери будут больше $1M"`,
    features: [
      'Параметрический VaR',
      'Historical VaR',
      'Monte Carlo VaR',
      'Marginal VaR',
      'Component VaR'
    ],
    howToUse: [
      'Выберите уровень доверия (95%, 99%)',
      'Укажите временной горизонт (1d, 10d)',
      'Сравните методы расчёта',
      'Используйте Marginal VaR для оценки вклада позиций'
    ],
    relatedItems: ['cvar', 'stress', 'backtest']
  },
  {
    id: 'cvar',
    code: 'CVAR',
    title: 'Expected Shortfall (CVaR)',
    category: 'risk',
    path: '/greeks',
    description: 'Conditional VaR — ожидаемые потери при условии, что VaR превышен. Более консервативная метрика, учитывающая хвостовые риски.',
    formula: 'ES_α = E[Loss | Loss > VaR_α]',
    formulaExplanation: `Expected Shortfall (ES / CVaR):

Определение:
ES_α = -E[X | X < -VaR_α]
     = среднее потерь в худших (1-α)% случаев

Для нормального распределения:
ES_α = μ + σ × φ(z_α)/(1-α)
где φ — плотность N(0,1)

Свойства ES vs VaR:
• ES всегда ≥ VaR
• ES — когерентная мера риска
• ES учитывает форму хвоста
• Basel III требует ES 97.5% (≈ VaR 99%)

Пример:
VaR 95% = $1M, ES 95% = $1.4M означает:
"В худшие 5% дней средние потери = $1.4M"

Историческая формула:
ES = -Среднее(worst 5% returns)`,
    features: [
      'Параметрический ES',
      'Historical ES',
      'Сравнение с VaR',
      'Tail risk analysis',
      'Basel III compliance'
    ],
    howToUse: [
      'Рассчитайте VaR для выбранного уровня',
      'ES покажет "цену" превышения VaR',
      'Используйте для stress capital requirements'
    ],
    relatedItems: ['var', 'stress', 'extreme-value']
  },
  {
    id: 'stress',
    code: 'STRESS',
    title: 'Стресс-тестирование',
    category: 'risk',
    path: '/stress',
    description: 'Оценка поведения портфеля в экстремальных, но правдоподобных сценариях. Выявляет уязвимости, не видимые в VaR.',
    formula: 'ΔPortfolio = Σᵢ Sensitivityᵢ × Shockᵢ',
    formulaExplanation: `Типы стресс-тестов:

1. Исторические сценарии:
   • Кризис 2008 (Lehman)
   • COVID-19 (март 2020)
   • Рубль 2014

2. Гипотетические сценарии:
   • Параллельный сдвиг ставок +200bp
   • Падение акций -30%
   • Рост волатильности ×2

3. Sensitivity-based:
   ΔP ≈ Σ(∂P/∂xᵢ × Δxᵢ)

   Для портфеля облигаций:
   ΔP ≈ -Duration × ΔY + ½×Convexity×(ΔY)²

   Для опционов:
   ΔP ≈ Δ×ΔS + ½Γ×(ΔS)² + ν×Δσ

4. Reverse Stress Test:
   "Какой шок нужен для потери X?"`,
    features: [
      'Исторические сценарии',
      'Кастомные сценарии',
      'Shock multiplier',
      'P&L impact по активам',
      'Severity levels'
    ],
    howToUse: [
      'Выберите тип стресс-теста',
      'Настройте параметры шока',
      'Оцените impact на портфель',
      'Идентифицируйте уязвимые позиции'
    ],
    relatedItems: ['var', 'cvar', 'scenario']
  },
  {
    id: 'hedging',
    code: 'HEDGE',
    title: 'Хеджирование',
    category: 'risk',
    path: '/hedging-assistant',
    description: 'Построение хеджирующих позиций для снижения рисков портфеля. Включает delta-hedging, duration matching и regression-based hedging.',
    formula: 'Hedge Ratio = -Cov(Portfolio, Hedge) / Var(Hedge)',
    formulaExplanation: `Стратегии хеджирования:

1. Delta Hedging (опционы):
   Hedge = -Δ × Notional
   • Нейтрализует направленный риск
   • Требует частой ребалансировки

2. Duration Matching (облигации):
   Hedge_notional = -(DV01_portfolio / DV01_hedge)
   • Иммунизация от параллельного сдвига

3. Regression Hedging:
   Hedge Ratio = β = Cov(P,H)/Var(H)
   • Минимизирует дисперсию хеджированной позиции

4. Optimal Hedge (многофакторный):
   h* = argmin Var(Portfolio - h×Hedge)

Hedge Effectiveness:
R² = 1 - Var(hedged)/Var(unhedged)

Basis Risk:
Риск неполного хеджирования из-за
несовпадения hedge и underlying`,
    features: [
      'Delta hedging',
      'Duration matching',
      'Regression hedging',
      'Hedge ratio calculator',
      'Basis risk analysis'
    ],
    howToUse: [
      'Выберите позицию для хеджирования',
      'Определите тип риска (direction, duration, vol)',
      'Выберите hedge instrument',
      'Рассчитайте оптимальный hedge ratio'
    ],
    relatedItems: ['greeks', 'duration', 'basis']
  },
  {
    id: 'pnl-attr',
    code: 'PNLA',
    title: 'P&L Атрибуция',
    category: 'risk',
    path: '/analytics/pnl',
    description: 'Декомпозиция прибыли и убытков по источникам: рыночные движения, временной распад, волатильность, и другие факторы.',
    formula: 'ΔP&L = ΔS×Δ + ½(ΔS)²×Γ + Δσ×ν + Δt×Θ + residual',
    formulaExplanation: `Компоненты P&L Attribution:

1. Greeks-based (для опционов):
   • Market P&L = Δ × ΔS (направленное движение)
   • Gamma P&L = ½ × Γ × (ΔS)² (кривизна)
   • Vega P&L = ν × Δσ (волатильность)
   • Theta P&L = Θ × Δt (временной распад)
   • Residual = неучтённые эффекты

2. Factor-based (для акций):
   P&L = β_mkt × R_mkt + β_size × R_size + ...
   • Market factor
   • Size, Value, Momentum factors

3. Position-based:
   • P&L по каждой позиции
   • Contribution to total

Формула для облигаций:
ΔP ≈ -Dur×Δy + ½Conv×(Δy)² + Carry + Roll`,
    features: [
      'Greeks decomposition',
      'Factor attribution',
      'Position-level P&L',
      'Daily/Weekly/Monthly',
      'Contribution analysis'
    ],
    howToUse: [
      'Выберите период анализа',
      'Выберите метод атрибуции',
      'Изучите вклад каждого фактора',
      'Идентифицируйте источники прибыли/убытков'
    ],
    relatedItems: ['greeks', 'portfolio-options', 'var']
  },

  // ═══════════════════════════════════════════════════════════════
  // СИМУЛЯЦИИ - SIMULATIONS
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'monte-carlo',
    code: 'MC',
    title: 'Monte Carlo симуляция',
    category: 'simulation',
    path: '/monte-carlo',
    description: 'Стохастическое моделирование цен активов с использованием геометрического броуновского движения. Генерация тысяч сценариев для оценки рисков.',
    formula: 'S(t+Δt) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z]',
    formulaExplanation: `Geometric Brownian Motion (GBM):

Непрерывная форма:
dS = μSdt + σSdW

Дискретизация (Euler):
S(t+Δt) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z]
где Z ~ N(0,1)

Параметры:
• S₀ — начальная цена
• μ — дрифт (ожидаемая доходность)
• σ — волатильность
• T — горизонт симуляции
• N — количество путей
• dt — шаг по времени

Оценки из симуляции:
• E[S_T] ≈ (1/N) × Σ S_T^(i)
• VaR = Percentile(S_T, α)
• Prob(S_T > K) ≈ #{S_T > K} / N

Для опционов:
C ≈ e^(-rT) × (1/N) × Σ max(S_T^(i) - K, 0)`,
    features: [
      'GBM path generation',
      'Настраиваемые параметры',
      'VaR из симуляции',
      'Probability analysis',
      'Path visualization'
    ],
    howToUse: [
      'Введите S₀, μ, σ, T, N',
      'Запустите симуляцию',
      'Изучите распределение терминальных цен',
      'Оцените VaR и вероятности'
    ],
    relatedItems: ['var', 'bsm', 'heston']
  },
  {
    id: 'backtest',
    code: 'BACK',
    title: 'Бэктестинг стратегий',
    category: 'simulation',
    path: '/backtest',
    description: 'Тестирование торговых стратегий на исторических данных. Оценка CAGR, Sharpe Ratio, Maximum Drawdown и других метрик.',
    formula: 'Sharpe = (R_p - R_f) / σ_p',
    formulaExplanation: `Ключевые метрики бэктеста:

1. Total Return:
   R_total = (V_end - V_start) / V_start

2. CAGR (Compound Annual Growth Rate):
   CAGR = (V_end/V_start)^(1/years) - 1

3. Sharpe Ratio:
   Sharpe = (R_p - R_f) / σ_p
   • R_p — средняя доходность портфеля
   • R_f — безрисковая ставка
   • σ_p — волатильность портфеля
   • Sharpe > 1 — хорошо, > 2 — отлично

4. Maximum Drawdown:
   MDD = max[(Peak - Trough) / Peak]
   • Максимальная просадка от пика

5. Win Rate:
   Win Rate = # profitable trades / # total trades

6. Sortino Ratio (downside risk):
   Sortino = (R_p - R_f) / σ_downside`,
    features: [
      'Long/Short стратегии',
      'Equity curve',
      'Benchmark comparison',
      'Monthly returns table',
      'Risk-adjusted metrics'
    ],
    howToUse: [
      'Выберите стратегию',
      'Задайте исторический период',
      'Запустите бэктест',
      'Сравните с бенчмарком (S&P 500)',
      'Анализируйте метрики'
    ],
    relatedItems: ['sharpe', 'monte-carlo', 'portfolio']
  },
  {
    id: 'gbm',
    code: 'GBM',
    title: 'Геометрическое броуновское движение',
    category: 'simulation',
    description: 'Фундаментальная стохастическая модель для цен активов. Предполагает логнормальное распределение цен и постоянную волатильность.',
    formula: 'dS = μSdt + σSdW',
    formulaExplanation: `Геометрическое Броуновское Движение:

Стохастическое дифференциальное уравнение:
dS = μSdt + σSdW

Решение (Itô):
S(T) = S(0) × exp[(μ - σ²/2)T + σW(T)]

Свойства:
• S(T) > 0 всегда (цены неотрицательны)
• ln(S) ~ Normal (логнормальное распределение)
• E[S(T)] = S(0) × e^(μT)
• Var[S(T)] = S(0)² × e^(2μT) × (e^(σ²T) - 1)

Доходности:
R = ln(S(t+1)/S(t)) ~ N((μ-σ²/2)Δt, σ²Δt)

Ограничения модели:
• Постоянная волатильность (не реалистично)
• Непрерывные пути (нет скачков)
• Тонкие хвосты (недооценивает extreme events)`,
    features: [
      'Базовая модель цен',
      'Аналитические формулы',
      'Основа для BSM',
      'Простая калибровка'
    ],
    howToUse: [
      'Оцените μ и σ из исторических данных',
      'Используйте для симуляции цен',
      'Помните об ограничениях модели'
    ],
    relatedItems: ['monte-carlo', 'bsm', 'merton']
  },

  // ═══════════════════════════════════════════════════════════════
  // РЕЖИМЫ РЫНКА - MARKET REGIMES
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'hmm',
    code: 'HMM',
    title: 'Скрытые Марковские модели',
    category: 'regimes',
    path: '/regimes',
    description: 'Hidden Markov Model — статистическая модель для определения скрытых рыночных режимов (бычий/медвежий/боковой) по наблюдаемым доходностям.',
    formula: 'P(Xₜ|Sₜ) × P(Sₜ|Sₜ₋₁)',
    formulaExplanation: `Компоненты HMM:

1. Скрытые состояния (S):
   • Обычно 2-4 режима
   • Режим 1: низкая vol, позитивный дрифт (Bull)
   • Режим 2: высокая vol, негативный дрифт (Bear)

2. Матрица переходов (A):
   A[i,j] = P(Sₜ = j | Sₜ₋₁ = i)
   • Сумма строк = 1
   • Диагональ — persistence

3. Эмиссии (B):
   P(Xₜ | Sₜ = i) ~ N(μᵢ, σᵢ²)
   • Каждый режим имеет свои μ и σ

4. Алгоритмы:
   • Forward-Backward: P(S|X)
   • Viterbi: наиболее вероятный путь
   • Baum-Welch: оценка параметров (EM)

Стационарное распределение π:
π = π × A (собственный вектор)
π[i] — долгосрочная вероятность режима i`,
    features: [
      '2-5 режимов (auto-select)',
      'Матрица переходов',
      'Regime probability timeline',
      'Статистика по режимам',
      '2D/3D visualization'
    ],
    howToUse: [
      'Загрузите исторические данные',
      'Выберите количество режимов (или auto)',
      'Обучите модель',
      'Изучите характеристики режимов',
      'Прогнозируйте текущий режим'
    ],
    relatedItems: ['spectral', 'regime-stats', 'portfolio']
  },
  {
    id: 'spectral',
    code: 'SPEC',
    title: 'Спектральный анализ режимов',
    category: 'regimes',
    path: '/spectral-regime-analysis',
    description: 'Продвинутый анализ динамики режимов через спектральное разложение. Выявление полюсов, оценка стабильности и периодичности.',
    formula: 'G(z) = (zI - A)⁻¹',
    formulaExplanation: `Спектральный анализ матрицы переходов:

1. Собственные значения A:
   det(A - λI) = 0
   • λ₁ = 1 (Perron-Frobenius)
   • |λᵢ| < 1 для i > 1 (эргодичность)

2. Mixing Time:
   τ_mix ≈ 1 / (1 - |λ₂|)
   Время сходимости к стационарному распределению

3. Persistence:
   P_stay[i] = A[i,i]
   Expected duration = 1 / (1 - P_stay)

4. Передаточная функция:
   G(z) = (zI - A)⁻¹
   Полюса = 1/собственные значения

5. Stability Analysis:
   • Все |λ| < 1 → стабильная система
   • |λ| близко к 1 → медленное mixing

Мероморфное расширение для анализа
скрытой структуры переходов`,
    features: [
      'Eigenvalue analysis',
      'Pole detection',
      'Stability metrics',
      'Mixing time',
      'Complex plane visualization'
    ],
    howToUse: [
      'Обучите HMM на данных',
      'Запустите спектральный анализ',
      'Изучите собственные значения',
      'Оцените стабильность режимов'
    ],
    relatedItems: ['hmm', 'regime-stats']
  },

  // ═══════════════════════════════════════════════════════════════
  // ПОРТФЕЛЬ - PORTFOLIO
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'portfolio',
    code: 'PORT',
    title: 'Управление портфелем',
    category: 'portfolio',
    path: '/portfolio',
    description: 'Комплексный анализ инвестиционного портфеля: P&L, VaR, Sharpe Ratio, диверсификация, корреляции между активами.',
    formula: 'R_p = Σ wᵢ×Rᵢ, σ_p² = w\'Σw',
    formulaExplanation: `Метрики портфеля:

1. Доходность портфеля:
   R_p = Σ wᵢ × Rᵢ
   где wᵢ — вес актива i

2. Риск портфеля:
   σ_p² = Σᵢ Σⱼ wᵢwⱼσᵢσⱼρᵢⱼ = w'Σw
   Σ — ковариационная матрица

3. Sharpe Ratio:
   SR = (R_p - R_f) / σ_p

4. Diversification Ratio:
   DR = (Σ wᵢσᵢ) / σ_p
   DR > 1 означает выигрыш от диверсификации

5. Concentration (Herfindahl):
   HHI = Σ wᵢ²
   • HHI → 1: концентрация
   • HHI → 1/N: равномерное распределение

6. Correlation Contribution:
   Вклад корреляций в общий риск`,
    features: [
      'KPI dashboard',
      'Asset allocation chart',
      'Top-5 positions',
      'Correlation matrix',
      'PDF export'
    ],
    howToUse: [
      'Выберите портфель из списка',
      'Изучите KPI карточки',
      'Просмотрите аллокацию по активам',
      'Анализируйте корреляции',
      'Экспортируйте отчёт в PDF'
    ],
    relatedItems: ['optimization', 'var', 'sharpe']
  },
  {
    id: 'optimization',
    code: 'OPT',
    title: 'Оптимизация портфеля',
    category: 'portfolio',
    path: '/CCMVoptimization',
    description: 'Поиск оптимальных весов активов для максимизации доходности при заданном уровне риска (Markowitz Mean-Variance) или с использованием HJB-оптимизации.',
    formula: 'max w\'μ - (γ/2)×w\'Σw s.t. Σwᵢ=1',
    formulaExplanation: `Методы оптимизации:

1. Mean-Variance (Markowitz):
   min w'Σw (risk)
   s.t. w'μ ≥ R_target
        Σwᵢ = 1
        wᵢ ≥ 0 (no short)

   Или: max w'μ - (γ/2)×w'Σw
   γ — параметр риск-аверсии

2. Efficient Frontier:
   Множество портфелей с минимальным
   риском для каждого уровня доходности

3. HJB (Hamilton-Jacobi-Bellman):
   Динамическая оптимизация:
   max E[∫ U(c_t)dt + U(W_T)]

   w*(t) = (1/γ) × Σ⁻¹(μ - r)
   Оптимальные веса зависят от
   risk aversion и horizon

4. CCMV (Cluster-Constrained):
   Mean-Variance с ограничениями
   на группы активов`,
    features: [
      'Markowitz optimization',
      'HJB stochastic control',
      'Efficient Frontier',
      'Risk aversion tuning',
      'Constraint handling'
    ],
    howToUse: [
      'Выберите активы для оптимизации',
      'Задайте constraints (min/max weights)',
      'Выберите метод (MV или HJB)',
      'Найдите оптимальные веса',
      'Сравните с текущим портфелем'
    ],
    relatedItems: ['portfolio', 'sharpe', 'var']
  },
  {
    id: 'sharpe',
    code: 'SR',
    title: 'Sharpe Ratio',
    category: 'portfolio',
    description: 'Коэффициент Шарпа — отношение избыточной доходности к волатильности. Стандартная мера risk-adjusted performance.',
    formula: 'SR = (R_p - R_f) / σ_p',
    formulaExplanation: `Sharpe Ratio:

SR = (R_p - R_f) / σ_p

Где:
• R_p — средняя доходность портфеля
• R_f — безрисковая ставка
• σ_p — стандартное отклонение доходности

Интерпретация:
• SR < 0: портфель хуже безрисковой ставки
• SR = 0-1: умеренная risk-adjusted доходность
• SR = 1-2: хорошая performance
• SR > 2: отличная performance

Annualized Sharpe:
SR_annual = SR_daily × √252

Связанные метрики:
• Sortino Ratio = (R_p - R_f) / σ_downside
  (только downside volatility)

• Information Ratio = (R_p - R_b) / σ_tracking
  (относительно бенчмарка)

• Calmar Ratio = CAGR / Max Drawdown`,
    features: [
      'Расчёт Sharpe',
      'Annualization',
      'Rolling Sharpe',
      'Сравнение с бенчмарком',
      'Связанные метрики'
    ],
    howToUse: [
      'Загрузите returns портфеля',
      'Укажите безрисковую ставку',
      'Получите Sharpe Ratio',
      'Сравните с альтернативами'
    ],
    relatedItems: ['portfolio', 'backtest', 'optimization']
  },

  // ═══════════════════════════════════════════════════════════════
  // ТЕРМИНАЛ - TERMINAL
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'terminal',
    code: 'TERM',
    title: 'Дзета-Терминал',
    category: 'terminal',
    path: '/terminal',
    description: 'Продвинутый торговый терминал с потоковыми данными в реальном времени. Акции, криптовалюты, фьючерсы, опционы.',
    features: [
      'Real-time price updates',
      'Order book depth',
      'Multi-window layout',
      'Custom widgets',
      'Keyboard shortcuts (⌘K)'
    ],
    howToUse: [
      'Откройте терминал',
      'Используйте ⌘K для command palette',
      'Добавьте виджеты через Settings',
      'Создавайте multiple windows'
    ],
    relatedItems: ['czf', 'wave-sigma', 'liquidity']
  },
  {
    id: 'czf',
    code: 'CZF',
    title: 'Citadel Zeta Field',
    category: 'terminal',
    path: '/terminal',
    description: '3D визуализация гравитационного поля ликвидности. Частицы притягиваются к зонам высокой ликвидности.',
    features: [
      '3D particle system',
      'Gravity simulation',
      'Liquidity zones',
      'Real-time updates',
      'Interactive controls'
    ],
    relatedItems: ['terminal', 'liquidity', 'wave-sigma']
  },
  {
    id: 'wave-sigma',
    code: 'WSIG',
    title: 'WAVE_σ.9 Surface',
    category: 'terminal',
    path: '/terminal',
    description: 'Momentum-Volatility топологическая поверхность. 3D визуализация динамики momentum и волатильности рынка.',
    features: [
      '3D surface mesh',
      'Momentum dynamics',
      'Volatility mapping',
      'Regime coloring',
      'Trading simulation'
    ],
    relatedItems: ['terminal', 'volsurf', 'hmm']
  },

  // ═══════════════════════════════════════════════════════════════
  // ДОПОЛНИТЕЛЬНЫЕ МОДЕЛИ
  // ═══════════════════════════════════════════════════════════════
  {
    id: 'variance-gamma',
    code: 'VG',
    title: 'Variance Gamma процесс',
    category: 'options',
    description: 'Lévy-процесс с конечной вариацией и бесконечной активностью. Лучше описывает распределение доходностей с толстыми хвостами.',
    formula: 'X(t) = θG(t) + σW(G(t))',
    formulaExplanation: `Variance Gamma Process:

X(t) = θG(t) + σW(G(t))

Где:
• G(t) — Gamma process с параметром ν
• W(t) — Brownian motion
• θ — дрифт (skewness control)
• σ — волатильность
• ν — variance rate (kurtosis control)

Характеристическая функция:
φ(u) = (1 - iuθν + σ²u²ν/2)^(-t/ν)

Свойства:
• Конечные моменты всех порядков
• Толстые хвосты (kurtosis > 3)
• Асимметрия (skewness ≠ 0)
• Нет непрерывных путей (pure jump)

Pricing через FFT более эффективен`,
    features: [
      'Lévy process',
      'Fat tails',
      'Skewness control',
      'FFT pricing',
      'Calibration'
    ],
    relatedItems: ['merton', 'bsm', 'fft']
  },
  {
    id: 'bates',
    code: 'BATES',
    title: 'Модель Бейтса',
    category: 'options',
    description: 'Комбинация Heston (stochastic volatility) и Merton (jumps). Наиболее гибкая модель для ценообразования опционов.',
    formula: 'dS = (μ-λk)Sdt + √V·S·dW₁ + S(e^J-1)dN',
    formulaExplanation: `Модель Бейтса (SVJ):

dSₜ = (μ - λk)Sₜdt + √Vₜ·Sₜ·dW₁ + Sₜ(e^J - 1)dNₜ
dVₜ = κ(θ - Vₜ)dt + ξ√Vₜ·dW₂

Компоненты:
• Stochastic Volatility (от Heston):
  - κ: mean reversion speed
  - θ: long-run variance
  - ξ: vol of vol
  - ρ: correlation

• Jumps (от Merton):
  - λ: jump intensity
  - μⱼ: mean jump size
  - σⱼ: jump size volatility

Преимущества:
• Улыбка волатильности
• Толстые хвосты
• Asymmetry (leverage + jumps)
• Flexible calibration`,
    features: [
      'Stochastic volatility',
      'Jump diffusion',
      '8 parameters',
      'Most flexible model',
      'Calibration intensive'
    ],
    relatedItems: ['heston', 'merton', 'volsurf']
  }
]

// Helper functions
export const getCategoryItems = (categoryId: string): KnowledgeItem[] => {
  return items.filter(item => item.category === categoryId)
}

export const getCategoryById = (categoryId: string): Category | undefined => {
  return categories.find(cat => cat.id === categoryId)
}

export const searchItems = (query: string): KnowledgeItem[] => {
  const q = query.toLowerCase()
  return items.filter(item =>
    item.title.toLowerCase().includes(q) ||
    item.code.toLowerCase().includes(q) ||
    item.description.toLowerCase().includes(q) ||
    item.formula?.toLowerCase().includes(q)
  )
}

export const getRelatedItems = (itemId: string): KnowledgeItem[] => {
  const item = items.find(i => i.id === itemId)
  if (!item?.relatedItems) return []
  return items.filter(i => item.relatedItems?.includes(i.id))
}
