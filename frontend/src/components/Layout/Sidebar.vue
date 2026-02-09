<!-- src/components/layout/Sidebar.vue - Brutalist Design -->
<template>
  <div v-bind="$attrs" class="sidebar-wrapper">
    <!-- Narrow Tab Bar (Left Strip) -->
    <div
      class="sidebar-tab"
      @click="toggleSidebar"
      :class="{ hidden: isSidebarOpen }"
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
    <aside
      ref="sidebarRef"
      class="sidebar"
      :class="{ 'sidebar--open': isSidebarOpen }"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    >
      <div class="sidebar-header">
        <span class="app-logo font-anton">STOCHASTIC</span>
        <button class="close-btn" @click="closeSidebar">&times;</button>
      </div>

      <!-- Tools Navigation -->
      <nav class="sidebar-tools custom-scrollbar">

        <!-- HOME -->
        <router-link
          to="/"
          class="nav-entry"
          :class="{ active: isActive('/') }"
          @click="closeSidebar"
        >
          <div class="nav-indicator"></div>
          <div class="nav-info">
            <div class="nav-title font-oswald">ГЛАВНАЯ</div>
            <div class="nav-subtitle font-mono">Обзор инструментов</div>
          </div>
          <span class="nav-arrow font-mono">&rarr;</span>
        </router-link>

        <!-- Документация -->
        <router-link
          to="/docs"
          class="nav-entry"
          :class="{ active: isActive('/docs') }"
          @click="closeSidebar"
        >
          <div class="nav-indicator green"></div>
          <div class="nav-info">
            <div class="nav-title font-oswald">ДОКУМЕНТАЦИЯ</div>
            <div class="nav-subtitle font-mono">Как работать с этим приложением?</div>
          </div>
          <span class="nav-arrow font-mono">&rarr;</span>
        </router-link>

        <!-- Терминал -->
        <router-link
          to="/terminal"
          class="nav-entry terminal-entry"
          :class="{ active: isActive('/terminal') }"
          @click="closeSidebar"
        >
          <div class="zeta-icon font-anton">&zeta;</div>
          <div class="nav-info">
            <div class="nav-title font-oswald">ДЗЕТА-ТЕРМИНАЛ</div>
            <div class="nav-subtitle font-mono">Потоковые данные в реальном времени</div>
          </div>
          <span class="nav-arrow font-mono">&rarr;</span>
        </router-link>

        <!-- Divider -->
        <div class="sidebar-divider"></div>

        <!-- Tool Groups -->
        <div
          v-for="(group, key) in toolGroups"
          :key="key"
          class="tool-group"
        >
          <button
            class="tool-header"
            @click="toggleTool(key)"
            :class="{ expanded: expandedTools[key] }"
          >
            <div class="tool-indicator" :class="group.color"></div>
            <div class="tool-info">
              <span class="tool-title font-oswald">{{ group.title }}</span>
              <span class="tool-subtitle font-mono">{{ group.subtitle }}</span>
            </div>
            <div class="chevron">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </div>
          </button>

          <div
            class="tool-content-wrapper"
            :style="{ maxHeight: expandedTools[key] ? '600px' : '0' }"
          >
            <div class="tool-content">
              <router-link
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="nav-item"
                :class="{ active: isActive(item.path), 'coming-soon': item.soon }"
                @click="closeSidebar"
              >
                <span class="nav-label font-mono">{{ item.label }}</span>
                <span v-if="item.soon" class="nav-soon font-mono">SOON</span>
              </router-link>
            </div>
          </div>
        </div>
      </nav>

      <div class="sidebar-divider"></div>

      <!-- Settings Link -->
      <router-link
        to="/settings"
        class="settings-link"
        :class="{ active: isActive('/settings') }"
        @click="closeSidebar"
      >
        <div class="nav-indicator pink"></div>
        <div class="nav-info">
          <span class="nav-title font-oswald">ПАРАМЕТРЫ</span>
          <span class="nav-subtitle font-mono">Конфигурация</span>
        </div>
        <span class="nav-arrow font-mono">&rarr;</span>
      </router-link>

      <!-- Footer Status -->
      <div class="sidebar-footer">
        <div class="status-row">
          <span class="lbl font-mono">API</span>
          <span class="val online font-mono">● ONLINE</span>
        </div>
        <div class="status-row">
          <span class="lbl font-mono">TIME</span>
          <span class="val font-mono">{{ marketTime }}</span>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const marketTime = ref('--:--')
