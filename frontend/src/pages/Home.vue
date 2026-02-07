<template>
  <div class="home-root">
    <!-- Marquee text background -->
    <div class="marquee-container">
      <div class="marquee-row">
        <div class="marquee-track">
          <span class="marquee-text">PORTFOLIO</span>
          <span class="marquee-text accent">OPTIONS</span>
          <span class="marquee-text">BONDS</span>
          <span class="marquee-text accent">SWAPS</span>
          <span class="marquee-text">GREEKS</span>
          <span class="marquee-text accent">FORWARDS</span>
          <span class="marquee-text">PORTFOLIO</span>
          <span class="marquee-text accent">OPTIONS</span>
          <span class="marquee-text">BONDS</span>
          <span class="marquee-text accent">SWAPS</span>
          <span class="marquee-text">GREEKS</span>
          <span class="marquee-text accent">FORWARDS</span>
        </div>
      </div>
      <div class="marquee-row">
        <div class="marquee-track">
          <span class="marquee-text accent">HESTON</span>
          <span class="marquee-text">SABR</span>
          <span class="marquee-text accent">HMM</span>
          <span class="marquee-text">MONTE CARLO</span>
          <span class="marquee-text accent">VAR</span>
          <span class="marquee-text">DCF</span>
          <span class="marquee-text accent">HESTON</span>
          <span class="marquee-text">SABR</span>
          <span class="marquee-text accent">HMM</span>
          <span class="marquee-text">MONTE CARLO</span>
          <span class="marquee-text accent">VAR</span>
          <span class="marquee-text">DCF</span>
        </div>
      </div>
      <div class="marquee-row">
        <div class="marquee-track">
          <span class="marquee-text">VOLATILITY</span>
          <span class="marquee-text accent">REGIME</span>
          <span class="marquee-text">STRESS TEST</span>
          <span class="marquee-text accent">PNL</span>
          <span class="marquee-text">HEDGING</span>
          <span class="marquee-text accent">YIELD CURVE</span>
          <span class="marquee-text">VOLATILITY</span>
          <span class="marquee-text accent">REGIME</span>
          <span class="marquee-text">STRESS TEST</span>
          <span class="marquee-text accent">PNL</span>
          <span class="marquee-text">HEDGING</span>
          <span class="marquee-text accent">YIELD CURVE</span>
        </div>
      </div>
    </div>

    <!-- Hero content -->
    <div class="hero-overlay">
      <!-- Top bar -->
      <div class="hero-top">
        <div class="hero-logo">
          <span class="logo-diamond">◆</span>
          Quantitative Analytics
        </div>
      </div>

      <!-- Center: slider + title -->
      <div class="hero-center">
        <div class="hero-text">
          <h1 class="hero-title">
            Комплексный<br>
            <span class="gradient-text">калькулятор</span><br>
            деривативов
          </h1>
          <p class="hero-subtitle">
            Портфельный анализ, скрытые марковские цепи, справедливая стоимость и риск-менеджмент
          </p>
        </div>

        <div class="slider-wrap">
          <div class="slider-inner" ref="sliderRef">
            <div
              v-for="(slide, i) in slides"
              :key="i"
              class="slide"
              :class="{ active: currentSlide === i }"
            >
              <div class="slide-icon" :class="slide.color">
                <div class="slide-glow" :class="slide.color"></div>
              </div>
              <div class="slide-content">
                <span class="slide-label">{{ slide.label }}</span>
                <h2 class="slide-title">{{ slide.title }}</h2>
                <p class="slide-desc">{{ slide.desc }}</p>
              </div>
            </div>
          </div>
          <!-- Pagination dots -->
          <div class="slider-dots">
            <button
              v-for="(_, i) in slides"
              :key="i"
              class="dot"
              :class="{ active: currentSlide === i }"
              @click="currentSlide = i"
            ></button>
          </div>
        </div>
      </div>

      <!-- Scroll hint -->
      <div class="hero-bottom">
        <button class="scroll-hint" @click="scrollToTools">
          <span>Инструменты</span>
          <div class="scroll-line"></div>
        </button>
      </div>
    </div>

    <!-- Tools section -->
    <div class="tools-section" ref="toolsSectionRef">
      <div class="tools-container">
        <div class="tools-header">
          <span class="tools-label">Платформа</span>
          <h2 class="tools-title">Инструменты</h2>
        </div>

        <div class="tools-grid">
          <div
            v-for="tool in tools"
            :key="tool.path"
            class="tool-card"
            :class="{
              'is-exploding': activeExplosion === tool.path,
              'is-faded': isFaded(tool.path)
            }"
            @click="triggerExplosion(tool.path)"
          >
            <div class="tool-icon" :class="tool.color">
              <div class="supernova" :class="tool.color"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">{{ tool.name }}</div>
              <div class="tool-desc">{{ tool.desc }}</div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Terminal link -->
        <router-link to="/terminal" class="terminal-card">
          <div class="terminal-icon">
            <span class="zeta">ζ</span>
          </div>
          <div class="terminal-body">
            <div class="terminal-name">Дзета-Терминал</div>
            <div class="terminal-desc">Потоковые данные в реальном времени</div>
          </div>
          <div class="terminal-arrow">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Flash overlay for explosion -->
    <div class="flash-overlay" :class="{ active: !!activeExplosion }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeExplosion = ref<string | null>(null)
