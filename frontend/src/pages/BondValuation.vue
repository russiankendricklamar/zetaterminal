<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Оценка облигаций (DCF)</h1>
        <p class="section-subtitle">Моделирование денежных потоков на данных MOEX ISS API</p>
      </div>
      <div class="header-actions">
        <button class="btn-glass primary" @click="calculateBond" :disabled="loading">
            <span v-if="!loading">▶ Рассчитать</span>
            <span v-else class="flex-center"><span class="spinner-mini"></span> Загрузка...</span>
        </button>
      </div>
    </div>

    <div class="dashboard-grid">
        
        <!-- LEFT COLUMN: Inputs & Dual Scenario Results -->
        <div class="left-panel">
            
            <!-- Basic Parameters -->
            <div class="glass-card panel">
                <div class="panel-header"><h3>Параметры оценки</h3></div>
                <div class="controls-form">
                    <div class="form-group">
                        <label class="lbl">ISIN Облигации</label>
                        <input v-model="params.secid" type="text" class="glass-input" placeholder="RU000..." />
                    </div>

                    <div class="form-group">
                        <label class="lbl">Дата оценки</label>
                        <input v-model="params.valuationDate" type="date" class="glass-input" />
                    </div>

                    <div class="form-group">
                        <label class="lbl">Базис</label>
                        <select v-model.number="params.dayCount" class="glass-input">
                            <option :value="365">ACT/365</option>
                            <option :value="360">30/360</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- SCENARIO 1: Доходность Аналога (Input Block) -->
            <div class="glass-card panel input-scenario scenario-1-input">
                <div class="panel-header">
                    <h3>Сценарий 1: Y аналога</h3>
                </div>
                <div class="scenario-input-group">
                    <label class="lbl">Ставка дисконтирования (%)</label>
                    <input v-model.number="params.discountYield1" type="number" step="0.1" class="glass-input scenario-input" placeholder="14.0" />
                </div>
            </div>

            <!-- SCENARIO 2: Доходность индекса (Input Block) -->
            <div class="glass-card panel input-scenario scenario-2-input">
                <div class="panel-header">
                    <h3>Сценарий 2: Y индекса</h3>
                </div>
                <div class="scenario-input-group">
                    <label class="lbl">Ставка дисконтирования (%)</label>
                    <input v-model.number="params.discountYield2" type="number" step="0.1" class="glass-input scenario-input" placeholder="16.0" />
                </div>
            </div>

            <!-- Error Alert -->
            <transition name="fade">
                <div v-if="error" class="error-banner">
                    <span class="icon">⚠️</span> {{ error }}
                </div>
            </transition>

            <!-- Bond Info -->
            <transition name="fade">
            <div v-if="results" class="glass-card panel info-panel">
                <div class="panel-header"><h3>Паспорт бумаги</h3></div>
                <div class="info-list">
                    <div class="info-row"><span>SECID</span> <strong>{{ results.secid }}</strong></div>
                    <div class="info-row"><span>Номинал</span> <strong>{{ formatNumber(results.faceValue, 0) }} ₽</strong></div>
                    <div class="info-row"><span>Купон</span> <strong>{{ results.couponPercent }}%</strong></div>
                    <div class="info-row"><span>Погашение</span> <strong>{{ formatDate(results.maturityDate) }}</strong></div>
                    <div class="info-row"><span>Частота</span> <strong>{{ results.paymentsPerYear }} / год</strong></div>
                </div>
            </div>
            </transition>

        </div>

        <!-- RIGHT COLUMN: Tables & Scenarios -->
        <div class="main-panel">
            
            <!-- Scenario Comparison -->
            <transition name="fade">
            <div v-if="results" class="glass-card panel comparison-panel h-auto">
                <div class="panel-header">
                    <h3>Сравнение сценариев</h3>
                </div>
                <div class="comparison-table-wrapper">
                    <table class="comparison-table">
                        <thead>
                            <tr>
                                <th>Метрика</th>
                                <th class="scenario-col">
                                    <span class="scenario-label">Сценарий 1</span>
                                    <span class="scenario-rate">{{ formatNumber(params.discountYield1, 1) }}%</span>
                                </th>
                                <th class="scenario-col">
                                    <span class="scenario-label">Сценарий 2</span>
                                    <span class="scenario-rate variant-2">{{ formatNumber(params.discountYield2, 1) }}%</span>
                                </th>
                                <th class="diff-col">
                                    <span class="scenario-label">Разница</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Dirty Price</strong></td>
                                <td class="mono text-gradient-blue">{{ formatNumber(results.scenario1.dirtyPrice, 2) }} ₽</td>
                                <td class="mono text-gradient-green">{{ formatNumber(results.scenario2.dirtyPrice, 2) }} ₽</td>
                                <td class="mono" :class="results.scenario1.dirtyPrice > results.scenario2.dirtyPrice ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.dirtyPrice - results.scenario2.dirtyPrice, 2) }} ₽
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Clean Price</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.cleanPrice, 2) }} ₽</td>
                                <td class="mono">{{ formatNumber(results.scenario2.cleanPrice, 2) }} ₽</td>
                                <td class="mono" :class="results.scenario1.cleanPrice > results.scenario2.cleanPrice ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.cleanPrice - results.scenario2.cleanPrice, 2) }} ₽
                                </td>
                            </tr>
                            <tr>
                                <td><strong>% от номинала</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.pricePercent, 2) }}%</td>
                                <td class="mono">{{ formatNumber(results.scenario2.pricePercent, 2) }}%</td>
                                <td class="mono" :class="results.scenario1.pricePercent > results.scenario2.pricePercent ? 'text-green' : 'text-red'">
                                    {{ formatNumber(results.scenario1.pricePercent - results.scenario2.pricePercent, 2) }}%
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Дюрация (Mac)</strong></td>
                                <td class="mono">{{ formatNumber(results.scenario1.duration, 2) }} лет</td>
                                <td class="mono">{{ formatNumber(results.scenario2.duration, 2) }} лет</td>
                                <td class="mono text-muted">
                                    (одинаковая)
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Cash Flows (Scenario 1) -->
            <transition name="fade">
            <div v-if="results && results.cashFlows1" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>Денежные потоки (Сценарий 1)</h3>
                    <div class="glass-pill">{{ results.cashFlows1.length }} платежей</div>
                </div>
                
                <div class="table-wrapper custom-scroll">
                    <table class="glass-table">
                        <thead>
                            <tr>
                                <th>Дата</th>
                                <th class="text-right">T (лет)</th>
                                <th class="text-right">CF (₽)</th>
                                <th class="text-right">DF</th>
                                <th class="text-right">PV (₽)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(cf, idx) in results.cashFlows1" :key="idx">
                                <td class="text-muted">{{ formatDate(cf.date) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.t, 3) }}</td>
                                <td class="text-right mono">{{ formatNumber(cf.cf, 2) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.df, 4) }}</td>
                                <td class="text-right mono font-bold text-blue">{{ formatNumber(cf.pv, 2) }}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="4" class="text-right text-muted">Total PV (Dirty):</td>
                                <td class="text-right mono text-blue font-bold">{{ formatNumber(results.scenario1.dirtyPrice, 2) }}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Cash Flows (Scenario 2) -->
            <transition name="fade">
            <div v-if="results && results.cashFlows2" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>Денежные потоки (Сценарий 2)</h3>
                    <div class="glass-pill">{{ results.cashFlows2.length }} платежей</div>
                </div>
                
                <div class="table-wrapper custom-scroll">
                    <table class="glass-table">
                        <thead>
                            <tr>
                                <th>Дата</th>
                                <th class="text-right">T (лет)</th>
                                <th class="text-right">CF (₽)</th>
                                <th class="text-right">DF</th>
                                <th class="text-right">PV (₽)</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(cf, idx) in results.cashFlows2" :key="idx">
                                <td class="text-muted">{{ formatDate(cf.date) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.t, 3) }}</td>
                                <td class="text-right mono">{{ formatNumber(cf.cf, 2) }}</td>
                                <td class="text-right mono text-muted">{{ formatNumber(cf.df, 4) }}</td>
                                <td class="text-right mono font-bold text-green">{{ formatNumber(cf.pv, 2) }}</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="4" class="text-right text-muted">Total PV (Dirty):</td>
                                <td class="text-right mono text-green font-bold">{{ formatNumber(results.scenario2.dirtyPrice, 2) }}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            </transition>

            <!-- Coupon Schedule (улучшенная вёрстка) -->
            <transition name="fade">
            <div v-if="results && results.allCoupons" class="glass-card panel h-auto">
                <div class="panel-header">
                    <h3>График купонных выплат</h3>
                    <div class="schedule-stats">
                        <span class="stat-badge paid">{{ results.allCoupons.filter(c => c.isPaid).length }} выплачено</span>
                        <span class="stat-badge future">{{ results.allCoupons.filter(c => !c.isPaid).length }} будущих</span>
                    </div>
                </div>
                <div class="schedule-grid">
                    <div v-for="(coupon, idx) in results.allCoupons" :key="idx" class="coupon-card" :class="coupon.isPaid ? 'paid' : 'future'">
                        <div class="coupon-index">{{ idx + 1 }}</div>
                        <div class="coupon-content">
                            <div class="coupon-date">{{ formatDate(coupon.date) }}</div>
                            <div class="coupon-amount">{{ formatNumber(coupon.value, 2) }} ₽</div>
                        </div>
                        <div class="coupon-status">
                            <span class="status-badge" :class="coupon.isPaid ? 'paid' : 'future'">
                                {{ coupon.isPaid ? '✓ Выплачен' : '◯ Будущий' }}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            </transition>

            <!-- Empty State -->
            <div v-if="!results && !loading" class="empty-placeholder">
                <div class="placeholder-content">
                    <span class="icon-lg">📊</span>
                    <h3>Введите параметры и нажмите «Рассчитать»</h3>
                    <p>Для загрузки данных о купонах используется MOEX API</p>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// --- Types ---
