<!-- src/pages/OptionGreeksAnalyzer.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Анализ чувствительности (Greeks)</h1>
        <p class="section-subtitle">Дельта, гамма, вега, тета, ро — риск-ориентированный анализ</p>
      </div>
      
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="dot" :class="getGreekStatusColor"></span>
            <span class="status-label">Тип: <b class="text-white">{{ params.type.toUpperCase() }}</b></span>
         </div>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT PANEL: Controls -->
        <aside class="left-panel">
            
            <!-- Parameters Card -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры опциона</h3></div>
                
                <div class="controls-form">
                    <!-- Spot Price -->
                    <div class="input-group">
                        <label class="lbl">S (Spot)</label>
                        <input v-model.number="params.S" type="number" step="0.01" class="glass-input" @change="calculateGreeks" />
                    </div>
                    
                    <!-- Strike -->
                    <div class="input-group">
                        <label class="lbl">K (Strike)</label>
                        <input v-model.number="params.K" type="number" step="0.01" class="glass-input" @change="calculateGreeks" />
                    </div>

                    <!-- Rate -->
                    <div class="input-group">
                        <label class="lbl">r (Rate), %</label>
                        <input v-model.number="params.r" type="number" step="0.01" class="glass-input" @change="calculateGreeks" />
                    </div>

                    <!-- Volatility -->
                    <div class="input-group">
                        <label class="lbl">σ (Vol), %</label>
                        <input v-model.number="params.sigma" type="number" step="0.01" class="glass-input" @change="calculateGreeks" />
                    </div>

                    <!-- Time to Maturity -->
                    <div class="input-group">
                        <label class="lbl">T (Time), лет</label>
                        <input v-model.number="params.T" type="number" step="0.01" min="0.001" class="glass-input" @change="calculateGreeks" />
                    </div>

                    <!-- Option Type -->
                    <div class="input-group">
                        <label class="lbl">Тип опциона</label>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input v-model="params.type" type="radio" value="call" @change="calculateGreeks" />
                                <span>Call</span>
                            </label>
                            <label class="radio-label">
                                <input v-model="params.type" type="radio" value="put" @change="calculateGreeks" />
                                <span>Put</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Greeks Stats -->
            <transition name="fade">
            <div class="glass-card panel" v-if="greeks.delta !== null">
                 <div class="panel-header"><h3>Риск-метрики</h3></div>
                 <div class="stats-list">
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Δ</span> 
                             <span class="s-name">Дельта</span>
                         </div>
                         <span class="val mono">{{ greeks.delta.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Γ</span> 
                             <span class="s-name">Гамма</span>
                         </div>
                         <span class="val mono">{{ greeks.gamma.toFixed(6) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">ν</span> 
                             <span class="s-name">Вега</span>
                         </div>
                         <span class="val mono">{{ greeks.vega.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Θ</span> 
                             <span class="s-name">Тета</span>
                         </div>
                         <span class="val mono" :class="greeks.theta < 0 ? 'text-red' : 'text-green'">{{ greeks.theta.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">ρ</span> 
                             <span class="s-name">Ро</span>
                         </div>
                         <span class="val mono">{{ greeks.rho.toFixed(4) }}</span>
                     </div>
                 </div>
            </div>
            </transition>

        </aside>

        <!-- RIGHT PANEL: Analysis -->
        <main class="main-panel">
            
            <!-- P&L Scenario Analysis -->
            <div class="glass-card chart-card">
                <div class="chart-header">
                    <h3>Сценарный анализ P&L</h3>
                </div>

                <div class="scenario-controls">
                    <div class="scenario-input">
                        <label>ΔS (руб.)</label>
                        <input v-model.number="scenario.deltaS" type="number" step="0.1" class="glass-input-sm" />
                    </div>
                    <div class="scenario-input">
                        <label>Δσ (%)</label>
                        <input v-model.number="scenario.deltaSigma" type="number" step="0.1" class="glass-input-sm" />
                    </div>
                    <div class="scenario-input">
                        <label>Δt (дн.)</label>
                        <input v-model.number="scenario.deltaT" type="number" step="1" class="glass-input-sm" />
                    </div>
                </div>

                <div class="pl-results" v-if="greeks.delta !== null">
                    <div class="pl-row">
                        <span class="pl-label">Δ компонент</span>
                        <span class="pl-value mono">{{ deltaComponent.toFixed(2) }}</span>
                    </div>
                    <div class="pl-row">
                        <span class="pl-label">Γ компонент</span>
                        <span class="pl-value mono">{{ gammaComponent.toFixed(2) }}</span>
                    </div>
                    <div class="pl-row">
                        <span class="pl-label">ν компонент</span>
                        <span class="pl-value mono">{{ vegaComponent.toFixed(2) }}</span>
                    </div>
                    <div class="pl-row">
                        <span class="pl-label">Θ компонент</span>
                        <span class="pl-value mono">{{ thetaComponent.toFixed(2) }}</span>
                    </div>
                    <div class="pl-row divider"></div>
                    <div class="pl-row total">
                        <span class="pl-label">Всего (приблиз.)</span>
                        <span class="pl-value mono" :class="totalPL >= 0 ? 'text-green' : 'text-red'">{{ totalPL.toFixed(2) }}</span>
                    </div>
                </div>

                <div v-else class="pl-results empty-state">
                    <span>Рассчитайте греки для анализа</span>
                </div>
            </div>

            <!-- Sensitivity Matrix -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Матрица чувствительности P&L (ΔS × Δσ)</h3>
                </div>
                
                <div class="sensitivity-table" v-if="sensitivityMatrix.length">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ΔS (руб.)</th>
                                <th>σ - 2%</th>
                                <th>σ - 1%</th>
                                <th>σ базовое</th>
                                <th>σ + 1%</th>
                                <th>σ + 2%</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, i) in sensitivityMatrix" :key="i">
                                <td class="row-header">{{ [-10, -5, 0, 5, 10][i] }}</td>
                                <td v-for="(val, j) in row" :key="j" :class="{ positive: val > 0, negative: val < 0 }">
                                    {{ val.toFixed(2) }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div v-else class="pl-results empty-state">
                    <span>Матрица будет заполнена после расчёта</span>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

const params = reactive({
  S: 100,
  K: 100,
  r: 5,
  sigma: 20,
  T: 0.25,
  type: 'call',
})

const scenario = reactive({
  deltaS: 5,
  deltaSigma: 1,
  deltaT: 7,
})

const greeks = reactive({
  delta: null as number | null,
  gamma: null as number | null,
  vega: null as number | null,
  theta: null as number | null,
  rho: null as number | null,
})

const sensitivityMatrix = ref<number[][]>([])

// ===== Helpers =====
const normalPdf = (x: number): number => {
  return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI)
}

const normalCdf = (x: number): number => {
  const a1 = 0.254829592
  const a2 = -0.284496736
  const a3 = 1.421413741
  const a4 = -1.453152027
  const a5 = 1.061405429
  const p = 0.3275911
  const sign = x < 0 ? -1 : 1
  const absX = Math.abs(x) / Math.sqrt(2)
  const t = 1.0 / (1.0 + p * absX)
  const y = 1.0 - (a5 * Math.pow(t, 5) + a4 * Math.pow(t, 4) + a3 * Math.pow(t, 3) + a2 * Math.pow(t, 2) + a1 * t) * Math.exp(-absX * absX)
  return 0.5 * (1.0 + sign * y)
}

const calculateOptionPrice = (S: number, K: number, r: number, sigma: number, T: number, type: string): number => {
  if (sigma <= 0 || T <= 0) return 0
  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  if (type === 'call') {
    return S * normalCdf(d1) - K * Math.exp(-r * T) * normalCdf(d2)
  } else {
    return K * Math.exp(-r * T) * normalCdf(-d2) - S * normalCdf(-d1)
  }
}

const calculateGreeks = () => {
  const S = params.S
  const K = params.K
  const r = params.r / 100
  const sigma = params.sigma / 100
  const T = params.T

  if (sigma <= 0 || T <= 0) {
    greeks.delta = null
    greeks.gamma = null
    greeks.vega = null
    greeks.theta = null
    greeks.rho = null
    sensitivityMatrix.value = []
    return
  }

  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  const Nd1 = normalCdf(d1)
  const N_d1 = normalCdf(-d1)
  const nd1 = normalPdf(d1)
  const Nd2 = normalCdf(d2)
  const N_d2 = normalCdf(-d2)

  // Delta
  if (params.type === 'call') {
    greeks.delta = Nd1
  } else {
    greeks.delta = N_d1 - 1
  }

  // Gamma
  greeks.gamma = nd1 / (S * sigma * Math.sqrt(T))

  // Vega (на 1% изменения волатильности)
  greeks.vega = S * nd1 * Math.sqrt(T) / 100

  // Theta (в день)
  if (params.type === 'call') {
    greeks.theta = (-S * nd1 * sigma / (2 * Math.sqrt(T)) - r * K * Math.exp(-r * T) * Nd2) / 365
  } else {
    greeks.theta = (-S * nd1 * sigma / (2 * Math.sqrt(T)) + r * K * Math.exp(-r * T) * N_d2) / 365
  }

  // Rho (на 1% изменения ставки)
  greeks.rho = (params.type === 'call' 
    ? K * T * Math.exp(-r * T) * Nd2 
    : -K * T * Math.exp(-r * T) * N_d2) / 100

  // === Матрица чувствительности ===
  const spotShifts = [-10, -5, 0, 5, 10]
  const volShifts = [-2, -1, 0, 1, 2]
  const basePrice = calculateOptionPrice(S, K, r, sigma, T, params.type)

  sensitivityMatrix.value = spotShifts.map(dS => {
    return volShifts.map(dVol => {
      const newS = S + dS
      const newSigma = sigma + dVol / 100
      const newPrice = calculateOptionPrice(newS, K, r, newSigma, T, params.type)
      return newPrice - basePrice
    })
  })
}

// ===== Computed P&L Components =====
const deltaComponent = computed(() => {
  return (greeks.delta || 0) * scenario.deltaS
})

const gammaComponent = computed(() => {
  return 0.5 * (greeks.gamma || 0) * Math.pow(scenario.deltaS, 2)
})

const vegaComponent = computed(() => {
  return (greeks.vega || 0) * scenario.deltaSigma
})

const thetaComponent = computed(() => {
  return (greeks.theta || 0) * scenario.deltaT
})

const totalPL = computed(() => {
  return deltaComponent.value + gammaComponent.value + vegaComponent.value + thetaComponent.value
})

const getGreekStatusColor = computed(() => {
  return params.type === 'call' ? 'bg-green' : 'bg-red'
})

// Initial calculation
calculateGreeks()
</script>

<style scoped>
/* Main Layout */
.page-container {
  padding: 24px 32px;
  max-width: 1500px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  flex: 0;
  min-height: auto;
}

.left-panel, .main-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: visible;
  overflow-x: hidden;
}

/* Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: #fff;
  letter-spacing: -0.01em;
}

.section-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 0 0;
}

/* Glass Components */
.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  box-shadow: 0 20px 50px -10px rgba(0, 0, 0, 0.5);
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 99px;
  height: 36px;
}

.panel {
  padding: 24px;
}

.panel-header h3 {
  margin: 0 0 16px 0;
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 700;
  letter-spacing: 0.05em;
}

/* Controls */
.controls-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lbl {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.glass-input {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 12px;
  width: 100%;
  outline: none;
  transition: 0.2s;
  font-size: 12px;
}

.glass-input:focus {
  border-color: #3b82f6;
  background: rgba(0, 0, 0, 0.5);
}

.glass-input-sm {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 8px 10px;
  border-radius: 8px;
  outline: none;
  transition: 0.2s;
  font-size: 11px;
  width: 100%;
}

.glass-input-sm:focus {
  border-color: #3b82f6;
  background: rgba(0, 0, 0, 0.5);
}

.radio-group {
  display: flex;
  gap: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  cursor: pointer;
}

.radio-label input {
  cursor: pointer;
  accent-color: #3b82f6;
}

/* Stats */
.stats-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.greek-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #3b82f6;
  width: 20px;
}

.s-name {
  font-weight: 600;
  color: #fff;
}

.val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
  color: #fff;
}

/* Charts */
.chart-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Scenario */
.scenario-controls {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.scenario-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.scenario-input label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.pl-results {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.pl-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 12px;
}

.pl-row.divider {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 8px 0;
}

.pl-row.total {
  border-top: 2px solid rgba(255, 255, 255, 0.2);
  padding-top: 12px;
  margin-top: 8px;
  font-weight: 600;
}

.pl-label {
  color: rgba(255, 255, 255, 0.7);
}

.pl-value {
  font-family: "SF Mono", monospace;
  color: #fff;
}

.pl-results.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
}

/* Table */
.sensitivity-table {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.data-table th {
  text-align: center;
  padding: 10px 4px;
  background: rgba(59, 130, 246, 0.1);
  font-weight: 600;
  color: rgba(209, 213, 219, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td {
  text-align: center;
  padding: 8px 4px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: rgba(226, 232, 240, 0.9);
}

.row-header {
  font-weight: 600;
  background: rgba(59, 130, 246, 0.05);
}

.positive {
  color: #4ade80;
  font-weight: 600;
}

.negative {
  color: #f87171;
  font-weight: 600;
}

/* Utilities */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}

.bg-green {
  background: #4ade80;
  color: #4ade80;
}

.bg-red {
  background: #f87171;
  color: #f87171;
}

.text-white {
  color: #fff;
}

.text-green {
  color: #4ade80;
}

.text-red {
  color: #f87171;
}

.mono {
  font-family: "SF Mono", monospace;
}

.mt-4 {
  margin-top: 16px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .scenario-controls {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px 20px;
  }

  .scenario-controls {
    grid-template-columns: 1fr;
  }
}
</style>