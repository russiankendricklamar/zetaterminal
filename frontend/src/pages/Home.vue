<template>
  <div class="home-root">
    <!-- Marquee background -->
    <div class="marquee-bg">
      <div class="marquee-row" v-for="row in 3" :key="row">
        <div class="marquee-track" :class="'speed-' + row">
          <span v-for="(word, j) in marqueeWords[row - 1]" :key="j" class="marquee-word" :class="{ red: j % 2 === 1 }">{{ word }}</span>
          <span v-for="(word, j) in marqueeWords[row - 1]" :key="'d' + j" class="marquee-word" :class="{ red: j % 2 === 1 }">{{ word }}</span>
        </div>
      </div>
    </div>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-top-bar">
        <span class="brand">◆ QUANT ANALYTICS</span>
      </div>

      <div class="hero-main">
        <!-- Slider card -->
        <div class="slider-card">
          <div class="slider-border"></div>
          <div class="slider-viewport">
            <div
              v-for="(s, i) in slides"
              :key="i"
              class="s-slide"
              :class="{ active: current === i }"
            >
              <!-- Type A: bold text on red bg -->
              <div v-if="s.type === 'text'" class="slide-text-card" :style="{ background: s.bg }">
                <div class="slide-big-title">{{ s.bigTitle }}</div>
                <div class="slide-big-sub" v-if="s.bigSub">{{ s.bigSub }}</div>
              </div>
              <!-- Type B: info card -->
              <div v-else class="slide-info-card">
                <div class="slide-info-label">{{ s.label }}</div>
                <div class="slide-info-title">{{ s.title }}</div>
                <div class="slide-info-desc">{{ s.desc }}</div>
                <div class="slide-info-tags" v-if="s.tags">
                  <span v-for="t in s.tags" :key="t" class="slide-tag">{{ t }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="slider-pagination">
            <button
              v-for="(_, i) in slides"
              :key="i"
              class="s-dot"
              :class="{ active: current === i }"
              @click="goTo(i)"
            ></button>
          </div>
        </div>
      </div>

      <div class="hero-bottom-bar">
        <button class="scroll-cta" @click="scrollDown">
          <span>EXPLORE</span>
          <div class="scroll-bar"></div>
        </button>
      </div>
    </section>

    <!-- Tools -->
    <section class="tools-section" ref="toolsRef">
      <div class="tools-wrap">
        <div class="section-eyebrow">PLATFORM</div>
        <h2 class="section-heading">Инструменты</h2>

        <div class="cards-grid">
          <div
            v-for="tool in tools"
            :key="tool.path"
            class="g-card"
            :class="{
              'is-exploding': explosion === tool.path,
              'is-faded': explosion && explosion !== tool.path
            }"
            @click="explode(tool.path)"
          >
            <div class="g-card-accent" :class="tool.color"></div>
            <div class="g-card-body">
              <div class="g-card-title">{{ tool.name }}</div>
              <div class="g-card-desc">{{ tool.desc }}</div>
            </div>
            <div class="g-card-arrow">→</div>
          </div>
        </div>

        <!-- Terminal -->
        <router-link to="/terminal" class="terminal-row">
          <div class="terminal-zeta">ζ</div>
          <div class="terminal-info">
            <div class="terminal-title">Дзета-Терминал</div>
            <div class="terminal-sub">Потоковые данные в реальном времени</div>
          </div>
          <div class="terminal-go">→</div>
        </router-link>
      </div>
    </section>

    <div class="flash" :class="{ on: !!explosion }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const explosion = ref<string | null>(null)
const current = ref(0)
const toolsRef = ref<HTMLElement | null>(null)

const marqueeWords = [
  ['PORTFOLIO', 'OPTIONS', 'BONDS', 'SWAPS', 'GREEKS', 'FORWARDS'],
  ['HESTON', 'SABR', 'HMM', 'MONTE CARLO', 'VAR', 'DCF'],
  ['VOLATILITY', 'REGIME', 'STRESS TEST', 'PNL', 'HEDGING', 'YIELD'],
]

const slides = [
  { type: 'text', bg: '#e63946', bigTitle: 'QUANTITATIVE', bigSub: 'ANALYTICS' },
  { type: 'info', label: 'Портфель', title: 'Portfolio Analytics', desc: 'Доходность, VaR/ES, мониторинг позиций', tags: ['VaR', 'ES', 'Sharpe'] },
  { type: 'text', bg: '#1a1a1a', bigTitle: 'BLACK-SCHOLES', bigSub: '· HESTON · LÉVY' },
  { type: 'info', label: 'Опционы', title: 'Option Pricing', desc: 'БШМ, Хестон, Леви, FFT-ценообразование', tags: ['FFT', 'Greeks', 'IV'] },
  { type: 'text', bg: '#e63946', bigTitle: 'MARKET', bigSub: 'REGIMES' },
  { type: 'info', label: 'Облигации', title: 'Bond Valuation', desc: 'DCF, дюрация, convexity, спреды к кривой', tags: ['DCF', 'Duration', 'Z-spread'] },
  { type: 'text', bg: '#1a1a1a', bigTitle: 'SABR · SVI', bigSub: 'VOLATILITY SURFACE' },
  { type: 'info', label: 'Свопы', title: 'Swap Valuation', desc: 'IRS & FX свопы, NPV, DV01', tags: ['IRS', 'NPV', 'DV01'] },
]

