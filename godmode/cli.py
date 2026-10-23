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
from . import anomaly, audit, evidence, gate, paths, policy, profiles, session, tickets
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
        "META_ACCESS_TOKEN", "GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID",
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
                               hours_since_last_change=hours)
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
    return out({"ok": True, "ticket": t["id"], "verdict": decision.verdict, "reasons": decision.reasons,
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
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except profiles.ProfileError as exc:
        return fail(str(exc), 2)


if __name__ == "__main__":
    sys.exit(main())
