<!-- src/components/layout/MainLayout.vue - Brutalist Design -->
<template>
  <div class="app-root">
    <!-- Noise Overlay -->
    <div class="bg-noise"></div>

    <div class="app-container">
      <!-- Navigation (Sidebar) -->
      <Sidebar class="sidebar-layer" />

      <!-- Main Content Window -->
      <div class="main-window">

        <!-- Dynamic Island Container -->
        <div class="island-position">
          <TaskWidget />
        </div>

        <!-- Header -->
        <header class="window-header">
          <div class="header-content">

            <!-- Top Row: Breadcrumbs & System Status -->
            <div class="header-top">
              <nav class="breadcrumbs font-mono">
                <span class="crumb-root">STOCHASTIC</span>
                <span class="crumb-sep">/</span>
                <span class="crumb-active">{{ currentRouteName }}</span>
              </nav>

              <div class="system-status">
                <div class="status-pill">
                  <span class="status-dot online"></span>
                  <span class="status-label font-mono">API LIVE</span>
                </div>
                <div class="divider-v"></div>
                <div class="status-text font-mono">
                  {{ latency }}ms
                </div>
              </div>
            </div>

            <!-- Bottom Row: Search & Actions -->
            <div class="header-bottom">

              <!-- Search Input -->
              <div class="search-wrapper">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/>
                  <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                <input
                  type="text"
                  placeholder="Поиск по тикеру, ISIN..."
                  class="search-input font-mono"
                  v-model="searchQuery"
                >
                <div class="hk-badge font-mono">⌘K</div>
              </div>

              <!-- Actions Group -->
              <div class="actions-group">
                <button
                  class="icon-btn"
                  @click="toggleNotifications"
                  :class="{ active: showNotifications }"
                  aria-label="Notifications"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                  </svg>
                  <span v-if="unreadCount" class="notification-badge">{{ unreadCount }}</span>
                </button>

                <div class="user-avatar font-oswald">
                  <span>RK</span>
                </div>
              </div>
            </div>

          </div>

          <!-- Notifications Panel -->
          <transition name="slide">
            <div v-if="showNotifications" class="notifications-panel">
              <div class="panel-header">
                <h3 class="font-oswald">УВЕДОМЛЕНИЯ</h3>
                <button @click="unreadCount = 0" class="clear-btn font-mono">ОЧИСТИТЬ</button>
              </div>
              <div class="notifications-list">
                <div class="notif-item">
                  <div class="notif-indicator warning"></div>
                  <div class="notif-content">
                    <div class="notif-title font-oswald">HIGH VOLATILITY</div>
                    <div class="notif-desc font-mono">VIX spike > 25.0 detected</div>
                  </div>
                  <div class="notif-time font-mono">2m</div>
                </div>
                <div class="notif-item">
                  <div class="notif-indicator success"></div>
                  <div class="notif-content">
                    <div class="notif-title font-oswald">REBALANCED</div>
                    <div class="notif-desc font-mono">Target weights achieved</div>
                  </div>
                  <div class="notif-time font-mono">1h</div>
                </div>
              </div>
            </div>
          </transition>
        </header>

        <!-- Content Area -->
        <main class="window-content custom-scrollbar">
          <RouterView v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </RouterView>
        </main>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/Layout/Sidebar.vue'
import TaskWidget from '@/components/common/TaskWidget.vue'

const route = useRoute()
const searchQuery = ref('')
const showNotifications = ref(false)
const unreadCount = ref(2)
const latency = ref(14)

const currentRouteName = computed(() => {
  return route.name ? String(route.name).toUpperCase() : 'OVERVIEW'
})

const toggleNotifications = () => showNotifications.value = !showNotifications.value

onMounted(() => {
  setInterval(() => {
    latency.value = 12 + Math.floor(Math.random() * 8)
  }, 2000)
})
</script>

<style scoped>
/* ============================================
   ROOT - BRUTALIST
   ============================================ */
.app-root {
  width: 100vw;
  height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
  background: #050505;
  position: relative;
  color: #f5f5f5;
  -webkit-font-smoothing: antialiased;
  -webkit-overflow-scrolling: touch;
}

/* ============================================
   LAYOUT
   ============================================ */
.app-container {
  position: relative;
  z-index: 10;
  display: flex;
  min-height: 100%;
  padding: 0 0 0 64px;
  box-sizing: border-box;
}

/* ============================================
   MAIN WINDOW - BRUTALIST
   ============================================ */
.main-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  min-height: 100%;
  background: #0a0a0a;
  border-left: 1px solid #1a1a1a;
}

/* Dynamic Island Container */
.island-position {
  position: absolute;
  top: 12px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  z-index: 1000;
  pointer-events: none;
}

:deep(.dynamic-island) {
  pointer-events: auto;
}

/* ============================================
   HEADER - BRUTALIST
   ============================================ */
.window-header {
  flex-shrink: 0;
  position: relative;
  z-index: 20;
  border-bottom: 1px solid #1a1a1a;
  background: #050505;
}

