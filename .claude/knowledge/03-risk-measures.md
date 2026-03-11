# Risk Measures — Formula Reference

Sources: Hull (2022) Ch 22-23; RiskMetrics (1996); Shiryaev (1998)

## 1. Value at Risk (VaR)

**Definition**: VaR at confidence level X% over N days = loss V such that
P(Loss > V) = 1 - X/100

### Single Asset
```
VaR = σ · z_α · √N · P
```
where: σ = daily volatility, z_α = normal quantile (2.326 for 99%, 1.645 for 95%),
N = holding period (days), P = portfolio value.

### Portfolio (Model-Building, Linear)
```
ΔP = Σᵢ αᵢ·Δxᵢ
σ²_P = Σᵢ Σⱼ αᵢ·αⱼ·σᵢ·σⱼ·ρᵢⱼ
```
In matrix form: σ²_P = α' · C · α, where C is the covariance matrix.

VaR = z_α · σ_P · √N

### Hull Example 22.1
Portfolio: Microsoft (δ=1000, S=120) + AT&T (δ=20000, S=30)
α₁ = 120·1000 = 120,000; α₂ = 30·20,000 = 600,000
σ₁ = 2% daily, σ₂ = 1% daily, ρ = 0.3
σ_P = √(120²·0.02² + 600²·0.01² + 2·120·0.02·600·0.01·0.3) = 7.099 ($K)

### Scaling
```
VaR_N = VaR_1 · √N    # only valid for i.i.d. returns
```
Basel: 10-day VaR = 1-day VaR × √10

## 2. Expected Shortfall (ES / CVaR)

**Definition**: ES = E[Loss | Loss > VaR]

For normal distribution:
```
ES = σ_P · n(z_α) / (1 - α) · √N
```
where n(z) = standard normal PDF.

For 99%: ES = σ_P · n(2.326) / 0.01 = σ_P · 2.665
(ES/VaR ratio ≈ 2.665/2.326 ≈ 1.146 for normal at 99%)

ES is a **coherent risk measure** (satisfies subadditivity), VaR is not.

## 3. Historical Simulation

Algorithm:
1. Collect M days of historical data for all risk factors
2. For each day i (i=1..M): apply day-i's percentage changes to current portfolio
3. Compute portfolio P&L for each scenario
4. Sort losses; VaR = (1-α)·M-th largest loss
5. ES = average of losses beyond VaR

**Advantages**: No distributional assumptions, captures fat tails and correlations
**Disadvantages**: Limited by history window, all scenarios equally weighted

### Weighted Historical Simulation (Hull-White)
Weight recent observations more heavily. Replace equal weights 1/M with
exponentially declining weights.

## 4. Monte Carlo VaR

1. Define stochastic model for risk factors (GBM, etc.)
2. Simulate N paths of length Δt
3. Revalue portfolio on each path
4. VaR = quantile of simulated P&L distribution

For portfolio with options (quadratic model, Hull eq 22.8):
```
ΔP ≈ Σᵢ Sᵢ·δᵢ·Δxᵢ + ½·Σᵢ Σⱼ SᵢSⱼ·γᵢⱼ·Δxᵢ·Δxⱼ
```

## 5. EWMA — Exponentially Weighted Moving Average

Variance estimate (Hull Ch 23, RiskMetrics):
```
σ²_n = λ·σ²_{n-1} + (1-λ)·u²_{n-1}
```
where u_{n-1} = ln(S_{n-1}/S_{n-2}), λ = decay factor.

**RiskMetrics standard**: λ = 0.94 (daily), λ = 0.97 (monthly)

Recursion gives exponentially declining weights:
```
σ²_n = (1-λ) Σᵢ₌₁^∞ λ^(i-1) · u²_{n-i}
```

### EWMA Covariance
```
cov_n = λ·cov_{n-1} + (1-λ)·u_{n-1}·v_{n-1}
```

## 6. GARCH(1,1) — Generalized ARCH

Bollerslev (1986):
```
σ²_n = ω + α·u²_{n-1} + β·σ²_{n-1}
```
Constraints: ω > 0, α ≥ 0, β ≥ 0, α + β < 1

Long-run variance: V_L = ω / (1 - α - β)
Alternative form: σ²_n = γ·V_L + α·u²_{n-1} + β·σ²_{n-1}, where γ = 1 - α - β

**Mean reversion**: variance reverts to V_L at rate (1 - α - β) per day.

### Typical parameter values
| Asset class | ω | α | β | V_L |
|-------------|---|---|---|-----|
| Equities | 0.000001-0.00001 | 0.05-0.10 | 0.85-0.94 | varies |
| FX | similar | 0.03-0.08 | 0.90-0.96 | varies |

### Maximum Likelihood Estimation (Hull eq 23.7)
```
L = Σᵢ [-ln(σ²ᵢ) - u²ᵢ/σ²ᵢ]
```
Maximize L over (ω, α, β).

### GARCH Variance Term Structure
T-day variance forecast (Hull eq 23.8):
```
E[σ²_{n+t}] = V_L + (α + β)^t · (σ²_n - V_L)
```
Average variance over T days:
```
σ²(T) = V_L + (1 - e^(-aT))/(aT) · (σ²_n - V_L)
```
where a = -ln(α + β), or approximated.

## 7. Correlation Estimation

### EWMA Correlation
```
cov_{12,n} = λ·cov_{12,n-1} + (1-λ)·u_{1,n-1}·u_{2,n-1}
ρ_{12,n} = cov_{12,n} / (σ_{1,n}·σ_{2,n})
```

### GARCH Correlation (DCC — Dynamic Conditional Correlation)
Engle (2002):
```
q_{12,n} = ρ̄ + a·(u_{1,n-1}·u_{2,n-1} - ρ̄) + b·(q_{12,n-1} - ρ̄)
ρ_{12,n} = q_{12,n} / √(q_{11,n}·q_{22,n})
```

## 8. Principal Components Analysis (PCA) for VaR

For interest rate risk (Hull §22.9):
1. Compute covariance matrix of rate changes
2. Find eigenvalues/eigenvectors (principal components)
3. PC1 ≈ parallel shift (~87% variance)
4. PC2 ≈ twist/steepening (~8%)
5. PC3 ≈ butterfly/bowing (~2%)

Portfolio exposure to factor k:
```
exposure_k = Σᵢ δᵢ · loading_{k,i}
```
VaR from PCA:
```
σ²_P = Σ_k exposure²_k · var(factor_k)
```

## 9. Cornish-Fisher Expansion

For non-normal ΔP (with options, Hull eq 22.8):
Adjust quantile for skewness (S₃) and kurtosis (S₄):
```
z_adjusted = z_α + (z²_α - 1)·S₃/6 + (z³_α - 3z_α)·S₄/24 - (2z³_α - 5z_α)·S₃²/36
```
Use z_adjusted instead of z_α in VaR formula.

## Numerical Stability Notes

1. **Covariance matrix**: Must be positive semi-definite. Use Cholesky for simulation; if fails, apply nearest PSD correction (Higham 2002)
2. **GARCH MLE**: Use bounded optimization (scipy.optimize.minimize with bounds)
3. **Historical simulation**: Need min 500 observations for 99% VaR (Basel requirement)
4. **EWMA initialization**: Use sample variance of first 30 observations
5. **Correlation clipping**: Ensure -1 ≤ ρ ≤ 1 after estimation
