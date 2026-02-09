<template>
  <BaseWidget
    title="НОВОСТИ"
    icon="NewspaperIcon"
    icon-bg="icon-bg-purple"
    icon-color="text-purple-500"
    :width="width"
    :height="height"
    :resizable="resizable"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <div class="news-list">
      <div
        v-for="item in news.slice(0, 5)"
        :key="item.id"
        class="news-item"
      >
        <div class="news-meta">
          <span :class="['news-badge font-mono', { 'news-badge-critical': item.importance === 'Critical' }]">
            {{ getImportanceName(item.importance) }}
          </span>
          <span class="news-source font-mono">{{ item.source }}</span>
          <span class="news-time font-mono">{{ item.time }}</span>
        </div>
        <h4 class="news-title font-oswald">{{ item.title }}</h4>
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
/* ============================================
   NEWS WIDGET - BRUTALIST
   ============================================ */
.news-list {
  padding: 12px;
}

.news-item {
  padding: 12px;
  background: #050505;
  border: 1px solid #1a1a1a;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.news-item:last-child {
  margin-bottom: 0;
}

.news-item:hover {
  border-color: #DC2626;
  background: #0a0a0a;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.news-badge {
  font-size: 9px;
  font-weight: 600;
  padding: 2px 6px;
  background: #1a1a1a;
  border: 1px solid #262626;
  color: #737373;
  letter-spacing: 0.05em;
}

.news-badge-critical {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.news-source {
  font-size: 10px;
  color: #525252;
}

.news-time {
  font-size: 10px;
  color: #3f3f3f;
  margin-left: auto;
}

.news-title {
  font-size: 13px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.02em;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .news-list {
    padding: 8px;
  }

  .news-item {
    padding: 10px;
    margin-bottom: 6px;
  }
}

@media (max-width: 480px) {
  .news-list {
    padding: 6px;
  }

  .news-item {
    padding: 8px;
    margin-bottom: 4px;
  }

  .news-source {
    display: none;
  }

  .news-title {
    font-size: 12px;
    -webkit-line-clamp: 3;
  }
}

@media (max-width: 375px) {
  .news-item {
    padding: 6px;
  }

  .news-title {
    font-size: 11px;
  }

  .news-badge {
    font-size: 8px;
  }
}
</style>
