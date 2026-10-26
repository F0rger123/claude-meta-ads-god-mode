"""All-clients sweep: rank every client by what needs attention.

Input: the latest snapshot per client (godmode/snapshots.py) plus each
client's profile targets. Output: one row per client with a RED / AMBER /
GREEN status, the issues found (severity, evidence, recommended action) and a
priority score. Read-only: a sweep never changes anything.
"""

import calendar
import html
from datetime import date, datetime
from typing import Dict, List, Optional

from . import anomaly, learning, profiles, snapshots

SEV_POINTS = {"CRITICAL": 40, "HIGH": 20, "MEDIUM": 8, "LOW": 2, "OPPORTUNITY": 1}


def _issue(sev, platform, title, evidence, action, approval=True):
    return {"severity": sev, "platform": platform, "title": title, "evidence": evidence,
            "action": action, "approval_required": approval}


def _pct(a: float, b: float) -> Optional[float]:
    return None if not b else round((a - b) / b * 100, 1)


def _days(d: str) -> Optional[date]:
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def review_client(profile: profiles.Profile, snap: Optional[Dict], today: Optional[date] = None) -> Dict:
    today = today or date.today()
    econ = profile.data.get("economics", {})
    target_cpl = econ.get("desired_cpl") or econ.get("desired_cpa")
    monthly = econ.get("monthly_budget")
    issues: List[Dict] = []
    row = {"client": profile.slug, "name": profile.name, "mode": profile.mode, "issues": issues}

    if not snap:
        issues.append(_issue("HIGH", "-", "No data yet", "no snapshot saved for this client",
                             "Run a sweep for this client so its numbers are captured.", False))
        return _finish(row)

    captured = _days(snap.get("captured_at"))
    row["captured_at"] = snap.get("captured_at")
    if captured and (today - captured).days > 8:
        issues.append(_issue("MEDIUM", "-", "Stale data", f"last snapshot {snap['captured_at']}",
                             "Refresh this client's numbers.", False))

    total_spend = total_results = mtd = 0.0
    prev_spend = prev_results = 0.0
    for name, p in (snap.get("platforms") or {}).items():
        spend, results = float(p.get("spend") or 0), float(p.get("results") or 0)
        total_spend += spend
        total_results += results
        mtd += float(p.get("month_to_date_spend") or 0)
        prev = p.get("previous") or {}
        prev_spend += float(prev.get("spend") or 0)
        prev_results += float(prev.get("results") or 0)

        if p.get("tracking_ok") is False:
            issues.append(_issue("CRITICAL", name, "Conversion tracking broken or unverified",
                                 "tracking_ok=false in snapshot",
                                 "Run /ads:tracking before trusting any CPL; fix tracking first."))
        if spend > 0 and results == 0 and target_cpl and spend >= 2 * float(target_cpl):
            issues.append(_issue("HIGH", name, "Spending with no results",
                                 f"${spend:,.0f} spent, 0 results (target CPL ${target_cpl})",
                                 "Check tracking, then pause or fix the non-converting campaigns."))

        flagged = anomaly.detect([e for e in p.get("entities", []) if e.get("spend_today") is not None])
        for f in flagged[:3]:
            sev = "CRITICAL" if f["severity"] >= 3 else "HIGH"
            issues.append(_issue(sev, name, f"Unusual spend: {f.get('name') or f.get('id')}",
                                 "; ".join(f["reasons"]),
                                 f"/ads:emergency-stop {profile.slug} if not expected (pause only)."))

        ents = p.get("entities", [])
        limited = [e for e in ents if e.get("learning") == "limited"]
        if limited:
            issues.append(_issue("MEDIUM", name, f"{len(limited)} ad set(s) learning-limited",
                                 ", ".join(str(e.get("name") or e.get("id")) for e in limited[:3]),
                                 "Consolidate ad sets or raise budget toward ~50 results/week."))
        for e in ents:
            if target_cpl and e.get("learning") != "learning" and float(e.get("spend") or 0) >= 3 * float(target_cpl) \
                    and not e.get("results"):
                issues.append(_issue("HIGH", name, f"Zero-result spender: {e.get('name') or e.get('id')}",
                                     f"${float(e['spend']):,.0f} spent, 0 results, out of learning",
                                     "Plan a pause (adsgm plan pause) after checking tracking."))
            ctr, ctr_prev, freq = e.get("ctr"), e.get("ctr_prev"), e.get("frequency")
            if ctr and ctr_prev and freq and float(freq) >= 3 and float(ctr) < 0.8 * float(ctr_prev):
                issues.append(_issue("MEDIUM", name, f"Creative fatigue: {e.get('name') or e.get('id')}",
                                     f"frequency {freq}, CTR {ctr_prev}% -> {ctr}%",
                                     "Brief 2-3 new hooks (/ads:creative) and render graphics."))
        waste = p.get("search_term_waste")
        if waste and spend and waste / spend >= 0.1:
            issues.append(_issue("HIGH", name, "Search-term waste",
                                 f"${waste:,.0f} ({waste / spend * 100:.0f}% of spend) on irrelevant terms",
                                 "Run the search-term review and approve negatives."))
        lis = p.get("lost_is_budget")
        if lis and lis >= 20 and target_cpl and results and spend / results <= float(target_cpl):
            issues.append(_issue("OPPORTUNITY", name, "Budget-limited winner",
                                 f"{lis}% impression share lost to budget at CPL ${spend / results:,.0f}",
                                 "Consider a budget increase (adsgm plan budget)."))

    row.update(spend=round(total_spend, 2), results=total_results,
               cpl=round(total_spend / total_results, 2) if total_results else None,
               target_cpl=target_cpl,
               spend_change_pct=_pct(total_spend, prev_spend),
               results_change_pct=_pct(total_results, prev_results))
    qualified = (snap.get("crm") or {}).get("qualified_leads")
    if qualified is not None:
        row["qualified_leads"] = qualified

    tracking_broken = any(p.get("tracking_ok") is False for p in (snap.get("platforms") or {}).values())
    row["tracking_broken"] = tracking_broken
    if target_cpl and row["cpl"] and not tracking_broken:  # CPL verdicts mean nothing on broken tracking
        ratio = row["cpl"] / float(target_cpl)
        if ratio >= 1.5:
            issues.append(_issue("HIGH", "all", "CPL far above target",
                                 f"CPL ${row['cpl']:,.0f} vs target ${target_cpl}",
                                 "/ads:optimize - find the cause before cutting budget."))
        elif ratio >= 1.15:
            issues.append(_issue("MEDIUM", "all", "CPL above target",
                                 f"CPL ${row['cpl']:,.0f} vs target ${target_cpl}", "/ads:optimize"))
        elif ratio <= 0.8 and total_results >= 10:
            issues.append(_issue("OPPORTUNITY", "all", "Beating target CPL",
                                 f"CPL ${row['cpl']:,.0f} vs target ${target_cpl} on {int(total_results)} results",
                                 "Scaling candidate: /ads:budget."))

    if monthly and mtd:
        dim = calendar.monthrange(today.year, today.month)[1]
        expected = float(monthly) * today.day / dim
        pace = mtd / expected if expected else None
        row["pacing_pct"] = None if pace is None else round(pace * 100)
        if pace and pace >= 1.15:
            issues.append(_issue("HIGH", "all", "Overspending month budget",
                                 f"${mtd:,.0f} month-to-date vs ${expected:,.0f} expected ({pace * 100:.0f}%)",
                                 "/ads:budget to bring pacing back to plan."))
        elif pace and pace <= 0.75 and today.day >= 7:
            issues.append(_issue("MEDIUM", "all", "Underspending month budget",
                                 f"${mtd:,.0f} month-to-date vs ${expected:,.0f} expected ({pace * 100:.0f}%)",
                                 "Check delivery limits / learning; consider reallocating.", True))

    lessons = learning.summary(profile.slug)
    row["learning"] = {"tested": lessons["tested"], "works": len(lessons["works"]),
                       "doesnt": len(lessons["doesnt"]), "due_reads": len(learning.due(profile.slug))}
    if row["learning"]["due_reads"]:
        issues.append(_issue("LOW", "-", f"{row['learning']['due_reads']} change(s) ready to judge",
                             "predictions past their read date",
                             "Run /ads:learn so the outcome is recorded.", False))
    return _finish(row)


