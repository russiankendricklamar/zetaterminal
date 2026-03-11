# Derivatives Pricing — Formula Reference

Sources: Hull (2022) "Options, Futures, and Other Derivatives" 11th Ed;
Shiryaev (1998) "Основы стохастической финансовой математики" Т.1-2

## 1. Geometric Brownian Motion (GBM)

Stock price process (Hull eq 15.8, Shiryaev III§3):
```
dS = μS dt + σS dz
```
where dz is a Wiener process (dz = ε√dt, ε ~ N(0,1))

Log-price distribution (Hull eq 15.3):
```
ln(S_T) ~ N(ln(S_0) + (μ - σ²/2)T, σ²T)
```

Key: S_T is lognormally distributed. Mean of ln(S_T) uses μ - σ²/2 (Ito correction).

## 2. Black-Scholes-Merton (BSM)

### Differential Equation (Hull eq 15.16)
```
∂f/∂t + rS(∂f/∂S) + ½σ²S²(∂²f/∂S²) = rf
```
where f = derivative price, r = risk-free rate

### European Call & Put (Hull eq 15.20-15.21, Shiryaev VIII§1b)
```
c = S₀·N(d₁) - K·e^(-rT)·N(d₂)
p = K·e^(-rT)·N(-d₂) - S₀·N(-d₁)
```
where:
```
d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
d₂ = [ln(S₀/K) + (r - σ²/2)T] / (σ√T) = d₁ - σ√T
```

N(x) = cumulative standard normal distribution function.

### Interpretation
- N(d₂) = probability option is exercised (risk-neutral world)
- S₀·N(d₁)·e^(rT) = expected stock price at T conditional on S_T > K (counting S_T < K as 0)
- Put-call parity: c + K·e^(-rT) = p + S₀

### With Dividends
Replace S₀ with S₀ - PV(dividends) for discrete dividends.
For continuous dividend yield q:
```
c = S₀·e^(-qT)·N(d₁) - K·e^(-rT)·N(d₂)
d₁ = [ln(S₀/K) + (r - q + σ²/2)T] / (σ√T)
```

### Reference Values (Hull Example 15.6)
| S₀ | K | r | σ | T | Call | Put |
|----|---|---|---|---|------|-----|
| 42 | 40 | 0.10 | 0.20 | 0.5 | 4.76 | 0.81 |
| 40 | 40 | 0.09 | 0.30 | 0.5 | 3.67* | — |
*with dividends $0.50 at months 2 and 5

## 3. Black's Model (for futures/forwards)

European call/put on futures (Hull eq 18.7-18.8):
```
c = e^(-rT) [F₀·N(d₁) - K·N(d₂)]
p = e^(-rT) [K·N(-d₂) - F₀·N(-d₁)]
```
where:
```
d₁ = [ln(F₀/K) + σ²T/2] / (σ√T)
d₂ = [ln(F₀/K) - σ²T/2] / (σ√T) = d₁ - σ√T
```

Reference (Hull Example 18.6): F₀=20, K=20, r=0.09, T=4/12, σ=0.25 → put = $1.12

## 4. Ito's Lemma

For G(x,t) where dx = a·dt + b·dz (Hull eq 14A.9, Shiryaev III§3d):
```
dG = (∂G/∂x·a + ∂G/∂t + ½·∂²G/∂x²·b²) dt + (∂G/∂x·b) dz
```

Multivariate Ito (Hull eq 14A.10):
```
dG = [Σᵢ(∂G/∂xᵢ)aᵢ + ∂G/∂t + ½ΣᵢΣⱼ(∂²G/∂xᵢ∂xⱼ)bᵢbⱼρᵢⱼ] dt + Σᵢ(∂G/∂xᵢ)bᵢdzᵢ
```

## 5. Binomial Model (CRR)

Cox-Ross-Rubinstein tree (Hull Ch 13, Shiryaev V§1d):
```
u = e^(σ√Δt)
d = 1/u = e^(-σ√Δt)
p = (e^(rΔt) - d) / (u - d)    # risk-neutral probability
```
Option value at node:
```
f = e^(-rΔt) [p·f_u + (1-p)·f_d]
```
For American options: f = max(exercise_value, continuation_value)

## 6. Stochastic Volatility Models

### Heston Model
```
dS = μS dt + √v·S dz₁
dv = κ(θ - v) dt + ξ√v dz₂
```
where: v = variance, κ = mean-reversion speed, θ = long-run variance,
ξ = vol-of-vol, Corr(dz₁, dz₂) = ρ

### SABR (Hagan et al. 2002)
```
dF = σ_α · F^β · dW₁
dσ_α = ν · σ_α · dW₂
Corr(dW₁, dW₂) = ρ
```
Implied vol approximation (ATM):
```
σ_impl ≈ α/F^(1-β) · [1 + ((1-β)²/24 · α²/F^(2-2β) + ρβνα/(4F^(1-β)) + (2-3ρ²)/24 · ν²) · T]
```

## 7. Interest Rate Models

### Vasicek (Hull Ch 31)
```
dr = a(b - r) dt + σ dz
```
Mean-reverting to b with speed a. Bond price: P(t,T) = A(t,T)·e^(-B(t,T)·r(t))

### Cox-Ingersoll-Ross (CIR)
```
dr = a(b - r) dt + σ√r dz
```
Ensures r > 0 if 2ab > σ² (Feller condition)

### Hull-White (one-factor)
```
dr = [θ(t) - ar] dt + σ dz
```
θ(t) chosen to fit initial term structure exactly.

## 8. Bachelier Model (Normal Model)

For pricing under normal dynamics (Shiryaev VIII§1a):
```
dS = μ dt + σ_n dz   (σ_n in absolute terms, not relative)
c = (S₀ - K·e^(-rT))·N(d) + σ_n·√T·n(d)
```
where n(d) is the standard normal PDF, d = (S₀ - K·e^(-rT)) / (σ_n·√T)

## Numerical Stability Notes

1. **Always use float64** for all financial calculations
2. **Log-prices**: work with ln(S) not S for better numerical properties
3. **Near-zero T**: d₁, d₂ → ±∞ as T→0; handle with special cases
4. **Deep ITM/OTM**: N(d) near 0 or 1; use complementary normal or log-space
5. **σ→0**: BSM degenerates; return max(S-K·e^(-rT), 0) for calls
6. **Negative rates**: BSM still works, but check model assumptions

## Implementation in NumPy/SciPy

```python
from scipy.stats import norm
import numpy as np

def bsm_call(S, K, T, r, sigma):
    """Black-Scholes-Merton European call price."""
    if T <= 0:
        return max(S - K, 0.0)
    if sigma <= 0:
        return max(S - K * np.exp(-r * T), 0.0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
```
