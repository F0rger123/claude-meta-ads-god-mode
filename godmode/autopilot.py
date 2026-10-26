"""Autopilot: hands-off day-to-day fixes, inside money decisions already made.

When a client turns autopilot on (with a daily spend cap), Claude may - without
asking - do these, and only these:

  pause_losers      pause ads / ad sets that clearly fail the client's loser rules
  fix_and_relaunch  swap a failing ad for a fixed replacement in the SAME ad set
                    (pause old + activate new), while the account's total daily
                    budget stays at or under the cap; max N swaps per week
  google_negatives  add small negative-keyword lists (<= max per run)

Never on autopilot: new campaigns or ad sets going live, budget increases, new
locations, tracking changes, deletes, billing. Those still need a human yes.
Autopilot works in approval / guarded_auto / full_auto modes, not read_only or draft.
"""

import json
import time
from typing import Dict, List, Optional

from . import paths, profiles

DEFAULTS = {
    "enabled": False,
    "daily_spend_cap": None,
    "actions": ["pause_losers", "fix_and_relaunch", "google_negatives"],
    "max_swaps_per_week": 3,
    "max_entities_per_run": 3,
    "max_negatives_per_run": 10,
    "loser_rules": {
        "min_hours_live": 72,              # never judge anything younger than 3 days
        "zero_result_spend_multiple": 2.5,  # spent >= 2.5x target CPL with 0 results -> loser
        "cpl_multiple": 2.0,               # CPL >= 2x target with >= min_results -> loser
        "min_results_for_cpl": 5,
        "skip_learning": True,
    },
}
ACTIONS = ("pause_losers", "fix_and_relaunch", "google_negatives")


def settings(profile: profiles.Profile) -> Dict:
    raw = profile.data.get("automation", {}).get("autopilot") or {}
    out = {**DEFAULTS, **raw}
    out["loser_rules"] = {**DEFAULTS["loser_rules"], **(raw.get("loser_rules") or {})}
    return out


def active(profile: profiles.Profile) -> bool:
    return bool(settings(profile)["enabled"]) and profile.mode not in ("read_only", "draft")


def set_state(slug: str, enabled: bool, cap: Optional[float] = None, actions: Optional[List[str]] = None) -> Dict:
    """Toggle autopilot in the client profile (the profile file is the single source of truth)."""
    path = paths.clients_dir() / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    auto = data.setdefault("automation", {})
    ap = {**DEFAULTS, **(auto.get("autopilot") or {})}
    if enabled:
        if cap is None and not ap.get("daily_spend_cap"):
            raise ValueError("turning autopilot on needs a daily spend cap (--cap)")
        if auto.get("mode", "read_only") in ("read_only", "draft"):
            raise ValueError(f"client is in {auto.get('mode')} mode; switch to approval first so autopilot can act")
    if cap is not None:
        if cap <= 0:
            raise ValueError("cap must be positive")
        ap["daily_spend_cap"] = float(cap)
    if actions is not None:
        bad = [a for a in actions if a not in ACTIONS]
        if bad:
            raise ValueError(f"unknown autopilot actions {bad}; choose from {ACTIONS}")
        ap["actions"] = actions
    ap["enabled"] = bool(enabled)
    ap["changed_at"] = time.strftime("%Y-%m-%d %H:%M")
    auto["autopilot"] = ap
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return ap


def candidates(profile: profiles.Profile, snapshot: Dict) -> Dict:
    """Read a snapshot and list what autopilot would act on (pure; changes nothing)."""
    ap = settings(profile)
    rules = ap["loser_rules"]
    target = profile.data.get("economics", {}).get("desired_cpl") or profile.data.get("economics", {}).get("desired_cpa")
    losers, fatigued, waste = [], [], []
    for plat, p in (snapshot.get("platforms") or {}).items():
        if p.get("tracking_ok") is False:
            return {"blocked": f"{plat} tracking is broken - autopilot does nothing until tracking is fixed",
                    "losers": [], "fatigued": [], "google_negatives": []}
        for e in p.get("entities", []):
            if rules["skip_learning"] and e.get("learning") == "learning":
                continue
            hours = e.get("hours_live", (e.get("age_days") or 0) * 24)
            if hours and hours < rules["min_hours_live"]:
                continue
            spend, res = float(e.get("spend") or 0), float(e.get("results") or 0)
            why = None
            if target and res == 0 and spend >= rules["zero_result_spend_multiple"] * float(target):
                why = f"${spend:,.0f} spent, 0 results (>= {rules['zero_result_spend_multiple']}x target ${target})"
            elif target and res >= rules["min_results_for_cpl"] and spend / res >= rules["cpl_multiple"] * float(target):
                why = f"CPL ${spend / res:,.0f} is >= {rules['cpl_multiple']}x target ${target} on {int(res)} results"
            if why:
                losers.append({"platform": plat, "id": e.get("id"), "name": e.get("name"), "level": e.get("level"), "why": why})
                continue
            ctr, prev, freq = e.get("ctr"), e.get("ctr_prev"), e.get("frequency")
            if ctr and prev and freq and float(freq) >= 3 and float(ctr) < 0.8 * float(prev):
                fatigued.append({"platform": plat, "id": e.get("id"), "name": e.get("name"),
                                 "why": f"frequency {freq}, CTR {prev}% -> {ctr}%"})
        if plat == "google" and p.get("search_term_waste"):
            waste.append({"platform": "google", "waste": p["search_term_waste"]})
    acts = set(ap["actions"])
    return {"enabled": active(profile), "daily_spend_cap": ap["daily_spend_cap"],
            "losers": losers[: ap["max_entities_per_run"]] if "pause_losers" in acts else [],
            "fatigued": fatigued if "fix_and_relaunch" in acts else [],
            "google_negatives": waste if "google_negatives" in acts else []}