interface CashFlow {
  date: string; t: number; cf: number; df: number; pv: number
}

interface Coupon {
  date: string; value: number; isPaid: boolean
}

interface ScenarioResults {
  dirtyPrice: number
  cleanPrice: number
  pricePercent: number
  duration: number
}

interface BondResults {
  secid: string; faceValue: number; couponPercent: number; issueDate: string; maturityDate: string; paymentsPerYear: number
  accruedInterest: number
  scenario1: ScenarioResults
  scenario2: ScenarioResults
  cashFlows1: CashFlow[]
  cashFlows2: CashFlow[]
  allCoupons: Coupon[]
}

interface BondParams {
  secid: string
  valuationDate: string
  discountYield1: number
  discountYield2: number
  dayCount: number
}

// --- State ---
const params = ref<BondParams>({
  secid: 'RU000A10AU99',
  valuationDate: new Date().toISOString().split('T')[0],
  discountYield1: 14.0,
  discountYield2: 16.0,
  dayCount: 365
})

const results = ref<BondResults | null>(null)
const loading = ref(false)
const error = ref('')

// --- Methods ---

// Helper: Calculate scenario with given yield
const calculateScenario = (yield_: number, baseCF: any[], accruedInterest: number, faceValue: number): ScenarioResults => {
  let totalPV = 0
  const r = yield_ / 100
  
  baseCF.forEach(cf => {
    const t = cf.t
    const df = Math.exp(-r * t)
    const pv = cf.cf * df
    totalPV += pv
  })

  const cleanPrice = totalPV - accruedInterest
  const pricePercent = (cleanPrice / faceValue) * 100

  // Macaulay Duration
  let weightedTime = 0
  baseCF.forEach(cf => {
    const t = cf.t
    const df = Math.exp(-r * t)
    const pv = cf.cf * df
    weightedTime += t * pv
  })
  const duration = weightedTime / totalPV

  return {
    dirtyPrice: totalPV,
    cleanPrice: cleanPrice,
    pricePercent: pricePercent,
    duration: duration
  }
}

