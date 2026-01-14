<template>
  <div class="page-container custom-scroll">
    
    <!-- Header -->
    <div class="section-header">
      <div class="header-left">
        <h1 class="section-title">Детальный анализ режимов</h1>
        <p class="section-subtitle">Метрики устойчивости, матрицы переходов и сценарное прогнозирование</p>
      </div>
      <div class="header-actions">
         <div class="glass-pill status-pill">
            <span class="status-label text-muted">Данные: <b class="text-white">01.11.2025</b></span>
         </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-container">
        <div class="spinner-large"></div>
        <p>Загрузка данных режимов...</p>
    </div>

    <!-- 1. KEY METRICS CARDS -->
    <div v-else class="grid-3 mb-6">
        <div 
            v-for="(stat, i) in regimeStats" 
            :key="i"
            :class="['glass-card regime-card', `border-${getRegimeColor(i)}`]"
        >
            <div class="card-head">
                <span :class="['dot', `bg-${getRegimeColor(i)}`]"></span>
                <h3>Состояние {{ i }}: {{ getRegimeName(i) }}</h3>
            </div>
            <div class="card-body">
                <p class="desc">{{ getRegimeDescription(i) }}</p>
                <div class="metrics-table" v-if="getRegimeStats(i)">
                    <div class="m-row">
                        <span>Количество дней</span> 
                        <strong>{{ getRegimeStats(i)!.days }}</strong>
                    </div>
                    <div class="m-row">
                        <span>Доля периода</span> 
                        <strong>{{ (getRegimeStats(i)!.frequency * 100).toFixed(1) }}%</strong>
                    </div>
                    <div class="m-row">
                        <span>Ср. доходность</span> 
                        <strong :class="getRegimeStats(i)!.meanReturn >= 0 ? 'text-green' : 'text-red'">
                            {{ (getRegimeStats(i)!.meanReturn * 100).toFixed(3) }}%
                        </strong>
                    </div>
                    <div class="m-row">
                        <span>Волатильность</span> 
                        <strong>{{ (getRegimeStats(i)!.volatility * 100).toFixed(3) }}%</strong>
                    </div>
                    <div class="m-row">
                        <span>Устойчивость</span> 
                        <strong>{{ getRegimeStats(i)!.persistence.toFixed(4) }}</strong>
                    </div>
                    <div class="m-row">
                        <span>Ожид. длительность</span> 
                        <strong>{{ getRegimeStats(i)!.duration ? getRegimeStats(i)!.duration.toFixed(1) + ' дня' : '∞' }}</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 2. TRANSITION & STATIONARY ANALYSIS -->
    <div class="grid-2 mb-6">
        
        <!-- Transition Matrix Heatmap -->
        <div class="glass-card panel">
            <div class="panel-header">
                <h3>Матрица переходов</h3>
            </div>
            <div class="heatmap-container">
                <div class="heatmap-grid" v-if="transitionMatrix">
                    <div class="h-label">От \ К</div>
                    <div 
                        v-for="j in transitionMatrix.length" 
                        :key="j"
                        :class="['h-col-header', `text-${getRegimeColor(j-1)}`]"
                    >
                        {{ getRegimeName(j-1).substring(0, 6) }}
                    </div>

                    <template v-for="(row, i) in transitionMatrix" :key="i">
                        <div :class="['h-row-header', `text-${getRegimeColor(i)}`]">
                            {{ getRegimeName(i).substring(0, 6) }}
                        </div>
                        <div 
                            v-for="(prob, j) in row" 
                            :key="j"
                            class="h-cell"
                            :style="{ background: `rgba(${getRegimeColorRgb(j)}, ${prob * 0.8})` }"
                        >
                            {{ prob.toFixed(2) }}
                        </div>
                    </template>
                </div>
                <div class="analysis-note mt-4">
                    <p>• <strong>Стабильность</strong> имеет наивысшую инерцию (0.96).<br>• Из <strong>Падения</strong> выход в Рост (25%) вероятнее, чем в Стабильность (8%).</p>
                </div>
            </div>
        </div>

        <!-- Stationary Distribution & Forecast -->
        <div class="glass-card panel flex-col">
            <div class="panel-header">
                <h3>Прогноз вероятностей</h3>
                <span class="sub-label">Начальное состояние: <b>Рост</b></span>
            </div>
            
            <div class="table-wrapper">
                <table class="glass-table">
                    <thead v-if="transitionMatrix">
                        <tr>
                            <th class="text-left pl-2">Горизонт</th>
                            <th 
                                v-for="(stat, i) in regimeStats" 
                                :key="i"
                                :class="[`text-${getRegimeColor(i)}`, 'text-right']"
                            >
                                P({{ getRegimeName(i).substring(0, 4) }})
                            </th>
                        </tr>
                    </thead>
                    <tbody v-if="transitionMatrix && stationaryDistribution.length > 0">
                        <tr v-for="horizon in [1, 5, 10]" :key="horizon">
                            <td class="pl-2">{{ horizon }} {{ horizon === 1 ? 'день' : 'дней' }}</td>
                            <td 
                                v-for="(prob, i) in computeForecast(horizon)" 
                                :key="i"
                                class="text-right"
                            >
                                {{ (prob * 100).toFixed(1) }}%
                            </td>
                        </tr>
                        <tr class="stationary">
                            <td class="pl-2 text-orange font-bold">∞ (Долгосрочный)</td>
                            <td 
                                v-for="(prob, i) in stationaryDistribution" 
                                :key="i"
                                class="text-right font-bold text-orange"
                            >
                                {{ (prob * 100).toFixed(1) }}%
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="chart-mini mt-4">
                <div class="chart-label-sm">Сходимость к стационарному состоянию</div>
                <svg viewBox="0 0 400 60" class="svg-curves">
                     <!-- Simplified curves showing convergence -->
                     <path d="M0,50 Q100,45 200,30 T400,10" fill="none" stroke="#3b82f6" stroke-width="2"/>
                     <path d="M0,10 Q100,20 200,30 T400,45" fill="none" stroke="#4ade80" stroke-width="2"/>
                     <line x1="0" y1="10" x2="400" y2="10" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4"/>
                     <line x1="0" y1="50" x2="400" y2="50" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4"/>
                </svg>
            </div>
        </div>

    </div>

    <!-- 3. VISUALIZATION: HISTOGRAMS & COMPARISON -->
    <div class="grid-2 mb-6">
        
        <!-- Distribution Histograms -->
        <div class="glass-card panel">
            <div class="panel-header">
                <h3>Распределение доходностей по режимам</h3>
            </div>
            <div class="chart-container-rect">
                <svg viewBox="0 0 600 250" class="svg-chart">
                    <!-- Axes -->
                    <line x1="50" y1="220" x2="550" y2="220" stroke="rgba(255,255,255,0.1)" />
                    <line x1="300" y1="20" x2="300" y2="220" stroke="rgba(255,255,255,0.1)" stroke-dasharray="4" /> <!-- Zero line -->

                    <!-- Stability (Blue) - Narrow, Tall, Centered -->
                    <path d="M150,220 Q300,-100 450,220" fill="rgba(59, 130, 246, 0.1)" stroke="#3b82f6" stroke-width="2" />
                    
                    <!-- Decline (Red) - Wide, Shifted Left -->
                    <path d="M50,220 Q200,50 400,220" fill="rgba(248, 113, 113, 0.1)" stroke="#f87171" stroke-width="2" />
                    
                    <!-- Growth (Green) - Shifted Right -->
                    <path d="M200,220 Q380,50 500,220" fill="rgba(74, 222, 128, 0.1)" stroke="#4ade80" stroke-width="2" />
                    
                    <!-- Labels -->
                    <text x="310" y="30" fill="#3b82f6" font-size="10" font-weight="600">Стабильность (Низкая σ)</text>
                    <text x="100" y="100" fill="#f87171" font-size="10" font-weight="600">Падение (Отрицательная μ)</text>
                    <text x="450" y="100" fill="#4ade80" font-size="10" font-weight="600">Рост (Положительная μ)</text>
                </svg>
            </div>
            <p class="chart-caption">Распределение изменений доходностей. Режим «Падение» имеет "толстый хвост" слева.</p>
        </div>

        <!-- Comparative Bars -->
        <div class="glass-card panel">
             <div class="panel-header">
                <h3>Характеристики режимов (Волатильность vs Доходность)</h3>
            </div>
             <div class="chart-container-rect">
                <svg viewBox="0 0 500 250" class="svg-chart">
                    <!-- Bar Groups -->
                    <!-- Stability -->
                    <rect x="50" y="150" width="40" height="50" fill="#3b82f6" opacity="0.8" rx="4" /> <!-- Vol -->
                    <rect x="100" y="195" width="40" height="5" fill="#3b82f6" opacity="0.3" rx="4" /> <!-- Ret -->
                    
                    <!-- Decline -->
                    <rect x="200" y="50" width="40" height="150" fill="#f87171" opacity="0.8" rx="4" /> <!-- Vol High -->
                    <rect x="250" y="200" width="40" height="40" fill="#f87171" opacity="0.3" rx="4" /> <!-- Ret Negative (down) -->
                    
                    <!-- Growth -->
                    <rect x="350" y="100" width="40" height="100" fill="#4ade80" opacity="0.8" rx="4" /> <!-- Vol Med -->
                    <rect x="400" y="160" width="40" height="40" fill="#4ade80" opacity="0.3" rx="4" /> <!-- Ret Positive -->

                    <!-- Labels -->
                    <text x="95" y="240" fill="rgba(255,255,255,0.6)" text-anchor="middle" font-size="12">Стабильность</text>
                    <text x="245" y="240" fill="rgba(255,255,255,0.6)" text-anchor="middle" font-size="12">Падение</text>
                    <text x="395" y="240" fill="rgba(255,255,255,0.6)" text-anchor="middle" font-size="12">Рост</text>

                    <!-- Legend -->
                    <rect x="340" y="20" width="10" height="10" fill="#fff" opacity="0.8" rx="2" /> <text x="360" y="30" fill="#fff" font-size="10">Волатильность (σ)</text>
                    <rect x="340" y="40" width="10" height="10" fill="#fff" opacity="0.3" rx="2" /> <text x="360" y="50" fill="#fff" font-size="10">Доходность (|μ|)</text>
                </svg>
            </div>
        </div>

    </div>
    
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { getRegimeStatistics, getTransitionMatrix, getChartData } from '@/services/multivariateHmmService'

