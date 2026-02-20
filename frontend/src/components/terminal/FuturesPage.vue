<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-blue">
          <GitCommitIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ФЬЮЧЕРСЫ</h2>
          <p class="section-subtitle font-mono">КОНТРАКТЫ MOEX FORTS, ОИ И ОБЪЁМ</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка фьючерсов MOEX...
    </div>

    <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono mx-4">
      {{ loadError }}
    </div>

    <div class="flex-1 flex flex-col gap-6">
      <!-- ═══ Futures Contracts ═══ -->
      <div v-if="section === 'FUT'" class="flex flex-col h-full gap-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">Фьючерсы MOEX (RFUD)</h3>
          <button @click="loadFutures" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="futuresContracts.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
                <th class="p-4 font-bold">Тикер</th>
                <th class="p-4 font-bold">Название</th>
                <th class="p-4 font-bold text-right">Последняя</th>
                <th class="p-4 font-bold text-right">Изменение</th>
                <th class="p-4 font-bold text-right">Объём</th>
                <th class="p-4 font-bold text-right">OI</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="c in futuresContracts" :key="c.ticker" class="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer">
                <td class="p-4">
                  <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ c.ticker }}</span>
                </td>
                <td class="p-4 text-xs text-gray-400">{{ c.name }}</td>
                <td class="p-4 text-right font-bold text-white">{{ c.last != null ? c.last.toLocaleString() : '—' }}</td>
                <td class="p-4 text-right">
                  <span v-if="c.change_pct != null" :class="c.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono text-xs">
                    {{ c.change_pct >= 0 ? '+' : '' }}{{ c.change_pct.toFixed(2) }}%
                  </span>
                  <span v-else class="text-gray-500 text-xs">—</span>
                </td>
                <td class="p-4 text-right text-gray-400 text-xs">{{ c.volume != null ? formatVolume(c.volume) : '—' }}</td>
                <td class="p-4 text-right text-cyan-400 text-xs">{{ c.oi != null ? formatVolume(c.oi) : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!loading && futuresContracts.length === 0 && !loadError" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет данных по фьючерсам
        </div>
      </div>

      <!-- ═══ Open Interest Detail ═══ -->
      <div v-else-if="section === 'FWCV'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Открытый интерес — детали</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center cursor-pointer hover:bg-white/10 transition-colors"
               v-for="ticker in oiTickers" :key="ticker"
               @click="loadOI(ticker)">
            <span class="text-sm font-bold text-white">{{ ticker }}</span>
          </div>
        </div>

        <div v-if="oiData.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h3 class="font-bold text-white">OI: {{ selectedOiTicker }}</h3>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-500 uppercase">
                <th class="p-4">Дата</th>
                <th class="p-4 text-right">OI</th>
                <th class="p-4 text-right">Объём</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(item, i) in oiData" :key="i" class="border-t border-white/5 hover:bg-white/5">
                <td class="p-4 text-white">{{ item.date }}</td>
                <td class="p-4 text-right text-cyan-400">{{ formatVolume(item.oi) }}</td>
                <td class="p-4 text-right text-gray-400">{{ formatVolume(item.volume) }}</td>
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
import { getMoexSecurities, getMoexFuturesOI, type MoexSecurity } from '@/services/moexalgoService'

const GitCommitIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '4' }), h('line', { x1: '1.05', y1: '12', x2: '7', y2: '12' }), h('line', { x1: '17.01', y1: '12', x2: '22.96', y2: '12' })]) })

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'FUT')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'FUT', label: 'Фьючерсы' },
  { id: 'FWCV', label: 'Открытый интерес' },
]

const loading = ref(false)
const loadError = ref<string | null>(null)

interface FutureContract {
  ticker: string
  name: string
  last: number | null
  change_pct: number | null
  volume: number | null
  oi: number | null
}

const futuresContracts = ref<FutureContract[]>([])

// OI tab
const oiTickers = ['SiZ5', 'RIZ5', 'BRX5', 'GDZ5', 'EDZ5', 'EuZ5', 'SRZ5', 'GZZ5']
const selectedOiTicker = ref('')
const oiData = ref<Array<{ date: string; oi: number; volume: number }>>([])

const loadFutures = async () => {
  loading.value = true
  loadError.value = null
  try {
    const res = await getMoexSecurities('RFUD', 'futures', 'stock')
    futuresContracts.value = res.securities
      .filter((s: MoexSecurity) => s.last != null || s.volume != null)
      .sort((a: MoexSecurity, b: MoexSecurity) => (b.volume ?? 0) - (a.volume ?? 0))
      .slice(0, 30)
      .map((s: MoexSecurity) => ({
        ticker: s.secid,
        name: s.name || s.secid,
        last: s.last,
        change_pct: s.change_pct,
        volume: s.volume,
        oi: null,
      }))
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки фьючерсов'
  } finally {
    loading.value = false
  }
}

const loadOI = async (ticker: string) => {
  selectedOiTicker.value = ticker
  try {
    const res = await getMoexFuturesOI(ticker) as { data: Array<{ date: string; oi: number; volume: number }> }
    oiData.value = res.data.slice(0, 20).map((d) => ({
      date: d.date,
      oi: d.oi,
      volume: d.volume,
    }))
  } catch {
    oiData.value = []
  }
}

const formatVolume = (vol: number): string => {
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K`
  return vol.toString()
}

onMounted(() => {
  loadFutures()
})
</script>
