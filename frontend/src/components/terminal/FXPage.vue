<template>
  <div class="page-container custom-scrollbar">
    <!-- Header -->
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-green">
          <ZapIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">ВАЛЮТНЫЙ РЫНОК</h2>
          <p class="section-subtitle font-mono">SPOT RATES, FORWARDS & MACRO FLOWS</p>
        </div>
      </div>

      <div class="tab-group">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="section = tab.id"
          :class="['tab-btn', { active: section === tab.id }]"
        >
          <component :is="tab.icon" class="w-3.5 h-3.5" /> {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <!-- Currency Matrix -->
      <div v-if="section === 'FXC'" class="flex flex-col h-full">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-white">Кросс-валютная матрица</h3>
          <div class="flex gap-2 text-xs">
            <span class="flex items-center gap-1 text-emerald-400"><div class="w-2 h-2 rounded-full bg-emerald-500"></div> Strong</span>
            <span class="flex items-center gap-1 text-rose-400"><div class="w-2 h-2 rounded-full bg-rose-500"></div> Weak</span>
          </div>
        </div>

        <!-- Индикатор загрузки -->
        <div v-if="loadingRates" class="flex items-center justify-center py-4 text-gray-400 mb-4">
          <div class="flex items-center gap-2">
            <div class="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
            <span class="text-xs font-bold">Загрузка курсов валют...</span>
          </div>
        </div>

        <div class="flex-1 overflow-auto bg-black/20 rounded-2xl border border-white/5" :class="{ 'opacity-50': loadingRates }">
          <table class="w-full text-center border-collapse">
            <thead>
              <tr>
                <th class="p-4 bg-white/5 border-b border-white/10 text-xs font-bold text-gray-500 sticky top-0 left-0 z-20">Base / Quote</th>
                <th v-for="c in currencies" :key="c" class="p-4 bg-white/5 border-b border-white/10 text-xs font-bold text-white sticky top-0 z-10">{{ c }}</th>
              </tr>
            </thead>
            <tbody class="text-xs font-mono">
              <tr v-for="base in currencies" :key="base" class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4 font-bold text-white bg-white/5 sticky left-0 border-r border-white/5">{{ base }}</td>
                <td 
                  v-for="quote in currencies" 
                  :key="quote"
                  :class="`p-4 ${base === quote ? 'text-gray-600 bg-black/40' : getRate(base, quote) > 1.0 ? 'text-emerald-400' : 'text-rose-400'}`"
                >
                  {{ base === quote ? '-' : getRate(base, quote).toFixed(4) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Currency Conversion -->
      <div v-else-if="section === 'FXCA'" class="grid grid-cols-1 lg:grid-cols-3 gap-8 h-full">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col gap-6">
          <h3 class="text-lg font-bold text-white">Расчет спот-курса</h3>
          
          <!-- Индикатор загрузки -->
          <div v-if="loadingRates" class="flex items-center justify-center py-4 text-gray-400">
            <div class="flex items-center gap-2">
              <div class="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
              <span class="text-xs font-bold">Загрузка курсов...</span>
            </div>
          </div>
          
          <div class="space-y-4" :class="{ 'opacity-50': loadingRates }">
            <div>
              <label class="text-xs text-gray-500 font-bold uppercase mb-1 block">Количество</label>
              <input 
                type="number" 
                v-model="amount"
                class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white font-mono text-lg outline-none focus:border-green-500/50"
              />
            </div>
            
            <div class="grid grid-cols-[1fr_auto_1fr] gap-2 items-end">
              <div>
                <label class="text-xs text-gray-500 font-bold uppercase mb-1 block">Из</label>
                <select v-model="fromCurrency" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white outline-none">
                  <option v-for="c in ['USD', 'EUR', 'GBP', 'JPY', 'CAD']" :key="c">{{ c }}</option>
                </select>
              </div>
              <button @click="loadCurrencyRates" class="p-3 bg-white/10 rounded-xl hover:bg-white/20 text-white mb-1 transition-colors" :disabled="loadingRates">
                <RefreshCwIcon :class="`w-4 h-4 ${loadingRates ? 'animate-spin' : ''}`" />
              </button>
              <div>
                <label class="text-xs text-gray-500 font-bold uppercase mb-1 block">В</label>
                <select v-model="toCurrency" class="w-full bg-black/40 border border-white/10 rounded-xl py-3 px-4 text-white outline-none">
                  <option v-for="c in ['EUR', 'USD', 'GBP', 'JPY', 'CAD']" :key="c">{{ c }}</option>
                </select>
              </div>
            </div>
          </div>

          <div class="mt-auto p-4 rounded-xl bg-black/30 border border-white/10 text-center">
            <div class="text-xs text-gray-500 uppercase mb-1">Результат</div>
            <div class="text-3xl font-bold text-green-400 font-mono">
              {{ (amount * conversionRate).toFixed(2) }} <span class="text-sm text-gray-400">{{ toCurrency }}</span>
            </div>
            <div class="text-xs text-gray-500 mt-2">Курс: 1 {{ fromCurrency }} = {{ conversionRate.toFixed(4) }} {{ toCurrency }}</div>
          </div>
        </div>

        <div class="lg:col-span-2 p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-white">Исторический курс валютной пары ({{ fromCurrency }}/{{ toCurrency }})</h3>
            <div class="flex gap-2">
              <button v-for="p in ['1W', '1M', '3M', '1Y']" :key="p" class="px-3 py-1 text-xs font-bold rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-colors">
                {{ p }}
              </button>
            </div>
          </div>
          <div class="flex-1 min-h-[300px]">
            <v-chart class="w-full h-full" :option="fxChartOption" autoresize />
          </div>
        </div>
      </div>

      <!-- FX Forecasts -->
      <div v-else-if="section === 'FXFC'" class="flex flex-col h-full gap-6">
        <div class="grid grid-cols-3 gap-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Прогноз индекса DXY (Годовой)</h3>
            <div class="text-3xl font-bold text-white">102.50</div>
            <div class="text-xs text-rose-400 mt-1">Bearish vs Current (104.20)</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Наиболее количество сделок (Q4)</h3>
            <div class="text-3xl font-bold text-emerald-400">Short USD/JPY</div>
            <div class="text-xs text-gray-500 mt-1">Carry Unwind Theme</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Обзор волатильности рынка</h3>
            <div class="text-3xl font-bold text-white">Повышающаяся</div>
            <div class="text-xs text-gray-500 mt-1">Election Risk Premium</div>
          </div>
        </div>

        <div class="flex-1 bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
          <div class="p-4 border-b border-white/10 bg-white/5">
            <h3 class="font-bold text-white">Консенсус-прогнозы по валютным парам (Медиана)</h3>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-500 uppercase">
                <th class="p-4">Валютная пара</th>
                <th class="p-4 text-right">Спот-курс</th>
                <th class="p-4 text-right">Q1 26</th>
                <th class="p-4 text-right">Q2 26</th>
                <th class="p-4 text-right">Q3 26</th>
                <th class="p-4 text-right">Q4 26</th>
                <th class="p-4 text-right">Консенсус</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(f, i) in forecasts" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4 font-bold text-white">{{ f.pair }}</td>
                <td class="p-4 text-right">{{ f.spot.toFixed(4) }}</td>
                <td class="p-4 text-right text-gray-400">{{ f.q1.toFixed(2) }}</td>
                <td class="p-4 text-right text-gray-400">{{ f.q2.toFixed(2) }}</td>
                <td class="p-4 text-right text-gray-400">{{ f.q3.toFixed(2) }}</td>
                <td class="p-4 text-right text-gray-400">{{ f.q4.toFixed(2) }}</td>
                <td class="p-4 text-right">
                  <span :class="`px-2 py-1 rounded text-xs font-bold border ${f.consensus === 'Рост' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'}`">
                    {{ f.consensus }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Global Markets Monitor -->
      <div v-else-if="section === 'GMM'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 h-full">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">G10 Currencies</h3>
          <div class="space-y-4 flex-1">
            <div v-for="row in g10Currencies" :key="row.p" class="flex justify-between items-center p-3 rounded-xl bg-black/20">
              <span class="font-bold text-white">{{ row.p }}</span>
              <div class="text-right">
                <div class="text-white font-mono">{{ row.r.toFixed(4) }}</div>
                <div :class="`text-xs ${row.c > 0 ? 'text-emerald-400' : 'text-rose-400'}`">
                  {{ row.c > 0 ? '+' : '' }}{{ row.c }}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Emerging Markets</h3>
          <div class="space-y-4 flex-1">
            <div v-for="row in emCurrencies" :key="row.p" class="flex justify-between items-center p-3 rounded-xl bg-black/20">
              <span class="font-bold text-white">{{ row.p }}</span>
              <div class="text-right">
                <div class="text-white font-mono">{{ row.r.toFixed(4) }}</div>
                <div :class="`text-xs ${row.c > 0 ? 'text-emerald-400' : 'text-rose-400'}`">
                  {{ row.c > 0 ? '+' : '' }}{{ row.c }}%
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex flex-col">
          <h3 class="text-sm font-bold text-gray-400 uppercase mb-4">Макроиндикаторы</h3>
          <div class="space-y-4 flex-1">
            <div v-for="(row, i) in macroIndicators" :key="i" class="flex justify-between items-center p-3 rounded-xl bg-black/20">
              <span class="text-sm text-gray-300">{{ row.name }}</span>
              <span class="font-bold text-white">{{ row.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Default -->
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <h3 class="text-xl font-bold text-white mb-2">{{ section }} View</h3>
          <p class="text-gray-400">Content coming soon</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { getCurrencyRate, type CurrencyRate } from '@/services/marketDataService';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, GridComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, GridComponent]);

interface Props {
  symbol: string;
  activeSection: string;
}

const props = defineProps<Props>();

const section = ref(props.activeSection);

watch(() => props.activeSection, (val) => { section.value = val; });

const tabs = [
  { id: 'FXC', label: 'Кросс-валютная матрица'},
  { id: 'FXCA', label: 'Расчет спот-курса'},
  { id: 'FXFC', label: 'Прогнозы'},
  { id: 'WIRA', label: 'Международные резервы'},
  { id: 'WCRS', label: 'Рейтинги'},
  { id: 'GMM', label: 'Монитор'},
];

const currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CAD', 'AUD'];

// Хранилище реальных курсов валют (относительно USD)
const bases = ref<Record<string, number>>({ 
  'USD': 1, 'EUR': 1.08, 'GBP': 1.26, 'AUD': 0.65, 'CAD': 0.73, 'CHF': 1.10, 'JPY': 0.0066 
});

const loadingRates = ref(false);

// Загрузка реальных курсов валют
const loadCurrencyRates = async () => {
  loadingRates.value = true;
  try {
    console.log('Loading currency rates...');
    // Загружаем курсы относительно USD
    const ratePromises = currencies
      .filter(c => c !== 'USD')
      .map(async (currency) => {
        try {
          // yfinance использует формат BASE-QUOTE=X, для USD/JPY это JPY=X
          const rateData = await getCurrencyRate(currency, 'USD');
          // Если курс возвращается как currency/USD, конвертируем в USD/currency
          bases.value[currency] = 1 / rateData.rate;
          console.log(`Loaded ${currency}/USD:`, rateData.rate);
        } catch (error: any) {
          console.error(`Error loading rate for ${currency}:`, error.message);
        }
      });
    
    await Promise.all(ratePromises);
    console.log('Currency rates loaded successfully');
  } catch (error: any) {
    console.error('Error loading currency rates:', error);
    console.error('Error details:', error.message, error.stack);
  } finally {
    loadingRates.value = false;
  }
};

const getRate = (r1: string, r2: string) => {
  if (r1 === r2) return 1.0;
  return bases.value[r1] / bases.value[r2];
};

const amount = ref(1000);
const fromCurrency = ref('USD');
const toCurrency = ref('EUR');

const conversionRate = computed(() => {
  return getRate(fromCurrency.value, toCurrency.value);
});

const fxChartData = computed(() => {
  return Array.from({ length: 30 }, (_, i) => ({
    day: i,
    rate: conversionRate.value + Math.sin(i / 5) * 0.02 + (Math.random() - 0.5) * 0.01
  }));
});

// Переменная для интервала обновления
let currencyUpdateInterval: ReturnType<typeof setInterval> | null = null;

// Загружаем курсы при монтировании
onMounted(async () => {
  await loadCurrencyRates();
  // Обновляем курсы каждые 60 секунд
  currencyUpdateInterval = setInterval(loadCurrencyRates, 60000);
});

onBeforeUnmount(() => {
  if (currencyUpdateInterval) {
    clearInterval(currencyUpdateInterval);
  }
});

const fxChartOption = computed(() => ({
  grid: { left: 40, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: fxChartData.value.map(d => d.day), show: false },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#9ca3af', fontSize: 10, formatter: (v: number) => v.toFixed(3) },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }
  },
  series: [{
    type: 'line',
    data: fxChartData.value.map(d => d.rate),
    smooth: true,
    symbol: 'none',
    lineStyle: { color: '#10b981', width: 3 },
    areaStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16,185,129,0.3)' }, { offset: 1, color: 'rgba(16,185,129,0)' }] }
    }
  }],
  tooltip: { backgroundColor: '#18181b', borderColor: '#27272a', textStyle: { color: '#fff' } }
}));

const forecasts = [
  { pair: 'EUR/USD', spot: 1.0850, q1: 1.09, q2: 1.10, q3: 1.12, q4: 1.14, consensus: 'Рост' },
  { pair: 'USD/JPY', spot: 151.20, q1: 150.00, q2: 148.00, q3: 145.00, q4: 142.00, consensus: 'Спад' },
  { pair: 'GBP/USD', spot: 1.2640, q1: 1.27, q2: 1.28, q3: 1.29, q4: 1.30, consensus: 'Рост' },
  { pair: 'AUD/USD', spot: 0.6550, q1: 0.66, q2: 0.67, q3: 0.68, q4: 0.70, consensus: 'Рост' },
  { pair: 'USD/CAD', spot: 1.3580, q1: 1.35, q2: 1.34, q3: 1.33, q4: 1.32, consensus: 'Рост' },
];

const g10Currencies = [
  { p: 'EUR/USD', r: 1.0850, c: -0.15 },
  { p: 'USD/JPY', r: 151.20, c: 0.32 },
  { p: 'GBP/USD', r: 1.2640, c: 0.05 },
  { p: 'USD/CHF', r: 0.9020, c: -0.10 },
];

const emCurrencies = [
  { p: 'USD/CNH', r: 7.2450, c: 0.05 },
  { p: 'USD/MXN', r: 16.5020, c: -0.25 },
  { p: 'USD/BRL', r: 5.0510, c: 0.12 },
  { p: 'USD/ZAR', r: 18.8500, c: 0.45 },
];

const macroIndicators = [
  { name: 'US 10Y Yield', value: '4.25%' },
  { name: 'DXY Index', value: '104.20' },
  { name: 'Gold (XAU)', value: '$2,685' },
  { name: 'Brent Oil', value: '$74.50' },
];

// Icon components
const ZapIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>' };
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const ArrowLeftRightIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="7 16 3 12 7 8"/><line x1="21" y1="12" x2="3" y2="12"/><polyline points="17 8 21 12 17 16"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const DollarSignIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>' };
const BarChart2Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' };
const GlobeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>' };
const RefreshCwIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>' };
</script>