const tools = [
  { name: 'Портфельный анализ', desc: 'Доходность, VaR/ES, мониторинг позиций, корреляции', color: 'red', path: '/portfolio' },
  { name: 'Риск-менеджмент', desc: 'Стресс-тесты, бэктестинг VaR, сценарный анализ', color: 'dark', path: '/stress' },
  { name: 'Рыночные режимы', desc: 'HMM, стационарное распределение, комплексный анализ', color: 'red', path: '/regimes' },
  { name: 'Стоимость облигаций', desc: 'DCF подход, спреды к кривой, дюрация, convexity', color: 'dark', path: '/bond-valuation' },
  { name: 'Стоимость опционов', desc: 'БШМ, Хестон, Леви, FFT-ценообразование', color: 'red', path: '/pricing/options' },
  { name: 'Волатильность', desc: 'Калибровка SABR/SVI, smile & term-structure', color: 'dark', path: '/analytics/volatility' },
  { name: 'Стоимость СВОПов', desc: 'IRS & FX свопы, NPV, DV01, чувствительность', color: 'red', path: 'valuation/swaps' },
  { name: 'Стоимость форвардов', desc: 'Справедливая стоимость, построение кривой', color: 'dark', path: 'valuation/forwards' },
  { name: 'Отчёты', desc: 'Bond Report, шаблонные отчеты и аналитика', color: 'red', path: '/vanila-bond-report' },
]

const goTo = (i: number) => { current.value = i }

const explode = (path: string) => {
  if (explosion.value) return
  explosion.value = path
  setTimeout(() => router.push(path), 600)
}

const scrollDown = () => {
  toolsRef.value?.scrollIntoView({ behavior: 'smooth' })
}

