<template>
  <BaseWidget
    title="Новости"
    icon="NewspaperIcon"
    icon-bg="bg-purple-500/20"
    icon-color="text-purple-400"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <div class="p-4 space-y-3">
      <div 
        v-for="item in news.slice(0, 5)" 
        :key="item.id"
        class="p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors cursor-pointer"
      >
        <div class="flex items-center gap-2 mb-2">
          <span :class="`text-[10px] font-bold px-2 py-0.5 rounded ${item.importance === 'Critical' ? 'bg-rose-500 text-white' : 'bg-gray-700 text-gray-300'}`">
            {{ getImportanceName(item.importance) }}
          </span>
          <span class="text-[10px] text-gray-500 font-mono">{{ item.source }}</span>
          <span class="text-[10px] text-gray-500 ml-auto">{{ item.time }}</span>
        </div>
        <h4 class="text-sm font-bold text-white leading-snug line-clamp-2">{{ item.title }}</h4>
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

const news = [
  { id: 1, title: "Bitcoin достиг исторического максимума на фоне институционального ажиотажа", source: "Bloomberg", time: "2 мин назад", importance: "High" },
  { id: 2, title: "Федеральная резервная система назначила экстренное заседание на понедельник", source: "Reuters", time: "15 мин назад", importance: "Critical" },
  { id: 3, title: "NVIDIA анонсировала революционный AI-чип 'Rubin'", source: "TechCrunch", time: "42 мин назад", importance: "High" },
  { id: 4, title: "Цены на нефть снижаются по мере небольшого ослабления напряжённости на Ближнем Востоке", source: "CNBC", time: "1 ч назад", importance: "Medium" },
  { id: 5, title: "Apple сообщила о рекордной выручке от услуг в Q3", source: "MarketWatch", time: "2 ч назад", importance: "Medium" },
];

const getImportanceName = (importance: string) => {
  const names: Record<string, string> = {
    'Critical': 'КРИТИЧНО',
    'High': 'ВЫСОКАЯ',
    'Medium': 'СРЕДНЯЯ',
  };
  return names[importance] || importance.toUpperCase();
};

const NewspaperIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/></svg>' };
</script>

<style scoped>
/* Mobile Responsive Styles */
@media (max-width: 768px) {
  .p-4 {
    padding: 0.75rem;
  }

  .p-3 {
    padding: 0.625rem;
  }

  .space-y-3 > * + * {
    margin-top: 0.5rem;
  }

  .text-sm {
    font-size: 0.8125rem;
  }
}

@media (max-width: 480px) {
  .p-4 {
    padding: 0.5rem;
  }

  .p-3 {
    padding: 0.5rem;
  }

  .space-y-3 > * + * {
    margin-top: 0.375rem;
  }

  /* Hide source on small screens */
  .text-\[10px\].text-gray-500.font-mono {
    display: none;
  }

  .text-sm {
    font-size: 0.75rem;
  }

  .line-clamp-2 {
    -webkit-line-clamp: 3;
  }
}

@media (max-width: 375px) {
  .p-4 {
    padding: 0.375rem;
  }

  .p-3 {
    padding: 0.375rem;
  }

  .text-sm {
    font-size: 0.6875rem;
  }

  .text-\[10px\] {
    font-size: 8px;
  }
}
</style>
