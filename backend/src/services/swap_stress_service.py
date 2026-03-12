"""
Service for swap portfolio stress testing.
Applies curve, spread, and volatility shocks to swap positions,
computes Greeks (DV01, gamma, vega, theta) and key rate durations.
"""

from src.services.swap_service import calculate_swap_valuation

# Predefined stress scenarios matching the frontend StressTestingSwap.vue
PREDEFINED_SCENARIOS: list[dict] = [
    {
        "id": 1,
        "name": "Parallel shift +200 bp",
        "description": "All rates rise by 200 basis points",
        "shockType": "Curve",
        "severity": "high",
        "probability": 0.08,
        "duration": "1-2 days",
        "shocks": {"curve_shift_bp": 200, "vol_shift_pct": -5},
    },
    {
        "id": 2,
        "name": "Parallel shift -200 bp",
        "description": "All rates fall by 200 basis points",
        "shockType": "Curve",
        "severity": "high",
        "probability": 0.08,
        "duration": "1-2 days",
        "shocks": {"curve_shift_bp": -200, "vol_shift_pct": 5},
    },
    {
        "id": 3,
        "name": "Curve twist",
        "description": "Short rates +150 bp, long rates -50 bp",
        "shockType": "Curve",
        "severity": "medium",
        "probability": 0.18,
        "duration": "2-5 days",
        "shocks": {"twist_short_bp": 150, "twist_long_bp": -50},
    },
    {
        "id": 4,
        "name": "Butterfly",
        "description": "Belly of curve moves relative to wings",
        "shockType": "Curve",
        "severity": "low",
        "probability": 0.25,
        "duration": "3-10 days",
        "shocks": {"butterfly_wing_bp": 50, "butterfly_belly_bp": -100},
    },
    {
        "id": 5,
        "name": "Credit spread +100 bp",
        "description": "Wide OAS expansion (+100 bp)",
        "shockType": "Spread",
        "severity": "high",
        "probability": 0.12,
        "duration": "1-5 days",
        "shocks": {"spread_shift_bp": 100, "vol_shift_pct": 8},
    },
    {
        "id": 6,
        "name": "Credit spread -50 bp",
        "description": "Spread compression (OAS -50 bp)",
        "shockType": "Spread",
        "severity": "medium",
        "probability": 0.20,
        "duration": "2-10 days",
        "shocks": {"spread_shift_bp": -50, "vol_shift_pct": -4},
    },
    {
        "id": 7,
        "name": "Rate vol spike (Swaption)",
        "description": "Swap rate volatility +300 bp (ATM vol +5%)",
        "shockType": "Vol",
        "severity": "high",
        "probability": 0.06,
        "duration": "1-3 days",
        "shocks": {"vol_shift_pct": 5, "curve_shift_bp": 0},
    },
    {
        "id": 8,
        "name": "Rate vol drop",
        "description": "Swap rate volatility -200 bp",
        "shockType": "Vol",
        "severity": "medium",
        "probability": 0.15,
        "duration": "5-15 days",
        "shocks": {"vol_shift_pct": -3.5, "curve_shift_bp": 0},
    },
    {
        "id": 9,
        "name": "Shock scenario",
        "description": "Combined: rates +150 bp, spread +75 bp, vol +4%",
        "shockType": "Curve",
        "severity": "critical",
        "probability": 0.02,
        "duration": "1-2 days",
        "shocks": {"curve_shift_bp": 150, "spread_shift_bp": 75, "vol_shift_pct": 4},
    },
]


def _revalue_swap(
    notional: float,
    tenor: float,
    fixed_rate: float,
    floating_rate: float,
    spread: float,
    coupons_per_year: int,
    discount_rate: float,
    volatility: float | None = None,
    swap_type: str = "irs",
) -> dict:
    """Wrapper around calculate_swap_valuation for stress re-pricing."""
    return calculate_swap_valuation(
        notional=notional,
        tenor=tenor,
        fixed_rate=fixed_rate,
        floating_rate=floating_rate,
        spread=spread,
        coupons_per_year=coupons_per_year,
        discount_rate=discount_rate,
        volatility=volatility,
        swap_type=swap_type,
    )


