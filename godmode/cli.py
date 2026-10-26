"""adsgm - command line for the Ads God Mode safety core.

Claude runs these through Bash; every command prints JSON.

  adsgm doctor                       environment and profile health
  adsgm clients list|show|validate|add|new|check-isolation
  adsgm resolve "D-Hauss"            name -> exactly one client profile
  adsgm use "D-Hauss"                set the active client for writes
  adsgm whoami                       show the active client
  adsgm plan <action> ...            verify + price a write, create a ticket
  adsgm tickets                      open tickets for the active client
  adsgm route <platform> <op>        which connector/tool serves an operation
  adsgm classify <tool_name>         how the gate sees a tool call
  adsgm quality ...                  grade evidence behind a recommendation
  adsgm anomaly --input rows.json    flag runaway spend
  adsgm google apply --plan f.json [--ticket T] [--execute]
  adsgm log [-n 20]                  recent audit records
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from . import actions as A
from . import anomaly, audit, autopilot, budget_plan, creative, evidence, gate, learning, niche, paths, policy, portfolio, profiles, schedule, session, snapshots, tickets
from .budget import BudgetChange, format_summary
from .classify import classify

ROOT = Path(__file__).resolve().parent.parent


def out(obj, code: int = 0) -> int:
    print(json.dumps(obj, indent=2, default=str))
    return code


def fail(msg: str, code: int = 1) -> int:
    return out({"ok": False, "error": msg}, code)


def _adapters():
    sys.path.insert(0, str(ROOT))
    from connectors.analytics import AnalyticsAdapter
    from connectors.google import GoogleAdsAdapter
    from connectors.meta import MetaAdsAdapter
    return {"meta": MetaAdsAdapter(), "google": GoogleAdsAdapter(), "analytics": AnalyticsAdapter()}


def _profile_summary(p: profiles.Profile):
    return {"slug": p.slug, "name": p.name, "mode": p.mode,
            "meta_accounts": p.account_ids("meta") if p.platform_enabled("meta") else [],
            "google_customers": p.account_ids("google") if p.platform_enabled("google") else []}


# ---------------------------------------------------------------- commands

def cmd_doctor(a) -> int:
    checks = {"python": sys.version.split()[0], "home": str(paths.home())}
    checks["python_ok"] = sys.version_info >= (3, 9)
    env = {k: bool(os.environ.get(k)) for k in (
        "META_ACCESS_TOKEN", "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET", "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_LOGIN_CUSTOMER_ID")}
    checks["env_present"] = env  # presence only; values are never printed
    try:
        import google.ads.googleads  # noqa: F401
        checks["google_ads_client"] = True
    except ImportError:
        checks["google_ads_client"] = False
    try:
        profs = profiles.list_all()
        checks["clients"] = [p.slug for p in profs]
        checks["isolation_problems"] = profiles.isolation_problems(profs)
    except profiles.ProfileError as exc:
        checks["clients_error"] = str(exc)
    checks["active_client"] = session.get_active()
    checks["unattended_mode"] = session.unattended()
    checks["full_auto_enabled"] = policy.full_auto_enabled()
    return out(checks)


def cmd_clients(a) -> int:
    if a.sub == "list":
        return out([_profile_summary(p) for p in profiles.list_all()])
    if a.sub == "show":
        return out(profiles.load(profiles.resolve(a.name).slug).data)
    if a.sub == "validate":
        data = json.loads(Path(a.name).read_text(encoding="utf-8"))
        errors = profiles.validate(data)
        return out({"ok": not errors, "errors": errors}, 0 if not errors else 1)
    if a.sub == "add":
        src = Path(a.name)
        data = json.loads(src.read_text(encoding="utf-8"))
        errors = profiles.validate(data)
        if errors:
            return out({"ok": False, "errors": errors}, 1)
        paths.ensure_dirs()
        existing = [p for p in profiles.list_all() if p.slug != data["slug"]]
        candidate = profiles.Profile(data["slug"], data)
        problems = profiles.isolation_problems(existing + [candidate])
        if problems:
            return out({"ok": False, "errors": problems}, 1)
        dest = paths.clients_dir() / f"{data['slug']}.json"
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        audit.log("client_saved", client=data["slug"])
        return out({"ok": True, "saved": str(dest)})
    if a.sub == "new":
        paths.ensure_dirs()
        dest = paths.clients_dir() / f"{a.name}.json"
        if dest.exists():
            return fail(f"{dest} already exists")
        tpl = json.loads((ROOT / "templates" / "client-profile.json").read_text(encoding="utf-8"))
        tpl["slug"] = a.name
        dest.write_text(json.dumps(tpl, indent=2), encoding="utf-8")
        return out({"ok": True, "created": str(dest), "next": "fill it in, then adsgm clients validate"})
    if a.sub == "check-isolation":
        problems = profiles.isolation_problems()
        return out({"ok": not problems, "problems": problems}, 0 if not problems else 1)
    return fail("unknown clients subcommand")


def cmd_resolve(a) -> int:
    return out({"ok": True, **_profile_summary(profiles.resolve(a.query))})


def cmd_use(a) -> int:
    p = profiles.resolve(a.query)
    session.set_active(p.slug)
    audit.log("client_selected", client=p.slug)
    return out({"ok": True, "active": _profile_summary(p),
                "reminder": "Writes are now checked against this client only. Confirm the accounts above."})


def cmd_whoami(a) -> int:
    active = session.get_active()
    if not active:
        return out({"active": None})
    return out({"active": _profile_summary(profiles.load(active))})


def cmd_plan(a) -> int:
    active = session.get_active()
    if not active:
        return fail("no active client; run adsgm use <client>")
    profile = profiles.load(active)
    platform = a.platform
    details = {}
    action = a.action
    entities = list(a.entity or [])

    if a.google_plan:
        sys.path.insert(0, str(ROOT))
        from connectors.google import writer
        plan = json.loads(Path(a.google_plan).read_text(encoding="utf-8"))
        _, cid, specs = writer.check_plan(plan)
        platform, account = "google", cid
        action = writer.plan_action(specs)
        entities = writer.plan_entities(specs)
        details["google_plan"] = str(Path(a.google_plan).resolve())
    else:
        if not a.account:
            return fail("--account is required")
        try:
            account = profiles.normalize_account_id(platform, a.account)
        except profiles.ProfileError as exc:
            return fail(str(exc))
    if not profile.owns(platform, account):
        owners = profiles.owner_of(platform, account)
        return fail(f"WRONG ACCOUNT: {account} is not a {platform} account of {active}"
                    + (f"; it belongs to {', '.join(owners)}" if owners else ""), 2)
    if action not in A.ALL:
        return fail(f"unknown action {action!r}; one of {sorted(A.ALL - A.NON_MUTATING)}")
    if action not in (A.CREATE,) and not entities:
        return fail("--entity is required (campaign / ad set / ad id) for this action")
    if action == A.CREATIVE_SWAP:
        if not a.replaces or len(entities) != 1:
            return fail("creative_swap needs exactly one --entity (the NEW ad) and --replaces (the ad it replaces)")
        details["swap"] = {"new": str(entities[0]), "old": str(a.replaces), "adset": a.adset}
        entities = [str(entities[0]), str(a.replaces)]

    change = None
    hours = None
    if entities:
        hs = [h for h in (tickets.hours_since_last_change(active, platform, e) for e in entities) if h is not None]
        hours = min(hs) if hs else None
    if action == A.BUDGET:
        if a.current is None or a.proposed is None:
            return fail("budget plans need --current and --proposed")
        change = BudgetChange(current=a.current, proposed=a.proposed, currency=a.currency, period=a.period,
                              reason=a.reason or "", evidence=a.evidence or "", expected_effect=a.expected or "",
                              risks=a.risks or "", confidence=a.confidence, spend_in_window=a.spend,
                              conversions_in_window=a.conversions)
    decision = policy.evaluate(profile, action, budget_change=change, entity_count=max(1, len(entities)),
                               negative_keyword_count=a.negatives or 0, bid_change_pct=a.bid_pct,
                               hours_since_last_change=hours if action != A.CREATIVE_SWAP else None,
                               account_daily_budget=a.account_daily_budget,
                               swaps_last_7d=tickets.count_changes(active, A.CREATIVE_SWAP, 7))
    if change is not None:
        from .budget import check_limits
        change.limit_violations = check_limits(change, profile.guarded_limits,
                                               profile.approval.get("high_budget_daily_threshold"), hours)
        details["budget"] = change.to_dict()
        summary = format_summary(change, a.entity_label or ", ".join(entities))
    else:
        summary = (f"{action.upper()} on {platform} {account}: {a.entity_label or ', '.join(entities) or '(account)'}"
                   + (f"\nREASON: {a.reason}" if a.reason else "")
                   + (f"\nDATA: {a.evidence}" if a.evidence else "")
                   + (f"\nRISKS: {a.risks}" if a.risks else ""))
    header = f"CLIENT: {profile.name} ({active}) | PLATFORM: {platform} | ACCOUNT: {account}"
    summary = header + "\n" + summary
    if decision.verdict == policy.BLOCKED:
        audit.log("plan_blocked", client=active, platform=platform, action=action, reasons=decision.reasons)
        return out({"ok": False, "verdict": "blocked", "reasons": decision.reasons, "summary": summary}, 3)
    t = tickets.create(active, platform, account, action, entities, decision.to_dict(), summary, details)
    audit.log("plan_created", client=active, platform=platform, action=action, ticket=t["id"],
              verdict=decision.verdict)
    prediction = None
    if a.predict_metric:
        if a.baseline is None or a.predict_direction not in ("up", "down"):
            return fail("predictions need --predict-direction up|down and --baseline")
        prediction = learning.predict(active, platform, action, entities, a.predict_metric, a.predict_direction,
                                      a.baseline, a.baseline_n or 0, a.predict_pct, a.read_after,
                                      [x.strip() for x in (a.tags or "").split(",") if x.strip()], t["id"],
                                      a.reason or "")["id"]
    return out({"ok": True, "ticket": t["id"], "prediction": prediction,
                "verdict": decision.verdict, "reasons": decision.reasons,
                "summary": summary, "expires_in_minutes": 30,
                "next": ("Show the summary to the user. " +
                         ("The write will prompt for approval." if decision.verdict == policy.APPROVAL
                          else "Within policy; the write will run without a prompt."))})


def cmd_tickets(a) -> int:
    return out(tickets.list_open(None if a.all else session.get_active()))


def cmd_route(a) -> int:
    adapters = _adapters()
    from connectors.base import CapabilityNotSupported
    if a.platform not in adapters:
        return fail(f"platform must be one of {sorted(adapters)}")
    avail = [x.strip() for x in a.available.split(",")] if a.available else None
    try:
        return out(adapters[a.platform].route(a.op, avail, a.prefer).to_dict())
    except CapabilityNotSupported as exc:
        return fail(str(exc), 4)


def cmd_capabilities(a) -> int:
    return out({k: v.capability_matrix() for k, v in _adapters().items()})


def cmd_classify(a) -> int:
    tool_input = json.loads(a.input) if a.input else {}
    c = classify(a.tool_name, tool_input)
    if c is None:
        return out({"ads_tool": False})
    from .extract import extract
    ex = extract(tool_input)
    return out({"ads_tool": True, "platform": c.platform, "family": c.family, "action": c.action,
                "refined_action": gate.refine_action(c, ex), "accounts": ex.account_ids,
                "entities": ex.entity_ids})


def cmd_quality(a) -> int:
    q = evidence.assess(a.conversions, a.spend, a.days, a.target_cpa,
                        None if a.tracking is None else a.tracking == "ok",
                        a.in_learning, a.days_since_change, a.lag_days, "", a.seasonal)
    return out(q.to_dict())


def cmd_anomaly(a) -> int:
    rows = json.loads(Path(a.input).read_text(encoding="utf-8"))
    flags = anomaly.detect(rows, a.z, a.pace, a.min_spend)
    return out({"flagged": len(flags), "rows": flags})


def cmd_google(a) -> int:
    sys.path.insert(0, str(ROOT))
    from connectors.google import writer
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    try:
        report = writer.apply(plan, execute=a.execute, ticket_id=a.ticket)
    except writer.PlanError as exc:
        return fail(str(exc), 2)
    audit.log("google_apply", **report)
    return out({"ok": True, **report})


def cmd_log(a) -> int:
    return out(audit.tail(a.n))


def cmd_snapshot(a) -> int:
    if a.sub == "save":
        snap = json.loads(Path(a.file).read_text(encoding="utf-8"))
        try:
            path = snapshots.save(snap)
        except snapshots.SnapshotError as exc:
            return fail(str(exc), 2)
        return out({"ok": True, "saved": path})
    client = profiles.resolve(a.client).slug if a.client else None
    if not client:
        return fail("--client is required")
    return out([{"captured_at": s.get("captured_at"), "platforms": sorted((s.get("platforms") or {}).keys())}
                for s in snapshots.history(client)])


def _report_dir():
    from datetime import date
    d = paths.home() / "reports" / date.today().isoformat()
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_sweep(a) -> int:
    clients = [profiles.resolve(c.strip()).slug for c in a.clients.split(",")] if a.clients else None
    rep = portfolio.sweep(clients)
    d = _report_dir()
    md, page = d / "portfolio.md", d / "portfolio.html"
    md.write_text(portfolio.to_markdown(rep), encoding="utf-8")
    page.write_text(portfolio.to_html(rep), encoding="utf-8")
    (d / "portfolio.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
    audit.log("sweep", totals=rep["totals"])
    slim = [{k: r.get(k) for k in ("client", "status", "score", "spend", "results", "cpl", "target_cpl", "pacing_pct")}
            | {"top_issues": [f"[{i['severity']}] {i['title']}" for i in r["issues"][:3]]} for r in rep["clients"]]
    return out({"ok": True, "totals": rep["totals"], "clients": slim, "markdown": str(md), "dashboard": str(page)})


def cmd_learn(a) -> int:
    client = profiles.resolve(a.client).slug if a.client else None
    if a.sub == "summary":
        if a.niche:
            return out(niche.niche_patterns(a.niche))
        if a.portfolio:
            return out({"patterns": learning.portfolio_patterns([p.slug for p in profiles.list_all()])})
        if not client:
            return fail("--client or --portfolio is required")
        return out(learning.summary(client))
    if a.sub == "due":
        targets = [client] if client else [p.slug for p in profiles.list_all()]
        return out({c: learning.due(c) for c in targets if learning.due(c)})
    if not client:
        return fail("--client is required")
    if a.sub == "record":
        rec = learning.record_outcome(client, a.prediction, a.value or 0, a.n or 0,
                                      executed=not a.not_executed, note=a.note or "")
        return out(rec)
    if a.sub == "auto":
        snap = snapshots.latest(client)
        if not snap:
            return fail(f"no snapshot for {client}; save one first")
        return out({"recorded": learning.auto_read(client, snap, tickets.get)})
    if a.sub == "lesson":
        tags = [x.strip() for x in (a.tags or "").split(",") if x.strip()]
        return out(learning.add_lesson(client, tags, a.text or "", a.verdict, a.note or ""))
    return fail("unknown learn subcommand")


def cmd_creative(a) -> int:
    brief = json.loads(Path(a.brief).read_text(encoding="utf-8"))
    try:
        m = creative.render_brief(brief, png=not a.no_png, out_dir=a.out)
    except (creative.CreativeError, profiles.ProfileError) as exc:
        return fail(str(exc), 2)
    audit.log("creative_render", client=m["client"], concept=m.get("concept"), dir=m["dir"])
    return out({"ok": True, "dir": m["dir"], "contact_sheet": str(Path(m["dir"]) / "index.html"),
                "png": bool(m["png_renderer"]),
                "variants": [{"id": v["id"], "errors": v["errors"], "warnings": v["warnings"],
                              "files": len(v["files"])} for v in m["variants"]]})


def cmd_budget_plan(a) -> int:
    over = dict(monthly=a.monthly, daily=a.daily, target_cpl=a.target_cpl, job_value=a.job_value,
                close_rate_pct=a.close_rate, margin_pct=a.margin, lead_value=a.lead_value,
                google_cpc=a.google_cpc, goal_results_per_month=a.goal, hard_monthly_cap=a.hard_cap or None,
                flight_days=a.flight_days,
                platforms=[x.strip() for x in a.platforms.split(",")] if a.platforms else None)
    if a.client:
        p = profiles.load(profiles.resolve(a.client).slug)
        inputs = budget_plan.from_profile(p, **over)
    else:
        inputs = budget_plan.BudgetInputs(**{k: v for k, v in over.items() if v is not None})
    try:
        result = budget_plan.plan(inputs)
    except ValueError as exc:
        return fail(str(exc))
    if a.save:
        if not a.client:
            return fail("--save needs --client")
        path = paths.clients_dir() / f"{p.slug}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        econ = data.setdefault("economics", {})
        econ["monthly_budget"] = result["monthly"]
        econ["budget_plan"] = {"split": result["split"], "budget_type": result["budget_type"],
                               "platforms": result["platforms"], "saved": __import__("time").strftime("%Y-%m-%d")}
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        audit.log("budget_plan_saved", client=p.slug, monthly=result["monthly"])
    return out({**result, "text": budget_plan.to_text(result),
                "note": "Recommendation only. Budgets change in the ad accounts only through adsgm plan + approval."})


def cmd_autopilot(a) -> int:
    p = profiles.resolve(a.client)
    if a.sub in ("on", "off"):
        acts = [x.strip() for x in a.actions.split(",")] if a.actions else None
        try:
            state = autopilot.set_state(p.slug, a.sub == "on", a.cap, acts)
        except ValueError as exc:
            return fail(str(exc))
        audit.log("autopilot_" + a.sub, client=p.slug, cap=state.get("daily_spend_cap"), actions=state.get("actions"))
        return out({"ok": True, "client": p.slug, "autopilot": state})
    prof = profiles.load(p.slug)
    if a.sub == "status":
        return out({"client": p.slug, "active": autopilot.active(prof), "settings": autopilot.settings(prof),
                    "swaps_last_7d": tickets.count_changes(p.slug, A.CREATIVE_SWAP, 7)})
    snap = snapshots.latest(p.slug)
    if not snap:
        return fail("no snapshot for this client yet; run a sweep first")
    return out(autopilot.candidates(prof, snap))


def cmd_niche(a) -> int:
    if a.sub == "list":
        return out(niche.list_all())
    if a.sub == "save":
        try:
            return out({"ok": True, "saved": niche.save(json.loads(Path(a.file).read_text(encoding="utf-8")))})
        except niche.NicheError as exc:
            return fail(str(exc), 2)
    if not a.name:
        return fail("niche name required")
    if a.sub == "patterns":
        return out(niche.niche_patterns(a.name))
    try:
        pb = niche.load(a.name)
    except niche.NicheError as exc:
        return fail(str(exc), 2)
    return out({**pb, "stale": niche.stale(pb), "clients": niche.clients_in(a.name)})


def cmd_unattended(a) -> int:
    if a.sub == "on":
        session.set_unattended(a.hours)
        audit.log("unattended_on", hours=a.hours)
    elif a.sub == "off":
        session.clear_unattended()
        audit.log("unattended_off")
    return out({"unattended": session.unattended()})


def cmd_schedule(a) -> int:
    osn = a.os or ("windows" if os.name == "nt" else "posix")
    return out(schedule.plan(osn, write=a.write))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="adsgm", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)

    sp.add_parser("doctor").set_defaults(fn=cmd_doctor)

    c = sp.add_parser("clients")
    c.add_argument("sub", choices=["list", "show", "validate", "add", "new", "check-isolation"])
    c.add_argument("name", nargs="?", default="")
    c.set_defaults(fn=cmd_clients)

    r = sp.add_parser("resolve"); r.add_argument("query"); r.set_defaults(fn=cmd_resolve)
    u = sp.add_parser("use"); u.add_argument("query"); u.set_defaults(fn=cmd_use)
    sp.add_parser("whoami").set_defaults(fn=cmd_whoami)

    p = sp.add_parser("plan")
    p.add_argument("action")
    p.add_argument("--platform", choices=["meta", "google"], default="meta")
    p.add_argument("--account")
    p.add_argument("--entity", action="append", help="repeat for several entities")
    p.add_argument("--entity-label")
    p.add_argument("--current", type=float)
    p.add_argument("--proposed", type=float)
    p.add_argument("--currency", default="USD")
    p.add_argument("--period", default="daily", choices=["daily", "lifetime"])
    p.add_argument("--reason"); p.add_argument("--evidence"); p.add_argument("--expected"); p.add_argument("--risks")
    p.add_argument("--confidence", default="EXPERIMENT", choices=["HIGH", "MODERATE", "EXPERIMENT"])
    p.add_argument("--spend", type=float, help="spend in the evaluation window")
    p.add_argument("--conversions", type=int, help="conversions in the evaluation window")
    p.add_argument("--negatives", type=int)
    p.add_argument("--bid-pct", type=float)
    p.add_argument("--google-plan", help="derive action/entities from a Google writer plan file")
    p.add_argument("--replaces", help="creative_swap: the ad id being replaced (paused by the swap)")
    p.add_argument("--adset", help="creative_swap: the ad set both ads live in")
    p.add_argument("--account-daily-budget", type=float, help="current total daily budget of the account (autopilot cap check)")
    p.add_argument("--predict-metric", help="learning loop: metric expected to move (cpl, results, ctr, roas...)")
    p.add_argument("--predict-direction", choices=["up", "down"])
    p.add_argument("--predict-pct", type=float, help="expected change in percent (optional)")
    p.add_argument("--baseline", type=float, help="metric value now")
    p.add_argument("--baseline-n", type=int, help="results behind the baseline (sample size)")
    p.add_argument("--read-after", type=int, default=7, help="days until the outcome is judged")
    p.add_argument("--tags", help="comma tactic tags, e.g. budget-up,ugc-hook")
    p.set_defaults(fn=cmd_plan)

    t = sp.add_parser("tickets"); t.add_argument("--all", action="store_true"); t.set_defaults(fn=cmd_tickets)

    ro = sp.add_parser("route")
    ro.add_argument("platform"); ro.add_argument("op")
    ro.add_argument("--available", help="comma list of MCP server names or backend keys in this session")
    ro.add_argument("--prefer")
    ro.set_defaults(fn=cmd_route)
    sp.add_parser("capabilities").set_defaults(fn=cmd_capabilities)

    cl = sp.add_parser("classify"); cl.add_argument("tool_name"); cl.add_argument("--input"); cl.set_defaults(fn=cmd_classify)

    q = sp.add_parser("quality")
    q.add_argument("--conversions", type=int, default=0)
    q.add_argument("--spend", type=float)
    q.add_argument("--days", type=int, default=7)
    q.add_argument("--target-cpa", type=float)
    q.add_argument("--tracking", choices=["ok", "broken"])
    q.add_argument("--in-learning", action="store_true")
    q.add_argument("--days-since-change", type=float)
    q.add_argument("--lag-days", type=float, default=0)
    q.add_argument("--seasonal", action="store_true")
    q.set_defaults(fn=cmd_quality)

    an = sp.add_parser("anomaly")
    an.add_argument("--input", required=True)
    an.add_argument("--z", type=float, default=3.0)
    an.add_argument("--pace", type=float, default=1.5)
    an.add_argument("--min-spend", type=float, default=20.0)
    an.set_defaults(fn=cmd_anomaly)

    g = sp.add_parser("google")
    g.add_argument("sub", choices=["apply"])
    g.add_argument("--plan", required=True)
    g.add_argument("--ticket")
    g.add_argument("--execute", action="store_true", help="apply for real (default: validate_only)")
    g.set_defaults(fn=cmd_google)

    lg = sp.add_parser("log"); lg.add_argument("-n", type=int, default=20); lg.set_defaults(fn=cmd_log)

    sn = sp.add_parser("snapshot")
    sn.add_argument("sub", choices=["save", "list"])
    sn.add_argument("--file"); sn.add_argument("--client")
    sn.set_defaults(fn=cmd_snapshot)

    sw = sp.add_parser("sweep")
    sw.add_argument("--clients", help="comma list; default all clients")
    sw.set_defaults(fn=cmd_sweep)

    le = sp.add_parser("learn")
    le.add_argument("sub", choices=["summary", "due", "record", "auto", "lesson"])
    le.add_argument("--client"); le.add_argument("--portfolio", action="store_true"); le.add_argument("--niche")
    le.add_argument("--prediction"); le.add_argument("--value", type=float); le.add_argument("--n", type=int)
    le.add_argument("--not-executed", action="store_true")
    le.add_argument("--tags"); le.add_argument("--text"); le.add_argument("--note")
    le.add_argument("--verdict", choices=["worked", "failed", "inconclusive"])
    le.set_defaults(fn=cmd_learn)

    cr = sp.add_parser("creative")
    cr.add_argument("sub", choices=["render"])
    cr.add_argument("--brief", required=True); cr.add_argument("--out"); cr.add_argument("--no-png", action="store_true")
    cr.set_defaults(fn=cmd_creative)

    bp = sp.add_parser("budget-plan")
    bp.add_argument("--client"); bp.add_argument("--monthly", type=float); bp.add_argument("--daily", type=float)
    bp.add_argument("--target-cpl", type=float); bp.add_argument("--job-value", type=float)
    bp.add_argument("--close-rate", type=float, help="percent of leads that become sales")
    bp.add_argument("--margin", type=float, help="gross margin percent"); bp.add_argument("--lead-value", type=float)
    bp.add_argument("--platforms", help="meta,google"); bp.add_argument("--google-cpc", type=float)
    bp.add_argument("--goal", type=int, help="leads wanted per month")
    bp.add_argument("--hard-cap", action="store_true", help="never exceed the monthly amount")
    bp.add_argument("--flight-days", type=int, help="fixed-length campaign")
    bp.add_argument("--save", action="store_true", help="store the plan in the client profile")
    bp.set_defaults(fn=cmd_budget_plan)

    ap_ = sp.add_parser("autopilot")
    ap_.add_argument("sub", choices=["on", "off", "status", "candidates"])
    ap_.add_argument("--client", required=True); ap_.add_argument("--cap", type=float, help="max total daily budget")
    ap_.add_argument("--actions", help="comma: pause_losers,fix_and_relaunch,google_negatives")
    ap_.set_defaults(fn=cmd_autopilot)

    ni = sp.add_parser("niche")
    ni.add_argument("sub", choices=["list", "show", "save", "patterns"])
    ni.add_argument("name", nargs="?"); ni.add_argument("--file")
    ni.set_defaults(fn=cmd_niche)

    un = sp.add_parser("unattended")
    un.add_argument("sub", choices=["on", "off", "status"])
    un.add_argument("--hours", type=float, default=3.0)
    un.set_defaults(fn=cmd_unattended)

    sc = sp.add_parser("schedule")
    sc.add_argument("sub", choices=["plan"])
    sc.add_argument("--os", choices=["windows", "posix"])
    sc.add_argument("--write", action="store_true", help="write the wrapper scripts to ~/.ads-godmode/jobs/")
    sc.set_defaults(fn=cmd_schedule)
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except profiles.ProfileError as exc:
        return fail(str(exc), 2)


if __name__ == "__main__":
    sys.exit(main())
