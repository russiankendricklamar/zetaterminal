<template>
  <div class="home-root">
    <!-- Лавовая лампа / liquid glass фон -->
    <div class="lava-layer">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="blob blob-4"></div>
      <div class="glass-gradient"></div>
    </div>

    <!-- Контент поверх -->
    <div class="home-layout">
      <!-- Левая колонка -->
      <section class="hero">
        <div class="logo-badge">
          <span class="badge-icon">◆</span>
          Quantitative Analytics
        </div>
        <h1 class="hero-title">
          Комплексный <span>калькулятор</span> для портфелей и деривативов
        </h1>
        
        <!-- Framed subtitle -->
        <div class="subtitle-frame">
          <p class="hero-subtitle">
            Единая платформа для портфельного анализа, скрытых марковских цепей, справедливой стоимости деривативов и риск‑менеджмента институционального уровня.
          </p>
        </div>

        <div class="hero-actions">
          <router-link to="/dashboard" class="btn primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
              <polyline points="13 2 13 9 20 9"></polyline>
            </svg>
            Открыть рабочую панель
          </router-link>
          <router-link to="/regimes" class="btn ghost">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="12 3 20 7.5 20 16.5 12 21 4 16.5 4 7.5 12 3"></polyline>
              <line x1="12" y1="12" x2="20" y2="7.5"></line>
              <line x1="12" y1="12" x2="12" y2="21"></line>
              <line x1="12" y1="12" x2="4" y2="7.5"></line>
            </svg>
            Смотреть рыночные режимы
          </router-link>
        </div>
      </section>

      <!-- Правая колонка: список инструментов -->
      <section class="tool-grid">
        <div class="tools-header">
          <h2 class="tools-title">Инструменты платформы</h2>
        </div>

        <div class="tools-grid">
          <!-- 1. Portfolio Analytics -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === '/portfolio', 'is-faded': isFaded('/portfolio') }"
            @click="triggerExplosion('/portfolio')"
          >
            <div class="tool-icon purple">
              <div class="supernova purple"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Портфельный анализ</div>
              <div class="tool-desc">
                Доходность, VaR/ES, мониторинг позиций, корреляции активов
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 2. Risk Management -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === '/stress', 'is-faded': isFaded('/stress') }"
            @click="triggerExplosion('/stress')"
          >
            <div class="tool-icon purple">
              <div class="supernova purple"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Риск-менеджмент</div>
              <div class="tool-desc">
                Стресс-тесты, бэктестинг VaR, сценарный анализ портфеля
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 3. Market Regimes (HMM) -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === '/regimes', 'is-faded': isFaded('/regimes') }"
            @click="triggerExplosion('/regimes')"
          >
            <div class="tool-icon blue">
              <div class="supernova blue"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Скрытая Марковская цепь</div>
              <div class="tool-desc">
                Рыночные режимы, матрицы переходов, стационарное распределение
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 4. Bond Valuation (DCF) -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === '/bond-valuation', 'is-faded': isFaded('/bond-valuation') }"
            @click="triggerExplosion('/bond-valuation')"
          >
            <div class="tool-icon green">
              <div class="supernova green"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Справедливая стоимость облигаций</div>
              <div class="tool-desc">
                DCF подход, спреды к кривой, дюрация, выпуклость (convexity)
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 6. Option Pricing -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === '/pricing/options', 'is-faded': isFaded('/pricing/options') }"
            @click="triggerExplosion('/pricing/options')"
          >
            <div class="tool-icon green">
              <div class="supernova green"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Справедливая стоимость опционов</div>
              <div class="tool-desc">
                БШМ, модель Хестона, процессы Леви, FFT-ценообразование
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 8. Volatility Surface -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === '/analytics/volatility', 'is-faded': isFaded('/analytics/volatility') }"
            @click="triggerExplosion('/analytics/volatility')"
          >
            <div class="tool-icon blue">
              <div class="supernova blue"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Поверхность волатильности</div>
              <div class="tool-desc">
                Калибровка SABR/SVI, smile & term-structure, arbitrage-free
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 7. Swaps -->
          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === 'valuation/swaps', 'is-faded': isFaded('valuation/swaps') }"
            @click="triggerExplosion('valuation/swaps')"
          >
            <div class="tool-icon green">
              <div class="supernova green"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Справедливая стоимость СВОПов</div>
              <div class="tool-desc">
                IRS & FX свопы, NPV, DV01, чувствительность к кривой
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <div 
            class="tool-card"
            :class="{ 'is-exploding': activeExplosion === 'valuation/forwards', 'is-faded': isFaded('valuation/forwards') }"
            @click="triggerExplosion('valuation/forwards')"
          >
            <div class="tool-icon green">
              <div class="supernova green"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Справедливая стоимость форвардов</div>
              <div class="tool-desc">
                Оценка справедливой стоимости, построение кривой, арбитраж
              </div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>

          <!-- 10. Margin -->
          <div 
            class="tool-card coming-soon"
            :class="{ 'is-exploding': activeExplosion === '/pricing/margin', 'is-faded': isFaded('/pricing/margin') }"
            @click="triggerExplosion('/pricing/margin')"
          >
            <div class="tool-icon orange">
              <div class="supernova orange"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Маржа по деривативам</div>
              <div class="tool-desc">
                Вариационная/начальная маржа, SIMM, стресс-надбавки
              </div>
              <div class="tool-tag">Soon</div>
            </div>
            <div class="tool-arrow">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </div>
          </div>
        </div>

        <div 
          class="tool-card"
          :class="{ 'is-exploding': activeExplosion === '/vanila-bond-report', 'is-faded': isFaded('/vanila-bond-report') }"
          @click="triggerExplosion('/vanila-bond-report')"
        >
          <div class="tool-icon nova">
            <div class="supernova nova"></div>
          </div>
          <div class="tool-body">
            <div class="tool-name">Отчёты по облигациям</div>
            <div class="tool-desc">
              Vanila Bond Report, шаблонные отчеты и аналитика
            </div>
          </div>
          <div class="tool-arrow">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </div>
        </div>

      </section>
    </div>
    
    <!-- Flash Overlay -->
    <div class="flash-overlay" :class="{ active: !!activeExplosion }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeExplosion = ref<string | null>(null)

