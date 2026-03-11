# Bibliography — Source Library Reference

Available books in user's library. Agent should cite these when implementing models.

## Primary Sources (PDF available locally)

### Stochastic Financial Mathematics
1. **Ширяев А.Н.** "Основы стохастической финансовой математики. Том 1. Факты. Модели." ФАЗИС, 1998. 512 с.
   - Covers: Financial structures, random walk, EMH, CAPM, APT, ARMA/GARCH models, Lévy processes, fractals, Ito calculus, diffusion models, statistical analysis
   - Key chapters: I§2 (Markowitz, CAPM, APT), II (discrete stochastic models), III (continuous models, Ito, SDE), IV (statistical analysis)

2. **Ширяев А.Н.** "Основы стохастической финансовой математики. Том 2. Теория." ФАЗИС, 1998. 544 с.
   - Covers: Arbitrage theory, hedging, martingale pricing, Girsanov theorem, BSM derivation, American/European options, bond models
   - Key chapters: V (arbitrage, FTAPs), VI (hedging calculations), VII (continuous-time arbitrage), VIII (BSM, American options, bond options)

### Probability Theory
3. **Ширяев А.Н.** "Вероятность-1" МЦНМО, 2004. 520 с.
   - Elementary probability, mathematical foundations, limit theorems
   - Key: Bernoulli scheme, LLN, CLT, conditional expectations

4. **Ширяев А.Н.** "Вероятность-2: Суммы и последовательности..." МЦНМО.
   - Martingales, Markov chains, stationary processes

### Random Processes
5. **Булинский А.В., Ширяев А.Н.** "Теория случайных процессов" ФИЗМАТЛИТ, 2005. 408 с.
   - Comprehensive: distributions, Poisson/Wiener processes, Brownian motion, martingales, stochastic integrals, SDE, Markov processes
   - Key chapters: II (independent increments, Wiener), III (BM properties), IV-V (martingales, stochastic integrals)

6. **Липцер Р.Ш., Ширяев А.Н.** "Статистика случайных процессов: нелинейная фильтрация" Наука, 1974. 696 с.
   - Optimal filtering (Kalman-Bucy), sequential estimation, martingale theory
   - Application: hidden state estimation, signal extraction from noisy data

### Limit Theorems
7. **Жакод Дж., Ширяев А.Н.** "Предельные теоремы для случайных процессов" Т.1-2.
   - Convergence of stochastic processes, semimartingale theory
   - Application: theoretical foundation for approximation of continuous models by discrete

### Mathematical Statistics
8. **Боровков А.А.** "Математическая статистика" 2010.
   - Estimation theory, hypothesis testing, regression
   - Application: parameter estimation for financial models

### Derivatives (English)
9. **Hull J.C.** "Options, Futures, and Other Derivatives" 11th Ed, Pearson 2022. 882 pages.
   - THE standard practitioner reference
   - Key chapters: 14 (Ito), 15 (BSM), 19 (Greeks), 20 (Vol smiles), 21 (Numerical methods), 22 (VaR/ES), 23 (EWMA/GARCH), 26 (Exotics), 27 (Climate/ESG), 28 (Martingales/Measures), 29 (IR derivatives), 31-32 (Short rate models), 33 (HJM/LMM), 34 (Swaps/Exotics)

### Problem Sets
10. **Прохоров А.В., Ушаков В.Г., Ушаков Н.Г.** "Задачи по теории вероятностей" 1986.
11. **Ширяев А.Н., Эрлих И.Г., Яськов П.А.** "Вероятность в теоремах и задачах"
12. **Мешалкин Л.Д.** Сборник задач (1963)

## Citation Format for Docstrings

When implementing a model, cite as:
```python
def calculate_bsm_price(S, K, T, r, sigma):
    """Black-Scholes-Merton European option pricing.

    References:
        Black, Scholes (1973). J. Political Economy, 81, 637-659.
        Merton (1973). Bell J. Economics, 4, 141-183.
        Hull (2022) Ch.15, eq 15.20-15.21.
        Ширяев (1998) Т.2, Гл.VIII, §1b.
    """
```

## Key Papers by Topic

### Options Pricing
- Black, Scholes (1973) — BSM formula
- Merton (1973) — Continuous-time option pricing
- Cox, Ross, Rubinstein (1979) — Binomial model
- Heston (1993) — Stochastic volatility
- Hagan et al. (2002) — SABR model

### Portfolio Theory
- Markowitz (1952) — Mean-variance optimization
- Sharpe (1964), Lintner (1965) — CAPM
- Ross (1976) — APT
- Black, Litterman (1992) — BL model
- Maillard, Roncalli, Teïletche (2010) — Risk parity

### Risk Management
- RiskMetrics (1996) — EWMA, VaR methodology
- Bollerslev (1986) — GARCH
- Engle (2002) — DCC (Dynamic Conditional Correlation)
- Rockafellar, Uryasev (2000) — CVaR optimization
- Artzner et al. (1999) — Coherent risk measures
- Jorion (2007) — VaR comprehensive reference

### Fixed Income
- Vasicek (1977) — Short rate model
- Cox, Ingersoll, Ross (1985) — CIR model
- Hull, White (1990) — Extended Vasicek
- Heath, Jarrow, Morton (1992) — HJM framework
- Brace, Gatarek, Musiela (1997) — LIBOR Market Model

### Credit Risk
- Merton (1974) — Structural model
- KMV (Kealhofer, McQuown, Vasicek) — Distance-to-default
- Li (2000) — Gaussian copula for credit
- Longstaff, Schwartz (2001) — American options (LSM)

### Volatility
- Dupire (1994) — Local volatility
- Gatheral (2004) — SVI parameterization
- Demeterfi et al. (1999) — Variance swaps
- Avellaneda & Parás (1996) — Uncertain volatility model

### Jump-Diffusion & Lévy
- Merton (1976) — Jump-diffusion model
- Kou (2002) — Double exponential jump-diffusion
- Carr, Madan (1999) — FFT option pricing
- Madan, Seneta (1990) — Variance Gamma

## Additional Sources (English)

13. **Wilmott P.** "Frequently Asked Questions in Quantitative Finance" Wiley, 2007. 432 pages.
    - Comprehensive Q&A covering all quant finance
    - Key chapters: Ch 3 (probability distributions), Ch 4 (10 ways to derive BSM),
      Ch 5 (complete models & equations catalog), Ch 6 (BS formulas & all Greeks tables)
    - Ch 1: History/timeline of quantitative finance
    - Unique: CrashMetrics, Platinum Hedging, coherent risk measures explanation

14. **McDougall C.** "Quant Trading Guide" v2, 2020. 58 pages.
    - Interview preparation: probability, logic, strategy games, Fermi estimation
    - Market making fundamentals and adverse selection
    - Bayesian statistics applications in trading
    - Mental math and decision-making under uncertainty
