<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-orange">
          <BoxIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">СЫРЬЁ</h2>
          <p class="section-subtitle font-mono">ЭНЕРГОРЕСУРСЫ, МЕТАЛЛЫ, АГРОКОМПЛЕКС</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка котировок сырья...
    </div>

    <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono mx-4">
      {{ loadError }}
    </div>

    <div class="flex-1 flex flex-col gap-6">
      <!-- ═══ Global Commodities ═══ -->
      <div v-if="section === 'GLCO'" class="flex flex-col h-full gap-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Global Benchmark Prices</h3>
          <button @click="loadCommodities" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="item in commodities"
            :key="item.ticker"
            class="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all cursor-pointer group"
          >
            <div class="flex justify-between items-start mb-2">
              <h4 class="text-sm font-bold text-gray-300 group-hover:text-white">{{ item.name }}</h4>
              <span class="text-[10px] text-gray-500 font-mono">{{ item.ticker }}</span>
            </div>
            <div class="flex items-baseline gap-2 mb-1">
              <span class="text-2xl font-bold text-white">{{ item.price != null ? formatPrice(item.price) : '—' }}</span>
              <span class="text-xs text-gray-500">{{ item.currency }}</span>
            </div>
            <div v-if="item.changePercent != null" :class="['text-xs font-bold', item.changePercent >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ CBR Precious Metals ═══ -->
      <div v-else-if="section === 'NRG'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Драгоценные металлы — Банк России</h3>
        <div v-if="metals.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="metal in metals" :key="metal.name" class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">{{ metal.name }}</h3>
            <div class="text-3xl font-bold text-white">{{ metal.price.toFixed(2) }}</div>
            <div class="text-xs text-gray-500 mt-1">RUB / грамм</div>
            <div class="text-xs text-gray-500 mt-1">{{ metal.date }}</div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет данных по металлам
        </div>
      </div>

      <!-- ═══ Commodity Tickers (yfinance) ═══ -->
      <div v-else-if="section === 'NGAS'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Котировки через yfinance</h3>
        <div v-if="yfinanceCommodities.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5">
                <th class="p-4">Тикер</th>
                <th class="p-4">Название</th>
                <th class="p-4 text-right">Цена</th>
                <th class="p-4 text-right">Изменение</th>
                <th class="p-4 text-right">Объём</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="c in yfinanceCommodities" :key="c.ticker" class="border-b border-white/5 hover:bg-white/5">
                <td class="p-4">
                  <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ c.ticker }}</span>
                </td>
                <td class="p-4 text-gray-300">{{ c.name }}</td>
                <td class="p-4 text-right font-bold text-white">{{ c.price.toFixed(2) }}</td>
                <td class="p-4 text-right">
                  <span :class="c.changePercent >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono text-xs">
                    {{ c.changePercent >= 0 ? '+' : '' }}{{ c.changePercent.toFixed(2) }}%
                  </span>
                </td>
                <td class="p-4 text-right text-gray-400 text-xs">{{ formatVolume(c.volume) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Загрузка...
        </div>
      </div>

      <div v-else class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Выберите раздел
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineComponent, h } from 'vue'
import { getCbrPreciousMetals, type CbrPreciousMetals } from '@/services/macroDataService'
import { getMultipleStocks, type StockInfo } from '@/services/marketDataService'

const BoxIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('path', { d: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z' }), h('polyline', { points: '3.27 6.96 12 12.01 20.73 6.96' }), h('line', { x1: '12', y1: '22.08', x2: '12', y2: '12' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'GLCO')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'GLCO', label: 'Международное сырьё' },
  { id: 'NRG', label: 'Металлы ЦБР' },
  { id: 'NGAS', label: 'Котировки yfinance' },
]

const loading = ref(false)
const loadError = ref<string | null>(null)

interface CommodityItem {
  ticker: string
  name: string
  price: number | null
  changePercent: number | null
  currency: string
}

const commodities = ref<CommodityItem[]>([])
const metals = ref<Array<{ name: string; price: number; date: string }>>([])
const yfinanceCommodities = ref<Array<{ ticker: string; name: string; price: number; changePercent: number; volume: number }>>([])

const COMMODITY_TICKERS = ['GC=F', 'SI=F', 'CL=F', 'NG=F', 'HG=F', 'ZC=F', 'ZS=F', 'ZW=F']
const COMMODITY_NAMES: Record<string, string> = {
  'GC=F': 'Gold', 'SI=F': 'Silver', 'CL=F': 'Crude Oil (WTI)', 'NG=F': 'Natural Gas',
  'HG=F': 'Copper', 'ZC=F': 'Corn', 'ZS=F': 'Soybeans', 'ZW=F': 'Wheat',
}

const loadCommodities = async () => {
  loading.value = true
  loadError.value = null
  try {
    const [stocksRes, metalsRes] = await Promise.allSettled([
      getMultipleStocks(COMMODITY_TICKERS),
      getCbrPreciousMetals(),
    ])

    if (stocksRes.status === 'fulfilled') {
      commodities.value = stocksRes.value.map((s) => ({
        ticker: s.ticker || s.symbol,
        name: COMMODITY_NAMES[s.ticker || s.symbol] || s.name,
        price: s.price,
        changePercent: s.changePercent,
        currency: s.currency || 'USD',
      }))

      yfinanceCommodities.value = stocksRes.value.map((s) => ({
        ticker: s.ticker || s.symbol,
        name: s.name || COMMODITY_NAMES[s.ticker || s.symbol] || s.ticker,
        price: s.price,
        changePercent: s.changePercent,
        volume: s.volume,
      }))
    }

    if (metalsRes.status === 'fulfilled') {
      const metalNames: Record<string, string> = { '1': 'Золото', '2': 'Серебро', '3': 'Платина', '4': 'Палладий' }
      const metalData: Array<{ name: string; price: number; date: string }> = []
      for (const [code, entries] of Object.entries(metalsRes.value.metals)) {
        if (entries.length > 0) {
          const latest = entries[0]
          metalData.push({
            name: metalNames[code] || `Металл ${code}`,
            price: latest.price,
            date: latest.date,
          })
        }
      }
      metals.value = metalData
    }
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const formatPrice = (price: number): string => {
  if (price >= 1000) return price.toLocaleString('en-US', { maximumFractionDigits: 2 })
  return price.toFixed(2)
}

const formatVolume = (vol: number): string => {
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K`
  return vol.toString()
}

onMounted(() => {
  loadCommodities()
})
</script>
