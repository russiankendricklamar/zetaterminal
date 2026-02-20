<template>
  <div class="page-container custom-scrollbar">
    <!-- Header -->
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4 self-start md:self-auto">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 flex items-center justify-center text-lg font-bold text-emerald-300 border border-emerald-500/30">
          {{ (localSymbol || 'BT').substring(0, 2) }}
        </div>
        <div>
          <div class="flex items-center gap-3 mb-1">
            <h2 class="text-2xl font-bold text-white tracking-tight">{{ localSymbol }}</h2>
          </div>
          <div class="flex items-center gap-4 text-xs text-gray-400">
            <span v-if="currentPrice != null" class="font-mono text-white">${{ currentPrice.toFixed(2) }}</span>
            <span v-if="currentChange != null" :class="currentChange >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-bold">
              {{ currentChange >= 0 ? '+' : '' }}{{ currentChange.toFixed(2) }}%
            </span>
            <span class="px-1.5 py-0.5 rounded bg-white/5 text-[10px] uppercase">Анализ цен</span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-4 self-stretch md:self-auto">
        <div class="flex items-center gap-2">
          <input
            v-model="tickerInput"
            type="text"
            placeholder="Тикер..."
            class="w-32 bg-black/40 border border-white/10 rounded-lg py-1.5 px-3 text-white font-mono text-sm focus:border-emerald-500/50 outline-none"
            @keydown.enter="changeSymbol"
          />
          <button @click="changeSymbol" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition-colors">
            Загрузить
          </button>
        </div>
        <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="section = tab.id"
            :class="`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${section === tab.id ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5'}`"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Quick picks -->
    <div class="flex flex-wrap gap-2 px-6 pt-4">
      <button
        v-for="t in quickTickers"
        :key="t"
        @click="tickerInput = t; changeSymbol()"
        class="px-3 py-1 bg-white/5 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-lg border border-white/5 transition-colors"
      >
        {{ t }}
      </button>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs px-6 pt-4">
      <div class="w-3 h-3 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка данных для {{ localSymbol }}...
    </div>

    <div v-if="loadError" class="mx-6 mt-4 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono">
      {{ loadError }}
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <!-- Historical Price Table -->
      <div v-if="section === 'HP'" class="space-y-4">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Исторические данные (OHLCV)</h3>
          <div class="flex gap-2">
            <button
              v-for="p in periodOptions"
              :key="p.value"
              @click="selectedPeriod = p.value; loadHistoricalData()"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${selectedPeriod === p.value ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300' : 'border-white/10 text-gray-500 hover:text-white'}`"
            >
              {{ p.label }}
            </button>
          </div>
        </div>
        <div v-if="historyData.length > 0" class="overflow-x-auto rounded-xl border border-white/5">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-white/5 text-xs text-gray-400 uppercase">
                <th class="p-4 font-bold">Дата</th>
                <th class="p-4 font-bold text-right">Открытие</th>
                <th class="p-4 font-bold text-right">Максимум</th>
                <th class="p-4 font-bold text-right">Минимум</th>
                <th class="p-4 font-bold text-right">Закрытие</th>
                <th class="p-4 font-bold text-right">Объём</th>
                <th class="p-4 font-bold text-right">Изменение %</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(row, i) in historyData" :key="i" class="border-t border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4">{{ row.date }}</td>
                <td class="p-4 text-right">{{ row.open.toFixed(2) }}</td>
                <td class="p-4 text-right text-emerald-400/80">{{ row.high.toFixed(2) }}</td>
                <td class="p-4 text-right text-rose-400/80">{{ row.low.toFixed(2) }}</td>
                <td class="p-4 text-right font-bold text-white">{{ row.close.toFixed(2) }}</td>
                <td class="p-4 text-right text-gray-500">{{ formatVolume(row.volume) }}</td>
                <td :class="`p-4 text-right font-bold ${row.changePct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`">
                  {{ row.changePct >= 0 ? '+' : '' }}{{ row.changePct.toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else-if="!loading" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет данных
        </div>
      </div>

      <!-- Price Chart -->
      <div v-else-if="section === 'GP'" class="h-full flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Технический график цены</h3>
          <div class="flex gap-2">
            <button
              @click="showMA = !showMA"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${showMA ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300' : 'border-white/10 text-gray-500'}`"
            >
              MA (20)
            </button>
            <button
              @click="showBB = !showBB"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${showBB ? 'bg-indigo-500/20 border-indigo-500/50 text-indigo-300' : 'border-white/10 text-gray-500'}`"
            >
              Полосы Боллинджера
            </button>
          </div>
        </div>
        <div class="flex-1 bg-black/20 rounded-xl border border-white/5 p-4 min-h-[400px]">
          <v-chart v-if="historyData.length > 0" class="w-full h-full" :option="priceChartOption" autoresize />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-500 text-sm">Нет данных для графика</div>
        </div>
      </div>

      <!-- Intraday Chart -->
      <div v-else-if="section === 'GIP'" class="h-full flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-bold text-white">Внутридневной график</h3>
          <div class="flex gap-2">
            <button
              v-for="interval in intradayIntervals"
              :key="interval.value"
              @click="selectedIntradayInterval = interval.value; loadIntradayData()"
              :class="`px-3 py-1 rounded-lg text-xs font-bold border transition-all ${
                selectedIntradayInterval === interval.value
                  ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                  : 'border-white/10 text-gray-500 hover:text-white hover:bg-white/5'
              }`"
            >
              {{ interval.label }}
            </button>
          </div>
        </div>
        <div class="flex-1 bg-black/20 rounded-xl border border-white/5 p-4 min-h-[400px]">
          <v-chart v-if="intradayData.length > 0" class="w-full h-full" :option="intradayChartOption" autoresize />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-500 text-sm">Нет данных</div>
        </div>
        <div v-if="intradayData.length > 0" class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Открытие</div>
            <div class="text-lg font-bold text-white font-mono">{{ intradayStats.open }}</div>
          </div>
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Максимум</div>
            <div class="text-lg font-bold text-emerald-400 font-mono">{{ intradayStats.high }}</div>
          </div>
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Минимум</div>
            <div class="text-lg font-bold text-rose-400 font-mono">{{ intradayStats.low }}</div>
          </div>
          <div class="bg-black/20 rounded-xl border border-white/5 p-4 text-center">
            <div class="text-xs text-gray-400 mb-1">Последняя</div>
            <div class="text-lg font-bold text-white font-mono">{{ intradayStats.current }}</div>
          </div>
        </div>
      </div>

      <!-- Beta Analysis -->
      <div v-else-if="section === 'BETA'" class="h-full grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 bg-black/20 rounded-xl border border-white/5 p-6 flex flex-col min-h-[400px]">
          <h3 class="text-lg font-bold text-white mb-4">Регрессионный анализ (vs SPX)</h3>
          <div class="flex-1">
            <v-chart v-if="scatterPoints.length > 0" class="w-full h-full" :option="scatterChartOption" autoresize />
            <div v-else class="w-full h-full flex items-center justify-center text-gray-500 text-sm">Загрузите данные</div>
          </div>
        </div>
        <div class="space-y-4">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Коэффициент Бета</span>
            <span class="text-5xl font-bold text-emerald-400 mb-2">{{ betaStats.beta }}</span>
            <span class="text-xs text-gray-500">{{ betaStats.beta !== '—' ? (parseFloat(betaStats.beta) > 1 ? 'Высокая волатильность к рынку' : 'Низкая волатильность к рынку') : '' }}</span>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Альфа (Дженсен)</span>
            <span class="text-5xl font-bold text-white mb-2">{{ betaStats.alpha }}</span>
            <span class="text-xs text-gray-500">Избыточная доходность</span>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col items-center justify-center text-center">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">R-квадрат</span>
            <span class="text-5xl font-bold text-indigo-400 mb-2">{{ betaStats.r2 }}</span>
            <span class="text-xs text-gray-500">Сила корреляции</span>
          </div>
        </div>
      </div>

      <!-- Technical Analysis Hub -->
      <div v-else-if="section === 'TECH'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 col-span-1 lg:col-span-2">
          <h3 class="text-sm font-bold text-white uppercase mb-6">Осцилляторы</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="osc in computedOscillators" :key="osc.name" class="bg-black/20 p-4 rounded-xl text-center border border-white/5">
              <div class="text-xs text-gray-500 mb-1">{{ osc.name }}</div>
              <div :class="`text-xl font-bold ${osc.color}`">{{ osc.value }}</div>
              <div :class="`text-[10px] mt-1 ${osc.color}`">{{ osc.signal }}</div>
            </div>
          </div>
        </div>

        <div class="p-6 rounded-2xl bg-gradient-to-br from-indigo-900/30 to-black border border-white/5 flex flex-col items-center justify-center text-center">
          <h3 class="text-sm font-bold text-white uppercase mb-4">Общий сигнал</h3>
          <div class="relative w-32 h-32 flex items-center justify-center mb-4">
            <div :class="`absolute inset-0 rounded-full border-4 border-white/5 ${overallSignal.borderClass} transform rotate-45`"></div>
            <div :class="`text-2xl font-bold ${overallSignal.color}`">{{ overallSignal.label }}</div>
          </div>
          <p class="text-xs text-gray-400 px-4">На основе осцилляторов и скользящих средних</p>
        </div>

        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 col-span-1 lg:col-span-3">
          <h3 class="text-sm font-bold text-white uppercase mb-4">Скользящие средние</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-left">
              <thead>
                <tr class="text-xs text-gray-500 uppercase border-b border-white/10">
                  <th class="py-2">Период</th>
                  <th class="py-2">Простая MA</th>
                  <th class="py-2">Экспоненциальная MA</th>
                  <th class="py-2 text-right">Действие</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono">
                <tr v-for="ma in computedMAs" :key="ma.period" class="border-b border-white/5">
                  <td class="py-3 font-bold text-white">{{ ma.period }}</td>
                  <td class="py-3 text-gray-300">{{ ma.sma }}</td>
                  <td class="py-3 text-gray-300">{{ ma.ema }}</td>
                  <td :class="`py-3 text-right font-bold ${ma.action === 'ПОКУПКА' ? 'text-emerald-400' : 'text-rose-400'}`">{{ ma.action }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <h3 class="text-xl font-bold text-white mb-2">{{ tabs.find(t => t.id === section)?.label || section }}</h3>
          <p class="text-gray-400">Содержимое появится в ближайшее время</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, ScatterChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, MarkLineComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getStockHistory, getStockInfo, type StockHistoryPoint } from '@/services/marketDataService'

use([CanvasRenderer, LineChart, ScatterChart, BarChart, TitleComponent, TooltipComponent, GridComponent, MarkLineComponent])

const props = defineProps<{ symbol?: string; activeSection?: string }>()

const section = ref(props.activeSection || 'HP')
const localSymbol = ref(props.symbol || 'AAPL')
const tickerInput = ref(props.symbol || 'AAPL')
const showMA = ref(true)
const showBB = ref(false)
const selectedIntradayInterval = ref('1h')
const selectedPeriod = ref('1mo')

const loading = ref(false)
const loadError = ref<string | null>(null)
const currentPrice = ref<number | null>(null)
const currentChange = ref<number | null>(null)

watch(() => props.activeSection, (val) => { if (val) section.value = val })
watch(() => props.symbol, (val) => { if (val) { localSymbol.value = val; tickerInput.value = val; loadAllData() } })

const quickTickers = ['AAPL', 'NVDA', 'MSFT', 'TSLA', 'AMZN', 'GOOGL', 'SBER.ME', 'GAZP.ME']

const tabs = [
  { id: 'HP', label: 'Историческая цена' },
  { id: 'GP', label: 'График цены' },
  { id: 'GIP', label: 'Внутридневной' },
  { id: 'BETA', label: 'Анализ Бета' },
  { id: 'TECH', label: 'Технический анализ' },
]

const periodOptions = [
  { label: '1Н', value: '5d' },
  { label: '1М', value: '1mo' },
  { label: '3М', value: '3mo' },
  { label: '6М', value: '6mo' },
  { label: '1Г', value: '1y' },
]

const intradayIntervals = [
  { label: '5 мин', value: '5m' },
  { label: '15 мин', value: '15m' },
  { label: '1 час', value: '1h' },
]

// ─── Data refs ─────────────────────────────────────────────────────────────────

interface HistoryRow {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  changePct: number
}

const historyData = ref<HistoryRow[]>([])
const intradayData = ref<StockHistoryPoint[]>([])
const benchmarkData = ref<StockHistoryPoint[]>([])

// ─── Data loading ──────────────────────────────────────────────────────────────

const changeSymbol = () => {
  const t = tickerInput.value.trim().toUpperCase()
  if (!t) return
  localSymbol.value = t
  loadAllData()
}

const loadAllData = async () => {
  loading.value = true
  loadError.value = null
  try {
    const [infoRes, histRes] = await Promise.allSettled([
      getStockInfo(localSymbol.value),
      getStockHistory(localSymbol.value, selectedPeriod.value, '1d'),
    ])
    if (infoRes.status === 'fulfilled') {
      currentPrice.value = infoRes.value.price
      currentChange.value = infoRes.value.changePercent
    }
    if (histRes.status === 'fulfilled') {
      const raw = histRes.value
      historyData.value = raw.map((p, i) => ({
        date: p.date,
        open: p.open,
        high: p.high,
        low: p.low,
        close: p.close,
        volume: p.volume,
        changePct: i > 0 ? ((p.close - raw[i - 1].close) / raw[i - 1].close) * 100 : 0,
      }))
    } else {
      loadError.value = 'Не удалось загрузить историю цен'
    }
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const loadHistoricalData = async () => {
  loading.value = true
  loadError.value = null
  try {
    const raw = await getStockHistory(localSymbol.value, selectedPeriod.value, '1d')
    historyData.value = raw.map((p, i) => ({
      date: p.date,
      open: p.open,
      high: p.high,
      low: p.low,
      close: p.close,
      volume: p.volume,
      changePct: i > 0 ? ((p.close - raw[i - 1].close) / raw[i - 1].close) * 100 : 0,
    }))
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

const loadIntradayData = async () => {
  loading.value = true
  try {
    const intervalMap: Record<string, string> = { '5m': '5m', '15m': '15m', '1h': '1h' }
    const interval = intervalMap[selectedIntradayInterval.value] || '1h'
    intradayData.value = await getStockHistory(localSymbol.value, '1d', interval)
  } catch {
    intradayData.value = []
  } finally {
    loading.value = false
  }
}

const loadBetaData = async () => {
  loading.value = true
  try {
    const [assetRes, benchRes] = await Promise.allSettled([
      getStockHistory(localSymbol.value, '1y', '1d'),
      getStockHistory('^GSPC', '1y', '1d'),
    ])
    if (assetRes.status === 'fulfilled') {
      historyData.value = assetRes.value.map((p, i) => ({
        date: p.date,
        open: p.open,
        high: p.high,
        low: p.low,
        close: p.close,
        volume: p.volume,
        changePct: i > 0 ? ((p.close - assetRes.value[i - 1].close) / assetRes.value[i - 1].close) * 100 : 0,
      }))
    }
    if (benchRes.status === 'fulfilled') {
      benchmarkData.value = benchRes.value
    }
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

// ─── Chart computations ────────────────────────────────────────────────────────

const formatVolume = (vol: number): string => {
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K`
  return vol.toString()
}

const computeMA = (data: number[], period: number): (number | null)[] => {
  return data.map((_, i) => {
    if (i < period - 1) return null
    const slice = data.slice(i - period + 1, i + 1)
    return slice.reduce((a, b) => a + b, 0) / period
  })
}

const computeEMA = (data: number[], period: number): (number | null)[] => {
  const k = 2 / (period + 1)
  const result: (number | null)[] = []
  let ema: number | null = null
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null)
    } else if (ema === null) {
      ema = data.slice(0, period).reduce((a, b) => a + b, 0) / period
      result.push(ema)
    } else {
      ema = data[i] * k + ema * (1 - k)
      result.push(ema)
    }
  }
  return result
}

