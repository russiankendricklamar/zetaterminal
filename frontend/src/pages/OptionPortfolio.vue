<!-- src/pages/PortfolioOptions.vue -->
<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Портфель опционов</h1>
        <p class="section-subtitle">Агрегированный риск-анализ, греки портфеля, сценарное моделирование</p>
      </div>
      
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="dot bg-blue"></span>
            <span class="status-label">Позиций: <b class="text-white">{{ positions.length }}</b></span>
         </div>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT PANEL: Positions -->
        <aside class="left-panel">
            
            <!-- Portfolio Value Card -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Портфель</h3></div>
                
                <div class="portfolio-summary">
                    <div class="summary-item">
                        <span class="summary-label">Общая стоимость</span>
                        <span class="summary-value">{{ portfolioValue.toFixed(2) }}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Позиций</span>
                        <span class="summary-value">{{ positions.length }}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Дельта портфеля</span>
                        <span class="summary-value">{{ portfolioGreeks.delta.toFixed(2) }}</span>
                    </div>
                </div>

                <button class="btn-primary mt-4" @click="addPosition">+ Добавить позицию</button>
            </div>

            <!-- Positions List -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Позиции</h3></div>
                
                <div class="positions-list">
                    <div v-for="(pos, i) in positions" :key="i" class="position-item">
                        <div class="pos-header">
                            <span class="pos-ticker">{{ pos.ticker }}</span>
                            <span class="pos-type" :class="pos.type">{{ pos.type.toUpperCase() }}</span>
                        </div>
                        <div class="pos-details">
                            <div class="pos-row">
                                <span>K:</span>
                                <span>{{ pos.strike }}</span>
                            </div>
                            <div class="pos-row">
                                <span>Кол-во:</span>
                                <input v-model.number="pos.quantity" type="number" min="0" @change="calculatePortfolio" class="pos-input" />
                            </div>
                            <div class="pos-row">
                                <span>Цена:</span>
                                <span>{{ pos.price.toFixed(2) }}</span>
                            </div>
                            <div class="pos-row">
                                <span>Сумма:</span>
                                <span class="pos-sum">{{ (pos.price * pos.quantity).toFixed(2) }}</span>
                            </div>
                        </div>
                        <button class="btn-delete-small" @click="removePosition(i)">✕</button>
                    </div>
                </div>
            </div>

        </aside>

        <!-- RIGHT PANEL: Analysis -->
        <main class="main-panel">
            
            <!-- Portfolio Greeks -->
            <div class="glass-card chart-card">
                <div class="chart-header">
                    <h3>Агрегированные греки</h3>
                </div>

                <div class="greeks-grid">
                    <div class="greek-card">
                        <div class="greek-icon">Δ</div>
                        <div class="greek-title">Дельта</div>
                        <div class="greek-value">{{ portfolioGreeks.delta.toFixed(2) }}</div>
                        <div class="greek-info">Позиция в базовом активе</div>
                    </div>

                    <div class="greek-card">
                        <div class="greek-icon">Γ</div>
                        <div class="greek-title">Гамма</div>
                        <div class="greek-value">{{ portfolioGreeks.gamma.toFixed(6) }}</div>
                        <div class="greek-info">Кривизна портфеля</div>
                    </div>

                    <div class="greek-card">
                        <div class="greek-icon">ν</div>
                        <div class="greek-title">Вега</div>
                        <div class="greek-value">{{ portfolioGreeks.vega.toFixed(2) }}</div>
                        <div class="greek-info">Чувствительность к vol</div>
                    </div>

                    <div class="greek-card">
                        <div class="greek-icon">Θ</div>
                        <div class="greek-title">Тета</div>
                        <div class="greek-value" :class="portfolioGreeks.theta < 0 ? 'text-red' : 'text-green'">{{ portfolioGreeks.theta.toFixed(2) }}</div>
                        <div class="greek-info">Дневная убыль времени</div>
                    </div>

                    <div class="greek-card">
                        <div class="greek-icon">ρ</div>
                        <div class="greek-title">Ро</div>
                        <div class="greek-value">{{ portfolioGreeks.rho.toFixed(2) }}</div>
                        <div class="greek-info">Чувствительность к ставкам</div>
                    </div>

                    <div class="greek-card">
                        <div class="greek-icon"></div>
                        <div class="greek-title">Риск</div>
                        <div class="greek-value">{{ Math.abs(maxLoss).toFixed(2) }}</div>
                        <div class="greek-info">Максимальный убыток</div>
                    </div>
                </div>
            </div>

            <!-- Scenario Analysis -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Сценарный анализ P&L</h3>
                </div>

                <div class="scenarios-grid">
                    <div class="scenario-card">
                        <div class="scenario-label">Спот +5%</div>
                        <div class="scenario-value" :class="getScenarioPL(5) > 0 ? 'text-green' : 'text-red'">
                            {{ getScenarioPL(5).toFixed(2) }}
                        </div>
                    </div>

                    <div class="scenario-card">
                        <div class="scenario-label">Спот +2.5%</div>
                        <div class="scenario-value" :class="getScenarioPL(2.5) > 0 ? 'text-green' : 'text-red'">
                            {{ getScenarioPL(2.5).toFixed(2) }}
                        </div>
                    </div>

                    <div class="scenario-card">
                        <div class="scenario-label">Спот без изм.</div>
                        <div class="scenario-value" :class="getScenarioPL(0) > 0 ? 'text-green' : 'text-red'">
                            {{ getScenarioPL(0).toFixed(2) }}
                        </div>
                    </div>

                    <div class="scenario-card">
                        <div class="scenario-label">Спот -2.5%</div>
                        <div class="scenario-value" :class="getScenarioPL(-2.5) > 0 ? 'text-green' : 'text-red'">
                            {{ getScenarioPL(-2.5).toFixed(2) }}
                        </div>
                    </div>

                    <div class="scenario-card">
                        <div class="scenario-label">Спот -5%</div>
                        <div class="scenario-value" :class="getScenarioPL(-5) > 0 ? 'text-green' : 'text-red'">
                            {{ getScenarioPL(-5).toFixed(2) }}
                        </div>
                    </div>

                    <div class="scenario-card">
                        <div class="scenario-label">Vol +10%</div>
                        <div class="scenario-value" :class="getScenarioPL(0, 10) > 0 ? 'text-green' : 'text-red'">
                            {{ getScenarioPL(0, 10).toFixed(2) }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- P&L Matrix -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Матрица P&L (Спот vs Волатильность)</h3>
                </div>

                <div class="table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Спот / Vol</th>
                                <th>Vol -2%</th>
                                <th>Vol -1%</th>
                                <th>Vol базовое</th>
                                <th>Vol +1%</th>
                                <th>Vol +2%</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(row, i) in plMatrix" :key="i">
                                <td class="row-header">{{ [-5, -2.5, 0, 2.5, 5][i] }}%</td>
                                <td v-for="(val, j) in row" :key="j" :class="{ positive: val > 0, negative: val < 0 }">
                                    {{ val.toFixed(2) }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Risk Metrics -->
            <div class="glass-card chart-card mt-4">
                <div class="chart-header">
                    <h3>Риск-метрики</h3>
                </div>

                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">Макс. прибыль</div>
                        <div class="metric-value text-green">{{ maxGain.toFixed(2) }}</div>
                        <div class="metric-info">Максимальный выигрыш</div>
                    </div>

                    <div class="metric-item">
                        <div class="metric-label">Макс. убыток</div>
                        <div class="metric-value text-red">{{ maxLoss.toFixed(2) }}</div>
                        <div class="metric-info">Максимальный убыток</div>
                    </div>

                    <div class="metric-item">
                        <div class="metric-label">Точка безубыточности</div>
                        <div class="metric-value">{{ breakeven.toFixed(2) }}</div>
                        <div class="metric-info">Точка безубыточности</div>
                    </div>

                    <div class="metric-item">
                        <div class="metric-label">Риск/Доходность</div>
                        <div class="metric-value">{{ (Math.abs(maxLoss) / Math.abs(maxGain) || 0).toFixed(2) }}</div>
                        <div class="metric-info">Соотношение риска</div>
                    </div>
                </div>
            </div>

        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

interface Position {
  ticker: string
  type: 'call' | 'put'
  strike: number
  quantity: number
  price: number
  delta: number
}

const positions = ref<Position[]>([
  { ticker: 'AAPL', type: 'call', strike: 150, quantity: 100, price: 8.52, delta: 0.654 },
  { ticker: 'MSFT', type: 'put', strike: 250, quantity: 50, price: 12.34, delta: -0.432 },
  { ticker: 'TSLA', type: 'call', strike: 200, quantity: 25, price: 5.67, delta: 0.512 },
])

const portfolioGreeks = reactive({
  delta: 0,
  gamma: 0,
  vega: 0,
  theta: 0,
  rho: 0,
})

const portfolioValue = ref(0)
const plMatrix = ref<number[][]>([])
const maxGain = ref(0)
const maxLoss = ref(0)
const breakeven = ref(0)

const calculatePortfolio = () => {
  portfolioGreeks.delta = positions.value.reduce((sum, pos) => sum + pos.delta * pos.quantity, 0)
  portfolioGreeks.gamma = positions.value.reduce((sum, pos) => sum + 0.0184 * pos.quantity, 0)
  portfolioGreeks.vega = positions.value.reduce((sum, pos) => sum + 0.197 * pos.quantity, 0)
  portfolioGreeks.theta = positions.value.reduce((sum, pos) => sum + (-0.024) * pos.quantity, 0)
  portfolioGreeks.rho = positions.value.reduce((sum, pos) => sum + 0.089 * pos.quantity, 0)

  portfolioValue.value = positions.value.reduce((sum, pos) => sum + pos.price * pos.quantity, 0)

  // P&L Matrix
  const spotShifts = [-5, -2.5, 0, 2.5, 5]
  const volShifts = [-2, -1, 0, 1, 2]

  plMatrix.value = spotShifts.map(dS => {
    return volShifts.map(dVol => {
      let pl = portfolioGreeks.delta * dS
      pl += 0.5 * portfolioGreeks.gamma * dS * dS
      pl += portfolioGreeks.vega * dVol
      return pl
    })
  })

  maxGain.value = portfolioValue.value * 5
  maxLoss.value = -portfolioValue.value
  breakeven.value = portfolioValue.value / Math.abs(portfolioGreeks.delta || 1)
}

const addPosition = () => {
  positions.value.push({
    ticker: 'NEW',
    type: 'call',
    strike: 100,
    quantity: 10,
    price: 5.0,
    delta: 0.5,
  })
  calculatePortfolio()
}

const removePosition = (index: number) => {
  positions.value.splice(index, 1)
  calculatePortfolio()
}

const getScenarioPL = (spotChange: number, volChange: number = 0): number => {
  return (
    portfolioGreeks.delta * spotChange +
    0.5 * portfolioGreeks.gamma * spotChange * spotChange +
    portfolioGreeks.vega * volChange
  )
}

calculatePortfolio()
</script>

<style scoped>
/* Main Layout */
.page-container {
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  overflow-y: auto;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
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

/* Portfolio Summary */
.portfolio-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.summary-label {
  color: rgba(255, 255, 255, 0.6);
}

.summary-value {
  font-weight: 700;
  color: #3b82f6;
  font-family: "SF Mono", monospace;
}

/* Positions List */
.positions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.position-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 10px;
  position: relative;
}

.pos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.pos-ticker {
  font-weight: 700;
  color: #fff;
  font-size: 12px;
}

.pos-type {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.pos-type.call {
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
}

.pos-type.put {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.pos-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
}

.pos-row {
  display: flex;
  justify-content: space-between;
  gap: 6px;
  color: rgba(255, 255, 255, 0.7);
}

.pos-input {
  width: 50px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 4px;
  border-radius: 4px;
  font-size: 11px;
  text-align: center;
}

.pos-sum {
  font-weight: 600;
  color: #3b82f6;
}

.btn-delete-small {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 20px;
  height: 20px;
  padding: 0;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #f87171;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  transition: 0.2s;
}

.btn-delete-small:hover {
  background: rgba(239, 68, 68, 0.2);
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  padding: 12px;
  border-radius: 12px;
  color: #fff;
  font-weight: 700;
  font-size: 13px;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
  transition: all 0.2s;
  width: 100%;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(37, 99, 235, 0.5);
}

.mt-4 {
  margin-top: 16px;
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

/* Greeks Grid */
.greeks-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.greek-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 14px;
  text-align: center;
}

.greek-icon {
  font-size: 18px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 4px;
}

.greek-title {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.greek-value {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
  margin-bottom: 4px;
}

.greek-info {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

/* Scenarios */
.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.scenario-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

.scenario-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.scenario-value {
  font-size: 14px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
}

/* Table */
.table-wrapper {
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
  font-family: "SF Mono", monospace;
  font-weight: 600;
}

.row-header {
  font-weight: 700;
  background: rgba(59, 130, 246, 0.05);
}

.positive {
  color: #4ade80;
}

.negative {
  color: #f87171;
}

/* Metrics */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric-item {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.metric-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
  margin-bottom: 4px;
}

.metric-info {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
}

/* Utilities */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}

.bg-blue {
  background: #3b82f6;
  color: #3b82f6;
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

.mt-4 {
  margin-top: 16px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .greeks-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .scenarios-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px 20px;
  }

  .greeks-grid {
    grid-template-columns: 1fr;
  }

  .scenarios-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>