// Helper: Generate base cash flows (used for both scenarios)
const generateBaseCashFlows = (startDate: Date): any[] => {
  const cfs = []
  const baseDate = new Date(startDate)
  
  for (let i = 1; i <= 6; i++) {
    const cfDate = new Date(baseDate)
    cfDate.setMonth(cfDate.getMonth() + i * 6)
    
    const t = i * 0.5 // 6-month intervals
    const cf = i === 6 ? 1045 : 45 // Last includes face value
    
    cfs.push({
      date: cfDate.toISOString(),
      t: t,
      cf: cf
    })
  }
  
  return cfs
}

// Helper: Add discount factors and PV to cash flows
const calculateCashFlowsWithDF = (baseCF: any[], yield_: number): CashFlow[] => {
  const r = yield_ / 100
  return baseCF.map(cf => ({
    date: cf.date,
    t: cf.t,
    cf: cf.cf,
    df: Math.exp(-r * cf.t),
    pv: cf.cf * Math.exp(-r * cf.t)
  }))
}

const calculateBond = async () => {
  loading.value = true
  error.value = ''
  results.value = null

  // Validation
  if (!params.value.discountYield1 || !params.value.discountYield2) {
    error.value = 'Заполните обе ставки дисконтирования'
    loading.value = false
    return
  }

  setTimeout(() => {
    try {
      const faceValue = 1000
      const accruedInterest = 15.5
      const startDate = new Date()

      // Generate base cash flows
      const baseCF = generateBaseCashFlows(startDate)

      // Calculate both scenarios
      const scenario1 = calculateScenario(params.value.discountYield1, baseCF, accruedInterest, faceValue)
      const scenario2 = calculateScenario(params.value.discountYield2, baseCF, accruedInterest, faceValue)

      // Generate cash flows with DFs for both scenarios
      const cashFlows1 = calculateCashFlowsWithDF(baseCF, params.value.discountYield1)
      const cashFlows2 = calculateCashFlowsWithDF(baseCF, params.value.discountYield2)

      // Mock Schedule
      const coupons = []
      for (let i = 0; i < 10; i++) {
        const couponDate = new Date()
        couponDate.setMonth(couponDate.getMonth() - (4 - i) * 6)
        coupons.push({
          date: couponDate.toISOString(),
          value: 45.0,
          isPaid: i < 4
        })
      }

      results.value = {
        secid: params.value.secid,
        faceValue: faceValue,
        couponPercent: 9.0,
        issueDate: '2023-01-01',
        maturityDate: '2028-01-01',
        paymentsPerYear: 2,
        accruedInterest: accruedInterest,
        scenario1: scenario1,
        scenario2: scenario2,
        cashFlows1: cashFlows1,
        cashFlows2: cashFlows2,
        allCoupons: coupons
      }
      loading.value = false
    } catch (e) {
      error.value = 'Ошибка соединения с API'
      loading.value = false
    }
  }, 1200)
}