const priceChartOption = computed(() => {
  const closes = historyData.value.map(d => d.close)
  const dates = historyData.value.map(d => d.date)
  const ma20 = computeMA(closes, 20)
  const ma20Num = ma20.filter((v): v is number => v !== null)
  const stdDev = ma20Num.length > 0 ? Math.sqrt(ma20Num.reduce((sum, v) => sum + Math.pow(v - ma20Num.reduce((a, b) => a + b, 0) / ma20Num.length, 2), 0) / ma20Num.length) : 0

  const series: unknown[] = [
    {
      type: 'line',
      data: closes,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: '#10b981', width: 2 },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16, 185, 129, 0.3)' }, { offset: 1, color: 'rgba(16, 185, 129, 0)' }] }
      }
    },
  ]

  if (showMA.value) {
    series.push({ type: 'line', data: ma20, smooth: true, symbol: 'none', lineStyle: { color: '#fbbf24', width: 2 } })
  }

  if (showBB.value) {
    const upper = ma20.map(v => v != null ? v + 2 * stdDev : null)
    const lower = ma20.map(v => v != null ? v - 2 * stdDev : null)
    series.push(
      { type: 'line', data: upper, smooth: true, symbol: 'none', lineStyle: { color: '#60a5fa', width: 1, type: 'dashed' } },
      { type: 'line', data: lower, smooth: true, symbol: 'none', lineStyle: { color: '#60a5fa', width: 1, type: 'dashed' } },
    )
  }

  return {
    grid: { left: 40, right: 40, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: dates, axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10 }, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', position: 'right', axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10 }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    series,
    tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
  }
})

