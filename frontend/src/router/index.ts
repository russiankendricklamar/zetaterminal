// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/components/Layout/MainLayout.vue'

import Home from '@/pages/Home.vue'
import MainDashboard from '@/pages/MainDashboard.vue'
import Portfolio from '@/pages/Portfolio.vue'
import MonteCarlo from '@/pages/MonteCarlo.vue'
import GreekParameters from '@/pages/GreekParameters.vue'
import StressTesting from '@/pages/StressTesting.vue'
import Backtesting from '@/pages/Backtesting.vue'
import Reports from '@/pages/Reports.vue'
import Settings from '@/pages/Settings.vue'
import RegimeAnalysis from '@/pages/RegimeAnalysis.vue'
import RegimeDetails from '@/pages/RegimeDetails.vue'
import YieldAnalysis from '@/pages/YieldAnalysis.vue'
import NotFound from '@/pages/NotFound.vue'

const routes = [
  // HOME — без MainLayout, чистый фуллскрин
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Главная', icon: '🏠', bare: true }
  },

  // Остальное — под MainLayout (с сайдбаром и хедером)
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: 'dashboard',
        component: MainDashboard,
        name: 'Сводный дашборд по портфельному анализу',
        meta: { title: 'Дашборд', icon: '📊' }
      },
      {
        path: 'portfolio',
        component: Portfolio,
        name: 'Портфель',
        meta: { title: 'Портфель', icon: '💼' }
      },
      {
        path: 'monte-carlo',
        component: MonteCarlo,
        name: 'Монте-Карло',
        meta: { title: 'Monte Carlo', icon: '🎲' }
      },
      {
        path: 'greeks',
        component: GreekParameters,
        name: 'Риск-метрики',
        meta: { title: 'Греческие параметры', icon: '🎯', badge: '3' }
      },
      {
        path: 'stress',
        component: StressTesting,
        name: 'Стресс-тестирование',
        meta: { title: 'Стресс-тестирование', icon: '⚡' },
        alias: 'stress-testing'
      },
      {
        path: 'backtest',
        component: Backtesting,
        name: 'Бэктестинг',
        meta: { title: 'Бэктестинг', icon: '📉' }
      },
      {
        path: 'reports',
        component: Reports,
        name: 'Отчёты',
        meta: { title: 'Отчёты', icon: '📋' }
      },
      {
        path: 'settings',
        component: Settings,
        name: 'Настройки',
        meta: { title: 'Настройки', icon: '⚙️' },
        alias: 'parameters'
      },
      {
        path: 'regimes',
        component: RegimeAnalysis,
        name: 'Анализ режимов',
        meta: { title: 'Рыночные режимы', icon: '🌊' }
      },
      {
        path: 'fixed-income',
        component: YieldAnalysis,
        name: 'Доходности облигаций',
        meta: { title: 'Доходность облигаций', icon: '📈' }
      },
      {
        path: 'regime-details',
        component: RegimeDetails,
        name: 'Режимная аналитика',
        meta: { title: 'HMM Аналитика', icon: '🔬' }
      },
      // pricing‑маршруты, если уже добавил
      // {
      //   path: 'pricing/options',
      //   component: () => import('@/pages/OptionPricing.vue'),
      //   name: 'OptionPricing',
      //   meta: { title: 'Оценка опционов', icon: 'ƒ' }
      // },
      // {
      //   path: 'pricing/swaps',
      //   component: () => import('@/pages/SwapValuation.vue'),
      //   name: 'SwapValuation',
      //   meta: { title: 'Оценка свопов', icon: '⇄' }
      // },
      // {
      //   path: 'pricing/surface',
      //   component: () => import('@/pages/VolSurface.vue'),
      //   name: 'VolSurface',
      //   meta: { title: 'Поверхность волатильности', icon: '🌋' }
      // },
      // {
      //   path: 'pricing/bonds',
      //   component: () => import('@/pages/BondPricing.vue'),
      //   name: 'BondPricing',
      //   meta: { title: 'Справедливая стоимость облигаций', icon: '💰' }
      // },
      // {
      //   path: 'pricing/forwards',
      //   component: () => import('@/pages/ForwardPricing.vue'),
      //   name: 'ForwardPricing',
      //   meta: { title: 'Справедливая цена форвардов', icon: '↝' }
      // },
      // {
      //   path: 'pricing/margin',
      //   component: () => import('@/pages/DerivativesMargin.vue'),
      //   name: 'DerivativesMargin',
      //   meta: { title: 'Маржинальная позиция деривативов', icon: '⚖️' }
      // },
    ]
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const title = (to.meta?.title as string) || 'QuantPro'
  document.title = `${title} | Risk Management`
  next()
})

export default router
