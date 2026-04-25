"""Git commit and push helpers. Never raise — git failures must not block trading."""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACKED_DIRS = ["state", "journal", "research", "performance"]

log = logging.getLogger(__name__)


def _run(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        args, cwd=REPO_ROOT, capture_output=True, text=True
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def commit_and_push(run_type: str, date_str: str) -> bool:
    for d in TRACKED_DIRS:
        _run(["git", "add", d])

    code, _ = _run(["git", "diff", "--cached", "--quiet"])
    if code == 0:
        log.info("git: nothing to commit")
        return True

    msg = f"agent run: {run_type} {date_str}"
    code, out = _run(["git", "commit", "-m", msg])
    if code != 0:
        log.error("git commit failed: %s", out)
        return False

    for attempt in (1, 2):
        code, out = _run(["git", "push", "origin", "HEAD"])
        if code == 0:
            return True
        log.warning("git push attempt %d failed: %s", attempt, out)
    return False
