/**
 * Three.js renderer for WAVE_σ.9 market momentum surface visualization
 */

import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { MarketRegime } from './types'
import { noise, getHeatmapColor } from './mathUtils'

// Grid Settings
const WIDTH = 50
const HEIGHT = 50
const SEGMENTS_W = 60
const SEGMENTS_H = 60

export type SignalCallback = (signal: number, volatility: number) => void

/**
 * Class for rendering 3D wave surface
 */
export class WaveSigmaRenderer {
  private scene!: THREE.Scene
  private camera!: THREE.PerspectiveCamera
  private renderer!: THREE.WebGLRenderer
  private controls!: OrbitControls
  private container: HTMLElement

  // 3D objects
  private mesh: THREE.Mesh | null = null
  private wireframeMesh: THREE.Mesh | null = null
  private geometry: THREE.PlaneGeometry | null = null
  private colors: Float32Array | null = null

  // Animation state
  private animationId: number | null = null
  private isAnimating = false
  private time = 0

  // Regime
  private regime: MarketRegime = MarketRegime.TRENDING

  // Signal callback
  private onSignal: SignalCallback | null = null

  constructor(container: HTMLElement, onSignal?: SignalCallback) {
    this.container = container
    this.onSignal = onSignal || null
    this.initScene()
    this.initCamera()
    this.initRenderer()
    this.initControls()
    this.initLighting()
    this.initSurface()
    this.animate()
  }

