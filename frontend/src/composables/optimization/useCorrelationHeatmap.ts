import { ref, type Ref } from 'vue'

let Plotly: any = null
let plotlyLoadPromise: Promise<any> | null = null

const loadPlotly = async () => {
  if (typeof window !== 'undefined') {
    const win = window as any

    if (win.Plotly) {
      Plotly = win.Plotly
      return Plotly
    }

    if (plotlyLoadPromise) return plotlyLoadPromise

    const existingScript = document.querySelector('script[src*="plotly"]')
    if (existingScript) {
      plotlyLoadPromise = new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          if (win.Plotly) {
            clearInterval(checkInterval)
            Plotly = win.Plotly
            resolve(Plotly)
          }
        }, 100)
        setTimeout(() => {
          clearInterval(checkInterval)
          resolve(null)
        }, 10000)
      })
      return plotlyLoadPromise
    }

    plotlyLoadPromise = new Promise((resolve) => {
      const script = document.createElement('script')
      script.src = 'https://cdn.plot.ly/plotly-2.27.0.min.js'
      script.async = true
      script.onload = () => {
        Plotly = win.Plotly
        resolve(Plotly)
      }
      script.onerror = () => {
        resolve(null)
      }
      document.head.appendChild(script)
    })

    return plotlyLoadPromise
  }
  return null
}

