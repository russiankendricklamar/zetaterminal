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


## Frontend Application
