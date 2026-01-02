<!-- src/pages/BacktestResults.vue -->
<template>
  <div class="page-container">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Результаты бэктестинга</h1>
        <p class="section-subtitle">Анализ исторической производительности стратегии</p>
      </div>
      
      <!-- Glass Segmented Control -->
      <div class="segmented-control">
        <button
          v-for="period in periods"
          :key="period"
          @click="selectedPeriod = period"
          class="seg-btn"
          :class="{ active: selectedPeriod === period }"
        >
          {{ period }}
        </button>
      </div>
    </div>

    <!-- KPI Cards (4-column) -->
    <div class="kpi-cards-grid">
      <div class="kpi-card">
        <div class="kpi-label">Полная доходность</div>
        <div class="kpi-value text-gradient-green">+24.5%</div>
        <div class="kpi-change text-green">vs S&P 500: +18.3%</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">CAGR (Годовая)</div>
        <div class="kpi-value text-white">18.2%</div>
        <div class="kpi-change text-muted">Безрисковая: 5.0%</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Коэф. Шарпа</div>
        <div class="kpi-value text-gradient-blue">1.58</div>
        <div class="kpi-change text-blue">Высокая эфф.</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Макс. Просадка</div>
        <div class="kpi-value text-red">-14.2%</div>
        <div class="kpi-change text-red">vs Рынок: -23.5%</div>
      </div>
    </div>

    <!-- Equity Curve Chart (Full Width) -->
    <div class="card glass-panel chart-panel">
      <div class="panel-header">
        <h3>Накопленная доходность (Equity Curve)</h3>
        <div class="chart-legend">
          <div class="legend-item"><span class="dot strategy"></span>Стратегия</div>
          <div class="legend-item"><span class="dot benchmark"></span>S&P 500</div>
        </div>
      </div>
      <div class="chart-container">
        <!-- Placeholder for Chart -->
        <div class="chart-mockup">
           <svg viewBox="0 0 1000 200" preserveAspectRatio="none" class="mock-chart">
              <!-- Grid -->
              <line x1="0" y1="50" x2="1000" y2="50" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="100" x2="1000" y2="100" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="150" x2="1000" y2="150" stroke="rgba(255,255,255,0.05)" />

              <!-- Benchmark (Dashed) -->
              <path d="M0,200 Q100,190 200,180 T400,170 T600,140 T800,130 T1000,90" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2" stroke-dasharray="5,5"/>
              
              <!-- Gradient Defs -->
              <defs>
                <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="rgba(74, 222, 128, 0.2)"/>
                  <stop offset="100%" stop-color="rgba(74, 222, 128, 0)"/>
                </linearGradient>
              </defs>
              
              <!-- Strategy Area -->
              <path d="M0,200 Q100,180 200,150 T400,160 T600,100 T800,80 T1000,20 V200 H0" fill="url(#fade)" stroke="none"/>
              <!-- Strategy Line -->
              <path d="M0,200 Q100,180 200,150 T400,160 T600,100 T800,80 T1000,20" fill="none" stroke="#4ade80" stroke-width="2"/>
           </svg>
        </div>
      </div>
    </div>

    <!-- Split View: Heatmap & Stats -->
    <div class="dashboard-grid">
      
      <!-- Left: Monthly Heatmap -->
      <div class="col-left">
        <div class="card glass-panel">
          <div class="panel-header">
             <h3>Месячная доходность</h3>
          </div>
          <div class="table-wrapper">
            <table class="heatmap-table">
              <thead>
                <tr>
                  <th class="col-month">Месяц</th>
                  <th v-for="year in years" :key="year" class="col-year">{{ year }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(month, idx) in months" :key="month">
                  <td class="col-month">{{ month }}</td>
                  <td v-for="year in years" :key="`${month}-${year}`" class="col-val">
                    <div class="val-pill" :class="getReturnClass(monthlyReturns[idx][year])">
                      {{ monthlyReturns[idx][year] }}%
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right: Stats & Drawdowns -->
      <div class="col-right">
        
        <!-- Detailed Stats -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Статистика сделок</h3>
          </div>
          <div class="stats-grid-mini">
             <div class="stat-box">
                <span class="lbl">Всего сделок</span>
                <span class="val">243</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Win Rate</span>
                <span class="val text-green">64.2%</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Profit Factor</span>
                <span class="val text-green">2.34</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Ср. Прибыль</span>
                <span class="val text-green">+$245</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Ср. Убыток</span>
                <span class="val text-red">-$145</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Дней в поз.</span>
                <span class="val">8.4</span>
             </div>
          </div>
        </div>

        <!-- Drawdowns List -->
        <div class="card glass-panel">
          <div class="panel-header">
            <h3>Топ просадок</h3>
          </div>
          <div class="drawdown-list">
             <div v-for="(dd, idx) in drawdowns" :key="idx" class="dd-item">
                <div class="dd-info">
                   <span class="dd-period">{{ dd.period }}</span>
                   <span class="dd-rec">Восст: {{ dd.recovery }}</span>
                </div>
                <span class="dd-val text-red">{{ dd.amount }}%</span>
             </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const periods = ref(['1M', '3M', '6M', 'YTD', '1Y', 'All'])
const selectedPeriod = ref('YTD')

const years = ref(['2024', '2025'])
const months = ref(['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'])

// Typed Interface for Monthly Returns
interface MonthlyData {
  [key: string]: string;
}

// Mock data: [MonthIndex][YearKey]
const monthlyReturns = ref<MonthlyData[]>([
  { '2024': '+2.1', '2025': '+1.8' },
  { '2024': '+3.4', '2025': '-1.2' },
  { '2024': '-0.5', '2025': '+2.9' },
  { '2024': '+1.7', '2025': '+0.8' },
  { '2024': '+2.3', '2025': '-0.3' },
  { '2024': '+1.9', '2025': '+1.5' },
  { '2024': '+2.8', '2025': '+2.1' },
  { '2024': '-1.1', '2025': '+0.9' },
  { '2024': '+3.2', '2025': '+1.4' },
  { '2024': '+2.5', '2025': '+3.1' },
  { '2024': '+1.8', '2025': '+2.2' },
  { '2024': '+4.1', '2025': '+2.8' },
])

const drawdowns = [
  { period: 'Март 23 — Май 23', amount: -14.2, recovery: '6 мес.' },
  { period: 'Сент 23 — Окт 23', amount: -8.5, recovery: '3 мес.' },
  { period: 'Фев 24 — Март 24', amount: -5.3, recovery: '2 мес.' },
]

const getReturnClass = (returnValue: string) => {
  const value = parseFloat(returnValue)
  if (value > 3) return 'bg-green-strong'
  if (value > 0) return 'bg-green'
  if (value > -2) return 'bg-red-soft'
  return 'bg-red-strong'
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 26px; padding: 28px;
  max-width: 1280px; margin: 0 auto;
}

.section-header {
  display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px;
}
.section-title { font-size: 28px; font-weight: 700; margin: 0; color: #fff; letter-spacing: -0.02em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* ============================================
   GLASS CARD ENGINE (Unified)
   ============================================ */
.card, .kpi-card {
  position: relative; border-radius: 18px; overflow: hidden;
  background: rgba(20, 22, 28, 0.18);
  backdrop-filter: blur(34px) saturate(185%);
  -webkit-backdrop-filter: blur(34px) saturate(185%);
  box-shadow: 0 18px 40px -18px rgba(0,0,0,0.55), inset 0 0 0 1px rgba(255, 255, 255, 0.14), inset 0 1px 0 0 rgba(255, 255, 255, 0.10);
  transform: translateZ(0); transition: all 220ms ease;
}

/* Glare & Noise */
.card::before, .kpi-card::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.0) 40%); opacity: 0.8; z-index: 0;
}
.card::after, .kpi-card::after {
  content: ""; position: absolute; inset: -1px; pointer-events: none;
  background: radial-gradient(800px circle at 50% 0%, rgba(255,255,255,0.06), transparent 40%); opacity: 0.6; z-index: 0;
}
.card:hover, .kpi-card:hover { transform: translateY(-2px); background: rgba(20, 22, 28, 0.24); }

