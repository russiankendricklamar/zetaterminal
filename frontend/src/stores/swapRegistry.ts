import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SwapValuationResponse } from '@/services/swapService'

export interface SwapRegistryItem {
  id?: string
  notional: number
  tenor: number
  fixedRate: number
  floatingRate: number
  spread: number
  couponsPerYear: number
  discountRate: number
  volatility?: number
  swapType: string
  // Результаты расчета (опционально)
  valuationResult?: SwapValuationResponse | null
}

export const useSwapRegistryStore = defineStore('swapRegistry', () => {
  // Реестр свопов
  const registrySwaps = ref<SwapRegistryItem[]>([])
  
  // Результаты расчетов для каждого свопа
  const swapResults = ref<(SwapValuationResponse | null)[]>([])

  // Дата оценки
  const valuationDate = ref<string>(new Date().toISOString().split('T')[0])

  // Computed: общее количество свопов
  const totalSwaps = computed(() => registrySwaps.value.length)

  // Computed: свопы с рассчитанными результатами
  const calculatedSwaps = computed(() => {
    return registrySwaps.value.filter((_, idx) => swapResults.value[idx] !== null && swapResults.value[idx] !== undefined)
  })

  // Computed: общий DV01 портфеля
  const totalDv01 = computed(() => {
    return swapResults.value.reduce((sum, result) => {
      return sum + (result?.dv01 || 0)
    }, 0)
  })

  // Computed: общая стоимость портфеля
  const totalSwapValue = computed(() => {
    return swapResults.value.reduce((sum, result) => {
      return sum + (result?.swapValue || 0)
    }, 0)
  })

  // Computed: общая Convexity
  const totalConvexity = computed(() => {
    return swapResults.value.reduce((sum, result) => {
      return sum + (result?.convexity || 0)
    }, 0)
  })

  // Computed: общий Spread DV01
  const totalSpreadDv01 = computed(() => {
    return swapResults.value.reduce((sum, result) => {
      return sum + (result?.spreadDv01 || 0)
    }, 0)
  })

  // Добавить своп в реестр
  function addSwap(swap: SwapRegistryItem) {
    const newSwap = {
      ...swap,
      id: swap.id || `swap_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    }
    registrySwaps.value.push(newSwap)
    swapResults.value.push(null)
    return newSwap.id
  }

  // Обновить своп в реестре
  function updateSwap(id: string, swap: Partial<SwapRegistryItem>) {
    const index = registrySwaps.value.findIndex(s => s.id === id)
    if (index !== -1) {
      registrySwaps.value[index] = { ...registrySwaps.value[index], ...swap }
    }
  }

  // Удалить своп из реестра
  function removeSwap(id: string) {
    const index = registrySwaps.value.findIndex(s => s.id === id)
    if (index !== -1) {
      registrySwaps.value.splice(index, 1)
      swapResults.value.splice(index, 1)
    }
  }

  // Загрузить реестр свопов (из Excel или вручную)
  function loadRegistry(swaps: SwapRegistryItem[]) {
    registrySwaps.value = swaps.map((swap, idx) => ({
      ...swap,
      id: swap.id || `swap_${Date.now()}_${idx}_${Math.random().toString(36).substr(2, 9)}`
    }))
    swapResults.value = new Array(swaps.length).fill(null)
  }

  // Очистить реестр
  function clearRegistry() {
    registrySwaps.value = []
    swapResults.value = []
  }

  // Установить результат расчета для свопа
  function setSwapResult(index: number, result: SwapValuationResponse | null) {
    if (index >= 0 && index < swapResults.value.length) {
      swapResults.value[index] = result
      if (index < registrySwaps.value.length) {
        registrySwaps.value[index].valuationResult = result || undefined
      }
    }
  }

  // Установить результаты для всех свопов
  function setAllResults(results: (SwapValuationResponse | null)[]) {
    swapResults.value = [...results]
    results.forEach((result, idx) => {
      if (idx < registrySwaps.value.length) {
        registrySwaps.value[idx].valuationResult = result || undefined
      }
    })
  }

  // Установить дату оценки
  function setValuationDate(date: string) {
    valuationDate.value = date
  }

  // Получить своп по индексу
  function getSwapByIndex(index: number): SwapRegistryItem | null {
    return registrySwaps.value[index] || null
  }

  // Получить результат расчета по индексу
  function getResultByIndex(index: number): SwapValuationResponse | null {
    return swapResults.value[index] || null
  }

  // Получить свопы по типу
  function getSwapsByType(type: string): SwapRegistryItem[] {
    return registrySwaps.value.filter(swap => swap.swapType === type)
  }

  return {
    // State
    registrySwaps,
    swapResults,
    valuationDate,
    
    // Computed
    totalSwaps,
    calculatedSwaps,
    totalDv01,
    totalSwapValue,
    totalConvexity,
    totalSpreadDv01,
    
    // Actions
    addSwap,
    updateSwap,
    removeSwap,
    loadRegistry,
    clearRegistry,
    setSwapResult,
    setAllResults,
    setValuationDate,
    getSwapByIndex,
    getResultByIndex,
    getSwapsByType
  }
})
