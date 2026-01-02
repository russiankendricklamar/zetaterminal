<!-- src/pages/DashboardHome.vue -->
<template>
  <div class="page-container">
    
    <!-- 1. Top Market Ticker (Marquee) -->
    <div class="ticker-wrapper">
      <div class="ticker-content">
        <div v-for="(item, i) in marketTicker" :key="i" class="ticker-item">
          <span class="t-symbol">{{ item.symbol }}</span>
          <span class="t-price">{{ item.price }}</span>
          <span class="t-change" :class="item.change > 0 ? 'text-green' : 'text-red'">
            {{ item.change > 0 ? '▲' : '▼' }} {{ Math.abs(item.change) }}%
          </span>
        </div>
         <!-- Duplicate for infinite scroll effect (optional implementation) -->
         <div v-for="(item, i) in marketTicker" :key="'dup'+i" class="ticker-item">
          <span class="t-symbol">{{ item.symbol }}</span>
          <span class="t-price">{{ item.price }}</span>
          <span class="t-change" :class="item.change > 0 ? 'text-green' : 'text-red'">
            {{ item.change > 0 ? '▲' : '▼' }} {{ Math.abs(item.change) }}%
          </span>
        </div>
      </div>
    </div>

    <!-- 2. Hero / Welcome Section -->
    <header class="hero-section">
      <div class="hero-text">
        <h1 class="hero-title">Доброе день</h1>
        <p class="hero-subtitle">Системы работают штатно.</p>
      </div>
      <div class="hero-status">
        <div class="status-pill">
            <span class="dot bg-green pulse"></span> API активен
        </div>
        <div class="status-pill">
            <span class="dot bg-blue"></span> Задержка: 12ms
        </div>
      </div>
    </header>

    <!-- 3. Main Dashboard Grid -->
    <div class="dashboard-grid">
      
      <!-- LEFT: Quick Access (Shortcuts) -->
      <section class="grid-col-left">
        <h3 class="section-label">Инструменты</h3>
        <div class="shortcuts-grid">
            
            <router-link to="/monte-carlo" class="shortcut-card">
                <div class="sc-icon-box blue">
                    <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M2 12h20M2 12l5-5m-5 5l5 5M22 12l-5-5m5 5l-5 5"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Монте-Карло</span>
                    <span class="sc-desc">Симуляция сценариев</span>
                </div>
                <div class="sc-arrow">→</div>
            </router-link>

            <router-link to="/stress" class="shortcut-card">
                <div class="sc-icon-box orange">
                    <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Стресс-тестирование</span>
                    <span class="sc-desc">Шоковые события</span>
                </div>
                 <div class="sc-arrow">→</div>
            </router-link>

            <router-link to="/portfolio" class="shortcut-card">
                <div class="sc-icon-box purple">
                    <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Портфель ценных бумаг</span>
                    <span class="sc-desc">Ребалансировка</span>
                </div>
                 <div class="sc-arrow">→</div>
            </router-link>

             <router-link to="/reports" class="shortcut-card">
                <div class="sc-icon-box gray">
                    <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Отчеты</span>
                    <span class="sc-desc">Экспорт данных</span>
                </div>
                 <div class="sc-arrow">→</div>
            </router-link>

        </div>

        <!-- System Alerts -->
        <h3 class="section-label mt-6">Уведомления</h3>
        <div class="card glass-panel alerts-panel">
            <div class="alert-item" v-for="alert in alerts" :key="alert.id">
                <div class="alert-icon" :class="alert.type">!</div>
                <div class="alert-content">
                    <span class="alert-msg">{{ alert.message }}</span>
                    <span class="alert-time">{{ alert.time }}</span>
                </div>
            </div>
        </div>
      </section>

      <!-- CENTER/RIGHT: Portfolio & Market Overview -->
      <section class="grid-col-main">
          
          <!-- Total Equity Card (Big) -->
          <div class="card glass-panel equity-card">
              <div class="equity-header">
                  <div>
                      <span class="lbl">Капитал</span>
                      <h2 class="val-big">1 000 000 руб.</h2>
                  </div>
                  <div class="pnl-badge bg-green-subtle">
                      +2.45% (24ч)
                  </div>
              </div>
              
              <!-- Simple SVG Area Chart -->
              <div class="chart-wrapper">
                  <svg viewBox="0 0 800 200" preserveAspectRatio="none" class="equity-svg">
                      <defs>
                          <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stop-color="rgba(59, 130, 246, 0.3)" />
                              <stop offset="100%" stop-color="rgba(59, 130, 246, 0)" />
                          </linearGradient>
                      </defs>
                      <path d="M0,150 C150,140 300,80 450,100 S650,40 800,20 V200 H0 Z" fill="url(#eqGrad)" />
                      <path d="M0,150 C150,140 300,80 450,100 S650,40 800,20" fill="none" stroke="#3b82f6" stroke-width="3" />
                  </svg>
              </div>
          </div>

          <!-- Bottom Grid: 2 Columns -->
          <div class="bottom-split">
              
              <!-- Market Heatmap (Mini) -->
              <div class="card glass-panel">
                  <div class="panel-header-sm">
                      <h3>Сектора (Daily)</h3>
                  </div>
                  <div class="heatmap-grid">
                      <div class="hm-item bg-green-lg">Tech <span>+1.2%</span></div>
                      <div class="hm-item bg-green-md">Fin <span>+0.8%</span></div>
                      <div class="hm-item bg-red-md">Energy <span>-0.5%</span></div>
                      <div class="hm-item bg-green-sm">Cons <span>+0.2%</span></div>
                      <div class="hm-item bg-red-lg">Util <span>-1.1%</span></div>
                      <div class="hm-item bg-grey">Real Est <span>0.0%</span></div>
                  </div>
              </div>

              <!-- Risk Gauge (CSS only) -->
              <div class="card glass-panel">
                  <div class="panel-header-sm">
                      <h3>Текущий режим рынка</h3>
                  </div>
                  <div class="risk-gauge-container">
                      <div class="risk-meter">
                          <div class="risk-needle" style="transform: rotate(45deg)"></div>
                          <div class="risk-label">Высокая волатильность</div>
                      </div>
                      <div class="risk-stats">
                          <div class="rs-row"><span>VIX</span> <span class="mono">24.5</span></div>
                          <div class="rs-row"><span>Режим</span> <span class="text-orange">Нестабильный</span></div>
                      </div>
                  </div>
              </div>

          </div>

      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const marketTicker = ref([
    { symbol: 'S&P 500', price: '4,785.20', change: 0.45 },
    { symbol: 'NASDAQ', price: '15,120.50', change: 0.82 },
    { symbol: 'VIX', price: '14.20', change: -2.10 },
    { symbol: 'US 10Y', price: '4.05%', change: 0.05 },
    { symbol: 'BTC/USD', price: '45,230', change: 1.25 },
    { symbol: 'EUR/USD', price: '1.0950', change: -0.15 },
])

