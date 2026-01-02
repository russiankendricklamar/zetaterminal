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
        <div class="logo-badge">Калькулятор количественной аналитики</div>
        <h1 class="hero-title">
          Комплексный <span>калькулятор</span> для портфелей ценных бумаг и деривативов
        </h1>
        <p class="hero-subtitle">
          Единая панель для портфельного анализа, режимов рынка, справедливой
          стоимости деривативов и риск‑менеджмента институционального уровня.
        </p>

        <div class="hero-actions">
          <router-link to="/dashboard" class="btn primary">
            Открыть рабочую панель
          </router-link>
          <router-link to="/regimes" class="btn ghost">
            Смотреть рыночные режимы
          </router-link>
        </div>
      </section>

      <!-- Правая колонка: список инструментов -->
      <section class="tool-grid">
        <h2 class="tools-title">Инструменты платформы</h2>

        <div class="tools-grid">
          <!-- 
            Мы заменили router-link на div с обработчиком click.
            Добавлен класс :class="{ 'is-exploding': activeExplosion === '/portfolio' }"
          -->

          <!-- Portfolio -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/portfolio', 'is-faded': isFaded('/portfolio') }"
            @click="triggerExplosion('/portfolio')"
          >
            <div class="tool-icon blue">
              <div class="supernova blue"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Портфельный анализ</div>
              <div class="tool-desc">
                Доходность, риск‑метрики, VaR/ES, мониторинг позиций.
              </div>
            </div>
          </div>

          <!-- Market Regimes -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/regimes', 'is-faded': isFaded('/regimes') }"
            @click="triggerExplosion('/regimes')"
          >
            <div class="tool-icon indigo">
              <div class="supernova indigo"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Скрытая марковская цепь для портфелей ценных бумаг</div>
              <div class="tool-desc">
                Скрытые состояния, матрицы переходов, стационарное распределение.
              </div>
            </div>
          </div>

          <!-- Option Pricing -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/pricing/options', 'is-faded': isFaded('/pricing/options') }"
            @click="triggerExplosion('/pricing/options')"
          >
            <div class="tool-icon orange">
              <div class="supernova orange"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Вычисление справедливой стоимости опционов</div>
              <div class="tool-tag">Soon</div>
              <div class="tool-desc">
                БШМ, Модель Хестона, процессы Леви.
              </div>
            </div>
          </div>

          <!-- Swaps -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/pricing/swaps', 'is-faded': isFaded('/pricing/swaps') }"
            @click="triggerExplosion('/pricing/swaps')"
          >
            <div class="tool-icon orange">
              <div class="supernova orange"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Вычисление справедливой стоимости сделок СВОП</div>
              <div class="tool-tag">Soon</div>
              <div class="tool-desc">
                Процентные и валютные свопы, NPV, DV01, чувствительность.
              </div>
            </div>
          </div>

          <!-- Vol Surface -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/pricing/surface', 'is-faded': isFaded('/pricing/surface') }"
            @click="triggerExplosion('/pricing/surface')"
          >
            <div class="tool-icon orange">
              <div class="supernova orange"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Поверхность волатильности</div>
              <div class="tool-tag">Soon</div>
              <div class="tool-desc">
                Калибровка SABR/SVI, smile & term‑structure, арбитраж‑free.
              </div>
            </div>
          </div>

          <!-- Bonds -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/pricing/bonds', 'is-faded': isFaded('/pricing/bonds') }"
            @click="triggerExplosion('/pricing/bonds')"
          >
            <div class="tool-icon green">
              <div class="supernova green"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Определение справедливой стоимости облигаций (DCF)</div>
              <div class="tool-tag">Soon</div>
              <div class="tool-desc">
                Доходный подход, спреды к кривой, модифиц. дюрация, convexity.
              </div>
            </div>
          </div>

          <!-- Forwards -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/pricing/forwards', 'is-faded': isFaded('/pricing/forwards') }"
            @click="triggerExplosion('/pricing/forwards')"
          >
            <div class="tool-icon orange">
              <div class="supernova orange"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Определение справедливой стоимости сделок Форвард</div>
              <div class="tool-tag">Soon</div>
              <div class="tool-desc">
                Теоретическая цена, cost‑of‑carry, кросс‑курсы, roll‑down.
              </div>
            </div>
          </div>

          <!-- Margin -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/pricing/margin', 'is-faded': isFaded('/pricing/margin') }"
            @click="triggerExplosion('/pricing/margin')"
          >
            <div class="tool-icon orange">
              <div class="supernova orange"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Маржа по деривативам</div>
              <div class="tool-tag">Soon</div>
              <div class="tool-desc">
                Вариационная/начальная, стресс‑надбавки.
              </div>
            </div>
          </div>

          <!-- Risk -->
          <div 
            class="tool-card cursor-pointer"
            :class="{ 'is-exploding': activeExplosion === '/stress', 'is-faded': isFaded('/stress') }"
            @click="triggerExplosion('/stress')"
          >
            <div class="tool-icon red">
              <div class="supernova red"></div>
            </div>
            <div class="tool-body">
              <div class="tool-name">Риск менеджмент</div>
              <div class="tool-desc">
                Стресс‑тесты, бэктестинг VaR, сценарный анализ портфеля.
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
    
    <!-- Flash Overlay (optional extra smoothness) -->
    <div class="flash-overlay" :class="{ active: !!activeExplosion }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeExplosion = ref<string | null>(null)

