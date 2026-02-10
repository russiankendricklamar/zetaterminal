<template>
  <div class="kb-root" ref="rootRef">
    <!-- Three.js Canvas -->
    <canvas ref="canvasRef" class="kb-canvas"></canvas>

    <!-- Noise Overlay -->
    <div class="bg-noise"></div>

    <!-- Cursor Glow -->
    <div
      class="cursor-glow"
      :style="{
        left: `${mousePos.x}px`,
        top: `${mousePos.y}px`,
        opacity: isMouseInside ? 1 : 0
      }"
    ></div>

    <!-- Main Content -->
    <div class="kb-content">
      <!-- Header -->
      <header class="kb-header">
        <div class="kb-logo" @click="$router.push('/')">
          <span class="logo-symbol font-anton">ζ</span>
          <span class="logo-text font-oswald">STOCHASTIC</span>
        </div>

        <nav class="kb-nav">
          <button
            v-for="cat in categories"
            :key="cat.id"
            @click="activeCategory = cat.id"
            :class="['nav-btn font-mono', { active: activeCategory === cat.id }]"
          >
            {{ cat.name }}
          </button>
        </nav>

        <router-link to="/terminal" class="terminal-btn font-oswald">
          ТЕРМИНАЛ →
        </router-link>
      </header>

      <!-- Hero Section -->
      <section class="kb-hero">
        <div class="hero-badge font-mono">
          <span class="badge-dot"></span>
          KNOWLEDGE BASE v2.0
        </div>

        <h1 class="hero-title font-anton">
          <span class="title-line">БАЗА</span>
          <span class="title-line accent">ЗНАНИЙ</span>
        </h1>

        <p class="hero-subtitle font-mono">
          {{ totalItems }} документов · {{ categories.length }} категорий · Интерактивное исследование
        </p>

        <!-- Search -->
        <div class="search-container">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск по базе знаний..."
              class="search-input font-mono"
              @focus="isSearchFocused = true"
              @blur="isSearchFocused = false"
            />
            <div class="search-shortcut font-mono">⌘K</div>
          </div>

          <!-- Search Results -->
          <div v-if="searchQuery && filteredItems.length" class="search-results custom-scrollbar">
            <div
              v-for="item in filteredItems.slice(0, 8)"
              :key="item.id"
              class="search-result"
              @click="openItem(item)"
            >
              <div class="result-icon" :style="{ background: getCategoryColor(item.category) }">
                {{ item.title.charAt(0) }}
              </div>
              <div class="result-info">
                <span class="result-title font-oswald">{{ item.title }}</span>
                <span class="result-category font-mono">{{ getCategoryName(item.category) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Categories Grid -->
      <section class="kb-categories">
        <div
          v-for="(cat, index) in categories"
          :key="cat.id"
          class="category-card"
          :class="{ expanded: activeCategory === cat.id }"
          :style="{ '--delay': `${index * 0.1}s`, '--accent': cat.color }"
          @click="toggleCategory(cat.id)"
        >
          <div class="card-header">
            <div class="card-icon" :style="{ background: cat.color }">
              <component :is="cat.icon" />
            </div>
            <div class="card-meta">
              <h3 class="card-title font-oswald">{{ cat.name }}</h3>
              <span class="card-count font-mono">{{ getCategoryItems(cat.id).length }} элементов</span>
            </div>
            <div class="card-expand">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline :points="activeCategory === cat.id ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"></polyline>
              </svg>
            </div>
          </div>

          <p class="card-desc font-mono">{{ cat.description }}</p>

          <!-- Expanded Items -->
          <div v-if="activeCategory === cat.id" class="card-items custom-scrollbar">
            <div
              v-for="item in getCategoryItems(cat.id)"
              :key="item.id"
              class="item-row"
              @click.stop="openItem(item)"
            >
              <span class="item-code font-mono">{{ item.code }}</span>
              <span class="item-title font-oswald">{{ item.title }}</span>
              <span class="item-arrow">→</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Stats Bar -->
      <section class="kb-stats">
        <div class="stat-item" v-for="stat in stats" :key="stat.label">
          <span class="stat-value font-anton">{{ stat.value }}</span>
          <span class="stat-label font-mono">{{ stat.label }}</span>
        </div>
      </section>

      <!-- Footer -->
      <footer class="kb-footer">
        <div class="footer-left">
          <span class="font-mono">© 2026 STOCHASTIC PLATFORM</span>
        </div>
        <div class="footer-right">
          <router-link to="/" class="footer-link font-mono">Главная</router-link>
          <router-link to="/terminal" class="footer-link font-mono">Терминал</router-link>
        </div>
      </footer>
    </div>

    <!-- Detail Modal -->
    <Teleport to="body">
      <div v-if="selectedItem" class="modal-overlay" @click="selectedItem = null">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="selectedItem = null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <div class="modal-header">
            <span class="modal-badge font-mono" :style="{ background: getCategoryColor(selectedItem.category) }">
              {{ getCategoryName(selectedItem.category) }}
            </span>
            <h2 class="modal-title font-anton">{{ selectedItem.title }}</h2>
            <p class="modal-code font-mono">{{ selectedItem.code }}</p>
          </div>

          <div class="modal-body custom-scrollbar">
            <div class="modal-section" v-if="selectedItem.description">
              <h4 class="section-title font-oswald">Описание</h4>
              <p class="section-text font-mono">{{ selectedItem.description }}</p>
            </div>

            <div class="modal-section" v-if="selectedItem.formula">
              <h4 class="section-title font-oswald">Формула</h4>
              <code class="formula-code font-mono">{{ selectedItem.formula }}</code>
            </div>

            <div class="modal-section formula-explanation" v-if="selectedItem.formulaExplanation">
              <h4 class="section-title font-oswald">Объяснение</h4>
              <pre class="explanation-text font-mono">{{ selectedItem.formulaExplanation }}</pre>
            </div>

            <div class="modal-section" v-if="selectedItem.features?.length">
              <h4 class="section-title font-oswald">Функции</h4>
              <ul class="feature-list">
                <li v-for="(f, i) in selectedItem.features" :key="i" class="font-mono">{{ f }}</li>
              </ul>
            </div>

            <div class="modal-section" v-if="selectedItem.howToUse?.length">
              <h4 class="section-title font-oswald">Как использовать</h4>
              <ol class="howto-list">
                <li v-for="(step, i) in selectedItem.howToUse" :key="i" class="font-mono">{{ step }}</li>
              </ol>
            </div>

            <div class="modal-section" v-if="selectedItem.path">
              <h4 class="section-title font-oswald">Путь</h4>
              <code class="path-code font-mono">{{ selectedItem.path }}</code>
            </div>
          </div>

          <div class="modal-footer">
            <router-link
              v-if="selectedItem.path"
              :to="selectedItem.path"
              class="modal-btn primary font-oswald"
            >
              Открыть страницу →
            </router-link>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, defineComponent, h } from 'vue'
import * as THREE from 'three'
import {
  categories as dataCategories,
  items as dataItems,
  getCategoryItems as getDataCategoryItems,
  searchItems as dataSearchItems,
  type KnowledgeItem,
  type Category as DataCategory
} from '@/data/knowledgeBaseData'

// Extended Category with icon component
interface Category extends DataCategory {
  icon: any
}

// Refs
const rootRef = ref<HTMLElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const mousePos = ref({ x: 0, y: 0 })
const isMouseInside = ref(false)
const searchQuery = ref('')
const isSearchFocused = ref(false)
const activeCategory = ref<string | null>(null)
const selectedItem = ref<KnowledgeItem | null>(null)

// Icons
const PortfolioIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z' }),
    h('polyline', { points: '3.27 6.96 12 12.01 20.73 6.96' }),
    h('line', { x1: '12', y1: '22.08', x2: '12', y2: '12' })
  ])
})

const RiskIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z' }),
    h('line', { x1: '12', y1: '9', x2: '12', y2: '13' }),
    h('line', { x1: '12', y1: '17', x2: '12.01', y2: '17' })
  ])
})

const PricingIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('line', { x1: '12', y1: '1', x2: '12', y2: '23' }),
    h('path', { d: 'M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6' })
  ])
})

const TerminalIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('polyline', { points: '4 17 10 11 4 5' }),
    h('line', { x1: '12', y1: '19', x2: '20', y2: '19' })
  ])
})

const AnalyticsIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('line', { x1: '18', y1: '20', x2: '18', y2: '10' }),
    h('line', { x1: '12', y1: '20', x2: '12', y2: '4' }),
    h('line', { x1: '6', y1: '20', x2: '6', y2: '14' })
  ])
})

const ModelsIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('polygon', { points: '12 2 2 7 12 12 22 7 12 2' }),
    h('polyline', { points: '2 17 12 22 22 17' }),
    h('polyline', { points: '2 12 12 17 22 12' })
  ])
})

const RegimesIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('path', { d: 'M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z' })
  ])
})

const SimulationIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('path', { d: 'M2 20h.01' }),
    h('path', { d: 'M7 20v-4' }),
    h('path', { d: 'M12 20v-8' }),
    h('path', { d: 'M17 20V8' }),
    h('path', { d: 'M22 4v16' })
  ])
})

