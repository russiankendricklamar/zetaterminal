<!-- src/pages/VolatilitySurface.vue -->
<template>
  <div class="volatility-surface-page">
    
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Volatility Surface</h1>
        <p class="page-subtitle">3D поверхность волатильности: Моненость × Срок × IV</p>
      </div>
      
      <div class="header-right">
        <!-- Instrument -->
        <div class="control-group">
          <label class="control-label">Инструмент:</label>
          <select v-model="selectedInstrument" class="instrument-select" @change="regenerateSurface">
            <option value="spy">SPY (Equity Index)</option>
            <option value="eur">EUR/USD (FX)</option>
            <option value="brent">Brent Oil</option>
            <option value="rates">USD Rates</option>
          </select>
        </div>

        <!-- Show Grid -->
        <div class="control-group checkbox">
          <input type="checkbox" v-model="showGrid" @change="updateSurface" id="grid-check" />
          <label for="grid-check">Grid</label>
        </div>

        <!-- Show Wireframe -->
        <div class="control-group checkbox">
          <input type="checkbox" v-model="showWireframe" @change="updateSurface" id="wire-check" />
          <label for="wire-check">Wireframe</label>
        </div>

        <!-- Animation Toggle -->
        <button @click="toggleAnimation" class="btn-primary">
          {{ animating ? '⏸ Стоп' : '▶ Вращение' }}
        </button>

        <!-- Reset View -->
        <button @click="resetCamera" class="btn-secondary">🔄 Reset</button>
      </div>
    </div>

    <!-- 3D Canvas -->
    <div class="three-d-container">
      <canvas ref="threeCanvas" class="three-canvas"></canvas>
      <div class="controls-overlay">
        <div class="controls-hint">
          <p>🖱 Drag to rotate | Scroll to zoom | Right-click to pan</p>
        </div>
      </div>
    </div>

    <div class="axes-labels">
      <div class="axis-label x-label">X: Strike (%)</div>
      <div class="axis-label y-label">Y: IV (%)</div>
      <div class="axis-label z-label">Z: Tenor</div>
    </div>

    <!-- Statistics & Info -->
    <div class="grid-4">
      <div class="stat-card">
        <div class="stat-header">
          <h3>ATM Volatility</h3>
          <span class="stat-unit">Волатильность ATM</span>
        </div>
        <div class="stat-value accent">{{ (atmVol * 100).toFixed(2) }}%</div>
        <div class="stat-detail">
          <span class="label">3M</span>
          <span class="value">{{ (atmVol3M * 100).toFixed(2) }}%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <h3>Skew (25 Delta)</h3>
          <span class="stat-unit">Асимметрия улыбки</span>
        </div>
        <div class="stat-value" :class="skew25 >= 0 ? 'positive' : 'negative'">
          {{ skew25 >= 0 ? '+' : '' }}{{ (skew25 * 100).toFixed(2) }}%
        </div>
        <div class="stat-detail">
          <span class="label">Put - Call</span>
          <span class="value">{{ skewDelta25 >= 0 ? '+' : '' }}{{ (skewDelta25 * 100).toFixed(1) }}%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <h3>Term Structure</h3>
          <span class="stat-unit">Структура по срокам</span>
        </div>
        <div class="stat-value cyan">
          {{ (termSlope * 100).toFixed(2) }}%
        </div>
        <div class="stat-detail">
          <span class="label">1M vs 12M</span>
          <span class="value">{{ termTrend }}</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-header">
          <h3>Vol of Vol</h3>
          <span class="stat-unit">Волатильность волатильности</span>
        </div>
        <div class="stat-value green">{{ (volOfVol * 100).toFixed(2) }}%</div>
        <div class="stat-detail">
          <span class="label">Realized</span>
          <span class="value">{{ (realizedVolOfVol * 100).toFixed(2) }}%</span>
        </div>
      </div>
    </div>

    <!-- Surface Details Table -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Volatility Surface Matrix</h3>
        <span class="card-subtitle">Таблица IV по страйкам и срокам</span>
      </div>
      <div class="surface-matrix-container">
        <table class="surface-matrix-table">
          <thead>
            <tr>
              <th class="header-label">Strike / Term</th>
              <th v-for="tenor in tenors" :key="tenor">{{ tenor }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="strike in strikes" :key="strike">
              <td class="strike-label">{{ ((strike - 1) * 100).toFixed(0) }}%</td>
              <td 
                v-for="tenor in tenors" 
                :key="tenor"
                class="vol-cell"
                :style="{ backgroundColor: getVolColor(getVolForStrikeTenor(strike, tenor)) }"
              >
                <span class="vol-value">{{ (getVolForStrikeTenor(strike, tenor) * 100).toFixed(1) }}%</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Volatility Slices -->
    <div class="grid-2">
      <!-- Smile by Term -->
      <div class="card">
        <div class="chart-header">
          <h3>Volatility Smile (by Tenor)</h3>
          <span class="chart-subtitle">Кривая улыбки для разных сроков</span>
        </div>
        <div class="chart-container">
          <canvas ref="smileChartRef"></canvas>
        </div>
      </div>

      <!-- Term Structure -->
      <div class="card">
        <div class="chart-header">
          <h3>Term Structure (by Moneyness)</h3>
          <span class="chart-subtitle">Временная структура для разных страйков</span>
        </div>
        <div class="chart-container">
          <canvas ref="termChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- 2D Heatmap -->
    <div class="card full-width">
      <div class="chart-header">
        <h3>2D Heatmap: Strike × Tenor</h3>
        <span class="chart-subtitle">Тепловая карта волатильности</span>
      </div>
      <div class="chart-container tall">
        <canvas ref="heatmapChartRef"></canvas>
      </div>
    </div>

    <!-- Greeks Surface -->
    <div class="grid-2">
      <!-- Vega Surface -->
      <div class="card">
        <div class="chart-header">
          <h3>Vega (by Strike & Tenor)</h3>
          <span class="chart-subtitle">Чувствительность к волатильности</span>
        </div>
        <div class="chart-container">
          <canvas ref="vegaChartRef"></canvas>
        </div>
      </div>

      <!-- Vol Convexity -->
      <div class="card">
        <div class="chart-header">
          <h3>Volatility Convexity</h3>
          <span class="chart-subtitle">Кривизна поверхности</span>
        </div>
        <div class="chart-container">
          <canvas ref="convexityChartRef"></canvas>
        </div>
      </div>
    </div>

    <!-- Info Panel -->
    <div class="card full-width">
      <div class="card-header">
        <h3>Surface Model Details</h3>
        <span class="card-subtitle">Технические параметры модели</span>
      </div>
      <div class="info-grid">
        <div class="info-item">
          <span class="label">Model Type</span>
          <span class="value">SABR + Local Vol</span>
        </div>
        <div class="info-item">
          <span class="label">Calibration</span>
          <span class="value">Least Squares + Regularization</span>
        </div>
        <div class="info-item">
          <span class="label">Last Updated</span>
          <span class="value">{{ updateTime }}</span>
        </div>
        <div class="info-item">
          <span class="label">Market Close</span>
          <span class="value">{{ marketStatus }}</span>
        </div>
        <div class="info-item">
          <span class="label">Spot Price</span>
          <span class="value mono">{{ spotPrice }}</span>
        </div>
        <div class="info-item">
          <span class="label">Risk-free Rate</span>
          <span class="value mono">{{ (riskFreeRate * 100).toFixed(2) }}%</span>
        </div>
        <div class="info-item">
          <span class="label">Dividend Yield</span>
          <span class="value mono">{{ (dividendYield * 100).toFixed(2) }}%</span>
        </div>
        <div class="info-item">
          <span class="label">Repo Rate</span>
          <span class="value mono">{{ (repoRate * 100).toFixed(2) }}%</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="page-footer">
      <span>• Source: Bloomberg Terminal / Broker Data</span>
      <span>• Frequency: Real-time Updates</span>
      <span>• Last Sync: 15s ago</span>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import * as THREE from 'three'

/* --- CONTROLS & STATE --- */
const selectedInstrument = ref('spy')
const showGrid = ref(true)
const showWireframe = ref(false)
const animating = ref(false)

const threeCanvas = ref<HTMLCanvasElement | null>(null)
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let mesh: THREE.Mesh | null = null
let animationId: number | null = null

/* --- MOCK DATA PARAMS --- */
const tenors = ['1M', '3M', '6M', '1Y', '2Y', '3Y']
const strikes = [0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3]

const spotPrice = ref('4850.25')
const atmVol = ref(0.158)
const atmVol3M = ref(0.162)
const skew25 = ref(-0.035)
const skewDelta25 = ref(-0.025)
const termSlope = ref(0.008)
const termTrend = ref('Upward')
const volOfVol = ref(0.068)
const realizedVolOfVol = ref(0.045)

const riskFreeRate = ref(0.0425)
const dividendYield = ref(0.018)
const repoRate = ref(0.041)
const updateTime = ref('14:35:22 UTC')
const marketStatus = ref('LIVE')

/* --- CHART REFS --- */
const smileChartRef = ref<HTMLCanvasElement | null>(null)
const termChartRef = ref<HTMLCanvasElement | null>(null)
const heatmapChartRef = ref<HTMLCanvasElement | null>(null)
const vegaChartRef = ref<HTMLCanvasElement | null>(null)
const convexityChartRef = ref<HTMLCanvasElement | null>(null)

let charts: { [key: string]: Chart | null } = {}

/* --- VOLATILITY SURFACE FUNCTION --- */
const generateVolatilitySurface = (instrumentType: string): number[][] => {
  const data: number[][] = []
  
  // SABR-like model parameters
  let alpha = 0.15
  let beta = 0.8
  let rho = -0.3
  let nu = 0.4

  if (instrumentType === 'eur') {
    alpha = 0.08
    nu = 0.25
    rho = -0.15
  } else if (instrumentType === 'brent') {
    alpha = 0.35
    rho = 0.1
    nu = 0.5
  } else if (instrumentType === 'rates') {
    alpha = 0.012
    beta = 0.5
    rho = -0.5
    nu = 0.35
  }

  for (let i = 0; i < strikes.length; i++) {
    const row: number[] = []
    const strike = strikes[i]
    const moneyness = Math.log(strike)
    
    for (let j = 0; j < tenors.length; j++) {
      const tenorYears = [1/12, 0.25, 0.5, 1, 2, 3][j]
      
      // Simplified SABR formula
      const sqrtT = Math.sqrt(tenorYears)
      const f = 1.0
      
      // ATM vol (alpha * beta term)
      let atmVol = alpha * Math.pow(f, beta - 1)
      
      // Smile (skew) term
      const smileTerm = Math.pow(f * strike, (beta - 1) / 2) * 
        Math.sinh(rho * Math.acosh(Math.sqrt((alpha / nu) * (alpha / nu) + 1)))
      
      const smile = moneyness < 0 
        ? 1 + (-0.4) * moneyness // put skew
        : 1 + (-0.2) * moneyness  // call skew
      
      // Term structure
      const termFactor = 1 + 0.05 * (1 - tenorYears)
      
      // Vol of vol smile
      const volvol = 1 + Math.abs(moneyness) * 0.15
      
      const vol = atmVol * smile * termFactor * volvol / sqrtT
      row.push(Math.max(0.05, Math.min(1.0, vol)))
    }
    data.push(row)
  }
  
  return data
}

let volSurfaceData: number[][] = generateVolatilitySurface('spy')

const getVolForStrikeTenor = (strike: number, tenor: string): number => {
  const strikeIdx = strikes.indexOf(strike)
  const tenorIdx = tenors.indexOf(tenor)
  if (strikeIdx >= 0 && tenorIdx >= 0) {
    return volSurfaceData[strikeIdx][tenorIdx]
  }
  return 0.15
}

const getVolColor = (vol: number): string => {
  if (vol < 0.1) return 'rgba(74, 222, 128, 0.7)'
  if (vol < 0.15) return 'rgba(96, 165, 250, 0.7)'
  if (vol < 0.2) return 'rgba(245, 158, 11, 0.7)'
  if (vol < 0.25) return 'rgba(248, 113, 113, 0.7)'
  return 'rgba(239, 68, 68, 0.7)'
}

/* --- THREE.JS INITIALIZATION --- */
const initThreeJS = () => {
  if (!threeCanvas.value) return

  const width = threeCanvas.value.clientWidth
  const height = threeCanvas.value.clientHeight

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0f1419)

  // Camera
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(12, 12, 0)
  camera.lookAt(0, 0, 0)

  // Renderer
  renderer = new THREE.WebGLRenderer({ 
    canvas: threeCanvas.value, 
    antialias: true, 
    alpha: true 
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 15, 10)
  scene.add(directionalLight)

  // Build surface geometry
  buildSurface()

  // Orbit controls-like behavior
  setupControls()

  // Animation loop
  const animate = () => {
    animationId = requestAnimationFrame(animate)
    
    if (animating.value && mesh) {
      mesh.rotation.y += 0.003
    }
    
    renderer?.render(scene as THREE.Scene, camera as THREE.PerspectiveCamera)
  }
  animate()
}

let sceneContainer: THREE.Group | null = null

const buildSurface = () => {
  if (!scene) return
  
  if (sceneContainer) {
    scene.remove(sceneContainer)
  }

  // Создаём контейнер, в который поместим ВСЁ
  sceneContainer = new THREE.Group()
  sceneContainer.name = 'sceneContainer'

  // Create geometry
  const geometry = new THREE.BufferGeometry()
  const vertices: number[] = []
  const indices: number[] = []
  const colors: number[] = []

  // Generate vertices
  for (let i = 0; i < strikes.length; i++) {
    for (let j = 0; j < tenors.length; j++) {
      const x = (i / strikes.length - 0.5) * 10
      const y = volSurfaceData[i][j] * 15
      const z = (j / tenors.length - 0.5) * 8

      vertices.push(x, y, z)

      // Color based on vol
      const vol = volSurfaceData[i][j]
      if (vol < 0.1) {
        colors.push(0.29, 0.87, 0.50) // green
      } else if (vol < 0.15) {
        colors.push(0.38, 0.65, 1.0) // blue
      } else if (vol < 0.2) {
        colors.push(0.96, 0.62, 0.04) // orange
      } else {
        colors.push(0.97, 0.44, 0.44) // red
      }
    }
  }

  // Generate indices
  for (let i = 0; i < strikes.length - 1; i++) {
    for (let j = 0; j < tenors.length - 1; j++) {
      const a = i * tenors.length + j
      const b = a + 1
      const c = (i + 1) * tenors.length + j
      const d = c + 1

      indices.push(a, b, c)
      indices.push(b, d, c)
    }
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vertices), 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(colors), 3))
  geometry.setIndex(new THREE.BufferAttribute(new Uint32Array(indices), 1))
  geometry.computeVertexNormals()

  // Material
  const material = new THREE.MeshPhongMaterial({
    vertexColors: true,
    wireframe: showWireframe.value,
    flatShaping: false,
    emissive: 0x1a1a1a,
    shininess: 30
  })

  mesh = new THREE.Mesh(geometry, material)
  sceneContainer.add(mesh)

  // Add grid if enabled
  if (showGrid.value) {
    const gridHelper = new THREE.GridHelper(12, 12, 0x444444, 0x222222)
    gridHelper.position.y = -0.5
    sceneContainer.add(gridHelper)
  }

  // Create axes и добавь их в КОНТЕЙНЕР
  createAxes(sceneContainer)

  // Добавь контейнер в сцену
  scene!.add(sceneContainer)
}

