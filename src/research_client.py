"""Research journaling stub. Claude performs web search itself; this just records notes."""
from __future__ import annotations

from .utils.state_manager import append_research


def record_research(date_str: str, topic: str, summary: str):
    return append_research(date_str, topic, summary)
