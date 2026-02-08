<template>
  <div class="home-root" ref="rootRef">
    <!-- ═══ FIXED BACKGROUND LAYER (crossfades on scroll) ═══ -->
    <div class="bg-layer">
      <div
        v-for="(bg, bi) in backgrounds"
        :key="bi"
        class="bg-slide"
        :class="bg.type"
        :ref="(el) => setBgRef(el as HTMLElement | null, bi)"
      >
        <!-- DARK: marquee letter rows -->
        <template v-if="bg.type === 'dark'">
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
      <!-- Section 0: Hero -->
      <section class="section hero-section" ref="section0">
        <div class="hero-inner">
          <div class="brand">&#9670; STOCHASTIC</div>
          <h1 class="hero-headline">QUANTITATIVE</h1>
          <p class="hero-subline">ANALYTICS</p>
          <p class="hero-desc">Платформа количественного анализа для финансовых рынков</p>
          <div class="hero-scroll-hint">
            <span>SCROLL</span>
            <div class="scroll-line"></div>
          </div>
        </div>
      </section>

      <!-- Section 1: statement -->
      <section class="section statement-section" ref="section1">
        <div class="statement-inner">
          <div class="stat-eyebrow">STOCHASTIC PLATFORM</div>
          <div class="stat-text">Стохастические модели, ценообразование деривативов, портфельный анализ и риск-менеджмент</div>
        </div>
      </section>

      <!-- Section 2: features -->
      <section class="section features-section" ref="section2">
        <div class="features-inner">
          <div class="stat-eyebrow">RISK ENGINE</div>
          <div class="stat-text">VaR, стресс-тесты, HMM-режимы, факторный анализ, бэктестинг</div>
        </div>
      </section>

      <!-- Section 3: models -->
      <section class="section models-section" ref="section3">
        <div class="models-inner">
          <div class="stat-eyebrow">MODELS</div>
          <div class="stat-text">Black-Scholes · Heston · SABR · Monte Carlo · Lévy · FFT</div>
        </div>
      </section>

      <!-- Section 4: volatility -->
      <section class="section vol-section" ref="section4">
        <div class="vol-inner">
          <div class="stat-eyebrow">VOLATILITY SURFACE</div>
          <div class="stat-text">SABR/SVI калибровка, smile & term-structure, FFT-ценообразование</div>
        </div>
      </section>

      <!-- Section 5: optimize -->
      <section class="section opt-section" ref="section5">
        <div class="opt-inner">
          <div class="stat-eyebrow">OPTIMIZATION</div>
          <div class="stat-text">Sharpe, VaR, Greeks, P&L Attribution, портфельная оптимизация</div>
        </div>
      </section>

      <!-- Tools grid -->
      <section class="section tools-section" ref="toolsSection">
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

      <!-- Terminal -->
      <section class="section terminal-section">
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
import { useKineticMarquee, type MarqueeTrack } from '@/composables/useKineticMarquee'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()
const rootRef = ref<HTMLElement | null>(null)
const activeTool = ref<string | null>(null)

// Section refs
const section0 = ref<HTMLElement | null>(null)
const section1 = ref<HTMLElement | null>(null)
const section2 = ref<HTMLElement | null>(null)
const section3 = ref<HTMLElement | null>(null)
const section4 = ref<HTMLElement | null>(null)
const section5 = ref<HTMLElement | null>(null)
const toolsSection = ref<HTMLElement | null>(null)

// Background definitions
interface DarkBg {
  type: 'dark'
  letters: string[]
}

interface RedBg {
  type: 'red'
  topLine?: string
  headline: string
  bottomLine?: string
}

type BgSlide = DarkBg | RedBg

