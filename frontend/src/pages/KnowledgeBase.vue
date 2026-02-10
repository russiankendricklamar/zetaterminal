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
        opacity: isMouseInside ? 1 : 0,
        background: hoveredCluster ? `radial-gradient(circle, ${hoveredCluster.color}30 0%, transparent 70%)` : undefined
      }"
    ></div>

    <!-- Cluster Labels (HTML overlay) -->
    <div
      v-for="cluster in clusterLabels"
      :key="cluster.id"
      class="cluster-label"
      :class="{ active: activeCategory === cluster.id, hovered: hoveredCluster?.id === cluster.id }"
      :style="{
        left: `${cluster.x}px`,
        top: `${cluster.y}px`,
        '--accent': cluster.color,
        opacity: cluster.visible ? 1 : 0,
        pointerEvents: cluster.visible ? 'auto' : 'none'
      }"
      @click="selectCluster(cluster.id)"
    >
      <div class="label-dot" :style="{ background: cluster.color }"></div>
      <span class="label-text font-oswald">{{ cluster.name }}</span>
      <span class="label-count font-mono">{{ cluster.count }}</span>
    </div>

    <!-- Header -->
    <header class="kb-header">
      <div class="kb-logo" @click="$router.push('/')">
        <span class="logo-symbol font-anton">ζ</span>
        <span class="logo-text font-oswald">STOCHASTIC</span>
      </div>

      <div class="header-center">
        <span class="header-title font-mono">KNOWLEDGE BASE</span>
        <span class="header-version font-mono">v3.0</span>
      </div>

      <div class="header-actions">
        <button class="search-trigger" @click="showSearch = true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <path d="m21 21-4.35-4.35"></path>
          </svg>
          <span class="font-mono">⌘K</span>
        </button>
        <router-link to="/terminal" class="terminal-btn font-oswald">
          ТЕРМИНАЛ →
        </router-link>
      </div>
    </header>

    <!-- Hero (only when no category selected) -->
    <section v-if="!activeCategory" class="kb-hero">
      <div class="hero-badge font-mono">
        <span class="badge-dot"></span>
        INTERACTIVE GALAXY
      </div>

      <h1 class="hero-title font-anton">
        <span class="title-line">БАЗА</span>
        <span class="title-line accent">ЗНАНИЙ</span>
      </h1>

      <p class="hero-subtitle font-mono">
        {{ totalItems }} документов · {{ categories.length }} созвездий · Кликните на скопление для навигации
      </p>

      <div class="hero-hint font-mono">
        Выберите категорию ниже или используйте ⌘K для поиска
      </div>
    </section>

    <!-- Category Panel (slides from right when active) -->
    <Teleport to="body">
      <Transition name="panel">
        <div v-if="activeCategory" class="category-panel" @click.self="closePanel">
          <div class="panel-content custom-scrollbar">
            <button class="panel-close" @click="closePanel">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>

            <div class="panel-header" :style="{ '--accent': activeCategoryData?.color }">
              <div class="panel-icon" :style="{ background: activeCategoryData?.color }">
                <component :is="activeCategoryData?.icon" />
              </div>
              <div class="panel-meta">
                <h2 class="panel-title font-anton">{{ activeCategoryData?.name }}</h2>
                <p class="panel-desc font-mono">{{ activeCategoryData?.longDescription }}</p>
              </div>
            </div>

            <div class="panel-items">
              <div
                v-for="item in getCategoryItems(activeCategory)"
                :key="item.id"
                class="panel-item"
                @click="openItem(item)"
              >
                <div class="item-header">
                  <span class="item-code font-mono" :style="{ color: activeCategoryData?.color }">{{ item.code }}</span>
                  <span class="item-title font-oswald">{{ item.title }}</span>
                </div>
                <p class="item-desc font-mono">{{ item.description?.slice(0, 100) }}...</p>
                <div class="item-tags">
                  <span v-if="item.formula" class="item-tag formula font-mono">Формула</span>
                  <span v-if="item.path" class="item-tag path font-mono">Страница</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Search Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showSearch" class="search-overlay" @click.self="showSearch = false">
          <div class="search-modal">
            <div class="search-box">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по базе знаний..."
                class="search-input font-mono"
                @keydown.escape="showSearch = false"
              />
            </div>

            <div v-if="filteredItems.length" class="search-results custom-scrollbar">
              <div
                v-for="item in filteredItems.slice(0, 10)"
                :key="item.id"
                class="search-result"
                @click="openItem(item); showSearch = false"
              >
                <div class="result-icon" :style="{ background: getCategoryColor(item.category) }">
                  {{ item.code.slice(0, 2) }}
                </div>
                <div class="result-info">
                  <span class="result-title font-oswald">{{ item.title }}</span>
                  <span class="result-category font-mono">{{ getCategoryName(item.category) }}</span>
                </div>
              </div>
            </div>

            <div v-else-if="searchQuery" class="search-empty font-mono">
              Ничего не найдено
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Detail Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="selectedItem" class="modal-overlay" @click.self="selectedItem = null">
          <div class="modal-content custom-scrollbar">
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

            <div class="modal-body">
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
            </div>

            <div class="modal-footer" v-if="selectedItem.path">
              <router-link :to="selectedItem.path" class="modal-btn primary font-oswald">
                Открыть страницу →
              </router-link>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Category Navigation Bar -->
    <nav class="kb-nav-bar" v-if="!activeCategory">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="nav-category"
        :style="{ '--accent': cat.color }"
        @click="selectCluster(cat.id)"
      >
        <span class="nav-dot" :style="{ background: cat.color }"></span>
        <span class="nav-name font-oswald">{{ cat.name }}</span>
        <span class="nav-count font-mono">{{ getCategoryItems(cat.id).length }}</span>
      </button>
    </nav>

    <!-- Stats Footer -->
    <footer class="kb-footer" v-if="!activeCategory">
      <div class="footer-stats">
        <div class="stat-item" v-for="stat in stats" :key="stat.label">
          <span class="stat-value font-anton">{{ stat.value }}</span>
          <span class="stat-label font-mono">{{ stat.label }}</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, defineComponent, h, nextTick } from 'vue'
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