// Checks if we should fade out this card (if another card is exploding)
const isFaded = (path: string) => {
  return activeExplosion.value !== null && activeExplosion.value !== path
}

const triggerExplosion = (path: string) => {
  if (activeExplosion.value) return // prevent double clicks
  
  activeExplosion.value = path
  
  // Wait for the explosion animation to fill the screen
  setTimeout(() => {
    router.push(path)
  }, 350) // Match this with CSS animation duration
}
</script>

<style scoped>
/* --------------------------------------
   EXPLOSION LOGIC
   -------------------------------------- */

.cursor-pointer {
  cursor: pointer;
}

/* When a card explodes */
.tool-card.is-exploding {
  z-index: 9999;
  border-color: rgba(255,255,255,0.8); /* Сразу светлеет */
  background: rgba(15,23,42,1); 
  transform: scale(1.02);
  animation: shockwave 0.3s linear; 
}

/* 
   CRITICAL: Remove overflow hidden from the icon container 
   when exploding so the star can expand infinitely.
*/
.tool-card.is-exploding .tool-icon {
  overflow: visible !important;
  background: transparent !important; /* Hide the container box background */
  box-shadow: none !important;
  border-color: transparent !important;
}

/* 
   Hide the "beam" effect during explosion so it doesn't 
   look weird floating in the middle of a giant star 
*/
.tool-card.is-exploding .tool-icon::after {
  display: none; /* Убираем сразу, чтобы не мерцало */
}

/* THE BIG BANG ANIMATION */
.tool-card.is-exploding .supernova {
  /* 
     Было: 0.8s
     Стало: 0.5s 
     Bezier: (0.1, 0, 0, 1) — "экспоненциальный взлет" (сразу быстро)
  */
  animation: big-bang 0.5s cubic-bezier(0.1, 0, 0, 1) forwards !important;
}

@keyframes big-bang {
  0% {
    transform: scale(1);
    opacity: 1;
    background: #fff;
  }
  30% {
    /* Очень быстрая вспышка до белого */
    transform: scale(8);
    box-shadow: 0 0 100px 50px rgba(255,255,255,1);
  }
  100% {
    /* Заполнение экрана */
    transform: scale(200); 
    opacity: 1;
    background: #fff;
    box-shadow: 0 0 1000px 500px rgba(255,255,255,1);
  }
}

@keyframes shockwave {
  0% { transform: scale(1); }
  50% { transform: scale(0.96); } /* Сжатие перед взрывом */
  100% { transform: scale(1.02); }
}

/* Fade out other cards when one is active */
.tool-card.is-faded {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.9);
  filter: blur(4px);
  transition: all 0.3s ease; /* Ускорено с 0.4s */
}

/* White Flash Overlay for smoother transition to next page */
.flash-overlay {
  position: fixed;
  inset: 0;
  background: #fff;
  z-index: 9998;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.1s ease; /* Мгновенное появление */
}
.flash-overlay.active {
  transition-delay: 0.25s; /* Появляется почти сразу за взрывом */
  opacity: 1;
}


/* --------------------------------------
   STANDARD STYLES (Kept exactly as before)
   -------------------------------------- */

.home-root {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at top, #050816 0%, #020308 45%, #000 100%);
  color: #f9fafb;
}

/* ===================== LAVA LAMP BACKGROUND ===================== */
.lava-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
  filter: blur(36px) saturate(150%);
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
    radial-gradient(circle at 10% 0%, rgba(255,255,255,0.10), transparent 40%),
    radial-gradient(circle at 90% 100%, rgba(255,255,255,0.06), transparent 45%);
  opacity: 0.9;
}

/* ===================== LAYOUT ===================== */
.home-layout {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto;
  padding: 64px 32px 40px 32px;
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1.1fr);
  gap: 40px;
  align-items: start;
}

.hero {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 560px;
}

.logo-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(148,163,184,0.4);
  background: radial-gradient(circle at 0 0, rgba(255,255,255,0.18), rgba(15,23,42,0.8));
  box-shadow: 0 10px 30px rgba(15,23,42,0.8);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.logo-badge span {
  color: #38bdf8;
}

.hero-title {
  font-size: 32px;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.03em;
}
.hero-title span {
  color: #a5b4fc;
}