const createAxes = (container: THREE.Group) => {
  const axesGroup = new THREE.Group()
  axesGroup.name = 'axesGroup'

  // Оси на углу плоскости XZ, ВЫШЕ на оси Y
  const offset = new THREE.Vector3(-6, 0, -6)  // ← ВЫШЕ (Y = -2.8)
  axesGroup.position.copy(offset)

  const axesLength = 12
  const arrowSize = 0.3
  const lineWidth = 3

  const whiteColor = 0xffffff
  const lineMaterial = new THREE.LineBasicMaterial({ color: whiteColor, linewidth: lineWidth })

  // ===== X-AXIS (Strike) - Вправо =====
  const xGeometry = new THREE.BufferGeometry()
  xGeometry.setAttribute(
    'position',
    new THREE.BufferAttribute(
      new Float32Array([0, 0, 0, axesLength, 0, 0]),
      3
    )
  )
  const xLine = new THREE.Line(xGeometry, lineMaterial)
  axesGroup.add(xLine)

  // X arrow
  const xArrowGeometry = new THREE.ConeGeometry(arrowSize * 0.35, arrowSize, 8)
  const xArrowMaterial = new THREE.MeshBasicMaterial({ color: whiteColor })
  const xArrow = new THREE.Mesh(xArrowGeometry, xArrowMaterial)
  xArrow.position.set(axesLength + 0.15, 0, 0)
  xArrow.rotation.z = -Math.PI / 2
  axesGroup.add(xArrow)

  // ===== Y-AXIS (Volatility) - Вверх =====
  const yGeometry = new THREE.BufferGeometry()
  yGeometry.setAttribute(
    'position',
    new THREE.BufferAttribute(
      new Float32Array([0, 0, 0, 0, axesLength, 0]),
      3
    )
  )
  const yLine = new THREE.Line(yGeometry, lineMaterial)
  axesGroup.add(yLine)

  // Y arrow
  const yArrowGeometry = new THREE.ConeGeometry(arrowSize * 0.35, arrowSize, 8)
  const yArrowMaterial = new THREE.MeshBasicMaterial({ color: whiteColor })
  const yArrow = new THREE.Mesh(yArrowGeometry, yArrowMaterial)
  yArrow.position.set(0, axesLength + 0.15, 0)
  axesGroup.add(yArrow)

  // ===== Z-AXIS (Tenor) - Назад (ЛЕВАЯ ТРОЙКА) =====
  const zGeometry = new THREE.BufferGeometry()
  zGeometry.setAttribute(
    'position',
    new THREE.BufferAttribute(
      new Float32Array([0, 0, 0, 0, 0, axesLength]),
      3
    )
  )
  const zLine = new THREE.Line(zGeometry, lineMaterial)
  axesGroup.add(zLine)

  // Z arrow
  const zArrowGeometry = new THREE.ConeGeometry(arrowSize * 0.35, arrowSize, 8)
  const zArrowMaterial = new THREE.MeshBasicMaterial({ color: whiteColor })
  const zArrow = new THREE.Mesh(zArrowGeometry, zArrowMaterial)
  zArrow.position.set(0, 0, axesLength - 0.15)
  zArrow.rotation.x = Math.PI / 2
  axesGroup.add(zArrow)

  // Origin point
  const originGeometry = new THREE.SphereGeometry(0.12, 12, 12)
  const originMaterial = new THREE.MeshBasicMaterial({ color: whiteColor })
  const origin = new THREE.Mesh(originGeometry, originMaterial)
  axesGroup.add(origin)

  container.add(axesGroup)
}

