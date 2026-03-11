# Numerical Methods in Finance — Formula Reference

Sources: Wilmott (2007) "FAQ in Quantitative Finance" Ch 5 & FAQs 28-30;
Glasserman (2003) "Monte Carlo Methods in Financial Engineering";
Jäckel (2002) "Monte Carlo Methods in Finance"

## 1. Monte Carlo Simulation

### Basic Algorithm
```
1. Simulate N paths of risk-neutral random walk: dS = rS dt + σS dW
2. For each path i, compute payoff: Payoff_i = f(S_T^(i))
3. Price = exp(-rT) · (1/N) · Σ Payoff_i
4. Standard error = σ_payoff / √N
```

### Discrete GBM Path Simulation
```
S_{t+dt} = S_t · exp((r - σ²/2)·dt + σ·√dt·Z)
where Z ~ N(0,1)
```
Key: Use exp() form, not Euler: S_{t+dt} = S_t + r·S_t·dt + σ·S_t·√dt·Z (less accurate).

### Correlated Paths (Cholesky)
For d assets with correlation matrix Σ:
```
L = cholesky(Σ)       # Lower triangular
Z = N(0, I_d)         # Independent normals
ε = L · Z             # Correlated normals
S_i(t+dt) = S_i(t) · exp((r - σ_i²/2)·dt + σ_i·√dt·ε_i)
```

### Convergence
```
Standard MC:      error = O(1/√N)        — independent of dimension
Quasi-MC (Sobol): error = O((log N)^d / N) — faster, weakly dimension-dependent
```
Key advantage of MC: Complexity independent of dimension. Ideal for basket options, multi-asset.

### Variance Reduction
- **Antithetic variates**: For each Z, also use -Z. Halves variance for monotonic payoffs.
- **Control variates**: Use known E[f(S)] to reduce variance. E.g., geometric Asian as control for arithmetic Asian.
- **Importance sampling**: Shift distribution to sample more from important regions.
- **Stratified sampling**: Divide [0,1] into bins, sample uniformly within each.

### Low-Discrepancy Sequences (Quasi-Monte Carlo)
Sobol', Halton, Faure sequences — deterministic, fill space more uniformly.
```
Discrepancy D*_N < C·(ln N)^d / N
Convergence: O((ln N)^d / N) vs O(1/√N) for standard MC
```
Advantage: Typically 10-100x fewer samples needed for same accuracy.
Caution: Effectiveness degrades in very high dimensions (d > 30).

## 2. Finite Difference Methods

### Grid Setup
```
S: S_min to S_max, M steps, δS = (S_max - S_min)/M
t: 0 to T, N steps, δt = T/N
V_i^k ≈ V(S_min + i·δS, k·δt)
```

### BS PDE Discretization
```
∂V/∂t + ½σ²S²·∂²V/∂S² + rS·∂V/∂S - rV = 0
```

Approximations:
```
∂V/∂S ≈ (V_{i+1} - V_{i-1}) / (2δS)          — central difference
∂²V/∂S² ≈ (V_{i+1} - 2V_i + V_{i-1}) / (δS²)  — central second
∂V/∂t ≈ (V^{k+1} - V^k) / δt                   — forward difference
```

### Explicit Method
```
V_i^k = a_i·V_{i-1}^{k+1} + b_i·V_i^{k+1} + c_i·V_{i+1}^{k+1}
```
Pros: Simple, parallelizable. Cons: Stability requires δt < δS²/(σ²S²_max).

### Implicit Method (Crank-Nicolson)
Average of explicit and implicit → second-order in both S and t.
Requires solving tridiagonal system at each time step (Thomas algorithm).
Pros: Unconditionally stable, accurate. Cons: More complex to implement.

### Method Comparison (Wilmott)
| Feature | FD | MC | Quadrature |
|---------|----|----|------------|
| Low dimensions | Excellent | Inefficient | Good |
| High dimensions | Slow | Excellent | Good |
| Path dependent | Depends | Excellent | Not good |
| Greeks | Excellent | Not good | Excellent |
| Portfolio | Inefficient | Very good | Very good |
| Decisions (American) | Excellent | Poor | Very poor |
| Non-linear PDE | Excellent | Poor | Very poor |

## 3. American Options — Longstaff-Schwartz (LSM)

```
1. Simulate N paths forward
2. At final time: cashflow = payoff
3. Walk backward through exercise dates:
   a. At time t_k, regress continuation value on basis functions of S
   b. Compare immediate exercise vs estimated continuation
   c. Exercise if immediate payoff > continuation estimate
4. Price = average of discounted optimal exercise cashflows
```
Basis functions: typically {1, S, S², S³} or Laguerre polynomials.

## 4. Greeks by Finite Differences

### Bump-and-Revalue
```
Delta ≈ (V(S+δS) - V(S-δS)) / (2δS)
Gamma ≈ (V(S+δS) - 2V(S) + V(S-δS)) / (δS²)
Vega  ≈ (V(σ+δσ) - V(σ-δσ)) / (2δσ)
Theta ≈ (V(t+δt) - V(t)) / δt
```
Key: Central differences more accurate than forward differences.

### Pathwise (Likelihood Ratio) Method for MC Greeks
```
Delta = exp(-rT) · E[payoff'(S_T) · ∂S_T/∂S_0]
      = exp(-rT) · E[payoff'(S_T) · S_T/S_0]
```
More efficient than bump-and-revalue for smooth payoffs.

## 5. Calibration Methods

### Implied Volatility (Newton-Raphson)
```
σ_{n+1} = σ_n - (V_BS(σ_n) - V_market) / Vega(σ_n)
```
Converges in 3-5 iterations. Initial guess: σ_0 ≈ √(2|ln(S/K) + rT| / T).

### Model Calibration (Least Squares)
```
min_θ Σ_i w_i · (V_model(θ; K_i, T_i) - V_market(K_i, T_i))²
```
Use `scipy.optimize.minimize` (L-BFGS-B) or `scipy.optimize.least_squares`.

## 6. Numerical Stability Notes

- **Log-space arithmetic**: Always use log prices for MC paths to avoid overflow
- **Cholesky**: Requires positive definite correlation matrix. Add small diagonal if needed: Σ + εI
- **Sobol dimensionality**: For d > 30, consider randomized QMC (scrambled Sobol)
- **FD grid boundaries**: Set S_max = 4-5× strike, check boundary condition influence
- **MC convergence**: Use confidence intervals, not point estimates. 10,000 paths minimum for pricing.

## NumPy/SciPy Implementation Notes

```python
# MC path generation (vectorized)
Z = np.random.standard_normal((n_paths, n_steps))
S = S0 * np.exp(np.cumsum((r - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z, axis=1))

# Sobol sequences
from scipy.stats.qmc import Sobol
sampler = Sobol(d=n_assets, scramble=True)
U = sampler.random(n_paths)  # uniform [0,1]^d
Z = scipy.stats.norm.ppf(U)  # transform to normal

# Cholesky correlation
L = np.linalg.cholesky(corr_matrix)
Z_corr = Z @ L.T

# Tridiagonal solver (for FD)
from scipy.linalg import solve_banded
```
