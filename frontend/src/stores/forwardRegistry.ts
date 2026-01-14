import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ForwardValuationResponse } from '@/services/forwardService'

export interface ForwardRegistryItem {
  id?: string
  forwardType: string
  spotPrice: number
  timeToMaturity: number
  marketForwardPrice: number
  contractSize?: number
  valuationDate?: string
  expirationDate?: string
  
  // Cost-of-Carry параметры
  dividendYield?: number
  carryingCost?: number
  convenienceYield?: number
  riskFreeRate?: number
  repoRate?: number
  
  // Bond параметры
  accruedInterest?: number
  couponRate?: number
  couponFrequency?: number
  faceValue?: number
  lastCouponDate?: string
  maturityDate?: string
  dayCountConvention?: string
  
  // FX параметры
  fxBuyCurrency?: string
  fxSellCurrency?: string
  fxBuyAmount?: number
  fxSellAmount?: number
  fxInternalRate?: number
  fxExternalRate?: number
  
  // Результаты расчета (опционально)
  valuationResult?: ForwardValuationResponse | null
}

export const useForwardRegistryStore = defineStore('forwardRegistry', () => {
  // Реестр форвардов
  const registryForwards = ref<ForwardRegistryItem[]>([])
  
  // Результаты расчетов для каждого форварда
  const forwardResults = ref<(ForwardValuationResponse | null)[]>([])

  // Дата оценки
  const valuationDate = ref<string>(new Date().toISOString().split('T')[0])

  // Computed: общее количество форвардов
  const totalForwards = computed(() => registryForwards.value.length)

  // Computed: форварды с рассчитанными результатами
  const calculatedForwards = computed(() => {
    return registryForwards.value.filter((_, idx) => forwardResults.value[idx] !== null && forwardResults.value[idx] !== undefined)
  })

  // Computed: общая стоимость портфеля
  const totalForwardValue = computed(() => {
    return forwardResults.value.reduce((sum, result, idx) => {
      if (result && registryForwards.value[idx]) {
        const contractSize = registryForwards.value[idx].contractSize || 1_000_000
        return sum + (result.forwardValue * contractSize || 0)
      }
      return sum
    }, 0)
  })

  // Computed: общая Delta
  const totalDelta = computed(() => {
    return forwardResults.value.reduce((sum, result, idx) => {
      if (result && registryForwards.value[idx]) {
        const contractSize = registryForwards.value[idx].contractSize || 1_000_000
        return sum + (result.delta * contractSize || 0)
      }
      return sum
    }, 0)
  })

  // Computed: общая Rho
  const totalRho = computed(() => {
    return forwardResults.value.reduce((sum, result, idx) => {
      if (result && registryForwards.value[idx]) {
        const contractSize = registryForwards.value[idx].contractSize || 1_000_000
        return sum + (result.rho * contractSize || 0)
      }
      return sum
    }, 0)
  })

  // Computed: общая DV01 (для bond форвардов)
  const totalDv01 = computed(() => {
    return forwardResults.value.reduce((sum, result, idx) => {
      if (result && result.dv01 && registryForwards.value[idx]) {
        const contractSize = registryForwards.value[idx].contractSize || 1_000_000
        const faceValue = registryForwards.value[idx].faceValue || 100
        return sum + (result.dv01 * contractSize * faceValue / 100 || 0)
      }
      return sum
    }, 0)
  })

  // Добавить форвард в реестр
  function addForward(forward: ForwardRegistryItem) {
    const newForward = {
      ...forward,
      id: forward.id || `forward_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
    registryForwards.value.push(newForward)
    forwardResults.value.push(null)
    return newForward.id
  }

  // Обновить форвард в реестре
  function updateForward(id: string, forward: Partial<ForwardRegistryItem>) {
    const index = registryForwards.value.findIndex(f => f.id === id)
    if (index !== -1) {
      registryForwards.value[index] = { ...registryForwards.value[index], ...forward }
    }
  }

  // Удалить форвард из реестра
  function removeForward(id: string) {
    const index = registryForwards.value.findIndex(f => f.id === id)
    if (index !== -1) {
      registryForwards.value.splice(index, 1)
      forwardResults.value.splice(index, 1)
    }
  }

  // Загрузить реестр форвардов (из Excel или вручную)
  function loadRegistry(forwards: ForwardRegistryItem[]) {
    registryForwards.value = forwards.map((forward, idx) => ({
      ...forward,
      id: forward.id || `forward_${Date.now()}_${idx}_${Math.random().toString(36).substr(2, 9)}`
    }))
    forwardResults.value = new Array(forwards.length).fill(null)
  }

  // Очистить реестр
  function clearRegistry() {
    registryForwards.value = []
    forwardResults.value = []
  }

  // Установить результат расчета для форварда
  function setForwardResult(index: number, result: ForwardValuationResponse | null) {
    if (index >= 0 && index < forwardResults.value.length) {
      forwardResults.value[index] = result
      if (index < registryForwards.value.length) {
        registryForwards.value[index].valuationResult = result || undefined
      }
    }
  }

  // Установить результаты для всех форвардов
  function setAllResults(results: (ForwardValuationResponse | null)[]) {
    forwardResults.value = [...results]
    results.forEach((result, idx) => {
      if (idx < registryForwards.value.length) {
        registryForwards.value[idx].valuationResult = result || undefined
      }
    })
  }

  // Установить дату оценки
  function setValuationDate(date: string) {
    valuationDate.value = date
  }

  // Получить форвард по индексу
  function getForwardByIndex(index: number): ForwardRegistryItem | null {
    return registryForwards.value[index] || null
  }

  // Получить результат расчета по индексу
  function getResultByIndex(index: number): ForwardValuationResponse | null {
    return forwardResults.value[index] || null
  }

  // Получить форварды по типу
  function getForwardsByType(type: string): ForwardRegistryItem[] {
    return registryForwards.value.filter(forward => forward.forwardType === type)
  }

  // Получить форварды по типу с результатами
  function getForwardsByTypeWithResults(type: string): Array<{ forward: ForwardRegistryItem; result: ForwardValuationResponse | null }> {
    return registryForwards.value
      .map((forward, idx) => ({
        forward,
        result: forwardResults.value[idx] || null
      }))
      .filter(item => item.forward.forwardType === type)
  }

  return {
    // State
    registryForwards,
    forwardResults,
    valuationDate,
    
    // Computed
    totalForwards,
    calculatedForwards,
    totalForwardValue,
    totalDelta,
    totalRho,
    totalDv01,
    
    // Actions
    addForward,
    updateForward,
    removeForward,
    loadRegistry,
    clearRegistry,
    setForwardResult,
    setAllResults,
    setValuationDate,
    getForwardByIndex,
    getResultByIndex,
    getForwardsByType,
    getForwardsByTypeWithResults
  }
})
