import { ref, computed } from 'vue'
import { usePortfolioStore } from '../../stores/portfolio'
import { useRiskMetricsStore } from '../../stores/riskMetrics'
import {
  optimizeBlackLitterman,
  type BlackLittermanResponse,
  type BLView,
} from '../../services/blackLittermanService'

export interface InvestorView {
  id: number
  type: 'absolute' | 'relative'
  asset1Index: number
  asset2Index: number
  expectedReturn: number
  confidence: number
}

export function useBlackLittermanOptimization() {
  const portfolioStore = usePortfolioStore()
  const riskMetricsStore = useRiskMetricsStore()

  const portfolioPositions = computed(() => portfolioStore.positions)
  const correlationMatrix = computed(() => portfolioStore.correlationMatrix)
  const selectedBank = computed(() => portfolioStore.selectedBank)

  const isComputing = ref(false)
  const blResult = ref<BlackLittermanResponse | null>(null)

  const params = ref({
    tau: 0.05,
    delta: 2.5,
    riskFreeRate: 0.045,
    maxWeight: 0.30,
  })

  // Investor views: editable list
  const views = ref<InvestorView[]>([
    { id: 1, type: 'absolute', asset1Index: 0, asset2Index: 1, expectedReturn: 0.10, confidence: 0.7 },
    { id: 2, type: 'relative', asset1Index: 0, asset2Index: 2, expectedReturn: 0.03, confidence: 0.5 },
  ])

  let nextViewId = 3

  const addView = () => {
    const n = portfolioPositions.value.length
    views.value = [
      ...views.value,
      {
        id: nextViewId++,
        type: 'absolute',
        asset1Index: Math.min(views.value.length, n - 1),
        asset2Index: Math.min(views.value.length + 1, n - 1),
        expectedReturn: 0.05,
        confidence: 0.5,
      },
    ]
  }

  const removeView = (id: number) => {
    views.value = views.value.filter((v) => v.id !== id)
  }

  // Market weights from portfolio allocations
  const marketWeights = computed(() => {
    const positions = portfolioPositions.value
    const totalAlloc = positions.reduce((s, p) => s + p.allocation, 0)
    if (totalAlloc <= 0) return positions.map(() => 1 / positions.length)
    return positions.map((p) => p.allocation / totalAlloc)
  })

  // Build P matrix and Q vector from views
  const buildViewsPayload = (): BLView[] => {
    const n = portfolioPositions.value.length
    return views.value.map((v) => {
      if (v.type === 'absolute') {
        return {
          assets: [v.asset1Index],
          weights: [1.0],
          expected_return: v.expectedReturn,
          confidence: v.confidence,
        }
      }
      // relative: asset1 - asset2 = expectedReturn
      return {
        assets: [v.asset1Index, v.asset2Index],
        weights: [1.0, -1.0],
        expected_return: v.expectedReturn,
        confidence: v.confidence,
      }
    })
  }

  // Computed results
  const optimalWeights = computed<Record<string, number>>(() => {
    if (!blResult.value) {
      const w: Record<string, number> = {}
      portfolioPositions.value.forEach((p) => {
        w[p.symbol] = p.allocation / 100
      })
      return w
    }
    const w: Record<string, number> = {}
    blResult.value.optimal_weights.forEach((weight, idx) => {
      const symbol = portfolioPositions.value[idx]?.symbol
      if (symbol) w[symbol] = weight
    })
    return w
  })

  const equilibriumWeights = computed<Record<string, number>>(() => {
    if (!blResult.value) return marketWeights.value.reduce((acc, w, i) => {
      const sym = portfolioPositions.value[i]?.symbol
      if (sym) acc[sym] = w
      return acc
    }, {} as Record<string, number>)

    const w: Record<string, number> = {}
    blResult.value.equilibrium_weights.forEach((weight, idx) => {
      const symbol = portfolioPositions.value[idx]?.symbol
      if (symbol) w[symbol] = weight
    })
    return w
  })

  const equilibriumReturns = computed<number[]>(() => {
    if (!blResult.value) {
      return portfolioPositions.value.map((p) => {
        const dailyReturn = p.dayChange / 100
        return 0.05 + dailyReturn * 252
      })
    }
    return blResult.value.equilibrium_returns
  })

  const posteriorReturns = computed<number[]>(() => {
    if (!blResult.value) return equilibriumReturns.value
    return blResult.value.posterior_returns
  })

  const portfolioStats = computed(() => {
    if (!blResult.value) {
      return {
        expectedReturn: 0.065,
        volatility: 0.14,
        sharpeRatio: 0.143,
        numPositions: portfolioPositions.value.length,
      }
    }
    return blResult.value.portfolio_stats
  })

  const equilibriumStats = computed(() => {
    if (!blResult.value) {
      return { expectedReturn: 0.055, volatility: 0.15, sharpeRatio: 0.033 }
    }
    return blResult.value.equilibrium_stats
  })

  const viewsImpact = computed(() => {
    if (!blResult.value) return []
    return blResult.value.views_impact
  })

  const riskContributions = computed<number[]>(() => {
    if (!blResult.value) return portfolioPositions.value.map(() => 0)
    return blResult.value.risk_contributions
  })

  const getOptimalWeight = (symbol: string): number => {
    const w = optimalWeights.value[symbol]
    return w !== undefined ? w * 100 : 0
  }

  const getEquilibriumWeight = (symbol: string): number => {
    const w = equilibriumWeights.value[symbol]
    return w !== undefined ? w * 100 : 0
  }

  const getWeightDelta = (symbol: string): number => {
    return getOptimalWeight(symbol) - (portfolioPositions.value.find((p) => p.symbol === symbol)?.allocation ?? 0)
  }

  const getDeltaClass = (delta: number): string => {
    if (Math.abs(delta) < 0.1) return 'neutral'
    return delta > 0 ? 'positive' : 'negative'
  }

  const runOptimization = async (
    showToast: (msg: string, type: 'success' | 'error' | 'info') => void
  ) => {
    isComputing.value = true
    try {
      const positions = portfolioPositions.value
      const n = positions.length
      if (n === 0) throw new Error('Портфель пуст')
      if (views.value.length === 0) throw new Error('Добавьте хотя бы один взгляд')

      // Build covariance matrix
      const corrMatrix = correlationMatrix.value
      const volatilities = positions.map(() => 0.2)
      const covMatrix: number[][] = []
      for (let i = 0; i < n; i++) {
        const row: number[] = []
        for (let j = 0; j < n; j++) {
          const corr = corrMatrix[i]?.values[j] || (i === j ? 1 : 0)
          row.push(corr * volatilities[i] * volatilities[j])
        }
        covMatrix.push(row)
      }

      const result = await optimizeBlackLitterman({
        cov_matrix: covMatrix,
        market_weights: marketWeights.value,
        views: buildViewsPayload(),
        tau: params.value.tau,
        delta: params.value.delta,
        risk_free_rate: params.value.riskFreeRate,
        max_weight: params.value.maxWeight,
        asset_names: positions.map((p) => p.symbol),
      })

      blResult.value = result

      // Update risk metrics store
      const portfolioValue = 2400000
      const stats = result.portfolio_stats
      const varMetrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.95, 1)
      const var99Metrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.99, 1)

      const riskContribs = riskMetricsStore.calculateRiskContributions(
        positions.map((p, idx) => ({
          symbol: p.symbol,
          allocation: result.optimal_weights[idx] * 100,
          notional: portfolioValue * result.optimal_weights[idx],
          color: p.color,
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
        riskContributions: riskContribs,
        maxDrawdown: 0.124,
      })

      showToast(
        `Black-Litterman завершён: Sharpe = ${stats.sharpe_ratio.toFixed(2)}`,
        'success'
      )
    } catch (error) {
      console.error('Black-Litterman Error:', error)
      showToast(
        `Ошибка: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'error'
      )
    } finally {
      isComputing.value = false
    }
  }

  return {
    isComputing,
    params,
    views,
    blResult,
    portfolioPositions,
    selectedBank,
    marketWeights,
    optimalWeights,
    equilibriumWeights,
    equilibriumReturns,
    posteriorReturns,
    portfolioStats,
    equilibriumStats,
    viewsImpact,
    riskContributions,
    addView,
    removeView,
    getOptimalWeight,
    getEquilibriumWeight,
    getWeightDelta,
    getDeltaClass,
    runOptimization,
  }
}
