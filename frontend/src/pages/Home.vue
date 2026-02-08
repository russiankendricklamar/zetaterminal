<template>
  <div class="home-root">
    <!-- ═══ LOADING SCREEN ═══ -->
    <div class="loading-screen" :class="{ gone: !isLoading }" ref="loadingRef">
      <h1 class="loading-text" ref="loadingTextRef">STOCHASTIC</h1>
    </div>

    <!-- ═══ NOISE OVERLAY ═══ -->
    <div class="noise-overlay"></div>

    <!-- ═══ FIXED NAVIGATION ═══ -->
    <nav class="top-nav" v-show="!isLoading">
      <div class="nav-left">
        <span class="nav-diamond">&#9670;</span>
        <span class="nav-brand">STOCHASTIC / PLATFORM</span>
      </div>
      <div class="nav-links">
        <a class="nav-link" @click.prevent="scrollToTools">Инструменты</a>
        <a class="nav-link" @click.prevent="scrollToTerminal">Терминал</a>
      </div>
    </nav>

    <!-- ═══ FIXED BACKGROUND LAYER ═══ -->
    <div class="bg-layer" ref="bgLayerRef">
      <div
        v-for="(bg, bi) in backgrounds"
        :key="bi"
        class="bg-slide"
        :class="bg.type"
        :ref="(el) => setBgRef(el as HTMLElement | null, bi)"
      >
        <!-- DARK: marquee letter rows + center card -->
        <template v-if="bg.type === 'dark'">
          <!-- Grid overlay -->
          <div class="grid-overlay"></div>
          <div class="marquee-bg">
            <div
              v-for="(letter, li) in bg.letters"
              :key="li"
              class="marquee-row"
              :ref="(el) => setTrackRef(el as HTMLElement | null, bi, li)"
            >
              <div class="marquee-inner">
                <span v-for="n in 20" :key="'a' + n" class="marquee-letter">{{ letter }}</span>
                <span v-for="n in 20" :key="'b' + n" class="marquee-letter">{{ letter }}</span>
              </div>
            </div>
          </div>
          <div class="slide-center">
            <div class="center-card">
              <div class="card-eyebrow">{{ bg.eyebrow }}</div>
              <div class="card-title">{{ bg.title }}</div>
              <div class="card-desc">{{ bg.desc }}</div>
            </div>
          </div>
          <!-- Decorative vertical lines -->
          <div class="decor-line decor-line-left"></div>
          <div class="decor-line decor-line-right"></div>
        </template>

        <!-- RED: bold typography -->
        <template v-if="bg.type === 'red'">
          <div class="red-content">
            <div v-if="bg.topLine" class="red-top">{{ bg.topLine }}</div>
            <div class="red-headline">{{ bg.headline }}</div>
            <div v-if="bg.bottomLine" class="red-bottom">{{ bg.bottomLine }}</div>
          </div>
        </template>
      </div>
    </div>

    <!-- ═══ SCROLLABLE CONTENT (one continuous page) ═══ -->
    <div class="content-layer">
      <!-- Hero -->
      <section class="section hero-section" ref="sectionRefs_0">
        <div class="hero-inner">
          <div class="hero-eyebrow" ref="heroEyebrowRef">THE FINAL CHAPTER</div>
          <div class="hero-title-wrap">
            <h1 class="hero-headline" ref="heroHeadlineRef">QUANTITATIVE</h1>
            <p class="hero-subline" ref="heroSublineRef">ANALYTICS</p>
          </div>
          <p class="hero-desc" ref="heroDescRef">Платформа количественного анализа для финансовых рынков</p>
          <div class="hero-bottom" ref="heroBottomRef">
            <span>&#9670; Stochastic</span>
            <span>2026</span>
            <span class="hero-bottom-hide-mobile">Quantitative Platform</span>
          </div>
          <div class="hero-scroll-hint" ref="heroScrollRef">
            <span>SCROLL</span>
            <div class="scroll-line"></div>
          </div>
        </div>
      </section>

      <!-- Marquee strip divider -->
      <div class="marquee-strip" ref="marqueeStripRef">
        <div class="marquee-strip-inner">
          <span v-for="n in 6" :key="n" class="strip-text">STOCHASTIC &mdash; QUANTITATIVE ANALYTICS &mdash; DERIVATIVES &mdash; RISK &mdash; </span>
        </div>
      </div>

      <!-- Spacer sections (transparent, trigger bg change) -->
      <section class="section spacer" ref="sectionRefs_1"></section>
      <section class="section spacer" ref="sectionRefs_2"></section>
      <section class="section spacer" ref="sectionRefs_3"></section>
      <section class="section spacer" ref="sectionRefs_4"></section>
      <section class="section spacer" ref="sectionRefs_5"></section>

      <!-- Marquee strip divider (dark) -->
      <div class="marquee-strip marquee-strip-dark">
        <div class="marquee-strip-inner marquee-strip-reverse">
          <span v-for="n in 6" :key="n" class="strip-text">LEGENDARY STATUS &mdash; PORTFOLIO OPTIMIZATION &mdash; MONTE CARLO &mdash; </span>
        </div>
      </div>

      <!-- Tools grid -->
      <section class="tools-section" ref="sectionRefs_6">
        <div class="tools-wrap">
          <div class="tools-header">
            <div class="tools-header-left">
              <div class="section-eyebrow">PLATFORM</div>
              <h2 class="section-heading">Инструменты</h2>
            </div>
            <span class="tools-counter">{{ tools.length }} tools</span>
          </div>
          <div class="tools-grid">
            <div
              v-for="(tool, ti) in tools"
              :key="tool.path"
              class="g-card"
              :class="{
                'is-active': activeTool === tool.path,
                'is-faded': activeTool !== null && activeTool !== tool.path
              }"
              :ref="(el) => setCardRef(el as HTMLElement | null, ti)"
              @click="navigateTo(tool.path, $event)"
            >
              <div class="g-card-accent" :class="tool.color"></div>
              <div class="g-card-body">
                <span class="g-card-index">{{ String(ti + 1).padStart(2, '0') }}</span>
                <div class="g-card-title">{{ tool.name }}</div>
                <div class="g-card-desc">{{ tool.desc }}</div>
              </div>
              <div class="g-card-arrow">&rarr;</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Terminal -->
      <section class="terminal-section" ref="terminalSectionRef">
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

    <!-- Transition overlay -->
    <div class="transition-overlay" :class="{ active: activeTool !== null }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/dist/ScrollTrigger'