const totalTools = computed(() => 10)

const isFaded = (path: string) => {
  return activeExplosion.value !== null && activeExplosion.value !== path
}

const triggerExplosion = (path: string) => {
  if (activeExplosion.value) return
  
  activeExplosion.value = path
  
  setTimeout(() => {
    router.push(path)
  }, 350)
}
</script>

<style scoped>
/* ============================================
   EXPLOSION ANIMATIONS
   ============================================ */
.tool-card.is-exploding {
  z-index: 9999;
  border-color: rgba(255, 255, 255, 0.8);
  background: rgba(15, 23, 42, 1);
  transform: scale(1.02);
  animation: shockwave 0.3s linear;
}

.tool-card.is-exploding .tool-icon {
  overflow: visible !important;
  background: transparent !important;
  box-shadow: none !important;
  border-color: transparent !important;
}

.tool-card.is-exploding .tool-icon::after {
  display: none;
}

.tool-card.is-exploding .supernova {
  animation: big-bang 0.5s cubic-bezier(0.1, 0, 0, 1) forwards !important;
}

@keyframes big-bang {
  0% {
    transform: scale(1);
    opacity: 1;
    background: #fff;
  }
  30% {
    transform: scale(8);
    box-shadow: 0 0 100px 50px rgba(255, 255, 255, 1);
  }
  100% {
    transform: scale(200);
    opacity: 1;
    background: #fff;
    box-shadow: 0 0 1000px 500px rgba(255, 255, 255, 1);
  }
}

@keyframes shockwave {
  0% { transform: scale(1); }
  50% { transform: scale(0.96); }
  100% { transform: scale(1.02); }
}

.tool-card.is-faded {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.9);
  filter: blur(4px);
  transition: all 0.3s ease;
}

.flash-overlay {
  position: fixed;
  inset: 0;
  background: #fff;
  z-index: 9998;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.1s ease;
}
.flash-overlay.active {
  transition-delay: 0.25s;
  opacity: 1;
}

