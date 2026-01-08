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

export interface HoverInfo {
  type: 'regime' | 'trajectory-node' | 'centroid' | 'ellipsoid'
  title: string
  data: Record<string, any>
  position: [number, number, number]
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
  private regimeSphereRadii: Map<number, number> = new Map() // Радиусы сфер для каждого режима

  // Анимация
  private animationId: number | null = null
  private isAnimating = false
  private autoRotate = false
  private autoAnimationPlaying = false
  private autoAnimationStartTime = 0
  private autoAnimationDuration = 5000 // 5 секунд для полной анимации
  
  // Интерактивность - hover детализация
  private raycaster: THREE.Raycaster | null = null
  private mouse: THREE.Vector2 = new THREE.Vector2()
  private hoveredObject: THREE.Object3D | null = null
  private onHoverCallback: ((info: HoverInfo | null) => void) | null = null

  // Настройки - изначально включены сетка, эллипсоиды и траектория (для анимации)
  private showTrajectory = true
  private showEllipsoids = true
  private showCentroids = false
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
    this.initInteractivity()
    this.animate()
  }

  /**
   * Инициализация сцены
   */
  private initScene() {
    this.scene = new THREE.Scene()
    // Чёрный фон
    this.scene.background = new THREE.Color(0x000000)
    this.scene.fog = new THREE.FogExp2(0x000000, 0.008)
  }

  /**
   * Инициализация камеры
   */
  private initCamera() {
    const width = this.container.clientWidth
    const height = this.container.clientHeight
    this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
    // Позиция камеры для обзора всей сцены (сетка 0-120 по XZ, 0-80 по Y)
    // Центр сцены примерно в (60, 40, 60)
    this.camera.position.set(90, 90, 90)
    this.camera.lookAt(60, 40, 60)
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
    // Устанавливаем target на центр сцены
    this.controls.target.set(60, 40, 60)
    this.controls.update()
  }

  /**
   * Инициализация освещения
   */
  private initLighting() {
    // Ambient light - увеличиваем для более яркой сцены
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    this.scene.add(ambientLight)

    // Directional lights - увеличиваем интенсивность
    const light1 = new THREE.DirectionalLight(0x60a5fa, 0.7)
    light1.position.set(30, 30, 30)
    light1.castShadow = true
    this.scene.add(light1)

    const light2 = new THREE.DirectionalLight(0xa78bfa, 0.5)
    light2.position.set(-30, 30, -30)
    this.scene.add(light2)

    const light3 = new THREE.DirectionalLight(0x4ade80, 0.4)
    light3.position.set(0, -30, 0)
    this.scene.add(light3)
  }

  /**
   * Инициализация интерактивности - hover детализация
   */
  private initInteractivity() {
    this.raycaster = new THREE.Raycaster()
    
    // Обработчики событий мыши
    const onMouseMove = (event: MouseEvent) => {
      if (!this.renderer || !this.camera) return
      
      const rect = this.renderer.domElement.getBoundingClientRect()
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
      
      this.updateHover()
    }
    
    const onMouseOut = () => {
      if (this.hoveredObject) {
        this.hoveredObject = null
        if (this.onHoverCallback) {
          this.onHoverCallback(null)
        }
      }
    }
    
    this.renderer.domElement.addEventListener('mousemove', onMouseMove)
    this.renderer.domElement.addEventListener('mouseout', onMouseOut)
  }

  /**
   * Обновление состояния hover
   * Приоритет: 1) Узлы траектории, 2) Центроиды, 3) Эллипсоиды
   */
  private updateHover() {
    if (!this.raycaster || !this.camera) return
    
    this.raycaster.setFromCamera(this.mouse, this.camera)
    
    // Отдельные проверки для каждого типа объектов с приоритетом
    let finalObject: THREE.Object3D | null = null
    let finalDistance = Infinity
    
    // 1. Приоритет: Узлы траектории (маленькие шарики)
    // Собираем все узлы: из trajectoryNodes и из групп эллипсоидов (regimePoints)
    const allTrajectoryNodes: THREE.Object3D[] = [...this.trajectoryNodes]
    
    // Добавляем узлы из групп эллипсоидов (regimePoints с userData.point)
    this.regimeEllipsoids.forEach(group => {
      group.children.forEach(child => {
        if (child instanceof THREE.Mesh && child.userData.point && !allTrajectoryNodes.includes(child)) {
          allTrajectoryNodes.push(child)
        }
      })
    })
    
    if (allTrajectoryNodes.length > 0) {
      const nodeIntersects = this.raycaster.intersectObjects(allTrajectoryNodes, false)
      if (nodeIntersects.length > 0 && nodeIntersects[0].distance < finalDistance) {
        finalObject = nodeIntersects[0].object
        finalDistance = nodeIntersects[0].distance
      }
    }
    
    // 2. Центроиды (ядра) - только если узел траектории не найден или дальше
    if (this.regimeCentroids.length > 0) {
      const centroidIntersects = this.raycaster.intersectObjects(this.regimeCentroids, false)
      if (centroidIntersects.length > 0 && centroidIntersects[0].distance < finalDistance) {
        finalObject = centroidIntersects[0].object
        finalDistance = centroidIntersects[0].distance
      }
    }
    
    // 3. Эллипсоиды - только если нет более приоритетных объектов поблизости
    // Проверяем только если нет узла или центроида в радиусе 5 единиц
    if (!finalObject || finalDistance > 5) {
      const ellipsoidMeshes: THREE.Object3D[] = []
      this.regimeEllipsoids.forEach(group => {
        group.children.forEach(child => {
          if (child instanceof THREE.Mesh && !(child instanceof THREE.LineSegments)) {
            ellipsoidMeshes.push(child)
          }
        })
      })
      
      if (ellipsoidMeshes.length > 0) {
        const ellipsoidIntersects = this.raycaster.intersectObjects(ellipsoidMeshes, false)
        // Эллипсоид выбираем только если нет более приоритетных объектов
        if (ellipsoidIntersects.length > 0 && !finalObject) {
          finalObject = ellipsoidIntersects[0].object
          finalDistance = ellipsoidIntersects[0].distance
        }
      }
    }
    
    // Обновляем состояние hover
    if (finalObject) {
      if (this.hoveredObject !== finalObject) {
        this.hoveredObject = finalObject
        const info = this.getHoverInfo(finalObject)
        if (this.onHoverCallback) {
          this.onHoverCallback(info)
        }
      }
    } else {
      if (this.hoveredObject) {
        this.hoveredObject = null
        if (this.onHoverCallback) {
          this.onHoverCallback(null)
        }
      }
    }
  }

  /**
   * Получение информации об объекте для hover
   */
  private getHoverInfo(object: THREE.Object3D): HoverInfo | null {
    // Проверяем узлы траектории (включая те, что находятся в группах эллипсоидов)
    // Сначала проверяем прямо в trajectoryNodes
    for (const node of this.trajectoryNodes) {
      if (node === object) {
        return this.createTrajectoryNodeInfo(node)
      }
    }
    
    // Затем проверяем узлы внутри групп эллипсоидов (regimePoints)
    for (const group of this.regimeEllipsoids) {
      for (const child of group.children) {
        if (child === object && child instanceof THREE.Mesh && child.userData.point) {
          return this.createTrajectoryNodeInfo(child)
        }
      }
    }
    
    // Проверяем центроиды
    for (const centroid of this.regimeCentroids) {
      if (centroid === object || (centroid.parent && centroid.parent.children.includes(object))) {
        const userData = centroid.userData
        const config = userData.config as RegimeConfig | undefined
        if (config && this.hmmModel) {
          const means = this.hmmModel.getEmissionMeans()
          const mean = means[config.id]
          return {
            type: 'centroid',
            title: `Ядро режима: ${config.name}`,
            data: {
              'Режим': config.name,
              'Доходность (mean)': mean && mean[0] !== undefined ? (mean[0] * 100).toFixed(2) + '%' : 'N/A',
              'Волатильность (mean)': mean && mean[1] !== undefined ? mean[1].toFixed(2) + '%' : 'N/A',
              'Ликвидность (mean)': mean && mean[2] !== undefined ? mean[2].toFixed(3) : 'N/A',
              'X': centroid.position.x.toFixed(2),
              'Y': centroid.position.y.toFixed(2),
              'Z': centroid.position.z.toFixed(2)
            },
            position: [centroid.position.x, centroid.position.y, centroid.position.z]
          }
        }
      }
    }
    
    // Проверяем эллипсоиды режимов
    for (let i = 0; i < this.regimeEllipsoids.length; i++) {
      const group = this.regimeEllipsoids[i]
      // object может быть группой или mesh внутри группы
      let isThisEllipsoid = false
      let ellipsoidMesh: THREE.Object3D | null = null
      
      if (group === object) {
        isThisEllipsoid = true
        ellipsoidMesh = group.children.find(c => c instanceof THREE.Mesh) || group
      } else {
        for (const child of group.children) {
          if (child === object) {
            isThisEllipsoid = true
            ellipsoidMesh = child
            break
          }
        }
      }
      
      if (isThisEllipsoid && ellipsoidMesh) {
        // Получаем regimeId и config из userData группы
        const regimeId = group.userData?.regimeId ?? i
        const config = group.userData?.config || this.regimeConfigs.find(c => c.id === regimeId)
        if (config && this.hmmModel) {
          const means = this.hmmModel.getEmissionMeans()
          const mean = means[config.id]
          const radius = this.regimeSphereRadii.get(config.id) || 0
          // Позиция эллипсоида на самом mesh, не на группе
          const center = ellipsoidMesh.position.clone()
          if (center.lengthSq() === 0 && group.children[0]) {
            // Если позиция mesh нулевая, берём позицию первого ребенка
            center.copy(group.children[0].position)
          }
          return {
            type: 'ellipsoid',
            title: `Сфера режима: ${config.name}`,
            data: {
              'Режим': config.name,
              'Радиус сферы': radius.toFixed(2),
              'Доходность (mean)': mean && mean[0] !== undefined ? (mean[0] * 100).toFixed(2) + '%' : 'N/A',
              'Волатильность (mean)': mean && mean[1] !== undefined ? mean[1].toFixed(2) + '%' : 'N/A',
              'Ликвидность (mean)': mean && mean[2] !== undefined ? mean[2].toFixed(3) : 'N/A',
              'Позиция X': center.x.toFixed(2),
              'Позиция Y': center.y.toFixed(2),
              'Позиция Z': center.z.toFixed(2),
              'Наблюдений в режиме': String(this.marketData.filter(p => (p.regime || 0) === config.id).length)
            },
            position: [center.x, center.y, center.z]
          }
        }
      }
    }
    
    return null
  }

  /**
   * Создание информации об узле траектории
   */
  private createTrajectoryNodeInfo(node: THREE.Mesh): HoverInfo | null {
    const userData = node.userData
    const point = userData.point as MarketPoint | undefined
    if (!point) return null
    
    return {
      type: 'trajectory-node',
      title: `Наблюдение #${userData.timeIndex ?? 'N/A'}`,
      data: {
        'Индекс': String(userData.timeIndex ?? 0),
        'Режим ID': String(userData.regimeId ?? 0),
        'Дата': point.date || 'N/A',
        'Доходность': point.return !== undefined ? (point.return * 100).toFixed(2) + '%' : 'N/A',
        'Волатильность': point.volatility !== undefined ? point.volatility.toFixed(2) + '%' : 'N/A',
        'Ликвидность': point.liquidity !== undefined ? point.liquidity.toFixed(3) : 'N/A',
        'Режим': this.getRegimeName(userData.regimeId ?? 0),
        'X': node.position.x.toFixed(2),
        'Y': node.position.y.toFixed(2),
        'Z': node.position.z.toFixed(2),
        'point': point
      },
      position: [node.position.x, node.position.y, node.position.z]
    }
  }

  /**
   * Получение названия режима
   */
  private getRegimeName(regimeId: number): string {
    const config = this.regimeConfigs.find(c => c.id === regimeId)
    return config ? config.name : `Режим ${regimeId}`
  }

  /**
   * Установка callback для hover событий
   */
  setOnHover(callback: (info: HoverInfo | null) => void) {
    this.onHoverCallback = callback
  }

  /**
   * Настройка данных
   */
  setData(marketData: MarketPoint[], hmmModel: HMMModel, regimeConfigs: RegimeConfig[]) {
    console.log('RegimeSpaceRenderer.setData called:', {
      marketDataLength: marketData.length,
      hmmModelExists: !!hmmModel,
      regimeConfigsLength: regimeConfigs.length,
      showTrajectory: this.showTrajectory,
      samplePoint: marketData.length > 0 ? marketData[0] : null
    })
    
    this.marketData = marketData
    this.hmmModel = hmmModel
    this.regimeConfigs = regimeConfigs
    this.currentTimeIndex = marketData.length - 1 // Показываем все данные сразу
    this.updateVisualization()
    
    console.log('After updateVisualization:', {
      trajectoryNodesCount: this.trajectoryNodes.length,
      trajectoryLineExists: !!this.trajectoryLine,
      regimeEllipsoidsCount: this.regimeEllipsoids.length
    })
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
    
    this.regimeEllipsoids.forEach(group => this.scene.remove(group))
    // Центроиды находятся в группах, удаляем группы
    this.regimeCentroids.forEach(centroid => {
      if (centroid.parent) {
        this.scene.remove(centroid.parent)
      }
    })
    this.transitionArrows.forEach(arrow => this.scene.remove(arrow))
    
    // Clear Renaissance overlays
    this.clearRenaissanceOverlays()
    
    this.regimeEllipsoids = []
    this.regimeCentroids = []
    this.transitionArrows = []
    this.transitionMarkers = []
  }

  /**
   * Получение X-позиции режима, распределенной равномерно вдоль оси Return
   * Порядок: синий и оранжевый остаются на местах, красный перемещается за синий
   */
  private getRegimeXPosition(regimeId: number): number {
    if (!this.hmmModel) return 0
    const means = this.hmmModel.getEmissionMeans()
    if (!means || !Array.isArray(means)) return 0
    
    // Подсчитываем количество валидных режимов и сортируем по волатильности
    const validRegimes: Array<{ id: number, volatility: number }> = []
    means.forEach((mean, id) => {
      if (mean && Array.isArray(mean) && mean.length >= 3) {
        const volatility = mean[1] !== undefined ? mean[1] : 0
        validRegimes.push({ id, volatility })
      }
    })
    
    if (validRegimes.length === 0) return 0
    
    // Сортируем по волатильности (от низкой к высокой)
    validRegimes.sort((a, b) => a.volatility - b.volatility)
    
    // Определяем порядок: синий (низкая) -> красный (высокая) -> оранжевый (средняя)
    // То есть: индекс 0 (низкая) -> индекс 2 (высокая) -> индекс 1 (средняя)
    const sortedIds = validRegimes.map(r => r.id)
    let positionIndex = sortedIds.indexOf(regimeId)
    
    // Переставляем: красный (высокая волатильность, последний) идет за синий (низкая, первый)
    if (validRegimes.length === 3 && positionIndex === 2) {
      // Красный (высокая волатильность) идет на позицию 1 (за синим)
      positionIndex = 1
    } else if (validRegimes.length === 3 && positionIndex === 1) {
      // Оранжевый (средняя волатильность) идет на позицию 2
      positionIndex = 2
    }
    
    // Распределяем режимы равномерно вдоль оси X с большими интервалами
    // Увеличенный масштаб: от 15 до 100
    const minX = 15
    const maxX = 100
    const spacing = validRegimes.length > 1 ? (maxX - minX) / (validRegimes.length - 1) : 0
    const x = minX + (positionIndex * spacing)
    
    return x
  }

  /**
   * Получение Z-позиции режима, распределенной равномерно вдоль оси Liquidity
   * Порядок: синий и оранжевый остаются на местах, красный перемещается за синий
   */
  private getRegimeZPosition(regimeId: number): number {
    if (!this.hmmModel) return 0
    const means = this.hmmModel.getEmissionMeans()
    if (!means || !Array.isArray(means)) return 0
    
    // Подсчитываем количество валидных режимов и сортируем по волатильности
    const validRegimes: Array<{ id: number, volatility: number }> = []
    means.forEach((mean, id) => {
      if (mean && Array.isArray(mean) && mean.length >= 3) {
        const volatility = mean[1] !== undefined ? mean[1] : 0
        validRegimes.push({ id, volatility })
      }
    })
    
    if (validRegimes.length === 0) return 0
    
    // Сортируем по волатильности (от низкой к высокой)
    validRegimes.sort((a, b) => a.volatility - b.volatility)
    
    // Определяем порядок: синий (низкая) -> красный (высокая) -> оранжевый (средняя)
    // То есть: индекс 0 (низкая) -> индекс 2 (высокая) -> индекс 1 (средняя)
    const sortedIds = validRegimes.map(r => r.id)
    let positionIndex = sortedIds.indexOf(regimeId)
    
    // Переставляем: красный (высокая волатильность, последний) идет за синий (низкая, первый)
    if (validRegimes.length === 3 && positionIndex === 2) {
      // Красный (высокая волатильность) идет на позицию 1 (за синим)
      positionIndex = 1
    } else if (validRegimes.length === 3 && positionIndex === 1) {
      // Оранжевый (средняя волатильность) идет на позицию 2
      positionIndex = 2
    }
    
    // Распределяем режимы равномерно вдоль оси Z с интервалами
    // Увеличенный масштаб: от 15 до 100
    const minZ = 15
    const maxZ = 100
    const spacing = validRegimes.length > 1 ? (maxZ - minZ) / (validRegimes.length - 1) : 0
    const z = minZ + (positionIndex * spacing)
    
    return z
  }

  /**
   * Получение позиции режима в 3D пространстве
   */
  private getRegimePosition(regimeId: number): THREE.Vector3 {
    if (!this.hmmModel) return new THREE.Vector3(0, 0, 0)
    const means = this.hmmModel.getEmissionMeans()
    if (!means || !means[regimeId] || !Array.isArray(means[regimeId])) {
      return new THREE.Vector3(0, 0, 0)
    }
    const mean = means[regimeId]
    // mean[0] = Return, mean[1] = Volatility, mean[2] = Liquidity
    // Переворачиваем диагонально: X и Z меняются местами
    // Только положительное пространство: Y должен быть >= 0
    const x = this.getRegimeZPosition(regimeId)
    const y = Math.max(0, mean[1] !== undefined ? mean[1] : 0) // Гарантируем положительное значение
    const z = this.getRegimeXPosition(regimeId)
    return new THREE.Vector3(x, y, z)
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
   * Создание осей координат (только подписи, без стрелок)
   */
  private createAxes() {
    // Оси теперь отображаются только через подписи вдоль граней сетки
    // Стрелки убраны по запросу пользователя
    this.axesHelper = new THREE.Group()
    this.scene.add(this.axesHelper)
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
    
    const gridGroup = new THREE.Group()
    
    // Материалы для сеток - ярко белые
    const gridMaterial = new THREE.LineBasicMaterial({ 
      color: 0xffffff,
      opacity: 1.0,
      transparent: false
    })
    const gridSecondaryMaterial = new THREE.LineBasicMaterial({ 
      color: 0xffffff,
      opacity: 0.7,
      transparent: true
    })
    
    // Создаем горизонтальную сетку на плоскости XZ (плоскость Liquidity-Return) вручную
    // Увеличенный масштаб (от 0 до 120) для вмещения всех элементов
    const horizontalDivisions = 24
    const horizontalGridSize = 120
    const horizontalStep = horizontalGridSize / horizontalDivisions
    
    // Линии параллельные оси X (Liquidity)
    for (let i = 0; i <= horizontalDivisions; i++) {
      const z = i * horizontalStep
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array([
        0, 0, z,
        horizontalGridSize, 0, z
      ])
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const isMainLine = i % 4 === 0
      const line = new THREE.Line(geometry, isMainLine ? gridMaterial : gridSecondaryMaterial)
      gridGroup.add(line)
    }
    
    // Линии параллельные оси Z (Return)
    for (let i = 0; i <= horizontalDivisions; i++) {
      const x = i * horizontalStep
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array([
        x, 0, 0,
        x, 0, horizontalGridSize
      ])
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const isMainLine = i % 4 === 0
      const line = new THREE.Line(geometry, isMainLine ? gridMaterial : gridSecondaryMaterial)
      gridGroup.add(line)
    }
    
    // Создаем левую вертикальную сетку (плоскость YZ, X = 0)
    const verticalGridSize = 80 // Увеличенная область по Y
    const verticalDivisions = 16
    const verticalStep = verticalGridSize / verticalDivisions
    
    // Вертикальные линии (параллельны Y)
    for (let i = 0; i <= horizontalDivisions; i++) {
      const z = i * horizontalStep
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array([
        0, 0, z,
        0, verticalGridSize, z
      ])
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const line = new THREE.Line(geometry, i % 4 === 0 ? gridMaterial : gridSecondaryMaterial)
      gridGroup.add(line)
    }
    
    // Горизонтальные линии (параллельны Z)
    for (let i = 0; i <= verticalDivisions; i++) {
      const y = i * verticalStep
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array([
        0, y, 0,
        0, y, horizontalGridSize
      ])
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
      const line = new THREE.Line(geometry, i % 4 === 0 ? gridMaterial : gridSecondaryMaterial)
      gridGroup.add(line)
    }
    
    // Названия осей на концах осей
    // Ось X (Return)
    const xAxisLabel = this.createAxisLabelAtEnd('Return', new THREE.Vector3(horizontalGridSize, 5, 10), 0x60a5fa)
    if (xAxisLabel) gridGroup.add(xAxisLabel)
    
    // Ось Y (Volatility)
    const yAxisLabel = this.createAxisLabelAtEnd('Volatility', new THREE.Vector3(5, verticalGridSize, 10), 0xa78bfa)
    if (yAxisLabel) gridGroup.add(yAxisLabel)
    
    // Ось Z (Liquidity)
    const zAxisLabel = this.createAxisLabelAtEnd('Liquidity', new THREE.Vector3(10, 5, horizontalGridSize), 0x4ade80)
    if (zAxisLabel) gridGroup.add(zAxisLabel)
    
    this.gridHelper = gridGroup
    this.scene.add(gridGroup)
  }

  /**
   * Создание длинного названия оси, растянутого вдоль грани сетки
   */
  private createLongAxisLabel(text: string, startPosition: THREE.Vector3, direction: THREE.Vector3, color: number): THREE.Group | null {
    try {
      const group = new THREE.Group()
      const length = direction.length()
      const normalizedDirection = direction.clone().normalize()
      
      // Центральная позиция вдоль грани
      const centerPosition = startPosition.clone().add(normalizedDirection.clone().multiplyScalar(length / 2))
      
      // Создаем большой текст для названия оси
      const canvas = document.createElement('canvas')
      canvas.width = 8192
      canvas.height = 2048
      const ctx = canvas.getContext('2d')
      if (!ctx) return null
      
      ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`
      ctx.font = 'bold 200px Arial' // Увеличиваем размер шрифта
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(text, canvas.width / 2, canvas.height / 2)
      
      const texture = new THREE.CanvasTexture(canvas)
      texture.needsUpdate = true
      const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        alphaTest: 0.1
      })
      
      // Создаем один большой спрайт, растянутый вдоль грани
      // Увеличиваем высоту для лучшей видимости с изометрического вида
      const sprite = new THREE.Sprite(spriteMaterial)
      sprite.scale.set(length * 0.9, 25, 1) // Увеличиваем высоту с 12 до 25
      sprite.position.copy(centerPosition)
      
      // Поднимаем немного выше для лучшей видимости
      if (normalizedDirection.y === 0) {
        sprite.position.y += 2 // Для горизонтальных осей поднимаем выше
      }
      
      // Поворачиваем спрайт вдоль направления
      if (normalizedDirection.x !== 0 || normalizedDirection.z !== 0) {
        const angle = Math.atan2(normalizedDirection.x, normalizedDirection.z)
        sprite.rotation.y = angle
      } else if (normalizedDirection.y !== 0) {
        sprite.rotation.x = Math.PI / 2
      }
      
      group.add(sprite)
      return group
    } catch (error) {
      console.error('Error creating long axis label:', error)
      return null
    }
  }

  /**
   * Создание метки оси на конце оси (ближе к камере)
   */
  private createAxisLabelAtEnd(text: string, position: THREE.Vector3, color: number): THREE.Sprite | null {
    try {
      const canvas = document.createElement('canvas')
      canvas.width = 2048
      canvas.height = 512
      const ctx = canvas.getContext('2d')
      if (!ctx) return null
      
      ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`
      ctx.font = 'bold 120px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(text, canvas.width / 2, canvas.height / 2)
      
      const texture = new THREE.CanvasTexture(canvas)
      texture.needsUpdate = true
      const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        alphaTest: 0.1
      })
      const sprite = new THREE.Sprite(spriteMaterial)
      // Большой размер для видимости с изометрического вида
      sprite.scale.set(20, 5, 1)
      sprite.position.copy(position)
      
      return sprite
    } catch (error) {
      console.error('Error creating axis label at end:', error)
      return null
    }
  }

  /**
   * Создание текстовой метки для сетки
   */
  private createGridLabel(text: string, position: THREE.Vector3, color: number, isTitle: boolean = false, isLarge: boolean = false): THREE.Sprite | null {
    try {
      const canvas = document.createElement('canvas')
      // Увеличиваем размер для больших надписей
      canvas.width = isTitle ? 1024 : (isLarge ? 512 : 256)
      canvas.height = isTitle ? 512 : (isLarge ? 256 : 128)
      const ctx = canvas.getContext('2d')
      if (!ctx) return null
      
      ctx.fillStyle = `#${color.toString(16).padStart(6, '0')}`
      // Увеличиваем размер шрифта для больших надписей
      if (isTitle) {
        ctx.font = 'bold 48px Arial'
      } else if (isLarge) {
        ctx.font = 'bold 36px Arial'
      } else {
        ctx.font = 'bold 20px Arial'
      }
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(text, canvas.width / 2, canvas.height / 2)
      
      const texture = new THREE.CanvasTexture(canvas)
      texture.needsUpdate = true
      const spriteMaterial = new THREE.SpriteMaterial({ 
        map: texture,
        transparent: true,
        alphaTest: 0.1
      })
      const sprite = new THREE.Sprite(spriteMaterial)
      // Увеличиваем масштаб для больших надписей
      if (isTitle) {
        sprite.scale.set(16, 8, 1)
      } else if (isLarge) {
        sprite.scale.set(8, 4, 1)
      } else {
        sprite.scale.set(4, 2, 1)
      }
      sprite.position.copy(position)
      
      return sprite
    } catch (error) {
      console.error('Error creating grid label:', error)
      return null
    }
  }

  /**
   * Создание эллипсоидов режимов
   */
  /**
   * Вычисление радиусов сфер для всех режимов (нужно для центроидов и траекторий)
   */
  private calculateSphereRadii() {
    if (!this.hmmModel) return
    
    this.regimeSphereRadii.clear()
    const covariances = this.hmmModel.getEmissionCovariances()
    
    covariances.forEach((cov, regimeId) => {
      if (!cov || !Array.isArray(cov) || cov.length < 3) return
      if (!cov[0] || !cov[1] || !cov[2]) return
      
      const cov00 = cov[0][0] !== undefined ? cov[0][0] : 1
      const cov11 = cov[1][1] !== undefined ? cov[1][1] : 1
      const cov22 = cov[2][2] !== undefined ? cov[2][2] : 1
      
      const avgStdDev = (Math.sqrt(Math.max(0, cov00)) + 
                         Math.sqrt(Math.max(0, cov11)) + 
                         Math.sqrt(Math.max(0, cov22))) / 3
      
      const sphereRadius = avgStdDev * 4.5
      this.regimeSphereRadii.set(regimeId, sphereRadius)
    })
  }

  private createRegimeEllipsoids() {
    if (!this.hmmModel) return
    
    // Всегда вычисляем радиусы (нужно для центроидов и траекторий)
    this.calculateSphereRadii()
    
    if (!this.showEllipsoids) return

    const means = this.hmmModel.getEmissionMeans()
    const covariances = this.hmmModel.getEmissionCovariances()

    means.forEach((mean, regimeId) => {
      const config = this.regimeConfigs.find(r => r.id === regimeId)
      if (!config) return

      // Проверяем, что mean и cov определены и являются массивами
      if (!mean || !Array.isArray(mean) || mean.length < 3) return
      
      const cov = covariances[regimeId]
      if (!cov || !Array.isArray(cov) || cov.length < 3) return
      if (!cov[0] || !Array.isArray(cov[0]) || cov[0].length < 3) return
      if (!cov[1] || !Array.isArray(cov[1]) || cov[1].length < 3) return
      if (!cov[2] || !Array.isArray(cov[2]) || cov[2].length < 3) return
      
      // Определяем цвет по волатильности (mean[1] - это волатильность)
      const volatility = mean[1] !== undefined ? mean[1] : 0
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      
      // Создаем эллипсоид из сферы с масштабированием
      const geometry = new THREE.SphereGeometry(1, 32, 32)
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(regimeColor),
        transparent: true,
        opacity: 0.5,
        side: THREE.DoubleSide,
        emissive: new THREE.Color(regimeColor),
        emissiveIntensity: 0.5
      })

      const ellipsoid = new THREE.Mesh(geometry, material)
      
      // Делаем каждый режим в виде шара (одинаковый масштаб по всем осям)
      // Используем среднее значение ковариаций для создания сферы
      const cov00 = cov[0][0] !== undefined ? cov[0][0] : 1
      const cov11 = cov[1][1] !== undefined ? cov[1][1] : 1
      const cov22 = cov[2][2] !== undefined ? cov[2][2] : 1
      
      // Вычисляем среднее значение стандартных отклонений для создания шара
      const avgStdDev = (Math.sqrt(Math.max(0, cov00)) + 
                         Math.sqrt(Math.max(0, cov11)) + 
                         Math.sqrt(Math.max(0, cov22))) / 3
      
      // Применяем одинаковый масштаб по всем осям (шар)
      const sphereRadius = this.regimeSphereRadii.get(regimeId) || avgStdDev * 4.5
      ellipsoid.scale.set(sphereRadius, sphereRadius, sphereRadius)
      
      // Используем реальные позиции режимов в 3D пространстве
      // mean[0] = Return, mean[1] = Volatility, mean[2] = Liquidity
      // Переворачиваем диагонально: X и Z меняются местами
      // Только положительное пространство: Y должен быть >= 0
      const x = this.getRegimeZPosition(regimeId)
      const y = Math.max(0, mean[1] !== undefined ? mean[1] : 0) // Гарантируем положительное значение
      const z = this.getRegimeXPosition(regimeId)
      ellipsoid.position.set(x, y, z)
      
      // Wireframe сетка на сфере
      const wireframe = new THREE.LineSegments(
        new THREE.EdgesGeometry(geometry),
        new THREE.LineBasicMaterial({ 
          color: new THREE.Color(regimeColor), 
          opacity: 0.7, 
          transparent: true 
        })
      )
      wireframe.scale.copy(ellipsoid.scale)
      wireframe.position.copy(ellipsoid.position)
      
      // Добавляем текстовую метку над режимом
      const labelPosition = new THREE.Vector3(x, y + sphereRadius + 3, z)
      const label = this.createRegimeLabel(config.name, labelPosition, regimeColor)
      
      // Создаем маленькие кружки внутри эллипсоида для наблюдений этого режима
      const regimePoints: THREE.Mesh[] = []
      if (this.marketData.length > 0) {
        // Находим ВСЕ точки траектории, принадлежащие этому режиму
        const regimeObservations = this.marketData
          .filter(point => (point.regime || 0) === regimeId)
        
        // Ограничиваем количество точек для производительности (максимум 50 на режим)
        const maxPoints = 50
        const step = Math.max(1, Math.floor(regimeObservations.length / maxPoints))
        
        regimeObservations.forEach((point, idx) => {
          // Пропускаем некоторые точки, если их слишком много
          if (idx % step !== 0 && regimeObservations.length > maxPoints) return
          
          // Проверяем, что все значения определены
          if (point.return === undefined || point.volatility === undefined || point.liquidity === undefined) {
            return
          }
          
          // Узлы должны быть ВНУТРИ сферы текущего режима
          const maxRadius = sphereRadius * 0.6
          
          // Вычисляем ненормализованные смещения
          let offsetX = (point.liquidity - 0.5) * 2
          let offsetY = (point.volatility / 60 - 0.5) * 2
          let offsetZ = (point.return * 2.5)
          
          // Нормализуем вектор смещения
          const offsetLength = Math.sqrt(offsetX * offsetX + offsetY * offsetY + offsetZ * offsetZ)
          if (offsetLength > 0) {
            const scale = Math.min(1, 1 / offsetLength) * maxRadius
            offsetX *= scale
            offsetY *= scale
            offsetZ *= scale
          }
          
          // x и z - это позиции сферы режима (уже установлены выше)
          // Ограничиваем координаты границами сетки
          const nodeX = Math.max(5, Math.min(115, x + offsetX))
          const nodeY = Math.max(5, Math.min(75, y + offsetY))
          const nodeZ = Math.max(5, Math.min(115, z + offsetZ))
          
          // Определяем цвет узла по наиболее вероятному режиму
          // Используем regime из point (результат Viterbi-декодирования или сглаживания)
          const nodeRegimeId = point.regime || regimeId
          const nodeConfig = this.regimeConfigs.find(r => r.id === nodeRegimeId)
          let nodeColor = regimeColor
          if (nodeConfig && this.hmmModel) {
            // Получаем цвет по волатильности режима узла
            const means = this.hmmModel.getEmissionMeans()
            if (means && means[nodeRegimeId] && Array.isArray(means[nodeRegimeId])) {
              const nodeVolatility = means[nodeRegimeId][1] !== undefined ? means[nodeRegimeId][1] : point.volatility
              nodeColor = this.getRegimeColorByVolatility(nodeVolatility)
            }
          }
          
          // Создаем маленькую белую сферу для наблюдения (узел траектории)
          // Белый цвет как на картинке для лучшей видимости внутри сфер
          const pointGeometry = new THREE.SphereGeometry(0.8, 12, 12)
          const pointMaterial = new THREE.MeshPhongMaterial({
            color: new THREE.Color(0xffffff), // Белый цвет как на картинке
            emissive: new THREE.Color(0xffffff),
            emissiveIntensity: 0.6,
            transparent: true,
            opacity: 1.0,
            shininess: 100
          })
          
          const pointMesh = new THREE.Mesh(pointGeometry, pointMaterial)
          pointMesh.position.set(nodeX, nodeY, nodeZ)
          
          // Сохраняем информацию о точке
          pointMesh.userData = {
            regimeId: nodeRegimeId,
            point: point,
            timeIndex: idx
          }
          
          regimePoints.push(pointMesh)
        })
      }
      
      const group = new THREE.Group()
      group.userData = { regimeId, config } // Сохраняем regimeId для getHoverInfo
      group.add(ellipsoid)
      group.add(wireframe)
      if (label) group.add(label)
      // Добавляем все маленькие узлы траектории (наблюдения) в группу
      // (hover обрабатывается отдельно через поиск в группах эллипсоидов)
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
   * Центроид - это центр кластера режима, математическое ожидание (mean) эмиссионного распределения
   * Показывает "центр тяжести" режима в пространстве (Return × Volatility × Liquidity)
   * Используется как визуальная точка отсчета для каждого режима, показывает где в среднем находится рынок в этом режиме
   */
  private createRegimeCentroids() {
    if (!this.showCentroids || !this.hmmModel) return

    console.log('createRegimeCentroids called, showCentroids:', this.showCentroids)

    const means = this.hmmModel.getEmissionMeans()

    means.forEach((mean, regimeId) => {
      const config = this.regimeConfigs.find(r => r.id === regimeId)
      if (!config) return

      // Проверяем, что mean определен и является массивом
      if (!mean || !Array.isArray(mean) || mean.length < 3) return

      // Определяем цвет по волатильности
      const volatility = mean[1] !== undefined ? mean[1] : 0
      const regimeColor = this.getRegimeColorByVolatility(volatility)

      // Получаем радиус сферы для этого режима - ядро будет 25% от радиуса
      // Минимальный размер ядра = 3 единицы для видимости
      const sphereRadius = this.regimeSphereRadii.get(regimeId) || 10
      const coreRadius = Math.max(3, sphereRadius * 0.25)
      const glowRadius = Math.max(5, sphereRadius * 0.4)
      
      console.log('Creating centroid for regime', regimeId, 'sphereRadius:', sphereRadius, 'coreRadius:', coreRadius)

      // Ядро сферы - яркое и светящееся
      const geometry = new THREE.SphereGeometry(coreRadius, 24, 24)
      const material = new THREE.MeshPhongMaterial({
        color: new THREE.Color(0xffffff), // Белое ядро
        emissive: new THREE.Color(regimeColor),
        emissiveIntensity: 1.5,
        transparent: true,
        opacity: 1.0,
        shininess: 200,
        depthTest: false // Рендерится поверх других объектов
      })

      const centroid = new THREE.Mesh(geometry, material)
      centroid.renderOrder = 100 // Рендерится после эллипсоидов
      // Позиция в центре сферы
      const x = this.getRegimeZPosition(regimeId)
      const y = Math.max(0, mean[1] !== undefined ? mean[1] : 0)
      const z = this.getRegimeXPosition(regimeId)
      centroid.position.set(x, y, z)
      centroid.userData = { 
        regimeId, 
        config, 
        pulsePhase: Math.random() * Math.PI * 2,
        baseRadius: coreRadius
      }

      // Glow effect - внешнее свечение ядра
      const glowGeometry = new THREE.SphereGeometry(glowRadius, 24, 24)
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(regimeColor),
        transparent: true,
        opacity: 0.4,
        depthTest: false // Рендерится поверх
      })
      const glow = new THREE.Mesh(glowGeometry, glowMaterial)
      glow.renderOrder = 99 // Рендерится перед ядром но после эллипсоидов
      glow.position.copy(centroid.position)
      glow.userData = { 
        baseScale: 1, 
        baseOpacity: 0.3, 
        pulsePhase: Math.random() * Math.PI * 2,
        baseRadius: glowRadius
      }

      const group = new THREE.Group()
      group.add(centroid)
      group.add(glow)
      
      this.regimeCentroids.push(centroid)
      this.scene.add(group)
    })
  }

  /**
   * Создание траектории рынка - соединяет последовательные наблюдения кривыми линиями
   * Показывает путь рынка через пространство режимов и переходы s_t−1 → s_t
   */
  private createTrajectory() {
    console.log('createTrajectory called, marketData.length:', this.marketData.length, 'showTrajectory:', this.showTrajectory)
    
    if (this.marketData.length === 0) return

    // Создаем массив точек для кривой из ВСЕХ наблюдений
    const points: THREE.Vector3[] = []
    const pointColors: THREE.Color[] = []
    const pointRegimes: number[] = []

    // Проходим по ВСЕМ наблюдениям и создаем точки траектории
    // Узлы должны быть ВНУТРИ сфер соответствующих режимов
    this.marketData.forEach((point, i) => {
      // Проверяем, что все значения определены
      if (point.return === undefined || point.volatility === undefined || point.liquidity === undefined) {
        return
      }
      
      // Получаем позицию сферы режима для этого наблюдения
      const regimeId = point.regime || 0
      const regimeX = this.getRegimeZPosition(regimeId)
      const regimeZ = this.getRegimeXPosition(regimeId)
      
      // Получаем Y позицию из волатильности режима
      let regimeY = 15
      if (this.hmmModel) {
        const means = this.hmmModel.getEmissionMeans()
        if (means && means[regimeId] && means[regimeId][1] !== undefined) {
          regimeY = means[regimeId][1]
        }
      }
      
      // Смещения пропорциональны радиусу сферы
      const sphereRadius = this.regimeSphereRadii.get(regimeId) || 10
      const maxRadius = sphereRadius * 0.6 // 60% от радиуса для гарантии нахождения внутри
      
      // Вычисляем ненормализованные смещения
      let offsetX = (point.liquidity - 0.5) * 2
      let offsetY = (point.volatility / 60 - 0.5) * 2
      let offsetZ = (point.return * 2.5)
      
      // Нормализуем вектор смещения, чтобы не выходить за радиус
      const offsetLength = Math.sqrt(offsetX * offsetX + offsetY * offsetY + offsetZ * offsetZ)
      if (offsetLength > 0) {
        const scale = Math.min(1, 1 / offsetLength) * maxRadius
        offsetX *= scale
        offsetY *= scale
        offsetZ *= scale
      }
      
      // Ограничиваем координаты границами сетки (0-115 по XZ, 5-75 по Y)
      const x = Math.max(5, Math.min(115, regimeX + offsetX))
      const y = Math.max(5, Math.min(75, regimeY + offsetY))
      const z = Math.max(5, Math.min(115, regimeZ + offsetZ))

      points.push(new THREE.Vector3(x, y, z))

      // Цвет и режим (regimeId уже определён выше)
      pointRegimes.push(regimeId)
      
      // Получаем волатильность из mean режима или из самого point
      let volatility = point.volatility
      if (this.hmmModel) {
        const means = this.hmmModel.getEmissionMeans()
        if (means && means[regimeId] && Array.isArray(means[regimeId]) && means[regimeId][1] !== undefined) {
          volatility = means[regimeId][1]
        }
      }
      
      const regimeColor = this.getRegimeColorByVolatility(volatility)
      const color = new THREE.Color(regimeColor)
      pointColors.push(color)
    })

    console.log('Trajectory points created:', points.length, 'showTrajectory:', this.showTrajectory)
    if (points.length > 0) {
      console.log('Sample point coordinates:', points[0], points[points.length - 1])
    }

    // Trajectory line - используем кривые вместо прямых линий
    // Соединяем последовательные наблюдения, показывая путь рынка через пространство режимов
    if (this.showTrajectory && points.length > 1) {
      // Проверяем, что есть достаточно точек для создания кривой
      if (points.length < 2) return
      
      // Создаем кривую Catmull-Rom для плавного соединения точек
      // Это создает плавную кривую, проходящую через все узлы (наблюдения)
      const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal')
      
      // Генерируем точки вдоль кривой (больше точек = более плавная кривая)
      // Используем достаточно точек для плавной кривой, показывающей переходы между режимами
      const curvePoints = curve.getPoints(Math.max(100, points.length * 15))
      
      // Создаем цвета для каждой точки кривой (интерполируем между узлами)
      // Цвет показывает переход между режимами s_t−1 → s_t
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
        
        // Интерполируем цвет между узлами, показывая переход между режимами
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
        opacity: 0.9,
        linewidth: 3
      })

      this.trajectoryLine = new THREE.Line(curveGeometry, lineMaterial)
      this.scene.add(this.trajectoryLine)
      
      // Создаем шарики переходов между режимами на кривой
      this.createTransitionMarkers(curve, points)
    }

    // Создаем маленькие белые шарики (узлы) вдоль всей траектории
    // Они отображают конкретные наблюдения рынка в каждый момент времени
    // Эти узлы должны быть видны как внутри сфер режимов, так и между ними
    this.trajectoryNodes = []
    if (this.showTrajectory && points.length > 1) {
      // Создаем узлы вдоль всей траектории - для каждого наблюдения marketData
      this.marketData.forEach((point, i) => {
        if (point.return === undefined || point.volatility === undefined || point.liquidity === undefined) {
          return
        }
        
        // Узлы должны быть внутри сфер режимов - используем позиции сфер
        const nodeRegimeId = point.regime || 0
        const regimeX = this.getRegimeZPosition(nodeRegimeId)
        const regimeZ = this.getRegimeXPosition(nodeRegimeId)
        
        // Получаем Y позицию из волатильности режима
        let regimeY = 15
        if (this.hmmModel) {
          const means = this.hmmModel.getEmissionMeans()
          if (means && means[nodeRegimeId] && means[nodeRegimeId][1] !== undefined) {
            regimeY = means[nodeRegimeId][1]
          }
        }
        
        // Смещения пропорциональны радиусу сферы
        const sphereRadius = this.regimeSphereRadii.get(nodeRegimeId) || 10
        const maxRadius = sphereRadius * 0.6
        
        // Вычисляем ненормализованные смещения
        let offsetX = (point.liquidity - 0.5) * 2
        let offsetY = (point.volatility / 60 - 0.5) * 2
        let offsetZ = (point.return * 2.5)
        
        // Нормализуем вектор смещения
        const offsetLength = Math.sqrt(offsetX * offsetX + offsetY * offsetY + offsetZ * offsetZ)
        if (offsetLength > 0) {
          const scale = Math.min(1, 1 / offsetLength) * maxRadius
          offsetX *= scale
          offsetY *= scale
          offsetZ *= scale
        }
        
        // Ограничиваем координаты границами сетки
        const x = Math.max(5, Math.min(115, regimeX + offsetX))
        const y = Math.max(5, Math.min(75, regimeY + offsetY))
        const z = Math.max(5, Math.min(115, regimeZ + offsetZ))
        
        // Создаем маленькую белую сферу для узла (как на картинке)
        const nodeGeometry = new THREE.SphereGeometry(0.6, 12, 12)
        const nodeMaterial = new THREE.MeshPhongMaterial({
          color: new THREE.Color(0xffffff), // Белый цвет, как на картинке
          emissive: new THREE.Color(0xffffff),
          emissiveIntensity: 0.6,
          transparent: true,
          opacity: 1.0,
          shininess: 100
        })
        
        const node = new THREE.Mesh(nodeGeometry, nodeMaterial)
        node.position.set(x, y, z)
        
        // Сохраняем информацию о узле
        node.userData = {
          timeIndex: i,
          point: point,
          regimeId: point.regime || 0
        }
        
        // Узлы видны по умолчанию
        node.visible = true
        
        this.trajectoryNodes.push(node)
        this.scene.add(node)
      })
      
      console.log('Trajectory nodes created:', this.trajectoryNodes.length)
    }
    
    // Устанавливаем currentTimeIndex на конец данных
    this.currentTimeIndex = this.marketData.length - 1
    
    console.log('createTrajectory finished:', {
      trajectoryLineExists: !!this.trajectoryLine,
      trajectoryNodesCount: this.trajectoryNodes.length
    })
  }
  
  /**
   * Запуск автоматической анимации траектории при загрузке страницы
   * Показывает постепенное появление узлов вдоль траектории
   */
  private startAutoAnimation() {
    if (this.trajectoryNodes.length === 0 || this.autoAnimationPlaying) return
    
    this.autoAnimationPlaying = true
    this.autoAnimationStartTime = Date.now()
    this.currentTimeIndex = 0
    
    // Изначально скрываем все узлы и линию траектории
    this.trajectoryNodes.forEach(node => {
      node.visible = false
    })
    if (this.trajectoryLine) {
      this.scene.remove(this.trajectoryLine)
      this.trajectoryLine = null
    }
    
    // Анимация будет обновляться в методе animate()
  }
  
  /**
   * Обновление автоматической анимации
   */
  private updateAutoAnimation() {
    if (!this.autoAnimationPlaying || this.trajectoryNodes.length === 0) return
    
    const elapsed = Date.now() - this.autoAnimationStartTime
    const progress = Math.min(1, elapsed / this.autoAnimationDuration)
    
    // Вычисляем сколько узлов должно быть видно
    const totalNodes = this.trajectoryNodes.length
    const visibleCount = Math.min(totalNodes - 1, Math.floor(progress * totalNodes))
    
    // Обновляем видимость узлов
    this.trajectoryNodes.forEach((node, i) => {
      const shouldBeVisible = i <= visibleCount
      node.visible = shouldBeVisible
      
      // Добавляем эффект свечения для последнего видимого узла
      if (shouldBeVisible && node.material instanceof THREE.MeshPhongMaterial) {
        if (i === visibleCount) {
          // Активный узел (текущая позиция в анимации) - пульсирует
          const pulse = Math.sin(Date.now() * 0.01) * 0.3 + 0.7
          node.material.emissiveIntensity = 0.8 + pulse * 0.4
          node.scale.setScalar(1 + pulse * 0.3)
        } else {
          // Обычные видимые узлы
          node.material.emissiveIntensity = 0.6
          node.scale.setScalar(1)
        }
      }
    })
    
    // Обновляем текущий индекс времени для траектории
    const newTimeIndex = Math.min(this.marketData.length - 1, visibleCount)
    if (newTimeIndex !== this.currentTimeIndex) {
      this.currentTimeIndex = newTimeIndex
      // Обновляем видимую часть линии траектории (только если есть узлы)
      if (visibleCount > 0) {
        this.createTrajectoryLine()
      }
    }
    
    // Если анимация завершена, останавливаем её
    if (progress >= 1 || visibleCount >= totalNodes - 1) {
      this.autoAnimationPlaying = false
      // Показываем все узлы после завершения анимации
      this.trajectoryNodes.forEach(node => {
        node.visible = true
        if (node.material instanceof THREE.MeshPhongMaterial) {
          node.material.emissiveIntensity = 0.6
          node.scale.setScalar(1)
        }
      })
      this.currentTimeIndex = this.marketData.length - 1
      // Создаем полную линию траектории
      this.createTrajectoryLine()
    }
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
        
        // Проверяем, что позиция валидна
        if (!transitionPosition || 
            transitionPosition.x === undefined || 
            transitionPosition.y === undefined || 
            transitionPosition.z === undefined) {
          continue
        }
        
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
    // Если идет автоматическая анимация, не пересоздаем траекторию полностью
    // Просто обновляем видимую часть
    if (this.autoAnimationPlaying) {
      // Обновляем только видимую часть линии траектории
      if (this.trajectoryLine) {
        this.scene.remove(this.trajectoryLine)
        this.trajectoryLine = null
      }
      this.createTrajectoryLine()
      return
    }
    
    // Полное обновление траектории (когда не идет анимация)
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
   * Создание только линии траектории (без узлов, для анимации)
   */
  private createTrajectoryLine() {
    if (this.marketData.length === 0 || !this.showTrajectory) return
    
    const points: THREE.Vector3[] = []
    const pointColors: THREE.Color[] = []
    
    // Используем ВСЕ данные для линии траектории
    this.marketData.forEach((point, i) => {
      if (point.return === undefined || point.volatility === undefined || point.liquidity === undefined) {
        return
      }
      
      // Узлы траектории внутри сфер режимов
      const lineRegimeId = point.regime || 0
      const regimeX = this.getRegimeZPosition(lineRegimeId)
      const regimeZ = this.getRegimeXPosition(lineRegimeId)
      
      let regimeY = 15
      if (this.hmmModel) {
        const means = this.hmmModel.getEmissionMeans()
        if (means && means[lineRegimeId] && means[lineRegimeId][1] !== undefined) {
          regimeY = means[lineRegimeId][1]
        }
      }
      
      // Смещения пропорциональны радиусу сферы
      const sphereRadius = this.regimeSphereRadii.get(lineRegimeId) || 10
      const maxRadius = sphereRadius * 0.6
      
      // Вычисляем ненормализованные смещения
      let offsetX = (point.liquidity - 0.5) * 2
      let offsetY = (point.volatility / 60 - 0.5) * 2
      let offsetZ = (point.return * 2.5)
      
      // Нормализуем вектор смещения
      const offsetLength = Math.sqrt(offsetX * offsetX + offsetY * offsetY + offsetZ * offsetZ)
      if (offsetLength > 0) {
        const scale = Math.min(1, 1 / offsetLength) * maxRadius
        offsetX *= scale
        offsetY *= scale
        offsetZ *= scale
      }
      
      // Ограничиваем координаты границами сетки
      const x = Math.max(5, Math.min(115, regimeX + offsetX))
      const y = Math.max(5, Math.min(75, regimeY + offsetY))
      const z = Math.max(5, Math.min(115, regimeZ + offsetZ))
      
      points.push(new THREE.Vector3(x, y, z))
      
      // regimeId уже определён выше
      const regimeColor = this.getRegimeColorByVolatility(point.volatility)
      pointColors.push(new THREE.Color(regimeColor))
    })
    
    if (points.length < 2) return
    
    const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal')
    const curvePoints = curve.getPoints(Math.max(100, points.length * 15))
    
    const curveColors: number[] = []
    for (let i = 0; i < curvePoints.length; i++) {
      const t = i / (curvePoints.length - 1)
      const nodeIndex = Math.min(
        Math.floor(t * (points.length - 1)),
        points.length - 2
      )
      const nextNodeIndex = Math.min(nodeIndex + 1, points.length - 1)
      const localT = (t * (points.length - 1)) - nodeIndex
      
      const color1 = pointColors[nodeIndex]
      const color2 = pointColors[nextNodeIndex]
      const interpolatedColor = new THREE.Color().lerpColors(color1, color2, localT)
      
      curveColors.push(interpolatedColor.r, interpolatedColor.g, interpolatedColor.b)
    }
    
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
      opacity: 0.9,
      linewidth: 3
    })
    
    this.trajectoryLine = new THREE.Line(curveGeometry, lineMaterial)
    this.scene.add(this.trajectoryLine)
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
    
    // Обновление hover интерактивности
    if (this.raycaster) {
      this.updateHover()
    }
    
    // Обновление автоматической анимации траектории
    if (this.autoAnimationPlaying) {
      this.updateAutoAnimation()
    }
    
    // Auto-rotate
    if (this.autoRotate) {
      // Already handled by OrbitControls
    }
    
    // Пульсирующие ядра сфер (центроиды)
    const time = Date.now() * 0.001
    this.regimeCentroids.forEach((centroid, idx) => {
      if (!centroid || !centroid.parent) return
      
      // Усиленная пульсация ядра - быстрее и заметнее
      if (centroid.userData.pulsePhase !== undefined) {
        // Пульсация размера: от 0.7 до 1.3 (±30%)
        const pulse = Math.sin(time * 3 + centroid.userData.pulsePhase) * 0.3 + 1
        centroid.scale.setScalar(pulse)
        
        // Пульсация свечения - яркий эффект "биения сердца"
        if (centroid.material instanceof THREE.MeshPhongMaterial) {
          const intensity = 0.8 + Math.sin(time * 4 + centroid.userData.pulsePhase) * 0.5
          centroid.material.emissiveIntensity = intensity
          // Пульсация яркости цвета
          centroid.material.opacity = 0.8 + Math.sin(time * 3 + centroid.userData.pulsePhase) * 0.15
        }
      }
      
      // Пульсация glow эффекта - расширяющееся свечение
      const glow = centroid.parent.children.find(child => child !== centroid && child.type === 'Mesh') as THREE.Mesh | undefined
      if (glow && glow.userData.pulsePhase !== undefined) {
        // Более сильная пульсация свечения: от 0.5 до 1.5
        const glowPulse = Math.sin(time * 2.5 + glow.userData.pulsePhase + Math.PI/4) * 0.5 + 1
        const baseScale = glow.userData.baseScale || 1
        glow.scale.setScalar(baseScale * glowPulse)
        
        if (glow.material instanceof THREE.MeshBasicMaterial) {
          // Пульсация прозрачности свечения
          const baseOpacity = glow.userData.baseOpacity || 0.3
          const opacityPulse = Math.sin(time * 2.5 + glow.userData.pulsePhase) * 0.15 + baseOpacity
          glow.material.opacity = Math.max(0.15, Math.min(0.6, opacityPulse))
        }
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
        // Учитываем диагональное отражение и гарантируем положительные значения
        const points: THREE.Vector3[] = []
        window.forEach((point, idx) => {
          if (point.return === undefined || point.volatility === undefined || point.liquidity === undefined) {
            return
          }
          // Диагональное отражение: X и Z поменяны местами, только положительные значения
          const x = Math.max(0, point.liquidity * 35)
          const y = Math.max(0, point.volatility)
          const z = Math.max(0, point.return)
          points.push(new THREE.Vector3(x, y, z))
        })
        
        if (points.length < 2) return
        
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
        // Переворачиваем диагонально: X и Z меняются местами
        const x = this.getRegimeZPosition(regimeId)
        const y = Math.max(0, mean[1] !== undefined ? mean[1] : 0) // Гарантируем положительное значение
        const z = this.getRegimeXPosition(regimeId)
        sphere.position.set(x, y, z)
        
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
        // Используем реальные позиции режимов с учетом диагонального отражения
        // Только положительное пространство
        const x1 = this.getRegimeZPosition(i)
        const y1 = Math.max(0, means[i][1] !== undefined ? means[i][1] : 0)
        const z1 = this.getRegimeXPosition(i)
        const mean1 = new THREE.Vector3(x1, y1, z1)
        
        const x2 = this.getRegimeZPosition(j)
        const y2 = Math.max(0, means[j][1] !== undefined ? means[j][1] : 0)
        const z2 = this.getRegimeXPosition(j)
        const mean2 = new THREE.Vector3(x2, y2, z2)
        
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
        
        if (currentPoint.return === undefined || currentPoint.volatility === undefined || currentPoint.liquidity === undefined) continue
        if (prevPoint.return === undefined || prevPoint.volatility === undefined || prevPoint.liquidity === undefined) continue
        
        // Учитываем диагональное отражение и гарантируем положительные значения
        const currX = Math.max(0, currentPoint.liquidity * 35)
        const currY = Math.max(0, currentPoint.volatility)
        const currZ = Math.max(0, currentPoint.return)
        
        const prevX = Math.max(0, prevPoint.liquidity * 35)
        const prevY = Math.max(0, prevPoint.volatility)
        const prevZ = Math.max(0, prevPoint.return)
        
        const direction = new THREE.Vector3(
          currX - prevX,
          currY - prevY,
          currZ - prevZ
        ).normalize()
        
        const position = new THREE.Vector3(currX, currY, currZ)
        
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
        if (current.return === undefined || current.volatility === undefined || current.liquidity === undefined) continue
        
        // Учитываем диагональное отражение и гарантируем положительные значения
        const x = Math.max(0, current.liquidity * 35)
        const y = Math.max(0, current.volatility)
        const z = Math.max(0, current.return)
        
        const position = new THREE.Vector3(x, y, z)
        
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
        // Переворачиваем диагонально: X и Z меняются местами
        // Только положительное пространство: Y должен быть >= 0
        const x = this.getRegimeZPosition(regimeId)
        const y = Math.max(0, mean[1] !== undefined ? mean[1] : 0) // Гарантируем положительное значение
        const z = this.getRegimeXPosition(regimeId)
        wave.position.set(x, y, z)
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
        if (marketData[i].return === undefined || marketData[i].volatility === undefined || marketData[i].liquidity === undefined) continue
        
        // Учитываем диагональное отражение и гарантируем положительные значения
        const baseX = Math.max(0, marketData[i].liquidity * 35)
        const baseY = Math.max(0, marketData[i].volatility)
        const baseZ = Math.max(0, marketData[i].return)
        
        for (let j = 0; j < 20; j++) {
          const x = baseX + (Math.random() - 0.5) * 10
          const y = baseY + Math.random() * 5
          const z = baseZ + (Math.random() - 0.5) * 5
          
          particles.push(Math.max(0, x), Math.max(0, y), Math.max(0, z))
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
      // Переворачиваем диагонально: X и Z меняются местами
      // Только положительное пространство: Y должен быть >= 0
      const x = this.getRegimeZPosition(regimeId)
      const y = Math.max(0, mean[1] !== undefined ? mean[1] : 0) - 5 // Гарантируем положительное значение
      const z = this.getRegimeXPosition(regimeId)
      plane.position.set(x, y, z)
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
      if (point.return === undefined || point.volatility === undefined || point.liquidity === undefined) {
        return
      }
      
      // Учитываем диагональное отражение и гарантируем положительные значения
      const benchmarkReturn = Math.max(0, point.return * 1.2) // Предполагаем 20% лучше
      const x = Math.max(0, point.liquidity * 35)
      const y = Math.max(0, point.volatility * 0.9)
      const z = Math.max(0, benchmarkReturn)
      
      points.push(new THREE.Vector3(x, y, z))
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
