import { ref, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import { calculateGARCH, type GARCHResponse } from '../../services/computeService'

export function useGARCHChart(
  portfolioPositions: Ref<any[]>
) {
  const garchChart = ref<HTMLCanvasElement | null>(null)
  const garchData = ref<GARCHResponse | null>(null)
  const garchAnimationFrame = ref<number | null>(null)
  const garchAnimationStep = ref(0)
  const isGARCHAnimating = ref(false)

  const getPortfolioReturnsForGARCH = (): number[] => {
    const positions = portfolioPositions.value
    if (positions.length === 0) return []

    const returns: number[] = []
    for (let i = 0; i < 500; i++) {
      const baseReturn = positions.reduce((sum, pos) => {
        const dailyReturn = (pos.dayChange / 100) / 252
        return sum + dailyReturn * (pos.allocation || 0)
      }, 0)
      const noise = (Math.random() - 0.5) * 0.02
      returns.push(baseReturn + noise)
    }
    return returns
  }

  const generateLocalGARCHData = () => {
    const returns = getPortfolioReturnsForGARCH()
    if (returns.length === 0) {
      const dataPoints = 500
      const volatilities: number[] = []
      let currentVol = 0.18

      for (let i = 0; i < dataPoints; i++) {
        const noise = (Math.random() - 0.5) * 0.05
        currentVol = Math.max(0.05, Math.min(0.5, currentVol * 0.95 + noise))
        volatilities.push(currentVol)
      }

      garchData.value = {
        result: {
          variances: volatilities.map(v => v * v),
          volatilities,
          residuals: Array(dataPoints).fill(0).map(() => (Math.random() - 0.5) * 0.3),
          parameters: { omega: 0.000025, alpha: 0.082, beta: 0.893 },
          long_term_volatility: 0.182,
          mean_variance: 0.033,
          mean_volatility: 0.18
        },
        status: 'success',
        timestamp: new Date().toISOString()
      }
      garchAnimationStep.value = 0
      startGARCHAnimation()
    }
  }

  const loadGARCHData = async () => {
    try {
      const returns = getPortfolioReturnsForGARCH()
      if (returns.length === 0) return

      const result = await calculateGARCH({
        returns,
        omega: 0.000025,
        alpha: 0.082,
        beta: 0.893
      })

      garchData.value = result
      garchAnimationStep.value = 0
      startGARCHAnimation()
    } catch (error) {
      console.error('Failed to load GARCH data:', error)
      generateLocalGARCHData()
    }
  }

  const startGARCHAnimation = () => {
    if (isGARCHAnimating.value) return
    isGARCHAnimating.value = true
    garchAnimationStep.value = 0
    animateGARCHChart()
  }

  const stopGARCHAnimation = () => {
    isGARCHAnimating.value = false
    if (garchAnimationFrame.value) {
      cancelAnimationFrame(garchAnimationFrame.value)
      garchAnimationFrame.value = null
    }
  }

  const animateGARCHChart = () => {
    if (!isGARCHAnimating.value || !garchData.value) return

    const canvas = document.getElementById('garch-chart') as HTMLCanvasElement
    if (!canvas) {
      stopGARCHAnimation()
      return
    }

    const ctx = canvas.getContext('2d')
    if (!ctx) {
      stopGARCHAnimation()
      return
    }

    const width = canvas.offsetWidth || 1200
    const height = 200
    canvas.width = width
    canvas.height = height

    const volatilities = garchData.value.result.volatilities
    const dataPoints = volatilities.length

    garchAnimationStep.value += 2
    const currentLength = Math.min(garchAnimationStep.value, dataPoints)

    ctx.fillStyle = 'rgba(20, 22, 28, 0.5)'
    ctx.fillRect(0, 0, width, height)

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
    ctx.lineWidth = 1
    ctx.setLineDash([5, 5])
    ctx.beginPath()
    ctx.moveTo(0, height / 2)
    ctx.lineTo(width, height / 2)
    ctx.stroke()
    ctx.setLineDash([])

    if (currentLength > 0) {
      const meanVol = garchData.value.result.mean_volatility
      const maxDev = Math.max(...volatilities.slice(0, currentLength).map(v => Math.abs(v - meanVol))) * 1.2
      const rangeY = maxDev * 2 || 0.1

      ctx.strokeStyle = '#60a5fa'
      ctx.lineWidth = 2
      ctx.beginPath()

      for (let i = 0; i < currentLength; i++) {
        const x = (i / (dataPoints - 1)) * width
        const normalizedVol = (volatilities[i] - meanVol) / rangeY
        const y = height / 2 - normalizedVol * (height * 0.8)
        if (i === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
      }
      ctx.stroke()

      ctx.fillStyle = 'rgba(96, 165, 250, 0.15)'
      if (currentLength > 0) {
        const lastX = ((currentLength - 1) / (dataPoints - 1)) * width
        ctx.lineTo(lastX, height / 2)
        ctx.lineTo(0, height / 2)
        ctx.closePath()
        ctx.fill()
      }

      ctx.fillStyle = '#60a5fa'
      for (let i = 0; i < currentLength; i += 10) {
        const x = (i / (dataPoints - 1)) * width
        const normalizedVol = (volatilities[i] - meanVol) / rangeY
        const y = height / 2 - normalizedVol * (height * 0.8)
        ctx.beginPath()
        ctx.arc(x, y, 2, 0, Math.PI * 2)
        ctx.fill()
      }

      if (currentLength < dataPoints) {
        const currentX = ((currentLength - 1) / (dataPoints - 1)) * width
        ctx.strokeStyle = '#fbbf24'
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(currentX, 0)
        ctx.lineTo(currentX, height)
        ctx.stroke()
      }
    }

    if (currentLength < dataPoints) {
      garchAnimationFrame.value = requestAnimationFrame(animateGARCHChart)
    } else {
      setTimeout(() => {
        garchAnimationStep.value = 0
        garchAnimationFrame.value = requestAnimationFrame(animateGARCHChart)
      }, 2000)
    }
  }

  const initGARCHChart = () => {
    const canvas = document.getElementById('garch-chart') as HTMLCanvasElement
    if (!canvas) return
    loadGARCHData()
  }

  onUnmounted(() => {
    stopGARCHAnimation()
  })

  return {
    garchChart,
    garchData,
    isGARCHAnimating,
    initGARCHChart,
    loadGARCHData,
    stopGARCHAnimation,
    animateGARCHChart
  }
}
