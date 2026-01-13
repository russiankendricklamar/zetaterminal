<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Результаты бэктеста</h1>
        <p class="section-subtitle">Историческая симуляция стратегии (Long/Short)</p>
      </div>
      
      <div class="header-right">
        <!-- Selected Bank -->
        <div class="glass-pill control-pill">
           <span class="lbl-mini">Банк:</span>
           <span class="text-white font-bold">{{ selectedBank.name }}</span>
        </div>
        
        <!-- Glass Segmented Control -->
        <div class="glass-segmented-control">
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
    </div>

    <!-- KPI Cards (4-column) -->
    <div class="kpi-cards-grid">
      <div class="glass-card kpi-card">
        <div class="kpi-label">Общая доходность</div>
        <div class="kpi-value text-gradient-green">
          {{ backtestResults?.metrics ? (backtestResults.metrics.total_return * 100).toFixed(1) + '%' : '+24.5%' }}
        </div>
        <div class="kpi-change text-green">
           <span class="icon-up">↑</span> vs SPY: +6.2%
        </div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-label">CAGR (Годовая)</div>
        <div class="kpi-value text-white">
          {{ backtestResults?.metrics ? (backtestResults.metrics.cagr * 100).toFixed(1) + '%' : '18.2%' }}
        </div>
        <div class="kpi-change text-muted">Безрисковая ставка: 5.0%</div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-label">Коэф. Шарпа</div>
        <div class="kpi-value text-gradient-blue">
          {{ backtestResults?.metrics ? backtestResults.metrics.sharpe_ratio.toFixed(2) : '1.58' }}
        </div>
        <div class="kpi-change text-blue">Топ 15%</div>
      </div>

      <div class="glass-card kpi-card">
        <div class="kpi-label">Макс. Просадка</div>
        <div class="kpi-value text-red">
          {{ backtestResults?.metrics ? (backtestResults.metrics.max_drawdown * 100).toFixed(1) + '%' : '-14.2%' }}
        </div>
        <div class="kpi-change text-red">Высокий риск</div>
      </div>
    </div>

    <!-- Equity Curve Chart -->
    <div class="glass-card chart-panel">
      <div class="panel-header">
        <div class="ph-left">
            <h3>Кривая капитала</h3>
            <span class="badge-live">Накопительный</span>
        </div>
        <div class="chart-legend">
          <div class="legend-item"><span class="dot strategy"></span>Портфель</div>
          <div class="legend-item"><span class="dot benchmark"></span>S&P 500</div>
        </div>
      </div>
      <div class="chart-container">
         <svg viewBox="0 0 1000 250" preserveAspectRatio="none" class="main-svg">
              <!-- Gradients -->
              <defs>
                <linearGradient id="grad-green" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="rgba(74, 222, 128, 0.3)"/>
                  <stop offset="100%" stop-color="rgba(74, 222, 128, 0)"/>
                </linearGradient>
              </defs>

              <!-- Grid -->
              <line x1="0" y1="50" x2="1000" y2="50" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="125" x2="1000" y2="125" stroke="rgba(255,255,255,0.05)" />
              <line x1="0" y1="200" x2="1000" y2="200" stroke="rgba(255,255,255,0.05)" />

              <!-- Benchmark (Dashed) -->
              <path :d="generateBenchmarkPath()" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2" stroke-dasharray="6,4"/>
              
              <!-- Strategy Area -->
              <path :d="generateStrategyAreaPath()" fill="url(#grad-green)" stroke="none"/>
              <!-- Strategy Line -->
              <path :d="generateStrategyPath()" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round"/>
              
              <!-- Max Drawdown Marker -->
              <circle v-if="maxDrawdownMarker" :cx="maxDrawdownMarker.x" :cy="maxDrawdownMarker.y" r="4" fill="#1e293b" stroke="#f87171" stroke-width="2" />
         </svg>
      </div>
    </div>

    <!-- Split View: Heatmap & Stats -->
    <div class="dashboard-grid">
      
      <!-- Left: Monthly Heatmap -->
      <div class="col-left">
        <div class="glass-card panel-full">
          <div class="panel-header">
             <h3>Месячная доходность</h3>
          </div>
          <div class="table-wrapper custom-scroll">
            <table class="heatmap-table">
              <thead>
                <tr>
                  <th class="col-month"></th>
                  <th v-for="year in computedYears" :key="year" class="col-year">{{ year }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(month, idx) in months" :key="month">
                  <td class="col-month">{{ month }}</td>
                  <td v-for="year in computedYears" :key="`${month}-${year}`" class="col-val">
                    <div class="val-pill" :class="getReturnClass(computedMonthlyReturns[idx]?.[year] || '0.0')">
                      {{ computedMonthlyReturns[idx]?.[year] || '0.0' }}%
                    </div>
                  </td>
                </tr>
                <!-- Total Row -->
                <tr class="row-total">
                    <td class="col-month">YTD</td>
                    <td class="col-val"><span class="text-green font-bold">+24.1%</span></td>
                    <td class="col-val"><span class="text-green font-bold">+18.5%</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right: Stats & Drawdowns -->
      <div class="col-right">
        
        <!-- Detailed Stats -->
        <div class="glass-card panel-full">
          <div class="panel-header">
            <h3>Статистика сделок</h3>
          </div>
          <div class="stats-grid-mini">
             <div class="stat-box">
                <span class="lbl">Всего сделок</span>
                <span class="val">{{ backtestResults?.metrics?.total_trades || 243 }}</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Win Rate</span>
                <span class="val text-green">{{ backtestResults?.metrics ? (backtestResults.metrics.win_rate * 100).toFixed(1) + '%' : '64.2%' }}</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Profit Factor</span>
                <span class="val text-green">{{ backtestResults?.metrics ? backtestResults.metrics.profit_factor.toFixed(2) : '2.34' }}</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Средняя прибыль</span>
                <span class="val text-green">{{ backtestResults?.metrics ? '+' + backtestResults.metrics.avg_profit.toFixed(0) : '+₽245' }}</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Средний убыток</span>
                <span class="val text-red">{{ backtestResults?.metrics ? '-' + backtestResults.metrics.avg_loss.toFixed(0) : '-₽145' }}</span>
             </div>
             <div class="stat-box">
                <span class="lbl">Время удержания</span>
                <span class="val">{{ backtestResults?.metrics ? backtestResults.metrics.hold_time.toFixed(1) + 'd' : '8.4d' }}</span>
             </div>
          </div>
        </div>

        <!-- Drawdowns List -->
        <div class="glass-card panel-full">
          <div class="panel-header">
            <h3>Топ 3 просадки</h3>
          </div>
          <div class="drawdown-list">
             <div v-for="(dd, idx) in (backtestResults?.metrics?.drawdowns || drawdowns)" :key="idx" class="dd-item">
                <div class="dd-info">
                   <span class="dd-period">{{ dd.period }}</span>
                   <span class="dd-rec">Восстановление: {{ dd.recovery }}</span>
                </div>
                <div class="dd-right">
                    <span class="dd-val text-red">{{ dd.amount.toFixed(1) }}%</span>
                    <div class="dd-bar-bg">
                        <div class="dd-bar-fill" :style="{ width: Math.abs(dd.amount) * 3 + 'px' }"></div>
                    </div>
                </div>
             </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { runPortfolioBacktest, type BacktestResponse } from '@/services/backtestService'
import { usePortfolioStore } from '@/stores/portfolio'

const portfolioStore = usePortfolioStore()

const selectedBank = computed(() => portfolioStore.selectedBank)

const periods = ref(['1M', '3M', '6M', 'YTD', '1Y', 'All'])
const selectedPeriod = ref('YTD')
const isRunning = ref(false)
const backtestResults = ref<BacktestResponse | null>(null)

const years = ref(['2024', '2025'])
const months = ref(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])

