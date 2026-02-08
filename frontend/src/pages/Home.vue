<template>
  <div class="home-root">
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

      <!-- Spacer sections (transparent, trigger bg change) -->
      <section class="section spacer" ref="sectionRefs_1"></section>
      <section class="section spacer" ref="sectionRefs_2"></section>
      <section class="section spacer" ref="sectionRefs_3"></section>
      <section class="section spacer" ref="sectionRefs_4"></section>
      <section class="section spacer" ref="sectionRefs_5"></section>

      <!-- Tools grid -->
      <section class="tools-section" ref="sectionRefs_6">
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
const bgLayerRef = ref<HTMLElement | null>(null)
const activeTool = ref<string | null>(null)

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

const { initTracks } = useKineticMarquee()

// Navigation
function navigateTo(path: string, e: MouseEvent) {
  if (activeTool.value) return
  activeTool.value = path
  const card = e.currentTarget as HTMLElement
  gsap.to(card, { scale: 1.03, duration: 0.3, ease: 'power2.out' })
  setTimeout(() => router.push(path), 500)
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

function setupScrollTriggers(container: HTMLElement) {
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

  // bg indices: hero→0, spacer1→1, spacer2→2, spacer3→3, spacer4→4, spacer5→5, tools→0
  const bgMap = [0, 1, 2, 3, 4, 5, 0]

  sections.forEach((section, i) => {
    if (!section) return

    ScrollTrigger.create({
      trigger: section,
      scroller: container,
      start: 'top 60%',
      end: 'bottom 40%',
      onEnter: () => fadeToBackground(bgMap[i]),
      onEnterBack: () => fadeToBackground(bgMap[i]),
    })
  })
}

onMounted(async () => {
  await nextTick()

  const container = document.getElementById('app')
  if (!container) return

  initAllMarquees(container)
  setupScrollTriggers(container)
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
  --stretch: 1;
}

.bg-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
}

.bg-slide.dark { background: #000; }
.bg-slide.red { background: #e63946; }

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

/* ══════ TOOLS ══════ */
.tools-section {
  padding: 80px 2rem 60px;
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
}

@media (max-width: 480px) {
  .marquee-letter { font-size: clamp(2.5rem, 18vw, 4.5rem); }
  .tools-grid { grid-template-columns: 1fr; }
  .g-card-arrow { display: none; }
  .hero-headline { font-size: 2.2rem; }
  .hero-subline { font-size: 1.4rem; }
  .terminal-card { flex-wrap: wrap; }
  .terminal-cta { width: 100%; text-align: center; padding-top: 8px; border-top: 1px solid rgba(255, 255, 255, 0.06); }
}
</style>
