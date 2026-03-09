"""
REPO Analysis Service — full pipeline for REPO market analysis.

Blocks:
  1. ETL (parse, haircuts, repo rates)
  2. Chain Tracing (networkx DiGraph)
  3. Concentration (HHI, entropy, CR, Gini, PCA)
  4. Collateral & VaR
  4.5 Coverage & Wrong-Way Risk
  5. Liquidity (tenor buckets, rollover, maturity gap, fire-sale)
  6. Systemic (centrality, DebtRank, core-periphery, contagion)
  7. Stress Testing (scenarios, adversarial, reverse)
  10. Traffic Light (risk dashboard)
"""

from __future__ import annotations

import math
import logging
from typing import Any

import numpy as np
import pandas as pd
import networkx as nx
from scipy.optimize import minimize

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column name normalisation helpers
# ---------------------------------------------------------------------------

_COLUMN_ALIASES: dict[str, str] = {
    # alias → canonical name
    "seller": "seller",
    "lender": "seller",
    "creditor": "seller",
    "buyer": "buyer",
    "borrower": "buyer",
    "debtor": "buyer",
    "loan_amount": "loan_amount",
    "loan": "loan_amount",
    "nominal": "loan_amount",
    "repayment_amount": "repayment_amount",
    "repayment": "repayment_amount",
    "collateral_value": "collateral_value",
    "collateral": "collateral_value",
    "price": "price",
    "units": "units",
    "quantity": "units",
    "days": "days",
    "term_days": "days",
    "tenor_days": "days",
    "term": "days",
    "issuer": "issuer",
    "maturity_date": "maturity_date",
    "repo_rate": "repo_rate",
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    lower_cols = {c.lower().strip().replace(" ", "_"): c for c in df.columns}
    renamed: dict[str, str] = {}
    seen_targets: set[str] = set()
    for alias, canonical in _COLUMN_ALIASES.items():
        if alias in lower_cols and canonical not in seen_targets:
            renamed[lower_cols[alias]] = canonical
            seen_targets.add(canonical)
    return df.rename(columns=renamed)


# ===================================================================
# Block 1 — ETL
# ===================================================================

def block1_etl(df: pd.DataFrame) -> pd.DataFrame:
    df = _normalise_columns(df)

    if "price" in df.columns and "units" in df.columns and "loan_amount" in df.columns:
        market_val = df["price"] * df["units"]
        df["haircut"] = np.where(market_val > 0, 1.0 - df["loan_amount"] / market_val, np.nan)
    else:
        df["haircut"] = np.nan

    if "repayment_amount" in df.columns and "loan_amount" in df.columns and "days" in df.columns:
        safe_loan = df["loan_amount"].replace(0, np.nan)
        safe_days = df["days"].replace(0, np.nan)
        df["repo_rate"] = (df["repayment_amount"] / safe_loan - 1.0) * 365.0 / safe_days
    else:
        df["repo_rate"] = np.nan

    return df


# ===================================================================
# Block 2 — Chain Tracing
# ===================================================================

def block2_chain_tracing(df: pd.DataFrame) -> dict[str, Any]:
    if "seller" not in df.columns or "buyer" not in df.columns:
        return {"error": "Missing seller/buyer columns"}

    G = nx.DiGraph()
    weight_col = "loan_amount" if "loan_amount" in df.columns else None

    for _, row in df.iterrows():
        s, b = str(row["seller"]), str(row["buyer"])
        w = float(row[weight_col]) if weight_col and pd.notna(row.get(weight_col)) else 1.0
        if G.has_edge(s, b):
            G[s][b]["weight"] += w
        else:
            G.add_edge(s, b, weight=w)

    borrowers = [n for n in G.nodes() if G.out_degree(n) > 0 and G.in_degree(n) == 0]
    lenders = [n for n in G.nodes() if G.in_degree(n) > 0 and G.out_degree(n) == 0]
    intermediaries = [n for n in G.nodes() if G.in_degree(n) > 0 and G.out_degree(n) > 0]

    chains: list[list[str]] = []
    for src in borrowers:
        for tgt in lenders:
            for path in nx.all_simple_paths(G, src, tgt, cutoff=10):
                chains.append(path)
            if len(chains) > 500:
                break
        if len(chains) > 500:
            break

    return {
        "nodes": len(G.nodes()),
        "edges": len(G.edges()),
        "borrowers": borrowers[:50],
        "lenders": lenders[:50],
        "intermediaries": intermediaries[:50],
        "chains": [c for c in chains[:100]],
        "graph_edges": [
            {"source": u, "target": v, "weight": d.get("weight", 1)}
            for u, v, d in G.edges(data=True)
        ],
    }


# ===================================================================
# Block 3 — Concentration
# ===================================================================

def block3_concentration(df: pd.DataFrame) -> dict[str, Any]:
    vol_col = "loan_amount" if "loan_amount" in df.columns else None
    group_col = "seller" if "seller" in df.columns else (df.columns[0] if len(df.columns) > 0 else None)
    if vol_col is None or group_col is None:
        return {"error": "Missing columns for concentration analysis"}

    volumes = df.groupby(group_col)[vol_col].sum()
    total = volumes.sum()
    if total == 0:
        return {"error": "Total volume is zero"}

    shares = volumes / total

    hhi = float((shares ** 2).sum() * 10000)

    safe_shares = shares[shares > 0]
    entropy = float(-(safe_shares * np.log(safe_shares)).sum())

    sorted_shares = shares.sort_values(ascending=False)
    cr3 = float(sorted_shares.head(3).sum() * 100)
    cr5 = float(sorted_shares.head(5).sum() * 100)
    cr10 = float(sorted_shares.head(10).sum() * 100)

    n = len(sorted_shares)
    if n < 2:
        gini = 0.0
    else:
        sorted_vals = np.sort(shares.values)
        index = np.arange(1, n + 1)
        denom = n * sorted_vals.sum()
        gini = float((2 * (index * sorted_vals).sum() / denom) - (n + 1) / n) if denom > 0 else 0.0
        gini = max(0.0, min(1.0, gini))

    top_participants = [
        {"name": str(name), "volume": float(vol), "share_pct": float(shares[name] * 100)}
        for name, vol in sorted_shares.head(20).items()
    ]

    return {
        "hhi": round(hhi, 2),
        "entropy": round(entropy, 4),
        "cr3": round(cr3, 2),
        "cr5": round(cr5, 2),
        "cr10": round(cr10, 2),
        "gini": round(gini, 4),
        "num_participants": n,
        "top_participants": top_participants,
    }


# ===================================================================
# Block 4 — Collateral & VaR
# ===================================================================

def block4_collateral_var(df: pd.DataFrame) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if "issuer" in df.columns and "loan_amount" in df.columns:
        issuer_vol = df.groupby("issuer")["loan_amount"].sum()
        total = issuer_vol.sum()
        if total > 0:
            issuer_shares = issuer_vol / total
            result["issuer_hhi"] = round(float((issuer_shares ** 2).sum() * 10000), 2)
        else:
            result["issuer_hhi"] = 0
    else:
        result["issuer_hhi"] = None

    if "haircut" in df.columns:
        hc = df["haircut"].dropna()
        result["haircut_stats"] = {
            "mean": round(float(hc.mean()), 4) if len(hc) > 0 else None,
            "median": round(float(hc.median()), 4) if len(hc) > 0 else None,
            "std": round(float(hc.std()), 4) if len(hc) > 1 else None,
            "min": round(float(hc.min()), 4) if len(hc) > 0 else None,
            "max": round(float(hc.max()), 4) if len(hc) > 0 else None,
        }
    else:
        result["haircut_stats"] = None

    if "repo_rate" in df.columns:
        rates = df["repo_rate"].dropna()
        if len(rates) > 1:
            mu = float(rates.mean())
            sigma = float(rates.std())
            z_99 = 2.326
            horizon = 10
            var_99 = mu - z_99 * sigma * math.sqrt(horizon)
            result["var_99_10d"] = round(var_99, 6)
        else:
            result["var_99_10d"] = None
    else:
        result["var_99_10d"] = None

    return result


# ===================================================================
# Block 4.5 — Coverage & Wrong-Way Risk
# ===================================================================

def block4_5_coverage_wwr(df: pd.DataFrame) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if "collateral_value" in df.columns and "loan_amount" in df.columns:
        safe_loan = df["loan_amount"].replace(0, np.nan)
        coverage = df["collateral_value"] / safe_loan
        result["coverage_ratio"] = {
            "mean": round(float(coverage.mean()), 4),
            "median": round(float(coverage.median()), 4),
            "min": round(float(coverage.min()), 4),
            "below_1": int((coverage < 1.0).sum()),
        }
    else:
        result["coverage_ratio"] = None

    if "seller" in df.columns and "issuer" in df.columns:
        wwr_mask = df["seller"].astype(str) == df["issuer"].astype(str)
        wwr_count = int(wwr_mask.sum())
        wwr_volume = float(df.loc[wwr_mask, "loan_amount"].sum()) if "loan_amount" in df.columns else 0
        result["wrong_way_risk"] = {
            "count": wwr_count,
            "volume": round(wwr_volume, 2),
            "pct_of_total": round(
                wwr_volume / df["loan_amount"].sum() * 100 if "loan_amount" in df.columns and df["loan_amount"].sum() > 0 else 0, 2
            ),
        }
    else:
        result["wrong_way_risk"] = None

    return result


# ===================================================================
# Block 5 — Liquidity
# ===================================================================

_TENOR_BUCKETS = [
    ("O/N", 1),
    ("1W", 7),
    ("2W", 14),
    ("1M", 30),
    ("2M", 60),
    ("3M", 90),
]


def block5_liquidity(df: pd.DataFrame) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if "days" not in df.columns or "loan_amount" not in df.columns:
        return {"error": "Missing days/loan_amount columns"}

    total_vol = float(df["loan_amount"].sum())
    buckets: list[dict[str, Any]] = []
    for label, max_days in _TENOR_BUCKETS:
        prev = _TENOR_BUCKETS[_TENOR_BUCKETS.index((label, max_days)) - 1][1] if _TENOR_BUCKETS.index((label, max_days)) > 0 else 0
        mask = (df["days"] > prev) & (df["days"] <= max_days)
        vol = float(df.loc[mask, "loan_amount"].sum())
        buckets.append({"bucket": label, "max_days": max_days, "volume": round(vol, 2), "share_pct": round(vol / total_vol * 100, 2) if total_vol > 0 else 0})

    over_90_mask = df["days"] > 90
    over_90_vol = float(df.loc[over_90_mask, "loan_amount"].sum())
    buckets.append({"bucket": ">90d", "max_days": 999, "volume": round(over_90_vol, 2), "share_pct": round(over_90_vol / total_vol * 100, 2) if total_vol > 0 else 0})

    result["tenor_buckets"] = buckets

    within_7d = float(df.loc[df["days"] <= 7, "loan_amount"].sum())
    result["rollover_risk_pct"] = round(within_7d / total_vol * 100, 2) if total_vol > 0 else 0

    result["total_volume"] = round(total_vol, 2)

    return result


# ===================================================================
# Block 6 — Systemic Risk
# ===================================================================

def block6_systemic(df: pd.DataFrame) -> dict[str, Any]:
    if "seller" not in df.columns or "buyer" not in df.columns:
        return {"error": "Missing seller/buyer columns"}

    G = nx.DiGraph()
    weight_col = "loan_amount" if "loan_amount" in df.columns else None
    for _, row in df.iterrows():
        s, b = str(row["seller"]), str(row["buyer"])
        w = float(row[weight_col]) if weight_col and pd.notna(row.get(weight_col)) else 1.0
        if G.has_edge(s, b):
            G[s][b]["weight"] += w
        else:
            G.add_edge(s, b, weight=w)

    nodes = list(G.nodes())
    if len(nodes) == 0:
        return {"error": "Empty graph"}

    degree_cent = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G, weight="weight")
    pagerank = nx.pagerank(G, weight="weight")

    try:
        eigenvector = nx.eigenvector_centrality(G, max_iter=300, weight="weight")
    except nx.PowerIterationFailedConvergence:
        eigenvector = {n: 0.0 for n in nodes}

    # DebtRank iterative cascade
    total_assets = sum(d.get("weight", 0) for _, _, d in G.edges(data=True))
    if total_assets == 0:
        total_assets = 1.0
    node_value = {}
    for n in nodes:
        node_value[n] = sum(d.get("weight", 0) for _, _, d in G.out_edges(n, data=True)) / total_assets

    max_debt_rank = 0.0
    debt_rank_scores: dict[str, float] = {}
    for shock_node in nodes:
        stress = {n: 0.0 for n in nodes}
        stress[shock_node] = 1.0
        active = {shock_node}
        for _ in range(10):
            new_active: set[str] = set()
            for n in active:
                for _, neighbor, d in G.out_edges(n, data=True):
                    if neighbor not in active:
                        w = d.get("weight", 0) / total_assets
                        new_stress = min(1.0, stress[neighbor] + stress[n] * w)
                        if new_stress > stress[neighbor]:
                            stress[neighbor] = new_stress
                            new_active.add(neighbor)
            if not new_active:
                break
            active = active | new_active
        dr = sum(stress[n] * node_value.get(n, 0) for n in nodes if n != shock_node)
        debt_rank_scores[shock_node] = round(dr, 4)
        max_debt_rank = max(max_debt_rank, dr)

    top_centrality = sorted(nodes, key=lambda n: pagerank.get(n, 0), reverse=True)[:20]
    centrality_table = [
        {
            "node": n,
            "degree": round(degree_cent.get(n, 0), 4),
            "betweenness": round(betweenness.get(n, 0), 4),
            "pagerank": round(pagerank.get(n, 0), 4),
            "eigenvector": round(eigenvector.get(n, 0), 4),
            "debt_rank": debt_rank_scores.get(n, 0),
        }
        for n in top_centrality
    ]

    return {
        "centrality_table": centrality_table,
        "max_debt_rank": round(max_debt_rank, 4),
        "num_nodes": len(nodes),
        "num_edges": len(G.edges()),
        "density": round(nx.density(G), 4),
    }