interface MonthlyData {
  [key: string]: string;
}

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
  { period: 'Mar 23 — May 23', amount: -14.2, recovery: '6 mo' },
  { period: 'Sep 23 — Oct 23', amount: -8.5, recovery: '3 mo' },
  { period: 'Feb 24 — Mar 24', amount: -5.3, recovery: '2 mo' },
]

const getReturnClass = (returnValue: string | number) => {
  const value = typeof returnValue === 'string' ? parseFloat(returnValue) : returnValue
  if (value >= 3) return 'bg-green-strong'
  if (value > 0) return 'bg-green-soft'
  if (value === 0) return 'bg-neutral'
  if (value > -2) return 'bg-red-soft'
  return 'bg-red-strong'
}

// Computed для месячной доходности
const computedMonthlyReturns = computed(() => {
  if (!backtestResults.value?.metrics?.monthly_returns) {
    return monthlyReturns.value
  }
  
  const apiReturns = backtestResults.value.metrics.monthly_returns
  const result: MonthlyData[] = []
  
  // Преобразуем данные из API в формат для отображения
  const monthNames = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
  const apiYears = Object.keys(apiReturns).sort()
  
  for (let monthIdx = 0; monthIdx < 12; monthIdx++) {
    const monthData: MonthlyData = {}
    for (const year of apiYears) {
      const monthValue = apiReturns[year]?.[monthIdx + 1]
      if (monthValue !== undefined) {
        monthData[year] = monthValue > 0 ? '+' + monthValue.toFixed(1) : monthValue.toFixed(1)
      } else {
        monthData[year] = '0.0'
      }
    }
    result.push(monthData)
  }
  
  return result
})

