<!-- src/views/NotFoundView.vue -->
<template>
  <div class="page-container center-content">
    
    <!-- Main Glass Card -->
    <div class="card glass-panel not-found-card">
      
      <!-- Ambient Glow Behind -->
      <div class="glow-bg"></div>

      <div class="content-wrapper">
        <div class="error-code-container">
            <span class="error-code">404</span>
            <div class="scan-line"></div>
        </div>
        
        <h1 class="error-title">Страница не найдена</h1>
        <p class="error-desc">
          Похоже, вы вышли за пределы известной вселенной или доступных данных.
        </p>

        <div class="actions">
            <router-link to="/" class="btn btn-primary-gradient">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                Вернуться на Дашборд
            </router-link>
            
            <button @click="goBack" class="btn btn-outline">
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
                Назад
            </button>
        </div>

        <div class="divider"></div>

        <div class="suggestions">
            <span class="suggestions-lbl">Быстрый переход:</span>
            <div class="links-row">
                <router-link to="/risk-metrics" class="link-pill">Риск-метрики</router-link>
                <router-link to="/monte-carlo" class="link-pill">Монте-Карло</router-link>
                <router-link to="/stress-testing" class="link-pill">Стресс-тесты</router-link>
            </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
const goBack = () => {
  window.history.back()
}
</script>

<style scoped>
/* ============================================
   LAYOUT & CONTAINER
   ============================================ */
.page-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* ============================================
   GLASS CARD ENGINE
   ============================================ */
.card {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  background: rgba(20, 22, 28, 0.3);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  box-shadow: 
    0 20px 50px -20px rgba(0,0,0,0.6),
    inset 0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.15);
  max-width: 500px;
  width: 100%;
}

.glass-panel {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 1;
}

/* Glow Effect */
.glow-bg {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.15), transparent 60%);
    pointer-events: none;
    z-index: 0;
    animation: pulse 4s ease-in-out infinite alternate;
}

@keyframes pulse {
    0% { opacity: 0.5; transform: scale(1); }
    100% { opacity: 0.8; transform: scale(1.1); }
}

.content-wrapper {
    position: relative;
    z-index: 2;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

/* ============================================
   TYPOGRAPHY & ELEMENTS
   ============================================ */
.error-code-container {
    position: relative;
    margin-bottom: 24px;
}

.error-code {
    font-size: 96px;
    font-weight: 800;
    line-height: 1;
    font-family: var(--font-family-mono); /* Или monospace */
    background: linear-gradient(135deg, #fff 30%, rgba(255,255,255,0.2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.05em;
    filter: drop-shadow(0 0 20px rgba(255,255,255,0.1));
}

.scan-line {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(to bottom, transparent 50%, rgba(255,255,255,0.05) 50%);
    background-size: 100% 4px;
    pointer-events: none;
    mix-blend-mode: overlay;
}

.error-title {
    font-size: 24px;
    font-weight: 700;
    color: #fff;
    margin: 0 0 12px 0;
    letter-spacing: -0.01em;
}

.error-desc {
    font-size: 14px;
    color: rgba(255,255,255,0.6);
    line-height: 1.5;
    margin: 0 0 32px 0;
    max-width: 320px;
}

/* ============================================
   BUTTONS
   ============================================ */
.actions {
    display: flex;
    gap: 12px;
    width: 100%;
    justify-content: center;
}

.btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    color: white;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-primary-gradient {
    background: linear-gradient(135deg, #0ea5e9, #2563eb);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3), inset 0 1px 0 rgba(255,255,255,0.2);
    flex: 2;
}
.btn-primary-gradient:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.btn-outline {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.8);
    flex: 1;
}
.btn-outline:hover {
    background: rgba(255,255,255,0.1);
    color: #fff;
}

.divider {
    height: 1px;
    width: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 32px 0;
}

/* ============================================
   SUGGESTIONS
   ============================================ */
.suggestions {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}

.suggestions-lbl {
    font-size: 11px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    letter-spacing: 0.05em;
    font-weight: 500;
}

.links-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
}

.link-pill {
    padding: 6px 12px;
    font-size: 11px;
    color: rgba(255,255,255,0.6);
    background: rgba(255,255,255,0.03);
    border-radius: 20px;
    text-decoration: none;
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.2s;
}

.link-pill:hover {
    background: rgba(255,255,255,0.1);
    color: #fff;
    border-color: rgba(255,255,255,0.2);
}
</style>