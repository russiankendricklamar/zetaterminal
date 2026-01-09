<template>
  <div 
    :class="`glass-panel rounded-2xl overflow-hidden shadow-2xl shadow-black/20 relative ${isResizing ? 'ring-2 ring-indigo-500/50' : ''}`"
  >
    <!-- Widget Header -->
    <div class="flex items-center justify-between p-3 border-b border-white/5 bg-black/20">
      <div class="flex items-center gap-2">
        <div :class="`p-1.5 rounded-lg ${iconBg}`">
          <component :is="icon" class="w-3.5 h-3.5" :class="iconColor" />
        </div>
        <h3 class="text-xs font-bold text-white">{{ title }}</h3>
      </div>
      <div class="flex items-center gap-1">
        <button 
          @click="$emit('settings')"
          class="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
          title="Настройки"
        >
          <SettingsIcon class="w-3 h-3" />
        </button>
        <button 
          @click="$emit('remove')"
          class="p-1 rounded hover:bg-rose-500/20 text-gray-400 hover:text-rose-400 transition-colors"
          title="Удалить"
        >
          <XIcon class="w-3 h-3" />
        </button>
      </div>
    </div>

    <!-- Widget Content -->
    <div class="h-[calc(100%-48px)] overflow-auto custom-scrollbar">
      <slot />
    </div>

    <!-- Resize Handles -->
    <div 
      v-if="resizable"
      class="absolute bottom-0 right-0 w-4 h-4 cursor-nwse-resize opacity-0 hover:opacity-100 transition-opacity group"
      @mousedown.stop="startResize"
    >
      <div class="absolute bottom-1 right-1 w-3 h-3 border-r-2 border-b-2 border-white/30 group-hover:border-white/60 rounded-br-lg"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  title: string;
  icon: string;
  iconBg?: string;
  iconColor?: string;
  width?: number;
  height?: number;
  resizable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  iconBg: 'bg-indigo-500/20',
  iconColor: 'text-indigo-400',
  width: 1,
  height: 1,
  resizable: true,
});

const emit = defineEmits<{
  settings: [];
  remove: [];
  resize: [width: number, height: number];
}>();

const isResizing = ref(false);
const startX = ref(0);
const startY = ref(0);
const startWidth = ref(0);
const startHeight = ref(0);

// Grid styles are applied by parent

const startResize = (e: MouseEvent) => {
  isResizing.value = true;
  startX.value = e.clientX;
  startY.value = e.clientY;
  startWidth.value = props.width;
  startHeight.value = props.height;

  const handleMouseMove = (e: MouseEvent) => {
    const deltaX = e.clientX - startX.value;
    const deltaY = e.clientY - startY.value;
    const gridSize = 20; // размер одной ячейки grid
    
    const newWidth = Math.max(1, Math.round(startWidth.value + deltaX / gridSize));
    const newHeight = Math.max(1, Math.round(startHeight.value + deltaY / gridSize));
    
    emit('resize', newWidth, newHeight);
  };

  const handleMouseUp = () => {
    isResizing.value = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  document.addEventListener('mousemove', handleMouseMove);
  document.addEventListener('mouseup', handleMouseUp);
};

const SettingsIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"/></svg>' };
const XIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' };
</script>