// Helper function для создания текстуры с подписью
const createLabelCanvas = (text: string, fontSize: number): HTMLCanvasElement => {
  const canvas = document.createElement('canvas')
  canvas.width = 128
  canvas.height = 128
  
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#ffffff'
  ctx.font = `bold ${fontSize}px Arial`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  
  const lines = text.split('\n')
  lines.forEach((line, idx) => {
    ctx.fillText(line, 64, 50 + idx * 30)
  })
  
  return canvas
}

const setupControls = () => {
  if (!threeCanvas.value || !camera || !sceneContainer) return

  let isDragging = false
  let previousMousePosition = { x: 0, y: 0 }
  let rotation = { x: 0, y: 0 }

  threeCanvas.value.addEventListener('mousedown', (e) => {
    isDragging = true
    previousMousePosition = { x: e.clientX, y: e.clientY }
  })

  threeCanvas.value.addEventListener('mousemove', (e) => {
    if (isDragging && sceneContainer) {  // ← Вращаем КОНТЕЙНЕР!
      const deltaX = e.clientX - previousMousePosition.x
      const deltaY = e.clientY - previousMousePosition.y

      rotation.y += deltaX * 0.005
      //rotation.x += deltaY * 0.005

      sceneContainer.rotation.y = rotation.y
      sceneContainer.rotation.x = rotation.x

      const panSpeed = 0.01
      camera.position.y -= deltaY * panSpeed

      previousMousePosition = { x: e.clientX, y: e.clientY }
    }
  })

  threeCanvas.value.addEventListener('mouseup', () => {
    isDragging = false
  })

  threeCanvas.value.addEventListener('wheel', (e) => {
    e.preventDefault()
    const zoomSpeed = 0.1
    if (e.deltaY > 0) {
      camera!.position.multiplyScalar(1 + zoomSpeed)
    } else {
      camera!.position.multiplyScalar(1 - zoomSpeed)
    }
  })
}

