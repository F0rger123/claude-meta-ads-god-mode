"""Automation-mode policy: decide auto / approval / blocked for one action.

Modes (per client, automation.mode):
  read_only    - analyze and recommend. No writes except an approved pause.
  draft        - may create PAUSED objects. Nothing else without approval;
                 activation and budget changes are blocked.
  approval     - may create PAUSED objects; every other write needs a human yes.
  guarded_auto - like approval, but small predefined changes inside the
                 client's limits run without a prompt.
  full_auto    - architecturally supported, disabled unless the operator sets
                 ADS_GODMODE_ENABLE_FULL_AUTO=1. Even then ALWAYS_APPROVAL
                 actions still need a human yes.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import actions as A
from .budget import BudgetChange, check_limits

AUTO, APPROVAL, BLOCKED = "auto", "approval", "blocked"

DEFAULT_GUARDED = {
    "allowed_actions": [A.BUDGET, A.PAUSE, A.NEGATIVE_KEYWORDS],
    "max_entities_per_change": 3,
    "max_negative_keywords_per_change": 10,
    "max_bid_change_pct": 15.0,
}


@dataclass
class Decision:
    verdict: str
    reasons: List[str] = field(default_factory=list)

    @property
    def allowed_without_prompt(self) -> bool:
        return self.verdict == AUTO

    def to_dict(self) -> Dict:
        return {"verdict": self.verdict, "reasons": self.reasons}


def full_auto_enabled() -> bool:
    return os.environ.get("ADS_GODMODE_ENABLE_FULL_AUTO") == "1"


def evaluate(profile, action: str, budget_change: Optional[BudgetChange] = None,
             entity_count: int = 1, negative_keyword_count: int = 0,
             bid_change_pct: Optional[float] = None,
             hours_since_last_change: Optional[float] = None) -> Decision:
    mode = profile.mode
    if action in A.NON_MUTATING:
        return Decision(AUTO, ["read-only or preview call"])
    if action not in A.ALL:
        action = A.UNKNOWN_WRITE

    if action in A.ALWAYS_BLOCKED:
        why = {
            A.CREATE_ACTIVE: "objects must be created PAUSED; activation is a separate approved step",
            A.BILLING: "billing and payment changes are never made by Claude; do this in the platform UI",
            A.ADMIN: "ownership, user and permission changes are never made by Claude",
        }[action]
        return Decision(BLOCKED, [why])

    if action in A.SPEND_REDUCING and mode in ("read_only", "draft"):
        return Decision(APPROVAL, [f"pause allowed in {mode} mode only with explicit approval"])

    if mode == "read_only":
        return Decision(BLOCKED, ["client is in read_only mode: analyze and recommend only"])

    if action == A.CREATE:
        return Decision(AUTO, ["creating PAUSED objects is allowed; activation needs approval"])

    if mode == "draft":
        return Decision(BLOCKED, [f"client is in draft mode: {action} is not allowed, only PAUSED creation"])

    if action in A.ALWAYS_APPROVAL:
        return Decision(APPROVAL, [f"{action} always requires explicit approval"])

    effective = mode
    reasons: List[str] = []
    if mode == "full_auto" and not full_auto_enabled():
        effective = "guarded_auto"
        reasons.append("full_auto is disabled on this machine; evaluated as guarded_auto")

    if effective == "approval":
        return Decision(APPROVAL, reasons + ["client is in approval mode"])

    high = profile.approval.get("high_budget_daily_threshold")

    if effective == "full_auto":
        if action == A.BUDGET and budget_change is not None:
            hard = check_limits(budget_change, {"max_budget_increase_pct": 50, "max_budget_decrease_pct": 100,
                                                "max_daily_dollar_change": 10 ** 9, "min_spend": 0,
                                                "min_conversions": 0, "min_confidence": "EXPERIMENT",
                                                "cooldown_hours": 0}, high, None)
            if hard:
                return Decision(APPROVAL, reasons + hard)
        return Decision(AUTO, reasons + ["full_auto enabled by operator and client"])

    # guarded_auto
    cfg = {**DEFAULT_GUARDED, **profile.guarded_limits}
    if action not in cfg["allowed_actions"] or action not in A.GUARDABLE:
        return Decision(APPROVAL, reasons + [f"{action} is not in this client's guarded_auto allowed_actions"])
    if entity_count > int(cfg["max_entities_per_change"]):
        return Decision(APPROVAL, reasons + [f"{entity_count} entities exceeds max {cfg['max_entities_per_change']} per change"])
    if action == A.BUDGET:
        if budget_change is None:
            return Decision(APPROVAL, reasons + ["budget change without a computed proposal"])
        violations = check_limits(budget_change, profile.guarded_limits, high, hours_since_last_change)
        if violations:
            return Decision(APPROVAL, reasons + violations)
    if action == A.NEGATIVE_KEYWORDS and negative_keyword_count > int(cfg["max_negative_keywords_per_change"]):
        return Decision(APPROVAL, reasons + [f"{negative_keyword_count} negatives exceeds max {cfg['max_negative_keywords_per_change']}"])
    if action == A.BID:
        if bid_change_pct is None or abs(bid_change_pct) > float(cfg["max_bid_change_pct"]):
            return Decision(APPROVAL, reasons + [f"bid change must be within {cfg['max_bid_change_pct']}%"])
    if action != A.BUDGET and hours_since_last_change is not None:
        cooldown = float(profile.guarded_limits.get("cooldown_hours", 72))
        if hours_since_last_change < cooldown:
            return Decision(APPROVAL, reasons + [f"entity changed {hours_since_last_change:.0f}h ago; cooldown {cooldown:.0f}h"])
    return Decision(AUTO, reasons + ["within guarded_auto limits"])
