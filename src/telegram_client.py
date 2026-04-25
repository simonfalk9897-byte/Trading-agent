"""Telegram notifier. Errors are swallowed — Telegram must never block a run."""
from __future__ import annotations

import logging
import os

import requests

log = logging.getLogger(__name__)


def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        log.warning("telegram: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
            timeout=10,
        )
        if resp.status_code != 200:
            log.error("telegram send failed (%s): %s", resp.status_code, resp.text)
            return False
        return True
    except requests.RequestException as e:
        log.error("telegram exception: %s", e)
        return False