const SwapsIcon = defineComponent({
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
    h('polyline', { points: '17 1 21 5 17 9' }),
    h('path', { d: 'M3 5h18' }),
    h('polyline', { points: '7 23 3 19 7 15' }),
    h('path', { d: 'M21 19H3' })
  ])
})

// Icon mapping for categories
const iconMap: Record<string, any> = {
  'options': PricingIcon,
  'bonds': AnalyticsIcon,
  'swaps': SwapsIcon,
  'risk': RiskIcon,
  'simulation': SimulationIcon,
  'regimes': RegimesIcon,
  'portfolio': PortfolioIcon,
  'terminal': TerminalIcon
}

// Build categories with icons from data
const categories = computed<Category[]>(() =>
  dataCategories.map(cat => ({
    ...cat,
    icon: iconMap[cat.id] || ModelsIcon
  }))
)

// Items from data
const items = computed(() => dataItems)

const stats = computed(() => [
  { value: items.value.length + '+', label: 'Документов' },
  { value: categories.value.length, label: 'Категорий' },
  { value: items.value.filter(i => i.formula).length + '+', label: 'Формул' },
  { value: '37+', label: 'Страниц' },
])

const totalItems = computed(() => items.value.length)

const filteredItems = computed(() => {
  if (!searchQuery.value) return []
  return dataSearchItems(searchQuery.value)
})

const getCategoryItems = (catId: string) => getDataCategoryItems(catId)
const getCategoryColor = (catId: string) => categories.value.find(c => c.id === catId)?.color || '#666'
const getCategoryName = (catId: string) => categories.value.find(c => c.id === catId)?.name || ''

const toggleCategory = (catId: string) => {
  activeCategory.value = activeCategory.value === catId ? null : catId
}

const openItem = (item: KnowledgeItem) => {
  selectedItem.value = item
}

// Three.js Particle System
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let particles: THREE.Points
let particlePositions: Float32Array
let particleVelocities: Float32Array
let particleSizes: Float32Array
let animationId: number
let mouseWorld = new THREE.Vector3()

const PARTICLE_COUNT = 3000