/* ============================================
   HOME ROOT & LAYOUT
   ============================================ */
.home-root {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
  background: radial-gradient(circle at top, #050816 0%, #020308 45%, #000 100%);
  color: #f9fafb;
}

.home-layout {
  position: relative;
  z-index: 1;
  max-width: 1480px;
  margin: 0 auto;
  padding: 80px 40px 80px 40px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 60px;
  align-items: flex-start;
  min-height: 100vh;
}

/* ============================================
   LAVA LAMP BACKGROUND
   ============================================ */
.lava-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
  filter: blur(40px) saturate(150%);
}

.blob {
  position: absolute;
  border-radius: 999px;
  opacity: 0.85;
  mix-blend-mode: screen;
  will-change: transform;
}

.blob-1 {
  width: 420px;
  height: 420px;
  background: radial-gradient(circle at 30% 30%, #34d399, #0f766e 60%, transparent 80%);
  animation: blobOrbit1 32s ease-in-out infinite;
}

.blob-2 {
  width: 520px;
  height: 520px;
  background: radial-gradient(circle at 70% 40%, #f97316, #ea580c 60%, transparent 80%);
  animation: blobOrbit2 40s ease-in-out infinite;
}

.blob-3 {
  width: 480px;
  height: 480px;
  background: radial-gradient(circle at 50% 20%, #6366f1, #22d3ee 60%, transparent 80%);
  animation: blobOrbit3 36s ease-in-out infinite;
}

.blob-4 {
  width: 260px;
  height: 260px;
  background: radial-gradient(circle at 40% 30%, #22d3ee, #0ea5e9 60%, transparent 80%);
  animation: blobOrbit4 24s ease-in-out infinite;
  animation-delay: -4s;
}

.glass-gradient {
  position: absolute;
  inset: 5%;
  background:
    radial-gradient(circle at 10% 0%, rgba(255, 255, 255, 0.1), transparent 40%),
    radial-gradient(circle at 90% 100%, rgba(255, 255, 255, 0.06), transparent 45%);
  opacity: 0.9;
}

/* ============================================
   HERO SECTION
   ============================================ */
.hero {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 580px;
  padding-top: 12px;
}

.logo-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: radial-gradient(circle at 0 0, rgba(255, 255, 255, 0.18), rgba(15, 23, 42, 0.8));
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.8);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  width: fit-content;
}

.badge-icon {
  color: #22d3ee;
  font-size: 14px;
}

.hero-title {
  font-size: 36px;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0;
}

.hero-title span {
  background: linear-gradient(135deg, #a5b4fc, #22d3ee, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* ============================================
   SUBTITLE FRAME
   ============================================ */
.subtitle-frame {
  backdrop-filter: blur(16px);
  background: rgba(34, 211, 238, 0.08);
  border: 1.5px solid rgba(34, 211, 238, 0.2);
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: 
    0 0 24px rgba(34, 211, 238, 0.1),
    inset 0 1px 16px rgba(34, 211, 238, 0.08);
}

.hero-subtitle {
  font-size: 15px;
  line-height: 1.7;
  color: rgba(226, 232, 240, 0.95);
  margin: 0;
  font-weight: 500;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 8px;
}

.btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 20px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn.primary {
  background: linear-gradient(135deg, #22d3ee, #6366f1);
  color: #0b1020;
  box-shadow: 0 12px 45px rgba(56, 189, 248, 0.3);
}

.btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 55px rgba(56, 189, 248, 0.45);
}

.btn.ghost {
  background: rgba(15, 23, 42, 0.85);
  color: #e5e7eb;
  border-color: rgba(148, 163, 184, 0.5);
}

.btn.ghost:hover {
  background: rgba(15, 23, 42, 0.95);
  border-color: rgba(148, 163, 184, 0.8);
}

/* ============================================
   TOOLS GRID - FRAMED CONTAINER
   ============================================ */
.tool-grid {
  backdrop-filter: blur(24px);
  background: rgba(15, 23, 42, 0.6);
  border-radius: 24px;
  border: 1.5px solid rgba(34, 211, 238, 0.25);
  box-shadow: 
    0 0 30px rgba(34, 211, 238, 0.15),
    inset 0 1px 20px rgba(34, 211, 238, 0.1),
    0 30px 80px rgba(15, 23, 42, 0.9);
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 160px);
  overflow-y: auto;
}

/* Стилизованный скроллбар */
.tool-grid::-webkit-scrollbar {
  width: 6px;
}

.tool-grid::-webkit-scrollbar-track {
  background: transparent;
}

.tool-grid::-webkit-scrollbar-thumb {
  background: rgba(34, 211, 238, 0.2);
  border-radius: 3px;
}

.tool-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(34, 211, 238, 0.4);
}

.tools-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}

.tools-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(209, 213, 219, 0.9);
  margin: 0;
}

