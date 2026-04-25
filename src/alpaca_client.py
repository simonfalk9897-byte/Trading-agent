"""Thin wrapper over alpaca-py. LIVE endpoint. Loads creds from env."""
from __future__ import annotations

import logging
import os
import time
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from typing import Iterable

log = logging.getLogger(__name__)


def _retry(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:  # noqa: BLE001
        log.warning("alpaca retry after error: %s", e)
        time.sleep(0.5)
        return fn(*args, **kwargs)


@lru_cache(maxsize=1)
def _trading_client():
    from alpaca.trading.client import TradingClient

    key = os.environ["ALPACA_KEY"]
    secret = os.environ["ALPACA_SECRET"]
    return TradingClient(key, secret, paper=False)


@lru_cache(maxsize=1)
def _stock_data_client():
    from alpaca.data.historical import StockHistoricalDataClient

    return StockHistoricalDataClient(
        os.environ["ALPACA_KEY"], os.environ["ALPACA_SECRET"]
    )


def is_market_open_today() -> bool:
    from alpaca.trading.requests import GetCalendarRequest

    today = date.today()
    cal = _retry(
        _trading_client().get_calendar,
        GetCalendarRequest(start=today, end=today),
    )
    return bool(cal)


def market_is_open_now() -> bool:
    return bool(_retry(_trading_client().get_clock).is_open)


def get_account_info() -> dict:
    a = _retry(_trading_client().get_account)
    return {
        "cash": float(a.cash),
        "equity": float(a.equity),
        "portfolio_value": float(a.portfolio_value),
        "buying_power": float(a.buying_power),
        "last_equity": float(a.last_equity),
        "status": str(a.status),
    }


def get_positions() -> list[dict]:
    raw = _retry(_trading_client().get_all_positions)
    out = []
    for p in raw:
        out.append(
            {
                "ticker": p.symbol,
                "shares": int(float(p.qty)),
                "avg_entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "market_value": float(p.market_value),
                "unrealized_pnl": float(p.unrealized_pl),
                "unrealized_pnl_pct": float(p.unrealized_plpc) * 100.0,
            }
        )
    return out


def get_open_orders() -> list[dict]:
    return get_all_orders(status="open")


def get_all_orders(status: str = "all", after: datetime | None = None) -> list[dict]:
    from alpaca.trading.enums import QueryOrderStatus
    from alpaca.trading.requests import GetOrdersRequest

    status_map = {
        "all": QueryOrderStatus.ALL,
        "open": QueryOrderStatus.OPEN,
        "closed": QueryOrderStatus.CLOSED,
    }
    req = GetOrdersRequest(
        status=status_map.get(status, QueryOrderStatus.ALL),
        after=after,
        limit=500,
    )
    raw = _retry(_trading_client().get_orders, filter=req)
    out = []
    for o in raw:
        out.append(
            {
                "order_id": str(o.id),
                "ticker": o.symbol,
                "side": str(o.side).split(".")[-1].lower(),
                "type": str(o.order_type).split(".")[-1].lower(),
                "qty": int(float(o.qty)) if o.qty else 0,
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "stop_price": float(o.stop_price) if o.stop_price else None,
                "filled_qty": int(float(o.filled_qty or 0)),
                "filled_avg_price": float(o.filled_avg_price)
                if o.filled_avg_price
                else None,
                "status": str(o.status).split(".")[-1].lower(),
                "submitted_at": o.submitted_at.isoformat() if o.submitted_at else None,
            }
        )
    return out


def cancel_order(order_id: str) -> None:
    _retry(_trading_client().cancel_order_by_id, order_id)


def cancel_unfilled_orders() -> int:
    n = 0
    for o in get_open_orders():
        cancel_order(o["order_id"])
        n += 1
    return n


def get_price_data(ticker: str, lookback_days: int = 250):
    """Return a pandas DataFrame of daily OHLCV bars indexed by date."""
    import pandas as pd
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    end = datetime.now(timezone.utc) - timedelta(minutes=15)
    start = end - timedelta(days=int(lookback_days * 1.6) + 7)
    req = StockBarsRequest(
        symbol_or_symbols=ticker,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
    )
    bars = _retry(_stock_data_client().get_stock_bars, req)
    df = bars.df
    if df is None or df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    if "symbol" in df.index.names:
        df = df.xs(ticker, level="symbol")
    df = df[["open", "high", "low", "close", "volume"]].tail(lookback_days)
    return df


def get_current_price(ticker: str) -> float:
    return get_current_prices([ticker])[ticker]


def get_current_prices(tickers: Iterable[str]) -> dict[str, float]:
    from alpaca.data.requests import StockLatestTradeRequest

    syms = list(tickers)
    req = StockLatestTradeRequest(symbol_or_symbols=syms)
    trades = _retry(_stock_data_client().get_stock_latest_trade, req)
    return {s: float(trades[s].price) for s in syms if s in trades}


def get_eod_prices(tickers: Iterable[str]) -> dict[str, float]:
    out = {}
    for t in tickers:
        df = get_price_data(t, lookback_days=5)
        if not df.empty:
            out[t] = float(df["close"].iloc[-1])
    return out


def get_vix() -> float:
    """VIX via Alpaca isn't available; use Cboe public feed.

    Falls back to NaN if unreachable. Caller should treat NaN as "unknown" and
    take the cautious branch of any regime check.
    """
    import requests

    try:
        r = requests.get(
            "https://cdn.cboe.com/api/global/delayed_quotes/quotes/_VIX.json",
            timeout=10,
        )
        r.raise_for_status()
        return float(r.json()["data"]["last"])
    except Exception as e:  # noqa: BLE001
        log.error("VIX fetch failed: %s", e)
        return float("nan")


def submit_limit_order(
    ticker: str,
    qty: int,
    side: str,
    limit_price: float,
    time_in_force: str = "day",
) -> dict:
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.trading.requests import LimitOrderRequest

    req = LimitOrderRequest(
        symbol=ticker,
        qty=qty,
        side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
        time_in_force=TimeInForce.DAY
        if time_in_force == "day"
        else TimeInForce.GTC,
        limit_price=round(limit_price, 2),
    )
    o = _retry(_trading_client().submit_order, order_data=req)
    return {"order_id": str(o.id), "status": str(o.status).split(".")[-1].lower()}


def submit_stop_loss_order(ticker: str, qty: int, stop_price: float) -> dict:
    from alpaca.trading.enums import OrderSide, TimeInForce
    from alpaca.trading.requests import StopOrderRequest

    req = StopOrderRequest(
        symbol=ticker,
        qty=qty,
        side=OrderSide.SELL,
        time_in_force=TimeInForce.GTC,
        stop_price=round(stop_price, 2),
    )
    o = _retry(_trading_client().submit_order, order_data=req)
    return {"order_id": str(o.id), "status": str(o.status).split(".")[-1].lower()}
