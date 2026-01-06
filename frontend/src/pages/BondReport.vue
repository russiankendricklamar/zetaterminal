<template>
  <div class="page-container">
    
    <!-- Hero / Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Отчет по оценке облигаций</h1>
        <p class="section-subtitle">Формирование аналитического отчёта (DCF)</p>
      </div>
      <div class="header-actions">
        <button class="btn-glass primary" @click="generateReport" :disabled="loading || !results">
          <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-if="!loading">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m4-3H8m7-7H5a2 2 0 00-2 2v12a2 2 0 002 2h14a2 2 0 002-2V7a2 2 0 00-2-2z"></path>
          </svg>
          <span v-else class="spinner-mini"></span>
          <span>{{ loading ? 'Генерация...' : '📄 Скачать PDF' }}</span>
        </button>
      </div>
    </div>

    <!-- Step 1: Data Input -->
    <div class="glass-card panel step-panel">
      <div class="panel-header">
        <h3>Шаг 1: Загрузка данных из оценки</h3>
        <span class="step-badge">1</span>
      </div>
      <div class="controls-form">
        <div class="params-grid">
          <div class="form-group">
            <label class="lbl">ISIN Облигации</label>
            <input
              v-model="params.secid"
              type="text"
              class="glass-input"
              placeholder="RU000A10AU99"
              @change="onBondChange"
            />
          </div>

          <div class="form-group">
            <label class="lbl">Дата оценки</label>
            <input
              v-model="params.valuationDate"
              type="date"
              class="glass-input"
              @change="onBondChange"
            />
          </div>

          <div class="form-group">
            <label class="lbl">Доходность (%)</label>
            <input
              v-model.number="params.discountYield"
              type="number"
              step="0.01"
              class="glass-input"
              placeholder="14.0"
              @change="onBondChange"
            />
          </div>

          <div class="form-group">
            <label class="lbl">База расчета</label>
            <select v-model.number="params.dayCount" class="glass-input" @change="onBondChange">
              <option :value="365">ACT/365</option>
              <option :value="360">30/360</option>
            </select>
          </div>
        </div>
        
        <button class="btn-glass primary wide" @click="calculateBond" :disabled="loading">
          <span v-if="!loading">▶ Загрузить оценку</span>
          <span v-else class="flex-center"><span class="spinner-mini"></span> Загрузка...</span>
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <transition name="fade">
      <div v-if="error" class="alert-glass alert-danger">
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
        </svg>
        <span>{{ error }}</span>
      </div>
    </transition>

    <!-- Step 2: Report Configuration -->
    <transition name="fade">
    <div v-if="results" class="glass-card panel step-panel">
      <div class="panel-header">
        <h3>Шаг 2: Конфигурация отчёта</h3>
        <span class="step-badge variant-2">2</span>
      </div>

      <div class="report-config">
        <!-- Содержание -->
        <div class="config-section">
          <h4 class="section-label">Содержание отчета</h4>
          <div class="checkbox-grid">
            <label class="checkbox-item">
              <input v-model="report.includeExec" type="checkbox" />
              <span>Резюме (Executive Summary)</span>
            </label>
            <label class="checkbox-item">
              <input v-model="report.includeBondInfo" type="checkbox" />
              <span>Параметры облигации</span>
            </label>
            <label class="checkbox-item">
              <input v-model="report.includeValuation" type="checkbox" />
              <span>Результаты оценки</span>
            </label>
            <label class="checkbox-item">
              <input v-model="report.includeCashFlows" type="checkbox" />
              <span>Таблица денежных потоков</span>
            </label>
            <label class="checkbox-item">
              <input v-model="report.includeCoupons" type="checkbox" />
              <span>График купонов</span>
            </label>
            <label class="checkbox-item">
              <input v-model="report.includeMetadata" type="checkbox" />
              <span>Метаданные модели</span>
            </label>
          </div>
        </div>

        <!-- Параметры -->
        <div class="config-section">
          <h4 class="section-label">Параметры отчета</h4>
          <div class="form-row-2">
            <div class="form-group">
              <label class="lbl">Автор отчета</label>
              <input v-model="report.author" type="text" class="glass-input" placeholder="Имя аналитика" />
            </div>
            <div class="form-group">
              <label class="lbl">Компания</label>
              <input v-model="report.company" type="text" class="glass-input" placeholder="Компания/Фонд" />
            </div>
          </div>

          <div class="form-group">
            <label class="lbl">Дополнительные примечания</label>
            <textarea 
              v-model="report.notes"
              class="glass-input textarea"
              rows="4"
              placeholder="Комментарии, допущения, ограничения модели..."
            />
          </div>
        </div>
      </div>
    </div>
    </transition>

    <!-- Step 3: Report Preview -->
    <transition name="fade">
    <div v-if="results" class="glass-card panel step-panel preview-panel">
      <div class="panel-header">
        <h3>Шаг 3: Предпросмотр отчета</h3>
        <span class="step-badge variant-3">3</span>
      </div>

      <div class="report-preview">
        
        <!-- Executive Summary -->
        <div v-if="report.includeExec" class="report-section">
          <h2 class="report-title">Резюме (Executive Summary)</h2>
          <div class="summary-box">
            <div class="summary-row">
              <span class="label">Облигация (ISIN)</span>
              <span class="value mono">{{ results.secid }}</span>
            </div>
            <div class="summary-row">
              <span class="label">Справедливая стоимость (Dirty Price)</span>
              <span class="value text-gradient-blue">{{ formatNumber(results.dirtyPrice, 4) }} ₽</span>
            </div>
            <div class="summary-row">
              <span class="label">Чистая цена (Clean Price)</span>
              <span class="value">{{ formatNumber(results.cleanPrice, 4) }} ₽</span>
            </div>
            <div class="summary-row">
              <span class="label">% от номинала</span>
              <span class="value">{{ formatNumber(results.pricePercent, 2) }}%</span>
            </div>
            <div class="summary-row">
              <span class="label">Дюрация (Macaulay)</span>
              <span class="value text-orange">{{ formatNumber(results.duration, 4) }} лет</span>
            </div>
          </div>
        </div>

        <!-- Bond Info -->
        <div v-if="report.includeBondInfo" class="report-section">
          <h2 class="report-title">Параметры облигации</h2>
          <div class="report-table-wrapper">
            <table class="report-table">
              <tbody>
                <tr>
                  <td class="label">SECID/ISIN</td>
                  <td class="value mono">{{ results.secid }}</td>
                </tr>
                <tr>
                  <td class="label">Номинал</td>
                  <td class="value mono">{{ formatNumber(results.faceValue) }} ₽</td>
                </tr>
                <tr>
                  <td class="label">Купон</td>
                  <td class="value mono">{{ formatNumber(results.couponPercent, 3) }}% годовых</td>
                </tr>
                <tr>
                  <td class="label">Дата выпуска</td>
                  <td class="value">{{ formatDate(results.issueDate) }}</td>
                </tr>
                <tr>
                  <td class="label">Дата погашения</td>
                  <td class="value">{{ formatDate(results.maturityDate) }}</td>
                </tr>
                <tr>
                  <td class="label">Периодичность выплат</td>
                  <td class="value">{{ results.paymentsPerYear }} раз(а) в год</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Valuation Results -->
        <div v-if="report.includeValuation" class="report-section">
          <h2 class="report-title">Результаты оценки</h2>
          <div class="report-table-wrapper">
            <table class="report-table">
              <tbody>
                <tr>
                  <td class="label">Dirty Price (с НКД)</td>
                  <td class="value mono text-gradient-blue">{{ formatNumber(results.dirtyPrice, 4) }} ₽</td>
                </tr>
                <tr>
                  <td class="label">НКД</td>
                  <td class="value mono">{{ formatNumber(results.accruedInterest, 4) }} ₽</td>
                </tr>
                <tr>
                  <td class="label">Clean Price (без НКД)</td>
                  <td class="value mono">{{ formatNumber(results.cleanPrice, 4) }} ₽</td>
                </tr>
                <tr>
                  <td class="label">Цена в % от номинала</td>
                  <td class="value mono">{{ formatNumber(results.pricePercent, 3) }}%</td>
                </tr>
                <tr>
                  <td class="label">Дюрация Маколея</td>
                  <td class="value mono text-orange">{{ formatNumber(results.duration, 4) }} лет</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Cash Flows -->
        <div v-if="report.includeCashFlows && results.cashFlows" class="report-section">
          <h2 class="report-title">Денежные потоки (DCF)</h2>
          <p class="report-desc">Таблица дисконтированных денежных потоков</p>
          <div class="table-scroll">
            <table class="report-table cf-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Дата</th>
                  <th class="text-right">T (лет)</th>
                  <th class="text-right">CF (₽)</th>
                  <th class="text-right">DF</th>
                  <th class="text-right">PV (₽)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(cf, idx) in results.cashFlows" :key="idx">
                  <td>{{ idx + 1 }}</td>
                  <td>{{ formatDate(cf.date) }}</td>
                  <td class="text-right mono">{{ formatNumber(cf.t, 4) }}</td>
                  <td class="text-right mono">{{ formatNumber(cf.cf, 2) }}</td>
                  <td class="text-right mono">{{ formatNumber(cf.df, 6) }}</td>
                  <td class="text-right mono">{{ formatNumber(cf.pv, 4) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="5" class="text-right"><strong>Итого (Dirty Price)</strong></td>
                  <td class="text-right mono"><strong>{{ formatNumber(results.dirtyPrice, 4) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Coupons Schedule -->
        <div v-if="report.includeCoupons && results.allCoupons" class="report-section">
          <h2 class="report-title">График купонных выплат</h2>
          <p class="report-desc">Полное расписание выплат купонов и номинала</p>
          <div class="table-scroll">
            <table class="report-table coupon-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Дата купона</th>
                  <th class="text-right">Сумма (₽)</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(coupon, idx) in results.allCoupons" :key="idx">
                  <td>{{ idx + 1 }}</td>
                  <td>{{ formatDate(coupon.date) }}</td>
                  <td class="text-right mono">{{ formatNumber(coupon.value, 2) }}</td>
                  <td>
                    <span class="status-badge" :class="coupon.isPaid ? 'paid' : 'future'">
                      {{ coupon.isPaid ? '✓ Выплачен' : '◯ Будущий' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Metadata -->
        <div v-if="report.includeMetadata" class="report-section">
          <h2 class="report-title">Метаданные модели</h2>
          <div class="report-table-wrapper">
            <table class="report-table">
              <tbody>
                <tr>
                  <td class="label">Дата оценки</td>
                  <td class="value">{{ formatDate(params.valuationDate) }}</td>
                </tr>
                <tr>
                  <td class="label">Дисконтная ставка (YTM)</td>
                  <td class="value mono">{{ formatNumber(params.discountYield, 3) }}%</td>
                </tr>
                <tr>
                  <td class="label">База расчета дней</td>
                  <td class="value mono">{{ params.dayCount }} дней</td>
                </tr>
                <tr>
                  <td class="label">Кол-во денежных потоков</td>
                  <td class="value">{{ results.cashFlows.length }}</td>
                </tr>
                <tr v-if="report.notes">
                  <td class="label">Примечания</td>
                  <td class="value">{{ report.notes }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Footer -->
        <div class="report-footer">
          <div v-if="report.author" class="footer-item"><strong>Автор:</strong> {{ report.author }}</div>
          <div v-if="report.company" class="footer-item"><strong>Компания:</strong> {{ report.company }}</div>
          <div class="footer-item"><small>Отчет сформирован: {{ new Date().toLocaleString('ru-RU') }}</small></div>
        </div>
      </div>
    </div>
    </transition>

    <!-- Action Bar -->
    <transition name="fade">
    <div v-if="results" class="action-bar">
      <button class="btn-glass primary" @click="generateReport" :disabled="loading">
        📄 Скачать PDF
      </button>
      <button class="btn-glass secondary" @click="printReport">
        🖨️ Печать
      </button>
      <button class="btn-glass secondary" @click="copyToClipboard">
        📋 Копировать
      </button>
    </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

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

interface ReportConfig {
  includeExec: boolean
  includeBondInfo: boolean
  includeValuation: boolean
  includeCashFlows: boolean
  includeCoupons: boolean
  includeMetadata: boolean
  author: string
  company: string
  notes: string
}

// Mock data
const mockResults: BondResults = {
  secid: 'RU000A10AU99',
  faceValue: 1000,
  couponPercent: 9.0,
  issueDate: '2023-01-01',
  maturityDate: '2028-01-01',
  paymentsPerYear: 2,
  dirtyPrice: 987.65,
  accruedInterest: 15.50,
  cleanPrice: 972.15,
  pricePercent: 97.215,
  duration: 2.45,
  cashFlows: [
    { date: '2026-07-03', t: 0.5, cf: 45, df: 0.9326, pv: 41.97 },
    { date: '2027-01-03', t: 1.0, cf: 45, df: 0.8704, pv: 39.17 },
    { date: '2027-07-03', t: 1.5, cf: 45, df: 0.8118, pv: 36.53 },
    { date: '2028-01-03', t: 2.0, cf: 45, df: 0.7565, pv: 34.04 },
    { date: '2028-07-03', t: 2.5, cf: 45, df: 0.7041, pv: 31.69 },
    { date: '2029-01-03', t: 3.0, cf: 1045, df: 0.6543, pv: 683.55 }
  ],
  allCoupons: [
    { date: '2025-07-03', value: 45, isPaid: true },
    { date: '2026-01-03', value: 45, isPaid: true },
    { date: '2026-07-03', value: 45, isPaid: false },
    { date: '2027-01-03', value: 45, isPaid: false },
    { date: '2027-07-03', value: 45, isPaid: false },
    { date: '2028-01-03', value: 45, isPaid: false },
    { date: '2028-07-03', value: 45, isPaid: false },
    { date: '2029-01-03', value: 1045, isPaid: false }
  ]
}

// State
const params = ref<BondParams>({
  secid: 'RU000A10AU99',
  valuationDate: new Date().toISOString().split('T')[0],
  discountYield: 14.0,
  dayCount: 365
})

const results = ref<BondResults | null>(mockResults)
const loading = ref(false)
const error = ref('')

const report = ref<ReportConfig>({
  includeExec: true,
  includeBondInfo: true,
  includeValuation: true,
  includeCashFlows: true,
  includeCoupons: true,
  includeMetadata: true,
  author: 'Аналитик',
  company: 'Компания',
  notes: ''
})

// Methods
const calculateBond = async () => {
  loading.value = true
  error.value = ''
  results.value = null

  try {
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

    results.value = await response.json()
  } catch (err: any) {
    error.value = err.message || 'Ошибка при расчёте облигации'
    results.value = null
  } finally {
    loading.value = false
  }
}

const onBondChange = () => {
  results.value = null
}

const generateReport = async () => {
  if (!results.value) return
  try {
    loading.value = true
    window.print()
  } catch (err) {
    error.value = 'Ошибка при генерации отчета'
  } finally {
    loading.value = false
  }
}

const printReport = () => {
  window.print()
}

const copyToClipboard = async () => {
  const preview = document.querySelector('.report-preview')
  if (!preview) return

  try {
    const text = preview.innerText
    await navigator.clipboard.writeText(text)
    alert('Отчет скопирован в буфер обмена')
  } catch (err) {
    error.value = 'Ошибка при копировании'
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
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px 32px;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
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

.step-badge { 
  font-size: 12px; 
  width: 28px; 
  height: 28px; 
  background: rgba(59, 130, 246, 0.2); 
  color: #60a5fa; 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-weight: 700;
}
.step-badge.variant-2 { background: rgba(16, 185, 129, 0.2); color: #4ade80; }
.step-badge.variant-3 { background: rgba(249, 115, 22, 0.2); color: #fbbf24; }

/* ============================================
   FORMS
   ============================================ */
.controls-form { display: flex; flex-direction: column; gap: 16px; }

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.lbl {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  text-transform: uppercase;
}

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

.glass-input.textarea {
  resize: vertical;
  font-family: "SF Mono", monospace;
}

/* ============================================
   BUTTONS
   ============================================ */
.btn-glass {
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
}

.btn-glass.primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-glass.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.btn-glass.secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-glass.secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.btn-glass:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-glass.wide {
  width: 100%;
}

/* ============================================
   ALERTS
   ============================================ */
.alert-glass {
  padding: 14px 18px;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.alert-glass svg {
  flex-shrink: 0;
}

/* ============================================
   REPORT CONFIG
   ============================================ */
.report-config {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: rgba(255,255,255,0.7);
  letter-spacing: 0.05em;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
  color: rgba(255,255,255,0.8);
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.checkbox-item:hover {
  background: rgba(255,255,255,0.05);
}

.checkbox-item input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.form-row-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* ============================================
   REPORT PREVIEW
   ============================================ */
.preview-panel {
  max-height: 700px;
  overflow-y: auto;
}

.report-preview {
  font-size: 13px;
  line-height: 1.6;
  color: #1a1a1a;
  background: #ffffff;
  padding: 24px;
  border-radius: 8px;
}

.report-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

.report-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.report-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #60a5fa;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.report-desc {
  font-size: 11px;
  color: rgba(0,0,0,0.6);
  margin-bottom: 12px;
  font-style: italic;
}

.summary-box {
  background: rgba(96, 165, 250, 0.1);
  border-left: 3px solid #60a5fa;
  padding: 16px;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  padding: 8px 0;
}

.summary-row .label {
  color: rgba(0,0,0,0.7);
}

.summary-row .value {
  font-weight: 600;
  color: #1a1a1a;
}

/* ============================================
   TABLES
   ============================================ */
.report-table-wrapper {
  overflow-x: auto;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.report-table th {
  text-align: left;
  padding: 10px 12px;
  background: rgba(0,0,0,0.05);
  color: rgba(0,0,0,0.7);
  font-weight: 600;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

.report-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(0,0,0,0.05);
  color: rgba(0,0,0,0.9);
}

.report-table .label {
  font-weight: 500;
  color: rgba(0,0,0,0.7);
  width: 40%;
}

.report-table .value {
  color: #1a1a1a;
}

.report-table .mono {
  font-family: "SF Mono", monospace;
}

.table-scroll {
  overflow-x: auto;
}

.cf-table,
.coupon-table {
  font-size: 11px;
  min-width: 500px;
}

.status-badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
  display: inline-block;
}

.status-badge.paid {
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
}

.status-badge.future {
  background: rgba(0,0,0,0.1);
  color: rgba(0,0,0,0.7);
}

.report-footer {
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid rgba(0,0,0,0.1);
  font-size: 11px;
  color: rgba(0,0,0,0.6);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.footer-item {
  margin: 0;
}

/* ============================================
   ACTION BAR
   ============================================ */
.action-bar {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
}

.action-bar .btn-glass {
  flex: 1;
}

/* ============================================
   UTILS
   ============================================ */
.flex-center {
  display: flex;
  align-items: center;
  gap: 8px;
}

.text-gradient-blue {
  background: linear-gradient(to right, #60a5fa, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-orange { color: #fbbf24; }
.text-right { text-align: right; }
.mono { font-family: "SF Mono", monospace; }

.spinner-mini {
  width: 14px;
  height: 14px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

@media print {
  .page-container {
    gap: 0;
  }

  .action-bar,
  .section-header .btn-glass,
  .step-panel:nth-child(1),
  .step-panel:nth-child(2) {
    display: none;
  }

  .glass-card {
    page-break-inside: avoid;
    border: none;
    background: none;
    box-shadow: none;
    padding: 0;
  }

  .panel { padding: 0; }
  .preview-panel { max-height: none; }
}

@media (max-width: 1024px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }

  .checkbox-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container { padding: 16px; }
  .section-header { flex-direction: column; gap: 16px; }
  .action-bar { flex-direction: column; }
}
</style>