.tools-count {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(34, 211, 238, 0.15);
  color: #22d3ee;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(34, 211, 238, 0.3);
}

.tools-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-card {
  display: flex;
  gap: 14px;
  align-items: center;
  padding: 12px 12px;
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(148, 163, 184, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-card:hover {
  border-color: rgba(148, 163, 184, 0.4);
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(4px);
}

.tool-card.coming-soon {
  opacity: 0.65;
}

.tool-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.4);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.2s;
}

.tool-icon.blue { background: rgba(56, 189, 248, 0.12); }
.tool-icon.purple { background: rgba(168, 85, 247, 0.12); }
.tool-icon.cyan { background: rgba(34, 211, 238, 0.12); }
.tool-icon.green { background: rgba(34, 197, 94, 0.12); }
.tool-icon.nova { background: rgba(255, 51, 102, 0.12); }
.tool-icon.orange { background: rgba(249, 115, 22, 0.12); }

.tool-icon::after {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 60%);
  transform: scale(0);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s ease;
  z-index: 1;
}

.tool-card:hover .tool-icon::after {
  opacity: 0.2;
  animation: beam-wobble 2s infinite ease-in-out;
  transform: scale(1);
}

.supernova {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 33%, #faf5ff 66%, #ffffff 100%);
  background-size: 200% 200%;
  position: relative;
  z-index: 2;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  animation: star-pulse 3s infinite ease-in-out, shimmer 3s infinite linear;
}

.supernova.blue { box-shadow: 0 0 12px 2px rgba(59, 130, 246, 0.6); }
.supernova.purple { box-shadow: 0 0 12px 2px rgba(168, 85, 247, 0.6); }
.supernova.cyan { box-shadow: 0 0 12px 2px rgba(34, 211, 238, 0.6); }
.supernova.green { box-shadow: 0 0 12px 2px rgba(34, 197, 94, 0.6); }
.supernova.nova { box-shadow: 0 0 12px 2px rgba(255, 51, 102, 0.6); }
.supernova.orange { box-shadow: 0 0 12px 2px rgba(249, 115, 22, 0.6); }

.tool-card:hover .supernova {
  transform: scale(1.2);
  animation-duration: 1.5s;
}

