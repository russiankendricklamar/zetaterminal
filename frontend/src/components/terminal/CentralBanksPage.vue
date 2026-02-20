<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box">
          <BuildingIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ЦЕНТРАЛЬНЫЕ БАНКИ</h2>
          <p class="section-subtitle font-mono">ДЕНЕЖНО-КРЕДИТНАЯ ПОЛИТИКА, СТАВКИ, ЛИКВИДНОСТЬ</p>
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
      Загрузка данных центральных банков...
    </div>

    <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono mx-4">
      {{ loadError }}
    </div>

    <div class="flex-1 flex flex-col gap-6">
      <!-- ═══ Bank of Russia ═══ -->
      <div v-if="section === 'CBR'" class="flex flex-col h-full gap-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Ключевая ставка</h3>
            <div class="text-3xl font-bold text-rose-400">{{ cbrKeyRate != null ? cbrKeyRate.toFixed(2) + '%' : '—' }}</div>
            <div class="text-xs text-rose-500 mt-1">Банк России</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">RUONIA</h3>
            <div class="text-3xl font-bold text-white">{{ ruoniaRate != null ? ruoniaRate.toFixed(2) + '%' : '—' }}</div>
            <div class="text-xs text-gray-500 mt-1">Межбанковская ставка</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Курс USD/RUB</h3>
            <div class="text-3xl font-bold text-white">{{ usdRub != null ? usdRub.toFixed(2) : '—' }}</div>
            <div class="text-xs text-gray-500 mt-1">ЦБ РФ</div>
          </div>
        </div>

        <!-- Key rate history -->
        <div v-if="keyRateHistory.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h3 class="font-bold text-white">История ключевой ставки</h3>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-500 uppercase">
                <th class="p-4">Дата</th>
                <th class="p-4 text-right">Ставка</th>
                <th class="p-4 text-right">Изменение</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(item, i) in keyRateHistory" :key="i" class="border-t border-white/5 hover:bg-white/5">
                <td class="p-4 text-white">{{ item.date }}</td>
                <td class="p-4 text-right font-bold text-white">{{ item.rate.toFixed(2) }}%</td>
                <td class="p-4 text-right">
                  <span v-if="i < keyRateHistory.length - 1" :class="item.rate > keyRateHistory[i + 1].rate ? 'text-rose-400' : item.rate < keyRateHistory[i + 1].rate ? 'text-emerald-400' : 'text-gray-500'">
                    {{ item.rate > keyRateHistory[i + 1].rate ? '+' : '' }}{{ (item.rate - keyRateHistory[i + 1].rate).toFixed(2) }}%
                  </span>
                  <span v-else class="text-gray-500">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ Federal Reserve ═══ -->
      <div v-else-if="section === 'FED'" class="flex flex-col h-full gap-6">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-lg font-bold text-white">Federal Funds Rate</h3>
            <div class="flex items-center gap-3">
              <span class="text-3xl font-bold text-emerald-400">{{ fedRate != null ? fedRate.toFixed(2) + '%' : '—' }}</span>
              <span class="text-xs font-bold text-gray-500 bg-white/10 px-2 py-1 rounded">FRED: FEDFUNDS</span>
            </div>
          </div>
        </div>

        <div v-if="fedHistory.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h3 class="font-bold text-white">История ставки ФРС</h3>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-500 uppercase">
                <th class="p-4">Дата</th>
                <th class="p-4 text-right">Ставка</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(obs, i) in fedHistory" :key="i" class="border-t border-white/5 hover:bg-white/5">
                <td class="p-4 text-white">{{ obs.date }}</td>
                <td class="p-4 text-right font-bold text-emerald-400">{{ obs.value != null ? obs.value.toFixed(2) + '%' : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ Global Central Banks ═══ -->
      <div v-else-if="section === 'CENB'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Global Policy Rates</h3>
        <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5">
                <th class="p-4">Страна</th>
                <th class="p-4">Центральный банк</th>
                <th class="p-4 text-right">Текущая ставка</th>
                <th class="p-4 text-right">Источник</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="cb in globalRates" :key="cb.country" class="border-b border-white/5 hover:bg-white/5">
                <td class="p-4 font-bold text-white">{{ cb.country }}</td>
                <td class="p-4">{{ cb.bank }}</td>
                <td class="p-4 text-right font-bold text-white">{{ cb.rate }}</td>
                <td class="p-4 text-right text-xs text-gray-500">{{ cb.source }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ CBR FX Rates ═══ -->
      <div v-else-if="section === 'FOMC'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Курсы валют ЦБ РФ</h3>
        <div v-if="cbrRatesList.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5">
                <th class="p-4">Код</th>
                <th class="p-4">Валюта</th>
                <th class="p-4 text-right">Номинал</th>
                <th class="p-4 text-right">Курс ЦБ</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="r in cbrRatesList" :key="r.char_code" class="border-b border-white/5 hover:bg-white/5">
                <td class="p-4">
                  <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ r.char_code }}</span>
                </td>
                <td class="p-4 text-gray-300">{{ r.name }}</td>
                <td class="p-4 text-right text-gray-400">{{ r.nominal }}</td>
                <td class="p-4 text-right font-bold text-white">{{ r.value.toFixed(4) }}</td>
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
import {
  getCbrKeyRate,
  getCbrRuonia,
  getCbrRates,
  getFredSeries,
  getEcbLatestRates,
  type CbrKeyRate,
  type CbrRuonia,
  type CbrDailyRates,
  type FredObservation,
} from '@/services/macroDataService'

const BuildingIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('rect', { x: '3', y: '4', width: '18', height: '16', rx: '2' }), h('path', { d: 'M16 2v2' }), h('path', { d: 'M8 2v2' }), h('path', { d: 'M3 10h18' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'CBR')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'CBR', label: 'Банк России' },
  { id: 'FED', label: 'ФРС' },
  { id: 'CENB', label: 'Международные ЦБ' },
  { id: 'FOMC', label: 'Курсы валют ЦБ' },
]

