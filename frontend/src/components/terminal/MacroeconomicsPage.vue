<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box">
          <GlobeIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">МАКРОЭКОНОМИКА</h2>
          <p class="section-subtitle font-mono">ИНДИКАТОРЫ, РЕЛИЗЫ И ЭКОНОМИЧЕСКАЯ ПОЛИТИКА</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="flex-1 flex flex-col gap-6">
      <!-- ECO: Ставки и курсы -->
      <div v-if="section === 'ECO'" class="flex flex-col gap-6">
        <!-- CBR Key Rate -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">Ключевая ставка ЦБ РФ</h3>
            <div v-if="cbrKeyRate" class="text-3xl font-bold text-white">{{ cbrKeyRate.current_rate }}%</div>
            <div v-else class="text-3xl font-bold text-gray-600">—</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">EUR/RUB (ECB)</h3>
            <div v-if="ecbRates" class="text-3xl font-bold text-white">{{ ecbRates.rates['RUB']?.toFixed(2) ?? '—' }}</div>
            <div v-else class="text-3xl font-bold text-gray-600">—</div>
            <div v-if="ecbRates" class="text-xs text-gray-500 mt-1">{{ ecbRates.date }}</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">EUR/USD (ECB)</h3>
            <div v-if="ecbRates" class="text-3xl font-bold text-white">{{ ecbRates.rates['USD']?.toFixed(4) ?? '—' }}</div>
            <div v-else class="text-3xl font-bold text-gray-600">—</div>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="ratesLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          Загрузка курсов...
        </div>

        <!-- CBR Daily Rates Table -->
        <div v-if="cbrRates" class="flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <h3 class="font-oswald text-sm text-gray-400 uppercase tracking-wider">КУРСЫ ЦБ РФ НА {{ cbrRates.date }}</h3>
          </div>
          <div class="overflow-auto rounded-2xl border border-white/5 bg-black/20">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0">
                  <th class="p-3">Код</th>
                  <th class="p-3">Валюта</th>
                  <th class="p-3 text-right">Номинал</th>
                  <th class="p-3 text-right">Курс</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono text-gray-300">
                <tr v-for="rate in cbrRates.rates" :key="rate.char_code" class="border-b border-white/5 hover:bg-white/5">
                  <td class="p-3"><span class="text-xs font-bold bg-white/10 px-1.5 py-0.5 rounded text-white">{{ rate.char_code }}</span></td>
                  <td class="p-3 text-gray-400">{{ rate.name }}</td>
                  <td class="p-3 text-right text-gray-500">{{ rate.nominal }}</td>
                  <td class="p-3 text-right font-bold text-white">{{ rate.value.toFixed(4) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Error -->
        <div v-if="ratesError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono">
          {{ ratesError }}
        </div>
      </div>

      <!-- ECST: FRED Time Series -->
      <div v-else-if="section === 'ECST'" class="flex flex-col gap-6">
        <div class="flex items-center gap-4">
          <div class="search-box max-w-md flex-1">
            <input
              v-model="fredSearchQuery"
              type="text"
              placeholder="ПОИСК СЕРИИ FRED (GDP, CPI, UNRATE...)"
              class="w-full bg-transparent text-sm font-mono text-white placeholder-gray-500 outline-none"
              @keydown.enter="searchFred"
            />
          </div>
          <button @click="searchFred" class="btn btn-primary text-xs">ПОИСК</button>
        </div>

        <!-- Quick series buttons -->
        <div class="flex flex-wrap gap-2">
          <button
            v-for="s in quickSeries"
            :key="s.id"
            @click="loadFredSeries(s.id)"
            :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all border', activeFredSeries === s.id ? 'bg-white/10 text-white border-white/20' : 'text-gray-500 border-white/5 hover:text-white hover:border-white/20']"
          >
            {{ s.label }}
          </button>
        </div>

        <!-- Loading -->
        <div v-if="fredLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          Загрузка данных FRED...
        </div>

        <!-- FRED Search Results -->
        <div v-if="fredSearchResults.length > 0 && !fredSeriesData" class="flex flex-col gap-2">
          <h3 class="font-oswald text-sm text-gray-400 uppercase">Результаты поиска</h3>
          <div
            v-for="series in fredSearchResults"
            :key="series.id"
            @click="loadFredSeries(series.id)"
            class="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/20 cursor-pointer transition-all"
          >
            <div class="flex items-center justify-between">
              <div>
                <span class="font-mono text-xs text-orange-400">{{ series.id }}</span>
                <h4 class="text-sm text-white mt-1">{{ series.title }}</h4>
                <div class="flex gap-3 mt-1 text-xs text-gray-500 font-mono">
                  <span>{{ series.frequency }}</span>
                  <span>{{ series.units }}</span>
                </div>
              </div>
              <span class="text-xs text-gray-500">{{ series.observation_start }} — {{ series.observation_end }}</span>
            </div>
          </div>
        </div>

        <!-- FRED Series Data Table -->
        <div v-if="fredSeriesData" class="flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <h3 class="font-oswald text-sm text-gray-400 uppercase tracking-wider">
              {{ fredSeriesData.series_id }} — {{ fredSeriesData.count }} наблюдений
            </h3>
            <button @click="fredSeriesData = null" class="text-xs text-gray-500 hover:text-white font-mono">НАЗАД</button>
          </div>
          <div class="overflow-auto rounded-2xl border border-white/5 bg-black/20 max-h-[500px]">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0">
                  <th class="p-3">Дата</th>
                  <th class="p-3 text-right">Значение</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono text-gray-300">
                <tr v-for="obs in fredSeriesData.observations" :key="obs.date" class="border-b border-white/5 hover:bg-white/5">
                  <td class="p-3 text-gray-400">{{ obs.date }}</td>
                  <td class="p-3 text-right font-bold text-white">{{ obs.value ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!fredLoading && !fredSeriesData && fredSearchResults.length === 0" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Выберите серию из быстрых кнопок или введите запрос
        </div>
      </div>

      <!-- ECFC: Forecasts (FRED search + compare) -->
      <div v-else-if="section === 'ECFC'" class="flex flex-col gap-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">Global Growth (2025E)</h3>
            <div class="text-3xl font-bold text-white">2.9%</div>
            <div class="text-xs text-rose-400 mt-1">Revised Down</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">US Recession Prob</h3>
            <div class="text-3xl font-bold text-orange-400">45%</div>
            <div class="text-xs text-gray-500 mt-1">Next 12 Months</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">Peak Rates (Fed)</h3>
            <div class="text-3xl font-bold text-emerald-400">5.50%</div>
          </div>
        </div>

        <!-- CBR Key Rate History -->
        <div v-if="cbrKeyRate && cbrKeyRate.history.length > 0" class="flex flex-col gap-3">
          <h3 class="font-oswald text-sm text-gray-400 uppercase tracking-wider">ИСТОРИЯ КЛЮЧЕВОЙ СТАВКИ ЦБ РФ</h3>
          <div class="overflow-auto rounded-2xl border border-white/5 bg-black/20 max-h-[400px]">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0">
                  <th class="p-3">Дата</th>
                  <th class="p-3 text-right">Ставка</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono text-gray-300">
                <tr v-for="entry in cbrKeyRate.history" :key="entry.date" class="border-b border-white/5 hover:bg-white/5">
                  <td class="p-3 text-gray-400">{{ entry.date }}</td>
                  <td class="p-3 text-right font-bold text-white">{{ entry.rate }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ECWB: Workbench placeholder -->
      <div v-else-if="section === 'ECWB'" class="flex items-center justify-center h-full text-gray-500 font-mono text-sm">
        [Economic Workbench — Multi-series FRED chart overlay]
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, defineComponent, h } from 'vue'
import {
  getFredSeries,
  searchFredSeries,
  getEcbLatestRates,
  getCbrRates,
  getCbrKeyRate,
  type FredSeriesData,
  type FredSeriesInfo,
  type EcbRates,
  type CbrDailyRates,
  type CbrKeyRate,
} from '@/services/macroDataService'

const GlobeIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }), h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'ECO')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'ECO', label: 'Ставки и курсы' },
  { id: 'ECST', label: 'FRED данные' },
  { id: 'ECFC', label: 'Прогнозы' },
  { id: 'ECWB', label: 'Workbench' },
]