interface ClusterLabel {
  id: string
  name: string
  count: number
  color: string
  x: number
  y: number
  visible: boolean
}

// Refs
const rootRef = ref<HTMLElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)
const mousePos = ref({ x: 0, y: 0 })
const isMouseInside = ref(false)
const searchQuery = ref('')
const showSearch = ref(false)
const activeCategory = ref<string | null>(null)
const selectedItem = ref<KnowledgeItem | null>(null)
const hoveredCluster = ref<{ id: string; color: string } | null>(null)
const clusterLabels = ref<ClusterLabel[]>([])

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
    icon: iconMap[cat.id] || PortfolioIcon
  }))
)

const activeCategoryData = computed(() =>
  categories.value.find(c => c.id === activeCategory.value)
)

// Items from data
const items = computed(() => dataItems)

const stats = computed(() => [
  { value: items.value.length + '+', label: 'Документов' },
  { value: categories.value.length, label: 'Созвездий' },
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

const selectCluster = (clusterId: string) => {
  activeCategory.value = clusterId
}

const closePanel = () => {
  activeCategory.value = null
}

const openItem = (item: KnowledgeItem) => {
  selectedItem.value = item
}

// Three.js Galaxy System
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animationId: number
let mouseWorld = new THREE.Vector3()
let raycaster = new THREE.Raycaster()
let mouse = new THREE.Vector2()

interface ClusterData {
  id: string
  name: string
  color: THREE.Color
  center: THREE.Vector3
  particles: THREE.Points
  count: number
}

let clusters: ClusterData[] = []
const PARTICLES_PER_CLUSTER = 300
const BACKGROUND_PARTICLES = 1500

const initThreeJS = () => {
  if (!canvasRef.value) return

  // Scene
  scene = new THREE.Scene()

  // Camera
  camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000)
  camera.position.z = 100

  // Renderer
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    alpha: true,
    antialias: true
  })
  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  // Create category clusters
  const clusterPositions = [
    { x: -50, y: 30 },   // Top left
    { x: 0, y: 40 },     // Top center
    { x: 50, y: 30 },    // Top right
    { x: -40, y: -5 },   // Middle left
    { x: 40, y: -5 },    // Middle right
    { x: -50, y: -35 },  // Bottom left
    { x: 0, y: -40 },    // Bottom center
    { x: 50, y: -35 },   // Bottom right
  ]

  categories.value.forEach((cat, index) => {
    const pos = clusterPositions[index % clusterPositions.length]
    const cluster = createCluster(cat, pos.x, pos.y, index)
    clusters.push(cluster)
    scene.add(cluster.particles)
  })

  // Background stars
  createBackgroundStars()

  // Update labels initially
  updateClusterLabels()

  animate()
}

