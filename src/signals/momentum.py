"""Momentum signals: RSI, SMA, composite momentum score, sector ranking."""
from __future__ import annotations

from typing import Mapping


def calculate_rsi(prices, period: int = 14) -> float:
    """Wilder's RSI on a pandas Series of closes. Returns the most recent value."""
    import pandas as pd

    s = pd.Series(prices).astype(float).dropna()
    if len(s) <= period:
        return float("nan")
    delta = s.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


def calculate_sma(prices, period: int) -> float:
    import pandas as pd

    s = pd.Series(prices).astype(float).dropna()
    if len(s) < period:
        return float("nan")
    return float(s.tail(period).mean())


def momentum_score(
    prices,
    weights: Mapping[str, float] | None = None,
) -> float:
    """Weighted composite of 1m / 3m / 6m total return (in pct).

    Trading-day windows: 21 / 63 / 126.
    """
    import pandas as pd

    s = pd.Series(prices).astype(float).dropna()
    if len(s) < 127:
        return float("nan")
    w = dict(weights or {"1_month": 0.33, "3_month": 0.33, "6_month": 0.34})
    last = s.iloc[-1]
    r1 = 100.0 * (last / s.iloc[-22] - 1.0)
    r3 = 100.0 * (last / s.iloc[-64] - 1.0)
    r6 = 100.0 * (last / s.iloc[-127] - 1.0)
    return float(
        w["1_month"] * r1 + w["3_month"] * r3 + w["6_month"] * r6
    )


def rank_sectors(
    price_data: Mapping[str, "object"],
    weights: Mapping[str, float] | None = None,
    sector_names: Mapping[str, str] | None = None,
) -> list[dict]:
    rows = []
    for ticker, df in price_data.items():
        closes = df["close"] if hasattr(df, "columns") else df
        score = momentum_score(closes, weights)
        sma50 = calculate_sma(closes, 50)
        last = float(closes.iloc[-1]) if len(closes) else float("nan")
        rows.append(
            {
                "sector": ticker,
                "name": (sector_names or {}).get(ticker, ticker),
                "score": None if score != score else round(score, 3),
                "above_50ma": bool(last > sma50) if sma50 == sma50 else False,
                "last_price": round(last, 2) if last == last else None,
            }
        )
    rows.sort(
        key=lambda r: (r["score"] if r["score"] is not None else float("-inf")),
        reverse=True,
    )
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows


def screen_momentum_candidate(prices, volumes) -> bool:
    """RSI(14) in [40, 70] AND latest volume > 20-day average volume."""
    import pandas as pd

    rsi = calculate_rsi(prices, 14)
    if rsi != rsi:
        return False
    if not (40.0 <= rsi <= 70.0):
        return False
    v = pd.Series(volumes).astype(float).dropna()
    if len(v) < 21:
        return False
    avg20 = float(v.tail(21).iloc[:-1].mean())
    return float(v.iloc[-1]) > avg20