const currentSlide = ref(0)
const toolsSectionRef = ref<HTMLElement | null>(null)

const slides = [
  { label: 'Портфель', title: 'Portfolio Analytics', desc: 'Доходность, VaR/ES, мониторинг позиций', color: 'purple' },
  { label: 'Опционы', title: 'Option Pricing', desc: 'БШМ, Хестон, Леви, FFT-ценообразование', color: 'green' },
  { label: 'Режимы', title: 'Market Regimes', desc: 'HMM, стационарное распределение', color: 'blue' },
  { label: 'Облигации', title: 'Bond Valuation', desc: 'DCF, дюрация, convexity, спреды', color: 'green' },
  { label: 'Волатильность', title: 'Volatility Surface', desc: 'SABR/SVI калибровка, smile & term-structure', color: 'blue' },
  { label: 'Свопы', title: 'Swap Valuation', desc: 'IRS & FX свопы, NPV, DV01', color: 'green' },
]

const tools = [
  { name: 'Портфельный анализ', desc: 'Доходность, VaR/ES, мониторинг позиций, корреляции активов', color: 'purple', path: '/portfolio' },
  { name: 'Риск-менеджмент', desc: 'Стресс-тесты, бэктестинг VaR, сценарный анализ портфеля', color: 'purple', path: '/stress' },
  { name: 'Анализ рыночных режимов', desc: 'Рыночные режимы, комплексный анализ, стационарное распределение', color: 'blue', path: '/regimes' },
  { name: 'Справедливая стоимость облигаций', desc: 'DCF подход, спреды к кривой, дюрация, выпуклость', color: 'green', path: '/bond-valuation' },
  { name: 'Справедливая стоимость опционов', desc: 'БШМ, модель Хестона, процессы Леви, FFT-ценообразование', color: 'green', path: '/pricing/options' },
  { name: 'Поверхность волатильности', desc: 'Калибровка SABR/SVI, smile & term-structure, arbitrage-free', color: 'blue', path: '/analytics/volatility' },
  { name: 'Справедливая стоимость СВОПов', desc: 'IRS & FX свопы, NPV, DV01, чувствительность к кривой', color: 'green', path: 'valuation/swaps' },
  { name: 'Справедливая стоимость форвардов', desc: 'Оценка справедливой стоимости, построение кривой, арбитраж', color: 'green', path: 'valuation/forwards' },
  { name: 'Отчёты по облигациям', desc: 'Vanila Bond Report, шаблонные отчеты и аналитика', color: 'nova', path: '/vanila-bond-report' },
]

const isFaded = (path: string) => {
  return activeExplosion.value !== null && activeExplosion.value !== path
}

