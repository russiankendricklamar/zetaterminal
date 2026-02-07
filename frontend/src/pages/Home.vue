<template>
  <div class="home-root">
    <!-- Brand (fixed) -->
    <div class="fixed-brand">
      <span class="brand-text">&#9670; QUANT ANALYTICS</span>
    </div>

    <!-- Pagination (fixed) -->
    <nav class="slide-pagination" :class="{ horizontal: isMobile }">
      <button
        v-for="(slide, i) in slides"
        :key="slide.id"
        class="slide-dot"
        :class="{ active: currentSlide === i }"
        @click="goToSlide(i)"
      ></button>
    </nav>

    <!-- Slides -->
    <div class="slides-container">
      <section
        v-for="(slide, i) in slides"
        :key="slide.id"
        :ref="el => setSectionRef(el as HTMLElement | null, i)"
        class="fp-slide"
        :style="{ background: slide.bgColor }"
      >
        <!-- Background text -->
        <div class="slide-bg-text">
          <span
            v-for="(word, wi) in slide.bgText"
            :key="wi"
            class="slide-bg-word"
            :style="{ color: slide.bgTextColor }"
          >{{ word }}</span>
        </div>

        <!-- Content: hero -->
        <div v-if="slide.type === 'hero'" class="slide-content" :ref="el => setContentRef(el as HTMLElement | null, i)">
          <div class="hero-content">
            <h1 class="hero-headline">{{ slide.headline }}</h1>
            <p class="hero-subline">{{ slide.subline }}</p>
            <p class="hero-desc">{{ slide.description }}</p>
          </div>
        </div>

        <!-- Content: theme -->
        <div v-if="slide.type === 'theme'" class="slide-content" :ref="el => setContentRef(el as HTMLElement | null, i)">
          <div class="theme-content">
            <span class="theme-label">{{ slide.label }}</span>
            <h2 class="theme-headline">{{ slide.headline }}</h2>
            <p class="theme-subline">{{ slide.subline }}</p>
            <p class="theme-desc">{{ slide.description }}</p>
            <div class="theme-tags" v-if="slide.tags">
              <span v-for="t in slide.tags" :key="t" class="theme-tag">{{ t }}</span>
            </div>
          </div>
        </div>

        <!-- Content: tools -->
        <div v-if="slide.type === 'tools'" class="slide-content" :ref="el => setContentRef(el as HTMLElement | null, i)">
          <div class="tools-fullpage">
            <div class="section-eyebrow">PLATFORM</div>
            <h2 class="section-heading">&#1048;&#1085;&#1089;&#1090;&#1088;&#1091;&#1084;&#1077;&#1085;&#1090;&#1099;</h2>
            <div class="tools-grid">
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
                <div class="g-card-arrow">&rarr;</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Content: terminal -->
        <div v-if="slide.type === 'terminal'" class="slide-content" :ref="el => setContentRef(el as HTMLElement | null, i)">
          <div class="terminal-fullpage" @click="explode('/terminal')">
            <div class="terminal-zeta-big">&zeta;</div>
            <div class="terminal-title-big">&#1044;&#1079;&#1077;&#1090;&#1072;-&#1058;&#1077;&#1088;&#1084;&#1080;&#1085;&#1072;&#1083;</div>
            <div class="terminal-sub-big">&#1055;&#1086;&#1090;&#1086;&#1082;&#1086;&#1074;&#1099;&#1077; &#1076;&#1072;&#1085;&#1085;&#1099;&#1077; &#1074; &#1088;&#1077;&#1072;&#1083;&#1100;&#1085;&#1086;&#1084; &#1074;&#1088;&#1077;&#1084;&#1077;&#1085;&#1080;</div>
            <div class="terminal-cta">&#1054;&#1090;&#1082;&#1088;&#1099;&#1090;&#1100; &#1090;&#1077;&#1088;&#1084;&#1080;&#1085;&#1072;&#1083; &rarr;</div>
          </div>
        </div>
      </section>
    </div>

    <!-- Explosion flash -->
    <div class="flash" :class="{ on: !!explosion }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { useFullPageSlider } from '@/composables/useFullPageSlider'
import { useIsMobile } from '@/composables/useIsMobile'

const router = useRouter()
const { isMobile } = useIsMobile()
const explosion = ref<string | null>(null)

interface SlideData {
  id: string
  bgText: string[]
  bgTextColor: string
  bgColor: string
  type: 'hero' | 'theme' | 'tools' | 'terminal'
  headline?: string
  subline?: string
  description?: string
  label?: string
  tags?: string[]
}

