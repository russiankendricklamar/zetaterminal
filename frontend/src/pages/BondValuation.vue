<template>
  <div class="bond-valuation-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Оценка облигаций</h1>
        <p class="subtitle">DCF-модель с данными MOEX ISS API</p>
      </div>
      <button class="btn btn-primary" @click="calculateBond" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Рассчитать' }}
      </button>
    </div>

    <!-- Input Parameters Card -->
    <div class="card">
      <div class="card-header">
        <h3>Параметры оценки</h3>
      </div>
      <div class="card-body">
        <div class="params-grid">
          <div class="form-group">
            <label>ISIN оцениваемой облигации</label>
            <input
              v-model="params.secid"
              type="text"
              class="form-control"
              placeholder="RU000A10AU99"
            />
          </div>

          <div class="form-group">
            <label>Дата оценки</label>
            <input
              v-model="params.valuationDate"
              type="date"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label>Доходность (аналога/индекса) %</label>
            <input
              v-model.number="params.discountYield"
              type="number"
              step="0.01"
              class="form-control"
              placeholder="14.0"
            />
          </div>

          <div class="form-group">
            <label>База расчета</label>
            <select v-model.number="params.dayCount" class="form-control">
              <option :value="365">365 (Actual/365)</option>
              <option :value="360">360 (30/360)</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger">
      <span>⚠️</span>
      <span>{{ error }}</span>
    </div>

    <!-- Results Grid -->
    <div v-if="results" class="results-grid">
      <!-- Bond Info Card -->
      <div class="card">
        <div class="card-header">
          <h3>Параметры облигации</h3>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">SECID:</span>
            <span class="value">{{ results.secid }}</span>
          </div>
          <div class="info-row">
            <span class="label">Номинал:</span>
            <span class="value">{{ formatNumber(results.faceValue) }} ₽</span>
          </div>
          <div class="info-row">
            <span class="label">Купон:</span>
            <span class="value">{{ results.couponPercent }}% годовых</span>
          </div>
          <div class="info-row">
            <span class="label">Дата выпуска:</span>
            <span class="value">{{ formatDate(results.issueDate) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Дата погашения:</span>
            <span class="value">{{ formatDate(results.maturityDate) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Периодичность:</span>
            <span class="value">{{ results.paymentsPerYear }} в год</span>
          </div>
        </div>
      </div>

      <!-- Valuation Results Card -->
      <div class="card">
        <div class="card-header">
          <h3>Результаты оценки</h3>
        </div>
        <div class="card-body">
          <div class="metric-large">
            <div class="metric-label">Dirty Price (с НКД)</div>
            <div class="metric-value text-gradient-blue">
              {{ formatNumber(results.dirtyPrice, 4) }} ₽
            </div>
          </div>

          <div class="metrics-row">
            <div class="metric">
              <div class="metric-label">НКД</div>
              <div class="metric-value">{{ formatNumber(results.accruedInterest, 4) }}</div>
            </div>
            <div class="metric">
              <div class="metric-label">Clean Price</div>
              <div class="metric-value text-gradient-green">{{ formatNumber(results.cleanPrice, 4) }}</div>
            </div>
          </div>

          <div class="info-row">
            <span class="label">Цена в % от номинала:</span>
            <span class="value">{{ formatNumber(results.pricePercent, 3) }}%</span>
          </div>
          <div class="info-row">
            <span class="label">Дюрация:</span>
            <span class="value">{{ formatNumber(results.duration, 4) }} лет</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cash Flows Table -->
    <div v-if="results && results.cashFlows" class="card table-card">
      <div class="card-header">
        <h3>Денежные потоки (дисконтированные)</h3>
        <span class="badge">{{ results.cashFlows.length }} платежей</span>
      </div>
      <div class="card-body">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Дата</th>
                <th>t (лет)</th>
                <th>CF (₽)</th>
                <th>DF</th>
                <th>PV (₽)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(cf, idx) in results.cashFlows" :key="idx">
                <td>{{ idx + 1 }}</td>
                <td>{{ formatDate(cf.date) }}</td>
                <td class="mono">{{ formatNumber(cf.t, 4) }}</td>
                <td class="mono">{{ formatNumber(cf.cf, 2) }}</td>
                <td class="mono">{{ formatNumber(cf.df, 6) }}</td>
                <td class="mono" :class="cf.pv > 0 ? 'positive' : ''">
                  {{ formatNumber(cf.pv, 4) }}
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="5" class="text-right"><strong>Итого (Dirty Price):</strong></td>
                <td class="mono positive"><strong>{{ formatNumber(results.dirtyPrice, 4) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>

    <!-- All Coupons Schedule -->
    <div v-if="results && results.allCoupons" class="card table-card">
      <div class="card-header">
        <h3>Полное расписание купонов</h3>
        <span class="badge">{{ results.allCoupons.length }} купонов</span>
      </div>
      <div class="card-body">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Дата купона</th>
                <th>Сумма (₽)</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(coupon, idx) in results.allCoupons" :key="idx">
                <td>{{ idx + 1 }}</td>
                <td>{{ formatDate(coupon.date) }}</td>
                <td class="mono">{{ formatNumber(coupon.value, 2) }}</td>
                <td>
                  <span 
                    class="status-badge" 
                    :class="coupon.isPaid ? 'paid' : 'future'"
                  >
                    {{ coupon.isPaid ? '✓ Выплачен' : '◷ Будущий' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Types
interface BondParams {
  secid: string
  valuationDate: string
  discountYield: number
  dayCount: number
}

interface CashFlow {
  date: string
  t: number
  cf: number
  df: number
  pv: number
}

interface Coupon {
  date: string
  value: number
  isPaid: boolean
}

interface BondResults {
  secid: string
  faceValue: number
  couponPercent: number
  issueDate: string
  maturityDate: string
  paymentsPerYear: number
  dirtyPrice: number
  accruedInterest: number
  cleanPrice: number
  pricePercent: number
  duration: number
  cashFlows: CashFlow[]
  allCoupons: Coupon[]
}

// State
const params = ref<BondParams>({
  secid: 'RU000A10AU99',
  valuationDate: '2026-01-01',
  discountYield: 14.0,
  dayCount: 365
})

const results = ref<BondResults | null>(null)
const loading = ref(false)
const error = ref('')

// Methods
const calculateBond = async () => {
  loading.value = true
  error.value = ''
  results.value = null

  try {
    // Вызов бэкенда (Flask/FastAPI)
    const response = await fetch('http://localhost:8000/api/bond/valuation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        secid: params.value.secid,
        valuation_date: params.value.valuationDate,
        discount_yield: params.value.discountYield / 100,
        day_count: params.value.dayCount
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()
    results.value = data
  } catch (err: any) {
    error.value = err.message || 'Ошибка при расчёте облигации'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Formatters
const formatNumber = (val: number, decimals = 2): string => {
  return val.toLocaleString('ru-RU', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('ru-RU')
}

// Auto-load on mount (optional)
onMounted(() => {
  // calculateBond()
})
</script>

<style scoped>
.bond-valuation-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px; /* 🎯 Главный gap между всеми элементами */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  /* убрал margin-bottom, теперь gap в родителе */
}

.page-header h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.8px;
}

.page-header .subtitle {
  margin-top: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

/* Parameters Grid */
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Alert */
.alert {
  padding: 14px 18px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 13px;
  /* убрал margin-bottom */
}

/* Results Grid */
.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  /* убрал margin-bottom */
}

/* Info Rows */
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--glass-border-soft);
  font-size: 13px;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: var(--text-secondary);
  font-weight: 500;
}

.info-row .value {
  color: var(--text-primary);
  font-family: var(--font-family-mono);
}

/* Metrics */
.metric-large {
  text-align: center;
  padding: 20px 0;
  border-bottom: 1px solid var(--glass-border-soft);
  margin-bottom: 16px;
}

.metric-large .metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 8px;
}

.metric-large .metric-value {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--font-family-mono);
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric {
  text-align: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-sm);
  border: 1px solid var(--glass-border-soft);
}

.metric .metric-label {
  font-size: 11px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.metric .metric-value {
  font-size: 20px;
  font-weight: 600;
  font-family: var(--font-family-mono);
}

/* Badge */
.badge {
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}

/* Table Cards - добавил дополнительный класс для визуального разделения */
.table-card {
  /* можно добавить дополнительные стили если нужно */
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  border-radius: var(--radius-sm);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table thead th {
  text-align: left;
  padding: 10px 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--glass-border-soft);
}

.data-table tbody td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
}

.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.data-table tfoot td {
  padding: 12px;
  font-weight: 600;
  border-top: 2px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.02);
}

.data-table .mono {
  font-family: var(--font-family-mono);
}

.data-table .positive {
  color: var(--color-accent-success);
}

.data-table .text-right {
  text-align: right;
}

/* Status Badge */
.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: var(--radius-pill);
  font-size: 11px;
  font-weight: 600;
}

.status-badge.paid {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
}

.status-badge.future {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

/* Responsive */
@media (max-width: 768px) {
  .bond-valuation-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-header .btn {
    width: 100%;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }

  .params-grid {
    grid-template-columns: 1fr;
  }
}
</style>
