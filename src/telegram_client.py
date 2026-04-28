"""Telegram notifier. Errors are swallowed — Telegram must never block a run."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import requests

log = logging.getLogger(__name__)


def _creds() -> tuple[str | None, str | None]:
    return os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")


def send_message(text: str, parse_mode: str = "Markdown") -> bool:
    token, chat_id = _creds()
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


def send_photo(png_path: str | Path, caption: str = "") -> bool:
    """Send an image to the configured chat. Caption is plain text (Telegram
    limits photo captions to 1024 chars)."""
    token, chat_id = _creds()
    if not token or not chat_id:
        log.warning("telegram: missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False
    path = Path(png_path)
    if not path.exists():
        log.error("telegram: photo path does not exist: %s", path)
        return False
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        with open(path, "rb") as f:
            resp = requests.post(
                url,
                data={"chat_id": chat_id, "caption": caption[:1024]},
                files={"photo": (path.name, f, "image/png")},
                timeout=30,
            )
        if resp.status_code != 200:
            log.error("telegram photo failed (%s): %s", resp.status_code, resp.text)
            return False
        return True
    except requests.RequestException as e:
        log.error("telegram photo exception: %s", e)
        return False
