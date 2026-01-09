<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 flex flex-col animate-fade-in h-full">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-white/5 bg-black/20">
      <div>
        <h2 class="text-xl font-bold text-white tracking-tight">Главная панель</h2>
        <p class="text-xs text-gray-400">Настраиваемая рабочая область</p>
      </div>
      <button 
        @click="isEditMode = !isEditMode"
        :class="`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
          isEditMode 
            ? 'bg-indigo-500 text-white' 
            : 'bg-white/10 text-gray-300 hover:text-white'
        }`"
      >
        {{ isEditMode ? 'Сохранить' : 'Редактировать' }}
      </button>
    </div>

    <!-- Dashboard Grid -->
    <div 
      ref="gridRef"
      class="flex-1 p-4 overflow-auto custom-scrollbar"
      :class="{ 'cursor-move': isEditMode }"
    >
      <div 
        class="dashboard-grid"
        :style="{ gridTemplateColumns: `repeat(${gridColumns}, 1fr)` }"
      >
        <component
          v-for="widget in widgets"
          :key="widget.id"
          :is="widget.component"
          v-bind="widget.props"
          :width="widget.width"
          :height="widget.height"
          :resizable="isEditMode"
          @remove="removeWidget(widget.id)"
          @resize="(w, h) => resizeWidget(widget.id, w, h)"
          @settings="editWidget(widget.id)"
          :style="{ gridColumn: `span ${widget.width}`, gridRow: `span ${widget.height}` }"
        />
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
import { Candle } from '@/types/terminal';

const widgetComponents: Record<string, any> = {
  OrderBook: OrderBookWidget,
  Chart: ChartWidgetWrapper,
  News: NewsWidget,
  AI: AIWidget,
  Footer: FooterWidget,
  Markets: MarketsWidget,
  Analytics: AnalyticsWidget,
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

const isEditMode = ref(false);
const gridRef = ref<HTMLElement | null>(null);
const gridColumns = ref(12);
const draggedWidgetId = ref<string | null>(null);

// Загружаем виджеты из localStorage или используем дефолтные
const loadWidgets = (): Widget[] => {
  const saved = localStorage.getItem('terminal-widgets');
  if (saved) {
    try {
      const savedWidgets = JSON.parse(saved);
      return savedWidgets.map((w: any) => ({
        ...w,
        component: widgetComponents[w.type],
        props: getWidgetProps(w.type),
      }));
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

const widgets = ref<Widget[]>(loadWidgets());

const saveWidgets = () => {
  localStorage.setItem('terminal-widgets', JSON.stringify(widgets.value));
};

const removeWidget = (id: string) => {
  widgets.value = widgets.value.filter(w => w.id !== id);
  saveWidgets();
};

const resizeWidget = (id: string, width: number, height: number) => {
  const widget = widgets.value.find(w => w.id === id);
  if (widget) {
    widget.width = width;
    widget.height = height;
    saveWidgets();
  }
};

const editWidget = (id: string) => {
  // Открыть настройки виджета
  console.log('Edit widget:', id);
};

const startDrag = (e: DragEvent, id: string) => {
  draggedWidgetId.value = id;
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move';
  }
};

const endDrag = () => {
  draggedWidgetId.value = null;
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

onMounted(() => {
  // Слушаем обновления виджетов из настроек
  window.addEventListener('widgets-updated', () => {
    widgets.value = loadWidgets();
  });
});
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  gap: 1rem;
  grid-auto-rows: minmax(100px, auto);
}
</style>
