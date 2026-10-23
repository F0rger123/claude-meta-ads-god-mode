import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import (ALPHA_GOOGLE, ALPHA_META, META, FakeGoogleAdsClient, Sandbox,  # noqa: E402
                     install_fake_protobuf)

from godmode import anomaly, evidence, gate, tickets  # noqa: E402

ENTITY = "120000000000001"


class ApprovalMode(Sandbox):
    def test_plan_then_write_asks_human(self):
        out, code = self.plan("activate", "--account", ALPHA_META, "--entity", ENTITY, "--entity-label", "Kitchen leads")
        self.assertEqual((code, out["verdict"]), (0, "approval"))
        self.assertIn("CLIENT: Alpha Remodeling", out["summary"])
        r = gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": ENTITY}))
        self.assertEqual(r.decision, gate.ASK)
        self.assertIn("APPROVAL REQUIRED", r.reason)

    def test_no_prompt_modes_turn_ask_into_deny(self):
        self.plan("activate", "--account", ALPHA_META, "--entity", ENTITY)
        for mode in ("bypassPermissions", "dontAsk", "auto"):
            r = gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": ENTITY}, permission_mode=mode))
            self.assertEqual(r.decision, gate.DENY, mode)

    def test_ticket_is_single_use(self):
        self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY)
        payload = self.hook(META + "ads_update_entity", {"entity_id": ENTITY, "status": "PAUSED"})
        self.assertEqual(gate.decide(payload).decision, gate.ASK)
        payload["tool_response"] = {"success": True}
        gate.after(payload)
        self.assertEqual(gate.decide(payload).decision, gate.DENY)

    def test_ticket_expires(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY)
        t = tickets.get(out["ticket"])
        t["expires_at"] = time.time() - 1
        tickets._path(t["id"]).write_text(json.dumps(t))
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": ENTITY, "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.DENY)

    def test_ticket_from_other_client_not_usable(self):
        self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY)
        from godmode import session
        session.set_active("beta-roofing")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": ENTITY, "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.DENY)

    def test_audit_log_written_and_redacted(self):
        self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY)
        payload = self.hook(META + "ads_update_entity", {"entity_id": ENTITY, "status": "PAUSED",
                                                          "access_token": "EAAB" + "x" * 40})
        gate.after(payload)
        from godmode import audit
        rec = audit.tail(1)[0]
        self.assertEqual(rec["event"], "write")
        self.assertNotIn("EAAB", json.dumps(rec))