import { useKineticMarquee, getScrollContainer, type MarqueeTrack } from '@/composables/useKineticMarquee'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const bgLayerRef = ref<HTMLElement | null>(null)
const activeTool = ref<string | null>(null)
const isLoading = ref(true)

// Refs
const loadingRef = ref<HTMLElement | null>(null)
const loadingTextRef = ref<HTMLElement | null>(null)
const heroEyebrowRef = ref<HTMLElement | null>(null)
const heroHeadlineRef = ref<HTMLElement | null>(null)
const heroSublineRef = ref<HTMLElement | null>(null)
const heroDescRef = ref<HTMLElement | null>(null)
const heroBottomRef = ref<HTMLElement | null>(null)
const heroScrollRef = ref<HTMLElement | null>(null)
const marqueeStripRef = ref<HTMLElement | null>(null)
const terminalSectionRef = ref<HTMLElement | null>(null)

// Section refs
const sectionRefs_0 = ref<HTMLElement | null>(null)
const sectionRefs_1 = ref<HTMLElement | null>(null)
const sectionRefs_2 = ref<HTMLElement | null>(null)
const sectionRefs_3 = ref<HTMLElement | null>(null)
const sectionRefs_4 = ref<HTMLElement | null>(null)
const sectionRefs_5 = ref<HTMLElement | null>(null)
const sectionRefs_6 = ref<HTMLElement | null>(null)

// Background definitions
interface DarkBg {
  type: 'dark'
  letters: string[]
  eyebrow: string
  title: string
  desc: string
}

interface RedBg {
  type: 'red'
  topLine?: string
  headline: string
  bottomLine?: string
}

type BgSlide = DarkBg | RedBg

