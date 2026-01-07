/**
 * Three.js рендерер для 3D визуализации пространства скрытых состояний
 */

import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import type { MarketPoint, HMMModel } from './useHMMModel'

// Dynamic import for GSAP to avoid SSR issues
let gsapPromise: Promise<any> | null = null
async function getGSAP() {
  if (typeof window === 'undefined') return null
  if (gsapPromise) return gsapPromise
  gsapPromise = import('gsap').then(m => m.gsap)
  return gsapPromise
}

export interface RegimeConfig {
  id: number
  name: string
  color: string
  mean: [number, number, number]  // [return, volatility, liquidity]
}

export interface CameraPreset {
  name: string
  position: [number, number, number]
  target: [number, number, number]
}

/**
 * Класс для рендеринга 3D пространства режимов
 */
export class RegimeSpaceRenderer {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private container: HTMLElement

  // 3D объекты
  private trajectoryLine: THREE.Line | null = null
  private trajectoryPoints: THREE.Points | null = null
  private regimeEllipsoids: THREE.Group[] = []
  private regimeCentroids: THREE.Mesh[] = []
  private axesHelper: THREE.Group | null = null
  private gridHelper: THREE.GridHelper | null = null

  // Данные
  private marketData: MarketPoint[] = []
  private hmmModel: HMMModel | null = null
  private regimeConfigs: RegimeConfig[] = []

  // Анимация
  private animationId: number | null = null
  private isAnimating = false
  private autoRotate = false

  // Настройки
  private showTrajectory = true
  private showEllipsoids = true
  private showCentroids = true
  private showGrid = true
  private currentTimeIndex = 0
  private showTransitionArrows = false
  private transitionArrows: THREE.ArrowHelper[] = []

  constructor(container: HTMLElement) {
    this.container = container
    this.initScene()
    this.initCamera()
    this.initRenderer()
    this.initControls()
    this.initLighting()
    this.animate()
  }

