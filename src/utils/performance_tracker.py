"""Track daily P&L vs SPY, compute alpha, drawdown, Sharpe, win rate, profit factor."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Iterable

from .state_manager import load_performance, save_performance


def record_daily(
    date_str: str,
    portfolio_value: float,
    cash: float,
    spy_close: float,
    vix_close: float,
    positions_count: int,
    trades_today: int,
    starting_capital: float,
) -> dict:
    history: list = load_performance("daily")  # type: ignore[assignment]
    if not isinstance(history, list):
        history = []

    prev = history[-1] if history else None
    prev_pv = prev["portfolio_value"] if prev else starting_capital
    prev_spy = prev["spy_close"] if prev else spy_close
    prev_peak = prev["peak_value"] if prev else starting_capital
    prev_cum = prev["cumulative_return_pct"] if prev else 0.0
    prev_spy_cum = prev["spy_cumulative_return_pct"] if prev else 0.0
    spy_baseline = prev["spy_baseline"] if prev and "spy_baseline" in prev else spy_close

    daily_ret = _pct_change(prev_pv, portfolio_value)
    spy_daily_ret = _pct_change(prev_spy, spy_close)
    cum_ret = _pct_change(starting_capital, portfolio_value)
    spy_cum_ret = _pct_change(spy_baseline, spy_close)
    peak = max(prev_peak, portfolio_value)
    drawdown = _pct_change(peak, portfolio_value) if peak > 0 else 0.0

    invested_pct = (
        100.0 * (portfolio_value - cash) / portfolio_value if portfolio_value else 0.0
    )
    cash_pct = 100.0 * cash / portfolio_value if portfolio_value else 0.0

    entry = {
        "date": date_str,
        "portfolio_value": round(portfolio_value, 2),
        "cash": round(cash, 2),
        "cash_pct": round(cash_pct, 2),
        "invested_pct": round(invested_pct, 2),
        "daily_return_pct": round(daily_ret, 4),
        "spy_close": round(spy_close, 2),
        "spy_daily_return_pct": round(spy_daily_ret, 4),
        "daily_alpha_pct": round(daily_ret - spy_daily_ret, 4),
        "cumulative_return_pct": round(cum_ret, 4),
        "spy_cumulative_return_pct": round(spy_cum_ret, 4),
        "cumulative_alpha_pct": round(cum_ret - spy_cum_ret, 4),
        "peak_value": round(peak, 2),
        "drawdown_pct": round(drawdown, 4),
        "vix_close": round(vix_close, 2),
        "positions_count": positions_count,
        "trades_today": trades_today,
        "spy_baseline": spy_baseline,
        "recorded_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
    history.append(entry)
    save_performance("daily", history)
    return entry


def calculate_sharpe(returns: Iterable[float], periods_per_year: int = 252) -> float:
    rs = [r for r in returns]
    if len(rs) < 2:
        return 0.0
    mean = sum(rs) / len(rs)
    var = sum((r - mean) ** 2 for r in rs) / (len(rs) - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean / sd) * math.sqrt(periods_per_year)


def calculate_win_rate(trades: list[dict]) -> float:
    closed = [t for t in trades if "pnl" in t]
    if not closed:
        return 0.0
    wins = sum(1 for t in closed if t["pnl"] > 0)
    return 100.0 * wins / len(closed)


def calculate_profit_factor(trades: list[dict]) -> float:
    gains = sum(t["pnl"] for t in trades if t.get("pnl", 0) > 0)
    losses = -sum(t["pnl"] for t in trades if t.get("pnl", 0) < 0)
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return gains / losses


def _pct_change(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return 100.0 * (new - old) / old
