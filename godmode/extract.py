"""Pull account ids, entity ids, status, budget and geo fields out of a tool input.

Connector schemas differ (official Meta MCP passes some params as JSON strings,
getmcpads uses camelCase, Google uses resource names), so this walks the whole
input recursively. It is deliberately greedy: an id it cannot attribute makes
the gate stricter, never looser.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, List, Optional

_ACT_RE = re.compile(r"\bact_(\d{5,20})\b")
_GOOGLE_RESOURCE_RE = re.compile(r"customers/(\d{10})(?:/(\w+)/(\d+)(?:~(\d+))?)?")
_ACCOUNT_KEYS = re.compile(r"^(ad_?account_?id|account_?id|adaccountid|customer_?id|login_customer_id)$", re.I)
_ENTITY_KEYS = re.compile(r"^(id|ids|entity_?ids?|object_?ids?|(campaign|ad_?set|ad_?group|ad|creative|asset_group|keyword|criterion)_?ids?)$", re.I)
_BUDGET_KEYS = re.compile(r"^(daily_?budget|lifetime_?budget|budget|amount|amount_?micros|budget_?amount)$", re.I)
_GEO_KEYS = re.compile(r"^(geo_?locations|countries|regions|cities|zips|location_?ids|custom_locations|proximity|radius)$", re.I)


@dataclass
class Extracted:
    account_ids: List[str] = field(default_factory=list)
    entity_ids: List[str] = field(default_factory=list)
    statuses: List[str] = field(default_factory=list)
    budgets: List[float] = field(default_factory=list)
    budget_keys: List[str] = field(default_factory=list)
    touches_geo: bool = False
    touches_bid: bool = False
    touches_tracking: bool = False

    @property
    def status(self) -> Optional[str]:
        return self.statuses[-1] if self.statuses else None


def _maybe_json(v: Any) -> Any:
    if isinstance(v, str) and v[:1] in "{[":
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v


def _add(lst: List[str], v: str) -> None:
    if v not in lst:
        lst.append(v)


def _walk(obj: Any, out: Extracted, key: str = "") -> None:
    obj = _maybe_json(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk(v, out, str(k))
        return
    if isinstance(obj, list):
        for v in obj:
            _walk(v, out, key)
        return
    if obj is None or isinstance(obj, bool):
        return
    text = str(obj)
    k = key.lower()

    for m in _ACT_RE.finditer(text):
        _add(out.account_ids, "act_" + m.group(1))
    for m in _GOOGLE_RESOURCE_RE.finditer(text):
        _add(out.account_ids, "google:" + m.group(1))
        if m.group(3):
            _add(out.entity_ids, m.group(3))

    if _ACCOUNT_KEYS.match(key):
        digits = re.sub(r"\D", "", text)
        if "customer" in k and len(digits) == 10:
            _add(out.account_ids, "google:" + digits)
        elif digits and not text.startswith("act_"):
            _add(out.account_ids, "act_" + digits)
    elif _ENTITY_KEYS.match(key) and re.fullmatch(r"\d{4,25}", text):
        _add(out.entity_ids, text)

    if k in ("status", "configured_status", "effective_status", "new_status", "target_status"):
        out.statuses.append(text.upper())
    if _BUDGET_KEYS.match(key):
        try:
            out.budgets.append(float(text))
            out.budget_keys.append(key)
        except ValueError:
            pass
    if _GEO_KEYS.match(key):
        out.touches_geo = True
    if "bid" in k:
        out.touches_bid = True
    if any(t in k for t in ("pixel", "dataset", "conversion", "promoted_object", "custom_event")):
        out.touches_tracking = True


def extract(tool_input: Any) -> Extracted:
    out = Extracted()
    _walk(tool_input or {}, out)
    # A geo key with a nested value still sets touches_geo via its children; also
    # catch keys whose value is a container.
    blob = json.dumps(tool_input, default=str).lower() if tool_input else ""
    if any(f'"{g}"' in blob for g in ("geo_locations", "custom_locations", "countries", "cities", "regions")):
        out.touches_geo = True
    return out


def split_accounts(ex: Extracted):
    """-> (meta_accounts, google_accounts)"""
    meta = [a for a in ex.account_ids if a.startswith("act_")]
    google = [a.split(":", 1)[1] for a in ex.account_ids if a.startswith("google:")]
    return meta, google
