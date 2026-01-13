<!-- src/components/layout/Sidebar.vue -->
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
    <aside class="sidebar" :class="{ 'sidebar--open': isSidebarOpen }">
    <!-- Lava Lamp Background -->
    <div class="sidebar-lava-layer"></div>

    <div class="sidebar-header">
      <span class="app-logo">Quantitative <span class="highlight">Analytics</span></span>
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
          <div class="supernova-home"></div>
        </div>
        <div class="home-info">
          <div class="home-title">Главная</div>
          <div class="home-subtitle">Обзор инструментов</div>
        </div>
      </router-link>

      <!-- Документация -->
      <router-link
        to="/docs"
        class="docs-entry"
        :class="{ active: isActive('/docs') }"
        @click="closeSidebar"
      >
        <div class="home-icon">
          <div class="supernova-home"></div>
        </div>
        <div class="home-info">
          <div class="home-title">Документация</div>
          <div class="home-subtitle">Как работать с этим приложением?</div>
        </div>
      </router-link>

      <router-link
        to="/terminal"
        class="data-entry"
        :class="{ active: isActive('/terminal') }"
        @click="closeSidebar"
      >
        <div class="data-icon">
          <span class="zeta-logo">ζ</span>
        </div>
        <div class="data-info">
          <div class="data-title">Дзета-Терминал</div>
          <div class="data-subtitle">Потоковые данные в реальном времени</div>
        </div>
      </router-link>

      <!-- 1) Portfolio Analytics -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('portfolio')"
          :class="{ expanded: expandedTools.portfolio }"
        >
          <div class="glossy-icon">
            <div class="supernova purple"></div>
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
          :style="{ maxHeight: expandedTools.portfolio ? '1000px' : '0' }"
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

      <!-- 2) Risk Management -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('risk')"
          :class="{ expanded: expandedTools.risk }"
        >
          <div class="glossy-icon">
            <div class="supernova purple"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Риск-менеджмент</span>
            <span class="tool-subtitle">Бэктестинг, стресс-тестирование</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>

        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.risk ? '1000px' : '0' }"
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

      <!-- 3) Hidden Markov Chain -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('quant')"
          :class="{ expanded: expandedTools.quant }"
        >
          <div class="glossy-icon">
            <div class="supernova indigo"></div>
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
          :style="{ maxHeight: expandedTools.quant ? '1000px' : '0' }"
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

      <!-- 4) Bond Valuation -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('bonds')"
          :class="{ expanded: expandedTools.bonds }"
        >
          <div class="glossy-icon">
            <div class="supernova green"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Справедливая стоимость облигаций</span>
            <span class="tool-subtitle">Оценка и анализ</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.bonds ? '1000px' : '0' }"
        >
          <div class="tool-content">
            <router-link 
              to="/bond-valuation" 
              class="nav-item"
              :class="{ active: isActive('/bond-valuation') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Оценка облигаций</span>
            </router-link>
            
            <router-link 
              to="/zcyc-viewer" 
              class="nav-item"
              :class="{ active: isActive('/zcyc-viewer') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Кривая бескупонной доходности</span>
            </router-link>

            <router-link 
              to="/bond-report" 
              class="nav-item"
              :class="{ active: isActive('/bond-report') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Отчет об оценке</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 6) Option Pricing -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('options')"
          :class="{ expanded: expandedTools.options }"
        >
          <div class="glossy-icon">
            <div class="supernova green"></div>
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
          :style="{ maxHeight: expandedTools.options ? '1000px' : '0' }"
        >
          <div class="tool-content">
            <router-link 
              to="/pricing/options" 
              class="nav-item"
              :class="{ active: isActive('/pricing/options') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Справедливая стоимость опционов</span>
            </router-link>

            <router-link 
              to="/pricing/options/models" 
              class="nav-item"
              :class="{ active: isActive('/pricing/options/models') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Сравнение моделей</span>
            </router-link>

            <router-link 
              to="/pricing/options/greeks" 
              class="nav-item"
              :class="{ active: isActive('/pricing/options/greeks') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Анализ Greeks</span>
            </router-link>

            <router-link 
              to="/pricing/options/portfolio" 
              class="nav-item"
              :class="{ active: isActive('/pricing/options/portfolio') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Портфель опционов</span>
            </router-link>

            <router-link
              to="/analytics/volatility"
              class="nav-item"
              :class="{ active: isActive('/analytics/volatility') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Поверхность волатильности</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- 7) Swap Valuation -->
      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('swaps')"
          :class="{ expanded: expandedTools.swaps }"
        >
          <div class="glossy-icon">
            <div class="supernova green"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">СВОПы</span>
            <span class="tool-subtitle">Greeks, Pricing & Risk</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>

        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.swaps ? '1000px' : '0' }"
        >
          <div class="tool-content">
            <router-link
              to="/valuation/swaps"
              class="nav-item"
              :class="{ active: isActive('/valuation/swaps') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Справедливая стоимость СВОПов</span>
            </router-link>

            <router-link
              to="/swap-greeks"
              class="nav-item"
              :class="{ active: isActive('/swap-greeks') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Греки</span>
            </router-link>

            <router-link
              to="/analytics/pnl"
              class="nav-item"
              :class="{ active: isActive('/analytics/pnl') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Факторная декомпозиция P&L</span>
            </router-link>

            <router-link
              to="/hedging"
              class="nav-item"
              :class="{ active: isActive('/hedging') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Регрессионное хеджирование</span>
            </router-link>

            <router-link
              to="/reports/swaps"
              class="nav-item coming-soon"
            >
              <span class="nav-label">Отчеты по СВОПам</span>
              <span class="nav-soon">SOON</span>
            </router-link>
          </div>
        </div>
      </div>

      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('forwards')"
          :class="{ expanded: expandedTools.forwards }"
        >
          <div class="glossy-icon">
            <div class="supernova green"></div>
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
          :style="{ maxHeight: expandedTools.forwards ? '1000px' : '0' }"
        >
          <div class="tool-content">
            <router-link
              to="/valuation/forwards"
              class="nav-item"
              :class="{ active: isActive('/valuation/forwards') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Оценка форвардов</span>
            </router-link>

            <router-link
              to="/forwards/curve"
              class="nav-item"
              :class="{ active: isActive('/forwards/curve') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Построение форвардной кривой</span>
            </router-link>

            <router-link
              to="/forwards/greeks"
              class="nav-item"
              :class="{ active: isActive('/forwards/greeks') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Греки</span>
            </router-link>

            <router-link
              to="/forwards/basis"
              class="nav-item"
              :class="{ active: isActive('/forwards/basis') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Анализ спот-форвард базиса</span>
            </router-link>
          </div>
        </div>
      </div>

      <div class="tool-group">
        <button
          class="tool-header"
          @click="toggleTool('bondReports')"
          :class="{ expanded: expandedTools.bondReports }"
        >
          <div class="glossy-icon">
            <div class="supernova nova"></div>
          </div>
          <div class="tool-info">
            <span class="tool-title">Отчёты по облигациям</span>
            <span class="tool-subtitle">Шаблонные отчеты</span>
          </div>
          <div class="chevron">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </button>
        <div
          class="tool-content-wrapper"
          :style="{ maxHeight: expandedTools.bondReports ? '1000px' : '0' }"
        >
          <div class="tool-content">
            <router-link 
              to="/vanila-bond-report" 
              class="nav-item"
              :class="{ active: isActive('/vanila-bond-report') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Vanila Bond Report</span>
            </router-link>
            <router-link 
              to="/floater-bond-report" 
              class="nav-item"
              :class="{ active: isActive('/floater-bond-report') }"
              @click="closeSidebar"
            >
              <span class="nav-label">Floater Bond Report</span>
            </router-link>
          </div>
        </div>
      </div>

    </nav>

    <div class="sidebar-divider"></div>

    <!-- SETTINGS LINK (Bottom) -->
    <router-link
      to="/settings"
      class="settings-link-button"
      :class="{ active: isActive('/settings') }"
      @click="closeSidebar"
    >
      <div class="settings-glossy-icon">
        <div class="supernova pink"></div>
      </div>
      <div class="settings-info">
        <span class="settings-title">Параметры</span>
        <span class="settings-subtitle">Конфигурация</span>
      </div>
      <svg class="settings-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="9 18 15 12 9 6" />
      </svg>
    </router-link>

    <!-- Footer Status -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const marketTime = ref('--:--')
