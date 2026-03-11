import type { KnowledgeItem } from './types'

export const regimesItems: KnowledgeItem[] = [
  {
    id: 'hmm',
    code: 'HMM',
    title: 'Скрытые Марковские модели',
    category: 'regimes',
    path: '/regimes',
    description: 'Hidden Markov Model \u2014 статистическая модель для определения скрытых рыночных режимов (бычий/медвежий/боковой) по наблюдаемым доходностям.',
    formula: 'P(X\u209c|S\u209c) \u00d7 P(S\u209c|S\u209c\u208b\u2081)',
    formulaExplanation: `Компоненты HMM:

1. Скрытые состояния (S):
   \u2022 Обычно 2-4 режима
   \u2022 Режим 1: низкая vol, позитивный дрифт (Bull)
   \u2022 Режим 2: высокая vol, негативный дрифт (Bear)

2. Матрица переходов (A):
   A[i,j] = P(S\u209c = j | S\u209c\u208b\u2081 = i)
   \u2022 Сумма строк = 1
   \u2022 Диагональ \u2014 persistence

3. Эмиссии (B):
   P(X\u209c | S\u209c = i) ~ N(\u03bc\u1d62, \u03c3\u1d62\u00b2)
   \u2022 Каждый режим имеет свои \u03bc и \u03c3

4. Алгоритмы:
   \u2022 Forward-Backward: P(S|X)
   \u2022 Viterbi: наиболее вероятный путь
   \u2022 Baum-Welch: оценка параметров (EM)

Стационарное распределение \u03c0:
\u03c0 = \u03c0 \u00d7 A (собственный вектор)
\u03c0[i] \u2014 долгосрочная вероятность режима i`,
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
    formula: 'G(z) = (zI - A)\u207b\u00b9',
    formulaExplanation: `Спектральный анализ матрицы переходов:

1. Собственные значения A:
   det(A - \u03bbI) = 0
   \u2022 \u03bb\u2081 = 1 (Perron-Frobenius)
   \u2022 |\u03bb\u1d62| < 1 для i > 1 (эргодичность)

2. Mixing Time:
   \u03c4_mix \u2248 1 / (1 - |\u03bb\u2082|)
   Время сходимости к стационарному распределению

3. Persistence:
   P_stay[i] = A[i,i]
   Expected duration = 1 / (1 - P_stay)

4. Передаточная функция:
   G(z) = (zI - A)\u207b\u00b9
   Полюса = 1/собственные значения

5. Stability Analysis:
   \u2022 Все |\u03bb| < 1 \u2192 стабильная система
   \u2022 |\u03bb| близко к 1 \u2192 медленное mixing

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
  }
]
