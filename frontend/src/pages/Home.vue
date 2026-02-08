<template>
  <div class="home-root">
    <!-- ═══ FULL-VIEWPORT FADE SLIDER ═══ -->
    <div class="slider-viewport" ref="viewportRef">
      <!-- Each slide is position:absolute, crossfaded via opacity -->
      <div
        v-for="(slide, si) in slides"
        :key="si"
        class="slide"
        :class="[slide.type, { active: si === currentSlide }]"
      >
        <!-- DARK SLIDE: marquee letter rows + center card -->
        <template v-if="slide.type === 'dark'">
          <div class="marquee-bg">
            <div
              v-for="(letter, li) in slide.letters"
              :key="li"
              class="marquee-row"
              :ref="(el) => setTrackRef(el as HTMLElement | null, si, li)"
            >
              <div class="marquee-inner">
                <span v-for="n in 20" :key="'a' + n" class="marquee-letter">{{ letter }}</span>
                <span v-for="n in 20" :key="'b' + n" class="marquee-letter">{{ letter }}</span>
              </div>
            </div>
          </div>
          <div class="slide-center">
            <div class="center-card">
              <div class="card-eyebrow">{{ slide.eyebrow }}</div>
              <div class="card-title">{{ slide.title }}</div>
              <div class="card-desc">{{ slide.desc }}</div>
            </div>
          </div>
        </template>

        <!-- RED SLIDE: bold typography statement -->
        <template v-if="slide.type === 'red'">
          <div class="red-content">
            <div v-if="slide.topLine" class="red-top">{{ slide.topLine }}</div>
            <div class="red-headline">{{ slide.headline }}</div>
            <div v-if="slide.bottomLine" class="red-bottom">{{ slide.bottomLine }}</div>
          </div>
        </template>
      </div>

      <!-- Slide indicators -->
      <div class="slide-indicators">
        <button
          v-for="(_, si) in slides"
          :key="si"
          class="indicator"
          :class="{ active: si === currentSlide }"
          @click="goToSlide(si)"
        ></button>
      </div>

      <!-- Scroll down hint -->
      <div class="scroll-hint">
        <span>SCROLL</span>
        <div class="scroll-line"></div>
      </div>
    </div>

    <!-- ═══ TOOLS + TERMINAL (scrollable below slider) ═══ -->
    <div class="below-fold" ref="belowFoldRef">
      <section class="tools-section">
        <div class="tools-wrap">
          <div class="section-eyebrow">PLATFORM</div>
          <h2 class="section-heading">Инструменты</h2>

          <div class="tools-grid">
            <div
              v-for="tool in tools"
              :key="tool.path"
              class="g-card"
              :class="{
                'is-active': activeTool === tool.path,
                'is-faded': activeTool !== null && activeTool !== tool.path
              }"
              @click="navigateTo(tool.path, $event)"
            >
              <div class="g-card-accent" :class="tool.color"></div>
              <div class="g-card-body">
                <div class="g-card-title">{{ tool.name }}</div>
                <div class="g-card-desc">{{ tool.desc }}</div>
              </div>
              <div class="g-card-arrow">&rarr;</div>
            </div>
          </div>
        </div>
      </section>

      <section class="terminal-section">
        <div
          class="terminal-card"
          :class="{ 'is-active': activeTool === '/terminal' }"
          @click="navigateTo('/terminal', $event)"
        >
          <div class="terminal-zeta">&zeta;</div>
          <div class="terminal-info">
            <div class="terminal-title">Дзета-Терминал</div>
            <div class="terminal-sub">Потоковые данные в реальном времени &middot; Акции &middot; Крипто &middot; Фьючерсы &middot; Опционы</div>
          </div>
          <div class="terminal-cta">Открыть &rarr;</div>
        </div>
      </section>

      <div class="footer-spacer"></div>
    </div>

    <!-- Transition overlay for navigation -->
    <div class="transition-overlay" :class="{ active: activeTool !== null }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { useKineticMarquee, type MarqueeTrack } from '@/composables/useKineticMarquee'

