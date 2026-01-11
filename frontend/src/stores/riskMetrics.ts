/**
 * Store для риск-метрик портфеля
 * Получает данные из CCMVOptimization и предоставляет их для GreekParameters
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

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
   * Вычисляет Risk Contribution (Marginal VaR) для каждого актива
   */
  const calculateRiskContributions = (
    positions: Array<{ symbol: string; allocation: number; notional: number; color: string }>,
    portfolioVolatility: number,
    correlationMatrix: Array<{ label: string; values: number[] }>,
    portfolioValue: number = totalEquity.value
  ): RiskContribution[] => {
    if (!positions.length || portfolioVolatility === 0) return []
    
    // Вычисляем веса активов
    const totalNotional = positions.reduce((sum, p) => sum + p.notional, 0)
    if (totalNotional === 0) return []
    
    // Вычисляем ковариации активов с портфелем
    const contributions: RiskContribution[] = []
    
    positions.forEach((pos, idx) => {
      const weight = pos.notional / totalNotional
      
      // Находим корреляции этого актива со всеми другими
      const corrRow = correlationMatrix.find(r => r.label === pos.symbol)
      if (!corrRow) return
      
      // Упрощенный расчет Marginal VaR
      // В реальности нужно использовать матрицу ковариаций и градиент VaR
      // Здесь используем упрощенную формулу: contribution ≈ weight * volatility * correlation_with_portfolio
      let avgCorrelation = 0
      positions.forEach((otherPos, otherIdx) => {
        if (otherIdx < corrRow.values.length) {
          avgCorrelation += corrRow.values[otherIdx] * (otherPos.notional / totalNotional)
        }
      })
      
      // Marginal VaR contribution (упрощенная формула)
      const marginalVaR = portfolioVolatility * weight * avgCorrelation * portfolioValue
      contributions.push({
        symbol: pos.symbol,
        weight: weight * 100,
        contribution: Math.abs(marginalVaR),
        percentRisk: 0, // Вычислим после
        color: pos.color
      })
    })
    
    // Нормализуем проценты
    const totalContribution = contributions.reduce((sum, c) => sum + c.contribution, 0)
    if (totalContribution > 0) {
      contributions.forEach(c => {
        c.percentRisk = (c.contribution / totalContribution) * 100
      })
    }
    
    return contributions.sort((a, b) => b.contribution - a.contribution)
  }
  
  /**
   * Вычисляет VaR и CVaR на основе волатильности портфеля
   */
  const calculateVaR = (
    portfolioValue: number,
    volatility: number,
    confidenceLevel: number = 0.95,
    timeHorizon: number = 1  // в днях
  ): { var: number; cvar: number } => {
    // Z-score для нормального распределения
    const zScores: Record<number, number> = {
      0.90: 1.282,
      0.95: 1.645,
      0.99: 2.326,
      0.999: 3.090
    }
    
    const z = zScores[confidenceLevel] || 1.645
    const scaledVol = volatility * Math.sqrt(timeHorizon / 252) // Annualized to daily
    
    // VaR = Portfolio Value * Z * Volatility
    const varValue = portfolioValue * z * scaledVol
    
    // CVaR ≈ VaR * 1.25 (упрощенная формула для нормального распределения)
    const cvarValue = varValue * 1.25
    
    return {
      var: -varValue, // Negative для отображения как потери
      cvar: -cvarValue
    }
  }
  
  /**
   * Обновляет stress scenarios
   */
  const updateStressScenarios = (scenarios: StressScenario[]) => {
    stressScenarios.value = scenarios
  }
  
  /**
   * Вычисляет Sortino Ratio (аналогично Sharpe, но только учитывает негативную волатильность)
   */
  const calculateSortinoRatio = (expectedReturn: number, volatility: number): number => {
    // Упрощенная формула: Sortino ≈ Sharpe * 1.5 (обычно выше, так как учитывает только downside risk)
    const sharpe = volatility > 0 ? expectedReturn / volatility : 0
    return sharpe * 1.5
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
