import type { KnowledgeItem } from './types'

export const terminalItems: KnowledgeItem[] = [
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
      'Keyboard shortcuts (\u2318K)'
    ],
    howToUse: [
      'Откройте терминал',
      'Используйте \u2318K для command palette',
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
    title: 'WAVE_\u03c3.9 Surface',
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
  }
]
