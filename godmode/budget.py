"""Budget change proposals and guarded-auto budget limits."""

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

DEFAULT_LIMITS = {
    "max_budget_increase_pct": 20.0,
    "max_budget_decrease_pct": 30.0,
    "max_daily_dollar_change": 50.0,
    "min_spend": 100.0,
    "min_conversions": 15,
    "min_confidence": "MODERATE",
    "cooldown_hours": 72,
}

CONFIDENCE_ORDER = {"EXPERIMENT": 0, "MODERATE": 1, "HIGH": 2}


@dataclass
class BudgetChange:
    current: float
    proposed: float
    currency: str = "USD"
    period: str = "daily"            # daily | lifetime
    reason: str = ""
    evidence: str = ""
    expected_effect: str = ""
    risks: str = ""
    confidence: str = "EXPERIMENT"
    spend_in_window: Optional[float] = None
    conversions_in_window: Optional[int] = None
    limit_violations: List[str] = field(default_factory=list)

    @property
    def delta(self) -> float:
        return round(self.proposed - self.current, 2)

    @property
    def pct(self) -> Optional[float]:
        if self.current <= 0:
            return None
        return round((self.proposed - self.current) / self.current * 100, 1)

    @property
    def direction(self) -> str:
        return "increase" if self.delta > 0 else "decrease" if self.delta < 0 else "none"

    def to_dict(self) -> Dict:
        d = asdict(self)
        d.update(delta=self.delta, pct=self.pct, direction=self.direction)
        return d


def check_limits(change: BudgetChange, limits: Dict, high_budget_threshold: Optional[float] = None,
                 hours_since_last_change: Optional[float] = None) -> List[str]:
    """Return every guarded-auto limit this change breaks. Empty = within limits."""
    lim = {**DEFAULT_LIMITS, **(limits or {})}
    v = []
    if change.proposed < 0:
        v.append("proposed budget is negative")
    if change.pct is None:
        v.append("current budget unknown or zero; percent change cannot be computed")
    elif change.direction == "increase" and change.pct > float(lim["max_budget_increase_pct"]):
        v.append(f"increase {change.pct}% exceeds max {lim['max_budget_increase_pct']}%")
    elif change.direction == "decrease" and abs(change.pct) > float(lim["max_budget_decrease_pct"]):
        v.append(f"decrease {abs(change.pct)}% exceeds max {lim['max_budget_decrease_pct']}%")
    if abs(change.delta) > float(lim["max_daily_dollar_change"]):
        v.append(f"change of {abs(change.delta)} {change.currency} exceeds max {lim['max_daily_dollar_change']}")
    if high_budget_threshold is not None and change.proposed > float(high_budget_threshold):
        v.append(f"proposed budget {change.proposed} is above the client's high-budget threshold {high_budget_threshold}")
    if change.direction == "increase":
        if change.spend_in_window is None or change.spend_in_window < float(lim["min_spend"]):
            v.append(f"spend in window below minimum {lim['min_spend']} (or unknown)")
        if change.conversions_in_window is None or change.conversions_in_window < int(lim["min_conversions"]):
            v.append(f"conversions in window below minimum {lim['min_conversions']} (or unknown)")
    need = CONFIDENCE_ORDER.get(str(lim["min_confidence"]).upper(), 1)
    if CONFIDENCE_ORDER.get(change.confidence.upper(), 0) < need:
        v.append(f"confidence {change.confidence} below required {lim['min_confidence']}")
    if hours_since_last_change is not None and hours_since_last_change < float(lim["cooldown_hours"]):
        v.append(f"last change on this entity was {hours_since_last_change:.0f}h ago; cooldown is {lim['cooldown_hours']}h")
    return v


def to_minor_units(amount: float) -> int:
    """Meta budgets are in the account currency's minor unit (cents for USD)."""
    return int(round(amount * 100))


def to_micros(amount: float) -> int:
    """Google Ads amounts are in micros (1 unit = 1,000,000 micros)."""
    return int(round(amount * 1_000_000))


def format_summary(change: BudgetChange, entity_label: str = "") -> str:
    pct = "n/a" if change.pct is None else f"{change.pct:+.1f}%"
    lines = [
        f"BUDGET CHANGE{(' - ' + entity_label) if entity_label else ''}",
        f"CURRENT BUDGET : {change.current:,.2f} {change.currency} ({change.period})",
        f"PROPOSED BUDGET: {change.proposed:,.2f} {change.currency} ({change.period})",
        f"PERCENT CHANGE : {pct}",
        f"DOLLAR CHANGE  : {change.delta:+,.2f} {change.currency}",
        f"REASON         : {change.reason or '(missing)'}",
        f"DATA           : {change.evidence or '(missing)'}",
        f"EXPECTED EFFECT: {change.expected_effect or '(missing)'}",
        f"RISKS          : {change.risks or '(missing)'}",
        f"CONFIDENCE     : {change.confidence}",
    ]
    if change.limit_violations:
        lines.append("OUTSIDE GUARDED-AUTO LIMITS: " + "; ".join(change.limit_violations))
    return "\n".join(lines)