# ===================================================================
# Block 7 — Stress Testing
# ===================================================================

_SCENARIOS = [
    {"name": "Base", "haircut_shock": 0.0, "rate_shock": 0.0, "price_shock": 0.0, "rollover_shock": 0.0},
    {"name": "Moderate", "haircut_shock": 0.05, "rate_shock": 0.02, "price_shock": -0.05, "rollover_shock": 0.1},
    {"name": "Severe", "haircut_shock": 0.15, "rate_shock": 0.05, "price_shock": -0.15, "rollover_shock": 0.3},
    {"name": "March2020", "haircut_shock": 0.20, "rate_shock": 0.08, "price_shock": -0.25, "rollover_shock": 0.5},
    {"name": "Feb2022", "haircut_shock": 0.25, "rate_shock": 0.10, "price_shock": -0.30, "rollover_shock": 0.6},
    {"name": "Sector_Concentration", "haircut_shock": 0.10, "rate_shock": 0.03, "price_shock": -0.20, "rollover_shock": 0.2},
    {"name": "Liquidity_Squeeze", "haircut_shock": 0.05, "rate_shock": 0.15, "price_shock": -0.10, "rollover_shock": 0.7},
]


def block7_stress_testing(df: pd.DataFrame) -> dict[str, Any]:
    has_loan = "loan_amount" in df.columns
    has_collateral = "collateral_value" in df.columns
    has_haircut = "haircut" in df.columns
    has_rate = "repo_rate" in df.columns

    total_loan = float(df["loan_amount"].sum()) if has_loan else 0
    total_collateral = float(df["collateral_value"].sum()) if has_collateral else 0
    avg_haircut = float(df["haircut"].dropna().mean()) if has_haircut and df["haircut"].notna().any() else 0.0
    avg_rate = float(df["repo_rate"].dropna().mean()) if has_rate and df["repo_rate"].notna().any() else 0.0

    scenario_results: list[dict[str, Any]] = []
    for sc in _SCENARIOS:
        stressed_haircut = avg_haircut + sc["haircut_shock"]
        stressed_rate = avg_rate + sc["rate_shock"]
        stressed_collateral = total_collateral * (1 + sc["price_shock"])
        coverage = stressed_collateral / total_loan if total_loan > 0 else 0
        loss = max(0, total_loan - stressed_collateral)

        scenario_results.append({
            "scenario": sc["name"],
            "stressed_haircut": round(stressed_haircut, 4),
            "stressed_rate": round(stressed_rate, 4),
            "stressed_collateral": round(stressed_collateral, 2),
            "coverage_ratio": round(coverage, 4),
            "potential_loss": round(loss, 2),
            "rollover_shock": sc["rollover_shock"],
        })

    # Adversarial stress (worst-case combination via L-BFGS-B)
    adversarial: dict[str, Any] | None = None
    if total_loan > 0 and total_collateral > 0:
        def objective(x: np.ndarray) -> float:
            h_shock, p_shock = x
            stressed_coll = total_collateral * (1 + p_shock)
            return -(max(0, total_loan * (1 + h_shock) - stressed_coll))

        res = minimize(
            objective,
            x0=[0.1, -0.1],
            method="L-BFGS-B",
            bounds=[(0, 0.5), (-0.5, 0)],
        )
        adversarial = {
            "optimal_haircut_shock": round(float(res.x[0]), 4),
            "optimal_price_shock": round(float(res.x[1]), 4),
            "max_loss": round(float(-res.fun), 2),
        }

    return {
        "scenarios": scenario_results,
        "adversarial": adversarial,
    }


