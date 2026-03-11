import type { KnowledgeItem } from './types'

export const simulationItems: KnowledgeItem[] = [
  {
    id: 'monte-carlo',
    code: 'MC',
    title: 'Monte Carlo симуляция',
    category: 'simulation',
    path: '/monte-carlo',
    description: 'Стохастическое моделирование цен активов с использованием геометрического броуновского движения. Генерация тысяч сценариев для оценки рисков.',
    formula: 'S(t+\u0394t) = S(t) \u00d7 exp[(\u03bc - \u03c3\u00b2/2)\u0394t + \u03c3\u221a\u0394t \u00d7 Z]',
    formulaExplanation: `Geometric Brownian Motion (GBM):

Непрерывная форма:
dS = \u03bcSdt + \u03c3SdW

Дискретизация (Euler):
S(t+\u0394t) = S(t) \u00d7 exp[(\u03bc - \u03c3\u00b2/2)\u0394t + \u03c3\u221a\u0394t \u00d7 Z]
где Z ~ N(0,1)

Параметры:
\u2022 S\u2080 \u2014 начальная цена
\u2022 \u03bc \u2014 дрифт (ожидаемая доходность)
\u2022 \u03c3 \u2014 волатильность
\u2022 T \u2014 горизонт симуляции
\u2022 N \u2014 количество путей
\u2022 dt \u2014 шаг по времени

Оценки из симуляции:
\u2022 E[S_T] \u2248 (1/N) \u00d7 \u03a3 S_T^(i)
\u2022 VaR = Percentile(S_T, \u03b1)
\u2022 Prob(S_T > K) \u2248 #{S_T > K} / N

Для опционов:
C \u2248 e^(-rT) \u00d7 (1/N) \u00d7 \u03a3 max(S_T^(i) - K, 0)`,
    features: [
      'GBM path generation',
      'Настраиваемые параметры',
      'VaR из симуляции',
      'Probability analysis',
      'Path visualization'
    ],
    howToUse: [
      'Введите S\u2080, \u03bc, \u03c3, T, N',
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
    formula: 'Sharpe = (R_p - R_f) / \u03c3_p',
    formulaExplanation: `Ключевые метрики бэктеста:

1. Total Return:
   R_total = (V_end - V_start) / V_start

2. CAGR (Compound Annual Growth Rate):
   CAGR = (V_end/V_start)^(1/years) - 1

3. Sharpe Ratio:
   Sharpe = (R_p - R_f) / \u03c3_p
   \u2022 R_p \u2014 средняя доходность портфеля
   \u2022 R_f \u2014 безрисковая ставка
   \u2022 \u03c3_p \u2014 волатильность портфеля
   \u2022 Sharpe > 1 \u2014 хорошо, > 2 \u2014 отлично

4. Maximum Drawdown:
   MDD = max[(Peak - Trough) / Peak]
   \u2022 Максимальная просадка от пика

5. Win Rate:
   Win Rate = # profitable trades / # total trades

6. Sortino Ratio (downside risk):
   Sortino = (R_p - R_f) / \u03c3_downside`,
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
    formula: 'dS = \u03bcSdt + \u03c3SdW',
    formulaExplanation: `Геометрическое Броуновское Движение:

Стохастическое дифференциальное уравнение:
dS = \u03bcSdt + \u03c3SdW

Решение (It\u00f4):
S(T) = S(0) \u00d7 exp[(\u03bc - \u03c3\u00b2/2)T + \u03c3W(T)]

Свойства:
\u2022 S(T) > 0 всегда (цены неотрицательны)
\u2022 ln(S) ~ Normal (логнормальное распределение)
\u2022 E[S(T)] = S(0) \u00d7 e^(\u03bcT)
\u2022 Var[S(T)] = S(0)\u00b2 \u00d7 e^(2\u03bcT) \u00d7 (e^(\u03c3\u00b2T) - 1)

Доходности:
R = ln(S(t+1)/S(t)) ~ N((\u03bc-\u03c3\u00b2/2)\u0394t, \u03c3\u00b2\u0394t)

Ограничения модели:
\u2022 Постоянная волатильность (не реалистично)
\u2022 Непрерывные пути (нет скачков)
\u2022 Тонкие хвосты (недооценивает extreme events)`,
    features: [
      'Базовая модель цен',
      'Аналитические формулы',
      'Основа для BSM',
      'Простая калибровка'
    ],
    howToUse: [
      'Оцените \u03bc и \u03c3 из исторических данных',
      'Используйте для симуляции цен',
      'Помните об ограничениях модели'
    ],
    relatedItems: ['monte-carlo', 'bsm', 'merton']
  }
]
