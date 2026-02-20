<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-indigo">
          <ArrowLeftRightIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">СВОПЫ</h2>
          <p class="section-subtitle font-mono">ЦЕНООБРАЗОВАНИЕ, ОЦЕНКА И КРИВЫЕ</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка...
    </div>

    <div class="flex-1 flex flex-col gap-6 p-6">
      <!-- ═══ Swap Pricing Model ═══ -->
      <div v-if="section === 'SWPM'" class="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
        <div class="space-y-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Deal Parameters</h3>
            <div class="space-y-4">
              <div><label class="text-xs text-gray-500 block mb-1">Notional ($M)</label><input type="number" v-model.number="notional" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Fixed Rate (%)</label><input type="number" v-model.number="fixedRate" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">Tenor (Years)</label><input type="range" min="1" max="30" v-model.number="tenor" class="w-full" /><div class="text-right text-xs text-indigo-400">{{ tenor }} Years</div></div>
            </div>
            <button @click="calculateNpv" class="w-full mt-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold">Calculate NPV</button>
          </div>
          <div class="p-6 rounded-2xl bg-black/20 border border-white/5 text-center">
            <h3 class="text-xs font-bold text-gray-500 uppercase mb-2">Net Present Value</h3>
            <div :class="['text-3xl font-bold font-mono', npvResult >= 0 ? 'text-emerald-400' : 'text-rose-400']">
              {{ npvResult >= 0 ? '+' : '' }}${{ Math.abs(npvResult).toLocaleString() }}
            </div>
          </div>
        </div>
        <div class="lg:col-span-2 p-6 rounded-2xl bg-white/5 border border-white/5">
          <h4 class="text-sm font-bold text-gray-400 uppercase mb-4">Cash Flow Schedule</h4>
          <div v-if="cashFlows.length > 0" class="overflow-auto max-h-96">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="text-xs text-gray-500 uppercase">
                  <th class="p-3">Период</th>
                  <th class="p-3 text-right">Fixed Leg</th>
                  <th class="p-3 text-right">Float Leg</th>
                  <th class="p-3 text-right">Net</th>
                </tr>
              </thead>
              <tbody class="text-sm font-mono text-gray-300">
                <tr v-for="(cf, i) in cashFlows" :key="i" class="border-t border-white/5">
                  <td class="p-3 text-white">Year {{ cf.year }}</td>
                  <td class="p-3 text-right text-rose-400">-${{ cf.fixedLeg.toLocaleString() }}</td>
                  <td class="p-3 text-right text-emerald-400">+${{ cf.floatLeg.toLocaleString() }}</td>
                  <td :class="['p-3 text-right font-bold', cf.net >= 0 ? 'text-emerald-400' : 'text-rose-400']">
                    {{ cf.net >= 0 ? '+' : '' }}${{ cf.net.toLocaleString() }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- ═══ Interest Rate Basics ═══ -->
      <div v-else-if="section === 'IRSB'" class="flex flex-col h-full">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-white">Treasury Swap Rates (FRED)</h3>
          <button @click="loadRateData" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>
        <div v-if="swapRates.length > 0" class="flex-1 bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
          <table class="w-full text-left border-collapse">
            <thead><tr class="text-xs text-gray-500 uppercase bg-white/5"><th class="p-4">Currency / Series</th><th class="p-4 text-right">2Y</th><th class="p-4 text-right">5Y</th><th class="p-4 text-right">10Y</th><th class="p-4 text-right">30Y</th></tr></thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="r in swapRates" :key="r.ccy" class="border-b border-white/5 hover:bg-white/5">
                <td class="p-4 font-bold text-white">{{ r.ccy }}</td>
                <td class="p-4 text-right">{{ r.t2y }}</td>
                <td class="p-4 text-right">{{ r.t5y }}</td>
                <td class="p-4 text-right font-bold text-white">{{ r.t10y }}</td>
                <td class="p-4 text-right">{{ r.t30y }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ Swap Monitor ═══ -->
      <div v-else-if="section === 'IRSM'" class="flex flex-col gap-6">
        <h3 class="text-lg font-bold text-white">Мониторинг своп-спредов</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="ss in swapSpreads" :key="ss.name" class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
            <div class="text-xs text-gray-500 uppercase mb-1">{{ ss.name }}</div>
            <div :class="['text-2xl font-bold font-mono', ss.value >= 0 ? 'text-white' : 'text-rose-400']">{{ ss.value.toFixed(1) }}</div>
            <div class="text-[10px] text-gray-500">bps</div>
          </div>
        </div>
      </div>

      <!-- ═══ Asset Swap ═══ -->
      <div v-else-if="section === 'ASW'" class="grid grid-cols-1 md:grid-cols-2 gap-8 h-full items-center">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-lg font-bold text-white mb-6">Asset Details</h3>
          <div class="space-y-4">
            <div><label class="text-xs text-gray-500 block mb-1">Bond Price</label><input type="number" v-model.number="aswBondPrice" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="text-xs text-gray-500 block mb-1">Coupon (%)</label><input type="number" v-model.number="aswCoupon" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
              <div><label class="text-xs text-gray-500 block mb-1">YTM (%)</label><input type="number" v-model.number="aswYtm" step="0.01" class="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white font-mono text-sm" /></div>
            </div>
          </div>
        </div>
        <div class="p-8 rounded-2xl bg-gradient-to-br from-teal-900/20 to-black border border-teal-500/30 text-center">
          <h3 class="text-sm font-bold text-teal-500 uppercase mb-2">Asset Swap Spread</h3>
          <div class="text-6xl font-bold text-white mb-2">{{ computedAswSpread.toFixed(1) }} <span class="text-2xl text-gray-500">bps</span></div>
          <p class="text-xs text-gray-400">Spread over risk-free rate</p>
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
import { getFredSeries } from '@/services/macroDataService'

const ArrowLeftRightIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('polyline', { points: '18 8 22 12 18 16' }), h('polyline', { points: '6 8 2 12 6 16' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'SWPM')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'SWPM', label: 'Модель ценообразования' },
  { id: 'IRSB', label: 'Rate Basics' },
  { id: 'IRSM', label: 'Монитор' },
  { id: 'ASW', label: 'Asset Swap' },
]

const loading = ref(false)

// ─── Swap Pricing Model ────────────────────────────────────────────────────────

const notional = ref(10)
const fixedRate = ref(4.25)
const tenor = ref(5)
const npvResult = ref(0)
const floatRateEstimate = ref(4.50)

interface CashFlow { year: number; fixedLeg: number; floatLeg: number; net: number }
const cashFlows = ref<CashFlow[]>([])

const calculateNpv = () => {
  const n = notional.value * 1e6
  const fixed = fixedRate.value / 100
  const floatR = floatRateEstimate.value / 100
  const flows: CashFlow[] = []
  let totalNpv = 0
  for (let y = 1; y <= tenor.value; y++) {
    const fixedLeg = Math.round(n * fixed)
    const floatLeg = Math.round(n * floatR)
    const net = floatLeg - fixedLeg
    const df = 1 / Math.pow(1 + fixed, y)
    totalNpv += net * df
    flows.push({ year: y, fixedLeg, floatLeg, net })
  }
  cashFlows.value = flows
  npvResult.value = Math.round(totalNpv)
}

// ─── Rate Basics (FRED Treasury Rates) ─────────────────────────────────────────

interface SwapRate { ccy: string; t2y: string; t5y: string; t10y: string; t30y: string }
const swapRates = ref<SwapRate[]>([])

const loadRateData = async () => {
  loading.value = true
  try {
    const seriesIds = ['DGS2', 'DGS5', 'DGS10', 'DGS30']
    const results = await Promise.allSettled(
      seriesIds.map(id => getFredSeries(id, 1))
    )
    const vals = seriesIds.map((_, i) => {
      const res = results[i]
      if (res.status === 'fulfilled' && res.value.observations.length > 0) {
        return res.value.observations[res.value.observations.length - 1].value
      }
      return null
    })
    const fmt = (v: number | null) => v != null ? v.toFixed(2) + '%' : '—'
    swapRates.value = [
      { ccy: 'USD (Treasury)', t2y: fmt(vals[0]), t5y: fmt(vals[1]), t10y: fmt(vals[2]), t30y: fmt(vals[3]) },
    ]

    // Update float rate estimate from 2Y Treasury
    if (vals[0] != null) floatRateEstimate.value = vals[0]
  } catch {
    // silent
  } finally {
    loading.value = false
  }
}

// ─── Swap Spreads ──────────────────────────────────────────────────────────────

const swapSpreads = computed(() => {
  const parseRate = (s: string) => {
    const n = parseFloat(s)
    return isNaN(n) ? null : n
  }
  if (swapRates.value.length === 0) return []
  const r = swapRates.value[0]
  const y2 = parseRate(r.t2y)
  const y5 = parseRate(r.t5y)
  const y10 = parseRate(r.t10y)
  const y30 = parseRate(r.t30y)
  return [
    { name: '2s10s Spread', value: y2 != null && y10 != null ? (y10 - y2) * 100 : 0 },
    { name: '2s30s Spread', value: y2 != null && y30 != null ? (y30 - y2) * 100 : 0 },
    { name: '5s10s Spread', value: y5 != null && y10 != null ? (y10 - y5) * 100 : 0 },
    { name: '10s30s Spread', value: y10 != null && y30 != null ? (y30 - y10) * 100 : 0 },
  ]
})

// ─── Asset Swap ────────────────────────────────────────────────────────────────

const aswBondPrice = ref(98.50)
const aswCoupon = ref(4.00)
const aswYtm = ref(4.50)

const computedAswSpread = computed(() => {
  return (aswYtm.value - aswCoupon.value + (100 - aswBondPrice.value) / 10) * 100
})

watch(section, (s) => {
  if (s === 'IRSB' && swapRates.value.length === 0) loadRateData()
})

onMounted(() => {
  calculateNpv()
})
</script>
