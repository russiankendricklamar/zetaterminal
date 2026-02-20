<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-green">
          <LayersIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ОБЛИГАЦИИ</h2>
          <p class="section-subtitle font-mono">ОФЗ, КОРПОРАТИВНЫЕ ОБЛИГАЦИИ MOEX</p>
        </div>
      </div>
      <div class="tab-group">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['tab-btn', { active: section === tab.id }]">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs p-4">
      <div class="w-3 h-3 border-2 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
      Загрузка облигаций MOEX...
    </div>

    <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono mx-4">
      {{ loadError }}
    </div>

    <div class="flex-1 flex flex-col gap-6">
      <!-- ═══ OFZ (Government Bonds) ═══ -->
      <div v-if="section === 'BBT'" class="flex flex-col h-full gap-6">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-bold text-white">ОФЗ — Облигации федерального займа</h3>
          <button @click="loadBonds" class="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-xs font-bold text-white rounded-lg transition-colors">
            Обновить
          </button>
        </div>

        <div v-if="ofzBonds.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
                <th class="p-4 font-bold">Тикер</th>
                <th class="p-4 font-bold">Название</th>
                <th class="p-4 font-bold text-right">Цена</th>
                <th class="p-4 font-bold text-right">Изменение</th>
                <th class="p-4 font-bold text-right">Объём</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="bond in ofzBonds" :key="bond.ticker" class="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer">
                <td class="p-4">
                  <span class="text-xs font-bold bg-teal-500/10 px-2 py-1 rounded text-teal-400 border border-teal-500/20">{{ bond.ticker }}</span>
                </td>
                <td class="p-4 text-gray-300 text-xs">{{ bond.name }}</td>
                <td class="p-4 text-right font-bold text-white">{{ bond.last != null ? bond.last.toFixed(2) : '—' }}</td>
                <td class="p-4 text-right">
                  <span v-if="bond.change_pct != null" :class="bond.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono text-xs">
                    {{ bond.change_pct >= 0 ? '+' : '' }}{{ bond.change_pct.toFixed(2) }}%
                  </span>
                  <span v-else class="text-gray-500 text-xs">—</span>
                </td>
                <td class="p-4 text-right text-gray-400 text-xs">{{ bond.volume != null ? formatVolume(bond.volume) : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!loading && ofzBonds.length === 0 && !loadError" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
          Нет данных по ОФЗ
        </div>
      </div>

      <!-- ═══ Corporate Bonds ═══ -->
      <div v-else-if="section === 'ALLQ'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Корпоративные облигации MOEX</h3>

        <div v-if="corpBonds.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
                <th class="p-4 font-bold">Тикер</th>
                <th class="p-4 font-bold">Название</th>
                <th class="p-4 font-bold text-right">Цена</th>
                <th class="p-4 font-bold text-right">Изменение</th>
                <th class="p-4 font-bold text-right">Объём</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="bond in corpBonds" :key="bond.ticker" class="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer">
                <td class="p-4">
                  <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ bond.ticker }}</span>
                </td>
                <td class="p-4 text-gray-300 text-xs">{{ bond.name }}</td>
                <td class="p-4 text-right font-bold text-white">{{ bond.last != null ? bond.last.toFixed(2) : '—' }}</td>
                <td class="p-4 text-right">
                  <span v-if="bond.change_pct != null" :class="bond.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono text-xs">
                    {{ bond.change_pct >= 0 ? '+' : '' }}{{ bond.change_pct.toFixed(2) }}%
                  </span>
                  <span v-else class="text-gray-500 text-xs">—</span>
                </td>
                <td class="p-4 text-right text-gray-400 text-xs">{{ bond.volume != null ? formatVolume(bond.volume) : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- ═══ CBR Deposit & Repo Rates ═══ -->
      <div v-else-if="section === 'PICK'" class="flex flex-col h-full gap-6">
        <h3 class="text-lg font-bold text-white">Ставки ЦБР: Депозиты и Репо</h3>
        <div v-if="depositRates.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <div class="p-4 bg-white/5 border-b border-white/5">
            <h3 class="font-bold text-white text-sm">Средние ставки по депозитам</h3>
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
                <td class="p-4 text-right text-teal-400">{{ r.overnight != null ? r.overnight.toFixed(2) + '%' : '—' }}</td>
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
import { getMoexSecurities, type MoexSecurity } from '@/services/moexalgoService'
import { getCbrDepositRates } from '@/services/macroDataService'

const LayersIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [h('polygon', { points: '12 2 2 7 12 12 22 7 12 2' }), h('polyline', { points: '2 17 12 22 22 17' }), h('polyline', { points: '2 12 12 17 22 12' })]) })

const props = defineProps<{ activeSection?: string }>()
const section = ref(props.activeSection || 'BBT')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'BBT', label: 'ОФЗ' },
  { id: 'ALLQ', label: 'Корпоративные' },
  { id: 'PICK', label: 'Ставки ЦБР' },
]

const loading = ref(false)
const loadError = ref<string | null>(null)

interface BondItem {
  ticker: string
  name: string
  last: number | null
  change_pct: number | null
  volume: number | null
}

const ofzBonds = ref<BondItem[]>([])
const corpBonds = ref<BondItem[]>([])
const depositRates = ref<Array<{ date: string; overnight: number | null }>>([])

const loadBonds = async () => {
  loading.value = true
  loadError.value = null
  try {
    const [ofzRes, corpRes, depoRes] = await Promise.allSettled([
      getMoexSecurities('TQOB', 'bonds', 'stock'),
      getMoexSecurities('TQCB', 'bonds', 'stock'),
      getCbrDepositRates(),
    ])

    if (ofzRes.status === 'fulfilled') {
      ofzBonds.value = ofzRes.value.securities
        .filter((s: MoexSecurity) => s.last != null)
        .sort((a: MoexSecurity, b: MoexSecurity) => (b.volume ?? 0) - (a.volume ?? 0))
        .slice(0, 30)
        .map((s: MoexSecurity) => ({
          ticker: s.secid,
          name: s.name || s.secid,
          last: s.last,
          change_pct: s.change_pct,
          volume: s.volume,
        }))
    }

    if (corpRes.status === 'fulfilled') {
      corpBonds.value = corpRes.value.securities
        .filter((s: MoexSecurity) => s.last != null)
        .sort((a: MoexSecurity, b: MoexSecurity) => (b.volume ?? 0) - (a.volume ?? 0))
        .slice(0, 30)
        .map((s: MoexSecurity) => ({
          ticker: s.secid,
          name: s.name || s.secid,
          last: s.last,
          change_pct: s.change_pct,
          volume: s.volume,
        }))
    }

    if (depoRes.status === 'fulfilled') {
      depositRates.value = depoRes.value.rates.slice(0, 20)
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
  loadBonds()
})
</script>
