<!-- src/pages/OptionPricingAnalyzer.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Справедливая стоимость опционов</h1>
        <p class="section-subtitle">Black-Scholes, модель Хестона, процессы Леви, FFT-ценообразование</p>
      </div>
      
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="dot" :class="params.optionType === 'call' ? 'bg-green' : 'bg-red'"></span>
            <span class="status-label">Модель: <b class="text-white">{{ params.model === 'bsm' ? 'Black-Scholes' : 'Heston' }}</b></span>
         </div>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT PANEL: Controls -->
        <aside class="left-panel">
            
            <!-- Parameters Card -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Входные параметры</h3></div>
                
                <div class="controls-form">
                    <!-- Spot Price -->
                    <div class="input-group">
                        <label class="lbl">S (Spot)</label>
                        <input v-model.number="params.S" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>
                    
                    <!-- Strike -->
                    <div class="input-group">
                        <label class="lbl">K (Strike)</label>
                        <input v-model.number="params.K" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Rate -->
                    <div class="input-group">
                        <label class="lbl">r (Rate), %</label>
                        <input v-model.number="params.r" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Volatility -->
                    <div class="input-group">
                        <label class="lbl">σ (Vol), %</label>
                        <input v-model.number="params.sigma" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Time to Maturity -->
                    <div class="input-group">
                        <label class="lbl">T (Time), years</label>
                        <input v-model.number="params.T" type="number" step="0.01" min="0.001" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Dividend Yield -->
                    <div class="input-group">
                        <label class="lbl">q (Div Yield), %</label>
                        <input v-model.number="params.q" type="number" step="0.01" class="glass-input" @change="calculatePrice" />
                    </div>

                    <!-- Option Type -->
                    <div class="input-group">
                        <label class="lbl">Тип опциона</label>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input v-model="params.optionType" type="radio" value="call" @change="calculatePrice" />
                                <span>Call</span>
                            </label>
                            <label class="radio-label">
                                <input v-model="params.optionType" type="radio" value="put" @change="calculatePrice" />
                                <span>Put</span>
                            </label>
                        </div>
                    </div>

                    <!-- Model Type -->
                    <div class="input-group">
                        <label class="lbl">Модель</label>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input v-model="params.model" type="radio" value="bsm" @change="calculatePrice" />
                                <span>BSM</span>
                            </label>
                            <label class="radio-label">
                                <input v-model="params.model" type="radio" value="heston" @change="calculatePrice" />
                                <span>Heston</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Price & Greeks Stats -->
            <transition name="fade">
            <div class="glass-card panel" v-if="results.price !== null">
                 <div class="panel-header"><h3>Цена & греки</h3></div>
                 <div class="stats-list">
                     <div class="stat-item price-highlight">
                         <div class="stat-head">
                             <span class="stat-icon">💰</span> 
                             <span class="s-name">Цена опциона</span>
                         </div>
                         <span class="val mono" style="font-size: 16px; color: #3b82f6;">{{ results.price.toFixed(4) }}</span>
                     </div>

                     <div class="divider"></div>

                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Δ</span> 
                             <span class="s-name">Дельта</span>
                         </div>
                         <span class="val mono">{{ results.delta?.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Γ</span> 
                             <span class="s-name">Гамма</span>
                         </div>
                         <span class="val mono">{{ results.gamma?.toFixed(6) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">ν</span> 
                             <span class="s-name">Вега</span>
                         </div>
                         <span class="val mono">{{ results.vega?.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">Θ</span> 
                             <span class="s-name">Тета</span>
                         </div>
                         <span class="val mono" :class="results.theta < 0 ? 'text-red' : 'text-green'">{{ results.theta?.toFixed(4) }}</span>
                     </div>
                     <div class="stat-item">
                         <div class="stat-head">
                             <span class="greek-symbol">ρ</span> 
                             <span class="s-name">Ро</span>
                         </div>
                         <span class="val mono">{{ results.rho?.toFixed(4) }}</span>
                     </div>
                 </div>
            </div>
            </transition>

        </aside>

        <!-- RIGHT PANEL: Analysis -->
        <main class="main-panel">
            
            <!-- Price Decomposition -->
            <div class="glass-card chart-card">
                <div class="chart-header">
                    <h3>Декомпозиция стоимости</h3>
                </div>

                <div class="decomposition-grid" v-if="results.price !== null">
                    <div class="decomp-item">
                        <div class="decomp-label">Внутренняя стоимость</div>
                        <div class="decomp-value">{{ results.intrinsicValue?.toFixed(4) }}</div>
                        <div class="decomp-percent">{{ ((results.intrinsicValue / results.price) * 100).toFixed(1) }}%</div>
                    </div>
                    <div class="decomp-item">
                        <div class="decomp-label">Временная стоимость</div>
                        <div class="decomp-value">{{ results.timeValue?.toFixed(4) }}</div>
                        <div class="decomp-percent">{{ ((results.timeValue / results.price) * 100).toFixed(1) }}%</div>
                    </div>
                    <div class="decomp-item">
                        <div class="decomp-label">Moneyness (S/K)</div>
                        <div class="decomp-value">{{ (params.S / params.K).toFixed(4) }}</div>
                        <div class="decomp-percent" :class="params.S/params.K > 1 ? 'text-green' : params.S/params.K < 1 ? 'text-red' : ''">
                            {{ params.S > params.K ? 'ITM' : params.S < params.K ? 'OTM' : 'ATM' }}
                        </div>
                    </div>
                </div>

                <div class="empty-state" v-else>
                    <span>Рассчитайте стоимость для анализа</span>
                </div>
            </div>

            <!-- Greeks Sensitivity -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Матрица чувствительности (S × σ)</h3>
                </div>
                
                <div class="sensitivity-table" v-if="sensitivityMatrix.length">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>S \ σ</th>
                                <th>σ - 5%</th>
                                <th>σ - 2.5%</th>
                                <th>σ базовая</th>
                                <th>σ + 2.5%</th>
                                <th>σ + 5%</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, i) in sensitivityMatrix" :key="i">
                                <td class="row-header">{{ [-20, -10, 0, 10, 20][i] }}%</td>
                                <td v-for="(val, j) in row" :key="j" :class="{ positive: val > results.price, negative: val < results.price }">
                                    {{ val.toFixed(3) }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="empty-state" v-else>
                    <span>Матрица будет заполнена после расчёта</span>
                </div>
            </div>

            <!-- Payoff Diagram -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Payoff диаграмма (при экспирации)</h3>
                </div>
                
                <div class="chart-container">
                    <svg v-if="payoffData.length" viewBox="0 0 800 300" preserveAspectRatio="none" class="payoff-svg">
                        <!-- Grid -->
                        <line x1="0" y1="150" x2="800" y2="150" stroke="rgba(255,255,255,0.1)" stroke-dasharray="2" />
                        <line v-for="x in [0, 200, 400, 600, 800]" :key="x" :x1="x" y1="140" :x2="x" y2="160" stroke="rgba(255,255,255,0.2)" />
                        
                        <!-- Strike line -->
                        <line :x1="strikeX" y1="0" :x2="strikeX" y2="300" stroke="rgba(148, 163, 184, 0.3)" stroke-dasharray="4" />
                        
                        <!-- Payoff line -->
                        <polyline :points="payoffPath" fill="none" stroke="#3b82f6" stroke-width="3" stroke-linejoin="round" />
                        
                        <!-- Current price marker -->
                        <circle :cx="currentPriceX" :cy="currentPriceY" r="5" fill="#ef4444" />
                    </svg>
                    <div v-else class="empty-state">
                        <span>График будет построен после расчёта</span>
                    </div>
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
  q: 0,
  optionType: 'call',
  model: 'bsm',
})

const results = reactive({
  price: null as number | null,
  delta: null as number | null,
  gamma: null as number | null,
  vega: null as number | null,
  theta: null as number | null,
  rho: null as number | null,
  intrinsicValue: null as number | null,
  timeValue: null as number | null,
})

const sensitivityMatrix = ref<number[][]>([])
const payoffData = ref<number[]>([])

// ===== Black-Scholes Helpers =====
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

const calculateOptionPrice = (S: number, K: number, r: number, sigma: number, T: number, q: number, optionType: string): number => {
  if (sigma <= 0 || T <= 0) return 0
  const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  if (optionType === 'call') {
    return S * Math.exp(-q * T) * normalCdf(d1) - K * Math.exp(-r * T) * normalCdf(d2)
  } else {
    return K * Math.exp(-r * T) * normalCdf(-d2) - S * Math.exp(-q * T) * normalCdf(-d1)
  }
}

const calculatePrice = () => {
  const S = params.S
  const K = params.K
  const r = params.r / 100
  const sigma = params.sigma / 100
  const T = params.T
  const q = params.q / 100

  if (S <= 0 || K <= 0 || T <= 0 || sigma <= 0) {
    results.price = null
    results.delta = null
    results.gamma = null
    results.vega = null
    results.theta = null
    results.rho = null
    sensitivityMatrix.value = []
    payoffData.value = []
    return
  }

  const d1 = (Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * Math.sqrt(T))
  const d2 = d1 - sigma * Math.sqrt(T)

  const Nd1 = normalCdf(d1)
  const Nd2 = normalCdf(d2)
  const N_d1 = normalCdf(-d1)
  const N_d2 = normalCdf(-d2)
  const nd1 = normalPdf(d1)

  let price: number
  if (params.optionType === 'call') {
    price = S * Math.exp(-q * T) * Nd1 - K * Math.exp(-r * T) * Nd2
    results.delta = Math.exp(-q * T) * Nd1
  } else {
    price = K * Math.exp(-r * T) * N_d2 - S * Math.exp(-q * T) * N_d1
    results.delta = -Math.exp(-q * T) * N_d1
  }

  results.gamma = (Math.exp(-q * T) * nd1) / (S * sigma * Math.sqrt(T))
  results.vega = S * Math.exp(-q * T) * nd1 * Math.sqrt(T) / 100
  results.rho = (params.optionType === 'call' 
    ? K * T * Math.exp(-r * T) * Nd2 
    : -K * T * Math.exp(-r * T) * N_d2) / 100

  if (params.optionType === 'call') {
    results.theta = (-S * Math.exp(-q * T) * nd1 * sigma / (2 * Math.sqrt(T)) + q * S * Math.exp(-q * T) * Nd1 - r * K * Math.exp(-r * T) * Nd2) / 365
  } else {
    results.theta = (-S * Math.exp(-q * T) * nd1 * sigma / (2 * Math.sqrt(T)) - q * S * Math.exp(-q * T) * N_d1 + r * K * Math.exp(-r * T) * N_d2) / 365
  }

  results.price = price
  
  if (params.optionType === 'call') {
    results.intrinsicValue = Math.max(S - K, 0)
  } else {
    results.intrinsicValue = Math.max(K - S, 0)
  }
  results.timeValue = Math.max(price - results.intrinsicValue, 0)

  // === Sensitivity Matrix ===
  const spotShifts = [-20, -10, 0, 10, 20]
  const volShifts = [-5, -2.5, 0, 2.5, 5]

  sensitivityMatrix.value = spotShifts.map(dS => {
    return volShifts.map(dVol => {
      const newS = S * (1 + dS / 100)
      const newSigma = sigma + dVol / 100
      return calculateOptionPrice(newS, K, r, newSigma, T, q, params.optionType)
    })
  })

  // === Payoff Diagram ===
  payoffData.value = []
  const minS = K * 0.5
  const maxS = K * 1.5
  for (let s = minS; s <= maxS; s += (maxS - minS) / 50) {
    let payoff = 0
    if (params.optionType === 'call') {
      payoff = Math.max(s - K, 0)
    } else {
      payoff = Math.max(K - s, 0)
    }
    payoffData.value.push(payoff)
  }
}

const payoffPath = computed(() => {
  if (!payoffData.value.length) return ''
  const minS = params.K * 0.5
  const maxS = params.K * 1.5
  const maxPayoff = Math.max(...payoffData.value)
  
  return payoffData.value.map((p, i) => {
    const x = (i / payoffData.value.length) * 800
    const y = 300 - (p / (maxPayoff || 1)) * 250 - 25
    return `${x},${y}`
  }).join(' ')
})

const strikeX = computed(() => {
  const minS = params.K * 0.5
  const maxS = params.K * 1.5
  return ((params.K - minS) / (maxS - minS)) * 800
})

const currentPriceX = computed(() => {
  const minS = params.K * 0.5
  const maxS = params.K * 1.5
  return ((params.S - minS) / (maxS - minS)) * 800
})

const currentPriceY = computed(() => {
  if (!payoffData.value.length) return 0
  const maxPayoff = Math.max(...payoffData.value)
  let payoff = 0
  if (params.optionType === 'call') {
    payoff = Math.max(params.S - params.K, 0)
  } else {
    payoff = Math.max(params.K - params.S, 0)
  }
  return 300 - (payoff / (maxPayoff || 1)) * 250 - 25
})

calculatePrice()
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

.stat-item.price-highlight {
  background: rgba(59, 130, 246, 0.1);
  padding: 10px 8px;
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  margin-bottom: 4px;
}

.stat-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-icon {
  font-size: 14px;
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

.divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin: 8px 0;
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

/* Decomposition */
.decomposition-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.decomp-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.decomp-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.decomp-value {
  font-size: 16px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 4px;
}

.decomp-percent {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
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

/* Chart */
.chart-container {
  width: 100%;
  height: 300px;
  position: relative;
}

.payoff-svg {
  width: 100%;
  height: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
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

  .decomposition-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px 20px;
  }

  .decomposition-grid {
    grid-template-columns: 1fr;
  }
}
</style>