const loading = ref(false)
const loadError = ref<string | null>(null)

// CBR data
const cbrKeyRate = ref<number | null>(null)
const ruoniaRate = ref<number | null>(null)
const usdRub = ref<number | null>(null)
const keyRateHistory = ref<Array<{ date: string; rate: number }>>([])
const cbrRatesList = ref<Array<{ char_code: string; name: string; nominal: number; value: number }>>([])

// Fed data
const fedRate = ref<number | null>(null)
const fedHistory = ref<FredObservation[]>([])

// Global rates
const globalRates = ref<Array<{ country: string; bank: string; rate: string; source: string }>>([])

const loadData = async () => {
  loading.value = true
  loadError.value = null
  try {
    const [keyRateRes, ruoniaRes, cbrDailyRes, fedRes, ecbRes] = await Promise.allSettled([
      getCbrKeyRate(),
      getCbrRuonia(),
      getCbrRates(),
      getFredSeries('FEDFUNDS', 24, 'desc'),
      getEcbLatestRates('EUR'),
    ])

    // CBR Key Rate
    if (keyRateRes.status === 'fulfilled') {
      const kr = keyRateRes.value
      cbrKeyRate.value = kr.current_rate
      keyRateHistory.value = kr.history.slice(0, 20)
    }

    // RUONIA
    if (ruoniaRes.status === 'fulfilled') {
      ruoniaRes.value.history.length > 0
        ? (ruoniaRate.value = ruoniaRes.value.current_rate)
        : (ruoniaRate.value = ruoniaRes.value.current_rate)
    }

    // CBR Daily Rates
    if (cbrDailyRes.status === 'fulfilled') {
      const rates = cbrDailyRes.value.rates
      const usd = rates.find((r) => r.char_code === 'USD')
      if (usd) usdRub.value = usd.vunit_rate || usd.value / usd.nominal
      cbrRatesList.value = rates.map((r) => ({
        char_code: r.char_code,
        name: r.name,
        nominal: r.nominal,
        value: r.value,
      }))
    }

    // Fed Funds Rate
    if (fedRes.status === 'fulfilled') {
      const obs = fedRes.value.observations.filter((o) => o.value != null)
      if (obs.length > 0) fedRate.value = obs[0].value
      fedHistory.value = obs
    }

    // Build global rates table
    const rates: Array<{ country: string; bank: string; rate: string; source: string }> = []

    if (keyRateRes.status === 'fulfilled') {
      rates.push({ country: 'Россия', bank: 'ЦБ РФ', rate: keyRateRes.value.current_rate.toFixed(2) + '%', source: 'CBR API' })
    }
    if (fedRes.status === 'fulfilled') {
      const obs = fedRes.value.observations.filter((o) => o.value != null)
      if (obs.length > 0) {
        rates.push({ country: 'США', bank: 'ФРС', rate: obs[0].value!.toFixed(2) + '%', source: 'FRED' })
      }
    }
    if (ecbRes.status === 'fulfilled') {
      rates.push({ country: 'Еврозона', bank: 'ЕЦБ', rate: 'EUR base', source: 'Frankfurter' })
    }

    globalRates.value = rates
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
