# Hidden Markov Models (HMM) — Formula Reference

Sources: Аджалова С.Ф. (2024) "Применение скрытых марковских цепей для оценки
неизмеримых экономических параметров" ВКР МГТУ Баумана;
Ширяев (2004) "Вероятность-2" (марковские цепи);
Rabiner (1989) "A Tutorial on Hidden Markov Models"

## 1. HMM Definition

Elements of a Hidden Markov Model λ = (P, Q, π):
- **State space** I = {1, ..., s} — hidden (unobservable) states
- **Observation alphabet** K = {1, ..., k} — observable symbols
- **Transition matrix** P = {p_ij}: p_ij = P(X_{t+1}=j | X_t=i)
- **Emission matrix** Q = {q_ij}: q_ij = P(Y_t=j | X_t=i)
- **Initial distribution** π = {π_i}: π_i = P(X_0=i)

Markov property: P(X_{t+1} | X_t, X_{t-1}, ...) = P(X_{t+1} | X_t)

## 2. Three Fundamental Problems

| Problem | Algorithm | Complexity |
|---------|-----------|------------|
| Evaluation: P(Y\|λ) | Forward-Backward | O(s²T) |
| Decoding: argmax P(X\|Y,λ) | Viterbi | O(s²T) |
| Learning: argmax_λ P(Y\|λ) | Baum-Welch (EM) | O(s²T) per iteration |

Brute-force decoding: O(s^T) — exponentially worse.

## 3. Forward-Backward Algorithm

### Forward variable α
```
α_t(j) = P(Y_0=y_0, ..., Y_t=y_t, X_t=j | λ)
```

Initialization:
```
α_0(j) = π_j · q_j(y_0)
```

Recursion (Аджалова eq 54):
```
α_t(j) = [Σ_i α_{t-1}(i) · p_ij] · q_j(y_t)
```

### Backward variable β
```
β_t(j) = P(Y_{t+1}=y_{t+1}, ..., Y_T=y_T | X_t=j, λ)
```

Initialization:
```
β_T(j) = 1
```

Recursion (Аджалова eq 56):
```
β_t(j) = Σ_i p_ji · q_i(y_{t+1}) · β_{t+1}(i)
```

### Likelihood
```
P(Y | λ) = Σ_j α_T(j) = Σ_j α_t(j) · β_t(j)  (for any t)
```

### Log-space computation
To avoid underflow, work in log-space:
```
log α_t(j) = log q_j(y_t) + log_sum_exp_i [log α_{t-1}(i) + log p_ij]
```
where log_sum_exp(x_1,...,x_n) = max(x) + log(Σ exp(x_i - max(x)))

## 4. Viterbi Algorithm (Dynamic Programming)

Find most probable state sequence X* = argmax_X P(X | Y, λ)

### Variables
```
δ_t(j) = max_{x_0,...,x_{t-1}} P(X_0=x_0,...,X_{t-1}=x_{t-1}, X_t=j, Y_0,...,Y_t | λ)
ψ_t(j) = argmax_i [δ_{t-1}(i) · p_ij]  — backpointer
```

### Algorithm (Аджалова eq 69-75)
1. Init: δ_0(j) = π_j · q_j(y_0), ψ_0(j) = 0
2. Recursion: δ_t(j) = max_i [δ_{t-1}(i) · p_ij] · q_j(y_t)
             ψ_t(j) = argmax_i [δ_{t-1}(i) · p_ij]
3. Termination: P* = max_j δ_T(j), x*_T = argmax_j δ_T(j)
4. Backtracking: x*_t = ψ_{t+1}(x*_{t+1})

Work in log-space to avoid underflow.

## 5. Baum-Welch Algorithm (EM for HMM)

Iteratively re-estimates λ = (P, Q, π) to maximize P(Y|λ).

### E-step: compute auxiliary variables

Posterior state probability:
```
γ_t(i) = P(X_t=i | Y, λ) = α_t(i)·β_t(i) / Σ_j α_t(j)·β_t(j)
```

Posterior transition probability:
```
ξ_t(i,j) = P(X_t=i, X_{t+1}=j | Y, λ)
         = α_t(i)·p_ij·q_j(y_{t+1})·β_{t+1}(j) / P(Y|λ)
```

### M-step: re-estimate parameters (Аджалова eq 21-23, 44, 48, 50)

Initial distribution:
```
π̂_i = γ_0(i)
```

Transition matrix:
```
p̂_ij = Σ_{t=0}^{T-1} ξ_t(i,j) / Σ_{t=0}^{T-1} γ_t(i)
```

Emission matrix:
```
q̂_j(k) = Σ_{t: y_t=k} γ_t(j) / Σ_{t=0}^T γ_t(j)
```

### Convergence (Аджалова Theorem 3)
- Log-likelihood is monotonically non-decreasing: L(λ̂) ≥ L(λ)
- Under mild regularity conditions, iterates converge to a local maximum
- Stopping criterion: |L^{n+1} - L^n| / |L^n| < ε (e.g., ε = 0.01%)

### Practical notes from Аджалова
- Tested on 3-state HMM with 100-observation sequences
- 149 iterations to convergence (typical: 50-200)
- Filtering accuracy: ~79% state recovery (single sequence)
- Multi-run averaging improves parameter estimates
- Applied to GDP → unemployment prediction with 84% accuracy

## 6. Gaussian HMM (Continuous Observations)

Replace discrete emission Q with Gaussian:
```
b_j(y) = N(y; μ_j, σ²_j) = (1/√(2πσ²_j)) · exp(-(y-μ_j)²/(2σ²_j))
```

M-step for Gaussian emissions:
```
μ̂_j = Σ_t γ_t(j)·y_t / Σ_t γ_t(j)
σ̂²_j = Σ_t γ_t(j)·(y_t - μ̂_j)² / Σ_t γ_t(j)
```

## 7. Applications in Zeta Terminal

### Regime Detection (existing: spectral_regime_service.py)
States = market regimes (bull/bear/neutral)
Observations = returns, volatility, volume

### Structural Break Detection
HMM with 2-3 states for detecting:
- Volatility regime changes (low-vol ↔ high-vol)
- Trend changes (trending ↔ mean-reverting)
- Correlation regime shifts

### Economic State Estimation (Аджалова application)
Hidden states = economic conditions (expansion/recession/stagnation)
Observations = GDP, CPI, employment data
Use Viterbi to decode most likely economic regime path.

## 8. Implementation (hmmlearn / manual)

```python
# Using hmmlearn
from hmmlearn import hmm
model = hmm.GaussianHMM(n_components=3, covariance_type="diag", n_iter=200)
model.fit(observations.reshape(-1, 1))
states = model.predict(observations.reshape(-1, 1))

# Manual forward (log-space, numpy)
def forward_log(obs, log_pi, log_P, log_Q):
    T, S = len(obs), len(log_pi)
    log_alpha = np.full((T, S), -np.inf)
    log_alpha[0] = log_pi + log_Q[:, obs[0]]
    for t in range(1, T):
        for j in range(S):
            log_alpha[t, j] = log_Q[j, obs[t]] + logsumexp(log_alpha[t-1] + log_P[:, j])
    return log_alpha
```

## Numerical Stability
1. **Always use log-space** for forward/backward (α,β underflow in ~50 steps)
2. **Multiple restarts**: Baum-Welch finds local optima; run 5-10x with random init
3. **Scaling**: Alternative to log-space — normalize α_t at each step, track scale factors
4. **Degenerate states**: If γ_t(j)≈0 for all t, state j is unused — reduce n_components
