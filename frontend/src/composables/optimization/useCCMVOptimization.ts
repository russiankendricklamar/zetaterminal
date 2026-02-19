import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import { usePortfolioStore } from '../../stores/portfolio'
import { useRiskMetricsStore } from '../../stores/riskMetrics'
import { optimizeCCMVPortfolio, type CCMVResponse, type CCMVCluster } from '../../services/ccmvService'

interface Cluster {
  assets: string[]
}

interface ClusterMetric {
  expectedReturn: number
  volatility: number
  avgCorrelation: number
  deltaK: number
  alphaK: number
}

export function useCCMVOptimization() {
  const portfolioStore = usePortfolioStore()
  const riskMetricsStore = useRiskMetricsStore()

  const portfolioPositions = computed(() => portfolioStore.positions)
  const correlationMatrix = computed(() => portfolioStore.correlationMatrix)
  const selectedBank = computed(() => portfolioStore.selectedBank)

  const isComputing = ref(false)
  const ccmvOptimizationResult = ref<CCMVResponse | null>(null)

  const params = ref({
    Delta: 3,
    bar_w: 0.25,
    gamma: 2.0,
    method: 'delta' as 'delta' | 'alpha'
  })

  const clusterColors = [
    '#3b82f6',
    '#10b981',
    '#f59e0b'
  ]

  const clusteringResult = computed(() => {
    if (!ccmvOptimizationResult.value) {
      const positions = portfolioPositions.value
      const numAssets = positions.length
      const sorted = [...positions].sort((a, b) => b.allocation - a.allocation)
      const clusterSize = Math.ceil(sorted.length / 3)

      const clusters: Cluster[] = []
      for (let i = 0; i < sorted.length; i += clusterSize) {
        const clusterAssets = sorted.slice(i, i + clusterSize).map(p => p.symbol)
        if (clusterAssets.length > 0) clusters.push({ assets: clusterAssets })
      }

      return {
        numClusters: clusters.length || 3,
        numAssets: numAssets,
        clusters: clusters.length > 0 ? clusters : [
          { assets: sorted.slice(0, Math.ceil(sorted.length / 3)).map(p => p.symbol) },
          { assets: sorted.slice(Math.ceil(sorted.length / 3), Math.ceil(sorted.length * 2 / 3)).map(p => p.symbol) },
          { assets: sorted.slice(Math.ceil(sorted.length * 2 / 3)).map(p => p.symbol) }
        ].filter(c => c.assets.length > 0) as Cluster[]
      }
    }

    const result = ccmvOptimizationResult.value
    return {
      numClusters: result.clusters.length,
      numAssets: result.optimal_weights.length,
      clusters: result.clusters.map(c => ({ assets: c.assets })) as Cluster[]
    }
  })

  const clusterMetrics = computed<ClusterMetric[]>(() => {
    if (!ccmvOptimizationResult.value) {
      return [
        { expectedReturn: 0.085, volatility: 0.18, avgCorrelation: 0.75, deltaK: 2, alphaK: params.value.method === 'delta' ? 0.33 : 0.35 },
        { expectedReturn: 0.045, volatility: 0.08, avgCorrelation: 0.65, deltaK: 1, alphaK: params.value.method === 'delta' ? 0.33 : 0.30 },
        { expectedReturn: 0.055, volatility: 0.12, avgCorrelation: 0.40, deltaK: 1, alphaK: params.value.method === 'delta' ? 0.34 : 0.35 }
      ]
    }

    const result = ccmvOptimizationResult.value
    const corrMatrix = correlationMatrix.value

    return result.clusters.map(cluster => {
      let avgCorr = 0
      let corrCount = 0
      for (let i = 0; i < cluster.asset_indices.length; i++) {
        for (let j = i + 1; j < cluster.asset_indices.length; j++) {
          const idx1 = cluster.asset_indices[i]
          const idx2 = cluster.asset_indices[j]
          const corr = corrMatrix[idx1]?.values[idx2] || 0
          avgCorr += corr
          corrCount++
        }
      }
      avgCorr = corrCount > 0 ? avgCorr / corrCount : 0

      return {
        expectedReturn: 0.06,
        volatility: 0.15,
        avgCorrelation: avgCorr,
        deltaK: cluster.delta_k,
        alphaK: cluster.alpha_k
      }
    })
  })

  const optimizationResult = computed(() => {
    if (!ccmvOptimizationResult.value) {
      const weights: Record<string, number> = {}
      portfolioPositions.value.forEach(pos => {
        weights[pos.symbol] = pos.allocation / 100
      })
      return { weights, method: params.value.method }
    }

    const result = ccmvOptimizationResult.value
    const weights: Record<string, number> = {}
    result.optimal_weights.forEach((weight, idx) => {
      const symbol = portfolioPositions.value[idx]?.symbol
      if (symbol) weights[symbol] = weight
    })
    return { weights, method: result.method }
  })

  const objectiveValue = computed(() => {
    if (!ccmvOptimizationResult.value) return 0.0185 - params.value.gamma * 0.0625
    return ccmvOptimizationResult.value.portfolio_stats.objective_value
  })

  const objectiveComponents = computed(() => {
    if (!ccmvOptimizationResult.value) return { variance: 0.0185, return: 0.0625 }
    const stats = ccmvOptimizationResult.value.portfolio_stats
    return { variance: stats.volatility * stats.volatility, return: stats.expected_return }
  })

  const portfolioStats = computed(() => {
    if (!ccmvOptimizationResult.value) {
      return {
        expectedReturn: 0.0625,
        volatility: 0.136,
        sharpeRatio: (0.0625 - 0.042) / 0.136,
        numPositions: Object.values(optimizationResult.value.weights).filter(w => w > 0.001).length
      }
    }
    const result = ccmvOptimizationResult.value
    const stats = result.portfolio_stats
    return {
      expectedReturn: stats.expected_return,
      volatility: stats.volatility,
      sharpeRatio: stats.sharpe_ratio,
      numPositions: result.optimal_weights.filter((w: number) => w > 0.001).length
    }
  })

  const clusterAllocations = computed(() => {
    if (!ccmvOptimizationResult.value) {
      return clusterMetrics.value.map(m => ({ percentage: m.alphaK * 100 }))
    }
    return ccmvOptimizationResult.value.clusters.map(c => ({ percentage: c.alpha_k * 100 }))
  })

  const getDeltaClass = (delta: number): string => {
    if (Math.abs(delta) < 0.1) return 'neutral'
    return delta > 0 ? 'positive' : 'negative'
  }

  const getOptimalWeight = (symbol: string): number => {
    const weights = optimizationResult.value.weights as Record<string, number>
    const optWeight = weights[symbol]
    if (optWeight !== undefined && optWeight !== null) return optWeight * 100
    const currentPos = portfolioPositions.value.find(p => p.symbol === symbol)
    return currentPos?.allocation || 0
  }

  const getWeightDelta = (pos: any): number => {
    return getOptimalWeight(pos.symbol) - pos.allocation
  }

  const getAssetAllocation = (symbol: string): number | null => {
    if (ccmvOptimizationResult.value) {
      const idx = portfolioPositions.value.findIndex(p => p.symbol === symbol)
      if (idx >= 0 && idx < ccmvOptimizationResult.value.optimal_weights.length) {
        const weight = ccmvOptimizationResult.value.optimal_weights[idx]
        return weight > 0.001 ? weight * 100 : null
      }
    }
    const pos = portfolioPositions.value.find(p => p.symbol === symbol)
    return pos?.allocation || null
  }

  const recomputeOptimization = async (
    showToast: (msg: string, type: 'success' | 'error' | 'info') => void
  ) => {
    isComputing.value = true
    try {
      const positions = portfolioPositions.value
      const n = positions.length
      if (n === 0) throw new Error('Портфель пуст')

      const timeSteps = 252
      const R: number[][] = []
      for (let t = 0; t < timeSteps; t++) {
        const row: number[] = []
        positions.forEach(pos => {
          const dailyReturn = (pos.dayChange / 100) / 252 + (Math.random() - 0.5) * (pos.dayChange / 100) / 10
          row.push(dailyReturn)
        })
        R.push(row)
      }

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
          row.push(corr * volatilities[i] * volatilities[j])
        }
        covMatrix.push(row)
      }

      const result = await optimizeCCMVPortfolio({
        R, mu, cov_matrix: covMatrix,
        Delta: params.value.Delta,
        bar_w: params.value.bar_w,
        gamma: params.value.gamma,
        method: params.value.method,
        asset_names: positions.map(p => p.symbol)
      })

      ccmvOptimizationResult.value = result

      const portfolioValue = 2400000
      const stats = result.portfolio_stats
      const varMetrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.95, 1)
      const var99Metrics = riskMetricsStore.calculateVaR(portfolioValue, stats.volatility, 0.99, 1)

      const optimizedPositions = positions.map((pos, idx) => {
        const optimalWeight = result.optimal_weights[idx] || 0
        return { symbol: pos.symbol, allocation: optimalWeight * 100, notional: portfolioValue * optimalWeight, color: pos.color }
      })

      const riskContributions = riskMetricsStore.calculateRiskContributions(
        optimizedPositions, stats.volatility, correlationMatrix.value, portfolioValue
      )

      riskMetricsStore.updateMetrics({
        var95: varMetrics.var, var99: var99Metrics.var,
        cvar95: varMetrics.cvar, cvar99: var99Metrics.cvar,
        expectedReturn: stats.expected_return, volatility: stats.volatility,
        sharpeRatio: stats.sharpe_ratio, portfolioBeta: 0.85,
        riskContributions, maxDrawdown: 0.124
      })

      showToast(
        `Оптимизация завершена (${params.value.method === 'delta' ? 'Δ-CCMV' : 'α-CCMV'}). Sharpe = ${result.portfolio_stats.sharpe_ratio.toFixed(2)}`,
        'success'
      )
    } catch (error) {
      console.error('CCMV Optimization Error:', error)
      showToast(
        `Ошибка оптимизации: ${error instanceof Error ? error.message : 'Unknown error'}`,
        'error'
      )
    } finally {
      isComputing.value = false
    }
  }

  return {
    isComputing,
    params,
    clusterColors,
    clusteringResult,
    clusterMetrics,
    optimizationResult,
    objectiveValue,
    objectiveComponents,
    portfolioStats,
    clusterAllocations,
    ccmvOptimizationResult,
    getDeltaClass,
    getOptimalWeight,
    getWeightDelta,
    getAssetAllocation,
    recomputeOptimization,
    portfolioPositions,
    selectedBank
  }
}