const computedYears = computed(() => {
  if (!backtestResults.value?.metrics?.monthly_returns) {
    return years.value
  }
  return Object.keys(backtestResults.value.metrics.monthly_returns).sort()
})

// Функция для запуска бэктеста
const runBacktest = async () => {
  if (isRunning.value) return
  isRunning.value = true
  
  try {
    // Генерируем mock данные для mu и cov_matrix
    const nAssets = portfolioStore.positions.length || 23
    const assetNames = portfolioStore.positions.map(p => p.symbol)
    
    // Mock ожидаемые доходности (5-15% годовых)
    const mu = Array.from({ length: nAssets }, () => 0.05 + Math.random() * 0.10)
    
    // Mock ковариационная матрица
    const correlationMatrix = portfolioStore.correlationMatrix
    const volatilities = Array.from({ length: nAssets }, () => 0.15 + Math.random() * 0.15)
    
    const covMatrix: number[][] = []
    for (let i = 0; i < nAssets; i++) {
      const row: number[] = []
      for (let j = 0; j < nAssets; j++) {
        let correlation = 0.3
        if (correlationMatrix.length > i && correlationMatrix[i]?.values?.[j] !== undefined) {
          correlation = correlationMatrix[i].values[j]
        } else if (i === j) {
          correlation = 1.0
        }
        row.push(correlation * volatilities[i] * volatilities[j])
      }
      covMatrix.push(row)
    }
    
    const response = await runPortfolioBacktest({
      mu,
      cov_matrix: covMatrix,
      initial_capital: 1000000,
      risk_free_rate: 0.1394, // 13.94% безрисковая ставка
      gamma: 3.0,
      horizon_years: 1.0,
      n_steps: 252,
      asset_names: assetNames,
      n_paths: 1000,
      seed: 42
    })
    
    backtestResults.value = response
  } catch (e) {
    console.error('Ошибка бэктестинга:', e)
  } finally {
    isRunning.value = false
  }
}

// Функции для генерации путей SVG
const generateStrategyPath = () => {
  if (!backtestResults.value?.equity_curve || backtestResults.value.equity_curve.length === 0) {
    return "M0,220 Q150,200 300,150 T600,100 T1000,40"
  }
  
  const curve = backtestResults.value.equity_curve
  const minValue = Math.min(...curve)
  const maxValue = Math.max(...curve)
  const range = maxValue - minValue || 1
  const height = 250
  const width = 1000
  const steps = curve.length
  
  let path = ""
  for (let i = 0; i < steps; i++) {
    const x = (i / (steps - 1)) * width
    const y = height - ((curve[i] - minValue) / range) * (height - 50) - 25
    if (i === 0) {
      path += `M${x},${y}`
    } else {
      path += ` L${x},${y}`
    }
  }
  
  return path
}

const generateBenchmarkPath = () => {
  if (!backtestResults.value?.benchmark_curve || backtestResults.value.benchmark_curve.length === 0) {
    return "M0,220 Q150,210 300,190 T600,160 T1000,120"
  }
  
  const curve = backtestResults.value.benchmark_curve
  const minValue = Math.min(...backtestResults.value.equity_curve || [0], ...curve)
  const maxValue = Math.max(...backtestResults.value.equity_curve || [0], ...curve)
  const range = maxValue - minValue || 1
  const height = 250
  const width = 1000
  const steps = curve.length
  
  let path = ""
  for (let i = 0; i < steps; i++) {
    const x = (i / (steps - 1)) * width
    const y = height - ((curve[i] - minValue) / range) * (height - 50) - 25
    if (i === 0) {
      path += `M${x},${y}`
    } else {
      path += ` L${x},${y}`
    }
  }
  
  return path
}

