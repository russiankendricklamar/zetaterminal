<!-- src/components/layout/Sidebar.vue - Brutalist Design with Animations -->
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
      <!-- Header with Marquee -->
      <div class="sidebar-header">
        <div class="logo-marquee">
          <div class="marquee-track">
            <span class="font-anton">STOCHASTIC &mdash; QUANT &mdash; RISK &mdash; SIGMA &mdash;&nbsp;</span>
            <span class="font-anton">STOCHASTIC &mdash; QUANT &mdash; RISK &mdash; SIGMA &mdash;&nbsp;</span>
          </div>
        </div>
        <button class="close-btn" @click="closeSidebar">&times;</button>
      </div>

      <!-- Tools Navigation -->
      <nav class="sidebar-tools custom-scrollbar">

        <!-- HOME -->
        <router-link
          to="/"
          class="nav-entry"
          :class="{ active: isActive('/') }"
          @click.native="handleNavClick"
        >
          <span class="nav-index font-mono">01</span>
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
          @click.native="handleNavClick"
        >
          <span class="nav-index font-mono">02</span>
          <div class="nav-info">
            <div class="nav-title font-oswald">ДОКУМЕНТАЦИЯ</div>
            <div class="nav-subtitle font-mono">Как работать с приложением</div>
          </div>
          <span class="nav-arrow font-mono">&rarr;</span>
        </router-link>

        <!-- Терминал -->
        <router-link
          to="/terminal"
          class="nav-entry terminal-entry"
          :class="{ active: isActive('/terminal') }"
          @click.native="handleNavClick"
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
          v-for="(group, key, groupIndex) in toolGroups"
          :key="key"
          class="tool-group"
          :style="{ '--group-index': groupIndex }"
        >
          <button
            class="tool-header"
            @click="toggleTool(key, $event)"
            :class="{ expanded: expandedTools[key] }"
          >
            <span class="tool-index font-mono">{{ String(groupIndex + 3).padStart(2, '0') }}</span>
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
            :class="{ expanded: expandedTools[key] }"
          >
            <div class="tool-content">
              <template v-for="(item, itemIndex) in group.items" :key="item.path || item.label">
                <div v-if="item.section" class="section-label font-mono">{{ item.label }}</div>
                <router-link
                  v-else
                  :to="item.path"
                  class="nav-item"
                  :class="{ active: isActive(item.path), 'coming-soon': item.soon }"
                  :style="{ '--item-index': itemIndex }"
                  @click.native="!item.soon && handleNavClick($event)"
                >
                  <span class="item-dot"></span>
                  <span class="nav-label font-mono">{{ item.label }}</span>
                  <span v-if="item.soon" class="nav-soon font-mono">SOON</span>
                  <span v-else class="item-arrow font-mono">&rarr;</span>
                </router-link>
              </template>
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
        @click.native="handleNavClick"
      >
        <span class="nav-index font-mono">&#9881;</span>
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
          <span class="val online font-mono">
            <span class="pulse-dot"></span>
            ONLINE
          </span>
        </div>
        <div class="status-row">
          <span class="lbl font-mono">TIME</span>
          <span class="val font-mono">{{ marketTime }}</span>
        </div>
        <div class="version-tag font-mono">v2.0 BRUTALIST</div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const marketTime = ref('--:--')
const isSidebarOpen = ref(false)

const touchStartX = ref(0)
const touchEndX = ref(0)
const sidebarRef = ref<HTMLElement | null>(null)

const expandedTools = reactive<Record<string, boolean>>({
  portfolio: false,
  riskAnalytics: false,
  signalsModels: false,
  bonds: false,
  derivatives: false,
})