const backgrounds: BgSlide[] = [
  { type: 'dark', letters: ['Q', 'U', 'A', 'N', 'T'], eyebrow: 'STOCHASTIC PLATFORM', title: 'Quantitative Analytics', desc: 'Стохастические модели, ценообразование деривативов, портфельный анализ' },
  { type: 'red', topLine: 'QUANTITATIVE', headline: 'ANALYTICS', bottomLine: 'STOCHASTIC MODELS' },
  { type: 'dark', letters: ['R', 'I', 'S', 'K'], eyebrow: 'RISK ENGINE', title: 'Risk Management', desc: 'VaR, стресс-тесты, режимы рынка, факторный анализ' },
  { type: 'red', topLine: 'BLACK-SCHOLES', headline: 'HESTON', bottomLine: 'MONTE CARLO \u00b7 L\u00c9VY' },
  { type: 'dark', letters: ['S', 'I', 'G', 'M', 'A'], eyebrow: 'VOLATILITY', title: 'Options & Sigma', desc: 'SABR/SVI калибровка, smile, FFT-ценообразование' },
  { type: 'red', topLine: 'PORTFOLIO', headline: 'OPTIMIZE', bottomLine: 'SHARPE \u00b7 VAR \u00b7 GREEKS' },
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

// Bg refs
const bgRefs = new Map<number, HTMLElement>()
function setBgRef(el: HTMLElement | null, idx: number) {
  if (el) { bgRefs.set(idx, el) } else { bgRefs.delete(idx) }
}

// Track refs for marquee
const trackRefMap = new Map<string, HTMLElement>()
function setTrackRef(el: HTMLElement | null, bgIdx: number, rowIdx: number) {
  const key = `${bgIdx}-${rowIdx}`
  if (el) { trackRefMap.set(key, el) } else { trackRefMap.delete(key) }
}

// Card refs for reveal animation
const cardRefs = new Map<number, HTMLElement>()
function setCardRef(el: HTMLElement | null, idx: number) {
  if (el) { cardRefs.set(idx, el) } else { cardRefs.delete(idx) }
}

const { initTracks } = useKineticMarquee()

// Custom easing matching J. Cole project
const EASE_EXPO = 'expo.out'

// Navigation scroll helpers
function scrollToTools() {
  sectionRefs_6.value?.scrollIntoView({ behavior: 'smooth' })
}
function scrollToTerminal() {
  terminalSectionRef.value?.scrollIntoView({ behavior: 'smooth' })
}

// Navigation
function navigateTo(path: string, e: MouseEvent) {
  if (activeTool.value) return
  activeTool.value = path
  const card = e.currentTarget as HTMLElement
  gsap.to(card, { scale: 1.03, duration: 0.3, ease: 'power2.out' })
  setTimeout(() => router.push(path), 500)
}

// Loading screen animation
function animateLoading() {
  const tl = gsap.timeline()

  // Pulse the loading text
  if (loadingTextRef.value) {
    tl.fromTo(loadingTextRef.value,
      { scaleY: 0, opacity: 0 },
      { scaleY: 1, opacity: 1, duration: 0.8, ease: EASE_EXPO }
    )
  }

  // After delay, fade out loading screen
  tl.to(loadingRef.value, {
    opacity: 0,
    y: -60,
    duration: 0.8,
    ease: 'power4.inOut',
    delay: 0.6,
    onComplete: () => {
      isLoading.value = false
      animateHeroEntrance()
    },
  })
}

// Hero entrance animations (scaleY reveal like J. Cole Hero.tsx)
function animateHeroEntrance() {
  const ease = 'power4.out'

  if (heroEyebrowRef.value) {
    gsap.fromTo(heroEyebrowRef.value,
      { y: 40, opacity: 0 },
      { y: 0, opacity: 1, duration: 1, delay: 0.1, ease }
    )
  }

  if (heroHeadlineRef.value) {
    gsap.fromTo(heroHeadlineRef.value,
      { scaleY: 0, opacity: 0 },
      { scaleY: 1, opacity: 1, duration: 1, delay: 0.2, ease, transformOrigin: 'bottom center' }
    )
  }

  if (heroSublineRef.value) {
    gsap.fromTo(heroSublineRef.value,
      { scaleY: 0, opacity: 0 },
      { scaleY: 1, opacity: 1, duration: 1, delay: 0.4, ease, transformOrigin: 'top center' }
    )
  }

  if (heroDescRef.value) {
    gsap.fromTo(heroDescRef.value,
      { y: 30, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.8, delay: 0.6, ease }
    )
  }

  if (heroBottomRef.value) {
    gsap.fromTo(heroBottomRef.value,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.8, delay: 0.7, ease }
    )
  }

  if (heroScrollRef.value) {
    gsap.fromTo(heroScrollRef.value,
      { opacity: 0 },
      { opacity: 1, duration: 1, delay: 1.2, ease }
    )
  }
}

