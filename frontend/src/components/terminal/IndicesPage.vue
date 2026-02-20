<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-blue">
          <GlobeIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ИНДЕКСЫ</h2>
          <p class="section-subtitle font-mono">МИРОВЫЕ РЫНКИ, MOEX И СОСТАВ</p>
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
      Загрузка индексов...
    </div>

    <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono mx-4">
      {{ loadError }}
    </div>

    <div class="flex-1 flex flex-col gap-4">
      <!-- ═══ MOEX Indices ═══ -->
      <div v-if="section === 'WINDEX'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Индексы MOEX</h3>
          <button @click="loadData" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="moexIndices.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="idx in moexIndices"
            :key="idx.ticker"
            class="p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all cursor-pointer"
          >
            <div class="flex justify-between items-start mb-2">
              <div>
                <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ idx.ticker }}</span>
                <span class="text-xs text-gray-500 ml-2">{{ idx.name }}</span>
              </div>
            </div>
            <div class="text-2xl font-bold text-white mt-2">{{ idx.last != null ? idx.last.toFixed(2) : '—' }}</div>
            <div v-if="idx.change_pct != null" :class="['text-xs font-bold mt-1', idx.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ International via yfinance ═══ -->
      <div v-else-if="section === 'IMAP'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Международные индексы (yfinance)</h3>
        </div>

        <div v-for="region in regions" :key="region.name" class="bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h3 class="font-bold text-white">{{ region.name }}</h3>
          </div>
          <table class="w-full text-left">
            <thead>
              <tr class="text-xs text-gray-500 uppercase">
                <th class="p-4">Индекс</th>
                <th class="p-4">Тикер</th>
                <th class="p-4 text-right">Последняя</th>
                <th class="p-4 text-right">Изменение</th>
                <th class="p-4 text-right">Объём</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="idx in region.indices" :key="idx.ticker" class="border-t border-white/5 hover:bg-white/5 cursor-pointer">
                <td class="p-4 font-bold text-white">{{ idx.name }}</td>
                <td class="p-4 text-gray-400">{{ idx.ticker }}</td>
                <td class="p-4 text-right">{{ idx.price != null ? idx.price.toFixed(2) : '—' }}</td>
                <td :class="['p-4 text-right font-bold', (idx.changePercent || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400']">
                  {{ idx.changePercent != null ? ((idx.changePercent >= 0 ? '+' : '') + idx.changePercent.toFixed(2) + '%') : '—' }}
                </td>
                <td class="p-4 text-right text-gray-500 text-xs">{{ idx.volume != null ? formatVolume(idx.volume) : '—' }}</td>
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
import { ref, watch, onMounted, defineComponent, h } from 'vue'
import { getMoexIndex, type MoexIndexData } from '@/services/moexalgoService'
import { getMultipleStocks, type StockInfo } from '@/services/marketDataService'

const GlobeIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }), h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'WINDEX')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'WINDEX', label: 'Индексы MOEX' },
  { id: 'IMAP', label: 'Международные' },
]

const loading = ref(false)
const loadError = ref<string | null>(null)

interface IndexItem {
  ticker: string
  name: string
  last: number | null
  change_pct: number | null
}

const moexIndices = ref<IndexItem[]>([])

const MOEX_INDEX_IDS = ['IMOEX', 'RTSI', 'MOEXBC', 'MOEXBMI', 'MOEXFN', 'MOEXOG', 'MOEXMM', 'MOEXEU', 'MOEXTL', 'MOEXCN', 'MOEXRE', 'MOEXINN', 'MOEXCH', 'MOEXTN']

interface IntlIndex {
  ticker: string
  name: string
  price: number | null
  changePercent: number | null
  volume: number | null
}

interface Region {
  name: string
  indices: IntlIndex[]
}

const regions = ref<Region[]>([])

const INTL_TICKERS: Record<string, { tickers: string[]; names: Record<string, string> }> = {
  Americas: {
    tickers: ['^GSPC', '^IXIC', '^DJI', '^RUT'],
    names: { '^GSPC': 'S&P 500', '^IXIC': 'Nasdaq Composite', '^DJI': 'Dow Jones', '^RUT': 'Russell 2000' },
  },
  EMEA: {
    tickers: ['^FTSE', '^GDAXI', '^FCHI', '^STOXX50E'],
    names: { '^FTSE': 'FTSE 100', '^GDAXI': 'DAX', '^FCHI': 'CAC 40', '^STOXX50E': 'Euro Stoxx 50' },
  },
  APAC: {
    tickers: ['^N225', '^HSI', '000001.SS', '^KS11'],
    names: { '^N225': 'Nikkei 225', '^HSI': 'Hang Seng', '000001.SS': 'Shanghai Composite', '^KS11': 'KOSPI' },
  },
}

const loadData = async () => {
  loading.value = true
  loadError.value = null
  try {
    // Load MOEX indices
    const moexResults = await Promise.allSettled(
      MOEX_INDEX_IDS.map((id) => getMoexIndex(id))
    )

    const loadedIndices: IndexItem[] = []
    moexResults.forEach((res, i) => {
      if (res.status === 'fulfilled') {
        const data = res.value as { analytics?: Array<Record<string, unknown>> }
        if (data.analytics && data.analytics.length > 0) {
          const a = data.analytics[0]
          loadedIndices.push({
            ticker: MOEX_INDEX_IDS[i],
            name: (a.short_name as string) || MOEX_INDEX_IDS[i],
            last: (a.close as number) || (a.last as number) || null,
            change_pct: (a.change_pct as number) ?? null,
          })
        }
      }
    })
    moexIndices.value = loadedIndices

    // Load international indices
    const allIntlTickers = Object.values(INTL_TICKERS).flatMap((r) => r.tickers)
    try {
      const intlStocks = await getMultipleStocks(allIntlTickers)
      const stockMap = new Map<string, StockInfo>()
      intlStocks.forEach((s) => stockMap.set(s.ticker || s.symbol, s))

      const loadedRegions: Region[] = []
      for (const [regionName, config] of Object.entries(INTL_TICKERS)) {
        const indices: IntlIndex[] = config.tickers.map((t) => {
          const s = stockMap.get(t)
          return {
            ticker: t,
            name: config.names[t] || t,
            price: s?.price ?? null,
            changePercent: s?.changePercent ?? null,
            volume: s?.volume ?? null,
          }
        })
        loadedRegions.push({ name: regionName, indices })
      }
      regions.value = loadedRegions
    } catch {
      // International indices failed, still show MOEX
    }
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки'
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

onMounted(() => {
  loadData()
})
</script>
