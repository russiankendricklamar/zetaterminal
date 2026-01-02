import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

export const usePortfolioStore = defineStore('portfolio', () => {
  // State
  const kpis = ref({
    totalPnL: 15400,
    var95: 12500,
    expectedShortfall: 15200,
    sharpeRatio: 0.64,
    maxDrawdown: -12.4,
    ytdReturn: 8.2,
    lastUpdated: new Date()
  })

  // Расширенные данные позиций
  const positions = ref([
    { 
      symbol: 'SPY', 
      name: 'Акции (MSCI)',
      type: 'ETF', 
      notional: 450000, 
      pnl: 12500, 
      pnlPct: 2.5,
      allocation: 45, // Текущий вес %
      targetAllocation: 42, // Целевой вес %
      color: '#3b82f6' // Blue
    },
    { 
      symbol: 'AGG', 
      name: 'Облигации (AGG)',
      type: 'Bond ETF', 
      notional: 350000, 
      pnl: 8900, 
      pnlPct: 2.97,
      allocation: 35,
      targetAllocation: 38,
      color: '#10b981' // Green
    },
    { 
      symbol: 'GLD', 
      name: 'Товары (GLD)',
      type: 'Commodity', 
      notional: 120000, 
      pnl: -3200, 
      pnlPct: -1.6,
      allocation: 12,
      targetAllocation: 15,
      color: '#f59e0b' // Amber
    },
    { 
      symbol: 'VNQ', 
      name: 'Недвижимость (VNQ)',
      type: 'REIT', 
      notional: 80000, 
      pnl: 1500, 
      pnlPct: 1.8,
      allocation: 8,
      targetAllocation: 5,
      color: '#ef4444' // Red
    }
  ])

  // Результаты оптимизации
  const optimization = ref({
    targetSharpe: 0.714, // Был 0.640
    targetVol: 11.90,    // Была 12.80%
    targetReturn: 8.50,  // Был 8.20%
    improvements: {
      sharpe: 11.56,
      risk: 7.03,
      return: 3.66,
      costs: 0.50
    },
    riskFactors: {
      beta: 0.85,
      duration: 4.2,
      fxRisk: -0.15
    }
  })

  // ... (оставьте остальные методы fetch/computed без изменений) ...
  
  // Добавьте getters/computed если нужно
  const totalNotional = computed(() => positions.value.reduce((sum, p) => sum + p.notional, 0))

  return {
    kpis,
    positions,
    optimization, // Не забудьте экспортировать
    totalNotional,
    // ... экспортируйте методы fetch ...
  }
})