const router = useRouter()
const viewportRef = ref<HTMLElement | null>(null)
const belowFoldRef = ref<HTMLElement | null>(null)
const activeTool = ref<string | null>(null)
const currentSlide = ref(0)

interface DarkSlide {
  type: 'dark'
  letters: string[]
  eyebrow: string
  title: string
  desc: string
}

interface RedSlide {
  type: 'red'
  topLine?: string
  headline: string
  bottomLine?: string
}

type Slide = DarkSlide | RedSlide

const slides: Slide[] = [
  {
    type: 'dark',
    letters: ['Q', 'U', 'A', 'N'],
    eyebrow: 'STOCHASTIC PLATFORM',
    title: 'Quantitative Analytics',
    desc: 'Стохастические модели, ценообразование деривативов, портфельный анализ',
  },
  {
    type: 'red',
    topLine: 'QUANTITATIVE',
    headline: 'ANALYTICS',
    bottomLine: 'STOCHASTIC MODELS',
  },
  {
    type: 'dark',
    letters: ['R', 'I', 'S', 'K'],
    eyebrow: 'RISK ENGINE',
    title: 'Risk Management',
    desc: 'VaR, стресс-тесты, режимы рынка, факторный анализ',
  },
  {
    type: 'red',
    topLine: 'BLACK-SCHOLES',
    headline: 'HESTON',
    bottomLine: 'MONTE CARLO · LÉVY',
  },
  {
    type: 'dark',
    letters: ['V', 'O', 'L', 'A'],
    eyebrow: 'VOLATILITY SURFACE',
    title: 'Options & Volatility',
    desc: 'SABR/SVI калибровка, smile, FFT-ценообразование',
  },
  {
    type: 'red',
    topLine: 'PORTFOLIO',
    headline: 'OPTIMIZE',
    bottomLine: 'SHARPE · VAR · GREEKS',
  },
]

const tools = [
  { name: 'Портфельный анализ', desc: 'Доходность, VaR/ES, мониторинг позиций', color: 'red', path: '/portfolio' },
  { name: 'Риск-менеджмент', desc: 'Стресс-тесты, бэктестинг VaR, сценарии', color: 'dark', path: '/stress' },
  { name: 'Рыночные режимы', desc: 'HMM, стационарное распределение', color: 'red', path: '/regimes' },
  { name: 'Стоимость облигаций', desc: 'DCF, дюрация, convexity, спреды', color: 'dark', path: '/bond-valuation' },
  { name: 'Стоимость опционов', desc: 'БШМ, Хестон, Леви, FFT', color: 'red', path: '/pricing/options' },
  { name: 'Волатильность', desc: 'SABR/SVI калибровка, smile', color: 'dark', path: '/analytics/volatility' },
  { name: 'Стоимость СВОПов', desc: 'IRS & FX свопы, NPV, DV01', color: 'red', path: 'valuation/swaps' },
  { name: 'Стоимость форвардов', desc: 'Справедливая стоимость, кривая', color: 'dark', path: 'valuation/forwards' },
  { name: 'Отчёты', desc: 'Bond Report, шаблонные отчёты', color: 'red', path: '/vanila-bond-report' },
  { name: 'Монте-Карло', desc: 'Симуляции, стохастические модели', color: 'dark', path: '/monte-carlo' },
  { name: 'Кривая доходности', desc: 'ZCYC, zero-coupon yield curve', color: 'red', path: '/zcyc-viewer' },
  { name: 'P&L Attribution', desc: 'Факторная декомпозиция P&L', color: 'dark', path: '/analytics/pnl' },
  { name: 'Citadel Zeta Field', desc: 'Гравитационное поле ликвидности', color: 'red', path: '/terminal' },
  { name: 'Phase Space', desc: 'Фазовое пространство, аттракторы', color: 'dark', path: '/terminal' },
  { name: 'Liquidity Model', desc: 'Модель ликвидности рынка', color: 'red', path: '/terminal' },
]

