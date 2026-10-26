import json
import os
import re
import sys
import unittest
import zipfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_META, META, ROOT, Sandbox  # noqa: E402

from godmode import autopilot, budget_plan, gate, learning, niche, policy, profiles, tickets  # noqa: E402

NEW_AD, OLD_AD = "120000000000101", "120000000000100"


class BudgetPlanner(unittest.TestCase):
    def test_monthly_daily_conversion_and_expected_range(self):
        p = budget_plan.plan(budget_plan.BudgetInputs(monthly=3040, target_cpl=80))
        self.assertEqual(p["daily"], 100.0)
        lo, hi = p["platforms"]["meta"]["expected_results_per_month"]
        self.assertTrue(lo < 38 < hi)

    def test_learning_limited_advice(self):
        p = budget_plan.plan(budget_plan.BudgetInputs(daily=40, target_cpl=60))
        self.assertEqual(p["platforms"]["meta"]["ad_sets"], 1)
        self.assertTrue(any(r["type"] == "learning" for r in p["recommendations"]))

    def test_squeeze_more_when_economics_allow(self):
        p = budget_plan.plan(budget_plan.BudgetInputs(monthly=3000, target_cpl=90, job_value=38000,
                                                      close_rate_pct=12, margin_pct=35))
        scale = [r for r in p["recommendations"] if r["type"] == "scale"]
        self.assertTrue(scale and "more leads" in scale[0]["text"])

    def test_warns_when_target_unaffordable(self):
        p = budget_plan.plan(budget_plan.BudgetInputs(monthly=2000, target_cpl=200, lead_value=120))
        self.assertTrue(any(r["type"] == "economics" for r in p["recommendations"]))

    def test_budget_types(self):
        cap = budget_plan.plan(budget_plan.BudgetInputs(monthly=1500, target_cpl=50, hard_monthly_cap=True))
        self.assertIn("lifetime budget per calendar month", cap["budget_type"]["meta"])
        flight = budget_plan.plan(budget_plan.BudgetInputs(monthly=3040, target_cpl=50, flight_days=14))
        self.assertIn("Lifetime budget", flight["budget_type"]["meta"])

    def test_small_two_platform_budget_starts_with_google(self):
        p = budget_plan.plan(budget_plan.BudgetInputs(monthly=2000, target_cpl=90, platforms=["meta", "google"],
                                                      google_cpc=7))
        self.assertEqual(p["split"], {"google": 1.0, "meta": 0.0})
        big = budget_plan.plan(budget_plan.BudgetInputs(monthly=9000, target_cpl=90, platforms=["meta", "google"],
                                                        google_cpc=7))
        self.assertEqual(big["split"], {"google": 0.6, "meta": 0.4})

    def test_needs_an_amount(self):
        with self.assertRaises(ValueError):
            budget_plan.plan(budget_plan.BudgetInputs())


