<template>
  <BaseWidget
    title="WAVE_σ.9"
    icon="WaveIcon"
    icon-bg="bg-orange-500/20"
    icon-color="text-orange-400"
    :width="width"
    :height="height"
    :resizable="resizable"
    :show-controls="showControls"
    @settings="$emit('settings')"
    @remove="$emit('remove')"
    @resize="handleResize"
  >
    <div class="flex h-full">
      <!-- 3D Canvas (2/3) -->
      <div class="flex-[2] relative border-r border-white/5">
        <!-- Header Overlay -->
        <div class="absolute top-0 left-0 p-3 z-10 pointer-events-none">
          <p class="text-[10px] text-gray-400 font-mono border-l-2 border-orange-500 pl-2">
            Regime:
            <span :class="regime === 'TRENDING' ? 'text-green-400 font-bold' : 'text-red-400 font-bold'">
              {{ regime }}
            </span>
          </p>
        </div>

        <!-- 3D Container -->
        <div ref="canvasRef" class="w-full h-full"></div>
      </div>

      <!-- Control Panel (1/3) -->
      <div class="flex-1 bg-gradient-to-b from-[#0a0a0a] to-black flex flex-col">
        <!-- Header -->
        <div class="p-2 border-b border-white/10 bg-black/50 flex justify-between items-center">
          <div>
            <div class="text-[8px] text-gray-500 font-mono uppercase tracking-widest">Output</div>
            <div class="flex items-center gap-1">
              <div class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
              <span class="text-[10px] font-bold text-white">LIVE</span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-[8px] text-gray-500 font-mono uppercase tracking-widest">Backtest</div>
            <div class="font-mono text-xs text-cyan-400">{{ formatElapsed }}</div>
          </div>
        </div>

        <!-- Charts -->
        <div class="flex-1 flex flex-col p-2 gap-2 overflow-hidden">
          <!-- Position Chart -->
          <div class="flex-1 bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-2 min-h-0">
            <div class="flex justify-between items-center mb-1">
              <h3 class="text-[8px] font-mono font-bold text-orange-400 uppercase tracking-widest">Position</h3>
              <span class="text-[8px] text-gray-500 font-mono">-1 : 1</span>
            </div>
            <div ref="positionChartRef" class="w-full h-[calc(100%-16px)]"></div>
          </div>

          <!-- Equity Chart -->
          <div class="flex-1 bg-black/40 backdrop-blur-md border border-white/10 rounded-lg p-2 min-h-0">
            <div class="flex justify-between items-center mb-1">
              <h3 class="text-[8px] font-mono font-bold text-cyan-400 uppercase tracking-widest">Equity</h3>
              <span class="text-[8px] text-gray-500 font-mono">Rolling</span>
            </div>
            <div ref="equityChartRef" class="w-full h-[calc(100%-16px)]"></div>
          </div>
        </div>

        <!-- Stats Footer -->
        <div class="p-2 border-t border-white/10 bg-[#080808]">
          <div class="flex justify-between items-center mb-2">
            <div class="text-[8px] text-gray-500 font-mono uppercase tracking-widest">Equity</div>
            <div :class="`font-mono text-sm ${equity > 1000 ? 'text-green-400' : 'text-red-400'}`">
              ${{ equity.toFixed(2) }}
            </div>
          </div>
          <div class="grid grid-cols-2 gap-1 text-[8px] font-mono text-gray-500">
            <div class="flex justify-between border border-white/5 p-1 rounded">
              <span>SHARPE</span>
              <span class="text-white">2.1</span>
            </div>
            <div class="flex justify-between border border-white/5 p-1 rounded">
              <span>VOL</span>
              <span class="text-white">15%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseWidget>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import BaseWidget from './BaseWidget.vue'
import { useWaveSigma3D } from '@/composables/waveSigma/useWaveSigma3D'
import { MarketRegime, SimulationData } from '@/composables/waveSigma/types'

interface Props {
  width?: number
  height?: number
  resizable?: boolean
  showControls?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: 6,
  height: 4,
  resizable: true,
  showControls: true
})

const emit = defineEmits<{
  settings: []
  remove: []
  resize: [width: number, height: number]
}>()

// Refs
const canvasRef = ref<HTMLElement | null>(null)
const positionChartRef = ref<HTMLElement | null>(null)
const equityChartRef = ref<HTMLElement | null>(null)

// State
const width = ref(props.width)
const height = ref(props.height)
const regime = ref<MarketRegime>(MarketRegime.TRENDING)
const equity = ref(1000)
const elapsedDays = ref(0)
const simData = ref<SimulationData[]>([])

// Charts
let positionChart: echarts.ECharts | null = null
let equityChart: echarts.ECharts | null = null

// 3D Renderer
const { init, dispose, setRegime, resize } = useWaveSigma3D()

// Refs for signal handling
const dataRef = ref<SimulationData[]>([])
const lastUpdateRef = ref(0)
const startTimeRef = ref(Date.now())

// Computed
const formatElapsed = computed(() => {
  const years = Math.floor(elapsedDays.value / 365)
  const days = elapsedDays.value % 365
  return years > 0 ? `${years}Y ${days}D` : `${days}D`
})

