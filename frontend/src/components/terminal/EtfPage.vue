<template>
  <div class="page-container custom-scrollbar">
    <div class="section-header flex-col gap-4">
      <div class="flex justify-between items-center w-full">
        <div>
          <h2 class="section-title font-anton">ETF</h2>
          <p class="section-subtitle font-mono">БИРЖЕВЫЕ ФОНДЫ — MOEX И МЕЖДУНАРОДНЫЕ</p>
        </div>
        <div class="tab-group">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ MOEX ETFs ═══ -->
    <div v-if="activeTab === 'RU'" class="flex flex-col gap-4">
      <div v-if="loading" class="flex items-center gap-2 text-gray-400 text-xs">
        <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        Загрузка ETF с MOEX...
      </div>

      <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono">
        {{ loadError }}
      </div>

      <div class="overflow-auto custom-scrollbar flex-1">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-500 border-b border-white/5 uppercase tracking-wider">
              <th class="font-bold py-4 px-4 pl-0">Тикер</th>
              <th class="font-bold py-4 px-4">Название</th>
              <th class="font-bold py-4 px-4 text-right">Цена</th>
              <th class="font-bold py-4 px-4 text-right">Изменение</th>
              <th class="font-bold py-4 px-4 text-right hidden md:table-cell">Объём</th>
              <th class="font-bold py-4 px-4 text-right hidden lg:table-cell">ISIN</th>
            </tr>
          </thead>
          <tbody class="text-sm font-medium">
            <tr
              v-for="etf in sortedEtfs"
              :key="etf.ticker"
              class="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
            >
              <td class="py-3 px-4 pl-0">
                <span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ etf.ticker }}</span>
              </td>
              <td class="py-3 px-4 text-gray-300">{{ etf.name }}</td>
              <td class="py-3 px-4 text-right font-mono text-white">
                {{ etf.last != null ? etf.last.toFixed(2) : '—' }}
                <span class="text-[10px] text-gray-500 ml-1">{{ etf.currency }}</span>
              </td>
              <td class="py-3 px-4 text-right">
                <span v-if="etf.change_pct != null" :class="etf.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono text-xs">
                  {{ etf.change_pct >= 0 ? '+' : '' }}{{ etf.change_pct.toFixed(2) }}%
                </span>
                <span v-else class="text-gray-500 text-xs">—</span>
              </td>
              <td class="py-3 px-4 text-right hidden md:table-cell font-mono text-gray-400 text-xs">
                {{ etf.volume != null ? formatVolume(etf.volume) : '—' }}
              </td>
              <td class="py-3 px-4 text-right hidden lg:table-cell font-mono text-gray-500 text-xs">
                {{ etf.isin || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loading && etfs.length === 0 && !loadError" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Нет данных по ETF
      </div>
    </div>

    <!-- ═══ International ETFs ═══ -->
    <div v-else-if="activeTab === 'INTL'" class="flex flex-col gap-6">
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div
          v-for="ticker in intlTickers"
          :key="ticker"
          class="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/20 transition-all cursor-pointer text-center"
        >
          <div class="text-sm font-bold text-white">{{ ticker }}</div>
          <div class="text-[10px] text-gray-500 mt-1 font-mono">{{ getEtfDescription(ticker) }}</div>
        </div>
      </div>
      <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-xs text-gray-500 font-mono">
        Данные по международным ETF доступны через API market-data (yfinance).
        Используйте раздел "Акции" для просмотра цен.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getEtfList, type EtfItem } from '@/services/etfService'

const tabs = [
  { id: 'RU', label: 'MOEX ETF' },
  { id: 'INTL', label: 'Международные' },
]
const activeTab = ref('RU')

// ─── MOEX ETFs ──────────────────────────────────────────────────────────────
const etfs = ref<EtfItem[]>([])
const loading = ref(false)
const loadError = ref<string | null>(null)

const loadEtfs = async () => {
  loading.value = true
  loadError.value = null
  try {
    const result = await getEtfList()
    etfs.value = result.etfs
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки ETF'
  } finally {
    loading.value = false
  }
}

const sortedEtfs = computed(() =>
  [...etfs.value].sort((a, b) => (b.value ?? 0) - (a.value ?? 0))
)

const formatVolume = (vol: number): string => {
  if (vol >= 1e9) return `${(vol / 1e9).toFixed(2)}B`
  if (vol >= 1e6) return `${(vol / 1e6).toFixed(2)}M`
  if (vol >= 1e3) return `${(vol / 1e3).toFixed(1)}K`
  return vol.toString()
}

// ─── International ETFs ─────────────────────────────────────────────────────
const intlTickers = [
  'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'EFA', 'EEM',
  'GLD', 'SLV', 'TLT', 'HYG', 'LQD', 'XLF', 'XLE', 'XLK', 'XLV',
  'ARKK', 'IBIT', 'ETHA',
]

const etfDescriptions: Record<string, string> = {
  SPY: 'S&P 500', QQQ: 'Nasdaq 100', IWM: 'Russell 2000', VTI: 'Total US Market',
  VOO: 'S&P 500 (Vanguard)', VEA: 'Developed Markets', VWO: 'Emerging Markets',
  EFA: 'EAFE (iShares)', EEM: 'Emerging (iShares)', GLD: 'Gold', SLV: 'Silver',
  TLT: '20+ Year Treasury', HYG: 'High Yield Corp', LQD: 'Invest Grade Corp',
  XLF: 'Financials', XLE: 'Energy', XLK: 'Technology', XLV: 'Healthcare',
  ARKK: 'ARK Innovation', IBIT: 'Bitcoin (iShares)', ETHA: 'Ethereum (iShares)',
}

const getEtfDescription = (ticker: string): string => etfDescriptions[ticker] || ticker

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  loadEtfs()
})
</script>
