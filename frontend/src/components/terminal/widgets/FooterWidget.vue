<template>
  <BaseWidget
    title="Ордера и позиции"
    icon="ListIcon"
    icon-bg="bg-orange-500/20"
    icon-color="text-orange-400"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <FooterPanel />
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseWidget from './BaseWidget.vue';
import FooterPanel from '../FooterPanel.vue';

interface Props {
  width?: number;
  height?: number;
  resizable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  width: 3,
  height: 1,
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

const ListIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>' };
</script>