def apply_curve_shock(
    position: dict,
    shift_bp: float,
    multiplier: float = 1.0,
) -> dict:
    """
    Apply a parallel curve shift to a swap position.

    Args:
        position: Swap position parameters.
        shift_bp: Basis-point shift to apply (e.g. +200 = rates up 200bp).
        multiplier: Severity multiplier.

    Returns:
        Dict with base_pv, shocked_pv, pnl_impact.
    """
    effective_shift = shift_bp * multiplier / 100.0  # bp -> percentage points

    base = _revalue_swap(**position)

    shocked_pos = {
        **position,
        "fixed_rate": position["fixed_rate"] + effective_shift,
        "floating_rate": position["floating_rate"] + effective_shift,
        "discount_rate": position["discount_rate"] + effective_shift,
    }
    shocked = _revalue_swap(**shocked_pos)

    return {
        "basePv": base["swapValue"],
        "shockedPv": shocked["swapValue"],
        "pnlImpact": shocked["swapValue"] - base["swapValue"],
    }


def apply_spread_shock(
    position: dict,
    spread_shift_bp: float,
    multiplier: float = 1.0,
) -> dict:
    """
    Apply a credit/OAS spread shock to the floating leg.

    Args:
        position: Swap position parameters.
        spread_shift_bp: Basis-point spread shift.
        multiplier: Severity multiplier.

    Returns:
        Dict with base_pv, shocked_pv, pnl_impact.
    """
    effective_shift = spread_shift_bp * multiplier  # spread is already in bp

    base = _revalue_swap(**position)

    shocked_pos = {
        **position,
        "spread": position["spread"] + effective_shift,
    }
    shocked = _revalue_swap(**shocked_pos)

    return {
        "basePv": base["swapValue"],
        "shockedPv": shocked["swapValue"],
        "pnlImpact": shocked["swapValue"] - base["swapValue"],
    }


def apply_vol_shock(
    position: dict,
    vol_shift_pct: float,
    multiplier: float = 1.0,
) -> dict:
    """
    Apply a volatility shock and compute vega via finite difference.

    Args:
        position: Swap position parameters.
        vol_shift_pct: Percentage-point vol shift (e.g. +5 = vol up 5pp).
        multiplier: Severity multiplier.

    Returns:
        Dict with vega, pnl from vol move.
    """
    effective_shift = vol_shift_pct * multiplier
    base_vol = position.get("volatility") or 20.0

    # Base PV at current vol
    pos_base = {**position, "volatility": base_vol}
    base = _revalue_swap(**pos_base)

    # Shocked PV
    pos_shocked = {**position, "volatility": base_vol + effective_shift}
    shocked = _revalue_swap(**pos_shocked)

    # Vega = dPV / dVol (per 1% vol move)
    vega = (shocked["swapValue"] - base["swapValue"]) / effective_shift if effective_shift != 0.0 else 0.0

    return {
        "basePv": base["swapValue"],
        "shockedPv": shocked["swapValue"],
        "pnlImpact": shocked["swapValue"] - base["swapValue"],
        "vega": vega,
    }


def compute_swap_greeks(position: dict) -> dict:
    """
    Compute swap Greeks via finite difference.

    Returns:
        delta (DV01 per 100bp), gamma, vega (per 1% vol), theta (1-day decay).
    """
    bump_bp = 1.0  # 1 basis point
    bump_pct = bump_bp / 100.0

    base = _revalue_swap(**position)
    base_pv = base["swapValue"]

    # Delta (DV01): PV change per 1bp rate move
    pos_up = {
        **position,
        "fixed_rate": position["fixed_rate"] + bump_pct,
        "floating_rate": position["floating_rate"] + bump_pct,
        "discount_rate": position["discount_rate"] + bump_pct,
    }
    pos_down = {
        **position,
        "fixed_rate": position["fixed_rate"] - bump_pct,
        "floating_rate": position["floating_rate"] - bump_pct,
        "discount_rate": position["discount_rate"] - bump_pct,
    }
    pv_up = _revalue_swap(**pos_up)["swapValue"]
    pv_down = _revalue_swap(**pos_down)["swapValue"]

    dv01 = (pv_up - pv_down) / 2.0  # per 1bp
    delta = dv01 * 100  # per 100bp (M/100bp)

    # Gamma: second-order rate sensitivity
    gamma = (pv_up - 2 * base_pv + pv_down) / (bump_pct ** 2)

    # Vega: PV change per 1% vol move
    base_vol = position.get("volatility") or 20.0
    pos_vol_up = {**position, "volatility": base_vol + 1.0}
    pos_vol_down = {**position, "volatility": max(base_vol - 1.0, 0.1)}
    vega = (_revalue_swap(**pos_vol_up)["swapValue"] - _revalue_swap(**pos_vol_down)["swapValue"]) / 2.0

    # Theta: time-decay (approximate by reducing tenor by 1/365)
    day_fraction = 1.0 / 365.0
    if position["tenor"] > day_fraction:
        pos_theta = {**position, "tenor": position["tenor"] - day_fraction}
        theta = _revalue_swap(**pos_theta)["swapValue"] - base_pv
    else:
        theta = 0.0

    return {
        "delta": float(delta),
        "gamma": float(gamma),
        "vega": float(vega),
        "theta": float(theta),
    }


