<template>
  <BaseWidget
    title="СТАКАН"
    icon="BookIcon"
    icon-bg="icon-bg-blue"
    icon-color="text-blue-500"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <OrderBook :bids="bids" :asks="asks" :currentPrice="currentPrice" />
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseWidget from './BaseWidget.vue';
import OrderBook from '../OrderBook.vue';

interface Props {
  bids: any[];
  asks: any[];
  currentPrice: number;
  width?: number;
  height?: number;
  resizable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: 1,
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

const BookIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>' };
</script>
