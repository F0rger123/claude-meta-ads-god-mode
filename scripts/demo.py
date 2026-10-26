#!/usr/bin/env python3
"""Try God Mode with made-up clients - no ad accounts, no network, nothing real.

    python scripts/demo.py            # builds ./demo-home (or --home PATH)

Creates 4 fictional clients with brand colors, a week of fake snapshots, a
learning history, then runs the portfolio sweep and renders graphic ads.
Open the printed dashboard and contact-sheet paths in a browser.
Everything lives in the demo folder; your real ~/.ads-godmode is untouched.
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLIENTS = [
    # slug, name, meta acct, google cid, target CPL, monthly budget, brand colors, snapshot tweaks
    ("harbor-roofing", "Harbor Roofing", "act_900000000001", "9000000001", 120, 6000,
     ("#0f2d4a", "#eef3f8", "#f2a541"), dict(spend=1650, results=9, mtd=5800, tracking=True,
                                              ents=[("Storm damage - broad", 900, 0, "active", None, None, None)])),
    ("maple-dental", "Maple Street Dental", "act_900000000002", "9000000002", 70, 3500,
     ("#14532d", "#f0fdf4", "#22c55e"), dict(spend=820, results=16, mtd=2600, tracking=True,
                                              ents=[("Implants - UGC", 420, 9, "active", 0.9, 1.6, 4.2)])),
    ("bright-hvac", "Bright HVAC", "act_900000000003", "9000000003", 95, 5000,
     ("#7c2d12", "#fff7ed", "#fb923c"), dict(spend=900, results=14, mtd=3500, tracking=False, ents=[])),
    ("oak-and-iron", "Oak & Iron Remodeling", "act_900000000004", "9000000004", 110, 4500,
     ("#1f3a5f", "#f4efe6", "#e07a2e"), dict(spend=1050, results=17, mtd=3400, tracking=True,
                                              ents=[("Kitchens - offer card", 600, 12, "active", 1.4, 1.3, 2.1)])),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=os.path.join(os.getcwd(), "demo-home"))
    ap.add_argument("--no-png", action="store_true")
    a = ap.parse_args()
    home = os.path.abspath(a.home)
    marker = os.path.join(home, ".godmode-demo")
    if os.path.isdir(home) and os.listdir(home):
        if not os.path.exists(marker):
            print(f"Refusing to use {home}: it is not empty and was not created by this demo.")
            return 1
        import shutil
        shutil.rmtree(home)  # fresh demo each run; only ever a folder this script created
    os.makedirs(home, exist_ok=True)
    open(marker, "w").close()
    os.environ["ADS_GODMODE_HOME"] = home
    sys.path.insert(0, ROOT)
    from godmode import creative, learning, paths, portfolio, snapshots  # noqa: E402

    paths.ensure_dirs()
    with open(os.path.join(ROOT, "templates", "client-profile.json"), encoding="utf-8") as fh:
        tpl = json.load(fh)
    today = date.today()
    for slug, name, meta, gcid, cpl, budget, (prim, sec, acc), s in CLIENTS:
        p = json.loads(json.dumps(tpl))
        p.update(slug=slug, aliases=[name])
        p["business"]["name"] = name
        p["brand"]["colors"].update(primary=prim, secondary=sec, accent=acc)
        p["economics"].update(desired_cpl=cpl, monthly_budget=budget)
        p["platforms"]["meta"]["ad_account_ids"] = [meta]
        p["platforms"]["google"]["customer_ids"] = [gcid]
        with open(paths.clients_dir() / f"{slug}.json", "w", encoding="utf-8") as fh:
            json.dump(p, fh, indent=2)
        ents = [{"id": str(9000 + i), "name": n, "level": "adset", "status": "ACTIVE", "learning": lrn,
                 "spend": sp, "results": r, "ctr": ctr, "ctr_prev": ctrp, "frequency": fq}
                for i, (n, sp, r, lrn, ctr, ctrp, fq) in enumerate(s["ents"])]
        if slug == "harbor-roofing":
            ents.append({"id": "9100", "name": "Retargeting", "daily_budget": 40, "spend_today": 118,
                         "hours_elapsed": 13, "spend_history": [39, 41, 40, 38, 42, 40, 39]})
        snapshots.save({"client": slug, "captured_at": (today - timedelta(days=1)).isoformat(),
                        "window": {"days": 7},
                        "platforms": {"meta": {"account_id": meta, "spend": s["spend"], "results": s["results"],
                                               "month_to_date_spend": s["mtd"], "tracking_ok": s["tracking"],
                                               "previous": {"spend": s["spend"] * 0.9, "results": s["results"]},
                                               "entities": ents}}})
        # a small learning history
        start = today - timedelta(days=30)
        for tag, base, val in (("budget-up-20", 20, 31), ("budget-up-20", 18, 27), ("budget-up-20", 22, 33),
                               ("broad-match", 25, 14), ("broad-match", 30, 17), ("broad-match", 28, 15)):
            pr = learning.predict(slug, "meta", "budget", ["9000"], "results", "up", base, base,
                                  read_after_days=7, tags=[tag], today=start)
            learning.record_outcome(slug, pr["id"], val, val, source="demo")
        learning.add_lesson(slug, ["ugc-hook"], "UGC founder hook beat studio video on CTR", "worked", "demo")

    rep = portfolio.sweep(today=today)
    out = paths.home() / "reports" / today.isoformat()
    out.mkdir(parents=True, exist_ok=True)
    (out / "portfolio.md").write_text(portfolio.to_markdown(rep), encoding="utf-8")
    (out / "portfolio.html").write_text(portfolio.to_html(rep), encoding="utf-8")

    brief = {"client": "oak-and-iron", "concept": "Free design consult", "formats": ["1x1", "4x5", "9x16"],
             "hypothesis": "Offer-first static beats lifestyle photo for cold audiences",
             "variants": [
                 {"id": "A", "template": "offer-card", "badge": "Free", "headline": "Your new kitchen, planned for free",
                  "subhead": "In-home design consult across the county", "cta": "Book my free consult"},
                 {"id": "B", "template": "quote", "headline": "They finished two days early and left the place spotless.",
                  "subhead": "A. Customer (demo review)"}]}
    m = creative.render_brief(brief, png=not a.no_png)
    print(json.dumps({"demo_home": str(paths.home()), "dashboard": str(out / "portfolio.html"),
                      "report": str(out / "portfolio.md"), "creatives": str(m["dir"]) + os.sep + "index.html",
                      "learning": learning.summary("oak-and-iron")["proposals"],
                      "totals": rep["totals"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
