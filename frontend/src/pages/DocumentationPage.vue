<!-- src/views/DocumentationPage.vue -->
<template>
  <div class="docs-root">
    <!-- Лавовая лампа / liquid glass фон - везде -->
    <div class="lava-layer">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="blob blob-4"></div>
      <div class="glass-gradient"></div>
    </div>

    <!-- Контент поверх -->
    <div class="docs-wrapper">
      <div class="docs-layout">
        <!-- ЛЕВАЯ КОЛОНКА: Hero с фоном -->
        <section class="hero">
          <div class="logo-badge">
            <span class="badge-icon">📚</span>
            Documentation & Glossary
          </div>
          <h1 class="hero-title">
            Полная <span>документация</span> платформы
          </h1>

          <div class="subtitle-frame">
            <p class="hero-subtitle">
              Руководства, глоссарий терминов, описание архитектуры и математические модели Stochastic Dashboard v1.
            </p>
          </div>

          <div class="hero-actions">
            <router-link to="/dashboard" class="btn primary">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                <polyline points="13 2 13 9 20 9"></polyline>
              </svg>
              К платформе
            </router-link>
            <button class="btn ghost" @click="scrollToContent">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              К контенту
            </button>
          </div>
        </section>

        <!-- ПРАВАЯ КОЛОНКА: Разделы со скроллом -->
        <section class="tool-grid-wrapper">
          <div class="tool-grid">
            <div class="tools-header">
              <h2 class="tools-title">Разделы документации</h2>
            </div>

            <div class="tools-grid">
              <!-- 1. Overview -->
              <button 
                class="tool-card"
                :class="{ active: activeSection === 'overview' }"
                @click="setActiveSection('overview')"
              >
                <div class="tool-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">Обзор платформы</div>
                  <div class="tool-desc">
                    Целевые пользователи, функции, технологический стек
                  </div>
                </div>
              </button>

              <!-- 2. Architecture -->
              <button 
                class="tool-card"
                :class="{ active: activeSection === 'architecture' }"
                @click="setActiveSection('architecture')"
              >
                <div class="tool-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="7" height="7"></rect>
                    <rect x="14" y="3" width="7" height="7"></rect>
                    <rect x="14" y="14" width="7" height="7"></rect>
                    <rect x="3" y="14" width="7" height="7"></rect>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">Архитектура системы</div>
                  <div class="tool-desc">
                    Структура интерфейса, модули, компоненты и навигация
                  </div>
                </div>
              </button>

              <!-- 3. Pages -->
              <button 
                class="tool-card"
                :class="{ active: activeSection === 'pages' }"
                @click="setActiveSection('pages')"
              >
                <div class="tool-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">Страницы приложения</div>
                  <div class="tool-desc">
                    30+ страниц с подробным описанием функционала и методики
                  </div>
                </div>
              </button>

              <!-- 4. Glossary -->
              <button 
                class="tool-card"
                :class="{ active: activeSection === 'glossary' }"
                @click="setActiveSection('glossary')"
              >
                <div class="tool-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 3H4a2 2 0 0 0-2 2v14c0 1.1.9 2 2 2h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-6"></path>
                    <path d="M14 3v4"></path>
                    <path d="M10 12h4"></path>
                    <path d="M10 16h4"></path>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">Глоссарий терминов</div>
                  <div class="tool-desc">
                    40+ определений по портфелям, облигациям, опциям и HMM
                  </div>
                </div>
              </button>

              <!-- 5. Models -->
              <button 
                class="tool-card"
                :class="{ active: activeSection === 'models' }"
                @click="setActiveSection('models')"
              >
                <div class="tool-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="12 3 20 7.5 20 16.5 12 21 4 16.5 4 7.5 12 3"></polyline>
                    <line x1="12" y1="12" x2="20" y2="7.5"></line>
                    <line x1="12" y1="12" x2="12" y2="21"></line>
                    <line x1="12" y1="12" x2="4" y2="7.5"></line>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">Математические модели</div>
                  <div class="tool-desc">
                    VaR/ES, BSM, Heston, Lévy, HMM, DCF, формулы и примеры
                  </div>
                </div>
              </button>

              <!-- 6. API Reference -->
              <button 
                class="tool-card coming-soon"
                :class="{ active: activeSection === 'api' }"
                @click="setActiveSection('api')"
              >
                <div class="tool-icon soon-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="16 18 22 12 16 6"></polyline>
                    <polyline points="8 6 2 12 8 18"></polyline>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">REST API Reference</div>
                  <div class="tool-desc">
                    Endpoints, методы, примеры запросов и ответов
                  </div>
                  <div class="tool-tag">Soon</div>
                </div>
              </button>
            </div>
          </div>
        </section>
      </div>

      <!-- КОНТЕНТ ВНИЗУ -->
      <div class="docs-content" ref="contentRef">
        <div class="content-container">
          <!-- Overview -->
          <section v-if="activeSection === 'overview'" class="content-section">
            <h2>Обзор платформы Stochastic Dashboard</h2>
            <p>
              Stochastic Dashboard v1 — комплексная веб-платформа для количественного анализа финансовых инструментов, управления портфельным риском и ценообразования деривативов на базе стохастических моделей.
            </p>
            
            <h3>Целевые пользователи</h3>
            <ul>
              <li>Риск-менеджеры и аналитики</li>
              <li>Портфельные менеджеры и трейдеры</li>
              <li>Структурщики и квантовые исследователи</li>
              <li>Риск-комитеты и регуляторные отделы</li>
            </ul>

            <h3>Основные функции</h3>
            <ul>
              <li>Портфельный анализ (VaR, ES, Sharpe)</li>
              <li>HMM рыночные режимы</li>
              <li>Ценообразование деривативов (BSM, Heston, Lévy)</li>
              <li>DCF оценка облигаций</li>
              <li>Стресс-тестирование</li>
            </ul>
          </section>

          <!-- Architecture -->
          <section v-if="activeSection === 'architecture'" class="content-section">
            <h2>Архитектура платформы</h2>
            <p>
              Стандартная структура навигации и компонентов для всех страниц платформы.
            </p>

            <h3>Основные элементы интерфейса</h3>
            <ul>
              <li><strong>Верхняя панель:</strong> Логотип, поиск (⌘K), API статус, уведомления, профиль</li>
              <li><strong>Левый сайдбар:</strong> Иерархия модулей (PORTFOLIO, HMM, FIXED INCOME, PRICING, VALUATION, ANALYTICS)</li>
              <li><strong>Контент-зона:</strong> Данные, таблицы, графики, параметры управления</li>
              <li><strong>API статус:</strong> Индикаторы: API Live / Ping X ms</li>
            </ul>

            <h3>Модули платформы</h3>
            <ul>
              <li><strong>PORTFOLIO:</strong> Управление портфелем активов (оптимизация, анализ, отчёты)</li>
              <li><strong>HMM:</strong> Анализ рыночных режимов скрытых Марковских цепей</li>
              <li><strong>FIXED INCOME:</strong> Анализ облигаций (справедливая стоимость, кривые доходности)</li>
              <li><strong>PRICING:</strong> Ценообразование опционов (BSM, Heston, Lévy, FFT)</li>
              <li><strong>VALUATION:</strong> Оценка свопов и форвардов (DCF, Greeks)</li>
              <li><strong>ANALYTICS:</strong> Аналитика и отчётность (P&L, хеджирование)</li>
            </ul>
          </section>

          <!-- Pages -->
          <section v-if="activeSection === 'pages'" class="content-section">
            <h2>Страницы приложения</h2>
            <p>
              Платформа содержит 30+ специализированных страниц для анализа портфелей, управления рисками и ценообразования финансовых инструментов.
            </p>

            <h3>Портфельный анализ</h3>
            <ul>
              <li><strong>/portfolio</strong> — Портфельный анализ (доходность, VaR/ES, позиции)</li>
              <li><strong>/CCMVoptimization</strong> — CCMV оптимизация портфеля</li>
              <li><strong>/monte-carlo</strong> — Monte Carlo симуляция цен активов</li>
              <li><strong>/stress</strong> — Стресс-тестирование портфеля</li>
              <li><strong>/backtest</strong> — Бэктестинг Long/Short стратегий</li>
            </ul>

            <h3>Управление рисками</h3>
            <ul>
              <li><strong>/greeks</strong> — Risk Metrics (VaR, ES, чувствительность)</li>
              <li><strong>/reports</strong> — Генерация PDF отчётов</li>
              <li><strong>/stress/swaps</strong> — Стресс-тестирование портфеля свопов</li>
            </ul>

            <h3>Рыночные режимы</h3>
            <ul>
              <li><strong>/regimes</strong> — Анализ HMM (скрытые состояния, режимы)</li>
              <li><strong>/regime-details</strong> — Детальная аналитика (матрица переходов, прогноз)</li>
            </ul>

            <h3>Облигации</h3>
            <ul>
              <li><strong>/fixed-income</strong> — Анализ кривых доходности</li>
              <li><strong>/bond-valuation</strong> — DCF оценка облигаций</li>
              <li><strong>/zcyc-viewer</strong> — Просмотр кривой бескупонных доходностей</li>
            </ul>

            <h3>Опционы</h3>
            <ul>
              <li><strong>/pricing/options</strong> — Ценообразование опционов</li>
              <li><strong>/pricing/options/models</strong> — Сравнение моделей (BS, Heston, Lévy, FFT)</li>
              <li><strong>/pricing/options/greeks</strong> — Анализ Greeks (Δ, Γ, ν, Θ, ρ)</li>
              <li><strong>/pricing/options/portfolio</strong> — Анализ портфеля опционов</li>
            </ul>

            <h3>Свопы и форварды</h3>
            <ul>
              <li><strong>/valuation/swaps</strong> — DCF оценка IRS/CDS/Basis/CCS</li>
              <li><strong>/valuation/forwards</strong> — Оценка форвардов</li>
              <li><strong>/forwards/basis</strong> — Анализ спот-форвард базиса</li>
            </ul>
          </section>

          <!-- Glossary -->
          <section v-if="activeSection === 'glossary'" class="content-section">
            <h2 id="glossary">Глоссарий терминов</h2>
            
            <h3>Портфельные метрики</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>TOTAL P&L</dt>
                <dd>Совокупная доходность портфеля за выбранный период (% и абсолютное значение).</dd>
              </div>
              <div class="glossary-item">
                <dt>NAV</dt>
                <dd>Net Asset Value — текущая совокупная стоимость портфеля с учётом рыночной переоценки позиций.</dd>
              </div>
              <div class="glossary-item">
                <dt>VaR</dt>
                <dd>Value at Risk — оценка максимального ожидаемого убытка портфеля на заданном уровне доверия и горизонте.</dd>
              </div>
              <div class="glossary-item">
                <dt>ES / CVaR</dt>
                <dd>Expected Shortfall — средний убыток при сценариях, превышающих VaR на том же уровне доверия.</dd>
              </div>
              <div class="glossary-item">
                <dt>Sharpe Ratio</dt>
                <dd>Отношение избыточной доходности портфеля к его волатильности.</dd>
              </div>
              <div class="glossary-item">
                <dt>Max Drawdown</dt>
                <dd>Максимальная просадка портфеля от пика до минимума в рассматриваемом периоде.</dd>
              </div>
            </div>

            <h3>Облигационные метрики</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>DCF</dt>
                <dd>Discounted Cash Flow — оценка инструмента дисконтированием ожидаемых будущих денежных потоков.</dd>
              </div>
              <div class="glossary-item">
                <dt>Duration</dt>
                <dd>Взвешенный по PV срок до получения денежных потоков, чувствительность цены к сдвигу ставок.</dd>
              </div>
              <div class="glossary-item">
                <dt>DV01</dt>
                <dd>Dollar Value of 1 bp — изменение стоимости инструмента при сдвиге кривой на 1 basis point.</dd>
              </div>
              <div class="glossary-item">
                <dt>Convexity</dt>
                <dd>Вторая производная цены по ставке, уточняющая чувствительность при крупных сдвигах.</dd>
              </div>
            </div>

            <h3>Опционные метрики (Greeks)</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>Delta (Δ)</dt>
                <dd>Первая производная цены опциона по споту, оценивает изменение цены при сдвиге базового актива на 1 пункт.</dd>
              </div>
              <div class="glossary-item">
                <dt>Gamma (Γ)</dt>
                <dd>Вторая производная цены опциона по споту, риск дельты, чувствительность дельты к движениям спота.</dd>
              </div>
              <div class="glossary-item">
                <dt>Vega (ν)</dt>
                <dd>Производная цены опциона по волатильности, показывает P&L при изменении волатильности на 1%.</dd>
              </div>
              <div class="glossary-item">
                <dt>Theta (Θ)</dt>
                <dd>Производная цены опциона по времени, показывает временной распад опциона (time decay).</dd>
              </div>
              <div class="glossary-item">
                <dt>Rho (ρ)</dt>
                <dd>Производная цены опциона по процентной ставке, чувствительность к сдвигу кривой ставок.</dd>
              </div>
            </div>

            <h3>HMM и рыночные режимы</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>HMM</dt>
                <dd>Hidden Markov Model — стохастическая модель с невидимыми состояниями и наблюдаемыми доходностями.</dd>
              </div>
              <div class="glossary-item">
                <dt>Рыночные режимы</dt>
                <dd>Дискретные скрытые состояния (low vol, normal, high vol, crisis и т.п.), управляющие динамикой параметров.</dd>
              </div>
              <div class="glossary-item">
                <dt>Матрица переходов</dt>
                <dd>Матрица вероятностей перехода между режимами за один временной шаг.</dd>
              </div>
            </div>
          </section>

          <!-- Models -->
          <section v-if="activeSection === 'models'" class="content-section">
            <h2>Математические модели</h2>
            
            <div class="model-block">
              <h3>📊 VaR & Expected Shortfall</h3>
              <p>
                <strong>VaR (Value at Risk)</strong> — максимальный ожидаемый убыток портфеля на заданном уровне доверия (95%, 99%) и горизонте (1D, 10D).
              </p>
              <p>
                <strong>ES / CVaR</strong> — средний убыток при сценариях, превышающих VaR, более консервативная метрика tail-risk.
              </p>
            </div>

            <div class="model-block">
              <h3>📈 Black–Scholes–Merton</h3>
              <p>
                Классическая модель ценообразования европейских опционов на базе логнормального распределения доходностей.
                Параметры: S, K, r, σ, T, q.
              </p>
              <p>
                Greeks: Δ, Γ, ν, Θ, ρ — метрики чувствительности цены опциона.
              </p>
            </div>

            <div class="model-block">
              <h3>🔄 Heston Model</h3>
              <p>
                Модель со стохастической волатильностью, позволяющая моделировать улыбку волатильности (volatility smile).
              </p>
              <p>
                Параметры: V₀, κ (mean reversion), θ (long-term vol²), Σ_V (vol of vol), ρ (correlation S-V).
              </p>
            </div>

            <div class="model-block">
              <h3>🌊 Lévy Processes</h3>
              <p>
                Обобщённые стохастические процессы с толстыми хвостами (heavy tails) и скачками (jumps).
              </p>
              <p>
                Параметры: α (stability index), β (skewness), Σ (scale), μ (location).
              </p>
            </div>

            <div class="model-block">
              <h3>🔍 Hidden Markov Model (HMM)</h3>
              <p>
                Модель с невидимыми состояниями (регимы), управляющими динамикой наблюдаемых доходностей.
              </p>
              <p>
                Выходные данные: матрица переходов, стационарное распределение, ожидаемая длительность режимов.
              </p>
            </div>

            <div class="model-block">
              <h3>💰 DCF Bond Valuation</h3>
              <p>
                Дисконтирование денежных потоков облигации (купоны + номинал) по кривой доходностей.
              </p>
              <p>
                Выходные данные: Dirty Price, Clean Price, Дюрация, DV01, Выпуклость.
              </p>
            </div>
          </section>

          <!-- API (Coming Soon) -->
          <section v-if="activeSection === 'api'" class="content-section coming-soon-section">
            <h2>REST API Reference</h2>
            <p style="text-align: center; font-size: 18px; color: rgba(255, 255, 255, 0.6);">
              📋 Документация API скоро будет доступна
            </p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeSection = ref<string>('overview')
