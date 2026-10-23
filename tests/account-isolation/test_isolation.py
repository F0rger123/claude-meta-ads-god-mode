import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_GOOGLE, ALPHA_META, BETA_GOOGLE, BETA_META, META, Sandbox, make_profile  # noqa: E402

from godmode import gate, paths, profiles, session  # noqa: E402


class Resolve(Sandbox):
    def test_exact_slug_alias_and_fuzzy(self):
        self.assertEqual(profiles.resolve("alpha-remodeling").slug, "alpha-remodeling")
        self.assertEqual(profiles.resolve("D-Alpha").slug, "alpha-remodeling")
        self.assertEqual(profiles.resolve("dalpha").slug, "alpha-remodeling")
        self.assertEqual(profiles.resolve("Beta Roofing").slug, "beta-roofing")

    def test_unknown_client(self):
        with self.assertRaises(profiles.ProfileError):
            profiles.resolve("Gamma Plumbing")

    def test_ambiguous_client_is_never_guessed(self):
        self.write_client(make_profile("alpha-roofing", "Alpha Roofing", "act_333333333", "3333333333"))
        with self.assertRaises(profiles.ProfileError) as ctx:
            profiles.resolve("Alpha R")
        self.assertIn("ambiguous", str(ctx.exception))


class Ownership(Sandbox):
    def test_normalization(self):
        p = profiles.load("alpha-remodeling")
        self.assertTrue(p.owns("meta", ALPHA_META))
        self.assertTrue(p.owns("meta", ALPHA_META.replace("act_", "")))
        self.assertTrue(p.owns("google", "111-111-1111"))
        self.assertFalse(p.owns("meta", BETA_META))
        self.assertFalse(p.owns("google", BETA_GOOGLE))
        self.assertFalse(p.owns("meta", "garbage"))

    def test_duplicate_account_across_clients_detected(self):
        self.write_client(make_profile("gamma", "Gamma", ALPHA_META, "4444444444"))
        problems = profiles.isolation_problems()
        self.assertTrue(any(ALPHA_META in p for p in problems))

    def test_invalid_profile_rejected(self):
        bad = make_profile("bad", "Bad", "not-an-id", "123")
        self.assertTrue(profiles.validate(bad))


class WrongAccountPrevention(Sandbox):
    def test_create_in_other_clients_account_denied_with_owner(self):
        r = gate.decide(self.hook(META + "ads_create_campaign",
                                  {"ad_account_id": BETA_META, "name": "x", "objective": "OUTCOME_LEADS"}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("WRONG ACCOUNT", r.reason)
        self.assertIn("beta-roofing", r.reason)

    def test_unlisted_account_denied(self):
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": "act_999999999"}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("not in any client profile", r.reason)

    def test_account_inside_json_string_param_is_found(self):
        r = gate.decide(self.hook(META + "ads_create_ad_set",
                                  {"params": json.dumps({"account": BETA_META, "name": "y"})}))
        self.assertEqual(r.decision, gate.DENY)

    def test_mixed_platform_ids_denied(self):
        r = gate.decide(self.hook(META + "ads_create_campaign",
                                  {"ad_account_id": ALPHA_META, "customer_id": ALPHA_GOOGLE}))
        self.assertEqual(r.decision, gate.DENY)

    def test_no_active_client_denies_writes_but_not_reads(self):
        session.clear()
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("no active client", r.reason)
        self.assertIsNone(gate.decide(self.hook(META + "ads_get_ad_accounts", {})))

    def test_session_expires(self):
        data = json.loads(paths.session_file().read_text())
        data["selected_at"] = time.time() - 13 * 3600
        paths.session_file().write_text(json.dumps(data))
        self.assertIsNone(session.get_active())

    def test_switching_client_changes_what_is_allowed(self):
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(r.decision, gate.ALLOW)
        session.set_active("beta-roofing")
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(r.decision, gate.DENY)

    def test_plan_refuses_other_clients_account(self):
        out, code = self.plan("pause", "--platform", "meta", "--account", BETA_META, "--entity", "123456789")
        self.assertEqual(code, 2)
        self.assertIn("WRONG ACCOUNT", out["error"])

    def test_platform_disabled_for_client(self):
        p = profiles.load("alpha-remodeling").data
        p["platforms"]["google"]["enabled"] = False
        self.write_client(p)
        r = gate.decide(self.hook("mcp__adplane__google_create_campaign", {"customer_id": ALPHA_GOOGLE}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("not enabled", r.reason)


class GoogleWriterIsolation(Sandbox):
    def test_plan_for_other_customer_rejected(self):
        from connectors.google import writer
        plan = {"client": "alpha-remodeling", "customer_id": BETA_GOOGLE,
                "operations": [{"op": "set_status", "resource": "campaign", "id": "1", "status": "PAUSED"}]}
        with self.assertRaises(writer.PlanError) as ctx:
            writer.check_plan(plan)
        self.assertIn("beta-roofing", str(ctx.exception))

    def test_plan_for_other_client_rejected(self):
        from connectors.google import writer
        plan = {"client": "beta-roofing", "customer_id": BETA_GOOGLE, "operations": []}
        with self.assertRaises(writer.PlanError):
            writer.check_plan(plan)


if __name__ == "__main__":
    unittest.main()