// ─── ECO: Rates ──────────────────────────────────────────────────────────────
const ecbRates = ref<EcbRates | null>(null)
const cbrRates = ref<CbrDailyRates | null>(null)
const cbrKeyRate = ref<CbrKeyRate | null>(null)
const ratesLoading = ref(false)
const ratesError = ref<string | null>(null)

const loadRates = async () => {
  ratesLoading.value = true
  ratesError.value = null
  try {
    const [ecb, cbr, keyRate] = await Promise.all([
      getEcbLatestRates('EUR').catch(() => null),
      getCbrRates().catch(() => null),
      getCbrKeyRate().catch(() => null),
    ])
    ecbRates.value = ecb
    cbrRates.value = cbr
    cbrKeyRate.value = keyRate
  } catch (e: unknown) {
    ratesError.value = e instanceof Error ? e.message : 'Ошибка загрузки курсов'
  } finally {
    ratesLoading.value = false
  }
}

// ─── ECST: FRED ──────────────────────────────────────────────────────────────
const fredSearchQuery = ref('')
const fredSearchResults = ref<FredSeriesInfo[]>([])
const fredSeriesData = ref<FredSeriesData | null>(null)
const fredLoading = ref(false)
const activeFredSeries = ref('')

const quickSeries = [
  { id: 'GDP', label: 'GDP' },
  { id: 'CPIAUCSL', label: 'CPI' },
  { id: 'UNRATE', label: 'Безработица' },
  { id: 'FEDFUNDS', label: 'Fed Funds' },
  { id: 'DGS10', label: '10Y Treasury' },
  { id: 'DGS2', label: '2Y Treasury' },
  { id: 'T10Y2Y', label: '10Y-2Y Spread' },
  { id: 'VIXCLS', label: 'VIX' },
]

const searchFred = async () => {
  if (!fredSearchQuery.value.trim()) return
  fredLoading.value = true
  fredSeriesData.value = null
  try {
    const result = await searchFredSeries(fredSearchQuery.value, 10)
    fredSearchResults.value = result.series
  } catch (e: unknown) {
    fredSearchResults.value = []
  } finally {
    fredLoading.value = false
  }
}

const loadFredSeries = async (seriesId: string) => {
  fredLoading.value = true
  activeFredSeries.value = seriesId
  fredSearchResults.value = []
  try {
    fredSeriesData.value = await getFredSeries(seriesId, 50, 'desc')
  } catch (e: unknown) {
    fredSeriesData.value = null
  } finally {
    fredLoading.value = false
  }
}

// ─── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(() => {
  loadRates()
})
</script>
