<!-- src/components/layout/Sidebar.vue -->
<template>
  <!-- Narrow Tab Bar (Left Strip) -->
  <div
    class="sidebar-tab"
    @click="toggleSidebar"
    :class="{ active: isSidebarOpen, hidden: isSidebarOpen }"
    title="Open Menu"
  >
    <div class="burger-icon">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>

  <!-- Backdrop Overlay -->
  <div v-if="isSidebarOpen" class="sidebar-backdrop" @click="closeSidebar" />

  <!-- Sliding Sidebar Panel -->
  <aside class="sidebar" :class="{ 'sidebar--open': isSidebarOpen }">
    <div class="sidebar-header">
      <span class="app-logo">Quantitative Analitics</span>
      <button class="close-btn" @click="closeSidebar">✕</button>
    </div>

    <!-- Tools Navigation (SCROLLABLE AREA) -->
    <nav class="sidebar-tools custom-scroll">
      
      <!-- HOME (Landing) -->
      <router-link
        to="/"
        class="home-entry"
        :class="{ active: isActive('/') }"
        @click="closeSidebar"
      >
        <div class="home-icon">
          <!-- The "Home" supernova style -->
          <div class="supernova-home"></div>
        </div>
        <div class="home-info">
          <div class="home-title">Главная</div>
          <div class="home-subtitle">Обзор инструментов</div>
        </div>
      </router-link>

      <!-- =========================================================
           TOP 3 (AVAILABLE): Portfolio Analytics -> Risk -> Research
           ========================================================= -->

      <!-- 1) Portfolio Analytics -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('portfolio')"
          :class="{ expanded: expandedTools.portfolio }"
        >
          <!-- BLUE SUPERNOVA -->
          <div class="glossy-icon">
             <div class="supernova blue"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Портфельный анализ</span>
            <span class="tool-subtitle">Анализ и оптимизация</span>
          </div>
          <div class="chevron">
             <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>

        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.portfolio ? '600px' : '0' }"
        >
          <div class="tool-content">
            <router-link
              v-for="item in portfolioItems"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: isActive(item.path) }"
              @click="closeSidebar"
            >
              <span class="nav-label">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 2) Risk Management (ENABLED) -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('risk')"
          :class="{ expanded: expandedTools.risk }"
        >
          <!-- PURPLE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova purple"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Риск-менеджмент</span>
            <span class="tool-subtitle">Бэктестинг, стресс-тестировние</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>

        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.risk ? '220px' : '0' }"
        >
          <div class="tool-content">
            <router-link
              v-for="item in riskItems"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: isActive(item.path) }"
              @click="closeSidebar"
            >
              <span class="nav-label">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 3) Market Research -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('quant')"
          :class="{ expanded: expandedTools.quant }"
        >
          <!-- CYAN SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova cyan"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Скрытая марковская цепь</span>
            <span class="tool-subtitle">Модели и режимы</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>

        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.quant ? '300px' : '0' }"
        >
          <div class="tool-content">
            <router-link
              v-for="item in quantItems"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: isActive(item.path) }"
              @click="closeSidebar"
            >
              <span class="nav-label">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- =========================================================
           BELOW: UNAVAILABLE / SOON BLOCKS
           ========================================================= -->

      <!-- Option Pricing -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('options')"
          :class="{ expanded: expandedTools.options }"
        >
          <!-- ORANGE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova orange"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Опционы</span>
            <span class="tool-subtitle">Справедливая стоимость</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.options ? '100px' : '0' }"
        >
          <div class="tool-content">
            <router-link to="/pricing/options" class="nav-item coming-soon">
              <span class="nav-label">Калькулятор опционов</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Swap Valuation -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('swaps')"
          :class="{ expanded: expandedTools.swaps }"
        >
           <!-- ORANGE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova orange"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">СВОПы</span>
            <span class="tool-subtitle">Справедливая стоимость</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.swaps ? '100px' : '0' }"
        >
          <div class="tool-content">
            <router-link to="/pricing/swaps" class="nav-item coming-soon">
              <span class="nav-label">IRS & Currency Swaps</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Volatility Surface -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('vol')"
          :class="{ expanded: expandedTools.vol }"
        >
           <!-- ORANGE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova orange"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Поверхность волатильности</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.vol ? '100px' : '0' }"
        >
          <div class="tool-content">
            <router-link to="/pricing/surface" class="nav-item coming-soon">
              <span class="nav-label">Построение (SABR/SVI)</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Bond Fair Value -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('bonds')"
          :class="{ expanded: expandedTools.bonds }"
        >
           <!-- ORANGE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova orange"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Справедливая стоимость облигаций</span>
            <span class="tool-subtitle">Доходный подход (DCF)</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.bonds ? '100px' : '0' }"
        >
          <div class="tool-content">
            <router-link to="/pricing/bonds" class="nav-item coming-soon">
              <span class="nav-label">Оценка облигаций</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Forward Pricing -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('forwards')"
          :class="{ expanded: expandedTools.forwards }"
        >
           <!-- ORANGE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova orange"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Форварды</span>
            <span class="tool-subtitle">Оценка справедливой стоимости</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.forwards ? '100px' : '0' }"
        >
          <div class="tool-content">
            <router-link to="/pricing/forwards" class="nav-item coming-soon">
              <span class="nav-label">Оценка форвардов</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Derivatives Margin -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('margin')"
          :class="{ expanded: expandedTools.margin }"
        >
           <!-- ORANGE SUPERNOVA -->
          <div class="glossy-icon">
            <div class="supernova orange"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Маржа по деривативам</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.margin ? '100px' : '0' }"
        >
          <div class="tool-content">
            <router-link to="/pricing/margin" class="nav-item coming-soon">
              <span class="nav-label">Расчет маржи</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <div class="sidebar-divider"></div>

    <div class="sidebar-footer">
      <div class="status-row">
        <span class="lbl">API статус</span>
        <span class="val connected">● Онлайн</span>
      </div>
      <div class="status-row">
        <span class="lbl">Время</span>
        <span class="val mono">{{ marketTime }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const marketTime = ref('--:--')
const isSidebarOpen = ref(false)

// Independent state for each block
const expandedTools = reactive({
  portfolio: true,
  risk: false,
  quant: false,
  // SOON blocks
  options: false,
  swaps: false,
  vol: false,
  bonds: false,
  forwards: false,
  margin: false,
})

const toggleTool = (id: keyof typeof expandedTools) => {
  expandedTools[id] = !expandedTools[id]
}

const portfolioItems = [
  { path: '/dashboard', label: 'Главная'},
  { path: '/portfolio', label: 'Оптимизация портфеля'},
  { path: '/monte-carlo', label: 'Симуляция Монте-Карло'},
  { path: '/greeks', label: 'Риск-метрики'},
  { path: '/reports', label: 'Отчёты'},
  { path: '/settings', label: 'Параметры'},
]

const riskItems = [
  { path: '/backtest', label: 'Бэктестинг'},
  { path: '/stress', label: 'Стресс-тестирование'},
]

const quantItems = [
  { path: '/regimes', label: 'Рыночные режимы'},
  { path: '/regime-details', label: 'Детальный анализ режимов'},
  { path: '/fixed-income', label: 'Доходности облигаций'},
]

const isActive = (path: string) => route.path === path
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}
const closeSidebar = () => {
  isSidebarOpen.value = false
}

