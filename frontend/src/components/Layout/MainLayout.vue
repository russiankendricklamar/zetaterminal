<!-- src/components/layout/MainLayout.vue -->
<template>
  <div class="app-root">
    
    <!-- 🌌 AMBIENT LIVE BACKGROUND 🌌 -->
    <div class="ambient-layer">
      <div class="glow-orb gray"></div>
      <div class="glow-orb blue"></div>
      <div class="glow-orb orange"></div>
    </div>

    <!-- Текстура шума (Film Grain) для реализма -->
    <div class="noise-overlay"></div>

    <div class="app-container">
      
      <!-- Navigation (Sidebar) -->
      <Sidebar class="sidebar-layer" />

      <!-- 💎 MAIN GLASS WINDOW 💎 -->
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
                <span class="crumb-root">PORTFOLIO</span>
                <span class="crumb-sep">/</span>
                <span class="crumb-active">{{ currentRouteName }}</span>
              </nav>

              <div class="system-status">
                <div class="status-pill">
                  <span class="pulse-dot"></span>
                  <span class="status-label">API Live</span>
                </div>
                <div class="divider"></div>
                <div class="status-text">
                  Ping <span class="mono">{{ latency }}ms</span>
                </div>
              </div>
            </div>

            <!-- Bottom Row: Search & Actions -->
            <div class="header-bottom">
              
              <!-- Recessed Search Input -->
              <div class="search-wrapper">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                <input 
                  type="text" 
                  placeholder="Поиск по тикеру, ISIN..." 
                  class="search-input"
                  v-model="searchQuery"
                >
                <div class="hk-badge">⌘K</div>
              </div>

              <!-- Glass Actions Group -->
              <div class="actions-group">
                <button 
                  class="icon-btn" 
                  @click="toggleNotifications"
                  :class="{ active: showNotifications }"
                  aria-label="Notifications"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                  <span v-if="unreadCount" class="notification-dot"></span>
                  <div class="btn-glow"></div> <!-- Внутреннее свечение при ховере -->
                </button>
                
                <div class="user-avatar">
                   <span>RK</span>
                </div>
              </div>
            </div>

          </div>

          <!-- Notifications Drawer (Frosted Glass) -->
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
                     <div class="notif-title">High Volatility</div>
                     <div class="notif-desc">VIX spike > 25.0 detected</div>
                   </div>
                   <div class="notif-time">2m</div>
                 </div>
                 <div class="notif-item success">
                   <div class="notif-icon">✅</div>
                   <div class="notif-content">
                     <div class="notif-title">Rebalanced</div>
                     <div class="notif-desc">Target weights achieved</div>
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
import TaskWidget from '@/components/common/TaskWidget.vue'
import { useIsMobile } from '@/composables/useIsMobile'

const route = useRoute()
const { isMobile } = useIsMobile()
const searchQuery = ref('')
const showNotifications = ref(false)
const unreadCount = ref(2)
const latency = ref(14)

const currentRouteName = computed(() => {
  return route.name ? String(route.name).toUpperCase() : 'OVERVIEW'
})

const toggleNotifications = () => showNotifications.value = !showNotifications.value

onMounted(() => {
  // Эмуляция живого пинга
  setInterval(() => {
    latency.value = 12 + Math.floor(Math.random() * 8)
  }, 2000)
})
</script>

<style scoped>
/* ============================================
   ROOT & BACKGROUND PHYSICS
   ============================================ */
.app-root {
  width: 100vw; 
  height: 100vh; 
  overflow-x: hidden;
  overflow-y: auto;
  background-color: #02040a; /* Deep Space Black */
  position: relative;
  color: #f5f5f7; /* Apple Off-White */
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -webkit-overflow-scrolling: touch;
}

