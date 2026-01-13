<!-- src/pages/StressTestingSwap.vue -->
<template>
  <div class="stress-swap-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Стресс-тест СВОП портфеля</h1>
        <p class="page-subtitle">Анализ чувствительности к сдвигам кривой, спредам и волатильности</p>
      </div>
      
      <div class="header-right">
        <!-- Severity Multiplier -->
        <div class="control-group">
          <label class="control-label">Множитель:</label>
          <div class="multiplier-control">
            <input 
              type="range"
              v-model.number="shockMultiplier"
              :step="0.1"
              :min="0.5"
              :max="3.0"
              class="range-input"
            />
            <span class="multiplier-display">{{ shockMultiplier.toFixed(1) }}x</span>
          </div>
        </div>

        <button 
          @click="runStressTests" 
          class="btn-primary"
          :disabled="isRunning"
        >
          <span v-if="!isRunning">Запустить</span>
          <span v-else>Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Shock Type Filters -->
    <div class="filters-bar">
      <button 
        v-for="shockType in shockTypes"
        :key="shockType.id"
        @click="activeShockType = shockType.id"
        class="filter-btn"
        :class="{ active: activeShockType === shockType.id }"
      >
        <span class="filter-icon">{{ shockType.icon }}</span>
        <span class="filter-text">{{ shockType.name }}</span>
      </button>
    </div>

    <!-- Scenarios Grid -->
    <div class="scenarios-container">
      <div class="grid-header">Сценарии стресс-тестирования</div>
      <div class="scenarios-grid">
        <div 
          v-for="scenario in filteredScenarios" 
          :key="scenario.id"
          @click="selectScenario(scenario)"
          class="scenario-tile"
          :class="{ active: selectedScenario?.id === scenario.id }"
        >
          <div class="tile-header">
            <h3 class="tile-title">{{ scenario.name }}</h3>
            <span class="severity-indicator">
              {{ getSeverityIcon(scenario.severity) }}
            </span>
          </div>
          <p class="tile-description">{{ scenario.description }}</p>
          <div class="tile-metrics">
            <span class="metric-value" :class="scenario.pnlImpact < 0 ? 'loss' : 'gain'">
              {{ formatCompactCurrency(scenario.pnlImpact * shockMultiplier) }}
            </span>
            <span class="metric-probability">Вер.: {{ (scenario.probability * 100).toFixed(0) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Panel -->
    <transition name="expand">
      <div v-if="selectedScenario" class="details-container">
        
        <!-- Left Column -->
        <div class="details-left">
          
          <!-- Impact Summary Card -->
          <div class="card">
            <div class="card-header">
              <h3>{{ selectedScenario.name }}</h3>
            </div>
            <div class="metrics-grid">
              <div class="metric-box">
                <span class="metric-label">Влияние на P&L</span>
                <span class="metric-num" :class="selectedScenario.pnlImpact < 0 ? 'loss' : 'gain'">
                  {{ formatCurrency(selectedScenario.pnlImpact * shockMultiplier) }}
                </span>
              </div>
              <div class="metric-box">
                <span class="metric-label">DV01 Δ</span>
                <span class="metric-num accent">
                  {{ (selectedScenario.dv01Change * shockMultiplier).toFixed(1) }}М
                </span>
              </div>
              <div class="metric-box">
                <span class="metric-label">Spread DV01</span>
                <span class="metric-num blue">
                  {{ (selectedScenario.spreadDv01 * shockMultiplier).toFixed(2) }}М
                </span>
              </div>
              <div class="metric-box">
                <span class="metric-label">Длительность</span>
                <span class="metric-num">{{ selectedScenario.duration }}</span>
              </div>
            </div>
          </div>

          <!-- Greeks Card -->
          <div class="card">
            <div class="card-header">
              <h3>Греки</h3>
            </div>
            <div class="greeks-grid">
              <div class="greek-item">
                <span class="greek-symbol">Δ</span>
                <span class="greek-name">Delta</span>
                <span class="greek-val accent">{{ selectedScenario.delta.toFixed(3) }}</span>
                <span class="greek-unit">М/100bp</span>
              </div>
              <div class="greek-item">
                <span class="greek-symbol">Γ</span>
                <span class="greek-name">Gamma</span>
                <span class="greek-val blue">{{ selectedScenario.gamma.toFixed(4) }}</span>
                <span class="greek-unit">bp²</span>
              </div>
              <div class="greek-item">
                <span class="greek-symbol">V</span>
                <span class="greek-name">Vega</span>
                <span class="greek-val green">{{ selectedScenario.vega.toFixed(2) }}</span>
                <span class="greek-unit">М/% vol</span>
              </div>
              <div class="greek-item">
                <span class="greek-symbol">Θ</span>
                <span class="greek-name">Theta</span>
                <span class="greek-val purple">{{ selectedScenario.theta.toFixed(2) }}</span>
                <span class="greek-unit">М/день</span>
              </div>
            </div>
          </div>

          <!-- Key Rate Durations Card -->
          <div class="card">
            <div class="card-header">
              <h3>Срочный риск (Key Rate Durations)</h3>
            </div>
            <div class="krd-bars">
              <div v-for="(krd, tenor) in selectedScenario.keyRateDurations" :key="tenor" class="krd-row">
                <span class="krd-label">{{ tenor }}</span>
                <div class="krd-track">
                  <div 
                    class="krd-bar"
                    :class="krd < 0 ? 'negative' : 'positive'"
                    :style="{ width: Math.min(100, Math.abs(krd * shockMultiplier * 8)) + '%' }"
                  />
                </div>
                <span class="krd-value" :class="krd < 0 ? 'loss' : 'gain'">
                  {{ krd > 0 ? '+' : '' }}{{ (krd * shockMultiplier).toFixed(2) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="details-right">
          
          <!-- Market Shocks Card -->
          <div class="card">
            <div class="card-header">
              <h3>Параметры шока</h3>
            </div>
            <div class="shocks-list">
              <div v-for="(change, key) in selectedScenario.marketShocks" :key="key" class="shock-row">
                <span class="shock-label">{{ formatLabel(key) }}</span>
                <span class="shock-val" :class="change.includes('-') ? 'loss' : 'gain'">
                  {{ change }}
                </span>
              </div>
            </div>
          </div>

          <!-- Affected Positions Card -->
          <div class="card">
            <div class="card-header">
              <h3>Позиции под риском</h3>
            </div>
            <div class="positions-list">
              <div v-for="(posImpact, posName) in selectedScenario.positionImpact" :key="posName" class="position-row">
                <span class="pos-name">{{ posName }}</span>
                <span class="pos-val" :class="posImpact < 0 ? 'loss' : 'gain'">
                  {{ posImpact > 0 ? '+' : '' }}{{ formatCompactCurrency(posImpact * shockMultiplier) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Info Card -->
          <div class="card info-card">
            <div class="info-item">
              <strong>Множитель:</strong> {{ shockMultiplier.toFixed(1) }}x
            </div>
            <div class="info-item">
              <strong>Расчёт:</strong> В реальном времени
            </div>
            <div class="info-item">
              <strong>Модель:</strong> Vasicek
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Summary Table -->
    <div class="table-container">
      <div class="table-header">Матрица стресс-тестов</div>
      <table class="data-table">
        <thead>
          <tr>
            <th class="col-name">Сценарий</th>
            <th class="col-type">Тип</th>
            <th class="col-value">P&L</th>
            <th class="col-value">ΔDV01</th>
            <th class="col-value">Spread DV01</th>
            <th class="col-value">Вероят.</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="scenario in scenarios" 
            :key="scenario.id"
            class="table-row"
            :class="{ active: selectedScenario?.id === scenario.id }"
            @click="selectScenario(scenario)"
          >
            <td class="col-name">{{ scenario.name }}</td>
            <td class="col-type">{{ scenario.shockType }}</td>
            <td class="col-value" :class="scenario.pnlImpact < 0 ? 'loss' : 'gain'">
              {{ formatCurrency(scenario.pnlImpact * shockMultiplier) }}
            </td>
            <td class="col-value accent">{{ (scenario.dv01Change * shockMultiplier).toFixed(1) }}</td>
            <td class="col-value blue">{{ (scenario.spreadDv01 * shockMultiplier).toFixed(2) }}</td>
            <td class="col-value accent">{{ (scenario.probability * 100).toFixed(0) }}%</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Историческое моделирование Vasicek</span>
      <span>• Пересмотр каждые 2 недели</span>
      <span>• Коррелированные шоки между параметрами</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const isRunning = ref(false)
const shockMultiplier = ref(1.0)
const activeShockType = ref('curve')

// Shock Types
const shockTypes = ref([
  { id: 'curve', name: 'Сдвиг кривой', icon: '' },
  { id: 'spread', name: 'Спред', icon: '' },
  { id: 'vol', name: 'Волатильность', icon: '' },
  { id: 'twist', name: 'Кривизна', icon: '' }
])

// All Scenarios
const scenarios = ref([
  // === CURVE SHOCKS ===
  {
    id: 1,
    name: 'Параллельный сдвиг +200 bp',
    description: 'Все ставки растут на 200 базисных пункта',
    shockType: 'Curve',
    pnlImpact: -285000,
    dv01Change: -28.5,
    spreadDv01: 0,
    delta: 5.2,
    gamma: 0.018,
    vega: -12.5,
    theta: 1.2,
    duration: '1–2 дня',
    probability: 0.08,
    severity: 'high',
    marketShocks: { 'Key Rate (2Y)': '+200 bp', 'Key Rate (5Y)': '+200 bp', 'Key Rate (10Y)': '+200 bp', 'Volatility': '-5%' },
    keyRateDurations: { '2Y': -3.5, '5Y': -8.2, '10Y': -5.1, '30Y': -2.8 },
    positionImpact: { 'IRS Payer 5Y': -145000, 'IRS Receiver 2Y': 25000, 'Bond Hold': -165000 }
  },
  {
    id: 2,
    name: 'Параллельный сдвиг −200 bp',
    description: 'Все ставки падают на 200 базисных пункта',
    shockType: 'Curve',
    pnlImpact: 285000,
    dv01Change: 28.5,
    spreadDv01: 0,
    delta: -5.2,
    gamma: 0.018,
    vega: 12.5,
    theta: -1.2,
    duration: '1–2 дня',
    probability: 0.08,
    severity: 'high',
    marketShocks: { 'Key Rate (2Y)': '-200 bp', 'Key Rate (5Y)': '-200 bp', 'Key Rate (10Y)': '-200 bp', 'Volatility': '+5%' },
    keyRateDurations: { '2Y': 3.5, '5Y': 8.2, '10Y': 5.1, '30Y': 2.8 },
    positionImpact: { 'IRS Payer 5Y': 145000, 'IRS Receiver 2Y': -25000, 'Bond Hold': 165000 }
  },
  {
    id: 3,
    name: 'Крутизна кривой (Twist)',
    description: 'Короткие ставки +150 bp, длинные −50 bp',
    shockType: 'Curve',
    pnlImpact: -45200,
    dv01Change: -8.5,
    spreadDv01: 0.5,
    delta: 2.1,
    gamma: 0.025,
    vega: -8.3,
    theta: 0.6,
    duration: '2–5 дней',
    probability: 0.18,
    severity: 'medium',
    marketShocks: { 'Key Rate (2Y)': '+150 bp', 'Key Rate (5Y)': '+50 bp', 'Key Rate (10Y)': '-50 bp', 'Slope': '−200 bp' },
    keyRateDurations: { '2Y': -2.8, '5Y': 1.2, '10Y': 3.5, '30Y': 1.1 },
    positionImpact: { 'IRS Payer 5Y': -32000, 'IRS Receiver 10Y': 18000, 'Curve Trade': -31200 }
  },
  {
    id: 4,
    name: 'Бабочка (Butterfly)',
    description: 'Середина кривой сдвигается относительно краёв',
    shockType: 'Curve',
    pnlImpact: 18500,
    dv01Change: 3.2,
    spreadDv01: -0.8,
    delta: 1.5,
    gamma: 0.035,
    vega: -3.1,
    theta: 0.4,
    duration: '3–10 дней',
    probability: 0.25,
    severity: 'low',
    marketShocks: { 'Key Rate (2Y)': '+50 bp', 'Key Rate (5Y)': '-100 bp', 'Key Rate (10Y)': '+50 bp' },
    keyRateDurations: { '2Y': 1.2, '5Y': -3.5, '10Y': 1.8, '30Y': -0.5 },
    positionImpact: { 'IRS Payer 5Y': 28500, 'Butterfly Trade': 12000, 'Long Bond': -22000 }
  },
  // === SPREAD SHOCKS ===
  {
    id: 5,
    name: 'Кредитный спред +100 bp',
    description: 'Широкое расширение spreads (OAS +100 bp)',
    shockType: 'Spread',
    pnlImpact: -125400,
    dv01Change: 0,
    spreadDv01: 5.2,
    delta: 0.8,
    gamma: 0.008,
    vega: -15.2,
    theta: 0.2,
    duration: '1–5 дней',
    probability: 0.12,
    severity: 'high',
    marketShocks: { 'OAS': '+100 bp', 'Credit Curve': '−25 bp', 'Term Spread': '+75 bp', 'Vol': '+8%' },
    keyRateDurations: { '2Y': -0.5, '5Y': -2.1, '10Y': -1.8, '30Y': -0.9 },
    positionImpact: { 'Corporate Bonds': -85000, 'Credit Default Swaps': -40400, 'IRS': 0 }
  },
  {
    id: 6,
    name: 'Кредитный спред −50 bp',
    description: 'Сжатие spreads (OAS −50 bp)',
    shockType: 'Spread',
    pnlImpact: 62700,
    dv01Change: 0,
    spreadDv01: -2.6,
    delta: -0.4,
    gamma: 0.008,
    vega: 7.6,
    theta: -0.1,
    duration: '2–10 дней',
    probability: 0.20,
    severity: 'medium',
    marketShocks: { 'OAS': '−50 bp', 'Credit Curve': '+15 bp', 'Term Spread': '−35 bp', 'Vol': '−4%' },
    keyRateDurations: { '2Y': 0.3, '5Y': 1.1, '10Y': 0.9, '30Y': 0.5 },
    positionImpact: { 'Corporate Bonds': 45000, 'CDS': 18000, 'IRS': -300 }
  },
  // === VOLATILITY SHOCKS ===
  {
    id: 7,
    name: 'Скачок vol ставок (Swaption)',
    description: 'Волатильность swap rates +300 bp (ATM vol +5%)',
    shockType: 'Vol',
    pnlImpact: -95300,
    dv01Change: 2.5,
    spreadDv01: 0,
    delta: 1.2,
    gamma: 0.012,
    vega: 18.5,
    theta: -0.8,
    duration: '1–3 дня',
    probability: 0.06,
    severity: 'high',
    marketShocks: { 'Volatility (ATM)': '+5%', 'Implied Vol': '+500 bp', 'Skew': '+50 bp', 'Term Vol': '+3%' },
    keyRateDurations: { '2Y': 0.8, '5Y': 2.3, '10Y': 1.5, '30Y': 0.6 },
    positionImpact: { 'Swaptions (Long)': 85000, 'IRS': -15000, 'Vol Hedges': -165300 }
  },
  {
    id: 8,
    name: 'Падение vol ставок',
    description: 'Волатильность swap rates −200 bp',
    shockType: 'Vol',
    pnlImpact: 63500,
    dv01Change: -1.8,
    spreadDv01: 0,
    delta: -0.8,
    gamma: -0.012,
    vega: -12.3,
    theta: 0.5,
    duration: '5–15 дней',
    probability: 0.15,
    severity: 'medium',
    marketShocks: { 'Volatility (ATM)': '−3.5%', 'Implied Vol': '−350 bp', 'Skew': '−30 bp', 'Term Vol': '−2%' },
    keyRateDurations: { '2Y': -0.6, '5Y': -1.8, '10Y': -1.1, '30Y': -0.5 },
    positionImpact: { 'Swaptions (Short)': 78500, 'Vol Trades': -15000 }
  },
  // === COMBINED ===
  {
    id: 9,
    name: 'Шоковый сценарий',
    description: 'Комбинация: ставки +150 bp, спред +75 bp, vol +4%',
    shockType: 'Curve',
    pnlImpact: -425600,
    dv01Change: -32.1,
    spreadDv01: 3.8,
    delta: 7.5,
    gamma: 0.042,
    vega: -28.4,
    theta: 0.8,
    duration: '1–2 дня',
    probability: 0.02,
    severity: 'critical',
    marketShocks: { 'Curve': '+150 bp', 'OAS': '+75 bp', 'Volatility': '+4%', 'Correlation': '+0.35' },
    keyRateDurations: { '2Y': -5.2, '5Y': -12.5, '10Y': -9.3, '30Y': -5.1 },
    positionImpact: { 'IRS Payer 5Y': -245000, 'Corp Bonds': -125000, 'Swaptions': -55600 }
  }
])

const selectedScenario = ref(scenarios.value[0])

// Computed
const filteredScenarios = computed(() => {
  const typeMap: { [key: string]: string } = {
    'curve': 'Curve',
    'spread': 'Spread',
    'vol': 'Vol',
    'twist': 'Curve'
  }
  return scenarios.value.filter(s => s.shockType === typeMap[activeShockType.value])
})

// Methods
const selectScenario = (scenario: any) => {
  selectedScenario.value = scenario
}

const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(val)
}

const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(1) + 'М'
  }
  return '$' + (val / 1000).toFixed(0) + 'K'
}

const formatLabel = (key: string) => {
  const map: { [key: string]: string } = {
    'Volatility (ATM)': 'Vol (ATM)',
    'Key Rate (2Y)': 'Rate 2Y',
    'Key Rate (5Y)': 'Rate 5Y',
    'Key Rate (10Y)': 'Rate 10Y',
    'OAS': 'OAS Spread',
  }
  return map[key] || key
}

const getSeverityIcon = (severity: string) => {
  const icons: { [key: string]: string } = {
    'critical': '',
    'high': '',
    'medium': '',
    'low': ''
  }
  return icons[severity] || ''
}

const runStressTests = async () => {
  if (isRunning.value) return
  isRunning.value = true
  
  try {
    for (let i = 0; i <= 100; i += 20) {
      await new Promise(r => setTimeout(r, 250))
    }
  } catch (e) {
    console.error(e)
  } finally {
    isRunning.value = false
  }
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.stress-swap-page {
  width: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(15,20,25,0.5) 0%, rgba(26,31,46,0.3) 100%);
  color: #fff;
}

/* ============================================
   HEADER
   ============================================ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
  flex-wrap: wrap;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.04);
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
}

.control-label {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.multiplier-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-input {
  -webkit-appearance: none;
  appearance: none;
  width: 80px;
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.range-input::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.range-input::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: grab;
  border: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.multiplier-display {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 13px;
  color: #3b82f6;
  width: 35px;
  text-align: right;
}

.btn-primary {
  padding: 8px 16px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* ============================================
   FILTERS BAR
   ============================================ */
.filters-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 8px 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.2);
  color: #fff;
}

.filter-btn.active {
  background: #3b82f6;
  border-color: #2563eb;
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.filter-icon {
  font-size: 14px;
}

.filter-text {
  white-space: nowrap;
}

/* ============================================
   SCENARIOS GRID
   ============================================ */
.scenarios-container {
  margin-bottom: 32px;
}

.grid-header {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.scenario-tile {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 140px;
  justify-content: space-between;
}

.scenario-tile:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(30, 32, 40, 0.6);
}

.scenario-tile.active {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.15);
}

.tile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.tile-title {
  font-size: 13px;
  font-weight: 700;
  margin: 0;
  line-height: 1.3;
  flex: 1;
}

.severity-indicator {
  font-size: 16px;
  flex-shrink: 0;
}

.tile-description {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  margin: 0;
  line-height: 1.4;
}

.tile-metrics {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.metric-value {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 14px;
}

.metric-value.loss {
  color: #f87171;
}

.metric-value.gain {
  color: #4ade80;
}

.metric-probability {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   DETAILS PANEL
   ============================================ */
.details-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.details-left,
.details-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Card Styling */
.card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.metric-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(255,255,255,0.03);
  padding: 12px;
  border-radius: 8px;
}

.metric-label {
  font-size: 9px;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.metric-num {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 13px;
  color: #fff;
}

.metric-num.loss {
  color: #f87171;
}

.metric-num.gain {
  color: #4ade80;
}

.metric-num.accent {
  color: #f59e0b;
}

.metric-num.blue {
  color: #60a5fa;
}

/* Greeks Grid */
.greeks-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.greek-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: rgba(255,255,255,0.03);
  padding: 12px;
  border-radius: 8px;
  text-align: center;
}

.greek-symbol {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.greek-name {
  font-size: 9px;
  color: rgba(255,255,255,0.5);
  font-weight: 500;
}

.greek-val {
  font-family: "SF Mono", monospace;
  font-weight: 700;
  font-size: 12px;
}

.greek-val.accent {
  color: #f59e0b;
}

.greek-val.blue {
  color: #60a5fa;
}

.greek-val.green {
  color: #4ade80;
}

.greek-val.purple {
  color: #c084fc;
}

.greek-unit {
  font-size: 8px;
  color: rgba(255,255,255,0.3);
}

/* KRD Bars */
.krd-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.krd-row {
  display: grid;
  grid-template-columns: 45px 1fr 45px;
  align-items: center;
  gap: 10px;
}

.krd-label {
  font-size: 10px;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
  text-align: center;
}

.krd-track {
  height: 5px;
  background: rgba(255,255,255,0.05);
  border-radius: 2px;
  overflow: hidden;
}

.krd-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.krd-bar.negative {
  background: #f87171;
}

.krd-bar.positive {
  background: #4ade80;
}

.krd-value {
  font-family: "SF Mono", monospace;
  font-size: 10px;
  text-align: right;
  font-weight: 600;
}

.krd-value.loss {
  color: #f87171;
}

.krd-value.gain {
  color: #4ade80;
}

/* Shocks List */
.shocks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.shock-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.shock-row:last-child {
  border-bottom: none;
}

.shock-label {
  color: rgba(255,255,255,0.6);
  font-weight: 500;
}

.shock-val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.shock-val.loss {
  color: #f87171;
}

.shock-val.gain {
  color: #4ade80;
}

/* Positions List */
.positions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.position-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.position-row:last-child {
  border-bottom: none;
}

.pos-name {
  color: rgba(255,255,255,0.7);
  font-weight: 500;
}

.pos-val {
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.pos-val.loss {
  color: #f87171;
}

.pos-val.gain {
  color: #4ade80;
}

/* Info Card */
.info-card {
  background: rgba(255,255,255,0.02);
  border-left: 2px solid rgba(59, 130, 246, 0.3);
}

.info-item {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  line-height: 1.6;
}

.info-item strong {
  color: #fff;
}

/* ============================================
   TABLE
   ============================================ */
.table-container {
  margin-bottom: 24px;
}

.table-header {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
  font-size: 12px;
}

.data-table thead {
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.data-table th {
  padding: 12px;
  text-align: right;
  color: rgba(255,255,255,0.4);
  font-weight: 600;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table th.col-name {
  text-align: left;
}

.data-table td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: "SF Mono", monospace;
  color: #fff;
  font-weight: 500;
}

.data-table td.col-name {
  text-align: left;
  font-family: inherit;
}

.data-table tbody tr {
  cursor: pointer;
  transition: background 0.2s;
}

.data-table tbody tr:hover {
  background: rgba(255,255,255,0.05);
}

.data-table tbody tr.active {
  background: rgba(59, 130, 246, 0.1);
}

.col-value.loss {
  color: #f87171;
}

.col-value.gain {
  color: #4ade80;
}

.col-value.accent {
  color: #f59e0b;
}

.col-value.blue {
  color: #60a5fa;
}

.col-type {
  color: rgba(255,255,255,0.5);
}

/* ============================================
   FOOTER
   ============================================ */
.page-footer {
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 11px;
  color: rgba(255,255,255,0.3);
  margin-top: 24px;
  flex-wrap: wrap;
}

/* ============================================
   TRANSITIONS
   ============================================ */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.expand-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1400px) {
  .scenarios-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }

  .details-container {
    grid-template-columns: 1fr;
  }

  .metrics-grid,
  .greeks-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .control-group {
    width: 100%;
    justify-content: space-between;
  }

  .btn-primary {
    width: 100%;
  }

  .filters-bar {
    flex-direction: column;
  }

  .filter-btn {
    width: 100%;
    justify-content: center;
  }

  .scenarios-grid {
    grid-template-columns: 1fr;
  }

  .metrics-grid,
  .greeks-grid {
    grid-template-columns: 1fr;
  }

  .page-footer {
    flex-direction: column;
    gap: 8px;
  }
}
</style>