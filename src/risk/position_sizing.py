"""Position sizing: turn risk-% and stop distance into a share count."""
from __future__ import annotations

import math


def calculate_position_size(
    portfolio_value: float,
    risk_pct: float,
    entry_price: float,
    stop_price: float,
    max_position_pct: float = 10.0,
) -> dict:
    if entry_price <= 0 or stop_price <= 0:
        return {"shares": 0, "notional": 0.0, "risk_amount": 0.0, "position_pct": 0.0}
    stop_dist = abs(entry_price - stop_price)
    if stop_dist <= 0:
        return {"shares": 0, "notional": 0.0, "risk_amount": 0.0, "position_pct": 0.0}

    risk_amount = portfolio_value * (risk_pct / 100.0)
    risk_shares = math.floor(risk_amount / stop_dist)
    cap_notional = portfolio_value * (max_position_pct / 100.0)
    cap_shares = math.floor(cap_notional / entry_price)
    shares = max(0, min(risk_shares, cap_shares))
    notional = shares * entry_price
    position_pct = 100.0 * notional / portfolio_value if portfolio_value else 0.0
    return {
        "shares": shares,
        "notional": round(notional, 2),
        "risk_amount": round(shares * stop_dist, 2),
        "position_pct": round(position_pct, 2),
    }


def calculate_stop_price(entry_price: float, strategy: str, config: dict | None = None) -> float:
    config = config or {}
    if strategy == "momentum":
        pct = config.get("momentum", {}).get("trailing_stop_pct", 8.0)
    elif strategy == "mean_reversion":
        pct = config.get("mean_reversion", {}).get("hard_stop_pct", 4.0)
    else:
        pct = 5.0
    return round(entry_price * (1 - pct / 100.0), 2)
