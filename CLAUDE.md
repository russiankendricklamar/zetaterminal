# Zeta Terminal — CLAUDE.md

## Vision: Open-Source Aladdin

Open-source аналог **BlackRock Aladdin** для российского рынка. Количественный анализ, управление портфелем, оценка рисков — без enterprise-ценника.

### Реализованные модули Aladdin

- **Risk** — VaR/CVaR (parametric, historical, Monte Carlo), stress testing (MC + adversarial DRO + EVT + 5 historical crises), GARCH, HMM, component VaR
- **Portfolio** — Markowitz, Max Sharpe, CVaR, Risk Parity, Kelly, Black-Litterman, CCMV, HJB + Brinson-Fachler/factor attribution + PCA/RMT eigenportfolio
- **Fixed Income** — bond valuation, ZCYC curves, Cbonds API, day count conventions
- **Derivatives** — BSM/Heston/VG/CGMY options, swaps (valuation + stress), forwards (curves + Greeks)
- **Volatility** — SABR/SVI 3D surfaces, calibration
- **Regimes** — HMM 3D, Prony/ACF spectral detection
- **Backtesting** — Monte Carlo, historical replay, walk-forward optimization, transaction costs
- **Data Platform** — 12 источников: MOEX ISS, ZCYC, RuData, Cbonds, FRED, ECB, ЦБ РФ, SEC EDGAR, OpenFIGI, CoinGecko, Polygon/AV/12Data, Yahoo Finance

### Roadmap (TODO)

| Приоритет | Модуль | Описание |
|-----------|--------|----------|
| P1 | **Reporting** | PDF/Excel генерация отчётов (html2pdf.js + xlsx) |
| P1 | **AI Copilot** | Claude Issues auto-responder, расширение |
| P2 | **Trading & Execution** | Order routing, execution algorithms |
| P2 | **Compliance** | Regulatory checks, limits monitoring |

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

| Source | Purpose | Implementation | Auth |
|--------|---------|---------------|------|
| MOEX ISS | Акции, свечи, стаканы, индексы, фьючерсы OI | `moexalgo_service.py` | None |
| ZCYC | Кривая бескупонной доходности, дисконт-факторы | `zcyc_service.py` | None |
| RuData/Interfax | Облигации, кэшфлоу, расчёты, поиск | `rudata_service.py` (5 req/s) | Login |
| Cbonds | Эмиссии, котировки, рейтинги, индексы | `cbonds_service.py` (30 req/min) | Login |
| FRED | GDP, CPI, безработица, макро-индикаторы | `macro_data_service.py` | API Key |
| ECB/Frankfurter | Валютные курсы EUR | `macro_data_service.py` | None |
| ЦБ РФ | Курсы, ключевая ставка, RUONIA, металлы | `macro_data_service.py` | None |
| SEC EDGAR | Filings, XBRL, company facts | `macro_data_service.py` | User-Agent |
| OpenFIGI | Ticker→FIGI идентификаторы | `macro_data_service.py` | API Key |
| CoinGecko/CoinGap | Крипто рынки, арбитраж | `crypto_data_service.py` | Optional |
| Polygon/AV/12Data | Глобальные акции, опционы, новости | `market_feeds_service.py` | API Key |
| Yahoo Finance | Глобальные акции, FX, крипто | `yfinance_service.py` | None |

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
