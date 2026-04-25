"""Read/write JSON state files and append to journal entries."""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / "state"
JOURNAL_DIR = REPO_ROOT / "journal"
RESEARCH_DIR = REPO_ROOT / "research"
PERFORMANCE_DIR = REPO_ROOT / "performance"


def load(name: str) -> dict | list:
    path = STATE_DIR / f"{name}.json"
    with open(path, "r") as f:
        return json.load(f)


def save(name: str, data: dict | list) -> None:
    path = STATE_DIR / f"{name}.json"
    _atomic_write_json(path, data)


def load_performance(name: str) -> list | dict:
    path = PERFORMANCE_DIR / f"{name}.json"
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_performance(name: str, data: list | dict) -> None:
    path = PERFORMANCE_DIR / f"{name}.json"
    _atomic_write_json(path, data)


def _atomic_write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def append_journal(date_str: str, markdown_block: str) -> Path:
    JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    path = JOURNAL_DIR / f"{date_str}.md"
    if not path.exists():
        path.write_text(f"# Journal — {date_str}\n\n")
    with open(path, "a") as f:
        if not markdown_block.startswith("\n"):
            f.write("\n")
        f.write(markdown_block.rstrip() + "\n")
    return path


def append_research(date_str: str, topic: str, summary: str) -> Path:
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    path = RESEARCH_DIR / f"{date_str}.md"
    if not path.exists():
        path.write_text(f"# Research — {date_str}\n\n")
    with open(path, "a") as f:
        f.write(f"\n## {topic}\n\n{summary.rstrip()}\n")
    return path