.hero-subtitle {
  font-size: 14px;
  line-height: 1.7;
  color: rgba(226,232,240,0.75);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
.btn.primary {
  background: radial-gradient(circle at 0 0, #22d3ee, #6366f1);
  color: #0b1020;
  box-shadow: 0 10px 40px rgba(56,189,248,0.35);
}
.btn.primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 45px rgba(56,189,248,0.45);
}
.btn.ghost {
  background: rgba(15,23,42,0.8);
  color: #e5e7eb;
  border-color: rgba(148,163,184,0.5);
}
.btn.ghost:hover {
  background: rgba(15,23,42,0.95);
}

.hero-footnote {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(148,163,184,0.9);
}

/* ===================== TOOLS GRID ===================== */
.tool-grid {
  backdrop-filter: blur(24px);
  background: radial-gradient(circle at 0 0, rgba(15,23,42,0.9), rgba(15,23,42,0.85));
  border-radius: 24px;
  border: 1px solid rgba(148,163,184,0.35);
  box-shadow: 0 30px 80px rgba(15,23,42,0.9);
  padding: 20px 18px 18px;
  transform: translateY(-24px);
}

.tools-title {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(209,213,219,0.9);
  margin-bottom: 14px;
}

.tools-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

/* Note: we removed router-link, using div now */
.tool-card {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 10px 10px;
  border-radius: 14px;
  text-decoration: none;
  color: inherit;
  background: radial-gradient(circle at 0 0, rgba(255,255,255,0.04), rgba(15,23,42,0.8));
  border: 1px solid transparent;
  transition: all 0.2s ease;
}
.tool-card:hover {
  border-color: rgba(148,163,184,0.7);
  background: radial-gradient(circle at 0 0, rgba(255,255,255,0.08), rgba(15,23,42,0.9));
  transform: translateY(-1px);
}

/* CONTAINER FOR THE SUPERNOVA */
.tool-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px; 
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.3);
  position: relative;
  overflow: hidden; /* Clips the beam normally */
  border: 1px solid rgba(255,255,255,0.05);
  transition: all 0.2s;
}

.tool-icon.blue { background: rgba(56,189,248,0.1); }
.tool-icon.indigo { background: rgba(129,140,248,0.1); }
.tool-icon.orange { background: rgba(249,115,22,0.1); }
.tool-icon.green { background: rgba(34,197,94,0.1); }
.tool-icon.red { background: rgba(248,113,113,0.1); }

/* The "Light Beam" */
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

/* SUPERNOVA CORE */
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

.supernova.blue   { box-shadow: 0 0 12px 2px rgba(59, 130, 246, 0.6); }
.supernova.indigo { box-shadow: 0 0 12px 2px rgba(129, 140, 248, 0.6); }
.supernova.orange { box-shadow: 0 0 12px 2px rgba(249, 115, 22, 0.6); }
.supernova.green  { box-shadow: 0 0 12px 2px rgba(34, 197, 94, 0.6); }
.supernova.red    { box-shadow: 0 0 12px 2px rgba(248, 113, 113, 0.6); }

/* Standard Hover */
.tool-card:hover .supernova {
  transform: scale(1.15);
  animation-duration: 1.5s;
}
.tool-card:hover .supernova.blue { box-shadow: 0 0 15px 5px #60a5fa, 0 0 30px 10px rgba(59, 130, 246, 0.4); }
.tool-card:hover .supernova.indigo { box-shadow: 0 0 15px 5px #a5b4fc, 0 0 30px 10px rgba(129, 140, 248, 0.4); }
.tool-card:hover .supernova.orange { box-shadow: 0 0 15px 5px #fb923c, 0 0 30px 10px rgba(249, 115, 22, 0.4); }
.tool-card:hover .supernova.green { box-shadow: 0 0 15px 5px #4ade80, 0 0 30px 10px rgba(34, 197, 94, 0.4); }
.tool-card:hover .supernova.red { box-shadow: 0 0 15px 5px #f87171, 0 0 30px 10px rgba(248, 113, 113, 0.4); }

.tool-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.tool-name { font-size: 13px; font-weight: 600; }
.tool-desc { font-size: 11px; color: rgba(148,163,184,0.95); }
.tool-tag {
  align-self: flex-start;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  padding: 1px 6px;
  border-radius: 999px;
  border: 1px solid rgba(251,191,36,0.6);
  color: #facc15;
  background: rgba(15,23,42,0.9);
}

/* ===================== ANIMATIONS ===================== */
@keyframes star-pulse {
  0%, 100% { opacity: 0.85; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.05); }
}
@keyframes shimmer {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
@keyframes beam-wobble {
  0%   { transform: translate(0, 0) scale(1); }
  50%  { transform: translate(2px, -2px) scale(1.1); }
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
  80% { transform: translate3d(40%, 45%, 0) scale(1.0); }
  100% { transform: translate3d(35%, 30%, 0) scale(0.9); }
}

@media (max-width: 1024px) {
  .home-layout {
    padding: 72px 16px 32px 16px;
    grid-template-columns: minmax(0, 1fr);
    gap: 32px;
  }
  .tool-grid {
    max-width: 520px;
    margin-top: 8px;
    transform: translateY(0);     
  }
}
@media (max-width: 640px) {
  .home-layout {
    padding: 64px 16px 24px 16px;
  }
}
</style>