const intradayStats = computed(() => {
  const prices = intradayData.value.map(d => d.close)
  if (prices.length === 0) return { open: '—', high: '—', low: '—', current: '—' }
  return {
    open: prices[0].toFixed(2),
    high: Math.max(...prices).toFixed(2),
    low: Math.min(...prices).toFixed(2),
    current: prices[prices.length - 1].toFixed(2),
  }
})

const intradayChartOption = computed(() => ({
  grid: { left: 50, right: 50, top: 20, bottom: 40 },
  xAxis: {
    type: 'category',
    data: intradayData.value.map(d => d.date),
    axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10, rotate: 45 },
    axisLine: { show: false }, axisTick: { show: false }
  },
  yAxis: { type: 'value', position: 'right', axisLabel: { color: 'rgba(255,255,255,0.3)', fontSize: 10 }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
  series: [{
    type: 'line',
    data: intradayData.value.map(d => d.close),
    smooth: false,
    symbol: 'none',
    lineStyle: { color: '#10b981', width: 2 },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16, 185, 129, 0.3)' }, { offset: 1, color: 'rgba(16, 185, 129, 0)' }] } }
  }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' }, trigger: 'axis' }
}))

// ─── Beta / Regression ─────────────────────────────────────────────────────────

const computeReturns = (data: { close: number }[]) => {
  return data.slice(1).map((d, i) => ((d.close - data[i].close) / data[i].close) * 100)
}