  /**
   * Initialize scene
   */
  private initScene(): void {
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x050505)
  }

  /**
   * Initialize camera
   */
  private initCamera(): void {
    const width = this.container.clientWidth
    const height = this.container.clientHeight
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
    this.camera.position.set(0, 25, 40)
    this.camera.lookAt(0, 0, 0)
  }

  /**
   * Initialize renderer
   */
  private initRenderer(): void {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    })
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.container.appendChild(this.renderer.domElement)
  }

  /**
   * Initialize orbit controls
   */
  private initControls(): void {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.05
    this.controls.enablePan = false
    this.controls.enableZoom = true
    this.controls.maxPolarAngle = Math.PI / 2
    this.controls.minPolarAngle = 0
    this.controls.autoRotate = true
    this.controls.autoRotateSpeed = 0.5
  }

  /**
   * Initialize lighting
   */
  private initLighting(): void {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
    this.scene.add(ambientLight)

    const pointLight = new THREE.PointLight(0xffffff, 1)
    pointLight.position.set(10, 10, 10)
    this.scene.add(pointLight)
  }

  /**
   * Initialize surface mesh
   */
  private initSurface(): void {
    this.geometry = new THREE.PlaneGeometry(WIDTH, HEIGHT, SEGMENTS_W, SEGMENTS_H)

    // Initialize colors attribute
    const vertexCount = (SEGMENTS_W + 1) * (SEGMENTS_H + 1)
    this.colors = new Float32Array(vertexCount * 3)
    this.geometry.setAttribute('color', new THREE.BufferAttribute(this.colors, 3))

    // Main surface material
    const material = new THREE.MeshBasicMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.8
    })

    this.mesh = new THREE.Mesh(this.geometry, material)
    this.mesh.rotation.x = -Math.PI / 2.5
    this.mesh.position.y = -5
    this.scene.add(this.mesh)

    // Wireframe overlay
    const wireframeMaterial = new THREE.MeshBasicMaterial({
      wireframe: true,
      color: 0xffffff,
      transparent: true,
      opacity: 0.15,
      depthWrite: false
    })

    this.wireframeMesh = new THREE.Mesh(this.geometry, wireframeMaterial)
    this.wireframeMesh.rotation.x = -Math.PI / 2.5
    this.wireframeMesh.position.y = -5
    this.scene.add(this.wireframeMesh)
  }

  /**
   * Update surface geometry based on time and regime
   */
  private updateSurface(delta: number): void {
    if (!this.geometry || !this.colors) return

    const posAttr = this.geometry.getAttribute('position') as THREE.BufferAttribute
    const colAttr = this.geometry.getAttribute('color') as THREE.BufferAttribute
    if (!posAttr || !colAttr) return

    // Slow down time for the simulation
    const dt = delta * 1.5
    this.time += dt
    const t = this.time

    const positions = posAttr.array as Float32Array
    const colorAttrib = colAttr.array as Float32Array
    const count = posAttr.count
    const tempColor = { r: 0, g: 0, b: 0 }

    let centerSignal = 0
    let totalVolatility = 0

    for (let i = 0; i < count; i++) {
      const x = positions[i * 3]
      const y = positions[i * 3 + 1]

      // Calculate effective coordinate in the "infinite" stream
      const streamY = y - t * 4

      // Base rolling wave
      let z = Math.sin(x * 0.2 + streamY * 0.2) * 2

      // Regime specific logic
      const ridge = Math.exp(-Math.pow(x * 0.15, 2)) * 12
      const chop = (noise(x * 0.8 + streamY) + noise(x * 1.5 - streamY * 1.5) * 0.5) * 3

      if (this.regime === MarketRegime.TRENDING) {
        z += ridge * 1.5
        z += chop * 0.2
      } else {
        z += ridge * 0.2
        z += chop * 2.5
      }

      z += Math.sin(Math.sqrt(x * x + y * y) - t * 5) * 0.5

      // Update Position Z
      positions[i * 3 + 2] = z

      // Update Color based on Z height
      const normHeight = (z + 5) / 20
      getHeatmapColor(normHeight, tempColor)

      colorAttrib[i * 3] = tempColor.r
      colorAttrib[i * 3 + 1] = tempColor.g
      colorAttrib[i * 3 + 2] = tempColor.b

      // Sample leading edge (approx center of the grid's far edge)
      if (Math.abs(y - HEIGHT / 2) < 1 && Math.abs(x) < 1) {
        centerSignal = z
      }
      if (Math.abs(y - HEIGHT / 2) < 1) {
        totalVolatility += Math.abs(z)
      }
    }

    // Mark attributes as needing update
    posAttr.needsUpdate = true
    colAttr.needsUpdate = true

    // Emit signal
    const normalizedPosition = Math.max(-1, Math.min(1, (centerSignal - 5) / 10))
    if (this.onSignal) {
      this.onSignal(normalizedPosition, totalVolatility)
    }
  }

  /**
   * Animation loop
   */
  private animate = (): void => {
    if (!this.isAnimating) {
      this.isAnimating = true
    }

    this.animationId = requestAnimationFrame(this.animate)

    // Update surface with fixed delta for consistency
    this.updateSurface(0.016) // ~60fps

    // Update controls
    this.controls.update()

    // Render
    this.renderer.render(this.scene, this.camera)
  }

  /**
   * Set market regime
   */
  public setRegime(regime: MarketRegime): void {
    this.regime = regime
  }

  /**
   * Get current regime
   */
  public getRegime(): MarketRegime {
    return this.regime
  }

  /**
   * Handle window resize
   */
  public resize(): void {
    const width = this.container.clientWidth
    const height = this.container.clientHeight

    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
  }

  /**
   * Dispose of all resources
   */
  public dispose(): void {
    this.isAnimating = false

    if (this.animationId !== null) {
      cancelAnimationFrame(this.animationId)
      this.animationId = null
    }

    // Dispose geometry
    if (this.geometry) {
      this.geometry.dispose()
    }

    // Dispose materials
    if (this.mesh) {
      const material = this.mesh.material as THREE.Material
      material.dispose()
      this.scene.remove(this.mesh)
    }

    if (this.wireframeMesh) {
      const material = this.wireframeMesh.material as THREE.Material
      material.dispose()
      this.scene.remove(this.wireframeMesh)
    }

    // Dispose controls
    this.controls.dispose()

    // Dispose renderer
    this.renderer.dispose()
    if (this.renderer.domElement.parentNode) {
      this.renderer.domElement.parentNode.removeChild(this.renderer.domElement)
    }
  }
}

/**
 * Composable for using WaveSigmaRenderer in Vue components
 */
export function useWaveSigma3D() {
  let renderer: WaveSigmaRenderer | null = null

  const init = (container: HTMLElement, onSignal?: SignalCallback): WaveSigmaRenderer => {
    renderer = new WaveSigmaRenderer(container, onSignal)
    return renderer
  }

  const dispose = (): void => {
    if (renderer) {
      renderer.dispose()
      renderer = null
    }
  }

  const setRegime = (regime: MarketRegime): void => {
    if (renderer) {
      renderer.setRegime(regime)
    }
  }

  const resize = (): void => {
    if (renderer) {
      renderer.resize()
    }
  }

  return {
    init,
    dispose,
    setRegime,
    resize,
    getRenderer: () => renderer
  }
}