class EmergencyStop(Sandbox):
    alpha_mode = "read_only"

    def test_pause_possible_in_read_only_with_approval(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY, "--entity", "120000000000002",
                           "--reason", "spend 3x budget, 0 leads")
        self.assertEqual(out["verdict"], "approval")
        r = gate.decide(self.hook(META + "ads_update_entity",
                                  {"entity_ids": [ENTITY, "120000000000002"], "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.ASK)

    def test_multi_entity_ticket_survives_one_call_per_entity(self):
        self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY, "--entity", "120000000000002")
        for eid in (ENTITY, "120000000000002"):
            payload = self.hook(META + "ads_update_entity", {"entity_id": eid, "status": "PAUSED"})
            self.assertEqual(gate.decide(payload).decision, gate.ASK, eid)
            payload["tool_response"] = {"success": True}
            gate.after(payload)
        payload = self.hook(META + "ads_update_entity", {"entity_id": ENTITY, "status": "PAUSED"})
        self.assertEqual(gate.decide(payload).decision, gate.DENY)
        self.assertEqual(tickets.list_open("alpha-remodeling"), [])

    def test_activation_still_blocked_in_read_only(self):
        out, code = self.plan("activate", "--account", ALPHA_META, "--entity", ENTITY)
        self.assertEqual(out["verdict"], "blocked")

    def test_anomaly_detection(self):
        rows = [
            {"id": "1", "name": "runaway", "daily_budget": 50, "spend_today": 140, "hours_elapsed": 14,
             "spend_history": [48, 51, 47, 50, 52, 49, 50], "conversions_today": 0},
            {"id": "2", "name": "normal", "daily_budget": 50, "spend_today": 28, "hours_elapsed": 14,
             "spend_history": [48, 51, 47, 50, 52, 49, 50]},
            {"id": "3", "name": "tiny", "spend_today": 5},
        ]
        flags = anomaly.detect(rows)
        self.assertEqual([f["id"] for f in flags], ["1"])
        self.assertGreaterEqual(flags[0]["severity"], 3)


class GuardedAuto(Sandbox):
    alpha_mode = "guarded_auto"

    def test_activation_always_asks(self):
        out, _ = self.plan("activate", "--account", ALPHA_META, "--entity", ENTITY)
        self.assertEqual(out["verdict"], "approval")

    def test_pause_within_policy_runs(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", ENTITY)
        self.assertEqual(out["verdict"], "auto")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": ENTITY, "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.ALLOW)

    def test_large_negative_list_needs_approval(self):
        out, _ = self.plan("negative_keywords", "--platform", "google", "--account", ALPHA_GOOGLE,
                           "--entity", "555", "--negatives", "40")
        self.assertEqual(out["verdict"], "approval")


class DataQuality(unittest.TestCase):
    def test_tiny_sample_is_experiment(self):
        q = evidence.assess(conversions=3, spend=120, days=3, target_cpa=90, tracking_healthy=True)
        self.assertEqual(q.confidence, evidence.EXPERIMENT)

    def test_solid_sample_is_high(self):
        q = evidence.assess(conversions=60, spend=5000, days=30, tracking_healthy=True)
        self.assertEqual(q.confidence, evidence.HIGH)

    def test_broken_tracking_caps_confidence(self):
        q = evidence.assess(conversions=60, spend=5000, days=30, tracking_healthy=False)
        self.assertNotEqual(q.confidence, evidence.HIGH)

    def test_rate_comparison(self):
        self.assertEqual(evidence.compare_rates(30, 1000, 31, 1000)["confidence"], evidence.EXPERIMENT)
        self.assertEqual(evidence.compare_rates(80, 1000, 30, 1000)["confidence"], evidence.HIGH)


class GoogleWriterApproval(Sandbox):
    def setUp(self):
        super().setUp()
        install_fake_protobuf()
        from connectors.google import writer
        self.writer = writer

    def campaign_plan(self, **extra):
        op = {"op": "create_search_campaign", "name": "York Kitchen Remodel - Search", "daily_budget": 60,
              "bidding": {"strategy": "maximize_conversions"},
              "proximity": {"lat": 39.9626, "lng": -76.7277, "radius_miles": 20},
              "negative_keywords": [{"text": "jobs", "match_type": "PHRASE"}],
              "ad_groups": [{"name": "Kitchen remodel", "keywords": [{"text": "kitchen remodel york pa", "match_type": "PHRASE"}],
                             "rsa": {"headlines": ["Kitchen Remodeling York", "Free Design Consult", "Local Craftsmen"],
                                     "descriptions": ["Plan your new kitchen with a local team.", "Book a free in-home consult."],
                                     "final_url": "https://www.example.com/kitchen-remodeling"}}]}
        op.update(extra)
        return {"client": "alpha-remodeling", "customer_id": ALPHA_GOOGLE, "operations": [op]}

    def test_validate_only_is_default(self):
        fake = FakeGoogleAdsClient()
        report = self.writer.apply(self.campaign_plan(), client=fake)
        self.assertTrue(report["validate_only"])
        self.assertTrue(fake.service.requests[0].validate_only)

    def test_campaign_created_paused(self):
        fake = FakeGoogleAdsClient()
        self.writer.apply(self.campaign_plan(), client=fake)
        ops = fake.service.requests[0].mutate_operations.items
        campaign = ops[1].campaign_operation.create
        self.assertEqual(campaign.status, "CampaignStatusEnum.PAUSED")

    def test_status_field_rejected(self):
        with self.assertRaises(self.writer.PlanError):
            self.writer.normalize(self.campaign_plan(status="ENABLED"))

    def test_geo_required(self):
        with self.assertRaises(self.writer.PlanError):
            self.writer.normalize(self.campaign_plan(proximity=None))

    def test_rsa_limits(self):
        bad = self.campaign_plan()
        bad["operations"][0]["ad_groups"][0]["rsa"]["headlines"] = ["x" * 31, "b", "c"]
        with self.assertRaises(self.writer.PlanError):
            self.writer.normalize(bad)

    def test_execute_requires_ticket(self):
        with self.assertRaises(self.writer.PlanError):
            self.writer.apply(self.campaign_plan(), execute=True, client=FakeGoogleAdsClient())

    def test_execute_with_matching_ticket(self):
        path = os.path.join(self.tmp, "plan.json")
        with open(path, "w") as fh:
            json.dump(self.campaign_plan(), fh)
        out, _ = self.plan("create", "--google-plan", path)
        self.assertEqual(out["verdict"], "auto")
        fake = FakeGoogleAdsClient()
        report = self.writer.apply(self.campaign_plan(), execute=True, ticket_id=out["ticket"], client=fake)
        self.assertFalse(report["validate_only"])
        self.assertTrue(tickets.get(out["ticket"])["consumed"])

    def test_ticket_action_must_match_plan(self):
        pause = {"client": "alpha-remodeling", "customer_id": ALPHA_GOOGLE,
                 "operations": [{"op": "set_status", "resource": "campaign", "id": "777", "status": "PAUSED"}]}
        out, _ = self.plan("pause", "--platform", "google", "--account", ALPHA_GOOGLE, "--entity", "777")
        pause["operations"][0]["status"] = "ENABLED"
        with self.assertRaises(self.writer.PlanError):
            self.writer.apply(pause, execute=True, ticket_id=out["ticket"], client=FakeGoogleAdsClient())

    def test_bash_execute_gated(self):
        cmd = 'python "/p/adsgm.py" google apply --plan p.json --execute'
        r = gate.decide(self.hook("Bash", {"command": cmd}))
        self.assertEqual(r.decision, gate.DENY)
        out, _ = self.plan("pause", "--platform", "google", "--account", ALPHA_GOOGLE, "--entity", "777")
        r = gate.decide(self.hook("Bash", {"command": cmd + f" --ticket {out['ticket']}"}))
        self.assertEqual(r.decision, gate.ASK)


if __name__ == "__main__":
    unittest.main()