const updateTime = () => {
  marketTime.value = new Date().toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
let timer: any
onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
/* --------------------------------------
   GLOSSY ICON CONTAINER
   -------------------------------------- */
.glossy-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px; 
  background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.08), rgba(255,255,255,0.02) 80%);
  border: 1px solid rgba(255,255,255,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden; 
  transition: transform 0.3s ease, border-color 0.3s ease;
  flex-shrink: 0;
}

/* Hover: subtle lift & brighter border */
.tool-header:hover .glossy-icon {
  transform: translateY(-1px);
  border-color: rgba(255,255,255,0.3);
}

/* 
   THE "LIGHT BEAM" / WOBBLE 
   (Background ambience)
*/
.glossy-icon::after {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4) 0%, transparent 60%);
  transform: scale(0);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s ease;
  z-index: 1; /* Below the supernova */
}
.tool-header:hover .glossy-icon::after {
  opacity: 0.15;
  animation: beam-wobble 2s infinite ease-in-out; 
  transform: scale(1);
}
@keyframes beam-wobble {
  0%   { transform: translate(0, 0) scale(1); }
  50%  { transform: translate(2px, -2px) scale(1.1); }
  100% { transform: translate(0, 0) scale(1); }
}

/* --------------------------------------
   SUPERNOVA (The Glowing Core)
   -------------------------------------- */