const regenerateSurface = () => {
  volSurfaceData = generateVolatilitySurface(selectedInstrument.value)
  buildSurface()
  buildCharts()
}

const updateSurface = () => {
  buildSurface()
}

const resetCamera = () => {
  if (camera && mesh) {
    camera.position.set(5, 8, 8)
    camera.lookAt(0, 0, 0)
    mesh.rotation.set(0, 0, 0)
  }
}

const toggleAnimation = () => {
  animating.value = !animating.value
}

/* --- CHART BUILDERS --- */
const buildCharts = () => {
  buildSmileChart()
  buildTermChart()
  buildHeatmapChart()
  buildVegaChart()
  buildConvexityChart()
}

const buildSmileChart = () => {
  if (!smileChartRef.value) return
  const ctx = smileChartRef.value.getContext('2d')
  if (!ctx) return

  charts.smile?.destroy()

  const labels = strikes.map(s => ((s - 1) * 100).toFixed(0) + '%')
  const datasets = [
    {
      label: '1M',
      data: volSurfaceData.map(row => row[0] * 100),
      borderColor: '#60a5fa',
      backgroundColor: 'rgba(96,165,250,0.1)',
      tension: 0.4
    },
    {
      label: '6M',
      data: volSurfaceData.map(row => row[2] * 100),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245,158,11,0.1)',
      tension: 0.4
    },
    {
      label: '2Y',
      data: volSurfaceData.map(row => row[4] * 100),
      borderColor: '#ec4899',
      backgroundColor: 'rgba(236,72,153,0.1)',
      tension: 0.4
    }
  ]

  charts.smile = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
      }
    }
  })
}

