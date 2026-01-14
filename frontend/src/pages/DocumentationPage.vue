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
            <router-link to="/" class="btn primary">
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
                    VaR/ES, BSM, Heston, Lévy, HMM, DCF, формулы
                  </div>
                </div>
              </button>

              <!-- 6. Examples -->
              <button 
                class="tool-card"
                :class="{ active: activeSection === 'examples' }"
                @click="setActiveSection('examples')"
              >
                <div class="tool-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                </div>
                <div class="tool-body">
                  <div class="tool-name">Примеры расчетов</div>
                  <div class="tool-desc">
                    Практические примеры использования формул
                  </div>
                </div>
              </button>

              <!-- 7. API Reference -->
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
              <strong>Stochastic Dashboard v1</strong> — комплексная веб-платформа для количественного анализа финансовых инструментов, управления портфельным риском и ценообразования деривативов на базе стохастических моделей и современных методов машинного обучения.
            </p>
            
            <h3>Целевые пользователи</h3>
            <ul>
              <li><strong>Риск-менеджеры и аналитики</strong> — оценка и мониторинг рисков портфелей, расчет VaR/ES, стресс-тестирование</li>
              <li><strong>Портфельные менеджеры и трейдеры</strong> — оптимизация портфелей, анализ производительности, бэктестинг стратегий</li>
              <li><strong>Структурщики и квантовые исследователи</strong> — ценообразование сложных деривативов, анализ Greeks, моделирование волатильности</li>
              <li><strong>Риск-комитеты и регуляторные отделы</strong> — генерация отчетов, соответствие регуляторным требованиям, анализ стресс-сценариев</li>
              <li><strong>Аналитики облигаций</strong> — оценка справедливой стоимости, анализ кривых доходности, расчет Duration/DV01</li>
            </ul>

            <h3>Основные функции платформы</h3>
            <div class="features-grid">
              <div class="feature-card">
                <h4>Портфельный анализ</h4>
                <ul>
                  <li>Расчет VaR и Expected Shortfall (Historical, Parametric, Cornish-Fisher)</li>
                  <li>Анализ производительности (Sharpe, Sortino, Calmar Ratio)</li>
                  <li>Оптимизация портфеля (CCMV, Markowitz, Risk Parity)</li>
                  <li>Мониторинг позиций и P&L</li>
                  <li>Анализ корреляций и диверсификации</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>HMM рыночные режимы</h4>
                <ul>
                  <li>Идентификация скрытых рыночных режимов</li>
                  <li>Матрица переходов между режимами</li>
                  <li>Прогнозирование вероятностей режимов</li>
                  <li>Анализ длительности режимов</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>Ценообразование деривативов</h4>
                <ul>
                  <li>Black-Scholes-Merton модель</li>
                  <li>Heston стохастическая волатильность</li>
                  <li>Lévy процессы и FFT методы</li>
                  <li>Расчет всех Greeks (Δ, Γ, ν, Θ, ρ)</li>
                  <li>Поверхность волатильности (volatility surface)</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>Оценка облигаций</h4>
                <ul>
                  <li>DCF оценка (Discounted Cash Flow)</li>
                  <li>Расчет Duration, Modified Duration, DV01</li>
                  <li>Convexity анализ</li>
                  <li>Кривые доходности (Yield Curves, ZCYC)</li>
                  <li>Отчеты по облигациям (Vanilla, Floater)</li>
                  <li>Работа с реестрами (загрузка/выгрузка XLSX/XLSM)</li>
                  <li>Получение рыночной доходности из MOEX API</li>
                  <li>Сохранение реестров в формате Parquet</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>Свопы и форварды</h4>
                <ul>
                  <li>Оценка процентных свопов (IRS)</li>
                  <li>Кредитные дефолтные свопы (CDS)</li>
                  <li>Валютные свопы (CCS)</li>
                  <li>Оценка форвардов и анализ базисов</li>
                  <li>Работа с реестрами (загрузка/выгрузка XLSX)</li>
                  <li>Сохранение реестров в формате Parquet</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>Управление рисками</h4>
                <ul>
                  <li>Стресс-тестирование портфелей</li>
                  <li>Monte Carlo симуляции</li>
                  <li>Атрибуция P&L</li>
                  <li>Хеджирование позиций</li>
                  <li>Генерация PDF отчетов</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>Рыночные данные</h4>
                <ul>
                  <li>Потоковые данные российского рынка</li>
                  <li>Индексы, акции, облигации, ПИФы</li>
                  <li>Количественный анализ (3D визуализации)</li>
                  <li>Manifold learning и анализ ликвидности</li>
                </ul>
              </div>
              <div class="feature-card">
                <h4>Вспомогательные инструменты</h4>
                <ul>
                  <li>Бэктестинг стратегий</li>
                  <li>Помощник по хеджированию</li>
                  <li>Работа с реестрами и экспорт данных</li>
                </ul>
              </div>
            </div>

            <h3>Технологический стек</h3>
            <ul>
              <li><strong>Frontend:</strong> Vue.js 3, TypeScript, Chart.js, D3.js, Three.js, Plotly.js</li>
              <li><strong>Стилизация:</strong> Tailwind CSS, кастомные CSS переменные, Apple Vision Pro "Glass" дизайн</li>
              <li><strong>Математические библиотеки:</strong> Собственные реализации BSM, Heston, Monte Carlo, HMM</li>
              <li><strong>Визуализация:</strong> 3D графики (Three.js), интерактивные графики (Chart.js, D3.js), поверхности (Plotly.js)</li>
            </ul>

            <h3>Ключевые особенности</h3>
            <ul>
              <li><strong>Реальное время:</strong> Обновление данных и расчетов в реальном времени</li>
              <li><strong>Интерактивность:</strong> Интерактивные графики, детальная информация по клику</li>
              <li><strong>Профессиональные отчеты:</strong> Генерация PDF отчетов с графиками и таблицами</li>
              <li><strong>Адаптивный дизайн:</strong> Оптимизация для мобильных устройств и планшетов</li>
              <li><strong>Расширяемость:</strong> Модульная архитектура, легко добавлять новые функции</li>
            </ul>
          </section>

          <!-- Architecture -->
          <section v-if="activeSection === 'architecture'" class="content-section">
            <h2>Архитектура платформы</h2>
            <p>
              Stochastic Dashboard построен на модульной архитектуре с четким разделением функциональности и единообразным интерфейсом для всех страниц.
            </p>

            <h3>Основные элементы интерфейса</h3>
            <div class="architecture-block">
              <h4>Верхняя панель (Header)</h4>
              <ul>
                <li><strong>Логотип и навигация:</strong> Переход на главную страницу, поиск по платформе</li>
                <li><strong>Поиск (⌘K):</strong> Быстрый поиск страниц, инструментов, активов</li>
                <li><strong>API статус:</strong> Индикатор подключения к API (API Live / Ping X ms)</li>
                <li><strong>Уведомления:</strong> Системные уведомления и алерты</li>
                <li><strong>Профиль пользователя:</strong> Настройки, выход из системы</li>
            </ul>
            </div>

            <div class="architecture-block">
              <h4>Левый сайдбар (Sidebar)</h4>
              <p>Иерархическая структура модулей с группировкой по функциональности:</p>
              <ul>
                <li><strong>PORTFOLIO:</strong> Управление портфелем, оптимизация, анализ производительности</li>
                <li><strong>HMM:</strong> Анализ рыночных режимов, матрица переходов, прогнозирование</li>
                <li><strong>FIXED INCOME:</strong> Оценка облигаций, кривые доходности, отчеты</li>
                <li><strong>PRICING:</strong> Ценообразование опционов, сравнение моделей, Greeks</li>
                <li><strong>VALUATION:</strong> Оценка свопов, форвардов, базисов</li>
                <li><strong>ANALYTICS:</strong> Аналитика, P&L атрибуция, хеджирование, отчеты</li>
                <li><strong>DATA:</strong> Рыночные данные, количественный анализ</li>
              </ul>
            </div>

            <div class="architecture-block">
              <h4>Контент-зона (Main Content)</h4>
              <p>Стандартная структура страниц:</p>
              <ul>
                <li><strong>Заголовок секции:</strong> Название страницы, подзаголовок, кнопки действий</li>
                <li><strong>KPI карточки:</strong> Ключевые метрики в виде карточек с визуальными индикаторами</li>
                <li><strong>Параметры управления:</strong> Формы ввода, слайдеры, селекторы</li>
                <li><strong>Графики и визуализации:</strong> Интерактивные графики, 3D поверхности, тепловые карты</li>
                <li><strong>Таблицы данных:</strong> Детальная информация в табличном виде</li>
                <li><strong>Результаты расчетов:</strong> Отформатированные числовые результаты</li>
              </ul>
            </div>

            <h3>Модули платформы</h3>
            
            <div class="module-detail">
              <h4>PORTFOLIO — Управление портфелем</h4>
              <p><strong>Страницы:</strong> /portfolio, /CCMVoptimization, /monte-carlo, /stress, /backtest</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>Мониторинг позиций и P&L в реальном времени</li>
                <li>Расчет рисков (VaR, ES, Beta, Sharpe)</li>
                <li>Оптимизация весов активов</li>
                <li>Monte Carlo симуляции</li>
                <li>Стресс-тестирование</li>
                <li>Бэктестинг стратегий</li>
            </ul>
            </div>

            <div class="module-detail">
              <h4>HMM — Рыночные режимы</h4>
              <p><strong>Страницы:</strong> /regimes, /regime-details</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>Идентификация скрытых рыночных режимов</li>
                <li>Обучение HMM модели на исторических данных</li>
                <li>Визуализация режимов на временной шкале</li>
                <li>Анализ матрицы переходов</li>
                <li>Прогнозирование вероятностей режимов</li>
              </ul>
            </div>

            <div class="module-detail">
              <h4>FIXED INCOME — Облигации</h4>
              <p><strong>Страницы:</strong> /bond-valuation, /vanila-bond-report, /floater-bond-report, /fixed-income, /zcyc-viewer</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>DCF оценка облигаций</li>
                <li>Расчет Duration, DV01, Convexity</li>
                <li>Анализ кривых доходности</li>
                <li>Генерация отчетов по облигациям</li>
                <li>Сравнение с индексами</li>
            </ul>
            </div>

            <div class="module-detail">
              <h4>PRICING — Ценообразование опционов</h4>
              <p><strong>Страницы:</strong> /pricing/options, /pricing/options/models, /pricing/options/greeks, /pricing/options/portfolio, /volatility-surface</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>Расчет цены опционов (BSM, Heston, Lévy)</li>
                <li>Анализ всех Greeks</li>
                <li>Сравнение моделей</li>
                <li>Поверхность волатильности</li>
                <li>Анализ портфеля опционов</li>
            </ul>
            </div>

            <div class="module-detail">
              <h4>VALUATION — Оценка свопов и форвардов</h4>
              <p><strong>Страницы:</strong> /valuation/swaps, /valuation/forwards, /forwards/basis, /forwards/greeks</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>Оценка процентных свопов (IRS)</li>
                <li>Кредитные дефолтные свопы (CDS)</li>
                <li>Валютные свопы (CCS)</li>
                <li>Оценка форвардов</li>
                <li>Анализ базисов</li>
            </ul>
            </div>

            <div class="module-detail">
              <h4>ANALYTICS — Аналитика</h4>
              <p><strong>Страницы:</strong> /greeks, /reports, /pnl-attribution, /hedging-assistant, /stress/swaps</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>Комплексный анализ рисков</li>
                <li>Генерация PDF отчетов</li>
                <li>Атрибуция P&L</li>
                <li>Помощник по хеджированию</li>
                <li>Стресс-тестирование свопов</li>
            </ul>
            </div>

            <div class="module-detail">
              <h4>TERMINAL — Терминал</h4>
              <p><strong>Страницы:</strong> /terminal</p>
              <p><strong>Функции:</strong></p>
              <ul>
                <li>Потоковые данные российского рынка</li>
                <li>Индексы, акции, облигации, ПИФы</li>
                <li>Количественный анализ (3D визуализации)</li>
                <li>Manifold learning и анализ ликвидности</li>
                <li>Детальная информация по активам</li>
            </ul>
            </div>

            <h3>Дизайн-система</h3>
            <p>
              Платформа использует единую дизайн-систему "Apple Liquid Glass" с прозрачными стеклянными панелями, размытием фона и современной типографикой.
            </p>
            <ul>
              <li><strong>Цветовая палитра:</strong> Темная тема с акцентами (cyan, green, orange, red)</li>
              <li><strong>Типографика:</strong> SF Pro / Inter для основного текста, SF Mono для числовых данных</li>
              <li><strong>Компоненты:</strong> Glass cards, glass panels, glass inputs, glass pills</li>
              <li><strong>Анимации:</strong> Плавные переходы, hover эффекты, пульсирующие индикаторы</li>
              <li><strong>Адаптивность:</strong> Оптимизация для мобильных устройств и планшетов</li>
            </ul>

            <h3>Навигация</h3>
            <ul>
              <li><strong>Главная страница (/):</strong> Обзор платформы, быстрый доступ к основным функциям</li>
              <li><strong>Документация (/docs):</strong> Полная документация по платформе</li>
              <li><strong>Настройки (/settings):</strong> Конфигурация моделей и параметров</li>
            </ul>
          </section>

          <!-- Pages -->
          <section v-if="activeSection === 'pages'" class="content-section">
            <h2>Страницы приложения и инструкции по использованию</h2>
            <p>
              Платформа содержит 30+ специализированных страниц для анализа портфелей, управления рисками и ценообразования финансовых инструментов. Ниже приведено подробное описание каждой страницы с инструкциями по использованию.
            </p>

            <h3>Портфельный анализ</h3>
            
            <div class="page-detail-block">
              <h4>/portfolio — Управление портфелем</h4>
              <p><strong>Назначение:</strong> Комплексный анализ портфеля активов с расчетом доходности, рисков и визуализацией позиций.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Просмотрите KPI карточки: Total P&L, VaR 95%, Sharpe Ratio, Diversification</li>
                <li>Изучите графики: WAVE_σ.9 Momentum-Volatility Surface, Latent Volatility Surface</li>
                <li>Проверьте вкладки метрик: Performance, Risk, Stats</li>
                <li>Используйте кнопку "Пересчитать" для обновления данных</li>
                <li>Экспортируйте отчет в PDF через кнопку "Экспорт PDF"</li>
              </ol>
              <p><strong>Ключевые метрики:</strong> NAV, Total P&L, VaR, ES, Sharpe Ratio, Max Drawdown, Correlation</p>
            </div>

            <div class="page-detail-block">
              <h4>/CCMVoptimization — Оптимизация портфеля (CCMV)</h4>
              <p><strong>Назначение:</strong> Оптимизация весов активов в портфеле по модели Constant Correlation Matrix.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите активы для включения в портфель</li>
                <li>Установите целевую доходность или максимальный риск</li>
                <li>Нажмите "Оптимизировать" для расчета оптимальных весов</li>
                <li>Просмотрите эффективную границу (Efficient Frontier)</li>
                <li>Сравните текущий и оптимальный портфели</li>
              </ol>
              <p><strong>Выходные данные:</strong> Оптимальные веса активов, ожидаемая доходность, волатильность портфеля</p>
            </div>

            <div class="page-detail-block">
              <h4>/monte-carlo — Симуляция Монте-Карло</h4>
              <p><strong>Назначение:</strong> Генерация стохастических сценариев цен активов по модели Geometric Brownian Motion.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Введите параметры модели: Начальная цена (S₀), Волатильность (σ), Доходность (μ)</li>
                <li>Установите временной горизонт (Дней) и количество путей (N)</li>
                <li>Нажмите "Запустить симуляцию"</li>
                <li>Изучите график распределения цен и статистику (мин, макс, медиана, квантили)</li>
                <li>Используйте результаты для оценки вероятности достижения целевой цены</li>
              </ol>
              <p><strong>Параметры модели:</strong> S₀ — начальная цена, σ — волатильность (%), μ — дрейф (%), T — период (дни), N — количество сценариев</p>
            </div>

            <div class="page-detail-block">
              <h4>/stress — Стресс-тестирование портфеля</h4>
              <p><strong>Назначение:</strong> Оценка влияния стрессовых сценариев на портфель (шоки цен, волатильности, корреляций).</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите тип стресс-сценария (ценовой шок, волатильность, корреляция)</li>
                <li>Установите параметры шока (процент изменения)</li>
                <li>Запустите расчет стресс-теста</li>
                <li>Просмотрите изменение P&L, VaR, позиций</li>
                <li>Экспортируйте отчет о стресс-тестировании</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/backtest — Бэктестинг стратегий</h4>
              <p><strong>Назначение:</strong> Тестирование торговых стратегий на исторических данных.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите стратегию (Long/Short, Market Neutral, Momentum)</li>
                <li>Установите параметры стратегии (период удержания, фильтры входа/выхода)</li>
                <li>Выберите исторический период для тестирования</li>
                <li>Запустите бэктест</li>
                <li>Изучите метрики производительности: Total Return, Sharpe, Max DD, Win Rate</li>
              </ol>
            </div>

            <h3>Управление рисками</h3>

            <div class="page-detail-block">
              <h4>/greeks — Risk Metrics</h4>
              <p><strong>Назначение:</strong> Комплексный анализ рисков портфеля с расчетом VaR, ES и чувствительностей.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите уровень доверия для VaR (95%, 99%)</li>
                <li>Установите временной горизонт (1D, 10D, 30D)</li>
                <li>Просмотрите KPI: VaR, Expected Shortfall, Бета портфеля, Sharpe Ratio</li>
                <li>Изучите матрицу чувствительности к факторам риска</li>
                <li>Проверьте распределение P&L и tail risk</li>
              </ol>
              <p><strong>Метрики:</strong> VaR (Historical/Parametric), ES (CVaR), Beta, Sharpe, Sortino, Correlation Matrix</p>
            </div>

            <div class="page-detail-block">
              <h4>/reports — Генерация PDF отчётов</h4>
              <p><strong>Назначение:</strong> Создание профессиональных PDF отчетов по портфелю, рискам и производительности.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите тип отчета (Portfolio Summary, Risk Report, Performance Analysis)</li>
                <li>Настройте параметры отчета (период, уровень детализации)</li>
                <li>Выберите разделы для включения</li>
                <li>Нажмите "Сгенерировать PDF"</li>
                <li>Скачайте готовый отчет</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/stress/swaps — Стресс-тестирование свопов</h4>
              <p><strong>Назначение:</strong> Оценка влияния стрессовых сценариев на портфель процентных и кредитных свопов.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите портфель свопов для анализа</li>
                <li>Установите стресс-сценарии (параллельный сдвиг кривой, изменение спредов)</li>
                <li>Запустите расчет</li>
                <li>Просмотрите изменение стоимости и P&L по каждому свопу</li>
              </ol>
            </div>

            <h3>Рыночные режимы (HMM)</h3>

            <div class="page-detail-block">
              <h4>/regimes — Анализ HMM режимов</h4>
              <p><strong>Назначение:</strong> Идентификация скрытых рыночных режимов (low vol, normal, high vol, crisis) с помощью Hidden Markov Model.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите актив или индекс для анализа</li>
                <li>Установите количество режимов (обычно 3-5)</li>
                <li>Запустите обучение HMM модели</li>
                <li>Просмотрите идентифицированные режимы на временной шкале</li>
                <li>Изучите параметры каждого режима (средняя доходность, волатильность)</li>
              </ol>
              <p><strong>Выходные данные:</strong> Идентифицированные режимы, матрица переходов, стационарное распределение, параметры режимов</p>
            </div>

            <div class="page-detail-block">
              <h4>/regime-details — Детальная аналитика режимов</h4>
              <p><strong>Назначение:</strong> Глубокий анализ HMM режимов с матрицей переходов, прогнозами и статистикой.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Изучите матрицу переходов между режимами</li>
                <li>Просмотрите ожидаемую длительность каждого режима</li>
                <li>Проверьте прогноз вероятностей режимов на следующий период</li>
                <li>Анализируйте историческую статистику по каждому режиму</li>
              </ol>
            </div>

            <h3>Облигации (Fixed Income)</h3>

            <div class="page-detail-block">
              <h4>/bond-valuation — DCF оценка облигаций</h4>
              <p><strong>Назначение:</strong> Расчет справедливой стоимости облигации методом дисконтирования денежных потоков.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Введите ISIN облигации или выберите из списка</li>
                <li>Установите дату оценки</li>
                <li>Выберите режим работы: два сценария или рыночная доходность из MOEX</li>
                <li>Для режима двух сценариев: введите ставки дисконтирования для двух сценариев (базовый и стрессовый)</li>
                <li>Для режима рыночной доходности: включите флажок "Использовать доходность из MOEX API" и нажмите "Загрузить из MOEX" или введите вручную</li>
                <li>Загрузите реестр облигаций через кнопку "Загрузить Excel" (формат XLSX или XLSM)</li>
                <li>Нажмите "Рассчитать все" для оценки всех облигаций в реестре</li>
                <li>Просмотрите результаты: Dirty Price, Clean Price, Duration, DV01, Convexity</li>
                <li>Экспортируйте результаты в Excel через кнопку "Выгрузить Excel"</li>
                <li>Сохраните реестр в Parquet через кнопку "Сохранить в DB (Parquet)"</li>
                <li>Изучите таблицу денежных потоков с дисконт-факторами</li>
              </ol>
              <p><strong>Выходные данные:</strong> Dirty/Clean Price, Macaulay/Modified Duration, DV01, Convexity, Cash Flows Schedule</p>
              <p><strong>Работа с реестрами:</strong> Поддерживается загрузка реестров в формате XLSX и XLSM. Реестр должен содержать колонки: ISIN, Дата оценки, Y аналога (%), Y индекса (%), Рыночная доходность (%), Активность рынка, Базис расчета.</p>
            </div>

            <div class="page-detail-block">
              <h4>/vanila-bond-report — Отчет по ванильной облигации</h4>
              <p><strong>Назначение:</strong> Комплексный отчет по ванильной облигации с графиками, метриками и сравнением с индексами.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Введите ISIN облигации</li>
                <li>Просмотрите блоки: Котировка и доходность, Риск-метрики, Активность рынка</li>
                <li>Изучите график сравнения с индексами (наведите курсор для деталей)</li>
                <li>Проверьте историю котировок на scatter plot (красная точка — основная облигация)</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/floater-bond-report — Отчет по плавающей облигации</h4>
              <p><strong>Назначение:</strong> Анализ облигации с плавающей купонной ставкой (floater).</p>
              <p><strong>Как использовать:</strong> Аналогично ванильной облигации, но с учетом специфики плавающей ставки.</p>
            </div>

            <div class="page-detail-block">
              <h4>/fixed-income — Анализ кривых доходности</h4>
              <p><strong>Назначение:</strong> Визуализация и анализ кривых доходности (yield curves) для различных классов облигаций.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите тип кривой (государственные, корпоративные, по срокам)</li>
                <li>Просмотрите график кривой доходности</li>
                <li>Сравните кривые на разные даты</li>
                <li>Анализируйте спреды между кривыми</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/zcyc-viewer — Кривая бескупонных доходностей</h4>
              <p><strong>Назначение:</strong> Просмотр и анализ кривой бескупонных доходностей (Zero-Coupon Yield Curve, ZCYC).</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите дату для отображения кривой</li>
                <li>Просмотрите график ZCYC</li>
                <li>Изучите таблицу ставок по срокам</li>
                <li>Сравните кривые на разные даты</li>
              </ol>
            </div>

            <h3>Опционы (Options Pricing)</h3>

            <div class="page-detail-block">
              <h4>/pricing/options — Ценообразование опционов</h4>
              <p><strong>Назначение:</strong> Расчет справедливой стоимости опциона по модели Black-Scholes-Merton и анализ Greeks.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Введите параметры опциона: Spot (S), Strike (K), Волатильность (σ), Безрисковая ставка (r), Время до экспирации (T), Дивидендная доходность (q)</li>
                <li>Выберите тип опциона (Call/Put)</li>
                <li>Выберите модель (BSM, Heston, Lévy)</li>
                <li>Нажмите "Рассчитать"</li>
                <li>Просмотрите результаты: Цена опциона, Intrinsic Value, Time Value, все Greeks (Δ, Γ, ν, Θ, ρ)</li>
                <li>Изучите матрицу чувствительности к изменениям спота и волатильности</li>
                <li>Проверьте график Payoff функции</li>
              </ol>
              <p><strong>Параметры:</strong> S — текущая цена актива, K — страйк, σ — волатильность (%), r — безрисковая ставка (%), T — время до экспирации (годы), q — дивидендная доходность (%)</p>
            </div>

            <div class="page-detail-block">
              <h4>/pricing/options/models — Сравнение моделей</h4>
              <p><strong>Назначение:</strong> Сравнение цен опционов, рассчитанных по различным моделям (BSM, Heston, Lévy, FFT).</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Введите базовые параметры опциона</li>
                <li>Настройте параметры для каждой модели (если требуется)</li>
                <li>Запустите расчет по всем моделям</li>
                <li>Сравните цены Call и Put опционов</li>
                <li>Изучите различия в Greeks между моделями</li>
                <li>Проанализируйте, какая модель лучше подходит для вашего случая</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/pricing/options/greeks — Анализ Greeks</h4>
              <p><strong>Назначение:</strong> Детальный анализ чувствительностей опциона (Greeks) и их влияния на P&L.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Введите параметры опциона</li>
                <li>Просмотрите значения всех Greeks: Delta, Gamma, Vega, Theta, Rho</li>
                <li>Изучите матрицу чувствительности (изменение цены при изменении спота и волатильности)</li>
                <li>Проверьте P&L разложение по компонентам Greeks</li>
                <li>Используйте для планирования хеджирования</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/pricing/options/portfolio — Портфель опционов</h4>
              <p><strong>Назначение:</strong> Анализ портфеля опционов с агрегированными рисками и Greeks.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Добавьте опционы в портфель (введите параметры каждого)</li>
                <li>Просмотрите агрегированные Greeks портфеля</li>
                <li>Проверьте общий P&L и риски</li>
                <li>Изучите распределение позиций по страйкам и экспирациям</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/volatility-surface — Поверхность волатильности</h4>
              <p><strong>Назначение:</strong> Визуализация 3D поверхности волатильности (implied volatility) по страйкам и экспирациям.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите базовый актив</li>
                <li>Просмотрите 3D график поверхности волатильности</li>
                <li>Изучите "улыбку волатильности" (volatility smile) и "наклон" (skew)</li>
                <li>Используйте для выявления арбитражных возможностей</li>
              </ol>
            </div>

            <h3>Свопы и форварды</h3>

            <div class="page-detail-block">
              <h4>/valuation/swaps — Оценка свопов</h4>
              <p><strong>Назначение:</strong> Расчет справедливой стоимости процентных (IRS), кредитных (CDS), базисных (Basis) и валютных (CCS) свопов.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите тип свопа (IRS, CDS, Basis, CCS)</li>
                <li>Введите параметры свопа: номинал, фиксированная/плавающая ставка, даты платежей</li>
                <li>Выберите кривую дисконтирования</li>
                <li>Загрузите реестр свопов через кнопку "Загрузить Excel" (формат XLSX)</li>
                <li>Нажмите "Рассчитать все" для оценки всех свопов в реестре</li>
                <li>Рассчитайте справедливую стоимость</li>
                <li>Просмотрите денежные потоки и их приведенную стоимость</li>
                <li>Изучите Greeks свопа (DV01, Convexity)</li>
                <li>Экспортируйте результаты в Excel через кнопку "Выгрузить Excel"</li>
                <li>Сохраните реестр в Parquet через кнопку "Сохранить в DB (Parquet)"</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/valuation/forwards — Оценка форвардов</h4>
              <p><strong>Назначение:</strong> Расчет справедливой форвардной цены и стоимости форвардного контракта.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите тип форварда (FX, Bond, Commodity, Equity, Rate)</li>
                <li>Введите спотовую цену актива</li>
                <li>Установите безрисковую ставку и дивидендную доходность</li>
                <li>Введите время до экспирации форварда</li>
                <li>Загрузите реестр форвардов через кнопку "Загрузить Excel" (формат XLSX)</li>
                <li>Нажмите "Рассчитать все" для оценки всех форвардов в реестре</li>
                <li>Рассчитайте справедливую форвардную цену</li>
                <li>Сравните с рыночной форвардной ценой для выявления арбитража</li>
                <li>Экспортируйте результаты в Excel через кнопку "Выгрузить Excel"</li>
                <li>Сохраните реестр в Parquet через кнопку "Сохранить в DB (Parquet)"</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/forwards/basis — Анализ спот-форвард базиса</h4>
              <p><strong>Назначение:</strong> Анализ разницы между спотовой и форвардной ценой (basis) и выявление арбитражных возможностей.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите актив</li>
                <li>Просмотрите график базиса по времени</li>
                <li>Изучите факторы, влияющие на базис (стоимость хранения, дивиденды)</li>
                <li>Используйте для арбитражных стратегий</li>
              </ol>
            </div>

            <div class="page-detail-block">
              <h4>/forwards/greeks — Greeks форвардов</h4>
              <p><strong>Назначение:</strong> Анализ чувствительности форвардных контрактов к изменениям параметров.</p>
              <p><strong>Как использовать:</strong> Аналогично опционам, но для форвардов (Delta, Theta, Rho)</p>
            </div>

            <h3>Рыночные данные и аналитика</h3>

            <div class="page-detail-block">
              <h4>/terminal — Терминал</h4>
              <p><strong>Назначение:</strong> Потоковые рыночные данные российского финансового рынка с количественным анализом.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Просмотрите вкладки: "Обзор рынка", "Акции", "Облигации", "ПИФы", "Количественный анализ"</li>
                <li>Используйте поиск для быстрого нахождения актива по тикеру или ISIN</li>
                <li>Кликните на актив для просмотра детальной информации (график, стакан заявок)</li>
                <li>Во вкладке "Количественный анализ" изучите 3D визуализации ликвидности и волатильности</li>
                <li>Просмотрите дашборды: Quant Alpha Terminal, QuantLatent v9.2, Volatility Trading System</li>
              </ol>
              <p><strong>Функции:</strong> Поиск активов, детальная информация по активам, графики цен (линия/свечи), стакан заявок, количественный анализ</p>
            </div>

            <div class="page-detail-block">
              <h4>/yield-analysis — Анализ доходности</h4>
              <p><strong>Назначение:</strong> Анализ доходности различных классов активов и сравнение с бенчмарками.</p>
            </div>

            <div class="page-detail-block">
              <h4>/basis-analysis — Анализ базисов</h4>
              <p><strong>Назначение:</strong> Анализ базисов между различными инструментами и выявление арбитражных возможностей.</p>
            </div>

            <div class="page-detail-block">
              <h4>/forward-curve-builder — Построение форвардных кривых</h4>
              <p><strong>Назначение:</strong> Построение и анализ форвардных кривых для различных активов.</p>
            </div>

            <h3>Вспомогательные инструменты</h3>

            <div class="page-detail-block">
              <h4>/hedging-assistant — Помощник по хеджированию</h4>
              <p><strong>Назначение:</strong> Расчет оптимальных позиций для хеджирования портфеля.</p>
            </div>

            <div class="page-detail-block">
              <h4>/analytics/pnl — Атрибуция P&L</h4>
              <p><strong>Назначение:</strong> Разложение P&L портфеля по источникам (ценовые движения, волатильность, время, корреляции).</p>
            </div>

            <div class="page-detail-block">
              <h4>/settings — Настройки</h4>
              <p><strong>Назначение:</strong> Настройка параметров платформы, моделей расчета, валют, единиц измерения.</p>
              <p><strong>Как использовать:</strong></p>
              <ol>
                <li>Выберите модель оптимизации портфеля (Markowitz, Black-Litterman, Risk Parity, HRP)</li>
                <li>Выберите модель VaR (Historical, Parametric, Cornish-Fisher, GPD)</li>
                <li>Настройте валюту и единицы измерения</li>
                <li>Сохраните настройки</li>
              </ol>
            </div>
          </section>

          <!-- Glossary -->
          <section v-if="activeSection === 'glossary'" class="content-section">
            <h2 id="glossary">Глоссарий терминов</h2>
            
            <h3>Портфельные метрики и риск</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>TOTAL P&L</dt>
                <dd>Совокупная прибыль/убыток портфеля за выбранный период, выраженная в процентах и абсолютном значении. Включает реализованную и нереализованную прибыль.</dd>
              </div>
              <div class="glossary-item">
                <dt>NAV (Net Asset Value)</dt>
                <dd>Чистая стоимость активов — текущая совокупная стоимость портфеля с учётом рыночной переоценки всех позиций. NAV = Σ (Количество × Текущая цена) - Обязательства.</dd>
              </div>
              <div class="glossary-item">
                <dt>VaR (Value at Risk)</dt>
                <dd>Максимальный ожидаемый убыток портфеля на заданном уровне доверия (обычно 95% или 99%) и временном горизонте (1 день, 10 дней). Например, VaR 95% = -2.5% означает, что с вероятностью 95% убыток не превысит 2.5%.</dd>
              </div>
              <div class="glossary-item">
                <dt>ES / CVaR (Expected Shortfall / Conditional VaR)</dt>
                <dd>Средний убыток при сценариях, превышающих VaR на том же уровне доверия. Более консервативная метрика tail-risk, учитывающая экстремальные события.</dd>
              </div>
              <div class="glossary-item">
                <dt>Sharpe Ratio</dt>
                <dd>Отношение избыточной доходности портфеля (над безрисковой ставкой) к его волатильности. SR = (R<sub>p</sub> - R<sub>f</sub>) / σ<sub>p</sub>. Показывает доходность на единицу риска.</dd>
              </div>
              <div class="glossary-item">
                <dt>Sortino Ratio</dt>
                <dd>Аналогичен Sharpe Ratio, но учитывает только downside deviation (волатильность отрицательных доходностей). Более точная метрика для оценки управления рисками.</dd>
              </div>
              <div class="glossary-item">
                <dt>Max Drawdown</dt>
                <dd>Максимальная просадка портфеля от пика до минимума в рассматриваемом периоде. Показывает максимальный понесенный убыток от исторического максимума.</dd>
              </div>
              <div class="glossary-item">
                <dt>Calmar Ratio</dt>
                <dd>Отношение годовой доходности к максимальной просадке. Calmar = Annual Return / |Max Drawdown|. Показывает эффективность восстановления после просадок.</dd>
              </div>
              <div class="glossary-item">
                <dt>Beta (β)</dt>
                <dd>Мера чувствительности портфеля к движениям рынка (бенчмарка). β = 1 означает движение вместе с рынком, β > 1 — более волатильный, β < 1 — менее волатильный.</dd>
              </div>
              <div class="glossary-item">
                <dt>Correlation</dt>
                <dd>Мера линейной зависимости между доходностями двух активов. Значения от -1 до +1. +1 — полная положительная корреляция, -1 — полная отрицательная, 0 — отсутствие корреляции.</dd>
              </div>
              <div class="glossary-item">
                <dt>Diversification</dt>
                <dd>Снижение риска портфеля за счет включения некоррелированных активов. Измеряется коэффициентом диверсификации (1 - корреляция портфеля).</dd>
              </div>
            </div>

            <h3>Облигационные метрики</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>DCF (Discounted Cash Flow)</dt>
                <dd>Метод оценки справедливой стоимости инструмента дисконтированием ожидаемых будущих денежных потоков по соответствующей ставке дисконтирования.</dd>
              </div>
              <div class="glossary-item">
                <dt>Dirty Price</dt>
                <dd>Полная стоимость облигации, включающая накопленный купонный доход (Accrued Interest). Dirty Price = Clean Price + Accrued Interest.</dd>
              </div>
              <div class="glossary-item">
                <dt>Clean Price</dt>
                <dd>Котировочная цена облигации без учета накопленного купонного дохода. Цена, по которой облигация котируется на рынке.</dd>
              </div>
              <div class="glossary-item">
                <dt>Accrued Interest</dt>
                <dd>Накопленный купонный доход с момента последней выплаты купона до даты расчета. AI = Coupon × (Days since last coupon / Days in coupon period).</dd>
              </div>
              <div class="glossary-item">
                <dt>Duration (Macaulay Duration)</dt>
                <dd>Взвешенный по приведенной стоимости срок до получения денежных потоков. Показывает средний срок жизни облигации. D = Σ[tᵢ × PV(CFᵢ)] / P.</dd>
              </div>
              <div class="glossary-item">
                <dt>Modified Duration</dt>
                <dd>Модифицированная дюрация, показывающая процентное изменение цены при изменении доходности на 1%. D<sub>mod</sub> = D / (1 + y).</dd>
              </div>
              <div class="glossary-item">
                <dt>DV01 (Рублевая стоимость 1 базисного пункта)</dt>
                <dd>Изменение стоимости облигации в денежных единицах при сдвиге кривой доходности на 1 basis point (0.01%). DV01 = -P × D<sub>mod</sub> × 0.0001.</dd>
              </div>
              <div class="glossary-item">
                <dt>Convexity</dt>
                <dd>Вторая производная цены облигации по доходности. Уточняет оценку изменения цены при крупных сдвигах ставок, учитывая нелинейность зависимости. C = Σ[tᵢ(tᵢ + 1) × PV(CFᵢ)] / [P × (1 + y)²].</dd>
              </div>
              <div class="glossary-item">
                <dt>Yield to Maturity (YTM)</dt>
                <dd>Доходность к погашению — внутренняя норма доходности облигации при удержании до погашения. Ставка дисконтирования, при которой текущая стоимость денежных потоков равна цене облигации.</dd>
              </div>
              <div class="glossary-item">
                <dt>ZCYC (Zero-Coupon Yield Curve)</dt>
                <dd>Кривая бескупонных доходностей — кривая ставок дисконтирования для бескупонных облигаций различных сроков погашения. Основа для оценки всех облигаций.</dd>
              </div>
              <div class="glossary-item">
                <dt>Spread</dt>
                <dd>Разница между доходностью облигации и безрисковой ставкой (обычно ОФЗ). Измеряет кредитный риск и ликвидность. Spread = YTM<sub>bond</sub> - YTM<sub>risk-free</sub>.</dd>
              </div>
            </div>

            <h3>Опционные метрики (Greeks)</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>Delta (Δ)</dt>
                <dd>Первая производная цены опциона по спотовой цене базового актива. Показывает изменение цены опциона при изменении спота на 1 пункт. Для Call: Δ = e<sup>-qT</sup>N(d₁), для Put: Δ = -e<sup>-qT</sup>N(-d₁). Диапазон для Call: 0 до 1, для Put: -1 до 0.</dd>
              </div>
              <div class="glossary-item">
                <dt>Gamma (Γ)</dt>
                <dd>Вторая производная цены опциона по споту, или первая производная Delta. Показывает скорость изменения Delta при движении спота. Γ = e<sup>-qT</sup>n(d₁) / (Sσ√T). Максимальна для опционов "at-the-money".</dd>
              </div>
              <div class="glossary-item">
                <dt>Vega (ν)</dt>
                <dd>Производная цены опциона по волатильности. Показывает изменение цены опциона при изменении волатильности на 1 процентный пункт. ν = S₀e<sup>-qT</sup>n(d₁)√T / 100. Всегда положительна для длинных позиций.</dd>
              </div>
              <div class="glossary-item">
                <dt>Theta (Θ)</dt>
                <dd>Производная цены опциона по времени (временной распад). Показывает изменение цены опциона при уменьшении времени до экспирации на 1 день. Обычно отрицательна (опцион теряет стоимость со временем).</dd>
              </div>
              <div class="glossary-item">
                <dt>Rho (ρ)</dt>
                <dd>Производная цены опциона по безрисковой процентной ставке. Показывает изменение цены опциона при изменении ставки на 1 процентный пункт. Для Call: ρ = KTe<sup>-rT</sup>N(d₂) / 100, для Put: отрицательна.</dd>
              </div>
              <div class="glossary-item">
                <dt>Intrinsic Value</dt>
                <dd>Внутренняя стоимость опциона — разница между текущей ценой актива и страйком (для Call: max(S - K, 0), для Put: max(K - S, 0)). Минимальная стоимость опциона.</dd>
              </div>
              <div class="glossary-item">
                <dt>Time Value</dt>
                <dd>Временная стоимость опциона — разница между рыночной ценой опциона и его внутренней стоимостью. Time Value = Option Price - Intrinsic Value. Убывает по мере приближения к экспирации.</dd>
              </div>
              <div class="glossary-item">
                <dt>Moneyness</dt>
                <dd>Отношение текущей цены актива к страйку опциона. In-the-money (ITM): Call при S > K, Put при S < K. At-the-money (ATM): S ≈ K. Out-of-the-money (OTM): Call при S < K, Put при S > K.</dd>
              </div>
              <div class="glossary-item">
                <dt>Volatility Smile</dt>
                <dd>Явление, при котором подразумеваемая волатильность (implied volatility) варьируется в зависимости от страйка. График напоминает улыбку, отсюда название.</dd>
              </div>
            </div>

            <h3>HMM и рыночные режимы</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>HMM (Hidden Markov Model)</dt>
                <dd>Стохастическая модель с невидимыми состояниями (скрытые режимы) и наблюдаемыми доходностями. Каждое состояние характеризуется своими параметрами распределения (средняя, волатильность).</dd>
              </div>
              <div class="glossary-item">
                <dt>Рыночные режимы (Market Regimes)</dt>
                <dd>Дискретные скрытые состояния рынка (например: low volatility, normal, high volatility, crisis), управляющие динамикой наблюдаемых доходностей. Каждый режим имеет свои характеристики.</dd>
              </div>
              <div class="glossary-item">
                <dt>Матрица переходов (Transition Matrix)</dt>
                <dd>Матрица вероятностей перехода между режимами за один временной шаг. A<sub>ij</sub> = P(S<sub>t+1</sub> = j | S<sub>t</sub> = i). Сумма по строке равна 1.</dd>
              </div>
              <div class="glossary-item">
                <dt>Стационарное распределение (Stationary Distribution)</dt>
                <dd>Долгосрочное распределение вероятностей режимов, не изменяющееся со временем. Решение системы π = π × A. Показывает долю времени, проводимого в каждом режиме.</dd>
              </div>
              <div class="glossary-item">
                <dt>Ожидаемая длительность режима</dt>
                <dd>Среднее время пребывания в режиме перед переходом в другой. Рассчитывается как 1 / (1 - A<sub>ii</sub>), где A<sub>ii</sub> — вероятность остаться в режиме i.</dd>
              </div>
            </div>

            <h3>Стохастические модели</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>Geometric Brownian Motion (GBM)</dt>
                <dd>Стохастический процесс для моделирования цен активов: dS = μS dt + σS dW, где μ — дрейф, σ — волатильность, dW — винеровский процесс. Основа модели Black-Scholes.</dd>
              </div>
              <div class="glossary-item">
                <dt>Wiener Process (Brownian Motion)</dt>
                <dd>Случайный процесс с независимыми нормально распределенными приращениями. dW ~ N(0, dt). Основа стохастического исчисления.</dd>
              </div>
              <div class="glossary-item">
                <dt>Monte Carlo Simulation</dt>
                <dd>Метод численного моделирования, использующий случайные числа для генерации множества сценариев. Применяется для оценки сложных финансовых инструментов и портфелей.</dd>
              </div>
              <div class="glossary-item">
                <dt>Stochastic Volatility</dt>
                <dd>Модели, в которых волатильность сама является случайным процессом (например, Heston модель). Позволяют моделировать volatility smile и динамику волатильности.</dd>
              </div>
              <div class="glossary-item">
                <dt>Lévy Process</dt>
                <dd>Обобщённые стохастические процессы с толстыми хвостами (heavy tails) и скачками (jumps). Включают нормальное распределение как частный случай.</dd>
              </div>
            </div>

            <h3>Свопы и форварды</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>IRS (Interest Rate Swap)</dt>
                <dd>Процентный своп — соглашение об обмене фиксированной процентной ставки на плавающую (или наоборот) на определенный номинал в течение срока действия.</dd>
              </div>
              <div class="glossary-item">
                <dt>CDS (Credit Default Swap)</dt>
                <dd>Кредитный дефолтный своп — соглашение о защите от дефолта эмитента. Покупатель CDS платит премию и получает компенсацию при дефолте.</dd>
              </div>
              <div class="glossary-item">
                <dt>Basis Swap</dt>
                <dd>Базисный своп — обмен одной плавающей ставки на другую (например, LIBOR на EURIBOR) на одинаковый номинал.</dd>
              </div>
              <div class="glossary-item">
                <dt>CCS (Cross-Currency Swap)</dt>
                <dd>Валютный своп — обмен процентных платежей в одной валюте на платежи в другой валюте, часто с обменом номиналов в начале и конце.</dd>
              </div>
              <div class="glossary-item">
                <dt>Forward Price</dt>
                <dd>Справедливая форвардная цена актива: F = S₀ × e<sup>(r - q)T</sup>, где S₀ — спотовая цена, r — безрисковая ставка, q — дивидендная доходность, T — время до экспирации.</dd>
              </div>
              <div class="glossary-item">
                <dt>Basis</dt>
                <dd>Разница между спотовой и форвардной ценой. Basis = Spot - Forward. Может быть положительным (contango) или отрицательным (backwardation).</dd>
              </div>
            </div>

            <h3>Количественный анализ и визуализация</h3>
            <div class="glossary-terms">
              <div class="glossary-item">
                <dt>Manifold Learning</dt>
                <dd>Класс алгоритмов машинного обучения для обнаружения низкоразмерной структуры в высокоразмерных данных. Применяется для анализа рыночной микроструктуры.</dd>
              </div>
              <div class="glossary-item">
                <dt>Liquidity Surface</dt>
                <dd>3D визуализация ликвидности рынка как функции различных параметров (flow pressure, time evolution). Используется для детекции стресса ликвидности.</dd>
              </div>
              <div class="glossary-item">
                <dt>Signal Matrix</dt>
                <dd>Тепловая карта (heatmap) сигналов количественной модели, показывающая временные паттерны и интенсивность сигналов по различным измерениям.</dd>
              </div>
              <div class="glossary-item">
                <dt>Order Book (Стакан заявок)</dt>
                <dd>Список заявок на покупку (bids) и продажу (asks) актива с указанием цен и объемов. Показывает текущую ликвидность и спред.</dd>
              </div>
              <div class="glossary-item">
                <dt>Spread</dt>
                <dd>Разница между лучшей ценой покупки (best bid) и лучшей ценой продажи (best ask) в стакане заявок. Мера ликвидности и транзакционных издержек.</dd>
              </div>
            </div>
          </section>

          <!-- Models -->
          <section v-if="activeSection === 'models'" class="content-section">
            <h2>Математические модели и формулы</h2>
            
            <div class="model-block">
              <h3>Value at Risk (VaR) & Expected Shortfall (ES)</h3>
              <p>
                <strong>VaR (Value at Risk)</strong> — максимальный ожидаемый убыток портфеля на заданном уровне доверия α и горизонте времени T.
              </p>
              <div class="formula-block">
                <div class="formula-title">VaR (Historical Simulation):</div>
                <div class="latex-formula display-mode">\text{VaR}_\alpha = -\text{Quantile}_\alpha(\text{Returns})</div>
                <p class="formula-desc">где <span class="latex-formula">\text{Quantile}_\alpha</span> — α-квантиль исторических доходностей портфеля</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">VaR (Parametric, Normal):</div>
                <div class="latex-formula display-mode">\text{VaR}_\alpha = -\mu - z_\alpha \times \sigma \times \sqrt{T}</div>
                <p class="formula-desc">где <span class="latex-formula">\mu</span> — средняя доходность, <span class="latex-formula">\sigma</span> — волатильность, <span class="latex-formula">z_\alpha</span> — квантиль нормального распределения (1.645 для 95%, 2.326 для 99%)</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Expected Shortfall (CVaR):</div>
                <div class="latex-formula display-mode">\text{ES}_\alpha = \mathbb{E}[\text{Loss} \mid \text{Loss} \geq \text{VaR}_\alpha]</div>
                <p class="formula-desc">Средний убыток при сценариях, превышающих VaR. Более консервативная метрика tail-risk.</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/greeks</code> — расчет VaR/ES для портфеля. Страница <code>/portfolio</code> — отображение VaR в KPI.</p>
            </div>

            <div class="model-block">
              <h3>Black–Scholes–Merton (BSM) Model</h3>
              <p>
                Классическая модель ценообразования европейских опционов на базе логнормального распределения доходностей базового актива.
              </p>
              <div class="formula-block">
                <div class="formula-title">Цена Call опциона:</div>
                <div class="latex-formula display-mode">C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)</div>
              </div>
              <div class="formula-block">
                <div class="formula-title">Цена Put опциона:</div>
                <div class="latex-formula display-mode">P = K e^{-rT} N(-d_2) - S_0 e^{-qT} N(-d_1)</div>
              </div>
              <div class="formula-block">
                <div class="formula-title">Вспомогательные переменные:</div>
                <div class="latex-formula display-mode">d_1 = \frac{\ln(S_0/K) + (r - q + \sigma^2/2)T}{\sigma\sqrt{T}}</div>
                <div class="latex-formula display-mode">d_2 = d_1 - \sigma\sqrt{T}</div>
                <p class="formula-desc">где <span class="latex-formula">S_0</span> — текущая цена актива, <span class="latex-formula">K</span> — страйк, <span class="latex-formula">r</span> — безрисковая ставка, <span class="latex-formula">q</span> — дивидендная доходность, <span class="latex-formula">\sigma</span> — волатильность, <span class="latex-formula">T</span> — время до экспирации, <span class="latex-formula">N(\cdot)</span> — функция стандартного нормального распределения</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Greeks (чувствительности):</div>
                <div class="latex-formula display-mode">\Delta = \frac{\partial C}{\partial S} = e^{-qT} N(d_1) \quad \text{(для Call)}</div>
                <div class="latex-formula display-mode">\Gamma = \frac{\partial^2 C}{\partial S^2} = \frac{e^{-qT} n(d_1)}{S\sigma\sqrt{T}}</div>
                <div class="latex-formula display-mode">\nu = \frac{\partial C}{\partial \sigma} = \frac{S_0 e^{-qT} n(d_1)\sqrt{T}}{100}</div>
                <div class="latex-formula display-mode">\Theta = \frac{\partial C}{\partial T} = -\frac{S_0 e^{-qT} n(d_1)\sigma/(2\sqrt{T}) + qS_0 e^{-qT} N(d_1) - rK e^{-rT} N(d_2)}{365}</div>
                <div class="latex-formula display-mode">\rho = \frac{\partial C}{\partial r} = \frac{K T e^{-rT} N(d_2)}{100} \quad \text{(для Call)}</div>
                <p class="formula-desc">где <span class="latex-formula">n(\cdot)</span> — плотность стандартного нормального распределения</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/pricing/options</code> — расчет цены и Greeks. Страница <code>/pricing/options/greeks</code> — детальный анализ чувствительностей.</p>
            </div>

            <div class="model-block">
              <h3>Heston Stochastic Volatility Model</h3>
              <p>
                Модель со стохастической волатильностью, позволяющая моделировать улыбку волатильности (volatility smile) и корреляцию между ценой и волатильностью.
              </p>
              <div class="formula-block">
                <div class="formula-title">Система стохастических уравнений:</div>
                <div class="latex-formula display-mode">dS = \mu S \, dt + \sqrt{V} S \, dW_1</div>
                <div class="latex-formula display-mode">dV = \kappa(\theta - V) \, dt + \sigma_v \sqrt{V} \, dW_2</div>
                <div class="latex-formula display-mode">\mathbb{E}[dW_1 \, dW_2] = \rho \, dt</div>
                <p class="formula-desc">где <span class="latex-formula">V</span> — мгновенная дисперсия, <span class="latex-formula">\kappa</span> — скорость возврата к среднему (mean reversion), <span class="latex-formula">\theta</span> — долгосрочная дисперсия, <span class="latex-formula">\sigma_v</span> — волатильность волатильности, <span class="latex-formula">\rho</span> — корреляция между ценой и волатильностью</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/pricing/options/models</code> — сравнение BSM и Heston моделей.</p>
            </div>

            <div class="model-block">
              <h3>Geometric Brownian Motion (GBM)</h3>
              <p>
                Стохастический процесс для моделирования цен активов в Monte Carlo симуляциях.
              </p>
              <div class="formula-block">
                <div class="formula-title">Стохастическое дифференциальное уравнение:</div>
                <div class="latex-formula display-mode">dS = \mu S \, dt + \sigma S \, dW</div>
                <p class="formula-desc">где <span class="latex-formula">\mu</span> — дрейф (drift), <span class="latex-formula">\sigma</span> — волатильность, <span class="latex-formula">dW</span> — винеровский процесс</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Дискретная аппроксимация (Euler scheme):</div>
                <div class="latex-formula display-mode">S_{t+\Delta t} = S_t \times \exp\left[(\mu - \sigma^2/2)\Delta t + \sigma\sqrt{\Delta t} \times Z\right]</div>
                <p class="formula-desc">где <span class="latex-formula">Z \sim \mathcal{N}(0,1)</span> — стандартная нормальная случайная величина, <span class="latex-formula">\Delta t</span> — временной шаг</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/monte-carlo</code> — генерация сценариев цен. Страница <code>/terminal</code> — симуляция в Quant Alpha Terminal.</p>
            </div>

            <div class="model-block">
              <h3>DCF Bond Valuation (Discounted Cash Flow)</h3>
              <p>
                Оценка справедливой стоимости облигации дисконтированием будущих денежных потоков (купоны + номинал).
              </p>
              <div class="formula-block">
                <div class="formula-title">Dirty Price (полная стоимость):</div>
                <div class="latex-formula display-mode">P_{\text{dirty}} = \sum_{i=1}^{n} \frac{CF_i}{(1 + r_i)^{t_i}}</div>
                <p class="formula-desc">где <span class="latex-formula">CF_i</span> — денежный поток в момент <span class="latex-formula">t_i</span>, <span class="latex-formula">r_i</span> — ставка дисконтирования для периода i, <span class="latex-formula">n</span> — количество платежей</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Clean Price (котировочная цена):</div>
                <div class="latex-formula display-mode">P_{\text{clean}} = P_{\text{dirty}} - \text{Accrued Interest}</div>
                <p class="formula-desc"><span class="latex-formula">\text{Accrued Interest} = \text{Coupon} \times \frac{\text{Days since last coupon}}{\text{Days in coupon period}}</span></p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Macaulay Duration:</div>
                <div class="latex-formula display-mode">D = \frac{\sum_{i=1}^{n} t_i \times \text{PV}(CF_i)}{P_{\text{dirty}}}</div>
                <p class="formula-desc">Взвешенный по приведенной стоимости срок до получения денежных потоков</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Modified Duration:</div>
                <div class="latex-formula display-mode">D_{\text{mod}} = \frac{D}{1 + y}</div>
                <p class="formula-desc">где <span class="latex-formula">y</span> — доходность к погашению. Показывает процентное изменение цены при изменении доходности на 1%</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">DV01 (Рублевая стоимость 1 б.п.):</div>
                <div class="latex-formula display-mode">\text{DV01} = -P \times D_{\text{mod}} \times 0.0001</div>
                <p class="formula-desc">Изменение стоимости облигации при сдвиге кривой доходности на 1 basis point (0.01%)</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Convexity:</div>
                <div class="latex-formula display-mode">C = \frac{\sum_{i=1}^{n} t_i(t_i + 1) \times \text{PV}(CF_i)}{P \times (1 + y)^2}</div>
                <p class="formula-desc">Вторая производная цены по доходности, уточняет оценку изменения цены при крупных сдвигах ставок</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/bond-valuation</code> — расчет DCF, Duration, DV01, Convexity. Страницы <code>/vanila-bond-report</code> и <code>/floater-bond-report</code> — отчеты по облигациям.</p>
            </div>

            <div class="model-block">
              <h3>Sharpe Ratio & Risk-Adjusted Returns</h3>
              <div class="formula-block">
                <div class="formula-title">Sharpe Ratio:</div>
                <div class="latex-formula display-mode">\text{SR} = \frac{R_p - R_f}{\sigma_p}</div>
                <p class="formula-desc">где <span class="latex-formula">R_p</span> — средняя доходность портфеля, <span class="latex-formula">R_f</span> — безрисковая ставка, <span class="latex-formula">\sigma_p</span> — волатильность портфеля. Показывает избыточную доходность на единицу риска</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Sortino Ratio:</div>
                <div class="latex-formula display-mode">\text{Sortino} = \frac{R_p - R_f}{\sigma_{\text{down}}}</div>
                <p class="formula-desc">где <span class="latex-formula">\sigma_{\text{down}}</span> — волатильность отрицательных доходностей (downside deviation). Учитывает только негативный риск</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Calmar Ratio:</div>
                <div class="latex-formula display-mode">\text{Calmar} = \frac{\text{Annual Return}}{|\text{Max Drawdown}|}</div>
                <p class="formula-desc">Отношение годовой доходности к максимальной просадке</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/portfolio</code> — отображение Sharpe Ratio в KPI. Страница <code>/greeks</code> — детальные метрики риска.</p>
            </div>

            <div class="model-block">
              <h3>Hidden Markov Model (HMM)</h3>
              <p>
                Модель с невидимыми состояниями (рыночные режимы), управляющими динамикой наблюдаемых доходностей.
              </p>
              <div class="formula-block">
                <div class="formula-title">Вероятность наблюдения:</div>
                <div class="latex-formula display-mode">P(O_t \mid S_t = i) \sim \mathcal{N}(\mu_i, \sigma_i^2)</div>
                <p class="formula-desc">где <span class="latex-formula">O_t</span> — наблюдаемая доходность в момент t, <span class="latex-formula">S_t</span> — скрытое состояние (режим), <span class="latex-formula">\mu_i</span> и <span class="latex-formula">\sigma_i</span> — параметры нормального распределения для режима i</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Матрица переходов:</div>
                <div class="latex-formula display-mode">A_{ij} = P(S_{t+1} = j \mid S_t = i)</div>
                <p class="formula-desc">Вероятность перехода из режима i в режим j за один временной шаг</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Стационарное распределение:</div>
                <div class="latex-formula display-mode">\pi = \pi \times A</div>
                <p class="formula-desc">Долгосрочное распределение вероятностей режимов, решение системы линейных уравнений</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/regimes</code> — анализ HMM режимов. Страница <code>/regime-details</code> — детальная аналитика режимов.</p>
            </div>

            <div class="model-block">
              <h3>Portfolio Optimization (CCMV)</h3>
              <p>
                Constant Correlation Matrix Model — упрощенная модель оптимизации портфеля с постоянной корреляцией между активами.
              </p>
              <div class="formula-block">
                <div class="formula-title">Ожидаемая доходность портфеля:</div>
                <div class="latex-formula display-mode">\mathbb{E}[R_p] = \sum_{i=1}^{n} w_i \times \mathbb{E}[R_i]</div>
                <p class="formula-desc">где <span class="latex-formula">w_i</span> — вес актива i в портфеле, <span class="latex-formula">\mathbb{E}[R_i]</span> — ожидаемая доходность актива i</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Волатильность портфеля:</div>
                <div class="latex-formula display-mode">\sigma_p = \sqrt{\sum_{i,j} w_i w_j \sigma_i \sigma_j \rho_{ij}}</div>
                <p class="formula-desc">где <span class="latex-formula">\sigma_i</span> — волатильность актива i, <span class="latex-formula">\rho_{ij}</span> — корреляция между активами i и j</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/CCMVoptimization</code> — оптимизация весов портфеля.</p>
            </div>

            <div class="model-block">
              <h3>Swap Valuation (IRS)</h3>
              <p>
                Оценка справедливой стоимости процентного свопа (Interest Rate Swap) методом дисконтирования денежных потоков.
              </p>
              <div class="formula-block">
                <div class="formula-title">Стоимость свопа (для получателя фиксированной ставки):</div>
                <div class="latex-formula display-mode">V_{\text{swap}} = \text{PV}_{\text{fixed}} - \text{PV}_{\text{floating}}</div>
                <p class="formula-desc">где <span class="latex-formula">\text{PV}_{\text{fixed}} = \sum_i [\text{Fixed Rate} \times \text{Notional} \times \text{DF}_i]</span>, <span class="latex-formula">\text{PV}_{\text{floating}} = \text{Notional} \times (1 - \text{DF}_n)</span></p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/valuation/swaps</code> — оценка IRS, CDS, Basis, CCS свопов.</p>
            </div>

            <div class="model-block">
              <h3>Forward Valuation</h3>
              <p>
                Оценка справедливой форвардной цены и стоимости форвардного контракта.
              </p>
              <div class="formula-block">
                <div class="formula-title">Форвардная цена (без дивидендов):</div>
                <div class="latex-formula display-mode">F = S_0 \times e^{(r - q)T}</div>
                <p class="formula-desc">где <span class="latex-formula">S_0</span> — спотовая цена, <span class="latex-formula">r</span> — безрисковая ставка, <span class="latex-formula">q</span> — дивидендная доходность, <span class="latex-formula">T</span> — время до экспирации</p>
              </div>
              <div class="formula-block">
                <div class="formula-title">Стоимость форварда (для длинной позиции):</div>
                <div class="latex-formula display-mode">V = (F - K) \times e^{-rT}</div>
                <p class="formula-desc">где <span class="latex-formula">K</span> — форвардная цена контракта</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/valuation/forwards</code> — оценка форвардов. Страница <code>/forwards/basis</code> — анализ спот-форвард базиса.</p>
            </div>

            <div class="model-block">
              <h3>Manifold Learning & Liquidity Surface</h3>
              <p>
                Нестационарный manifold inference для детекции стресса ликвидности на основе топологии рыночной микроструктуры.
              </p>
              <div class="formula-block">
                <div class="formula-title">Параметрическая поверхность ликвидности:</div>
                <div class="latex-formula display-mode">z(x,y,t) = \text{FlowPressure} \times \sin(r \times f + t) \times \cos(\theta \times 3 + t \times 0.5) \times \text{Liquidity} + \text{TimeEffect}</div>
                <p class="formula-desc">где <span class="latex-formula">r = \sqrt{x^2 + y^2}</span>, <span class="latex-formula">\theta = \text{atan2}(y, x)</span>, <span class="latex-formula">f</span> — частота, <span class="latex-formula">t</span> — время эволюции</p>
              </div>
              <p><strong>Использование:</strong> Страница <code>/terminal</code> → вкладка "Количественный анализ" — 3D визуализация поверхности ликвидности.</p>
            </div>
          </section>

          <!-- Examples -->
          <section v-if="activeSection === 'examples'" class="content-section">
            <h2>Примеры расчетов</h2>
            <p>
              Практические примеры использования формул и моделей платформы с пошаговыми расчетами.
            </p>

            <div class="example-block">
              <h3>Пример 1: Расчет цены Call опциона (Black-Scholes)</h3>
              <p><strong>Условия:</strong></p>
              <ul>
                <li>Текущая цена актива (S₀): 100 ₽</li>
                <li>Страйк (K): 105 ₽</li>
                <li>Волатильность (σ): 20%</li>
                <li>Безрисковая ставка (r): 8%</li>
                <li>Время до экспирации (T): 0.25 года (3 месяца)</li>
                <li>Дивидендная доходность (q): 2%</li>
              </ul>
              <p><strong>Решение:</strong></p>
              <ol>
                <li>Рассчитываем d₁:
                  <div class="formula">d₁ = [ln(100/105) + (0.08 - 0.02 + 0.2²/2) × 0.25] / (0.2 × √0.25)</div>
                  <div class="formula">d₁ = [-0.0488 + 0.015] / 0.1 = -0.338</div>
                </li>
                <li>Рассчитываем d₂:
                  <div class="formula">d₂ = -0.338 - 0.2 × √0.25 = -0.438</div>
                </li>
                <li>Находим N(d₁) и N(d₂) из таблицы нормального распределения:
                  <div class="formula">N(d₁) = N(-0.338) ≈ 0.368</div>
                  <div class="formula">N(d₂) = N(-0.438) ≈ 0.331</div>
                </li>
                <li>Рассчитываем цену Call опциона:
                  <div class="formula">C = 100 × e<sup>-0.02×0.25</sup> × 0.368 - 105 × e<sup>-0.08×0.25</sup> × 0.331</div>
                  <div class="formula">C = 36.6 - 33.9 = 2.7 ₽</div>
                </li>
              </ol>
              <p><strong>Использование в платформе:</strong> Страница <code>/pricing/options</code> — введите параметры и получите результат автоматически.</p>
            </div>

            <div class="example-block">
              <h3>Пример 2: Расчет VaR портфеля (Parametric)</h3>
              <p><strong>Условия:</strong></p>
              <ul>
                <li>Текущая стоимость портфеля: 1,000,000 ₽</li>
                <li>Средняя дневная доходность (μ): 0.1%</li>
                <li>Волатильность портфеля (σ): 1.5%</li>
                <li>Уровень доверия: 95% (z₀.₀₅ = 1.645)</li>
                <li>Временной горизонт: 1 день</li>
              </ul>
              <p><strong>Решение:</strong></p>
              <div class="formula">VaR<sub>95%</sub> = -μ - z<sub>α</sub> × σ × √T</div>
              <div class="formula">VaR<sub>95%</sub> = -0.001 - 1.645 × 0.015 × √1</div>
              <div class="formula">VaR<sub>95%</sub> = -0.001 - 0.0247 = -0.0257 = -2.57%</div>
              <p>В абсолютном выражении:</p>
              <div class="formula">VaR = 1,000,000 × 0.0257 = 25,700 ₽</div>
              <p><strong>Интерпретация:</strong> С вероятностью 95% убыток портфеля за 1 день не превысит 25,700 ₽.</p>
              <p><strong>Использование в платформе:</strong> Страница <code>/greeks</code> — выберите "Parametric" модель VaR.</p>
            </div>

            <div class="example-block">
              <h3>Пример 3: Расчет Duration облигации</h3>
              <p><strong>Условия:</strong></p>
              <ul>
                <li>Номинал облигации: 1,000 ₽</li>
                <li>Купон: 50 ₽ (выплачивается раз в полгода)</li>
                <li>Срок до погашения: 3 года (6 купонных периодов)</li>
                <li>Доходность к погашению: 6% годовых (3% за полгода)</li>
              </ul>
              <p><strong>Решение:</strong></p>
              <ol>
                <li>Рассчитываем денежные потоки и их приведенную стоимость:
                  <table class="example-table">
                    <thead>
                      <tr>
                        <th>Период</th>
                        <th>Денежный поток</th>
                        <th>DF (3%)</th>
                        <th>PV</th>
                        <th>t × PV</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td>1</td><td>50</td><td>0.971</td><td>48.5</td><td>48.5</td></tr>
                      <tr><td>2</td><td>50</td><td>0.943</td><td>47.2</td><td>94.4</td></tr>
                      <tr><td>3</td><td>50</td><td>0.915</td><td>45.8</td><td>137.4</td></tr>
                      <tr><td>4</td><td>50</td><td>0.888</td><td>44.4</td><td>177.6</td></tr>
                      <tr><td>5</td><td>50</td><td>0.863</td><td>43.2</td><td>216.0</td></tr>
                      <tr><td>6</td><td>1,050</td><td>0.838</td><td>879.9</td><td>5,279.4</td></tr>
                      <tr class="total-row"><td><strong>Итого</strong></td><td></td><td></td><td><strong>1,109.0</strong></td><td><strong>5,953.3</strong></td></tr>
                    </tbody>
                  </table>
                </li>
                <li>Рассчитываем Macaulay Duration:
                  <div class="formula">D = Σ(tᵢ × PVᵢ) / P = 5,953.3 / 1,109.0 = 5.37 полугодий = 2.69 лет</div>
                </li>
                <li>Рассчитываем Modified Duration:
                  <div class="formula">D<sub>mod</sub> = D / (1 + y) = 5.37 / 1.03 = 5.21</div>
                </li>
                <li>Рассчитываем DV01:
                  <div class="formula">DV01 = -P × D<sub>mod</sub> × 0.0001 = -1,109 × 5.21 × 0.0001 = -0.58 ₽</div>
                </li>
              </ol>
              <p><strong>Интерпретация:</strong> При увеличении доходности на 1 bp (0.01%) цена облигации снизится на 0.58 ₽.</p>
              <p><strong>Использование в платформе:</strong> Страница <code>/bond-valuation</code> — введите параметры облигации и получите все метрики автоматически.</p>
            </div>

            <div class="example-block">
              <h3>Пример 4: Monte Carlo симуляция цены актива</h3>
              <p><strong>Условия:</strong></p>
              <ul>
                <li>Начальная цена (S₀): 100 ₽</li>
                <li>Дрейф (μ): 10% годовых</li>
                <li>Волатильность (σ): 25% годовых</li>
                <li>Период: 30 дней</li>
                <li>Количество сценариев: 10,000</li>
              </ul>
              <p><strong>Алгоритм:</strong></p>
              <ol>
                <li>Для каждого сценария генерируем случайное число Z ~ N(0,1)</li>
                <li>Рассчитываем цену через 30 дней:
                  <div class="formula">S<sub>30</sub> = 100 × exp[(0.10 - 0.25²/2) × (30/365) + 0.25 × √(30/365) × Z]</div>
                </li>
                <li>Повторяем 10,000 раз</li>
                <li>Анализируем распределение: медиана, квантили, вероятность достижения целевой цены</li>
              </ol>
              <p><strong>Использование в платформе:</strong> Страница <code>/monte-carlo</code> — введите параметры и запустите симуляцию.</p>
            </div>

            <div class="example-block">
              <h3>Пример 5: Расчет Sharpe Ratio</h3>
              <p><strong>Условия:</strong></p>
              <ul>
                <li>Средняя годовая доходность портфеля: 15%</li>
                <li>Безрисковая ставка: 5%</li>
                <li>Волатильность портфеля: 12%</li>
              </ul>
              <p><strong>Решение:</strong></p>
              <div class="formula">Sharpe Ratio = (R<sub>p</sub> - R<sub>f</sub>) / σ<sub>p</sub></div>
              <div class="formula">Sharpe Ratio = (0.15 - 0.05) / 0.12 = 0.833</div>
              <p><strong>Интерпретация:</strong> Портфель генерирует 0.833 единицы избыточной доходности на единицу риска. Значение выше 1 считается хорошим, выше 2 — отличным.</p>
              <p><strong>Использование в платформе:</strong> Страница <code>/portfolio</code> — Sharpe Ratio отображается в KPI карточке.</p>
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
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import katex from 'katex'
import 'katex/dist/katex.min.css'

