<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <div class="flex flex-col md:flex-row items-center justify-between p-6 border-b border-white/5 bg-black/20 gap-4">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-700/20 to-zinc-700/20 flex items-center justify-center text-lg font-bold text-gray-300 border border-gray-500/30">
          <component :is="section === 'FLDS' ? DatabaseIcon : HelpCircleIcon" class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">{{ section === 'FLDS' ? 'Справочные данные' : 'Помощь и поддержка' }}</h2>
          <p class="text-xs text-gray-400">{{ section === 'FLDS' ? 'Каталог полей данных терминала' : 'Документация, FAQ и поддержка' }}</p>
        </div>
      </div>
      <div class="flex bg-black/40 rounded-xl p-1 border border-white/5 overflow-x-auto">
        <button @click="section = 'FLDS'" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === 'FLDS' ? 'bg-gray-600/20 text-gray-200 border border-gray-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          Справочные данные
        </button>
        <button @click="section = 'HL'" :class="['px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap', section === 'HL' ? 'bg-gray-600/20 text-gray-200 border border-gray-500/30' : 'text-gray-500 hover:text-white hover:bg-white/5']">
          Помощь
        </button>
      </div>
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar p-6 bg-gradient-to-b from-black/10 to-transparent">
      <DataFieldsCatalog v-if="section === 'FLDS'" />
      <HelpCenter v-else />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, defineComponent, h } from 'vue';

const DatabaseIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('ellipse', { cx: '12', cy: '5', rx: '9', ry: '3' }), h('path', { d: 'M21 12c0 1.66-4 3-9 3s-9-1.34-9-3' }), h('path', { d: 'M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5' })]) });
const HelpCircleIcon = defineComponent({ render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('circle', { cx: '12', cy: '12', r: '10' }), h('path', { d: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3' }), h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' })]) });

const props = defineProps<{ activeSection?: string; }>();
const section = ref(props.activeSection || 'FLDS');
watch(() => props.activeSection, (v) => { if (v) section.value = v; });