// Handle signal from 3D surface
const handleSignal = (rawSignal: number, _volatility: number) => {
  const now = performance.now()
  if (now - lastUpdateRef.value < 50) return
  lastUpdateRef.value = now

  let position = 0
  if (regime.value === MarketRegime.TRENDING) {
    position = rawSignal > 0.2 ? 1 : rawSignal < -0.2 ? -1 : 0
  } else {
    position = rawSignal > 0.5 ? 0.5 : rawSignal < -0.5 ? -0.5 : Math.random() - 0.5
  }

  const pnl =
    Math.abs(position) * (regime.value === MarketRegime.TRENDING ? 1.5 : -2.0) + (Math.random() * 2 - 1)

  const newEquity = equity.value + pnl
  equity.value = newEquity

  const newDataPoint: SimulationData = {
    position: position,
    equity: newEquity,
    price: 0,
    timestamp: now
  }

  const currentHistory = dataRef.value
  const newHistory = [...currentHistory.slice(1), newDataPoint]
  dataRef.value = newHistory
  simData.value = newHistory

  updateCharts()
}

// Initialize charts
const initCharts = () => {
  if (positionChartRef.value) {
    positionChart = echarts.init(positionChartRef.value)
    positionChart.setOption({
      animation: false,
      grid: {
        top: 5,
        right: 5,
        bottom: 15,
        left: 5
      },
      xAxis: {
        type: 'category',
        show: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          show: true,
          color: '#444',
          fontSize: 8,
          interval: 14,
          formatter: (_: string, index: number) => `-${((60 - index) * 0.05).toFixed(1)}s`
        },
        data: Array(60)
          .fill(0)
          .map((_, i) => i)
      },
      yAxis: {
        type: 'value',
        min: -1.2,
        max: 1.2,
        show: false,
        splitLine: { show: false }
      },
      series: [
        {
          type: 'line',
          step: 'end',
          data: [],
          lineStyle: { color: '#ff9f43', width: 1.5 },
          showSymbol: false,
          markLine: {
            silent: true,
            data: [{ yAxis: 0 }],
            lineStyle: { color: '#222', type: 'solid' },
            label: { show: false },
            symbol: 'none'
          }
        }
      ]
    })
  }

  if (equityChartRef.value) {
    equityChart = echarts.init(equityChartRef.value)
    equityChart.setOption({
      animation: false,
      grid: {
        top: 5,
        right: 5,
        bottom: 15,
        left: 5
      },
      xAxis: {
        type: 'category',
        show: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          show: true,
          color: '#444',
          fontSize: 8,
          interval: 14,
          formatter: (_: string, index: number) => `-${((60 - index) * 0.05).toFixed(1)}s`
        },
        data: Array(60)
          .fill(0)
          .map((_, i) => i)
      },
      yAxis: {
        type: 'value',
        show: false,
        splitLine: { show: false }
      },
      series: [
        {
          type: 'line',
          smooth: true,
          data: [],
          lineStyle: { color: '#00d2d3', width: 2 },
          showSymbol: false,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0, 210, 211, 0.2)' },
              { offset: 1, color: 'rgba(0, 210, 211, 0)' }
            ])
          }
        }
      ]
    })
  }
}

// Update charts with new data
const updateCharts = () => {
  const visibleData = simData.value.slice(-60)

  if (positionChart) {
    positionChart.setOption({
      series: [
        {
          data: visibleData.map((d) => d.position)
        }
      ]
    })
  }

  if (equityChart) {
    equityChart.setOption({
      series: [
        {
          data: visibleData.map((d) => d.equity)
        }
      ]
    })
  }
}

// Handle resize
const handleResize = (w: number, h: number) => {
  width.value = w
  height.value = h
  emit('resize', w, h)

  nextTick(() => {
    resize()
    positionChart?.resize()
    equityChart?.resize()
  })
}

// Regime switching interval
let regimeInterval: ReturnType<typeof setInterval> | null = null

// Elapsed time interval
let elapsedInterval: ReturnType<typeof setInterval> | null = null

// Initialize
onMounted(() => {
  // Initialize data
  const initialData: SimulationData[] = Array(60)
    .fill(0)
    .map((_, i) => ({
      position: 0,
      equity: 1000,
      price: 100,
      timestamp: i
    }))
  dataRef.value = initialData
  simData.value = initialData

  // Initialize 3D renderer
  nextTick(() => {
    if (canvasRef.value) {
      init(canvasRef.value, handleSignal)
    }

    // Initialize charts
    initCharts()
    updateCharts()
  })

  // Regime switching every 8 seconds
  regimeInterval = setInterval(() => {
    const newRegime =
      regime.value === MarketRegime.TRENDING ? MarketRegime.CHOPPY : MarketRegime.TRENDING
    regime.value = newRegime
    setRegime(newRegime)
  }, 8000)

  // Elapsed time (1 real second = 7 market days)
  elapsedInterval = setInterval(() => {
    const realElapsedSeconds = (Date.now() - startTimeRef.value) / 1000
    elapsedDays.value = Math.floor(realElapsedSeconds * 7)
  }, 100)

  // Handle window resize
  window.addEventListener('resize', handleWindowResize)
})

const handleWindowResize = () => {
  resize()
  positionChart?.resize()
  equityChart?.resize()
}

// Cleanup
onUnmounted(() => {
  if (regimeInterval) clearInterval(regimeInterval)
  if (elapsedInterval) clearInterval(elapsedInterval)

  dispose()

  positionChart?.dispose()
  equityChart?.dispose()

  window.removeEventListener('resize', handleWindowResize)
})

// Watch for prop changes
watch(
  () => props.width,
  (newWidth) => {
    width.value = newWidth
  }
)

watch(
  () => props.height,
  (newHeight) => {
    height.value = newHeight
  }
)

// Icons
const WaveIcon = {
  template:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12c1.5-3 3-5 5-5s3.5 2 5 5 3 5 5 5 3.5-2 5-5"/></svg>'
}
</script>