const portfolioStore = usePortfolioStore()

const regimeStats = ref<any[]>([])
const transitionMatrix = ref<number[][] | null>(null)
const chartData = ref<any[]>([])
const isLoading = ref(true)

// Загружаем данные при монтировании компонента
onMounted(async () => {
    try {
        const [statsResponse, matrixResponse, chartResponse] = await Promise.all([
            getRegimeStatistics(),
            getTransitionMatrix(),
            getChartData()
        ])
        
        regimeStats.value = statsResponse.statistics
        transitionMatrix.value = matrixResponse.transition_matrix
        chartData.value = chartResponse.data
        
        isLoading.value = false
    } catch (e) {
        console.error('Ошибка загрузки данных режимов:', e)
        isLoading.value = false
    }
})

// Вычисляем стационарное распределение из матрицы переходов
const stationaryDistribution = computed(() => {
    if (!transitionMatrix.value) return []
    
    // Используем метод степеней для вычисления стационарного распределения
    let pi = Array(transitionMatrix.value.length).fill(1 / transitionMatrix.value.length)
    
    for (let i = 0; i < 100; i++) {
        const newPi = transitionMatrix.value[0].map((_, j) => 
            pi.reduce((sum, p, k) => sum + p * transitionMatrix.value![k][j], 0)
        )
        const sum = newPi.reduce((a, b) => a + b, 0)
        pi = newPi.map(p => p / sum)
    }
    
    return pi
})

