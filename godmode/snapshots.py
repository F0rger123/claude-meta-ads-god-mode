"""Per-client performance snapshots - the data layer for sweeps and learning.

Claude collects numbers with the ad-platform MCP tools (read-only) and saves
one snapshot per client per run. Python never calls the ad platforms itself.

Schema (only `client`, `window` and one platform are required):

    {
      "client": "example-remodeling",
      "captured_at": "2026-10-25",
      "window": {"start": "2026-10-18", "end": "2026-10-24", "days": 7},
      "platforms": {
        "meta": {
          "account_id": "act_...",
          "spend": 412.5, "results": 6, "value": 0, "impressions": 52000, "clicks": 610,
          "month_to_date_spend": 1350.0, "tracking_ok": true,
          "previous": {"spend": 398.0, "results": 7},
          "entities": [
            {"id": "1202...", "name": "...", "level": "adset", "status": "ACTIVE",
             "learning": "active|learning|limited", "spend": 210.0, "results": 4,
             "ctr": 1.1, "ctr_prev": 1.4, "frequency": 3.4, "cpm": 9.5,
             "daily_budget": 30, "spend_today": 18.2, "hours_elapsed": 14,
             "spend_history": [29, 31, 30, 28, 30, 31, 29], "age_days": 41,
             "tags": ["ugc", "free-consult"]}
          ]
        },
        "google": {"account_id": "1234567890", "...": "same fields",
                   "search_term_waste": 84.0, "lost_is_budget": 22.5}
      },
      "crm": {"qualified_leads": 3, "revenue": 0}
    }
"""

import json
import re
from datetime import date
from typing import Dict, List, Optional

from . import paths, profiles

PLATFORM_KEYS = ("meta", "google")


class SnapshotError(Exception):
    pass


def snapshots_dir():
    return paths.home() / "snapshots"


def validate(snap: Dict, profile: profiles.Profile) -> List[str]:
    """Problems with a snapshot. Account ids must belong to the snapshot's client."""
    errors = []
    if snap.get("client") != profile.slug:
        errors.append(f"snapshot client {snap.get('client')!r} != profile {profile.slug!r}")
    win = snap.get("window") or {}
    if not isinstance(win.get("days"), (int, float)) or win.get("days", 0) <= 0:
        errors.append("window.days must be a positive number")
    plats = snap.get("platforms") or {}
    if not plats:
        errors.append("at least one platform is required")
    for name, p in plats.items():
        if name not in PLATFORM_KEYS:
            errors.append(f"unknown platform {name!r}")
            continue
        acc = p.get("account_id")
        if not acc or not profile.owns(name, acc):
            owners = profiles.owner_of(name, acc) if acc else []
            errors.append(f"{name}: account {acc!r} is not {profile.slug}'s"
                          + (f" (belongs to {', '.join(owners)})" if owners else ""))
        for k in ("spend", "results"):
            if not isinstance(p.get(k, 0), (int, float)) or p.get(k, 0) < 0:
                errors.append(f"{name}.{k} must be a non-negative number")
    return errors


def save(snap: Dict) -> str:
    profile = profiles.load(snap.get("client", ""))
    errors = validate(snap, profile)
    if errors:
        raise SnapshotError("; ".join(errors))
    day = snap.get("captured_at") or date.today().isoformat()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
        raise SnapshotError("captured_at must be YYYY-MM-DD")
    snap["captured_at"] = day
    d = snapshots_dir() / profile.slug
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{day}.json"
    path.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    return str(path)


def history(client: str) -> List[Dict]:
    d = snapshots_dir() / client
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return out


def latest(client: str) -> Optional[Dict]:
    h = history(client)
    return h[-1] if h else None


def entity_metric(snap: Dict, platform: str, entity_id: str, metric: str) -> Optional[Dict]:
    """Return {"value": x, "n": sample} for one entity metric, or None if absent."""
    p = (snap.get("platforms") or {}).get(platform) or {}
    rows = [e for e in p.get("entities", []) if str(e.get("id")) == str(entity_id)]
    if not rows and str(entity_id) in ("", "account", str(p.get("account_id"))):
        rows = [p]
    if not rows:
        return None
    return metric_from(rows[0], metric)


def metric_from(row: Dict, metric: str) -> Optional[Dict]:
    spend, results = float(row.get("spend") or 0), float(row.get("results") or 0)
    n = int(results)
    m = metric.lower()
    if m in ("cpl", "cpa", "cost_per_result"):
        return None if results <= 0 else {"value": spend / results, "n": n}
    if m == "roas":
        return None if spend <= 0 else {"value": float(row.get("value") or 0) / spend, "n": n}
    if m in ("results", "leads", "conversions"):
        return {"value": results, "n": n}
    if m in row and isinstance(row[m], (int, float)):
        return {"value": float(row[m]), "n": int(row.get("clicks") or row.get("impressions") or n)}
    return None
