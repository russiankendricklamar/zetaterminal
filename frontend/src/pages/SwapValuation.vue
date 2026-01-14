<!-- src/pages/SwapValuation.vue -->
<template>
  <div class="swap-valuation-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Оценка свопов</h1>
        <p class="page-subtitle">Справедливая стоимость и анализ IRS, CDS, Basis Swaps</p>
      </div>
      
      <div class="header-right">
        <!-- Valuation Date -->
        <div class="control-group">
          <label class="control-label">Дата оценки:</label>
          <input 
            v-model="valuationDate" 
            type="date" 
            class="date-input"
            @change="updateValuation"
          />
        </div>

        <!-- Excel Upload -->
        <div class="control-group">
          <label class="control-label">Реестр:</label>
          <input 
            type="file" 
            ref="fileInputRef"
            @change="handleFileUpload" 
            accept=".xlsx,.xls"
            style="display: none"
            id="excel-upload"
          />
          <button 
            @click="() => { if (fileInputRef) fileInputRef.click() }" 
            class="btn-secondary"
            title="Загрузить реестр свопов из Excel"
          >
            Загрузить Excel
          </button>
        </div>

        <!-- Swap Type Selector -->
        <div class="control-group">
          <label class="control-label">Тип свопа:</label>
          <select v-model="selectedSwapType" class="swap-type-select" @change="updateValuation">
            <option value="irs">Interest Rate Swap (IRS)</option>
            <option value="cds">Credit Default Swap (CDS)</option>
            <option value="basis">Basis Swap</option>
            <option value="xccy">Cross-Currency Swap</option>
          </select>
        </div>

        <!-- Calculation Button -->
        <button 
          @click="calculateValuation" 
          class="btn-primary"
          :disabled="calculating"
        >
          <span v-if="!calculating">Пересчитать</span>
          <span v-else>↺ Считаю...</span>
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-message">
      ⚠️ {{ error }}
    </div>

    <!-- Registry Table (if loaded) -->
    <div v-if="registrySwaps.length > 0" class="card full-width" style="margin-bottom: 24px;">
      <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h3>Реестр свопов</h3>
          <span class="card-subtitle">Загружено свопов: {{ registrySwaps.length }}</span>
        </div>
        <div style="display: flex; gap: 8px;">
          <button 
            @click="exportRegistryToExcel" 
            class="btn-secondary"
            :disabled="registrySwaps.length === 0"
            style="font-size: 11px; padding: 6px 12px;"
            title="Выгрузить реестр в Excel"
          >
            📥 Выгрузить Excel
          </button>
          <button 
            @click="saveRegistryToParquetHandler" 
            class="btn-secondary"
            :disabled="registrySwaps.length === 0 || savingParquet"
            style="font-size: 11px; padding: 6px 12px;"
            title="Сохранить реестр в Supabase (parquet)"
          >
            <span v-if="!savingParquet">💾 Сохранить в БД</span>
            <span v-else>↺ Сохранение...</span>
          </button>
          <button 
            @click="calculateAllSwaps" 
            class="btn-secondary"
            :disabled="calculatingAll"
            style="font-size: 11px; padding: 6px 12px;"
          >
            <span v-if="!calculatingAll">Рассчитать все</span>
            <span v-else>↺ Считаю...</span>
          </button>
          <button 
            @click="clearRegistry" 
            class="btn-secondary"
            style="font-size: 11px; padding: 6px 12px; background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.3);"
          >
            ✕ Очистить
          </button>
        </div>
      </div>
      <div class="scenario-table-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Тип</th>
              <th>Номинал (млн)</th>
              <th>Срок (лет)</th>
              <th>Фикс. ставка (%)</th>
              <th>Плавающая (%)</th>
              <th v-if="swapResults.length > 0">Swap Value</th>
              <th v-if="swapResults.length > 0">DV01</th>
              <th>Действие</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(swap, idx) in registrySwaps" 
              :key="idx"
              :class="{ 'selected': selectedSwapIndex === idx }"
              @click="selectSwap(idx)"
            >
              <td>{{ idx + 1 }}</td>
              <td>{{ swap.swapType?.toUpperCase() || 'IRS' }}</td>
              <td class="mono">{{ swap.notional ? swap.notional.toFixed(2) : '-' }}</td>
              <td class="mono">{{ swap.tenor ? swap.tenor.toFixed(2) : '-' }}</td>
              <td class="mono">{{ swap.fixedRate ? swap.fixedRate.toFixed(2) + '%' : '-' }}</td>
              <td class="mono">{{ swap.floatingRate ? swap.floatingRate.toFixed(2) + '%' : '-' }}</td>
              <td v-if="swapResults.length > 0 && swapResults[idx]" class="mono" 
                  :class="swapResults[idx]?.swapValue >= 0 ? 'positive' : 'negative'">
                {{ swapResults[idx]?.swapValue ? formatCurrency(swapResults[idx].swapValue) : '-' }}
              </td>
              <td v-if="swapResults.length > 0 && swapResults[idx]" class="mono accent">
                {{ swapResults[idx]?.dv01 ? formatCompactCurrency(swapResults[idx].dv01) : '-' }}
              </td>
              <td>
                <button 
                  @click.stop="loadSwapToForm(idx)" 
                  class="btn-small"
                  title="Загрузить в форму"
                >
                  Загрузить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Input Parameters Section -->
    <div class="grid-2">
      <!-- Swap Parameters -->
      <div class="card">
        <div class="card-header">
          <h3>Параметры свопа</h3>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Номинал (млн)</label>
            <input v-model.number="params.notional" type="number" class="param-input" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Срок (годы)</label>
            <input v-model.number="params.tenor" type="number" class="param-input" step="0.5" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Фиксированная ставка (%)</label>
            <input v-model.number="params.fixedRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Купонов в год</label>
            <select v-model.number="params.couponsPerYear" class="param-input" @change="updateValuation">
              <option value="1">1</option>
              <option value="2">2 (Раз в полгода)</option>
              <option value="4">4 (Ежеквартально)</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Market Conditions -->
      <div class="card">
        <div class="card-header">
          <h3>Рыночные условия</h3>
        </div>
        <div class="parameter-group">
          <div class="param-row">
            <label>Индекс плавающей ставки (%)</label>
            <input v-model.number="params.floatingRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Спред (bp)</label>
            <input v-model.number="params.spread" type="number" class="param-input" step="1" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Дисконт кривая (базовая ставка, %)</label>
            <input v-model.number="params.discountRate" type="number" class="param-input" step="0.01" @change="updateValuation" />
          </div>
          <div class="param-row">
            <label>Волатильность (%)</label>
            <input v-model.number="params.volatility" type="number" class="param-input" step="0.1" @change="updateValuation" />
          </div>
        </div>
      </div>
    </div>

    <!-- Valuation Results -->
    <div class="grid-3">
      <!-- PV Fixed Leg -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>PV фиксированной ноги</h3>
          <span class="metric-unit">млн RUB</span>
        </div>
        <div class="metric-value accent">
          {{ formatCurrency(valuationResults.pvFixedLeg) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Купоны:</span>
          <span class="detail-value">{{ params.couponsPerYear * params.tenor }} шт.</span>
        </div>
      </div>

      <!-- PV Floating Leg -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>PV плавающей ноги</h3>
          <span class="metric-unit">млн RUB</span>
        </div>
        <div class="metric-value blue">
          {{ formatCurrency(valuationResults.pvFloatingLeg) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">Forward Rate:</span>
          <span class="detail-value">{{ (params.floatingRate + params.spread / 100).toFixed(2) }}%</span>
        </div>
      </div>

      <!-- Swap Value -->
      <div class="metric-card">
        <div class="metric-header">
          <h3>Стоимость свопа (Payer)</h3>
          <span class="metric-unit">млн RUB</span>
        </div>
        <div class="metric-value" :class="valuationResults.swapValue >= 0 ? 'positive' : 'negative'">
          {{ formatCurrency(valuationResults.swapValue) }}
        </div>
        <div class="metric-detail">
          <span class="detail-label">В % номинала:</span>
          <span class="detail-value">{{ ((valuationResults.swapValue / params.notional) * 100).toFixed(2) }}%</span>
        </div>
      </div>
    </div>

    <!-- Key Metrics Grid -->
    <div class="grid-3">
      <!-- Duration -->
      <div class="card">
        <div class="card-header">
          <h3>Анализ Duration</h3>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <span class="label">Modified Duration</span>
            <span class="value">{{ valuationResults.duration.toFixed(2) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">DV01 (М/bp)</span>
            <span class="value" :class="valuationResults.dv01 >= 0 ? 'positive' : 'negative'">
              {{ formatCompactCurrency(valuationResults.dv01) }}
            </span>
          </div>
          <div class="metric-item">
            <span class="label">BPV (М)</span>
            <span class="value mono">{{ (valuationResults.dv01 / 10000).toFixed(4) }}</span>
          </div>
        </div>
      </div>

      <!-- Convexity -->
      <div class="card">
        <div class="card-header">
          <h3>Выпуклость</h3>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <span class="label">Convexity</span>
            <span class="value">{{ valuationResults.convexity.toFixed(2) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">Gamma (М/bp²)</span>
            <span class="value">{{ (valuationResults.convexity / 100).toFixed(4) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">Уровень гарантирован</span>
            <span class="value">Низкий</span>
          </div>
        </div>
      </div>

      <!-- Spread Metrics -->
      <div class="card">
        <div class="card-header">
          <h3>Спред-метрики</h3>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <span class="label">Spread DV01 (М/bp)</span>
            <span class="value mono">{{ formatCompactCurrency(valuationResults.spreadDv01) }}</span>
          </div>
          <div class="metric-item">
            <span class="label">ASW (All-in Swap)</span>
            <span class="value">{{ params.spread }} bp</span>
          </div>
          <div class="metric-item">
            <span class="label">Z-spread</span>
            <span class="value">{{ (params.spread * 1.05).toFixed(0) }} bp</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Cashflow Schedule -->
    <div class="card full-width">
      <div class="card-header">
        <h3>График денежных потоков</h3>
        <span class="card-subtitle">Сравнение фиксированной и плавающей ног</span>
      </div>
      <div class="cashflow-table-container">
        <table class="cashflow-table">
          <thead>
            <tr>
              <th class="col-period">Период</th>
              <th class="col-date">Дата платежа</th>
              <th class="col-amount">Fixed Leg (М)</th>
              <th class="col-amount">Floating Leg (М)</th>
              <th class="col-amount">Net (М)</th>
              <th class="col-pv">PV (М)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(cf, idx) in valuationResults.cashflows" :key="idx">
              <td class="col-period">{{ idx + 1 }}</td>
              <td class="col-date mono">{{ formatDate(cf.date) }}</td>
              <td class="col-amount accent">{{ formatCurrency(cf.fixedLeg) }}</td>
              <td class="col-amount blue">{{ formatCurrency(cf.floatingLeg) }}</td>
              <td class="col-amount" :class="cf.net >= 0 ? 'positive' : 'negative'">
                {{ cf.net >= 0 ? '+' : '' }}{{ formatCurrency(cf.net) }}
              </td>
              <td class="col-pv mono">{{ formatCurrency(cf.pv) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Valuation Charts -->
    <div class="grid-2">
      <!-- PV Profile -->
      <div class="card">
        <div class="chart-header">
          <h3>Стоимость свопа vs Фиксированная ставка</h3>
          <span class="chart-subtitle">Чувствительность к изменению фиксированной ставки</span>
        </div>
        <div class="chart-container">
          <canvas ref="pvProfileRef"></canvas>
        </div>
      </div>

      <!-- DV01 Profile -->
      <div class="card">
        <div class="chart-header">
          <h3>DV01 vs Срок</h3>
          <span class="chart-subtitle">Риск по различным срокам</span>
        </div>
        <div class="chart-container">
          <canvas ref="dv01ProfileRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Scenario Analysis -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Анализ сценариев</h3>
        <span class="card-subtitle">Swap Value при различных уровнях ставок</span>
      </div>
      <div class="scenario-container">
        <table class="scenario-table">
          <thead>
            <tr>
              <th>Сценарий</th>
              <th>Fixed Rate</th>
              <th>Floating Rate</th>
              <th>PV Fixed Leg</th>
              <th>PV Floating Leg</th>
              <th>Swap Value (М)</th>
              <th>PnL (М)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="scenario in scenarioAnalysis" :key="scenario.name" :class="scenario.isBase ? 'base' : ''">
              <td class="scenario-name">{{ scenario.name }}</td>
              <td class="mono">{{ scenario.fixedRate.toFixed(2) }}%</td>
              <td class="mono">{{ scenario.floatingRate.toFixed(2) }}%</td>
              <td class="accent">{{ formatCurrency(scenario.pvFixed) }}</td>
              <td class="blue">{{ formatCurrency(scenario.pvFloating) }}</td>
              <td class="mono" :class="scenario.swapValue >= 0 ? 'positive' : 'negative'">
                {{ scenario.swapValue >= 0 ? '+' : '' }}{{ formatCurrency(scenario.swapValue) }}
              </td>
              <td class="mono" :class="scenario.pnl >= 0 ? 'positive' : 'negative'">
                {{ scenario.pnl >= 0 ? '+' : '' }}{{ formatCurrency(scenario.pnl) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Risk Summary -->
    <div class="grid-3">
      <div class="risk-card risk-high">
        <div class="risk-header">
          <span class="risk-icon"></span>
          <h3>Риск Duration</h3>
        </div>
        <div class="risk-value">{{ valuationResults.duration.toFixed(2) }} y</div>
        <div class="risk-detail">ΔPV / 100bp: {{ formatCompactCurrency(valuationResults.dv01) }}</div>
      </div>

      <div class="risk-card risk-medium">
        <div class="risk-header">
          <span class="risk-icon"></span>
          <h3>Риск спреда</h3>
        </div>
        <div class="risk-value">{{ params.spread }} bp</div>
        <div class="risk-detail">Spread DV01: {{ formatCompactCurrency(valuationResults.spreadDv01) }}</div>
      </div>

      <div class="risk-card risk-low">
        <div class="risk-header">
          <span class="risk-icon"></span>
          <h3>Риск Convexity</h3>
        </div>
        <div class="risk-value">{{ valuationResults.convexity.toFixed(2) }}</div>
        <div class="risk-detail">Низкий риск для vanilla</div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Модель: Discounted Cash Flow (DCF)</span>
      <span>• Метод: Bootstrap yield curve</span>
      <span>• Расчёт в реальном времени</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'
import * as XLSX from 'xlsx'
import { valuateSwap, saveRegistryToParquet, type SwapValuationResponse } from '@/services/swapService'

const selectedSwapType = ref('irs')
const calculating = ref(false)
const error = ref('')
const fileInputRef = ref<HTMLInputElement | null>(null)
const registrySwaps = ref<any[]>([])
const selectedSwapIndex = ref<number | null>(null)
const swapResults = ref<(SwapValuationResponse | null)[]>([])
const calculatingAll = ref(false)
const savingParquet = ref(false)
const valuationDate = ref(new Date().toISOString().split('T')[0])

// Swap Parameters
const params = ref({
  notional: 100,            // млн
  tenor: 5,                 // лет
  fixedRate: 4.25,          // %
  floatingRate: 4.15,       // %
  spread: 15,               // bp
  couponsPerYear: 2,
  discountRate: 4.2,        // %
  volatility: 12            // %
})

// Valuation Results
const valuationResults = ref<SwapValuationResponse>({
  pvFixedLeg: 0,
  pvFloatingLeg: 0,
  swapValue: 0,
  duration: 0,
  dv01: 0,
  spreadDv01: 0,
  convexity: 0,
  cashflows: [],
  scenarios: []
})

// Scenario Analysis - используем данные из API
const scenarioAnalysis = computed(() => {
  return valuationResults.value.scenarios || []
})

// Chart References
const pvProfileRef = ref<HTMLCanvasElement | null>(null)
const dv01ProfileRef = ref<HTMLCanvasElement | null>(null)

let pvProfileChart: Chart | null = null
let dv01ProfileChart: Chart | null = null

// Methods
const formatCurrency = (val: number) => {
  if (Math.abs(val) >= 1) {
    return (val >= 0 ? '+' : '') + val.toFixed(2)
  }
  return (val >= 0 ? '+' : '') + (val * 1_000_000).toFixed(0)
}

const formatCompactCurrency = (val: number) => {
  if (Math.abs(val) >= 1_000_000) {
    return (val / 1_000_000).toFixed(1) + 'М'
  }
  return '$' + (val / 1000).toFixed(0) + 'K'
}

const formatDate = (dateStr: string) => {
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch {
    return dateStr
  }
}

const updateValuation = () => {
  initCharts()
}

const calculateValuation = async () => {
  calculating.value = true
  error.value = ''
  
  try {
    const result = await valuateSwap({
      notional: params.value.notional,
      tenor: params.value.tenor,
      fixedRate: params.value.fixedRate,
      floatingRate: params.value.floatingRate,
      spread: params.value.spread,
      couponsPerYear: params.value.couponsPerYear,
      discountRate: params.value.discountRate,
      volatility: params.value.volatility,
      swapType: selectedSwapType.value
    })
    
    valuationResults.value = result
    updateValuation()
  } catch (err: any) {
    error.value = err.message || 'Ошибка при расчете свопа'
    console.error('Swap valuation error:', err)
  } finally {
    calculating.value = false
  }
}

const initCharts = () => {
  if (pvProfileChart) pvProfileChart.destroy()
  if (dv01ProfileChart) dv01ProfileChart.destroy()

  // PV Profile
  if (pvProfileRef.value?.getContext('2d')) {
    pvProfileChart = new Chart(pvProfileRef.value.getContext('2d') as any, {
      type: 'line',
      data: {
        labels: ['3.25%', '3.75%', '4.25%', '4.75%', '5.25%'],
        datasets: [{
          label: 'Swap Value',
          data: [5.8, 4.2, 2.45, 0.95, -0.5],
          borderColor: '#38bdf8',
          backgroundColor: 'rgba(56, 189, 248, 0.08)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }

  // DV01 Profile
  if (dv01ProfileRef.value?.getContext('2d')) {
    dv01ProfileChart = new Chart(dv01ProfileRef.value.getContext('2d') as any, {
      type: 'bar',
      data: {
        labels: ['2Y', '3Y', '5Y', '7Y', '10Y'],
        datasets: [{
          label: 'DV01 (RUB)',
          data: [28000, 35000, 42500, 48000, 52000],
          backgroundColor: 'rgba(96, 165, 250, 0.6)',
          borderColor: '#60a5fa',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
        }
      }
    } as any)
  }
}

// Excel File Upload Handler
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const arrayBuffer = await file.arrayBuffer()
    const workbook = XLSX.read(arrayBuffer, { type: 'array' })
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { raw: false })

    // Парсим данные из Excel
    const swaps: any[] = []
    
    for (const row of jsonData as any[]) {
      const swap: any = {
        notional: parseFloat(row['Notional'] || row['notional'] || row['Номинал'] || row['Номинал (млн)'] || '100'),
        tenor: parseFloat(row['Tenor'] || row['tenor'] || row['Срок'] || row['Срок (лет)'] || row['Срок (годы)'] || '5'),
        fixedRate: parseFloat(row['Fixed Rate'] || row['fixedRate'] || row['Фиксированная ставка'] || row['Фикс. ставка'] || row['Fixed'] || '4.25'),
        floatingRate: parseFloat(row['Floating Rate'] || row['floatingRate'] || row['Плавающая ставка'] || row['Floating'] || row['Index'] || '4.15'),
        spread: parseFloat(row['Spread'] || row['spread'] || row['Спред'] || row['Спред (bp)'] || '15'),
        couponsPerYear: parseFloat(row['Coupons Per Year'] || row['couponsPerYear'] || row['Купонов в год'] || row['Frequency'] || '2'),
        discountRate: parseFloat(row['Discount Rate'] || row['discountRate'] || row['Дисконт кривая'] || row['Базовая ставка'] || '4.2'),
        volatility: parseFloat(row['Volatility'] || row['volatility'] || row['Волатильность'] || row['Vol'] || '12'),
        swapType: (row['Type'] || row['Swap Type'] || row['type'] || row['Тип'] || row['Тип свопа'] || 'irs').toLowerCase(),
      }

      // Нормализация типа свопа
      if (swap.swapType && !['irs', 'cds', 'basis', 'xccy'].includes(swap.swapType)) {
        const typeMap: Record<string, string> = {
          'interest rate swap': 'irs',
          'credit default swap': 'cds',
          'basis swap': 'basis',
          'cross currency': 'xccy',
          'cross-currency': 'xccy',
          'процентный': 'irs',
          'кредитный': 'cds',
          'базисный': 'basis',
          'валютный': 'xccy'
        }
        swap.swapType = typeMap[swap.swapType.toLowerCase()] || 'irs'
      }

      // Проверяем, что есть минимальные данные
      if (swap.notional > 0 && swap.tenor > 0) {
        swaps.push(swap)
      }
    }

    registrySwaps.value = swaps
    selectedSwapIndex.value = null
    swapResults.value = []
  } catch (err: any) {
    console.error('Excel parsing error:', err)
    error.value = `Ошибка при загрузке файла: ${err.message}`
  }
}

// Select swap from registry
const selectSwap = (index: number) => {
  selectedSwapIndex.value = index
}

// Load swap to form
const loadSwapToForm = (index: number) => {
  const swap = registrySwaps.value[index]
  if (!swap) return

  params.value.notional = swap.notional || params.value.notional
  params.value.tenor = swap.tenor || params.value.tenor
  params.value.fixedRate = swap.fixedRate || params.value.fixedRate
  params.value.floatingRate = swap.floatingRate || params.value.floatingRate
  params.value.spread = swap.spread || params.value.spread
  params.value.couponsPerYear = swap.couponsPerYear || params.value.couponsPerYear
  params.value.discountRate = swap.discountRate || params.value.discountRate
  params.value.volatility = swap.volatility || params.value.volatility
  selectedSwapType.value = swap.swapType || selectedSwapType.value

  // Автоматически рассчитываем после загрузки
  setTimeout(() => {
    calculateValuation()
  }, 100)
}

// Calculate all swaps
const calculateAllSwaps = async () => {
  calculatingAll.value = true
  swapResults.value = []
  error.value = ''

  try {
    for (let i = 0; i < registrySwaps.value.length; i++) {
      const swap = registrySwaps.value[i]
      try {
        const result = await valuateSwap({
          notional: swap.notional,
          tenor: swap.tenor,
          fixedRate: swap.fixedRate,
          floatingRate: swap.floatingRate,
          spread: swap.spread,
          couponsPerYear: swap.couponsPerYear,
          discountRate: swap.discountRate,
          volatility: swap.volatility,
          swapType: swap.swapType || 'irs'
        })
        swapResults.value.push(result)
      } catch (err: any) {
        swapResults.value.push(null)
        console.error(`Error calculating swap ${i + 1}:`, err)
      }
    }
  } catch (err: any) {
    console.error('Error calculating swaps:', err)
    error.value = `Ошибка при расчете свопов: ${err.message}`
  } finally {
    calculatingAll.value = false
  }
}

// Export registry to Excel
const exportRegistryToExcel = () => {
  if (registrySwaps.value.length === 0) return

  // Prepare data for export
  const exportData = registrySwaps.value.map((swap, idx) => ({
    '№': idx + 1,
    'Тип': swap.swapType?.toUpperCase() || 'IRS',
    'Номинал (млн)': swap.notional || 0,
    'Срок (лет)': swap.tenor || 0,
    'Фиксированная ставка (%)': swap.fixedRate || 0,
    'Плавающая ставка (%)': swap.floatingRate || 0,
    'Спред (bp)': swap.spread || 0,
    'Купонов в год': swap.couponsPerYear || 2,
    'Дисконт кривая (%)': swap.discountRate || 0,
    'Волатильность (%)': swap.volatility || 0,
    'Swap Value': swapResults.value[idx]?.swapValue || '',
    'DV01': swapResults.value[idx]?.dv01 || '',
    'Duration': swapResults.value[idx]?.duration || '',
    'Convexity': swapResults.value[idx]?.convexity || ''
  }))

  // Create workbook
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Реестр свопов')

  // Generate filename with date
  const dateStr = new Date().toISOString().split('T')[0]
  const fileName = `реестр_свопов_${dateStr}.xlsx`

  // Save file
  XLSX.writeFile(wb, fileName)
}

// Save registry to parquet
const saveRegistryToParquetHandler = async () => {
  if (registrySwaps.value.length === 0) return

  savingParquet.value = true
  error.value = ''

  try {
    const result = await saveRegistryToParquet(registrySwaps.value)
    if (result.success) {
      error.value = `Реестр успешно сохранен: ${result.data.file_name}`
      setTimeout(() => {
        error.value = ''
      }, 5000)
    }
  } catch (err: any) {
    console.error('Error saving registry to parquet:', err)
    error.value = `Ошибка при сохранении реестра: ${err.message}`
  } finally {
    savingParquet.value = false
  }
}

// Clear registry
const clearRegistry = () => {
  registrySwaps.value = []
  selectedSwapIndex.value = null
  swapResults.value = []
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

onMounted(() => {
  calculateValuation()
})

onBeforeUnmount(() => {
  if (pvProfileChart) pvProfileChart.destroy()
  if (dv01ProfileChart) dv01ProfileChart.destroy()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.swap-valuation-page {
  width: 100%;
  padding: 24px;
  background: linear-gradient(180deg, rgba(15,20,25,0.5) 0%, rgba(26,31,46,0.3) 100%);
  color: #fff;
  min-height: 100vh;
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
  min-width: 300px;
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
  white-space: nowrap;
}

.swap-type-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
}

.swap-type-select option {
  background: #1e1f28;
  color: #fff;
}

.date-input {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  padding: 4px 8px;
  cursor: pointer;
  font-family: inherit;
}

.date-input::-webkit-calendar-picker-indicator {
  filter: invert(1);
  cursor: pointer;
}

.date-input::-webkit-datetime-edit-text {
  color: #fff;
}

.date-input::-webkit-datetime-edit-month-field,
.date-input::-webkit-datetime-edit-day-field,
.date-input::-webkit-datetime-edit-year-field {
  color: #fff;
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

.btn-secondary {
  padding: 8px 16px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

.btn-secondary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-small {
  padding: 4px 8px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.card-subtitle {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  display: block;
  margin-top: 4px;
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
}

.scenario-table-container {
  overflow-x: auto;
}

.scenario-table tr.selected {
  background: rgba(59, 130, 246, 0.15);
  border-left: 3px solid #3b82f6;
}

/* ============================================
   CARDS
   ============================================ */
.card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
  margin-bottom: 20px;
}

.card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 
    0 25px 50px -10px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
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

.card-subtitle {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  display: block;
  margin-top: 4px;
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
}

.full-width {
  grid-column: 1 / -1;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

/* ============================================
   PARAMETERS
   ============================================ */
.parameter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.param-row label {
  font-size: 11px;
  color: rgba(255,255,255,0.6);
  font-weight: 600;
  min-width: 150px;
}

.param-input {
  flex: 1;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-family: "SF Mono", monospace;
}

.param-input:focus {
  outline: none;
  border-color: rgba(59, 130, 246, 0.5);
  background: rgba(59, 130, 246, 0.05);
}

/* ============================================
   METRIC CARDS
   ============================================ */
.metric-card {
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 
    0 20px 40px -10px rgba(0, 0, 0, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.metric-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.metric-header {
  margin-bottom: 8px;
}

.metric-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.metric-unit {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  display: block;
  margin-top: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.metric-value.accent {
  color: #f59e0b;
}

.metric-value.blue {
  color: #60a5fa;
}

.metric-value.positive {
  color: #4ade80;
}

.metric-value.negative {
  color: #f87171;
}

.metric-detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   METRICS LIST
   ============================================ */
.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  font-size: 11px;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-item .label {
  color: rgba(255,255,255,0.5);
}

.metric-item .value {
  font-weight: 600;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.metric-item .value.positive {
  color: #4ade80;
}

.metric-item .value.negative {
  color: #f87171;
}

/* ============================================
   CASHFLOW TABLE
   ============================================ */
.cashflow-table-container {
  overflow-x: auto;
}

.cashflow-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.cashflow-table th,
.cashflow-table td {
  padding: 10px;
  text-align: right;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.cashflow-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.col-period,
.col-date {
  text-align: left;
}

.col-amount.accent {
  color: #f59e0b;
}

.col-amount.blue {
  color: #60a5fa;
}

.col-amount.positive {
  color: #4ade80;
}

.col-amount.negative {
  color: #f87171;
}

.col-pv {
  font-family: "SF Mono", monospace;
}

.mono {
  font-family: "SF Mono", monospace;
}

/* ============================================
   SCENARIO TABLE
   ============================================ */
.scenario-container {
  overflow-x: auto;
}

.scenario-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.scenario-table th,
.scenario-table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: right;
}

.scenario-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 10px;
}

.scenario-table tr.base {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.scenario-name {
  text-align: left;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
}

.scenario-table .accent {
  color: #f59e0b;
}

.scenario-table .blue {
  color: #60a5fa;
}

.scenario-table .positive {
  color: #4ade80;
}

.scenario-table .negative {
  color: #f87171;
}

/* ============================================
   RISK CARDS
   ============================================ */
.risk-card {
  background: rgba(30, 32, 40, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  border-left: 3px solid;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-card.risk-high {
  border-left-color: #f87171;
}

.risk-card.risk-medium {
  border-left-color: #f59e0b;
}

.risk-card.risk-low {
  border-left-color: #4ade80;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-icon {
  font-size: 18px;
}

.risk-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
  margin: 0;
}

.risk-value {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  font-family: "SF Mono", monospace;
}

.risk-detail {
  font-size: 10px;
  color: rgba(255,255,255,0.4);
}

/* ============================================
   CHARTS
   ============================================ */
.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  flex-direction: column;
  gap: 4px;
}

.chart-header h3 {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255,255,255,0.6);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0;
}

.chart-subtitle {
  font-size: 10px;
  color: rgba(255,255,255,0.3);
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 360px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(107, 114, 128, 0.08);
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* ============================================
   ERROR MESSAGE
   ============================================ */
.error-message {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  color: #fca5a5;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
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
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .page-header {
    flex-direction: column;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
  }

  .control-group {
    width: 100%;
  }

  .grid-2,
  .grid-3 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .swap-valuation-page {
    padding: 16px;
  }

  .page-header {
    gap: 16px;
  }

  .param-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .param-row label {
    min-width: unset;
  }

  .param-input {
    width: 100%;
  }

  .chart-container {
    height: 300px;
  }

  .cashflow-table,
  .scenario-table {
    font-size: 10px;
  }

  .cashflow-table th,
  .cashflow-table td,
  .scenario-table th,
  .scenario-table td {
    padding: 6px;
  }
}
</style>
