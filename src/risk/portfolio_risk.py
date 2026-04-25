"""Portfolio-level risk checks: drawdown circuit breakers, sector caps, cash floor."""
from __future__ import annotations


def calculate_drawdown_from_peak(current_value: float, peak_value: float) -> float:
    if peak_value <= 0:
        return 0.0
    return 100.0 * (peak_value - current_value) / peak_value


def circuit_breaker_state(
    drawdown_pct: float,
    half_size_threshold: float = 10.0,
    pause_threshold: float = 15.0,
    stop_threshold: float = 20.0,
) -> str:
    if drawdown_pct >= stop_threshold:
        return "stop"
    if drawdown_pct >= pause_threshold:
        return "pause"
    if drawdown_pct >= half_size_threshold:
        return "half_size"
    return "normal"


def sector_exposure(
    positions: list[dict],
    portfolio_value: float,
    ticker_to_sector: dict[str, str],
) -> dict[str, float]:
    out: dict[str, float] = {}
    if portfolio_value <= 0:
        return out
    for p in positions:
        sector = ticker_to_sector.get(p["ticker"], "UNKNOWN")
        notional = p.get("market_value", p["shares"] * p.get("current_price", 0.0))
        out[sector] = out.get(sector, 0.0) + 100.0 * notional / portfolio_value
    return {k: round(v, 2) for k, v in out.items()}


def check_position_limits(
    portfolio: dict,
    new_trade: dict,
    ticker_to_sector: dict[str, str],
    max_position_pct: float = 10.0,
    max_sector_pct: float = 30.0,
    min_cash_pct: float = 20.0,
) -> tuple[bool, str]:
    pv = portfolio["account"]["portfolio_value"]
    cash = portfolio["account"]["cash"]
    notional = new_trade["shares"] * new_trade["entry_price"]

    if pv <= 0:
        return False, "portfolio value is zero"

    pos_pct = 100.0 * notional / pv
    if pos_pct > max_position_pct:
        return False, f"position {pos_pct:.1f}% > {max_position_pct}% cap"

    new_cash = cash - notional
    new_cash_pct = 100.0 * new_cash / pv
    if new_cash_pct < min_cash_pct:
        return False, f"cash would drop to {new_cash_pct:.1f}% < {min_cash_pct}% floor"

    sector = ticker_to_sector.get(new_trade["ticker"], "UNKNOWN")
    exposure = sector_exposure(portfolio.get("positions", []), pv, ticker_to_sector)
    new_sector_pct = exposure.get(sector, 0.0) + pos_pct
    if new_sector_pct > max_sector_pct:
        return (
            False,
            f"sector {sector} would be {new_sector_pct:.1f}% > {max_sector_pct}% cap",
        )

    return True, "ok"
