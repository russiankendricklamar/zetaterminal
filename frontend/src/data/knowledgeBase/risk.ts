import type { KnowledgeItem } from './types'

export const riskItems: KnowledgeItem[] = [
  {
    id: 'var',
    code: 'VAR',
    title: 'Value at Risk (VaR)',
    category: 'risk',
    path: '/greeks',
    description: 'VaR \u2014 максимальные потери портфеля за период с заданной вероятностью. Ключевая метрика рыночного риска.',
    formula: 'VaR_\u03b1 = -\u03bc + \u03c3 \u00d7 \u03a6\u207b\u00b9(\u03b1)',
    formulaExplanation: `Методы расчёта VaR:

1. Параметрический (Variance-Covariance):
   VaR = Portfolio \u00d7 \u03c3 \u00d7 z_\u03b1 \u00d7 \u221aT
   \u2022 z_\u03b1 \u2014 квантиль нормального распределения
   \u2022 z_95% = 1.645, z_99% = 2.326
   \u2022 Предполагает нормальность returns

2. Исторический:
   VaR = -Percentile(returns, 1-\u03b1)
   \u2022 Берём \u03b1-квантиль реальных returns
   \u2022 Не требует допущений о распределении

3. Monte Carlo:
   \u2022 Генерируем N сценариев
   \u2022 VaR = -Percentile(simulated P&L, 1-\u03b1)

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
    description: 'Conditional VaR \u2014 ожидаемые потери при условии, что VaR превышен. Более консервативная метрика, учитывающая хвостовые риски.',
    formula: 'ES_\u03b1 = E[Loss | Loss > VaR_\u03b1]',
    formulaExplanation: `Expected Shortfall (ES / CVaR):

Определение:
ES_\u03b1 = -E[X | X < -VaR_\u03b1]
     = среднее потерь в худших (1-\u03b1)% случаев

Для нормального распределения:
ES_\u03b1 = \u03bc + \u03c3 \u00d7 \u03c6(z_\u03b1)/(1-\u03b1)
где \u03c6 \u2014 плотность N(0,1)

Свойства ES vs VaR:
\u2022 ES всегда \u2265 VaR
\u2022 ES \u2014 когерентная мера риска
\u2022 ES учитывает форму хвоста
\u2022 Basel III требует ES 97.5% (\u2248 VaR 99%)

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
    formula: '\u0394Portfolio = \u03a3\u1d62 Sensitivity\u1d62 \u00d7 Shock\u1d62',
    formulaExplanation: `Типы стресс-тестов:

1. Исторические сценарии:
   \u2022 Кризис 2008 (Lehman)
   \u2022 COVID-19 (март 2020)
   \u2022 Рубль 2014

2. Гипотетические сценарии:
   \u2022 Параллельный сдвиг ставок +200bp
   \u2022 Падение акций -30%
   \u2022 Рост волатильности \u00d72

3. Sensitivity-based:
   \u0394P \u2248 \u03a3(\u2202P/\u2202x\u1d62 \u00d7 \u0394x\u1d62)

   Для портфеля облигаций:
   \u0394P \u2248 -Duration \u00d7 \u0394Y + \u00bd\u00d7Convexity\u00d7(\u0394Y)\u00b2

   Для опционов:
   \u0394P \u2248 \u0394\u00d7\u0394S + \u00bd\u0393\u00d7(\u0394S)\u00b2 + \u03bd\u00d7\u0394\u03c3

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
   Hedge = -\u0394 \u00d7 Notional
   \u2022 Нейтрализует направленный риск
   \u2022 Требует частой ребалансировки

2. Duration Matching (облигации):
   Hedge_notional = -(DV01_portfolio / DV01_hedge)
   \u2022 Иммунизация от параллельного сдвига

3. Regression Hedging:
   Hedge Ratio = \u03b2 = Cov(P,H)/Var(H)
   \u2022 Минимизирует дисперсию хеджированной позиции

4. Optimal Hedge (многофакторный):
   h* = argmin Var(Portfolio - h\u00d7Hedge)

Hedge Effectiveness:
R\u00b2 = 1 - Var(hedged)/Var(unhedged)

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
    formula: '\u0394P&L = \u0394S\u00d7\u0394 + \u00bd(\u0394S)\u00b2\u00d7\u0393 + \u0394\u03c3\u00d7\u03bd + \u0394t\u00d7\u0398 + residual',
    formulaExplanation: `Компоненты P&L Attribution:

1. Greeks-based (для опционов):
   \u2022 Market P&L = \u0394 \u00d7 \u0394S (направленное движение)
   \u2022 Gamma P&L = \u00bd \u00d7 \u0393 \u00d7 (\u0394S)\u00b2 (кривизна)
   \u2022 Vega P&L = \u03bd \u00d7 \u0394\u03c3 (волатильность)
   \u2022 Theta P&L = \u0398 \u00d7 \u0394t (временной распад)
   \u2022 Residual = неучтённые эффекты

2. Factor-based (для акций):
   P&L = \u03b2_mkt \u00d7 R_mkt + \u03b2_size \u00d7 R_size + ...
   \u2022 Market factor
   \u2022 Size, Value, Momentum factors

3. Position-based:
   \u2022 P&L по каждой позиции
   \u2022 Contribution to total

Формула для облигаций:
\u0394P \u2248 -Dur\u00d7\u0394y + \u00bdConv\u00d7(\u0394y)\u00b2 + Carry + Roll`,
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
  }
]