  /**
   * Инициализация сцены
   */
  private initScene() {
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x0a0a0f)
    this.scene.fog = new THREE.FogExp2(0x0a0a0f, 0.01)
  }

  /**
   * Инициализация камеры
   */
  private initCamera() {
    const width = this.container.clientWidth
    const height = this.container.clientHeight
    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
    this.camera.position.set(40, 40, 40)
    this.camera.lookAt(0, 0, 0)
  }

  /**
   * Инициализация рендерера
   */
  private initRenderer() {
    this.renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: 'high-performance'
    })
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.container.appendChild(this.renderer.domElement)
  }

  /**
   * Инициализация контролов камеры
   */
  private initControls() {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.05
    this.controls.minDistance = 10
    this.controls.maxDistance = 200
    this.controls.maxPolarAngle = Math.PI
  }

  /**
   * Инициализация освещения
   */
  private initLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
    this.scene.add(ambientLight)

    // Directional lights - muted colors
    const light1 = new THREE.DirectionalLight(0x60a5fa, 0.5)
    light1.position.set(30, 30, 30)
    light1.castShadow = true
    this.scene.add(light1)

    const light2 = new THREE.DirectionalLight(0xa78bfa, 0.3)
    light2.position.set(-30, 30, -30)
    this.scene.add(light2)

    const light3 = new THREE.DirectionalLight(0x4ade80, 0.2)
    light3.position.set(0, -30, 0)
    this.scene.add(light3)
  }

  /**
   * Настройка данных
   */
  setData(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    this.marketData = marketData
    this.hmmModel = hmmModel
    this.regimeConfigs = regimeConfigs
    this.updateVisualization()
  }

  /**
   * Обновление визуализации
   */
  updateVisualization() {
    this.clearScene()
    this.createAxes()
    this.createGrid()
    this.createRegimeEllipsoids()
    this.createRegimeCentroids()
    this.createTrajectory()
    if (this.showTransitionArrows) {
      this.createTransitionArrows()
    }
  }

  /**
   * Очистка сцены
   */
  private clearScene() {
    // Remove existing objects
    if (this.trajectoryLine) this.scene.remove(this.trajectoryLine)
    if (this.trajectoryPoints) this.scene.remove(this.trajectoryPoints)
    if (this.axesHelper) this.scene.remove(this.axesHelper)
    if (this.gridHelper) this.scene.remove(this.gridHelper)
    
    this.regimeEllipsoids.forEach(ellipsoid => this.scene.remove(ellipsoid))
    this.regimeCentroids.forEach(centroid => this.scene.remove(centroid))
    this.transitionArrows.forEach(arrow => this.scene.remove(arrow))
    
    this.regimeEllipsoids = []
    this.regimeCentroids = []
    this.transitionArrows = []
  }

  /**
   * Создание стрелок вероятностей переходов
   */
  private createTransitionArrows() {
    if (!this.hmmModel || this.marketData.length === 0) return
    
    const currentPoint = this.marketData[this.currentTimeIndex]
    if (!currentPoint || currentPoint.regime === undefined) return
    
    const transitionMatrix = this.hmmModel.getTransitionMatrix()
    const currentRegime = currentPoint.regime
    const currentConfig = this.regimeConfigs.find(r => r.id === currentRegime)
    if (!currentConfig) return
    
    const means = this.hmmModel.getEmissionMeans()
    const currentPos = new THREE.Vector3(
      means[currentRegime][0],
      means[currentRegime][1],
      means[currentRegime][2] * 35
    )
    
    // Создаем стрелки для вероятных переходов (>0.1)
    transitionMatrix[currentRegime].forEach((prob, targetRegime) => {
      if (targetRegime === currentRegime || prob < 0.1) return
      
      const targetConfig = this.regimeConfigs.find(r => r.id === targetRegime)
      if (!targetConfig) return
      
      const targetPos = new THREE.Vector3(
        means[targetRegime][0],
        means[targetRegime][1],
        means[targetRegime][2] * 35
      )
      
      const direction = new THREE.Vector3()
      direction.subVectors(targetPos, currentPos)
      const length = direction.length()
      if (length < 5) return // Skip if too close
      
      direction.normalize()
      
      // Color based on probability
      const intensity = prob
      const color = new THREE.Color(targetConfig.color)
      
      const arrow = new THREE.ArrowHelper(
        direction,
        currentPos,
        length * 0.8,
        color.getHex(),
        2,
        1
      )
      
      // Set opacity based on probability
      const material = arrow.line.material as THREE.LineBasicMaterial
      material.opacity = intensity
      material.transparent = true
      
      this.transitionArrows.push(arrow)
      this.scene.add(arrow)
    })
  }

  /**
   * Создание осей координат
   */
  private createAxes() {
    const axesGroup = new THREE.Group()
    
    // X-axis (Return) - Muted Cyan
    const xAxis = new THREE.ArrowHelper(
      new THREE.Vector3(1, 0, 0),
      new THREE.Vector3(0, 0, 0),
      35,
      0x60a5fa,
      2,
      1
    )
    axesGroup.add(xAxis)
    
    // Y-axis (Volatility) - Muted Magenta
    const yAxis = new THREE.ArrowHelper(
      new THREE.Vector3(0, 1, 0),
      new THREE.Vector3(0, 0, 0),
      35,
      0xa78bfa,
      2,
      1
    )
    axesGroup.add(yAxis)
    
    // Z-axis (Liquidity) - Muted Green
    const zAxis = new THREE.ArrowHelper(
      new THREE.Vector3(0, 0, 1),
      new THREE.Vector3(0, 0, 0),
      35,
      0x4ade80,
      2,
      1
    )
    axesGroup.add(zAxis)
    
    // Note: Axis labels could be added with text sprites or HTML overlays
    // For now, axes are color-coded:
    // X (Cyan) = Return, Y (Magenta) = Volatility, Z (Green) = Liquidity
    
    this.axesHelper = axesGroup
    this.scene.add(axesGroup)
  }

  /**
   * Создание сетки
   */
  private createGrid() {
    if (!this.showGrid) return
    
    const grid = new THREE.GridHelper(100, 20, 0x333333, 0x222222)
    grid.rotation.x = Math.PI / 2
    this.gridHelper = grid
    this.scene.add(grid)
  }

  /**
   * Создание эллипсоидов режимов
   */
  private createRegimeEllipsoids() {
    if (!this.showEllipsoids || !this.hmmModel) return

    const means = this.hmmModel.getEmissionMeans()
    const covariances = this.hmmModel.getEmissionCovariances()

    means.forEach((mean, regimeId) => {
      const config = this.regimeConfigs.find(r => r.id === regimeId)
      if (!config) return

      const cov = covariances[regimeId]
      
      // Создаем эллипсоид из сферы с масштабированием
      const geometry = new THREE.SphereGeometry(1, 32, 32)
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(config.color),
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide,
        emissive: new THREE.Color(config.color),
        emissiveIntensity: 0.1
      })

      const ellipsoid = new THREE.Mesh(geometry, material)
      
      // Масштабируем по стандартным отклонениям (2 sigma)
      const scaleX = Math.sqrt(cov[0][0]) * 2
      const scaleY = Math.sqrt(cov[1][1]) * 2
      const scaleZ = Math.sqrt(cov[2][2]) * 2
      
      ellipsoid.scale.set(scaleX, scaleY, scaleZ)
      ellipsoid.position.set(mean[0], mean[1], mean[2] * 35) // Scale liquidity
      
      // Wireframe
      const wireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(geometry),
        new THREE.LineBasicMaterial({ 
          color: new THREE.Color(config.color), 
          opacity: 0.3, 
          transparent: true 
        })
      )
      wireframe.scale.copy(ellipsoid.scale)
      wireframe.position.copy(ellipsoid.position)
      
      const group = new THREE.Group()
      group.add(ellipsoid)
      group.add(wireframe)
      
      this.regimeEllipsoids.push(group)
      this.scene.add(group)
    })
  }

  /**
   * Создание центроидов режимов
   */
  private createRegimeCentroids() {
    if (!this.showCentroids || !this.hmmModel) return

    const means = this.hmmModel.getEmissionMeans()

    means.forEach((mean, regimeId) => {
      const config = this.regimeConfigs.find(r => r.id === regimeId)
      if (!config) return

      const geometry = new THREE.SphereGeometry(1.5, 16, 16)
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(config.color),
        emissive: new THREE.Color(config.color),
        emissiveIntensity: 0.8,
        transparent: true,
        opacity: 0.9
      })

      const centroid = new THREE.Mesh(geometry, material)
      centroid.position.set(mean[0], mean[1], mean[2] * 35)
      centroid.userData = { regimeId, config }

      // Glow effect
      const glowGeometry = new THREE.SphereGeometry(2, 16, 16)
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(config.color),
        transparent: true,
        opacity: 0.2
      })
      const glow = new THREE.Mesh(glowGeometry, glowMaterial)
      glow.position.copy(centroid.position)

      const group = new THREE.Group()
      group.add(centroid)
      group.add(glow)
      
      this.regimeCentroids.push(centroid)
      this.scene.add(group)
    })
  }

  /**
   * Создание траектории рынка
   */
  private createTrajectory() {
    if (this.marketData.length === 0) return

    const positions: number[] = []
    const colors: number[] = []
    const sizes: number[] = []
    const indices: number[] = []

    // Масштабирование: Return (x), Volatility (y), Liquidity * 35 (z)
    this.marketData.slice(0, this.currentTimeIndex + 1).forEach((point, i) => {
      const x = point.return
      const y = point.volatility
      const z = point.liquidity * 35

      positions.push(x, y, z)

      const config = this.regimeConfigs.find(r => r.id === (point.regime || 0))
      const color = config ? new THREE.Color(config.color) : new THREE.Color(0xffffff)
      colors.push(color.r, color.g, color.b)

      // Размер точки зависит от вероятности
      const prob = point.probability ? Math.max(...point.probability) : 0.5
      sizes.push(prob * 3 + 1)

      indices.push(i)
    })

    // Trajectory line
    if (this.showTrajectory && positions.length > 1) {
      const lineGeometry = new THREE.BufferGeometry()
      lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
      lineGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))

      const lineMaterial = new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        linewidth: 2
      })

      this.trajectoryLine = new THREE.Line(lineGeometry, lineMaterial)
      this.scene.add(this.trajectoryLine)
    }

    // Trajectory points
    if (positions.length > 0) {
      const pointsGeometry = new THREE.BufferGeometry()
      pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
      pointsGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
      pointsGeometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))

      const pointsMaterial = new THREE.PointsMaterial({
        size: 3,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        sizeAttenuation: true
      })

      this.trajectoryPoints = new THREE.Points(pointsGeometry, pointsMaterial)
      this.scene.add(this.trajectoryPoints)
    }
  }

  /**
   * Установка текущего индекса времени
   */
  setTimeIndex(index: number) {
    this.currentTimeIndex = Math.max(0, Math.min(index, this.marketData.length - 1))
    this.updateTrajectory()
  }

  /**
   * Обновление только траектории (без пересоздания всей сцены)
   */
  private updateTrajectory() {
    if (this.trajectoryLine) this.scene.remove(this.trajectoryLine)
    if (this.trajectoryPoints) this.scene.remove(this.trajectoryPoints)
    this.createTrajectory()
    
    if (this.showTransitionArrows) {
      this.transitionArrows.forEach(arrow => this.scene.remove(arrow))
      this.transitionArrows = []
      this.createTransitionArrows()
    }
  }

  /**
   * Показать/скрыть стрелки переходов
   */
  setShowTransitionArrows(show: boolean) {
    this.showTransitionArrows = show
    if (show) {
      this.createTransitionArrows()
    } else {
      this.transitionArrows.forEach(arrow => this.scene.remove(arrow))
      this.transitionArrows = []
    }
  }

  /**
   * Переключение видимости элементов
   */
  setShowTrajectory(show: boolean) {
    this.showTrajectory = show
    this.updateVisualization()
  }

  setShowEllipsoids(show: boolean) {
    this.showEllipsoids = show
    this.updateVisualization()
  }

  setShowCentroids(show: boolean) {
    this.showCentroids = show
    this.updateVisualization()
  }

  setShowGrid(show: boolean) {
    this.showGrid = show
    if (this.gridHelper) {
      if (show) {
        this.scene.add(this.gridHelper)
      } else {
        this.scene.remove(this.gridHelper)
      }
    }
  }

  /**
   * Установка preset камеры
   */
  async setCameraPreset(preset: CameraPreset) {
    const gsap = await getGSAP()
    if (!gsap) {
      // Fallback without animation
      this.camera.position.set(...preset.position)
      this.controls.target.set(...preset.target)
      this.controls.update()
      return
    }
    
    gsap.to(this.camera.position, {
      duration: 1.2,
      x: preset.position[0],
      y: preset.position[1],
      z: preset.position[2],
      ease: 'power2.out',
      onUpdate: () => {
        this.controls.target.set(...preset.target)
        this.controls.update()
      }
    })
  }

  /**
   * Переключение auto-rotate
   */
  setAutoRotate(enabled: boolean) {
    this.autoRotate = enabled
    this.controls.autoRotate = enabled
    this.controls.autoRotateSpeed = 1.0
  }

  /**
   * Анимационный цикл
   */
  private animate() {
    this.animationId = requestAnimationFrame(() => this.animate())
    
    if (this.controls) {
      this.controls.update()
    }
    
    // Auto-rotate
    if (this.autoRotate) {
      // Already handled by OrbitControls
    }
    
    // Pulsing centroids
    this.regimeCentroids.forEach((centroid, i) => {
      if (centroid && centroid.material instanceof THREE.MeshPhongMaterial) {
        const pulse = Math.sin(Date.now() * 0.001 + i) * 0.1 + 1
        centroid.scale.setScalar(pulse)
      }
    })
    
    this.renderer.render(this.scene, this.camera)
  }

  /**
   * Изменение размера
   */
  resize(width: number, height: number) {
    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
  }

  /**
   * Очистка ресурсов
   */
  dispose() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
    }
    
    this.clearScene()
    
    if (this.renderer) {
      this.renderer.dispose()
    }
    
    if (this.container && this.renderer?.domElement) {
      this.container.removeChild(this.renderer.domElement)
    }
  }

  /**
   * Экспорт скриншота
   */
  exportScreenshot(filename: string = 'regime-space.png') {
    this.renderer.render(this.scene, this.camera)
    const dataUrl = this.renderer.domElement.toDataURL('image/png')
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = filename
    link.click()
  }
}
