// src/router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Home from '@/pages/Home.vue'
import Portfolio from '@/pages/Portfolio.vue'
import MonteCarlo from '@/pages/MonteCarlo.vue'
import GreekParameters from '@/pages/GreekParameters.vue'
import StressTesting from '@/pages/StressTesting.vue'
import Backtesting from '@/pages/Backtesting.vue'
import Reports from '@/pages/Reports.vue'
import Settings from '@/pages/Settings.vue'
import RegimeAnalysis from '@/pages/RegimeAnalysis.vue'
import RegimeDetails from '@/pages/RegimeDetails.vue'
import SpectralRegimeAnalysis from '@/pages/SpectralRegimeAnalysis.vue'
import YieldAnalysis from '@/pages/YieldAnalysis.vue'
import BondValuation from '@/pages/BondValuation.vue'
import ZCYCViewer from '@/pages/ZCYCViewer.vue'
import BondReport from '@/pages/BondReport.vue'
import VanilaBondReport from '@/pages/VanilaBondReport.vue'
import FloaterBondReport from '@/pages/FloaterBondReport.vue'
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
import VolatilitySurface from '@/pages/VolatilitySurface.vue'
import CCMVOptimizationPage from '@/pages/CCMVOptimization.vue'
import DocumentationPage from '@/pages/DocumentationPage.vue'
import KnowledgeBase from '@/pages/KnowledgeBase.vue'
import Terminal from '@/pages/Terminal.vue'
import Profile from '@/pages/Profile.vue'
import SharpeStats from '@/pages/SharpeStats.vue'
import RealizedKernels from '@/pages/RealizedKernels.vue'
import HARModel from '@/pages/HARModel.vue'
import FactorAnalysis from '@/pages/FactorAnalysis.vue'
import Eigenportfolio from '@/pages/Eigenportfolio.vue'
import PBOAnalysis from '@/pages/PBOAnalysis.vue'
import AlphaStacking from '@/pages/AlphaStacking.vue'
import MetaLabeling from '@/pages/MetaLabeling.vue'
import ConvexPortfolio from '@/pages/ConvexPortfolio.vue'

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
    component: KnowledgeBase,
    meta: { title: 'База знаний', bare: true }
  },
  {
    path: '/docs-legacy',
    name: 'DocumentationLegacy',
    component: DocumentationPage,
    meta: { title: 'Документация (старая)' }
  },
  {
    path: '/terminal',
    name: 'Terminal',
    component: Terminal,
    meta: { title: 'Терминал', icon: '💻' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: 'Профиль', icon: '👤', bare: true }
  },
  {
    path: '/',
    component: MainLayout,
    children: [
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
        path: 'spectral-regimes',
        component: SpectralRegimeAnalysis,
        name: 'SpectralRegimeAnalysis',
        meta: { title: 'Комплексный анализ режимов', icon: '🌀' }
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
        path: 'floater-bond-report/:isin?',
        component: FloaterBondReport,
        name: 'FloaterBondReport',
        meta: { title: 'Floater Bond Report', icon: '📋' }
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
      {
        path: 'analytics/sharpe-stats',
        name: 'SharpeStats',
        component: SharpeStats,
        meta: { title: 'Статистика Шарпа', icon: '📐' }
      },
      {
        path: 'analytics/realized-kernels',
        name: 'RealizedKernels',
        component: RealizedKernels,
        meta: { title: 'Realized Kernels', icon: '📡' }
      },
      {
        path: 'analytics/har-model',
        name: 'HARModel',
        component: HARModel,
        meta: { title: 'HAR Model', icon: '📊' }
      },
      {
        path: 'analytics/factor-analysis',
        name: 'FactorAnalysis',
        component: FactorAnalysis,
        meta: { title: 'TS vs CS Factor Analysis', icon: '🧮' }
      },
      {
        path: 'analytics/eigenportfolio',
        name: 'Eigenportfolio',
        component: Eigenportfolio,
        meta: { title: 'Eigenportfolios (PCA)', icon: '🔬' }
      },
      {
        path: 'analytics/pbo',
        name: 'PBOAnalysis',
        component: PBOAnalysis,
        meta: { title: 'PBO / DSR', icon: '🧪' }
      },
      {
        path: 'analytics/alpha-stacking',
        name: 'AlphaStacking',
        component: AlphaStacking,
        meta: { title: 'Orthogonal Alpha Stacking', icon: '🔗' }
      },
      {
        path: 'analytics/meta-labeling',
        name: 'MetaLabeling',
        component: MetaLabeling,
        meta: { title: 'Meta-Labeling', icon: '🏷️' }
      },
      {
        path: 'analytics/convex-portfolio',
        name: 'ConvexPortfolio',
        component: ConvexPortfolio,
        meta: { title: 'Convex Portfolio', icon: '📐' }
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
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const title = (to.meta?.title as string) || 'QuantPro'
  document.title = `${title} | Risk Management`
  next()
})

export default router