const isSidebarOpen = ref(false)

const expandedTools = reactive({
  portfolio: false,
  risk: false,
  quant: false,
  bonds: false,
  bondReports: false,
  options: false,
  swaps: false,
  forwards: false,

})

const toggleTool = (id: keyof typeof expandedTools) => {
  expandedTools[id] = !expandedTools[id]
}

const portfolioItems = [
  { path: '/portfolio', label: 'Состав портфеля' },
  { path: '/CCMVoptimization', label: 'Оптимизация портфеля' },
  { path: '/greeks', label: 'Риск-метрики' },
  { path: '/reports', label: 'Отчёты' },
]

const riskItems = [
  { path: '/backtest', label: 'Бэктестинг' },
  { path: '/stress', label: 'Стресс-тестирование портфеля облигаций' },
  { path: '/stress/swaps', label: 'Стресс-тестирование портфеля СВОПов' },
]

const quantItems = [
  { path: '/regimes', label: 'Рыночные режимы' },
  { path: '/regime-details', label: 'Детальный анализ режимов' },
  { path: '/fixed-income', label: 'Доходности облигаций' },
]

const isActive = (path: string): boolean => {
  return route.path === path
}

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
/* ============================================
   LAVA LAMP BACKGROUND — СТАТИЧЕСКИЙ ФОН
   ============================================ */