// Вычисляем ожидаемую длительность режимов
const expectedDurations = computed(() => {
    if (!transitionMatrix.value) return []
    
    return transitionMatrix.value.map((row, i) => {
        const persistence = row[i]
        if (persistence >= 1) return null
        return 1 / (1 - persistence)
    })
})

// Получаем статистику для режима
const getRegimeStats = (regimeId: number) => {
    if (!regimeStats.value[regimeId]) return null
    
    const stat = regimeStats.value[regimeId]
    const daysInRegime = chartData.value.filter(d => d.regime === regimeId).length
    const totalDays = chartData.value.length
    const frequency = daysInRegime / totalDays
    
    return {
        days: daysInRegime,
        frequency: frequency,
        meanReturn: stat.mean.reduce((a: number, b: number) => a + b, 0) / stat.mean.length,
        volatility: stat.volatility_per_asset.reduce((a: number, b: number) => a + b, 0) / stat.volatility_per_asset.length,
        persistence: stat.persistence,
        duration: stat.duration_days
    }
}

// Получаем название режима
const getRegimeName = (regimeId: number) => {
    const names = ['Стабильность', 'Падение', 'Рост', 'Коррекция', 'Восстановление']
    return names[regimeId] || `Режим ${regimeId}`
}

// Получаем цвет режима
const getRegimeColor = (regimeId: number) => {
    const colors = ['blue', 'red', 'green', 'orange', 'purple']
    return colors[regimeId % colors.length]
}