const initThreeJS = () => {
  if (!canvasRef.value) return

  // Scene
  scene = new THREE.Scene()

  // Camera
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = 50

  // Renderer
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    alpha: true,
    antialias: true
  })
  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  // Particles
  const geometry = new THREE.BufferGeometry()
  particlePositions = new Float32Array(PARTICLE_COUNT * 3)
  particleVelocities = new Float32Array(PARTICLE_COUNT * 3)
  particleSizes = new Float32Array(PARTICLE_COUNT)
  const colors = new Float32Array(PARTICLE_COUNT * 3)

  const colorPalette = [
    new THREE.Color('#DC2626'), // Red
    new THREE.Color('#22c55e'), // Green
    new THREE.Color('#3b82f6'), // Blue
    new THREE.Color('#f59e0b'), // Orange
    new THREE.Color('#8b5cf6'), // Purple
    new THREE.Color('#06b6d4'), // Cyan
    new THREE.Color('#ffffff'), // White
  ]

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const i3 = i * 3

    // Position - spread across the screen
    particlePositions[i3] = (Math.random() - 0.5) * 150
    particlePositions[i3 + 1] = (Math.random() - 0.5) * 100
    particlePositions[i3 + 2] = (Math.random() - 0.5) * 80

    // Velocity
    particleVelocities[i3] = (Math.random() - 0.5) * 0.02
    particleVelocities[i3 + 1] = (Math.random() - 0.5) * 0.02
    particleVelocities[i3 + 2] = (Math.random() - 0.5) * 0.01

    // Size
    particleSizes[i] = Math.random() * 2 + 0.5

    // Color
    const color = colorPalette[Math.floor(Math.random() * colorPalette.length)]
    colors[i3] = color.r
    colors[i3 + 1] = color.g
    colors[i3 + 2] = color.b
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(particleSizes, 1))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  // Shader Material
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector3() },
    },
    vertexShader: `
      attribute float size;
      attribute vec3 color;
      varying vec3 vColor;
      varying float vAlpha;
      uniform float uTime;
      uniform vec3 uMouse;

      void main() {
        vColor = color;

        vec3 pos = position;

        // Mouse interaction
        float dist = distance(pos.xy, uMouse.xy);
        float influence = smoothstep(30.0, 0.0, dist);

        // Repel from mouse
        vec2 dir = normalize(pos.xy - uMouse.xy + 0.001);
        pos.xy += dir * influence * 8.0;

        // Subtle wave motion
        pos.x += sin(uTime * 0.5 + position.y * 0.1) * 0.3;
        pos.y += cos(uTime * 0.3 + position.x * 0.1) * 0.3;

        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;

        vAlpha = 1.0 - influence * 0.5;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        float dist = length(gl_PointCoord - vec2(0.5));
        if (dist > 0.5) discard;

        float alpha = smoothstep(0.5, 0.1, dist) * vAlpha;
        gl_FragColor = vec4(vColor, alpha * 0.8);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  })

  particles = new THREE.Points(geometry, material)
  scene.add(particles)

  animate()
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  const time = performance.now() * 0.001

  // Update uniforms
  const material = particles.material as THREE.ShaderMaterial
  material.uniforms.uTime.value = time
  material.uniforms.uMouse.value = mouseWorld

  // Update particle positions
  const positions = particles.geometry.attributes.position.array as Float32Array

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const i3 = i * 3

    positions[i3] += particleVelocities[i3]
    positions[i3 + 1] += particleVelocities[i3 + 1]
    positions[i3 + 2] += particleVelocities[i3 + 2]

    // Bounds check
    if (positions[i3] > 75) positions[i3] = -75
    if (positions[i3] < -75) positions[i3] = 75
    if (positions[i3 + 1] > 50) positions[i3 + 1] = -50
    if (positions[i3 + 1] < -50) positions[i3 + 1] = 50
  }

  particles.geometry.attributes.position.needsUpdate = true

  // Subtle rotation
  particles.rotation.y = time * 0.02
  particles.rotation.x = Math.sin(time * 0.1) * 0.05

  renderer.render(scene, camera)
}

const handleMouseMove = (e: MouseEvent) => {
  mousePos.value = { x: e.clientX, y: e.clientY }

  // Convert to 3D coordinates
  const x = (e.clientX / window.innerWidth) * 2 - 1
  const y = -(e.clientY / window.innerHeight) * 2 + 1
  mouseWorld.set(x * 50, y * 30, 0)
}

const handleMouseEnter = () => { isMouseInside.value = true }
const handleMouseLeave = () => { isMouseInside.value = false }

const handleResize = () => {
  if (!renderer || !camera) return
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
}

const handleKeydown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    const input = document.querySelector('.search-input') as HTMLInputElement
    input?.focus()
  }
  if (e.key === 'Escape') {
    selectedItem.value = null
    searchQuery.value = ''
  }
}

onMounted(() => {
  initThreeJS()

  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('resize', handleResize)
  window.addEventListener('keydown', handleKeydown)

  if (rootRef.value) {
    rootRef.value.addEventListener('mouseenter', handleMouseEnter)
    rootRef.value.addEventListener('mouseleave', handleMouseLeave)
  }
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) renderer.dispose()

  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* ============================================
   ROOT & CANVAS
   ============================================ */
.kb-root {
  min-height: 100vh;
  background: #030303;
  color: #f5f5f5;
  position: relative;
  overflow-x: hidden;
}

.kb-canvas {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.bg-noise {
  position: fixed;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

.cursor-glow {
  position: fixed;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(220, 38, 38, 0.15) 0%, transparent 70%);
  pointer-events: none;
  transform: translate(-50%, -50%);
  z-index: 3;
  transition: opacity 0.3s;
}

/* ============================================
   CONTENT LAYER
   ============================================ */
.kb-content {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ============================================
   HEADER
   ============================================ */
.kb-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  background: rgba(3, 3, 3, 0.7);
  position: sticky;
  top: 0;
  z-index: 100;
}

.kb-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-symbol {
  width: 40px;
  height: 40px;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #000;
}

.logo-text {
  font-size: 14px;
  letter-spacing: 0.2em;
  color: #f5f5f5;
}

.kb-nav {
  display: flex;
  gap: 8px;
}

.nav-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #737373;
  font-size: 11px;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  border-color: #DC2626;
  color: #f5f5f5;
}

.nav-btn.active {
  background: #DC2626;
  border-color: #DC2626;
  color: #000;
}

.terminal-btn {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid #DC2626;
  color: #DC2626;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-decoration: none;
  transition: all 0.2s;
}

.terminal-btn:hover {
  background: #DC2626;
  color: #000;
}

/* ============================================
   HERO
   ============================================ */
.kb-hero {
  padding: 120px 40px 80px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: #DC2626;
  font-size: 11px;
  letter-spacing: 0.15em;
  margin-bottom: 32px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #DC2626;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.hero-title {
  font-size: clamp(4rem, 15vw, 12rem);
  line-height: 0.85;
  margin: 0;
  text-transform: uppercase;
}

.title-line {
  display: block;
  color: #f5f5f5;
}

.title-line.accent {
  color: #DC2626;
  -webkit-text-stroke: 2px #DC2626;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 14px;
  color: #525252;
  margin-top: 24px;
  letter-spacing: 0.1em;
}

/* ============================================
   SEARCH
   ============================================ */
.search-container {
  width: 100%;
  max-width: 600px;
  margin-top: 48px;
  position: relative;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(10, 10, 10, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.2s;
}

.search-box:focus-within {
  border-color: #DC2626;
  box-shadow: 0 0 30px rgba(220, 38, 38, 0.2);
}

.search-icon {
  width: 20px;
  height: 20px;
  color: #525252;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #f5f5f5;
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: #404040;
}

.search-shortcut {
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  color: #525252;
}

.search-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  background: rgba(10, 10, 10, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-height: 400px;
  overflow-y: auto;
  backdrop-filter: blur(20px);
}

.search-result {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result:hover {
  background: rgba(220, 38, 38, 0.1);
}

.result-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #000;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.result-title {
  font-size: 14px;
  color: #f5f5f5;
}

.result-category {
  font-size: 11px;
  color: #525252;
}

/* ============================================
   CATEGORIES
   ============================================ */
.kb-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
  padding: 60px 40px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.category-card {
  background: rgba(10, 10, 10, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  animation: fadeInUp 0.6s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.category-card:hover {
  border-color: var(--accent);
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.category-card.expanded {
  border-color: var(--accent);
  background: rgba(10, 10, 10, 0.9);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
}

.card-icon svg {
  width: 24px;
  height: 24px;
}

.card-meta {
  flex: 1;
}

.card-title {
  font-size: 18px;
  color: #f5f5f5;
  margin: 0;
  letter-spacing: 0.1em;
}

.card-count {
  font-size: 11px;
  color: #525252;
}

.card-expand {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
}

.card-expand svg {
  width: 16px;
  height: 16px;
  color: #525252;
  transition: transform 0.3s;
}

.category-card:hover .card-expand {
  border-color: var(--accent);
}

.category-card:hover .card-expand svg {
  color: var(--accent);
}

.card-desc {
  font-size: 13px;
  color: #525252;
  margin: 16px 0 0;
  line-height: 1.5;
}

.card-items {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  max-height: 300px;
  overflow-y: auto;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  transition: all 0.2s;
}

.item-row:hover {
  padding-left: 12px;
  background: rgba(255, 255, 255, 0.02);
}

.item-row:last-child {
  border-bottom: none;
}

.item-code {
  font-size: 11px;
  color: var(--accent);
  min-width: 50px;
}

.item-title {
  flex: 1;
  font-size: 14px;
  color: #a3a3a3;
}

.item-row:hover .item-title {
  color: #f5f5f5;
}

.item-arrow {
  color: #525252;
  opacity: 0;
  transition: all 0.2s;
}

.item-row:hover .item-arrow {
  opacity: 1;
  transform: translateX(4px);
  color: var(--accent);
}

/* ============================================
   STATS
   ============================================ */
.kb-stats {
  display: flex;
  justify-content: center;
  gap: 64px;
  padding: 60px 40px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(10, 10, 10, 0.5);
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: clamp(2rem, 5vw, 4rem);
  color: #DC2626;
  display: block;
}

.stat-label {
  font-size: 12px;
  color: #525252;
  letter-spacing: 0.1em;
  margin-top: 8px;
}

/* ============================================
   FOOTER
   ============================================ */
.kb-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 40px;
  margin-top: auto;
}

.footer-left {
  font-size: 12px;
  color: #404040;
}

.footer-right {
  display: flex;
  gap: 24px;
}

.footer-link {
  font-size: 12px;
  color: #525252;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: #DC2626;
}

/* ============================================
   MODAL
   ============================================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  width: 100%;
  max-width: 700px;
  max-height: 85vh;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #525252;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  border-color: #DC2626;
  color: #DC2626;
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-header {
  padding: 32px 32px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-badge {
  display: inline-block;
  padding: 4px 12px;
  font-size: 10px;
  letter-spacing: 0.1em;
  color: #000;
  margin-bottom: 16px;
}

.modal-title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  color: #f5f5f5;
  margin: 0;
  letter-spacing: 0.05em;
}

.modal-code {
  font-size: 12px;
  color: #525252;
  margin-top: 8px;
}

.modal-body {
  padding: 24px 32px;
  overflow-y: auto;
  flex: 1;
}

.modal-section {
  margin-bottom: 24px;
}

.modal-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  color: #DC2626;
  margin: 0 0 12px;
  letter-spacing: 0.1em;
}

.section-text {
  font-size: 14px;
  color: #a3a3a3;
  line-height: 1.6;
  margin: 0;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  padding: 8px 0;
  font-size: 13px;
  color: #a3a3a3;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  gap: 12px;
}

.feature-list li::before {
  content: '→';
  color: #DC2626;
}

.feature-list li:last-child {
  border-bottom: none;
}

.path-code {
  display: block;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 13px;
  color: #22c55e;
}

.formula-code {
  display: block;
  padding: 16px 20px;
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.2);
  font-size: 15px;
  color: #f87171;
  white-space: pre-wrap;
  line-height: 1.6;
}

.formula-explanation {
  max-height: 300px;
  overflow-y: auto;
}

.explanation-text {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 12px;
  color: #a3a3a3;
  white-space: pre-wrap;
  line-height: 1.7;
  margin: 0;
  overflow-x: auto;
}

.howto-list {
  list-style: none;
  padding: 0;
  margin: 0;
  counter-reset: step-counter;
}

.howto-list li {
  padding: 12px 0 12px 40px;
  font-size: 13px;
  color: #a3a3a3;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  position: relative;
  counter-increment: step-counter;
}

.howto-list li::before {
  content: counter(step-counter);
  position: absolute;
  left: 0;
  top: 12px;
  width: 24px;
  height: 24px;
  background: rgba(220, 38, 38, 0.2);
  border: 1px solid rgba(220, 38, 38, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #DC2626;
}

.howto-list li:last-child {
  border-bottom: none;
}

.modal-footer {
  padding: 24px 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.modal-btn {
  display: inline-block;
  padding: 12px 24px;
  font-size: 14px;
  text-decoration: none;
  letter-spacing: 0.1em;
  transition: all 0.2s;
}

.modal-btn.primary {
  background: #DC2626;
  color: #000;
  border: 1px solid #DC2626;
}

.modal-btn.primary:hover {
  background: transparent;
  color: #DC2626;
}

/* ============================================
   SCROLLBAR
   ============================================ */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .kb-header {
    padding: 16px 24px;
  }

  .kb-nav {
    display: none;
  }

  .kb-hero {
    padding: 80px 24px 60px;
  }

  .kb-categories {
    padding: 40px 24px;
    grid-template-columns: 1fr;
  }

  .kb-stats {
    gap: 32px;
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .kb-header {
    flex-wrap: wrap;
    gap: 16px;
  }

  .terminal-btn {
    width: 100%;
    text-align: center;
    order: 3;
  }

  .hero-title {
    font-size: clamp(3rem, 20vw, 6rem);
  }

  .search-shortcut {
    display: none;
  }

  .kb-stats {
    padding: 40px 24px;
  }

  .kb-footer {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .category-card {
    padding: 16px;
  }

  .card-icon {
    width: 40px;
    height: 40px;
  }

  .card-title {
    font-size: 16px;
  }

  .modal-content {
    max-height: 90vh;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding-left: 20px;
    padding-right: 20px;
  }
}
</style>
