// src/router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/components/Layout/MainLayout.vue'
import Home from '@/pages/Home.vue'

// Everything else is lazy-loaded for code splitting
const NotFound = () => import('@/pages/NotFound.vue')
const Portfolio = () => import('@/pages/Portfolio.vue')
const GreekParameters = () => import('@/pages/GreekParameters.vue')
const StressTesting = () => import('@/pages/StressTesting.vue')
const Backtesting = () => import('@/pages/Backtesting.vue')
const Reports = () => import('@/pages/Reports.vue')
const Settings = () => import('@/pages/Settings.vue')
const RegimeAnalysis = () => import('@/pages/RegimeAnalysis.vue')
const RegimeDetails = () => import('@/pages/RegimeDetails.vue')
const SpectralRegimeAnalysis = () => import('@/pages/SpectralRegimeAnalysis.vue')
const YieldAnalysis = () => import('@/pages/YieldAnalysis.vue')
const BondValuation = () => import('@/pages/BondValuation.vue')
const ZCYCViewer = () => import('@/pages/ZCYCViewer.vue')
const BondReport = () => import('@/pages/BondReport.vue')
const VanilaBondReport = () => import('@/pages/VanilaBondReport.vue')
const FloaterBondReport = () => import('@/pages/FloaterBondReport.vue')
const OptionPricing = () => import('@/pages/OptionPricing.vue')
const OptionModelsComparison = () => import('@/pages/OptionModelsComparison.vue')
const OptionGreeksAnalyzer = () => import('@/pages/OptionGreeksAnalyzer.vue')
const OptionPortfolio = () => import('@/pages/OptionPortfolio.vue')
const StressSwapsView = () => import('@/pages/StressTestingSwap.vue')
const SwapGreeksDashboard = () => import('@/pages/SwapGreeksDashboard.vue')
const SwapValuation = () => import('@/pages/SwapValuation.vue')
const PnLAttribution = () => import('@/pages/PnLAttribution.vue')
const HedgingAssistant = () => import('@/pages/HedgingAssistant.vue')
const ForwardValuation = () => import('@/pages/ForwardValuation.vue')
const ForwardCurveBuilder = () => import('@/pages/ForwardCurveBuilder.vue')
const ForwardsGreeksDashboard = () => import('@/pages/ForwardsGreeksDashboard.vue')
const BasisAnalysis = () => import('@/pages/BasisAnalysis.vue')
const VolatilitySurface = () => import('@/pages/VolatilitySurface.vue')
const PortfolioOptimization = () => import('@/pages/PortfolioOptimization.vue')
const KnowledgeBase = () => import('@/pages/KnowledgeBase.vue')
const Terminal = () => import('@/pages/Terminal.vue')
const Profile = () => import('@/pages/Profile.vue')
const SharpeStats = () => import('@/pages/SharpeStats.vue')
const RealizedKernels = () => import('@/pages/RealizedKernels.vue')
const HARModel = () => import('@/pages/HARModel.vue')
const FactorAnalysis = () => import('@/pages/FactorAnalysis.vue')
const Eigenportfolio = () => import('@/pages/Eigenportfolio.vue')
const PBOAnalysis = () => import('@/pages/PBOAnalysis.vue')
const AlphaStacking = () => import('@/pages/AlphaStacking.vue')
const MetaLabeling = () => import('@/pages/MetaLabeling.vue')
const AdversarialStress = () => import('@/pages/AdversarialStress.vue')

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
      { path: 'portfolio', component: Portfolio, name: 'Portfolio', meta: { title: 'Портфель', icon: '💼' } },
      { path: 'greeks', component: GreekParameters, name: 'GreekParameters', meta: { title: 'Греческие параметры', icon: '🎯', badge: '3' } },
      { path: 'stress', component: StressTesting, name: 'StressTesting', meta: { title: 'Стресс-тестирование', icon: '⚡' }, alias: 'stress-testing' },
      { path: 'backtest', component: Backtesting, name: 'Backtesting', meta: { title: 'Бэктестинг', icon: '📉' } },
      { path: 'reports', component: Reports, name: 'Reports', meta: { title: 'Отчёты', icon: '📋' } },
      { path: 'settings', component: Settings, name: 'Settings', meta: { title: 'Настройки', icon: '⚙️' }, alias: 'parameters' },
      { path: 'regimes', component: RegimeAnalysis, name: 'RegimeAnalysis', meta: { title: 'Рыночные режимы', icon: '🌊' } },
      { path: 'fixed-income', component: YieldAnalysis, name: 'YieldAnalysis', meta: { title: 'Доходность облигаций', icon: '📈' } },
      { path: 'regime-details', component: RegimeDetails, name: 'RegimeDetails', meta: { title: 'HMM Аналитика', icon: '🔬' } },
      { path: 'spectral-regimes', component: SpectralRegimeAnalysis, name: 'SpectralRegimeAnalysis', meta: { title: 'Комплексный анализ режимов', icon: '🌀' } },
      { path: 'bond-valuation', component: BondValuation, name: 'BondValuation', meta: { title: 'Справедливая стоимость облигаций', icon: '💰' } },
      { path: 'zcyc-viewer', component: ZCYCViewer, name: 'ZCYCViewer', meta: { title: 'Кривая бескупонных доходностей', icon: '📈' } },
      { path: 'bond-report', component: BondReport, name: 'BondReport', meta: { title: 'Отчет об оценке облигаций', icon: '📄' } },
      { path: 'vanila-bond-report/:isin?', component: VanilaBondReport, name: 'VanilaBondReport', meta: { title: 'Vanila Bond Report', icon: '📊' } },
      { path: 'floater-bond-report/:isin?', component: FloaterBondReport, name: 'FloaterBondReport', meta: { title: 'Floater Bond Report', icon: '📋' } },
      { path: 'pricing/options', component: OptionPricing, name: 'OptionPricing', meta: { title: 'Справедливая стоимость опционов', icon: 'ƒ' } },
      { path: 'pricing/options/models', component: OptionModelsComparison, name: 'OptionModelsComparison', meta: { title: 'Сравнение моделей ценообразования', icon: 'ƒ' } },
      { path: 'pricing/options/greeks', component: OptionGreeksAnalyzer, name: 'OptionGreeksAnalyzer', meta: { title: 'Анализ чувствительности (Greeks)', icon: 'ƒ' } },
      { path: 'pricing/options/portfolio', component: OptionPortfolio, name: 'OptionPortfolio', meta: { title: 'Портфель опционов', icon: 'ƒ' } },
      { path: 'stress/swaps', component: StressSwapsView, name: 'stress-swaps', meta: { title: 'Стресс-тестирование Свопов', icon: 'ƒ' } },
      { path: 'swap-greeks', component: SwapGreeksDashboard, name: 'SwapGreeksDashboard', meta: { title: 'Греки СВОПов', icon: '⚡' } },
      { path: 'valuation/swaps', component: SwapValuation, name: 'SwapValuation', meta: { title: 'Оценка справедливой стоимости СВОПов', icon: '💰' } },
      { path: 'analytics/pnl', component: PnLAttribution, name: 'PnLAttribution', meta: { title: 'Факторная декомпозиция P&L', icon: '📊' } },
      { path: 'hedging', component: HedgingAssistant, name: 'HedgingAssistant', meta: { title: 'Регрессионное хеджирование', icon: '🎯' } },
      { path: 'valuation/forwards', component: ForwardValuation, name: 'ForwardValuation', meta: { title: 'Forward Valuation', icon: '📊' } },
      { path: 'forwards/curve', component: ForwardCurveBuilder, name: 'ForwardCurveBuilder', meta: { title: 'Forward Curve Builder', icon: '📈' } },
      { path: 'forwards/greeks', component: ForwardsGreeksDashboard, name: 'ForwardsGreeksDashboard', meta: { title: 'Greeks Dashboard', icon: '🎯' } },
      { path: 'forwards/basis', component: BasisAnalysis, name: 'BasisAnalysis', meta: { title: 'Basis Analysis', icon: '📈' } },
      { path: 'analytics/volatility', component: VolatilitySurface, name: 'VolatilitySurface', meta: { title: 'Volatility Surface', icon: '📊' } },
      { path: 'optimization', name: 'PortfolioOptimization', component: PortfolioOptimization, meta: { title: 'Оптимизация портфеля', icon: '📊' } },
      { path: 'analytics/sharpe-stats', name: 'SharpeStats', component: SharpeStats, meta: { title: 'Статистика Шарпа', icon: '📐' } },
      { path: 'analytics/realized-kernels', name: 'RealizedKernels', component: RealizedKernels, meta: { title: 'Realized Kernels', icon: '📡' } },
      { path: 'analytics/har-model', name: 'HARModel', component: HARModel, meta: { title: 'HAR Model', icon: '📊' } },
      { path: 'analytics/factor-analysis', name: 'FactorAnalysis', component: FactorAnalysis, meta: { title: 'TS vs CS Factor Analysis', icon: '🧮' } },
      { path: 'analytics/eigenportfolio', name: 'Eigenportfolio', component: Eigenportfolio, meta: { title: 'Eigenportfolios (PCA)', icon: '🔬' } },
      { path: 'analytics/pbo', name: 'PBOAnalysis', component: PBOAnalysis, meta: { title: 'PBO / DSR', icon: '🧪' } },
      { path: 'analytics/alpha-stacking', name: 'AlphaStacking', component: AlphaStacking, meta: { title: 'Orthogonal Alpha Stacking', icon: '🔗' } },
      { path: 'analytics/meta-labeling', name: 'MetaLabeling', component: MetaLabeling, meta: { title: 'Meta-Labeling', icon: '🏷️' } },
      { path: 'analytics/adversarial-stress', name: 'AdversarialStress', component: AdversarialStress, meta: { title: 'Adversarial Stress Testing', icon: '🛡️' } },
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