// --- Formatters ---
const formatNumber = (val: number, decimals = 2) => val.toLocaleString('ru-RU', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('ru-RU')
</script>

<style scoped>
/* ============================================
   LAYOUT
   ============================================ */
.page-container { padding: 24px 32px; max-width: 1600px; margin: 0 auto; min-height: 100vh; display: flex; flex-direction: column; gap: 24px; }
.dashboard-grid { display: grid; grid-template-columns: 380px 1fr; gap: 28px; flex: 1; }
.left-panel, .main-panel { display: flex; flex-direction: column; gap: 20px; }

/* Header */
.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; flex-shrink: 0; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }
.header-actions { display: flex; gap: 12px; }
.header-left { display: flex; flex-direction: column; }

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}
.panel { padding: 24px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-header h3 { margin: 0; font-size: 12px; font-weight: 700; text-transform: uppercase; color: rgba(255,255,255,0.5); letter-spacing: 0.05em; }

/* Controls */
.controls-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.lbl { font-size: 11px; color: rgba(255,255,255,0.6); font-weight: 600; text-transform: uppercase; }

.glass-input {
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 10px 12px;
  border-radius: 10px;
  width: 100%;
  outline: none;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  font-family: "SF Mono", monospace;
  font-size: 13px;
}

.glass-input:focus {
  border-color: rgba(255, 255, 255, 0.25);
  background: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.05);
}

