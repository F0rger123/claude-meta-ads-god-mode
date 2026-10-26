"""Change tickets: a verified plan for one write, created before the write.

`adsgm plan ...` checks client, platform, account and entity, computes the
budget math, evaluates policy, and stores a ticket. The PreToolUse hook only
lets an entity-level write through when an unexpired, unconsumed ticket covers
exactly that client, platform, action and entity.
"""

import json
import time
import uuid
from typing import Dict, List, Optional

from . import paths

TICKET_TTL_SECONDS = 30 * 60


def _path(ticket_id: str):
    return paths.tickets_dir() / f"{ticket_id}.json"


def create(client: str, platform: str, account_id: str, action: str, entity_ids: List[str],
           decision: Dict, summary: str, details: Optional[Dict] = None) -> Dict:
    paths.ensure_dirs()
    now = time.time()
    ticket = {
        "id": "tkt_" + uuid.uuid4().hex[:12],
        "client": client,
        "platform": platform,
        "account_id": account_id,
        "action": action,
        "entity_ids": [str(e) for e in entity_ids],
        "decision": decision,
        "summary": summary,
        "details": details or {},
        "created_at": now,
        "expires_at": now + TICKET_TTL_SECONDS,
        "consumed": False,
    }
    _path(ticket["id"]).write_text(json.dumps(ticket, indent=2), encoding="utf-8")
    return ticket


def get(ticket_id: str) -> Optional[Dict]:
    p = _path(ticket_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def list_open(client: Optional[str] = None, now: Optional[float] = None) -> List[Dict]:
    now = time.time() if now is None else now
    d = paths.tickets_dir()
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("tkt_*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if t.get("consumed") or t.get("expires_at", 0) < now:
            continue
        if client and t.get("client") != client:
            continue
        out.append(t)
    return out


def find_match(client: str, platform: str, action: str, entity_ids: List[str],
               account_ids: List[str], now: Optional[float] = None) -> Optional[Dict]:
    """Newest open ticket covering every entity (or account) in the call."""
    wanted = {str(e) for e in entity_ids}
    for t in reversed(list_open(client, now)):
        if t["platform"] != platform or t["action"] != action:
            continue
        if account_ids and any(a != t["account_id"] for a in account_ids):
            continue
        if wanted:
            remaining = set(t["entity_ids"]) - set(t.get("done_entities", []))
            if wanted.issubset(remaining):
                return t
        elif account_ids:
            return t
    return None


def consume(ticket_id: str, entity_ids: Optional[List[str]] = None) -> None:
    """Mark entities done. The ticket closes when every entity is done
    (or immediately when entity_ids is None)."""
    t = get(ticket_id)
    if not t or t.get("consumed"):
        return
    done = set(t.get("done_entities", []))
    done.update(str(e) for e in (entity_ids if entity_ids is not None else t["entity_ids"]))
    t["done_entities"] = sorted(done)
    if entity_ids is None or done.issuperset(t["entity_ids"]):
        t["consumed"] = True
        t["consumed_at"] = time.time()
    _path(ticket_id).write_text(json.dumps(t, indent=2), encoding="utf-8")
    record_change({**t, "entity_ids": [str(e) for e in (entity_ids or t["entity_ids"])]})


def record_change(ticket: Dict) -> None:
    rec = {"ts": time.time(), "client": ticket["client"], "platform": ticket["platform"],
           "action": ticket["action"], "entity_ids": ticket["entity_ids"], "ticket": ticket["id"]}
    f = paths.change_history_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def hours_since_last_change(client: str, platform: str, entity_id: str, now: Optional[float] = None) -> Optional[float]:
    f = paths.change_history_file()
    if not f.exists():
        return None
    now = time.time() if now is None else now
    last = None
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("client") == client and rec.get("platform") == platform and str(entity_id) in rec.get("entity_ids", []):
            last = max(last or 0, rec["ts"])
    return None if last is None else (now - last) / 3600


def count_changes(client: str, action: str, days: float = 7, now: Optional[float] = None) -> int:
    """How many changes of this action were made for a client in the last N days."""
    f = paths.change_history_file()
    if not f.exists():
        return 0
    now = time.time() if now is None else now
    seen = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("client") == client and rec.get("action") == action and now - rec.get("ts", 0) <= days * 86400:
            seen.add(rec.get("ticket"))
    return len(seen)

