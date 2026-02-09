<template>
  <div class="page-container custom-scrollbar">
    <!-- Header -->
    <div class="section-header flex-col md:flex-row gap-4">
      <div class="flex items-center gap-4">
        <div class="icon-box icon-blue">
          <FilterIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="section-title font-anton">СКРИНИНГ РЫНКА</h2>
          <p class="section-subtitle font-mono">ОБНАРУЖЕНИЕ, АНАЛИЗ И ОТСЛЕЖИВАНИЕ ВОЗМОЖНОСТЕЙ</p>
        </div>
      </div>

      <div class="tab-group">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="section = tab.id"
          :class="['tab-btn', { active: section === tab.id }]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 flex flex-col gap-6">
      <!-- Equity Screener -->
      <div v-if="section === 'EQS'" class="flex flex-col h-full gap-6">
        <!-- Filters -->
        <div class="p-4 rounded-2xl bg-white/5 border border-white/5 flex flex-wrap gap-4 items-center">
          <div class="flex items-center gap-2 px-3 py-2 bg-black/20 rounded-xl border border-white/10">
            <SlidersIcon class="w-3.5 h-3.5 text-gray-400" />
            <span class="text-xs font-bold text-white">Фильтры:</span>
          </div>
          
          <!-- Сектор Dropdown -->
          <div class="relative" data-dropdown-sector>
            <button
              @click="isSectorOpen = !isSectorOpen"
              class="px-4 py-2 bg-black/20 text-xs text-white border border-white/10 rounded-lg hover:border-blue-500/50 transition-all flex items-center justify-between gap-3 min-w-[180px]"
            >
              <span>{{ selectedSector === 'All' ? 'Все сектора' : getSectorName(selectedSector) }}</span>
              <ChevronDownIcon :class="`w-3.5 h-3.5 transition-transform ${isSectorOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isSectorOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectSector('All')"
                :class="`w-full px-4 py-3 text-left text-xs transition-colors ${
                  selectedSector === 'All' 
                    ? 'bg-blue-500/20 text-blue-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все сектора
              </button>
              <button
                v-for="sector in availableSectors"
                :key="sector"
                @click="selectSector(sector)"
                :class="`w-full px-4 py-3 text-left text-xs transition-colors ${
                  selectedSector === sector 
                    ? 'bg-blue-500/20 text-blue-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getSectorName(sector) }}
              </button>
            </div>
          </div>

          <!-- Капитализация Dropdown -->
          <div class="relative" data-dropdown-cap>
            <button
              @click="isCapOpen = !isCapOpen"
              class="px-4 py-2 bg-black/20 text-xs text-white border border-white/10 rounded-lg hover:border-blue-500/50 transition-all flex items-center justify-between gap-3 min-w-[180px]"
            >
              <span>{{ selectedCap === 'All' ? 'Все' : getCapName(selectedCap) }}</span>
              <ChevronDownIcon :class="`w-3.5 h-3.5 transition-transform ${isCapOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isCapOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectCap('All')"
                :class="`w-full px-4 py-3 text-left text-xs transition-colors ${
                  selectedCap === 'All' 
                    ? 'bg-blue-500/20 text-blue-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все
              </button>
              <button
                v-for="cap in capRanges"
                :key="cap"
                @click="selectCap(cap)"
                :class="`w-full px-4 py-3 text-left text-xs transition-colors ${
                  selectedCap === cap 
                    ? 'bg-blue-500/20 text-blue-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getCapName(cap) }}
              </button>
            </div>
          </div>

          <!-- P/E Ratio Dropdown -->
          <div class="relative" data-dropdown-pe>
            <button
              @click="isPEOpen = !isPEOpen"
              class="px-4 py-2 bg-black/20 text-xs text-white border border-white/10 rounded-lg hover:border-blue-500/50 transition-all flex items-center justify-between gap-3 min-w-[180px]"
            >
              <span>{{ selectedPE === 'All' ? 'Все' : getPEName(selectedPE) }}</span>
              <ChevronDownIcon :class="`w-3.5 h-3.5 transition-transform ${isPEOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isPEOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectPE('All')"
                :class="`w-full px-4 py-3 text-left text-xs transition-colors ${
                  selectedPE === 'All' 
                    ? 'bg-blue-500/20 text-blue-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все
              </button>
              <button
                v-for="pe in peRanges"
                :key="pe"
                @click="selectPE(pe)"
                :class="`w-full px-4 py-3 text-left text-xs transition-colors ${
                  selectedPE === pe 
                    ? 'bg-blue-500/20 text-blue-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getPEName(pe) }}
              </button>
            </div>
          </div>

          <div class="ml-auto flex gap-2">
            <button class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition-colors shadow-lg shadow-blue-500/20">
              Запустить скрининг
            </button>
            <button class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-xs font-bold rounded-lg transition-colors">
              Сохранить шаблон
            </button>
          </div>
        </div>

        <!-- Results Table -->
        <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 backdrop-blur-md z-10">
                <th class="p-4 font-bold">Тикер</th>
                <th class="p-4 font-bold">Компания</th>
                <th class="p-4 font-bold text-right">Цена</th>
                <th class="p-4 font-bold text-right">Изменение</th>
                <th class="p-4 font-bold text-right">P/E</th>
                <th class="p-4 font-bold text-right">Капитализация</th>
                <th class="p-4 font-bold text-right">Волатильность (30д)</th>
                <th class="p-4 font-bold text-right">Сектор</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr 
                v-for="(row, i) in screeningData" 
                :key="i"
                class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer"
              >
                <td class="p-4 font-bold text-white group-hover:text-blue-400">{{ row.s }}</td>
                <td class="p-4 text-xs font-sans text-gray-400">{{ row.n }}</td>
                <td class="p-4 text-right">${{ row.p.toFixed(2) }}</td>
                <td :class="`p-4 text-right font-bold ${row.c.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`">{{ row.c }}</td>
                <td class="p-4 text-right text-gray-400">{{ row.pe }}</td>
                <td class="p-4 text-right">{{ row.mc }}</td>
                <td class="p-4 text-right text-xs">
                  <span :class="`px-2 py-0.5 rounded ${row.v === 'High' ? 'bg-indigo-500/20 text-indigo-300' : row.v === 'Med' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-gray-700/30 text-gray-400'}`">
                    {{ row.v === 'High' ? 'Высокая' : row.v === 'Med' ? 'Средняя' : 'Низкая' }}
                  </span>
                </td>
                <td class="p-4 text-right text-xs text-gray-500">{{ getSectorName(row.sec) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Watchlist Analytics -->
      <div v-else-if="section === 'WLT'" class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full">
        <div class="lg:col-span-1 flex flex-col gap-4">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 flex-1">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-bold text-white">Портфель A</h3>
              <button class="p-1.5 rounded-lg bg-blue-500 hover:bg-blue-600 text-white transition-colors">
                <PlusIcon class="w-4 h-4" />
              </button>
            </div>
            <div class="space-y-2">
              <div 
                v-for="asset in watchlistAssets" 
                :key="asset"
                class="flex justify-between items-center p-3 rounded-xl bg-black/20 hover:bg-white/5 group border border-transparent hover:border-white/10 cursor-pointer"
              >
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center text-xs font-bold text-gray-300">
                    {{ asset }}
                  </div>
                  <div class="flex flex-col">
                    <span class="text-sm font-bold text-white">{{ asset }}</span>
                    <span class="text-[10px] text-gray-500">25% Вес</span>
                  </div>
                </div>
                <button class="text-gray-600 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  <TrashIcon class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2 flex flex-col gap-6">
          <div class="grid grid-cols-3 gap-4">
            <div class="p-4 rounded-xl bg-emerald-900/10 border border-emerald-500/20 text-center">
              <div class="text-xs text-emerald-500/70 font-bold uppercase mb-1">Общая доходность (YTD)</div>
              <div class="text-2xl font-bold text-emerald-400">+24.5%</div>
            </div>
            <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
              <div class="text-xs text-gray-500 font-bold uppercase mb-1">Бета</div>
              <div class="text-2xl font-bold text-white">1.25</div>
            </div>
            <div class="p-4 rounded-xl bg-white/5 border border-white/5 text-center">
              <div class="text-xs text-gray-500 font-bold uppercase mb-1">Коэффициент Шарпа</div>
              <div class="text-2xl font-bold text-white">1.8</div>
            </div>
          </div>

          <div class="flex-1 p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-sm font-bold text-gray-400 uppercase mb-6">Корреляционная матрица</h3>
            <div class="grid grid-cols-5 gap-1">
              <div class="h-10"></div>
              <div v-for="a in watchlistAssets" :key="a" class="h-10 flex items-center justify-center font-bold text-xs text-gray-400">{{ a }}</div>
              
              <template v-for="(row, rowIndex) in correlationMatrix" :key="rowIndex">
                <div class="h-12 flex items-center justify-center font-bold text-xs text-gray-400">{{ watchlistAssets[rowIndex] }}</div>
                <div 
                  v-for="(val, colIndex) in row" 
                  :key="`${rowIndex}-${colIndex}`"
                  class="h-12 flex items-center justify-center rounded-lg text-xs font-bold transition-all hover:scale-105 cursor-default"
                  :style="{
                    backgroundColor: val > 0 
                      ? `rgba(16, 185, 129, ${val})` 
                      : `rgba(244, 63, 94, ${Math.abs(val)})`,
                    color: Math.abs(val) > 0.5 ? 'white' : 'rgba(255,255,255,0.7)'
                  }"
                >
                  {{ val.toFixed(2) }}
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- M&A Tracking -->
      <div v-else-if="section === 'MA'" class="flex flex-col h-full">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div class="p-6 rounded-2xl bg-gradient-to-br from-indigo-600/20 to-indigo-900/20 border border-indigo-500/20">
            <h3 class="text-indigo-300 font-bold text-sm uppercase mb-1">Объём активных сделок</h3>
            <div class="text-3xl font-bold text-white">$142B</div>
            <div class="text-xs text-gray-400 mt-1">Q4 2025 (В процессе)</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-gray-400 font-bold text-sm uppercase mb-1">Средний арбитражный спред</h3>
            <div class="text-3xl font-bold text-white">3.2%</div>
            <div class="text-xs text-gray-400 mt-1">Годовая доходность</div>
          </div>
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5">
            <h3 class="text-gray-400 font-bold text-sm uppercase mb-1">Регуляторный риск</h3>
            <div class="text-3xl font-bold text-rose-400">Высокий</div>
            <div class="text-xs text-gray-400 mt-1">Проверка FTC</div>
          </div>
        </div>

        <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
          <table class="w-full text-left">
            <thead>
              <tr class="text-xs text-gray-400 uppercase bg-white/5">
                <th class="p-4">Дата</th>
                <th class="p-4">Покупатель</th>
                <th class="p-4">Цель</th>
                <th class="p-4">Стоимость сделки</th>
                <th class="p-4">Премия</th>
                <th class="p-4">Арб. спред</th>
                <th class="p-4 text-right">Статус</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(deal, i) in deals" :key="i" class="border-b border-white/5 hover:bg-white/5">
                <td class="p-4 text-gray-500 text-xs">{{ deal.date }}</td>
                <td class="p-4 font-bold text-white">{{ deal.acquirer }}</td>
                <td class="p-4 text-blue-300">{{ deal.target }}</td>
                <td class="p-4">{{ deal.val }}</td>
                <td class="p-4 text-emerald-400">{{ deal.prem }}</td>
                <td class="p-4 text-yellow-400 font-bold">{{ deal.spread }}</td>
                <td class="p-4 text-right">
                  <span :class="`px-2 py-1 rounded-lg text-xs font-bold border ${getStatusStyle(deal.status)}`">
                    {{ getStatusName(deal.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Default placeholder -->
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <h3 class="text-xl font-bold text-white mb-2">{{ getSectionName(section) }}</h3>
          <p class="text-gray-400">Содержимое появится в ближайшее время</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue';

interface Props {
  symbol: string;
  activeSection: string;
}

const props = defineProps<Props>();

const section = ref(props.activeSection);
const selectedSector = ref('All');
const selectedCap = ref('All');
const selectedPE = ref('All');
const isSectorOpen = ref(false);
const isCapOpen = ref(false);
const isPEOpen = ref(false);

watch(() => props.activeSection, (val) => {
  section.value = val;
});

const tabs = [
  { id: 'EQS', label: 'Скринер акций', icon: 'FilterIcon' },
  { id: 'WLT', label: 'Аналитика списка наблюдения', icon: 'ListIcon' },
  { id: 'EQRV', label: 'Относительная оценка', icon: 'PieChartIcon' },
  { id: 'MA', label: 'Отслеживание M&A', icon: 'GitMergeIcon' },
];

const availableSectors = computed(() => {
  const sectors = new Set(screeningData.map(d => d.sec));
  return Array.from(sectors).sort();
});

const capRanges = ['Mega', 'Large', 'Mid', 'Small', 'Micro'];
const peRanges = ['Under15', 'Under25', 'Under50', 'All'];

const selectSector = (sector: string) => {
  selectedSector.value = sector;
  isSectorOpen.value = false;
};

const selectCap = (cap: string) => {
  selectedCap.value = cap;
  isCapOpen.value = false;
};

const selectPE = (pe: string) => {
  selectedPE.value = pe;
  isPEOpen.value = false;
};

const getSectorName = (sector: string) => {
  const names: Record<string, string> = {
    'Technology': 'Технологии',
    'Tech': 'Технологии',
    'Healthcare': 'Здравоохранение',
    'Finance': 'Финансы',
    'Energy': 'Энергетика',
    'Consumer': 'Потребительские товары',
    'Industrial': 'Промышленность',
    'Telecommunications': 'Телекоммуникации',
    'Materials': 'Материалы',
    'Oil & Gas': 'Нефть и газ',
    'Banking': 'Банковский сектор',
    'Retail': 'Розничная торговля',
    'Automotive': 'Автомобильная промышленность',
    'Real Estate': 'Недвижимость',
    'Utilities': 'Коммунальные услуги',
  };
  return names[sector] || sector;
};

const getCapName = (cap: string) => {
  const names: Record<string, string> = {
    'Mega': 'Мега (>100B)',
    'Large': 'Крупные (10B-100B)',
    'Mid': 'Средние (1B-10B)',
    'Small': 'Малые (100M-1B)',
    'Micro': 'Микро (<100M)',
  };
  return names[cap] || cap;
};

const getPEName = (pe: string) => {
  const names: Record<string, string> = {
    'Under15': 'P/E < 15',
    'Under25': 'P/E < 25',
    'Under50': 'P/E < 50',
    'All': 'Все',
  };
  return names[pe] || pe;
};

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    'Completed': 'Завершено',
    'Closing': 'Закрытие',
    'Pending': 'Ожидание',
    'Regulator Review': 'Проверка регулятора',
  };
  return names[status] || status;
};

const getSectionName = (sectionId: string) => {
  const section = tabs.find(t => t.id === sectionId);
  return section ? section.label : sectionId;
};

// Закрытие выпадающих меню при клике вне их
let clickOutsideHandler: ((e: MouseEvent) => void) | null = null;

onMounted(() => {
  clickOutsideHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-dropdown-sector]') && !target.closest('[data-dropdown-cap]') && !target.closest('[data-dropdown-pe]')) {
      isSectorOpen.value = false;
      isCapOpen.value = false;
      isPEOpen.value = false;
    }
  };
  document.addEventListener('click', clickOutsideHandler);
});