const scatterPoints = computed(() => {
  if (historyData.value.length < 10 || benchmarkData.value.length < 10) return []
  const assetReturns = computeReturns(historyData.value)
  const benchReturns = computeReturns(benchmarkData.value)
  const minLen = Math.min(assetReturns.length, benchReturns.length)
  return Array.from({ length: minLen }, (_, i) => [benchReturns[i], assetReturns[i]])
})

const betaStats = computed(() => {
  if (scatterPoints.value.length < 5) return { beta: '—', alpha: '—', r2: '—' }
  const pts = scatterPoints.value
  const n = pts.length
  const sumX = pts.reduce((s, p) => s + p[0], 0)
  const sumY = pts.reduce((s, p) => s + p[1], 0)
  const sumXY = pts.reduce((s, p) => s + p[0] * p[1], 0)
  const sumX2 = pts.reduce((s, p) => s + p[0] * p[0], 0)
  const sumY2 = pts.reduce((s, p) => s + p[1] * p[1], 0)
  const beta = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
  const alpha = (sumY - beta * sumX) / n
  const ssRes = pts.reduce((s, p) => s + Math.pow(p[1] - alpha - beta * p[0], 2), 0)
  const ssTot = pts.reduce((s, p) => s + Math.pow(p[1] - sumY / n, 2), 0)
  const r2 = ssTot > 0 ? 1 - ssRes / ssTot : 0
  return {
    beta: beta.toFixed(2),
    alpha: `${alpha >= 0 ? '+' : ''}${alpha.toFixed(2)}%`,
    r2: r2.toFixed(2),
  }
})

