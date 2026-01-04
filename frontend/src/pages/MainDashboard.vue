<!-- src/pages/DashboardHome.vue -->
<template>
  <div class="page-container">
    
    <!-- 1. Top Market Ticker (Marquee) -->
    <div class="ticker-wrapper">
      <div class="ticker-track">
        <!-- Original List -->
        <div class="ticker-group">
           <div v-for="(item, i) in marketTicker" :key="i" class="ticker-item">
             <span class="t-symbol">{{ item.symbol }}</span>
             <span class="t-price">{{ item.price }}</span>
             <span class="t-change" :class="item.change > 0 ? 'text-green' : 'text-red'">
               {{ item.change > 0 ? '▲' : '▼' }} {{ Math.abs(item.change) }}%
             </span>
           </div>
        </div>
        <!-- Duplicate for infinite loop -->
        <div class="ticker-group">
           <div v-for="(item, i) in marketTicker" :key="'dup'+i" class="ticker-item">
             <span class="t-symbol">{{ item.symbol }}</span>
             <span class="t-price">{{ item.price }}</span>
             <span class="t-change" :class="item.change > 0 ? 'text-green' : 'text-red'">
               {{ item.change > 0 ? '▲' : '▼' }} {{ Math.abs(item.change) }}%
             </span>
           </div>
        </div>
      </div>
    </div>

    <!-- 2. Hero / Welcome Section -->
    <header class="hero-section">
      <div class="hero-text">
        <h1 class="hero-title">Доброе утро, <span class="text-gradient-blue">Егор</span></h1>
        <p class="hero-subtitle">Все системы работают в штатном режиме.</p>
      </div>
      <div class="hero-status">
        <div class="glass-pill status-pill">
            <span class="dot bg-green pulse"></span> API Active
        </div>
        <div class="glass-pill status-pill">
            <span class="dot bg-blue"></span> 12ms Latency
        </div>
      </div>
    </header>

    <!-- 3. Main Dashboard Grid -->
    <div class="dashboard-grid">
      
      <!-- LEFT: Quick Access (Shortcuts) -->
      <section class="grid-col-left">
        <h3 class="section-label">Инструменты</h3>
        <div class="shortcuts-grid">
            
            <router-link to="/monte-carlo" class="glass-card shortcut-card">
                <div class="sc-icon-box blue-glow">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M2 12h20M2 12l5-5m-5 5l5 5M22 12l-5-5m5 5l-5 5"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Монте-Карло</span>
                    <span class="sc-desc">Симуляция сценариев</span>
                </div>
                <div class="sc-arrow">→</div>
            </router-link>

            <router-link to="/stress" class="glass-card shortcut-card">
                <div class="sc-icon-box orange-glow">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Стресс-тест</span>
                    <span class="sc-desc">Шоковые события</span>
                </div>
                 <div class="sc-arrow">→</div>
            </router-link>

            <router-link to="/portfolio" class="glass-card shortcut-card">
                <div class="sc-icon-box purple-glow">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
                </div>
                <div class="sc-info">
                    <span class="sc-title">Портфель</span>
                    <span class="sc-desc">Балансировка активов</span>
                </div>
                 <div class="sc-arrow">→</div>
            </router-link>

             <router-link to="/reports" class="glass-card shortcut-card">
                <div class="sc-icon-box gray-glow">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
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
        <div class="glass-card alerts-panel">
            <div class="alert-item" v-for="alert in alerts" :key="alert.id">
                <div class="alert-dot" :class="alert.type"></div>
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
          <div class="glass-card equity-card">
              <div class="equity-bg-glow"></div>
              <div class="equity-header">
                  <div>
                      <span class="lbl">Общий Капитал</span>
                      <h2 class="val-big">1,000,000 <span class="currency">RUB</span></h2>
                  </div>
                  <div class="pnl-badge bg-green-subtle">
                      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4"><path d="M18 15l-6-6-6 6"/></svg>
                      2.45%
                  </div>
              </div>
              
              <!-- Simple SVG Area Chart -->
              <div class="chart-wrapper">
                  <svg viewBox="0 0 800 240" preserveAspectRatio="none" class="equity-svg">
                      <defs>
                          <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3" />
                              <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
                          </linearGradient>
                      </defs>
                      <path d="M0,180 C100,170 200,120 400,140 S600,60 800,40 V240 H0 Z" fill="url(#eqGrad)" />
                      <path d="M0,180 C100,170 200,120 400,140 S600,60 800,40" fill="none" stroke="#3b82f6" stroke-width="3" stroke-linecap="round" />
                  </svg>
              </div>
          </div>

          <!-- Bottom Grid: 2 Columns -->
          <div class="bottom-split">
              
              <!-- Market Heatmap (Mini) -->
              <div class="glass-card padded-card">
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

              <!-- Risk Gauge -->
              <div class="glass-card padded-card">
                  <div class="panel-header-sm">
                      <h3>Режим рынка</h3>
                  </div>
                  <div class="risk-gauge-container">
                      <div class="risk-meter-wrapper">
                          <div class="risk-meter">
                              <div class="risk-needle" style="transform: rotate(45deg)"></div>
                          </div>
                          <div class="risk-label-center">Volatile</div>
                      </div>
                      <div class="risk-stats">
                          <div class="rs-row">
                              <span>VIX Index</span> 
                              <span class="mono">24.5</span>
                          </div>
                          <div class="rs-row">
                              <span>Regime</span> 
                              <span class="text-orange">High Risk</span>
                          </div>
                          <div class="rs-row">
                             <span>Liquidity</span>
                             <span class="text-green">Stable</span>
                          </div>
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
   PAGE LAYOUT & SHARED
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 24px 32px;
  max-width: 1600px; margin: 0 auto; height: 100%; overflow-y: auto;
  position: relative;
}

