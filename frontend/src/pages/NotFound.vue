<template>
  <div class="page-container center-content">
    <!-- Main Card -->
    <div class="not-found-card">
      <div class="content-wrapper">
        <div class="error-code-container">
          <span class="error-code font-anton">404</span>
          <div class="scan-line"></div>
        </div>

        <h1 class="error-title font-oswald">СТРАНИЦА НЕ НАЙДЕНА</h1>
        <p class="error-desc font-mono">
          Похоже, вы вышли за пределы известной вселенной или доступных данных.
        </p>

        <div class="actions">
          <router-link to="/" class="btn btn-primary">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
            Вернуться на Дашборд
          </router-link>

          <button @click="goBack" class="btn btn-secondary">
            <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Назад
          </button>
        </div>

        <div class="divider"></div>

        <div class="suggestions">
          <span class="suggestions-lbl font-mono">БЫСТРЫЙ ПЕРЕХОД:</span>
          <div class="links-row">
            <router-link to="/greeks" class="link-pill">Риск-метрики</router-link>
            <router-link to="/stress" class="link-pill">Стресс-тесты</router-link>
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
  background: var(--bg-primary);
}

/* ============================================
   BRUTALIST CARD
   ============================================ */
.not-found-card {
  position: relative;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-dark);
  max-width: 500px;
  width: 100%;
  padding: 48px;
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
  font-size: 120px;
  font-weight: 800;
  line-height: 1;
  color: var(--accent-red);
  letter-spacing: -0.05em;
  text-shadow: 0 0 60px rgba(220, 38, 38, 0.3);
}

.scan-line {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to bottom, transparent 50%, rgba(255,255,255,0.02) 50%);
  background-size: 100% 4px;
  pointer-events: none;
}

.error-title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.error-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
  margin: 0 0 32px 0;
  max-width: 320px;
  text-align: center;
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
  padding: 12px 24px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid var(--border-dark);
  color: white;
  text-decoration: none;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-family: var(--font-family-mono);
}

.btn-primary {
  background: var(--accent-red);
  border-color: var(--accent-red);
  flex: 2;
}

.btn-primary:hover {
  background: #b91c1c;
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  flex: 1;
}

.btn-secondary:hover {
  background: var(--border-dark);
  color: #fff;
  border-color: var(--text-muted);
}

.divider {
  height: 1px;
  width: 100%;
  background: var(--border-dark);
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
  font-size: 10px;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  font-weight: 500;
}

.links-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.link-pill {
  padding: 8px 16px;
  font-size: 11px;
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  text-decoration: none;
  border: 1px solid var(--border-dark);
  transition: all 0.2s;
  font-family: var(--font-family-mono);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.link-pill:hover {
  background: var(--border-dark);
  color: #fff;
  border-color: var(--accent-red);
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .not-found-card {
    padding: 32px 24px;
  }

  .error-code {
    font-size: 80px;
  }

  .error-title {
    font-size: 20px;
  }

  .error-desc {
    font-size: 12px;
  }

  .actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .links-row {
    flex-direction: column;
    width: 100%;
  }

  .link-pill {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .page-container {
    padding: 12px;
  }

  .not-found-card {
    padding: 24px 16px;
  }

  .error-code {
    font-size: 64px;
  }

  .error-title {
    font-size: 18px;
  }

  .error-desc {
    font-size: 11px;
    max-width: 100%;
  }

  .btn {
    font-size: 11px;
    padding: 10px 16px;
  }
}
</style>
