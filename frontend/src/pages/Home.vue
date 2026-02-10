<template>
  <div class="home-root">
    <!-- Noise Overlay -->
    <div class="bg-noise"></div>

    <!-- Loading Screen -->
    <div v-if="showLoader" ref="loaderRef" class="loader">
      <h1 class="loader-text">LOADING...</h1>
    </div>

    <!-- Navigation -->
    <nav class="nav">
      <div class="nav-left">
        <span class="nav-brand font-mono">&#9670; Quantitative / Dashboard</span>
      </div>
      <div class="nav-links">
        <a href="#tools" class="nav-link font-oswald" @click.prevent="scrollTo('tools')">Инструменты</a>
        <a href="#terminal" class="nav-link font-oswald" @click.prevent="scrollTo('terminal')">Терминал</a>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">

      <!-- ══════ HERO ══════ -->
      <section ref="heroRef" class="hero">
        <div class="hero-grid-overlay"></div>
        <div ref="heroContentRef" class="hero-content">
          <h2 ref="heroSubtitleRef" class="hero-subtitle font-mono">Quantitative Dashboard</h2>
          <div class="hero-titles">
            <h1 ref="heroTitle1Ref" class="hero-title font-anton">ZETA TERMINAL</h1>
          </div>
        </div>
        <div ref="heroBottomRef" class="hero-bottom font-oswald">
          <span>&#9670; Finance</span>
          <span>2026</span>
          <span class="hide-mobile">Quantitative Analytics</span>
        </div>
        <div class="hero-line hero-line-left"></div>
        <div class="hero-line hero-line-right"></div>
      </section>

      <!-- ══════ MARQUEE RED ══════ -->
      <div class="marquee-strip marquee-red">
        <div class="marquee-track">
          <span v-for="n in 5" :key="'r'+n" class="font-anton">STOCHASTIC ANALYSIS &mdash; QUANTITATIVE ANALYTICS &mdash; DERIVATIVES &mdash; BONDS &mdash; SWAPS &mdash; FORWARDS &mdash; OPTIONS &mdash; MARKET REGIMES &mdash; P&L CALCULATIONS &mdash; RISK-MANAGEMENT &mdash;&nbsp;</span>
        </div>
      </div>

      <!-- ══════ ABOUT (ReviewContent) ══════ -->
      <section class="about">
        <div class="about-grid">
          <div class="about-left">
            <div class="about-sticky">
              <h2 class="about-title font-anton">КОЛИЧЕСТВЕННЫЙ<br/>РИСК<br/>МЕНЕДЖМЕНТ</h2>
              <div class="about-divider"></div>
              <div class="about-meta font-mono">
                <p>ИНСТРУМЕНТОВ: 27</p>
                <p>МОДЕЛЕЙ: 8+</p>
              </div>
            </div>
          </div>
          <div class="about-right">
            <div ref="aboutBlock1" class="about-block">
              <p class="about-intro font-oswald">Платформа стохастического моделирования для количественного анализа финансовых рынков, ценообразования деривативов и управления рисками.</p>
              <p class="about-body font-mono">Дзета Терминал объединяет классические модели ценообразования с современными вычислительными методами. Модели Блэка-Шоулза-Мертона и Хестона, Случайные процессы Леви, 2D и 3D симуляции Монте-Карло, тепловые карты активов — все инструменты доступны в едином интерфейсе</p>
            </div>
            <div ref="aboutBlock2" class="about-block about-quote">
              <p class="about-quote-text font-anton">СТОХАСТИЧЕСКОЕ МОДЕЛИРОВАНИЕ НА УРОВНЕ ИНСТИТУЦИОНАЛЬНЫХ ПЛАТФОРМ</p>
            </div>
            <div ref="aboutBlock3" class="about-block about-cols">
              <div>
                <h3 class="about-col-title font-oswald">Ценообразование</h3>
                <p class="about-col-body font-mono">Black-Scholes, Heston, SABR, FFT-методы, implied volatility surface. Полный стек для опционов, свопов, форвардов и структурных продуктов.</p>
              </div>
              <div>
                <h3 class="about-col-title font-oswald">Риск-менеджмент</h3>
                <p class="about-col-body font-mono">VaR, Expected Shortfall, стресс-тестирование, бэктестинг, греки, режимы рынка через HMM. Портфельная оптимизация по Марковицу и Black-Litterman.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ══════ MARQUEE DARK ══════ -->
      <div class="marquee-strip marquee-dark">
        <div class="marquee-track marquee-reverse">
          <span v-for="n in 5" :key="'d'+n" class="font-anton">BLACK-SCHOLES &mdash; HESTON &mdash; MONTE CARLO &mdash; L&Eacute;VY &mdash;&nbsp;</span>
        </div>
      </div>

      <!-- ══════ TOOLS (TrackList) ══════ -->
      <section id="tools" class="tools">
        <div class="tools-bg-text font-anton">
          QQQQQQQ<br/>UUUUUUU<br/>AAAAAAA<br/>NNNNNNN<br/>TTTTTTT
        </div>
        <div class="tools-inner">
          <div class="tools-header">
            <h2 class="tools-title font-anton">Инструменты</h2>
            <div class="tools-underline"></div>
          </div>
          <div class="tools-list">
            <div
              v-for="(tool, i) in tools"
              :key="tool.path + i"
              ref="toolRowRefs"
              class="tool-row"
              @click="navigateTo(tool.path)"
            >
              <div class="tool-left">
                <span class="tool-index font-mono">{{ String(i + 1).padStart(2, '0') }}</span>
                <button class="tool-play">
                  <span>&rarr;</span>
                </button>
                <div class="tool-info">
                  <span class="tool-name font-oswald">{{ tool.name }}</span>
                  <span v-if="tool.desc" class="tool-desc font-mono">{{ tool.desc }}</span>
                </div>
              </div>
              <span class="tool-arrow font-mono">&rarr;</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ══════ TERMINAL ══════ -->
      <section id="terminal" class="terminal-section">
        <div class="terminal-card" @click="navigateTo('/terminal')">
          <div class="terminal-zeta font-anton">&zeta;</div>
          <div class="terminal-info">
            <div class="terminal-title font-oswald">Дзета-Терминал</div>
            <div class="terminal-sub font-mono">Потоковые данные в реальном времени &middot; Акции &middot; Крипто &middot; Фьючерсы &middot; Опционы</div>
          </div>
          <div class="terminal-cta font-oswald">Открыть &rarr;</div>
        </div>
      </section>

      <!-- ══════ FOOTER ══════ -->
      <footer class="footer">
        <div class="footer-inner">
          <div class="footer-main">
            <h2 class="footer-title font-anton">STOCHASTIC</h2>
            <p class="footer-subtitle font-oswald">Quantitative Analytics Platform</p>
          </div>
          <div class="footer-credits">
            <div class="footer-col">
              <h4 class="footer-col-head">Platform</h4>
              <p class="font-mono">Vue 3 / TypeScript</p>
              <p class="font-mono">GSAP / ECharts</p>
              <p class="font-mono">Three.js</p>
            </div>
            <div class="footer-col">
              <h4 class="footer-col-head">Models</h4>
              <p class="font-mono">Black-Scholes</p>
              <p class="font-mono">Heston / SABR</p>
              <p class="font-mono">Monte Carlo</p>
            </div>
          </div>
        </div>
        <div class="footer-bottom font-mono">
          <span>&copy; 2026 Stochastic Platform</span>
          <span>Quantitative Analytics</span>
        </div>
      </footer>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/dist/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()

