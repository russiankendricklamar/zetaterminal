# Option Greeks — Formula Reference

Sources: Hull (2022) Ch 19 "The Greek Letters";
Wilmott (2007) "FAQ in Quantitative Finance" Ch 6 (complete tables with dividends)

## Definition Summary

| Greek | Symbol | Definition | Measures |
|-------|--------|-----------|----------|
| Delta | Δ | ∂f/∂S | Price sensitivity to underlying |
| Gamma | Γ | ∂²f/∂S² | Delta sensitivity (curvature) |
| Theta | Θ | ∂f/∂t | Time decay |
| Vega | ν | ∂f/∂σ | Volatility sensitivity |
| Rho | ρ | ∂f/∂r | Interest rate sensitivity |

## BSM Greeks (European, no dividends)

### Delta
```
Call: Δ_c = N(d₁)
Put:  Δ_p = N(d₁) - 1
```

### Gamma (same for call and put)
```
Γ = n(d₁) / (S₀·σ·√T)
```
where n(x) = (1/√(2π))·e^(-x²/2) is the standard normal PDF.

### Theta
```
Call: Θ_c = -S₀·n(d₁)·σ/(2√T) - r·K·e^(-rT)·N(d₂)
Put:  Θ_p = -S₀·n(d₁)·σ/(2√T) + r·K·e^(-rT)·N(-d₂)
```

### Vega (same for call and put)
```
ν = S₀·√T·n(d₁)
```

### Rho
```
Call: ρ_c = K·T·e^(-rT)·N(d₂)
Put:  ρ_p = -K·T·e^(-rT)·N(-d₂)
```

## Relationship: Delta-Theta-Gamma
```
Θ + r·S·Δ + ½·σ²·S²·Γ = r·f
```
This follows directly from the BSM PDE.

## With Continuous Dividend Yield q

Replace S₀ with S₀·e^(-qT) in all formulas above:
```
Call: Δ_c = e^(-qT)·N(d₁)
Γ = e^(-qT)·n(d₁) / (S₀·σ·√T)
ν = S₀·e^(-qT)·√T·n(d₁)
```

## Futures Options (Black's Model)

Replace S₀ with F₀·e^(-rT):
```
Call: Δ_c = e^(-rT)·N(d₁)
Γ = e^(-rT)·n(d₁) / (F₀·σ·√T)
```

## Second-Order Greeks

### Vanna (∂Δ/∂σ = ∂ν/∂S)
```
Vanna = -n(d₁)·d₂/σ
```

### Volga/Vomma (∂²f/∂σ² = ∂ν/∂σ)
```
Volga = ν·d₁·d₂/σ
```

### Charm (∂Δ/∂t = -∂Θ/∂S)
```
Charm = -n(d₁)·[2(r-q)T - d₂·σ·√T] / (2T·σ·√T)
```

### Speed (∂Γ/∂S = ∂³f/∂S³)
```
Speed = -Γ/S · (d₁/(σ√T) + 1)
```

## Delta Hedging

Portfolio Π = -f + Δ·S (short derivative, long Δ shares).
This makes Π insensitive to small moves in S.

Rebalance frequency: daily in practice (discrete hedging).
Hedging error ~ O(Δt) due to gamma (convexity).

## Gamma Hedging

To neutralize both delta and gamma:
1. Use another option (C₂) to zero gamma
2. Then use underlying to zero delta
```
w₂ = -Γ_portfolio / Γ₂   (units of C₂)
Δ_adjusted = Δ_portfolio + w₂·Δ₂
hedge_shares = -Δ_adjusted
```

## Portfolio Greeks Approximation (Hull eq 22.6)
```
ΔP ≈ Σᵢ Sᵢ·δᵢ·Δxᵢ                    # linear (delta)
ΔP ≈ Σᵢ Sᵢ·δᵢ·Δxᵢ + ½·Σᵢ Sᵢ²·γᵢ·(Δxᵢ)²  # quadratic (delta-gamma)
```
where δᵢ, γᵢ are portfolio delta/gamma w.r.t. variable i.