const alerts = ref([
    { id: 1, type: 'warning', message: 'VaR Usage reached 85%', time: '10:42 AM' },
    { id: 2, type: 'info', message: 'Monte Carlo simulation completed', time: '09:15 AM' },
    { id: 3, type: 'error', message: 'Data feed latency spike (fixed)', time: '08:30 AM' },
])

</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 28px;
  max-width: 1400px; margin: 0 auto; height: 100vh; overflow-y: auto;
  position: relative;
}

/* ============================================
   TICKER (MARQUEE)
   ============================================ */
.ticker-wrapper {
    position: absolute; top: 0; left: 0; right: 0;
    height: 32px; background: rgba(0,0,0,0.3); border-bottom: 1px solid rgba(255,255,255,0.05);
    overflow: hidden; display: flex; align-items: center;
    backdrop-filter: blur(5px); z-index: 10;
}
.ticker-content {
    display: flex; gap: 32px; animation: marquee 30s linear infinite; padding-left: 20px;
    white-space: nowrap;
}
.ticker-item { display: flex; gap: 8px; font-size: 11px; font-family: var(--font-family-mono); }
.t-symbol { color: rgba(255,255,255,0.6); font-weight: 600; }
.t-price { color: #fff; }
.t-change { font-weight: 500; }

@keyframes marquee {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); } 
}

/* ============================================
   HERO
   ============================================ */
.hero-section {
    margin-top: 32px; /* Space for ticker */
    display: flex; justify-content: space-between; align-items: flex-end;
}
.hero-title { font-size: 32px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.02em; }
.hero-subtitle { font-size: 14px; color: rgba(255,255,255,0.5); margin: 6px 0 0 0; }
.hero-status { display: flex; gap: 12px; }

.status-pill {
    display: flex; align-items: center; gap: 6px; padding: 6px 12px;
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; font-size: 11px; color: rgba(255,255,255,0.7);
}
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot.pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

/* ============================================
   MAIN GRID
   ============================================ */
.dashboard-grid {
    display: grid; grid-template-columns: 320px 1fr; gap: 24px;
    padding-bottom: 40px;
}
.grid-col-left { display: flex; flex-direction: column; gap: 12px; }
.grid-col-main { display: flex; flex-direction: column; gap: 20px; }

.section-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.4); letter-spacing: 0.05em; margin: 0 0 8px 4px; }
.mt-6 { margin-top: 24px; }

/* ============================================
   SHORTCUTS
   ============================================ */
.shortcuts-grid { display: flex; flex-direction: column; gap: 12px; }