def compute_key_rate_durations(
    position: dict,
    multiplier: float = 1.0,
) -> dict[str, float]:
    """
    Compute key rate durations by bumping 2Y/5Y/10Y/30Y tenors independently by 1bp.

    For simplicity, we map the position's tenor to the nearest bucket and
    apply proportional sensitivity.

    Returns:
        Dict mapping tenor labels to KRD values (M per bp).
    """
    tenor = position["tenor"]
    base = _revalue_swap(**position)
    base_pv = base["swapValue"]

    bump_pct = 0.01  # 1bp in percentage points
    buckets = {"2Y": 2.0, "5Y": 5.0, "10Y": 10.0, "30Y": 30.0}
    krd: dict[str, float] = {}

    for label, bucket_tenor in buckets.items():
        # Weight: how much this bucket affects the position
        # Closer tenors get higher weight
        distance = abs(tenor - bucket_tenor)
        weight = max(0.0, 1.0 - distance / 30.0)

        if weight > 0:
            # Bump discount rate proportional to bucket weight
            pos_bumped = {
                **position,
                "discount_rate": position["discount_rate"] + bump_pct * weight,
            }
            bumped_pv = _revalue_swap(**pos_bumped)["swapValue"]
            krd_val = (bumped_pv - base_pv) / bump_pct * weight
        else:
            krd_val = 0.0

        krd[label] = float(krd_val * multiplier)

    return krd


def _build_market_shocks(scenario: dict, multiplier: float) -> dict[str, str]:
    """Build human-readable market shock descriptions for a scenario."""
    shocks = scenario.get("shocks", {})
    result: dict[str, str] = {}

    curve_bp = shocks.get("curve_shift_bp", 0)
    if curve_bp:
        val = curve_bp * multiplier
        sign = "+" if val >= 0 else ""
        result["Key Rate (2Y)"] = f"{sign}{val:.0f} bp"
        result["Key Rate (5Y)"] = f"{sign}{val:.0f} bp"
        result["Key Rate (10Y)"] = f"{sign}{val:.0f} bp"

    twist_short = shocks.get("twist_short_bp", 0)
    twist_long = shocks.get("twist_long_bp", 0)
    if twist_short or twist_long:
        s_val = twist_short * multiplier
        l_val = twist_long * multiplier
        result["Key Rate (2Y)"] = f"{'+' if s_val >= 0 else ''}{s_val:.0f} bp"
        result["Key Rate (5Y)"] = f"{'+' if (s_val + l_val) / 2 >= 0 else ''}{(s_val + l_val) / 2:.0f} bp"
        result["Key Rate (10Y)"] = f"{'+' if l_val >= 0 else ''}{l_val:.0f} bp"
        result["Slope"] = f"{'+' if (l_val - s_val) >= 0 else ''}{l_val - s_val:.0f} bp"

    butterfly_wing = shocks.get("butterfly_wing_bp", 0)
    butterfly_belly = shocks.get("butterfly_belly_bp", 0)
    if butterfly_wing or butterfly_belly:
        w_val = butterfly_wing * multiplier
        b_val = butterfly_belly * multiplier
        result["Key Rate (2Y)"] = f"{'+' if w_val >= 0 else ''}{w_val:.0f} bp"
        result["Key Rate (5Y)"] = f"{'+' if b_val >= 0 else ''}{b_val:.0f} bp"
        result["Key Rate (10Y)"] = f"{'+' if w_val >= 0 else ''}{w_val:.0f} bp"

    spread_bp = shocks.get("spread_shift_bp", 0)
    if spread_bp:
        val = spread_bp * multiplier
        result["OAS"] = f"{'+' if val >= 0 else ''}{val:.0f} bp"

    vol_pct = shocks.get("vol_shift_pct", 0)
    if vol_pct:
        val = vol_pct * multiplier
        result["Volatility"] = f"{'+' if val >= 0 else ''}{val:.1f}%"

    return result