const scatterChartOption = computed(() => ({
  grid: { left: 40, right: 20, top: 20, bottom: 40 },
  xAxis: {
    type: 'value', name: 'Доходность SPX %', nameLocation: 'middle', nameGap: 25,
    nameTextStyle: { color: '#6b7280', fontSize: 10 }, axisLabel: { color: '#9ca3af', fontSize: 10 },
    axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  yAxis: {
    type: 'value', name: 'Доходность актива %', nameLocation: 'middle', nameGap: 30,
    nameTextStyle: { color: '#6b7280', fontSize: 10 }, axisLabel: { color: '#9ca3af', fontSize: 10 },
    axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [{ type: 'scatter', data: scatterPoints.value, symbolSize: 8, itemStyle: { color: '#34d399' } }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
}))

// ─── Technical Analysis ────────────────────────────────────────────────────────

const computedOscillators = computed(() => {
  const closes = historyData.value.map(d => d.close)
  if (closes.length < 14) return [
    { name: 'RSI (14)', value: '—', signal: 'Нет данных', color: 'text-gray-400' },
    { name: 'Stoch %K', value: '—', signal: 'Нет данных', color: 'text-gray-400' },
    { name: 'CCI (20)', value: '—', signal: 'Нет данных', color: 'text-gray-400' },
    { name: 'Momentum', value: '—', signal: 'Нет данных', color: 'text-gray-400' },
  ]

  // RSI
  const gains: number[] = []
  const losses: number[] = []
  for (let i = 1; i < closes.length; i++) {
    const diff = closes[i] - closes[i - 1]
    gains.push(diff > 0 ? diff : 0)
    losses.push(diff < 0 ? -diff : 0)
  }
  const avgGain = gains.slice(-14).reduce((a, b) => a + b, 0) / 14
  const avgLoss = losses.slice(-14).reduce((a, b) => a + b, 0) / 14
  const rsi = avgLoss === 0 ? 100 : 100 - 100 / (1 + avgGain / avgLoss)

  // Stochastic %K
  const last14 = closes.slice(-14)
  const stochK = last14.length > 0 ? ((closes[closes.length - 1] - Math.min(...last14)) / (Math.max(...last14) - Math.min(...last14))) * 100 : 50

  // CCI
  const last20 = closes.slice(-20)
  const meanPrice = last20.reduce((a, b) => a + b, 0) / last20.length
  const meanDev = last20.reduce((a, b) => a + Math.abs(b - meanPrice), 0) / last20.length
  const cci = meanDev > 0 ? (closes[closes.length - 1] - meanPrice) / (0.015 * meanDev) : 0

  // Momentum (10-day)
  const mom = closes.length >= 10 ? ((closes[closes.length - 1] / closes[closes.length - 10]) - 1) * 100 : 0

  const rsiSignal = rsi > 70 ? 'Перекупленность' : rsi < 30 ? 'Перепроданность' : 'Нейтрально'
  const rsiColor = rsi > 70 ? 'text-rose-400' : rsi < 30 ? 'text-emerald-400' : 'text-emerald-400'

  return [
    { name: 'RSI (14)', value: rsi.toFixed(1), signal: rsiSignal, color: rsiColor },
    { name: 'Stoch %K', value: stochK.toFixed(1), signal: stochK > 80 ? 'Перекупленность' : stochK < 20 ? 'Перепроданность' : 'Нейтрально', color: stochK > 80 ? 'text-rose-400' : stochK < 20 ? 'text-emerald-400' : 'text-emerald-400' },
    { name: 'CCI (20)', value: cci.toFixed(1), signal: cci > 100 ? 'Покупка' : cci < -100 ? 'Продажа' : 'Нейтрально', color: cci > 100 ? 'text-emerald-400' : cci < -100 ? 'text-rose-400' : 'text-white' },
    { name: 'Momentum', value: `${mom >= 0 ? '+' : ''}${mom.toFixed(2)}%`, signal: mom > 0 ? 'Бычий' : 'Медвежий', color: mom > 0 ? 'text-emerald-400' : 'text-rose-400' },
  ]
})

const overallSignal = computed(() => {
  const buys = computedOscillators.value.filter(o => o.color === 'text-emerald-400').length
  const sells = computedOscillators.value.filter(o => o.color === 'text-rose-400').length
  if (buys > sells + 1) return { label: 'ПОКУПКА', color: 'text-emerald-400', borderClass: 'border-t-emerald-500 border-r-emerald-500' }
  if (sells > buys + 1) return { label: 'ПРОДАЖА', color: 'text-rose-400', borderClass: 'border-t-rose-500 border-r-rose-500' }
  return { label: 'НЕЙТРАЛЬНО', color: 'text-white', borderClass: 'border-t-gray-500 border-r-gray-500' }
})

const computedMAs = computed(() => {
  const closes = historyData.value.map(d => d.close)
  const lastPrice = closes.length > 0 ? closes[closes.length - 1] : 0
  const periods = [10, 20, 50, 200]
  return periods.map(p => {
    const sma = closes.length >= p ? closes.slice(-p).reduce((a, b) => a + b, 0) / p : null
    const emaArr = computeEMA(closes, p)
    const ema = emaArr.length > 0 ? emaArr[emaArr.length - 1] : null
    const action = sma != null && lastPrice > sma ? 'ПОКУПКА' : sma != null ? 'ПРОДАЖА' : '—'
    return {
      period: `MA${p}`,
      sma: sma != null ? sma.toFixed(2) : '—',
      ema: ema != null ? ema.toFixed(2) : '—',
      action,
    }
  })
})

// ─── Section watchers ──────────────────────────────────────────────────────────

watch(section, (newSection) => {
  if (newSection === 'GIP' && intradayData.value.length === 0) loadIntradayData()
  if (newSection === 'BETA' && benchmarkData.value.length === 0) loadBetaData()
})

onMounted(() => {
  loadAllData()
})
</script>
