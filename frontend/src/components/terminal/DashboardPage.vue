<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h2 class="dashboard-title font-oswald">ГЛАВНАЯ ПАНЕЛЬ</h2>
        <p class="dashboard-subtitle font-mono">Настраиваемая рабочая область</p>
      </div>
    </div>

    <!-- Dashboard Grid -->
    <div
      ref="gridRef"
      class="dashboard-grid-wrapper custom-scrollbar"
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
      <div v-else class="dashboard-empty">
        <div class="empty-content">
          <p class="empty-title font-oswald">НЕТ ВИДЖЕТОВ</p>
          <p class="empty-subtitle font-mono">Загрузка виджетов...</p>
          <p class="empty-count font-mono">Количество виджетов: {{ widgets.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useIsMobile } from '@/composables/useIsMobile';

const { isMobile, isSmallMobile, isTablet } = useIsMobile();
import OrderBookWidget from './widgets/OrderBookWidget.vue';
import ChartWidgetWrapper from './widgets/ChartWidgetWrapper.vue';
import NewsWidget from './widgets/NewsWidget.vue';
import AIWidget from './widgets/AIWidget.vue';
import FooterWidget from './widgets/FooterWidget.vue';
import MarketsWidget from './widgets/MarketsWidget.vue';
import AnalyticsWidget from './widgets/AnalyticsWidget.vue';
import QuantitativeToolWidget from './widgets/QuantitativeToolWidget.vue';
import WaveSigmaWidget from './widgets/WaveSigmaWidget.vue';
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
  WSIGMA: WaveSigmaWidget,
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

// Responsive grid columns based on screen size
const gridColumns = computed(() => {
  if (isSmallMobile.value) return 1;
  if (isMobile.value) return 2;
  if (isTablet.value) return 6;
  return 12;
});

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
/* ============================================
   DASHBOARD CONTAINER - BRUTALIST
   ============================================ */
.dashboard-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  overflow: hidden;
}

/* ============================================
   DASHBOARD HEADER
   ============================================ */
.dashboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #1a1a1a;
  background: #050505;
  flex-shrink: 0;
}

.dashboard-title {
  font-size: 16px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.1em;
  margin: 0;
}

.dashboard-subtitle {
  font-size: 11px;
  color: #525252;
  margin-top: 4px;
}

/* ============================================
   DASHBOARD GRID
   ============================================ */
.dashboard-grid-wrapper {
  flex: 1;
  padding: 16px;
  overflow: auto;
  position: relative;
}

.dashboard-grid {
  display: grid;
  gap: 16px;
  grid-auto-rows: minmax(100px, auto);
}

.dashboard-grid > * {
  transition:
    grid-column 0.3s ease,
    grid-row 0.3s ease,
    transform 0.2s ease;
}

/* ============================================
   EMPTY STATE
   ============================================ */
.dashboard-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-content {
  text-align: center;
}

.empty-title {
  font-size: 18px;
  color: #f5f5f5;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.empty-subtitle {
  font-size: 12px;
  color: #525252;
}

.empty-count {
  font-size: 10px;
  color: #3f3f3f;
  margin-top: 8px;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .dashboard-grid-wrapper {
    padding: 12px;
  }

  .dashboard-grid {
    gap: 12px;
    grid-auto-rows: minmax(80px, auto);
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: 12px 16px;
  }

  .dashboard-grid-wrapper {
    padding: 8px;
  }

  .dashboard-grid {
    gap: 8px;
    grid-auto-rows: minmax(120px, auto);
  }

  .widget-container {
    grid-column: span 2 !important;
    min-height: 150px !important;
  }
}

@media (max-width: 480px) {
  .dashboard-header {
    padding: 10px 12px;
  }

  .dashboard-title {
    font-size: 14px;
  }

  .dashboard-grid {
    gap: 6px;
    grid-auto-rows: minmax(100px, auto);
  }

  .widget-container {
    grid-column: span 1 !important;
    grid-row: span 1 !important;
    min-height: 180px !important;
  }
}

@media (max-width: 375px) {
  .dashboard-grid {
    gap: 4px;
  }

  .widget-container {
    min-height: 160px !important;
  }
}
</style>