// Track refs for marquee initialization
const trackRefMap = new Map<string, HTMLElement>()

function setTrackRef(el: HTMLElement | null, slideIdx: number, rowIdx: number) {
  const key = `${slideIdx}-${rowIdx}`
  if (el) {
    trackRefMap.set(key, el)
  } else {
    trackRefMap.delete(key)
  }
}

const { initTracks, boostAll, resetSpeed } = useKineticMarquee()

// Slide timer
let slideTimer: ReturnType<typeof setInterval> | null = null
const SLIDE_INTERVAL = 3500

function goToSlide(idx: number) {
  if (idx === currentSlide.value) return
  currentSlide.value = idx
  boostAll(3, 0.3)
  setTimeout(() => resetSpeed(0.8), 400)
  resetTimer()
}

function nextSlide() {
  const next = (currentSlide.value + 1) % slides.length
  goToSlide(next)
}

function resetTimer() {
  if (slideTimer) clearInterval(slideTimer)
  slideTimer = setInterval(nextSlide, SLIDE_INTERVAL)
}

// Navigation with fade transition
function navigateTo(path: string, e: MouseEvent) {
  if (activeTool.value) return
  activeTool.value = path

  const card = e.currentTarget as HTMLElement
  gsap.to(card, { scale: 1.03, duration: 0.3, ease: 'power2.out' })

  boostAll(5, 0.3)

  setTimeout(() => router.push(path), 500)
}

// Init marquee tracks for ALL dark slides
function initAllMarquees() {
  const allTracks: MarqueeTrack[] = []

  slides.forEach((slide, si) => {
    if (slide.type !== 'dark') return
    const directions: Array<1 | -1> = [1, -1, 1, -1]
    slide.letters.forEach((_, li) => {
      const el = trackRefMap.get(`${si}-${li}`)
      if (el) {
        allTracks.push({ el, direction: directions[li] })
      }
    })
  })

  initTracks(allTracks)
}

// Wheel/touch to advance slide when in viewport
function handleWheel(e: WheelEvent) {
  // Only intercept if we're at the slider viewport
  const vp = viewportRef.value
  if (!vp) return

  const rect = vp.getBoundingClientRect()
  // If slider is mostly visible
  if (rect.top > -100 && rect.bottom > window.innerHeight * 0.5) {
    // Don't prevent scroll if on last slide and scrolling down
    if (e.deltaY > 0 && currentSlide.value === slides.length - 1) return
    // Don't prevent scroll if on first slide and scrolling up
    if (e.deltaY < 0 && currentSlide.value === 0) return

    e.preventDefault()
    if (Math.abs(e.deltaY) < 30) return

    if (e.deltaY > 0) {
      goToSlide(Math.min(currentSlide.value + 1, slides.length - 1))
    } else {
      goToSlide(Math.max(currentSlide.value - 1, 0))
    }
  }
}

let touchStartY = 0

function handleTouchStart(e: TouchEvent) {
  touchStartY = e.touches[0].clientY
}

function handleTouchEnd(e: TouchEvent) {
  const vp = viewportRef.value
  if (!vp) return

  const rect = vp.getBoundingClientRect()
  if (rect.top > -100 && rect.bottom > window.innerHeight * 0.5) {
    const dy = touchStartY - e.changedTouches[0].clientY
    if (Math.abs(dy) < 40) return

    if (dy > 0 && currentSlide.value < slides.length - 1) {
      goToSlide(currentSlide.value + 1)
    } else if (dy < 0 && currentSlide.value > 0) {
      goToSlide(currentSlide.value - 1)
    }
  }
}