export function useCorrelationHeatmap(
  portfolioPositions: Ref<any[]>,
  correlationMatrix: Ref<any[]>
) {
  const hoveredAsset = ref<any>(null)

  const initCorrelation3DHeatmap = async () => {
    try {
      await loadPlotly()
      if (!Plotly) return

      const container = document.getElementById('correlation-3d-heatmap')
      if (!container) return

      const allAssets = [...portfolioPositions.value]
      if (allAssets.length === 0) return

      const matrix = correlationMatrix.value

      const calculate3DPositions = (assets: any[], corrMatrix: any[]) => {
        return assets.map((asset) => {
          const isBond = asset.symbol.includes('SU') || asset.symbol.includes('RU000')
          const assetColor = isBond ? '#3b82f6' : '#10b981'
          const volatility = isBond ? (3 + Math.random() * 4) : (15 + Math.random() * 20)

          const matrixIndex = corrMatrix.findIndex(row => row.label === asset.symbol)
          let avgCorrelation = 0
          if (matrixIndex !== -1) {
            const values = corrMatrix[matrixIndex].values
            avgCorrelation = values.reduce((a: number, b: number) => a + b, 0) / values.length
          }

          return {
            x: volatility,
            y: avgCorrelation,
            z: asset.allocation,
            asset: { ...asset, color: assetColor, volatility, avgCorrelation }
          }
        })
      }

      const positions3D = calculate3DPositions(allAssets, matrix)
      if (positions3D.length === 0) return

      const xValues = positions3D.map(p => p.x)
      const yValues = positions3D.map(p => p.y)
      const zValues = positions3D.map(p => p.z)

      const xMin = Math.min(...xValues), xMax = Math.max(...xValues)
      const yMin = Math.min(...yValues), yMax = Math.max(...yValues)
      const zMin = Math.min(...zValues), zMax = Math.max(...zValues)

      const normalize = (val: number, min: number, max: number) => {
        if (max === min) return 5
        return ((val - min) / (max - min)) * 10
      }

      const normalizedPositions = positions3D.map(p => ({
        ...p,
        nx: normalize(p.x, xMin, xMax),
        ny: normalize(p.y, yMin, yMax),
        nz: normalize(p.z, zMin, zMax)
      }))

      const createSphere = (cx: number, cy: number, cz: number, r: number, color: string, asset: any) => {
        const x: number[] = [], y: number[] = [], z: number[] = []
        const steps = 16

        for (let i = 0; i < steps; i++) {
          const t = (i / (steps - 1)) * Math.PI
          for (let j = 0; j < steps; j++) {
            const p = (j / (steps - 1)) * 2 * Math.PI
            x.push(cx + r * Math.sin(t) * Math.cos(p))
            y.push(cy + r * Math.sin(t) * Math.sin(p))
            z.push(cz + r * Math.cos(t))
          }
        }

        return {
          type: 'mesh3d', x, y, z, color, alphahull: 0, opacity: 1, flatshading: false,
          lighting: { ambient: 0.6, diffuse: 0.9, specular: 1.0, roughness: 0.1, fresnel: 0.8 },
          lightposition: { x: 10, y: 10, z: 20 },
          hoverinfo: 'none',
          customdata: asset,
          name: asset.symbol
        }
      }

      const traces: any[] = []

      normalizedPositions.forEach((pos) => {
        const size = 0.3 + (pos.asset.allocation / 25)
        traces.push(createSphere(pos.nx, pos.ny, pos.nz, size, pos.asset.color, pos.asset))
      })

      traces.push({
        x: normalizedPositions.map(p => p.nx),
        y: normalizedPositions.map(p => p.ny),
        z: normalizedPositions.map(p => p.nz),
        mode: 'markers',
        type: 'scatter3d',
        marker: {
          size: normalizedPositions.map(p => Math.max(40, (0.3 + p.asset.allocation / 25) * 40)),
          color: 'rgba(255,255,255,0)',
          opacity: 0,
          line: { width: 0 }
        },
        hoverinfo: 'skip',
        customdata: normalizedPositions.map(p => p.asset)
      })

      const makeTickText = (min: number, max: number, suffix: string, decimals: number = 0) => {
        const vals = [0, 2.5, 5, 7.5, 10]
        return vals.map(v => {
          const real = min + (v / 10) * (max - min)
          return real.toFixed(decimals) + suffix
        })
      }

      const layout = {
        showlegend: false,
        hovermode: 'closest',
        scene: {
          xaxis: {
            title: 'РИСК (Волатильность %)',
            backgroundcolor: 'rgba(20, 22, 28, 0.8)',
            gridcolor: 'rgba(255,255,255,0.08)',
            zeroline: false, showbackground: true,
            titlefont: { color: '#ffffff', size: 12, weight: 'bold' },
            tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
            tickvals: [0, 2.5, 5, 7.5, 10],
            ticktext: makeTickText(xMin, xMax, '%'),
            showspikes: false
          },
          yaxis: {
            title: 'СВЯЗЬ (Корреляция)',
            backgroundcolor: 'rgba(30, 32, 38, 0.6)',
            gridcolor: 'rgba(255,255,255,0.08)',
            zeroline: false, showbackground: true,
            titlefont: { color: '#ffffff', size: 12, weight: 'bold' },
            tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
            tickvals: [0, 2.5, 5, 7.5, 10],
            ticktext: makeTickText(yMin, yMax, '', 2),
            showspikes: false
          },
          zaxis: {
            title: 'ДОЛЯ (Вес %)',
            backgroundcolor: 'rgba(20, 22, 28, 0.8)',
            gridcolor: 'rgba(255,255,255,0.08)',
            zeroline: false, showbackground: true,
            titlefont: { color: '#ffffff', size: 12, weight: 'bold' },
            tickfont: { size: 9, color: 'rgba(255,255,255,0.6)' },
            tickvals: [0, 2.5, 5, 7.5, 10],
            ticktext: makeTickText(zMin, zMax, '%', 1),
            showspikes: false
          },
          bgcolor: 'rgba(0,0,0,0)',
          camera: { eye: { x: 1.8, y: 1.8, z: 1.2 }, center: { x: 0, y: 0, z: 0 }, up: { x: 0, y: 0, z: 1 } },
          aspectmode: 'cube'
        },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#fff', family: 'system-ui' },
        margin: { l: 0, r: 0, b: 0, t: 0 },
        autosize: true
      }

      Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false, staticPlot: false, displaylogo: false })

      const plotlyContainer = container as any

      plotlyContainer.on('plotly_hover', (data: any) => {
        if (data?.points?.length > 0) {
          for (const point of data.points) {
            if (point.customdata) {
              const asset = Array.isArray(point.customdata) ? point.customdata[0] : point.customdata
              if (asset) {
                hoveredAsset.value = asset
                return
              }
            }

            const scatterTraceIndex = traces.length - 1
            if (point.curveNumber === scatterTraceIndex && point.pointNumber !== undefined) {
              const index = point.pointNumber
              if (index >= 0 && index < normalizedPositions.length && normalizedPositions[index]) {
                hoveredAsset.value = normalizedPositions[index].asset
                return
              }
            }

            if (point.curveNumber < scatterTraceIndex && point.curveNumber < normalizedPositions.length) {
              if (normalizedPositions[point.curveNumber]) {
                hoveredAsset.value = normalizedPositions[point.curveNumber].asset
                return
              }
            }
          }
        }
      })

      plotlyContainer.on('plotly_unhover', () => {
        hoveredAsset.value = null
      })
    } catch (err) {
      console.error('Error initializing 3D Correlation Heatmap:', err)
    }
  }

  return {
    hoveredAsset,
    initCorrelation3DHeatmap
  }
}
