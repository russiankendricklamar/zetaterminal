<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-orange">
          <ActivityIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">АНАЛИЗ ОБЛИГАЦИЙ</h2>
          <p class="section-subtitle font-mono">ДОХОДНОСТИ, КРИВЫЕ И СТАВКИ</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка данных...
    </div>

    <div class="flex-1 flex flex-col gap-6 p-6">
      <!-- ═══ US Treasury Yield Curve ═══ -->
      <div v-if="section === 'YCRV'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Кривая доходности US Treasury</h3>
          <button @click="loadYieldCurve" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="yieldCurveData.length > 0" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          <div v-for="point in yieldCurveData" :key="point.tenor" class="p-4 rounded-xl bg-white/5 border border-white/5 text-center hover:bg-white/10 transition-colors">
            <div class="text-xs text-gray-500 uppercase font-bold mb-2">{{ point.tenor }}</div>
            <div class="text-2xl font-bold text-amber-400 font-mono">{{ point.yield != null ? point.yield.toFixed(2) + '%' : '—' }}</div>
            <div v-if="point.prevYield != null" :class="['text-xs mt-1 font-mono', (point.yield ?? 0) > point.prevYield ? 'text-rose-400' : 'text-emerald-400']">
              {{ ((point.yield ?? 0) - point.prevYield) >= 0 ? '+' : '' }}{{ ((point.yield ?? 0) - point.prevYield).toFixed(2) }}bp
            </div>
          </div>
        </div>

        <div v-if="yieldCurveData.length > 0" class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h4 class="text-sm font-bold text-gray-400 uppercase mb-4">Спреды</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div v-for="spread in computedSpreads" :key="spread.name" class="text-center">
              <div class="text-xs text-gray-500 mb-1">{{ spread.name }}</div>
              <div :class="['text-xl font-bold font-mono', spread.value >= 0 ? 'text-white' : 'text-rose-400']">{{ spread.value.toFixed(0) }} bps</div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ CBR & FRED Rates ═══ -->
      <div v-else-if="section === 'YAS'" class="space-y-6">
        <h3 class="text-lg font-bold text-white">Ставки: ЦБР, ФРС, ЕЦБ</h3>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 text-center">
            <h4 class="text-xs text-gray-500 uppercase font-bold mb-2">Ключевая ставка ЦБР</h4>
            <div class="text-4xl font-bold text-amber-400 font-mono">{{ cbrKeyRate != null ? cbrKeyRate.toFixed(2) + '%' : '—' }}</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 text-center">
            <h4 class="text-xs text-gray-500 uppercase font-bold mb-2">Fed Funds Rate</h4>
            <div class="text-4xl font-bold text-blue-400 font-mono">{{ fedFundsRate != null ? fedFundsRate.toFixed(2) + '%' : '—' }}</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 text-center">
            <h4 class="text-xs text-gray-500 uppercase font-bold mb-2">ECB Main Rate</h4>
            <div class="text-4xl font-bold text-indigo-400 font-mono">{{ ecbRate != null ? ecbRate.toFixed(2) + '%' : '—' }}</div>
          </div>
        </div>

        <div v-if="depositRates.length > 0" class="rounded-2xl border border-white/5 bg-black/20 overflow-hidden">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h4 class="font-bold text-white text-sm">Средние ставки по депозитам (ЦБР)</h4>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-500 uppercase">
                <th class="p-4">Дата</th>
                <th class="p-4 text-right">Overnight (%)</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(r, i) in depositRates" :key="i" class="border-t border-white/5 hover:bg-white/5">
                <td class="p-4 text-white">{{ r.date }}</td>
                <td class="p-4 text-right text-amber-400">{{ r.overnight != null ? r.overnight.toFixed(2) + '%' : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ Yield Analysis ═══ -->
      <div v-else-if="section === 'YA'" class="space-y-6">
        <h3 class="text-lg font-bold text-white">Историческая динамика доходностей</h3>
        <div v-if="yieldHistory.length > 0" class="rounded-2xl border border-white/5 bg-black/20 overflow-hidden">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-500 uppercase bg-white/5">
                <th class="p-4">Дата</th>
                <th class="p-4 text-right">2Y</th>
                <th class="p-4 text-right">5Y</th>
                <th class="p-4 text-right">10Y</th>
                <th class="p-4 text-right">30Y</th>
                <th class="p-4 text-right">2s10s Spread</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(row, i) in yieldHistory" :key="i" class="border-t border-white/5 hover:bg-white/5">
                <td class="p-4 text-white">{{ row.date }}</td>
                <td class="p-4 text-right">{{ row.y2 != null ? row.y2.toFixed(2) + '%' : '—' }}</td>
                <td class="p-4 text-right">{{ row.y5 != null ? row.y5.toFixed(2) + '%' : '—' }}</td>
                <td class="p-4 text-right font-bold text-white">{{ row.y10 != null ? row.y10.toFixed(2) + '%' : '—' }}</td>
                <td class="p-4 text-right">{{ row.y30 != null ? row.y30.toFixed(2) + '%' : '—' }}</td>
                <td :class="['p-4 text-right font-bold', row.spread >= 0 ? 'text-emerald-400' : 'text-rose-400']">
                  {{ row.spread.toFixed(0) }} bps
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ MOEX ZCYC (КБД) ═══ -->
      <div v-else-if="section === 'ZCYC'" class="space-y-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">КБД MOEX — Кривая бескупонных доходностей</h3>
          <button @click="loadZcyc" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="zcycDate" class="text-xs text-gray-500 font-mono">
          Дата: {{ zcycDate }} · Точек: {{ zcycPoints.length }} · Среднее: {{ zcycMean != null ? zcycMean.toFixed(2) + '%' : '—' }}
        </div>

        <div v-if="zcycPoints.length > 0" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <div v-for="pt in zcycKeyPoints" :key="pt.term" class="p-3 rounded-xl bg-white/5 border border-white/5 text-center hover:bg-white/10 transition-colors">
            <div class="text-xs text-gray-500 font-bold mb-1">{{ pt.label }}</div>
            <div class="text-xl font-bold text-amber-400 font-mono">{{ pt.value.toFixed(2) }}%</div>
          </div>
        </div>

        <div v-if="zcycPoints.length > 0" class="rounded-2xl border border-white/5 bg-black/20 overflow-hidden">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h4 class="font-bold text-white text-sm">Полная кривая (срок → доходность)</h4>
          </div>
          <div class="overflow-auto max-h-96">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="text-xs text-gray-500 uppercase sticky top-0 bg-black/80 backdrop-blur-md">
                  <th class="p-3">Срок (лет)</th>
                  <th class="p-3 text-right">Доходность (%)</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono text-gray-300">
                <tr v-for="pt in zcycPoints" :key="pt.term" class="border-t border-white/5 hover:bg-white/5">
                  <td class="p-3 text-white">{{ pt.term.toFixed(2) }}</td>
                  <td class="p-3 text-right text-amber-400">{{ pt.value.toFixed(4) }}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-else-if="!loading" class="flex items-center justify-center h-32 text-gray-500 font-mono text-sm">
          Нет данных КБД
        </div>
      </div>

      <!-- ═══ OAS Calculator ═══ -->
      <div v-else-if="section === 'OAS1'" class="space-y-6">
        <h3 class="text-lg font-bold text-white">Калькулятор OAS</h3>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 space-y-4">
            <h4 class="text-sm font-bold text-gray-400 uppercase">Параметры облигации</h4>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="text-xs text-gray-500 block mb-1">Рыночная цена</label><input type="number" v-model.number="oasPrice" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Купон (%)</label><input type="number" v-model.number="oasCoupon" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Номинал</label><input type="number" v-model.number="oasFace" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Срок (лет)</label><input type="number" v-model.number="oasMaturity" step="0.5" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
            </div>
            <div><label class="text-xs text-gray-500 block mb-1">Benchmark доходность (%)</label><input type="number" v-model.number="oasBenchmark" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
          </div>
          <div class="space-y-4">
            <div class="p-6 rounded-2xl bg-gradient-to-br from-amber-900/20 to-black border border-amber-500/30 text-center">
              <h4 class="text-sm font-bold text-amber-500 uppercase mb-2">OAS (Option-Adjusted Spread)</h4>
              <div class="text-5xl font-bold text-white font-mono mb-2">{{ computedOas.toFixed(1) }} <span class="text-xl text-gray-500">bps</span></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
                <div class="text-xs text-gray-500 uppercase mb-1">Z-Spread</div>
                <div class="text-xl font-bold text-white font-mono">{{ computedZSpread.toFixed(1) }} bps</div>
              </div>
              <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
                <div class="text-xs text-gray-500 uppercase mb-1">YTM</div>
                <div class="text-xl font-bold text-amber-400 font-mono">{{ computedYtm.toFixed(2) }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ Bond Pricing ═══ -->
      <div v-else-if="section === 'BB'" class="space-y-6">
        <h3 class="text-lg font-bold text-white">Оценка облигаций</h3>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 space-y-4">
            <h4 class="text-sm font-bold text-gray-400 uppercase">Параметры</h4>
            <div class="space-y-3">
              <div><label class="text-xs text-gray-500 block mb-1">Купон (%)</label><input type="number" v-model.number="bpCoupon" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Номинал</label><input type="number" v-model.number="bpFace" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Срок (лет)</label><input type="number" v-model.number="bpMaturity" step="0.5" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Требуемая доходность (%)</label><input type="number" v-model.number="bpYield" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Частота купонов</label>
                <select v-model.number="bpFreq" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm">
                  <option :value="1">Ежегодно</option>
                  <option :value="2">Полугодовой</option>
                  <option :value="4">Квартальный</option>
                </select>
              </div>
            </div>
          </div>
          <div class="p-6 rounded-2xl bg-black/20 border border-white/5">
            <h4 class="text-sm font-bold text-gray-400 uppercase mb-4">Результат</h4>
            <div class="grid grid-cols-2 gap-6">
              <div><span class="text-xs text-gray-500 block mb-1">Clean Price</span><span class="text-2xl font-bold text-white font-mono">{{ bondPricing.cleanPrice.toFixed(2) }}</span></div>
              <div><span class="text-xs text-gray-500 block mb-1">Macaulay Duration</span><span class="text-2xl font-bold text-blue-400 font-mono">{{ bondPricing.macDuration.toFixed(2) }}</span></div>
              <div><span class="text-xs text-gray-500 block mb-1">Modified Duration</span><span class="text-2xl font-bold text-amber-400 font-mono">{{ bondPricing.modDuration.toFixed(2) }}</span></div>
              <div><span class="text-xs text-gray-500 block mb-1">Convexity</span><span class="text-2xl font-bold text-white font-mono">{{ bondPricing.convexity.toFixed(2) }}</span></div>
            </div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h4 class="text-sm font-bold text-gray-400 uppercase mb-4">Денежные потоки</h4>
            <div class="overflow-auto max-h-64">
              <table class="w-full text-left border-collapse text-sm font-mono">
                <thead><tr class="text-xs text-gray-500 uppercase"><th class="py-2">Период</th><th class="py-2 text-right">CF</th><th class="py-2 text-right">PV</th></tr></thead>
                <tbody class="text-gray-300">
                  <tr v-for="(cf, i) in bondPricing.cashFlows" :key="i" class="border-t border-white/5">
                    <td class="py-2">{{ cf.period }}</td>
                    <td class="py-2 text-right">{{ cf.cf.toFixed(2) }}</td>
                    <td class="py-2 text-right text-amber-400">{{ cf.pv.toFixed(2) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Выберите раздел
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, defineComponent, h } from 'vue'
import { getFredSeries, getCbrKeyRate, getCbrDepositRates, getEcbLatestRates } from '@/services/macroDataService'
import { getZCYC, type ZCYCPoint } from '@/services/zcycService'

const ActivityIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '22 12 18 12 15 21 9 3 6 12 2 12' })]) })

