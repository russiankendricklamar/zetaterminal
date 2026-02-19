import { ref, computed, watch, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import type { HJBResponse } from '../../services/hjbService'

export interface PathPoint3D {
  x: number
  y: number
  z: number
  isJump?: boolean
}

export interface SimulationResult3D {
  paths: PathPoint3D[][]
  jumps: PathPoint3D[]
  stats: {
    meanFinalPrice: number
    maxPrice: number
    minPrice: number
    stdDev: number
  }
}

export interface SimulationConfig3D {
  initialPrice: number
  drift: number
  volatility: number
  timeSteps: number
  numPaths: number
  dt: number
  jumpIntensity: number
  jumpMean: number
  jumpSd: number
}

export function useMonteCarlo3D(
  hjbParams: Ref<{
    expectedReturn: number
    marketVol: number
    monteCarloTrajectories: number
  }>,
  trajectoriesDays: Ref<number>,
  initialPrice: Ref<number>
) {
  const trajectories3DCanvas = ref<HTMLCanvasElement | null>(null)
  let scene3D: THREE.Scene | null = null
  let camera3D: THREE.PerspectiveCamera | null = null
  let renderer3D: THREE.WebGLRenderer | null = null
  let controls3D: any = null
  let animationId3D: number | null = null
  const currentStep3D = ref(0)
  let cameraPositioned = false
  const simulationResult3D = ref<SimulationResult3D | null>(null)
  const trajectories3DLines: THREE.Line[] = []
  let cachedScaleParams: { scaleX: number; scaleY: number; scaleZ: number; stats: any; boxWidth: number; boxDepth: number } | null = null

  const isPlaying3D = ref(false)
  const playbackStep3D = ref(0)
  let animationFrame3D: number | null = null

  let gridObjects: THREE.Group[] = []
  let axisLabels: THREE.Sprite[] = []

  const maxStep3D = computed(() => {
    if (!simulationResult3D.value || !simulationResult3D.value.paths.length) return 0
    return simulationResult3D.value.paths[0].length - 1
  })

  const formatPercent = (value: number): string => {
    return (value * 100).toFixed(2) + '%'
  }

  const getPortfolioReturns = (): number[] => {
    if (!simulationResult3D.value || !simulationResult3D.value.paths.length) return []
    const paths = simulationResult3D.value.paths
    const returns: number[] = []
    const initPrice = paths[0]?.[0]?.y || 1000000

    for (const path of paths) {
      if (path.length > 0) {
        const finalPrice = path[path.length - 1].y
        returns.push((finalPrice / initPrice) - 1)
      }
    }
    return returns
  }

  const averageReturn = computed(() => {
    const returns = getPortfolioReturns()
    if (returns.length === 0) return 0
    return returns.reduce((sum, r) => sum + r, 0) / returns.length
  })

  const medianReturn = computed(() => {
    const returns = getPortfolioReturns()
    if (returns.length === 0) return 0
    const sorted = [...returns].sort((a, b) => a - b)
    const mid = Math.floor(sorted.length / 2)
    return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
  })

  const sharpeRatio = computed(() => {
    const returns = getPortfolioReturns()
    if (returns.length === 0) return 0
    const mean = averageReturn.value
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
    const stdDev = Math.sqrt(variance)
    const simulationDays = trajectoriesDays.value || 252
    const years = simulationDays / 252
    const annualMean = mean / years
    const annualStdDev = stdDev / Math.sqrt(years)
    if (annualStdDev === 0) return 0
    return annualMean / annualStdDev
  })

  const var95 = computed(() => {
    const returns = getPortfolioReturns()
    if (returns.length === 0) return 0
    const sorted = [...returns].sort((a, b) => a - b)
    return sorted[Math.floor(sorted.length * 0.05)] || 0
  })

  const cvar95 = computed(() => {
    const returns = getPortfolioReturns()
    if (returns.length === 0) return 0
    const sorted = [...returns].sort((a, b) => a - b)
    const varIndex = Math.floor(sorted.length * 0.05)
    const tailReturns = sorted.slice(0, varIndex + 1)
    if (tailReturns.length === 0) return 0
    return tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length
  })

  const averageMDD = computed(() => {
    if (!simulationResult3D.value || !simulationResult3D.value.paths.length) return 0
    const paths = simulationResult3D.value.paths
    const mddValues: number[] = []
    for (const path of paths) {
      if (path.length === 0) continue
      let peak = path[0].y
      let maxDrawdown = 0
      for (const point of path) {
        if (point.y > peak) peak = point.y
        const drawdown = (peak - point.y) / peak
        if (drawdown > maxDrawdown) maxDrawdown = drawdown
      }
      mddValues.push(maxDrawdown)
    }
    if (mddValues.length === 0) return 0
    return mddValues.reduce((sum, mdd) => sum + mdd, 0) / mddValues.length
  })

  const runMonteCarlo3D = (config: SimulationConfig3D): SimulationResult3D => {
    const { initialPrice: initPrice, drift, volatility, timeSteps, numPaths, dt, jumpIntensity, jumpMean, jumpSd } = config
    const paths: PathPoint3D[][] = []
    const allJumps: PathPoint3D[] = []
    let totalFinalPrice = 0
    let maxPrice = -Infinity
    let minPrice = Infinity
    const finalPrices: number[] = []

    for (let i = 0; i < numPaths; i++) {
      const path: PathPoint3D[] = []
      let currentPrice = initPrice
      path.push({ x: 0, y: currentPrice, z: i })

      for (let t = 1; t <= timeSteps; t++) {
        const u1 = Math.random()
        const u2 = Math.random()
        const z = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2)
        let diffusion = (drift - 0.5 * volatility * volatility) * dt + volatility * Math.sqrt(dt) * z

        let jumpMultiplier = 1
        let isJumpStep = false

        if (Math.random() < jumpIntensity * dt) {
          isJumpStep = true
          const jU1 = Math.random()
          const jU2 = Math.random()
          const jZ = Math.sqrt(-2.0 * Math.log(jU1)) * Math.cos(2.0 * Math.PI * jU2)
          jumpMultiplier = Math.exp(jumpMean + jumpSd * jZ)
        }

        currentPrice = currentPrice * Math.exp(diffusion) * jumpMultiplier
        const point: PathPoint3D = { x: t, y: currentPrice, z: i, isJump: isJumpStep }
        path.push(point)
        if (isJumpStep) allJumps.push(point)
        maxPrice = Math.max(maxPrice, currentPrice)
        minPrice = Math.min(minPrice, currentPrice)
      }

      paths.push(path)
      totalFinalPrice += currentPrice
      finalPrices.push(currentPrice)
    }

    const meanFinalPrice = totalFinalPrice / numPaths
    const variance = finalPrices.reduce((acc, p) => acc + Math.pow(p - meanFinalPrice, 2), 0) / numPaths

    return {
      paths,
      jumps: allJumps,
      stats: { meanFinalPrice, maxPrice, minPrice, stdDev: Math.sqrt(variance) }
    }
  }

  const createAxisLabelSprite = (text: string, position: THREE.Vector3, size: number = 8): THREE.Sprite => {
    const canvas = document.createElement('canvas')
    canvas.width = 6144
    canvas.height = 3072
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#ffffff'
    ctx.strokeStyle = '#000000'
    ctx.lineWidth = 24
    ctx.font = `bold ${600}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.strokeText(text, 3072, 1536)
    ctx.fillText(text, 3072, 1536)

    const texture = new THREE.CanvasTexture(canvas)
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture })
    const sprite = new THREE.Sprite(spriteMaterial)
    sprite.scale.set(size, size / 2, 1)
    sprite.position.copy(position)
    return sprite
  }

  const update3DGrids = (stats: any, scaleX: number, scaleY: number, scaleZ: number, boxWidth: number, boxDepth: number) => {
    if (!scene3D) return

    gridObjects.forEach(grid => {
      if (scene3D) scene3D.remove(grid)
      grid.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          child.geometry.dispose()
          if (child.material instanceof THREE.Material) child.material.dispose()
        }
      })
    })
    gridObjects.length = 0

    axisLabels.forEach(sprite => {
      if (scene3D) scene3D.remove(sprite)
      if (sprite.material instanceof THREE.SpriteMaterial) {
        sprite.material.map?.dispose()
        sprite.material.dispose()
      }
    })
    axisLabels.length = 0

    const boxHeight = (stats.maxPrice - stats.minPrice) * scaleY * 1.2
    const gridGroup = new THREE.Group()

    const createGrid = (w: number, h: number, axis: 'xz' | 'xy' | 'yz') => {
      const g = new THREE.Group()
      const cellSize = 50
      const sectionSize = 250
      const lineMat = new THREE.LineBasicMaterial({ color: 0x0088aa, opacity: 0.3, transparent: true })
      const secMat = new THREE.LineBasicMaterial({ color: 0x003344, opacity: 0.5, transparent: true })

      for (let i = 0; i <= w; i += cellSize) {
        const isSec = i % sectionSize === 0
        const mat = isSec ? secMat : lineMat
        const pts = axis === 'xz' ? [new THREE.Vector3(i, 0, 0), new THREE.Vector3(i, 0, h)]
          : axis === 'xy' ? [new THREE.Vector3(i, 0, 0), new THREE.Vector3(i, h, 0)]
          : [new THREE.Vector3(0, 0, i), new THREE.Vector3(0, h, i)]
        g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat))
      }

      for (let i = 0; i <= h; i += cellSize) {
        const isSec = i % sectionSize === 0
        const mat = isSec ? secMat : lineMat
        const pts = axis === 'xz' ? [new THREE.Vector3(0, 0, i), new THREE.Vector3(w, 0, i)]
          : axis === 'xy' ? [new THREE.Vector3(0, i, 0), new THREE.Vector3(w, i, 0)]
          : [new THREE.Vector3(0, i, 0), new THREE.Vector3(0, i, w)]
        g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), mat))
      }
      return g
    }

    gridGroup.add(createGrid(boxWidth, boxDepth, 'xz'))
    gridGroup.add(createGrid(boxWidth, boxHeight, 'xy'))
    gridGroup.add(createGrid(boxDepth, boxHeight, 'yz'))

    // Axes
    const axesMat = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 3 })
    const tickMat = new THREE.LineBasicMaterial({ color: 0xaaaaaa, opacity: 0.8, transparent: true })
    const tickSize = Math.max(boxWidth, boxDepth, boxHeight) * 0.03
    const cellSize = 50
    const sectionSize = 250

    // X axis
    gridGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(boxWidth, 0, 0)]), axesMat))
    for (let x = 0; x <= boxWidth; x += cellSize) {
      const isSec = x % sectionSize === 0
      const tl = isSec ? tickSize * 1.5 : tickSize
      gridGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(x, -tl, 0), new THREE.Vector3(x, tl, 0)]), isSec ? axesMat : tickMat))
    }

    // Y axis
    gridGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, boxHeight, 0)]), axesMat))
    for (let y = 0; y <= boxHeight; y += cellSize) {
      const isSec = y % sectionSize === 0
      const tl = isSec ? tickSize * 1.5 : tickSize
      gridGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-tl, y, 0), new THREE.Vector3(tl, y, 0)]), isSec ? axesMat : tickMat))
    }

    // Z axis
    gridGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, boxDepth)]), axesMat))
    for (let z = 0; z <= boxDepth; z += cellSize) {
      const isSec = z % sectionSize === 0
      const tl = isSec ? tickSize * 1.5 : tickSize
      gridGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-tl, 0, z), new THREE.Vector3(tl, 0, z)]), isSec ? axesMat : tickMat))
    }

    // Labels
    const xLabel = createAxisLabelSprite('ВРЕМЯ (t)', new THREE.Vector3(boxWidth / 2, -120, 0), 150)
    axisLabels.push(xLabel)
    scene3D.add(xLabel)

    const yLabel = createAxisLabelSprite('Капитал', new THREE.Vector3(-150, boxHeight / 2, 0), 150)
    axisLabels.push(yLabel)
    scene3D.add(yLabel)

    const zLabel = createAxisLabelSprite('ТРАЕКТОРИИ (N)', new THREE.Vector3(-120, -120, boxDepth / 2), 150)
    axisLabels.push(zLabel)
    scene3D.add(zLabel)

    scene3D.add(gridGroup)
    gridObjects.push(gridGroup)
  }

  const update3DTrajectories = () => {
    if (!scene3D || !simulationResult3D.value) return

    trajectories3DLines.forEach(line => {
      scene3D?.remove(line)
      line.geometry.dispose()
      if ((line.material as THREE.Material).dispose) (line.material as THREE.Material).dispose()
    })
    trajectories3DLines.length = 0

    const { paths, stats } = simulationResult3D.value

    if (!cachedScaleParams || cachedScaleParams.stats !== stats) {
      const sx = 3.0
      const sz = 8.0
      const targetVisualHeight = 300
      const priceRange = stats.maxPrice - stats.minPrice
      const safeRange = Math.max(priceRange, stats.meanFinalPrice * 0.05, 1.0)
      const sy = targetVisualHeight / safeRange
      cachedScaleParams = { scaleX: sx, scaleY: sy, scaleZ: sz, stats, boxWidth: paths[0].length * sx, boxDepth: paths.length * sz }
    }

    const { scaleX: sx, scaleY: sy, scaleZ: sz, boxWidth, boxDepth } = cachedScaleParams
    const maxY = (stats.maxPrice - stats.minPrice) * sy
    const targetY = maxY / 2
    const boxCenterX = boxWidth / 2
    const boxCenterZ = boxDepth / 2

    if (camera3D && controls3D && !cameraPositioned) {
      const cameraDistance = Math.max(boxWidth, boxDepth, maxY) * 0.8
      camera3D.position.set(cameraDistance, targetY + cameraDistance * 0.5, cameraDistance)
      controls3D.target.set(boxCenterX, targetY, boxCenterZ)
      controls3D.update()
      cameraPositioned = true
    }

    const primaryMaterial = new THREE.LineBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.6, linewidth: 1.5 })
    const whiteMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 1.0, linewidth: 2.5 })

    paths.forEach((path, idx) => {
      const finalVal = path[path.length - 1].y
      const isOutlier = Math.abs(finalVal - paths[0][0].y) > (stats.stdDev * 1.5)
      const material = isOutlier ? whiteMaterial : primaryMaterial
      const limit = Math.max(2, Math.min(path.length, currentStep3D.value))
      const activePoints = path.slice(0, limit)
      if (activePoints.length < 2) return

      const points = activePoints.map(p => new THREE.Vector3(p.x * sx, (p.y - stats.minPrice) * sy, p.z * sz))
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      const line = new THREE.Line(geometry, material)
      if (scene3D) {
        scene3D.add(line)
        trajectories3DLines[idx] = line
      }
    })

    update3DGrids(stats, sx, sy, sz, boxWidth, boxDepth)

    if (renderer3D && scene3D && camera3D) {
      renderer3D.render(scene3D, camera3D)
    }
  }

  const init3DTrajectories = async () => {
    if (!trajectories3DCanvas.value) return

    if (renderer3D) {
      renderer3D.dispose()
      renderer3D = null
    }
    if (animationId3D) {
      cancelAnimationFrame(animationId3D)
      animationId3D = null
    }
    cameraPositioned = false
    cachedScaleParams = null

    const container = trajectories3DCanvas.value.parentElement as HTMLElement
    if (!container) return

    const width = container.clientWidth || 800
    const height = container.clientHeight || 600
    if (width === 0 || height === 0) {
      setTimeout(() => {
        if (trajectories3DCanvas.value) init3DTrajectories()
      }, 500)
      return
    }

    scene3D = new THREE.Scene()
    scene3D.background = null

    camera3D = new THREE.PerspectiveCamera(45, width / height, 0.1, 50000)
    renderer3D = new THREE.WebGLRenderer({ canvas: trajectories3DCanvas.value, antialias: true, alpha: true })
    renderer3D.setSize(width, height)
    renderer3D.setPixelRatio(window.devicePixelRatio)

    controls3D = new OrbitControls(camera3D, renderer3D.domElement)
    controls3D.enableDamping = true
    controls3D.dampingFactor = 0.1
    controls3D.rotateSpeed = 0.5

    scene3D.add(new THREE.AmbientLight(0xffffff, 3))

    const basePrice = initialPrice.value * 10000
    const config: SimulationConfig3D = {
      initialPrice: basePrice,
      drift: hjbParams.value.expectedReturn,
      volatility: hjbParams.value.marketVol,
      timeSteps: trajectoriesDays.value,
      numPaths: hjbParams.value.monteCarloTrajectories,
      dt: 1 / 252,
      jumpIntensity: 2.0,
      jumpMean: 0.05,
      jumpSd: 0.15
    }

    simulationResult3D.value = runMonteCarlo3D(config)
    const maxStep = simulationResult3D.value.paths[0]?.length || 0
    currentStep3D.value = maxStep
    playbackStep3D.value = maxStep
    update3DTrajectories()

    const animate = () => {
      animationId3D = requestAnimationFrame(animate)
      if (controls3D) controls3D.update()
      if (renderer3D && scene3D && camera3D) renderer3D.render(scene3D, camera3D)
    }
    animate()

    const handleResize = () => {
      if (!container || !camera3D || !renderer3D) return
      camera3D.aspect = container.clientWidth / (container.clientHeight || 500)
      camera3D.updateProjectionMatrix()
      renderer3D.setSize(container.clientWidth, container.clientHeight || 500)
    }
    window.addEventListener('resize', handleResize)

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
      if (animationId3D) cancelAnimationFrame(animationId3D)
      if (renderer3D) renderer3D.dispose()
    })
  }

  const update3DVisualizationFromBackend = (monteCarloData: NonNullable<HJBResponse['monte_carlo']>) => {
    if (!monteCarloData || !monteCarloData.paths.length) return

    const paths3D: PathPoint3D[][] = []
    const tGrid = monteCarloData.t_grid || monteCarloData.paths[0].map((_, i) => i)
    const numPaths = Math.min(hjbParams.value.monteCarloTrajectories, monteCarloData.paths.length)

    for (let i = 0; i < numPaths; i++) {
      const path = monteCarloData.paths[i]
      const path3D: PathPoint3D[] = []
      for (let t = 0; t < path.length; t++) {
        path3D.push({ x: tGrid[t] || t, y: path[t], z: i })
      }
      paths3D.push(path3D)
    }

    const finalPrices = monteCarloData.paths.map(path => path[path.length - 1])
    simulationResult3D.value = {
      paths: paths3D,
      jumps: [],
      stats: {
        meanFinalPrice: monteCarloData.stats.mean_final || finalPrices.reduce((a, b) => a + b, 0) / finalPrices.length,
        maxPrice: monteCarloData.stats.max_final || Math.max(...finalPrices),
        minPrice: monteCarloData.stats.min_final || Math.min(...finalPrices),
        stdDev: monteCarloData.stats.std_final || 0
      }
    }

    if (paths3D.length > 0 && paths3D[0].length > 0) {
      const ms = paths3D[0].length - 1
      currentStep3D.value = ms
      playbackStep3D.value = ms
      cameraPositioned = false
      stopPlay3D()

      if (trajectories3DCanvas.value) {
        if (!renderer3D) {
          init3DTrajectories()
        } else {
          update3DTrajectories()
        }
      }
    }
  }

  // Playback
  const togglePlay3D = () => {
    if (isPlaying3D.value) {
      stopPlay3D()
    } else {
      if (playbackStep3D.value >= maxStep3D.value) playbackStep3D.value = 0
      isPlaying3D.value = true
      animate3D()
    }
  }

  const stopPlay3D = () => {
    isPlaying3D.value = false
    if (animationFrame3D) {
      cancelAnimationFrame(animationFrame3D)
      animationFrame3D = null
    }
  }

  const resetPlayback3D = () => {
    stopPlay3D()
    playbackStep3D.value = 0
    currentStep3D.value = 0
    update3DTrajectories()
  }

  const animate3D = () => {
    if (!isPlaying3D.value) return
    const ms = maxStep3D.value
    const nextStep = playbackStep3D.value + Math.max(1, Math.floor(ms / 100))
    if (nextStep >= ms) {
      playbackStep3D.value = ms
      currentStep3D.value = ms
      stopPlay3D()
      update3DTrajectories()
    } else {
      playbackStep3D.value = nextStep
      currentStep3D.value = nextStep
      update3DTrajectories()
      animationFrame3D = requestAnimationFrame(animate3D)
    }
  }

  watch(playbackStep3D, (newStep) => {
    if (!isPlaying3D.value) {
      currentStep3D.value = newStep
      update3DTrajectories()
    }
  })

  const cleanup3D = () => {
    if (animationId3D) {
      cancelAnimationFrame(animationId3D)
      animationId3D = null
    }
    if (renderer3D) {
      renderer3D.dispose()
      renderer3D = null
    }
    scene3D = null
    camera3D = null
    controls3D = null
    trajectories3DLines.length = 0
    gridObjects.length = 0
    axisLabels.forEach(sprite => {
      if (sprite.material instanceof THREE.SpriteMaterial) {
        sprite.material.map?.dispose()
        sprite.material.dispose()
      }
    })
    axisLabels.length = 0
  }

  return {
    trajectories3DCanvas,
    simulationResult3D,
    isPlaying3D,
    playbackStep3D,
    maxStep3D,
    formatPercent,
    averageReturn,
    medianReturn,
    sharpeRatio,
    var95,
    cvar95,
    averageMDD,
    runMonteCarlo3D,
    init3DTrajectories,
    update3DTrajectories,
    update3DVisualizationFromBackend,
    togglePlay3D,
    stopPlay3D,
    resetPlayback3D,
    cleanup3D
  }
}
