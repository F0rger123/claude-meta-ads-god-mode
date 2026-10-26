"""Budget planner: turn "I can spend $X a month (or a day)" into a recommendation.

Answers, with the math shown:
  * daily vs monthly vs fixed-flight budgets, per platform
  * what the money buys: expected results range at the target cost per result
  * whether it is enough for Meta to learn (~50 optimization events/week/ad set)
    and for Google Search to get useful click volume
  * how to split Meta vs Google
  * whether to spend more ("squeeze more out"), with the ROI math, or less

All thresholds are HEURISTICS (see references/metrics.md) except where noted.
This module only recommends. It never changes a budget or billing setting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

DAYS_PER_MONTH = 30.4          # PLATFORM FACT (Google): monthly cap = 30.4 x average daily budget
META_LEARNING_EVENTS = 50      # PLATFORM FACT (Meta guidance): ~50 optimization events / 7 days
META_VIABLE_EVENTS_PER_WEEK = 5  # HEURISTIC: below ~5 results/week Meta has too little signal to optimize
GOOGLE_MIN_CLICKS_PER_DAY = 10  # HEURISTIC: below this a Search campaign learns slowly
DEFAULT_ACQ_SHARE = 0.30       # HEURISTIC: share of gross profit a business can spend to acquire a sale


@dataclass
class BudgetInputs:
    monthly: Optional[float] = None
    daily: Optional[float] = None
    target_cpl: Optional[float] = None
    job_value: Optional[float] = None
    close_rate_pct: Optional[float] = None
    margin_pct: Optional[float] = None
    lead_value: Optional[float] = None
    platforms: List[str] = field(default_factory=lambda: ["meta"])
    google_cpc: Optional[float] = None
    goal_results_per_month: Optional[int] = None
    hard_monthly_cap: bool = False   # "never go over this amount in a month"
    flight_days: Optional[int] = None  # a fixed-length campaign (promo, launch)
    currency: str = "USD"


def _round(x: float, step: float = 5) -> float:
    return round(x / step) * step if x >= 20 else round(x, 2)


def max_affordable_cpl(i: BudgetInputs) -> Optional[float]:
    if i.job_value and i.close_rate_pct and i.margin_pct:
        return i.job_value * (i.close_rate_pct / 100) * (i.margin_pct / 100) * DEFAULT_ACQ_SHARE
    if i.lead_value:
        return i.lead_value
    return None


def plan(i: BudgetInputs) -> Dict:
    if not i.monthly and not i.daily:
        raise ValueError("give a monthly or a daily budget")
    monthly = i.monthly if i.monthly else i.daily * DAYS_PER_MONTH
    daily = monthly / DAYS_PER_MONTH
    plats = [p for p in i.platforms if p in ("meta", "google")] or ["meta"]
    cpl = i.target_cpl
    mac = max_affordable_cpl(i)
    recs: List[Dict] = []
    out: Dict = {"currency": i.currency, "monthly": round(monthly, 2), "daily": round(daily, 2),
                 "max_affordable_cpl": None if mac is None else round(mac, 2), "platforms": {}, "recommendations": recs}

    # ---- split
    split = {"meta": 1.0} if plats == ["meta"] else {"google": 1.0} if plats == ["google"] else None
    if split is None:
        meta_min = (META_VIABLE_EVENTS_PER_WEEK * cpl / 7) if cpl else None
        g_min = (GOOGLE_MIN_CLICKS_PER_DAY * i.google_cpc) if i.google_cpc else None
        if meta_min and g_min and daily < (g_min + meta_min):
            split = {"google": 1.0, "meta": 0.0}
            recs.append({"type": "split", "label": "HEURISTIC",
                         "text": f"At ${daily:,.0f}/day, start with Google Search only (it catches people already searching). "
                                 f"Add Meta once there is about ${meta_min:,.0f}/day more for it (~{META_VIABLE_EVENTS_PER_WEEK} leads/week)."})
        else:
            split = {"google": 0.6, "meta": 0.4}
            recs.append({"type": "split", "label": "HEURISTIC",
                         "text": "Start about 60% Google Search / 40% Meta for local lead generation. "
                                 "Shift toward whichever brings cheaper *qualified* leads after 4-6 weeks, not last-click ROAS alone."})
    out["split"] = split

    # ---- per platform
    for p, share in split.items():
        if share <= 0:
            continue
        pd_ = daily * share
        pm = monthly * share
        info: Dict = {"daily": round(pd_, 2), "monthly": round(pm, 2)}
        if cpl:
            exp = pm / cpl
            info["expected_results_per_month"] = [int(exp * 0.7), int(exp * 1.3)]
        if p == "meta" and cpl:
            weekly_events = pd_ * 7 / cpl
            info["weekly_optimization_events"] = round(weekly_events, 1)
            need = META_LEARNING_EVENTS * cpl / 7
            info["daily_needed_to_exit_learning"] = _round(need)
            if weekly_events >= META_LEARNING_EVENTS * 2:
                info["ad_sets"] = int(weekly_events // META_LEARNING_EVENTS)
            else:
                info["ad_sets"] = 1
            if weekly_events < META_LEARNING_EVENTS:
                recs.append({"type": "learning", "platform": "meta", "label": "PLATFORM FACT + HEURISTIC",
                             "text": f"Meta budget ${pd_:,.0f}/day buys about {weekly_events:.0f} results a week. Meta's guidance is about 50 a week "
                                     f"for an ad set to finish learning. Use ONE campaign with ONE ad set (no splitting), expect 'learning limited', "
                                     f"and judge it over 2-3 weeks. ~${need:,.0f}/day would let it fully learn."})
        if p == "google":
            if i.google_cpc:
                clicks = pd_ / i.google_cpc
                info["clicks_per_day"] = round(clicks, 1)
                if clicks < GOOGLE_MIN_CLICKS_PER_DAY:
                    recs.append({"type": "volume", "platform": "google", "label": "HEURISTIC",
                                 "text": f"${pd_:,.0f}/day at ~${i.google_cpc:.2f}/click is ~{clicks:.0f} clicks a day. Keep it to ONE tightly themed "
                                         f"Search campaign and exact/phrase keywords so the money isn't spread thin."})
            info["note"] = "PLATFORM FACT: Google may spend up to 2x the daily budget on a busy day but keeps the month at or under 30.4x daily."
        out["platforms"][p] = info

    # ---- budget type
    if i.flight_days:
        bt = {"meta": f"Lifetime budget of ${monthly / DAYS_PER_MONTH * i.flight_days * split.get('meta', 0):,.0f} over {i.flight_days} days (hard total, Meta paces it).",
              "google": f"Daily budget of ${daily * split.get('google', 0):,.0f} with start/end dates for the {i.flight_days}-day flight."}
        why = "fixed-length promotion: a lifetime/flight budget caps the total automatically."
    elif i.hard_monthly_cap:
        bt = {"meta": "Monthly campaigns with a lifetime budget per calendar month (start 1st, end last day), "
                      "plus an account spending limit you set yourself in Meta Billing as a safety net.",
              "google": f"Average daily budget of ${daily * split.get('google', 0):,.0f} (Google's monthly limit is 30.4x daily, so the month can't run over)."}
        why = "you never want to exceed the month: lifetime-per-month on Meta, Google's built-in monthly limit."
    else:
        bt = {"meta": f"Daily budget of ${daily * split.get('meta', 0):,.0f} at the campaign level (Advantage+ campaign budget), always on.",
              "google": f"Average daily budget of ${daily * split.get('google', 0):,.0f}, always on."}
        why = "always-on lead flow: daily budgets are steady and easy to scale in small steps."
    out["budget_type"] = {k: v for k, v in bt.items() if split.get(k, 0) > 0}
    recs.append({"type": "budget_type", "label": "BEST PRACTICE", "text": "Recommended budget type - " + why})

    # ---- spend more / less
    if cpl and mac:
        if mac >= cpl * 1.3:
            extra = daily * 0.25
            extra_leads = extra * DAYS_PER_MONTH / cpl
            close = (i.close_rate_pct or 0) / 100
            rev = extra_leads * close * (i.job_value or 0) if i.job_value else None
            text = (f"You can afford up to ~${mac:,.0f} per lead and are targeting ${cpl:,.0f}. There is room to spend more: "
                    f"+${extra:,.0f}/day (+25%) would buy about {extra_leads:.0f} more leads a month")
            if rev:
                text += f", or about {extra_leads * close:.1f} more jobs (~${rev:,.0f} revenue) at your close rate"
            text += ". Raise it in 20% steps after the first 2-3 weeks prove the cost per lead."
            recs.append({"type": "scale", "label": "RECOMMENDATION (math shown)", "text": text})
        elif mac < cpl:
            recs.append({"type": "economics", "label": "WARNING",
                         "text": f"Your target ${cpl:,.0f} per lead is above what the numbers support (~${mac:,.0f}). "
                                 "Improve the offer or close rate first, or lower the target; more budget would lose money."})
    if i.goal_results_per_month and cpl:
        need = i.goal_results_per_month * cpl
        if need > monthly * 1.1:
            recs.append({"type": "goal", "label": "MATH",
                         "text": f"{i.goal_results_per_month} leads/month at ${cpl:,.0f} needs about ${need:,.0f}/month; "
                                 f"the budget is ${monthly:,.0f}. Either raise the budget or expect ~{int(monthly / cpl)} leads."})
    recs.append({"type": "billing", "label": "SETUP",
                 "text": "You add the payment method yourself in Meta Billing / Google Ads Billing; the platforms charge it as ads run. "
                         "God Mode keeps spend inside these budgets and flags overspend or failed payments."})
    return out


def from_profile(profile, **overrides) -> BudgetInputs:
    e = profile.data.get("economics", {})
    plats = [p for p in ("meta", "google") if profile.platform_enabled(p)]
    args = dict(monthly=e.get("monthly_budget"), target_cpl=e.get("desired_cpl") or e.get("desired_cpa"),
                job_value=e.get("average_job_value"), close_rate_pct=e.get("lead_to_sale_rate_pct"),
                margin_pct=e.get("gross_margin_pct"), lead_value=e.get("lead_value"), platforms=plats or ["meta"],
                currency=e.get("currency", "USD"))
    args.update({k: v for k, v in overrides.items() if v is not None})
    return BudgetInputs(**args)


def to_text(p: Dict) -> str:
    c = p["currency"]
    lines = [f"BUDGET PLAN - {p['monthly']:,.0f} {c}/month (~{p['daily']:,.0f}/day)"]
    if p.get("max_affordable_cpl"):
        lines.append(f"Max affordable cost per lead: ~{p['max_affordable_cpl']:,.0f} {c}")
    for name, info in p["platforms"].items():
        bits = [f"{info['daily']:,.0f}/day", f"{info['monthly']:,.0f}/month"]
        if "expected_results_per_month" in info:
            lo, hi = info["expected_results_per_month"]
            bits.append(f"{lo}-{hi} results/month")
        lines.append(f"- {name.title()}: " + ", ".join(bits))
        if name in p.get("budget_type", {}):
            lines.append(f"  Budget type: {p['budget_type'][name]}")
    lines.append("Recommendations:")
    for r in p["recommendations"]:
        lines.append(f"- [{r['label']}] {r['text']}")
    return "\n".join(lines)
