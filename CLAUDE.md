# Zeta Terminal — CLAUDE.md

## Vision: Open-Source Aladdin

Zeta Terminal — open-source аналог **BlackRock Aladdin** (Asset, Liability, Debt, and Derivative Investment Network) для российского рынка. Aladdin управляет $21.6T активами для 200+ институциональных клиентов и является индустриальным стандартом risk management.

**Цель:** создать доступную платформу с ключевыми возможностями Aladdin для количественного анализа, управления портфелем и оценки рисков — без enterprise-ценника ($750K–$2M+/год).

### Маппинг модулей: Aladdin → Zeta Terminal

| Aladdin Module | Zeta Terminal | Статус | Приоритет |
|---------------|---------------|--------|-----------|
| **Aladdin Risk** — VaR, stress testing, factor models, scenario analysis | `/portfolio` VaR/CVaR, `/stress` stress testing, GARCH, HMM regime detection | Частично | P0 |
| **Portfolio Management** — construction, optimization, rebalancing, attribution | `/portfolio`, `/ccmv` CCMV optimization, `/hjb` HJB dynamic, Markowitz | Частично | P0 |
| **Trading & Execution** — OMS, FIX connectivity, electronic trading | — | Не начато | P2 |
| **Operations & Settlement** — reconciliation, corporate actions | — | Не начато | P3 |
| **Compliance & Regulatory** — pre-trade checks, guideline monitoring | — | Не начато | P2 |
| **Fixed Income Analytics** — OAS, duration, convexity, yield curves | `/bond-valuation` DCF, `/zcyc-viewer` ZCYC, duration, convexity | Готово | — |
| **Derivatives Pricing** — options, swaps, forwards | `/pricing/options` BSM/Heston/VG/CGMY, `/valuation/swaps` IRS/CDS, `/valuation/forwards` | Готово | — |
| **Volatility** — surfaces, calibration | `/analytics/volatility` SABR/SVI 3D surface | Готово | — |
| **Market Regimes** — regime detection, spectral analysis | `/terminal` Prony/ACF, `/regimes` HMM 3D | Готово | — |
| **Aladdin Wealth** — advisor tools, client reporting, stress testing for wealth | — | Не начато | P1 |
| **Aladdin Studio** — API platform, SDK, data cloud | REST API (FastAPI), но без SDK/docs | Частично | P1 |
| **Aladdin Sustainability** — ESG metrics, climate risk | — | Не начато | P3 |
| **Aladdin Copilot** — AI assistant (LangChain/GPT-4) | GitHub Issues auto-responder (Claude) | Минимально | P1 |
| **Data Platform** — multi-source data ingestion, time-series | MOEX ISS, RuData, Yahoo Finance | Частично | P1 |
| **Client Reporting** — PDF/Excel reports, dashboards | PDF export (`html2pdf.js`), Excel (`xlsx`) | Частично | P1 |
| **Backtesting** — strategy backtesting with historical data | `/backtest` | Частично | P0 |

### Ключевые принципы Aladdin, которым следуем

1. **"One Platform"** — единая точка доступа к данным, аналитике и торговле (у нас: единый SPA с Command Palette `⌘K`)
2. **Risk-First** — риск-аналитика как фундамент всех решений, а не надстройка
3. **Multi-Asset** — поддержка всех классов активов в одном интерфейсе (облигации, акции, деривативы, портфели)
4. **Real-Time + Historical** — сочетание live-данных с историческим анализом
5. **API-First** — каждая функция доступна через API (у нас: FastAPI REST endpoints)

### Чего у Aladdin нет, а у нас есть

- **Open-source** — весь код открыт (MIT)
- **Российский рынок** — MOEX ISS, RuData/Interfax, ZCYC ЦБ РФ
- **Zero cost** — бесплатный деплой (GitHub Pages + Render free tier + Neon)
- **Brutalist UI** — уникальный дизайн vs корпоративный Aladdin

### Roadmap к паритету с Aladdin (приоритеты)

**P0 — Core (текущий фокус):**
- Расширение risk analytics: Monte Carlo VaR, factor risk decomposition, correlation stress
- Portfolio construction: Black-Litterman, risk parity, min-CVaR
- Backtesting: multi-strategy, transaction costs, slippage