/* Base Glass Card */
.glass-card {
  border-radius: 20px; overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
  transition: transform 0.2s, background 0.2s;
}

/* ============================================
   TICKER (MARQUEE)
   ============================================ */
.ticker-wrapper {
    position: absolute; top: 0; left: 0; right: 0;
    height: 36px; background: rgba(10, 12, 16, 0.5); border-bottom: 1px solid rgba(255,255,255,0.05);
    overflow: hidden; display: flex; align-items: center;
    backdrop-filter: blur(10px); z-index: 10;
}
.ticker-track {
    display: flex; gap: 40px; width: fit-content;
    animation: marquee 40s linear infinite;
}
.ticker-group { display: flex; gap: 40px; }

.ticker-item { display: flex; gap: 10px; font-size: 12px; font-family: "SF Mono", monospace; align-items: center; }
.t-symbol { color: rgba(255,255,255,0.5); font-weight: 600; }
.t-price { color: #fff; font-weight: 500; }
.t-change { font-weight: 600; }

@keyframes marquee {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); } 
}

/* ============================================
   HERO
   ============================================ */
.hero-section {
    margin-top: 36px;
    display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 8px;
}
.hero-title { font-size: 32px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.hero-subtitle { font-size: 14px; color: rgba(255,255,255,0.5); margin: 6px 0 0 0; }
.hero-status { display: flex; gap: 12px; }

.glass-pill {
    display: flex; align-items: center; gap: 8px; padding: 6px 14px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 99px; font-size: 12px; color: rgba(255,255,255,0.8); font-weight: 500;
}
.dot { width: 6px; height: 6px; border-radius: 50%; box-shadow: 0 0 6px currentColor; }
.dot.pulse { animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

/* ============================================
   MAIN GRID
   ============================================ */
.dashboard-grid {
    display: grid; grid-template-columns: 340px 1fr; gap: 24px;
    padding-bottom: 40px;
}
.grid-col-left { display: flex; flex-direction: column; gap: 16px; }
.grid-col-main { display: flex; flex-direction: column; gap: 24px; }

.section-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.4); letter-spacing: 0.08em; margin: 0 0 8px 8px; font-weight: 600; }
.mt-6 { margin-top: 24px; }

/* ============================================
   SHORTCUTS
   ============================================ */
.shortcuts-grid { display: flex; flex-direction: column; gap: 12px; }

.shortcut-card {
    display: flex; align-items: center; gap: 16px; padding: 16px;
    text-decoration: none; cursor: pointer;
}
.shortcut-card:hover {
    background: rgba(40, 45, 55, 0.6); transform: translateX(4px);
}