.sidebar-lava-layer {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle 80px at 30% 20%, rgba(99, 102, 241, 0.15), transparent 60%),
    radial-gradient(circle 60px at 60% 60%, rgba(34, 211, 238, 0.12), transparent 50%),
    radial-gradient(circle 70px at 20% 80%, rgba(168, 85, 247, 0.12), transparent 55%);
  filter: blur(30px);
  pointer-events: none;
  z-index: 1;
  backface-visibility: hidden;
}

/* ============================================
   GLOSSY ICON
   ============================================ */
.glossy-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02) 80%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  transition: transform 0.3s ease, border-color 0.3s ease;
  backface-visibility: hidden;
}

.tool-header:hover .glossy-icon {
  transform: translateY(-1px);
  border-color: rgba(255, 255, 255, 0.3);
}

/* ============================================
   SUPERNOVA — БЕЗ АНИМАЦИЙ
   ============================================ */
.supernova {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: relative;
  z-index: 2;
  backface-visibility: hidden;
}

.supernova.blue { 
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #1e40af 100%);
  box-shadow: 0 0 12px 2px rgba(59, 130, 246, 0.8);
}

.supernova.purple { 
  background: linear-gradient(135deg, #c084fc 0%, #a855f7 50%, #7e22ce 100%);
  box-shadow: 0 0 12px 2px rgba(168, 85, 247, 0.8);
}

.supernova.cyan { 
  background: linear-gradient(135deg, #67e8f9 0%, #22d3ee 50%, #0891b2 100%);
  box-shadow: 0 0 12px 2px rgba(34, 211, 238, 0.8);
}

.supernova.green { 
  background: linear-gradient(135deg, #4ade80 0%, #22c55e 50%, #15803d 100%);
  box-shadow: 0 0 12px 2px rgba(34, 197, 94, 0.8);
}

.supernova.pink { 
  background: linear-gradient(135deg, #f472b6 0%, #ec4899 50%, #be185d 100%);
  box-shadow: 0 0 12px 2px rgba(236, 72, 153, 0.8);
}

.supernova.nova {
  background: linear-gradient(135deg, #ff3366 0%, #ff99cc 33%, #ff6699 66%, #ff3366 100%);
  box-shadow: 0 0 12px 2px rgba(255, 51, 102, 0.85), 0 0 20px 4px rgba(255, 102, 153, 0.5);
}

.supernova.yellow {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
  box-shadow: 0 0 12px 2px rgba(251, 191, 36, 0.85);
}

.supernova.indigo {
  background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 50%, #4f46e5 100%);
  box-shadow: 0 0 12px 2px rgba(129, 140, 248, 0.85);
}

.supernova.red {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 50%, #b91c1c 100%);
  box-shadow: 0 0 12px 2px rgba(239, 68, 68, 0.85);
}

.supernova.violet {
  background: linear-gradient(135deg, #d8b4fe 0%, #c4b5fd 50%, #7c3aed 100%);
  box-shadow: 0 0 12px 2px rgba(124, 58, 237, 0.85);
}

.supernova-home {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22d3ee, #ffffff, #6366f1);
  background-size: 200% 200%;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.8);
  backface-visibility: hidden;
}

/* Hover states — только box-shadow */
.tool-header:hover .supernova.blue { 
  box-shadow: 0 0 18px 4px rgba(96, 165, 250, 0.9), 0 0 32px 8px rgba(59, 130, 246, 0.4);
}
.tool-header:hover .supernova.purple { 
  box-shadow: 0 0 18px 4px rgba(192, 132, 252, 0.9), 0 0 32px 8px rgba(168, 85, 247, 0.4);
}
.tool-header:hover .supernova.cyan { 
  box-shadow: 0 0 18px 4px rgba(103, 232, 249, 0.9), 0 0 32px 8px rgba(34, 211, 238, 0.4);
}
.tool-header:hover .supernova.green { 
  box-shadow: 0 0 18px 4px rgba(74, 222, 128, 0.9), 0 0 32px 8px rgba(34, 197, 94, 0.4);
}
.tool-header:hover .supernova.pink { 
  box-shadow: 0 0 18px 4px rgba(244, 114, 182, 0.9), 0 0 32px 8px rgba(236, 72, 153, 0.4);
}
.tool-header:hover .supernova.nova { 
  box-shadow: 0 0 18px 4px rgba(255, 51, 102, 0.95), 0 0 32px 8px rgba(255, 102, 153, 0.5);
}
.tool-header:hover .supernova.yellow { 
  box-shadow: 0 0 18px 4px rgba(251, 191, 36, 0.95), 0 0 32px 8px rgba(251, 191, 36, 0.4);
}
.tool-header:hover .supernova.indigo { 
  box-shadow: 0 0 18px 4px rgba(165, 180, 252, 0.9), 0 0 32px 8px rgba(129, 140, 248, 0.4);
}
.tool-header:hover .supernova.red { 
  box-shadow: 0 0 18px 4px rgba(248, 113, 113, 0.9), 0 0 32px 8px rgba(239, 68, 68, 0.4);
}
.tool-header:hover .supernova.violet { 
  box-shadow: 0 0 18px 4px rgba(216, 180, 254, 0.9), 0 0 32px 8px rgba(124, 58, 237, 0.4);
}

/* ============================================
   SIDEBAR LAYOUT
   ============================================ */
.sidebar-wrapper {
  position: relative;
}

.sidebar-tab {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 64px;
  z-index: 1100;
  background: rgba(15, 15, 30, 0.6);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, opacity;
  backface-visibility: hidden;
  touch-action: manipulation;
}

.sidebar-tab:hover {
  background: rgba(255, 255, 255, 0.05);
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
  background: #00d9ff;
  border-radius: 2px;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backface-visibility: hidden;
}

.sidebar-tab:hover span {
  background: #fff;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1105;
  backdrop-filter: blur(2px);
  animation: fade-in 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backface-visibility: hidden;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  z-index: 1110;
  background: rgba(20, 22, 28, 0.95);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(40px) saturate(180%);
  display: flex;
  flex-direction: column;
  transform: translateX(-100%);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
  box-shadow: 20px 0 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  backface-visibility: hidden;
}

.sidebar.sidebar--open {
  transform: translateX(0);
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.app-logo {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.05em;
}

.highlight {
  color: #00d9ff;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 4px;
  backface-visibility: hidden;
}

.close-btn:hover {
  color: #fff;
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
  gap: 12px;
  position: relative;
  z-index: 5;
  -webkit-overflow-scrolling: touch;
}

.custom-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.15) transparent;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

.custom-scroll::-webkit-scrollbar {
  width: 6px;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backface-visibility: hidden;
  border: 1px solid transparent;
  background-clip: padding-box;
}

.custom-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.custom-scroll::-webkit-scrollbar-thumb:active {
  background: rgba(255, 255, 255, 0.35);
}

.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 10px;
}

/* HOME ENTRY */
.home-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: radial-gradient(circle at 0 0, rgba(148, 163, 184, 0.25), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(148, 163, 184, 0.5);
  text-decoration: none;
  color: #e5e7eb;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 8px;
  backface-visibility: hidden;
}

.home-entry:hover {
  background: radial-gradient(circle at 0 0, rgba(248, 250, 252, 0.22), rgba(15, 23, 42, 0.98));
  border-color: rgba(226, 232, 240, 0.9);
  transform: translateY(-1px);
}

.home-entry.active {
  border-color: #38bdf8;
  box-shadow: 0 18px 45px rgba(56, 189, 248, 0.45);
}

.home-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.7);
  background: radial-gradient(circle at 0 0, rgba(248, 250, 252, 0.32), rgba(15, 23, 42, 0.96));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  backface-visibility: hidden;
}

.home-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.home-title {
  font-size: 13px;
  font-weight: 600;
}

.home-subtitle {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.9);
}

.docs-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: radial-gradient(circle at 0 0, rgba(74, 222, 128, 0.12), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(34, 197, 94, 0.6);
  text-decoration: none;
  color: #e5e7eb;
  box-shadow: 0 16px 40px rgba(34, 197, 94, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 8px;
  backface-visibility: hidden;
}

.docs-entry:hover {
  background: radial-gradient(circle at 0 0, rgba(74, 222, 128, 0.18), rgba(15, 23, 42, 0.98));
  border-color: rgba(34, 197, 94, 0.9);
  transform: translateY(-1px);
}

.docs-entry.active {
  border-color: #22c55e;
  box-shadow: 0 18px 45px rgba(34, 197, 94, 0.45);
}

.docs-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.7);
  background: radial-gradient(circle at 0 0, rgba(248, 250, 252, 0.32), rgba(15, 23, 42, 0.96));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  backface-visibility: hidden;
}