const buildTermChart = () => {
  if (!termChartRef.value) return
  const ctx = termChartRef.value.getContext('2d')
  if (!ctx) return

  charts.term?.destroy()

  const datasets = [
    {
      label: 'ITM 80%',
      data: volSurfaceData[1].map(v => v * 100),
      borderColor: '#4ade80',
      tension: 0.3
    },
    {
      label: 'ATM',
      data: volSurfaceData[4].map(v => v * 100),
      borderColor: '#fbbf24',
      tension: 0.3
    },
    {
      label: 'OTM 120%',
      data: volSurfaceData[7].map(v => v * 100),
      borderColor: '#f87171',
      tension: 0.3
    }
  ]

  charts.term = new Chart(ctx, {
    type: 'line',
    data: { labels: tenors, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: 'rgba(255,255,255,0.6)' } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
      }
    }
  })
}

const buildHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  const ctx = heatmapChartRef.value.getContext('2d')
  if (!ctx) return

  charts.heatmap?.destroy()

  const heatmapData = []
  for (let i = 0; i < strikes.length; i++) {
    for (let j = 0; j < tenors.length; j++) {
      heatmapData.push({
        x: j,
        y: i,
        v: volSurfaceData[i][j] * 100
      })
    }
  }

  charts.heatmap = new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: [{
        label: 'IV',
        data: heatmapData.map(d => ({
          x: d.x,
          y: d.y,
          r: d.v / 2
        })),
        backgroundColor: heatmapData.map(d => {
          const v = d.v
          if (v < 10) return 'rgba(74,222,128,0.8)'
          if (v < 15) return 'rgba(96,165,250,0.8)'
          if (v < 20) return 'rgba(245,158,11,0.8)'
          return 'rgba(248,113,113,0.8)'
        })
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { min: -0.5, max: 5.5, grid: { display: false }, ticks: { color: 'rgba(255,255,255,0.3)' } },
        y: { min: -0.5, max: 8.5, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: 'rgba(255,255,255,0.3)' } }
      }
    }
  })
}

