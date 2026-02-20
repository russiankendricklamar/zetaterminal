<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-blue">
          <FilterIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">СКРИНИНГ РЫНКА</h2>
          <p class="section-subtitle font-mono">MOEX И ЗАРУБЕЖНЫЕ АКЦИИ — ПОИСК И ФИЛЬТРАЦИЯ</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка...
    </div>

    <div class="flex-1 flex flex-col gap-6">
      <!-- ═══ MOEX Stocks ═══ -->
      <div v-if="section === 'EQS'" class="flex flex-col h-full gap-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Акции MOEX (TQBR)</h3>
          <button @click="loadMoexStocks" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="moexStocks.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
                <th class="p-4 font-bold cursor-pointer" @click="sortBy('ticker')">Тикер</th>
                <th class="p-4 font-bold">Название</th>
                <th class="p-4 font-bold text-right cursor-pointer" @click="sortBy('last')">Цена</th>
                <th class="p-4 font-bold text-right cursor-pointer" @click="sortBy('change_pct')">Изменение</th>
                <th class="p-4 font-bold text-right cursor-pointer" @click="sortBy('volume')">Объём</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="s in sortedMoexStocks" :key="s.ticker" class="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer">
                <td class="p-4">
                  <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ s.ticker }}</span>
                </td>
                <td class="p-4 text-gray-300 text-xs">{{ s.name }}</td>
                <td class="p-4 text-right font-bold text-white">{{ s.last != null ? s.last.toFixed(2) : '—' }}</td>
                <td class="p-4 text-right">
                  <span v-if="s.change_pct != null" :class="s.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono text-xs">
                    {{ s.change_pct >= 0 ? '+' : '' }}{{ s.change_pct.toFixed(2) }}%
                  </span>
                  <span v-else class="text-gray-500 text-xs">—</span>
                </td>
                <td class="p-4 text-right text-gray-400 text-xs">{{ s.volume != null ? formatVolume(s.volume) : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ International Stocks (yfinance) ═══ -->
      <div v-else-if="section === 'WLT'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Зарубежные акции (yfinance)</h3>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <input
              v-model="intlSearchQuery"
              type="text"
              placeholder="Введите тикеры через запятую: AAPL, MSFT, TSLA..."
              class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-blue-500/50 outline-none text-sm"
              @keydown.enter="loadIntlStocks"
            />
          </div>
          <button @click="loadIntlStocks" class="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-sm transition-colors">
            Загрузить
          </button>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            v-for="preset in presets"
            :key="preset.label"
            @click="intlSearchQuery = preset.tickers; loadIntlStocks()"
            class="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-lg border border-white/5 transition-colors"
          >
            {{ preset.label }}
          </button>
        </div>

        <div v-if="intlStocks.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
                <th class="p-4 font-bold">Тикер</th>
                <th class="p-4 font-bold">Компания</th>
                <th class="p-4 font-bold text-right">Цена</th>
                <th class="p-4 font-bold text-right">Изменение</th>
                <th class="p-4 font-bold text-right">P/E</th>
                <th class="p-4 font-bold text-right">Market Cap</th>
                <th class="p-4 font-bold text-right">Сектор</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="s in intlStocks" :key="s.ticker" class="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer">
                <td class="p-4 font-bold text-white">{{ s.ticker }}</td>
                <td class="p-4 text-xs text-gray-400">{{ s.name }}</td>
                <td class="p-4 text-right font-bold text-white">${{ s.price.toFixed(2) }}</td>
                <td :class="['p-4 text-right font-bold', s.changePercent >= 0 ? 'text-emerald-400' : 'text-rose-400']">
                  {{ s.changePercent >= 0 ? '+' : '' }}{{ s.changePercent.toFixed(2) }}%
                </td>
                <td class="p-4 text-right text-gray-400">{{ s.peRatio != null ? s.peRatio.toFixed(1) : '—' }}</td>
                <td class="p-4 text-right text-gray-400">{{ formatLargeNumber(s.marketCap) }}</td>
                <td class="p-4 text-right text-xs text-gray-500">{{ s.sector || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Выберите раздел
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { getMoexSecurities, type MoexSecurity } from '@/services/moexalgoService'
import { getMultipleStocks, type StockInfo } from '@/services/marketDataService'

const FilterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' }

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'EQS')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'EQS', label: 'Акции MOEX' },
  { id: 'WLT', label: 'Зарубежные акции' },
]

const loading = ref(false)

interface MoexStock {
  ticker: string
  name: string
  last: number | null
  change_pct: number | null
  volume: number | null
}

const moexStocks = ref<MoexStock[]>([])
const sortKey = ref<string>('volume')
const sortAsc = ref(false)

const sortedMoexStocks = computed(() => {
  const sorted = [...moexStocks.value]
  sorted.sort((a, b) => {
    const av = (a as Record<string, unknown>)[sortKey.value] as number | null
    const bv = (b as Record<string, unknown>)[sortKey.value] as number | null
    const diff = ((av ?? 0) - (bv ?? 0))
    return sortAsc.value ? diff : -diff
  })
  return sorted
})

const sortBy = (key: string) => {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = false
  }
}

const loadMoexStocks = async () => {
  loading.value = true
  try {
    const res = await getMoexSecurities('TQBR', 'shares', 'stock')
    moexStocks.value = res.securities
      .filter((s: MoexSecurity) => s.last != null)
      .map((s: MoexSecurity) => ({
        ticker: s.secid,
        name: s.name || s.secid,
        last: s.last,
        change_pct: s.change_pct,
        volume: s.volume,
      }))
  } catch {
    moexStocks.value = []
  } finally {
    loading.value = false
  }
}

// International stocks
const intlSearchQuery = ref('AAPL, MSFT, NVDA, TSLA, AMZN, META, GOOGL')
const intlStocks = ref<StockInfo[]>([])

const presets = [
  { label: 'FAANG+', tickers: 'AAPL, MSFT, NVDA, TSLA, AMZN, META, GOOGL' },
  { label: 'Банки', tickers: 'JPM, BAC, GS, MS, C, WFC' },
  { label: 'Энергетика', tickers: 'XOM, CVX, COP, SLB, EOG' },
  { label: 'Здравоохранение', tickers: 'JNJ, UNH, LLY, ABBV, PFE' },
]

const loadIntlStocks = async () => {
  const tickers = intlSearchQuery.value.split(',').map((t) => t.trim()).filter(Boolean)
  if (tickers.length === 0) return
  loading.value = true
  try {
    intlStocks.value = await getMultipleStocks(tickers)
  } catch {
    intlStocks.value = []
  } finally {
    loading.value = false
  }
}

const formatVolume = (vol: number): string => {
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K`
  return vol.toString()
}

const formatLargeNumber = (n: number | undefined): string => {
  if (n == null) return '—'
  if (n >= 1e12) return `${(n / 1e12).toFixed(2)}T`
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`
  return n.toLocaleString()
}

onMounted(() => {
  loadMoexStocks()
})
</script>