const isSidebarOpen = ref(false)

const touchStartX = ref(0)
const touchEndX = ref(0)
const sidebarRef = ref<HTMLElement | null>(null)

const expandedTools = reactive<Record<string, boolean>>({
  portfolio: false,
  risk: false,
  quant: false,
  bonds: false,
  bondReports: false,
  options: false,
  swaps: false,
  forwards: false,
})

const toolGroups = {
  portfolio: {
    title: 'ПОРТФЕЛЬНЫЙ АНАЛИЗ',
    subtitle: 'Анализ и оптимизация',
    color: 'purple',
    items: [
      { path: '/portfolio', label: 'Состав портфеля' },
      { path: '/CCMVoptimization', label: 'Оптимизация портфеля' },
      { path: '/greeks', label: 'Риск-метрики' },
      { path: '/reports', label: 'Отчёты' },
    ]
  },
  risk: {
    title: 'РИСК-МЕНЕДЖМЕНТ',
    subtitle: 'Бэктестинг, стресс-тестирование',
    color: 'purple',
    items: [
      { path: '/backtest', label: 'Бэктестинг' },
      { path: '/stress', label: 'Стресс-тестирование портфеля облигаций' },
      { path: '/stress/swaps', label: 'Стресс-тестирование портфеля СВОПов' },
    ]
  },
  quant: {
    title: 'АНАЛИЗ РЫНОЧНЫХ РЕЖИМОВ',
    subtitle: 'Модели и режимы',
    color: 'indigo',
    items: [
      { path: '/regimes', label: 'Рыночные режимы' },
      { path: '/regime-details', label: 'Детальный анализ режимов' },
      { path: '/spectral-regimes', label: 'Комплексный анализ режимов' },
      { path: '/fixed-income', label: 'Доходности облигаций' },
    ]
  },
  bonds: {
    title: 'СПРАВЕДЛИВАЯ СТОИМОСТЬ ОБЛИГАЦИЙ',
    subtitle: 'Оценка и анализ',
    color: 'green',
    items: [
      { path: '/bond-valuation', label: 'Оценка облигаций' },
      { path: '/zcyc-viewer', label: 'Кривая бескупонной доходности' },
      { path: '/bond-report', label: 'Отчет об оценке' },
    ]
  },
  options: {
    title: 'ОПЦИОНЫ',
    subtitle: 'Справедливая стоимость',
    color: 'green',
    items: [
      { path: '/pricing/options', label: 'Справедливая стоимость опционов' },
      { path: '/pricing/options/models', label: 'Сравнение моделей' },
      { path: '/pricing/options/greeks', label: 'Анализ Greeks' },
      { path: '/pricing/options/portfolio', label: 'Портфель опционов' },
      { path: '/analytics/volatility', label: 'Поверхность волатильности' },
    ]
  },
  swaps: {
    title: 'СВОПЫ',
    subtitle: 'Greeks, Pricing & Risk',
    color: 'green',
    items: [
      { path: '/valuation/swaps', label: 'Справедливая стоимость СВОПов' },
      { path: '/swap-greeks', label: 'Греки' },
      { path: '/analytics/pnl', label: 'Факторная декомпозиция P&L' },
      { path: '/hedging', label: 'Регрессионное хеджирование' },
      { path: '/reports/swaps', label: 'Отчеты по СВОПам', soon: true },
    ]
  },
  forwards: {
    title: 'ФОРВАРДЫ',
    subtitle: 'Оценка справедливой стоимости',
    color: 'green',
    items: [
      { path: '/valuation/forwards', label: 'Оценка форвардов' },
      { path: '/forwards/curve', label: 'Построение форвардной кривой' },
      { path: '/forwards/greeks', label: 'Греки' },
      { path: '/forwards/basis', label: 'Анализ спот-форвард базиса' },
    ]
  },
  bondReports: {
    title: 'ОТЧЁТЫ ПО ОБЛИГАЦИЯМ',
    subtitle: 'Шаблонные отчеты',
    color: 'red',
    items: [
      { path: '/vanila-bond-report', label: 'Vanila Bond Report' },
      { path: '/floater-bond-report', label: 'Floater Bond Report' },
    ]
  },
}

