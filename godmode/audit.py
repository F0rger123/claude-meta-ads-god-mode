"""Append-only JSONL audit log with secret redaction."""

import json
import re
import time
from typing import Any, Dict

from . import paths

_SECRET_PATTERNS = [
    re.compile(r"EAA[A-Za-z0-9]{20,}"),                # Meta access tokens
    re.compile(r"ya29\.[A-Za-z0-9_\-]{20,}"),          # Google OAuth access tokens
    re.compile(r"1//[A-Za-z0-9_\-]{20,}"),             # Google refresh tokens
    re.compile(r"gh[opsu]_[A-Za-z0-9]{20,}"),          # GitHub tokens
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),             # generic API keys
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._\-]{16,}"),
]
_SECRET_KEYS = re.compile(r"(?i)(token|secret|password|api[_-]?key|authorization|refresh)")


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: ("[REDACTED]" if _SECRET_KEYS.search(str(k)) else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        out = value
        for pat in _SECRET_PATTERNS:
            out = pat.sub("[REDACTED]", out)
        return out
    return value


def log(event: str, **fields: Any) -> Dict:
    record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "event": event, **redact(fields)}
    path = paths.audit_log_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, default=str) + "\n")
    return record


def tail(n: int = 20):
    path = paths.audit_log_file()
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()[-n:]
    return [json.loads(l) for l in lines if l.strip()]
