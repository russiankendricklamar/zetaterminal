<template>
  <BaseWidget
    title="Аналитика"
    icon="BarChartIcon"
    icon-bg="bg-cyan-500/20"
    icon-color="text-cyan-400"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <div class="p-4 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-400 uppercase mb-1">Настроение</div>
          <div class="text-xl font-bold text-emerald-400">Бычье</div>
        </div>
        <div class="p-3 rounded-xl bg-white/5 border border-white/5 text-center">
          <div class="text-xs text-gray-400 uppercase mb-1">Уверенность</div>
          <div class="text-xl font-bold text-white">87%</div>
        </div>
      </div>
      <div class="p-3 rounded-xl bg-white/5 border border-white/5">
        <div class="text-xs text-gray-400 uppercase mb-2">Волатильность</div>
        <div class="text-lg font-bold text-white">Высокая</div>
      </div>
    </div>
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseWidget from './BaseWidget.vue';

interface Props {
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

const BarChartIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>' };
</script>