const contentRef = ref<HTMLElement | null>(null)

const setActiveSection = (section: string) => {
  activeSection.value = section
  // Плавная прокрутка к контенту
  setTimeout(() => {
    contentRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)
}

const scrollToContent = () => {
  contentRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<style scoped>
/* ============================================
   ROOT & LAYOUT
   ============================================ */
.docs-root {
  position: relative;
  min-height: 100vh;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  background: radial-gradient(circle at top, #050816 0%, #020308 45%, #000 100%);
  color: #f9fafb;
}

/* Красивый скроллбар по всей странице */
.docs-root::-webkit-scrollbar {
  width: 8px;
}

.docs-root::-webkit-scrollbar-track {
  background: transparent;
}

.docs-root::-webkit-scrollbar-thumb {
  background: rgba(34, 211, 238, 0.3);
  border-radius: 4px;
  border: 2px solid rgba(15, 23, 42, 0.6);
}

.docs-root::-webkit-scrollbar-thumb:hover {
  background: rgba(34, 211, 238, 0.5);
}

.docs-wrapper {
  position: relative;
  z-index: 1;
}

.docs-layout {
  position: relative;
  max-width: 1480px;
  margin: 0 auto;
  padding: 80px 40px 80px 40px;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 60px;
  align-items: flex-start;
}

/* ============================================
   LAVA LAMP BACKGROUND - везде
   ============================================ */
.lava-layer {
  position: fixed;
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
   HERO SECTION - С ФОНОВОЙ ПАНЕЛЬЮ
   ============================================ */
.hero {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 580px;
  padding: 32px;
  border-radius: 20px;
  backdrop-filter: blur(20px);
  background: rgba(15, 23, 42, 0.75);
  border: 1.5px solid rgba(34, 211, 238, 0.25);
  box-shadow: 
    0 0 40px rgba(34, 211, 238, 0.12),
    inset 0 1px 20px rgba(34, 211, 238, 0.08),
    0 20px 60px rgba(15, 23, 42, 0.8);
  position: sticky;
  top: 80px;
  height: fit-content;
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
  background: none;
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
   TOOLS GRID - СО СКРОЛЛОМ
   ============================================ */
.tool-grid-wrapper {
  position: sticky;
  top: 80px;
  height: fit-content;
  z-index: 5;
}

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
  overflow-y: visible;
  overflow-x: hidden;
}

/* Стилизованный скроллбар */
.tool-grid::-webkit-scrollbar {
  width: 8px;
}

.tool-grid::-webkit-scrollbar-track {
  background: transparent;
}

.tool-grid::-webkit-scrollbar-thumb {
  background: rgba(34, 211, 238, 0.3);
  border-radius: 4px;
  border: 2px solid rgba(15, 23, 42, 0.6);
}

.tool-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(34, 211, 238, 0.5);
}

.tools-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
  position: sticky;
  top: 0;
  background: rgba(15, 23, 42, 0.6);
  padding: 0 4px 12px 4px;
  z-index: 10;
}

.tools-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(209, 213, 219, 0.9);
  margin: 0;
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

.tool-card.active {
  border-color: rgba(34, 211, 238, 0.6);
  background: rgba(34, 211, 238, 0.15);
  color: #22d3ee;
}

.tool-card.coming-soon {
  opacity: 0.65;
}

.tool-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
  position: relative;
}

.tool-icon svg {
  position: relative;
  z-index: 2;
}

/* Суперновая анимация - основная волна */
.tool-icon::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0) 70%);
  animation: supernovaWave 2s ease-out infinite;
  z-index: 1;
}