const buildVegaChart = () => {
  if (!vegaChartRef.value) return
  const ctx = vegaChartRef.value.getContext('2d')
  if (!ctx) return

  charts.vega?.destroy()

  const labels = strikes.map(s => ((s - 1) * 100).toFixed(0) + '%')
  const vega6M = volSurfaceData.map((row, i) => {
    const T = 0.5
    const S = 1.0
    const K = strikes[i]
    const sigma = row[2]
    // Vega ≈ S * sqrt(T) * n(d1)
    const d1 = (Math.log(S / K) + 0.5 * sigma * sigma * T) / (sigma * Math.sqrt(T))
    const norm = (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * d1 * d1)
    return S * Math.sqrt(T) * norm * 100
  })

  charts.vega = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Vega (6M)',
        data: vega6M,
        backgroundColor: 'rgba(96,165,250,0.6)',
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
  })
}

const buildConvexityChart = () => {
  if (!convexityChartRef.value) return
  const ctx = convexityChartRef.value.getContext('2d')
  if (!ctx) return

  charts.convexity?.destroy()

  const labels = strikes.map(s => ((s - 1) * 100).toFixed(0) + '%')
  const convexity = volSurfaceData.map((row, i) => {
    // Approximation: second derivative of IV w.r.t. moneyness
    const left = i > 0 ? volSurfaceData[i - 1][2] : row[2]
    const right = i < strikes.length - 1 ? volSurfaceData[i + 1][2] : row[2]
    return (left - 2 * row[2] + right) * 10000
  })

  charts.convexity = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Convexity',
        data: convexity,
        borderColor: '#ec4899',
        backgroundColor: 'rgba(236,72,153,0.1)',
        tension: 0.3,
        pointRadius: 3
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
  })
}

