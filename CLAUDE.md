# Zeta Terminal — CLAUDE.md

## Vision: Open-Source Aladdin

Open-source аналог **BlackRock Aladdin** для российского рынка. Количественный анализ, управление портфелем, оценка рисков — без enterprise-ценника.

### Маппинг модулей: Aladdin → Zeta Terminal

| Aladdin Module | Zeta Terminal | Статус |
|---------------|---------------|--------|
| **Risk** — VaR, stress, factors | `/portfolio` VaR/CVaR, `/stress`, GARCH, HMM | Частично (P0) |
| **Portfolio** — optimization, attribution | `/portfolio`, `/ccmv`, `/hjb`, Markowitz, BL | Частично (P0) |
| **Fixed Income** — OAS, duration, curves | `/bond-valuation`, `/zcyc-viewer` | Готово |
| **Derivatives** — options, swaps, forwards | `/pricing/options` BSM/Heston/VG/CGMY, swaps, forwards | Готово |
| **Volatility** — surfaces, calibration | `/analytics/volatility` SABR/SVI 3D | Готово |
| **Regimes** — detection, spectral | `/terminal` Prony/ACF, `/regimes` HMM 3D | Готово |
| **Backtesting** | `/backtest` | Частично (P0) |
| **Trading & Execution** | — | P2 |
| **Compliance** | — | P2 |
| **Data Platform** | MOEX ISS, RuData, Yahoo Finance | Частично (P1) |
| **Reporting** | PDF (html2pdf.js), Excel (xlsx) | Частично (P1) |
| **AI Copilot** | Claude Issues auto-responder | Минимально (P1) |

---

## Tech Stack

### Frontend
Vue 3.4 + TypeScript 5.3 + Vite 5.0 + Tailwind 3.4 + Pinia 2.1

Визуализация: Three.js 0.182 (3D), Chart.js 4.4 + ECharts 6.0 (2D), KaTeX 0.16
Данные: Axios 1.6, XLSX 0.18, html2pdf.js 0.14
Desktop: Tauri 2.0 (опционально)

### Backend
FastAPI 0.115 + Uvicorn 0.34 + Python 3.11

Вычисления: NumPy 1.26, Pandas 2.2, SciPy 1.14, CVXPy 1.3
БД: SQLAlchemy 2.0 (async) + asyncpg + Neon PostgreSQL
HTTP: aiohttp 3.9, yfinance 0.2
Auth: PyJWT 2.8 + bcrypt + Fernet (cryptography 43)
Безопасность: slowapi (rate limiting), Pydantic v2 (validation)

---

## Application Routes (42 routes)

**Public:** `/` (Home), `/auth`, `/docs` (KnowledgeBase), `/terminal`, `/profile`

**Portfolio & Risk:** `/portfolio`, `/greeks`, `/stress`, `/backtest`, `/reports`, `/optimization`

**Fixed Income:** `/fixed-income`, `/bond-valuation`, `/zcyc-viewer`, `/bond-report`, `/vanila-bond-report/:isin?`, `/floater-bond-report/:isin?`, `/repo`

**Derivatives:** `/pricing/options`, `/pricing/options/models`, `/pricing/options/greeks`, `/pricing/options/portfolio`, `/valuation/swaps`, `/swap-greeks`, `/stress/swaps`, `/valuation/forwards`, `/forwards/curve`, `/forwards/greeks`, `/forwards/basis`, `/hedging`

**Analytics:** `/analytics/volatility`, `/analytics/pnl`, `/analytics/sharpe-stats`, `/analytics/realized-kernels`, `/analytics/har-model`, `/analytics/factor-analysis`, `/analytics/eigenportfolio`, `/analytics/pbo`, `/analytics/alpha-stacking`, `/analytics/meta-labeling`, `/analytics/adversarial-stress`

**Regimes:** `/regimes`, `/regime-details`, `/spectral-regimes`

**Admin:** `/admin` (requiresAdmin), `/settings`

Navigation: Sidebar + Command Palette (`Cmd+K`). Hash-based routing. All lazy-loaded.

---

## Design System — BRUTALIST (DO NOT DEVIATE)

### Colors (CSS variables ONLY, never hardcode hex)
```css
--bg-primary: #050505    --bg-secondary: #0A0A0A    --bg-tertiary: #111111
--accent-red: #DC2626    --accent-red-hover: #ef4444
--border-dark: #1a1a1a   --border-medium: #262626   --border-light: #333333
--text-primary: #f5f5f5  --text-secondary: #a3a3a3  --text-tertiary: #737373  --text-muted: #525252
```
Semantic: `#22c55e` (profit), `#DC2626` (loss), `#f59e0b` (warning)

### Typography
- `.font-anton` — Hero headings (ALL CAPS)
- `.font-oswald` — UI labels, navigation, buttons
- `.font-mono` — Numbers, data, metadata

### Hard Rules
- Border radius: **3–6px max** — never `rounded-full`
- No shadows, gradients, glassmorphism, light mode, emoji in UI
- Arrows: `→` — not icon libraries
- Dark-only forever
- Source of truth: `frontend/src/assets/styles/main.css` (1,543 LOC design system)

---

## External Data Sources

| Source | Purpose | Implementation |
|--------|---------|---------------|
| MOEX ISS | Market yields, ZCYC | `zcyc_service.py` |
| RuData/Interfax | Bond reference, cashflows | `rudata_service.py` (5 req/s) |
| Yahoo Finance | Historical prices | `yfinance` in services |

---

## Infrastructure

**Frontend:** GitHub Pages (`russiankendricklamar.github.io/zetaterminal/`), hash routing, 404.html SPA redirect
**Backend:** Render free tier (sleeps after 15min idle, warmupBackend() on mount)
**Database:** Neon PostgreSQL, auto-created tables via `init_db()`

### Environment Variables
```
VITE_API_BASE_URL    # Frontend → Render backend URL
DATABASE_URL         # postgresql+asyncpg://...neon.tech/neondb?sslmode=require
JWT_SECRET           # min 32 chars, validated at startup
CORS_ORIGINS         # allowed origins (restricted in prod)
ANTHROPIC_API_KEY    # GitHub Actions: claude_responder.py
```

---

## Architecture Pattern

**Backend:** Router (`api/`) → Service (`services/`) → Repository (`database/`)
- 40 routers, 40 services, strict layering — no DB calls in routers
- `asyncio.to_thread()` for CPU-heavy sync calculations
- `FinancialBaseModel` auto-rejects NaN/Inf, enforces Field bounds
- 3-tier errors: ValueError→400, RuntimeError→400, Exception→500
- Rate limiting on heavy endpoints (`@limiter.limit`)

**Frontend:** Page → Service → Backend API
- Composition API (`<script setup lang="ts">`) — no Options API
- `getApiBaseUrl()` + `getApiHeaders()` — never hardcode URLs
- Pinia stores for shared state (immutable patterns)
- Composables (`use*`) for reusable logic

**Security:** JWT (HS256) + IP Ban + Rate Limiting + Fernet-encrypted API keys + bcrypt passwords

---

## Code Review Checklist

**Python:** `ruff check` clean, type hints, Pydantic models, Router→Service→Repository, `from e` on re-raise, no secrets in code, reference tests for financial math

**Vue/TS:** `eslint` clean, `<script setup lang="ts">`, CSS variables only, `getApiBaseUrl()`, no `any`, no `console.log`, brutalist design rules

**Security:** no secrets in source, parameterized SQL only, CORS restricted, rate limiting on auth + heavy endpoints
