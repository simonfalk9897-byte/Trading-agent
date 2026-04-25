"""Mean reversion signals: RSI(2), IBS, screen and exit checks."""
from __future__ import annotations

from .momentum import calculate_rsi, calculate_sma


def calculate_rsi2(prices) -> float:
    return calculate_rsi(prices, period=2)


def calculate_ibs(high: float, low: float, close: float) -> float:
    rng = high - low
    if rng <= 0:
        return float("nan")
    return (close - low) / rng


def screen_mean_reversion(bars) -> bool:
    """Bars: pandas DataFrame with high/low/close columns and >=200 rows."""
    if bars is None or len(bars) < 201:
        return False
    last = bars.iloc[-1]
    rsi2 = calculate_rsi2(bars["close"])
    if rsi2 != rsi2 or rsi2 >= 10.0:
        return False
    ibs = calculate_ibs(float(last["high"]), float(last["low"]), float(last["close"]))
    if ibs != ibs or ibs >= 0.3:
        return False
    sma200 = calculate_sma(bars["close"], 200)
    return float(last["close"]) > sma200


def mean_reversion_exit_signal(bars) -> bool:
    rsi2 = calculate_rsi2(bars["close"])
    return rsi2 == rsi2 and rsi2 > 60.0
