<!-- src/pages/CryptoMarkets.vue — Crypto Markets Dashboard -->
<template>
  <div class="page-container">
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Крипто рынки</h1>
        <p class="section-subtitle">CoinGecko + CoinGap</p>
      </div>
      <div class="header-actions">
        <select v-model="currency" class="glass-select" @change="loadMarkets">
          <option value="usd">USD</option>
          <option value="eur">EUR</option>
          <option value="rub">RUB</option>
        </select>
        <button class="btn-glass" @click="refreshAll" :disabled="loading">
          {{ loading ? 'Загрузка...' : 'Обновить' }}
        </button>
      </div>
    </div>

    <!-- Global Stats -->
    <div v-if="globalStats" class="stats-row">
      <div class="stat-card">
        <span class="stat-label font-mono">Market Cap</span>
        <span class="stat-value font-mono">${{ formatNum(globalStats.total_market_cap?.usd || 0) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label font-mono">24h Volume</span>
        <span class="stat-value font-mono">${{ formatNum(globalStats.total_volume?.usd || 0) }}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label font-mono">BTC Dominance</span>
        <span class="stat-value font-mono">{{ (globalStats.market_cap_percentage?.btc || 0).toFixed(1) }}%</span>
      </div>
      <div class="stat-card">
        <span class="stat-label font-mono">24h Change</span>
        <span class="stat-value font-mono" :class="globalStats.market_cap_change_percentage_24h_usd > 0 ? 'text-green' : 'text-red'">
          {{ (globalStats.market_cap_change_percentage_24h_usd || 0).toFixed(2) }}%
        </span>
      </div>
    </div>

    <!-- Markets Table -->
    <div class="glass-panel">
      <h3 class="block-title">Топ криптовалюты</h3>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Монета</th>
              <th class="text-right">Цена</th>
              <th class="text-right">24h %</th>
              <th class="text-right">7d %</th>
              <th class="text-right">Market Cap</th>
              <th class="text-right">Volume 24h</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="coin in markets" :key="coin.id" @click="selectedCoin = coin.id" class="clickable">
              <td class="font-mono">{{ coin.market_cap_rank }}</td>
              <td>
                <div class="coin-cell">
                  <img :src="coin.image" :alt="coin.symbol" class="coin-img" />
                  <span class="coin-name">{{ coin.name }}</span>
                  <span class="coin-symbol font-mono">{{ coin.symbol.toUpperCase() }}</span>
                </div>
              </td>
              <td class="font-mono text-right">${{ coin.current_price?.toLocaleString() }}</td>
              <td class="font-mono text-right" :class="(coin.price_change_percentage_24h || 0) > 0 ? 'text-green' : 'text-red'">
                {{ (coin.price_change_percentage_24h || 0).toFixed(2) }}%
              </td>
              <td class="font-mono text-right" :class="(coin.price_change_percentage_7d_in_currency || 0) > 0 ? 'text-green' : 'text-red'">
                {{ (coin.price_change_percentage_7d_in_currency || 0).toFixed(2) }}%
              </td>
              <td class="font-mono text-right">${{ formatNum(coin.market_cap) }}</td>
              <td class="font-mono text-right">${{ formatNum(coin.total_volume) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Coin Detail Chart -->
    <div v-if="selectedCoin" class="glass-panel mt-4">
      <h3 class="block-title">{{ selectedCoin }} — История цены (30d)</h3>
      <div class="chart-container">
        <canvas ref="chartRef"></canvas>
      </div>
    </div>

    <!-- Trending -->
    <div v-if="trending" class="glass-panel mt-4">
      <h3 class="block-title">Trending</h3>
      <div class="trending-grid">
        <div v-for="item in trendingCoins" :key="item.id" class="trending-card" @click="selectedCoin = item.id">
          <img :src="item.thumb" class="trending-img" />
          <div>
            <span class="font-mono">{{ item.name }}</span>
            <span class="coin-symbol font-mono">{{ item.symbol }}</span>
          </div>
          <span class="font-mono text-muted">#{{ item.market_cap_rank }}</span>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import {
  getCoinGeckoMarkets, getGlobalStats, getTrendingCoins, getCoinChart,
  type CoinMarket, type GlobalStats, type MarketChart
} from '@/services/cryptoDataService'

Chart.register(...registerables)

const loading = ref(false)
const error = ref('')
const currency = ref('usd')
const markets = ref<CoinMarket[]>([])
const globalStats = ref<GlobalStats | null>(null)
const trending = ref<Record<string, unknown> | null>(null)
const selectedCoin = ref('')
const chartRef = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

const trendingCoins = computed(() => {
  if (!trending.value) return []
  const coins = (trending.value as any)?.coins || []
  return coins.map((c: any) => c.item).slice(0, 10)
})

function formatNum(n: number): string {
  if (n >= 1e12) return (n / 1e12).toFixed(2) + 'T'
  if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B'
  if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M'
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K'
  return n.toFixed(2)
}

async function loadMarkets() {
  try {
    markets.value = await getCoinGeckoMarkets(currency.value, 50)
  } catch (e: any) {
    error.value = e.message
  }
}

async function loadGlobal() {
  try {
    globalStats.value = await getGlobalStats()
  } catch (e: any) {
    error.value = e.message
  }
}

async function loadTrending() {
  try {
    trending.value = await getTrendingCoins()
  } catch (e: any) {
    error.value = e.message
  }
}

async function loadCoinChart() {
  if (!selectedCoin.value) return
  try {
    const data = await getCoinChart(selectedCoin.value, currency.value, 30)
    await nextTick()
    renderChart(data)
  } catch (e: any) {
    error.value = e.message
  }
}

function renderChart(data: MarketChart) {
  if (!chartRef.value) return
  if (chart) chart.destroy()
  const prices = data.prices || []
  chart = new Chart(chartRef.value, {
    type: 'line',
    data: {
      labels: prices.map(p => new Date(p[0]).toLocaleDateString()),
      datasets: [{
        label: `${selectedCoin.value} (${currency.value.toUpperCase()})`,
        data: prices.map(p => p[1]),
        borderColor: '#DC2626',
        backgroundColor: 'rgba(220,38,38,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#aaa' } } },
      scales: {
        x: { ticks: { color: '#666', maxTicksLimit: 10 }, grid: { color: '#1a1a1a' } },
        y: { ticks: { color: '#666' }, grid: { color: '#1a1a1a' } },
      },
    },
  })
}

watch(selectedCoin, () => { if (selectedCoin.value) loadCoinChart() })

async function refreshAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([loadMarkets(), loadGlobal(), loadTrending()])
  } finally {
    loading.value = false
  }
}