/* --- LIFECYCLE --- */
onMounted(async () => {
  await nextTick()
  initThreeJS()
  buildCharts()
})

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId)
  Object.values(charts).forEach(c => c?.destroy())
  renderer?.dispose()
})
</script>

<style scoped>
.volatility-surface-page {
  width: 100%;
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(180deg, rgba(15,20,25,0.5) 0%, rgba(26,31,46,0.3) 100%);
  color: #fff;
}

/* header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  gap: 24px;
  flex-wrap: wrap;
}
.header-left { flex: 1; min-width: 300px; }
.page-title { font-size: 28px; font-weight: 700; margin: 0 0 8px; letter-spacing: -0.01em; }
.page-subtitle { font-size: 13px; color: rgba(255,255,255,0.5); margin: 0; }

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(255,255,255,0.04);
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.08);
}

.control-group.checkbox {
  padding: 6px 10px;
}

.control-label {
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  white-space: nowrap;
}

.control-group.checkbox input {
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.control-group.checkbox label {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  cursor: pointer;
  margin: 0;
}

.instrument-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  outline: none;
  cursor: pointer;
}

.instrument-select option {
  background: #1e1f28;
  color: #fff;
}

.btn-primary,
.btn-secondary {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
  box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.btn-primary:hover { background: #2563eb; transform: translateY(-1px); }

.btn-secondary {
  background: rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.8);
  border: 1px solid rgba(255,255,255,0.2);
}

.btn-secondary:hover { background: rgba(255,255,255,0.15); }

/* 3D Canvas */
.three-d-container {
  position: relative;
  width: 100%;
  height: 600px;
  background: rgba(10,15,20,0.6);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  overflow: hidden;
  margin-bottom: 24px;
}

