import json
import os
import sys
import unittest
from datetime import date
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_GOOGLE, ALPHA_META, BETA_META, META, Sandbox  # noqa: E402

from godmode import gate, learning, portfolio, profiles, schedule, snapshots, tickets  # noqa: E402

TODAY = date(2026, 10, 25)


def snap(client="alpha-remodeling", account=ALPHA_META, **meta):
    m = {"account_id": account, "spend": 700, "results": 10, "month_to_date_spend": 3000,
         "tracking_ok": True, "previous": {"spend": 650, "results": 9}, "entities": []}
    m.update(meta)
    return {"client": client, "captured_at": "2026-10-24", "window": {"days": 7}, "platforms": {"meta": m}}


class Snapshots(Sandbox):
    def test_save_and_latest(self):
        path = snapshots.save(snap())
        self.assertTrue(os.path.exists(path))
        self.assertEqual(snapshots.latest("alpha-remodeling")["platforms"]["meta"]["spend"], 700)

    def test_refuses_other_clients_account(self):
        with self.assertRaises(snapshots.SnapshotError) as ctx:
            snapshots.save(snap(account=BETA_META))
        self.assertIn("beta-roofing", str(ctx.exception))

    def test_refuses_client_mismatch(self):
        s = snap()
        s["client"] = "beta-roofing"
        with self.assertRaises(snapshots.SnapshotError):
            snapshots.save(s)

    def test_entity_metric(self):
        s = snap(entities=[{"id": "111", "spend": 300, "results": 6, "ctr": 1.2, "clicks": 500}])
        self.assertEqual(snapshots.entity_metric(s, "meta", "111", "cpl"), {"value": 50.0, "n": 6})
        self.assertEqual(snapshots.entity_metric(s, "meta", "111", "ctr")["value"], 1.2)
        self.assertIsNone(snapshots.entity_metric(s, "meta", "999", "cpl"))


class Sweep(Sandbox):
    def review(self, s):
        return portfolio.review_client(profiles.load("alpha-remodeling"), s, TODAY)

    def titles(self, row):
        return [i["title"] for i in row["issues"]]

    def test_no_snapshot(self):
        row = self.review(None)
        self.assertEqual(row["status"], "AMBER")
        self.assertIn("No data yet", self.titles(row))

    def test_broken_tracking_is_red(self):
        row = self.review(snap(tracking_ok=False))
        self.assertEqual(row["status"], "RED")
        self.assertEqual(row["issues"][0]["severity"], "CRITICAL")

    def test_no_cpl_verdict_when_tracking_broken(self):
        row = self.review(snap(tracking_ok=False, spend=600, results=12))
        self.assertNotIn("Beating target CPL", self.titles(row))

    def test_overspend_pacing(self):
        row = self.review(snap(month_to_date_spend=4400))  # budget 4500, day 25 of 31 -> ~3629 expected
        self.assertIn("Overspending month budget", self.titles(row))

    def test_cpl_far_above_target(self):
        row = self.review(snap(spend=1500, results=10))  # target 90
        self.assertIn("CPL far above target", self.titles(row))

    def test_zero_result_spender_and_fatigue(self):
        row = self.review(snap(entities=[
            {"id": "1", "name": "Dead ad set", "spend": 400, "results": 0, "learning": "active"},
            {"id": "2", "name": "Tired", "spend": 200, "results": 3, "ctr": 0.8, "ctr_prev": 1.5, "frequency": 4.1}]))
        t = self.titles(row)
        self.assertIn("Zero-result spender: Dead ad set", t)
        self.assertIn("Creative fatigue: Tired", t)

    def test_runaway_spend_flagged(self):
        row = self.review(snap(entities=[{"id": "9", "name": "Runaway", "daily_budget": 50, "spend_today": 140,
                                          "hours_elapsed": 14, "spend_history": [48, 51, 47, 50, 52, 49, 50]}]))
        self.assertEqual(row["status"], "RED")
        self.assertTrue(any("Unusual spend" in x for x in self.titles(row)))

    def test_opportunity(self):
        row = self.review(snap(spend=600, results=12))  # CPL 50 vs 90
        self.assertIn("Beating target CPL", self.titles(row))
        self.assertEqual(row["status"], "GREEN")

    def test_portfolio_ranking_and_reports(self):
        snapshots.save(snap(tracking_ok=False))
        rep = portfolio.sweep(today=TODAY)
        self.assertEqual([r["client"] for r in rep["clients"]][0], "alpha-remodeling")
        self.assertEqual(rep["totals"]["clients"], 2)
        md = portfolio.to_markdown(rep)
        self.assertIn("Alpha Remodeling", md)
        page = portfolio.to_html(rep)
        self.assertIn("<!doctype html>", page)

    def test_html_escapes_names(self):
        p = profiles.load("alpha-remodeling").data
        p["business"]["name"] = "<script>x</script>"
        self.write_client(p)
        page = portfolio.to_html(portfolio.sweep(today=TODAY))
        self.assertNotIn("<script>x", page)


