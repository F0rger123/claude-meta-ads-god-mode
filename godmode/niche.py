"""Niche playbooks: what we know about a type of business, and what has worked for it.

A playbook is shared knowledge about a niche ("roofing", "dental-implants",
"kitchen-remodeling"), not about one client. It holds sourced facts (benchmarks,
offers, hooks, seasonality, conversion rates) gathered during niche research,
and it is combined with outcomes from every client tagged with that niche.

Rules: every fact carries a source (URL or "account data"), a date and a label
(PLATFORM FACT / THIRD-PARTY BENCHMARK / OBSERVED / HEURISTIC). Client data never
goes into a playbook - only tactic-level win rates, through learning.niche_patterns.

Storage: ADS_GODMODE_HOME/niches/<niche>.json (private).
"""

import json
import re
from datetime import date
from typing import Dict, List

from . import learning, paths, profiles

LABELS = {"PLATFORM FACT", "THIRD-PARTY BENCHMARK", "OBSERVED", "HEURISTIC"}
SECTIONS = ("benchmarks", "what_converts", "offers", "hooks", "audiences", "seasonality", "competitors_seen",
            "platform_fit", "landing_pages")


class NicheError(Exception):
    pass


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    if not s:
        raise NicheError("niche name is empty")
    return s


def _path(niche: str):
    d = paths.home() / "niches"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{slug(niche)}.json"


def validate(pb: Dict) -> List[str]:
    errors = []
    if not pb.get("niche"):
        errors.append("niche is required")
    for sec in SECTIONS:
        for i, item in enumerate(pb.get(sec, []) or []):
            where = f"{sec}[{i}]"
            if not isinstance(item, dict) or not item.get("text"):
                errors.append(f"{where}: needs text")
                continue
            if item.get("label") not in LABELS:
                errors.append(f"{where}: label must be one of {sorted(LABELS)}")
            if not item.get("source"):
                errors.append(f"{where}: source is required (URL or 'account data')")
            if not re.match(r"^\d{4}-\d{2}(-\d{2})?$", str(item.get("date", ""))):
                errors.append(f"{where}: date YYYY-MM or YYYY-MM-DD is required")
    return errors


def save(pb: Dict) -> str:
    errors = validate(pb)
    if errors:
        raise NicheError("; ".join(errors))
    pb["niche"] = slug(pb["niche"])
    pb["updated"] = date.today().isoformat()
    p = _path(pb["niche"])
    p.write_text(json.dumps(pb, indent=2), encoding="utf-8")
    return str(p)


def load(niche: str) -> Dict:
    p = _path(niche)
    if not p.exists():
        raise NicheError(f"no playbook for {slug(niche)!r} yet - run /ads:research")
    return json.loads(p.read_text(encoding="utf-8"))


def list_all() -> List[Dict]:
    d = paths.home() / "niches"
    if not d.exists():
        return []
    out = []
    for p in sorted(d.glob("*.json")):
        pb = json.loads(p.read_text(encoding="utf-8"))
        out.append({"niche": pb["niche"], "updated": pb.get("updated"),
                    "facts": sum(len(pb.get(s, []) or []) for s in SECTIONS)})
    return out


def clients_in(niche: str) -> List[str]:
    n = slug(niche)
    out = []
    for p in profiles.list_all():
        raw = p.data.get("business", {}).get("niche")
        if raw and slug(raw) == n:
            out.append(p.slug)
    return out


def niche_patterns(niche: str) -> Dict:
    """Tactic win rates across every client in this niche (2+ clients needed). Label: NICHE PATTERN."""
    cl = clients_in(niche)
    rows = learning.portfolio_patterns(cl) if len(cl) >= 2 else []
    for r in rows:
        r["label"] = "NICHE PATTERN"
    return {"niche": slug(niche), "clients": len(cl), "patterns": rows,
            "note": "Needs 2+ clients in the niche with judged outcomes." if len(cl) < 2 else ""}


def stale(pb: Dict, today: date = None, max_age_days: int = 120) -> bool:
    today = today or date.today()
    try:
        y, m, d = (pb.get("updated") or "1970-01-01").split("-")
        return (today - date(int(y), int(m), int(d))).days > max_age_days
    except ValueError:
        return True