// Refs
const loaderRef = ref<HTMLElement | null>(null)
const heroRef = ref<HTMLElement | null>(null)
const heroContentRef = ref<HTMLElement | null>(null)
const heroSubtitleRef = ref<HTMLElement | null>(null)
const heroTitle1Ref = ref<HTMLElement | null>(null)
const heroBottomRef = ref<HTMLElement | null>(null)
const aboutBlock1 = ref<HTMLElement | null>(null)
const aboutBlock2 = ref<HTMLElement | null>(null)
const aboutBlock3 = ref<HTMLElement | null>(null)
const toolRowRefs = ref<HTMLElement[]>([])
const showLoader = ref(true)

const tools = [
  { name: 'Портфельный анализ', desc: 'Доходность, VaR/ES, мониторинг позиций', path: '/portfolio' },
  { name: 'Риск-менеджмент', desc: 'Стресс-тесты, бэктестинг VaR, сценарии', path: '/stress' },
  { name: 'Рыночные режимы', desc: 'HMM, стационарное распределение', path: '/regimes' },
  { name: 'Стоимость облигаций', desc: 'DCF, дюрация, convexity, спреды', path: '/bond-valuation' },
  { name: 'Стоимость опционов', desc: 'БШМ, Хестон, Леви, FFT', path: '/pricing/options' },
  { name: 'Волатильность', desc: 'SABR/SVI калибровка, smile', path: '/analytics/volatility' },
  { name: 'Стоимость СВОПов', desc: 'IRS & FX свопы, NPV, DV01', path: '/valuation/swaps' },
  { name: 'Стоимость форвардов', desc: 'Справедливая стоимость, кривая', path: '/valuation/forwards' },
  { name: 'Отчёты', desc: 'Bond Report, шаблонные отчёты', path: '/vanila-bond-report' },
  { name: 'Монте-Карло', desc: 'Симуляции, стохастические модели', path: '/monte-carlo' },
  { name: 'Кривая доходности', desc: 'ZCYC, zero-coupon yield curve', path: '/zcyc-viewer' },
  { name: 'P&L Attribution', desc: 'Факторная декомпозиция P&L', path: '/analytics/pnl' },
  { name: 'Citadel Zeta Field', desc: 'Гравитационное поле ликвидности', path: '/terminal' },
  { name: 'Phase Space', desc: 'Фазовое пространство, аттракторы', path: '/terminal' },
  { name: 'Liquidity Model', desc: 'Модель ликвидности рынка', path: '/terminal' },
]