def _finish(row: Dict) -> Dict:
    issues = row["issues"]
    issues.sort(key=lambda i: -SEV_POINTS[i["severity"]])
    row["score"] = sum(SEV_POINTS[i["severity"]] for i in issues if i["severity"] != "OPPORTUNITY")
    if any(i["severity"] == "CRITICAL" for i in issues) or row["score"] >= 40:
        row["status"] = "RED"
    elif row["score"] >= 8:
        row["status"] = "AMBER"
    else:
        row["status"] = "GREEN"
    return row


def sweep(clients: Optional[List[str]] = None, today: Optional[date] = None) -> Dict:
    rows = []
    for p in profiles.list_all():
        if clients and p.slug not in clients:
            continue
        rows.append(review_client(p, snapshots.latest(p.slug), today))
    order = {"RED": 0, "AMBER": 1, "GREEN": 2}
    rows.sort(key=lambda r: (order[r["status"]], -r["score"]))
    totals = {"clients": len(rows), "red": sum(r["status"] == "RED" for r in rows),
              "amber": sum(r["status"] == "AMBER" for r in rows),
              "green": sum(r["status"] == "GREEN" for r in rows),
              "spend": round(sum(r.get("spend") or 0 for r in rows), 2),
              "results": sum(r.get("results") or 0 for r in rows)}
    return {"generated": (today or date.today()).isoformat(), "totals": totals, "clients": rows}