const generateStrategyAreaPath = () => {
  const strategyPath = generateStrategyPath()
  if (!strategyPath || strategyPath === "M0,220 Q150,200 300,150 T600,100 T1000,40") {
    return "M0,220 Q150,200 300,150 T600,100 T1000,40 V250 H0 Z"
  }
  
  // Добавляем нижнюю границу для area chart
  const bottomY = 250
  const width = 1000
  
  // Извлекаем последнюю точку из пути
  const lastMatch = strategyPath.match(/L([0-9.]+),([0-9.]+)$/)
  if (lastMatch) {
    return strategyPath + ` L${lastMatch[1]},${bottomY} L0,${bottomY} Z`
  }
  
  return strategyPath + ` V250 H0 Z`
}

const maxDrawdownMarker = computed(() => {
  if (!backtestResults.value?.metrics?.drawdowns || backtestResults.value.metrics.drawdowns.length === 0) {
    return null
  }
  
  const largestDD = backtestResults.value.metrics.drawdowns[0]
  const curve = backtestResults.value.equity_curve
  if (!curve || curve.length === 0) return null
  
  // Находим индекс максимальной просадки (упрощенно)
  const minValue = Math.min(...curve)
  const minIndex = curve.indexOf(minValue)
  
  if (minIndex === -1) return null
  
  const minVal = Math.min(...curve)
  const maxVal = Math.max(...curve)
  const range = maxVal - minVal || 1
  const height = 250
  const width = 1000
  const steps = curve.length
  
  const x = (minIndex / (steps - 1)) * width
  const y = height - ((minVal - minVal) / range) * (height - 50) - 25
  
  return { x, y }
})

// Запускаем бэктест при монтировании компонента
onMounted(() => {
  runBacktest()
})
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 24px 32px;
  max-width: 1400px; margin: 0 auto;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

/* ============================================
   GLASS COMPONENTS
   ============================================ */
.glass-card {
  border-radius: 20px; overflow: hidden;
  background: rgba(30, 32, 40, 0.4);
  backdrop-filter: blur(30px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.4);
}

.panel-full { height: 100%; display: flex; flex-direction: column; padding: 20px; }

/* ============================================
   CONTROLS
   ============================================ */
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.glass-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px;
  height: 36px;
}

.lbl-mini {
  font-size: 11px;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
}

