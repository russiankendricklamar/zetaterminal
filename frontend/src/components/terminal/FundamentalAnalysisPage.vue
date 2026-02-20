<template>
  <div class="page-container custom-scrollbar">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4 self-start md:self-auto">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center text-lg font-bold text-indigo-300 border border-indigo-500/30">
          FA
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Фундаментальный анализ</h2>
          <div class="flex items-center gap-4 text-xs text-gray-400">
            <span class="px-1.5 py-0.5 rounded bg-white/5 text-[10px] uppercase">DaData + SEC + yfinance</span>
          </div>
        </div>
      </div>

      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar self-stretch md:self-auto">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="section = tab.id"
          :class="`px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${section === tab.id ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5'}`"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <!-- ═══ Stock Info (yfinance) ═══ -->
      <div v-if="section === 'EE'" class="space-y-6">
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label class="text-xs text-gray-400 uppercase font-bold block mb-2">Тикер акции (yfinance)</label>
            <input
              v-model="stockTicker"
              type="text"
              placeholder="AAPL, MSFT, SBER.ME..."
              class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-indigo-500/50 outline-none"
              @keydown.enter="loadStockInfo"
            />
          </div>
          <button @click="loadStockInfo" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-colors">
            Загрузить
          </button>
        </div>

        <div class="flex flex-wrap gap-2">
          <button
            v-for="t in quickStockTickers"
            :key="t"
            @click="stockTicker = t; loadStockInfo()"
            class="px-3 py-1.5 bg-white/5 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-lg border border-white/5 transition-colors"
          >
            {{ t }}
          </button>
        </div>

        <div v-if="stockLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          Загрузка...
        </div>

        <div v-if="stockInfo" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-lg font-bold text-white mb-4">{{ stockInfo.name }}</h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between"><span class="text-gray-400">Цена</span><span class="text-white font-mono font-bold">{{ stockInfo.price?.toFixed(2) }} {{ stockInfo.currency }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Изменение</span><span :class="(stockInfo.changePercent || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'" class="font-mono">{{ (stockInfo.changePercent || 0) >= 0 ? '+' : '' }}{{ stockInfo.changePercent?.toFixed(2) }}%</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Market Cap</span><span class="text-white font-mono">{{ formatLargeNumber(stockInfo.marketCap) }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">P/E</span><span class="text-white font-mono">{{ stockInfo.peRatio?.toFixed(2) || '—' }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">P/B</span><span class="text-white font-mono">{{ stockInfo.priceToBook?.toFixed(2) || '—' }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Beta</span><span class="text-white font-mono">{{ stockInfo.beta?.toFixed(2) || '—' }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Dividend Yield</span><span class="text-white font-mono">{{ stockInfo.dividendYield ? (stockInfo.dividendYield * 100).toFixed(2) + '%' : '—' }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Sector</span><span class="text-white">{{ stockInfo.sector || '—' }}</span></div>
              <div class="flex justify-between"><span class="text-gray-400">Industry</span><span class="text-white">{{ stockInfo.industry || '—' }}</span></div>
            </div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Описание</h3>
            <p class="text-sm text-gray-300 leading-relaxed">{{ stockInfo.description || 'Нет описания' }}</p>
          </div>
        </div>
      </div>

      <!-- ═══ DaData Company Search ═══ -->
      <div v-else-if="section === 'ERN'" class="space-y-6">
        <h3 class="text-lg font-bold text-white">Поиск российских компаний (DaData)</h3>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label class="text-xs text-gray-400 uppercase font-bold block mb-2">ИНН / Название компании</label>
            <input
              v-model="dadataQuery"
              type="text"
              placeholder="7707083893 или Сбербанк..."
              class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-indigo-500/50 outline-none"
              @keydown.enter="searchDadata"
            />
          </div>
          <button @click="searchDadata" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-colors">
            Найти
          </button>
        </div>

        <div v-if="dadataLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          Поиск компании...
        </div>

        <div v-if="dadataResults.length > 0" class="space-y-4">
          <div v-for="(company, i) in dadataResults" :key="i" class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <div class="flex justify-between items-start mb-4">
              <div>
                <h4 class="text-lg font-bold text-white">{{ company.name }}</h4>
                <p class="text-xs text-gray-500 mt-1">{{ company.full_name }}</p>
              </div>
              <span :class="['px-2 py-1 rounded text-xs font-bold border', company.status === 'ACTIVE' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400']">
                {{ company.status }}
              </span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div><span class="text-gray-500 block text-xs">ИНН</span><span class="text-white font-mono">{{ company.inn }}</span></div>
              <div><span class="text-gray-500 block text-xs">ОГРН</span><span class="text-white font-mono">{{ company.ogrn }}</span></div>
              <div><span class="text-gray-500 block text-xs">КПП</span><span class="text-white font-mono">{{ company.kpp }}</span></div>
              <div><span class="text-gray-500 block text-xs">Тип</span><span class="text-white">{{ company.type }}</span></div>
            </div>
            <div v-if="company.address" class="mt-4 text-xs text-gray-400">
              {{ company.address }}
            </div>
            <div v-if="company.management_name" class="mt-2 text-xs text-gray-400">
              Руководитель: {{ company.management_name }} ({{ company.management_post }})
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ SEC Filings Search ═══ -->
      <div v-else-if="section === 'ANR'" class="space-y-6">
        <h3 class="text-lg font-bold text-white">SEC EDGAR — Поиск отчётности</h3>
        <div class="flex gap-4 items-end">
          <div class="flex-1">
            <label class="text-xs text-gray-400 uppercase font-bold block mb-2">Поиск (компания, CIK или форма)</label>
            <input
              v-model="secQuery"
              type="text"
              placeholder="Apple, Tesla, 10-K..."
              class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono focus:border-indigo-500/50 outline-none"
              @keydown.enter="searchSec"
            />
          </div>
          <button @click="searchSec" class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm transition-colors">
            Поиск
          </button>
        </div>

        <div v-if="secLoading" class="flex items-center gap-2 text-gray-400 text-xs">
          <div class="w-3 h-3 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          Поиск в SEC EDGAR...
        </div>

        <div v-if="secResults.length > 0" class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5">
                <th class="p-4">Форма</th>
                <th class="p-4">Компания</th>
                <th class="p-4">Дата</th>
                <th class="p-4">Описание</th>
              </tr>
            </thead>
            <tbody class="text-sm text-gray-300">
              <tr v-for="(filing, i) in secResults" :key="i" class="border-b border-white/5 hover:bg-white/5">
                <td class="p-4"><span class="text-xs font-bold bg-white/10 px-2 py-1 rounded text-white">{{ filing.form_type }}</span></td>
                <td class="p-4 text-white font-bold">{{ filing.entity_name }}</td>
                <td class="p-4 text-gray-400 font-mono text-xs">{{ filing.file_date }}</td>
                <td class="p-4 text-gray-500 text-xs">{{ filing.file_description }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <h3 class="text-xl font-bold text-white mb-2">{{ tabs.find(t => t.id === section)?.label }}</h3>
          <p class="text-gray-400">Содержимое появится в ближайшее время</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getStockInfo, type StockInfo } from '@/services/marketDataService'
import { suggestCompany, findCompany, type DaDataCompany } from '@/services/dadataService'
import { searchSecFilings } from '@/services/macroDataService'

const props = defineProps<{ symbol?: string; activeSection?: string }>()
const section = ref(props.activeSection || 'EE')
watch(() => props.activeSection, (v) => { if (v) section.value = v })

const tabs = [
  { id: 'EE', label: 'Акция (yfinance)' },
  { id: 'ERN', label: 'RU Компании (DaData)' },
  { id: 'ANR', label: 'SEC EDGAR' },
  { id: 'RV', label: 'Оценка' },
  { id: 'DVD', label: 'Дивиденды' },
]

// Stock info
const stockTicker = ref(props.symbol || 'AAPL')
const stockInfo = ref<StockInfo | null>(null)
const stockLoading = ref(false)
const quickStockTickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'SBER.ME', 'GAZP.ME', 'LKOH.ME']

const loadStockInfo = async () => {
  if (!stockTicker.value.trim()) return
  stockLoading.value = true
  try {
    stockInfo.value = await getStockInfo(stockTicker.value.trim())
  } catch {
    stockInfo.value = null
  } finally {
    stockLoading.value = false
  }
}

// DaData
const dadataQuery = ref('')
const dadataResults = ref<DaDataCompany[]>([])
const dadataLoading = ref(false)

const searchDadata = async () => {
  if (!dadataQuery.value.trim()) return
  dadataLoading.value = true
  try {
    const q = dadataQuery.value.trim()
    if (/^\d{10,13}$/.test(q)) {
      const res = await findCompany(q)
      dadataResults.value = res.companies
    } else {
      const res = await suggestCompany(q)
      dadataResults.value = res.suggestions.map((s) => ({
        ...s,
        full_name: s.name,
        short_name: s.name,
        kpp: '',
        okved: '',
        okved_type: '',
        management_name: '',
        management_post: '',
        capital: null,
        employees: null,
        registration_date: null,
      }))
    }
  } catch {
    dadataResults.value = []
  } finally {
    dadataLoading.value = false
  }
}

// SEC
const secQuery = ref('')
const secResults = ref<Array<{ form_type: string; entity_name: string; file_date: string; file_description: string }>>([])
const secLoading = ref(false)

const searchSec = async () => {
  if (!secQuery.value.trim()) return
  secLoading.value = true
  try {
    const res = await searchSecFilings(secQuery.value.trim())
    secResults.value = res.filings
  } catch {
    secResults.value = []
  } finally {
    secLoading.value = false
  }
}

const formatLargeNumber = (n: number | undefined): string => {
  if (n == null) return '—'
  if (n >= 1e12) return `${(n / 1e12).toFixed(2)}T`
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`
  return n.toLocaleString()
}
</script>