/* Шум для текстурности (убирает пластиковый эффект) */
.noise-overlay {
  position: absolute; inset: 0; pointer-events: none; z-index: 2;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

/* Живые орбиты */
.ambient-layer {
  position: absolute; inset: 0; z-index: 1; overflow: hidden;
}

.glow-orb {
  position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.5;
  animation: floatOrb 20s infinite ease-in-out alternate;
  mix-blend-mode: screen; /* Важно для смешивания цветов */
}

.glow-orb.purple { 
  width: 900px; height: 900px; background: radial-gradient(circle, #7c3aed 0%, transparent 70%);
  top: -20%; left: -10%;
}
.glow-orb.blue { 
  width: 800px; height: 800px; background: radial-gradient(circle, #2563eb 0%, transparent 70%);
  bottom: -20%; right: -10%; animation-delay: -5s;
}
.glow-orb.orange {
  width: 600px; height: 600px; background: radial-gradient(circle, #ea580c 0%, transparent 70%);
  top: 40%; left: 40%; opacity: 0.25; animation-duration: 30s;
}

@keyframes floatOrb {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(40px, -40px) scale(1.1); }
}

/* ============================================
   LAYOUT GRID
   ============================================ */
.app-container {
  position: relative; z-index: 10; display: flex;
  min-height: 100%;
  padding: 12px 12px 12px 80px; /* Отступы для "парящего" окна */
  box-sizing: border-box;
  gap: 12px;
}

@media (max-width: 768px) {
  .app-container {
    padding: 0 0 0 60px; /* Уменьшенный отступ для мобильного sidebar-tab */
  }
}

@media (max-width: 480px) {
  .app-container {
    padding: 0 0 0 56px; /* Еще меньше для маленьких экранов */
  }
}

/* ============================================
   💎 MAIN LIQUID GLASS WINDOW 💎
   ============================================ */
.main-window {
  flex: 1; display: flex; flex-direction: column;
  position: relative; 
  overflow-x: hidden;
  overflow-y: auto;
  min-height: 100%;
  
  /* GLASS RECIPE */
  background: rgba(30, 35, 45, 0.40); /* Полупрозрачная темная база */
  backdrop-filter: blur(40px) saturate(180%); /* Saturate делает цвета фона сочными */
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  
  border-radius: 24px;
  
  /* LIGHTING & BORDERS */
  /* Тонкая белая рамка + Внутренний блик сверху + Тень */
  box-shadow: 
    0 20px 50px -10px rgba(0, 0, 0, 0.6), /* Глубокая тень */
    inset 0 1px 0 0 rgba(255, 255, 255, 0.25), /* Яркий верхний блик (свет падает сверху) */
    inset 0 0 0 1px rgba(255, 255, 255, 0.05); /* Общая тонкая граница */
    
  border: 1px solid rgba(255, 255, 255, 0.02); /* Еле заметный физический бордер */
  
  transition: transform 0.3s ease;
}

/* Dynamic Island Container */
.island-position {
  position: absolute; top: 12px; left: 0; right: 0;
  display: flex; justify-content: center;
  z-index: 1000; pointer-events: none;
}
:deep(.dynamic-island) { pointer-events: auto; }

/* ============================================
   HEADER STYLES
   ============================================ */
.window-header {
  flex-shrink: 0; 
  position: relative; z-index: 20;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0) 100%);
}

.header-content { padding: 20px 32px; display: flex; flex-direction: column; gap: 20px; }

/* Top Row */
.header-top { display: flex; justify-content: space-between; align-items: center; }

.breadcrumbs { 
  font-size: 11px; font-weight: 700; letter-spacing: 0.1em; 
  display: flex; gap: 10px; color: rgba(255,255,255,0.4); 
  text-transform: uppercase;
}
.crumb-active { color: #fff; text-shadow: 0 0 12px rgba(255,255,255,0.4); }

.system-status { display: flex; align-items: center; gap: 16px; font-size: 11px; background: rgba(0,0,0,0.2); padding: 4px 10px; border-radius: 99px; border: 1px solid rgba(255,255,255,0.05); }
.status-pill { display: flex; align-items: center; gap: 6px; color: #4ade80; font-weight: 600; }
.pulse-dot { width: 6px; height: 6px; background: #4ade80; border-radius: 50%; box-shadow: 0 0 8px #4ade80; animation: pulse 2s infinite; }
.divider { width: 1px; height: 10px; background: rgba(255,255,255,0.15); }
.status-text { color: rgba(255,255,255,0.5); }
.mono { font-family: "SF Mono", monospace; color: #fff; }

@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(0.9); } }

/* Bottom Row */
.header-bottom { display: flex; justify-content: space-between; align-items: center; }

/* RECESSED SEARCH INPUT (Вдавленное стекло) */
.search-wrapper {
  position: relative; display: flex; align-items: center; width: 360px;
}
.search-icon { position: absolute; left: 12px; width: 18px; color: rgba(255,255,255,0.4); z-index: 2; transition: color 0.2s;}
.search-input {
  width: 100%; padding: 12px 12px 12px 40px;
  /* Темнее фона для эффекта глубины */
  background: rgba(0, 0, 0, 0.2); 
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.2), inset 0 0 0 1px rgba(255,255,255,0.05);
  border: none; border-bottom: 1px solid rgba(255,255,255,0.1); /* Рефлекс снизу */
  border-radius: 14px;
  color: #fff; font-size: 14px; font-weight: 400;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
}
.search-input:focus { 
  background: rgba(0,0,0,0.35); 
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.3), inset 0 0 0 1px rgba(255,255,255,0.15);
  outline: none;
}
.search-input:focus + .hk-badge { opacity: 0; }
.search-input:focus ~ .search-icon { color: #fff; }

.hk-badge {
  position: absolute; right: 10px; font-size: 10px; color: rgba(255,255,255,0.4); 
  border: 1px solid rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 6px; pointer-events: none; transition: opacity 0.2s;
}

/* Buttons */
.actions-group { display: flex; align-items: center; gap: 12px; }

.icon-btn {
  width: 42px; height: 42px; border-radius: 12px; border: none;
  background: rgba(255,255,255,0.05); /* Glass surface */
  box-shadow: 0 4px 10px rgba(0,0,0,0.1), inset 0 1px 0 rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.7); cursor: pointer; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;
  transition: all 0.25s cubic-bezier(0.3, 0.7, 0.4, 1);
}
.icon-btn:hover { 
  background: rgba(255,255,255,0.1); color: #fff; transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.2);
}
.icon-btn.active { background: rgba(255,255,255,0.15); color: #fff; }

.notification-dot {
  position: absolute; top: 10px; right: 10px; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 6px #ef4444;
}

.user-avatar {
  width: 42px; height: 42px; border-radius: 12px; 
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  border: 1px solid rgba(255,255,255,0.2);
}

/* ============================================
   NOTIFICATIONS DRAWER
   ============================================ */
.notifications-panel {
  position: absolute; top: 100%; right: 32px; width: 340px; margin-top: 12px;
  background: rgba(24, 26, 32, 0.85); 
  backdrop-filter: blur(25px) saturate(180%);
  border-radius: 18px;
  box-shadow: 0 25px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.08);
  z-index: 50; overflow: hidden;
}
.panel-header { padding: 16px 20px; background: rgba(255,255,255,0.02); border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; }
.panel-header h3 { font-size: 11px; color: rgba(255,255,255,0.5); font-weight: 700; text-transform: uppercase; margin: 0; letter-spacing: 0.05em; }
.clear-btn { background: none; border: none; font-size: 11px; color: #60a5fa; cursor: pointer; font-weight: 500; transition: opacity 0.2s; }
.clear-btn:hover { opacity: 0.8; }

.notif-item { padding: 14px 20px; display: flex; gap: 14px; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s; }
.notif-item:hover { background: rgba(255,255,255,0.04); }
.notif-item:last-child { border-bottom: none; }
.notif-title { font-size: 13px; font-weight: 600; color: #fff; margin-bottom: 2px;}
.notif-desc { font-size: 12px; color: rgba(255,255,255,0.6); line-height: 1.4; }
.notif-time { font-size: 10px; color: rgba(255,255,255,0.3); margin-left: auto; white-space: nowrap; font-variant-numeric: tabular-nums; }

/* Transitions */
.drawer-enter-active, .drawer-leave-active { 
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); 
  will-change: opacity, transform;
}
.drawer-enter-from, .drawer-leave-to { 
  opacity: 0; 
  transform: translateY(-8px) scale(0.98); 
}

/* Scrollbar & Content */
.window-content { 
  flex: 1; 
  overflow-y: auto; 
  overflow-x: hidden;
  position: relative; 
  padding: 0; /* Контент сам делает отступы */
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
}
/* Стеклянный скроллбар */
.window-content::-webkit-scrollbar { 
  width: 6px; 
}
.window-content::-webkit-scrollbar-track { 
  background: transparent; 
  border-radius: 10px;
}
.window-content::-webkit-scrollbar-thumb { 
  background: rgba(255,255,255,0.15); 
  border-radius: 10px;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  background-clip: padding-box;
}
.window-content::-webkit-scrollbar-thumb:hover { 
  background: rgba(255,255,255,0.25);
  border: 1px solid rgba(255,255,255,0.1);
}
.window-content::-webkit-scrollbar-thumb:active { 
  background: rgba(255,255,255,0.35);
}

.fade-enter-active, .fade-leave-active { 
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
  will-change: opacity;
}
.fade-enter-from, .fade-leave-to { 
  opacity: 0; 
}

@media (max-width: 768px) {
  .app-root {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    height: auto;
    min-height: 100vh;
  }

  .app-container {
    padding: 0 0 0 60px;
    gap: 0;
    min-height: 100vh;
    height: auto;
  }

  .main-window {
    border-radius: 0;
    border: none;
    background: #000;
    box-shadow: none;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    min-height: 100vh;
    /* Reduce blur on mobile for performance */
    backdrop-filter: blur(12px) saturate(150%);
    -webkit-backdrop-filter: blur(12px) saturate(150%);
  }

  .window-content {
    overflow-y: visible;
    -webkit-overflow-scrolling: touch;
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
    width: 100%;
  }

  .actions-group {
    justify-content: flex-end;
  }

  .notifications-panel {
    right: 16px;
    left: 16px;
    width: auto;
    max-width: none;
  }

  /* Hide ambient effects on mobile for performance */
  .ambient-layer {
    display: none;
  }

  .noise-overlay {
    display: none;
  }
}

@media (max-width: 480px) {
  .app-root {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .app-container {
    padding: 0 0 0 56px;
    min-height: 100vh;
  }

  .main-window {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    /* No blur on small mobile for better performance */
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
  }

  .window-content {
    overflow-y: visible;
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
    padding: 3px 8px;
  }

  .search-input {
    padding: 10px 10px 10px 36px;
    font-size: 13px;
  }

  .search-icon {
    width: 16px;
    left: 10px;
  }

  .hk-badge {
    display: none;
  }

  .icon-btn {
    width: 40px;
    height: 40px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
    font-size: 12px;
  }

  .notifications-panel {
    right: 12px;
    left: 12px;
    margin-top: 8px;
  }

  .notif-item {
    padding: 12px 14px;
    gap: 10px;
  }

  .notif-title {
    font-size: 12px;
  }

  .notif-desc {
    font-size: 11px;
  }
}

/* Extra small phones (375px and below) */
@media (max-width: 375px) {
  .app-container {
    padding: 0 0 0 48px;
  }

  .header-content {
    padding: 10px;
    gap: 8px;
  }

  .breadcrumbs {
    font-size: 9px;
    gap: 6px;
  }

  .icon-btn {
    width: 36px;
    height: 36px;
    border-radius: 10px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    font-size: 11px;
    border-radius: 10px;
  }

  .search-input {
    padding: 8px 8px 8px 32px;
    font-size: 12px;
    border-radius: 10px;
  }

  .search-icon {
    width: 14px;
    left: 8px;
  }
}
</style>