.glass-segmented-control {
  background: rgba(255,255,255,0.05); border-radius: 10px; padding: 4px; display: flex; gap: 4px;
  border: 1px solid rgba(255,255,255,0.05);
}
.seg-btn {
  background: transparent; border: none; color: rgba(255,255,255,0.6);
  padding: 6px 14px; font-size: 12px; font-weight: 600; border-radius: 8px; cursor: pointer; transition: all 0.2s;
}
.seg-btn:hover { color: #fff; }
.seg-btn.active { background: rgba(255,255,255,0.1); color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }

/* ============================================
   KPI GRID
   ============================================ */
.kpi-cards-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.kpi-card { padding: 20px; display: flex; flex-direction: column; justify-content: space-between; min-height: 110px; }
.kpi-label { font-size: 11px; text-transform: uppercase; color: rgba(255,255,255,0.5); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 700; font-family: "SF Mono", monospace; line-height: 1.1; letter-spacing: -0.02em; color: #fff; }
.kpi-change { font-size: 12px; margin-top: 8px; display: flex; align-items: center; gap: 4px; }

/* ============================================
   CHART
   ============================================ */
.chart-panel { padding: 24px; min-height: 320px; display: flex; flex-direction: column; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.ph-left { display: flex; align-items: center; gap: 12px; }
.panel-header h3 { margin: 0; font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.9); }

.badge-live { font-size: 10px; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-weight: 700; }

.chart-legend { display: flex; gap: 16px; }
.legend-item { font-size: 12px; color: rgba(255,255,255,0.6); display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.strategy { background: #4ade80; box-shadow: 0 0 8px rgba(74, 222, 128, 0.4); }
.dot.benchmark { background: rgba(255,255,255,0.3); }

.chart-container { flex: 1; width: 100%; position: relative; }
.main-svg { width: 100%; height: 100%; filter: drop-shadow(0 0 20px rgba(74, 222, 128, 0.1)); }

/* ============================================
   DASHBOARD SPLIT
   ============================================ */
.dashboard-grid { display: grid; grid-template-columns: 3fr 2fr; gap: 24px; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 24px; }

/* ============================================
   HEATMAP
   ============================================ */
.table-wrapper { overflow-x: auto; flex: 1; }
.heatmap-table { width: 100%; border-collapse: separate; border-spacing: 6px; font-size: 12px; }
.col-month { text-align: left; color: rgba(255,255,255,0.4); font-weight: 600; font-size: 10px; width: 40px; }
.col-year { text-align: center; color: rgba(255,255,255,0.4); padding-bottom: 8px; font-weight: 600; font-size: 11px; }
.col-val { text-align: center; }

.val-pill {
  padding: 6px 2px; border-radius: 6px; font-family: "SF Mono", monospace; font-size: 11px; font-weight: 500;
  transition: transform 0.1s; cursor: default;
}
.val-pill:hover { transform: scale(1.1); z-index: 2; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }

.bg-green-strong { background: #15803d; color: #fff; }
.bg-green-soft { background: rgba(21, 128, 61, 0.4); color: #86efac; }
.bg-neutral { background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.4); }
.bg-red-soft { background: rgba(185, 28, 28, 0.4); color: #fca5a5; }
.bg-red-strong { background: #b91c1c; color: #fff; }

.row-total td { padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); }

/* ============================================
   STATS & DRAWDOWNS
   ============================================ */
.stats-grid-mini { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.stat-box {
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
  border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 4px;
}
.stat-box .lbl { font-size: 10px; color: rgba(255,255,255,0.5); text-transform: uppercase; font-weight: 600; }
.stat-box .val { font-family: "SF Mono", monospace; font-weight: 600; font-size: 14px; color: #fff; }

.drawdown-list { display: flex; flex-direction: column; gap: 12px; }
.dd-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px; background: rgba(255,255,255,0.02); border-radius: 10px;
}
.dd-info { display: flex; flex-direction: column; gap: 2px; }
.dd-period { font-size: 12px; color: #fff; font-weight: 500; }
.dd-rec { font-size: 10px; color: rgba(255,255,255,0.4); }

.dd-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.dd-val { font-family: "SF Mono", monospace; font-weight: 700; font-size: 13px; }
.dd-bar-bg { width: 60px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; }
.dd-bar-fill { height: 100%; background: #f87171; }

/* UTILS */
.text-gradient-green { background: linear-gradient(135deg, #4ade80, #22c55e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-gradient-blue { background: linear-gradient(135deg, #60a5fa, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.text-red { color: #f87171; }
.text-green { color: #4ade80; }
.text-blue { color: #60a5fa; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-white { color: #fff; }
.font-bold { font-weight: 700; }

@media (max-width: 1200px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .kpi-cards-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
    gap: 16px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .section-title {
    font-size: 22px;
  }
  
  .section-subtitle {
    font-size: 12px;
  }
  
  .glass-segmented-control {
    width: 100%;
    overflow-x: auto;
  }
  
  .kpi-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-card {
    min-height: 90px;
    padding: 16px;
  }
  
  .kpi-value {
    font-size: 24px;
  }
  
  .chart-panel {
    padding: 16px;
    min-height: 250px;
  }
  
  .panel-full {
    padding: 16px;
  }
  
  .table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
    gap: 12px;
  }
  
  .section-title {
    font-size: 20px;
  }
  
  .section-subtitle {
    font-size: 11px;
  }
  
  .kpi-value {
    font-size: 20px;
  }
  
  .chart-panel {
    min-height: 200px;
    padding: 12px;
  }
  
  .panel-full {
    padding: 12px;
  }
  
  .heatmap-table {
    font-size: 10px;
  }
  
  .val-pill {
    font-size: 9px;
    padding: 4px 2px;
  }
}
</style>