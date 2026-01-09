<template>
  <BaseWidget
    title="График цены"
    icon="LineChartIcon"
    icon-bg="bg-emerald-500/20"
    icon-color="text-emerald-400"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <ChartWidget 
      :data="data" 
      :isExpanded="false"
      :symbol="symbol"
    />
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseWidget from './BaseWidget.vue';
import ChartWidget from '../ChartWidget.vue';
import { Candle } from '@/types/terminal';

interface Props {
  data: Candle[];
  symbol: string;
  width?: number;
  height?: number;
  resizable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: 3,
  height: 3,
  resizable: true,
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

const LineChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
</script>