const toggleTool = (id: string) => {
  expandedTools[id] = !expandedTools[id]
}

const isActive = (path: string): boolean => {
  return route.path === path
}

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  isSidebarOpen.value = false
}

const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.changedTouches[0].screenX
}

const handleTouchMove = (e: TouchEvent) => {
  touchEndX.value = e.changedTouches[0].screenX
}

const handleTouchEnd = () => {
  const swipeDistance = touchStartX.value - touchEndX.value
  if (swipeDistance > 50 && isSidebarOpen.value) {
    closeSidebar()
  }
}

const updateTime = () => {
  marketTime.value = new Date().toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

let timer: ReturnType<typeof setInterval>
onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
/* ============================================
   SIDEBAR WRAPPER
   ============================================ */
.sidebar-wrapper {
  position: relative;
}

/* ============================================
   SIDEBAR TAB - BRUTALIST
   ============================================ */
.sidebar-tab {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 64px;
  z-index: 1100;
  background: #050505;
  border-right: 1px solid #1a1a1a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.sidebar-tab:hover {
  background: #0a0a0a;
}

.sidebar-tab:hover .burger-icon span {
  background: #DC2626;
}

.sidebar-tab.hidden {
  transform: translateX(-100%);
  opacity: 0;
  pointer-events: none;
}

.burger-icon {
  display: flex;
  flex-direction: column;
  gap: 5px;
  pointer-events: none;
}

.burger-icon span {
  width: 20px;
  height: 2px;
  background: #525252;
  transition: background 0.2s;
}

/* ============================================
   BACKDROP
   ============================================ */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 1105;
  animation: fade-in 0.2s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ============================================
   SIDEBAR PANEL - BRUTALIST
   ============================================ */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 300px;
  z-index: 1110;
  background: #050505;
  border-right: 1px solid #262626;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow: hidden;
}

.sidebar.sidebar--open {
  transform: translateX(0);
}

/* ============================================
   HEADER
   ============================================ */
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #1a1a1a;
  flex-shrink: 0;
}

.app-logo {
  font-size: 18px;
  color: #DC2626;
  letter-spacing: 0.05em;
}

.close-btn {
  background: none;
  border: none;
  color: #525252;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s;
  line-height: 1;
}

.close-btn:hover {
  color: #DC2626;
}

/* ============================================
   NAVIGATION TOOLS
   ============================================ */
.sidebar-tools {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  -webkit-overflow-scrolling: touch;
}

/* ============================================
   NAV ENTRY - BRUTALIST
   ============================================ */
.nav-entry {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid #1a1a1a;
  text-decoration: none;
  color: #e5e5e5;
  transition: all 0.2s;
}