const triggerExplosion = (path: string) => {
  if (activeExplosion.value) return
  activeExplosion.value = path
  setTimeout(() => {
    router.push(path)
  }, 600)
}

const scrollToTools = () => {
  toolsSectionRef.value?.scrollIntoView({ behavior: 'smooth' })
}

// Auto-advance slides
let slideInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  slideInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % slides.length
  }, 3500)
})

onUnmounted(() => {
  if (slideInterval) clearInterval(slideInterval)
})
</script>

<style scoped>
/* ============================================
   ROOT & VARIABLES
   ============================================ */
.home-root {
  position: relative;
  width: 100%;
  min-height: 100vh;
  background: #050510;
  color: #f9fafb;
  overflow-x: hidden;
}

/* ============================================
   MARQUEE BACKGROUND
   ============================================ */
.marquee-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0;
  z-index: 0;
  opacity: 0.07;
  pointer-events: none;
}

.marquee-row {
  display: flex;
  white-space: nowrap;
  overflow: hidden;
  width: 100%;
}

.marquee-track {
  display: flex;
  animation: marquee-scroll 28s linear infinite;
  will-change: transform;
}

.marquee-row:nth-child(even) .marquee-track {
  animation-direction: reverse;
  animation-duration: 35s;
}

.marquee-row:nth-child(3) .marquee-track {
  animation-duration: 22s;
}

.marquee-text {
  font-size: clamp(4.5rem, 11vw, 9rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.04em;
  color: #fff;
  padding: 0 0.25em;
  line-height: 1.05;
  flex-shrink: 0;
  user-select: none;
}

.marquee-text.accent {
  color: #e63946;
}

@keyframes marquee-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* ============================================
   HERO OVERLAY
   ============================================ */
.hero-overlay {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 2rem;
}

.hero-top {
  flex-shrink: 0;
}

.hero-logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.4);
}

.logo-diamond {
  color: #22d3ee;
  font-size: 1rem;
}

/* ============================================
   HERO CENTER
   ============================================ */
.hero-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60px;
  max-width: 1300px;
  margin: 0 auto;
  width: 100%;
  padding: 2rem 0;
}

.hero-text {
  max-width: 480px;
  flex-shrink: 0;
}

.hero-title {
  font-size: clamp(2rem, 4.5vw, 3.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin: 0 0 1.2rem 0;
}

.gradient-text {
  background: linear-gradient(135deg, #a5b4fc, #22d3ee, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.7;
  margin: 0;
}

/* ============================================
   SLIDE CAROUSEL
   ============================================ */
.slider-wrap {
  width: 420px;
  flex-shrink: 0;
}

.slider-inner {
  position: relative;
  height: 320px;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(24px);
  border: 1.5px solid rgba(34, 211, 238, 0.2);
  box-shadow:
    0 0 60px rgba(34, 211, 238, 0.1),
    0 30px 80px rgba(0, 0, 0, 0.5);
}

.slide {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 2.5rem;
  opacity: 0;
  transform: scale(0.95);
  transition: opacity 0.8s ease, transform 0.8s ease;
  pointer-events: none;
}

.slide.active {
  opacity: 1;
  transform: scale(1);
  pointer-events: auto;
}

.slide-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.slide-icon.blue { background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); }
.slide-icon.purple { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); }
.slide-icon.green { background: rgba(34, 197, 94, 0.15); border: 1px solid rgba(34, 197, 94, 0.3); }

.slide-glow {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  animation: glow-pulse 2.5s ease-in-out infinite;
}

.slide-glow.blue { box-shadow: 0 0 20px 6px rgba(56, 189, 248, 0.6); }
.slide-glow.purple { box-shadow: 0 0 20px 6px rgba(168, 85, 247, 0.6); }
.slide-glow.green { box-shadow: 0 0 20px 6px rgba(34, 197, 94, 0.6); }

@keyframes glow-pulse {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.15); }
}

.slide-content {
  text-align: center;
}