const toolGroups = {
  portfolio: {
    title: 'ПОРТФЕЛЬ',
    subtitle: 'Анализ и оптимизация',
    items: [
      { path: '/portfolio', label: 'Состав портфеля' },
      { path: '/optimization', label: 'Оптимизация портфеля' },
      { path: '/greeks', label: 'Риск-метрики' },
      { path: '/reports', label: 'Отчёты' },
    ]
  },
  riskAnalytics: {
    title: 'РИСК И АНАЛИТИКА',
    subtitle: 'Стресс-тесты, статистика, факторы',
    items: [
      { path: '/backtest', label: 'Бэктестинг' },
      { path: '/stress', label: 'Стресс-тестирование' },
      { path: '/analytics/adversarial-stress', label: 'Adversarial Stress' },
      { path: '/analytics/pbo', label: 'PBO / DSR' },
      { path: '/analytics/sharpe-stats', label: 'Статистика Шарпа' },
      { path: '/analytics/realized-kernels', label: 'Realized Kernels' },
      { path: '/analytics/har-model', label: 'HAR Model' },
      { path: '/analytics/factor-analysis', label: 'Factor Analysis' },
    ]
  },
  signalsModels: {
    title: 'СИГНАЛЫ И МОДЕЛИ',
    subtitle: 'Режимы, PCA, стэкинг',
    items: [
      { path: '/regimes', label: 'Рыночные режимы' },
      { path: '/spectral-regimes', label: 'Спектральный анализ режимов' },
      { path: '/analytics/eigenportfolio', label: 'Eigenportfolios (PCA)' },
      { path: '/analytics/alpha-stacking', label: 'Alpha Stacking' },
      { path: '/analytics/meta-labeling', label: 'Meta-Labeling' },
    ]
  },
  bonds: {
    title: 'ОБЛИГАЦИИ',
    subtitle: 'Доходности, оценка, отчёты',
    items: [
      { path: '/fixed-income', label: 'Доходности облигаций' },
      { path: '/bond-valuation', label: 'Оценка облигаций' },
      { path: '/zcyc-viewer', label: 'Кривая бескупонной доходности' },
      { path: '/vanila-bond-report', label: 'Vanila Bond Report' },
      { path: '/floater-bond-report', label: 'Floater Bond Report' },
    ]
  },
  derivatives: {
    title: 'ДЕРИВАТИВЫ',
    subtitle: 'Опционы, свопы, форварды',
    items: [
      { label: 'ОПЦИОНЫ', section: true },
      { path: '/pricing/options', label: 'Ценообразование' },
      { path: '/pricing/options/models', label: 'Сравнение моделей' },
      { path: '/pricing/options/greeks', label: 'Анализ Greeks' },
      { path: '/analytics/volatility', label: 'Поверхность волатильности' },
      { label: 'СВОПЫ', section: true },
      { path: '/valuation/swaps', label: 'Справедливая стоимость' },
      { path: '/swap-greeks', label: 'Греки СВОПов' },
      { path: '/analytics/pnl', label: 'Факторная декомпозиция P&L' },
      { path: '/hedging', label: 'Регрессионное хеджирование' },
      { label: 'ФОРВАРДЫ', section: true },
      { path: '/valuation/forwards', label: 'Оценка форвардов' },
      { path: '/forwards/curve', label: 'Форвардная кривая' },
    ]
  },
}

