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
import BondValuation from '@/pages/BondValuation.vue'
import ZCYCViewer from '@/pages/ZCYCViewer.vue'
import BondReport from '@/pages/BondReport.vue'
import VanilaBondReport from '@/pages/VanilaBondReport.vue'
import NotFound from '@/pages/NotFound.vue'
import OptionPricing from '@/pages/OptionPricing.vue'
import OptionModelsComparison from '@/pages/OptionModelsComparison.vue'
import OptionGreeksAnalyzer from '@/pages/OptionGreeksAnalyzer.vue'
import OptionPortfolio from '@/pages/OptionPortfolio.vue'
import StressSwapsView from '@/pages/StressTestingSwap.vue'
import SwapGreeksDashboard from '@/pages/SwapGreeksDashboard.vue'
import SwapValuation from '@/pages/SwapValuation.vue'
import PnLAttribution from '@/pages/PnLAttribution.vue'
import HedgingAssistant from '@/pages/HedgingAssistant.vue'
import ForwardValuation from '@/pages/ForwardValuation.vue'
import ForwardCurveBuilder from '@/pages/ForwardCurveBuilder.vue'
import ForwardsGreeksDashboard from '@/pages/ForwardsGreeksDashboard.vue'
import BasisAnalysis from '@/pages/BasisAnalysis.vue'
import MarginFinancing from '@/pages/MarginFinancing.vue'
import ArbitrageScanner from '@/pages/ArbitrageScanner.vue'
import VolatilitySurface from '@/pages/VolatilitySurface.vue'
import CCMVOptimizationPage from '@/pages/CCMVOptimization.vue'
import DocumentationPage from '@/pages/DocumentationPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Главная', icon: '🏠', bare: true }
  },
  {
    path: '/docs',
    name: 'Documentation',
    component: DocumentationPage,
    meta: { title: 'Документация' }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: 'dashboard',
        component: MainDashboard,
        name: 'Dashboard',
        meta: { title: 'Дашборд', icon: '📊' }
      },
      {
        path: 'portfolio',
        component: Portfolio,
        name: 'Portfolio',
        meta: { title: 'Портфель', icon: '💼' }
      },
      {
        path: 'monte-carlo',
        component: MonteCarlo,
        name: 'MonteCarlo',
        meta: { title: 'Monte Carlo', icon: '🎲' }
      },
      {
        path: 'greeks',
        component: GreekParameters,
        name: 'GreekParameters',
        meta: { title: 'Греческие параметры', icon: '🎯', badge: '3' }
      },
      {
        path: 'stress',
        component: StressTesting,
        name: 'StressTesting',
        meta: { title: 'Стресс-тестирование', icon: '⚡' },
        alias: 'stress-testing'
      },
      {
        path: 'backtest',
        component: Backtesting,
        name: 'Backtesting',
        meta: { title: 'Бэктестинг', icon: '📉' }
      },
      {
        path: 'reports',
        component: Reports,
        name: 'Reports',
        meta: { title: 'Отчёты', icon: '📋' }
      },
      {
        path: 'settings',
        component: Settings,
        name: 'Settings',
        meta: { title: 'Настройки', icon: '⚙️' },
        alias: 'parameters'
      },
      {
        path: 'regimes',
        component: RegimeAnalysis,
        name: 'RegimeAnalysis',
        meta: { title: 'Рыночные режимы', icon: '🌊' }
      },
      {
        path: 'fixed-income',
        component: YieldAnalysis,
        name: 'YieldAnalysis',
        meta: { title: 'Доходность облигаций', icon: '📈' }
      },
      {
        path: 'regime-details',
        component: RegimeDetails,
        name: 'RegimeDetails',
        meta: { title: 'HMM Аналитика', icon: '🔬' }
      },
      {
        path: 'bond-valuation',
        component: BondValuation,
        name: 'BondValuation',
        meta: { title: 'Справедливая стоимость облигаций', icon: '💰' }
      },
      {
        path: 'zcyc-viewer',
        component: ZCYCViewer,
        name: 'ZCYCViewer',
        meta: { title: 'Кривая бескупонных доходностей', icon: '📈' }
      },
      {
        path: 'bond-report',
        component: BondReport,
        name: 'BondReport',
        meta: { title: 'Отчет об оценке облигаций', icon: '📄' }
      },
      {
        path: 'vanila-bond-report/:isin?',
        component: VanilaBondReport,
        name: 'VanilaBondReport',
        meta: { title: 'Vanila Bond Report', icon: '📊' }
      },
      {
        path: 'pricing/options',
        component: OptionPricing,
        name: 'OptionPricing',
        meta: { title: 'Справедливая стоимость опционов', icon: 'ƒ' }
      },
      {
        path: 'pricing/options/models',
        component: OptionModelsComparison,
        name: 'OptionModelsComparison',
        meta: { title: 'Сравнение моделей ценообразования', icon: 'ƒ' }
      },
      {
        path: 'pricing/options/greeks',
        component: OptionGreeksAnalyzer,
        name: 'OptionGreeksAnalyzer',
        meta: { title: 'Анализ чувствительности (Greeks)', icon: 'ƒ' }
      },
      {
        path: 'pricing/options/portfolio',
        component: OptionPortfolio,
        name: 'OptionPortfolio',
        meta: { title: 'Портфель опционов', icon: 'ƒ' }
      },
      {
        path: 'stress/swaps',
        component: StressSwapsView,
        name: 'stress-swaps',
        meta: { title: 'Стресс-тестирование Свопов', icon: 'ƒ' }
      },
      {
        path: 'swap-greeks',
        component: SwapGreeksDashboard,
        name: 'SwapGreeksDashboard',
        meta: { title: 'Греки СВОПов', icon: '⚡' }
      },
      {
        path: 'valuation/swaps',
        component: SwapValuation,
        name: 'SwapValuation',
        meta: { title: 'Оценка справедливой стоимости СВОПов', icon: '💰' }
      },
      {
        path: 'analytics/pnl',
        component: PnLAttribution,
        name: 'PnLAttribution',
        meta: { title: 'Факторная декомпозиция P&L', icon: '📊' }
      },
      {
        path: 'hedging',
        component: HedgingAssistant,
        name: 'HedgingAssistant',
        meta: { title: 'Регрессионное хеджирование', icon: '🎯' }
      },
      {
        path: 'valuation/forwards',
        component: ForwardValuation,
        name: 'ForwardValuation',
        meta: { title: 'Forward Valuation', icon: '📊' }
      },
      {
        path: 'forwards/curve',
        component: ForwardCurveBuilder,
        name: 'ForwardCurveBuilder',
        meta: { title: 'Forward Curve Builder', icon: '📈' }
      },
      {
        path: 'forwards/greeks',
        component: ForwardsGreeksDashboard,
        name: 'ForwardsGreeksDashboard',
        meta: { title: 'Greeks Dashboard', icon: '🎯' }
      },
      {
        path: 'forwards/basis',
        component: BasisAnalysis,
        name: 'BasisAnalysis',
        meta: { title: 'Basis Analysis', icon: '📈' }
      },
      {
        path: 'forwards/margin',
        component: MarginFinancing,
        name: 'MarginFinancing',
        meta: { title: 'Margin & Financing', icon: '💰' }
      },
      {
        path: 'forwards/arbitrage',
        component: ArbitrageScanner,
        name: 'ArbitrageScanner',
        meta: { title: 'Arbitrage Scanner', icon: '🔍' }
      },
      {
        path: 'analytics/volatility',
        component: VolatilitySurface,
        name: 'VolatilitySurface',
        meta: { title: 'Volatility Surface', icon: '📊' }
      },
      {
        path: 'CCMVoptimization',
        name: 'CCMVOptimization',
        component: CCMVOptimizationPage,
        meta: { title: 'CCMV Оптимизация' }
      },
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