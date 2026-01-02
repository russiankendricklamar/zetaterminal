<template>
  <div class="bond-report-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Отчет по оценке облигаций</h1>
        <p class="subtitle">Формирование аналитического отчёта (DCF)</p>
      </div>
      <button class="btn btn-primary" @click="generateReport" :disabled="loading || !results">
        {{ loading ? 'Генерация...' : '📄 Скачать PDF' }}
      </button>
    </div>

    <!-- Step 1: Data Input -->
    <div class="card">
      <div class="card-header">
        <h3>Шаг 1: Загрузка данных из оценки</h3>
      </div>
      <div class="card-body">
        <div class="params-grid">
          <div class="form-group">
            <label>Выберите облигацию (ISIN)</label>
            <input
              v-model="params.secid"
              type="text"
              class="form-control"
              placeholder="RU000A10AU99"
              @change="onBondChange"
            />
          </div>

          <div class="form-group">
            <label>Дата оценки</label>
            <input
              v-model="params.valuationDate"
              type="date"
              class="form-control"
              @change="onBondChange"
            />
          </div>

          <div class="form-group">
            <label>Доходность %</label>
            <input
              v-model.number="params.discountYield"
              type="number"
              step="0.01"
              class="form-control"
              placeholder="14.0"
              @change="onBondChange"
            />
          </div>

          <div class="form-group">
            <label>База расчета</label>
            <select v-model.number="params.dayCount" class="form-control" @change="onBondChange">
              <option :value="365">365 (Actual/365)</option>
              <option :value="360">360 (30/360)</option>
            </select>
          </div>
        </div>
        <button class="btn btn-secondary" @click="calculateBond" :disabled="loading" style="margin-top: 12px; width: 100%;">
          {{ loading ? 'Загрузка...' : 'Загрузить оценку' }}
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error" class="alert alert-danger">
      <span>⚠️</span>
      <span>{{ error }}</span>
    </div>

    <!-- Step 2: Report Configuration -->
    <div v-if="results" class="card">
      <div class="card-header">
        <h3>Шаг 2: Конфигурация отчёта</h3>
      </div>
      <div class="card-body">
        <div class="report-config">
          <!-- Основные параметры -->
          <div class="config-section">
            <h4>Содержание отчета</h4>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input v-model="report.includeExec" type="checkbox" />
                <span>Резюме (Executive Summary)</span>
              </label>
              <label class="checkbox-label">
                <input v-model="report.includeBondInfo" type="checkbox" />
                <span>Параметры облигации</span>
              </label>
              <label class="checkbox-label">
                <input v-model="report.includeValuation" type="checkbox" />
                <span>Результаты оценки (Dirty/Clean Price)</span>
              </label>
              <label class="checkbox-label">
                <input v-model="report.includeCashFlows" type="checkbox" />
                <span>Таблица денежных потоков</span>
              </label>
              <label class="checkbox-label">
                <input v-model="report.includeCoupons" type="checkbox" />
                <span>График купонов</span>
              </label>
              <label class="checkbox-label">
                <input v-model="report.includeMetadata" type="checkbox" />
                <span>Метаданные (дата, бэйс)</span>
              </label>
            </div>
          </div>

          <!-- Параметры отчёта -->
          <div class="config-section">
            <h4>Параметры отчета</h4>
            <div class="form-row">
              <div class="form-group">
                <label>Автор отчета</label>
                <input v-model="report.author" type="text" class="form-control" placeholder="Имя аналитика" />
              </div>
              <div class="form-group">
                <label>Компания</label>
                <input v-model="report.company" type="text" class="form-control" placeholder="Компания/Фонд" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Дополнительные примечания</label>
                <textarea 
                  v-model="report.notes"
                  class="form-control"
                  rows="4"
                  placeholder="Комментарии, допущения, ограничения модели..."
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Report Preview -->
    <div v-if="results" class="card preview-card">
      <div class="card-header">
        <h3>Шаг 3: Предпросмотр отчета</h3>
      </div>
      <div class="card-body report-preview">
        <!-- Executive Summary -->
        <div v-if="report.includeExec" class="report-section">
          <h2 class="section-title">Резюме (Executive Summary)</h2>
          <div class="summary-box">
            <p><strong>Облигация:</strong> {{ results.secid }}</p>
            <p><strong>Номинал:</strong> {{ formatNumber(results.faceValue) }} ₽</p>
            <p><strong>Справедливая стоимость (Dirty Price):</strong> {{ formatNumber(results.dirtyPrice, 4) }} ₽ ({{ formatNumber(results.pricePercent, 2) }}% от номинала)</p>
            <p><strong>Чистая цена (Clean Price):</strong> {{ formatNumber(results.cleanPrice, 4) }} ₽</p>
            <p><strong>Дюрация:</strong> {{ formatNumber(results.duration, 4) }} лет</p>
            <p><strong>Дата оценки:</strong> {{ formatDate(params.valuationDate) }}</p>
          </div>
        </div>

        <!-- Bond Info -->
        <div v-if="report.includeBondInfo" class="report-section">
          <h2 class="section-title">Параметры облигации</h2>
          <table class="report-table">
            <tr>
              <td class="label">SECID/ISIN:</td>
              <td class="value">{{ results.secid }}</td>
            </tr>
            <tr>
              <td class="label">Номинал:</td>
              <td class="value">{{ formatNumber(results.faceValue) }} ₽</td>
            </tr>
            <tr>
              <td class="label">Купон:</td>
              <td class="value">{{ formatNumber(results.couponPercent, 3) }}% годовых</td>
            </tr>
            <tr>
              <td class="label">Дата выпуска:</td>
              <td class="value">{{ formatDate(results.issueDate) }}</td>
            </tr>
            <tr>
              <td class="label">Дата погашения:</td>
              <td class="value">{{ formatDate(results.maturityDate) }}</td>
            </tr>
            <tr>
              <td class="label">Периодичность выплат:</td>
              <td class="value">{{ results.paymentsPerYear }} раз(а) в год</td>
            </tr>
          </table>
        </div>

        <!-- Valuation Results -->
        <div v-if="report.includeValuation" class="report-section">
          <h2 class="section-title">Результаты оценки</h2>
          <table class="report-table">
            <tr>
              <td class="label">Dirty Price (с НКД):</td>
              <td class="value">{{ formatNumber(results.dirtyPrice, 4) }} ₽</td>
            </tr>
            <tr>
              <td class="label">Накопленный купонный доход (НКД):</td>
              <td class="value">{{ formatNumber(results.accruedInterest, 4) }} ₽</td>
            </tr>
            <tr>
              <td class="label">Clean Price (без НКД):</td>
              <td class="value">{{ formatNumber(results.cleanPrice, 4) }} ₽</td>
            </tr>
            <tr>
              <td class="label">Цена в % от номинала:</td>
              <td class="value">{{ formatNumber(results.pricePercent, 3) }}%</td>
            </tr>
            <tr>
              <td class="label">Дюрация Маколея:</td>
              <td class="value">{{ formatNumber(results.duration, 4) }} лет</td>
            </tr>
          </table>
        </div>

        <!-- Cash Flows -->
        <div v-if="report.includeCashFlows && results.cashFlows" class="report-section">
          <h2 class="section-title">Денежные потоки (DCF)</h2>
          <p class="section-desc">Таблица дисконтированных денежных потоков. Сумма приведённых стоимостей равна Dirty Price.</p>
          <div class="table-scroll">
            <table class="report-table cf-table">
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
                  <td class="mono">{{ formatNumber(cf.pv, 4) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td colspan="5" class="text-right"><strong>Итого (Dirty Price):</strong></td>
                  <td class="mono"><strong>{{ formatNumber(results.dirtyPrice, 4) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- Coupons Schedule -->
        <div v-if="report.includeCoupons && results.allCoupons" class="report-section">
          <h2 class="section-title">График купонных выплат</h2>
          <p class="section-desc">Полное расписание выплат купонов и номинала.</p>
          <div class="table-scroll">
            <table class="report-table coupon-table">
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
                  <td>{{ coupon.isPaid ? '✓ Выплачен' : '◷ Будущий' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Metadata -->
        <div v-if="report.includeMetadata" class="report-section">
          <h2 class="section-title">Метаданные модели</h2>
          <table class="report-table">
            <tr>
              <td class="label">Дата оценки:</td>
              <td class="value">{{ formatDate(params.valuationDate) }}</td>
            </tr>
            <tr>
              <td class="label">Дисконтная ставка (YTM):</td>
              <td class="value">{{ formatNumber(params.discountYield, 3) }}%</td>
            </tr>
            <tr>
              <td class="label">База расчета дней:</td>
              <td class="value">{{ params.dayCount }} дней</td>
            </tr>
            <tr>
              <td class="label">Количество денежных потоков:</td>
              <td class="value">{{ results.cashFlows.length }}</td>
            </tr>
            <tr v-if="report.notes">
              <td class="label">Примечания:</td>
              <td class="value">{{ report.notes }}</td>
            </tr>
          </table>
        </div>

        <!-- Footer -->
        <div class="report-footer">
          <p v-if="report.author"><strong>Автор:</strong> {{ report.author }}</p>
          <p v-if="report.company"><strong>Компания:</strong> {{ report.company }}</p>
          <p><small>Отчет сформирован: {{ new Date().toLocaleString('ru-RU') }}</small></p>
        </div>
      </div>
    </div>

    <!-- Download Button -->
    <div v-if="results" class="action-bar">
      <button class="btn btn-primary" @click="generateReport" :disabled="loading">
        {{ loading ? 'Генерация PDF...' : '📄 Скачать отчет PDF' }}
      </button>
      <button class="btn btn-secondary" @click="printReport">
        🖨️ Печать
      </button>
      <button class="btn btn-secondary" @click="copyToClipboard">
        📋 Копировать в буфер
      </button>
    </div>
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

// State
const params = ref<BondParams>({
  secid: 'RU000A10AU99',
  valuationDate: new Date().toISOString().split('T')[0],
  discountYield: 14.0,
  dayCount: 365
})

const results = ref<BondResults | null>(null)
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

    const data = await response.json()
    results.value = data
  } catch (err: any) {
    error.value = err.message || 'Ошибка при расчёте облигации'
    console.error(err)
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
    // Здесь можно добавить генерацию PDF через библиотеку (jsPDF, html2pdf и т.д.)
    // Пока используем print API
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
.bond-report-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.card-body {
  /* body content */
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 12px;
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

.form-control {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  font-family: var(--font-family-mono);
}

.form-control:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(255, 255, 255, 0.08);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1e40af);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

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
}

/* Report Config */
.report-config {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-section h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #fff;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
}

.checkbox-label input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

textarea {
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  font-family: var(--font-family-mono);
  resize: vertical;
}

/* Report Preview */
.preview-card {
  max-height: 600px;
  overflow-y: auto;
}

.report-preview {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
}

.report-section {
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.report-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #3b82f6;
}

.section-desc {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-style: italic;
}

.summary-box {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
  padding: 12px 16px;
  border-radius: 4px;
}

.summary-box p {
  margin: 6px 0;
  font-size: 13px;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 12px;
}

.report-table tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.report-table th {
  text-align: left;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  font-weight: 600;
  color: var(--text-secondary);
}

.report-table td {
  padding: 8px 12px;
}

.report-table .label {
  font-weight: 600;
  color: var(--text-secondary);
  width: 40%;
}

.report-table .value {
  font-family: var(--font-family-mono);
  color: var(--text-primary);
}

.report-table .mono {
  font-family: var(--font-family-mono);
}

.table-scroll {
  overflow-x: auto;
  margin-top: 12px;
}

.cf-table,
.coupon-table {
  font-size: 11px;
  min-width: 500px;
}

.report-footer {
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  color: var(--text-secondary);
}

.report-footer p {
  margin: 4px 0;
}

.action-bar {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  position: sticky;
  bottom: 20px;
}

.action-bar .btn {
  flex: 1;
}

@media print {
  .bond-report-page {
    padding: 0;
  }

  .action-bar,
  .page-header .btn {
    display: none;
  }

  .card {
    page-break-inside: avoid;
    border: none;
    background: none;
    padding: 0;
  }

  .preview-card {
    max-height: none;
  }
}

@media (max-width: 768px) {
  .bond-report-page {
    padding: 16px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .checkbox-group {
    grid-template-columns: 1fr;
  }

  .action-bar {
    flex-direction: column;
  }
}
</style>