.nav-entry:hover {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.nav-entry:hover .nav-subtitle,
.nav-entry:hover .nav-arrow {
  color: #000;
}

.nav-entry.active {
  border-color: #DC2626;
  background: rgba(220, 38, 38, 0.1);
}

.nav-entry.active .nav-title {
  color: #DC2626;
}

.nav-indicator {
  width: 4px;
  height: 32px;
  background: #262626;
  flex-shrink: 0;
}

.nav-indicator.green { background: #22c55e; }
.nav-indicator.pink { background: #ec4899; }

.nav-entry:hover .nav-indicator,
.nav-entry.active .nav-indicator {
  background: #DC2626;
}

.nav-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.nav-title {
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.nav-subtitle {
  font-size: 10px;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.nav-arrow {
  color: #525252;
  font-size: 14px;
  flex-shrink: 0;
}

/* Terminal Entry - Special */
.terminal-entry {
  border-color: rgba(220, 38, 38, 0.3);
  background: rgba(220, 38, 38, 0.05);
}

.terminal-entry:hover {
  background: #DC2626;
  border-color: #DC2626;
}

.zeta-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #DC2626;
  border: 1px solid rgba(220, 38, 38, 0.3);
  flex-shrink: 0;
}

.terminal-entry:hover .zeta-icon {
  background: #000;
  border-color: #000;
}

/* ============================================
   TOOL GROUPS - BRUTALIST
   ============================================ */
.tool-group {
  border: 1px solid #1a1a1a;
  overflow: hidden;
  transition: border-color 0.2s;
}

.tool-group:hover {
  border-color: #262626;
}

.tool-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.2s;
}

.tool-header:hover {
  background: #0a0a0a;
}

.tool-header.expanded {
  background: #0a0a0a;
  border-bottom: 1px solid #1a1a1a;
}

.tool-indicator {
  width: 4px;
  height: 28px;
  background: #262626;
  flex-shrink: 0;
}

.tool-indicator.purple { background: #a855f7; }
.tool-indicator.indigo { background: #818cf8; }
.tool-indicator.green { background: #22c55e; }
.tool-indicator.red { background: #DC2626; }
.tool-indicator.pink { background: #ec4899; }

.tool-header:hover .tool-indicator {
  background: #DC2626;
}

.tool-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.tool-title {
  font-size: 12px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.tool-subtitle {
  font-size: 10px;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chevron {
  color: #525252;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.tool-header.expanded .chevron {
  transform: rotate(180deg);
}

.tool-content-wrapper {
  transition: max-height 0.3s ease;
  overflow: hidden;
}

.tool-content {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: #0a0a0a;
}

/* ============================================
   NAV ITEMS - BRUTALIST
   ============================================ */
.nav-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  color: #a3a3a3;
  text-decoration: none;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #DC2626;
  color: #000;
}

.nav-item.active {
  color: #DC2626;
  background: rgba(220, 38, 38, 0.1);
}

.nav-item.coming-soon {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-label {
  flex: 1;
}

.nav-soon {
  font-size: 9px;
  border: 1px solid currentColor;
  padding: 1px 4px;
  flex-shrink: 0;
}

/* ============================================
   SETTINGS LINK
   ============================================ */
.settings-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid #1a1a1a;
  text-decoration: none;
  color: #e5e5e5;
  transition: all 0.2s;
}

.settings-link:hover {
  background: #DC2626;
  color: #000;
}

.settings-link:hover .nav-subtitle,
.settings-link:hover .nav-arrow {
  color: #000;
}

.settings-link.active {
  background: rgba(220, 38, 38, 0.1);
}

.settings-link.active .nav-title {
  color: #DC2626;
}

/* ============================================
   DIVIDER & FOOTER
   ============================================ */
.sidebar-divider {
  height: 1px;
  background: #1a1a1a;
  margin: 8px 16px;
  flex-shrink: 0;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid #1a1a1a;
  background: #050505;
  flex-shrink: 0;
}

.status-row {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  margin-bottom: 6px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.status-row:last-child {
  margin-bottom: 0;
}

.lbl {
  color: #525252;
}

.val {
  color: #a3a3a3;
}

.val.online {
  color: #22c55e;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .sidebar-tab {
    width: 56px;
    padding-top: env(safe-area-inset-top, 0);
  }

  .sidebar {
    width: 85vw;
    max-width: 320px;
    padding-top: env(safe-area-inset-top, 0);
    padding-bottom: env(safe-area-inset-bottom, 0);
  }

  .sidebar-header {
    padding-top: calc(16px + env(safe-area-inset-top, 0));
  }

  .sidebar-footer {
    padding-bottom: calc(16px + env(safe-area-inset-bottom, 0));
  }

  .nav-item,
  .tool-header,
  .nav-entry {
    min-height: 44px;
  }
}

@media (max-width: 480px) {
  .sidebar-tab {
    width: 48px;
  }

  .sidebar {
    width: 100%;
    max-width: none;
  }

  .app-logo {
    font-size: 16px;
  }

  .tool-title,
  .nav-title {
    font-size: 11px;
  }

  .tool-subtitle,
  .nav-subtitle {
    font-size: 9px;
  }
}

@media (max-width: 375px) {
  .sidebar-tab {
    width: 44px;
  }

  .burger-icon span {
    width: 18px;
  }

  .sidebar-tools {
    padding: 12px;
    gap: 6px;
  }
}
</style>