.docs-entry .home-icon {
  border: 1px solid rgba(34, 197, 94, 0.7);
  background: radial-gradient(circle at 0 0, rgba(74, 222, 128, 0.32), rgba(15, 23, 42, 0.96));
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.6);
}

.docs-entry .supernova-home {
  background: linear-gradient(135deg, #4ade80, #22c55e, #10b981);
  box-shadow: 0 0 20px rgba(34, 197, 94, 0.9);
}

.docs-entry:hover .home-icon {
  border-color: rgba(34, 197, 94, 0.95);
  box-shadow: 0 0 30px rgba(74, 222, 128, 0.9), 0 0 50px rgba(34, 197, 94, 0.4);
}

.docs-entry:hover .supernova-home {
  box-shadow: 0 0 30px rgba(34, 197, 94, 1);
}

.docs-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.docs-title {
  font-size: 13px;
  font-weight: 600;
}

.docs-subtitle {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.9);
}

.data-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: radial-gradient(circle at 0 0, rgba(239, 68, 68, 0.15), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(239, 68, 68, 0.5);
  text-decoration: none;
  color: #e5e7eb;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.9);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 8px;
  backface-visibility: hidden;
}

.data-entry:hover {
  background: radial-gradient(circle at 0 0, rgba(248, 113, 113, 0.22), rgba(15, 23, 42, 0.98));
  border-color: rgba(226, 232, 240, 0.9);
  transform: translateY(-1px);
}

