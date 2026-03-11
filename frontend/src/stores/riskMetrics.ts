/**
 * Store для риск-метрик портфеля
 * Получает данные из CCMVOptimization и предоставляет их для GreekParameters
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { calculateVaR as apiCalculateVaR, type VaRMethod, type GarchModel, type VaRResult } from '@/services/riskService'

export interface RiskContribution {
  symbol: string
  weight: number
  contribution: number  // Marginal VaR contribution in currency
  percentRisk: number   // Percentage of total risk
  color: string
}

export interface StressScenario {
  id: number
  name: string
  description: string
  impact: number  // Impact in currency
  impactPct: number  // Impact as percentage
}

export interface Factor {
  name: string
  index: string
  beta: number
}

export interface PortfolioRiskMetrics {
  // Основные метрики
  var95: number  // Value at Risk 95%
  var99: number  // Value at Risk 99%
  cvar95: number // Conditional VaR 95%
  cvar99: number // Conditional VaR 99%
  expectedReturn: number
  volatility: number
  sharpeRatio: number
  sortinoRatio?: number
  
  // Beta и факторы
  portfolioBeta: number
  factors?: Factor[]
  
  // Risk Contribution
  riskContributions: RiskContribution[]
  
  // Drawdown
  maxDrawdown: number
  averageDrawdown?: number
  
  // Liquidity (можно добавить позже)
  liquidityMetrics?: {
    daysToLiquidate: number
    bidAskSpreadCost: number
  }
  
  // Timestamp
  timestamp?: Date
}

export const useRiskMetricsStore = defineStore('riskMetrics', () => {
  const metrics = ref<PortfolioRiskMetrics | null>(null)
  const stressScenarios = ref<StressScenario[]>([])
  const totalEquity = ref(2400000) // Базовая стоимость портфеля
  
  /**
   * Обновляет риск-метрики из результатов оптимизации
   */
  const updateMetrics = (newMetrics: Partial<PortfolioRiskMetrics>) => {
    if (!metrics.value) {
      metrics.value = {
        var95: 0,
        var99: 0,
        cvar95: 0,
        cvar99: 0,
        expectedReturn: 0,
        volatility: 0,
        sharpeRatio: 0,
        portfolioBeta: 0.85,
        riskContributions: [],
        maxDrawdown: 0,
        timestamp: new Date()
      }
    }
    
    metrics.value = {
      ...metrics.value,
      ...newMetrics,
      timestamp: new Date()
    }
  }
  
  /**
   * Euler decomposition: RC_i = w_i * (Σw)_i / σ_p * VaR_total
   * Σ RC_i = VaR_total (Euler's theorem for homogeneous functions)
   */
  const calculateRiskContributions = (
    positions: Array<{ symbol: string; allocation: number; notional: number; color: string }>,
    portfolioVolatility: number,
    correlationMatrix: Array<{ label: string; values: number[] }>,
    portfolioValue: number = totalEquity.value
  ): RiskContribution[] => {
    if (!positions.length || portfolioVolatility === 0) return []

    const totalNotional = positions.reduce((sum, p) => sum + p.notional, 0)
    if (totalNotional === 0) return []

    const n = positions.length
    const w = positions.map(p => p.notional / totalNotional)

    // Build covariance matrix from correlation matrix + individual vols
    // σ_i estimated from portfolioVolatility scaled by weight (fallback)
    const vols = positions.map(() => portfolioVolatility)

    // Σ_ij = ρ_ij * σ_i * σ_j
    const covMatrix: number[][] = Array.from({ length: n }, () => Array(n).fill(0))
    for (let i = 0; i < n; i++) {
      const corrRow = correlationMatrix.find(r => r.label === positions[i].symbol)
      for (let j = 0; j < n; j++) {
        const rho = corrRow && j < corrRow.values.length ? corrRow.values[j] : (i === j ? 1.0 : 0.3)
        covMatrix[i][j] = rho * vols[i] * vols[j]
      }
    }

    // (Σ·w)_i = Σ_j Σ_ij * w_j
    const covW = covMatrix.map(row =>
      row.reduce((sum, val, j) => sum + val * w[j], 0)
    )

    // σ_p = sqrt(w' Σ w)
    const sigmaP = Math.sqrt(w.reduce((sum, wi, i) => sum + wi * covW[i], 0))
    if (sigmaP < 1e-12) return []

    const z = 1.645 // 95% confidence
    const totalVaR = z * sigmaP * portfolioValue

    // RC_i = w_i * z * (Σw)_i / σ_p * portfolioValue
    const contributions: RiskContribution[] = positions.map((pos, i) => {
      const rc = w[i] * z * covW[i] / sigmaP * portfolioValue
      return {
        symbol: pos.symbol,
        weight: w[i] * 100,
        contribution: rc,
        percentRisk: totalVaR > 0 ? (rc / totalVaR) * 100 : 0,
        color: pos.color,
      }
    })

    return [...contributions].sort((a, b) => b.contribution - a.contribution)
  }
  
  /**
   * Вычисляет VaR и CVaR на основе волатильности портфеля (local fallback)
   */
  const calculateVaR = (
    portfolioValue: number,
    volatility: number,
    confidenceLevel: number = 0.95,
    timeHorizon: number = 1
  ): { var: number; cvar: number } => {
    const zScores: Record<number, number> = {
      0.90: 1.282,
      0.95: 1.645,
      0.99: 2.326,
      0.999: 3.090
    }

    const z = zScores[confidenceLevel] || 1.645
    const alpha = 1 - confidenceLevel
    const scaledVol = volatility * Math.sqrt(timeHorizon / 252)

    const varValue = portfolioValue * z * scaledVol

    // Analytical CVaR: sigma * phi(z) / alpha * portfolioValue
    const phi = Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI)
    const cvarValue = alpha > 0
      ? portfolioValue * scaledVol * phi / alpha
      : varValue * 1.25

    return {
      var: -varValue,
      cvar: -cvarValue
    }
  }

  /**
   * Вычисляет VaR/CVaR через backend Risk Engine API
   */
  const calculateVaRFromAPI = async (
    returns: number[],
    options: {
      method?: VaRMethod
      confidence?: number
      horizon?: number
      portfolioValue?: number
      useGarch?: boolean
      garchModel?: GarchModel
    } = {}
  ): Promise<VaRResult> => {
    const result = await apiCalculateVaR({
      returns,
      method: options.method ?? 'parametric',
      confidence: options.confidence ?? 0.95,
      horizon: options.horizon ?? 1,
      portfolio_value: options.portfolioValue ?? totalEquity.value,
      use_garch: options.useGarch ?? false,
      garch_model: options.garchModel ?? 'garch_11',
    })

    updateMetrics({
      var95: result.confidence === 0.95 ? -result.var : (metrics.value?.var95 ?? 0),
      cvar95: result.confidence === 0.95 ? -result.cvar : (metrics.value?.cvar95 ?? 0),
      var99: result.confidence === 0.99 ? -result.var : (metrics.value?.var99 ?? 0),
      cvar99: result.confidence === 0.99 ? -result.cvar : (metrics.value?.cvar99 ?? 0),
    })

    return result
  }
  
  /**
   * Обновляет stress scenarios
   */
  const updateStressScenarios = (scenarios: StressScenario[]) => {
    stressScenarios.value = scenarios
  }
  
  /**
   * Вычисляет Sortino Ratio = (E[R] - Rf) / σ_downside
   * где σ_downside = sqrt(E[min(R - Rf, 0)²])
   */
  const calculateSortinoRatio = (
    expectedReturn: number,
    returns: number[],
    riskFreeRate: number = 0
  ): number => {
    if (!returns.length) return 0
    const downsideSquares = returns
      .map(r => Math.min(r - riskFreeRate, 0))
      .map(d => d * d)
    const downsideVol = Math.sqrt(
      downsideSquares.reduce((sum, v) => sum + v, 0) / returns.length
    )
    return downsideVol > 1e-12 ? (expectedReturn - riskFreeRate) / downsideVol : 0
  }
  
  /**
   * Computed свойства для удобного доступа
   */
  const var95 = computed(() => metrics.value?.var95 || 0)
  const var99 = computed(() => metrics.value?.var99 || 0)
  const cvar95 = computed(() => metrics.value?.cvar95 || 0)
  const cvar99 = computed(() => metrics.value?.cvar99 || 0)
  const expectedReturn = computed(() => metrics.value?.expectedReturn || 0)
  const volatility = computed(() => metrics.value?.volatility || 0)
  const sharpeRatio = computed(() => metrics.value?.sharpeRatio || 0)
  const portfolioBeta = computed(() => metrics.value?.portfolioBeta || 0.85)
  const riskContributions = computed(() => metrics.value?.riskContributions || [])
  const maxDrawdown = computed(() => metrics.value?.maxDrawdown || 0)
  
  return {
    metrics,
    stressScenarios,
    totalEquity,
    updateMetrics,
    calculateRiskContributions,
    calculateVaR,
    calculateVaRFromAPI,
    updateStressScenarios,
    calculateSortinoRatio,
    // Computed
    var95,
    var99,
    cvar95,
    cvar99,
    expectedReturn,
    volatility,
    sharpeRatio,
    portfolioBeta,
    riskContributions,
    maxDrawdown
  }
})