// Easing from J. Cole project
const EASE = [0.76, 0, 0.24, 1]
const EASE_CSS = 'cubic-bezier(0.76, 0, 0.24, 1)'

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function navigateTo(path: string) {
  router.push(path)
}

function getScroller(): HTMLElement | undefined {
  const app = document.getElementById('app')
  if (!app) return undefined
  const style = getComputedStyle(app)
  if (style.height !== 'auto' && app.scrollHeight > app.clientHeight && (style.overflowY === 'auto' || style.overflowY === 'scroll')) {
    return app
  }
  return undefined
}

onMounted(async () => {
  await nextTick()

  const scroller = getScroller()

  // 1. Loading screen — 1.5s then exit
  setTimeout(() => {
    if (!loaderRef.value) return
    gsap.to(loaderRef.value, {
      opacity: 0,
      y: -50,
      duration: 0.8,
      ease: 'power4.out',
      onComplete: () => {
        showLoader.value = false
        animateHero()
      },
    })
  }, 1500)

  // 2. Hero entrance
  function animateHero() {
    if (heroSubtitleRef.value) {
      gsap.fromTo(heroSubtitleRef.value,
        { y: 100, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, delay: 0, ease: 'power4.out' }
      )
    }
    if (heroTitle1Ref.value) {
      gsap.fromTo(heroTitle1Ref.value,
        { scaleY: 0 },
        { scaleY: 1, duration: 1, delay: 0.1, ease: 'power4.out', transformOrigin: 'bottom center' }
      )
    }
    if (heroBottomRef.value) {
      gsap.fromTo(heroBottomRef.value,
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, delay: 0.3, ease: 'power4.out' }
      )
    }
  }

  // 3. Hero parallax
  if (heroRef.value && heroContentRef.value) {
    gsap.to(heroContentRef.value, {
      yPercent: 50,
      opacity: 0,
      ease: 'none',
      scrollTrigger: {
        trigger: heroRef.value,
        scroller,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    })
  }
  if (heroRef.value && heroBottomRef.value) {
    gsap.to(heroBottomRef.value, {
      yPercent: -50,
      ease: 'none',
      scrollTrigger: {
        trigger: heroRef.value,
        scroller,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    })
  }

  // 4. About blocks — whileInView
  ;[aboutBlock1.value, aboutBlock2.value, aboutBlock3.value].forEach((el) => {
    if (!el) return
    gsap.fromTo(el,
      { opacity: 0, y: 50 },
      {
        opacity: 1, y: 0, duration: 0.8, ease: 'power2.out',
        scrollTrigger: { trigger: el, scroller, start: 'top 85%', once: true },
      }
    )
  })

  // 5. Tool rows — stagger
  await nextTick()
  toolRowRefs.value.forEach((el, i) => {
    gsap.fromTo(el,
      { opacity: 0, x: -20 },
      {
        opacity: 1, x: 0, ease: 'power2.out',
        scrollTrigger: { trigger: el, scroller, start: 'top 90%', once: true },
        delay: i * 0.05,
      }
    )
  })
})

onUnmounted(() => {
  ScrollTrigger.getAll().forEach(st => st.kill())
})
</script>

<style scoped>
/* ══════ FONTS ══════ */
.font-anton { font-family: 'Anton', sans-serif; }
.font-oswald { font-family: 'Oswald', sans-serif; }
.font-mono { font-family: 'Space Mono', monospace; }

/* ══════ ROOT ══════ */
.home-root {
  background: #050505;
  color: #f5f5f5;
  min-height: 100vh;
  position: relative;
  -webkit-font-smoothing: antialiased;
}

.home-root ::selection {
  background: #DC2626;
  color: #fff;
}

/* ══════ SCROLLBAR ══════ */
.home-root ::-webkit-scrollbar { width: 8px; }
.home-root ::-webkit-scrollbar-track { background: #000; }
.home-root ::-webkit-scrollbar-thumb { background: #DC2626; }

/* ══════ NOISE OVERLAY ══════ */
.bg-noise {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 50;
  opacity: 0.05;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
}

/* ══════ LOADER ══════ */
.loader {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: #DC2626;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loader-text {
  font-family: 'Anton', sans-serif;
  font-size: clamp(3rem, 12vw, 9rem);
  color: #000;
  text-transform: uppercase;
  letter-spacing: -0.03em;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ══════ NAVIGATION ══════ */
.nav {
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

.nav-brand {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

.nav-links {
  display: flex;
  gap: 32px;
}

.nav-link {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: inherit;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-link:hover {
  text-decoration: line-through;
  text-decoration-color: #DC2626;
  text-decoration-thickness: 2px;
}

/* ══════ MAIN ══════ */
.main-content {
  position: relative;
  z-index: 10;
}

/* ══════ HERO ══════ */
.hero {
  position: relative;
  height: 100vh;
  overflow: hidden;
  background: #DC2626;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.hero-grid-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.2;
  background-image:
    linear-gradient(#000 1px, transparent 1px),
    linear-gradient(90deg, #000 1px, transparent 1px);
  background-size: 100px 100px;
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 0 16px;
}

.hero-subtitle {
  color: #000;
  font-size: clamp(12px, 1.4vw, 20px);
  margin-bottom: 16px;
  letter-spacing: 0.5em;
  text-transform: uppercase;
}

.hero-titles {
  position: relative;
}

.hero-title {
  font-size: clamp(3rem, 22vw, 22vw);
  line-height: 0.85;
  color: #000;
  text-transform: uppercase;
  mix-blend-mode: multiply;
  margin: 0;
}

.hero-bottom {
  position: absolute;
  bottom: 40px;
  left: 0;
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 0 24px;
  color: #000;
  text-transform: uppercase;
  font-size: 18px;
  z-index: 10;
}

.hero-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 1px;
  background: rgba(0, 0, 0, 0.2);
}
.hero-line-left { left: 48px; }
.hero-line-right { right: 48px; }

/* ══════ MARQUEE STRIP ══════ */
.marquee-strip {
  overflow: hidden;
  padding: 16px 0;
  display: flex;
  position: relative;
  z-index: 20;
}

.marquee-red {
  background: #DC2626;
}

.marquee-dark {
  background: #000;
  border-top: 1px solid #262626;
  border-bottom: 1px solid #262626;
}

.marquee-track {
  display: flex;
  white-space: nowrap;
  animation: marquee-scroll 20s linear infinite;
}

.marquee-reverse {
  animation-direction: reverse;
}

.marquee-track span {
  font-size: clamp(1.5rem, 5vw, 5rem);
  text-transform: uppercase;
  letter-spacing: -0.03em;
  flex-shrink: 0;
}

.marquee-red .marquee-track span { color: #000; }
.marquee-dark .marquee-track span { color: #fff; }

@keyframes marquee-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

@media (min-width: 768px) {
  .marquee-strip { padding: 32px 0; }
}

/* ══════ ABOUT (ReviewContent) ══════ */
.about {
  background: #0a0a0a;
  color: #e5e5e5;
  padding: 96px 24px;
  overflow: hidden;
}

.about-grid {
  max-width: 1280px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
}

.about-sticky {
  position: sticky;
  top: 96px;
}

.about-title {
  font-size: clamp(3rem, 8vw, 6rem);
  color: #DC2626;
  margin: 0 0 32px 0;
  line-height: 0.9;
}

.about-divider {
  width: 100%;
  height: 1px;
  background: #262626;
  margin-bottom: 16px;
}

.about-meta {
  font-size: 14px;
  color: #737373;
}

.about-meta p { margin: 4px 0; }

.about-right {
  display: flex;
  flex-direction: column;
  gap: 64px;
}

.about-block {}

.about-intro {
  font-size: clamp(1.2rem, 3vw, 2rem);
  line-height: 1.4;
  text-transform: uppercase;
  margin: 0 0 32px 0;
}

.about-body {
  color: #a3a3a3;
  font-size: clamp(13px, 1.2vw, 16px);
  line-height: 1.7;
  margin: 0;
}

.about-quote {
  border-left: 4px solid #DC2626;
  padding-left: 32px;
  padding-top: 8px;
  padding-bottom: 8px;
}

.about-quote-text {
  font-size: clamp(1.4rem, 4vw, 3rem);
  text-transform: uppercase;
  line-height: 1.1;
  color: #fff;
  margin: 0;
}

.about-cols {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

.about-col-title {
  font-size: 18px;
  color: #DC2626;
  margin: 0 0 16px 0;
  text-transform: uppercase;
}

.about-col-body {
  color: #a3a3a3;
  font-size: 14px;
  line-height: 1.7;
  margin: 0;
}

@media (min-width: 768px) {
  .about { padding: 96px 48px; }
  .about-grid { grid-template-columns: 4fr 8fr; }
  .about-cols { grid-template-columns: 1fr 1fr; }
}

/* ══════ TOOLS (TrackList) ══════ */
.tools {
  background: #0a0a0a;
  padding: 96px 24px;
  position: relative;
}

.tools-bg-text {
  position: absolute;
  inset: 0;
  overflow: hidden;
  opacity: 0.02;
  pointer-events: none;
  user-select: none;
  font-size: 20vw;
  line-height: 0.8;
  text-align: center;
  word-break: break-all;
  color: #fff;
}

.tools-inner {
  max-width: 896px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.tools-header {
  margin-bottom: 64px;
  text-align: center;
}

.tools-title {
  font-size: clamp(2.5rem, 6vw, 5rem);
  color: #fff;
  text-transform: uppercase;
  margin: 0;
}

.tools-underline {
  width: 96px;
  height: 8px;
  background: #DC2626;
  margin: 16px auto 0;
}

.tools-list {
  display: flex;
  flex-direction: column;
  border-top: 1px solid #262626;
}

.tool-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 16px;
  border-bottom: 1px solid #262626;
  cursor: pointer;
  transition: background 0.3s, color 0.3s;
}

.tool-row:hover {
  background: #DC2626;
  color: #000;
}

.tool-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.tool-index {
  font-size: 14px;
  opacity: 0.5;
  min-width: 24px;
}

.tool-row:hover .tool-index { opacity: 1; }

.tool-play {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid currentColor;
  background: transparent;
  color: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.tool-row:hover .tool-play { opacity: 1; }

.tool-info {
  display: flex;
  flex-direction: column;
}

.tool-name {
  font-size: clamp(1rem, 2.5vw, 1.8rem);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tool-desc {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 2px;
}

.tool-row:hover .tool-desc { opacity: 0.8; }

.tool-arrow {
  font-size: 14px;
}

.tool-row:hover .tool-arrow { font-weight: 700; }

@media (min-width: 768px) {
  .tools { padding: 96px 48px; }
}

/* ══════ TERMINAL ══════ */
.terminal-section {
  background: #0a0a0a;
  padding: 0 24px 48px;
}

.terminal-card {
  max-width: 896px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  background: rgba(13, 13, 13, 0.92);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.3s;
}

.terminal-card:hover {
  border-color: #DC2626;
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(220, 38, 38, 0.1);
}

.terminal-zeta {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: #DC2626;
  background: rgba(220, 38, 38, 0.08);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 3px;
  flex-shrink: 0;
}

.terminal-info { flex: 1; }
.terminal-title { font-size: 1rem; font-weight: 700; margin-bottom: 3px; }
.terminal-sub { font-size: 12px; color: #a3a3a3; line-height: 1.5; }

.terminal-cta {
  font-size: 14px;
  color: #DC2626;
  text-transform: uppercase;
  flex-shrink: 0;
  transition: transform 0.3s;
}

.terminal-card:hover .terminal-cta { transform: translateX(4px); }

@media (min-width: 768px) {
  .terminal-section { padding: 0 48px 48px; }
}

/* ══════ FOOTER ══════ */
.footer {
  background: #000;
  color: #fff;
  padding: 48px 24px;
  border-top: 1px solid #262626;
}

.footer-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.footer-title {
  font-size: clamp(4rem, 15vw, 10rem);
  line-height: 0.8;
  color: #DC2626;
  text-transform: uppercase;
  margin: 0;
}

.footer-subtitle {
  font-size: 20px;
  text-transform: uppercase;
  margin: 8px 0 0;
}

.footer-credits {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
}

.footer-col-head {
  color: #fff;
  margin: 0 0 16px;
  font-family: 'Space Mono', monospace;
  font-size: 12px;
  text-transform: uppercase;
}

.footer-credits p {
  margin: 4px 0;
  font-size: 12px;
  color: #737373;
  text-transform: uppercase;
}

.footer-bottom {
  margin-top: 96px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #404040;
  text-transform: uppercase;
}

@media (min-width: 768px) {
  .footer { padding: 48px; }
  .footer-inner { flex-direction: row; justify-content: space-between; align-items: flex-end; }
  .footer-title { font-size: clamp(4rem, 8vw, 8rem); }
}

/* ══════ RESPONSIVE ══════ */
@media (max-width: 768px) {
  .nav-links { display: none; }
  .hero-bottom { font-size: 14px; padding: 0 16px; bottom: 24px; }
  .hero-line { display: none; }
  .hide-mobile { display: none; }
  .tool-play { display: none; }
}
</style>