const toggleTool = (id: string, event?: Event) => {
  expandedTools[id] = !expandedTools[id]

  // Auto-scroll to show expanded content
  if (expandedTools[id] && event) {
    const target = event.currentTarget as HTMLElement
    const group = target.closest('.tool-group') as HTMLElement
    if (group) {
      setTimeout(() => {
        group.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }
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

const handleNavClick = (e?: Event) => {
  // Small delay to allow navigation to complete
  setTimeout(() => {
    closeSidebar()
  }, 50)
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
    second: '2-digit',
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

.sidebar-tab:hover .burger-icon span:nth-child(2) {
  width: 14px;
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
  transition: all 0.3s;
}

/* ============================================
   BACKDROP
   ============================================ */
.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  z-index: 1105;
  animation: fade-in 0.3s ease;
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
  width: 320px;
  z-index: 1110;
  background: #050505;
  border-right: 1px solid #DC2626;
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.sidebar.sidebar--open {
  transform: translateX(0);
}

/* ============================================
   HEADER WITH MARQUEE
   ============================================ */
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #1a1a1a;
  flex-shrink: 0;
  background: #DC2626;
  overflow: hidden;
}

.logo-marquee {
  flex: 1;
  overflow: hidden;
  mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
}

.marquee-track {
  display: flex;
  white-space: nowrap;
  animation: marquee-scroll 15s linear infinite;
}

.marquee-track span {
  font-size: 14px;
  color: #000;
  letter-spacing: 0.1em;
}

@keyframes marquee-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.close-btn {
  background: #000;
  border: none;
  color: #DC2626;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
  line-height: 1;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.close-btn:hover {
  background: #DC2626;
  color: #000;
}

/* ============================================
   NAVIGATION TOOLS - SCROLLABLE
   ============================================ */
.sidebar-tools {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  -webkit-overflow-scrolling: touch;
  min-height: 0; /* Important for flex scroll */
  scroll-behavior: smooth;
}

/* Custom scrollbar for sidebar */
.sidebar-tools::-webkit-scrollbar {
  width: 6px;
}

.sidebar-tools::-webkit-scrollbar-track {
  background: #0a0a0a;
}

.sidebar-tools::-webkit-scrollbar-thumb {
  background: #DC2626;
  border-radius: 0;
}

.sidebar-tools::-webkit-scrollbar-thumb:hover {
  background: #ef4444;
}

/* ============================================
   NAV ENTRY - BRUTALIST WITH INDEX
   ============================================ */
.nav-entry {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #1a1a1a;
  text-decoration: none;
  color: #e5e5e5;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
  flex-shrink: 0; /* Prevent compression */
}

.nav-entry::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background: #DC2626;
  transition: width 0.3s ease;
  z-index: 0;
}

.nav-entry:hover::before {
  width: 100%;
}

.nav-entry:hover {
  border-color: #DC2626;
  color: #000;
}

.nav-entry > * {
  position: relative;
  z-index: 1;
}

.nav-entry:hover .nav-subtitle,
.nav-entry:hover .nav-arrow {
  color: #000;
}

.nav-entry.active {
  border-color: #DC2626;
  background: rgba(220, 38, 38, 0.15);
}

.nav-entry.active .nav-title {
  color: #DC2626;
}

.nav-index {
  font-size: 10px;
  color: #525252;
  min-width: 20px;
}

.nav-entry:hover .nav-index {
  color: #000;
}

.nav-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.nav-title {
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.nav-subtitle {
  font-size: 9px;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.nav-arrow {
  color: #525252;
  font-size: 14px;
  flex-shrink: 0;
  transition: transform 0.2s;
}

.nav-entry:hover .nav-arrow {
  transform: translateX(4px);
}

/* Terminal Entry - Special */
.terminal-entry {
  border-color: rgba(220, 38, 38, 0.5);
  background: rgba(220, 38, 38, 0.1);
}

.zeta-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #DC2626;
  border: 1px solid rgba(220, 38, 38, 0.5);
  flex-shrink: 0;
  transition: all 0.2s;
}

.terminal-entry:hover .zeta-icon {
  background: #000;
  color: #DC2626;
  border-color: #000;
}

/* ============================================
   TOOL GROUPS - BRUTALIST WITH ANIMATION
   ============================================ */
.tool-group {
  border: 1px solid #1a1a1a;
  overflow: hidden;
  transition: border-color 0.2s;
  flex-shrink: 0; /* Prevent compression */
}

.tool-group:hover {
  border-color: #262626;
}

.tool-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}

.tool-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #262626;
  transition: all 0.3s;
}

.tool-header:hover::before,
.tool-header.expanded::before {
  background: #DC2626;
  width: 4px;
}

.tool-header:hover {
  background: #0a0a0a;
}

.tool-header.expanded {
  background: #0a0a0a;
  border-bottom: 1px solid #1a1a1a;
}

.tool-index {
  font-size: 10px;
  color: #525252;
  min-width: 20px;
  transition: color 0.2s;
}

.tool-header:hover .tool-index {
  color: #DC2626;
}

.tool-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.tool-title {
  font-size: 11px;
  font-weight: 500;
  color: #f5f5f5;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.tool-subtitle {
  font-size: 9px;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chevron {
  color: #525252;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.tool-header.expanded .chevron {
  transform: rotate(180deg);
  color: #DC2626;
}

/* Tool Content Wrapper - Animated Height */
.tool-content-wrapper {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.tool-content-wrapper.expanded {
  grid-template-rows: 1fr;
}

.tool-content {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: #0a0a0a;
  overflow: hidden;
  min-height: 0;
}

/* ============================================
   NAV ITEMS - BRUTALIST WITH STAGGER
   ============================================ */
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: #a3a3a3;
  text-decoration: none;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  transition: all 0.2s;
  position: relative;
}

.tool-content-wrapper.expanded .nav-item {
  animation: item-slide-in 0.3s ease forwards;
  animation-delay: calc(var(--item-index, 0) * 0.05s);
}

@keyframes item-slide-in {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.item-dot {
  width: 4px;
  height: 4px;
  background: #525252;
  transition: all 0.2s;
  flex-shrink: 0;
}

.nav-item:hover .item-dot {
  background: #DC2626;
  box-shadow: 0 0 8px #DC2626;
}

.nav-item:hover {
  background: #DC2626;
  color: #000;
}

.nav-item.active {
  color: #DC2626;
  background: rgba(220, 38, 38, 0.1);
}

.nav-item.active .item-dot {
  background: #DC2626;
}

.nav-item.coming-soon {
  opacity: 0.4;
  pointer-events: none;
}

.nav-label {
  flex: 1;
}

.nav-soon {
  font-size: 8px;
  border: 1px solid currentColor;
  padding: 1px 4px;
  flex-shrink: 0;
}

.section-label {
  font-size: 9px;
  color: #525252;
  letter-spacing: 0.1em;
  padding: 8px 12px 4px;
  text-transform: uppercase;
  border-top: 1px solid #1a1a1a;
}

.section-label:first-child {
  border-top: none;
  padding-top: 4px;
}

.item-arrow {
  font-size: 10px;
  color: #525252;
  transition: all 0.2s;
  opacity: 0;
  transform: translateX(-5px);
}

.nav-item:hover .item-arrow {
  opacity: 1;
  transform: translateX(0);
  color: #000;
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
  position: relative;
  overflow: hidden;
}

.settings-link::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background: #DC2626;
  transition: width 0.3s ease;
  z-index: 0;
}

.settings-link:hover::before {
  width: 100%;
}

.settings-link > * {
  position: relative;
  z-index: 1;
}

.settings-link:hover {
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
  background: linear-gradient(90deg, transparent, #1a1a1a, transparent);
  margin: 12px 16px;
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

.status-row:last-of-type {
  margin-bottom: 12px;
}

.lbl {
  color: #525252;
}

.val {
  color: #a3a3a3;
  display: flex;
  align-items: center;
  gap: 6px;
}

.val.online {
  color: #22c55e;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  background: #22c55e;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  50% { opacity: 0.6; box-shadow: 0 0 0 4px rgba(34, 197, 94, 0); }
}

.version-tag {
  font-size: 9px;
  color: #525252;
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #1a1a1a;
  letter-spacing: 0.1em;
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
    max-width: 340px;
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

  .marquee-track span {
    font-size: 12px;
  }

  .tool-title,
  .nav-title {
    font-size: 11px;
  }

  .tool-subtitle,
  .nav-subtitle {
    font-size: 8px;
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
    gap: 4px;
  }
}
</style>
