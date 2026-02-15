# Overview

This space provides a high-level introduction to the Zeta Terminal system: its purpose, architecture, technology stack, and key modules. This page serves as the entry point to understanding the codebase structure and how the major components interact.

For detailed information about specific subsystems, see:

- Frontend application structure: [Frontend Application](#frontend-application)
- Backend services and APIs: [Backend Services](#backend-services)
- Deployment pipelines and infrastructure: [Deployment & Operations](#deployment--operations)
- Development setup and workflows: [Development Guide](#development-guide)

## System Purpose

Zeta Terminal is a production-ready quantitative financial analysis platform designed for:

- **Derivatives Pricing**: Valuation of bonds, swaps, forwards, and options using DCF, Black-Scholes, Heston, and Lévy process models
- **Risk Management**: Stress testing, VaR/CVaR calculation, Greeks analysis, and portfolio hedging
- **Market Regime Analysis**: Hidden Markov Model (HMM) regime detection and spectral density analysis for identifying market states
- **Portfolio Optimization**: CCMV and HJB optimization strategies with GARCH volatility modeling
- **Fixed Income Analytics**: Bond valuation, zero-coupon yield curve (ZCYC) visualization, and market yield integration from MOEX

The system integrates with external data providers (MOEX ISS API, RuData/Interfax, Yahoo Finance) and provides both interactive web-based tools and programmatic API access.

## High-Level Architecture

The system follows a decoupled client-server architecture where a Vue.js Single Page Application (SPA) communicates with a Python FastAPI backend over HTTP/HTTPS.

### System Architecture Diagram

- Web Browser
- `index.html` + `main.ts`
- Vue Router — `src/router/index.ts`
- Pinia State Management — `src/stores/*`
- `MainLayout.vue` — Glass Design System

Client-facing pages:

- Portfolio Analysis — `RegimeSpace3D.vue`
- Zeta Terminal — `Terminal.vue`
- Bond Valuation — `BondValuation.vue`
- Options Pricing — `OptionPricing.vue`
- Optimization — `CCMVOptimization.vue`

Backend:

- `src/main.py` — FastAPI app
- `src/api/bond.py`
- `src/api/swap.py`
- `src/api/compute.py`
- `src/api/spectral_regime.py`
- `src/api/multivariate_hmm.py`
- `src/api/rudata.py`
- `src/api/zcyc.py`

Services:

- `src/services/compute_service.py` — GARCH(1,1)
- `src/services/spectral_regime_service.py` — Prony Method
- `src/services/rudata_service.py`

Database layer:

- `src/database/repositories.py` — `BondValuationRepository`, `PortfolioRepository`

External infrastructure:

- MOEX ISS API — `iss.moex.com`
- RuData/Interfax — `dh2.efir-net.ru`
- Yahoo Finance — `yfinance`
- Supabase — PostgreSQL + TimescaleDB
- Supabase Storage — Parquet files

The frontend is a static SPA hosted on **GitHub Pages** and built with **Vite**. The backend runs on **Railway** and is built with **FastAPI** and **Uvicorn**. All inter-service communication occurs over HTTPS with CORS configured in the backend.

## Technology Stack

### Frontend Stack

| Technology        | Version/Config | Purpose                                             | File Reference                                                                 |
|-------------------|----------------|-----------------------------------------------------|--------------------------------------------------------------------------------|
| **Vue.js**        | 3.4.15         | Core framework with Composition API                 | `frontend/package.json`                                                        |
| **TypeScript**    | 5.3.3          | Type safety and IDE support                         | `frontend/tsconfig.json`                                                       |
| **Vite**          | 5.0.8          | Build tool and dev server                           | `frontend/vite.config.ts`                                                      |
| **Vue Router**    | 4.6.4          | SPA routing with hash-based navigation              | `frontend/src/router/index.ts`                                                |
| **Pinia**         | 2.1.7          | State management                                    | `frontend/src/stores/`                                                         |
| **Three.js**      | 0.182.0        | 3D visualization (RegimeSpace3D, VolatilitySurface) | `frontend/src/utils/RegimeSpaceRenderer.ts`                                    |
| **Chart.js**      | 4.4.1          | 2D charting                                         | Various components                                                             |
| **ECharts**       | 6.0.0          | Advanced visualization                              | Terminal components                                                            |
| **KaTeX**         | 0.16.27        | LaTeX formula rendering                             | `frontend/src/pages/Documentation.vue`                                         |
| **XLSX**          | 0.18.5         | Excel import/export for registries                  | Bond valuation pages                                                           |
| **Tailwind CSS**  | 3.4.1          | Utility-first styling                               | `frontend/tailwind.config.js`                                                 |

### Backend Stack

| Technology          | Version   | Purpose                                   | File Reference                                   |
|---------------------|----------|-------------------------------------------|--------------------------------------------------|
| **FastAPI**         | ≥0.104.0 | ASGI web framework                        | `backend/src/main.py`                            |
| **Uvicorn**         | ≥0.24.0  | ASGI server                               | `backend/start.sh`                               |
| **Pydantic**        | ≥2.0.0   | Data validation and serialization         | All API routers                                  |
| **NumPy**           | ≥1.24.0  | Numerical computations                    | GARCH, HMM, pricing engines                      |
| **Pandas**          | ≥2.0.0   | Data processing                           | Registry operations                              |
| **SciPy**           | ≥1.11.0  | Scientific computing (optimization, interpolation) | CCMV, HJB solvers                        |
| **PyArrow**         | ≥14.0.0  | Parquet file I/O                          | `backend/src/database/repositories.py`           |
| **CVXPy**           | ≥1.3.0   | Convex optimization                       | Portfolio optimization                           |
| **Supabase Client** | ≥2.0.0   | Database and storage client               | `backend/src/database/client.py`                 |
| **aiohttp**         | ≥3.9.0   | Async HTTP client for MOEX and RuData     | `backend/src/services/rudata_service.py`         |
| **yfinance**        | ≥0.2.0   | Yahoo Finance data fetching               | `backend/src/services/spectral_regime_service.py`|

## Key Modules by Importance

Based on cluster analysis and usage patterns, the system's modules are ranked by importance.

### Critical Modules (Highest Priority)

| Module                  | Importance | Description                                                        | Frontend Component      | Backend API                            | Wiki Page                                                                 |
|-------------------------|------------|--------------------------------------------------------------------|-------------------------|----------------------------------------|---------------------------------------------------------------------------|
| **3D Regime Space**     | 47.68      | HMM market regime detection with Three.js 3D visualization         | `RegimeSpace3D.vue`     | `/api/multivariate-hmm/*`             | [RegimeSpace3D Component](#regimespace3d-component) |
| **Zeta Terminal**       | 18.54      | Spectral regime analysis using Prony method and ACF decomposition  | `Terminal.vue`          | `/api/spectral-regime/*`              | [Market Analysis Terminal](#market-analysis-terminal) |
| **ZCYC Viewer**         | 14.22      | Zero-coupon yield curve visualization with MOEX integration        | `ZCYCViewer.vue`        | `/api/zcyc/*`                         | [ZCYC Viewer](#zcyc-viewer)                         |
| **Documentation**       | 12.81      | KaTeX-rendered mathematical formulas and model explanations        | `Documentation.vue`     | N/A                                    | [Reporting & Documentation](#reporting--documentation) |
| **CCMV/HJB Optimization** | 9.12     | Portfolio optimization with GARCH volatility models                | `CCMVOptimization.vue`  | `/api/compute/garch`, `/api/ccmv/*`, `/api/hjb/*` | [Portfolio Optimization](#portfolio-optimization) |

### High Priority Modules

- **Bond Valuation**: DCF model with Excel registry import/export, market yield from MOEX
- **Swap Valuation**: IRS, CDS, and CCS pricing with portfolio stress testing
- **Option Pricing**: Black-Scholes, Heston, VG models with Greeks calculation
- **Volatility Surface**: 3D visualization of implied volatility using Three.js

### Standard Modules

- Market data feeds, portfolio management, backtesting, reports, settings

## Component Mapping: Natural Language to Code Entities

### Frontend Component Mapping

User-facing features:

- Portfolio Analysis with HMM Regimes
- Market Data Terminal with Spectral Analysis
- Bond Valuation Tools
- Derivatives Pricing
- Portfolio Optimization

Vue page components (`frontend/src/pages/`):

- `RegimeSpace3D.vue`
- `HMMAnalysis.vue`
- `Terminal.vue`
- `BondValuation.vue`
- `VanillaBondReport.vue`
- `ZCYCViewer.vue`
- `OptionPricing.vue`
- `VolatilitySurface3D.vue`
- `CCMVOptimization.vue`
- `HJBOptimization.vue`

TypeScript services (`frontend/src/services/`):

- `multivariateHmmService.ts`
- `spectralRegimeService.ts`
- `bondValuationService.ts`
- `rudataService.ts`
- `zcycService.ts`
- `optionPricingService.ts`
- `computeService.ts`

Utilities (`frontend/src/utils/`):

- `RegimeSpaceRenderer.ts` — Three.js renderer
- `HMMModel.ts` — Forward-Backward, Viterbi

### Backend API Mapping

Data access (`backend/src/database/`):

- `repositories.py` — `BondValuationRepository`, `PortfolioRepository`, `MarketDataRepository`

Business logic (`backend/src/services/`):

- `compute_service.py` — `ComputeService`
- `spectral_regime_service.py` — `SpectralRegimeAnalyzer`
- `rudata_service.py` — `RuDataService`
- `zcyc_service.py` — `ZCYCService`

FastAPI routers (`backend/src/api/`):

- `multivariate_hmm.py`
- `spectral_regime.py`
- `bond.py`
- `compute.py`
- `zcyc.py`
- `rudata.py`
- `swap.py`
- `pricing/options.py`

HTTP API endpoints:

- `/api/multivariate-hmm/*` — HMM chart data
- `/api/spectral-regime/*` — Analyze asset
- `/api/bond/*` — Bond valuation
- `/api/compute/*` — GARCH, statistics
- `/api/zcyc/*` — Yield curves
- `/api/rudata/*` — Bond info, search
- `/api/swap/*` — Swap valuation
- `/api/pricing/options/*` — Option pricing

## Data Flow Architecture

The system implements several data flow patterns depending on the operation type.

### Real-Time Market Data Flow

1. **User Request**: Frontend component (e.g., `Terminal.vue`) requests market data.
2. **API Call**: TypeScript service (e.g., `spectralRegimeService.ts`) sends HTTP request to backend.
3. **Backend Router**: FastAPI router (e.g., `spectral_regime.py`) receives request.
4. **External API Integration**: Service (e.g., `SpectralRegimeAnalyzer`) fetches data from Yahoo Finance via `yfinance`.
5. **Computation**: Backend performs spectral analysis (Prony method, ACF computation).
6. **Response**: JSON response returned to frontend.
7. **Visualization**: Frontend renders using ECharts or Three.js.

### Database-Backed Operations

1. **User Input**: User uploads bond registry via `BondValuation.vue`.
2. **Calculation**: Backend `bond.py` router invokes pricing engine.
3. **Persistence**: `BondValuationRepository` saves results to Supabase PostgreSQL.
4. **File Export**: Optional Parquet export to Supabase Storage.
5. **Retrieval**: Subsequent queries fetch from database cache.

### External API Integration Pattern

The system integrates with three primary external data sources:

| API                | Purpose                                   | Service Implementation  | Rate Limiting                      |
|--------------------|-------------------------------------------|-------------------------|------------------------------------|
| **MOEX ISS**       | Russian market yields, bond data          | `zcyc_service.py`       | Standard HTTP throttling           |
| **RuData/Interfax**| Bond reference data, cashflows, calculations | `rudata_service.py`  | 5 requests/second, max 100 items per filter |
| **Yahoo Finance**  | Historical price data for spectral analysis | `yfinance` via `spectral_regime_service.py` | Library-managed |

## Deployment Architecture

### Dual-Host Deployment Model

Production environment layout:

- GitHub Repository: `github.com/russiankendricklamar/zetaterminal`
- CI/CD Pipelines: `.github/workflows/`
  - `pages.yml` — frontend build and deploy
  - `deploy-backend.yml` — backend deploy to Railway
- Frontend build:
  - Node.js 20
  - `npm ci` in `./frontend`
  - `npm run build` using `vite.config.ts`
  - artifacts in `dist/`
- Backend build:
  - Python 3.11.0
  - Railway deploy action
  - `Procfile`: `uvicorn src.main:app`

Runtime:

- GitHub Pages: `russiankendricklamar.github.io/zetaterminal/`
- Railway platform: `backend-production.up.railway.app`
- `VITE_API_BASE_URL` used by frontend to call backend API

### Key Configuration Files

| File                          | Purpose                         | Key Settings                                                                 |
|-------------------------------|---------------------------------|-------------------------------------------------------------------------------|
| `.github/workflows/pages.yml` | Frontend deployment pipeline    | Triggers on push to main, builds with Vite, deploys to gh-pages branch        |
| `.github/workflows/deploy-backend.yml` | Backend deployment pipeline | Path filter for `backend/**`, deploys to Railway                              |
| `frontend/vite.config.ts`     | Vite build configuration        | Base path `/zetaterminal/`, terser minification, code splitting     |
| `backend/Procfile`            | Railway process configuration   | `web: uvicorn src.main:app --host 0.0.0.0 --port $PORT`                       |
| `backend/start.sh`            | Backend startup script          | Installs requirements, starts Uvicorn server                                  |
| `frontend/404.html`           | SPA redirect handler            | Converts 404 errors to hash-based routes for client-side routing              |

Environment variables:

- Frontend: `VITE_API_BASE_URL` set at build time to point to Railway backend.
- Backend: `CORS_ORIGINS`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY` configured in Railway.

## Core Mathematical Models

The system implements several sophisticated quantitative models.

### Financial Pricing Models

- **Bond DCF**: Discounted cash flow valuation with multiple day count conventions (Actual/365F, Actual/360, 30/360).
- **Black-Scholes-Merton**: European option pricing with Greeks (Delta, Gamma, Vega, Theta, Rho).
- **Heston Model**: Stochastic volatility model for path-dependent options.
- **Variance Gamma (VG)**: Lévy process model for capturing jumps and skewness.
- **CGMY**: Generalized Lévy model with flexible tail behavior.

### Statistical Models

- **GARCH(1,1)**: Conditional heteroskedasticity modeling for volatility forecasting (implemented in `compute_service.py`).
- **Hidden Markov Models**: 2–4 state regime detection with Baum-Welch (EM) parameter estimation, Viterbi decoding, forward-backward smoothing.
- **Spectral Regime Analysis**: Prony method for spectral factorization, ACF decomposition, pole clustering.

### Optimization Models

- **CCMV (Continuous-time Covariance Matrix Variation)**: Portfolio optimization under stochastic volatility.
- **HJB (Hamilton-Jacobi-Bellman)**: Dynamic portfolio optimization via PDE methods.
- **Markowitz Mean-Variance**: Classical portfolio optimization with quadratic programming.

## Security and API Integration

### Credential Management

The system implements secure credential storage for external API integrations:

- **RuData API**: Credentials stored in `localStorage` with base64 obfuscation (frontend) and environment variables (backend).
- **Settings Page**: UI for entering and testing API credentials in `frontend/src/pages/Settings.vue`.
- **Connection Testing**: Credentials validated before saving via `/api/rudata/test-connection` endpoint.

### CORS Configuration

The backend FastAPI application configures CORS middleware to allow cross-origin requests from the GitHub Pages frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

# Architecture

This space describes the overall system architecture of Zeta Terminal, including the separation between frontend and backend components, communication patterns, deployment infrastructure, and key architectural decisions.

For detailed information about specific layers (in separate docs):

- Frontend component organization, routing, and UI framework: see `Frontend Architecture`
- Backend API structure, service layer, and repository pattern: see `Backend Architecture`
- External API integrations and data pipelines: see `Data Flow & Integration`

## Purpose and Scope

This space focuses on:

- High-level system overview.
- Frontend–backend separation of responsibilities.
- Communication patterns between layers.
- Deployment architecture (GitHub Pages + Railway).
- Key architectural decisions and their trade-offs.

## System Overview

Zeta Terminal follows a **decoupled client–server architecture** with a Vue.js 3 SPA frontend communicating with a Python FastAPI backend over HTTPS. The frontend is statically hosted on GitHub Pages, while the backend runs on Railway PaaS.

High-level layers:

- Client (Web Browser, Mobile Device).
- Vue.js 3 SPA:
  - `index.html` + Vite build output (`frontend/dist/`).
  - `main.ts` (entry point).
  - `router/index.ts` (hash-based routing).
  - Pinia stores in `src/stores/*`.
  - Layout components: `MainLayout.vue`, `Sidebar.vue`, `CommandPalette.vue`.
  - Page components: `Portfolio.vue`, `RegimeSpace3D.vue`, `Terminal.vue`, `BondValuation.vue`, `OptionPricing.vue`, `SwapValuation.vue`, `Settings.vue`.
- TypeScript services:
  - `multivariateHmmService.ts`
  - `spectralRegimeService.ts`
  - `bondService.ts`
  - `rudataService.ts`
- Axios HTTP client configured with `VITE_API_BASE_URL`.

Backend:

- Uvicorn ASGI server.
- `FastAPI()` application in `backend/src/main.py`.
- CORS middleware.
- API routers in `backend/src/api/`:
  - `bond.py`, `swap.py`, `forward.py`
  - `compute.py`
  - `multivariate_hmm.py`
  - `spectral_regime.py`
  - `zcyc.py`
  - `rudata.py`
  - `database.py`
  - `portfolio.py`
  - `backtest.py`
  - `stress.py`
  - `ccmv.py`
  - `hjb.py`
  - `market_data.py`
- Service layer in `backend/src/services/`:
  - `ComputeService` (GARCH(1,1) calculations).
  - `SpectralRegimeAnalyzer` (Prony Method & ACF).
  - `RuDataService` (RuData API client).
  - `ZCYCService` (yield curve processing).
- Data access layer (`backend/src/database/`):
  - `client.py` with `get_supabase_client()`.
  - `repositories.py`:
    - `BondValuationRepository`
    - `PortfolioRepository`
    - `MarketDataRepository`
    - `FileRepository`

External infrastructure:

- Supabase: PostgreSQL + TimescaleDB, plus Storage (Parquet).
- MOEX ISS API (`iss.moex.com`) for market yields & ZCYC.
- RuData/Interfax API (`dh2.efir-net.ru`) for bond reference data.
- Yahoo Finance (via `yfinance`) for historical prices.

CI/CD:

- GitHub Actions workflows:
  - `pages.yml` — frontend deployment to GitHub Pages.
  - `deploy-backend.yml` — backend deployment to Railway.

## Frontend–Backend Separation

The system employs a strict separation between presentation and business logic.

### Frontend Responsibilities

The Vue.js 3 frontend (`frontend/` directory) is responsible for:

- **User Interface Rendering**:
  - Glass-morphism design system in `frontend/src/components/Layout/MainLayout.vue`.
  - Core layout: `MainLayout.vue`, `Sidebar.vue`, `CommandPalette.vue`.
- **Client-Side Routing**:
  - Hash-based routing via `vue-router` and `createWebHashHistory` in `frontend/src/router/index.ts`.
- **State Management**:
  - Pinia stores for portfolio data, risk metrics, swap registries and UI state.
- **3D Visualizations**:
  - Three.js renderers for regime space, volatility surfaces, correlation matrices.
- **Input Validation**:
  - Form-level validation and formatting before API submission.
- **Caching**:
  - `localStorage` for user preferences and RuData credentials (see `frontend/src/services/rudataService.ts`).

### Backend Responsibilities

The FastAPI backend (`backend/` directory) handles:

- **Business Logic**:
  - Financial calculations (DCF, Black–Scholes, GARCH, HMM, spectral analysis, optimization).
- **Data Persistence**:
  - Repository pattern for database operations in `backend/src/database/repositories.py`.
- **External Integrations**:
  - MOEX ISS, RuData/Interfax, Yahoo Finance.
- **Authentication**:
  - Token-based auth for RuData API in `backend/src/services/rudata_service.py`.
- **Computational Services**:
  - Heavy numerical computations (spectral analysis, regime detection, optimization).
- **File Export**:
  - Parquet file generation and Supabase Storage uploads.

## Communication Patterns

### REST API over HTTPS

All frontend–backend communication uses RESTful HTTP requests with JSON payloads. The API base URL is configured with `VITE_API_BASE_URL` at frontend build time.

Typical flow (example: bond valuation):

1. Vue component (e.g., `BondValuation.vue`) calls a TypeScript service method, e.g. `bondService.valuateBond(params)`.
2. Service uses Axios (configured with `VITE_API_BASE_URL`) to send `POST /api/bond/valuate` with JSON body `{isin, valuation_date, ...}`.
3. FastAPI router `backend/src/api/bond.py`:
   - Validates request using Pydantic models.
   - Delegates to bond pricing logic (e.g. `bond_pricing.calculate_dcf()`).
4. Repository (`BondValuationRepository`) reads/writes data in Supabase.
5. FastAPI returns JSON response with results:
   - `clean_price`, `dirty_price`, `duration`, etc.
6. Service parses response into typed result.
7. Vue component updates reactive state and displays results.

### API Router Structure

The backend exposes multiple routers, each responsible for a specific domain:

| Router Prefix                | Module                                   | Key Endpoints                        | Description                                   |
|-----------------------------|------------------------------------------|--------------------------------------|-----------------------------------------------|
| `/api/bond/*`              | `backend/src/api/bond.py`               | `POST /valuate`, `GET /market-yield` | Bond valuation, DCF calculations              |
| `/api/swap/*`              | `backend/src/api/swap.py`               | `POST /valuate`                      | IRS, CDS, CCS swap valuation                  |
| `/api/forward/*`           | `backend/src/api/forward.py`            | `POST /valuate`                      | Forward contract pricing                      |
| `/api/compute/*`           | `backend/src/api/compute.py`            | `POST /garch`, `POST /statistics`    | GARCH(1,1) and statistical calculations       |
| `/api/multivariate-hmm/*`  | `backend/src/api/multivariate_hmm.py`   | `GET /chart-data`, `GET /transition-matrix` | HMM regime analysis                   |
| `/api/spectral-regime/*`   | `backend/src/api/spectral_regime.py`    | `POST /analyze`, `GET /available-assets` | Spectral density analysis, Prony method |
| `/api/zcyc/*`              | `backend/src/api/zcyc.py`               | `GET /fetch`, `POST /interpolate`    | Zero-coupon yield curves from MOEX            |
| `/api/rudata/*`            | `backend/src/api/rudata.py`             | `POST /test-connection`, `POST /query` | RuData/Interfax API integration            |
| `/api/database/*`          | `backend/src/api/database.py`           | `POST /export/registry/parquet`      | Database operations, Parquet export           |
| `/api/portfolio/*`         | `backend/src/api/portfolio.py`          | `GET /`, `POST /create`              | Portfolio management                          |
| `/api/backtest/*`          | `backend/src/api/backtest.py`           | `POST /run`                          | Strategy backtesting                          |
| `/api/stress/*`            | `backend/src/api/stress.py`             | `POST /test`                         | Stress testing                                |
| `/api/ccmv/*`              | `backend/src/api/ccmv.py`               | `POST /optimize`                     | CCMV optimization                             |
| `/api/hjb/*`               | `backend/src/api/hjb.py`                | `POST /solve`                        | HJB equation solver                           |
| `/api/market-data/*`       | `backend/src/api/market_data.py`        | `GET /fetch`                         | Market data retrieval                         |

## Deployment Architecture

### Static Frontend Hosting

The Vue.js application is built using Vite and deployed to GitHub Pages via GitHub Actions (`.github/workflows/pages.yml`).

Build pipeline:

1. Trigger: push to `main`.
2. Actions:
   - `actions/checkout@v4`.
   - `actions/setup-node@v4` with Node.js 20.
   - `npm ci` in `./frontend`.
   - `npm run build` using `frontend/vite.config.ts`.
3. Deploy:
   - `peaceiris/actions-gh-pages` deploys `frontend/dist/` to `gh-pages` branch.

Runtime characteristics:

- Base path: `/zetaterminal/` (configured in `frontend/vite.config.ts`).
- Code splitting:
  - Separate chunks for vendor libraries, chart libraries, and PDF generation.
- Hash routing:
  - `createWebHashHistory` in `router/index.ts` to avoid 404s on static host.
- SPA redirect:
  - `frontend/404.html` redirects all 404 to root, preserving hash route.

User flow:

- Browser loads `index.html` from GitHub Pages.
- Vue app initializes with `main.ts`.
- Vue Router uses hash-based navigation (`/#/portfolio`, `/#/terminal`, etc).

### Backend Hosting on Railway

The FastAPI backend is deployed to Railway using `.github/workflows/deploy-backend.yml`.

Deployment pipeline:

1. Trigger: push to `main` with changes under `backend/**`.
2. Actions:
   - `actions/checkout@v4`.
   - `bervProject/railway-deploy@v1` using `$RAILWAY_TOKEN`.
3. Railway build:
   - Detects Python 3.11.0.
   - Executes `pip install -r requirements.txt`.
   - Runs `backend/start.sh` (or `Procfile`).

Runtime:

- `backend/start.sh`:
  - Installs dependencies.
  - Starts Uvicorn:
    - `uvicorn src.main:app --host 0.0.0.0 --port $PORT`.
- Alternatively `backend/Procfile`:
  - `web: uvicorn src.main:app --host 0.0.0.0 --port $PORT`.

Environment variables:

- `PORT` (provided by Railway).
- `CORS_ORIGINS` (allowed origins, default `*`).
- `DATABASE_URL` (PostgreSQL connection).
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` (Supabase).

CORS configuration in `backend/src/main.py`:

- Uses `CORSMiddleware` with `allow_origins`, `allow_methods`, `allow_headers`, `allow_credentials`.

## Technology Stack

### Frontend Stack

Core framework and tooling:

- Vue 3.4.15 — Composition API, `script setup`.
- TypeScript 5.3.3 — type safety.
- Vite 5.0.8 — dev server & bundler.

Routing & state:

- Vue Router 4.6.4 — `createWebHashHistory` routing.
- Pinia 2.1.7 — stores (e.g. `portfolioStore`, `riskMetricsStore`, `swapRegistryStore`).

UI styling:

- Tailwind CSS 3.4.1 — utility-first CSS.
- PostCSS 8.4.32 — Autoprefixer.
- Custom glass design with CSS variables.

Visualization:

- Three.js 0.182.0 — 3D graphics engine.
- `three-orbit-controls` — camera manipulation.
- Chart.js 4.4.1 — 2D charts.
- ECharts 6.0.0 — advanced charting.

Other libs:

- KaTeX 0.16.27 — LaTeX formulas in documentation pages.
- XLSX 0.18.5 — Excel import/export of registries.
- `html2pdf.js` 0.12.1 — PDF generation.
- Axios 1.6.5 — HTTP client configured with `VITE_API_BASE_URL`.

### Backend Stack

Web framework:

- FastAPI 0.104.0+ — async ASGI app.
- Uvicorn 0.24.0+ — ASGI server (often with `uvloop`).

Scientific computing:

- NumPy 1.24.0+ — core numerical arrays.
- Pandas 2.0.0+ — tabular & time series.
- SciPy 1.11.0+ — optimization & statistics.
- CVXPY 1.3.0+ — convex optimization.

Data storage:

- Supabase client 2.0.0+ — PostgreSQL access.
- PyArrow 14.0.0+ — Parquet I/O.

HTTP & utilities:

- `requests` 2.31.0+ — sync HTTP.
- `httpx` 0.25.0+ — async HTTP.
- `aiohttp` 3.9.0+ — async client for MOEX & RuData.
- `yfinance` 0.2.0+ — Yahoo Finance data.
- `python-dotenv` 1.0.0+ — env management.
- `python-dateutil` 2.8.2+ — date parsing.

## Key Architectural Decisions

### 1. Hash-Based Routing for Static Hosting

**Decision**: Use `createWebHashHistory` for Vue Router.

**Rationale**:

- GitHub Pages is a static file host without server-side routing.
- Hash routing ensures all routes are handled on the client without server configuration.
- `404.html` redirect script makes deep links (`/#/route`) work.

**Trade-offs**:

- ✅ Works on any static host out-of-the-box.
- ✅ No server-side routing required.
- ❌ URLs contain `#` (less clean).
- ❌ No server-side rendering (SSR).

### 2. Repository Pattern for Data Access

**Decision**: Implement repository classes (`BondValuationRepository`, `PortfolioRepository`, etc.) instead of direct DB access in API routes.

**Rationale**:

- Separates data access from routing logic.
- Simplifies testing and mocking.
- Enforces consistent error handling and CRUD patterns.

**Benefits**:

- Clear separation of concerns.
- Easier to swap DB implementations.
- Better testability without a live database.

### 3. Parquet for Registry Export

**Decision**: Use Apache Parquet (via PyArrow) for exporting registries to Supabase Storage.

**Rationale**:

- Columnar storage with strong compression.
- Preserves data types (dates, decimals) unlike CSV.
- Efficient for analytics and downstream processing.

**Benefits**:

- 5–10x smaller files compared to CSV (typical).
- Fast columnar queries.
- Broad ecosystem support (Pandas, DuckDB, etc.).

### 4. Service Layer for Business Logic

**Decision**: Use service classes (`ComputeService`, `SpectralRegimeAnalyzer`, `RuDataService`) to encapsulate business logic.

**Rationale**:

- Keep FastAPI routes thin and focused on I/O and validation.
- Make business logic reusable and testable outside HTTP context.

**Pattern**:

- API route (validate) → Service (business logic) → Repository (data access) → Database.

### 5. Async/Await for External API Calls

**Decision**: Use `async`/`await` with `aiohttp` for MOEX, RuData, Yahoo Finance integrations.

**Rationale**:

- External APIs have latency and rate limits.
- Async I/O allows concurrent requests without blocking threads.

**Benefits**:

- Non-blocking network I/O.
- Better throughput under concurrent load.
- Easier to implement rate limiting with `asyncio.sleep()`.

### 6. Environment-Based Configuration

**Decision**: All environment-specific configuration via env vars.

Frontend:

- `VITE_API_BASE_URL` — backend endpoint at build time.

Backend:

- `CORS_ORIGINS` — allowed origins.
- `DATABASE_URL` — DB connection string.
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` — Supabase credentials.
- `PORT` — server port (provided by Railway).

**Rationale**:

- Follows 12-factor app principles.
- Same codebase works for dev/staging/prod by changing env only.

## Component Communication Flow

End-to-end flow (example: market regime analysis, bond valuation):

1. **User Interaction**:
   - User clicks “Run analysis” in `RegimeSpace3D.vue` or submits a form in `BondValuation.vue`.
2. **Presentation Layer**:
   - Vue component triggers store actions or directly calls TS service.
3. **State Management**:
   - Pinia stores hold portfolio, risk metrics, swap registries, etc.
4. **Service Layer (TS)**:
   - `multivariateHmmService.ts` for HMM-related endpoints.
   - `bondService.ts` for bond valuation.
   - `rudataService.ts` for RuData connectivity.
   - Uses Axios client with `baseURL = VITE_API_BASE_URL`.
5. **API Gateway (FastAPI)**:
   - Corresponding routers handle HTTP requests (`multivariate_hmm.py`, `bond.py`, `rudata.py`, etc.).
6. **Business Logic (Python Services)**:
   - HMM processing, bond pricing, RuData client logic.
7. **Data Access (Repositories)**:
   - CRUD operations on Supabase: insert/read valuations, portfolios, market data.
8. **External Systems**:
   - MOEX ISS for yields.
   - RuData for reference data.
   - Supabase PostgreSQL & Storage for persistence.
9. **Response Flow**:
   - Results returned to frontend as JSON.
   - TS services parse and update Pinia stores.
   - Vue components re-render and show updated analytics.

## Navigation and User Flow

Navigation is implemented in `frontend/src/components/Layout/Sidebar.vue` and `CommandPalette.vue`.

Main elements:

- **Sidebar Menu**:
  - Expandable tool groups: Portfolio Analytics, Fixed Income, Derivatives, Market Regimes, Forwards, Swaps, Risk Management, System.
  - Routes like:
    - `/portfolio`
    - `/terminal`
    - `/bond-valuation`
    - `/zcyc-viewer`
    - `/pricing/options`
    - `/analytics/volatility`
    - `/backtest`
    - `/stress`
    - `/settings`
- **Command Palette**:
  - Global shortcut (⌘K / Ctrl+K).
  - Quick search and navigation across all routes.
- **Breadcrumbs**:
  - Built from route metadata in `router/index.ts` for context within complex flows.

## Error Handling Strategy

### Frontend Error Handling

- API errors:
  - Handled in TS service layer, returned as typed error objects.
- Network failures:
  - Axios interceptors manage timeouts and connectivity errors.
- Validation errors:
  - Form-level checks before sending API requests.
- User feedback:
  - Error messages rendered in glass-style cards with red accents.

### Backend Error Handling

- Pydantic validation:
  - Automatic body validation with detailed 422 errors.
- HTTP exceptions:
  - `HTTPException` for 4xx/5xx codes (400, 404, 500).
- External API failures:
  - `try/except` with fallbacks (e.g., alternative ZCYC construction).
- Database errors:
  - Repository layer catches and logs DB exceptions; returns consistent error structures.
