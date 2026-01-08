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
  private trajectoryNodes: THREE.Mesh[] = [] // Узлы траектории (маленькие кружки)
  private transitionMarkers: THREE.Mesh[] = [] // Шарики переходов между режимами
  private regimeEllipsoids: THREE.Group[] = []
  private regimeCentroids: THREE.Mesh[] = []
  private axesHelper: THREE.Group | null = null
  private gridHelper: THREE.Object3D | null = null

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
  
  // Renaissance Insights Mode
  private renaissanceMode = false
  private selectedTimeframe = 'daily'
  private nonRandomSegments: THREE.Group[] = []
  private arbitrageZones: THREE.Mesh[] = []
  private meanReversionBands: THREE.Mesh[] = []
  private momentumArrows: THREE.ArrowHelper[] = []
  private signalMarkers: THREE.Group[] = []
  private probabilityWaves: THREE.Group[] = []
  private decodingParticles: THREE.Points[] = []
  private portfolioHeatmap: THREE.Group | null = null
  private comparisonOverlay: THREE.Group | null = null

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
    this.trajectoryNodes.forEach(node => this.scene.remove(node))
    this.transitionMarkers.forEach(marker => this.scene.remove(marker))
    if (this.axesHelper) this.scene.remove(this.axesHelper)
    if (this.gridHelper) this.scene.remove(this.gridHelper)
    
    this.regimeEllipsoids.forEach(ellipsoid => this.scene.remove(ellipsoid))
    this.regimeCentroids.forEach(centroid => this.scene.remove(centroid))
    this.transitionArrows.forEach(arrow => this.scene.remove(arrow))
    
    // Clear Renaissance overlays
    this.clearRenaissanceOverlays()
    
    this.regimeEllipsoids = []
    this.regimeCentroids = []
    this.transitionArrows = []
    this.transitionMarkers = []
  }

  /**
   * Получение позиции режима в 3D пространстве
   */
  private getRegimePosition(regimeId: number): THREE.Vector3 {
    if (!this.hmmModel) return new THREE.Vector3(0, 0, 0)
    const means = this.hmmModel.getEmissionMeans()
    if (!means[regimeId]) return new THREE.Vector3(0, 0, 0)
    const mean = means[regimeId]
    // mean[0] = Return, mean[1] = Volatility, mean[2] = Liquidity
    return new THREE.Vector3(mean[0], mean[1], mean[2] * 35)
  }

  /**
   * Определение цвета режима по волатильности
   * Низкая волатильность (< 15) - голубой
   * Средняя волатильность (15-30) - оранжевый
   * Высокая волатильность (> 30) - красный
   */
  private getRegimeColorByVolatility(volatility: number): string {
    if (volatility < 15) {
      return '#60a5fa' // Голубой
    } else if (volatility <= 30) {
      return '#fb923c' // Оранжевый
    } else {
      return '#ef4444' // Красный
    }
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
    
    const currentPos = this.getRegimePosition(currentRegime)
    
    // Создаем стрелки для вероятных переходов (>0.1)
    transitionMatrix[currentRegime].forEach((prob, targetRegime) => {
      if (targetRegime === currentRegime || prob < 0.1) return
      
      const targetConfig = this.regimeConfigs.find(r => r.id === targetRegime)
      if (!targetConfig) return
      
      const targetPos = this.getRegimePosition(targetRegime)
      
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
    // Направлена к камере (положительное направление от пользователя)
    const xAxis = new THREE.ArrowHelper(
      new THREE.Vector3(-1, 0, 0),
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
    
    // Add axis labels using sprites
    this.addAxisLabel('Return (%)', new THREE.Vector3(-38, 0, 0), 0x60a5fa, axesGroup)
    this.addAxisLabel('Volatility (%)', new THREE.Vector3(0, 38, 0), 0xa78bfa, axesGroup)
    this.addAxisLabel('Liquidity', new THREE.Vector3(0, 0, 38), 0x4ade80, axesGroup)
    
    this.axesHelper = axesGroup
    this.scene.add(axesGroup)
  }

  /**
   * Добавление текстовой метки оси
   */
  private addAxisLabel(text: string, position: THREE.Vector3, color: number, parent: THREE.Group) {
    const canvas = document.createElement('canvas')
    canvas.width = 512
    canvas.height = 256
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`
    ctx.font = 'bold 48px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(text, 256, 128)
    
    const texture = new THREE.CanvasTexture(canvas)
    texture.needsUpdate = true
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture })
    const sprite = new THREE.Sprite(spriteMaterial)
    sprite.scale.set(8, 4, 1)
    sprite.position.copy(position)
    parent.add(sprite)
  }

  /**
   * Создание сетки
   */
  private createGrid() {
    if (!this.showGrid) return
    
    // Создаем сетку на плоскости Return-Volatility (плоскость XZ)
    // X = Return, Y = Volatility, Z = Liquidity
    // Сетка должна быть на плоскости Return-Volatility, т.е. горизонтальная плоскость
    const grid = new THREE.GridHelper(100, 20, 0x333333, 0x222222)
    grid.rotation.x = Math.PI / 2 // Поворачиваем на 90 градусов, чтобы сетка была горизонтальной
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
      
      // Определяем цвет по волатильности (mean[1] - это волатильность)
      const volatility = mean[1] || 0
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      
      // Создаем эллипсоид из сферы с масштабированием
      const geometry = new THREE.SphereGeometry(1, 32, 32)
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(regimeColor),
        transparent: true,
        opacity: 0.15,
        side: THREE.DoubleSide,
        emissive: new THREE.Color(regimeColor),
        emissiveIntensity: 0.1
      })

      const ellipsoid = new THREE.Mesh(geometry, material)
      
      // Увеличиваем размер эллипсоидов (увеличиваем множитель с 2 до 4-5)
      const scaleX = Math.sqrt(cov[0][0]) * 4.5
      const scaleY = Math.sqrt(cov[1][1]) * 4.5
      const scaleZ = Math.sqrt(cov[2][2]) * 4.5
      
      ellipsoid.scale.set(scaleX, scaleY, scaleZ)
      // Используем реальные позиции режимов в 3D пространстве
      // mean[0] = Return, mean[1] = Volatility, mean[2] = Liquidity
      ellipsoid.position.set(mean[0], mean[1], mean[2] * 35)
      
      // Wireframe
      const wireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(geometry),
        new THREE.LineBasicMaterial({ 
          color: new THREE.Color(regimeColor), 
          opacity: 0.3, 
          transparent: true 
        })
      )
      wireframe.scale.copy(ellipsoid.scale)
      wireframe.position.copy(ellipsoid.position)
      
      // Добавляем текстовую метку над режимом
      const labelPosition = new THREE.Vector3(mean[0], mean[1] + scaleY + 3, mean[2] * 35)
      const label = this.createRegimeLabel(config.name, labelPosition, regimeColor)
      
      // Создаем маленькие кружки внутри эллипсоида для наблюдений этого режима
      const regimePoints: THREE.Mesh[] = []
      if (this.marketData.length > 0) {
        // Находим все точки траектории, принадлежащие этому режиму
        const regimeObservations = this.marketData
          .slice(0, this.currentTimeIndex + 1)
          .filter(point => (point.regime || 0) === regimeId)
        
        // Ограничиваем количество точек для производительности (максимум 50 на режим)
        const maxPoints = 50
        const step = Math.max(1, Math.floor(regimeObservations.length / maxPoints))
        
        regimeObservations.forEach((point, idx) => {
          // Пропускаем некоторые точки, если их слишком много
          if (idx % step !== 0 && regimeObservations.length > maxPoints) return
          
          const x = point.return
          const y = point.volatility
          const z = point.liquidity * 35
          
          // Создаем маленькую сферу для наблюдения
          const pointGeometry = new THREE.SphereGeometry(0.3, 8, 8)
          const pointMaterial = new THREE.MeshPhongMaterial({
            color: new THREE.Color(regimeColor),
            emissive: new THREE.Color(regimeColor),
            emissiveIntensity: 0.5,
            transparent: true,
            opacity: 0.8,
            shininess: 50
          })
          
          const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial)
          pointMesh.position.set(x, y, z)
          
          // Сохраняем информацию о точке
          pointMesh.userData = {
            regimeId: regimeId,
            point: point,
            timeIndex: idx
          }
          
          regimePoints.push(pointMesh)
        })
      }
      
      const group = new THREE.Group()
      group.add(ellipsoid)
      group.add(wireframe)
      if (label) group.add(label)
      // Добавляем все маленькие кружки в группу
      regimePoints.forEach(point => group.add(point))
      
      this.regimeEllipsoids.push(group)
      this.scene.add(group)
    })
  }

  /**
   * Создание текстовой метки для режима
   */
  private createRegimeLabel(text: string, position: THREE.Vector3, color: string): THREE.Sprite | null {
    try {
      const canvas = document.createElement('canvas')
      canvas.width = 512
      canvas.height = 256
      const ctx = canvas.getContext('2d')
      if (!ctx) return null
      
      ctx.fillStyle = color
      ctx.font = 'bold 36px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(text, 256, 128)
      
      const texture = new THREE.CanvasTexture(canvas)
      texture.needsUpdate = true
      const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        alphaTest: 0.1
      })
      const sprite = new THREE.Sprite(spriteMaterial)
      sprite.scale.set(8, 4, 1)
      sprite.position.copy(position)
      
      return sprite
    } catch (error) {
      console.error('Error creating regime label:', error)
      return null
    }
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

      // Определяем цвет по волатильности
      const volatility = mean[1] || 0
      const regimeColor = this.getRegimeColorByVolatility(volatility)

      const geometry = new THREE.SphereGeometry(1.5, 16, 16)
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(regimeColor),
        emissive: new THREE.Color(regimeColor),
        emissiveIntensity: 0.8,
        transparent: true,
        opacity: 0.9
      })

      const centroid = new THREE.Mesh(geometry, material)
      // Используем реальные позиции режимов в 3D пространстве
      centroid.position.set(mean[0], mean[1], mean[2] * 35)
      centroid.userData = { regimeId, config }

      // Glow effect
      const glowGeometry = new THREE.SphereGeometry(2, 16, 16)
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(regimeColor),
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

    // Масштабирование: Return (x), Volatility (y), Liquidity * 35 (z)
    this.marketData.slice(0, this.currentTimeIndex + 1).forEach((point, i) => {
      const x = point.return
      const y = point.volatility
      const z = point.liquidity * 35

      positions.push(x, y, z)

      // Определяем цвет по волатильности режима
      const regimeId = point.regime || 0
      const config = this.regimeConfigs.find(r => r.id === regimeId)
      
      // Получаем волатильность из mean режима или из самого point
      let volatility = point.volatility
      if (this.hmmModel) {
        const means = this.hmmModel.getEmissionMeans()
        if (means[regimeId] && means[regimeId][1]) {
          volatility = means[regimeId][1]
        }
      }
      
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      const color = new THREE.Color(regimeColor)
      colors.push(color.r, color.g, color.b)
    })

    // Trajectory line - используем кривые вместо прямых линий
    if (this.showTrajectory && positions.length > 1) {
      // Создаем массив точек для кривой
      const points: THREE.Vector3[] = []
      const pointColors: THREE.Color[] = []
      
      for (let i = 0; i < positions.length; i += 3) {
        points.push(new THREE.Vector3(
          positions[i],
          positions[i + 1],
          positions[i + 2]
        ))
        pointColors.push(new THREE.Color(
          colors[i],
          colors[i + 1],
          colors[i + 2]
        ))
      }
      
      // Создаем кривую Catmull-Rom для плавного соединения точек
      const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal')
      
      // Генерируем точки вдоль кривой (больше точек = более плавная кривая)
      const curvePoints = curve.getPoints(Math.max(50, points.length * 10))
      
      // Создаем цвета для каждой точки кривой (интерполируем между узлами)
      const curveColors: number[] = []
      for (let i = 0; i < curvePoints.length; i++) {
        // Находим ближайшие узлы для интерполяции цвета
        const t = i / (curvePoints.length - 1)
        const nodeIndex = Math.min(
          Math.floor(t * (points.length - 1)),
          points.length - 2
        )
        const nextNodeIndex = Math.min(nodeIndex + 1, points.length - 1)
        const localT = (t * (points.length - 1)) - nodeIndex
        
        // Интерполируем цвет между узлами
        const color1 = pointColors[nodeIndex]
        const color2 = pointColors[nextNodeIndex]
        const interpolatedColor = new THREE.Color().lerpColors(color1, color2, localT)
        
        curveColors.push(interpolatedColor.r, interpolatedColor.g, interpolatedColor.b)
      }
      
      // Создаем геометрию для кривой линии
      const curveGeometry = new THREE.BufferGeometry()
      const curvePositions = new Float32Array(curvePoints.length * 3)
      curvePoints.forEach((point, i) => {
        curvePositions[i * 3] = point.x
        curvePositions[i * 3 + 1] = point.y
        curvePositions[i * 3 + 2] = point.z
      })
      
      curveGeometry.setAttribute('position', new THREE.BufferAttribute(curvePositions, 3))
      curveGeometry.setAttribute('color', new THREE.Float32BufferAttribute(curveColors, 3))

      const lineMaterial = new THREE.LineBasicMaterial({
        vertexColors: true,
        transparent: true,
        opacity: 0.6,
        linewidth: 2
      })

      this.trajectoryLine = new THREE.Line(curveGeometry, lineMaterial)
      this.scene.add(this.trajectoryLine)
      
      // Создаем шарики переходов между режимами на кривой
      this.createTransitionMarkers(curve, points)
    }

    // Создаем узлы траектории (маленькие кружки) - конкретные наблюдения рынка
    // Каждый узел - это вектор x_t = (r_t, σ_t, v_t)
    this.trajectoryNodes = []
    this.marketData.slice(0, this.currentTimeIndex + 1).forEach((point, i) => {
      const x = point.return
      const y = point.volatility
      const z = point.liquidity * 35

      // Определяем режим и цвет
      const regimeId = point.regime || 0
      let volatility = point.volatility
      if (this.hmmModel) {
        const means = this.hmmModel.getEmissionMeans()
        if (means[regimeId] && means[regimeId][1]) {
          volatility = means[regimeId][1]
        }
      }
      
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      
      // Вероятность режима для определения размера и прозрачности
      const prob = point.probability && point.probability[regimeId] !== undefined 
        ? point.probability[regimeId] 
        : (point.probability ? Math.max(...point.probability) : 0.5)

      // Создаем маленькую сферу для узла
      const nodeGeometry = new THREE.SphereGeometry(0.4, 12, 12)
      const nodeMaterial = new THREE.MeshPhongMaterial({
        color: new THREE.Color(regimeColor),
        emissive: new THREE.Color(regimeColor),
        emissiveIntensity: 0.3,
        transparent: true,
        opacity: 0.7 + prob * 0.3, // Прозрачность зависит от вероятности
        shininess: 30
      })

      const node = new THREE.Mesh(nodeGeometry, nodeMaterial)
      node.position.set(x, y, z)
      
      // Сохраняем информацию о узле
      node.userData = {
        timeIndex: i,
        regimeId: regimeId,
        point: point,
        probability: prob
      }

      this.trajectoryNodes.push(node)
      this.scene.add(node)
    })
  }

  /**
   * Создание шариков переходов между режимами на кривой траектории
   */
  private createTransitionMarkers(curve: THREE.CatmullRomCurve3, points: THREE.Vector3[]) {
    if (this.marketData.length < 2 || points.length < 2) return
    
    this.transitionMarkers = []
    const visibleData = this.marketData.slice(0, this.currentTimeIndex + 1)
    
    // Находим места, где происходит смена режима
    for (let i = 1; i < visibleData.length; i++) {
      const prevPoint = visibleData[i - 1]
      const currentPoint = visibleData[i]
      
      const prevRegime = prevPoint.regime || 0
      const currentRegime = currentPoint.regime || 0
      
      // Если режим изменился, создаем маркер перехода
      if (prevRegime !== currentRegime) {
        // Вычисляем позицию на кривой между двумя точками
        // Используем параметр t кривой, где t = (i-1) / (points.length - 1) для предыдущей точки
        // и t = i / (points.length - 1) для текущей точки
        // Маркер размещаем посередине между ними
        const t1 = Math.max(0, Math.min(1, (i - 1) / Math.max(1, points.length - 1)))
        const t2 = Math.max(0, Math.min(1, i / Math.max(1, points.length - 1)))
        const t = (t1 + t2) / 2 // Позиция перехода посередине
        
        // Получаем позицию на кривой
        const transitionPosition = curve.getPoint(t)
        
        // Определяем цвета обоих режимов для создания градиента
        let prevVolatility = prevPoint.volatility
        let currentVolatility = currentPoint.volatility
        if (this.hmmModel) {
          const means = this.hmmModel.getEmissionMeans()
          if (means[prevRegime] && means[prevRegime][1]) {
            prevVolatility = means[prevRegime][1]
          }
          if (means[currentRegime] && means[currentRegime][1]) {
            currentVolatility = means[currentRegime][1]
          }
        }
        
        const prevColor = this.getRegimeColorByVolatility(prevVolatility)
        const currentColor = this.getRegimeColorByVolatility(currentVolatility)
        
        // Создаем шарик перехода (белый или золотой для выделения)
        const markerGeometry = new THREE.SphereGeometry(0.6, 16, 16)
        const markerMaterial = new THREE.MeshPhongMaterial({
          color: 0xffffff, // Белый цвет для выделения
          emissive: 0xffd700, // Золотое свечение
          emissiveIntensity: 0.8,
          transparent: true,
          opacity: 0.9,
          shininess: 100
        })
        
        const marker = new THREE.Mesh(markerGeometry, markerMaterial)
        marker.position.copy(transitionPosition)
        
        // Добавляем внешнее свечение (больший полупрозрачный шар)
        const glowGeometry = new THREE.SphereGeometry(0.9, 16, 16)
        const glowMaterial = new THREE.MeshBasicMaterial({
          color: 0xffd700,
          transparent: true,
          opacity: 0.3
        })
        const glow = new THREE.Mesh(glowGeometry, glowMaterial)
        glow.position.copy(transitionPosition)
        
        const markerGroup = new THREE.Group()
        markerGroup.add(marker)
        markerGroup.add(glow)
        
        // Сохраняем информацию о переходе
        markerGroup.userData = {
          fromRegime: prevRegime,
          toRegime: currentRegime,
          timeIndex: i,
          transitionPoint: transitionPosition
        }
        
        this.transitionMarkers.push(markerGroup as any)
        this.scene.add(markerGroup)
      }
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
    this.trajectoryNodes.forEach(node => this.scene.remove(node))
    this.transitionMarkers.forEach(marker => this.scene.remove(marker))
    this.trajectoryNodes = []
    this.transitionMarkers = []
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
    
    // Animate Renaissance overlays
    if (this.renaissanceMode) {
      // Pulsing arbitrage zones
      this.arbitrageZones.forEach((zone, i) => {
        const pulse = Math.sin(Date.now() * 0.002 + i) * 0.2 + 1
        zone.scale.setScalar(pulse)
      })
      
      // Animate probability waves
      this.probabilityWaves.forEach((waveGroup) => {
        waveGroup.children.forEach((child, idx) => {
          if (child instanceof THREE.Mesh && child.material instanceof THREE.MeshBasicMaterial) {
            const baseOpacity = child.userData.baseOpacity || 0.3
            const opacity = baseOpacity * (0.5 + 0.5 * Math.sin(Date.now() * 0.001 + idx))
            child.material.opacity = opacity
          }
        })
      })
      
      // Animate decoding particles
      this.decodingParticles.forEach((particles) => {
        if (particles.userData.velocity) {
          const positions = particles.geometry.attributes.position.array as Float32Array
          const velocities = particles.userData.velocity
          for (let i = 0; i < positions.length; i += 3) {
            positions[i + 1] -= velocities[i / 3] // Move down in Y
            if (positions[i + 1] < -50) {
              positions[i + 1] = 50 // Reset at top
            }
          }
          particles.geometry.attributes.position.needsUpdate = true
        }
      })
      
      // Rotate mean reversion bands
      this.meanReversionBands.forEach((band, i) => {
        if (band.rotation) {
          band.rotation.z += 0.01 * (i % 2 === 0 ? 1 : -1)
        }
      })
    }
    
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

  /**
   * Включение/выключение режима Renaissance Insights
   */
  setRenaissanceMode(enabled: boolean, marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    this.renaissanceMode = enabled
    
    if (enabled) {
      this.createRenaissanceOverlays(marketData, hmmModel, regimeConfigs)
    } else {
      this.clearRenaissanceOverlays()
    }
  }

  /**
   * Установка таймфрейма
   */
  setTimeframe(timeframe: string) {
    this.selectedTimeframe = timeframe
    if (this.renaissanceMode && this.marketData.length > 0 && this.hmmModel) {
      this.clearRenaissanceOverlays()
      this.createRenaissanceOverlays(this.marketData, this.hmmModel, this.regimeConfigs)
    }
  }

  /**
   * Создание всех оверлеев Renaissance
   */
  private createRenaissanceOverlays(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    this.createNonRandomPatterns(marketData, regimeConfigs)
    this.createArbitrageZones(marketData, hmmModel, regimeConfigs)
    this.createMeanReversionBands(marketData, hmmModel, regimeConfigs)
    this.createMomentumArrows(marketData, regimeConfigs)
    this.createSignalMarkers(marketData, hmmModel, regimeConfigs)
    this.createProbabilityWaves(hmmModel, regimeConfigs)
    this.createDecodingEffect(marketData)
    this.createPortfolioHeatmap(marketData, hmmModel, regimeConfigs)
    this.createComparisonOverlay(marketData)
  }

  /**
   * Очистка всех оверлеев Renaissance
   */
  private clearRenaissanceOverlays() {
    this.nonRandomSegments.forEach(obj => this.scene.remove(obj))
    this.arbitrageZones.forEach(obj => this.scene.remove(obj))
    this.meanReversionBands.forEach(obj => this.scene.remove(obj))
    this.momentumArrows.forEach(obj => this.scene.remove(obj))
    this.signalMarkers.forEach(obj => this.scene.remove(obj))
    this.probabilityWaves.forEach(obj => this.scene.remove(obj))
    this.decodingParticles.forEach(obj => this.scene.remove(obj))
    
    if (this.portfolioHeatmap) this.scene.remove(this.portfolioHeatmap)
    if (this.comparisonOverlay) this.scene.remove(this.comparisonOverlay)
    
    this.nonRandomSegments = []
    this.arbitrageZones = []
    this.meanReversionBands = []
    this.momentumArrows = []
    this.signalMarkers = []
    this.probabilityWaves = []
    this.decodingParticles = []
    this.portfolioHeatmap = null
    this.comparisonOverlay = null
  }

  /**
   * Выделение non-random patterns (сегменты траектории с высокой предсказуемостью)
   */
  private createNonRandomPatterns(marketData: MarketPoint[], regimeConfigs: RegimeConfig[]) {
    // Находим сегменты с высокой вероятностью и стабильным режимом
    const windowSize = 10
    for (let i = 0; i < marketData.length - windowSize; i++) {
      const window = marketData.slice(i, i + windowSize)
      const regimeStability = this.calculateRegimeStability(window)
      const predictability = this.calculatePredictability(window)
      
      if (regimeStability > 0.8 && predictability > 0.7) {
        // Создаем highlighted сегмент
        const points: THREE.Vector3[] = []
        window.forEach((point, idx) => {
          points.push(new THREE.Vector3(
            point.return,
            point.volatility,
            point.liquidity * 35
          ))
        })
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points)
        const material = new THREE.LineBasicMaterial({
          color: 0xffff00,
          linewidth: 4,
          transparent: true,
          opacity: 0.8
        })
        
        const line = new THREE.Line(geometry, material)
        const group = new THREE.Group()
        group.add(line)
        
        // Добавляем свечение
        const glowGeometry = new THREE.BufferGeometry().setFromPoints(points)
        const glowMaterial = new THREE.LineBasicMaterial({
          color: 0xffff00,
          linewidth: 6,
          transparent: true,
          opacity: 0.3
        })
        const glow = new THREE.Line(glowGeometry, glowMaterial)
        group.add(glow)
        
        this.nonRandomSegments.push(group)
        this.scene.add(group)
      }
    }
  }

  /**
   * Создание зон статистического арбитража
   */
  private createArbitrageZones(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    const means = hmmModel.getEmissionMeans()
    const transitionMatrix = hmmModel.getTransitionMatrix()
    
    // Зоны с высокой предсказуемостью переходов
    means.forEach((mean, regimeId) => {
      const config = regimeConfigs.find(r => r.id === regimeId)
      if (!config) return
      
      // Определяем цвет по волатильности
      const volatility = mean[1] || 0
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      
      const maxTransitionProb = Math.max(...transitionMatrix[regimeId].filter((_, idx) => idx !== regimeId))
      
      if (maxTransitionProb > 0.3) {
        // Создаем сферическую зону
        const geometry = new THREE.SphereGeometry(5, 16, 16)
        const material = new THREE.MeshBasicMaterial({
          color: new THREE.Color(regimeColor),
          transparent: true,
          opacity: 0.2,
          wireframe: true
        })
        
        const sphere = new THREE.Mesh(geometry, material)
        // Используем реальные позиции режимов
        sphere.position.set(mean[0], mean[1], mean[2] * 35)
        
        // Анимация пульсации
        sphere.userData = { pulse: 0 }
        
        this.arbitrageZones.push(sphere)
        this.scene.add(sphere)
      }
    })
  }

  /**
   * Создание резиновых bands между режимами (mean reversion indicators)
   */
  private createMeanReversionBands(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    const means = hmmModel.getEmissionMeans()
    
    // Создаем bands между соседними режимами
    for (let i = 0; i < means.length; i++) {
      for (let j = i + 1; j < means.length; j++) {
        // Используем реальные позиции режимов
        const mean1 = new THREE.Vector3(means[i][0], means[i][1], means[i][2] * 35)
        const mean2 = new THREE.Vector3(means[j][0], means[j][1], means[j][2] * 35)
        
        const midPoint = new THREE.Vector3().addVectors(mean1, mean2).multiplyScalar(0.5)
        const direction = new THREE.Vector3().subVectors(mean2, mean1).normalize()
        
        // Создаем цилиндр как "резиновую band"
        const geometry = new THREE.CylinderGeometry(0.5, 0.5, mean1.distanceTo(mean2), 8)
        const material = new THREE.MeshBasicMaterial({
          color: 0xffffff,
          transparent: true,
          opacity: 0.15,
          wireframe: true
        })
        
        const cylinder = new THREE.Mesh(geometry, material)
        cylinder.position.copy(midPoint)
        cylinder.lookAt(mean2)
        cylinder.rotateX(Math.PI / 2)
        
        this.meanReversionBands.push(cylinder)
        this.scene.add(cylinder)
      }
    }
  }

  /**
   * Создание стрелок momentum в trending режимах
   */
  private createMomentumArrows(marketData: MarketPoint[], regimeConfigs: RegimeConfig[]) {
    // Находим trending режимы (высокая доходность и низкая волатильность)
    const windowSize = 5
    for (let i = windowSize; i < marketData.length; i++) {
      const window = marketData.slice(i - windowSize, i)
      const avgReturn = window.reduce((sum, p) => sum + p.return, 0) / windowSize
      const avgVol = window.reduce((sum, p) => sum + p.volatility, 0) / windowSize
      
      if (Math.abs(avgReturn) > 0.1 && avgVol < 20) {
        const currentPoint = marketData[i]
        const prevPoint = marketData[i - windowSize]
        
        const direction = new THREE.Vector3(
          currentPoint.return - prevPoint.return,
          currentPoint.volatility - prevPoint.volatility,
          (currentPoint.liquidity - prevPoint.liquidity) * 35
        ).normalize()
        
        const position = new THREE.Vector3(
          currentPoint.return,
          currentPoint.volatility,
          currentPoint.liquidity * 35
        )
        
        const color = avgReturn > 0 ? 0x4ade80 : 0xf87171
        
        const arrow = new THREE.ArrowHelper(
          direction,
          position,
          3,
          color,
          1.5,
          0.8
        )
        
        this.momentumArrows.push(arrow)
        this.scene.add(arrow)
      }
    }
  }

  /**
   * Создание Buy/Sell сигналов
   */
  private createSignalMarkers(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    const transitionMatrix = hmmModel.getTransitionMatrix()
    const means = hmmModel.getEmissionMeans()
    
    for (let i = 1; i < marketData.length; i++) {
      const current = marketData[i]
      const prev = marketData[i - 1]
      
      if (current.regime === undefined || prev.regime === undefined) continue
      
      // Определяем вероятность прибыльного перехода
      const probTransition = transitionMatrix[prev.regime][current.regime]
      const expectedReturn = means[current.regime][0]
      const profitProbability = probTransition * (expectedReturn > 0 ? 1 : 0.5)
      
      if (profitProbability > 0.4) {
        const position = new THREE.Vector3(
          current.return,
          current.volatility,
          current.liquidity * 35
        )
        
        // Buy signal (green) или Sell signal (red)
        const isBuy = expectedReturn > 0
        const color = isBuy ? 0x4ade80 : 0xf87171
        
        const geometry = new THREE.ConeGeometry(0.8, 2, 8)
        const material = new THREE.MeshBasicMaterial({
          color: color,
          transparent: true,
          opacity: 0.7
        })
        
        const marker = new THREE.Mesh(geometry, material)
        marker.position.copy(position)
        marker.lookAt(position.clone().add(new THREE.Vector3(0, isBuy ? 1 : -1, 0)))
        marker.rotateX(-Math.PI / 2)
        
        const group = new THREE.Group()
        group.add(marker)
        
        // Добавляем свечение
        const glowGeometry = new THREE.ConeGeometry(1, 2.5, 8)
        const glowMaterial = new THREE.MeshBasicMaterial({
          color: color,
          transparent: true,
          opacity: 0.2
        })
        const glow = new THREE.Mesh(glowGeometry, glowMaterial)
        glow.position.copy(position)
        glow.lookAt(position.clone().add(new THREE.Vector3(0, isBuy ? 1 : -1, 0)))
        glow.rotateX(-Math.PI / 2)
        group.add(glow)
        
        this.signalMarkers.push(group)
        this.scene.add(group)
      }
    }
  }

  /**
   * Создание probability waves от центроидов
   */
  private createProbabilityWaves(hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    const means = hmmModel.getEmissionMeans()
    
    means.forEach((mean, regimeId) => {
      const config = regimeConfigs.find(r => r.id === regimeId)
      if (!config) return
      
      // Определяем цвет по волатильности
      const volatility = mean[1] || 0
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      
      // Создаем концентрические волны
      for (let ring = 1; ring <= 3; ring++) {
        const geometry = new THREE.RingGeometry(ring * 2, ring * 2.5, 32)
        const material = new THREE.MeshBasicMaterial({
          color: new THREE.Color(regimeColor),
          transparent: true,
          opacity: 0.3 / ring,
          side: THREE.DoubleSide
        })
        
        const wave = new THREE.Mesh(geometry, material)
        // Используем реальные позиции режимов
        wave.position.set(mean[0], mean[1], mean[2] * 35)
        wave.rotation.x = Math.PI / 2
        
        wave.userData = { baseOpacity: 0.3 / ring, ring }
        
        const group = new THREE.Group()
        group.add(wave)
        this.probabilityWaves.push(group)
        this.scene.add(group)
      }
    })
  }

  /**
   * Создание Matrix-style decoding эффекта
   */
  private createDecodingEffect(marketData: MarketPoint[]) {
    // Создаем падающие частицы при смене режима
    const particles: number[] = []
    const colors: number[] = []
    
    for (let i = 1; i < marketData.length; i++) {
      if (marketData[i].regime !== marketData[i - 1].regime) {
        // Смена режима - добавляем частицы
        for (let j = 0; j < 20; j++) {
          const x = marketData[i].return + (Math.random() - 0.5) * 10
          const y = marketData[i].volatility + Math.random() * 5
          const z = marketData[i].liquidity * 35 + (Math.random() - 0.5) * 5
          
          particles.push(x, y, z)
          colors.push(0, 1, 0) // Green matrix code
        }
      }
    }
    
    if (particles.length > 0) {
      const geometry = new THREE.BufferGeometry()
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(particles, 3))
      geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))
      
      const material = new THREE.PointsMaterial({
        size: 0.5,
        vertexColors: true,
        transparent: true,
        opacity: 0.6
      })
      
      const points = new THREE.Points(geometry, material)
      points.userData = { velocity: particles.map(() => Math.random() * 0.1 - 0.05) }
      
      this.decodingParticles.push(points)
      this.scene.add(points)
    }
  }

  /**
   * Создание Portfolio Impact Heatmap
   */
  private createPortfolioHeatmap(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    const means = hmmModel.getEmissionMeans()
    const group = new THREE.Group()
    
    // Создаем heatmap как плоскости для каждого режима
    means.forEach((mean, regimeId) => {
      const config = regimeConfigs.find(r => r.id === regimeId)
      if (!config) return
      
      // Плоскость, показывающая ожидаемую доходность
      const geometry = new THREE.PlaneGeometry(10, 10, 10, 10)
      const expectedReturn = mean[0]
      const heatValue = (expectedReturn + 0.2) / 0.4 // Normalize to 0-1
      
      const material = new THREE.MeshBasicMaterial({
        color: new THREE.Color(
          expectedReturn > 0 ? 0x4ade80 : 0xf87171
        ),
        transparent: true,
        opacity: Math.abs(heatValue) * 0.3,
        side: THREE.DoubleSide
      })
      
      const plane = new THREE.Mesh(geometry, material)
      plane.position.set(mean[0], mean[1] - 5, mean[2] * 35)
      plane.rotation.x = -Math.PI / 2
      
      group.add(plane)
    })
    
    this.portfolioHeatmap = group
    this.scene.add(group)
  }

  /**
   * Создание Comparison Overlay (vs Renaissance benchmark)
   */
  private createComparisonOverlay(marketData: MarketPoint[]) {
    const group = new THREE.Group()
    
    // Создаем визуализацию benchmark performance
    // В реальности это будет сравнение с историческими данными Medallion Fund
    const points: THREE.Vector3[] = []
    
    marketData.forEach((point, i) => {
      // Mock benchmark trajectory (в реальности - данные фонда)
      const benchmarkReturn = point.return * 1.2 // Предполагаем 20% лучше
      points.push(new THREE.Vector3(
        benchmarkReturn,
        point.volatility * 0.9,
        point.liquidity * 35
      ))
    })
    
    if (points.length > 1) {
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      const material = new THREE.LineBasicMaterial({
        color: 0xffd700, // Gold color for benchmark
        transparent: true,
        opacity: 0.4,
        linewidth: 2,
        dashed: true
      })
      
      const line = new THREE.Line(geometry, material)
      group.add(line)
    }
    
    this.comparisonOverlay = group
    this.scene.add(group)
  }

  /**
   * Вспомогательные функции
   */
  private calculateRegimeStability(window: MarketPoint[]): number {
    if (window.length === 0) return 0
    const regimes = window.map(p => p.regime || 0)
    const mode = regimes.sort((a, b) =>
      regimes.filter(v => v === a).length - regimes.filter(v => v === b).length
    ).pop() || 0
    return regimes.filter(r => r === mode).length / window.length
  }

  private calculatePredictability(window: MarketPoint[]): number {
    if (window.length < 2) return 0
    let transitions = 0
    for (let i = 1; i < window.length; i++) {
      if (window[i].regime === window[i - 1].regime) {
        transitions++
      }
    }
    return transitions / (window.length - 1)
  }
}