**P1 — Platform:**
- AI Copilot: интеграция Claude API для natural language queries по портфелю
- Data Platform: больше источников (CBR, FRED, Binance), time-series storage
- Client Reporting: шаблонные отчёты для инвесторов, автокомментарии
- API documentation + Python SDK (`zetaterminal-sdk`)

**P2 — Trading & Compliance:**
- Order management (бумажный трейдинг → реальное исполнение)
- Pre-trade compliance checks
- Regulatory reporting templates

**P3 — Extended:**
- ESG/Climate risk scoring
- Private markets (eFront аналог)
- Operations & settlement

### Конкурентный контекст

| Платформа | AUM | Стоимость | Open-Source |
|-----------|-----|-----------|------------|
| **BlackRock Aladdin** | $21.6T | $750K–$2M+/год | Нет |
| **Bloomberg PORT** | — | $24K+/год за терминал | Нет |
| **MSCI RiskMetrics** | — | Enterprise pricing | Нет |
| **FactSet** | — | $12K+/год | Нет |
| **Zeta Terminal** | — | **Бесплатно** | **Да (MIT)** |

---

Production-ready quantitative financial analysis platform (SaaS).
Frontend on **GitHub Pages**, backend on **Render** (free tier).

---

## Repository Structure

```
zetaterminal/
├── .github/
│   ├── workflows/
│   │   ├── pages.yml              # Frontend CI/CD → GitHub Pages
│   │   └── deploy-backend.yml     # Backend CI (verify imports; Render auto-deploys)
│   └── scripts/
│       └── claude_responder.py    # GitHub Issues auto-responder (Claude AI)
├── backend/
│   ├── src/
│   │   ├── main.py                # FastAPI app entry, CORS config
│   │   ├── api/                   # API routers (one file per domain)
│   │   │   ├── bond.py            # POST /api/bond/valuate, GET /api/bond/market-yield
│   │   │   ├── swap.py            # POST /api/swap/valuate
│   │   │   ├── forward.py         # POST /api/forward/valuate
│   │   │   ├── compute.py         # POST /api/compute/garch, /statistics
│   │   │   ├── multivariate_hmm.py # GET /api/multivariate-hmm/chart-data, /transition-matrix
│   │   │   ├── spectral_regime.py # POST /api/spectral-regime/analyze, GET /available-assets
│   │   │   ├── zcyc.py            # GET /api/zcyc/fetch, POST /interpolate
│   │   │   ├── rudata.py          # POST /api/rudata/test-connection, /query
│   │   │   ├── database.py        # POST /api/database/export/registry/parquet
│   │   │   ├── portfolio.py       # GET/POST /api/portfolio
│   │   │   ├── backtest.py        # POST /api/backtest/run
│   │   │   ├── stress.py          # POST /api/stress/test
│   │   │   ├── ccmv.py            # POST /api/ccmv/optimize
│   │   │   ├── hjb.py             # POST /api/hjb/solve
│   │   │   ├── pricing/
│   │   │   │   └── options.py     # Options pricing (BSM, Heston, VG, CGMY)
│   │   │   └── market_data.py     # GET /api/market-data/fetch
│   │   ├── services/
│   │   │   ├── compute_service.py          # ComputeService — GARCH(1,1)
│   │   │   ├── spectral_regime_service.py  # SpectralRegimeAnalyzer — Prony method, ACF
│   │   │   ├── rudata_service.py           # RuDataService — RuData/Interfax API client
│   │   │   └── zcyc_service.py             # ZCYCService — yield curve from MOEX
│   │   └── database/
│   │       ├── client.py           # SQLAlchemy async engine (Neon PostgreSQL)
│   │       ├── sa_models.py        # ORM models (Base, BondValuation, Portfolio, etc.)
│   │       ├── models.py           # Pydantic schemas
│   │       ├── repositories.py     # BondValuationRepository, PortfolioRepository,
│   │       │                       # MarketDataRepository, FileRepository
│   │       └── storage.py          # Local file storage
│   ├── Procfile                    # web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
│   ├── start.sh
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.ts                 # App entry point
│   │   ├── router/index.ts         # Hash-based routing (createWebHashHistory)
│   │   ├── stores/                 # Pinia stores
│   │   ├── pages/                  # Vue page components (see routes below)
│   │   ├── components/Layout/
│   │   │   ├── MainLayout.vue
│   │   │   ├── Sidebar.vue
│   │   │   └── CommandPalette.vue  # Cmd+K / Ctrl+K global navigation
│   │   ├── services/               # TypeScript API clients (Axios)
│   │   │   ├── multivariateHmmService.ts
│   │   │   ├── spectralRegimeService.ts
│   │   │   ├── bondService.ts
│   │   │   └── rudataService.ts
│   │   ├── utils/
│   │   │   ├── RegimeSpaceRenderer.ts  # Three.js 3D renderer
│   │   │   └── HMMModel.ts             # Forward-Backward, Viterbi
│   │   └── assets/styles/main.css  # CSS variables — design system source of truth
│   ├── tailwind.config.js
│   ├── vite.config.ts              # Base path: /zetaterminal/, code splitting
│   ├── 404.html                    # SPA redirect for GitHub Pages hash routing
│   └── package.json
├── docs/                           # Project documentation / wiki
├── cvrc-visualizer/                # Standalone CVRC visualizer module
└── Шаблоны/                        # Report templates
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| Vue 3.4 + TypeScript 5.3 | Core framework, Composition API (`<script setup lang="ts">`) |
| Vite 5.0 | Build tool, dev server |
| Vue Router 4.6 | Hash-based routing (`createWebHashHistory`) |
| Pinia 2.1 | State management |
| Tailwind CSS 3.4 | Utility-first styling |
| Three.js 0.182 | 3D visualizations (RegimeSpace3D, VolatilitySurface3D) |
| Chart.js 4.4 + ECharts 6.0 | 2D charts |
| KaTeX 0.16 | LaTeX formula rendering in Documentation |
| XLSX 0.18 | Excel registry import/export |
| html2pdf.js 0.12 | PDF report generation |
| Axios 1.6 | HTTP client, base URL from `VITE_API_BASE_URL` |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI 0.115+ + Uvicorn 0.34+ | ASGI web framework |
| Pydantic v2 | Request/response validation |
| SQLAlchemy 2.0 + asyncpg | Async ORM + Neon PostgreSQL |
| NumPy 1.26, Pandas 2.2, SciPy 1.14 | Numerical computations |
| CVXPy 1.3 | Convex optimization |
| PyArrow 14.0 | Parquet export |
| aiohttp 3.9 | Async HTTP (MOEX, RuData) |
| yfinance 0.2 | Yahoo Finance historical prices |
| slowapi 0.1 | Rate limiting (per-IP) |

---

## Design System — BRUTALIST (DO NOT DEVIATE)

This is a hard constraint. Every UI change must respect these rules.

### Colors (from `frontend/src/assets/styles/main.css`)
```css
--bg-primary:    #050505
--bg-secondary:  #0A0A0A
--accent:        #DC2626   /* red — sparingly, emphasis only */
--text-primary:  #F5F5F5
--text-muted:    #888888
--border:        #1A1A1A
/* success: #22C55E  |  warning: #F59E0B */
```
**Never hardcode hex colors in Vue components.** Always use CSS variables.

### Typography
- `.font-anton` — Hero headings, large titles (ALL CAPS preferred)
- `.font-oswald` — UI labels, navigation, body text
- `.font-mono` / Space Mono — Numbers, data values, code, indices, arrows

### UI Rules
- Border radius: **3–6px max** — never `rounded-full`
- No box shadows, no gradients, no glassmorphism
- Arrows: use `→` (`&rarr;`), not icon libraries
- Grid overlay on hero sections — signature element, preserve it
- Marquee text strips — signature element, preserve them
- **Dark-only** — no light mode, ever
- Buttons: `btn btn-primary` (red fill) or `btn btn-outline` (border only)

---

## Application Routes

| Route | Component | Tools / Description |
|---|---|---|
| `/portfolio` | `Portfolio.vue` | Returns, VaR/ES, monitoring |
| `/terminal` | `Terminal.vue` | Spectral analysis (Prony method, ACF) |
| `/regimes` | `RegimeSpace3D.vue`, `HMMAnalysis.vue` | HMM 3D regime detection |
| `/bond-valuation` | `BondValuation.vue` | DCF, duration, convexity, MOEX yield |
| `/vanila-bond-report` | `VanillaBondReport.vue` | Templated bond reports |
| `/zcyc-viewer` | `ZCYCViewer.vue` | Zero-coupon yield curve from MOEX |
| `/pricing/options` | `OptionPricing.vue` | BSM, Heston, VG, CGMY + Greeks |
| `/analytics/volatility` | `VolatilitySurface3D.vue` | SABR/SVI calibration, 3D surface |
| `/analytics/pnl` | P&L attribution | Factor decomposition |
| `/valuation/swaps` | `SwapValuation.vue` | IRS, CDS, CCS — NPV, DV01 |
| `/valuation/forwards` | Forward valuation | Fair value, forward curve |
| `/backtest` | Backtesting | Strategy backtesting |
| `/stress` | Stress testing | Stress scenarios |
| `/ccmv` | `CCMVOptimization.vue` | CCMV portfolio optimization |
| `/hjb` | `HJBOptimization.vue` | HJB dynamic optimization |
| `/settings` | `Settings.vue` | RuData credentials, preferences |

Navigation: Sidebar + Command Palette (`⌘K` / `Ctrl+K`).

---

## Financial Models

### Options & Derivatives
- **Black-Scholes-Merton (BSM)** — European options, full Greeks (Δ, Γ, ν, Θ, ρ)
- **Heston** — stochastic volatility; params: κ, θ, σ, ρ, v₀
- **Variance Gamma (VG)** — Lévy process with finite variation
- **CGMY** — generalized Lévy; params: C, G, M, Y
- **FFT pricing** — for computationally intensive Lévy models

### Fixed Income
- **Bond DCF** — day count conventions: Actual/365F, Actual/360, 30/360
- **IRS / FX / CDS Swaps** — NPV, DV01
- **Forwards** — fair value, forward curve
- **ZCYC** — zero-coupon yield curve fitting from MOEX

### Volatility
- **SABR** — stochastic α, β, ρ, ν
- **SVI** — static volatility interpolation/extrapolation

### Risk & Portfolio
- **GARCH(1,1)** — conditional volatility (`compute_service.py`)
- **VaR / CVaR (ES)** — Value-at-Risk, Expected Shortfall
- **CCMV** — constrained convex mean-variance optimization
- **HJB** — Hamilton-Jacobi-Bellman PDE optimization
- **Markowitz** — classical mean-variance, quadratic programming

### Market Regimes
- **HMM** — 2–4 state Hidden Markov Model
  - Baum-Welch (EM) estimation, Viterbi decoding, Forward-Backward smoothing
  - 3D visualization: `RegimeSpaceRenderer.ts` + `HMMModel.ts`
- **Spectral analysis** — Prony method, ACF decomposition, pole clustering (`Terminal.vue`)

---

## External Data Sources

| Source | Purpose | Implementation |
|---|---|---|
| MOEX ISS (`iss.moex.com`) | Market yields, ZCYC | `zcyc_service.py` |
| RuData/Interfax (`dh2.efir-net.ru`) | Bond reference data, cashflows | `rudata_service.py` (5 req/s, 100 items/filter max) |
| Yahoo Finance | Historical prices for spectral analysis | `yfinance` in `spectral_regime_service.py` |

RuData credentials: `localStorage` (frontend) + env vars (backend). Validated via `/api/rudata/test-connection`.

---

## Infrastructure & Deployment

### Frontend → GitHub Pages
```
Trigger: push to main → pages.yml
Build:   Node.js 20 | npm ci in ./frontend | npm run build
Deploy:  frontend/dist/ → gh-pages branch
URL:     russiankendricklamar.github.io/zetaterminal/
Notes:   base path /zetaterminal/ | hash routing | 404.html SPA redirect
```

### Backend → Render (free tier)
```
Deploy:  Render auto-deploys on push to main (render.yaml Blueprint)
CI:      deploy-backend.yml verifies imports only
Runtime: Python 3.11.0
Start:   uvicorn src.main:app --host 0.0.0.0 --port $PORT
Note:    Free tier sleeps after 15min idle; App.vue calls warmupBackend() on mount
```

### Database — Neon PostgreSQL
Neon free tier. SQLAlchemy async ORM with `asyncpg`. Tables auto-created via `init_db()` on startup.

### Environment Variables
```bash
# Frontend (build-time via GitHub Actions)
VITE_API_BASE_URL        # Render backend URL

