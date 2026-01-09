<template>
  <BaseWidget
    :title="title"
    :icon="icon"
    :icon-bg="iconBg"
    :icon-color="iconColor"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <div class="p-4 flex flex-col items-center justify-center h-full">
      <component :is="iconComponent" :class="`w-16 h-16 ${iconColor} opacity-50 mb-4`" />
      <h4 class="text-lg font-bold text-white mb-2 text-center">{{ title }}</h4>
      <p class="text-sm text-gray-400 text-center mb-4">{{ description }}</p>
      <div class="px-3 py-1 rounded-lg bg-white/5 border border-white/10">
        <span class="text-xs font-mono text-gray-400">Код: {{ code }}</span>
      </div>
      <div v-if="selectedAsset" class="mt-4 px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
        <span class="text-xs text-emerald-400">Актив: {{ selectedAsset }}</span>
      </div>
      <div v-else class="mt-4 text-xs text-gray-500 text-center">
        Выберите актив для анализа
      </div>
    </div>
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import BaseWidget from './BaseWidget.vue';

interface Props {
  type: string;
  title?: string;
  description?: string;
  icon?: string;
  iconBg?: string;
  iconColor?: string;
  code?: string;
  width?: number;
  height?: number;
  resizable?: boolean;
  selectedAsset?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Инструмент',
  description: 'Инструмент количественного анализа',
  icon: 'ActivityIcon',
  iconBg: 'bg-emerald-500/20',
  iconColor: 'text-emerald-400',
  code: '',
  width: 3,
  height: 3,
  resizable: true,
  selectedAsset: '',
});

const emit = defineEmits<{
  settings: [];
  remove: [];
  resize: [width: number, height: number];
}>();

const width = ref(props.width);
const height = ref(props.height);

const handleResize = (w: number, h: number) => {
  width.value = w;
  height.value = h;
  emit('resize', w, h);
};

// Иконки для инструментов
const ActivityIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>' };
const LayersIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>' };
const TargetIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>' };
const BarChart2Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' };
const PieChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>' };
const ChartBarIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>' };
const TableCellsIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v18H3z"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/></svg>' };
const ShareIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const Squares2X2Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' };
const Bars3Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>' };
const BarChart3Icon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/><line x1="3" y1="20" x2="21" y2="20"/></svg>' };
const ScatterIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="7" cy="7" r="2"/><circle cx="17" cy="7" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const LineChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 3 7 9 12 5 15 9 21 3"/><polyline points="3 21 7 15 12 19 15 15 21 21"/></svg>' };

const iconMap: Record<string, any> = {
  ActivityIcon,
  LayersIcon,
  TargetIcon,
  BarChart2Icon,
  PieChartIcon,
  ChartBarIcon,
  TableCellsIcon,
  ShareIcon,
  TrendingDownIcon,
  Squares2X2Icon,
  Bars3Icon,
  BarChart3Icon,
  ScatterIcon,
  TrendingUpIcon,
  LineChartIcon,
};

const iconComponent = computed(() => {
  return iconMap[props.icon] || ActivityIcon;
});
</script>