let timer: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  timer = setInterval(() => {
    current.value = (current.value + 1) % slides.length
  }, 3000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
/* ── ROOT ── */
.home-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #000;
  color: #fff;
  overflow-x: hidden;
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* ── MARQUEE ── */
.marquee-bg {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 0;
  opacity: 0.1;
  pointer-events: none;
}

.marquee-row {
  overflow: hidden;
  white-space: nowrap;
}

.marquee-track {
  display: inline-flex;
  will-change: transform;
}

.speed-1 { animation: mq 22s linear infinite; }
.speed-2 { animation: mq 30s linear infinite reverse; }
.speed-3 { animation: mq 18s linear infinite; }

.marquee-word {
  font-size: clamp(5rem, 13vw, 11rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.05em;
  line-height: 1;
  padding: 0 0.2em;
  flex-shrink: 0;
  user-select: none;
  color: #fff;
}

.marquee-word.red { color: #e63946; }

@keyframes mq {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* ── HERO ── */
.hero {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.hero-top-bar {
  padding: 28px 32px;
}

.brand {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: rgba(255,255,255,0.35);
}

.hero-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 2rem;
}

/* ── SLIDER CARD ── */
.slider-card {
  position: relative;
  width: 520px;
  max-width: 92vw;
}

.slider-border {
  position: absolute;
  inset: -3px;
  border: 2px solid #e63946;
  border-radius: 4px;
  pointer-events: none;
  z-index: 3;
}

.slider-viewport {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  border-radius: 2px;
  background: #111;
}

/* slides */
.s-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.9s ease;
  pointer-events: none;
}
.s-slide.active {
  opacity: 1;
  pointer-events: auto;
}

/* type A: bold text */
.slide-text-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.slide-big-title {
  font-size: clamp(2.2rem, 6vw, 4rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  text-align: center;
  text-transform: uppercase;
}

.slide-big-sub {
  font-size: clamp(1.4rem, 3.5vw, 2.2rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  text-align: center;
  margin-top: 8px;
  opacity: 0.85;
}

/* type B: info */
.slide-info-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2.5rem 3rem;
  background: #0a0a0a;
}

.slide-info-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #e63946;
  margin-bottom: 12px;
}

.slide-info-title {
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 12px;
}

.slide-info-desc {
  font-size: 0.95rem;
  color: rgba(255,255,255,0.5);
  line-height: 1.6;
  margin-bottom: 16px;
}

.slide-info-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.slide-tag {
  padding: 4px 12px;
  border: 1px solid rgba(230,57,70,0.4);
  border-radius: 2px;
  font-size: 11px;
  font-weight: 600;
  color: #e63946;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* pagination */
.slider-pagination {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 14px;
}

.s-dot {
  width: 28px;
  height: 3px;
  background: rgba(255,255,255,0.15);
  border: none;
  border-radius: 1px;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
}
.s-dot.active {
  background: #e63946;
  width: 44px;
}

/* ── SCROLL CTA ── */
.hero-bottom-bar {
  display: flex;
  justify-content: center;
  padding: 24px 0 32px;
}

.scroll-cta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  color: rgba(255,255,255,0.3);
  font-family: inherit;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.2em;
  transition: color 0.3s;
}
.scroll-cta:hover { color: #e63946; }

.scroll-bar {
  width: 1px;
  height: 32px;
  background: currentColor;
  animation: pulse-bar 2s ease-in-out infinite;
}

@keyframes pulse-bar {
  0%,100% { opacity: 0.2; transform: scaleY(0.5); }
  50% { opacity: 1; transform: scaleY(1); }
}

/* ── TOOLS SECTION ── */
.tools-section {
  position: relative;
  z-index: 1;
  padding: 80px 2rem 100px;
  background: #000;
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
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  margin: 0 0 40px 0;
}

/* ── GRID CARDS ── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}

.g-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  background: #0d0d0d;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.g-card:hover {
  background: #141414;
  border-color: #e63946;
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(230, 57, 70, 0.12);
}

.g-card-accent {
  width: 4px;
  align-self: stretch;
  border-radius: 2px;
  flex-shrink: 0;
}

.g-card-accent.red { background: #e63946; }
.g-card-accent.dark { background: rgba(255,255,255,0.12); }

.g-card-body {
  flex: 1;
  min-width: 0;
}

.g-card-title {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.g-card-desc {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.4);
  line-height: 1.5;
}

.g-card-arrow {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.15);
  flex-shrink: 0;
  transition: all 0.3s;
}

.g-card:hover .g-card-arrow {
  color: #e63946;
  transform: translateX(4px);
}

/* ── TERMINAL ── */
.terminal-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding: 20px 24px;
  background: #0d0d0d;
  border: 1px solid rgba(230,57,70,0.2);
  border-radius: 3px;
  text-decoration: none;
  color: inherit;
  transition: all 0.35s;
}

.terminal-row:hover {
  border-color: #e63946;
  background: #141414;
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(230,57,70,0.1);
}

.terminal-zeta {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
  color: #e63946;
  background: rgba(230,57,70,0.08);
  border: 1px solid rgba(230,57,70,0.2);
  border-radius: 3px;
  flex-shrink: 0;
}

.terminal-info { flex: 1; }

.terminal-title {
  font-size: 0.95rem;
  font-weight: 700;
}

.terminal-sub {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.4);
  margin-top: 2px;
}

.terminal-go {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.15);
  transition: all 0.3s;
}

.terminal-row:hover .terminal-go {
  color: #e63946;
  transform: translateX(4px);
}

/* ── EXPLOSIONS ── */
.g-card.is-exploding {
  z-index: 9999;
  border-color: #fff;
  animation: shock 0.6s ease;
}

.g-card.is-exploding::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 24px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  transform: translate(-50%, -50%);
  animation: bang 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes bang {
  0% { transform: translate(-50%,-50%) scale(1); box-shadow: 0 0 10px #fff; }
  100% { transform: translate(-50%,-50%) scale(250); box-shadow: 0 0 600px 300px #fff; opacity: 1; }
}

@keyframes shock {
  0% { transform: scale(1); }
  30% { transform: scale(0.98); }
  100% { transform: scale(1.01); }
}

.g-card.is-faded {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.96);
  filter: blur(3px);
  transition: all 0.5s;
}

.flash {
  position: fixed;
  inset: 0;
  background: #fff;
  z-index: 9998;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s;
}
.flash.on {
  transition-delay: 0.4s;
  opacity: 1;
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .slider-card { width: 100%; }
  .marquee-word { font-size: clamp(3rem, 16vw, 6rem); }
  .tools-section { padding: 48px 1rem 60px; }
  .cards-grid { grid-template-columns: 1fr; }
  .slide-big-title { font-size: 2rem; }
  .slide-big-sub { font-size: 1.2rem; }
  .slide-info-card { padding: 2rem; }
}

@media (max-width: 480px) {
  .hero-top-bar { padding: 16px; }
  .g-card { padding: 14px 16px; }
  .g-card-title { font-size: 0.88rem; }
  .g-card-desc { font-size: 0.72rem; }
  .g-card-arrow { display: none; }
}
</style>