const props = defineProps<{ activeSection?: string }>()
const section = ref(props.activeSection || 'YCRV')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'YCRV', label: 'US Treasury' },
  { id: 'ZCYC', label: 'КБД MOEX' },
  { id: 'YAS', label: 'Ставки CB' },
  { id: 'YA', label: 'Историческая динамика' },
  { id: 'OAS1', label: 'Калькулятор OAS' },
  { id: 'BB', label: 'Оценка облигаций' },
]

const loading = ref(false)

// Data
interface YieldPoint {
  tenor: string
  seriesId: string
  yield: number | null
  prevYield: number | null
}

const yieldCurveData = ref<YieldPoint[]>([])
const cbrKeyRate = ref<number | null>(null)
const fedFundsRate = ref<number | null>(null)
const ecbRate = ref<number | null>(null)
const depositRates = ref<Array<{ date: string; overnight: number | null }>>([])

interface YieldHistoryRow {
  date: string
  y2: number | null
  y5: number | null
  y10: number | null
  y30: number | null
  spread: number
}
const yieldHistory = ref<YieldHistoryRow[]>([])

const TREASURY_SERIES = [
  { tenor: '1M', seriesId: 'DGS1MO' },
  { tenor: '3M', seriesId: 'DGS3MO' },
  { tenor: '6M', seriesId: 'DGS6MO' },
  { tenor: '1Y', seriesId: 'DGS1' },
  { tenor: '2Y', seriesId: 'DGS2' },
  { tenor: '5Y', seriesId: 'DGS5' },
  { tenor: '10Y', seriesId: 'DGS10' },
  { tenor: '30Y', seriesId: 'DGS30' },
]

