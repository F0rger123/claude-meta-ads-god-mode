"""Spend anomaly detection for the emergency-stop workflow.

Input rows (one per campaign or ad set), as Claude assembles them from reads:
  {"id": "123", "name": "...", "platform": "meta", "account_id": "act_1",
   "status": "ACTIVE", "daily_budget": 50, "spend_today": 140,
   "spend_history": [48, 51, 47, 50, 52, 49, 50],   # previous days, oldest first
   "conversions_today": 0, "hours_elapsed": 14}
"""

import statistics
from typing import Dict, List


def detect(rows: List[Dict], z_threshold: float = 3.0, pace_threshold: float = 1.5,
           min_spend: float = 20.0) -> List[Dict]:
    """Return flagged rows with reasons, most severe first."""
    flags = []
    for r in rows:
        reasons, severity = [], 0
        spend = float(r.get("spend_today") or 0)
        if spend < min_spend:
            continue
        budget = r.get("daily_budget")
        hours = float(r.get("hours_elapsed") or 24)
        if budget:
            expected_so_far = float(budget) * min(hours, 24) / 24
            if spend > float(budget) * 1.25:
                reasons.append(f"spend {spend:.2f} is over 125% of daily budget {float(budget):.2f}")
                severity += 3
            elif expected_so_far and spend > expected_so_far * pace_threshold and hours < 20:
                reasons.append(f"pacing {spend / expected_so_far:.1f}x expected for {hours:.0f}h elapsed")
                severity += 2
        hist = [float(x) for x in (r.get("spend_history") or []) if x is not None]
        if len(hist) >= 5:
            mean = statistics.mean(hist)
            sd = statistics.pstdev(hist) or max(mean * 0.1, 1.0)
            z = (spend - mean) / sd
            if z >= z_threshold:
                reasons.append(f"spend {spend:.2f} is {z:.1f} sd above the {len(hist)}-day mean {mean:.2f}")
                severity += 2
        elif not budget:
            reasons.append("new or unknown entity spending with no history or budget")
            severity += 1
        if r.get("conversions_today") == 0 and budget and spend > float(budget):
            reasons.append("no conversions today while over budget")
            severity += 1
        if reasons:
            flags.append({**r, "severity": severity, "reasons": reasons})
    return sorted(flags, key=lambda f: -f["severity"])