const slides: SlideData[] = [
  {
    id: 'hero',
    bgText: ['QUANT', 'ANALYTICS'],
    bgTextColor: '#fff',
    bgColor: '#000',
    type: 'hero',
    headline: 'QUANTITATIVE',
    subline: 'ANALYTICS',
    description: 'Платформа количественного анализа для финансовых рынков',
  },
  {
    id: 'pricing',
    bgText: ['BLACK', 'SCHOLES'],
    bgTextColor: '#e63946',
    bgColor: '#0a0a0a',
    type: 'theme',
    label: 'Опционы',
    headline: 'BLACK-SCHOLES',
    subline: '· HESTON · LÉVY',
    description: 'БШМ, Хестон, Леви, FFT-ценообразование',
    tags: ['FFT', 'Greeks', 'IV'],
  },
  {
    id: 'regimes',
    bgText: ['MARKET', 'REGIMES'],
    bgTextColor: '#fff',
    bgColor: '#000',
    type: 'theme',
    label: 'Режимы',
    headline: 'MARKET',
    subline: 'REGIMES',
    description: 'HMM, стационарное распределение, комплексный анализ',
    tags: ['HMM', 'Viterbi', 'Spectral'],
  },
  {
    id: 'volatility',
    bgText: ['SABR', 'SVI'],
    bgTextColor: '#e63946',
    bgColor: '#0a0a0a',
    type: 'theme',
    label: 'Волатильность',
    headline: 'SABR · SVI',
    subline: 'VOLATILITY SURFACE',
    description: 'Калибровка SABR/SVI, smile & term-structure',
    tags: ['SABR', 'SVI', 'Smile'],
  },
  {
    id: 'tools',
    bgText: ['TOOLS'],
    bgTextColor: '#fff',
    bgColor: '#000',
    type: 'tools',
  },
  {
    id: 'terminal',
    bgText: ['ZETA'],
    bgTextColor: '#e63946',
    bgColor: '#0a0a0a',
    type: 'terminal',
  },
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

// Refs for DOM elements
const sectionRefs = ref<(HTMLElement | null)[]>([])
const contentRefs = ref<(HTMLElement | null)[]>([])

const setSectionRef = (el: HTMLElement | null, i: number) => {
  sectionRefs.value[i] = el
}
const setContentRef = (el: HTMLElement | null, i: number) => {
  contentRefs.value[i] = el
}

// GSAP slide transition
function animateTransition(from: number, to: number, direction: 'up' | 'down') {
  const yOut = direction === 'down' ? -50 : 50
  const yIn = direction === 'down' ? 50 : -50

  const outSection = sectionRefs.value[from]
  const inSection = sectionRefs.value[to]
  const outBgWords = outSection?.querySelectorAll('.slide-bg-word')
  const outContent = contentRefs.value[from]
  const inBgWords = inSection?.querySelectorAll('.slide-bg-word')
  const inContent = contentRefs.value[to]

  const tl = gsap.timeline()

  // Out
  if (outBgWords?.length) {
    tl.to(outBgWords, { opacity: 0, y: yOut, duration: 0.4, stagger: 0.05 }, 0)
  }
  if (outContent) {
    tl.to(outContent, { opacity: 0, y: yOut * 0.6, duration: 0.35 }, 0)
  }
  if (outSection) {
    tl.set(outSection, { visibility: 'hidden' }, 0.45)
  }

  // In
  if (inSection) {
    tl.set(inSection, { visibility: 'visible' }, 0.2)
  }
  if (inBgWords?.length) {
    tl.fromTo(
      inBgWords,
      { opacity: 0, y: -yIn },
      { opacity: 0.06, y: 0, duration: 0.6, stagger: 0.08, ease: 'power2.out' },
      0.25
    )
  }
  if (inContent) {
    tl.fromTo(
      inContent,
      { opacity: 0, y: -yIn * 0.6 },
      { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' },
      0.35
    )
  }
}

// Full page slider composable
const { currentSlide, goToSlide } = useFullPageSlider({
  totalSlides: slides.length,
  onSlideChange: animateTransition,
  cooldownMs: 1000,
})

// Explosion animation (preserved)
function explode(path: string) {
  if (explosion.value) return
  explosion.value = path
  setTimeout(() => router.push(path), 600)
}

// Lifecycle
onMounted(async () => {
  document.documentElement.style.overflow = 'hidden'
  document.body.style.overflow = 'hidden'

  await nextTick()

  sectionRefs.value.forEach((section, i) => {
    if (!section) return
    if (i === 0) {
      section.style.visibility = 'visible'
      const bgWords = section.querySelectorAll('.slide-bg-word')
      const content = contentRefs.value[0]
      gsap.fromTo(
        bgWords,
        { opacity: 0, scale: 1.15 },
        { opacity: 0.06, scale: 1, duration: 1.2, stagger: 0.1, ease: 'power2.out' }
      )
      if (content) {
        gsap.fromTo(
          content,
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.8, delay: 0.4, ease: 'power2.out' }
        )
      }
    } else {
      section.style.visibility = 'hidden'
    }
  })
})

onUnmounted(() => {
  document.documentElement.style.overflow = ''
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ── ROOT ── */
.home-root {
  position: fixed;
  inset: 0;
  overflow: hidden;
  background: #000;
  color: #fff;
  font-family: 'Inter', -apple-system, system-ui, sans-serif;
}

/* ── BRAND ── */
.fixed-brand {
  position: fixed;
  top: 28px;
  left: 32px;
  z-index: 100;
}

.brand-text {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.35);
}

/* ── PAGINATION ── */
.slide-pagination {
  position: fixed;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 100;
}

.slide-pagination.horizontal {
  right: auto;
  top: auto;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  flex-direction: row;
}

.slide-dot {
  width: 3px;
  height: 20px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 2px;
  cursor: pointer;
  padding: 0;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-dot.active {
  height: 40px;
  background: #e63946;
}

.slide-pagination.horizontal .slide-dot {
  width: 20px;
  height: 3px;
}

.slide-pagination.horizontal .slide-dot.active {
  width: 40px;
  height: 3px;
}

/* ── SLIDES ── */
.slides-container {
  position: relative;
  width: 100%;
  height: 100vh;
  height: 100dvh;
}

.fp-slide {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
}

/* ── BG TEXT ── */
.slide-bg-text {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  gap: 0;
}

.slide-bg-word {
  font-size: clamp(8rem, 22vw, 20rem);
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: -0.05em;
  line-height: 0.85;
  user-select: none;
  opacity: 0.06;
  will-change: transform, opacity;
}

/* ── CONTENT LAYER ── */
.slide-content {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── HERO ── */
.hero-content {
  text-align: center;
  max-width: 800px;
  padding: 0 2rem;
}

.hero-headline {
  font-size: clamp(2.5rem, 7vw, 5rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  margin: 0;
}

.hero-subline {
  font-size: clamp(1.5rem, 4vw, 2.8rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-top: 8px;
  opacity: 0.85;
  color: #e63946;
}

.hero-desc {
  font-size: clamp(0.85rem, 1.5vw, 1.05rem);
  color: rgba(255, 255, 255, 0.4);
  margin-top: 20px;
  line-height: 1.6;
}

/* ── THEME ── */
.theme-content {
  text-align: center;
  max-width: 700px;
  padding: 0 2rem;
}

.theme-label {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #e63946;
  margin-bottom: 16px;
}

.theme-headline {
  font-size: clamp(2rem, 6vw, 4rem);
  font-weight: 900;
  letter-spacing: -0.04em;
  line-height: 1;
  margin: 0;
}

.theme-subline {
  font-size: clamp(1.2rem, 3vw, 2rem);
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-top: 8px;
  opacity: 0.7;
}

.theme-desc {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 16px;
  line-height: 1.6;
}

.theme-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 20px;
}

.theme-tag {
  padding: 5px 14px;
  border: 1px solid rgba(230, 57, 70, 0.4);
  border-radius: 2px;
  font-size: 11px;
  font-weight: 600;
  color: #e63946;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* ── TOOLS ── */
.tools-fullpage {
  width: 100%;
  max-width: 1100px;
  padding: 60px 40px;
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

.g-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
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
  box-shadow: 0 10px 30px rgba(230, 57, 70, 0.12);
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

/* ── TERMINAL ── */
.terminal-fullpage {
  text-align: center;
  cursor: pointer;
  padding: 2rem;
}

.terminal-zeta-big {
  font-size: clamp(4rem, 10vw, 8rem);
  font-weight: 900;
  color: #e63946;
  line-height: 1;
  margin-bottom: 16px;
}

.terminal-title-big {
  font-size: clamp(1.5rem, 4vw, 2.4rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 8px;
}

.terminal-sub-big {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.4);
  margin-bottom: 24px;
}

.terminal-cta {
  display: inline-block;
  padding: 12px 28px;
  border: 1px solid rgba(230, 57, 70, 0.4);
  border-radius: 3px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #e63946;
  letter-spacing: 0.05em;
  transition: all 0.3s;
}

.terminal-fullpage:hover .terminal-cta {
  background: #e63946;
  color: #fff;
  border-color: #e63946;
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
  0% { transform: translate(-50%, -50%) scale(1); box-shadow: 0 0 10px #fff; }
  100% { transform: translate(-50%, -50%) scale(250); box-shadow: 0 0 600px 300px #fff; opacity: 1; }
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
@media (max-width: 1024px) {
  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .slide-bg-word {
    font-size: clamp(4rem, 18vw, 8rem);
  }

  .fixed-brand {
    top: 16px;
    left: 16px;
  }

  .tools-fullpage {
    padding: 40px 16px;
  }

  .tools-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .g-card {
    padding: 12px 14px;
  }
}

@media (max-width: 480px) {
  .slide-bg-word {
    font-size: clamp(3rem, 16vw, 6rem);
  }

  .tools-grid {
    grid-template-columns: 1fr;
  }

  .g-card-arrow {
    display: none;
  }

  .hero-headline {
    font-size: 2rem;
  }

  .theme-headline {
    font-size: 1.8rem;
  }
}
</style>