const backgrounds: BgSlide[] = [
  { type: 'dark', letters: ['Q', 'U', 'A', 'N'] },
  { type: 'red', topLine: 'QUANTITATIVE', headline: 'ANALYTICS', bottomLine: 'STOCHASTIC MODELS' },
  { type: 'dark', letters: ['R', 'I', 'S', 'K'] },
  { type: 'red', topLine: 'BLACK-SCHOLES', headline: 'HESTON', bottomLine: 'MONTE CARLO \u00b7 L\u00c9VY' },
  { type: 'dark', letters: ['V', 'O', 'L', 'A'] },
  { type: 'red', topLine: 'PORTFOLIO', headline: 'OPTIMIZE', bottomLine: 'SHARPE \u00b7 VAR \u00b7 GREEKS' },
]

// Each content section maps to a background index
// section0 -> bg0 (QUAN dark)
// section1 -> bg1 (ANALYTICS red)
// section2 -> bg2 (RISK dark)
// section3 -> bg3 (HESTON red)
// section4 -> bg4 (VOLA dark)
// section5 -> bg5 (OPTIMIZE red)
// toolsSection -> bg0 (back to QUAN dark)

const tools = [
  { name: '\u041f\u043e\u0440\u0442\u0444\u0435\u043b\u044c\u043d\u044b\u0439 \u0430\u043d\u0430\u043b\u0438\u0437', desc: '\u0414\u043e\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u044c, VaR/ES, \u043c\u043e\u043d\u0438\u0442\u043e\u0440\u0438\u043d\u0433 \u043f\u043e\u0437\u0438\u0446\u0438\u0439', color: 'red', path: '/portfolio' },
  { name: '\u0420\u0438\u0441\u043a-\u043c\u0435\u043d\u0435\u0434\u0436\u043c\u0435\u043d\u0442', desc: '\u0421\u0442\u0440\u0435\u0441\u0441-\u0442\u0435\u0441\u0442\u044b, \u0431\u044d\u043a\u0442\u0435\u0441\u0442\u0438\u043d\u0433 VaR, \u0441\u0446\u0435\u043d\u0430\u0440\u0438\u0438', color: 'dark', path: '/stress' },
  { name: '\u0420\u044b\u043d\u043e\u0447\u043d\u044b\u0435 \u0440\u0435\u0436\u0438\u043c\u044b', desc: 'HMM, \u0441\u0442\u0430\u0446\u0438\u043e\u043d\u0430\u0440\u043d\u043e\u0435 \u0440\u0430\u0441\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435', color: 'red', path: '/regimes' },
  { name: '\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043e\u0431\u043b\u0438\u0433\u0430\u0446\u0438\u0439', desc: 'DCF, \u0434\u044e\u0440\u0430\u0446\u0438\u044f, convexity, \u0441\u043f\u0440\u0435\u0434\u044b', color: 'dark', path: '/bond-valuation' },
  { name: '\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043e\u043f\u0446\u0438\u043e\u043d\u043e\u0432', desc: '\u0411\u0428\u041c, \u0425\u0435\u0441\u0442\u043e\u043d, \u041b\u0435\u0432\u0438, FFT', color: 'red', path: '/pricing/options' },
  { name: '\u0412\u043e\u043b\u0430\u0442\u0438\u043b\u044c\u043d\u043e\u0441\u0442\u044c', desc: 'SABR/SVI \u043a\u0430\u043b\u0438\u0431\u0440\u043e\u0432\u043a\u0430, smile', color: 'dark', path: '/analytics/volatility' },
  { name: '\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0421\u0412\u041e\u041f\u043e\u0432', desc: 'IRS & FX \u0441\u0432\u043e\u043f\u044b, NPV, DV01', color: 'red', path: 'valuation/swaps' },
  { name: '\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0444\u043e\u0440\u0432\u0430\u0440\u0434\u043e\u0432', desc: '\u0421\u043f\u0440\u0430\u0432\u0435\u0434\u043b\u0438\u0432\u0430\u044f \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c, \u043a\u0440\u0438\u0432\u0430\u044f', color: 'dark', path: 'valuation/forwards' },
  { name: '\u041e\u0442\u0447\u0451\u0442\u044b', desc: 'Bond Report, \u0448\u0430\u0431\u043b\u043e\u043d\u043d\u044b\u0435 \u043e\u0442\u0447\u0451\u0442\u044b', color: 'red', path: '/vanila-bond-report' },
  { name: '\u041c\u043e\u043d\u0442\u0435-\u041a\u0430\u0440\u043b\u043e', desc: '\u0421\u0438\u043c\u0443\u043b\u044f\u0446\u0438\u0438, \u0441\u0442\u043e\u0445\u0430\u0441\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u043c\u043e\u0434\u0435\u043b\u0438', color: 'dark', path: '/monte-carlo' },
  { name: '\u041a\u0440\u0438\u0432\u0430\u044f \u0434\u043e\u0445\u043e\u0434\u043d\u043e\u0441\u0442\u0438', desc: 'ZCYC, zero-coupon yield curve', color: 'red', path: '/zcyc-viewer' },
  { name: 'P&L Attribution', desc: '\u0424\u0430\u043a\u0442\u043e\u0440\u043d\u0430\u044f \u0434\u0435\u043a\u043e\u043c\u043f\u043e\u0437\u0438\u0446\u0438\u044f P&L', color: 'dark', path: '/analytics/pnl' },
  { name: 'Citadel Zeta Field', desc: '\u0413\u0440\u0430\u0432\u0438\u0442\u0430\u0446\u0438\u043e\u043d\u043d\u043e\u0435 \u043f\u043e\u043b\u0435 \u043b\u0438\u043a\u0432\u0438\u0434\u043d\u043e\u0441\u0442\u0438', color: 'red', path: '/terminal' },
  { name: 'Phase Space', desc: '\u0424\u0430\u0437\u043e\u0432\u043e\u0435 \u043f\u0440\u043e\u0441\u0442\u0440\u0430\u043d\u0441\u0442\u0432\u043e, \u0430\u0442\u0442\u0440\u0430\u043a\u0442\u043e\u0440\u044b', color: 'dark', path: '/terminal' },
  { name: 'Liquidity Model', desc: '\u041c\u043e\u0434\u0435\u043b\u044c \u043b\u0438\u043a\u0432\u0438\u0434\u043d\u043e\u0441\u0442\u0438 \u0440\u044b\u043d\u043a\u0430', color: 'red', path: '/terminal' },
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

const { initTracks, boostAll } = useKineticMarquee()

// Navigation
function navigateTo(path: string, e: MouseEvent) {
  if (activeTool.value) return
  activeTool.value = path

  const card = e.currentTarget as HTMLElement
  gsap.to(card, { scale: 1.03, duration: 0.3, ease: 'power2.out' })
  boostAll(5, 0.3)

  setTimeout(() => router.push(path), 500)
}

// Init marquees for all dark backgrounds
function initAllMarquees() {
  const allTracks: MarqueeTrack[] = []
  const directions: Array<1 | -1> = [1, -1, 1, -1]

  backgrounds.forEach((bg, bi) => {
    if (bg.type !== 'dark') return
    bg.letters.forEach((_, li) => {
      const el = trackRefMap.get(`${bi}-${li}`)
      if (el) {
        allTracks.push({ el, direction: directions[li] })
      }
    })
  })

  initTracks(allTracks)
}

// Setup scroll-driven background crossfading
function setupScrollTriggers() {
  // Map: which section triggers which background
  const sectionToBg: Array<{ section: HTMLElement | null; bgIndex: number }> = [
    { section: section0.value, bgIndex: 0 },
    { section: section1.value, bgIndex: 1 },
    { section: section2.value, bgIndex: 2 },
    { section: section3.value, bgIndex: 3 },
    { section: section4.value, bgIndex: 4 },
    { section: section5.value, bgIndex: 5 },
    { section: toolsSection.value, bgIndex: 0 },
  ]

  // Show first bg initially
  bgRefs.forEach((el, idx) => {
    gsap.set(el, { opacity: idx === 0 ? 1 : 0 })
  })

  sectionToBg.forEach(({ section, bgIndex }) => {
    if (!section) return

    ScrollTrigger.create({
      trigger: section,
      start: 'top 60%',
      end: 'bottom 40%',
      onEnter: () => fadeToBackground(bgIndex),
      onEnterBack: () => fadeToBackground(bgIndex),
    })
  })
}

let currentBgIndex = 0

function fadeToBackground(targetIndex: number) {
  if (targetIndex === currentBgIndex) return

  const outEl = bgRefs.get(currentBgIndex)
  const inEl = bgRefs.get(targetIndex)

  if (outEl) {
    gsap.to(outEl, { opacity: 0, duration: 0.6, ease: 'power2.inOut' })
  }
  if (inEl) {
    gsap.to(inEl, { opacity: 1, duration: 0.6, ease: 'power2.inOut' })
  }

  // Boost marquee on transition
  boostAll(3, 0.2)
  setTimeout(() => {
    boostAll(1, 0.8)
  }, 300)

  currentBgIndex = targetIndex
}

onMounted(async () => {
  await nextTick()
  initAllMarquees()
  setupScrollTriggers()

  // Entrance animation for content
  gsap.fromTo('.content-layer', { opacity: 0 }, { opacity: 1, duration: 0.6, delay: 0.1 })
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

/* ══════ FIXED BACKGROUND LAYER ══════ */
.bg-layer {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.bg-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
}

.bg-slide.dark {
  background: #000;
}

.bg-slide.red {
  background: #e63946;
}

/* ── Marquee inside dark bg ── */
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

/* ══════ CONTENT LAYER (scrollable) ══════ */
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

/* ── Hero ── */
.hero-section {
  flex-direction: column;
}

.hero-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 0 2rem;
}

.brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 24px;
}

.hero-headline {
  font-size: clamp(2.8rem, 8vw, 6rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  margin: 0;
}

.hero-subline {
  font-size: clamp(1.6rem, 4.5vw, 3.2rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #e63946;
  margin-top: 8px;
}

.hero-desc {
  font-size: clamp(0.85rem, 1.4vw, 1.05rem);
  color: rgba(255, 255, 255, 0.4);
  margin-top: 20px;
  line-height: 1.6;
  max-width: 500px;
}

.hero-scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-top: 48px;
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

/* ── Statement/feature sections (overlay text on bg) ── */
.statement-section,
.features-section,
.models-section,
.vol-section,
.opt-section {
  padding: 0 2rem;
}

.statement-inner,
.features-inner,
.models-inner,
.vol-inner,
.opt-inner {
  max-width: 600px;
  text-align: center;
}

.stat-eyebrow {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.25em;
  margin-bottom: 16px;
  opacity: 0.5;
}

.stat-text {
  font-size: clamp(1.2rem, 2.5vw, 1.8rem);
  font-weight: 700;
  line-height: 1.5;
  letter-spacing: -0.02em;
}

/* On red backgrounds, text should be dark */
.statement-section .stat-eyebrow,
.models-section .stat-eyebrow,
.opt-section .stat-eyebrow {
  color: rgba(0, 0, 0, 0.4);
}

.statement-section .stat-text,
.models-section .stat-text,
.opt-section .stat-text {
  color: rgba(0, 0, 0, 0.85);
}

/* On dark backgrounds, text stays white */
.features-section .stat-eyebrow,
.vol-section .stat-eyebrow {
  color: rgba(255, 255, 255, 0.4);
}

.features-section .stat-text,
.vol-section .stat-text {
  color: rgba(255, 255, 255, 0.9);
}

/* ══════ TOOLS SECTION ══════ */
.tools-section {
  min-height: auto;
  padding: 80px 2rem 60px;
  display: block;
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
  background: rgba(13, 13, 13, 0.9);
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
  min-height: auto;
  padding: 20px 2rem 40px;
  display: block;
}

.terminal-card {
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  background: rgba(13, 13, 13, 0.9);
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

  .tools-section {
    padding: 60px 1rem 48px;
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

  .stat-text {
    font-size: clamp(1rem, 3vw, 1.4rem);
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

  .hero-headline {
    font-size: 2.2rem;
  }

  .hero-subline {
    font-size: 1.4rem;
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
}
</style>