.slide-label {
  display: inline-block;
  padding: 0.25rem 0.7rem;
  background: rgba(230, 57, 70, 0.9);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-radius: 6px;
  margin-bottom: 0.8rem;
}

.slide-title {
  font-size: 1.6rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 0.5rem 0;
}

.slide-desc {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

.slider-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 16px;
}

.dot {
  width: 24px;
  height: 3px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.dot.active {
  background: #e63946;
  width: 36px;
}

/* ============================================
   SCROLL HINT
   ============================================ */
.hero-bottom {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  padding-bottom: 1rem;
}

.scroll-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.35);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.3s ease;
  font-family: inherit;
}

.scroll-hint:hover {
  color: #22d3ee;
}

.scroll-line {
  width: 1px;
  height: 36px;
  background: rgba(255, 255, 255, 0.3);
  animation: scroll-pulse 2s ease-in-out infinite;
}

@keyframes scroll-pulse {
  0%, 100% { opacity: 0.2; transform: scaleY(0.5); }
  50% { opacity: 1; transform: scaleY(1); }
}

/* ============================================
   TOOLS SECTION
   ============================================ */
.tools-section {
  position: relative;
  z-index: 1;
  padding: 5rem 2rem 6rem;
  background: linear-gradient(180deg, transparent 0%, rgba(5, 5, 16, 0.95) 10%);
}

.tools-container {
  max-width: 900px;
  margin: 0 auto;
}

.tools-header {
  margin-bottom: 2.5rem;
}

.tools-label {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #e63946;
  margin-bottom: 0.6rem;
}

.tools-title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
}

.tools-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

/* ============================================
   TOOL CARDS
   ============================================ */
.tool-card {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(148, 163, 184, 0.12);
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, border-color, background;
}

.tool-card:hover {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.85);
  transform: translateX(6px);
}

.tool-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.3s ease;
}

.tool-icon.blue { background: rgba(56, 189, 248, 0.1); }
.tool-icon.purple { background: rgba(168, 85, 247, 0.1); }
.tool-icon.green { background: rgba(34, 197, 94, 0.1); }
.tool-icon.nova { background: rgba(255, 51, 102, 0.1); }

.supernova {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  position: relative;
  z-index: 2;
  animation: star-pulse 3s infinite ease-in-out;
  will-change: transform, box-shadow;
}

.supernova.blue { box-shadow: 0 0 10px 2px rgba(59, 130, 246, 0.5); }
.supernova.purple { box-shadow: 0 0 10px 2px rgba(168, 85, 247, 0.5); }
.supernova.green { box-shadow: 0 0 10px 2px rgba(34, 197, 94, 0.5); }
.supernova.nova { box-shadow: 0 0 10px 2px rgba(255, 51, 102, 0.5); }

.tool-card:hover .supernova {
  transform: scale(1.3);
}

