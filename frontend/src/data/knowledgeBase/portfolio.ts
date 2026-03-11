import type { KnowledgeItem } from './types'

export const portfolioItems: KnowledgeItem[] = [
  {
    id: 'portfolio',
    code: 'PORT',
    title: 'Управление портфелем',
    category: 'portfolio',
    path: '/portfolio',
    description: 'Комплексный анализ инвестиционного портфеля: P&L, VaR, Sharpe Ratio, диверсификация, корреляции между активами.',
    formula: 'R_p = \u03a3 w\u1d62\u00d7R\u1d62, \u03c3_p\u00b2 = w\'\u03a3w',
    formulaExplanation: `Метрики портфеля:

1. Доходность портфеля:
   R_p = \u03a3 w\u1d62 \u00d7 R\u1d62
   где w\u1d62 \u2014 вес актива i

2. Риск портфеля:
   \u03c3_p\u00b2 = \u03a3\u1d62 \u03a3\u2c7c w\u1d62w\u2c7c\u03c3\u1d62\u03c3\u2c7c\u03c1\u1d62\u2c7c = w'\u03a3w
   \u03a3 \u2014 ковариационная матрица

3. Sharpe Ratio:
   SR = (R_p - R_f) / \u03c3_p

4. Diversification Ratio:
   DR = (\u03a3 w\u1d62\u03c3\u1d62) / \u03c3_p
   DR > 1 означает выигрыш от диверсификации

5. Concentration (Herfindahl):
   HHI = \u03a3 w\u1d62\u00b2
   \u2022 HHI \u2192 1: концентрация
   \u2022 HHI \u2192 1/N: равномерное распределение

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
    formula: 'max w\'\u03bc - (\u03b3/2)\u00d7w\'\u03a3w s.t. \u03a3w\u1d62=1',
    formulaExplanation: `Методы оптимизации:

1. Mean-Variance (Markowitz):
   min w'\u03a3w (risk)
   s.t. w'\u03bc \u2265 R_target
        \u03a3w\u1d62 = 1
        w\u1d62 \u2265 0 (no short)

   Или: max w'\u03bc - (\u03b3/2)\u00d7w'\u03a3w
   \u03b3 \u2014 параметр риск-аверсии

2. Efficient Frontier:
   Множество портфелей с минимальным
   риском для каждого уровня доходности

3. HJB (Hamilton-Jacobi-Bellman):
   Динамическая оптимизация:
   max E[\u222b U(c_t)dt + U(W_T)]

   w*(t) = (1/\u03b3) \u00d7 \u03a3\u207b\u00b9(\u03bc - r)
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
    description: 'Коэффициент Шарпа \u2014 отношение избыточной доходности к волатильности. Стандартная мера risk-adjusted performance.',
    formula: 'SR = (R_p - R_f) / \u03c3_p',
    formulaExplanation: `Sharpe Ratio:

SR = (R_p - R_f) / \u03c3_p

Где:
\u2022 R_p \u2014 средняя доходность портфеля
\u2022 R_f \u2014 безрисковая ставка
\u2022 \u03c3_p \u2014 стандартное отклонение доходности

Интерпретация:
\u2022 SR < 0: портфель хуже безрисковой ставки
\u2022 SR = 0-1: умеренная risk-adjusted доходность
\u2022 SR = 1-2: хорошая performance
\u2022 SR > 2: отличная performance

Annualized Sharpe:
SR_annual = SR_daily \u00d7 \u221a252

Связанные метрики:
\u2022 Sortino Ratio = (R_p - R_f) / \u03c3_downside
  (только downside volatility)

\u2022 Information Ratio = (R_p - R_b) / \u03c3_tracking
  (относительно бенчмарка)

\u2022 Calmar Ratio = CAGR / Max Drawdown`,
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
  }
]
