"""Filesystem locations for private, per-user data.

Client profiles, session state, change tickets and the audit log live OUTSIDE
the repository, under ADS_GODMODE_HOME (default ~/.ads-godmode). Nothing in
this directory should ever be committed.
"""

import os
from pathlib import Path


def home() -> Path:
    root = os.environ.get("ADS_GODMODE_HOME")
    return Path(root).expanduser() if root else Path.home() / ".ads-godmode"


def clients_dir() -> Path:
    return home() / "clients"


def state_dir() -> Path:
    return home() / "state"


def tickets_dir() -> Path:
    return state_dir() / "tickets"


def session_file() -> Path:
    return state_dir() / "session.json"


def change_history_file() -> Path:
    return state_dir() / "change-history.jsonl"


def audit_log_file() -> Path:
    custom = os.environ.get("ADS_GODMODE_AUDIT_LOG")
    return Path(custom).expanduser() if custom else home() / "audit.jsonl"


def ensure_dirs() -> None:
    for d in (clients_dir(), state_dir(), tickets_dir()):
        d.mkdir(parents=True, exist_ok=True)