// Получаем описание режима
const getRegimeDescription = (regimeId: number) => {
    const descriptions = [
        'Динамическое равновесие без ярко выраженного направления. Рынок стабилизируется, волатильность минимальна.',
        'Фаза понижательного тренда с высокой волатильностью. "Липкое" состояние с короткими отскоками.',
        'Периоды возрастающего тренда. Систематический рост стоимости активов с умеренными колебаниями.',
        'Коррекционная фаза после роста. Умеренное снижение с сохранением общей тенденции.',
        'Фаза восстановления после падения. Постепенный возврат к равновесию.'
    ]
    return descriptions[regimeId] || 'Режим рыночной активности'
}

// Получаем RGB цвет для режима
const getRegimeColorRgb = (regimeId: number) => {
    const colors = [
        '59, 130, 246',  // blue
        '248, 113, 113', // red
        '74, 222, 128',  // green
        '251, 191, 36',  // orange
        '168, 85, 247'   // purple
    ]
    return colors[regimeId % colors.length]
}

// Вычисляем прогноз на горизонт дней
const computeForecast = (horizon: number) => {
    if (!transitionMatrix.value || !transitionMatrix.value.length) return []
    
    // Начальное состояние: последний режим из данных
    const lastRegime = chartData.value.length > 0 
        ? chartData.value[chartData.value.length - 1].regime 
        : 0
    
    let state = Array(transitionMatrix.value.length).fill(0)
    state[lastRegime] = 1
    
    // Умножаем на матрицу переходов horizon раз
    for (let i = 0; i < horizon; i++) {
        const newState = Array(transitionMatrix.value.length).fill(0)
        for (let j = 0; j < transitionMatrix.value.length; j++) {
            for (let k = 0; k < transitionMatrix.value.length; k++) {
                newState[j] += state[k] * transitionMatrix.value[k][j]
            }
        }
        state = newState
    }
    
    return state
}
</script>

<style scoped>
/* ============================================
   PAGE LAYOUT
   ============================================ */
.page-container {
  display: flex; flex-direction: column; gap: 24px; padding: 24px 32px 60px 32px;
  max-width: 1400px; margin: 0 auto; min-height: 100vh;
}

.section-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 4px; }
.section-title { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -0.01em; }
.section-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 4px 0 0 0; }

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
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.glass-card:hover {
  background: rgba(40, 45, 55, 0.5);
  border-color: rgba(255, 255, 255, 0.12);
}

.glass-pill {
  display: flex; align-items: center; gap: 8px; padding: 4px 12px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 99px; height: 36px;
}

/* Grids */
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.grid-2 { display: grid; grid-template-columns: 3fr 2fr; gap: 24px; }

