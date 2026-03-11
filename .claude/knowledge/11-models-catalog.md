# Financial Models Catalog — Quick Reference

Sources: Wilmott (2007) "FAQ in Quantitative Finance" Ch 5;
Hull (2022); Brigo & Mercurio (2006) "Interest Rate Models"

This is a compact catalog of all models with their SDEs and key formulas.
For detailed derivations, see the domain-specific knowledge files.

## Equity / FX / Commodity Models

### Lognormal (Black-Scholes)
```
dS = μS dt + σS dX
BS PDE: ∂V/∂t + ½σ²S²∂²V/∂S² + (r-D)S·∂V/∂S - rV = 0
```
Closed-form: European calls, puts, binaries.

### Jump-Diffusion (Merton 1976)
```
dS = μS dt + σS dX + (J-1)S dq
```
where dq is Poisson (rate λ), J is jump multiplier (ln J ~ N(μ_J, σ'²)).

European option = weighted sum of BS values:
```
V = Σ_{n=0}^∞ (1/n!) · exp(-λ'(T-t)) · (λ'(T-t))^n · V_BS(S, t; σ_n, r_n)
where σ_n² = σ² + nσ'²/(T-t),  r_n = r - λk + n·ln(1+k)/(T-t),  k = E[J-1]
```

### Stochastic Volatility — General
```
dS = μS dt + σS dX₁
dσ = (p - λq) dt + q dX₂     (correlation ρ)
```
PDE: ∂V/∂t + ½σ²S²V_SS + ρσSqV_Sσ + ½q²V_σσ + rSV_S + (p-λq)V_σ - rV = 0

### Heston (1993)
```
dv = (a - bv) dt + c√v dX₂    (v = σ²)
```
Closed-form via characteristic function (FFT). Arbitrary ρ.

### 3/2 Model
```
dv = (av - bv²) dt + cv^(3/2) dX₂
```
Also has closed-form solutions.

### GARCH-Diffusion
```
dv = (a - bv) dt + cv dX₂     (v = σ²)
```
Matches real data well (mean-reverting variance with proportional vol-of-vol).

### Ornstein-Uhlenbeck Log-Variance
```
dy = (a - by) dt + c dX₂      (y = ln v, v = σ²)
```
Best fit to real (non-risk-neutral) vol data.

### SABR (Hagan et al. 2002)
```
dF = α·F^β dX₁       (forward rate)
dα = ν·α dX₂          (stochastic vol)
corr(dX₁, dX₂) = ρ
```
Asymptotic implied vol formula (very fast):
```
σ_impl(K) ≈ (α/(F·K)^((1-β)/2)) · (z/x(z)) · [1 + correction terms]
```

### Local Volatility (Dupire 1994)
From market prices, extract σ_local(S, t):
```
σ²_local(K, T) = 2(∂C/∂T + (r-D)K·∂C/∂K + D·C) / (K²·∂²C/∂K²)
```

## Fixed Income Models

### Spot Rate — Single Factor

| Model | SDE (risk-neutral) | Closed-form bonds? |
|-------|----|----|
| Vasicek | dr = (a-br)dt + cdX | Yes: exp(A-Br) |
| CIR | dr = (a-br)dt + c√r dX | Yes: exp(A-Br) |
| Ho-Lee | dr = a(t)dt + cdX | Yes (calibrated) |
| Hull-White | dr = (a(t)-b(t)r)dt + c(t)dX | Yes (calibrated) |
| Black-Karasinski | d(ln r) = (a(t)-b(t)ln r)dt + c(t)dX | No |

Bond pricing PDE (all models):
```
∂V/∂t + ½w²·∂²V/∂r² + (u-λw)·∂V/∂r - rV = 0
```

### Two-Factor Models

**Brennan-Schwartz**: spot rate r + long rate l
**Fong-Vasicek**: spot rate r + stochastic variance ξ
**Longstaff-Schwartz**: two factors x, y with r = cx + dy
**Hull-White 2F**: r + mean-reversion driver u

### HJM Framework
Forward rate dynamics:
```
df(t,T) = μ(t,T)dt + σ(t,T)dW(t)
No-arbitrage drift: μ(t,T) = σ(t,T) · ∫_t^T σ(t,s) ds
```

### Black '76 Formulas

**Bond options**: C = e^(-r(T-t)) [F·N(d₁) - K·N(d₂)]
**Caplets**: same formula, F = forward rate
**Swaptions**:
```
Payer = A · e^(-r(T-t)) [F·N(d₁) - K·N(d₂)]
where A = (1 - 1/(1+F/m)^(τm)) / F
d₁ = (ln(F/K) + ½σ²(T-t)) / (σ√(T-t))
```

## Credit Models

### Merton Structural (1974)
Equity = call on firm assets:
```
E = V·N(d₁) - D·e^(-rT)·N(d₂)
d₁ = (ln(V/D) + (r + σ_V²/2)T) / (σ_V√T)
```
Distance-to-Default: DD = d₂

### Reduced-Form (Poisson)
Default as first jump of Poisson process (intensity λ):
```
P(survival to T) = exp(-∫_0^T λ(s) ds)
Risky bond = risk-free bond × survival probability × recovery
```

## Calibration vs Equilibrium (Wilmott FAQ 43)

| Aspect | Equilibrium | No-Arbitrage |
|--------|------------|--------------|
| Philosophy | Economic fundamentals | Match market prices |
| Parameters | Constant | Time-dependent |
| Bond prices | Output | Input |
| Examples | Vasicek, CIR | Ho-Lee, HW, BK, HJM |
| Pros | Few params, intuition | Exact fit to market |
| Cons | Poor fit to market | Many params, unstable |

## 10 Ways to Derive Black-Scholes (Wilmott Ch 4)

1. **Hedging + PDE** (Black & Scholes 1973) — delta-hedge → BS PDE
2. **Martingales** (Harrison & Kreps 1979) — risk-neutral expectation
3. **Change of Numeraire** — use stock as numeraire
4. **CAPM** — equilibrium argument (Rubinstein 1976)
5. **Binomial limit** (CRR 1979) — discrete → continuous
6. **Risk-neutral pricing** — Girsanov + Feynman-Kac
7. **Local time** — hedging at the strike (Carr)
8. **Dupire forward PDE** — implied from market prices
9. **Market price of risk** — CAPM-style argument
10. **Gamma P&L** — no-arbitrage from discrete hedging:
    ```
    Θ·δt + ½σ²S²Γ·δt + r(SΔ - V)·δt = 0  → BS equation
    ```
    This is the most intuitive: theta decay = cost of carry of hedge, gamma profit = realized variance.