const router = useRouter()
const activeSection = ref<string>('overview')
const contentRef = ref<HTMLElement | null>(null)

const setActiveSection = (section: string) => {
  activeSection.value = section
  // Плавная прокрутка к контенту
  setTimeout(() => {
    contentRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    nextTick(() => {
      renderFormulas()
    })
  }, 100)
}

const scrollToContent = () => {
  contentRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const renderFormulas = () => {
  nextTick(() => {
    const formulaElements = document.querySelectorAll('.latex-formula')
    formulaElements.forEach((el) => {
      if (el instanceof HTMLElement && !el.dataset.rendered) {
        try {
          const formula = el.textContent || ''
          katex.render(formula, el, {
            throwOnError: false,
            displayMode: el.classList.contains('display-mode')
          })
          el.dataset.rendered = 'true'
        } catch (e) {
          console.error('Error rendering formula:', e)
        }
      }
    })
  })
}

onMounted(() => {
  renderFormulas()
})
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
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

/* Красивый скроллбар по всей странице */
.docs-root::-webkit-scrollbar {
  width: 8px;
}

.docs-root::-webkit-scrollbar-track {
  background: transparent;
  border-radius: 10px;
}

.docs-root::-webkit-scrollbar-thumb {
  background: rgba(34, 211, 238, 0.3);
  border-radius: 10px;
  transition: background 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(15, 23, 42, 0.6);
  background-clip: padding-box;
}

.docs-root::-webkit-scrollbar-thumb:hover {
  background: rgba(34, 211, 238, 0.5);
  border-color: rgba(34, 211, 238, 0.3);
}

.docs-root::-webkit-scrollbar-thumb:active {
  background: rgba(34, 211, 238, 0.6);
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
  font-size: 18px;
  margin-bottom: 16px;
}

.model-block p {
  margin-bottom: 12px;
  line-height: 1.7;
}

.model-block p:last-child {
  margin-bottom: 0;
}

.formula-block {
  margin: 16px 0;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-left: 3px solid rgba(34, 211, 238, 0.6);
  border-radius: 8px;
}

.formula-title {
  font-size: 12px;
  font-weight: 600;
  color: rgba(34, 211, 238, 0.9);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
  font-family: var(--font-family-mono);
}

.formula {
  font-size: 16px;
  font-family: var(--font-family-mono);
  color: #fff;
  margin: 8px 0;
  padding: 8px 0;
  line-height: 1.8;
  white-space: pre-wrap;
}

.latex-formula {
  font-size: 16px;
  color: #fff;
  margin: 8px 0;
  padding: 8px 0;
  text-align: center;
}

.latex-formula.display-mode {
  display: block;
  margin: 16px auto;
  padding: 12px;
}

.formula sub, .formula sup {
  font-size: 0.7em;
  vertical-align: baseline;
  position: relative;
}

.formula sup {
  top: -0.4em;
}

.formula sub {
  bottom: -0.2em;
}

.formula-note {
  font-size: 0.85em;
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  margin-left: 8px;
}

.formula-desc {
  font-size: 12px;
  color: rgba(226, 232, 240, 0.7);
  margin-top: 8px;
  line-height: 1.6;
  font-style: italic;
}

.page-detail-block {
  margin: 24px 0;
  padding: 20px;
  background: rgba(34, 211, 238, 0.05);
  border: 1px solid rgba(34, 211, 238, 0.15);
  border-radius: 12px;
}

.page-detail-block h4 {
  font-size: 16px;
  font-weight: 700;
  color: #22d3ee;
  margin: 0 0 12px 0;
  font-family: var(--font-family-mono);
}

.page-detail-block p {
  margin-bottom: 12px;
}

.page-detail-block ol {
  margin: 12px 0;
  padding-left: 24px;
}

.page-detail-block ol li {
  margin-bottom: 8px;
  line-height: 1.6;
}

.page-detail-block code {
  background: rgba(0, 0, 0, 0.4);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-family-mono);
  font-size: 0.9em;
  color: #22d3ee;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin: 24px 0;
}