/* Panels */
.panel { display: flex; flex-direction: column; }
.panel-header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.panel-header h3 { margin: 0; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(255,255,255,0.8); }
.sub-label { font-size: 11px; color: rgba(255,255,255,0.5); }

/* Regime Cards */
.regime-card { position: relative; border-top: 2px solid transparent; transition: transform 0.2s; }
.regime-card:hover { transform: translateY(-2px); background: rgba(30, 32, 40, 0.6); }
.regime-card.border-blue { border-color: #3b82f6; }
.regime-card.border-red { border-color: #f87171; }
.regime-card.border-green { border-color: #4ade80; }

.card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.card-head h3 { margin: 0; font-size: 16px; font-weight: 700; color: #fff; }
.desc { font-size: 12px; color: rgba(255,255,255,0.6); line-height: 1.5; margin-bottom: 20px; height: 36px; }

/* Metrics Table */
.metrics-table { display: flex; flex-direction: column; gap: 8px; }
.m-row { display: flex; justify-content: space-between; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; }
.m-row span { color: rgba(255,255,255,0.5); font-weight: 500; }
.m-row strong { font-family: "SF Mono", monospace; color: #fff; }

/* Heatmap */
.heatmap-container { display: flex; flex-direction: column; align-items: center; }
.heatmap-grid { display: grid; grid-template-columns: 60px repeat(3, 1fr); gap: 4px; width: 100%; }
.h-label { font-size: 10px; color: rgba(255,255,255,0.3); grid-column: 1; grid-row: 1; display: flex; align-items: center; justify-content: center; }
.h-col-header { text-align: center; font-size: 11px; font-weight: 700; padding: 8px; text-transform: uppercase; }
.h-row-header { display: flex; align-items: center; justify-content: flex-end; padding-right: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.h-cell { display: flex; align-items: center; justify-content: center; height: 44px; border-radius: 6px; font-family: "SF Mono", monospace; font-weight: 700; color: #fff; font-size: 13px; text-shadow: 0 1px 2px rgba(0,0,0,0.5); }

/* Analysis Note */
.analysis-note { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; font-size: 12px; color: rgba(255,255,255,0.6); line-height: 1.5; width: 100%; margin-top: 16px; border: 1px solid rgba(255,255,255,0.05); }

/* Forecast Table */
.table-wrapper { width: 100%; overflow-x: auto; }
.glass-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.glass-table th { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); opacity: 0.8; font-weight: 600; }
.glass-table td { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: "SF Mono", monospace; color: #fff; }
.stationary td { font-weight: 700; border-top: 1px solid rgba(255,255,255,0.1); border-bottom: none; padding-top: 16px; }

/* Mini Chart */
.chart-mini { background: rgba(0,0,0,0.2); border-radius: 12px; padding: 12px; border: 1px solid rgba(255,255,255,0.05); margin-top: auto; }
.chart-label-sm { font-size: 10px; color: rgba(255,255,255,0.4); margin-bottom: 4px; text-transform: uppercase; }
.svg-curves { width: 100%; height: 60px; }

/* SVG Charts */
.chart-container-rect { width: 100%; height: 250px; position: relative; }
.svg-chart { width: 100%; height: 100%; }
.chart-caption { font-size: 11px; color: rgba(255,255,255,0.4); text-align: center; margin-top: 8px; font-style: italic; }

/* Utility */
.dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 8px currentColor; }
.bg-blue { background: #3b82f6; color: #3b82f6; } .text-blue { color: #3b82f6; }
.bg-red { background: #f87171; color: #f87171; } .text-red { color: #f87171; }
.bg-green { background: #4ade80; color: #4ade80; } .text-green { color: #4ade80; }
.text-orange { color: #fbbf24; }
.text-white { color: #fff; }
.text-muted { color: rgba(255,255,255,0.4); }
.text-right { text-align: right; }
.text-left { text-align: left; }
.pl-2 { padding-left: 8px; }
.font-bold { font-weight: 700; }
.mb-6 { margin-bottom: 24px; }
.flex-col { display: flex; flex-direction: column; }
.loading-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 400px; gap: 16px; }
.spinner-large { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 1200px) {
  .grid-3 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
}
</style>