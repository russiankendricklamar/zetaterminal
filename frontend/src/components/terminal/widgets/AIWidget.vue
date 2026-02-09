<template>
  <BaseWidget
    title="ИИ АНАЛИТИК"
    icon="BrainIcon"
    icon-bg="icon-bg-purple"
    icon-color="text-purple-500"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <AIPanel :data="data" />
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseWidget from './BaseWidget.vue';
import AIPanel from '../AIPanel.vue';
import { Candle } from '@/types/terminal';

interface Props {
  data: Candle[];
  width?: number;
  height?: number;
  resizable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: 2,
  height: 2,
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

const BrainIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.54ZM14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.54Z"/></svg>' };
</script>
