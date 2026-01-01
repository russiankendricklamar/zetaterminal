import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export const usePortfolioStore = defineStore('portfolio', () => {
  // State
  const kpis = ref({
    totalPnL: 0,
    var95: 0,
    expectedShortfall: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    ytdReturn: 0,
    lastUpdated: new Date()
  })

  const positions = ref([
    { symbol: 'SPY', type: 'ETF', notional: 500000, pnl: 12500, pnlPct: 2.5 },
    { symbol: 'TLT', type: 'Bond ETF', notional: 300000, pnl: 8900, pnlPct: 2.97 },
    { symbol: 'GC', type: 'Commodity', notional: 200000, pnl: -3200, pnlPct: -1.6 }
  ])

  const greeks = ref<any[]>([])
  const stressScenarios = ref<any[]>([])
  const modelDiagnostics = ref<any>({})
  const priceHistory = ref<any[]>([])
  const heatmapData = ref<any[]>([])

  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const selectedModel = ref('Lévy Process')
  const dateRange = ref({ start: new Date(), end: new Date() })

  // Computed
  const totalNotional = computed(() => 
    positions.value.reduce((sum, p) => sum + p.notional, 0)
  )

  const totalPnL = computed(() =>
    positions.value.reduce((sum, p) => sum + p.pnl, 0)
  )

  const portfolioReturn = computed(() =>
    (totalPnL.value / totalNotional.value) * 100
  )

  const riskMetrics = computed(() => ({
    var95: kpis.value.var95,
    expectedShortfall: kpis.value.expectedShortfall,
    sharpeRatio: kpis.value.sharpeRatio,
    maxDrawdown: kpis.value.maxDrawdown
  }))

  // Actions
  async function fetchKPIs() {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/kpis')
      kpis.value = {
        totalPnL: data.total_pnl,
        var95: data.var_95,
        expectedShortfall: data.expected_shortfall,
        sharpeRatio: data.sharpe_ratio,
        maxDrawdown: data.max_drawdown,
        ytdReturn: data.ytd_return,
        lastUpdated: new Date()
      }
    } catch (e) {
      error.value = `Failed to fetch KPIs: ${e}`
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchGreeks() {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/greeks')
      greeks.value = data.map((g: any) => ({
        position: g.position,
        delta: g.delta,
        gamma: g.gamma,
        vega: g.vega,
        theta: g.theta,
        rho: g.rho
      }))
    } catch (e) {
      error.value = `Failed to fetch Greeks: ${e}`
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchStressScenarios() {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/stress-testing')
      stressScenarios.value = data.map((s: any) => ({
        scenario: s.scenario,
        description: s.description,
        pnlImpact: s.pnl_impact,
        varChange: s.var_change,
        probability: s.probability
      }))
    } catch (e) {
      error.value = `Failed to fetch stress scenarios: ${e}`
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchModelDiagnostics() {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/model-diagnostics')
      modelDiagnostics.value = {
        modelName: data.model_name,
        ksTestPValue: data.ks_test_pvalue,
        backtestingAccuracy: data.backtesting_accuracy,
        parameters: data.parameters,
        lastUpdated: new Date()
      }
    } catch (e) {
      error.value = `Failed to fetch model diagnostics: ${e}`
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPriceHistory(asset: string = 'SPY', days: number = 60) {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/price-series', {
        params: { asset, days }
      })
      priceHistory.value = data.series.map((item: any) => ({
        date: new Date(item.date),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }))
    } catch (e) {
      error.value = `Failed to fetch price history: ${e}`
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchHeatmapData() {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/heatmap')
      heatmapData.value = data.map((item: any) => ({
        asset: item.asset,
        volatility: item.volatility,
        correlation: item.correlation,
        notional: item.notional,
        pnl: item.pnl,
        pnlPct: item.pnl_pct
      }))
    } catch (e) {
      error.value = `Failed to fetch heatmap data: ${e}`
      console.error(e)
    } finally {
      isLoading.value = false
    }
  }

  async function runMonteCarlo(
    nPaths: number = 10000,
    steps: number = 252,
    model: string = 'levy'
  ) {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.post('/monte-carlo', null, {
        params: {
          n_paths: nPaths,
          steps: steps,
          model: model
        }
      })

      return {
        nPaths: data.n_paths,
        steps: data.steps,
        results: {
          mean: data.results.mean,
          std: data.results.std,
          var95: data.results.var_95,
          var99: data.results.var_99,
          quantiles: data.results.quantiles
        },
        computationTime: data.computation_time_ms
      }
    } catch (e) {
      error.value = `Failed to run Monte Carlo: ${e}`
      console.error(e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function getBacktestResults(
    startDate?: string,
    endDate?: string
  ) {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.get('/backtest-results', {
        params: {
          start_date: startDate,
          end_date: endDate
        }
      })

      return {
        period: data.period,
        cumulativeReturn: data.cumulative_return,
        annualReturn: data.annual_return,
        volatility: data.volatility,
        sharpeRatio: data.sharpe_ratio,
        maxDrawdown: data.max_drawdown,
        winRate: data.win_rate,
        profitFactor: data.profit_factor
      }
    } catch (e) {
      error.value = `Failed to get backtest results: ${e}`
      console.error(e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function subscribeToLiveData(callback: (data: any) => void) {
    const ws = new WebSocket('ws://localhost:8000/ws/live-data')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      callback(data)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return ws
  }

  function subscribeToModelStream(callback: (data: any) => void) {
    const ws = new WebSocket('ws://localhost:8000/ws/model-stream')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      callback(data)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return ws
  }

  function setSelectedModel(model: string) {
    selectedModel.value = model
  }

  function setDateRange(start: Date, end: Date) {
    dateRange.value = { start, end }
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    kpis,
    positions,
    greeks,
    stressScenarios,
    modelDiagnostics,
    priceHistory,
    heatmapData,
    isLoading,
    error,
    selectedModel,
    dateRange,

    // Computed
    totalNotional,
    totalPnL,
    portfolioReturn,
    riskMetrics,

    // Actions
    fetchKPIs,
    fetchGreeks,
    fetchStressScenarios,
    fetchModelDiagnostics,
    fetchPriceHistory,
    fetchHeatmapData,
    runMonteCarlo,
    getBacktestResults,
    subscribeToLiveData,
    subscribeToModelStream,
    setSelectedModel,
    setDateRange,
    clearError
  }
})