/* Вторая волна с задержкой */
.tool-icon::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2), transparent 60%);
  animation: supernovaWave 2s ease-out infinite 0.6s;
  z-index: 0;
}

@keyframes supernovaWave {
  0% {
    transform: scale(0.3);
    opacity: 1;
  }
  100% {
    transform: scale(2.5);
    opacity: 0;
  }
}

.tool-icon.soon-icon {
  color: #f97316;
}

.tool-icon.soon-icon::before {
  background: radial-gradient(circle, rgba(249, 115, 22, 0.5), rgba(249, 115, 22, 0) 70%);
}

.tool-icon.soon-icon::after {
  background: radial-gradient(circle, rgba(249, 115, 22, 0.3), transparent 60%);
}

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

.tool-card.active .tool-name {
  color: #22d3ee;
}

html, body {
  overflow: auto !important;  /* на случай если глобальные стили блокируют */
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

/* ============================================
   CONTENT SECTION (внизу)
   ============================================ */
.docs-content {
  position: relative;
  z-index: 2;
  padding: 80px 40px;
  background: rgba(15, 23, 42, 0.5);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(34, 211, 238, 0.1);
  min-height: auto;
}

.content-container {
  max-width: 1000px;
  margin: 0 auto;
}

.content-section {
  grid-column: 1 / -1;  /* на всю ширину */
  padding: 40px;
  backdrop-filter: blur(20px);
  background: rgba(15, 23, 42, 0.75);
  border: 1.5px solid rgba(34, 211, 238, 0.25);
  border-radius: 20px;
  margin-top: 60px;
  /* Контент должен растягиваться */
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.content-section h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: #fff;
}

.content-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 32px 0 16px 0;
  color: #22d3ee;
}

