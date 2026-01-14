<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full relative">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-white/5 bg-black/20 z-10">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight">Главная панель</h2>
        <p class="text-xs text-gray-400">Настраиваемая рабочая область</p>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div 
      ref="gridRef"
      class="flex-1 p-4 overflow-auto custom-scrollbar relative z-10"
    >
      <div 
        v-if="widgets.length > 0"
        class="dashboard-grid"
        :style="{ gridTemplateColumns: `repeat(${gridColumns}, 1fr)` }"
      >
        <div
          v-for="widget in widgets"
          :key="widget.id"
          :style="{ 
            gridColumn: `span ${widget.width}`, 
            gridRow: `span ${widget.height}`,
            minHeight: '100px'
          }"
          class="widget-container"
        >
          <component
            :is="widget.component"
            v-bind="widget.props"
            :width="widget.width"
            :height="widget.height"
            :resizable="false"
            :show-controls="false"
          />
        </div>
      </div>
      <div v-else class="flex items-center justify-center h-full">
        <div class="text-center">
          <p class="text-white text-lg mb-2">Нет виджетов</p>
          <p class="text-gray-400 text-sm">Загрузка виджетов...</p>
          <p class="text-gray-500 text-xs mt-2">Количество виджетов: {{ widgets.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import OrderBookWidget from './widgets/OrderBookWidget.vue';
import ChartWidgetWrapper from './widgets/ChartWidgetWrapper.vue';
import NewsWidget from './widgets/NewsWidget.vue';
import AIWidget from './widgets/AIWidget.vue';
import FooterWidget from './widgets/FooterWidget.vue';
import MarketsWidget from './widgets/MarketsWidget.vue';
import AnalyticsWidget from './widgets/AnalyticsWidget.vue';
import QuantitativeToolWidget from './widgets/QuantitativeToolWidget.vue';
import { Candle } from '@/types/terminal';

const widgetComponents: Record<string, any> = {
  OrderBook: OrderBookWidget,
  Chart: ChartWidgetWrapper,
  News: NewsWidget,
  AI: AIWidget,
  Footer: FooterWidget,
  Markets: MarketsWidget,
  Analytics: AnalyticsWidget,
  // Quantitative Analysis Tools
  VOL: QuantitativeToolWidget,
  VOLG: QuantitativeToolWidget,
  CZF: QuantitativeToolWidget,
  CVRC: QuantitativeToolWidget,
  PSR: QuantitativeToolWidget,
  LVM: QuantitativeToolWidget,
  MVS: QuantitativeToolWidget,
  LIQ: QuantitativeToolWidget,
  HMM: QuantitativeToolWidget,
  TSIG: QuantitativeToolWidget,
  CORR: QuantitativeToolWidget,
  HMMD: QuantitativeToolWidget,
  ZSCR: QuantitativeToolWidget,
  OBHM: QuantitativeToolWidget,
  ENSD: QuantitativeToolWidget,
  FEAT: QuantitativeToolWidget,
  DDSH: QuantitativeToolWidget,
  EXEC: QuantitativeToolWidget,
  EXPO: QuantitativeToolWidget,
  OB3D: QuantitativeToolWidget,
  TVCN: QuantitativeToolWidget,
  CTENSOR: QuantitativeToolWidget,
  HELIX: QuantitativeToolWidget,
  HYPERCUBE: QuantitativeToolWidget,
  VORTEX: QuantitativeToolWidget,
  PLASMA: QuantitativeToolWidget,
  LATTICE: QuantitativeToolWidget,
  TICKCORE: QuantitativeToolWidget,
  GREEKS3D: QuantitativeToolWidget,
  REGNET: QuantitativeToolWidget,
  TAILCUBE: QuantitativeToolWidget,
};

interface Widget {
  id: string;
  type: string;
  component: any;
  props: any;
  width: number;
  height: number;
  x?: number;
  y?: number;
}

interface Props {
  orderBook?: { bids: any[]; asks: any[] };
  currentPrice?: number;
  chartData?: Candle[];
  symbol?: string;
}

const props = withDefaults(defineProps<Props>(), {
  orderBook: () => ({ bids: [], asks: [] }),
  currentPrice: 0,
  chartData: () => [],
  symbol: 'BTC/USDT',
});

const gridRef = ref<HTMLElement | null>(null);
const gridColumns = ref(12);

// Загружаем виджеты из localStorage или используем дефолтные
const loadWidgets = (): Widget[] => {
  const saved = localStorage.getItem('terminal-widgets');
  if (saved) {
    try {
      const savedWidgets = JSON.parse(saved);
      return savedWidgets
        .filter((w: any) => widgetComponents[w.type]) // Фильтруем только существующие компоненты
        .map((w: any) => {
          const component = widgetComponents[w.type];
          // Для инструментов количественного анализа передаем все метаданные
          if (component === QuantitativeToolWidget) {
            return {
              ...w,
              component,
              props: {
                type: w.type,
                title: w.title || w.type,
                description: w.description || '',
                icon: w.icon || 'ActivityIcon',
                iconBg: w.iconBg || 'bg-emerald-500/20',
                iconColor: w.iconColor || 'text-emerald-400',
                code: w.code || w.type,
                selectedAsset: '',
              },
            };
          }
          // Для обычных виджетов используем стандартные props
          return {
            ...w,
            component,
            props: getWidgetProps(w.type),
          };
        });
    } catch (e) {
      console.error('Failed to load widgets:', e);
    }
  }
  
  // Дефолтные виджеты
  return [
    {
      id: 'orderbook-1',
      type: 'OrderBook',
      component: OrderBookWidget,
      props: { bids: props.orderBook.bids, asks: props.orderBook.asks, currentPrice: props.currentPrice },
      width: 2,
      height: 4,
    },
    {
      id: 'chart-1',
      type: 'Chart',
      component: ChartWidgetWrapper,
      props: { data: props.chartData, symbol: props.symbol },
      width: 6,
      height: 4,
    },
    {
      id: 'news-1',
      type: 'News',
      component: NewsWidget,
      props: {},
      width: 4,
      height: 2,
    },
    {
      id: 'ai-1',
      type: 'AI',
      component: AIWidget,
      props: { data: props.chartData },
      width: 4,
      height: 2,
    },
    {
      id: 'footer-1',
      type: 'Footer',
      component: FooterWidget,
      props: {},
      width: 6,
      height: 1,
    },
  ];
};

const getWidgetProps = (type: string) => {
  switch (type) {
    case 'OrderBook':
      return { bids: props.orderBook.bids, asks: props.orderBook.asks, currentPrice: props.currentPrice };
    case 'Chart':
      return { data: props.chartData, symbol: props.symbol };
    case 'AI':
      return { data: props.chartData };
    default:
      return {};
  }
};

const widgets = ref<Widget[]>([]);

// Инициализируем виджеты после монтирования
onMounted(() => {
  widgets.value = loadWidgets();
  console.log('Loaded widgets:', widgets.value);
  console.log('Widget components:', widgetComponents);
  
  // Слушаем обновления виджетов из настроек
  window.addEventListener('widgets-updated', () => {
    widgets.value = loadWidgets();
    console.log('Widgets updated:', widgets.value);
  });
});

const saveWidgets = () => {
  localStorage.setItem('terminal-widgets', JSON.stringify(widgets.value));
};

const removeWidget = (id: string) => {
  widgets.value = widgets.value.filter(w => w.id !== id);
  saveWidgets();
};

let saveTimeout: ReturnType<typeof setTimeout> | null = null;

const resizeWidget = (id: string, width: number, height: number) => {
  const widget = widgets.value.find(w => w.id === id);
  if (widget) {
    // Плавное обновление размеров
    widget.width = width;
    widget.height = height;
    // Сохраняем с небольшой задержкой для плавности
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }
    saveTimeout = setTimeout(() => {
      saveWidgets();
    }, 300);
  }
};

const editWidget = (id: string) => {
  // Открыть настройки виджета
  console.log('Edit widget:', id);
};

watch(() => props.orderBook, () => {
  widgets.value.forEach(widget => {
    if (widget.type === 'OrderBook') {
      widget.props = { ...widget.props, bids: props.orderBook.bids, asks: props.orderBook.asks, currentPrice: props.currentPrice };
    }
  });
}, { deep: true });

watch(() => props.chartData, () => {
  widgets.value.forEach(widget => {
    if (widget.type === 'Chart') {
      widget.props = { ...widget.props, data: props.chartData, symbol: props.symbol };
    } else if (widget.type === 'AI') {
      widget.props = { ...widget.props, data: props.chartData };
    }
  });
}, { deep: true });

</script>

<style scoped>
.dashboard-grid {
  display: grid;
  gap: 1rem;
  grid-auto-rows: minmax(100px, auto);
}

/* Плавная анимация изменения размера виджетов */
.dashboard-grid > * {
  transition: 
    grid-column 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    grid-row 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    opacity 0.3s ease-out;
  will-change: grid-column, grid-row, transform;
}

.dashboard-grid > *:hover {
  transition-duration: 0.2s;
}
</style>