.tool-card:hover .supernova.blue { box-shadow: 0 0 18px 6px #60a5fa, 0 0 36px 12px rgba(59, 130, 246, 0.3); }
.tool-card:hover .supernova.purple { box-shadow: 0 0 18px 6px #c084fc, 0 0 36px 12px rgba(168, 85, 247, 0.3); }
.tool-card:hover .supernova.green { box-shadow: 0 0 18px 6px #4ade80, 0 0 36px 12px rgba(34, 197, 94, 0.3); }
.tool-card:hover .supernova.nova { box-shadow: 0 0 18px 6px #ff3366, 0 0 36px 12px rgba(255, 51, 102, 0.3); }

@keyframes star-pulse {
  0%, 100% { opacity: 0.85; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

.tool-body {
  flex: 1;
  min-width: 0;
}

.tool-name {
  font-size: 0.85rem;
  font-weight: 650;
  color: #fff;
  line-height: 1.3;
}

.tool-desc {
  font-size: 0.75rem;
  color: rgba(148, 163, 184, 0.75);
  line-height: 1.4;
  margin-top: 2px;
}

.tool-arrow {
  color: rgba(148, 163, 184, 0.3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.tool-card:hover .tool-arrow {
  color: rgba(148, 163, 184, 0.7);
  transform: translateX(3px);
}

/* ============================================
   TERMINAL CARD
   ============================================ */
.terminal-card {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 18px 20px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(20px);
  border: 1.5px solid rgba(34, 211, 238, 0.2);
  text-decoration: none;
  color: inherit;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 30px rgba(34, 211, 238, 0.08);
  margin-top: 16px;
}

.terminal-card:hover {
  border-color: rgba(34, 211, 238, 0.45);
  background: rgba(15, 23, 42, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 0 50px rgba(34, 211, 238, 0.15);
}

.terminal-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.25);
  border-radius: 12px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.terminal-card:hover .terminal-icon {
  background: rgba(34, 211, 238, 0.18);
  border-color: rgba(34, 211, 238, 0.4);
}

.zeta {
  font-size: 1.6rem;
  font-weight: 700;
  color: #22d3ee;
  line-height: 1;
}

.terminal-body { flex: 1; }

.terminal-name {
  font-size: 0.95rem;
  font-weight: 700;
}

.terminal-desc {
  font-size: 0.78rem;
  color: rgba(148, 163, 184, 0.7);
  margin-top: 2px;
}

.terminal-arrow {
  color: rgba(148, 163, 184, 0.3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.terminal-card:hover .terminal-arrow {
  color: #22d3ee;
  transform: translateX(4px);
}

/* ============================================
   EXPLOSION ANIMATIONS
   ============================================ */
.tool-card.is-exploding {
  z-index: 9999;
  border-color: rgba(255, 255, 255, 0.8);
  background: rgba(15, 23, 42, 1);
  animation: shockwave 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.tool-card.is-exploding .tool-icon {
  overflow: visible !important;
  background: transparent !important;
  border-color: transparent !important;
}

.tool-card.is-exploding .supernova {
  animation: big-bang 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
}

@keyframes big-bang {
  0% { transform: scale(1); opacity: 1; background: #fff; box-shadow: 0 0 12px 2px rgba(255, 255, 255, 0.8); }
  30% { transform: scale(5); opacity: 1; box-shadow: 0 0 60px 30px rgba(255, 255, 255, 0.9); }
  60% { transform: scale(30); opacity: 0.95; box-shadow: 0 0 200px 100px rgba(255, 255, 255, 0.9); }
  100% { transform: scale(200); opacity: 1; background: #fff; box-shadow: 0 0 1000px 500px rgba(255, 255, 255, 1); }
}

@keyframes shockwave {
  0% { transform: scale(1); }
  30% { transform: scale(0.98); }
  60% { transform: scale(1.01); }
  100% { transform: scale(1.02); }
}

.tool-card.is-faded {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.95);
  filter: blur(3px);
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.flash-overlay {
  position: fixed;
  inset: 0;
  background: #fff;
  z-index: 9998;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.flash-overlay.active {
  transition-delay: 0.4s;
  opacity: 1;
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1024px) {
  .hero-center {
    flex-direction: column;
    gap: 40px;
    text-align: center;
  }

  .hero-text {
    max-width: 600px;
  }

  .slider-wrap {
    width: 100%;
    max-width: 420px;
  }
}

@media (max-width: 768px) {
  .hero-overlay {
    padding: 1.5rem;
  }

  .marquee-text {
    font-size: clamp(3rem, 14vw, 5.5rem);
  }

  .slider-wrap {
    max-width: 360px;
  }

  .slider-inner {
    height: 280px;
  }

  .tools-section {
    padding: 3rem 1.2rem 4rem;
  }

  .tool-card {
    padding: 12px;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 1.7rem;
  }

  .slider-wrap {
    max-width: 300px;
  }

  .slider-inner {
    height: 260px;
  }

  .slide-title {
    font-size: 1.3rem;
  }

  .tool-name {
    font-size: 0.78rem;
  }

  .tool-desc {
    font-size: 0.68rem;
  }

  .tool-arrow {
    display: none;
  }
}
</style>
