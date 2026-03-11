# Probability Distributions in Finance — Formula Reference

Sources: Wilmott (2007) "Frequently Asked Questions in Quantitative Finance" Ch 3;
Hull (2022) Ch 14 (lognormal), Ch 22 (VaR distributions)

## 1. Normal (Gaussian)

Unbounded. Parameters: a (location), b > 0 (scale).
```
f(x) = (1/√(2πb²)) · exp(-(x-a)² / (2b²))
Mean = a, Variance = b²
```
Use: Equity returns, error distributions. Foundation via CLT.

## 2. Lognormal

Bounded below (x ≥ 0). Parameters: a (location), b > 0 (scale).
```
f(x) = (1/(x·b·√(2π))) · exp(-(ln(x) - a)² / (2b²))
Mean = exp(a + b²/2), Variance = exp(2a + b²)·(exp(b²) - 1)
```
Use: Stock prices (follows from normally distributed returns).
Key: If ln(S) ~ N(a, b²), then S is lognormal.

## 3. Poisson (Discrete)

Non-negative integers. Parameter: a > 0 (rate).
```
P(X = k) = e^(-a) · a^k / k!
Mean = a, Variance = a
```
Use: Credit events count, jump arrivals in jump-diffusion models.

## 4. Student's t

Unbounded. Parameters: a (location), b > 0 (scale), c > 0 (degrees of freedom).
```
f(x) = Γ((c+1)/2) / (b·√(πc)·Γ(c/2)) · (1 + ((x-a)/b)²/c)^(-(c+1)/2)
Mean = a, Variance = (c/(c-2))·b²  (exists only if c > 2)
```
Use: Equity returns (fat tails). The nth moment exists only if c > n.
With c → ∞, converges to Normal. Low c captures heavy tails.

## 5. Chi-Square

Bounded below (x ≥ 0). Parameters: a ≥ 0 (non-centrality), ν (degrees of freedom).
```
Mean = ν + a, Variance = 2(ν + 2a)
```
Use: Hedging error distribution (χ² with 1 df for discrete hedging of single option).

## 6. Lévy (Stable)

Unbounded. Parameters: μ (location), 0 < α ≤ 2 (peakedness), -1 < β < 1 (skewness), ν > 0 (spread).
No closed-form PDF. Defined via characteristic function:
```
ln M(z) = iμz - να|z|^α (1 - iβ·sgn(z)·tan(πα/2))  for α ≠ 1
```
Special cases:
- α = 2, β = 0 → Normal (ν = σ²/2)
- α = 1, β = 0 → Cauchy

Stability property: Sum of n i.i.d. Lévy → Lévy with same α, β but mean n^(1/α)μ, spread n^(1/α)ν.
```
Tail decay: |x|^(-1-α)
Mean = μ, Variance = ∞ (unless α = 2)
```
Use: Fat-tailed returns (VG, CGMY, NIG are special cases).

## 7. Pareto (Power Law)

Bounded below (x ≥ a). Parameters: a > 0 (scale), b > 0 (shape).
```
f(x) = b·a^b / x^(b+1)
Mean = ab/(b-1), Variance = a²b / ((b-2)(b-1)²)
```
Use: Wealth distribution, extreme loss modeling. nth moment exists only if b > n.

## 8. Gumbel (Extreme Value Type I)

Unbounded. Parameters: a (location), b > 0 (scale).
```
f(x) = (1/b) · exp((a-x)/b) · exp(-exp((a-x)/b))
Mean = a + γb  (γ = 0.577216... Euler's constant)
Variance = π²b²/6
```
Use: Distribution of maximum of large sample from unbounded distribution. EVT for VaR.

## 9. Weibull (Extreme Value Type III)

Bounded below (x > a). Parameters: a (location), b > 0 (scale), c > 0 (shape).
```
f(x) = (c/b)·((x-a)/b)^(c-1) · exp(-((x-a)/b)^c)
Mean = a + b·Γ((c+1)/c)
Variance = b²·(Γ((c+2)/c) - Γ((c+1)/c)²)
```
Use: Distribution of maximum from bounded distribution. Failure time models.

## 10. Gamma

Bounded below (x ≥ a). Parameters: a (location), b > 0 (scale), c > 0 (shape).
```
f(x) = (1/(b·Γ(c))) · ((x-a)/b)^(c-1) · exp((a-x)/b)
Mean = a + bc, Variance = b²c
```
Special cases: c=1 → Exponential, a=0 & b=2 → Chi-square(2c).
Use: Variance Gamma process (VG) in option pricing.

## 11. Inverse Normal (Inverse Gaussian)

Bounded below (x ≥ 0). Parameters: a > 0 (location), b > 0 (scale).
```
f(x) = √(b/(2πx³)) · exp(-b(x-a)² / (2a²x))
Mean = a, Variance = a³/b
```
Use: First passage time of Brownian motion. NIG process in option pricing.

## 12. Beta

Bounded [a, b]. Parameters: a, b (bounds), c > 0, d > 0 (shape).
```
f(x) = Γ(c+d) / (Γ(c)·Γ(d)·(b-a)^(c+d-1)) · (x-a)^(c-1)·(b-x)^(d-1)
Mean = (ad + bc)/(c+d)
Variance = cd(b-a)² / ((c+d+1)(c+d)²)
```
Use: Prior distributions in Bayesian estimation, bounded random variables.

## 13. Cauchy

Unbounded. Parameters: a (location), b > 0 (scale).
```
f(x) = 1 / (πb(1 + ((x-a)/b)²))
```
No finite moments (mean, variance undefined).
Use: Rarely in finance directly; appears as ratio of two normals.

## 14. Logistic

Unbounded. Parameters: a (location), b > 0 (scale).
```
f(x) = (1/b) · exp((x-a)/b) / (1 + exp((x-a)/b))²
Mean = a, Variance = π²b²/3
```
Use: Models mid-value of highs and lows of samples.

## Selection Guide for Zeta Terminal

| Distribution | When to Use | scipy Function |
|-------------|-------------|----------------|
| Normal | Returns, CLT | `scipy.stats.norm` |
| Lognormal | Prices, forward values | `scipy.stats.lognorm` |
| Student-t | Heavy-tailed returns | `scipy.stats.t` |
| Poisson | Jump counts, credit events | `scipy.stats.poisson` |
| Chi-square | Hedging error | `scipy.stats.chi2` |
| Gamma | VG process | `scipy.stats.gamma` |
| Inv. Gaussian | NIG process, first passage | `scipy.stats.invgauss` |
| Pareto | Tail risk, extreme losses | `scipy.stats.pareto` |
| GEV/Gumbel | EVT for VaR | `scipy.stats.genextreme` |
| Lévy stable | Fat tails, α-stable | `scipy.stats.levy_stable` |
