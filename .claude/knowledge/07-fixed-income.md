# Fixed Income & Interest Rates — Formula Reference

Sources: Hull (2022) Ch 4,6,29-33; Shiryaev (1998) Т.1 III§4, Т.2 VII§5, VIII§4

## 1. Bond Pricing Fundamentals

### Zero-Coupon Bond
```
P(t,T) = e^(-r(T-t))        # continuous compounding
P(t,T) = 1/(1+r)^(T-t)      # discrete compounding
```

### Coupon Bond
```
B = Σᵢ C·e^(-rᵢ·tᵢ) + F·e^(-r_n·T)
```
where C = coupon payments, F = face value, rᵢ = zero rate for maturity tᵢ.

## 2. Duration & Convexity

### Macaulay Duration
```
D = (1/B) · Σᵢ tᵢ·CFᵢ·e^(-y·tᵢ)
```

### Modified Duration
```
D_mod = D / (1 + y/m)    # m = compounding frequency
```
For continuous: D_mod = D

### Dollar Duration (DV01)
```
DV01 = -dB/dy · 0.0001 ≈ D_mod · B · 0.0001
```

### Convexity
```
C = (1/B) · Σᵢ tᵢ²·CFᵢ·e^(-y·tᵢ)
```

### Price Change Approximation
```
ΔB/B ≈ -D_mod·Δy + ½·C·(Δy)²
```

### Key Rate Durations (KRD)
Sensitivity to movement in specific point on yield curve:
```
KRD_k = -ΔB / (B · Δr_k)
```
Sum of KRDs ≈ total modified duration.

## 3. Yield Curve Construction

### Bootstrap Method
Given par yields or swap rates, solve for zero rates sequentially:
```
P_n = Σᵢ₌₁ⁿ⁻¹ c/2·e^(-rᵢ·tᵢ) + (1 + c/2)·e^(-r_n·t_n)
```
Solve for r_n at each maturity.

### Nelson-Siegel-Svensson
```
r(τ) = β₀ + β₁·(1-e^(-τ/λ₁))/(τ/λ₁)
       + β₂·[(1-e^(-τ/λ₁))/(τ/λ₁) - e^(-τ/λ₁)]
       + β₃·[(1-e^(-τ/λ₂))/(τ/λ₂) - e^(-τ/λ₂)]
```

### ZCYC (Zero Coupon Yield Curve) — MOEX
Currently implemented in Zeta: `zcyc_service.py` (fetches from MOEX ISS API).

## 4. Forward Rates

### Instantaneous Forward Rate
```
f(t,T) = -∂ln P(t,T)/∂T
```

### Discrete Forward Rate
```
F(t; T₁,T₂) = [P(t,T₁)/P(t,T₂) - 1] / (T₂ - T₁)
```

## 5. Interest Rate Swaps (Hull Ch 7)

### Swap Valuation
Fixed-for-floating swap (receive fixed):
```
V_swap = B_fixed - B_float
B_fixed = Σᵢ c·P(0,tᵢ) + P(0,T)
B_float = P(0,t_next)·(1 + r_float·Δ)    # resets at par on payment dates
```

### Swap Rate (par rate)
```
s = (1 - P(0,T)) / Σᵢ Δᵢ·P(0,tᵢ)
```

## 6. Short Rate Models (Hull Ch 31-32, Shiryaev III§4)

### Vasicek (1977)
```
dr = a(b - r)dt + σdW
P(t,T) = A(t,T)·e^(-B(t,T)·r(t))
B(t,T) = (1 - e^(-a(T-t)))/a
```

### CIR (1985)
```
dr = a(b - r)dt + σ√r dW
```
Bond price in closed form (Bessel functions involved).

### Hull-White (1990)
```
dr = [θ(t) - ar]dt + σdW
```
θ(t) calibrated to fit market term structure exactly.
Trinomial tree: standard implementation method.

### Black-Karasinski (1991)
```
d(ln r) = [θ(t) - a·ln r]dt + σdW
```
Log-normal short rate (always positive).

## 7. HJM Framework (Hull Ch 33)

Heath-Jarrow-Morton (1992):
```
df(t,T) = α(t,T)dt + σ(t,T)dW(t)
```
No-arbitrage drift condition:
```
α(t,T) = σ(t,T)·∫ᵗᵀ σ(t,s)ds
```

### LIBOR Market Model (Brace-Gatarek-Musiela, 1997)
Models forward LIBORs directly:
```
dFₖ(t)/Fₖ(t) = μₖ(t)dt + σₖ(t)dW(t)
```

## 8. Swaptions (Hull Ch 29)

### Black's Model for Swaptions
Payer swaption (right to pay fixed):
```
V = L·A·[s₀·N(d₁) - s_K·N(d₂)]
```
where:
- L = notional
- A = annuity factor = Σᵢ Δᵢ·P(0,tᵢ)
- s₀ = forward swap rate
- s_K = strike swap rate
- d₁ = [ln(s₀/s_K) + σ²T/2] / (σ√T)

## 9. Option-Adjusted Spread (OAS)

Price of bond with embedded option:
```
B_market = Σ_paths [Σᵢ CF_i(path)·e^(-(rᵢ+OAS)·tᵢ)] / N_paths
```

OAS: constant spread added to risk-free rates that equates model price to market price.
Solve numerically (bisection or Newton's method).

## 10. Credit Risk (Merton Model)

### Structural Model (Hull Ch 24, Shiryaev: Merton 1974)
Firm value: dV = μV dt + σ_V·V dW
Default: V(T) < D (debt face value)

Distance-to-Default:
```
DD = [ln(V/D) + (μ - σ²_V/2)T] / (σ_V√T)
```

Probability of Default:
```
PD = N(-DD)
```

Equity as call option on firm value:
```
E = V·N(d₁) - D·e^(-rT)·N(d₂)
```
(BSM with S₀=V, K=D)

## Implementation Notes

1. **Day count conventions**: ACT/365, ACT/360, 30/360 — critical for bond pricing
2. **Accrued interest**: Clean price = Dirty price - Accrued
3. **Yield solving**: Use scipy.optimize.brentq for YTM (robust bracket method)
4. **Curve interpolation**: Log-linear on discount factors, or cubic spline on zero rates
5. **Negative yields**: Models handle this; check for log(negative) in lognormal models
