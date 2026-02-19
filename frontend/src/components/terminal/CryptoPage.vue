<template>
  <div class="page-container custom-scrollbar">

    <div class="section-header flex-col gap-4">
      <div class="flex justify-between items-center w-full">
        <div>
          <h2 class="section-title font-anton">КРИПТОВАЛЮТЫ</h2>
          <p class="section-subtitle font-mono">ЦЕНЫ И АНАЛИТИКА В РЕАЛЬНОМ ВРЕМЕНИ</p>
        </div>
        <div class="tab-group">
          <button
            v-for="tab in mainTabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Global Stats Bar -->
      <div v-if="globalStats && activeTab === 'MARKET'" class="flex flex-wrap gap-4 text-xs font-mono">
        <span class="text-gray-500">
          Крипто: <span class="text-white font-bold">{{ globalStats.active_cryptocurrencies.toLocaleString() }}</span>
        </span>
        <span class="text-gray-500">
          Биржи: <span class="text-white font-bold">{{ globalStats.markets }}</span>
        </span>
        <span class="text-gray-500">
          Капитализация: <span class="text-white font-bold">${{ formatLargeNum(globalStats.total_market_cap?.usd) }}</span>
        </span>
        <span class="text-gray-500">
          Объём 24ч: <span class="text-white font-bold">${{ formatLargeNum(globalStats.total_volume?.usd) }}</span>
        </span>
        <span :class="globalStats.market_cap_change_percentage_24h_usd >= 0 ? 'text-emerald-400' : 'text-rose-400'">
          {{ globalStats.market_cap_change_percentage_24h_usd >= 0 ? '+' : '' }}{{ globalStats.market_cap_change_percentage_24h_usd?.toFixed(2) }}% 24ч
        </span>
        <span class="text-gray-500">
          BTC: <span class="text-orange-400 font-bold">{{ globalStats.market_cap_percentage?.btc?.toFixed(1) }}%</span>
        </span>
        <span class="text-gray-500">
          ETH: <span class="text-blue-400 font-bold">{{ globalStats.market_cap_percentage?.eth?.toFixed(1) }}%</span>
        </span>
      </div>

      <!-- Filters (Market tab only) -->
      <div v-if="activeTab === 'MARKET'" class="flex flex-wrap items-center gap-3">
        <div class="flex gap-2">
          <button
            v-for="filter in sortFilters"
            :key="filter.id"
            @click="activeSort = filter.id"
            :class="['tab-btn text-xs', { active: activeSort === filter.id }]"
          >
            {{ filter.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- ═══ MARKET TAB ═══ -->
    <div v-if="activeTab === 'MARKET'">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center py-8 text-gray-400 flex-shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-4 h-4 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-xs font-bold">Загрузка данных CoinGecko...</span>
        </div>
      </div>

      <!-- Error -->
      <div v-if="loadError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono mb-4">
        {{ loadError }}
      </div>

      <div class="overflow-auto custom-scrollbar flex-1" :class="{ 'opacity-50': loading }">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-500 border-b border-white/5 uppercase tracking-wider">
              <th class="font-bold py-4 px-4 pl-0 w-8">#</th>
              <th class="font-bold py-4 px-4">Инструмент</th>
              <th class="font-bold py-4 px-4 text-right">Цена</th>
              <th class="font-bold py-4 px-4 text-right">1ч</th>
              <th class="font-bold py-4 px-4 text-right">24ч</th>
              <th class="font-bold py-4 px-4 text-right hidden md:table-cell">7д</th>
              <th class="font-bold py-4 px-4 text-right hidden lg:table-cell">Капитализация</th>
              <th class="font-bold py-4 px-4 text-right hidden lg:table-cell">Объём 24ч</th>
              <th class="font-bold py-4 px-4 text-right hidden xl:table-cell w-[120px]">7д график</th>
            </tr>
          </thead>
          <tbody class="text-sm font-medium">
            <tr
              v-for="coin in sortedCoins"
              :key="coin.id"
              class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer"
            >
              <td class="py-3 px-4 pl-0 text-gray-500 text-xs font-mono">{{ coin.market_cap_rank }}</td>
              <td class="py-3 px-4">
                <div class="flex items-center gap-3">
                  <img v-if="coin.image" :src="coin.image" :alt="coin.symbol" class="w-8 h-8 rounded-full" loading="lazy" />
                  <div v-else class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold bg-gradient-to-br from-orange-500/20 to-yellow-500/20 text-orange-400">
                    {{ coin.symbol.substring(0, 2).toUpperCase() }}
                  </div>
                  <div>
                    <div class="text-white font-bold">{{ coin.symbol.toUpperCase() }}</div>
                    <div class="text-xs text-gray-500 truncate max-w-[140px]">{{ coin.name }}</div>
                  </div>
                </div>
              </td>
              <td class="py-3 px-4 text-right font-mono text-white">${{ formatPrice(coin.current_price) }}</td>
              <td class="py-3 px-4 text-right">
                <span :class="changeClass(coin.price_change_percentage_1h_in_currency)">
                  {{ formatPct(coin.price_change_percentage_1h_in_currency) }}
                </span>
              </td>
              <td class="py-3 px-4 text-right">
                <span :class="changeClass(coin.price_change_percentage_24h)">
                  {{ formatPct(coin.price_change_percentage_24h) }}
                </span>
              </td>
              <td class="py-3 px-4 text-right hidden md:table-cell">
                <span :class="changeClass(coin.price_change_percentage_7d_in_currency)">
                  {{ formatPct(coin.price_change_percentage_7d_in_currency) }}
                </span>
              </td>
              <td class="py-3 px-4 text-right hidden lg:table-cell font-mono text-gray-400">
                ${{ formatLargeNum(coin.market_cap) }}
              </td>
              <td class="py-3 px-4 text-right hidden lg:table-cell font-mono text-gray-400">
                ${{ formatLargeNum(coin.total_volume) }}
              </td>
              <td class="py-3 px-4 text-right hidden xl:table-cell">
                <svg v-if="coin.sparkline_in_7d?.price" :viewBox="`0 0 120 40`" class="w-[100px] h-[32px] inline-block">
                  <polyline
                    :points="sparklinePoints(coin.sparkline_in_7d.price)"
                    fill="none"
                    :stroke="(coin.price_change_percentage_7d_in_currency ?? 0) >= 0 ? '#10b981' : '#f43f5e'"
                    stroke-width="1.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ═══ TRENDING TAB ═══ -->
    <div v-else-if="activeTab === 'TRENDING'" class="flex flex-col gap-6">
      <div v-if="trendingLoading" class="flex items-center gap-2 text-gray-400 text-xs">
        <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        Загрузка трендов...
      </div>

      <div v-if="trendingCoins.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="(coin, idx) in trendingCoins"
          :key="coin.id"
          class="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/20 transition-all"
        >
          <div class="flex items-center gap-3 mb-3">
            <span class="text-xs font-bold text-gray-500">#{{ idx + 1 }}</span>
            <img v-if="coin.thumb" :src="coin.thumb" :alt="coin.name" class="w-6 h-6 rounded-full" />
            <div>
              <span class="text-sm text-white font-bold">{{ coin.name }}</span>
              <span class="text-xs text-gray-500 ml-2 uppercase">{{ coin.symbol }}</span>
            </div>
          </div>
          <div class="flex items-center justify-between text-xs font-mono">
            <span class="text-gray-500">Ранг: <span class="text-white">{{ coin.market_cap_rank ?? '—' }}</span></span>
            <span v-if="coin.price_btc" class="text-orange-400">{{ coin.price_btc.toFixed(8) }} BTC</span>
          </div>
        </div>
      </div>

      <div v-if="!trendingLoading && trendingCoins.length === 0" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Нет данных о трендах
      </div>
    </div>

    <!-- ═══ GLOBAL TAB ═══ -->
    <div v-else-if="activeTab === 'GLOBAL'" class="flex flex-col gap-6">
      <div v-if="!globalStats" class="flex items-center gap-2 text-gray-400 text-xs">
        <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        Загрузка глобальной статистики...
      </div>

      <div v-if="globalStats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">Общая капитализация</h3>
          <div class="text-3xl font-bold text-white">${{ formatLargeNum(globalStats.total_market_cap?.usd) }}</div>
          <div :class="['text-xs mt-1', globalStats.market_cap_change_percentage_24h_usd >= 0 ? 'text-emerald-400' : 'text-rose-400']">
            {{ globalStats.market_cap_change_percentage_24h_usd >= 0 ? '+' : '' }}{{ globalStats.market_cap_change_percentage_24h_usd?.toFixed(2) }}% за 24ч
          </div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">Объём торгов 24ч</h3>
          <div class="text-3xl font-bold text-white">${{ formatLargeNum(globalStats.total_volume?.usd) }}</div>
        </div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
          <h3 class="text-xs font-bold text-gray-400 uppercase mb-2">Активных криптовалют</h3>
          <div class="text-3xl font-bold text-white">{{ globalStats.active_cryptocurrencies?.toLocaleString() }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ globalStats.markets }} бирж</div>
        </div>
      </div>

      <!-- Dominance -->
      <div v-if="globalStats?.market_cap_percentage" class="flex flex-col gap-3">
        <h3 class="font-oswald text-sm text-gray-400 uppercase tracking-wider">ДОМИНАЦИЯ ПО КАПИТАЛИЗАЦИИ</h3>
        <div class="flex flex-wrap gap-3">
          <div
            v-for="(pct, symbol) in topDominance"
            :key="symbol"
            class="px-4 py-3 rounded-xl bg-white/5 border border-white/5 text-center min-w-[100px]"
          >
            <div class="text-xs text-gray-500 uppercase font-bold mb-1">{{ symbol }}</div>
            <div class="text-lg font-bold text-white font-mono">{{ pct.toFixed(1) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ ARBITRAGE TAB ═══ -->
    <div v-else-if="activeTab === 'ARB'" class="flex flex-col gap-6">
      <div v-if="arbLoading" class="flex items-center gap-2 text-gray-400 text-xs">
        <div class="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        Поиск арбитражных возможностей...
      </div>

      <div v-if="arbError" class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-mono">
        {{ arbError }}
      </div>

      <div v-if="arbOpportunities.length > 0" class="overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0">
              <th class="p-3">Пара</th>
              <th class="p-3 text-right">Биржа 1</th>
              <th class="p-3 text-right">Биржа 2</th>
              <th class="p-3 text-right">Спред</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr v-for="(opp, idx) in arbOpportunities" :key="idx" class="border-b border-white/5 hover:bg-white/5">
              <td class="p-3 text-white font-bold">{{ opp.symbol || opp.pair || '—' }}</td>
              <td class="p-3 text-right text-gray-400">{{ opp.exchange1 || opp.buy_exchange || '—' }}</td>
              <td class="p-3 text-right text-gray-400">{{ opp.exchange2 || opp.sell_exchange || '—' }}</td>
              <td class="p-3 text-right font-bold text-emerald-400">{{ opp.spread || opp.profit_pct || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!arbLoading && arbOpportunities.length === 0 && !arbError" class="flex items-center justify-center h-64 text-gray-500 font-mono text-sm">
        Нет доступных арбитражных возможностей
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import {
  getCoinGeckoMarkets,
  getTrendingCoins,
  getGlobalStats,
  getArbitrageOpportunities,
  type CoinMarket,
  type GlobalStats,
} from '@/services/cryptoDataService'

const emit = defineEmits<{
  navigate: [page: string]
}>()

// ─── Tabs ───────────────────────────────────────────────────────────────────
const mainTabs = [
  { id: 'MARKET', label: 'Рынок' },
  { id: 'TRENDING', label: 'Тренды' },
  { id: 'GLOBAL', label: 'Глобал' },
  { id: 'ARB', label: 'Арбитраж' },
]
const activeTab = ref('MARKET')

const sortFilters = [
  { id: 'market_cap', label: 'Капитализация' },
  { id: 'gainers', label: 'Топ роста' },
  { id: 'losers', label: 'Топ падения' },
  { id: 'volume', label: 'Объём' },
]
const activeSort = ref('market_cap')

// ─── MARKET: CoinGecko Markets ──────────────────────────────────────────────
const coins = ref<CoinMarket[]>([])
const loading = ref(false)
const loadError = ref<string | null>(null)

const loadMarkets = async () => {
  loading.value = true
  loadError.value = null
  try {
    coins.value = await getCoinGeckoMarkets('usd', 100, 1)
  } catch (e: unknown) {
    loadError.value = e instanceof Error ? e.message : 'Ошибка загрузки данных CoinGecko'
  } finally {
    loading.value = false
  }
}

const sortedCoins = computed(() => {
  const list = [...coins.value]
  switch (activeSort.value) {
    case 'gainers':
      return list.sort((a, b) => (b.price_change_percentage_24h ?? 0) - (a.price_change_percentage_24h ?? 0))
    case 'losers':
      return list.sort((a, b) => (a.price_change_percentage_24h ?? 0) - (b.price_change_percentage_24h ?? 0))
    case 'volume':
      return list.sort((a, b) => (b.total_volume ?? 0) - (a.total_volume ?? 0))
    default:
      return list.sort((a, b) => (a.market_cap_rank ?? 999) - (b.market_cap_rank ?? 999))
  }
})

// ─── TRENDING ───────────────────────────────────────────────────────────────
interface TrendingCoin {
  id: string
  name: string
  symbol: string
  thumb?: string
  market_cap_rank?: number
  price_btc?: number
}

const trendingCoins = ref<TrendingCoin[]>([])
const trendingLoading = ref(false)

const loadTrending = async () => {
  trendingLoading.value = true
  try {
    const data = await getTrendingCoins()
    const items = (data as Record<string, unknown>).coins as Array<{ item: TrendingCoin }> | undefined
    trendingCoins.value = items?.map(c => c.item) ?? []
  } catch {
    trendingCoins.value = []
  } finally {
    trendingLoading.value = false
  }
}

// ─── GLOBAL ─────────────────────────────────────────────────────────────────
const globalStats = ref<GlobalStats | null>(null)

const loadGlobal = async () => {
  try {
    globalStats.value = await getGlobalStats()
  } catch {
    globalStats.value = null
  }
}

const topDominance = computed(() => {
  if (!globalStats.value?.market_cap_percentage) return {}
  const entries = Object.entries(globalStats.value.market_cap_percentage)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
  return Object.fromEntries(entries)
})

// ─── ARBITRAGE ──────────────────────────────────────────────────────────────
const arbOpportunities = ref<Record<string, unknown>[]>([])
const arbLoading = ref(false)
const arbError = ref<string | null>(null)

const loadArbitrage = async () => {
  arbLoading.value = true
  arbError.value = null
  try {
    arbOpportunities.value = await getArbitrageOpportunities()
  } catch (e: unknown) {
    arbError.value = e instanceof Error ? e.message : 'Ошибка загрузки арбитражных данных'
  } finally {
    arbLoading.value = false
  }
}

// ─── Helpers ────────────────────────────────────────────────────────────────
const formatPrice = (price: number): string => {
  if (price >= 1) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  if (price >= 0.01) return price.toFixed(4)
  return price.toFixed(8)
}

const formatPct = (pct?: number): string => {
  if (pct == null) return '—'
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`
}

const changeClass = (pct?: number): string => {
  if (pct == null) return 'text-gray-500 font-mono text-xs'
  return pct >= 0
    ? 'text-emerald-400 font-mono text-xs'
    : 'text-rose-400 font-mono text-xs'
}

const formatLargeNum = (num?: number): string => {
  if (num == null) return '—'
  if (num >= 1e12) return `${(num / 1e12).toFixed(2)}T`
  if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`
  if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`
  return num.toLocaleString()
}

const sparklinePoints = (prices: number[]): string => {
  if (!prices || prices.length === 0) return ''
  const step = 120 / (prices.length - 1)
  const min = Math.min(...prices)
  const max = Math.max(...prices)
  const range = max - min || 1
  return prices
    .map((p, i) => `${(i * step).toFixed(1)},${(40 - ((p - min) / range) * 36).toFixed(1)}`)
    .join(' ')
}

// ─── Lifecycle ──────────────────────────────────────────────────────────────
let updateInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadMarkets()
  loadGlobal()
  loadTrending()

  updateInterval = setInterval(() => {
    loadMarkets()
  }, 60000)
})

onBeforeUnmount(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>
