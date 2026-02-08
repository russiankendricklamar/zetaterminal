<template>
  <div class="home-root">
    <!-- Kinetic marquee background (fixed) -->
    <div class="kinetic-bg">
      <div
        v-for="(row, ri) in marqueeRows"
        :key="ri"
        class="marquee-row"
        :ref="el => setRowRef(el as HTMLElement | null, ri)"
      >
        <div class="marquee-track">
          <span
            v-for="(word, wi) in row.words"
            :key="'a' + wi"
            class="marquee-word"
            :class="{ red: wi % 2 === 1 }"
          >{{ word }}</span>
          <span
            v-for="(word, wi) in row.words"
            :key="'b' + wi"
            class="marquee-word"
            :class="{ red: wi % 2 === 1 }"
          >{{ word }}</span>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="content-layer" ref="contentRef">
      <!-- Hero -->
      <section class="hero">
        <div class="brand">&#9670; QUANT ANALYTICS</div>
        <h1 class="hero-headline">QUANTITATIVE</h1>
        <p class="hero-subline">ANALYTICS</p>
        <p class="hero-desc">&#1055;&#1083;&#1072;&#1090;&#1092;&#1086;&#1088;&#1084;&#1072; &#1082;&#1086;&#1083;&#1080;&#1095;&#1077;&#1089;&#1090;&#1074;&#1077;&#1085;&#1085;&#1086;&#1075;&#1086; &#1072;&#1085;&#1072;&#1083;&#1080;&#1079;&#1072; &#1076;&#1083;&#1103; &#1092;&#1080;&#1085;&#1072;&#1085;&#1089;&#1086;&#1074;&#1099;&#1093; &#1088;&#1099;&#1085;&#1082;&#1086;&#1074;</p>
        <div class="hero-scroll-hint">
          <span>SCROLL</span>
          <div class="scroll-line"></div>
        </div>
      </section>

      <!-- Tools -->
      <section class="tools-section">
        <div class="tools-wrap">
          <div class="section-eyebrow">PLATFORM</div>
          <h2 class="section-heading">&#1048;&#1085;&#1089;&#1090;&#1088;&#1091;&#1084;&#1077;&#1085;&#1090;&#1099;</h2>

          <div class="tools-grid">
            <div
              v-for="tool in tools"
              :key="tool.path"
              class="g-card"
              :class="{
                'is-active': activeTool === tool.path,
                'is-faded': activeTool && activeTool !== tool.path
              }"
              @click="navigateTo(tool.path, $event)"
            >
              <div class="g-card-accent" :class="tool.color"></div>
              <div class="g-card-body">
                <div class="g-card-title">{{ tool.name }}</div>
                <div class="g-card-desc">{{ tool.desc }}</div>
              </div>
              <div class="g-card-arrow">&rarr;</div>
              <div class="g-ripple" ref="rippleRefs"></div>
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
            <div class="terminal-title">&#1044;&#1079;&#1077;&#1090;&#1072;-&#1058;&#1077;&#1088;&#1084;&#1080;&#1085;&#1072;&#1083;</div>
            <div class="terminal-sub">&#1055;&#1086;&#1090;&#1086;&#1082;&#1086;&#1074;&#1099;&#1077; &#1076;&#1072;&#1085;&#1085;&#1099;&#1077; &#1074; &#1088;&#1077;&#1072;&#1083;&#1100;&#1085;&#1086;&#1084; &#1074;&#1088;&#1077;&#1084;&#1077;&#1085;&#1080; &middot; &#1040;&#1082;&#1094;&#1080;&#1080; &middot; &#1050;&#1088;&#1080;&#1087;&#1090;&#1086; &middot; &#1060;&#1100;&#1102;&#1095;&#1077;&#1088;&#1089;&#1099; &middot; &#1054;&#1087;&#1094;&#1080;&#1086;&#1085;&#1099;</div>
          </div>
          <div class="terminal-cta">&#1054;&#1090;&#1082;&#1088;&#1099;&#1090;&#1100; &rarr;</div>
        </div>
      </section>

      <!-- Footer spacer -->
      <div class="footer-spacer"></div>
    </div>

    <!-- Transition overlay -->
    <div class="transition-overlay" :class="{ active: !!activeTool }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { useKineticMarquee } from '@/composables/useKineticMarquee'

const router = useRouter()
const activeTool = ref<string | null>(null)
const contentRef = ref<HTMLElement | null>(null)