.sc-icon-box {
    width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: all 0.2s;
}
.blue-glow { background: rgba(59, 130, 246, 0.15); color: #3b82f6; box-shadow: 0 0 15px rgba(59, 130, 246, 0.15); }
.orange-glow { background: rgba(251, 191, 36, 0.15); color: #fbbf24; box-shadow: 0 0 15px rgba(251, 191, 36, 0.15); }
.purple-glow { background: rgba(168, 85, 247, 0.15); color: #2c2a2d; box-shadow: 0 0 15px rgba(168, 85, 247, 0.15); }
.gray-glow { background: rgba(255, 255, 255, 0.08); color: rgba(255, 255, 255, 0.6); }

.sc-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.sc-title { font-size: 14px; font-weight: 600; color: #fff; }
.sc-desc { font-size: 12px; color: rgba(255,255,255,0.4); }
.sc-arrow { color: rgba(255,255,255,0.2); font-size: 18px; margin-right: 4px; transition: transform 0.2s; }
.shortcut-card:hover .sc-arrow { transform: translateX(4px); color: #fff; }

/* ============================================
   ALERTS
   ============================================ */
.alerts-panel { padding: 8px 0 !important; }
.alert-item {
    display: flex; gap: 14px; padding: 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.05);
    align-items: flex-start;
}
.alert-item:last-child { border-bottom: none; }

.alert-dot {
    width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0;
    box-shadow: 0 0 8px currentColor;
}
.alert-dot.warning { background: #fbbf24; color: #fbbf24; }
.alert-dot.error { background: #f87171; color: #f87171; }
.alert-dot.info { background: #3b82f6; color: #3b82f6; }

.alert-content { display: flex; flex-direction: column; gap: 4px; }
.alert-msg { font-size: 13px; color: rgba(255,255,255,0.9); line-height: 1.4; }
.alert-time { font-size: 11px; color: rgba(255,255,255,0.4); font-family: "SF Mono", monospace; }

/* ============================================
   EQUITY CARD
   ============================================ */
.equity-card { 
    padding: 28px; min-height: 300px; justify-content: space-between; position: relative; 
    border: 1px solid rgba(255,255,255,0.1);
}
/* Фоновое свечение */
.equity-bg-glow {
    position: absolute; top: -50%; right: -20%; width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
}

.equity-header { display: flex; justify-content: space-between; align-items: flex-start; z-index: 2; position: relative; }

.lbl { font-size: 12px; color: rgba(255,255,255,0.5); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
.val-big { font-size: 42px; font-weight: 700; color: #fff; margin: 4px 0 0 0; letter-spacing: -0.02em; line-height: 1; }
.currency { font-size: 20px; font-weight: 500; color: rgba(255,255,255,0.4); margin-left: 8px; }

.pnl-badge {
    display: flex; align-items: center; gap: 6px;
    padding: 6px 12px; border-radius: 12px; font-size: 14px; font-weight: 700;
    color: #4ade80; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.15);
}

.chart-wrapper {
    position: absolute; bottom: 0; left: 0; right: 0; height: 200px; z-index: 1; pointer-events: none;
}
.equity-svg { width: 100%; height: 100%; }

/* ============================================
   BOTTOM SPLIT
   ============================================ */
.bottom-split { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.padded-card { padding: 20px; }
.panel-header-sm h3 { margin: 0 0 16px 0; font-size: 12px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 700; letter-spacing: 0.05em; }

/* Heatmap */
.heatmap-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; height: 140px; }
.hm-item {
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    border-radius: 8px; font-size: 12px; font-weight: 600; color: rgba(0,0,0,0.8);
    transition: transform 0.2s; cursor: default;
}
.hm-item:hover { transform: scale(0.98); }
.hm-item span { font-size: 10px; opacity: 0.7; margin-top: 2px; }

/* Risk Gauge */
.risk-gauge-container { display: flex; align-items: center; justify-content: space-between; padding: 0 10px; height: 100%; }

.risk-meter-wrapper { position: relative; width: 120px; height: 60px; display: flex; justify-content: center; }
.risk-meter {
    width: 120px; height: 60px; border-top-left-radius: 120px; border-top-right-radius: 120px;
    background: conic-gradient(from 180deg at 50% 100%, #4ade80 0deg, #fbbf24 90deg, #f87171 180deg);
    position: relative; opacity: 0.9;
    mask-image: radial-gradient(circle at 50% 100%, transparent 40px, black 41px);
}
.risk-needle {
    position: absolute; bottom: 0; left: 50%; width: 4px; height: 65px;
    background: #fff; transform-origin: bottom center; border-radius: 4px;
    box-shadow: 0 0 10px rgba(0,0,0,0.5); z-index: 2;
}
.risk-label-center { position: absolute; bottom: -5px; font-size: 12px; font-weight: 700; color: #fff; }

.risk-stats { display: flex; flex-direction: column; gap: 10px; width: 50%; }
.rs-row { display: flex; justify-content: space-between; font-size: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 4px; color: rgba(255,255,255,0.6); }

/* Colors */
.text-green { color: #4ade80; }
.text-red { color: #f87171; }
.text-orange { color: #fbbf24; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.mono { font-family: "SF Mono", monospace; color: #fff; }

.bg-green-lg { background: #4ade80; }
.bg-green-md { background: #86efac; }
.bg-green-sm { background: #bbf7d0; }
.bg-red-lg { background: #f87171; }
.bg-red-md { background: #fca5a5; }
.bg-grey { background: #94a3b8; }

@media (max-width: 1200px) {
    .dashboard-grid { grid-template-columns: 1fr; }
    .hero-section { flex-direction: column; align-items: flex-start; gap: 12px; }
    .risk-gauge-container { flex-direction: column; gap: 20px; align-items: flex-start; }
    .risk-stats { width: 100%; }
}
</style>