.data-entry.active {
  border-color: #ef4444;
  box-shadow: 0 18px 45px rgba(239, 68, 68, 0.45);
}

.data-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid rgba(239, 68, 68, 0.7);
  background: radial-gradient(circle at 0 0, rgba(248, 113, 113, 0.32), rgba(15, 23, 42, 0.96));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.6);
  backface-visibility: hidden;
}

.zeta-logo {
  font-size: 20px;
  font-weight: bold;
  font-family: 'Inter', sans-serif;
  line-height: 1;
  color: #fff;
  z-index: 2;
  position: relative;
}

.data-entry .supernova-home {
  display: none;
}

.data-entry:hover .data-icon {
  border-color: rgba(239, 68, 68, 0.95);
  box-shadow: 0 0 30px rgba(248, 113, 113, 0.9), 0 0 50px rgba(239, 68, 68, 0.4);
}

.data-entry:hover .supernova-home {
  box-shadow: 0 0 30px rgba(239, 68, 68, 1);
}

.data-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.data-title {
  font-size: 13px;
  font-weight: 600;
}

.data-subtitle {
  font-size: 11px;
  color: rgba(148, 163, 184, 0.9);
}

/* TOOL GROUPS */
.tool-group {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  backface-visibility: hidden;
}

.tool-group:hover {
  border-color: rgba(255, 255, 255, 0.1);
}

.tool-header {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backface-visibility: hidden;
}

.tool-header:hover:not(.disabled) {
  background: rgba(255, 255, 255, 0.05);
}

.tool-header.expanded {
  background: rgba(255, 255, 255, 0.02);
}

