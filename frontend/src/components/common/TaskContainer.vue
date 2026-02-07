<!-- src/components/common/TaskContainer.vue -->
<template>
  <div class="task-container">
    <TransitionGroup name="task-slide">
      <div 
        v-for="task in taskStore.tasks" 
        :key="task.id" 
        class="task-card"
        :class="task.status"
      >
        <div class="task-header">
          <span class="task-icon">
            <span v-if="task.status === 'running'" class="spinner">⟳</span>
            <span v-else-if="task.status === 'completed'">✓</span>
            <span v-else-if="task.status === 'error'">✕</span>
          </span>
          <span class="task-title">{{ task.title }}</span>
          <span class="task-pct">{{ Math.round(task.progress) }}%</span>
        </div>
        
        <!-- Progress Bar Track -->
        <div class="progress-track">
          <div 
            class="progress-fill" 
            :style="{ width: task.progress + '%' }"
            :class="task.status"
          ></div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useTaskStore } from '@/stores/tasks'
const taskStore = useTaskStore()
</script>

<style scoped>
.task-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none; /* Чтобы клики проходили сквозь контейнер */
}

.task-card {
  width: 320px;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(12px);
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  pointer-events: auto; /* Сами карточки кликабельны */
  border-left: 3px solid #3b82f6; /* Blue default */
}

.task-card.completed { border-left-color: #4ade80; }
.task-card.error { border-left-color: #ef4444; }

.task-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px; font-size: 13px; color: #fff; font-weight: 500;
}
.task-icon { margin-right: 8px; width: 16px; text-align: center; }
.task-title { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 12px; }
.task-pct { font-family: monospace; color: rgba(255,255,255,0.6); font-size: 11px; }

/* Progress Bar */
.progress-track {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}
.progress-fill.completed { background: #4ade80; }
.progress-fill.error { background: #ef4444; }

/* Animations */
.task-slide-enter-active, .task-slide-leave-active { transition: all 0.3s ease; }
.task-slide-enter-from { opacity: 0; transform: translateX(20px); }
.task-slide-leave-to { opacity: 0; transform: translateX(20px); }

/* Spinner */
.spinner { display: inline-block; animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* Mobile Responsive */
@media (max-width: 768px) {
  .task-container {
    bottom: 16px;
    right: 16px;
    left: 16px;
    gap: 8px;
    /* Safe area for devices with home indicator */
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .task-card {
    width: 100%;
    max-width: none;
    padding: 10px 14px;
    border-radius: 10px;
  }

  .task-header {
    font-size: 12px;
    margin-bottom: 6px;
  }

  .task-pct {
    font-size: 10px;
  }

  .progress-track {
    height: 3px;
  }
}

@media (max-width: 480px) {
  .task-container {
    bottom: 12px;
    right: 12px;
    left: 12px;
    gap: 6px;
  }

  .task-card {
    padding: 8px 12px;
    border-radius: 8px;
    border-left-width: 2px;
  }

  .task-header {
    font-size: 11px;
    margin-bottom: 5px;
  }

  .task-title {
    margin-right: 8px;
  }

  .task-pct {
    font-size: 9px;
  }
}

@media (max-width: 375px) {
  .task-container {
    bottom: 10px;
    right: 10px;
    left: 10px;
  }

  .task-card {
    padding: 6px 10px;
  }

  .task-header {
    font-size: 10px;
    margin-bottom: 4px;
  }

  .task-icon {
    width: 14px;
    margin-right: 6px;
  }
}
</style>
