import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_META, META, META_SELF, Sandbox  # noqa: E402

from godmode import gate, policy, profiles  # noqa: E402
from godmode.budget import BudgetChange, check_limits, format_summary, to_micros, to_minor_units  # noqa: E402

GOOD = dict(spend_in_window=900, conversions_in_window=22, confidence="HIGH")


class BudgetMath(unittest.TestCase):
    def test_delta_and_pct(self):
        c = BudgetChange(current=50, proposed=60)
        self.assertEqual((c.delta, c.pct, c.direction), (10, 20.0, "increase"))
        c = BudgetChange(current=80, proposed=60)
        self.assertEqual((c.delta, c.pct, c.direction), (-20, -25.0, "decrease"))

    def test_units(self):
        self.assertEqual(to_minor_units(57.5), 5750)
        self.assertEqual(to_micros(12.34), 12_340_000)

    def test_summary_has_every_required_field(self):
        s = format_summary(BudgetChange(current=50, proposed=60, reason="r", evidence="e",
                                        expected_effect="x", risks="k", confidence="HIGH"))
        for label in ("CURRENT BUDGET", "PROPOSED BUDGET", "PERCENT CHANGE", "DOLLAR CHANGE", "REASON",
                      "DATA", "EXPECTED EFFECT", "RISKS", "CONFIDENCE"):
            self.assertIn(label, s)


class Limits(unittest.TestCase):
    def test_within_limits(self):
        self.assertEqual(check_limits(BudgetChange(50, 60, **GOOD), {}), [])

    def test_large_increase(self):
        v = check_limits(BudgetChange(50, 100, **GOOD), {})
        self.assertTrue(any("exceeds max 20" in x for x in v))

    def test_dollar_cap(self):
        v = check_limits(BudgetChange(400, 470, **GOOD), {"max_daily_dollar_change": 50})
        self.assertTrue(any("exceeds max 50" in x for x in v))

    def test_tiny_sample_blocks_increase(self):
        v = check_limits(BudgetChange(50, 55, spend_in_window=40, conversions_in_window=2, confidence="HIGH"), {})
        self.assertTrue(any("spend in window" in x for x in v))
        self.assertTrue(any("conversions in window" in x for x in v))

    def test_decrease_does_not_need_sample(self):
        self.assertEqual(check_limits(BudgetChange(50, 40, confidence="MODERATE"), {}), [])

    def test_low_confidence(self):
        v = check_limits(BudgetChange(50, 55, spend_in_window=900, conversions_in_window=40, confidence="EXPERIMENT"), {})
        self.assertTrue(any("confidence" in x for x in v))

    def test_unknown_current_budget(self):
        self.assertTrue(check_limits(BudgetChange(0, 50, **GOOD), {}))

    def test_cooldown(self):
        v = check_limits(BudgetChange(50, 55, **GOOD), {"cooldown_hours": 72}, hours_since_last_change=10)
        self.assertTrue(any("cooldown" in x for x in v))

    def test_high_budget_threshold(self):
        v = check_limits(BudgetChange(290, 310, **GOOD), {"max_daily_dollar_change": 100}, high_budget_threshold=300)
        self.assertTrue(any("high-budget threshold" in x for x in v))


class GuardedAutoBudget(Sandbox):
    alpha_mode = "guarded_auto"

    def budget_plan(self, current, proposed, conversions="22", spend="900", confidence="HIGH", entity="120000000000001"):
        return self.plan("budget", "--account", ALPHA_META, "--entity", entity, "--current", str(current),
                         "--proposed", str(proposed), "--spend", spend, "--conversions", conversions,
                         "--confidence", confidence, "--reason", "CPL 30% under target for 14 days")

    def test_small_increase_runs_without_prompt(self):
        out, _ = self.budget_plan(50, 58)
        self.assertEqual(out["verdict"], "auto")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "daily_budget": 5800}))
        self.assertEqual(r.decision, gate.ALLOW)

    def test_large_increase_needs_approval(self):
        out, _ = self.budget_plan(50, 90)
        self.assertEqual(out["verdict"], "approval")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "daily_budget": 9000}))
        self.assertEqual(r.decision, gate.ASK)
        self.assertIn("PROPOSED BUDGET", r.reason)

    def test_amount_in_call_must_match_plan(self):
        self.budget_plan(50, 58)
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "daily_budget": 58000}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("does not match", r.reason)

    def test_major_units_also_accepted(self):
        self.budget_plan(50, 58)
        r = gate.decide(self.hook(META_SELF + "meta_update_adset_budget",
                                  {"adSetId": "120000000000001", "dailyBudget": 58, "confirm": True}))
        self.assertEqual(r.decision, gate.ALLOW)

    def test_budget_not_allowed_action_needs_approval(self):
        self.set_mode("guarded_auto", {"allowed_actions": ["pause"]})
        out, _ = self.budget_plan(50, 52)
        self.assertEqual(out["verdict"], "approval")

    def test_cooldown_after_previous_change(self):
        from godmode import tickets
        out, _ = self.budget_plan(50, 55)
        tickets.consume(out["ticket"])
        out, _ = self.budget_plan(55, 60)
        self.assertEqual(out["verdict"], "approval")
        self.assertTrue(any("cooldown" in r for r in out["reasons"]))

    def test_too_many_entities(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", "1001", "--entity", "1002",
                           "--entity", "1003", "--entity", "1004")
        self.assertEqual(out["verdict"], "approval")


class FullAutoIsOptIn(Sandbox):
    alpha_mode = "full_auto"

    def test_disabled_by_default_falls_back_to_guarded(self):
        p = profiles.load("alpha-remodeling")
        d = policy.evaluate(p, "budget", BudgetChange(50, 100, **GOOD))
        self.assertEqual(d.verdict, policy.APPROVAL)
        self.assertTrue(any("disabled" in r for r in d.reasons))

    def test_enabled_still_caps_large_increase(self):
        os.environ["ADS_GODMODE_ENABLE_FULL_AUTO"] = "1"
        p = profiles.load("alpha-remodeling")
        self.assertEqual(policy.evaluate(p, "budget", BudgetChange(50, 70, **GOOD)).verdict, policy.AUTO)
        self.assertEqual(policy.evaluate(p, "budget", BudgetChange(50, 100, **GOOD)).verdict, policy.APPROVAL)
        self.assertEqual(policy.evaluate(p, "activate").verdict, policy.APPROVAL)
        self.assertEqual(policy.evaluate(p, "billing").verdict, policy.BLOCKED)


if __name__ == "__main__":
    unittest.main()