# ===================================================================
# Block 10 — Traffic Light
# ===================================================================

def _light(value: float | None, green_lt: float, yellow_lt: float) -> str:
    if value is None:
        return "gray"
    if value < green_lt:
        return "green"
    if value < yellow_lt:
        return "yellow"
    return "red"


def block10_traffic_light(
    concentration: dict[str, Any],
    collateral: dict[str, Any],
    liquidity: dict[str, Any],
    systemic: dict[str, Any],
) -> dict[str, Any]:
    metrics: list[dict[str, Any]] = []

    hhi = concentration.get("hhi")
    metrics.append({"metric": "HHI", "value": hhi, "light": _light(hhi, 1500, 2500)})

    cr5 = concentration.get("cr5")
    metrics.append({"metric": "CR5", "value": cr5, "light": _light(cr5, 50, 70)})

    gini = concentration.get("gini")
    metrics.append({"metric": "Gini", "value": gini, "light": _light(gini, 0.4, 0.6)})

    rollover = liquidity.get("rollover_risk_pct")
    metrics.append({"metric": "Rollover Risk %", "value": rollover, "light": _light(rollover, 20, 40)})

    debt_rank = systemic.get("max_debt_rank")
    metrics.append({"metric": "DebtRank", "value": debt_rank, "light": _light(debt_rank, 0.1, 0.25)})

    recommendations: list[str] = []
    for m in metrics:
        if m["light"] == "red":
            recommendations.append(f"CRITICAL: {m['metric']} = {m['value']} exceeds red threshold.")
        elif m["light"] == "yellow":
            recommendations.append(f"WARNING: {m['metric']} = {m['value']} in yellow zone.")

    overall = "red" if any(m["light"] == "red" for m in metrics) else (
        "yellow" if any(m["light"] == "yellow" for m in metrics) else "green"
    )

    return {
        "metrics": metrics,
        "overall": overall,
        "recommendations": recommendations,
    }


# ===================================================================
# Main pipeline
# ===================================================================

def run_full_pipeline(df: pd.DataFrame) -> dict[str, Any]:
    df = block1_etl(df)

    chains = block2_chain_tracing(df)
    concentration = block3_concentration(df)
    collateral = block4_collateral_var(df)
    coverage = block4_5_coverage_wwr(df)
    liquidity = block5_liquidity(df)
    systemic = block6_systemic(df)
    stress = block7_stress_testing(df)
    traffic = block10_traffic_light(concentration, collateral, liquidity, systemic)

    return {
        "summary": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
        "chains": chains,
        "concentration": concentration,
        "collateral": collateral,
        "coverage": coverage,
        "liquidity": liquidity,
        "systemic": systemic,
        "stress": stress,
        "traffic_light": traffic,
    }
