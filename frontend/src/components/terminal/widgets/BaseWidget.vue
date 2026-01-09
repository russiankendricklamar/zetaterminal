<template>
  <div 
    :class="`glass-panel rounded-2xl overflow-hidden shadow-2xl shadow-black/20 relative ${isResizing ? 'ring-2 ring-indigo-500/50' : ''}`"
    :style="{
      transition: isResizing 
        ? 'box-shadow 0.2s ease-out, border-color 0.2s ease-out' 
        : 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      transform: isResizing ? 'scale(1.005)' : 'scale(1)',
    }"
  >
    <!-- Widget Header -->
    <div class="flex items-center justify-between p-3 border-b border-white/5 bg-black/20 relative z-10">
      <div class="flex items-center gap-2">
        <div :class="`p-1.5 rounded-lg ${iconBg}`">
          <component :is="icon" class="w-3.5 h-3.5" :class="iconColor" />
        </div>
        <h3 class="text-xs font-bold text-white">{{ title }}</h3>
      </div>
      <div v-if="showControls" class="flex items-center gap-1.5">
        <button 
          @click.stop="$emit('settings')"
          class="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-all hover:scale-105 active:scale-95"
          title="Настройки"
        >
          <SettingsIcon class="w-3.5 h-3.5" />
        </button>
        <button 
          @click.stop="$emit('remove')"
          class="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 hover:text-rose-300 border border-rose-500/20 hover:border-rose-500/40 transition-all hover:scale-110 active:scale-95"
          title="Удалить виджет"
        >
          <XIcon class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- Widget Content -->
    <div class="h-[calc(100%-48px)] overflow-auto custom-scrollbar">
      <slot />
    </div>

    <!-- Resize Handles -->
    <div v-if="resizable" class="absolute inset-0 pointer-events-none">
      <!-- Right edge - resize width -->
      <div 
        class="absolute top-0 right-0 w-1 h-full cursor-ew-resize hover:bg-indigo-500/30 transition-colors pointer-events-auto"
        @mousedown.stop="(e) => startResize(e, 'width')"
        title="Изменить ширину"
      ></div>
      <!-- Bottom edge - resize height -->
      <div 
        class="absolute bottom-0 left-0 w-full h-1 cursor-ns-resize hover:bg-indigo-500/30 transition-colors pointer-events-auto"
        @mousedown.stop="(e) => startResize(e, 'height')"
        title="Изменить высоту"
      ></div>
      <!-- Corner - resize both -->
      <div 
        class="absolute bottom-0 right-0 w-6 h-6 cursor-nwse-resize opacity-60 hover:opacity-100 transition-opacity pointer-events-auto group"
        @mousedown.stop="(e) => startResize(e, 'both')"
        title="Изменить размер"
      >
        <div class="absolute bottom-1 right-1 w-4 h-4 border-r-2 border-b-2 border-indigo-400/50 group-hover:border-indigo-400 rounded-br-lg"></div>
        <div class="absolute bottom-0.5 right-0.5 w-2 h-2 border-r border-b border-indigo-300/70 group-hover:border-indigo-300 rounded-br-sm"></div>
      </div>
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
  showControls?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  iconBg: 'bg-indigo-500/20',
  iconColor: 'text-indigo-400',
  width: 1,
  height: 1,
  resizable: true,
  showControls: true,
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
const resizeMode = ref<'width' | 'height' | 'both'>('both');

// Grid styles are applied by parent

const startResize = (e: MouseEvent, mode: 'width' | 'height' | 'both' = 'both') => {
  e.preventDefault();
  e.stopPropagation();
  
  isResizing.value = true;
  resizeMode.value = mode;
  startX.value = e.clientX;
  startY.value = e.clientY;
  startWidth.value = props.width;
  startHeight.value = props.height;

  let rafId: number | null = null;
  let lastWidth = startWidth.value;
  let lastHeight = startHeight.value;
  let throttleTimeout: number | null = null;

  const handleMouseMove = (e: MouseEvent) => {
    e.preventDefault();
    
    // Throttle для более плавного изменения
    if (throttleTimeout) {
      return;
    }
    
    throttleTimeout = window.setTimeout(() => {
      throttleTimeout = null;
    }, 16); // ~60fps

    if (rafId) {
      cancelAnimationFrame(rafId);
    }

    rafId = requestAnimationFrame(() => {
      const deltaX = e.clientX - startX.value;
      const deltaY = e.clientY - startY.value;
      
      // Более мелкий шаг для плавного изменения (примерно 1 ячейка = 50px)
      const gridSize = 50;
      
      let newWidth = startWidth.value;
      let newHeight = startHeight.value;
      
      if (resizeMode.value === 'width' || resizeMode.value === 'both') {
        newWidth = Math.max(1, Math.round(startWidth.value + deltaX / gridSize));
      }
      
      if (resizeMode.value === 'height' || resizeMode.value === 'both') {
        newHeight = Math.max(1, Math.round(startHeight.value + deltaY / gridSize));
      }
      
      // Эмитим только если значение изменилось
      if (newWidth !== lastWidth || newHeight !== lastHeight) {
        lastWidth = newWidth;
        lastHeight = newHeight;
        emit('resize', newWidth, newHeight);
      }
    });
  };

  const handleMouseUp = () => {
    if (rafId) {
      cancelAnimationFrame(rafId);
    }
    if (throttleTimeout) {
      clearTimeout(throttleTimeout);
    }
    isResizing.value = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  document.addEventListener('mousemove', handleMouseMove, { passive: false });
  document.addEventListener('mouseup', handleMouseUp, { once: true });
};

const SettingsIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"/></svg>' };
const XIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>' };
</script>