.tool-card:hover .supernova.blue { box-shadow: 0 0 18px 6px #60a5fa, 0 0 36px 12px rgba(59, 130, 246, 0.3); }
.tool-card:hover .supernova.purple { box-shadow: 0 0 18px 6px #c084fc, 0 0 36px 12px rgba(168, 85, 247, 0.3); }
.tool-card:hover .supernova.cyan { box-shadow: 0 0 18px 6px #67e8f9, 0 0 36px 12px rgba(34, 211, 238, 0.3); }
.tool-card:hover .supernova.green { box-shadow: 0 0 18px 6px #4ade80, 0 0 36px 12px rgba(34, 197, 94, 0.3); }
.tool-card:hover .supernova.nova { box-shadow: 0 0 18px 6px #ff3366, 0 0 36px 12px rgba(255, 51, 102, 0.3); }
.tool-card:hover .supernova.orange { box-shadow: 0 0 18px 6px #fb923c, 0 0 36px 12px rgba(249, 115, 22, 0.3); }

.tool-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.tool-name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  line-height: 1.3;
}

.tool-desc {
  font-size: 12px;
  color: rgba(148, 163, 184, 0.85);
  line-height: 1.4;
}

.tool-tag {
  align-self: flex-start;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(251, 191, 36, 0.5);
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  margin-top: 2px;
}

.tool-arrow {
  color: rgba(148, 163, 184, 0.4);
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.tool-card:hover .tool-arrow {
  color: rgba(148, 163, 184, 0.8);
  transform: translateX(2px);
}

/* ============================================
   ANIMATIONS
   ============================================ */
@keyframes star-pulse {
  0%, 100% { opacity: 0.85; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}

@keyframes shimmer {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

@keyframes beam-wobble {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(2px, -2px) scale(1.1); }
  100% { transform: translate(0, 0) scale(1); }
}

@keyframes blobOrbit1 {
  0% { transform: translate3d(-160px, -120px, 0) scale(1); }
  25% { transform: translate3d(120px, -40px, 0) scale(1.15); }
  50% { transform: translate3d(260px, 120px, 0) scale(0.95); }
  75% { transform: translate3d(-40px, 220px, 0) scale(1.1); }
  100% { transform: translate3d(-160px, -120px, 0) scale(1); }
}

@keyframes blobOrbit2 {
  0% { transform: translate3d(220px, 40%, 0) scale(1) rotate(0deg); }
  20% { transform: translate3d(60px, 10%, 0) scale(1.05) rotate(10deg); }
  40% { transform: translate3d(-80px, 35%, 0) scale(0.9) rotate(-8deg); }
  60% { transform: translate3d(40px, 70%, 0) scale(1.12) rotate(4deg); }
  80% { transform: translate3d(260px, 55%, 0) scale(1.02) rotate(-6deg); }
  100% { transform: translate3d(220px, 40%, 0) scale(1) rotate(0deg); }
}

@keyframes blobOrbit3 {
  0% { transform: translate3d(10%, 80%, 0) scale(1); }
  25% { transform: translate3d(40%, 60%, 0) scale(1.18); }
  50% { transform: translate3d(65%, 85%, 0) scale(0.92); }
  75% { transform: translate3d(30%, 105%, 0) scale(1.08); }
  100% { transform: translate3d(10%, 80%, 0) scale(1); }
}

@keyframes blobOrbit4 {
  0% { transform: translate3d(35%, 30%, 0) scale(0.9); }
  20% { transform: translate3d(50%, 20%, 0) scale(1.1); }
  40% { transform: translate3d(65%, 35%, 0) scale(0.95); }
  60% { transform: translate3d(55%, 55%, 0) scale(1.15); }
  80% { transform: translate3d(40%, 45%, 0) scale(1); }
  100% { transform: translate3d(35%, 30%, 0) scale(0.9); }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 1200px) {
  .home-layout {
    grid-template-columns: 1fr;
    gap: 48px;
    padding: 72px 32px 60px 32px;
    height: auto;
  }

  .tool-grid {
    max-height: none;
    overflow-y: visible;
  }

  .hero-title {
    font-size: 32px;
  }
}

@media (max-width: 768px) {
  .home-root {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .home-layout {
    padding: 64px 20px 40px 20px;
    gap: 36px;
    min-height: auto;
    height: auto;
  }

  .hero-title {
    font-size: 28px;
  }

  .subtitle-frame {
    padding: 16px 18px;
  }

  .hero-subtitle {
    font-size: 14px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .tool-grid {
    padding: 18px 14px;
    max-height: none;
    overflow-y: visible;
  }

  .tool-card {
    padding: 10px 10px;
  }

  .tool-name {
    font-size: 12px;
  }

  .tool-desc {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .home-root {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .home-layout {
    padding: 56px 16px 32px 16px;
    min-height: auto;
    height: auto;
  }

  .hero-title {
    font-size: 24px;
  }

  .subtitle-frame {
    padding: 14px 16px;
  }

  .tool-icon {
    width: 36px;
    height: 36px;
  }

  .tool-arrow {
    display: none;
  }

  .tool-grid {
    max-height: none;
  }
}
</style>