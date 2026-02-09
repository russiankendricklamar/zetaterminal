<template>
  <div
    class="widget-container"
    :class="{ 'is-resizing': isResizing }"
  >
    <!-- Widget Header -->
    <div class="widget-header">
      <div class="widget-title-area">
        <div class="widget-icon" :class="iconBg">
          <component :is="icon" class="w-3.5 h-3.5" :class="iconColor" />
        </div>
        <h3 class="widget-title font-oswald">{{ title }}</h3>
      </div>
      <div v-if="showControls" class="widget-controls">
        <button
          @click.stop="$emit('settings')"
          class="widget-btn"
          title="Настройки"
        >
          <SettingsIcon class="w-3.5 h-3.5" />
        </button>
        <button
          @click.stop="$emit('remove')"
          class="widget-btn widget-btn-danger"
          title="Удалить виджет"
        >
          <XIcon class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- Widget Content -->
    <div class="widget-content custom-scrollbar">
      <slot />
    </div>

    <!-- Resize Handles -->
    <div v-if="resizable" class="resize-handles">
      <div
        class="resize-handle resize-handle-right"
        @mousedown.stop="(e) => startResize(e, 'width')"
        title="Изменить ширину"
      ></div>
      <div
        class="resize-handle resize-handle-bottom"
        @mousedown.stop="(e) => startResize(e, 'height')"
        title="Изменить высоту"
      ></div>
      <div
        class="resize-handle resize-handle-corner"
        @mousedown.stop="(e) => startResize(e, 'both')"
        title="Изменить размер"
      >
        <div class="resize-corner-indicator"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

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
  iconBg: 'icon-bg-red',
  iconColor: 'text-red-500',
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

    if (throttleTimeout) return;

    throttleTimeout = window.setTimeout(() => {
      throttleTimeout = null;
    }, 16);

    if (rafId) cancelAnimationFrame(rafId);

    rafId = requestAnimationFrame(() => {
      const deltaX = e.clientX - startX.value;
      const deltaY = e.clientY - startY.value;
      const gridSize = 50;

      let newWidth = startWidth.value;
      let newHeight = startHeight.value;

      if (resizeMode.value === 'width' || resizeMode.value === 'both') {
        newWidth = Math.max(1, Math.round(startWidth.value + deltaX / gridSize));
      }

      if (resizeMode.value === 'height' || resizeMode.value === 'both') {
        newHeight = Math.max(1, Math.round(startHeight.value + deltaY / gridSize));
      }

      if (newWidth !== lastWidth || newHeight !== lastHeight) {
        lastWidth = newWidth;
        lastHeight = newHeight;
        emit('resize', newWidth, newHeight);
      }
    });
  };

  const handleMouseUp = () => {
    if (rafId) cancelAnimationFrame(rafId);
    if (throttleTimeout) clearTimeout(throttleTimeout);
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

<style scoped>
/* ============================================
   WIDGET CONTAINER - BRUTALIST
   ============================================ */
.widget-container {
  background: #0a0a0a;
  border: 1px solid #1a1a1a;
  overflow: hidden;
  position: relative;
  transition: border-color 0.2s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.widget-container:hover {
  border-color: #262626;
}

.widget-container.is-resizing {
  border-color: #DC2626;
}

/* ============================================
   WIDGET HEADER
   ============================================ */
.widget-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #1a1a1a;
  background: #050505;
  flex-shrink: 0;
}

.widget-title-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.widget-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-bg-red {
  background: rgba(220, 38, 38, 0.15);
  border: 1px solid rgba(220, 38, 38, 0.3);
}

.icon-bg-green {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.icon-bg-blue {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.icon-bg-purple {
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.icon-bg-orange {
  background: rgba(249, 115, 22, 0.15);
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.icon-bg-cyan {
  background: rgba(34, 211, 238, 0.15);
  border: 1px solid rgba(34, 211, 238, 0.3);
}

.widget-title {
  font-size: 12px;
  font-weight: 500;
  color: #f5f5f5;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 0;
}

/* ============================================
   WIDGET CONTROLS
   ============================================ */
.widget-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.widget-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid #262626;
  color: #525252;
  cursor: pointer;
  transition: all 0.2s;
}

.widget-btn:hover {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.widget-btn-danger {
  border-color: rgba(220, 38, 38, 0.3);
  color: #DC2626;
}

.widget-btn-danger:hover {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

/* ============================================
   WIDGET CONTENT
   ============================================ */
.widget-content {
  flex: 1;
  overflow: auto;
  min-height: 0;
}

/* ============================================
   RESIZE HANDLES
   ============================================ */
.resize-handles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  pointer-events: auto;
  transition: background 0.2s;
}

.resize-handle-right {
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  cursor: ew-resize;
}

.resize-handle-bottom {
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  cursor: ns-resize;
}

.resize-handle-corner {
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: nwse-resize;
}

.resize-handle:hover {
  background: rgba(220, 38, 38, 0.3);
}

.resize-corner-indicator {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 8px;
  height: 8px;
  border-right: 2px solid #DC2626;
  border-bottom: 2px solid #DC2626;
  opacity: 0.5;
}

.resize-handle-corner:hover .resize-corner-indicator {
  opacity: 1;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .widget-header {
    padding: 10px 12px;
  }

  .widget-btn {
    min-width: 44px;
    min-height: 44px;
  }

  .resize-handle {
    display: none;
  }
}

@media (max-width: 480px) {
  .widget-header {
    padding: 8px 10px;
  }

  .widget-title {
    font-size: 10px;
  }

  .widget-icon {
    width: 24px;
    height: 24px;
  }
}
</style>