onMounted(() => refreshAll())
</script>

<style scoped>
.page-container { padding: 24px 32px; max-width: 1400px; }
.section-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.section-title { font-family: 'Oswald', sans-serif; font-size: 28px; font-weight: 700; text-transform: uppercase; color: #f5f5f5; letter-spacing: 2px; }
.section-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #666; margin-top: 4px; }
.header-actions { display: flex; gap: 8px; align-items: center; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.stat-card { background: rgba(255,255,255,0.02); border: 1px solid #1a1a1a; padding: 16px; display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 11px; color: #666; text-transform: uppercase; }
.stat-value { font-size: 18px; color: #f5f5f5; font-weight: 600; }

.glass-panel { background: rgba(255,255,255,0.02); border: 1px solid #1a1a1a; padding: 20px; }
.block-title { font-family: 'Oswald', sans-serif; font-size: 14px; font-weight: 600; text-transform: uppercase; color: #f5f5f5; letter-spacing: 1px; margin-bottom: 16px; }

.table-wrap { max-height: 600px; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 8px; color: #666; font-family: 'JetBrains Mono', monospace; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid #1a1a1a; position: sticky; top: 0; background: #0a0a0a; }
.data-table td { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.03); color: #ccc; }
.data-table tr.clickable { cursor: pointer; }
.data-table tr.clickable:hover td { background: rgba(255,255,255,0.03); }
.text-right { text-align: right; }
.text-green { color: #22c55e; }
.text-red { color: #DC2626; }
.text-muted { color: #555; }

.coin-cell { display: flex; align-items: center; gap: 8px; }
.coin-img { width: 24px; height: 24px; border-radius: 50%; }
.coin-name { color: #f5f5f5; }
.coin-symbol { color: #666; font-size: 11px; text-transform: uppercase; }

.chart-container { height: 300px; position: relative; }
.chart-container canvas { width: 100% !important; height: 100% !important; }

.trending-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.trending-card { display: flex; align-items: center; gap: 10px; padding: 12px; background: rgba(255,255,255,0.02); border: 1px solid #1a1a1a; cursor: pointer; transition: border-color 0.2s; }
.trending-card:hover { border-color: #DC2626; }
.trending-img { width: 28px; height: 28px; border-radius: 50%; }

.glass-select { background: rgba(255,255,255,0.03); border: 1px solid #333; padding: 8px 12px; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
.btn-glass { padding: 8px 16px; background: rgba(255,255,255,0.03); border: 1px solid #333; color: #f5f5f5; font-family: 'JetBrains Mono', monospace; font-size: 12px; cursor: pointer; text-transform: uppercase; }
.btn-glass:hover { border-color: #DC2626; color: #DC2626; }
.btn-glass:disabled { opacity: 0.5; cursor: not-allowed; }
.error-banner { background: rgba(220,38,38,0.1); border: 1px solid #DC2626; padding: 12px; margin-top: 16px; color: #DC2626; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
.font-mono { font-family: 'JetBrains Mono', monospace; }
.mt-4 { margin-top: 16px; }
</style>