def stress_test_swap_portfolio(
    positions: list[dict],
    scenarios: list[dict] | None = None,
    multiplier: float = 1.0,
) -> list[dict]:
    """
    Run stress tests on a swap portfolio.

    Args:
        positions: List of swap position dicts, each with keys matching
                   calculate_swap_valuation params (notional, tenor, fixed_rate,
                   floating_rate, spread, coupons_per_year, discount_rate,
                   volatility, swap_type).
        scenarios: Stress scenarios to run. Uses PREDEFINED_SCENARIOS if None.
        multiplier: Severity multiplier (default 1.0).

    Returns:
        List of scenario result dicts matching frontend shape.
    """
    if not positions:
        raise ValueError("At least one swap position is required")

    if scenarios is None:
        scenarios = PREDEFINED_SCENARIOS

    results: list[dict] = []

    for scenario in scenarios:
        shocks = scenario.get("shocks", {})

        # Aggregate P&L across all positions
        total_pnl = 0.0
        total_dv01_change = 0.0
        total_spread_dv01 = 0.0
        position_impact: dict[str, float] = {}
        total_greeks = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}
        total_krd: dict[str, float] = {"2Y": 0.0, "5Y": 0.0, "10Y": 0.0, "30Y": 0.0}

        for pos in positions:
            pos_label = f"{pos.get('swap_type', 'IRS').upper()} {pos.get('tenor', 0)}Y"

            pos_pnl = 0.0

            # Curve shock
            curve_bp = shocks.get("curve_shift_bp", 0)
            twist_short = shocks.get("twist_short_bp", 0)
            twist_long = shocks.get("twist_long_bp", 0)
            butterfly_wing = shocks.get("butterfly_wing_bp", 0)
            butterfly_belly = shocks.get("butterfly_belly_bp", 0)

            # Determine effective curve shift for this position's tenor
            effective_curve_bp = curve_bp
            if twist_short or twist_long:
                # Linear interpolation based on tenor
                tenor = pos.get("tenor", 5)
                if tenor <= 2:
                    effective_curve_bp = twist_short
                elif tenor >= 10:
                    effective_curve_bp = twist_long
                else:
                    t = (tenor - 2) / 8.0
                    effective_curve_bp = twist_short * (1 - t) + twist_long * t

            if butterfly_wing or butterfly_belly:
                tenor = pos.get("tenor", 5)
                effective_curve_bp = butterfly_wing if tenor <= 2 or tenor >= 10 else butterfly_belly

            if effective_curve_bp:
                curve_result = apply_curve_shock(pos, effective_curve_bp, multiplier)
                pos_pnl += curve_result["pnlImpact"]

            # Spread shock
            spread_bp = shocks.get("spread_shift_bp", 0)
            if spread_bp:
                spread_result = apply_spread_shock(pos, spread_bp, multiplier)
                pos_pnl += spread_result["pnlImpact"]
                total_spread_dv01 += abs(spread_result["pnlImpact"]) / max(abs(spread_bp * multiplier), 1)

            # Vol shock
            vol_pct = shocks.get("vol_shift_pct", 0)
            if vol_pct:
                vol_result = apply_vol_shock(pos, vol_pct, multiplier)
                pos_pnl += vol_result["pnlImpact"]

            total_pnl += pos_pnl
            position_impact[pos_label] = float(pos_pnl)

            # Greeks for this position
            greeks = compute_swap_greeks(pos)
            for key in total_greeks:
                total_greeks[key] += greeks[key]

            # DV01 change estimate (delta * curve shift)
            if effective_curve_bp:
                total_dv01_change += greeks["delta"] * (effective_curve_bp * multiplier / 100.0)

            # Key rate durations
            krd = compute_key_rate_durations(pos, multiplier)
            for k in total_krd:
                total_krd[k] += krd.get(k, 0.0)

        # Build market shocks description
        market_shocks = _build_market_shocks(scenario, multiplier)

        results.append({
            "id": scenario["id"],
            "name": scenario["name"],
            "description": scenario["description"],
            "shockType": scenario["shockType"],
            "severity": scenario["severity"],
            "probability": scenario["probability"],
            "duration": scenario["duration"],
            "pnlImpact": float(total_pnl),
            "dv01Change": float(total_dv01_change),
            "spreadDv01": float(total_spread_dv01),
            "delta": float(total_greeks["delta"]),
            "gamma": float(total_greeks["gamma"]),
            "vega": float(total_greeks["vega"]),
            "theta": float(total_greeks["theta"]),
            "keyRateDurations": {k: float(v) for k, v in total_krd.items()},
            "marketShocks": market_shocks,
            "positionImpact": position_impact,
        })

    return results


def get_predefined_scenarios() -> list[dict]:
    """Return the list of predefined stress scenarios."""
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "shockType": s["shockType"],
            "severity": s["severity"],
            "probability": s["probability"],
            "duration": s["duration"],
            "shocks": s["shocks"],
        }
        for s in PREDEFINED_SCENARIOS
    ]
