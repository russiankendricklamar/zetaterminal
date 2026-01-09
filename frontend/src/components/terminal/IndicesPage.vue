<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-600/20 to-blue-600/20 flex items-center justify-center text-lg font-bold text-sky-400 border border-sky-500/30">
          <GlobeIcon class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Индексы</h2>
          <p class="text-xs text-gray-400">Мировые рынки, сектора и состав</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto max-w-full custom-scrollbar">
        <button v-for="tab in tabs" :key="tab.id" @click="section = tab.id" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 whitespace-nowrap', section === tab.id ? 'bg-sky-500/20 text-sky-300 border border-sky-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          {{ tab.label }}
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <WorldIndices v-if="section === 'WINDEX'" />
      <MarketMap v-else-if="section === 'IMAP'" />
      <Constituents v-else-if="section === 'MEMB'" />
      <Analytics v-else-if="section === 'IMON'" />
      <WorldIndices v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, defineComponent, h } from 'vue';

const GlobeIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('line', { x1: '2', y1: '12', x2: '22', y2: '12' }), h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })]) });

const props = defineProps<{ symbol?: string; activeSection?: string; }>();
const section = ref(props.activeSection || 'WINDEX');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const tabs = [
  { id: 'WINDEX', label: 'Мировые индексы' },
  { id: 'IMAP', label: 'Карта рынка' },
  { id: 'MEMB', label: 'Состав' },
  { id: 'IMON', label: 'Аналитика' },
];