const DataFieldsCatalog = defineComponent({
  setup() {
    const searchQuery = ref('');
    const selectedCategory = ref('Все');
    
    const fields = [
      // Рыночные данные
      { mnemonic: 'LAST_PRICE', name: 'Последняя цена', category: 'Рыночные данные', desc: 'Цена последней сделки по активу', unit: '₽' },
      { mnemonic: 'PX_OPEN', name: 'Цена открытия', category: 'Рыночные данные', desc: 'Цена на момент открытия торгов', unit: '₽' },
      { mnemonic: 'PX_HIGH', name: 'Максимальная цена', category: 'Рыночные данные', desc: 'Максимальная цена за торговую сессию', unit: '₽' },
      { mnemonic: 'PX_LOW', name: 'Минимальная цена', category: 'Рыночные данные', desc: 'Минимальная цена за торговую сессию', unit: '₽' },
      { mnemonic: 'PX_CLOSE', name: 'Цена закрытия', category: 'Рыночные данные', desc: 'Цена на момент закрытия торгов', unit: '₽' },
      { mnemonic: 'VOLUME', name: 'Объем торгов', category: 'Рыночные данные', desc: 'Общий объем торгов за период', unit: 'шт' },
      { mnemonic: 'TURNOVER', name: 'Оборот', category: 'Рыночные данные', desc: 'Денежный оборот за период', unit: '₽' },
      { mnemonic: 'BID', name: 'Лучшая цена покупки', category: 'Рыночные данные', desc: 'Лучшая цена в стакане на покупку', unit: '₽' },
      { mnemonic: 'ASK', name: 'Лучшая цена продажи', category: 'Рыночные данные', desc: 'Лучшая цена в стакане на продажу', unit: '₽' },
      { mnemonic: 'SPREAD', name: 'Спред', category: 'Рыночные данные', desc: 'Разница между лучшей ценой покупки и продажи', unit: '₽' },
      
      // Фундаментальные данные
      { mnemonic: 'PE_RATIO', name: 'P/E (коэффициент)', category: 'Фундаментальные', desc: 'Отношение цены к прибыли на акцию (TTM)', unit: '' },
      { mnemonic: 'PB_RATIO', name: 'P/B (коэффициент)', category: 'Фундаментальные', desc: 'Отношение цены к балансовой стоимости', unit: '' },
      { mnemonic: 'EPS_FWD', name: 'Прогноз EPS', category: 'Фундаментальные', desc: 'Консенсус-прогноз прибыли на акцию на 12 месяцев', unit: '₽' },
      { mnemonic: 'EPS_TTM', name: 'EPS за 12 месяцев', category: 'Фундаментальные', desc: 'Прибыль на акцию за последние 12 месяцев', unit: '₽' },
      { mnemonic: 'DIV_YIELD', name: 'Дивидендная доходность', category: 'Фундаментальные', desc: 'Годовая дивидендная доходность', unit: '%' },
      { mnemonic: 'MARKET_CAP', name: 'Рыночная капитализация', category: 'Фундаментальные', desc: 'Общая стоимость компании на рынке', unit: '₽' },
      { mnemonic: 'REVENUE', name: 'Выручка', category: 'Фундаментальные', desc: 'Общая выручка компании за период', unit: '₽' },
      { mnemonic: 'NET_INCOME', name: 'Чистая прибыль', category: 'Фундаментальные', desc: 'Чистая прибыль компании за период', unit: '₽' },
      
      // Технические индикаторы
      { mnemonic: 'RSI_14D', name: 'RSI (14 периодов)', category: 'Технические', desc: 'Индекс относительной силы (14 периодов)', unit: '' },
      { mnemonic: 'MACD', name: 'MACD', category: 'Технические', desc: 'Схождение-расхождение скользящих средних', unit: '' },
      { mnemonic: 'MA_20', name: 'Скользящая средняя (20)', category: 'Технические', desc: 'Простая скользящая средняя за 20 периодов', unit: '₽' },
      { mnemonic: 'MA_50', name: 'Скользящая средняя (50)', category: 'Технические', desc: 'Простая скользящая средняя за 50 периодов', unit: '₽' },
      { mnemonic: 'MA_200', name: 'Скользящая средняя (200)', category: 'Технические', desc: 'Простая скользящая средняя за 200 периодов', unit: '₽' },
      { mnemonic: 'BB_UPPER', name: 'Верхняя полоса Боллинджера', category: 'Технические', desc: 'Верхняя граница полос Боллинджера', unit: '₽' },
      { mnemonic: 'BB_LOWER', name: 'Нижняя полоса Боллинджера', category: 'Технические', desc: 'Нижняя граница полос Боллинджера', unit: '₽' },
      { mnemonic: 'ATR_14', name: 'ATR (14 периодов)', category: 'Технические', desc: 'Средний истинный диапазон за 14 периодов', unit: '₽' },
      { mnemonic: 'STOCH_K', name: 'Стохастик %K', category: 'Технические', desc: 'Стохастический осциллятор %K', unit: '%' },
      { mnemonic: 'STOCH_D', name: 'Стохастик %D', category: 'Технические', desc: 'Стохастический осциллятор %D', unit: '%' },
      
      // Риск-метрики
      { mnemonic: 'BETA_RAW', name: 'Бета (коэффициент)', category: 'Риск', desc: 'Наклон линии регрессии относительно бенчмарка', unit: '' },
      { mnemonic: 'VOLATILITY', name: 'Волатильность', category: 'Риск', desc: 'Стандартное отклонение доходности (годовое)', unit: '%' },
      { mnemonic: 'VAR_95', name: 'VaR (95%)', category: 'Риск', desc: 'Value at Risk на уровне доверия 95%', unit: '%' },
      { mnemonic: 'VAR_99', name: 'VaR (99%)', category: 'Риск', desc: 'Value at Risk на уровне доверия 99%', unit: '%' },
      { mnemonic: 'CVAR', name: 'Expected Shortfall', category: 'Риск', desc: 'Условный Value at Risk (CVaR)', unit: '%' },
      { mnemonic: 'SHARPE', name: 'Коэффициент Шарпа', category: 'Риск', desc: 'Отношение избыточной доходности к волатильности', unit: '' },
      { mnemonic: 'SORTINO', name: 'Коэффициент Сортино', category: 'Риск', desc: 'Отношение избыточной доходности к downside deviation', unit: '' },
      { mnemonic: 'MAX_DD', name: 'Максимальная просадка', category: 'Риск', desc: 'Максимальная просадка от пика', unit: '%' },
      
      // Облигации
      { mnemonic: 'YTM', name: 'Доходность к погашению', category: 'Облигации', desc: 'Yield to Maturity - доходность к погашению', unit: '%' },
      { mnemonic: 'DURATION', name: 'Дюрация', category: 'Облигации', desc: 'Модифицированная дюрация облигации', unit: 'лет' },
      { mnemonic: 'DV01', name: 'DV01', category: 'Облигации', desc: 'Изменение цены при сдвиге кривой на 1 б.п.', unit: '₽' },
      { mnemonic: 'CONVEXITY', name: 'Выпуклость', category: 'Облигации', desc: 'Convexity облигации', unit: '' },
      { mnemonic: 'COUPON_RATE', name: 'Купонная ставка', category: 'Облигации', desc: 'Годовая купонная ставка', unit: '%' },
      { mnemonic: 'ACCRUED_INT', name: 'Накопленный купон', category: 'Облигации', desc: 'Накопленный купонный доход', unit: '₽' },
      { mnemonic: 'CLEAN_PRICE', name: 'Чистая цена', category: 'Облигации', desc: 'Цена облигации без накопленного купона', unit: '₽' },
      { mnemonic: 'DIRTY_PRICE', name: 'Грязная цена', category: 'Облигации', desc: 'Полная цена облигации с накопленным купоном', unit: '₽' },
      
      // Опционы
      { mnemonic: 'IV', name: 'Подразумеваемая волатильность', category: 'Опционы', desc: 'Implied Volatility опциона', unit: '%' },
      { mnemonic: 'DELTA', name: 'Дельта', category: 'Опционы', desc: 'Чувствительность цены опциона к изменению спота', unit: '' },
      { mnemonic: 'GAMMA', name: 'Гамма', category: 'Опционы', desc: 'Чувствительность дельты к изменению спота', unit: '' },
      { mnemonic: 'VEGA', name: 'Вега', category: 'Опционы', desc: 'Чувствительность цены опциона к изменению волатильности', unit: '' },
      { mnemonic: 'THETA', name: 'Тета', category: 'Опционы', desc: 'Временной распад опциона', unit: '₽/день' },
      { mnemonic: 'RHO', name: 'Ро', category: 'Опционы', desc: 'Чувствительность цены опциона к изменению ставки', unit: '' },
      { mnemonic: 'INTRINSIC', name: 'Внутренняя стоимость', category: 'Опционы', desc: 'Внутренняя стоимость опциона', unit: '₽' },
      { mnemonic: 'TIME_VALUE', name: 'Временная стоимость', category: 'Опционы', desc: 'Временная стоимость опциона', unit: '₽' },
    ];
    
    const categories = ['Все', 'Рыночные данные', 'Фундаментальные', 'Технические', 'Риск', 'Облигации', 'Опционы'];
    
    const filteredFields = computed(() => {
      let result = fields;
      
      if (selectedCategory.value !== 'Все') {
        result = result.filter(f => f.category === selectedCategory.value);
      }
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(f => 
          f.mnemonic.toLowerCase().includes(query) ||
          f.name.toLowerCase().includes(query) ||
          f.desc.toLowerCase().includes(query)
        );
      }
      
      return result;
    });
    
    return { fields, categories, searchQuery, selectedCategory, filteredFields };
  },
  template: `
    <div class="flex flex-col h-full gap-6">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="relative flex-1">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Поиск по мнемонике или названию..." 
            class="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:border-indigo-500/50 focus:bg-white/10 outline-none transition-all" 
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
        </div>
        <div class="flex gap-2 overflow-x-auto pb-2">
          <button 
            v-for="cat in categories" 
            :key="cat" 
            @click="selectedCategory = cat"
            :class="['px-3 py-2 rounded-lg text-xs font-bold border transition-all whitespace-nowrap', selectedCategory === cat ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 border-white/5']"
          >
            {{ cat }}
          </button>
        </div>
      </div>
      
      <div class="flex items-center justify-between text-xs text-gray-400 mb-2">
        <span>Найдено полей: <span class="text-white font-bold">{{ filteredFields.length }}</span></span>
        <span>Всего полей: <span class="text-white font-bold">{{ fields.length }}</span></span>
      </div>
      
      <div class="flex-1 overflow-auto rounded-2xl border border-white/5 bg-black/20">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="text-xs text-gray-400 uppercase bg-white/5 sticky top-0 z-10">
              <th class="p-4 font-bold">Мнемоника</th>
              <th class="p-4 font-bold">Название</th>
              <th class="p-4 font-bold">Категория</th>
              <th class="p-4 font-bold">Единица</th>
              <th class="p-4 font-bold">Описание</th>
            </tr>
          </thead>
          <tbody class="text-sm font-mono text-gray-300">
            <tr 
              v-for="(f, i) in filteredFields" 
              :key="i" 
              class="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td class="p-4 font-bold text-indigo-300">{{ f.mnemonic }}</td>
              <td class="p-4 text-white font-sans font-bold">{{ f.name }}</td>
              <td class="p-4">
                <span class="px-2 py-1 rounded bg-white/5 text-[10px] text-gray-400 uppercase border border-white/5">
                  {{ f.category }}
                </span>
              </td>
              <td class="p-4 text-gray-500 font-mono text-xs">{{ f.unit || '-' }}</td>
              <td class="p-4 text-gray-400 font-sans text-xs">{{ f.desc }}</td>
            </tr>
            <tr v-if="filteredFields.length === 0" class="border-b border-white/5">
              <td colspan="5" class="p-8 text-center text-gray-500 font-sans">
                Ничего не найдено. Попробуйте изменить параметры поиска.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
});

const HelpCenter = defineComponent({
  template: `
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 h-full">
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
        <div class="p-3 bg-blue-500/20 rounded-xl text-blue-400 w-fit mb-4">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white mb-2">Документация</h3>
        <p class="text-sm text-gray-400 mb-4">Подробные руководства по функциям терминала, синтаксису и API.</p>
        <span class="text-xs text-blue-400 font-bold group-hover:underline">Читать документацию →</span>
      </div>
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
        <div class="p-3 bg-emerald-500/20 rounded-xl text-emerald-400 w-fit mb-4">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white mb-2">Поддержка</h3>
        <p class="text-sm text-gray-400 mb-4">Чат с нашей службой поддержки 24/7 для решения технических вопросов.</p>
        <span class="text-xs text-emerald-400 font-bold group-hover:underline">Начать чат →</span>
      </div>
      <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer group">
        <div class="p-3 bg-purple-500/20 rounded-xl text-purple-400 w-fit mb-4">
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
        </div>
        <h3 class="text-lg font-bold text-white mb-2">API Справочник</h3>
        <p class="text-sm text-gray-400 mb-4">Интегрируйте данные терминала в свои приложения.</p>
        <span class="text-xs text-purple-400 font-bold group-hover:underline">Просмотреть спецификацию →</span>
      </div>
      <div class="col-span-1 md:col-span-2 lg:col-span-3 p-6 rounded-2xl bg-black/20 border border-white/5 mt-4">
        <h3 class="text-lg font-bold text-white mb-4">Часто задаваемые вопросы</h3>
        <div class="space-y-2">
          <div 
            v-for="q in [
              'Как создать пользовательскую формулу?', 
              'Где найти исторические данные по спредам?', 
              'Как экспортировать данные в Excel?', 
              'Какая задержка у Live feed?',
              'Как использовать справочные данные в формулах?',
              'Где найти документацию по API?'
            ]" 
            :key="q" 
            class="p-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 flex justify-between items-center cursor-pointer transition-colors"
          >
            <span class="text-sm text-gray-300">{{ q }}</span>
            <span class="text-gray-600">→</span>
          </div>
        </div>
      </div>
    </div>
  `
});
</script>