// Init marquees for all dark backgrounds
function initAllMarquees(container: HTMLElement) {
  const allTracks: MarqueeTrack[] = []
  const dirPattern: Array<1 | -1> = [1, -1, 1, -1, 1]

  backgrounds.forEach((bg, bi) => {
    if (bg.type !== 'dark') return
    bg.letters.forEach((_, li) => {
      const el = trackRefMap.get(`${bi}-${li}`)
      if (el) {
        allTracks.push({ el, direction: dirPattern[li % dirPattern.length] })
      }
    })
  })

  if (bgLayerRef.value) {
    initTracks(allTracks, container, bgLayerRef.value)
  }
}

// Background crossfade
let currentBgIndex = 0

function fadeToBackground(targetIndex: number) {
  if (targetIndex === currentBgIndex) return

  const outEl = bgRefs.get(currentBgIndex)
  const inEl = bgRefs.get(targetIndex)

  if (outEl) gsap.to(outEl, { opacity: 0, duration: 0.7, ease: 'power2.inOut' })
  if (inEl) gsap.to(inEl, { opacity: 1, duration: 0.7, ease: 'power2.inOut' })

  currentBgIndex = targetIndex
}

function setupScrollTriggers(scroller: HTMLElement | Window) {
  // Show first bg
  bgRefs.forEach((el, idx) => {
    gsap.set(el, { opacity: idx === 0 ? 1 : 0 })
  })

  const sections = [
    sectionRefs_0.value,
    sectionRefs_1.value,
    sectionRefs_2.value,
    sectionRefs_3.value,
    sectionRefs_4.value,
    sectionRefs_5.value,
    sectionRefs_6.value,
  ]

  const bgMap = [0, 1, 2, 3, 4, 5, 0]
  const scrollerOpt = scroller instanceof Window ? undefined : scroller

  sections.forEach((section, i) => {
    if (!section) return

    ScrollTrigger.create({
      trigger: section,
      scroller: scrollerOpt,
      start: 'top 60%',
      end: 'bottom 40%',
      onEnter: () => fadeToBackground(bgMap[i]),
      onEnterBack: () => fadeToBackground(bgMap[i]),
    })
  })

  // Hero parallax: move hero text up on scroll
  if (sectionRefs_0.value) {
    gsap.to('.hero-inner', {
      y: -120,
      ease: 'none',
      scrollTrigger: {
        trigger: sectionRefs_0.value,
        scroller: scrollerOpt,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    })
  }

  // Tools card reveal animation with stagger
  cardRefs.forEach((cardEl, idx) => {
    gsap.fromTo(cardEl,
      { opacity: 0, y: 40 },
      {
        opacity: 1,
        y: 0,
        duration: 0.6,
        ease: 'power2.out',
        scrollTrigger: {
          trigger: cardEl,
          scroller: scrollerOpt,
          start: 'top 90%',
          once: true,
        },
        delay: idx * 0.04,
      }
    )
  })
}

onMounted(async () => {
  await nextTick()

  // Start loading animation
  animateLoading()

  // Wait a frame for DOM to settle, then init scroll features
  requestAnimationFrame(() => {
    const scroller = getScrollContainer()
    const container = scroller instanceof Window
      ? document.getElementById('app') || document.body
      : scroller

    initAllMarquees(container)
    setupScrollTriggers(scroller)
  })
})

onUnmounted(() => {
  ScrollTrigger.getAll().forEach(st => st.kill())
})
</script>

<style scoped>
/* ══════ ROOT ══════ */
.home-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #000;
  color: #fff;
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* ══════ CUSTOM SCROLLBAR ══════ */
.home-root ::-webkit-scrollbar { width: 8px; }
.home-root ::-webkit-scrollbar-track { background: #000; }
.home-root ::-webkit-scrollbar-thumb { background: #e63946; }

/* ══════ LOADING SCREEN ══════ */
.loading-screen {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #e63946;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-screen.gone {
  pointer-events: none;
}

.loading-text {
  font-size: clamp(3rem, 12vw, 9rem);
  font-weight: 900;
  color: #000;
  letter-spacing: -0.05em;
  line-height: 0.9;
  text-transform: uppercase;
  transform-origin: bottom center;
}

/* ══════ NOISE OVERLAY ══════ */
.noise-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  pointer-events: none;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* ══════ TOP NAVIGATION ══════ */
.top-nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 40;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  mix-blend-mode: difference;
  color: #fff;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-diamond {
  font-size: 10px;
}

.nav-brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.nav-links {
  display: flex;
  gap: 28px;
}

.nav-link {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.nav-link:hover {
  text-decoration: line-through;
  text-decoration-color: #e63946;
  text-decoration-thickness: 2px;
}

/* ══════ FIXED BACKGROUND LAYER ══════ */
.bg-layer {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  --stretch: 1;
}

.bg-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
}

.bg-slide.dark { background: #050505; }
.bg-slide.red { background: #e63946; }

/* ── Grid overlay on dark slides ── */
.grid-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.06;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.15) 1px, transparent 1px);
  background-size: 100px 100px;
}

/* ── Decorative vertical lines ── */
.decor-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(255, 255, 255, 0.06);
}
.decor-line-left { left: 48px; }
.decor-line-right { right: 48px; }