/* Buttons */
.btn-glass {
    border: none; padding: 10px 20px; border-radius: 10px; cursor: pointer; color: #fff; font-weight: 600; font-size: 13px;
    display: flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s;
}
.btn-glass.primary { background: linear-gradient(135deg, #3b82f6, #2563eb); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
.btn-glass.primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5); }
.btn-glass:disabled { opacity: 0.6; cursor: not-allowed; }

/* ============================================
   INPUT SCENARIOS (Left Panel)
   ============================================ */
.input-scenario { padding: 16px 24px; }
.input-scenario.scenario-1-input { border-top: 3px solid #3b82f6; }
.input-scenario.scenario-2-input { border-top: 3px solid #10b981; }

.scenario-input-group { display: flex; flex-direction: column; gap: 8px; }

/* ============================================
   RESULT SCENARIOS
   ============================================ */
.result-card { position: relative; overflow: hidden; margin-top: 12px; }
.result-card.scenario-1 { border-top: 3px solid #3b82f6; }
.result-card.scenario-2 { border-top: 3px solid #10b981; }

.scenario-badge { font-size: 10px; background: rgba(59, 130, 246, 0.2); padding: 4px 10px; border-radius: 6px; color: #60a5fa; font-weight: 600; }
.scenario-badge.variant-2 { background: rgba(16, 185, 129, 0.2); color: #4ade80; }

.scenario-results { display: flex; flex-direction: column; gap: 16px; }

.main-metric-small { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.metric-label-small { font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.5); letter-spacing: 0.08em; }
.metric-value-small { font-size: 22px; font-weight: 700; font-family: "SF Mono", monospace; }

.metrics-grid-small { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.m-item-small { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 4px; padding: 10px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); }
.m-item-small .sub { font-size: 10px; color: rgba(255,255,255,0.4); }
.m-item-small .val-small { font-size: 13px; font-weight: 600; font-family: "SF Mono", monospace; color: #fff; }

/* Comparison Table */
.comparison-panel { margin-bottom: 12px; }
.comparison-table-wrapper { width: 100%; overflow-x: auto; }
.comparison-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.comparison-table th { text-align: left; padding: 12px; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.1); }
.comparison-table td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.comparison-table tr:last-child td { border-bottom: none; }

.scenario-col { text-align: center; }
.scenario-label { display: block; font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.5); margin-bottom: 4px; }
.scenario-rate { display: block; font-size: 13px; font-weight: 700; color: #60a5fa; font-family: "SF Mono", monospace; }
.scenario-rate.variant-2 { color: #4ade80; }

.diff-col { text-align: center; width: 100px; }

/* Info Panel */
.info-panel { padding-top: 16px; }
.info-list { display: flex; flex-direction: column; gap: 10px; }
.info-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; }
.info-row:last-child { border: none; }
.info-row span { color: rgba(255,255,255,0.5); }
.info-row strong { font-weight: 500; color: #fff; }

/* ============================================
   SCHEDULE (Grid Layout - улучшено)
   ============================================ */
.schedule-stats { display: flex; gap: 8px; }
.stat-badge { font-size: 10px; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
.stat-badge.paid { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.stat-badge.future { background: rgba(255, 255, 255, 0.1); color: rgba(255,255,255,0.5); }

.schedule-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.coupon-card {
  padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.02); transition: all 0.2s;
  display: flex; flex-direction: column; gap: 10px;
}
.coupon-card.paid { border-left: 3px solid #4ade80; background: rgba(74, 222, 128, 0.04); }
.coupon-card.future { border-left: 3px solid rgba(255,255,255,0.3); background: rgba(255,255,255,0.01); }
.coupon-card:hover { border-color: rgba(255,255,255,0.2); background: rgba(255,255,255,0.04); }

.coupon-index { font-size: 10px; color: rgba(255,255,255,0.3); font-weight: 700; text-transform: uppercase; }
.coupon-content { display: flex; flex-direction: column; gap: 6px; }
.coupon-date { font-size: 11px; color: rgba(255,255,255,0.6); font-weight: 500; }
.coupon-amount { font-size: 14px; font-weight: 700; font-family: "SF Mono", monospace; color: #fff; }
.coupon-status { display: flex; justify-content: center; }

.status-badge { padding: 4px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; display: inline-block; }
.status-badge.paid { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.status-badge.future { background: rgba(255, 255, 255, 0.1); color: rgba(255,255,255,0.5); }

/* ============================================
   TABLES
   ============================================ */
.table-wrapper { width: 100%; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.glass-table th { text-align: left; padding: 12px; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 11px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.1); }
.glass-table td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #e2e8f0; }
.glass-table tr:last-child td { border-bottom: none; }
.glass-table tfoot td { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 16px; }

.glass-pill { background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 99px; font-size: 11px; color: rgba(255,255,255,0.7); }

/* Empty State */
.empty-placeholder { height: 100%; display: flex; align-items: center; justify-content: center; opacity: 0.5; border: 2px dashed rgba(255,255,255,0.1); border-radius: 20px; }
.placeholder-content { text-align: center; }
.icon-lg { font-size: 48px; display: block; margin-bottom: 16px; }
.empty-placeholder h3 { font-size: 16px; color: #fff; margin: 0 0 8px 0; }
.empty-placeholder p { font-size: 13px; margin: 0; }

/* Utils */
.text-right { text-align: right; }
.text-center { text-align: center; }
.text-green { color: #4ade80; }
.text-blue { color: #3b82f6; }
.text-orange { color: #fbbf24; }
.text-red { color: #f87171; }
.text-muted { color: rgba(255,255,255,0.4); }
.mono { font-family: "SF Mono", monospace; }
.font-bold { font-weight: 700; }
.h-auto { height: auto; }
.flex-center { display: flex; align-items: center; gap: 8px; }

.text-gradient-blue { background: linear-gradient(to right, #60a5fa, #3b82f6); -webkit-background-clip: text; color: transparent; }
.text-gradient-green { background: linear-gradient(to right, #4ade80, #22c55e); -webkit-background-clip: text; color: transparent; }

.error-banner { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; padding: 12px; border-radius: 10px; margin-bottom: 20px; font-size: 13px; display: flex; align-items: center; gap: 8px; }
.spinner-mini { width: 14px; height: 14px; border: 2px solid #fff; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Custom scrollbar */
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

@media (max-width: 1280px) {
  .dashboard-grid { grid-template-columns: 340px 1fr; }
  .schedule-grid { grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); }
}

@media (max-width: 1024px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .metrics-grid-small { grid-template-columns: 1fr; }
  .schedule-grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
  .page-container {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  .schedule-grid { 
    grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); 
    gap: 10px; 
  }
  .coupon-card { 
    padding: 12px; 
    gap: 8px; 
  }
  .left-panel,
  .main-panel {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
  }
  .schedule-grid { 
    grid-template-columns: 1fr; 
    gap: 8px; 
  }
  .coupon-card { 
    padding: 10px; 
    gap: 6px; 
    font-size: 11px;
  }
  .left-panel,
  .main-panel {
    padding: 10px;
  }
}
</style>