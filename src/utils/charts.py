"""Generate the daily portfolio-vs-SPY chart for the morning Telegram heartbeat.

Reads performance/daily.json and plots cumulative return % from inception for
both the portfolio and SPY. Returns None if there are fewer than 2 data points
(can't draw a meaningful line on day zero).
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from .state_manager import PERFORMANCE_DIR, load_performance

log = logging.getLogger(__name__)

CHARTS_DIR = PERFORMANCE_DIR / "charts"


def generate_alpha_chart(out_path: str | Path | None = None) -> Path | None:
    history = load_performance("daily")
    if not isinstance(history, list) or len(history) < 2:
        log.info(
            "chart: %d data points, need >=2 — skipping",
            len(history) if isinstance(history, list) else 0,
        )
        return None

    # Lazy import — matplotlib is heavy and only needed here.
    import matplotlib

    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter

    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in history]
    portfolio = [float(row.get("cumulative_return_pct", 0.0)) for row in history]
    spy = [float(row.get("spy_cumulative_return_pct", 0.0)) for row in history]
    last = history[-1]
    alpha = float(last.get("cumulative_alpha_pct", 0.0))
    drawdown = float(last.get("drawdown_pct", 0.0))
    pv = float(last.get("portfolio_value", 0.0))

    if out_path is None:
        CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = CHARTS_DIR / f"{last['date']}.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=140)
    ax.plot(dates, portfolio, label="Portfolio", linewidth=2.2, color="#1f77b4")
    ax.plot(dates, spy, label="SPY (benchmark)", linewidth=2.0, color="#ff7f0e", linestyle="--")
    ax.axhline(0.0, color="#888", linewidth=0.8, alpha=0.6)
    ax.fill_between(
        dates,
        portfolio,
        spy,
        where=[p >= s for p, s in zip(portfolio, spy)],
        interpolate=True,
        alpha=0.12,
        color="#2ca02c",
        label="Alpha (positive)",
    )
    ax.fill_between(
        dates,
        portfolio,
        spy,
        where=[p < s for p, s in zip(portfolio, spy)],
        interpolate=True,
        alpha=0.12,
        color="#d62728",
        label="Alpha (negative)",
    )

    sign = "+" if alpha >= 0 else ""
    ax.set_title(
        f"Portfolio vs SPY — cumulative return since inception\n"
        f"Alpha {sign}{alpha:.2f}% · Drawdown {drawdown:.2f}% · "
        f"Portfolio ${pv:,.0f}",
        fontsize=12,
    )
    ax.set_ylabel("Cumulative return (%)")
    ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=9)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    return out_path