class Autopilot(Sandbox):
    def enable(self, cap=150, actions=None):
        return autopilot.set_state("alpha-remodeling", True, cap, actions)

    def test_toggle_requires_cap_and_active_mode(self):
        with self.assertRaises(ValueError):
            autopilot.set_state("alpha-remodeling", True, None)
        self.set_mode("draft")
        with self.assertRaises(ValueError):
            autopilot.set_state("alpha-remodeling", True, 100)
        self.set_mode("approval")
        st = self.enable()
        self.assertTrue(st["enabled"])
        self.assertTrue(autopilot.active(profiles.load("alpha-remodeling")))
        autopilot.set_state("alpha-remodeling", False)
        self.assertFalse(autopilot.active(profiles.load("alpha-remodeling")))

    def test_pause_is_auto_only_with_autopilot(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", OLD_AD)
        self.assertEqual(out["verdict"], "approval")
        self.enable()
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", OLD_AD)
        self.assertEqual(out["verdict"], "auto")

    def test_swap_within_cap_activates_new_and_pauses_old_only(self):
        self.enable(cap=150)
        out, code = self.plan("creative_swap", "--account", ALPHA_META, "--entity", NEW_AD, "--replaces", OLD_AD,
                              "--adset", "1200000000009", "--account-daily-budget", "120")
        self.assertEqual((code, out["verdict"]), (0, "auto"))
        act = gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": NEW_AD}))
        self.assertEqual(act.decision, gate.ALLOW)
        # the swap ticket can't activate the OLD ad or pause the NEW one
        self.assertEqual(gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": OLD_AD})).decision, gate.DENY)
        self.assertEqual(gate.decide(self.hook(META + "ads_update_entity",
                                               {"entity_id": NEW_AD, "status": "PAUSED"})).decision, gate.DENY)
        pause = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": OLD_AD, "status": "PAUSED"}))
        self.assertEqual(pause.decision, gate.ALLOW)

    def test_swap_over_cap_or_without_budget_needs_approval(self):
        self.enable(cap=100)
        out, _ = self.plan("creative_swap", "--account", ALPHA_META, "--entity", NEW_AD, "--replaces", OLD_AD,
                           "--account-daily-budget", "140")
        self.assertEqual(out["verdict"], "approval")
        out, _ = self.plan("creative_swap", "--account", ALPHA_META, "--entity", NEW_AD, "--replaces", OLD_AD)
        self.assertEqual(out["verdict"], "approval")

    def test_weekly_swap_limit(self):
        self.enable(cap=200)
        for i in range(3):
            out, _ = self.plan("creative_swap", "--account", ALPHA_META, "--entity", f"5550{i}0", "--replaces",
                               f"5550{i}1", "--account-daily-budget", "100")
            self.assertEqual(out["verdict"], "auto")
            tickets.consume(out["ticket"])
        out, _ = self.plan("creative_swap", "--account", ALPHA_META, "--entity", "555090", "--replaces", "555091",
                           "--account-daily-budget", "100")
        self.assertEqual(out["verdict"], "approval")

    def test_autopilot_never_activates_new_campaigns_or_raises_budgets(self):
        self.enable(cap=500)
        p = profiles.load("alpha-remodeling")
        self.assertEqual(policy.evaluate(p, "activate").verdict, policy.APPROVAL)
        self.assertEqual(policy.evaluate(p, "geo_expansion").verdict, policy.APPROVAL)
        self.assertNotEqual(policy.evaluate(p, "billing").verdict, policy.AUTO)
        out, _ = self.plan("budget", "--account", ALPHA_META, "--entity", OLD_AD, "--current", "50",
                           "--proposed", "60", "--spend", "900", "--conversions", "30", "--confidence", "HIGH")
        self.assertEqual(out["verdict"], "approval")

    def test_swap_needs_both_ads(self):
        self.enable()
        out, code = self.plan("creative_swap", "--account", ALPHA_META, "--entity", NEW_AD)
        self.assertNotEqual(code, 0)

    def test_unattended_allows_autopilot_auto_only(self):
        os.environ["ADS_GODMODE_UNATTENDED"] = "1"
        try:
            r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": OLD_AD, "status": "PAUSED"}))
            self.assertEqual(r.decision, gate.DENY)  # autopilot off
            self.enable()
            self.plan("pause", "--account", ALPHA_META, "--entity", OLD_AD)
            r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": OLD_AD, "status": "PAUSED"}))
            self.assertEqual(r.decision, gate.ALLOW)
            self.plan("activate", "--account", ALPHA_META, "--entity", NEW_AD)
            r = gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": NEW_AD}))
            self.assertEqual(r.decision, gate.DENY)
        finally:
            os.environ.pop("ADS_GODMODE_UNATTENDED", None)

    def test_candidates(self):
        self.enable()
        p = profiles.load("alpha-remodeling")  # target CPL 90
        snap = {"platforms": {"meta": {"account_id": ALPHA_META, "tracking_ok": True, "entities": [
            {"id": "1", "name": "dead", "spend": 300, "results": 0, "age_days": 6},
            {"id": "2", "name": "pricey", "spend": 1200, "results": 6, "age_days": 10},
            {"id": "3", "name": "young", "spend": 400, "results": 0, "age_days": 1},
            {"id": "4", "name": "tired", "spend": 300, "results": 5, "ctr": 0.7, "ctr_prev": 1.3, "frequency": 3.6,
             "age_days": 30}]}}}
        c = autopilot.candidates(p, snap)
        self.assertEqual({x["name"] for x in c["losers"]}, {"dead", "pricey"})
        self.assertEqual([x["name"] for x in c["fatigued"]], ["tired"])
        snap["platforms"]["meta"]["tracking_ok"] = False
        self.assertIn("blocked", autopilot.candidates(p, snap))


class Niches(Sandbox):
    def playbook(self, **kw):
        pb = {"niche": "Kitchen Remodeling", "benchmarks": [
            {"text": "Home services Meta CPL often $40-120", "source": "https://example.org/report", "date": "2026-09",
             "label": "THIRD-PARTY BENCHMARK"}],
              "offers": [{"text": "Free in-home design consult", "source": "account data", "date": "2026-10-01",
                          "label": "OBSERVED"}]}
        pb.update(kw)
        return pb

    def test_save_and_show(self):
        path = niche.save(self.playbook())
        self.assertTrue(path.endswith("kitchen-remodeling.json"))
        self.assertEqual(niche.load("kitchen remodeling")["offers"][0]["label"], "OBSERVED")
        self.assertEqual(niche.list_all()[0]["facts"], 2)

    def test_unsourced_fact_rejected(self):
        with self.assertRaises(niche.NicheError):
            niche.save(self.playbook(hooks=[{"text": "use urgency", "label": "HEURISTIC", "date": "2026-10"}]))
        with self.assertRaises(niche.NicheError):
            niche.save(self.playbook(hooks=[{"text": "x", "source": "s", "date": "2026-10", "label": "TRUST ME"}]))

    def test_niche_patterns_across_clients(self):
        for slug in ("alpha-remodeling", "beta-roofing"):
            p = profiles.load(slug).data
            p["business"]["niche"] = "kitchen-remodeling"
            self.write_client(p)
            pr = learning.predict(slug, "meta", "creative_swap", ["1"], "ctr", "up", 1.0, 400, tags=["before-after-static"])
            learning.record_outcome(slug, pr["id"], 1.6, 400)
        res = niche.niche_patterns("kitchen-remodeling")
        self.assertEqual(res["clients"], 2)
        self.assertEqual(res["patterns"][0]["tag"], "before-after-static")
        self.assertEqual(res["patterns"][0]["label"], "NICHE PATTERN")


class SetupDocs(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
            return fh.read()

    def test_wizard_gates_every_step_and_links_websites(self):
        w = self.read("docs", "SETUP_WIZARD.md")
        steps = re.split(r"\n## Step ", w)[1:]
        self.assertGreaterEqual(len(steps), 10)
        for s in steps:
            self.assertIn("✅", s, s.splitlines()[0])
        for s in steps[3:7]:  # Meta business, billing, connect, Google: all website steps
            self.assertRegex(s, r"\]\(https://", s.splitlines()[0])
        self.assertIn("Do not move on", w)
        self.assertIn("Autopilot", w)
        self.assertIn("console.cloud.google.com/google/ads-apis/overview", w)
        self.assertNotIn("apicenter", w.lower())

    def test_onboarding_offers_autopilot_and_budget_plan(self):
        s = self.read("skills", "ads-client-onboarding", "SKILL.md")
        for needle in ("adsgm budget-plan", "adsgm autopilot on", "/ads:schedule", "niche"):
            self.assertIn(needle, s)

    def test_chat_skill_zip(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import build_chat_skill
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            path = build_chat_skill.build(td)
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                skill = z.read("meta-ads-god-mode-chat/SKILL.md").decode()
        self.assertIn("meta-ads-god-mode-chat/references/learning-phase.md", names)
        m = re.match(r"^---\nname: (.+)\ndescription: (.+)\n---", skill)
        self.assertEqual(m.group(1), "meta-ads-god-mode-chat")
        self.assertLessEqual(len(m.group(2)), 1024)
        self.assertIn("type **yes**", skill)