onBeforeUnmount(() => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler);
  }
});

const screeningData = [
  // Technology
  { s: 'NVDA', n: 'NVIDIA Corp', p: 892.10, c: '+4.2%', pe: 75.2, mc: '2.2T', v: 'High', sec: 'Technology' },
  { s: 'AMD', n: 'Advanced Micro', p: 178.20, c: '+2.1%', pe: 42.1, mc: '280B', v: 'High', sec: 'Technology' },
  { s: 'TSM', n: 'Taiwan Semi', p: 142.50, c: '-0.5%', pe: 24.5, mc: '750B', v: 'Med', sec: 'Technology' },
  { s: 'AVGO', n: 'Broadcom Inc', p: 1350.00, c: '+1.8%', pe: 35.8, mc: '620B', v: 'Med', sec: 'Technology' },
  { s: 'INTC', n: 'Intel Corp', p: 42.10, c: '-1.2%', pe: 85.2, mc: '180B', v: 'Med', sec: 'Technology' },
  { s: 'QCOM', n: 'Qualcomm', p: 168.40, c: '+0.9%', pe: 18.2, mc: '190B', v: 'Low', sec: 'Technology' },
  { s: 'MU', n: 'Micron Tech', p: 124.30, c: '+3.5%', pe: -12.4, mc: '135B', v: 'High', sec: 'Technology' },
  { s: 'AAPL', n: 'Apple Inc', p: 173.50, c: '+1.2%', pe: 28.5, mc: '2.7T', v: 'Med', sec: 'Technology' },
  { s: 'MSFT', n: 'Microsoft', p: 420.55, c: '-0.45%', pe: 32.8, mc: '3.1T', v: 'Med', sec: 'Technology' },
  { s: 'GOOGL', n: 'Alphabet', p: 156.40, c: '-0.20%', pe: 24.2, mc: '1.9T', v: 'Med', sec: 'Technology' },
  { s: 'META', n: 'Meta Platforms', p: 495.10, c: '+1.85%', pe: 22.5, mc: '1.2T', v: 'High', sec: 'Technology' },
  { s: 'AMZN', n: 'Amazon', p: 180.25, c: '+0.95%', pe: 48.3, mc: '1.8T', v: 'Med', sec: 'Technology' },
  { s: 'ORCL', n: 'Oracle', p: 118.25, c: '+0.75%', pe: 19.8, mc: '320B', v: 'Low', sec: 'Technology' },
  { s: 'ADBE', n: 'Adobe', p: 545.80, c: '+1.85%', pe: 45.2, mc: '248B', v: 'Med', sec: 'Technology' },
  { s: 'CRM', n: 'Salesforce', p: 285.40, c: '+1.25%', pe: 52.1, mc: '280B', v: 'Med', sec: 'Technology' },
  { s: 'NOW', n: 'ServiceNow', p: 785.20, c: '+2.15%', pe: 68.5, mc: '155B', v: 'High', sec: 'Technology' },
  { s: 'ASML', n: 'ASML Holding', p: 945.60, c: '+2.85%', pe: 38.2, mc: '375B', v: 'High', sec: 'Technology' },
  
  // Healthcare
  { s: 'JNJ', n: 'Johnson & Johnson', p: 158.40, c: '+0.30%', pe: 22.8, mc: '420B', v: 'Low', sec: 'Healthcare' },
  { s: 'UNH', n: 'UnitedHealth', p: 525.40, c: '+1.20%', pe: 26.5, mc: '495B', v: 'Med', sec: 'Healthcare' },
  { s: 'LLY', n: 'Eli Lilly', p: 765.20, c: '+2.45%', pe: 58.2, mc: '728B', v: 'High', sec: 'Healthcare' },
  { s: 'ABBV', n: 'AbbVie', p: 168.90, c: '+0.40%', pe: 14.2, mc: '298B', v: 'Low', sec: 'Healthcare' },
  { s: 'MRK', n: 'Merck', p: 128.60, c: '+0.55%', pe: 18.5, mc: '326B', v: 'Low', sec: 'Healthcare' },
  { s: 'PFE', n: 'Pfizer', p: 27.80, c: '-0.50%', pe: 12.8, mc: '158B', v: 'Low', sec: 'Healthcare' },
  { s: 'TMO', n: 'Thermo Fisher', p: 585.40, c: '+1.15%', pe: 32.5, mc: '225B', v: 'Med', sec: 'Healthcare' },
  { s: 'ABT', n: 'Abbott Labs', p: 112.50, c: '+0.65%', pe: 28.2, mc: '195B', v: 'Low', sec: 'Healthcare' },
  { s: 'DHR', n: 'Danaher', p: 265.80, c: '+0.85%', pe: 35.8, mc: '195B', v: 'Med', sec: 'Healthcare' },
  { s: 'BMY', n: 'Bristol-Myers', p: 52.40, c: '+0.25%', pe: 12.5, mc: '108B', v: 'Low', sec: 'Healthcare' },
  { s: 'AMGN', n: 'Amgen', p: 285.60, c: '+0.95%', pe: 19.2, mc: '152B', v: 'Low', sec: 'Healthcare' },
  { s: 'GILD', n: 'Gilead Sciences', p: 78.20, c: '+0.35%', pe: 15.8, mc: '98B', v: 'Low', sec: 'Healthcare' },
  { s: 'REGN', n: 'Regeneron', p: 985.40, c: '+1.85%', pe: 24.5, mc: '108B', v: 'High', sec: 'Healthcare' },
  { s: 'VRTX', n: 'Vertex Pharma', p: 425.80, c: '+2.15%', pe: 28.5, mc: '110B', v: 'High', sec: 'Healthcare' },
  
  // Finance
  { s: 'JPM', n: 'JPMorgan Chase', p: 185.40, c: '+0.55%', pe: 12.5, mc: '540B', v: 'Med', sec: 'Finance' },
  { s: 'BAC', n: 'Bank of America', p: 38.50, c: '+0.40%', pe: 11.8, mc: '305B', v: 'Med', sec: 'Banking' },
  { s: 'WFC', n: 'Wells Fargo', p: 58.20, c: '+0.30%', pe: 12.2, mc: '215B', v: 'Low', sec: 'Banking' },
  { s: 'GS', n: 'Goldman Sachs', p: 425.80, c: '+0.85%', pe: 15.2, mc: '145B', v: 'Med', sec: 'Finance' },
  { s: 'MS', n: 'Morgan Stanley', p: 95.60, c: '+0.65%', pe: 14.8, mc: '175B', v: 'Med', sec: 'Finance' },
  { s: 'C', n: 'Citigroup', p: 62.40, c: '+0.25%', pe: 8.5, mc: '120B', v: 'Low', sec: 'Banking' },
  { s: 'BLK', n: 'BlackRock', p: 825.40, c: '+1.15%', pe: 22.5, mc: '125B', v: 'Med', sec: 'Finance' },
  { s: 'SCHW', n: 'Charles Schwab', p: 68.20, c: '+0.45%', pe: 18.2, mc: '125B', v: 'Med', sec: 'Finance' },
  { s: 'AXP', n: 'American Express', p: 225.60, c: '+0.75%', pe: 19.5, mc: '165B', v: 'Med', sec: 'Finance' },
  { s: 'COF', n: 'Capital One', p: 145.80, c: '+0.55%', pe: 10.2, mc: '55B', v: 'Med', sec: 'Banking' },
  
  // Energy / Oil & Gas
  { s: 'XOM', n: 'Exxon Mobil', p: 118.50, c: '+0.85%', pe: 13.2, mc: '495B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'CVX', n: 'Chevron', p: 162.40, c: '+0.75%', pe: 14.5, mc: '305B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'COP', n: 'ConocoPhillips', p: 115.80, c: '+1.05%', pe: 12.8, mc: '138B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'SLB', n: 'Schlumberger', p: 52.40, c: '+1.25%', pe: 18.5, mc: '75B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'EOG', n: 'EOG Resources', p: 128.60, c: '+1.45%', pe: 11.2, mc: '75B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'MPC', n: 'Marathon Petroleum', p: 185.40, c: '+0.95%', pe: 8.5, mc: '65B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'VLO', n: 'Valero Energy', p: 145.20, c: '+0.65%', pe: 7.8, mc: '58B', v: 'Med', sec: 'Oil & Gas' },
  { s: 'PSX', n: 'Phillips 66', p: 152.80, c: '+0.85%', pe: 9.2, mc: '68B', v: 'Med', sec: 'Oil & Gas' },
  
  // Consumer
  { s: 'WMT', n: 'Walmart', p: 165.30, c: '+0.45%', pe: 26.5, mc: '445B', v: 'Low', sec: 'Consumer' },
  { s: 'PG', n: 'Procter & Gamble', p: 168.90, c: '+0.35%', pe: 24.8, mc: '400B', v: 'Low', sec: 'Consumer' },
  { s: 'KO', n: 'Coca-Cola', p: 62.80, c: '+0.20%', pe: 25.2, mc: '270B', v: 'Low', sec: 'Consumer' },
  { s: 'PEP', n: 'PepsiCo', p: 172.50, c: '+0.40%', pe: 28.5, mc: '238B', v: 'Low', sec: 'Consumer' },
  { s: 'NKE', n: 'Nike', p: 98.40, c: '+1.15%', pe: 32.5, mc: '151B', v: 'Med', sec: 'Consumer' },
  { s: 'MCD', n: 'McDonald\'s', p: 295.60, c: '+0.50%', pe: 28.2, mc: '215B', v: 'Low', sec: 'Consumer' },
  { s: 'SBUX', n: 'Starbucks', p: 95.80, c: '+0.85%', pe: 25.8, mc: '110B', v: 'Med', sec: 'Consumer' },
  { s: 'TGT', n: 'Target', p: 145.20, c: '+0.65%', pe: 18.5, mc: '68B', v: 'Med', sec: 'Retail' },
  { s: 'HD', n: 'Home Depot', p: 385.40, c: '+0.75%', pe: 22.5, mc: '395B', v: 'Med', sec: 'Retail' },
  { s: 'LOW', n: 'Lowe\'s', p: 225.60, c: '+0.55%', pe: 19.8, mc: '135B', v: 'Med', sec: 'Retail' },
  { s: 'COST', n: 'Costco', p: 825.40, c: '+1.25%', pe: 42.5, mc: '365B', v: 'Med', sec: 'Retail' },
  { s: 'TJX', n: 'TJX Companies', p: 95.20, c: '+0.45%', pe: 24.2, mc: '108B', v: 'Med', sec: 'Retail' },
  
  // Industrial
  { s: 'BA', n: 'Boeing', p: 185.40, c: '+1.85%', pe: -45.2, mc: '115B', v: 'High', sec: 'Industrial' },
  { s: 'CAT', n: 'Caterpillar', p: 348.60, c: '+1.45%', pe: 15.8, mc: '175B', v: 'Med', sec: 'Industrial' },
  { s: 'GE', n: 'General Electric', p: 148.20, c: '+1.15%', pe: 28.5, mc: '162B', v: 'Med', sec: 'Industrial' },
  { s: 'HON', n: 'Honeywell', p: 225.40, c: '+0.85%', pe: 25.2, mc: '152B', v: 'Med', sec: 'Industrial' },
  { s: 'RTX', n: 'Raytheon', p: 95.60, c: '+0.65%', pe: 18.5, mc: '135B', v: 'Med', sec: 'Industrial' },
  { s: 'LMT', n: 'Lockheed Martin', p: 485.20, c: '+0.95%', pe: 19.2, mc: '125B', v: 'Med', sec: 'Industrial' },
  { s: 'DE', n: 'Deere & Co', p: 425.80, c: '+1.25%', pe: 12.5, mc: '125B', v: 'Med', sec: 'Industrial' },
  { s: 'EMR', n: 'Emerson Electric', p: 105.40, c: '+0.45%', pe: 22.8, mc: '58B', v: 'Low', sec: 'Industrial' },
  
  // Telecommunications
  { s: 'T', n: 'AT&T', p: 17.40, c: '+0.15%', pe: 8.5, mc: '124B', v: 'Low', sec: 'Telecommunications' },
  { s: 'VZ', n: 'Verizon', p: 40.80, c: '+0.10%', pe: 9.2, mc: '172B', v: 'Low', sec: 'Telecommunications' },
  { s: 'TMUS', n: 'T-Mobile', p: 165.40, c: '+0.65%', pe: 22.5, mc: '195B', v: 'Med', sec: 'Telecommunications' },
  { s: 'CMCSA', n: 'Comcast', p: 45.20, c: '+0.35%', pe: 12.8, mc: '185B', v: 'Low', sec: 'Telecommunications' },
  
  // Materials
  { s: 'LIN', n: 'Linde', p: 425.60, c: '+0.75%', pe: 32.5, mc: '205B', v: 'Med', sec: 'Materials' },
  { s: 'APD', n: 'Air Products', p: 285.40, c: '+0.55%', pe: 28.2, mc: '65B', v: 'Med', sec: 'Materials' },
  { s: 'ECL', n: 'Ecolab', p: 225.80, c: '+0.45%', pe: 42.5, mc: '62B', v: 'Med', sec: 'Materials' },
  { s: 'SHW', n: 'Sherwin-Williams', p: 285.60, c: '+0.65%', pe: 28.8, mc: '75B', v: 'Med', sec: 'Materials' },
  { s: 'FCX', n: 'Freeport-McMoRan', p: 42.50, c: '+1.25%', pe: 18.5, mc: '58B', v: 'Med', sec: 'Materials' },
  { s: 'NEM', n: 'Newmont', p: 38.20, c: '+0.85%', pe: 22.2, mc: '48B', v: 'Med', sec: 'Materials' },
  
  // Automotive
  { s: 'TSLA', n: 'Tesla', p: 175.30, c: '+2.10%', pe: 58.5, mc: '550B', v: 'High', sec: 'Automotive' },
  { s: 'F', n: 'Ford', p: 12.50, c: '+0.25%', pe: 8.2, mc: '48B', v: 'Med', sec: 'Automotive' },
  { s: 'GM', n: 'General Motors', p: 38.40, c: '+0.35%', pe: 5.8, mc: '52B', v: 'Med', sec: 'Automotive' },
  { s: 'STLA', n: 'Stellantis', p: 22.60, c: '+0.15%', pe: 3.2, mc: '68B', v: 'Med', sec: 'Automotive' },
];