# Backend (Render env)
PORT                     # provided by Render
CORS_ORIGINS             # allowed origins (default: *)
DATABASE_URL             # postgresql+asyncpg://user:pass@ep-xxx.neon.tech/neondb?sslmode=require
API_KEY                  # API authentication key

# GitHub Actions secrets
ANTHROPIC_API_KEY        # for claude_responder.py
# GITHUB_TOKEN is auto-provided
```

---

## Commands

```bash
# Frontend
cd frontend
npm install
npm run dev          # localhost:5173
npm run build        # → dist/
npm run type-check   # TypeScript check

# Backend
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload    # localhost:8000
# or
bash start.sh
```

---

## Code Conventions

### Python (backend)
- Type hints on **all** function signatures
- Pydantic v2 models for all request/response schemas
- Architecture: Router (validation + I/O) → Service (logic) → Repository (DB)
- `async/await` + `aiohttp` for external API calls
- `HTTPException` with descriptive `detail` — never generic 500
- Financial calculations must have **unit tests with known reference values**
  (e.g., BSM call price for known S=100, K=105, T=1, r=0.05, σ=0.2)

### TypeScript / Vue (frontend)
- Composition API, `<script setup lang="ts">` everywhere — no Options API
- CSS variables from `main.css` — **never hardcode hex values** in components
- `.font-anton`, `.font-oswald`, `.font-mono` utility classes only
- Axios with `VITE_API_BASE_URL` — never hardcode backend URLs
- `ref()` for primitives, `reactive()` for objects, Pinia for shared state

### GitHub Issues Automation
- Script: `.github/scripts/claude_responder.py`
- Uses `anthropic` Python SDK + `PyGithub`
- Init pattern: `auth = Auth.Token(os.environ['GITHUB_TOKEN']); github = Github(auth=auth)`
- This `CLAUDE.md` file is injected as system prompt context when responding to issues

---

## What NOT to Do

- **Never change the color palette** without explicit instruction
- **Never change fonts** — Anton, Oswald, Space Mono only, no exceptions
- **Never add light mode** — dark-only by design
- **Never use `rounded-full`** or border-radius > 6px
- **Never add shadows or glassmorphism** on primary UI elements
- **Never add icon libraries** — use `→` and text symbols
- **Never use emoji** in UI components
- **Never migrate to React / Next.js** or other frameworks
- **Never refactor financial math** without test coverage with reference values first
- **Never hardcode hex colors or backend URLs** in Vue components

---

## Code Review Standards

Every code change must satisfy these checks before commit.

### Python (backend) — Checklist
- [ ] `ruff check` passes with zero errors
- [ ] Type hints on all function parameters and return values
- [ ] Pydantic v2 model for every request/response — no raw dicts in router signatures
- [ ] Router → Service → Repository layering respected (no DB calls in routers)
- [ ] All `except` blocks log with `logger.error(msg, e, exc_info=True)` — never bare `except:`
- [ ] HTTPException detail is user-friendly, never leaks internals (stack traces, SQL, paths)
- [ ] No hardcoded secrets, API keys, or DB credentials — only `os.environ` / `.env`
- [ ] Financial math changes require unit test with known reference value
- [ ] `asyncio.to_thread()` wraps CPU-heavy sync calculations in async routes
- [ ] Rate limiting (`@limiter.limit`) on all public-facing heavy endpoints

### TypeScript / Vue (frontend) — Checklist
- [ ] `npx eslint` passes with zero errors
- [ ] `<script setup lang="ts">` — no Options API, no `defineComponent()`
- [ ] No hardcoded hex colors — use CSS variables from `main.css`
- [ ] No hardcoded URLs — use `getApiBaseUrl()` from `@/utils/apiBase`
- [ ] No `any` type — use proper interfaces/types from `@/types/`
- [ ] Composables (`use*`) for reusable logic — no logic duplication across pages
- [ ] No `console.log` in committed code (use `console.warn`/`console.error` if needed)
- [ ] Brutalist design rules: no rounded-full, no shadows, no gradients, border-radius ≤ 6px
- [ ] API error handling: catch, show user-friendly message, never swallow silently
- [ ] Pinia store for shared state — no prop drilling beyond 2 levels

### Security — Checklist
- [ ] No secrets in source code (grep for API_KEY, password, token, secret)
- [ ] All user input validated via Pydantic (backend) or Zod/runtime check (frontend)
- [ ] SQL injection: only parameterized queries via SQLAlchemy ORM — never raw SQL strings
- [ ] CORS origins restricted in production (not `*`)
- [ ] Rate limiting on auth endpoints and heavy computations
- [ ] JWT tokens: short expiry, refresh token rotation
