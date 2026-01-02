<!-- src/components/layout/MainLayout.vue -->
<template>
  <div class="app-root">
    
    <!-- Ambient Background -->
    <div class="ambient-glow purple"></div>
    <div class="ambient-glow blue"></div>

    <div class="app-container">
      
      <!-- Navigation -->
      <Sidebar />

      <!-- Main Glass Window -->
      <div class="main-window">
        
        <!-- 🔥 DYNAMIC ISLAND CONTAINER (Overlay) 🔥 -->
        <div class="island-position">
           <TaskWidget />
        </div>

        <!-- Header -->
        <header class="window-header">
          <div class="header-content">
            
            <!-- Top Row: Breadcrumbs & System Status -->
            <div class="header-top">
              <nav class="breadcrumbs">
                <span class="crumb-root">DASHBOARD</span>
                <span class="crumb-sep">/</span>
                <span class="crumb-active">{{ currentRouteName }}</span>
              </nav>

              <div class="system-status">
                <div class="status-pill">
                  <span class="pulse-dot"></span>
                  API Live
                </div>
                <div class="divider"></div>
                <div class="status-text">
                  Ping: <span class="mono">{{ latency }}ms</span>
                </div>
              </div>
            </div>

            <!-- Bottom Row: Search & Actions -->
            <div class="header-bottom">
              
              <!-- Search -->
              <div class="search-wrapper">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input 
                  type="text" 
                  placeholder="Поиск тикера, ISIN или стратегии..." 
                  class="search-input"
                  v-model="searchQuery"
                >
                <div class="hk-badge">⌘K</div>
              </div>

              <!-- Actions Group (Right Aligned) -->
              <div class="actions-group">
                <button 
                  class="icon-btn" 
                  @click="toggleNotifications"
                  :class="{ active: showNotifications }"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                  <span v-if="unreadCount" class="notification-dot"></span>
                </button>

              </div>
            </div>

          </div>

          <!-- Notifications Drawer -->
          <transition name="drawer">
            <div v-if="showNotifications" class="notifications-panel glass-panel">
               <div class="panel-header">
                 <h3>Уведомления</h3>
                 <button @click="unreadCount = 0" class="clear-btn">Очистить</button>
               </div>
               <div class="notifications-list">
                 <div class="notif-item warning">
                   <div class="notif-icon">⚠️</div>
                   <div class="notif-content">
                     <div class="notif-title">High Volatility Alert</div>
                     <div class="notif-desc">VIX index spike detected (>25.0)</div>
                   </div>
                   <div class="notif-time">2m</div>
                 </div>
                 <div class="notif-item success">
                   <div class="notif-icon">✅</div>
                   <div class="notif-content">
                     <div class="notif-title">Rebalancing Complete</div>
                     <div class="notif-desc">Portfolio adjusted successfully</div>
                   </div>
                   <div class="notif-time">1h</div>
                 </div>
               </div>
            </div>
          </transition>
        </header>

        <!-- Content Area -->
        <main class="window-content">
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
import TaskWidget from '@/components/common/TaskWidget.vue' // <-- Импорт виджета задач

const route = useRoute()
const searchQuery = ref('')
const showNotifications = ref(false)
const unreadCount = ref(2)
const latency = ref(14)

const currentRouteName = computed(() => {
  return route.name ? String(route.name).toUpperCase() : 'OVERVIEW'
})

const toggleNotifications = () => showNotifications.value = !showNotifications.value
const toggleTheme = () => console.log('Theme toggle logic')

onMounted(() => {
  setInterval(() => {
    latency.value = 12 + Math.floor(Math.random() * 8)
  }, 2000)
})
</script>

<style scoped>
/* ============================================
   ROOT & AMBIENT
   ============================================ */