.three-canvas {
  display: block;
  width: 100%;
  height: 100%;
}

.controls-overlay {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: rgba(0,0,0,0.5);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 10px;
  color: rgba(255,255,255,0.6);
  pointer-events: none;
}

/* grids */
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.full-width { grid-column: 1/-1; }

/* stat cards */
.stat-card {
  background: rgba(30,32,40,0.4);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  padding: 16px;
}

.stat-header h3 {
  font-size: 11px;
  text-transform: uppercase;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.stat-unit {
  font-size: 9px;
  color: rgba(255,255,255,0.35);
}

.stat-value {
  margin-top: 8px;
  font-size: 18px;
  font-weight: 700;
  font-family: "SF Mono", monospace;
}

.stat-value.accent { color: #f59e0b; }
.stat-value.green { color: #4ade80; }
.stat-value.cyan { color: #06b6d4; }
.stat-value.positive { color: #4ade80; }
.stat-value.negative { color: #f87171; }

.stat-detail {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  border-top: 1px solid rgba(255,255,255,0.05);
  margin-top: 6px;
  padding-top: 4px;
}

.stat-detail .label { color: rgba(255,255,255,0.5); }
.stat-detail .value { color: rgba(255,255,255,0.8); }

/* cards */
.card {
  background: rgba(30,32,40,0.4);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08);
  padding: 20px;
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.card-subtitle {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  margin-top: 4px;
}

/* matrix table */
.surface-matrix-container { overflow-x: auto; }

.surface-matrix-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.surface-matrix-table th,
.surface-matrix-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  text-align: center;
}

.surface-matrix-table th {
  background: rgba(255,255,255,0.02);
  color: rgba(255,255,255,0.5);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 9px;
}

.header-label {
  text-align: right;
  font-weight: 600;
}

.strike-label {
  text-align: right;
  color: rgba(255,255,255,0.7);
  font-weight: 600;
  min-width: 50px;
}

.vol-cell {
  position: relative;
  font-weight: 600;
}

.vol-value {
  position: relative;
  z-index: 2;
  color: #000;
  font-weight: 700;
  font-size: 9px;
}

/* charts */
.chart-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 10px;
}

.chart-header h3 {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  margin: 0;
}

.chart-subtitle {
  font-size: 10px;
  color: rgba(255,255,255,0.35);
}

.chart-container {
  position: relative;
  height: 280px;
  background: rgba(15,23,42,0.45);
  border-radius: 12px;
  border: 1px solid rgba(107,114,128,0.12);
  padding: 12px;
}

.chart-container.tall { height: 380px; }

.axes-labels {
  position: absolute;
  bottom: 20px;
  left: 20px;
  font-size: 11px;
  color: rgba(255,255,255,0.7);
  font-family: "SF Mono", monospace;
  pointer-events: none;
}

.axis-label {
  margin: 4px 0;
  padding: 4px 8px;
  background: rgba(0,0,0,0.4);
  border-radius: 4px;
  border-left: 2px solid rgba(255,255,255,0.6);
}

.x-label { border-left-color: rgba(255,255,255,0.8); }
.y-label { border-left-color: rgba(255,255,255,0.8); }
.z-label { border-left-color: rgba(255,255,255,0.8); }

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* info grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.info-item {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  font-size: 11px;
}

.info-item .label {
  color: rgba(255,255,255,0.6);
  font-weight: 600;
}

.info-item .value {
  color: rgba(255,255,255,0.8);
  font-family: "SF Mono", monospace;
}

.mono { font-family: "SF Mono", monospace; }

/* footer */
.page-footer {
  margin-top: 24px;
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 11px;
  color: rgba(255,255,255,0.35);
  flex-wrap: wrap;
}

/* responsive */
@media (max-width: 1200px) {
  .grid-4 { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 900px) {
  .page-header { flex-direction: column; }
  .header-right { width: 100%; flex-direction: column; }
  .control-group { width: 100%; }
  .grid-4 { grid-template-columns: 1fr; }
  .grid-2 { grid-template-columns: 1fr; }
  .three-d-container { height: 400px; }
}
</style>