const loadYieldCurve = async () => {
  loading.value = true
  try {
    const results = await Promise.allSettled(
      TREASURY_SERIES.map(s => getFredSeries(s.seriesId, 5))
    )
    yieldCurveData.value = TREASURY_SERIES.map((s, i) => {
      const res = results[i]
      if (res.status === 'fulfilled' && res.value.observations.length > 0) {
        const obs = res.value.observations
        const latest = obs[obs.length - 1]
        const prev = obs.length > 1 ? obs[obs.length - 2] : null
        return {
          tenor: s.tenor,
          seriesId: s.seriesId,
          yield: latest.value,
          prevYield: prev?.value ?? null,
        }
      }
      return { tenor: s.tenor, seriesId: s.seriesId, yield: null, prevYield: null }
    })
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

const loadRates = async () => {
  loading.value = true
  try {
    const [cbrRes, fredRes, ecbRes, depoRes] = await Promise.allSettled([
      getCbrKeyRate(),
      getFredSeries('FEDFUNDS', 1),
      getEcbLatestRates('EUR'),
      getCbrDepositRates(),
    ])
    if (cbrRes.status === 'fulfilled') {
      cbrKeyRate.value = cbrRes.value.rate
    }
    if (fredRes.status === 'fulfilled' && fredRes.value.observations.length > 0) {
      fedFundsRate.value = fredRes.value.observations[fredRes.value.observations.length - 1].value
    }
    if (ecbRes.status === 'fulfilled') {
      const rates = ecbRes.value as { rates?: Record<string, number> }
      if (rates.rates && rates.rates['USD']) {
        ecbRate.value = null // ECB doesn't return policy rate via Frankfurter, just FX
      }
    }
    if (depoRes.status === 'fulfilled') {
      depositRates.value = (depoRes.value as { rates: Array<{ date: string; overnight: number | null }> }).rates.slice(0, 15)
    }
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

const loadYieldHistory = async () => {
  loading.value = true
  try {
    const seriesIds = ['DGS2', 'DGS5', 'DGS10', 'DGS30']
    const results = await Promise.allSettled(
      seriesIds.map(id => getFredSeries(id, 30))
    )
    const dataMap: Record<string, Record<string, number | null>> = {}
    seriesIds.forEach((id, idx) => {
      const res = results[idx]
      if (res.status === 'fulfilled') {
        for (const obs of res.value.observations) {
          if (!dataMap[obs.date]) dataMap[obs.date] = {}
          dataMap[obs.date][id] = obs.value
        }
      }
    })
    yieldHistory.value = Object.entries(dataMap)
      .sort(([a], [b]) => b.localeCompare(a))
      .slice(0, 20)
      .map(([date, vals]) => ({
        date,
        y2: vals['DGS2'] ?? null,
        y5: vals['DGS5'] ?? null,
        y10: vals['DGS10'] ?? null,
        y30: vals['DGS30'] ?? null,
        spread: ((vals['DGS10'] ?? 0) - (vals['DGS2'] ?? 0)) * 100,
      }))
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

const computedSpreads = computed(() => {
  const findYield = (tenor: string) => yieldCurveData.value.find(p => p.tenor === tenor)?.yield ?? null
  const y2 = findYield('2Y')
  const y5 = findYield('5Y')
  const y10 = findYield('10Y')
  const y30 = findYield('30Y')
  return [
    { name: '2s10s', value: y2 != null && y10 != null ? (y10 - y2) * 100 : 0 },
    { name: '2s30s', value: y2 != null && y30 != null ? (y30 - y2) * 100 : 0 },
    { name: '5s10s', value: y5 != null && y10 != null ? (y10 - y5) * 100 : 0 },
    { name: '10s30s', value: y10 != null && y30 != null ? (y30 - y10) * 100 : 0 },
  ]
})

// ─── MOEX ZCYC ────────────────────────────────────────────────────────────────

const zcycPoints = ref<ZCYCPoint[]>([])
const zcycDate = ref<string | null>(null)
const zcycMean = ref<number | null>(null)

const zcycKeyPoints = computed(() => {
  const targets = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]
  const labels: Record<number, string> = { 0.25: '3M', 0.5: '6M', 1: '1Y', 2: '2Y', 3: '3Y', 5: '5Y', 7: '7Y', 10: '10Y', 15: '15Y', 20: '20Y', 30: '30Y' }
  return targets
    .map(t => {
      const closest = zcycPoints.value.reduce((prev, curr) =>
        Math.abs(curr.term - t) < Math.abs(prev.term - t) ? curr : prev,
        zcycPoints.value[0]
      )
      return closest ? { term: t, label: labels[t] || `${t}Y`, value: closest.value } : null
    })
    .filter((p): p is { term: number; label: string; value: number } => p !== null && Math.abs(p.value) > 0)
})

const loadZcyc = async () => {
  loading.value = true
  try {
    const res = await getZCYC()
    zcycPoints.value = res.data
    zcycDate.value = res.date
    zcycMean.value = res.mean_rate
  } catch {
    zcycPoints.value = []
  } finally {
    loading.value = false
  }
}

// ─── OAS Calculator ────────────────────────────────────────────────────────────

const oasPrice = ref(98.50)
const oasCoupon = ref(7.00)
const oasFace = ref(1000)
const oasMaturity = ref(5)
const oasBenchmark = ref(8.50)

const computedYtm = computed(() => {
  const c = oasCoupon.value / 100 * oasFace.value
  const n = oasMaturity.value
  const p = oasPrice.value / 100 * oasFace.value
  const f = oasFace.value
  return ((c + (f - p) / n) / ((f + p) / 2)) * 100
})

const computedZSpread = computed(() => {
  return (computedYtm.value - oasBenchmark.value) * 100
})

const computedOas = computed(() => {
  return computedZSpread.value * 0.95
})

// ─── Bond Pricing ──────────────────────────────────────────────────────────────

const bpCoupon = ref(7.00)
const bpFace = ref(1000)
const bpMaturity = ref(5)
const bpYield = ref(8.00)
const bpFreq = ref(2)

const bondPricing = computed(() => {
  const c = bpCoupon.value / 100 / bpFreq.value * bpFace.value
  const y = bpYield.value / 100 / bpFreq.value
  const n = bpMaturity.value * bpFreq.value
  const f = bpFace.value

  const cashFlows: Array<{ period: number; cf: number; pv: number }> = []
  let price = 0
  let macDur = 0
  let convexity = 0

  for (let t = 1; t <= n; t++) {
    const cf = t === n ? c + f : c
    const df = Math.pow(1 + y, -t)
    const pv = cf * df
    price += pv
    macDur += t * pv
    convexity += t * (t + 1) * pv
    cashFlows.push({ period: t, cf, pv })
  }

  macDur = price > 0 ? macDur / price / bpFreq.value : 0
  const modDur = macDur / (1 + y)
  convexity = price > 0 ? convexity / (price * Math.pow(1 + y, 2) * Math.pow(bpFreq.value, 2)) : 0

  return { cleanPrice: price / (bpFace.value / 100), macDuration: macDur, modDuration: modDur, convexity, cashFlows }
})

// ─── Section watchers ──────────────────────────────────────────────────────────

watch(section, (s) => {
  if (s === 'YAS' && cbrKeyRate.value === null) loadRates()
  if (s === 'YA' && yieldHistory.value.length === 0) loadYieldHistory()
  if (s === 'ZCYC' && zcycPoints.value.length === 0) loadZcyc()
})

onMounted(() => {
  loadYieldCurve()
})
</script>
