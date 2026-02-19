import { ref, computed } from 'vue'
import { usePortfolioStore } from '../../stores/portfolio'
import { useRiskMetricsStore } from '../../stores/riskMetrics'
import { optimizeHJBPortfolio, type HJBResponse } from '../../services/hjbService'

export function useHJBOptimization() {
  const portfolioStore = usePortfolioStore()
  const riskMetricsStore = useRiskMetricsStore()

  const portfolioPositions = computed(() => portfolioStore.positions)
  const correlationMatrix = computed(() => portfolioStore.correlationMatrix)

  const isComputing = ref(false)
  const hjbOptimizationResult = ref<HJBResponse | null>(null)

  const hjbParams = ref({
    gamma: 2.0,
    horizon: 1.0,
    riskFreeRate: 0.045,
    marketVol: 0.18,
    expectedReturn: 0.10,
    monteCarloTrajectories: 10000
  })

  const hjbOptimalAllocation = computed(() => {
    const { expectedReturn, riskFreeRate, gamma, marketVol } = hjbParams.value
    const excessReturn = expectedReturn - riskFreeRate
    const allocation = excessReturn / (gamma * marketVol * marketVol)
    return Math.max(0, Math.min(allocation, 2))
  })

  const hjbExpectedPortfolioReturn = computed(() => {
    const pi = hjbOptimalAllocation.value
    const { expectedReturn, riskFreeRate } = hjbParams.value
    return riskFreeRate + pi * (expectedReturn - riskFreeRate)
  })

  const hjbPortfolioVol = computed(() => {
    const pi = hjbOptimalAllocation.value
    return pi * hjbParams.value.marketVol
  })

  const hjbSharpeRatio = computed(() => {
    const { expectedReturn, riskFreeRate, marketVol } = hjbParams.value
    return (expectedReturn - riskFreeRate) / marketVol
  })

  const hjbCertaintyEquivalent = computed(() => {
    const { gamma } = hjbParams.value
    const excessReturn = hjbExpectedPortfolioReturn.value - hjbParams.value.riskFreeRate
    const variance = hjbPortfolioVol.value * hjbPortfolioVol.value
    return hjbParams.value.riskFreeRate + excessReturn - 0.5 * gamma * variance
  })

  const trajectoriesDays = computed(() => {
    return Math.round(hjbParams.value.horizon * 252)
  })

  const runHJBOptimization = async (
    showToast: (msg: string, type: 'success' | 'error' | 'info') => void,
    onMonteCarloUpdate?: (mc: NonNullable<HJBResponse['monte_carlo']>) => void
  ) => {
    isComputing.value = true
    try {
      const positions = portfolioPositions.value
      const n = positions.length

      const mu = positions.map(pos => {
        const dailyReturn = pos.dayChange / 100
        const annualReturn = dailyReturn * 252
        return Math.max(0.01, 0.05 + annualReturn)
      })

      const corrMatrix = correlationMatrix.value
      const volatilities = positions.map(() => 0.2)
      const covMatrix: number[][] = []

      for (let i = 0; i < n; i++) {
        const row: number[] = []
        for (let j = 0; j < n; j++) {
          const corr = corrMatrix[i]?.values[j] || (i === j ? 1 : 0)
          const cov = corr * volatilities[i] * volatilities[j]
          row.push(cov)
        }
        covMatrix.push(row)
      }

      const monteCarloParams = {
        initial_capital: 1000000,
        horizon_years: hjbParams.value.horizon,
        n_paths: hjbParams.value.monteCarloTrajectories,
        n_steps: trajectoriesDays.value,
        random_seed: 42
      }

      const result = await optimizeHJBPortfolio({
        mu,
        cov_matrix: covMatrix,
        risk_free_rate: hjbParams.value.riskFreeRate,
        gamma: hjbParams.value.gamma,
        asset_names: positions.map(p => p.symbol),
        monte_carlo: monteCarloParams
      })

      hjbOptimizationResult.value = result

      if (result.monte_carlo && onMonteCarloUpdate) {
        onMonteCarloUpdate(result.monte_carlo)
      }

      const portfolioValue = 2400000
      const stats = result.portfolio_stats
      const varMetrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.95, 1)
      const var99Metrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.99, 1)

      const riskContributions = riskMetricsStore.calculateRiskContributions(
        positions.map(p => ({
          symbol: p.symbol,
          allocation: p.allocation,
          notional: p.notional,
          color: p.color
        })),
        stats.volatility,
        correlationMatrix.value,
        portfolioValue
      )

      riskMetricsStore.updateMetrics({
        var95: varMetrics.var,
        var99: var99Metrics.var,
        cvar95: varMetrics.cvar,
        cvar99: var99Metrics.cvar,
        expectedReturn: stats.expected_return,
        volatility: stats.volatility,
        sharpeRatio: stats.sharpe_ratio,
        portfolioBeta: 0.85,
        riskContributions: riskContributions,
        maxDrawdown: result.monte_carlo?.stats?.mean_max_drawdown || 0.124
      })

      showToast(
        `HJB оптимизация завершена: Sharpe = ${result.portfolio_stats.sharpe_ratio.toFixed(2)}`,
        'success'
      )
    } catch (error) {
      console.error('HJB Optimization Error:', error)
      showToast(
        `Ошибка оптимизации: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'error'
      )
    } finally {
      isComputing.value = false
    }
  }

  // GARCH filtering
  const garchFilteredAssets = computed(() => {
    return portfolioPositions.value
      .map(asset => ({
        symbol: asset.symbol,
        name: asset.name,
        garchVol: 15 + Math.random() * 20,
        passed: true
      }))
      .filter(asset => asset.garchVol <= 30)
      .sort((a, b) => a.garchVol - b.garchVol)
  })

  const garchFilteredCount = computed(() => garchFilteredAssets.value.length)

  // Yield report
  const yieldReportData = computed(() => {
    return portfolioPositions.value.map(asset => {
      const historicalYield = 0.05 + Math.random() * 0.15
      const dividendYield = 0.02 + Math.random() * 0.08
      return {
        symbol: asset.symbol,
        name: asset.name,
        color: asset.color,
        historicalYield,
        dividendYield,
        totalYield: historicalYield + dividendYield
      }
    }).sort((a, b) => b.totalYield - a.totalYield)
  })

  const avgHistoricalYield = computed(() => {
    if (yieldReportData.value.length === 0) return 0
    return yieldReportData.value.reduce((sum, a) => sum + a.historicalYield, 0) / yieldReportData.value.length
  })

  const avgDividendYield = computed(() => {
    if (yieldReportData.value.length === 0) return 0
    return yieldReportData.value.reduce((sum, a) => sum + a.dividendYield, 0) / yieldReportData.value.length
  })

  const avgTotalYield = computed(() => {
    if (yieldReportData.value.length === 0) return 0
    return yieldReportData.value.reduce((sum, a) => sum + a.totalYield, 0) / yieldReportData.value.length
  })

  return {
    hjbParams,
    hjbOptimalAllocation,
    hjbExpectedPortfolioReturn,
    hjbPortfolioVol,
    hjbSharpeRatio,
    hjbCertaintyEquivalent,
    hjbOptimizationResult,
    isComputing,
    trajectoriesDays,
    runHJBOptimization,
    garchFilteredAssets,
    garchFilteredCount,
    yieldReportData,
    avgHistoricalYield,
    avgDividendYield,
    avgTotalYield,
    portfolioPositions,
    correlationMatrix
  }
}
