"""Data-quality and confidence grading for recommendations.

These are HEURISTICS (see references/metrics.md), not platform facts. They
exist so Claude says "not enough data" instead of over-reading noise.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

HIGH, MODERATE, EXPERIMENT = "HIGH", "MODERATE", "EXPERIMENT"


@dataclass
class Quality:
    confidence: str
    warnings: List[str] = field(default_factory=list)
    score: int = 0

    def to_dict(self) -> Dict:
        return {"confidence": self.confidence, "score": self.score, "warnings": self.warnings}


def assess(conversions: Optional[int], spend: Optional[float], days: int,
           target_cpa: Optional[float] = None, tracking_healthy: Optional[bool] = None,
           in_learning: bool = False, days_since_major_change: Optional[float] = None,
           conversion_lag_days: float = 0, attribution_note: str = "",
           seasonal_event: bool = False) -> Quality:
    """Grade the evidence behind a recommendation. Score 0-100 -> confidence band."""
    warnings, score = [], 100
    if tracking_healthy is False:
        warnings.append("tracking is broken or unverified: conversion numbers may be wrong")
        score -= 50
    elif tracking_healthy is None:
        warnings.append("tracking health not verified")
        score -= 15
    conv = conversions or 0
    if conv < 10:
        warnings.append(f"only {conv} conversions: too few to judge CPA")
        score -= 40
    elif conv < 30:
        warnings.append(f"{conv} conversions: directional only")
        score -= 20
    if target_cpa and spend is not None and spend < 2 * target_cpa and conv < 3:
        warnings.append("spend is under 2x target CPA: absence of conversions is not yet evidence")
        score -= 20
    if days < 7:
        warnings.append(f"{days}-day window misses day-of-week effects")
        score -= 15
    if conversion_lag_days and days <= conversion_lag_days * 2:
        warnings.append(f"window is short relative to ~{conversion_lag_days:g}-day conversion lag; recent days are undercounted")
        score -= 15
    if in_learning:
        warnings.append("ad set is in the learning phase: performance is unstable by design")
        score -= 20
    if days_since_major_change is not None and days_since_major_change < 7:
        warnings.append(f"major change {days_since_major_change:.0f} days ago: before/after comparison is unreliable")
        score -= 15
    if seasonal_event:
        warnings.append("window includes a seasonal/holiday period")
        score -= 10
    if attribution_note:
        warnings.append(attribution_note)
    score = max(0, min(100, score))
    band = HIGH if score >= 70 else MODERATE if score >= 40 else EXPERIMENT
    if conv < 10 or tracking_healthy is False:
        band = EXPERIMENT  # hard cap: no strong call on a handful of conversions or broken tracking
    return Quality(band, warnings, score)


def two_proportion_z(successes_a: int, trials_a: int, successes_b: int, trials_b: int) -> Optional[float]:
    """z statistic for rate A vs rate B (CTR or CVR). None when undefined."""
    if min(trials_a, trials_b) <= 0:
        return None
    p_a, p_b = successes_a / trials_a, successes_b / trials_b
    pooled = (successes_a + successes_b) / (trials_a + trials_b)
    se = math.sqrt(pooled * (1 - pooled) * (1 / trials_a + 1 / trials_b))
    if se == 0:
        return None
    return (p_a - p_b) / se


def compare_rates(successes_a: int, trials_a: int, successes_b: int, trials_b: int) -> Dict:
    z = two_proportion_z(successes_a, trials_a, successes_b, trials_b)
    if z is None:
        verdict = EXPERIMENT
    elif abs(z) >= 2.58:
        verdict = HIGH       # ~99% two-sided
    elif abs(z) >= 1.96:
        verdict = MODERATE   # ~95% two-sided
    else:
        verdict = EXPERIMENT
    return {"z": None if z is None else round(z, 2), "confidence": verdict,
            "rate_a": successes_a / trials_a if trials_a else None,
            "rate_b": successes_b / trials_b if trials_b else None}


def conversions_needed(tolerance: float = 0.3) -> int:
    """Rough Poisson rule: n conversions gives ~1/sqrt(n) relative error on CPA.
    tolerance 0.3 -> 12 conversions; 0.2 -> 25; 0.1 -> 100."""
    return max(1, math.ceil(1 / tolerance ** 2))