onMounted(async () => {
  await nextTick()
  initAllMarquees()
  resetTimer()

  // Entrance animation
  if (belowFoldRef.value) {
    gsap.set(belowFoldRef.value, { opacity: 1 })
  }

  window.addEventListener('wheel', handleWheel, { passive: false })
  window.addEventListener('touchstart', handleTouchStart, { passive: true })
  window.addEventListener('touchend', handleTouchEnd, { passive: true })
})

onUnmounted(() => {
  if (slideTimer) clearInterval(slideTimer)
  window.removeEventListener('wheel', handleWheel)
  window.removeEventListener('touchstart', handleTouchStart)
  window.removeEventListener('touchend', handleTouchEnd)
})
</script>

<style scoped>
/* ══════ ROOT ══════ */
.home-root {
  width: 100%;
  min-height: 100vh;
  background: #000;
  color: #fff;
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* ══════ SLIDER VIEWPORT ══════ */
.slider-viewport {
  position: relative;
  width: 100%;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

/* ══════ SLIDE (crossfade) ══════ */
.slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

.slide.active {
  opacity: 1;
  pointer-events: auto;
  z-index: 1;
}

/* ══════ DARK SLIDE ══════ */
.slide.dark {
  background: #000;
}

.marquee-bg {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0;
  overflow: hidden;
  z-index: 0;
}

.marquee-row {
  overflow: hidden;
  white-space: nowrap;
  line-height: 1;
}

.marquee-inner {
  display: inline-flex;
  will-change: transform;
}

.marquee-letter {
  font-size: clamp(6rem, 18vw, 16rem);
  font-weight: 900;
  color: #e63946;
  opacity: 0.85;
  letter-spacing: -0.02em;
  padding: 0 0.08em;
  flex-shrink: 0;
  user-select: none;
  line-height: 0.9;
}

/* Center card overlay on dark slides */
.slide-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.center-card {
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  padding: 36px 44px;
  max-width: 420px;
  text-align: center;
}

.card-eyebrow {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.25em;
  color: #e63946;
  margin-bottom: 12px;
}

.card-title {
  font-size: clamp(1.4rem, 3vw, 2rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.6;
}

/* ══════ RED SLIDE ══════ */
.slide.red {
  background: #e63946;
}

.red-content {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem;
}

.red-top {
  font-size: clamp(0.8rem, 1.4vw, 1.1rem);
  font-weight: 700;
  letter-spacing: 0.25em;
  color: rgba(0, 0, 0, 0.4);
  margin-bottom: 12px;
}

.red-headline {
  font-size: clamp(3.5rem, 12vw, 10rem);
  font-weight: 900;
  letter-spacing: -0.05em;
  line-height: 0.9;
  color: #000;
}

.red-bottom {
  font-size: clamp(0.7rem, 1.2vw, 1rem);
  font-weight: 700;
  letter-spacing: 0.2em;
  color: rgba(0, 0, 0, 0.35);
  margin-top: 16px;
}

/* ══════ SLIDE INDICATORS ══════ */
.slide-indicators {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.indicator {
  width: 32px;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 2px;
  cursor: pointer;
  padding: 0;
  transition: all 0.4s;
}

.indicator.active {
  background: #e63946;
  width: 48px;
}

/* Red slide adjusts indicator colors */
.slide.red.active ~ .slide-indicators .indicator {
  background: rgba(0, 0, 0, 0.2);
}

.slide.red.active ~ .slide-indicators .indicator.active {
  background: #000;
}

/* ══════ SCROLL HINT ══════ */
.scroll-hint {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  z-index: 10;
  color: rgba(255, 255, 255, 0.2);
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.2em;
}

.scroll-line {
  width: 1px;
  height: 24px;
  background: currentColor;
  animation: pulse-line 2s ease-in-out infinite;
}

@keyframes pulse-line {
  0%, 100% { opacity: 0.2; transform: scaleY(0.5); }
  50% { opacity: 1; transform: scaleY(1); }
}

/* ══════ BELOW FOLD ══════ */
.below-fold {
  position: relative;
  z-index: 2;
  background: #000;
}

/* ══════ TOOLS SECTION ══════ */
.tools-section {
  padding: 60px 2rem 60px;
}

.tools-wrap {
  max-width: 1100px;
  margin: 0 auto;
}

.section-eyebrow {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.25em;
  color: #e63946;
  margin-bottom: 8px;
}

.section-heading {
  font-size: clamp(1.8rem, 4vw, 2.6rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  margin: 0 0 32px 0;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

/* ══════ CARD ══════ */
.g-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: #0d0d0d;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.g-card:hover {
  background: #141414;
  border-color: #e63946;
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(230, 57, 70, 0.1);
}

.g-card.is-active {
  border-color: #e63946;
  z-index: 10;
}

.g-card.is-faded {
  opacity: 0.3;
  filter: blur(2px);
  pointer-events: none;
  transition: all 0.4s;
}

.g-card-accent {
  width: 3px;
  align-self: stretch;
  border-radius: 2px;
  flex-shrink: 0;
}

.g-card-accent.red { background: #e63946; }
.g-card-accent.dark { background: rgba(255, 255, 255, 0.12); }

.g-card-body {
  flex: 1;
  min-width: 0;
}

.g-card-title {
  font-size: 0.88rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 3px;
}

.g-card-desc {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.5;
}

.g-card-arrow {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  transition: all 0.3s;
}

.g-card:hover .g-card-arrow {
  color: #e63946;
  transform: translateX(4px);
}

/* ══════ TERMINAL ══════ */
.terminal-section {
  padding: 20px 2rem 40px;
}

.terminal-card {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  background: #0d0d0d;
  border: 1px solid rgba(230, 57, 70, 0.15);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}

.terminal-card:hover {
  border-color: #e63946;
  background: #111;
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.1);
}

.terminal-card.is-active {
  border-color: #e63946;
}

.terminal-zeta {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  font-weight: 900;
  color: #e63946;
  background: rgba(230, 57, 70, 0.08);
  border: 1px solid rgba(230, 57, 70, 0.2);
  border-radius: 3px;
  flex-shrink: 0;
}

.terminal-info {
  flex: 1;
}

.terminal-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 3px;
}

.terminal-sub {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.5;
}

.terminal-cta {
  font-size: 0.85rem;
  font-weight: 700;
  color: #e63946;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.terminal-card:hover .terminal-cta {
  transform: translateX(4px);
}

/* ══════ TRANSITION OVERLAY ══════ */
.transition-overlay {
  position: fixed;
  inset: 0;
  background: #000;
  z-index: 9998;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.transition-overlay.active {
  opacity: 1;
  transition-delay: 0.1s;
}

/* ══════ FOOTER SPACER ══════ */
.footer-spacer {
  height: 60px;
}

/* ══════ RESPONSIVE ══════ */
@media (max-width: 1024px) {
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .marquee-letter {
    font-size: clamp(4rem, 18vw, 8rem);
  }

  .center-card {
    padding: 24px 28px;
    margin: 0 1rem;
  }

  .tools-section {
    padding: 40px 1rem 48px;
  }

  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .g-card {
    padding: 14px 16px;
  }

  .terminal-section {
    padding: 12px 1rem 32px;
  }

  .terminal-card {
    padding: 18px 20px;
  }

  .red-headline {
    font-size: clamp(2.5rem, 14vw, 6rem);
  }
}

@media (max-width: 480px) {
  .marquee-letter {
    font-size: clamp(3rem, 20vw, 5rem);
  }

  .tools-grid {
    grid-template-columns: 1fr;
  }

  .g-card-arrow {
    display: none;
  }

  .center-card {
    padding: 20px 22px;
  }

  .card-title {
    font-size: 1.3rem;
  }

  .terminal-card {
    flex-wrap: wrap;
  }

  .terminal-cta {
    width: 100%;
    text-align: center;
    padding-top: 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .slide-indicators {
    bottom: 48px;
  }
}
</style>
