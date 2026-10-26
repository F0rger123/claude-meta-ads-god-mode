"""Self-learning loop: predict -> change -> read the outcome -> lesson.

Every planned change can carry a prediction ("CPL down ~10% within 7 days").
At the read date the outcome is recorded, from a snapshot or by hand, and
graded worked / failed / inconclusive with sample-size checks. Lessons roll up
by tactic tag ("budget-up-20", "ugc-hook", "negatives") into what works and
what doesn't, for each client.

Lessons only change *recommendations*. They never loosen safety limits by
themselves: any suggested limit change is a proposal the human must approve and
apply to the client profile.

Storage: ADS_GODMODE_HOME/learning/<client>.jsonl, append-only, private.
"""

import json
import math
import time
import uuid
from datetime import date, timedelta
from typing import Dict, List, Optional

from . import paths

LOWER_IS_BETTER = {"cpl", "cpa", "cost_per_result", "cpm", "cpc", "frequency"}
HIGHER_IS_BETTER = {"ctr", "cvr", "results", "leads", "conversions", "roas", "value", "hook_rate", "hold_rate"}


def _file(client: str):
    d = paths.home() / "learning"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{client}.jsonl"


def _append(client: str, rec: Dict) -> Dict:
    with _file(client).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def records(client: str) -> List[Dict]:
    f = _file(client)
    if not f.exists():
        return []
    out = []
    for line in f.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def predict(client: str, platform: str, action: str, entities: List[str], metric: str,
            direction: str, baseline: float, baseline_n: int = 0, expected_pct: Optional[float] = None,
            read_after_days: int = 7, tags: Optional[List[str]] = None, ticket: Optional[str] = None,
            note: str = "", today: Optional[date] = None) -> Dict:
    metric = metric.lower()
    if metric not in LOWER_IS_BETTER | HIGHER_IS_BETTER:
        raise ValueError(f"unknown metric {metric!r}")
    if direction not in ("up", "down"):
        raise ValueError("direction must be up or down")
    today = today or date.today()
    return _append(client, {
        "type": "prediction", "id": "prd_" + uuid.uuid4().hex[:10], "ts": time.time(),
        "client": client, "platform": platform, "action": action, "entities": [str(e) for e in entities],
        "metric": metric, "direction": direction, "expected_pct": expected_pct,
        "baseline": float(baseline), "baseline_n": int(baseline_n), "tags": tags or [], "ticket": ticket,
        "created": today.isoformat(), "read_on": (today + timedelta(days=read_after_days)).isoformat(),
        "note": note})


def _outcomes(client: str) -> Dict[str, Dict]:
    return {r["prediction"]: r for r in records(client) if r.get("type") == "outcome"}


def predictions(client: str) -> List[Dict]:
    return [r for r in records(client) if r.get("type") == "prediction"]


def due(client: str, today: Optional[date] = None) -> List[Dict]:
    today = (today or date.today()).isoformat()
    done = _outcomes(client)
    return [p for p in predictions(client) if p["id"] not in done and p["read_on"] <= today]


def grade(pred: Dict, value: float, n: int) -> Dict:
    """worked / failed / inconclusive, with the reason."""
    base = pred["baseline"]
    if base == 0:
        return {"verdict": "inconclusive", "change_pct": None, "reason": "baseline is zero"}
    change = (value - base) / abs(base) * 100
    sample = min(n, pred.get("baseline_n") or n)
    noise = 100 / math.sqrt(sample) if sample > 0 else 100.0  # ~1 sd relative error on count-based metrics
    if sample < 10:
        return {"verdict": "inconclusive", "change_pct": round(change, 1),
                "reason": f"only {sample} results in the smaller window (need 10+)"}
    if abs(change) < noise:
        return {"verdict": "inconclusive", "change_pct": round(change, 1),
                "reason": f"change {change:+.1f}% is within noise (+/-{noise:.0f}% at n={sample})"}
    # "worked" = the metric moved the way the plan predicted, beyond noise. Pick the
    # metric and direction that express the goal (e.g. budget-up -> results up).
    worked = (change > 0) == (pred["direction"] == "up")
    return {"verdict": "worked" if worked else "failed", "change_pct": round(change, 1),
            "reason": f"{pred['metric']} moved {change:+.1f}% (noise +/-{noise:.0f}% at n={sample})"}


def record_outcome(client: str, prediction_id: str, value: float, n: int,
                   executed: Optional[bool] = True, note: str = "", source: str = "manual") -> Dict:
    pred = next((p for p in predictions(client) if p["id"] == prediction_id), None)
    if not pred:
        raise ValueError(f"no prediction {prediction_id} for {client}")
    if executed is False:
        g = {"verdict": "not_executed", "change_pct": None, "reason": "change was never applied"}
    else:
        g = grade(pred, value, n)
    return _append(client, {"type": "outcome", "prediction": prediction_id, "ts": time.time(),
                            "value": value, "n": n, "source": source, "note": note, **g})