/* ── Marquee ── */
.marquee-bg {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0;
  overflow: hidden;
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
  font-size: clamp(5rem, 16vw, 14rem);
  font-weight: 900;
  color: #e63946;
  opacity: 0.85;
  letter-spacing: -0.02em;
  padding: 0 0.06em;
  flex-shrink: 0;
  user-select: none;
  line-height: 0.9;
  transform: scaleY(var(--stretch, 1));
  transform-origin: center center;
}

/* ── Center card on dark slides ── */
.slide-center {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.center-card {
  background: rgba(0, 0, 0, 0.82);
  backdrop-filter: blur(8px);
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

/* ── Red bg typography ── */
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

/* ══════ CONTENT LAYER ══════ */
.content-layer {
  position: relative;
  z-index: 1;
}

/* ══════ SECTIONS ══════ */
.section {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spacer {
  pointer-events: none;
}

/* ── Hero ── */
.hero-section {
  flex-direction: column;
  position: relative;
}

.hero-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 2rem;
  will-change: transform;
}

.hero-eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.5em;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  margin-bottom: 20px;
}

.hero-title-wrap {
  position: relative;
}

.hero-headline {
  font-size: clamp(2.8rem, 10vw, 8rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 0.85;
  margin: 0;
  text-transform: uppercase;
}

.hero-subline {
  font-size: clamp(2.8rem, 10vw, 8rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 0.85;
  color: #e63946;
  margin: 0;
  text-transform: uppercase;
}

.hero-desc {
  font-size: clamp(0.85rem, 1.4vw, 1.05rem);
  color: rgba(255, 255, 255, 0.35);
  margin-top: 28px;
  line-height: 1.6;
  max-width: 500px;
}

.hero-bottom {
  position: absolute;
  bottom: -60vh;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 24px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
}

.hero-scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 56px;
  color: rgba(255, 255, 255, 0.2);
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2em;
}

.scroll-line {
  width: 1px;
  height: 40px;
  background: currentColor;
  animation: pulse-line 2s ease-in-out infinite;
}

@keyframes pulse-line {
  0%, 100% { opacity: 0.2; transform: scaleY(0.5); }
  50% { opacity: 1; transform: scaleY(1); }
}

/* ══════ MARQUEE STRIP DIVIDER ══════ */
.marquee-strip {
  background: #e63946;
  overflow: hidden;
  padding: 12px 0;
  position: relative;
  z-index: 2;
}

.marquee-strip-dark {
  background: #000;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.marquee-strip-inner {
  display: flex;
  white-space: nowrap;
  animation: strip-scroll 25s linear infinite;
}

.marquee-strip-reverse {
  animation-direction: reverse;
}

.strip-text {
  font-size: clamp(1.5rem, 4vw, 3.5rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.03em;
  padding: 0 12px;
  flex-shrink: 0;
}

.marquee-strip .strip-text { color: #000; }
.marquee-strip-dark .strip-text { color: rgba(255, 255, 255, 0.8); }

@keyframes strip-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* ══════ TOOLS ══════ */
.tools-section {
  padding: 80px 2rem 60px;
}

.tools-wrap {
  max-width: 1100px;
  margin: 0 auto;
}

.tools-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.tools-header-left {}

.tools-counter {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.3);
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
  margin: 0;
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
  background: rgba(13, 13, 13, 0.92);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.g-card:hover {
  background: rgba(20, 20, 20, 0.95);
  border-color: #e63946;
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(230, 57, 70, 0.1);
}

.g-card.is-active { border-color: #e63946; z-index: 10; }
.g-card.is-faded { opacity: 0.3; filter: blur(2px); pointer-events: none; }

.g-card-accent { width: 3px; align-self: stretch; border-radius: 2px; flex-shrink: 0; }
.g-card-accent.red { background: #e63946; }
.g-card-accent.dark { background: rgba(255, 255, 255, 0.12); }

.g-card-body { flex: 1; min-width: 0; }

.g-card-index {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: rgba(255, 255, 255, 0.25);
  display: block;
  margin-bottom: 4px;
}

.g-card-title { font-size: 0.88rem; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 3px; }
.g-card-desc { font-size: 0.72rem; color: rgba(255, 255, 255, 0.4); line-height: 1.5; }

.g-card-arrow { font-size: 1rem; color: rgba(255, 255, 255, 0.15); flex-shrink: 0; transition: all 0.3s; }
.g-card:hover .g-card-arrow { color: #e63946; transform: translateX(4px); }

/* ══════ TERMINAL ══════ */
.terminal-section { padding: 20px 2rem 40px; }

.terminal-card {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  background: rgba(13, 13, 13, 0.92);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(230, 57, 70, 0.15);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}

.terminal-card:hover {
  border-color: #e63946;
  background: rgba(17, 17, 17, 0.95);
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.1);
}

.terminal-card.is-active { border-color: #e63946; }

.terminal-zeta {
  width: 52px; height: 52px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.8rem; font-weight: 900; color: #e63946;
  background: rgba(230, 57, 70, 0.08);
  border: 1px solid rgba(230, 57, 70, 0.2);
  border-radius: 3px; flex-shrink: 0;
}

.terminal-info { flex: 1; }
.terminal-title { font-size: 1rem; font-weight: 700; margin-bottom: 3px; }
.terminal-sub { font-size: 0.75rem; color: rgba(255, 255, 255, 0.4); line-height: 1.5; }

.terminal-cta { font-size: 0.85rem; font-weight: 700; color: #e63946; flex-shrink: 0; transition: transform 0.3s; }
.terminal-card:hover .terminal-cta { transform: translateX(4px); }

/* ══════ TRANSITION OVERLAY ══════ */
.transition-overlay {
  position: fixed; inset: 0; background: #000; z-index: 9998;
  opacity: 0; pointer-events: none;
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.transition-overlay.active { opacity: 1; transition-delay: 0.1s; }

.footer-spacer { height: 60px; }

/* ══════ RESPONSIVE ══════ */
@media (max-width: 1024px) {
  .tools-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 768px) {
  .marquee-letter { font-size: clamp(3.5rem, 16vw, 7rem); }
  .center-card { padding: 24px 28px; margin: 0 1rem; }
  .tools-section { padding: 60px 1rem 48px; }
  .tools-grid { grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .g-card { padding: 14px 16px; }
  .terminal-section { padding: 12px 1rem 32px; }
  .terminal-card { padding: 18px 20px; }
  .red-headline { font-size: clamp(2.5rem, 14vw, 6rem); }
  .nav-links { display: none; }
  .hero-bottom-hide-mobile { display: none; }
  .decor-line { display: none; }
  .hero-bottom { bottom: -40vh; }
}

@media (max-width: 480px) {
  .marquee-letter { font-size: clamp(2.5rem, 18vw, 4.5rem); }
  .tools-grid { grid-template-columns: 1fr; }
  .g-card-arrow { display: none; }
  .hero-headline { font-size: 2.5rem; }
  .hero-subline { font-size: 2.5rem; }
  .terminal-card { flex-wrap: wrap; }
  .terminal-cta { width: 100%; text-align: center; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.06); }
  .hero-bottom { padding: 0 16px; font-size: 11px; }
}
</style>
