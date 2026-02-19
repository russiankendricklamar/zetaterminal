import { ref, reactive, computed, onUnmounted } from 'vue'
import type { Ref } from 'vue'

interface TrajectoriesData {
  paths: number[][]
  displayPaths: number[][]
  medianPath: number[]
  q05: number[]
  q95: number[]
  minY: number
  maxY: number
}

export function useMonteCarlo2D(
  hjbParams: Ref<{
    horizon: number
    expectedReturn: number
    marketVol: number
    riskFreeRate: number
    monteCarloTrajectories: number
  }>,
  trajectoriesDays: Ref<number>
) {
  const playbackStepTrajectories = ref(0)
  const isPlayingTrajectories = ref(false)
  let animationFrameTrajectories: number | null = null
  const trajectoriesChartContainer = ref<HTMLElement | null>(null)
  const initialPrice = ref(0)

  const trajectoriesData = reactive<TrajectoriesData>({
    paths: [],
    displayPaths: [],
    medianPath: [],
    q05: [],
    q95: [],
    minY: 0,
    maxY: 200
  })

  const boxMullerRandom = (): number => {
    let u = 0, v = 0
    while (u === 0) u = Math.random()
    while (v === 0) v = Math.random()
    return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v)
  }

  const scaleX = (t: number): number => {
    const days = trajectoriesDays.value
    return (t / days) * 1000
  }

  const scaleY = (price: number): number => {
    const range = trajectoriesData.maxY - trajectoriesData.minY
    const normalized = (price - trajectoriesData.minY) / range
    return 400 - normalized * 400
  }

  const generatePathD = (path: number[], limit: number): string => {
    if (!path.length) return ''
    const sliced = path.slice(0, limit + 1)
    return 'M ' + sliced.map((p, i) => `${scaleX(i).toFixed(1)},${scaleY(p).toFixed(1)}`).join(' L ')
  }

  const generateAreaD = (lower: number[], upper: number[], limit: number): string => {
    if (!lower.length) return ''
    const lSliced = lower.slice(0, limit + 1)
    const uSliced = upper.slice(0, limit + 1)

    let d = 'M ' + lSliced.map((p, i) => `${scaleX(i).toFixed(1)},${scaleY(p).toFixed(1)}`).join(' L ')
    for (let i = uSliced.length - 1; i >= 0; i--) {
      d += ` L ${scaleX(i).toFixed(1)},${scaleY(uSliced[i]).toFixed(1)}`
    }
    d += ' Z'
    return d
  }

  const updateDisplayPaths = () => {
    if (!trajectoriesData.paths.length) return
    const numPaths = Math.min(
      hjbParams.value.monteCarloTrajectories,
      trajectoriesData.paths.length
    )
    trajectoriesData.displayPaths = trajectoriesData.paths.slice(0, numPaths)
  }

  const generateTrajectories = () => {
    const { expectedReturn, marketVol, monteCarloTrajectories } = hjbParams.value
    const days = trajectoriesDays.value
    const dt = 1 / 252
    const mu = expectedReturn
    const sigma = marketVol

    const newPaths: number[][] = []

    for (let i = 0; i < monteCarloTrajectories; i++) {
      const path = [initialPrice.value]
      let currentPrice = initialPrice.value

      for (let t = 1; t <= days; t++) {
        const Z = boxMullerRandom()
        const driftTerm = (mu - 0.5 * sigma * sigma) * dt
        const shockTerm = sigma * Math.sqrt(dt) * Z
        currentPrice = currentPrice * Math.exp(driftTerm + shockTerm)
        path.push(currentPrice)
      }
      newPaths.push(path)
    }

    const steps = days + 1
    const medianPath: number[] = []
    const q05Path: number[] = []
    const q95Path: number[] = []
    let globalMin = initialPrice.value
    let globalMax = initialPrice.value

    for (let t = 0; t < steps; t++) {
      const pricesAtT = newPaths.map(p => p[t]).sort((a, b) => a - b)
      const med = pricesAtT[Math.floor(monteCarloTrajectories * 0.5)]
      const q05 = pricesAtT[Math.floor(monteCarloTrajectories * 0.05)]
      const q95 = pricesAtT[Math.floor(monteCarloTrajectories * 0.95)]

      medianPath.push(med)
      q05Path.push(q05)
      q95Path.push(q95)

      if (q05 < globalMin) globalMin = q05
      if (q95 > globalMax) globalMax = q95
    }

    trajectoriesData.paths = newPaths
    updateDisplayPaths()
    trajectoriesData.medianPath = medianPath
    trajectoriesData.q05 = q05Path
    trajectoriesData.q95 = q95Path
    trajectoriesData.minY = globalMin * 0.9
    trajectoriesData.maxY = globalMax * 1.1

    if (!isPlayingTrajectories.value) {
      playbackStepTrajectories.value = days
    }
  }

  const animateTrajectories = () => {
    if (!isPlayingTrajectories.value) return

    const days = trajectoriesDays.value
    const nextStep = playbackStepTrajectories.value + Math.max(1, Math.floor(days / 100))

    if (nextStep >= days) {
      playbackStepTrajectories.value = days
      stopPlayTrajectories()
    } else {
      playbackStepTrajectories.value = nextStep
      animationFrameTrajectories = requestAnimationFrame(animateTrajectories)
    }
  }

  const togglePlayTrajectories = () => {
    if (isPlayingTrajectories.value) {
      stopPlayTrajectories()
    } else {
      if (playbackStepTrajectories.value >= trajectoriesDays.value) {
        playbackStepTrajectories.value = 0
      }
      isPlayingTrajectories.value = true
      animateTrajectories()
    }
  }

  const stopPlayTrajectories = () => {
    isPlayingTrajectories.value = false
    if (animationFrameTrajectories) {
      cancelAnimationFrame(animationFrameTrajectories)
    }
  }

  const resetPlaybackTrajectories = () => {
    stopPlayTrajectories()
    playbackStepTrajectories.value = 0
  }

  // Update trajectories from backend data
  const updateFromBackend = (monteCarlo: {
    paths: number[][]
    median_path: number[]
    q05_path: number[]
    q95_path: number[]
  }) => {
    trajectoriesData.paths = monteCarlo.paths
    updateDisplayPaths()
    trajectoriesData.medianPath = monteCarlo.median_path
    trajectoriesData.q05 = monteCarlo.q05_path
    trajectoriesData.q95 = monteCarlo.q95_path

    const allValues = [
      ...monteCarlo.q05_path,
      ...monteCarlo.q95_path
    ]
    trajectoriesData.minY = Math.min(...allValues) * 0.9
    trajectoriesData.maxY = Math.max(...allValues) * 1.1

    playbackStepTrajectories.value = trajectoriesDays.value
  }

  onUnmounted(() => {
    if (animationFrameTrajectories) {
      cancelAnimationFrame(animationFrameTrajectories)
    }
  })

  return {
    playbackStepTrajectories,
    isPlayingTrajectories,
    trajectoriesChartContainer,
    initialPrice,
    trajectoriesData,
    scaleX,
    scaleY,
    generatePathD,
    generateAreaD,
    updateDisplayPaths,
    generateTrajectories,
    togglePlayTrajectories,
    stopPlayTrajectories,
    resetPlaybackTrajectories,
    updateFromBackend
  }
}