const WorldIndices = defineComponent({
  setup() {
    const indices = [
      // США - Основные
      { name: 'S&P 500', symbol: 'SPX', region: 'Americas', last: '5,845.20', change: '+0.85%', ytd: '+22.4%' },
      { name: 'Nasdaq 100', symbol: 'NDX', region: 'Americas', last: '20,150.10', change: '+1.20%', ytd: '+35.1%' },
      { name: 'Dow Jones Industrial', symbol: 'DJI', region: 'Americas', last: '39,100.20', change: '+0.15%', ytd: '+18.5%' },
      { name: 'Russell 2000', symbol: 'RUT', region: 'Americas', last: '2,050.40', change: '+1.10%', ytd: '+12.8%' },
      { name: 'S&P 400 MidCap', symbol: 'MID', region: 'Americas', last: '2,985.60', change: '+0.75%', ytd: '+15.2%' },
      { name: 'VIX Volatility', symbol: 'VIX', region: 'Americas', last: '13.50', change: '-4.20%', ytd: '-18.5%' },
      { name: 'NYSE Composite', symbol: 'NYA', region: 'Americas', last: '17,250.40', change: '+0.55%', ytd: '+14.6%' },
      { name: 'Wilshire 5000', symbol: 'W5000', region: 'Americas', last: '48,250.80', change: '+0.65%', ytd: '+19.8%' },
      
      // США - Секторальные
      { name: 'S&P 500 Technology', symbol: 'SPT', region: 'Americas', last: '4,250.60', change: '+1.45%', ytd: '+38.2%' },
      { name: 'S&P 500 Financials', symbol: 'SPF', region: 'Americas', last: '685.40', change: '+0.35%', ytd: '+12.4%' },
      { name: 'S&P 500 Healthcare', symbol: 'SPH', region: 'Americas', last: '1,485.20', change: '+0.55%', ytd: '+8.6%' },
      { name: 'S&P 500 Energy', symbol: 'SPE', region: 'Americas', last: '485.80', change: '+1.25%', ytd: '+6.2%' },
      { name: 'S&P 500 Consumer', symbol: 'SPC', region: 'Americas', last: '1,125.40', change: '+0.45%', ytd: '+11.8%' },
      { name: 'Nasdaq Composite', symbol: 'IXIC', region: 'Americas', last: '16,850.60', change: '+1.35%', ytd: '+32.5%' },
      { name: 'Dow Jones Transportation', symbol: 'DJT', region: 'Americas', last: '15,250.40', change: '+0.85%', ytd: '+9.4%' },
      { name: 'S&P 500 Utilities', symbol: 'SPU', region: 'Americas', last: '285.60', change: '+0.15%', ytd: '+4.2%' },
      
      // Канада
      { name: 'S&P/TSX Composite', symbol: 'TSX', region: 'Americas', last: '22,485.60', change: '+0.65%', ytd: '+10.8%' },
      { name: 'S&P/TSX 60', symbol: 'TX60', region: 'Americas', last: '1,285.40', change: '+0.55%', ytd: '+11.2%' },
      
      // Мексика
      { name: 'IPC Mexico', symbol: 'MXX', region: 'Americas', last: '58,250.40', change: '+0.45%', ytd: '+8.5%' },
      
      // Бразилия
      { name: 'Bovespa', symbol: 'BVSP', region: 'Americas', last: '128,450.80', change: '+1.15%', ytd: '+15.6%' },
      { name: 'IBOVESPA', symbol: 'IBOV', region: 'Americas', last: '125,850.60', change: '+1.05%', ytd: '+14.8%' },
      
      // Великобритания
      { name: 'FTSE 100', symbol: 'UKX', region: 'EMEA', last: '8,320.40', change: '+0.25%', ytd: '+8.4%' },
      { name: 'FTSE 250', symbol: 'MCX', region: 'EMEA', last: '20,485.60', change: '+0.35%', ytd: '+12.6%' },
      { name: 'FTSE All-Share', symbol: 'ASX', region: 'EMEA', last: '4,585.20', change: '+0.30%', ytd: '+9.8%' },
      
      // Германия
      { name: 'DAX', symbol: 'DAX', region: 'EMEA', last: '19,250.80', change: '+0.60%', ytd: '+15.5%' },
      { name: 'MDAX', symbol: 'MDAX', region: 'EMEA', last: '28,450.60', change: '+0.55%', ytd: '+13.2%' },
      { name: 'TecDAX', symbol: 'TECDAX', region: 'EMEA', last: '3,285.40', change: '+1.25%', ytd: '+18.6%' },
      
      // Франция
      { name: 'CAC 40', symbol: 'PX1', region: 'EMEA', last: '8,100.30', change: '-0.20%', ytd: '+11.4%' },
      { name: 'CAC Next 20', symbol: 'CN20', region: 'EMEA', last: '5,850.60', change: '+0.30%', ytd: '+9.8%' },
      
      // Италия
      { name: 'FTSE MIB', symbol: 'FTSEMIB', region: 'EMEA', last: '33,850.40', change: '+0.45%', ytd: '+14.2%' },
      
      // Испания
      { name: 'IBEX 35', symbol: 'IBEX', region: 'EMEA', last: '10,485.60', change: '+0.50%', ytd: '+12.8%' },
      
      // Нидерланды
      { name: 'AEX', symbol: 'AEX', region: 'EMEA', last: '825.40', change: '+0.40%', ytd: '+13.5%' },
      
      // Швейцария
      { name: 'SMI', symbol: 'SMI', region: 'EMEA', last: '11,285.60', change: '+0.35%', ytd: '+10.6%' },
      
      // Швеция
      { name: 'OMX Stockholm 30', symbol: 'OMXS30', region: 'EMEA', last: '2,485.60', change: '+0.55%', ytd: '+16.8%' },
      
      // Норвегия
      { name: 'OSEBX', symbol: 'OSEBX', region: 'EMEA', last: '1,285.40', change: '+0.65%', ytd: '+18.2%' },
      
      // Польша
      { name: 'WIG 20', symbol: 'WIG20', region: 'EMEA', last: '2,485.60', change: '+0.45%', ytd: '+11.4%' },
      
      // Турция
      { name: 'BIST 100', symbol: 'XU100', region: 'EMEA', last: '10,485.60', change: '+1.25%', ytd: '+45.2%' },
      
      // ЮАР
      { name: 'JSE Top 40', symbol: 'JSE40', region: 'EMEA', last: '68,250.40', change: '+0.35%', ytd: '+8.6%' },
      
      // Пана-Европейские
      { name: 'Euro Stoxx 50', symbol: 'STOXX50', region: 'EMEA', last: '5,100.30', change: '+0.55%', ytd: '+12.4%' },
      { name: 'Stoxx Europe 600', symbol: 'SXXP', region: 'EMEA', last: '515.40', change: '+0.40%', ytd: '+11.8%' },
      
      // Япония
      { name: 'Nikkei 225', symbol: 'NI225', region: 'APAC', last: '40,100.00', change: '+1.50%', ytd: '+24.5%' },
      { name: 'Topix', symbol: 'TOPIX', region: 'APAC', last: '2,850.60', change: '+1.25%', ytd: '+22.8%' },
      { name: 'JPX-Nikkei 400', symbol: 'JPXN400', region: 'APAC', last: '15,485.60', change: '+1.35%', ytd: '+23.6%' },
      
      // Китай
      { name: 'Shanghai Composite', symbol: 'SSEC', region: 'APAC', last: '3,050.20', change: '+0.10%', ytd: '+5.4%' },
      { name: 'CSI 300', symbol: 'CSI300', region: 'APAC', last: '3,685.40', change: '+0.25%', ytd: '+6.8%' },
      { name: 'Shenzhen Composite', symbol: 'SZSE', region: 'APAC', last: '1,985.60', change: '+0.15%', ytd: '+4.2%' },
      { name: 'Hang Seng', symbol: 'HSI', region: 'APAC', last: '21,500.80', change: '-0.50%', ytd: '+18.2%' },
      { name: 'Hang Seng Tech', symbol: 'HSTECH', region: 'APAC', last: '4,285.60', change: '-0.85%', ytd: '+22.4%' },
      
      // Южная Корея
      { name: 'KOSPI', symbol: 'KS11', region: 'APAC', last: '2,685.40', change: '+0.75%', ytd: '+16.8%' },
      { name: 'KOSDAQ', symbol: 'KQ11', region: 'APAC', last: '885.60', change: '+1.15%', ytd: '+19.4%' },
      
      // Тайвань
      { name: 'Taiwan Weighted', symbol: 'TWII', region: 'APAC', last: '21,485.60', change: '+1.25%', ytd: '+28.6%' },
      
      // Индия
      { name: 'Nifty 50', symbol: 'NSEI', region: 'APAC', last: '24,285.60', change: '+0.85%', ytd: '+18.4%' },
      { name: 'BSE Sensex', symbol: 'BSESN', region: 'APAC', last: '78,485.60', change: '+0.75%', ytd: '+17.8%' },
      
      // Австралия
      { name: 'ASX 200', symbol: 'AXJO', region: 'APAC', last: '7,885.60', change: '+0.55%', ytd: '+9.6%' },
      { name: 'All Ordinaries', symbol: 'AORD', region: 'APAC', last: '8,125.40', change: '+0.50%', ytd: '+10.2%' },
      
      // Новая Зеландия
      { name: 'NZX 50', symbol: 'NZ50', region: 'APAC', last: '12,485.60', change: '+0.35%', ytd: '+7.8%' },
      
      // Сингапур
      { name: 'Straits Times', symbol: 'STI', region: 'APAC', last: '3,285.60', change: '+0.25%', ytd: '+6.4%' },
      
      // Индонезия
      { name: 'Jakarta Composite', symbol: 'JKSE', region: 'APAC', last: '7,285.60', change: '+0.65%', ytd: '+8.2%' },
      
      // Таиланд
      { name: 'SET Index', symbol: 'SET', region: 'APAC', last: '1,685.60', change: '+0.45%', ytd: '+5.6%' },
      
      // Малайзия
      { name: 'FTSE Bursa Malaysia', symbol: 'KLSE', region: 'APAC', last: '1,585.60', change: '+0.30%', ytd: '+4.8%' },
      
      // Филиппины
      { name: 'PSEi', symbol: 'PSEI', region: 'APAC', last: '6,485.60', change: '+0.55%', ytd: '+7.2%' },
      
      // Вьетнам
      { name: 'VN-Index', symbol: 'VNINDEX', region: 'APAC', last: '1,285.60', change: '+0.40%', ytd: '+6.8%' },
      
      // Россия
      { name: 'МосБиржа', symbol: 'IMOEX', region: 'EMEA', last: '3,285.40', change: '+1.25%', ytd: '+14.6%' },
      { name: 'RTS', symbol: 'RTSI', region: 'EMEA', last: '1,185.60', change: '+0.95%', ytd: '+12.8%' },
      { name: 'MOEX Russia', symbol: 'MOEX', region: 'EMEA', last: '3,185.40', change: '+1.15%', ytd: '+13.4%' },
    ];
    const regions = ['Americas', 'EMEA', 'APAC'];
    return { indices, regions };
  },
  template: `
    <div class="space-y-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Глобальный настрой</h3><div class="text-3xl font-bold text-emerald-400">Риск-он</div></div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Лидер роста</h3><div class="text-3xl font-bold text-white">Nikkei 225</div><div class="text-xs text-emerald-400 mt-1">+1.50%</div></div>
        <div class="p-6 rounded-2xl bg-white/5 border border-white/5"><h3 class="text-sm font-bold text-gray-400 uppercase mb-2">Аутсайдер</h3><div class="text-3xl font-bold text-white">Hang Seng</div><div class="text-xs text-rose-400 mt-1">-0.50%</div></div>
      </div>
      <div v-for="region in regions" :key="region" class="bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
        <div class="p-4 bg-white/5 border-b border-white/5"><h3 class="font-bold text-white">{{ region }}</h3></div>
        <table class="w-full text-left"><thead><tr class="text-xs text-gray-500 uppercase"><th class="p-4">Индекс</th><th class="p-4">Тикер</th><th class="p-4 text-right">Последняя</th><th class="p-4 text-right">Изменение</th><th class="p-4 text-right">С начала года</th></tr></thead>
        <tbody class="text-sm font-mono text-gray-300">
          <tr v-for="idx in indices.filter(i => i.region === region)" :key="idx.name" class="border-t border-white/5 hover:bg-white/5 cursor-pointer">
            <td class="p-4 font-bold text-white">{{ idx.name }}</td>
            <td class="p-4 text-gray-400">{{ idx.symbol }}</td>
            <td class="p-4 text-right">{{ idx.last }}</td>
            <td :class="['p-4 text-right font-bold', idx.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400']">{{ idx.change }}</td>
            <td :class="['p-4 text-right', idx.ytd.startsWith('+') ? 'text-emerald-400' : 'text-rose-400']">{{ idx.ytd }}</td>
          </tr>
        </tbody></table>
      </div>
    </div>
  `
});

const MarketMap = defineComponent({ template: `<div class="flex-1 flex items-center justify-center text-gray-500 h-full">[Карта рынка - Тепловая карта]</div>` });
const Constituents = defineComponent({ template: `<div class="flex-1 flex items-center justify-center text-gray-500 h-full">[Состав индекса - Таблица]</div>` });
const Analytics = defineComponent({ template: `<div class="flex-1 flex items-center justify-center text-gray-500 h-full">[Аналитика индексов - Графики]</div>` });
</script>