.feature-card {
  padding: 20px;
  background: rgba(34, 211, 238, 0.05);
  border: 1px solid rgba(34, 211, 238, 0.15);
  border-radius: 12px;
}

.feature-card h4 {
  font-size: 15px;
  font-weight: 700;
  color: #22d3ee;
  margin: 0 0 12px 0;
}

.feature-card ul {
  margin: 0;
  padding-left: 20px;
}

.feature-card li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 6px;
}

.architecture-block {
  margin: 20px 0;
  padding: 16px;
  background: rgba(34, 211, 238, 0.05);
  border-left: 3px solid rgba(34, 211, 238, 0.4);
  border-radius: 8px;
}

.architecture-block h4 {
  font-size: 15px;
  font-weight: 700;
  color: #22d3ee;
  margin: 0 0 12px 0;
}

.module-detail {
  margin: 20px 0;
  padding: 20px;
  background: rgba(34, 211, 238, 0.05);
  border: 1px solid rgba(34, 211, 238, 0.15);
  border-radius: 12px;
}

.module-detail h4 {
  font-size: 16px;
  font-weight: 700;
  color: #22d3ee;
  margin: 0 0 8px 0;
}

.module-detail p {
  margin: 8px 0;
  font-size: 13px;
}

.module-detail ul {
  margin: 12px 0;
  padding-left: 24px;
}

.module-detail li {
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 6px;
}

.example-block {
  margin: 32px 0;
  padding: 24px;
  background: rgba(34, 211, 238, 0.08);
  border: 1px solid rgba(34, 211, 238, 0.2);
  border-radius: 12px;
}

.example-block h3 {
  font-size: 17px;
  font-weight: 700;
  color: #22d3ee;
  margin: 0 0 16px 0;
}

.example-block ol {
  margin: 12px 0;
  padding-left: 24px;
}

.example-block ol li {
  margin-bottom: 12px;
  line-height: 1.7;
}

.example-table {
  width: 100%;
  margin: 16px 0;
  border-collapse: collapse;
  font-family: var(--font-family-mono);
  font-size: 12px;
}

.example-table thead {
  background: rgba(34, 211, 238, 0.15);
}

.example-table th {
  padding: 8px 12px;
  text-align: left;
  font-weight: 600;
  color: #22d3ee;
  border-bottom: 1px solid rgba(34, 211, 238, 0.3);
}

.example-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.example-table tr.total-row {
  background: rgba(34, 211, 238, 0.1);
  font-weight: 700;
}

.example-table tr.total-row td {
  border-top: 2px solid rgba(34, 211, 238, 0.4);
  padding-top: 12px;
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