"""Active-client session.

Writes are only evaluated against the client explicitly selected with
`adsgm use <client>`. The selection expires so a stale client from yesterday
cannot silently receive today's changes.
"""

import json
import time
from typing import Dict, Optional

from . import paths, profiles

SESSION_TTL_SECONDS = 12 * 3600


def set_active(slug: str) -> Dict:
    profile = profiles.load(slug)
    paths.ensure_dirs()
    data = {"client": profile.slug, "selected_at": time.time()}
    paths.session_file().write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def clear() -> None:
    f = paths.session_file()
    if f.exists():
        f.unlink()


def get_active(now: Optional[float] = None) -> Optional[str]:
    f = paths.session_file()
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    now = time.time() if now is None else now
    if now - float(data.get("selected_at", 0)) > SESSION_TTL_SECONDS:
        return None
    return data.get("client")


# ---- unattended switch -------------------------------------------------------
# Scheduled runs set ADS_GODMODE_UNATTENDED=1. Schedulers that cannot set
# environment variables (e.g. the Claude desktop app's scheduled tasks) run
# `adsgm unattended on` first instead; the switch expires on its own.

def _unattended_file():
    return paths.state_dir() / "unattended.json"


def set_unattended(hours: float = 3.0) -> Dict:
    paths.ensure_dirs()
    data = {"until": time.time() + hours * 3600}
    _unattended_file().write_text(json.dumps(data), encoding="utf-8")
    return data


def clear_unattended() -> None:
    f = _unattended_file()
    if f.exists():
        f.unlink()


def unattended(now: Optional[float] = None) -> bool:
    import os
    if os.environ.get("ADS_GODMODE_UNATTENDED") == "1":
        return True
    f = _unattended_file()
    if not f.exists():
        return False
    try:
        until = float(json.loads(f.read_text(encoding="utf-8")).get("until", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        return True  # unreadable switch: stay on the safe side
    return (time.time() if now is None else now) < until