.shortcut-card {
    display: flex; align-items: center; gap: 16px; padding: 16px;
    background: rgba(20, 22, 28, 0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px;
    text-decoration: none; transition: all 0.2s; position: relative; overflow: hidden;
}
.shortcut-card:hover {
    background: rgba(255,255,255,0.05); border-color: rgba(255,255,255,0.15); transform: translateX(4px);
}

.sc-icon-box {
    width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.sc-icon-box.blue { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.sc-icon-box.orange { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.sc-icon-box.purple { background: rgba(168, 85, 247, 0.15); color: #a855f7; }
.sc-icon-box.gray { background: rgba(255, 255, 255, 0.05); color: rgba(255, 255, 255, 0.5); }

.sc-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.sc-title { font-size: 14px; font-weight: 600; color: #fff; }
.sc-desc { font-size: 11px; color: rgba(255,255,255,0.4); }
.sc-arrow { color: rgba(255,255,255,0.2); font-size: 18px; margin-right: 4px; }

/* ============================================
   ALERTS
   ============================================ */
.alerts-panel { padding: 0 !important; gap: 0 !important; }
.alert-item {
    display: flex; gap: 12px; padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.alert-item:last-child { border-bottom: none; }

.alert-icon {
    width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 800; flex-shrink: 0;
}
.alert-icon.warning { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
.alert-icon.error { background: rgba(248, 113, 113, 0.2); color: #f87171; }
.alert-icon.info { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }

.alert-content { display: flex; flex-direction: column; gap: 2px; }
.alert-msg { font-size: 12px; color: rgba(255,255,255,0.9); }
.alert-time { font-size: 10px; color: rgba(255,255,255,0.4); }

/* ============================================
   CENTER: EQUITY CARD
   ============================================ */
.equity-card { padding: 24px; min-height: 280px; justify-content: space-between; position: relative; }
.equity-header { display: flex; justify-content: space-between; align-items: flex-start; z-index: 2; }

.lbl { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; font-weight: 600; }
.val-big { font-size: 36px; font-weight: 700; color: #fff; margin: 4px 0 0 0; letter-spacing: -0.03em; font-family: var(--font-family-mono); }

.pnl-badge {
    padding: 6px 12px; border-radius: 8px; font-size: 13px; font-weight: 600;
    color: #4ade80; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.2);
}

.chart-wrapper {
    position: absolute; bottom: 0; left: 0; right: 0; height: 180px; z-index: 1; pointer-events: none;
}
.equity-svg { width: 100%; height: 100%; opacity: 0.8; }

/* ============================================
   BOTTOM SPLIT
   ============================================ */
.bottom-split { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.panel-header-sm h3 { margin: 0 0 16px 0; font-size: 12px; text-transform: uppercase; color: rgba(255,255,255,0.5); }

/* Heatmap */
.heatmap-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; height: 140px; }
.hm-item {
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    border-radius: 6px; font-size: 11px; font-weight: 600; color: rgba(0,0,0,0.7);
    transition: transform 0.2s; cursor: default;
}
.hm-item:hover { transform: scale(0.98); }
.hm-item span { font-size: 10px; opacity: 0.8; }

/* Risk Gauge (Visual Hack with CSS) */
.risk-gauge-container { display: flex; align-items: center; justify-content: space-between; padding: 0 10px; }
.risk-meter {
    width: 100px; height: 50px; border-top-left-radius: 100px; border-top-right-radius: 100px;
    background: linear-gradient(90deg, #4ade80 0%, #fbbf24 50%, #f87171 100%);
    position: relative; overflow: hidden; opacity: 0.8;
}
.risk-needle {
    position: absolute; bottom: 0; left: 50%; width: 2px; height: 100%;
    background: #fff; transform-origin: bottom center;
    box-shadow: 0 0 10px rgba(0,0,0,0.5); z-index: 2;
}
.risk-label { position: absolute; bottom: -24px; left: 0; right: 0; text-align: center; font-size: 11px; color: #fff; font-weight: 600; }

.risk-stats { display: flex; flex-direction: column; gap: 8px; width: 50%; }
.rs-row { display: flex; justify-content: space-between; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; color: rgba(255,255,255,0.7); }

/* Colors */
.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-orange { color: #fbbf24; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.bg-green { background: #4ade80; }
.bg-blue { background: #3b82f6; }
.bg-green-lg { background: #4ade80; }
.bg-green-md { background: #86efac; }
.bg-green-sm { background: #bbf7d0; }
.bg-red-lg { background: #f87171; }
.bg-red-md { background: #fca5a5; }
.bg-grey { background: #9ca3af; }

/* Shared Glass */
.card, .glass-panel {
  border-radius: 18px; overflow: hidden;
  background: rgba(20, 22, 28, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
  padding: 20px;
}

@media (max-width: 1024px) {
    .dashboard-grid { grid-template-columns: 1fr; }
    .hero-section { flex-direction: column; align-items: flex-start; gap: 12px; }
}
</style>