.content-section p {
  font-size: 14px;
  color: rgba(226, 232, 240, 0.85);
  line-height: 1.7;
  margin: 0 0 16px 0;
}

.content-section ul {
  list-style: none;
  margin: 0 0 24px 0;
  padding: 0;
}

.content-section li {
  font-size: 14px;
  color: rgba(226, 232, 240, 0.8);
  line-height: 1.6;
  padding-left: 24px;
  position: relative;
  margin-bottom: 8px;
}

.content-section li::before {
  content: '◆';
  position: absolute;
  left: 0;
  color: #22d3ee;
  font-size: 10px;
}

.glossary-terms {
  display: grid;
  gap: 16px;
  margin-bottom: 32px;
}

.glossary-item {
  padding: 16px;
  background: rgba(34, 211, 238, 0.1);
  border-left: 3px solid rgba(34, 211, 238, 0.5);
  border-radius: 8px;
}

.glossary-item dt {
  font-size: 13px;
  font-weight: 600;
  color: #22d3ee;
  margin-bottom: 6px;
}

.glossary-item dd {
  font-size: 13px;
  color: rgba(226, 232, 240, 0.8);
  margin: 0;
  line-height: 1.6;
}

.model-block {
  padding: 24px;
  background: rgba(34, 211, 238, 0.08);
  border: 1px solid rgba(34, 211, 238, 0.2);
  border-radius: 12px;
  margin-bottom: 24px;
}