.tool-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.tool-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  line-height: 1.2;
}

.tool-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.2;
}

.chevron {
  color: rgba(255, 255, 255, 0.3);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  backface-visibility: hidden;
}

.tool-header.expanded .chevron {
  transform: rotate(180deg);
}

.tool-content-wrapper {
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  backface-visibility: hidden;
}

.tool-content {
  padding: 4px 12px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-top: 1px solid rgba(255, 255, 255, 0.03);
}

/* NAV ITEMS */
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backface-visibility: hidden;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.nav-item.active {
  background: rgba(0, 217, 255, 0.15);
  color: #00d9ff;
  font-weight: 500;
}

.nav-item.coming-soon {
  opacity: 0.6;
  cursor: not-allowed;
}

.nav-label {
  flex: 1;
}

.nav-soon {
  font-size: 9px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.5);
  padding: 1px 4px;
  border-radius: 4px;
  text-transform: uppercase;
  flex-shrink: 0;
}

/* ============================================
   SETTINGS LINK BUTTON (Bottom)
   ============================================ */
.settings-link-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(236, 72, 153, 0.08);
  border: 1px solid rgba(236, 72, 153, 0.2);
  text-decoration: none;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
  border-radius: 0;
  margin: 0;
  backface-visibility: hidden;
}

.settings-link-button:hover {
  background: rgba(236, 72, 153, 0.12);
  border-color: rgba(236, 72, 153, 0.4);
  color: #fff;
}

.settings-link-button.active {
  background: rgba(236, 72, 153, 0.15);
  border-color: rgba(236, 72, 153, 0.6);
  box-shadow: inset 0 0 20px rgba(236, 72, 153, 0.1);
}

.settings-glossy-icon {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02) 80%);
  border: 1px solid rgba(236, 72, 153, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  transition: transform 0.3s ease, border-color 0.3s ease;
  flex-shrink: 0;
  backface-visibility: hidden;
}

.settings-link-button:hover .settings-glossy-icon {
  transform: translateY(-1px);
  border-color: rgba(236, 72, 153, 0.6);
}

.settings-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.settings-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.settings-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.settings-arrow {
  color: rgba(236, 72, 153, 0.4);
  transition: transform 0.3s ease, color 0.3s ease;
  flex-shrink: 0;
  backface-visibility: hidden;
}

.settings-link-button:hover .settings-arrow {
  transform: translateX(2px);
  color: rgba(236, 72, 153, 0.8);
}

/* ============================================
   DIVIDER & FOOTER
   ============================================ */
.sidebar-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.status-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 4px;
  letter-spacing: 0.5px;
}

.status-row:last-child {
  margin-bottom: 0;
}

.lbl {
  color: rgba(255, 255, 255, 0.4);
}

.val {
  color: #fff;
  font-weight: 500;
}

.val.connected {
  color: #4ade80;
}

.val.mono {
  font-family: 'SF Mono', monospace;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .sidebar {
    width: 280px;
  }
  .tool-title {
    font-size: 12px;
  }
  .tool-subtitle {
    font-size: 10px;
  }
}

@media (max-width: 768px) {
  .sidebar-tab {
    width: 60px;
    min-width: 60px;
  }

  .burger-icon span {
    width: 21px;
    height: 2.5px;
  }

  .sidebar {
    width: 260px;
  }
  .tool-title {
    font-size: 11px;
  }
  .tool-subtitle {
    font-size: 9px;
  }
  .home-title,
  .data-title {
    font-size: 13px;
  }
  .home-subtitle,
  .data-subtitle {
    font-size: 11px;
  }
  .nav-label {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .sidebar-tab {
    width: 56px;
    min-width: 56px;
  }

  .burger-icon span {
    width: 22px;
    height: 2.5px;
  }

  .sidebar {
    width: 100%;
    max-width: 320px;
  }
  .sidebar-header {
    padding: 16px;
  }
  .app-logo {
    font-size: 16px;
  }
  .tool-title {
    font-size: 10px;
  }
  .tool-subtitle {
    font-size: 8px;
  }
  .home-title,
  .data-title {
    font-size: 12px;
  }
  .home-subtitle,
  .data-subtitle {
    font-size: 10px;
  }
  .nav-label {
    font-size: 10px;
  }
  .sidebar-footer {
    padding: 10px 12px;
  }
  .status-row {
    font-size: 10px;
  }
}
</style>