/* ============================================
   CONTROLS
   ============================================ */
.segmented-control {
  background: rgba(0,0,0,0.3); border-radius: 8px; padding: 4px; display: flex; gap: 2px;
  border: 1px solid rgba(255,255,255,0.1);
}
.seg-btn {
  background: transparent; border: none; color: rgba(255,255,255,0.6);
  padding: 6px 12px; font-size: 12px; font-weight: 500; border-radius: 6px; cursor: pointer; transition: all 0.2s;
}
.seg-btn:hover { color: #fff; }
.seg-btn.active { background: rgba(255,255,255,0.15); color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }

/* ============================================
   KPI GRID
   ============================================ */
.kpi-cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.kpi-card { padding: 18px; display: flex; flex-direction: column; justify-content: space-between; min-height: 92px; }
.kpi-label { position: relative; z-index: 1; font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 600; margin-bottom: 8px; }
.kpi-value { position: relative; z-index: 1; font-size: 26px; font-weight: 600; font-family: var(--font-family-mono); line-height: 1; }
.kpi-change { position: relative; z-index: 1; font-size: 11px; margin-top: 6px; color: rgba(255,255,255,0.4); }

/* ============================================
   DASHBOARD SPLIT
   ============================================ */
.dashboard-grid { display: grid; grid-template-columns: 3fr 2fr; gap: 18px; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 18px; }

.glass-panel { padding: 20px; }
.panel-header { position: relative; z-index: 1; display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.panel-header h3 { margin: 0; font-size: 13px; font-weight: 600; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 0.04em; }

/* ============================================
   CHART
   ============================================ */
.chart-panel { min-height: 300px; display: flex; flex-direction: column; }
.chart-container { position: relative; z-index: 1; height: 100%; width: 100%; flex: 1; min-height: 220px; }
.chart-mockup { width: 100%; height: 100%; overflow: hidden; border-radius: 8px; }
.mock-chart { width: 100%; height: 100%; }
.chart-legend { display: flex; gap: 12px; }
.legend-item { font-size: 11px; color: rgba(255,255,255,0.6); display: flex; align-items: center; gap: 6px; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot.strategy { background: #4ade80; box-shadow: 0 0 8px rgba(74, 222, 128, 0.5); }
.dot.benchmark { background: rgba(255,255,255,0.3); }

/* ============================================
   HEATMAP
   ============================================ */
.table-wrapper { position: relative; z-index: 1; overflow-x: auto; }
.heatmap-table { width: 100%; border-collapse: separate; border-spacing: 4px; font-size: 12px; }
.col-month { text-align: left; color: rgba(255,255,255,0.4); font-weight: 500; width: 40px; }
.col-year { text-align: center; color: rgba(255,255,255,0.4); padding-bottom: 8px; }
.col-val { text-align: center; }

.val-pill {
  padding: 6px 4px; border-radius: 6px; font-family: var(--font-family-mono); font-size: 11px; font-weight: 600;
  transition: transform 0.1s;
}
.val-pill:hover { transform: scale(1.05); }

.bg-green-strong { background: rgba(74, 222, 128, 0.25); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.1); }
.bg-green { background: rgba(74, 222, 128, 0.1); color: #86efac; }
.bg-red-soft { background: rgba(248, 113, 113, 0.1); color: #fca5a5; }
.bg-red-strong { background: rgba(248, 113, 113, 0.25); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.1); }

/* ============================================
   STATS & DRAWDOWNS
   ============================================ */
.stats-grid-mini {
  position: relative; z-index: 1;
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
}
.stat-box {
  background: rgba(255,255,255,0.03); border-radius: 8px; padding: 10px; display: flex; flex-direction: column; gap: 4px;
}
.stat-box .lbl { font-size: 10px; color: rgba(255,255,255,0.5); text-transform: uppercase; }
.stat-box .val { font-family: var(--font-family-mono); font-weight: 600; font-size: 14px; color: #fff; }

.drawdown-list { position: relative; z-index: 1; display: flex; flex-direction: column; gap: 10px; }
.dd-item {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);
}
.dd-item:last-child { border-bottom: none; }
.dd-info { display: flex; flex-direction: column; }
.dd-period { font-size: 12px; color: rgba(255,255,255,0.8); }
.dd-rec { font-size: 10px; color: rgba(255,255,255,0.4); }
.dd-val { font-family: var(--font-family-mono); font-weight: 700; font-size: 13px; }

/* ============================================
   UTILITY
   ============================================ */
.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-blue { color: #60a5fa; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-white { color: #fff; }

@media (max-width: 1024px) {
  .kpi-cards-grid, .dashboard-grid { grid-template-columns: 1fr; }
}
</style>