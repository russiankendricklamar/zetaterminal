import type { KnowledgeItem } from './types'

export const swapsItems: KnowledgeItem[] = [
  {
    id: 'irs',
    code: 'IRS',
    title: 'Процентные свопы (IRS)',
    category: 'swaps',
    path: '/valuation/swaps',
    description: 'Interest Rate Swap \u2014 контракт обмена фиксированных платежей на плавающие. Используется для хеджирования процентного риска.',
    formula: 'NPV = PV(Fixed Leg) - PV(Floating Leg)',
    formulaExplanation: `Структура IRS:

\u2022 Fixed Leg: платим/получаем фиксированную ставку K
  PV_fixed = K \u00d7 \u03a3[\u0394t\u1d62 \u00d7 DF(t\u1d62)] \u00d7 Notional

\u2022 Floating Leg: получаем/платим плавающую ставку
  PV_float = \u03a3[F\u1d62 \u00d7 \u0394t\u1d62 \u00d7 DF(t\u1d62)] \u00d7 Notional
  где F\u1d62 \u2014 forward rate

Par Swap Rate (справедливая фикс. ставка):
K* = [1 - DF(T)] / \u03a3[\u0394t\u1d62 \u00d7 DF(t\u1d62)]

DV01 свопа:
DV01 \u2248 \u03a3[\u0394t\u1d62 \u00d7 DF(t\u1d62)] \u00d7 Notional \u00d7 0.0001

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
    description: 'Credit Default Swap \u2014 страховка от дефолта. Покупатель платит премию, продавец компенсирует потери при дефолте.',
    formula: 'Spread \u00d7 RPV01 = (1-R) \u00d7 \u03a3[q(t\u1d62)\u00b7DF(t\u1d62)]',
    formulaExplanation: `Компоненты CDS:

\u2022 Premium Leg (платежи покупателя):
  PV_premium = Spread \u00d7 RPV01
  RPV01 = \u03a3[\u0394t\u1d62 \u00d7 DF(t\u1d62) \u00d7 Q(t\u1d62)]
  Q(t\u1d62) \u2014 вероятность выживания до t\u1d62

\u2022 Protection Leg (выплата при дефолте):
  PV_protection = (1-R) \u00d7 \u03a3[q(t\u1d62) \u00d7 DF(t\u1d62)]
  q(t\u1d62) = Q(t\u1d62\u208b\u2081) - Q(t\u1d62) \u2014 вероятность дефолта
  R \u2014 Recovery Rate (обычно 40%)

Par Spread (справедливый spread):
S* = (1-R) \u00d7 \u03a3[q(t\u1d62)\u00b7DF(t\u1d62)] / RPV01

Hazard Rate (интенсивность дефолта):
\u03bb \u2248 Spread / (1-R)`,
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
    description: 'Форвард \u2014 соглашение о покупке/продаже актива в будущем по фиксированной цене. Применяется для хеджирования и спекуляций.',
    formula: 'F = S \u00d7 e^((r-q)T) или F = S \u00d7 (1+r)^T / (1+q)^T',
    formulaExplanation: `Форвардная цена по типам активов:

\u2022 Акции без дивидендов:
  F = S \u00d7 e^(rT)

\u2022 Акции с дивидендной доходностью q:
  F = S \u00d7 e^((r-q)T)

\u2022 Валюта (Covered Interest Parity):
  F = S \u00d7 (1+r_domestic)^T / (1+r_foreign)^T

\u2022 Товары (cost-of-carry):
  F = S \u00d7 e^((r+c-y)T)
  c \u2014 storage cost, y \u2014 convenience yield

\u2022 Облигации:
  F = (S - PV(coupons)) \u00d7 e^(rT)

Стоимость существующего форварда:
V = (F_new - K) \u00d7 e^(-rT) \u00d7 Notional`,
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
    description: 'Базис \u2014 разница между форвардной и спотовой ценой. Анализ базиса важен для понимания стоимости хеджирования и арбитражных возможностей.',
    formula: 'Basis = F - S = S \u00d7 (e^((r-q)T) - 1)',
    formulaExplanation: `Компоненты базиса:

Basis = Forward Price - Spot Price

Для финансовых активов:
Basis \u2248 S \u00d7 (r - q) \u00d7 T
\u2022 r \u2014 безрисковая ставка
\u2022 q \u2014 дивидендная доходность

Для товаров:
Basis = S \u00d7 (r + c - y) \u00d7 T
\u2022 c \u2014 storage costs
\u2022 y \u2014 convenience yield

Типы базиса:
\u2022 Contango: F > S (basis > 0) \u2014 норма для финансов
\u2022 Backwardation: F < S (basis < 0) \u2014 commodity markets

Annualized Basis:
Basis% = (F/S - 1) \u00d7 (365/T)

Используется для:
\u2022 Оценки стоимости хеджа
\u2022 Cash-and-carry арбитража
\u2022 Rollover analysis`,
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
  }
]