.model-block h3 {
  color: rgba(209, 213, 219, 0.9);
  margin-top: 0;
}

.model-block p {
  margin-bottom: 12px;
}

.model-block p:last-child {
  margin-bottom: 0;
}

.coming-soon-section {
  padding: 100px 40px;
  text-align: center;
}

/* ============================================
   ANIMATIONS
   ============================================ */
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
  .docs-layout {
    grid-template-columns: 1fr;
    gap: 48px;
    padding: 72px 32px 60px 32px;
    height: auto;
  }

  .hero {
    position: static;
    top: auto;
  }

  .tool-grid-wrapper {
    position: static;
    top: auto;
  }

  .tool-grid {
    max-height: none;
    overflow-y: visible;
  }
}

@media (max-width: 768px) {
  .docs-layout {
    padding: 64px 20px 40px 20px;
    gap: 36px;
    height: auto;
  }

  .hero {
    position: static;
    top: auto;
    padding: 24px;
  }

  .tool-grid {
    padding: 18px 14px;
    max-height: none;
  }

  .docs-content {
    padding: 60px 20px;
  }

  .content-section h2 {
    font-size: 20px;
  }

  .content-section h3 {
    font-size: 14px;
  }

  .content-section p {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .docs-layout {
    padding: 56px 16px 32px 16px;
    height: auto;
  }

  .hero {
    padding: 20px;
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
</style>