const marqueeRows = [
  { words: ['BLACK-SCHOLES', 'HESTON', 'LÉVY', 'MONTE CARLO', 'SABR', 'DCF'], direction: 1, speed: 1.0 },
  { words: ['VOLATILITY', 'HMM', 'GREEKS', 'SHARPE', 'VAR', 'VITERBI', 'SVI'], direction: -1, speed: 1.4 },
  { words: ['PORTFOLIO', 'OPTIONS', 'FUTURES', 'SWAPS', 'FORWARDS', 'BONDS'], direction: 1, speed: 0.8 },
  { words: ['LIQUIDITY', 'CORRELATION', 'REGIME', 'STRESS TEST', 'ORDER BOOK', 'DURATION'], direction: -1, speed: 1.2 },
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
  { name: 'Монте-Карло', desc: 'Симуляции, стохастические модели, генерация путей', color: 'dark', path: '/monte-carlo' },
  { name: 'Кривая бескупонной доходности', desc: 'ZCYC, zero-coupon yield curve', color: 'red', path: '/zcyc-viewer' },
  { name: 'P&L Attribution', desc: 'Факторная декомпозиция P&L, атрибуция доходности', color: 'dark', path: '/analytics/pnl' },
]

// Marquee refs
const rowRefs = ref<(HTMLElement | null)[]>([])
const setRowRef = (el: HTMLElement | null, i: number) => {
  rowRefs.value[i] = el
}

const { init: initMarquee, boostAll } = useKineticMarquee()

// Navigation with ripple + fade transition
function navigateTo(path: string, e: MouseEvent) {
  if (activeTool.value) return
  activeTool.value = path

  // Ripple from click point on the card
  const card = (e.currentTarget as HTMLElement)
  const rect = card.getBoundingClientRect()
  const ripple = card.querySelector('.g-ripple') as HTMLElement
  if (ripple) {
    ripple.style.left = `${e.clientX - rect.left}px`
    ripple.style.top = `${e.clientY - rect.top}px`
    ripple.classList.add('active')
  }

  // Card scale up
  gsap.to(card, { scale: 1.03, duration: 0.3, ease: 'power2.out' })

  // Boost marquee
  boostAll(4, 0.3)

  // Fade out content
  if (contentRef.value) {
    gsap.to(contentRef.value, {
      opacity: 0,
      scale: 0.98,
      duration: 0.4,
      delay: 0.15,
      ease: 'power2.in',
    })
  }

  setTimeout(() => router.push(path), 550)
}

// Lifecycle
onMounted(async () => {
  await nextTick()

  const configs = rowRefs.value
    .filter((el): el is HTMLElement => el !== null)
    .map((el, i) => ({
      el,
      direction: (marqueeRows[i].direction === 1 ? 1 : -1) as 1 | -1,
      speedMultiplier: marqueeRows[i].speed,
    }))

  initMarquee(configs)

  // Entrance animation
  if (contentRef.value) {
    gsap.fromTo(
      contentRef.value,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.8, delay: 0.2, ease: 'power2.out' }
    )
  }
})
</script>

<style scoped>
/* ── ROOT ── */
.home-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #000;
  color: #fff;
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* ── KINETIC MARQUEE BG ── */
.kinetic-bg {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  z-index: 0;
  pointer-events: none;
  opacity: 0.07;
  overflow: hidden;
  gap: 4px;
}

.marquee-row {
  overflow: hidden;
  white-space: nowrap;
}

.marquee-track {
  display: inline-flex;
  will-change: transform;
}

.marquee-word {
  font-size: clamp(5rem, 14vw, 12rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.05em;
  line-height: 1;
  padding: 0 0.15em;
  flex-shrink: 0;
  user-select: none;
  color: #fff;
}

.marquee-word.red {
  color: #e63946;
}

/* ── CONTENT LAYER ── */
.content-layer {
  position: relative;
  z-index: 1;
}

/* ── HERO ── */
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: 0 2rem;
  text-align: center;
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

/* ── TOOLS SECTION ── */
.tools-section {
  padding: 40px 2rem 60px;
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

/* ── CARD ── */
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

/* ── RIPPLE ── */
.g-ripple {
  position: absolute;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(10, 10, 10, 0.8);
  transform: translate(-50%, -50%);
  pointer-events: none;
  opacity: 0;
}

.g-ripple.active {
  animation: ripple-expand 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes ripple-expand {
  0% { width: 0; height: 0; opacity: 0.6; }
  100% { width: 600px; height: 600px; opacity: 0; }
}

/* ── TERMINAL ── */
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

/* ── TRANSITION OVERLAY ── */
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
  transition-delay: 0.15s;
}

/* ── FOOTER SPACER ── */
.footer-spacer {
  height: 60px;
}

/* ── RESPONSIVE ── */
@media (max-width: 1024px) {
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .marquee-word {
    font-size: clamp(3rem, 14vw, 6rem);
  }

  .tools-section {
    padding: 32px 1rem 48px;
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
}

@media (max-width: 480px) {
  .marquee-word {
    font-size: clamp(2.5rem, 16vw, 4rem);
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
