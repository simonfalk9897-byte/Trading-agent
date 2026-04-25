"""Market regime detection from VIX and SPY trend filters."""
from __future__ import annotations

import math


def regime(
    vix: float,
    spy_price: float,
    spy_50ma: float,
    spy_200ma: float,
    vix_threshold: float = 30.0,
) -> dict:
    vix_known = isinstance(vix, (int, float)) and not math.isnan(vix)
    above_50 = spy_price > spy_50ma if not math.isnan(spy_50ma) else False
    above_200 = spy_price > spy_200ma if not math.isnan(spy_200ma) else False
    vix_high = vix_known and vix > vix_threshold

    if not above_200 and not above_50:
        mode = "defensive"
        max_invested, cash_floor = 30.0, 70.0
    elif above_200 and not above_50:
        mode = "cautious"
        max_invested, cash_floor = 60.0, 40.0
    else:
        mode = "full_offense"
        max_invested, cash_floor = 80.0, 20.0

    size_mult = 0.5 if vix_high else 1.0
    if mode == "defensive":
        size_mult = min(size_mult, 0.5)

    return {
        "mode": mode,
        "vix": vix if vix_known else None,
        "vix_above_threshold": vix_high,
        "spy_above_50ma": above_50,
        "spy_above_200ma": above_200,
        "position_size_multiplier": size_mult,
        "max_invested_pct": max_invested,
        "cash_floor_pct": cash_floor,
    }