.supernova {
  width: 12px; /* Increased from 6px */
  height: 12px;
  border-radius: 50%;
  
  /* IRIDESCENT CORE: Pearl-like shifting gradient */
  background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 33%, #faf5ff 66%, #ffffff 100%);
  background-size: 200% 200%;
  
  position: relative;
  z-index: 2;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  
  /* Pulse + Shimmer animation */
  animation: star-pulse 3s infinite ease-in-out, shimmer 3s infinite linear;
}

/* COLOR VARIANTS (The Normal State Glow) */
.supernova.blue {
  box-shadow: 0 0 12px 2px rgba(59, 130, 246, 0.6);
}
.supernova.purple {
  box-shadow: 0 0 12px 2px rgba(168, 85, 247, 0.6);
}
.supernova.cyan {
  box-shadow: 0 0 12px 2px rgba(34, 211, 238, 0.6);
}
.supernova.orange {
  box-shadow: 0 0 12px 2px rgba(249, 115, 22, 0.6);
}

/* Home Page Dot (Adjusted to match iridescent style but larger) */
.supernova-home {
  width: 18px; height: 18px; border-radius: 50%;
  background: linear-gradient(135deg, #22d3ee, #ffffff, #6366f1);
  background-size: 200% 200%;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
  animation: star-pulse 4s infinite ease-in-out, shimmer 4s infinite linear;
}

/* 
   INTERACTION: FLARE UP 
   Brighter halo and faster shimmer on hover
*/
.tool-header:hover .supernova {
  transform: scale(1.15);
  animation-duration: 1.5s; /* Speed up pulse */
}

/* Intense Glows on Hover (Double shadow for depth) */
.tool-header:hover .supernova.blue {
  box-shadow: 0 0 20px 6px #60a5fa, 0 0 40px 12px rgba(59, 130, 246, 0.4);
}
.tool-header:hover .supernova.purple {
  box-shadow: 0 0 20px 6px #c084fc, 0 0 40px 12px rgba(168, 85, 247, 0.4);
}
.tool-header:hover .supernova.cyan {
  box-shadow: 0 0 20px 6px #67e8f9, 0 0 40px 12px rgba(34, 211, 238, 0.4);
}
.tool-header:hover .supernova.orange {
  box-shadow: 0 0 20px 6px #fb923c, 0 0 40px 12px rgba(249, 115, 22, 0.4);
}

@keyframes star-pulse {
  0%, 100% { opacity: 0.85; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

@keyframes shimmer {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}


/* --------------------------------------
   EXISTING SIDEBAR STYLES
   -------------------------------------- */
.sidebar-tab {
  position: fixed; top: 0; left: 0; bottom: 0; width: 64px; z-index: 1100;
  background: rgba(15, 15, 30, 0.6); border-right: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px); cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: transform 0.3s ease, opacity 0.3s;
}
.sidebar-tab:hover { background: rgba(255, 255, 255, 0.05); }
.sidebar-tab.hidden { transform: translateX(-100%); opacity: 0; pointer-events: none; }

.burger-icon { display: flex; flex-direction: column; gap: 5px; }
.burger-icon span { width: 20px; height: 2px; background: #00d9ff; border-radius: 2px; transition: 0.3s; }
.sidebar-tab:hover span { background: #fff; }

.sidebar-backdrop { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.6); z-index: 1105; backdrop-filter: blur(2px); }

.sidebar {
  position: fixed; top: 0; left: 0; bottom: 0; width: 280px; z-index: 1110;
  background: rgba(20, 22, 28, 0.95); border-right: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(40px) saturate(180%); display: flex; flex-direction: column;
  transform: translateX(-100%); transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 20px 0 50px rgba(0, 0, 0, 0.5);
}
.sidebar.sidebar--open { transform: translateX(0); }

.sidebar-header {
  height: 64px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); flex-shrink: 0;
}
.app-logo { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 0.05em; }
.highlight { color: #00d9ff; }
.close-btn { background: none; border: none; color: rgba(255, 255, 255, 0.5); font-size: 18px; cursor: pointer; }
.close-btn:hover { color: #fff; }

.sidebar-tools { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.custom-scroll { scrollbar-width: thin; scrollbar-color: rgba(255, 255, 255, 0.1) transparent; }
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 2px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }

/* HOME entry */
.home-entry {
  display: flex; align-items: center; gap: 10px; padding: 10px 12px;
  border-radius: 12px;
  background: radial-gradient(circle at 0 0, rgba(148, 163, 184, 0.25), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(148, 163, 184, 0.5);
  text-decoration: none; color: #e5e7eb; box-shadow: 0 16px 40px rgba(15, 23, 42, 0.9);
  transition: all 0.2s ease;
}
.home-entry:hover {
  background: radial-gradient(circle at 0 0, rgba(248, 250, 252, 0.22), rgba(15, 23, 42, 0.98));
  border-color: rgba(226, 232, 240, 0.9); transform: translateY(-1px);
}
.home-entry.active { border-color: #38bdf8; box-shadow: 0 18px 45px rgba(56, 189, 248, 0.45); }

/* Keep Home Icon special (reusing supernova-home logic now inside CSS) */
.home-icon {
  width: 32px; height: 32px; border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.7);
  background: radial-gradient(circle at 0 0, rgba(248, 250, 252, 0.32), rgba(15, 23, 42, 0.96));
  display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;
}

.home-info { display: flex; flex-direction: column; gap: 1px; }
.home-title { font-size: 13px; font-weight: 600; }
.home-subtitle { font-size: 11px; color: rgba(148, 163, 184, 0.9); }

/* Tool Groups Container */
.tool-group {
  background: rgba(255, 255, 255, 0.03); border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden; transition: background 0.2s, border-color 0.2s; flex-shrink: 0;
}
.tool-group:hover { border-color: rgba(255, 255, 255, 0.1); }

/* Tool Header Button */
.tool-header {
  width: 100%; display: flex; align-items: center; gap: 12px; padding: 12px;
  background: transparent; border: none; cursor: pointer; text-align: left;
  transition: background 0.2s;
}
.tool-header:hover:not(.disabled) { background: rgba(255, 255, 255, 0.05); }
.tool-header.expanded { background: rgba(255, 255, 255, 0.02); }

/* Tool Info Text */
.tool-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.tool-title { font-size: 13px; font-weight: 600; color: #fff; }
.tool-subtitle { font-size: 11px; color: rgba(255, 255, 255, 0.5); }

/* Chevron */
.chevron { color: rgba(255, 255, 255, 0.3); transition: transform 0.3s; }
.tool-header.expanded .chevron { transform: rotate(180deg); }

/* Content Wrapper */
.tool-content-wrapper { transition: max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1); overflow: hidden; }
.tool-content {
  padding: 4px 12px 12px 12px; display: flex; flex-direction: column; gap: 2px;
  border-top: 1px solid rgba(255, 255, 255, 0.03);
}

/* Nav Items */
.nav-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px;
  color: rgba(255, 255, 255, 0.7); text-decoration: none; font-size: 13px; transition: all 0.2s;
}
.nav-item:hover { background: rgba(255, 255, 255, 0.05); color: #fff; }
.nav-item.active { background: rgba(0, 217, 255, 0.15); color: #00d9ff; font-weight: 500; }
.nav-item.coming-soon { opacity: 0.6; cursor: default; }
.nav-icon { width: 18px; text-align: center; font-size: 14px; }
.nav-badge { margin-left: auto; font-size: 10px; background: #ff006e; color: #fff; padding: 1px 5px; border-radius: 4px; font-weight: 700; }
.nav-soon { margin-left: auto; font-size: 9px; border: 1px solid rgba(255, 255, 255, 0.2); color: rgba(255, 255, 255, 0.5); padding: 1px 4px; border-radius: 4px; text-transform: uppercase; }

/* Footer */
.sidebar-divider { height: 1px; background: rgba(255, 255, 255, 0.05); margin: 0 20px; flex-shrink: 0; }
.sidebar-footer { padding: 16px 20px; border-top: 1px solid rgba(255, 255, 255, 0.05); background: rgba(0, 0, 0, 0.2); flex-shrink: 0; margin-top: auto; }
.status-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; }
.status-row:last-child { margin-bottom: 0; }
.lbl { color: rgba(255, 255, 255, 0.4); }
.val { color: #fff; font-weight: 500; }
.val.connected { color: #4ade80; }
.val.mono { font-family: monospace; }
</style>