def to_markdown(rep: Dict) -> str:
    t = rep["totals"]
    out = [f"# Portfolio sweep - {rep['generated']}", "",
           f"**{t['clients']} clients** · 🔴 {t['red']} · 🟠 {t['amber']} · 🟢 {t['green']} · "
           f"spend ${t['spend']:,.0f} · results {t['results']:.0f}", "",
           "| | Client | Spend | Results | CPL (target) | Top issue | Next step |", "|---|---|---|---|---|---|---|"]
    dot = {"RED": "🔴", "AMBER": "🟠", "GREEN": "🟢"}
    for r in rep["clients"]:
        top = r["issues"][0] if r["issues"] else None
        cpl = "-" if not r.get("cpl") else f"${r['cpl']:,.0f}"
        tgt = f" (${r['target_cpl']})" if r.get("target_cpl") else ""
        out.append(f"| {dot[r['status']]} | {r['name']} | ${r.get('spend', 0) or 0:,.0f} | {r.get('results', 0) or 0:.0f} | "
                   f"{cpl}{tgt} | {top['title'] if top else 'nothing urgent'} | {top['action'] if top else '-'} |")
    out.append("")
    for r in rep["clients"]:
        if not r["issues"]:
            continue
        out += [f"## {dot[r['status']]} {r['name']}", ""]
        for i in r["issues"]:
            appr = "needs approval" if i["approval_required"] else "no approval needed"
            out.append(f"- **[{i['severity']}] {i['title']}** ({i['platform']}) - {i['evidence']}. "
                       f"_Next:_ {i['action']} ({appr})")
        lr = r.get("learning")
        if lr and lr["tested"]:
            out.append(f"- Learning: {lr['tested']} changes judged, {lr['works']} patterns that work, "
                       f"{lr['doesnt']} that don't. See `adsgm learn summary --client {r['client']}`.")
        out.append("")
    return "\n".join(out)


def to_html(rep: Dict) -> str:
    """Self-contained dashboard (no external assets) for opening locally."""
    e = html.escape
    t = rep["totals"]
    color = {"RED": "#dc2626", "AMBER": "#d97706", "GREEN": "#16a34a"}
    cards = []
    for r in rep["clients"]:
        items = "".join(f"<li><b>{e(i['severity'])}</b> {e(i['title'])} <span>{e(i['evidence'])}</span>"
                        f"<em>Next: {e(i['action'])}</em></li>" for i in r["issues"][:6]) or "<li>Nothing urgent</li>"
        cpl = "-" if not r.get("cpl") else f"${r['cpl']:,.0f}"
        cards.append(f"""<section class="card" style="border-top:4px solid {color[r['status']]}">
<h2>{e(r['name'])}<small>{e(r['status'])} · {e(r['mode'])}</small></h2>
<div class="kpis"><div><b>${(r.get('spend') or 0):,.0f}</b>spend</div><div><b>{(r.get('results') or 0):.0f}</b>results</div>
<div><b>{e(cpl)}</b>CPL{(' / $' + str(r['target_cpl'])) if r.get('target_cpl') else ''}</div>
<div><b>{e(str(r.get('pacing_pct', '-')))}%</b>pacing</div></div><ul>{items}</ul></section>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Portfolio sweep {e(rep['generated'])}</title><style>
:root{{--bg:#0b1020;--card:#121a33;--text:#e6ecff;--muted:#9fb0d9}}
@media (prefers-color-scheme: light){{:root{{--bg:#f5f7fb;--card:#fff;--text:#111827;--muted:#4b5563}}}}
body{{margin:0;font-family:'Segoe UI',Inter,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);padding:24px 16px}}
h1{{margin:0 0 4px}}.sum{{color:var(--muted);margin-bottom:20px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
.card{{background:var(--card);border-radius:12px;padding:16px}}h2{{margin:0 0 12px;font-size:18px;display:flex;justify-content:space-between;gap:8px}}
h2 small{{color:var(--muted);font-weight:500;font-size:12px}}.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}}
.kpis div{{font-size:11px;color:var(--muted)}}.kpis b{{display:block;font-size:17px;color:var(--text)}}
ul{{margin:0;padding-left:18px}}li{{margin:6px 0;font-size:13px}}li span{{display:block;color:var(--muted)}}li em{{display:block;font-style:normal;color:#60a5fa}}
</style></head><body><h1>Portfolio sweep</h1><div class="sum">{e(rep['generated'])} · {t['clients']} clients ·
{t['red']} red · {t['amber']} amber · {t['green']} green · ${t['spend']:,.0f} spend · {t['results']:.0f} results</div>
<div class="grid">{''.join(cards)}</div></body></html>"""
