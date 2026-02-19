<template>
  <div class="optimization-page">
    <!-- Method Selector Tabs -->
    <div class="method-selector">
      <button
        v-for="method in methods"
        :key="method.key"
        :class="['method-tab', { active: activeMethod === method.key }]"
        @click="activeMethod = method.key"
      >
        <div :class="['method-icon', method.key]">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path :d="method.icon" />
          </svg>
        </div>
        <div class="method-info">
          <span class="method-title">{{ method.title }}</span>
          <span class="method-subtitle">{{ method.subtitle }}</span>
        </div>
      </button>
    </div>

    <!-- Active Method Component -->
    <component :is="activeComponent" @toast="showToast" />

    <!-- Toast -->
    <transition name="slide-up">
      <div
        v-if="toast.show"
        class="toast-notification"
        :class="'toast-' + toast.type"
      >
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'

const HJBOptimization = defineAsyncComponent(() => import('./optimization/HJBOptimization.vue'))
const CCMVOptimization = defineAsyncComponent(() => import('./optimization/CCMVOptimization.vue'))
const ConvexOptimization = defineAsyncComponent(() => import('./optimization/ConvexOptimization.vue'))
const BlackLittermanOptimization = defineAsyncComponent(() => import('./optimization/BlackLittermanOptimization.vue'))

const activeMethod = ref<string>('hjb')

const methods = [
  { key: 'hjb', title: 'HJB-стратегия', subtitle: 'Стохастическое оптимизирование', icon: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5' },
  { key: 'ccmv', title: 'CCMV модель', subtitle: 'Кластерная оптимизация', icon: 'M12 2a10 10 0 100 20 10 10 0 000-20zM12 6v6l4 2' },
  { key: 'bl', title: 'Black-Litterman', subtitle: 'Байесовская оптимизация', icon: 'M3 3h18v18H3zM12 8v8M8 12h8' },
  { key: 'convex', title: 'Convex Portfolio', subtitle: 'Выпуклая оптимизация', icon: 'M4 20L8 4l4 10 4-6 4 12' }
]

const componentMap: Record<string, any> = {
  hjb: HJBOptimization,
  ccmv: CCMVOptimization,
  bl: BlackLittermanOptimization,
  convex: ConvexOptimization
}

const activeComponent = computed(() => componentMap[activeMethod.value])

const toast = ref<{ show: boolean; message: string; type: 'success' | 'error' | 'info' }>({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (payload: { message: string; type: 'success' | 'error' | 'info' }) => {
  toast.value = { show: true, message: payload.message, type: payload.type }
  setTimeout(() => { toast.value.show = false }, 3000)
}
</script>

<style scoped>
.optimization-page {
  padding: 24px 32px;
  max-width: 1800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 100vh;
}

.method-selector {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.method-tab {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 22px;
  background: rgba(20, 22, 28, 0.5);
  backdrop-filter: blur(30px);
  border: 2px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  text-align: left;
}

.method-tab:hover {
  background: rgba(30, 32, 40, 0.6);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.method-tab.active {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.method-icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
}

.method-icon.hjb {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #60a5fa;
}

.method-icon.ccmv {
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.4);
  color: #4ade80;
}

.method-icon.bl {
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #c084fc;
}

.method-icon.convex {
  background: rgba(251, 191, 36, 0.2);
  border: 1px solid rgba(251, 191, 36, 0.4);
  color: #fbbf24;
}

.method-tab.active .method-icon {
  box-shadow: 0 0 20px currentColor;
}

.method-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.method-title {
  font-size: 15px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
}

.method-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.method-tab.active .method-title {
  color: #fff;
}

.method-tab.active .method-subtitle {
  color: rgba(255, 255, 255, 0.7);
}

/* Toast */
.toast-notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  max-width: 320px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-success {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}

.toast-error {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.3);
}

.toast-info {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.3);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

@media (max-width: 1400px) {
  .method-selector {
    flex-wrap: wrap;
  }
  .method-tab {
    min-width: calc(50% - 6px);
  }
}

@media (max-width: 768px) {
  .optimization-page {
    padding: 16px;
  }
  .method-selector {
    flex-direction: column;
  }
  .method-tab {
    padding: 14px;
  }
  .method-icon {
    width: 36px;
    height: 36px;
  }
  .method-title {
    font-size: 13px;
  }
}
</style>