const watchlistAssets = ['BTC', 'ETH', 'NVDA', 'GOLD'];

const correlationMatrix = [
  [1.0, 0.85, 0.42, -0.1],
  [0.85, 1.0, 0.38, -0.15],
  [0.42, 0.38, 1.0, 0.65],
  [-0.1, -0.15, 0.65, 1.0]
];

const deals = [
  { date: 'Oct 24', acquirer: 'Chevron', target: 'Hess Corp', val: '$53B', prem: '+10.2%', spread: '1.4%', status: 'Pending' },
  { date: 'Oct 12', acquirer: 'Exxon', target: 'Pioneer', val: '$59B', prem: '+18.0%', spread: '0.8%', status: 'Closing' },
  { date: 'Sep 28', acquirer: 'Cisco', target: 'Splunk', val: '$28B', prem: '+31.0%', spread: '2.1%', status: 'Regulator Review' },
  { date: 'Sep 15', acquirer: 'Broadcom', target: 'VMware', val: '$61B', prem: '+44.0%', spread: '0.2%', status: 'Completed' },
];

const getStatusStyle = (status: string) => {
  if (status === 'Completed') return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400';
  if (status === 'Closing') return 'bg-blue-500/10 border-blue-500/20 text-blue-400';
  return 'bg-gray-700/30 border-gray-600/30 text-gray-400';
};

// Icon components
const FilterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>' };
const SlidersIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>' };
const PlusIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>' };
const TrashIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
</script>