.app-root {
  width: 100vw; height: 100vh; overflow: hidden;
  background-color: #050505; 
  position: relative;
  color: #e0e0e0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.ambient-glow {
  position: absolute; width: 600px; height: 600px; border-radius: 50%; filter: blur(120px); opacity: 0.15; z-index: 0; pointer-events: none;
}
.ambient-glow.purple { top: -100px; left: -100px; background: #7c3aed; }
.ambient-glow.blue { bottom: -100px; right: -100px; background: #2563eb; }

/* ============================================
   LAYOUT CONTAINER
   ============================================ */
.app-container {
  position: relative; z-index: 1; display: flex; height: 100%;
  padding: 16px 16px 16px 80px; 
  box-sizing: border-box;
}

/* ============================================
   MAIN GLASS WINDOW
   ============================================ */
.main-window {
  flex: 1; display: flex; flex-direction: column;
  background: rgba(20, 22, 28, 0.6);
  backdrop-filter: blur(50px) saturate(150%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  position: relative; /* Для позиционирования Dynamic Island */
}

/* 🔥 DYNAMIC ISLAND POSITIONING 🔥 */
.island-position {
  position: absolute;
  top: 16px; /* Отступ от верхнего края окна */
  left: 0; 
  right: 0;
  display: flex;
  justify-content: center; /* Центрируем по горизонтали */
  z-index: 1000; /* Поверх хедера */
  pointer-events: none; /* Пропускаем клики мимо контейнера */
}

/* Разрешаем клик по самому виджету */
:deep(.dynamic-island) {
  pointer-events: auto;
}

/* ============================================
   HEADER
   ============================================ */
.window-header {
  flex-shrink: 0; border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  position: relative; z-index: 20;
}

.header-content { padding: 16px 24px; display: flex; flex-direction: column; gap: 16px; }

/* Top Row */
.header-top { display: flex; justify-content: space-between; align-items: center; }

.breadcrumbs { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; display: flex; gap: 8px; color: rgba(255,255,255,0.4); }
.crumb-active { color: #fff; text-shadow: 0 0 10px rgba(255,255,255,0.3); }

.system-status { display: flex; align-items: center; gap: 12px; font-size: 11px; }
.status-pill { display: flex; align-items: center; gap: 6px; color: #4ade80; font-weight: 600; }
.pulse-dot { width: 6px; height: 6px; background: #4ade80; border-radius: 50%; box-shadow: 0 0 8px #4ade80; animation: pulse 2s infinite; }
.divider { width: 1px; height: 12px; background: rgba(255,255,255,0.1); }
.status-text { color: rgba(255,255,255,0.5); }
.mono { font-family: monospace; color: #fff; }

@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

/* Bottom Row */
.header-bottom { display: flex; justify-content: space-between; align-items: center; }

.search-wrapper {
  position: relative; display: flex; align-items: center; width: 320px;
}
.search-icon { position: absolute; left: 10px; width: 16px; color: rgba(255,255,255,0.4); }
.search-input {
  width: 100%; padding: 10px 10px 10px 36px;
  background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;
  color: #fff; font-size: 13px; outline: none; transition: all 0.2s;
}
.search-input:focus { background: rgba(0,0,0,0.4); border-color: rgba(255,255,255,0.2); box-shadow: 0 0 0 2px rgba(255,255,255,0.05); }
.hk-badge {
  position: absolute; right: 8px; font-size: 10px; color: rgba(255,255,255,0.3); border: 1px solid rgba(255,255,255,0.1); padding: 1px 4px; border-radius: 4px;
}

.actions-group { display: flex; align-items: center; gap: 8px; }
.icon-btn {
  width: 36px; height: 36px; border-radius: 10px; border: 1px solid transparent; background: transparent;
  color: rgba(255,255,255,0.7); cursor: pointer; display: flex; align-items: center; justify-content: center; position: relative;
  transition: all 0.2s;
}
.icon-btn:hover, .icon-btn.active { background: rgba(255,255,255,0.08); color: #fff; }
.icon-btn svg { width: 18px; height: 18px; }

.notification-dot {
  position: absolute; top: 8px; right: 8px; width: 6px; height: 6px; background: #f87171; border-radius: 50%; border: 1px solid rgba(20, 22, 28, 0.6);
}

.user-avatar {
  width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #fff;
  border: 2px solid rgba(20, 22, 28, 0.5); margin-left: 8px;
}

/* ... Notifications Styles & Transitions ... (без изменений) */
.notifications-panel {
  position: absolute; top: 100%; right: 24px; width: 320px;
  background: rgba(30, 32, 40, 0.95); backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1); border-top: none;
  border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.5); z-index: 50; overflow: hidden;
}
.panel-header { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; }
.panel-header h3 { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; margin: 0; }
.clear-btn { background: none; border: none; font-size: 11px; color: #60a5fa; cursor: pointer; }
.notif-item { padding: 12px 16px; display: flex; gap: 12px; border-bottom: 1px solid rgba(255,255,255,0.03); }
.notif-item:last-child { border-bottom: none; }
.notif-item:hover { background: rgba(255,255,255,0.02); }
.notif-icon { font-size: 16px; }
.notif-title { font-size: 13px; font-weight: 600; color: #fff; }
.notif-desc { font-size: 11px; color: rgba(255,255,255,0.6); margin-top: 2px; }
.notif-time { font-size: 10px; color: rgba(255,255,255,0.3); margin-left: auto; white-space: nowrap; }
.drawer-enter-active, .drawer-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.drawer-enter-from, .drawer-leave-to { opacity: 0; transform: translateY(-10px); }
.window-content { flex: 1; overflow-y: auto; position: relative; scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.1) transparent; }
.window-content::-webkit-scrollbar { width: 6px; }
.window-content::-webkit-scrollbar-track { background: transparent; }
.window-content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
@media (max-width: 768px) {
  .app-container { padding: 0; }
  .main-window { border-radius: 0; border: none; }
  .header-bottom { flex-direction: column; gap: 12px; align-items: stretch; }
  .search-wrapper { width: 100%; }
  .actions-group { justify-content: flex-end; }
}
</style>