.header-content {
  padding: 20px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Top Row */
.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.breadcrumbs {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.15em;
  display: flex;
  gap: 10px;
  color: #525252;
  text-transform: uppercase;
}

.crumb-active {
  color: #DC2626;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 11px;
  border: 1px solid #262626;
  padding: 6px 12px;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #22c55e;
  font-weight: 500;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #DC2626;
}

.status-dot.online {
  background: #22c55e;
}

.divider-v {
  width: 1px;
  height: 12px;
  background: #262626;
}

.status-text {
  color: #737373;
}

/* Bottom Row */
.header-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

/* Search Input - Brutalist */
.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 12px;
  width: 16px;
  color: #525252;
  z-index: 2;
  transition: color 0.2s;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  background: #050505;
  border: 1px solid #262626;
  color: #f5f5f5;
  font-size: 13px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #DC2626;
}

.search-input:focus ~ .search-icon {
  color: #DC2626;
}

.search-input::placeholder {
  color: #525252;
}

.hk-badge {
  position: absolute;
  right: 12px;
  font-size: 10px;
  color: #525252;
  border: 1px solid #262626;
  padding: 2px 6px;
  pointer-events: none;
  transition: opacity 0.2s;
}

.search-input:focus + .hk-badge {
  opacity: 0;
}

/* Action Buttons */
.actions-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border: 1px solid #262626;
  background: transparent;
  color: #737373;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.icon-btn.active {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 16px;
  height: 16px;
  background: #DC2626;
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #000;
  letter-spacing: 0.05em;
}

/* ============================================
   NOTIFICATIONS PANEL - BRUTALIST
   ============================================ */
.notifications-panel {
  position: absolute;
  top: 100%;
  right: 32px;
  width: 340px;
  margin-top: 8px;
  background: #0a0a0a;
  border: 1px solid #262626;
  z-index: 50;
  overflow: hidden;
}

.panel-header {
  padding: 16px 20px;
  background: #050505;
  border-bottom: 1px solid #262626;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  font-size: 12px;
  color: #f5f5f5;
  letter-spacing: 0.1em;
  margin: 0;
}

.clear-btn {
  background: none;
  border: none;
  font-size: 10px;
  color: #DC2626;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: opacity 0.2s;
}

.clear-btn:hover {
  opacity: 0.7;
}

.notifications-list {
  max-height: 300px;
  overflow-y: auto;
}

.notif-item {
  padding: 16px 20px;
  display: flex;
  gap: 12px;
  border-bottom: 1px solid #1a1a1a;
  transition: background 0.2s;
}

.notif-item:hover {
  background: #111111;
}

.notif-item:last-child {
  border-bottom: none;
}

.notif-indicator {
  width: 4px;
  flex-shrink: 0;
}

.notif-indicator.warning {
  background: #f59e0b;
}

.notif-indicator.success {
  background: #22c55e;
}

.notif-content {
  flex: 1;
  min-width: 0;
}

.notif-title {
  font-size: 13px;
  font-weight: 500;
  color: #f5f5f5;
  margin-bottom: 4px;
  letter-spacing: 0.05em;
}

.notif-desc {
  font-size: 11px;
  color: #737373;
  line-height: 1.4;
}

.notif-time {
  font-size: 10px;
  color: #525252;
  flex-shrink: 0;
}

/* ============================================
   CONTENT AREA
   ============================================ */
.window-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  padding: 0;
  -webkit-overflow-scrolling: touch;
}

/* ============================================
   TRANSITIONS
   ============================================ */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .app-root {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    height: auto;
    min-height: 100vh;
  }

  .app-container {
    padding: 0 0 0 56px;
    min-height: 100vh;
  }

  .main-window {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    min-height: 100vh;
  }

  .header-content {
    padding: 16px;
    gap: 12px;
  }

  .header-top {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .system-status {
    width: 100%;
    justify-content: center;
  }

  .header-bottom {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .search-wrapper {
    max-width: none;
  }

  .actions-group {
    justify-content: flex-end;
  }

  .notifications-panel {
    right: 16px;
    left: 16px;
    width: auto;
  }
}

@media (max-width: 480px) {
  .app-container {
    padding: 0 0 0 48px;
  }

  .header-content {
    padding: 12px;
    gap: 10px;
  }

  .breadcrumbs {
    font-size: 10px;
  }

  .system-status {
    font-size: 10px;
    padding: 4px 8px;
  }

  .search-input {
    padding: 10px 10px 10px 36px;
    font-size: 12px;
  }

  .hk-badge {
    display: none;
  }

  .icon-btn {
    width: 36px;
    height: 36px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    font-size: 12px;
  }
}

@media (max-width: 375px) {
  .app-container {
    padding: 0 0 0 44px;
  }

  .header-content {
    padding: 10px;
  }

  .icon-btn {
    width: 34px;
    height: 34px;
  }

  .user-avatar {
    width: 34px;
    height: 34px;
  }
}
</style>