const createCluster = (category: Category, x: number, y: number, index: number): ClusterData => {
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(PARTICLES_PER_CLUSTER * 3)
  const sizes = new Float32Array(PARTICLES_PER_CLUSTER)
  const colors = new Float32Array(PARTICLES_PER_CLUSTER * 3)
  const randoms = new Float32Array(PARTICLES_PER_CLUSTER)

  const color = new THREE.Color(category.color)
  const center = new THREE.Vector3(x, y, (Math.random() - 0.5) * 20)

  // Spiral galaxy shape
  for (let i = 0; i < PARTICLES_PER_CLUSTER; i++) {
    const i3 = i * 3

    // Spiral arm pattern
    const angle = (i / PARTICLES_PER_CLUSTER) * Math.PI * 6 + index * 0.5
    const radius = 3 + (i / PARTICLES_PER_CLUSTER) * 12 + Math.random() * 3
    const armOffset = Math.sin(angle * 2) * 2

    positions[i3] = center.x + Math.cos(angle) * radius + armOffset + (Math.random() - 0.5) * 4
    positions[i3 + 1] = center.y + Math.sin(angle) * radius * 0.6 + (Math.random() - 0.5) * 3
    positions[i3 + 2] = center.z + (Math.random() - 0.5) * 8

    // Size variation
    const distFromCenter = Math.sqrt(
      Math.pow(positions[i3] - center.x, 2) +
      Math.pow(positions[i3 + 1] - center.y, 2)
    )
    sizes[i] = Math.max(0.5, 3 - distFromCenter * 0.15) * (0.5 + Math.random() * 0.5)

    // Color with variation
    const brightness = 0.7 + Math.random() * 0.3
    colors[i3] = color.r * brightness
    colors[i3 + 1] = color.g * brightness
    colors[i3 + 2] = color.b * brightness

    randoms[i] = Math.random()
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('aRandom', new THREE.BufferAttribute(randoms, 1))

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector3() },
      uHovered: { value: 0 },
    },
    vertexShader: `
      attribute float size;
      attribute vec3 color;
      attribute float aRandom;
      varying vec3 vColor;
      varying float vAlpha;
      uniform float uTime;
      uniform vec3 uMouse;
      uniform float uHovered;

      void main() {
        vColor = color;
        vec3 pos = position;

        // Orbital motion
        float angle = uTime * (0.1 + aRandom * 0.1);
        float dist = length(pos.xy - vec2(${center.x.toFixed(1)}, ${center.y.toFixed(1)}));
        pos.x += sin(angle + dist * 0.1) * 0.5;
        pos.y += cos(angle + dist * 0.1) * 0.3;

        // Breathing effect
        float breathe = sin(uTime * 0.5 + aRandom * 6.28) * 0.3;
        pos.xy += normalize(pos.xy - vec2(${center.x.toFixed(1)}, ${center.y.toFixed(1)})) * breathe;

        // Mouse repulsion
        float mouseDist = distance(pos.xy, uMouse.xy);
        float influence = smoothstep(25.0, 0.0, mouseDist);
        vec2 dir = normalize(pos.xy - uMouse.xy + 0.001);
        pos.xy += dir * influence * 5.0;

        // Hover expansion
        pos.xy += normalize(pos.xy - vec2(${center.x.toFixed(1)}, ${center.y.toFixed(1)})) * uHovered * 3.0;

        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * (250.0 / -mvPosition.z) * (1.0 + uHovered * 0.5);
        gl_Position = projectionMatrix * mvPosition;

        vAlpha = 0.8 + uHovered * 0.2;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        float dist = length(gl_PointCoord - vec2(0.5));
        if (dist > 0.5) discard;

        float glow = 1.0 - smoothstep(0.0, 0.5, dist);
        float core = 1.0 - smoothstep(0.0, 0.2, dist);

        vec3 finalColor = vColor * glow + vec3(1.0) * core * 0.3;
        float alpha = glow * vAlpha;

        gl_FragColor = vec4(finalColor, alpha);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  })

  const particles = new THREE.Points(geometry, material)
  particles.userData = { clusterId: category.id, center }

  return {
    id: category.id,
    name: category.name,
    color,
    center,
    particles,
    count: getCategoryItems(category.id).length
  }
}

const createBackgroundStars = () => {
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(BACKGROUND_PARTICLES * 3)
  const sizes = new Float32Array(BACKGROUND_PARTICLES)
  const colors = new Float32Array(BACKGROUND_PARTICLES * 3)

  for (let i = 0; i < BACKGROUND_PARTICLES; i++) {
    const i3 = i * 3

    positions[i3] = (Math.random() - 0.5) * 300
    positions[i3 + 1] = (Math.random() - 0.5) * 200
    positions[i3 + 2] = -50 - Math.random() * 100

    sizes[i] = Math.random() * 1.5

    const brightness = 0.3 + Math.random() * 0.4
    colors[i3] = brightness
    colors[i3 + 1] = brightness
    colors[i3 + 2] = brightness
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
    },
    vertexShader: `
      attribute float size;
      attribute vec3 color;
      varying vec3 vColor;
      varying float vAlpha;
      uniform float uTime;

      void main() {
        vColor = color;

        vec3 pos = position;
        pos.z += sin(uTime * 0.1 + position.x * 0.01) * 2.0;

        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * (150.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;

        float twinkle = sin(uTime * 2.0 + position.x + position.y) * 0.3 + 0.7;
        vAlpha = twinkle;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        float dist = length(gl_PointCoord - vec2(0.5));
        if (dist > 0.5) discard;

        float alpha = smoothstep(0.5, 0.0, dist) * vAlpha * 0.6;
        gl_FragColor = vec4(vColor, alpha);
      }
    `,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  })

  const stars = new THREE.Points(geometry, material)
  stars.userData = { isBackground: true }
  scene.add(stars)
}

const updateClusterLabels = () => {
  if (!camera || !renderer) return

  const labels: ClusterLabel[] = []

  clusters.forEach(cluster => {
    const screenPos = cluster.center.clone().project(camera)
    const x = (screenPos.x * 0.5 + 0.5) * window.innerWidth
    const y = (-screenPos.y * 0.5 + 0.5) * window.innerHeight

    const cat = categories.value.find(c => c.id === cluster.id)

    labels.push({
      id: cluster.id,
      name: cat?.name || cluster.id,
      count: cluster.count,
      color: cat?.color || '#ffffff',
      x,
      y,
      visible: screenPos.z < 1 && x > 0 && x < window.innerWidth && y > 0 && y < window.innerHeight
    })
  })

  clusterLabels.value = labels
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  const time = performance.now() * 0.001

  // Update all cluster materials
  scene.children.forEach(child => {
    if (child instanceof THREE.Points && child.material instanceof THREE.ShaderMaterial) {
      child.material.uniforms.uTime.value = time
      child.material.uniforms.uMouse.value = mouseWorld

      if (child.userData.clusterId) {
        const isHovered = hoveredCluster.value?.id === child.userData.clusterId
        child.material.uniforms.uHovered.value += (isHovered ? 1 : 0 - child.material.uniforms.uHovered.value) * 0.1
      }
    }
  })

  // Subtle camera movement
  camera.position.x = Math.sin(time * 0.1) * 3
  camera.position.y = Math.cos(time * 0.08) * 2
  camera.lookAt(0, 0, 0)

  updateClusterLabels()
  renderer.render(scene, camera)
}

const handleMouseMove = (e: MouseEvent) => {
  mousePos.value = { x: e.clientX, y: e.clientY }

  // Convert to normalized device coordinates
  mouse.x = (e.clientX / window.innerWidth) * 2 - 1
  mouse.y = -(e.clientY / window.innerHeight) * 2 + 1

  // Convert to world coordinates
  mouseWorld.set(mouse.x * 60, mouse.y * 40, 0)

  // Raycast for hover detection
  if (camera && scene) {
    raycaster.setFromCamera(mouse, camera)

    let foundHover: { id: string; color: string } | null = null

    for (const cluster of clusters) {
      const dist = raycaster.ray.distanceToPoint(cluster.center)
      if (dist < 15) {
        const cat = categories.value.find(c => c.id === cluster.id)
        foundHover = { id: cluster.id, color: cat?.color || '#ffffff' }
        break
      }
    }

    hoveredCluster.value = foundHover

    if (canvasRef.value) {
      canvasRef.value.style.cursor = foundHover ? 'pointer' : 'default'
    }
  }
}

const handleClick = (e: MouseEvent) => {
  if (hoveredCluster.value) {
    activeCategory.value = hoveredCluster.value.id
  }
}

const handleMouseEnter = () => { isMouseInside.value = true }
const handleMouseLeave = () => {
  isMouseInside.value = false
  hoveredCluster.value = null
}

const handleResize = () => {
  if (!renderer || !camera) return
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
  updateClusterLabels()
}

const handleKeydown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showSearch.value = true
    nextTick(() => searchInputRef.value?.focus())
  }
  if (e.key === 'Escape') {
    if (showSearch.value) {
      showSearch.value = false
    } else if (selectedItem.value) {
      selectedItem.value = null
    } else if (activeCategory.value) {
      activeCategory.value = null
    }
  }
}

onMounted(() => {
  initThreeJS()

  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('click', handleClick)
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

  clusters = []

  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('click', handleClick)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('keydown', handleKeydown)
})

// Watch for search modal open
watch(showSearch, (val) => {
  if (val) {
    nextTick(() => searchInputRef.value?.focus())
  } else {
    searchQuery.value = ''
  }
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
  overflow: hidden;
}

.kb-canvas {
  position: fixed;
  inset: 0;
  z-index: 1;
}

.bg-noise {
  position: fixed;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  opacity: 0.02;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

.cursor-glow {
  position: fixed;
  width: 500px;
  height: 500px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(220, 38, 38, 0.12) 0%, transparent 70%);
  pointer-events: none;
  transform: translate(-50%, -50%);
  z-index: 3;
  transition: opacity 0.3s, background 0.5s;
}

/* ============================================
   CLUSTER LABELS
   ============================================ */
.cluster-label {
  position: fixed;
  z-index: 20;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.cluster-label:hover,
.cluster-label.hovered {
  border-color: var(--accent);
  background: rgba(0, 0, 0, 0.8);
  transform: translate(-50%, -50%) scale(1.05);
  box-shadow: 0 0 30px var(--accent);
}

.cluster-label.active {
  border-color: var(--accent);
  background: var(--accent);
}

.cluster-label.active .label-text,
.cluster-label.active .label-count {
  color: #000;
}

.label-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: labelPulse 2s infinite;
}

@keyframes labelPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

.label-text {
  font-size: 13px;
  letter-spacing: 0.1em;
  color: #f5f5f5;
}

.label-count {
  font-size: 10px;
  color: #737373;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
}

.cluster-label.hovered .label-count {
  color: var(--accent);
}

/* ============================================
   HEADER
   ============================================ */
.kb-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  background: rgba(3, 3, 3, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.kb-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.logo-symbol {
  width: 36px;
  height: 36px;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #000;
}

.logo-text {
  font-size: 12px;
  letter-spacing: 0.2em;
  color: #f5f5f5;
}

.header-center {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 11px;
  letter-spacing: 0.15em;
  color: #737373;
}

.header-version {
  font-size: 10px;
  padding: 2px 8px;
  background: rgba(220, 38, 38, 0.2);
  color: #DC2626;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.search-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #737373;
  cursor: pointer;
  transition: all 0.2s;
}

.search-trigger:hover {
  border-color: #DC2626;
  color: #f5f5f5;
}

.search-trigger svg {
  width: 16px;
  height: 16px;
}

.search-trigger span {
  font-size: 11px;
}

.terminal-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid #DC2626;
  color: #DC2626;
  font-size: 11px;
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
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  text-align: center;
  pointer-events: none;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: #DC2626;
  font-size: 10px;
  letter-spacing: 0.15em;
  margin-bottom: 24px;
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
  font-size: clamp(3rem, 12vw, 8rem);
  line-height: 0.9;
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
  font-size: 13px;
  color: #525252;
  margin-top: 20px;
  letter-spacing: 0.1em;
}

.hero-hint {
  margin-top: 48px;
  font-size: 11px;
  color: #404040;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.hint-icon {
  animation: starPulse 2s infinite;
}

@keyframes starPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

/* ============================================
   CATEGORY PANEL
   ============================================ */
.category-panel {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: flex-end;
}

.panel-content {
  width: 100%;
  max-width: 500px;
  height: 100%;
  background: #0a0a0a;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  overflow-y: auto;
  position: relative;
}

.panel-close {
  position: absolute;
  top: 20px;
  right: 20px;
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
  z-index: 10;
}

.panel-close:hover {
  border-color: #DC2626;
  color: #DC2626;
}

.panel-close svg {
  width: 20px;
  height: 20px;
}

.panel-header {
  padding: 60px 32px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.panel-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #000;
  margin-bottom: 20px;
}

.panel-icon svg {
  width: 28px;
  height: 28px;
}

.panel-title {
  font-size: 2rem;
  color: #f5f5f5;
  margin: 0 0 12px;
  letter-spacing: 0.05em;
}

.panel-desc {
  font-size: 13px;
  color: #737373;
  line-height: 1.6;
  margin: 0;
}

.panel-items {
  padding: 24px;
}

.panel-item {
  padding: 20px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.panel-item:hover {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.04);
  transform: translateX(4px);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.item-code {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.05);
}

.item-title {
  font-size: 16px;
  color: #f5f5f5;
}

.item-desc {
  font-size: 12px;
  color: #525252;
  margin: 0 0 12px;
  line-height: 1.5;
}

.item-tags {
  display: flex;
  gap: 8px;
}

.item-tag {
  font-size: 9px;
  padding: 3px 8px;
  letter-spacing: 0.05em;
}

.item-tag.formula {
  background: rgba(220, 38, 38, 0.2);
  color: #f87171;
}

.item-tag.path {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

/* Panel Transition */
.panel-enter-active,
.panel-leave-active {
  transition: all 0.4s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
}

.panel-enter-from .panel-content,
.panel-leave-to .panel-content {
  transform: translateX(100%);
}

/* ============================================
   SEARCH MODAL
   ============================================ */
.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 120px 20px 20px;
}

.search-modal {
  width: 100%;
  max-width: 600px;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.search-icon {
  width: 24px;
  height: 24px;
  color: #525252;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #f5f5f5;
  font-size: 16px;
  outline: none;
}

.search-input::placeholder {
  color: #404040;
}

.search-results {
  max-height: 400px;
  overflow-y: auto;
}

.search-result {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result:hover {
  background: rgba(220, 38, 38, 0.1);
}

.result-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #000;
}

.result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-title {
  font-size: 15px;
  color: #f5f5f5;
}

.result-category {
  font-size: 11px;
  color: #525252;
}

.search-empty {
  padding: 40px 20px;
  text-align: center;
  color: #525252;
}

/* Modal Transition */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .search-modal,
.modal-enter-from .modal-content,
.modal-leave-to .search-modal,
.modal-leave-to .modal-content {
  transform: translateY(-20px) scale(0.95);
}

/* ============================================
   DETAIL MODAL
   ============================================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 400;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(20px);
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
  overflow-y: auto;
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
  z-index: 10;
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
   CATEGORY NAV BAR
   ============================================ */
.kb-nav-bar {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 50;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: rgba(10, 10, 10, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  max-width: 90vw;
}

.nav-category {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #a3a3a3;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-category:hover {
  border-color: var(--accent);
  background: rgba(255, 255, 255, 0.08);
  color: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px var(--accent);
}

.nav-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.nav-name {
  font-size: 11px;
  letter-spacing: 0.1em;
  white-space: nowrap;
}

.nav-count {
  font-size: 9px;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #737373;
}

.nav-category:hover .nav-count {
  color: var(--accent);
}

/* ============================================
   FOOTER
   ============================================ */
.kb-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  padding: 16px 24px;
  background: rgba(3, 3, 3, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.footer-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.25rem;
  color: #DC2626;
  display: block;
}

.stat-label {
  font-size: 9px;
  color: #525252;
  letter-spacing: 0.1em;
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
@media (max-width: 768px) {
  .kb-header {
    padding: 12px 16px;
  }

  .header-center {
    display: none;
  }

  .search-trigger span {
    display: none;
  }

  .cluster-label {
    padding: 6px 12px;
    gap: 6px;
  }

  .label-text {
    font-size: 11px;
  }

  .label-count {
    display: none;
  }

  .panel-content {
    max-width: 100%;
  }

  .hero-title {
    font-size: clamp(2rem, 15vw, 4rem);
  }

  .kb-nav-bar {
    bottom: 60px;
    padding: 12px;
    gap: 6px;
  }

  .nav-category {
    padding: 8px 12px;
  }

  .nav-name {
    font-size: 10px;
  }

  .nav-count {
    display: none;
  }

  .footer-stats {
    gap: 16px;
  }

  .stat-value {
    font-size: 1rem;
  }
}
</style>
