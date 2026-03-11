# Portfolio Theory & Optimization — Formula Reference

Sources: Hull (2022) Ch 1-3 Appendix, Ch 22; Shiryaev (1998) Т.1 I§2b-2d;
Markowitz (1952); Black-Litterman (1992); Maillard et al. (2010)

## 1. Markowitz Mean-Variance

Ширяев I§2b "Диверсификация Марковитца":

### Portfolio Return & Risk
```
E[R_p] = Σᵢ wᵢ·E[Rᵢ] = w'·μ
σ²_p = Σᵢ Σⱼ wᵢ·wⱼ·σᵢⱼ = w'·Σ·w
```
where w = weight vector, μ = expected returns, Σ = covariance matrix.

### Efficient Frontier (quadratic programming)
```
min  w'·Σ·w
s.t. w'·μ = μ_target
     w'·1 = 1
     wᵢ ≥ 0 (optional, long-only)
```

### Two-Fund Separation
Any efficient portfolio = α·P₁ + (1-α)·P₂ where P₁, P₂ are any two efficient portfolios.

## 2. CAPM

Ширяев I§2c, Hull Ch 3 Appendix:
```
E[Rᵢ] - r_f = βᵢ·(E[R_m] - r_f)
βᵢ = Cov(Rᵢ, R_m) / Var(R_m) = σᵢₘ / σ²_m
```

Security Market Line: E[R] = r_f + β·(E[R_m] - r_f)

### Alpha (Jensen's Alpha)
```
αᵢ = Rᵢ - [r_f + βᵢ·(R_m - r_f)]
```
α > 0 → outperformance, α < 0 → underperformance.

## 3. APT (Arbitrage Pricing Theory)

Ширяев I§2d:
```
E[Rᵢ] = r_f + Σ_k βᵢₖ·λ_k
```
where βᵢₖ = sensitivity to factor k, λ_k = risk premium for factor k.

Multi-factor model (Barra, Fama-French):
```
Rᵢ = αᵢ + Σ_k βᵢₖ·F_k + εᵢ
```

### Fama-French 3-Factor
```
Rᵢ - r_f = αᵢ + βᵢ,MKT·(R_m - r_f) + βᵢ,SMB·SMB + βᵢ,HML·HML + εᵢ
```
MKT = market, SMB = small minus big, HML = high B/M minus low B/M.

## 4. Black-Litterman Model

He & Litterman (1992). Реализован в Zeta: `black_litterman_service.py`

### Equilibrium Returns (prior)
```
Π = δ·Σ·w_mkt
```
where δ = risk aversion (typically (E[R_m]-r_f)/σ²_m), w_mkt = market-cap weights.

### Views
P·μ = Q + ε, ε ~ N(0, Ω)
P = pick matrix (K×N), Q = view vector (K×1), Ω = uncertainty of views.

### Posterior Returns
```
μ_BL = [(τΣ)⁻¹ + P'·Ω⁻¹·P]⁻¹ · [(τΣ)⁻¹·Π + P'·Ω⁻¹·Q]
Σ_BL = [(τΣ)⁻¹ + P'·Ω⁻¹·P]⁻¹
```
τ ≈ 0.025-0.05 (scalar, confidence in equilibrium).

Alternative (Master formula):
```
μ_BL = Π + τΣP'(PτΣP' + Ω)⁻¹(Q - PΠ)
```

### Optimal Weights
```
w_BL = (δΣ)⁻¹ · μ_BL
```

## 5. Risk Parity

Maillard, Roncalli, Teïletche (2010):

Each asset contributes equally to portfolio risk.

### Risk Contribution
```
RC_i = wᵢ · (Σ·w)ᵢ / σ_p
```
where (Σ·w)ᵢ = marginal risk contribution of asset i.

### Equal Risk Contribution (ERC)
```
min  Σᵢ Σⱼ (wᵢ·(Σw)ᵢ - wⱼ·(Σw)ⱼ)²
s.t. w'·1 = 1, wᵢ ≥ 0
```

Alternative: min Σᵢ(ln(wᵢ) - c·ln(σ_p))  (Roncalli formulation)

Simpler: for diagonal Σ, w_i ∝ 1/σ_i (inverse-vol weighting).

## 6. CVaR Optimization

Rockafellar & Uryasev (2000). Partially implemented in Zeta (CCMV).

```
min  CVaR_α(w)
s.t. w'·μ ≥ μ_target
     w'·1 = 1
```

CVaR reformulation as LP:
```
min  ζ + 1/(M(1-α)) · Σₛ zₛ
s.t. zₛ ≥ -w'·r_s - ζ,  ∀s
     zₛ ≥ 0
     w'·1 = 1
```
where r_s = scenario returns, ζ = VaR threshold, zₛ = excess losses.

## 7. Tracking Error Optimization

Bloomberg PORT model:
```
min  (w - w_bench)'·Σ·(w - w_bench)    # minimize tracking error
s.t. w'·α ≥ α_target                     # minimum alpha
     sector/factor constraints
```

Tracking Error: TE = √((w - w_bench)'·Σ·(w - w_bench)) · √252

Information Ratio: IR = α_portfolio / TE

## 8. Performance Attribution

### Brinson Attribution (single-period)
```
Allocation  = Σᵢ (w_p,i - w_b,i) · R_b,i
Selection   = Σᵢ w_b,i · (R_p,i - R_b,i)
Interaction = Σᵢ (w_p,i - w_b,i) · (R_p,i - R_b,i)
Total Active = Allocation + Selection + Interaction
```

### Factor Attribution
```
Active Return = Σ_k (β_p,k - β_b,k)·F_k + α + ε
```
Factor contribution = factor exposure × factor return.

## 9. Risk Metrics

### Sharpe Ratio
```
SR = (R_p - r_f) / σ_p
```

### Sortino Ratio
```
Sortino = (R_p - r_f) / σ_downside
σ_downside = √(E[min(R_p - r_f, 0)²])
```

### Maximum Drawdown
```
MDD = max_t (max_{s≤t} V(s) - V(t)) / max_{s≤t} V(s)
```

### Calmar Ratio
```
Calmar = Annualized_Return / MDD
```

## Implementation Notes (cvxpy)

```python
import cvxpy as cp
import numpy as np

w = cp.Variable(n)
ret = mu @ w
risk = cp.quad_form(w, Sigma)  # w'Σw

# Mean-variance
prob = cp.Problem(cp.Minimize(risk), [cp.sum(w) == 1, w >= 0, ret >= target])

# Min-CVaR (with scenarios)
z = cp.Variable(M)
zeta = cp.Variable()
cvar = zeta + cp.sum(z) / (M * (1 - alpha))
prob = cp.Problem(cp.Minimize(cvar), [z >= -returns @ w - zeta, z >= 0, cp.sum(w) == 1])
```

## Covariance Matrix Issues

1. **Not PSD**: Use nearest_pd() correction (Higham 2002)
2. **Estimation error**: Shrinkage (Ledoit-Wolf): Σ_shrunk = α·F + (1-α)·S
3. **High-dimensional**: Factor model Σ = B·F·B' + D (reduces params)
4. **Singular**: Add small diagonal (Σ + εI, ε ~ 1e-8)
