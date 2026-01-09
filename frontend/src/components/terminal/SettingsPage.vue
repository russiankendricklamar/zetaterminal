<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col md:flex-row animate-fade-in h-full">
    <!-- Sidebar -->
    <div class="w-full md:w-64 bg-black/20 border-r border-white/5 p-4 flex flex-col gap-2">
      <div class="px-4 py-4 mb-2">
        <h2 class="text-xl font-bold text-white tracking-tight">Настройки</h2>
        <p class="text-xs text-gray-500">Конфигурация системы</p>
      </div>
      <button
        v-for="item in menuItems"
        :key="item.id"
        @click="section = item.id"
        :class="`w-full flex items-center justify-center px-4 py-3 rounded-xl text-sm font-bold transition-all text-center ${
          section === item.id 
          ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' 
          : 'text-gray-400 hover:text-white hover:bg-white/5 border border-transparent'
        }`"
      >
        {{ item.label }}
      </button>
    </div>

    <!-- Content Area -->
    <div class="flex-1 bg-gradient-to-br from-black/10 to-transparent p-8 overflow-y-auto custom-scrollbar">
      <!-- Launchpad -->
      <div v-if="section === 'BLP'" class="space-y-8">
        <div>
          <h3 class="text-2xl font-bold text-white mb-2">Мониторинг панели</h3>
          <p class="text-sm text-gray-400">Настройте рабочие пространства и пользовательские панели.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 hover:border-indigo-500/50 transition-colors cursor-pointer group">
            <div class="flex justify-between items-start mb-4">
              <div class="p-3 bg-indigo-500/20 rounded-xl text-indigo-400">
                <MonitorIcon class="w-6 h-6" />
              </div>
              <span class="bg-emerald-500/10 text-emerald-400 text-xs px-2 py-1 rounded border border-emerald-500/20">Активно</span>
            </div>
            <h4 class="text-lg font-bold text-white mb-1">Главный терминал</h4>
            <p class="text-xs text-gray-500 mb-4">4 графика, стакан, лента новостей</p>
            <div class="h-24 bg-black/40 rounded-lg border border-white/5 relative overflow-hidden">
              <div class="absolute top-2 left-2 right-2 bottom-2 grid grid-cols-3 gap-1 opacity-50">
                <div class="col-span-2 bg-white/20 rounded"></div>
                <div class="bg-white/20 rounded"></div>
                <div class="col-span-3 h-8 bg-white/20 rounded mt-auto"></div>
              </div>
            </div>
          </div>

          <div class="p-6 rounded-2xl bg-white/5 border border-white/5 border-dashed flex flex-col items-center justify-center text-center cursor-pointer hover:bg-white/10 transition-colors">
            <div class="p-4 bg-white/5 rounded-full mb-4">
              <PlusIcon class="w-6 h-6 text-gray-400" />
            </div>
            <h4 class="text-sm font-bold text-white">Создать монитор</h4>
            <p class="text-xs text-gray-500 mt-1">Начать с нуля или шаблона</p>
          </div>
        </div>
      </div>

      <!-- Screen Constructor -->
      <div v-else-if="section === 'CONSTRUCTOR'" class="space-y-8">
        <div>
          <h3 class="text-2xl font-bold text-white mb-2">Конструктор экрана</h3>
          <p class="text-sm text-gray-400">Добавляйте и настраивайте виджеты для главной страницы терминала.</p>
        </div>

        <!-- Available Widgets -->
        <div>
          <h4 class="text-lg font-bold text-white mb-4">Доступные виджеты</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="widget in availableWidgets"
              :key="widget.type"
              class="p-4 rounded-xl bg-white/5 border border-white/5 hover:border-indigo-500/50 transition-colors cursor-pointer group"
              @click="addWidget(widget)"
            >
              <div class="flex items-center gap-3 mb-3">
                <div :class="`p-2 rounded-lg ${widget.iconBg}`">
                  <component :is="widget.icon" :class="`w-5 h-5 ${widget.iconColor}`" />
                </div>
                <div>
                  <h5 class="text-sm font-bold text-white">{{ widget.title }}</h5>
                  <p class="text-xs text-gray-500">{{ widget.description }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2 text-xs text-gray-400">
                <span>Размер:</span>
                <span class="font-mono text-white">{{ widget.defaultWidth }}×{{ widget.defaultHeight }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Active Widgets -->
        <div>
          <div class="flex justify-between items-center mb-4">
            <h4 class="text-lg font-bold text-white">Активные виджеты</h4>
            <span class="text-xs text-gray-500">{{ activeWidgets.length }} виджетов</span>
          </div>
          <div class="space-y-2">
            <div
              v-for="widget in activeWidgets"
              :key="widget.id"
              class="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
            >
              <div class="flex items-center gap-3">
                <div :class="`p-2 rounded-lg ${widget.iconBg}`">
                  <component :is="widget.icon" :class="`w-4 h-4 ${widget.iconColor}`" />
                </div>
                <div>
                  <div class="text-sm font-bold text-white">{{ widget.title }}</div>
                  <div class="text-xs text-gray-500">Размер: {{ widget.width }}×{{ widget.height }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click.stop="editWidgetSize(widget)"
                  class="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                  title="Изменить размер"
                >
                  <SlidersIcon class="w-4 h-4" />
                </button>
                <button
                  @click.stop="removeWidget(widget.id)"
                  class="p-2 rounded-lg hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 transition-colors"
                  title="Удалить"
                >
                  <XIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div v-if="activeWidgets.length === 0" class="text-center py-8 text-gray-500 text-sm">
              Нет активных виджетов. Добавьте виджеты из списка выше.
            </div>
          </div>
        </div>
      </div>

      <!-- Custom Screens -->
      <div v-else-if="section === 'NW'" class="space-y-8">
        <div class="flex justify-between items-center">
          <div>
            <h3 class="text-2xl font-bold text-white mb-2">Рабочие листы и списки</h3>
            <p class="text-sm text-gray-400">Управляйте пользовательскими экранами и списками активов.</p>
          </div>
          <button class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-xs flex items-center gap-2">
            <PlusIcon class="w-3.5 h-3.5" /> Новый лист
          </button>
        </div>

        <div class="bg-black/20 rounded-2xl border border-white/5 overflow-hidden">
          <table class="w-full text-left">
            <thead>
              <tr class="bg-white/5 text-xs text-gray-500 uppercase border-b border-white/10">
                <th class="p-4">Имя</th>
                <th class="p-4">Тип</th>
                <th class="p-4">Активы</th>
                <th class="p-4">Изменено</th>
                <th class="p-4 text-right">Действия</th>
              </tr>
            </thead>
            <tbody class="text-sm font-mono text-gray-300">
              <tr v-for="(row, i) in worksheets" :key="i" class="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td class="p-4 font-bold text-white">{{ row.name }}</td>
                <td class="p-4">
                  <span :class="`px-2 py-1 rounded text-xs border ${row.type === 'Watchlist' ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' : 'bg-purple-500/10 border-purple-500/20 text-purple-400'}`">
                    {{ row.type === 'Watchlist' ? 'Список' : 'Макет' }}
                  </span>
                </td>
                <td class="p-4">{{ row.count }}</td>
                <td class="p-4 text-gray-500 text-xs">{{ row.date }}</td>
                <td class="p-4 text-right">
                  <button class="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors">
                    <SlidersIcon class="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Personal Settings -->
      <div v-else-if="section === 'PDF'" class="space-y-8">
        <div>
          <h3 class="text-2xl font-bold text-white mb-2">Личные предпочтения</h3>
          <p class="text-sm text-gray-400">Настройте работу терминала под себя.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="space-y-6">
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Язык</label>
              <div class="flex items-center gap-2 p-3 bg-black/20 rounded-xl border border-white/10">
                <GlobeIcon class="w-4 h-4 text-gray-400" />
                <select class="bg-transparent text-white text-sm outline-none flex-1">
                  <option>Английский (US)</option>
                  <option>Русский</option>
                  <option>Китайский (упрощённый)</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Валюта по умолчанию</label>
              <div class="flex items-center gap-2 p-3 bg-black/20 rounded-xl border border-white/10">
                <span class="text-gray-400 text-sm font-bold">$</span>
                <select class="bg-transparent text-white text-sm outline-none flex-1">
                  <option>USD - Доллар США</option>
                  <option>EUR - Евро</option>
                  <option>RUB - Российский рубль</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Часовой пояс</label>
              <div class="flex items-center gap-2 p-3 bg-black/20 rounded-xl border border-white/10">
                <ClockIcon class="w-4 h-4 text-gray-400" />
                <select class="bg-transparent text-white text-sm outline-none flex-1">
                  <option>UTC-05:00 (Восточное время)</option>
                  <option>UTC+00:00 (Лондон)</option>
                  <option>UTC+03:00 (Москва)</option>
                </select>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Тема</label>
              <div class="grid grid-cols-2 gap-4">
                <button class="flex items-center justify-center gap-2 p-3 rounded-xl border border-white/10 bg-white/5 text-white hover:bg-white/10">
                  <MoonIcon class="w-4 h-4" /> Тёмная (Pro)
                </button>
                <button class="flex items-center justify-center gap-2 p-3 rounded-xl border border-white/10 bg-transparent text-gray-500 hover:text-white hover:bg-white/5">
                  <SunIcon class="w-4 h-4" /> Светлая
                </button>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Плотность макета</label>
              <div class="flex bg-black/20 rounded-xl p-1 border border-white/10">
                <button class="flex-1 py-2 text-xs font-bold text-gray-500 hover:text-white">Комфортная</button>
                <button class="flex-1 py-2 text-xs font-bold text-white bg-white/10 rounded-lg shadow">Компактная</button>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase mb-2">Избранные активы</label>
              <div class="space-y-2 max-h-48 overflow-y-auto custom-scrollbar">
                <div v-for="asset in favoriteAssets" :key="asset" class="flex items-center justify-between p-2 bg-black/20 rounded-lg border border-white/5 hover:bg-white/5 transition-colors">
                  <span class="text-sm text-white font-mono">{{ asset }}</span>
                  <button @click="removeFavorite(asset)" class="text-gray-500 hover:text-rose-400 transition-colors">
                    <XIcon class="w-4 h-4" />
                  </button>
                </div>
                <div v-if="favoriteAssets.length === 0" class="text-xs text-gray-500 text-center py-4">
                  Нет избранных активов
                </div>
              </div>
              <div class="mt-3 flex gap-2">
                <input 
                  v-model="newAsset"
                  @keyup.enter="addFavorite"
                  type="text"
                  placeholder="Введите тикер (например: BTC/USDT)"
                  class="flex-1 bg-black/20 border border-white/10 rounded-lg py-2 px-3 text-sm text-white focus:border-indigo-500/50 outline-none"
                />
                <button 
                  @click="addFavorite"
                  class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  Добавить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Default -->
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <h3 class="text-xl font-bold text-white mb-2">{{ section }} Раздел</h3>
          <p class="text-gray-400">Содержимое появится в ближайшее время</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { defineComponent, h } from 'vue';

interface Props {
  activeSection: string;
}

const props = defineProps<Props>();

const section = ref(props.activeSection);

watch(() => props.activeSection, (val) => { section.value = val; });

const menuItems = [
  { id: 'BLP', label: 'Панель запуска', icon: 'MonitorIcon' },
  { id: 'CONSTRUCTOR', label: 'Конструктор экрана', icon: 'LayoutIcon' },
  { id: 'NW', label: 'Пользовательские экраны', icon: 'LayoutIcon' },
  { id: 'ALRT', label: 'Уведомления', icon: 'BellIcon' },
  { id: 'PDF', label: 'Личные настройки', icon: 'UserIcon' },
  { id: 'SALT', label: 'Новостные уведомления', icon: 'MailIcon' },
];

const worksheets = [
  { name: 'Технологический рост', type: 'Watchlist', count: 12, date: '2 часа назад' },
  { name: 'Глобальный макро', type: 'Layout', count: '-', date: '1 день назад' },
  { name: 'Крипто ядро', type: 'Watchlist', count: 5, date: '3 дня назад' },
  { name: 'Сезон отчётов', type: 'Layout', count: '-', date: '15 окт' },
];

// Избранные активы
const favoriteAssets = ref<string[]>(['BTC/USDT', 'ETH/USDT', 'AAPL', 'TSLA']);
const newAsset = ref('');

const addFavorite = () => {
  if (newAsset.value.trim() && !favoriteAssets.value.includes(newAsset.value.trim().toUpperCase())) {
    favoriteAssets.value.push(newAsset.value.trim().toUpperCase());
    newAsset.value = '';
  }
};

const removeFavorite = (asset: string) => {
  favoriteAssets.value = favoriteAssets.value.filter(a => a !== asset);
};

// Конструктор экрана
const availableWidgets = [
  {
    type: 'OrderBook',
    title: 'Стакан',
    description: 'Отображение биржевого стакана с ордерами',
    icon: 'BookIcon',
    iconBg: 'bg-blue-500/20',
    iconColor: 'text-blue-400',
    defaultWidth: 2,
    defaultHeight: 4,
  },
  {
    type: 'Chart',
    title: 'График цены',
    description: 'Интерактивный график движения цены',
    icon: 'LineChartIcon',
    iconBg: 'bg-emerald-500/20',
    iconColor: 'text-emerald-400',
    defaultWidth: 6,
    defaultHeight: 4,
  },
  {
    type: 'News',
    title: 'Новости',
    description: 'Лента последних новостей рынка',
    icon: 'NewspaperIcon',
    iconBg: 'bg-purple-500/20',
    iconColor: 'text-purple-400',
    defaultWidth: 2,
    defaultHeight: 2,
  },
  {
    type: 'AI',
    title: 'ИИ Аналитик',
    description: 'Анализ рынка с помощью искусственного интеллекта',
    icon: 'BrainIcon',
    iconBg: 'bg-indigo-500/20',
    iconColor: 'text-indigo-400',
    defaultWidth: 2,
    defaultHeight: 2,
  },
  {
    type: 'Footer',
    title: 'Ордера и позиции',
    description: 'Открытые ордера и текущие позиции',
    icon: 'ListIcon',
    iconBg: 'bg-orange-500/20',
    iconColor: 'text-orange-400',
    defaultWidth: 3,
    defaultHeight: 1,
  },
  {
    type: 'Markets',
    title: 'Рынки',
    description: 'Топ активов и их изменения',
    icon: 'TrendingUpIcon',
    iconBg: 'bg-green-500/20',
    iconColor: 'text-green-400',
    defaultWidth: 2,
    defaultHeight: 3,
  },
  {
    type: 'Analytics',
    title: 'Аналитика',
    description: 'Ключевые метрики и показатели',
    icon: 'BarChartIcon',
    iconBg: 'bg-cyan-500/20',
    iconColor: 'text-cyan-400',
    defaultWidth: 2,
    defaultHeight: 2,
  },
];

const loadActiveWidgets = () => {
  const saved = localStorage.getItem('terminal-widgets');
  if (saved) {
    try {
      const widgets = JSON.parse(saved);
      return widgets.map((w: any) => {
        const template = availableWidgets.find(aw => aw.type === w.type);
        return {
          ...w,
          title: template?.title || w.type,
          icon: template?.icon || 'LayoutIcon',
          iconBg: template?.iconBg || 'bg-gray-500/20',
          iconColor: template?.iconColor || 'text-gray-400',
        };
      });
    } catch (e) {
      console.error('Failed to load widgets:', e);
    }
  }
  return [];
};

const activeWidgets = ref(loadActiveWidgets());

const addWidget = (widget: typeof availableWidgets[0]) => {
  const newWidget = {
    id: `${widget.type}-${Date.now()}`,
    type: widget.type,
    title: widget.title,
    icon: widget.icon,
    iconBg: widget.iconBg,
    iconColor: widget.iconColor,
    width: widget.defaultWidth,
    height: widget.defaultHeight,
  };
  
  activeWidgets.value.push(newWidget);
  saveWidgets();
};

const removeWidget = (id: string) => {
  activeWidgets.value = activeWidgets.value.filter(w => w.id !== id);
  saveWidgets();
};

const editWidgetSize = (widget: any) => {
  const newWidth = prompt('Ширина (в ячейках):', widget.width);
  const newHeight = prompt('Высота (в ячейках):', widget.height);
  
  if (newWidth && newHeight) {
    const w = parseInt(newWidth);
    const h = parseInt(newHeight);
    if (w > 0 && h > 0) {
      widget.width = w;
      widget.height = h;
      saveWidgets();
    }
  }
};

const saveWidgets = () => {
  const widgetsToSave = activeWidgets.value.map(w => ({
    id: w.id,
    type: w.type,
    width: w.width,
    height: w.height,
  }));
  localStorage.setItem('terminal-widgets', JSON.stringify(widgetsToSave));
  // Обновляем главную страницу
  window.dispatchEvent(new Event('widgets-updated'));
};

// Иконки для виджетов
const BookIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>' };
const LineChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const NewspaperIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>' };
const BrainIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.54ZM14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.54Z"/></svg>' };
const ListIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const BarChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' };

// Icon components
const MonitorIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>' };
const LayoutIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>' };
const BellIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>' };
const UserIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' };
const MailIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>' };
const PlusIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>' };
const SlidersIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/></svg>' };
const GlobeIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>' };
const ClockIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>' };
const MoonIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>' };
const SunIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>' };
const XIcon = defineComponent({ render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [h('line', { x1: '18', y1: '6', x2: '6', y2: '18' }), h('line', { x1: '6', y1: '6', x2: '18', y2: '18' })]) });
</script>