## Complete Greeks with Dividends (Wilmott Ch 6)

All formulas below use continuous dividend yield D.
```
d₁ = (ln(S/K) + (r - D + σ²/2)(T-t)) / (σ√(T-t))
d₂ = d₁ - σ√(T-t)
N'(x) = (1/√(2π))·exp(-x²/2)
```

### European Call (Wilmott Table 6.1)
```
Value:   V = S·e^(-D(T-t))·N(d₁) - K·e^(-r(T-t))·N(d₂)
Delta:   e^(-D(T-t))·N(d₁)
Gamma:   e^(-D(T-t))·N'(d₁) / (σS√(T-t))
Theta:   -σS·e^(-D(T-t))·N'(d₁)/(2√(T-t)) + DS·N(d₁)·e^(-D(T-t)) - rK·e^(-r(T-t))·N(d₂)
Speed:   -e^(-D(T-t))·N'(d₁)/(σ²S²(T-t)) · (d₁ + σ√(T-t))
Charm:   D·e^(-D(T-t))·N(d₁) + e^(-D(T-t))·N'(d₁)·(d₂/(2(T-t)) - (r-D)/(σ√(T-t)))
Colour:  e^(-D(T-t))·N'(d₁)/(σS√(T-t)) · (D + (1-d₁d₂)/(2(T-t)) - d₁(r-D)/(σ√(T-t)))
Vega:    S√(T-t)·e^(-D(T-t))·N'(d₁)
Rho(r):  K(T-t)·e^(-r(T-t))·N(d₂)
Rho(D):  -(T-t)S·e^(-D(T-t))·N(d₁)
Vanna:   -e^(-D(T-t))·N'(d₁)·d₂/σ
Volga:   S√(T-t)·e^(-D(T-t))·N'(d₁)·d₁d₂/σ
```

### European Put (Wilmott Table 6.2)
```
Value:   V = -S·e^(-D(T-t))·N(-d₁) + K·e^(-r(T-t))·N(-d₂)
Delta:   e^(-D(T-t))·(N(d₁) - 1)
Gamma:   same as call
Speed:   same as call
Vega:    same as call
Vanna:   same as call
Volga:   same as call
Theta:   -σS·e^(-D(T-t))·N'(-d₁)/(2√(T-t)) - DS·N(-d₁)·e^(-D(T-t)) + rK·e^(-r(T-t))·N(-d₂)
Rho(r):  -K(T-t)·e^(-r(T-t))·N(-d₂)
Rho(D):  (T-t)S·e^(-D(T-t))·N(-d₁)
```

### Binary Call (Wilmott Table 6.3)
```
Value:   e^(-r(T-t))·N(d₂)
Delta:   e^(-r(T-t))·N'(d₂) / (σS√(T-t))
Gamma:   -e^(-r(T-t))·d₁·N'(d₂) / (σ²S²(T-t))
Vega:    -e^(-r(T-t))·N'(d₂)·d₁/σ
Vanna:   -e^(-r(T-t))·N'(d₂)·(1 - d₁d₂) / (σ²S√(T-t))
Volga:   e^(-r(T-t))·N'(d₂)·(d₁²d₂ - d₁ - d₂) / σ²
```

### Binary Put (Wilmott Table 6.4)
```
Value:   e^(-r(T-t))·(1 - N(d₂))
Delta:   -e^(-r(T-t))·N'(d₂) / (σS√(T-t))
Gamma:   e^(-r(T-t))·d₁·N'(d₂) / (σ²S²(T-t))
```

## Numerical Implementation Notes

1. **n(d₁) computation**: Use scipy.stats.norm.pdf(d1), not manual formula (avoids overflow)
2. **Theta sign convention**: Θ is typically negative (time decay). Report in per-day units (÷365 or ÷252)
3. **Vega convention**: Usually reported per 1% change in σ (multiply by 0.01)
4. **Gamma scaling**: For portfolio risk, use dollar gamma = ½·Γ·S²·(Δx)²
5. **Near-expiry**: Greeks can blow up as T→0. Clamp or handle separately.