class Learning(Sandbox):
    def pred(self, **kw):
        args = dict(client="alpha-remodeling", platform="meta", action="budget", entities=["111"], metric="results",
                    direction="up", baseline=20, baseline_n=20, read_after_days=7, tags=["budget-up-20"],
                    today=date(2026, 10, 1))
        args.update(kw)
        return learning.predict(**args)

    def test_due_after_read_date(self):
        p = self.pred()
        self.assertEqual(learning.due("alpha-remodeling", date(2026, 10, 7)), [])
        self.assertEqual([d["id"] for d in learning.due("alpha-remodeling", date(2026, 10, 8))], [p["id"]])

    def test_grades(self):
        p = self.pred()
        self.assertEqual(learning.grade(p, 30, 30)["verdict"], "worked")
        self.assertEqual(learning.grade(p, 12, 12)["verdict"], "failed")
        self.assertEqual(learning.grade(p, 21, 21)["verdict"], "inconclusive")   # within noise
        self.assertEqual(learning.grade(p, 30, 5)["verdict"], "inconclusive")    # tiny sample
        down = self.pred(metric="cpl", direction="down", baseline=100, baseline_n=40)
        self.assertEqual(learning.grade(down, 70, 40)["verdict"], "worked")

    def test_invalid_metric(self):
        with self.assertRaises(ValueError):
            self.pred(metric="vibes")

    def test_auto_read_from_snapshot_and_not_executed(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", "222")
        p1 = self.pred(entities=["111"])
        p2 = self.pred(entities=["222"], ticket=out["ticket"])  # ticket never consumed
        s = snap(entities=[{"id": "111", "spend": 500, "results": 32}])
        recs = learning.auto_read("alpha-remodeling", s, tickets.get, today=date(2026, 10, 9))
        verdicts = {r["prediction"]: r["verdict"] for r in recs}
        self.assertEqual(verdicts[p1["id"]], "worked")
        self.assertEqual(verdicts[p2["id"]], "not_executed")
        self.assertEqual(learning.due("alpha-remodeling", date(2026, 10, 9)), [])

    def test_summary_and_proposals(self):
        for i in range(4):
            p = self.pred(tags=["budget-up-20"])
            learning.record_outcome("alpha-remodeling", p["id"], 30, 30)
        for i in range(3):
            p = self.pred(tags=["broad-match"])
            learning.record_outcome("alpha-remodeling", p["id"], 10, 30)
        learning.add_lesson("alpha-remodeling", ["ugc-hook"], "UGC beat studio", "worked")
        s = learning.summary("alpha-remodeling")
        works = {x["tag"]: x for x in s["works"]}
        doesnt = {x["tag"]: x for x in s["doesnt"]}
        self.assertEqual(works["budget-up-20"]["confidence"], "MODERATE")
        self.assertIn("broad-match", doesnt)
        self.assertTrue(any("budget-up-20" in x for x in s["proposals"]))
        self.assertTrue(any("broad-match" in x for x in s["proposals"]))

    def test_portfolio_patterns_need_two_clients(self):
        p = self.pred(tags=["negatives"])
        learning.record_outcome("alpha-remodeling", p["id"], 30, 30)
        self.assertEqual(learning.portfolio_patterns(["alpha-remodeling", "beta-roofing"]), [])
        q = self.pred(client="beta-roofing", tags=["negatives"])
        learning.record_outcome("beta-roofing", q["id"], 30, 30)
        pats = learning.portfolio_patterns(["alpha-remodeling", "beta-roofing"])
        self.assertEqual(pats[0]["tag"], "negatives")
        self.assertEqual(pats[0]["label"], "PORTFOLIO HEURISTIC")

    def test_plan_with_prediction(self):
        out, code = self.plan("pause", "--account", ALPHA_META, "--entity", "333", "--predict-metric", "cpl",
                              "--predict-direction", "down", "--baseline", "120", "--baseline-n", "14",
                              "--tags", "pause-loser")
        self.assertEqual(code, 0)
        self.assertTrue(out["prediction"].startswith("prd_"))
        rec = learning.predictions("alpha-remodeling")[0]
        self.assertEqual((rec["ticket"], rec["tags"]), (out["ticket"], ["pause-loser"]))

    def test_learnings_never_change_profile(self):
        before = json.dumps(profiles.load("alpha-remodeling").data, sort_keys=True)
        for _ in range(8):
            p = self.pred()
            learning.record_outcome("alpha-remodeling", p["id"], 40, 40)
        learning.summary("alpha-remodeling")
        self.assertEqual(json.dumps(profiles.load("alpha-remodeling").data, sort_keys=True), before)


class Unattended(Sandbox):
    alpha_mode = "guarded_auto"

    def setUp(self):
        super().setUp()
        os.environ["ADS_GODMODE_UNATTENDED"] = "1"

    def tearDown(self):
        os.environ.pop("ADS_GODMODE_UNATTENDED", None)
        super().tearDown()

    def test_writes_denied_without_opt_in(self):
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("unattended", r.reason)

    def test_reads_still_work(self):
        self.assertIsNone(gate.decide(self.hook(META + "ads_get_ad_entities", {"ad_account_id": ALPHA_META})))

    def test_opt_in_allows_auto_but_never_approval(self):
        p = profiles.load("alpha-remodeling").data
        p["automation"]["allow_unattended_writes"] = True
        self.write_client(p)
        self.plan("pause", "--account", ALPHA_META, "--entity", "120000000000001")  # guarded auto: pause allowed
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.ALLOW)
        self.plan("activate", "--account", ALPHA_META, "--entity", "120000000000002")
        r = gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": "120000000000002"}))
        self.assertEqual(r.decision, gate.DENY)


class Schedules(unittest.TestCase):
    def test_jobs_are_unattended(self):
        for osn in ("posix", "windows"):
            plan = schedule.plan(osn)
            self.assertEqual([j["name"] for j in plan["jobs"]], ["daily-check", "weekly-review", "autopilot-run", "monthly-report"])
            for j in plan["jobs"]:
                self.assertEqual(j["env"]["ADS_GODMODE_UNATTENDED"], "1")
                self.assertIn("ADS_GODMODE_UNATTENDED=1", j["command"])
                self.assertTrue("/ads:sweep" in j["command"] or "/ads:autopilot" in j["command"])
        self.assertTrue(schedule.plan("windows")["jobs"][0]["command"].startswith("schtasks /Create"))

    def test_allowed_tools_exclude_raw_shell(self):
        self.assertNotIn("Bash", schedule.ALLOWED_TOOLS)
        self.assertFalse(any(t.startswith("Bash(curl") for t in schedule.ALLOWED_TOOLS))


if __name__ == "__main__":
    unittest.main()
