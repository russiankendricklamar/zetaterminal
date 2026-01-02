<!-- src/components/common/TaskWidget.vue -->
<template>
  <Transition name="island-pop">
    <div v-if="activeTask" class="dynamic-island" @click="toggleDetails">
      
      <!-- Activity Indicator (Left) -->
      <div class="island-left">
        <div class="spinner-island"></div>
      </div>

      <!-- Content (Center) -->
      <div class="island-content">
        <span class="island-title">{{ activeTask.title }}</span>
      </div>

      <!-- Percentage (Right) -->
      <div class="island-right">
        <span class="island-pct">{{ Math.round(activeTask.progress) }}%</span>
      </div>

      <!-- Background Progress Fill (Subtle) -->
      <div class="island-progress-bg" :style="{ width: activeTask.progress + '%' }"></div>

    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTaskStore } from '@/stores/tasks'

const taskStore = useTaskStore()
const showDetails = ref(false)

const activeTask = computed(() => {
  const running = taskStore.tasks.filter(t => t.status === 'running' || t.status === 'pending')
  return running.length > 0 ? running[running.length - 1] : null
})

const toggleDetails = () => {
  if (taskStore.tasks.length > 1) showDetails.value = !showDetails.value
}
</script>

<style scoped>
.dynamic-island {
  /* Positioning & Size */
  width: auto;
  min-width: 200px;
  max-width: 320px;
  height: 36px;
  
  /* Appearance */
  background: #000000; /* Глубокий черный */
  border-radius: 999px; /* Pill shape */
  border: 1px solid rgba(255, 255, 255, 0.15); /* Тонкая обводка */
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.5),
    0 10px 30px -5px rgba(0, 0, 0, 0.8),
    inset 0 1px 0 rgba(255, 255, 255, 0.1); /* Inner lighting */
    
  /* Layout */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px;
  gap: 12px;
  
  cursor: pointer;
  position: relative;
  overflow: hidden;
  user-select: none;
}

/* --- Content Elements --- */

.island-left {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
  margin-left: 2px;
  z-index: 2;
}

.island-content {
  flex: 1;
  text-align: center;
  overflow: hidden;
  z-index: 2;
}

.island-title {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.island-right {
  margin-right: 12px;
  font-size: 11px;
  font-family: monospace;
  color: #fbbf24; /* Amber/Gold color for numbers */
  font-weight: 700;
  z-index: 2;
}

/* --- Progress Bar (Inside) --- */
.island-progress-bg {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  background: rgba(59, 130, 246, 0.2); /* Синяя заливка, но прозрачная */
  z-index: 1;
  transition: width 0.3s ease;
}

/* --- Spinner --- */
.spinner-island {
  width: 14px; height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- Pop Animation (Elastic) --- */
.island-pop-enter-active {
  animation: pop-in 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.island-pop-leave-active {
  animation: pop-in 0.3s cubic-bezier(0.6, -0.28, 0.735, 0.045) reverse;
}

@keyframes pop-in {
  0% { transform: scale(0.8) translateY(-20px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}
</style>