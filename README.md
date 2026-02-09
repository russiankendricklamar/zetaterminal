# Overview

This document provides a high-level introduction to the Stochastic Dashboard / v1 system: its purpose, architecture, technology stack, and key modules. This page serves as the entry point to understanding the codebase structure and how the major components interact.

For detailed information about specific subsystems, see:

- Frontend application structure: [Frontend Application] (#frontend-application)
- Backend services and APIs: [Backend Services]
- Deployment pipelines and infrastructure: [Deployment & Operations]
- Development setup and workflows: [Development Guide]

## System Purpose

Stochastic Dashboard / v1 is a production-ready quantitative financial analysis platform designed for:

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
| **3D Regime Space**     | 47.68      | HMM market regime detection with Three.js 3D visualization         | `RegimeSpace3D.vue`     | `/api/multivariate-hmm/*`             | [RegimeSpace3D Component]() |
| **Zeta Terminal**       | 18.54      | Spectral regime analysis using Prony method and ACF decomposition  | `Terminal.vue`          | `/api/spectral-regime/*`              | [Market Analysis Terminal]() |
| **ZCYC Viewer**         | 14.22      | Zero-coupon yield curve visualization with MOEX integration        | `ZCYCViewer.vue`        | `/api/zcyc/*`                         | [ZCYC Viewer]()                         |
| **Documentation**       | 12.81      | KaTeX-rendered mathematical formulas and model explanations        | `Documentation.vue`     | N/A                                    | [Reporting & Documentation]() |
| **CCMV/HJB Optimization** | 9.12     | Portfolio optimization with GARCH volatility models                | `CCMVOptimization.vue`  | `/api/compute/garch`, `/api/ccmv/*`, `/api/hjb/*` | [Portfolio Optimization]() |

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

- GitHub Repository: `github.com/russiankendricklamar/stochastic-dashbord-v1`
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

- GitHub Pages: `russiankendricklamar.github.io/stochastic-dashbord-v1/`
- Railway platform: `backend-production.up.railway.app`
- `VITE_API_BASE_URL` used by frontend to call backend API

### Key Configuration Files

| File                          | Purpose                         | Key Settings                                                                 |
|-------------------------------|---------------------------------|-------------------------------------------------------------------------------|
| `.github/workflows/pages.yml` | Frontend deployment pipeline    | Triggers on push to main, builds with Vite, deploys to gh-pages branch        |
| `.github/workflows/deploy-backend.yml` | Backend deployment pipeline | Path filter for `backend/**`, deploys to Railway                              |
| `frontend/vite.config.ts`     | Vite build configuration        | Base path `/stochastic-dashbord-v1/`, terser minification, code splitting     |
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