def auto_read(client: str, snapshot: Dict, ticket_lookup=None, today: Optional[date] = None) -> List[Dict]:
    """Record outcomes for due predictions using a fresh snapshot. Returns new outcomes."""
    from . import snapshots as snaps
    out = []
    for p in due(client, today):
        executed = None
        if p.get("ticket") and ticket_lookup:
            t = ticket_lookup(p["ticket"])
            executed = bool(t and t.get("consumed"))
            if executed is False:
                out.append(record_outcome(client, p["id"], 0, 0, executed=False, source="snapshot"))
                continue
        vals = [snaps.entity_metric(snapshot, p["platform"], e, p["metric"]) for e in p["entities"] or [""]]
        vals = [v for v in vals if v]
        if not vals:
            continue  # metric not in snapshot; stays due for a manual read
        n = sum(v["n"] for v in vals)
        value = sum(v["value"] for v in vals) / len(vals)
        out.append(record_outcome(client, p["id"], value, n, source=f"snapshot {snapshot.get('captured_at')}"))
    return out


def add_lesson(client: str, tags: List[str], text: str, verdict: str, evidence: str = "") -> Dict:
    """Manual lesson, e.g. from a creative test readout."""
    if verdict not in ("worked", "failed", "inconclusive"):
        raise ValueError("verdict must be worked, failed or inconclusive")
    return _append(client, {"type": "lesson", "ts": time.time(), "tags": tags, "text": text,
                            "verdict": verdict, "evidence": evidence})


def _confidence(n: int) -> str:
    return "HIGH" if n >= 6 else "MODERATE" if n >= 3 else "EXPERIMENT"


def summary(client: str) -> Dict:
    """What works / what doesn't for one client, by tactic tag and action."""
    preds = {p["id"]: p for p in predictions(client)}
    stats: Dict[str, Dict] = {}

    def bump(key, verdict, change=None):
        s = stats.setdefault(key, {"tag": key, "worked": 0, "failed": 0, "inconclusive": 0, "changes": []})
        if verdict in s:
            s[verdict] += 1
        if change is not None:
            s["changes"].append(change)

    for r in records(client):
        if r.get("type") == "outcome" and r["prediction"] in preds and r["verdict"] != "not_executed":
            p = preds[r["prediction"]]
            for key in (p.get("tags") or []) + [f"action:{p['action']}"]:
                bump(key, r["verdict"], r.get("change_pct"))
        elif r.get("type") == "lesson":
            for key in r.get("tags") or []:
                bump(key, r["verdict"])

    works, doesnt, unclear = [], [], []
    for s in stats.values():
        decided = s["worked"] + s["failed"]
        s["avg_change_pct"] = round(sum(s["changes"]) / len(s["changes"]), 1) if s["changes"] else None
        del s["changes"]
        s["confidence"] = _confidence(decided)
        if decided and s["worked"] / decided >= 0.6:
            works.append(s)
        elif decided and s["failed"] / decided >= 0.6:
            doesnt.append(s)
        else:
            unclear.append(s)
    key = lambda s: -(s["worked"] + s["failed"])  # noqa: E731
    outcomes = [r for r in records(client) if r.get("type") == "outcome"]
    return {"client": client, "tested": len([o for o in outcomes if o["verdict"] != "not_executed"]),
            "works": sorted(works, key=key), "doesnt": sorted(doesnt, key=key),
            "unclear": sorted(unclear, key=key), "proposals": proposals(works, doesnt)}


def proposals(works: List[Dict], doesnt: List[Dict]) -> List[str]:
    """Human-approved suggestions derived from lessons. Never applied automatically."""
    out = []
    for s in works:
        if s["confidence"] != "EXPERIMENT":
            out.append(f"Keep using '{s['tag']}' ({s['worked']}/{s['worked'] + s['failed']} worked, "
                       f"{s['confidence']}). Prefer it in the next plan for this client.")
    for s in doesnt:
        if s["confidence"] != "EXPERIMENT":
            out.append(f"Stop or rethink '{s['tag']}' ({s['failed']}/{s['worked'] + s['failed']} failed, "
                       f"{s['confidence']}). Do not repeat it without a new hypothesis.")
    return out


def portfolio_patterns(clients: List[str]) -> List[Dict]:
    """Tactic-level stats across clients (no client data mixed). Label: PORTFOLIO HEURISTIC."""
    agg: Dict[str, Dict] = {}
    for c in clients:
        for bucket in ("works", "doesnt", "unclear"):
            for s in summary(c)[bucket]:
                a = agg.setdefault(s["tag"], {"tag": s["tag"], "clients": 0, "worked": 0, "failed": 0})
                a["clients"] += 1
                a["worked"] += s["worked"]
                a["failed"] += s["failed"]
    rows = [a for a in agg.values() if a["clients"] >= 2]
    for a in rows:
        d = a["worked"] + a["failed"]
        a["win_rate"] = round(a["worked"] / d, 2) if d else None
        a["label"] = "PORTFOLIO HEURISTIC"
    return sorted(rows, key=lambda a: -(a["worked"] + a["failed"]))
