import contextlib
import importlib.util
import io
import json
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_META, META, META_SELF, ROOT, Sandbox  # noqa: E402

from godmode import gate  # noqa: E402


def load_hook_module():
    spec = importlib.util.spec_from_file_location("write_gate", os.path.join(ROOT, "hooks", "write_gate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class PausedFirstCreation(Sandbox):
    def test_paused_create_allowed_without_prompt(self):
        r = gate.decide(self.hook(META + "ads_create_campaign",
                                  {"ad_account_id": ALPHA_META, "name": "Kitchen leads", "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.ALLOW)

    def test_create_with_active_status_blocked(self):
        for status in ("ACTIVE", "active", "ENABLED"):
            r = gate.decide(self.hook(META + "ads_create_ad",
                                      {"ad_account_id": ALPHA_META, "status": status}))
            self.assertEqual(r.decision, gate.DENY, status)
            self.assertIn("PAUSED", r.reason)

    def test_create_without_verifiable_account_denied(self):
        r = gate.decide(self.hook(META + "ads_create_ad_set", {"campaign_id": "120000000000001"}))
        self.assertEqual(r.decision, gate.DENY)

    def test_selfhosted_preview_passes_but_confirmed_active_create_blocked(self):
        self.assertIsNone(gate.decide(self.hook(META_SELF + "meta_create_campaign",
                                                {"accountId": ALPHA_META, "status": "ACTIVE"})))
        r = gate.decide(self.hook(META_SELF + "meta_create_campaign",
                                  {"accountId": ALPHA_META, "status": "ACTIVE", "confirm": True}))
        self.assertEqual(r.decision, gate.DENY)


class ModeEnforcement(Sandbox):
    def test_read_only_blocks_create(self):
        self.set_mode("read_only")
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("read_only", r.reason)

    def test_draft_allows_paused_create_blocks_activation_plan(self):
        self.set_mode("draft")
        r = gate.decide(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(r.decision, gate.ALLOW)
        out, code = self.plan("activate", "--account", ALPHA_META, "--entity", "120000000000001")
        self.assertEqual((out["verdict"], code), ("blocked", 3))

    def test_draft_blocks_budget(self):
        self.set_mode("draft")
        out, code = self.plan("budget", "--account", ALPHA_META, "--entity", "1200001",
                              "--current", "50", "--proposed", "55")
        self.assertEqual(out["verdict"], "blocked")


class EntityWritesNeedTicket(Sandbox):
    def test_update_entity_without_ticket_denied(self):
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "name": "new"}))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("no verified change plan", r.reason)

    def test_activate_without_ticket_denied(self):
        r = gate.decide(self.hook(META + "ads_activate_entity", {"entity_id": "120000000000001"}))
        self.assertEqual(r.decision, gate.DENY)

    def test_write_naming_nothing_denied(self):
        r = gate.decide(self.hook(META + "ads_update_entity", {"name": "x"}))
        self.assertEqual(r.decision, gate.DENY)

    def test_ticket_for_other_entity_does_not_cover(self):
        self.plan("pause", "--account", ALPHA_META, "--entity", "120000000000001")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000999", "status": "PAUSED"}))
        self.assertEqual(r.decision, gate.DENY)

    def test_ticket_for_pause_does_not_cover_activation(self):
        self.plan("pause", "--account", ALPHA_META, "--entity", "120000000000001")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "status": "ACTIVE"}))
        self.assertEqual(r.decision, gate.DENY)


class DestructiveActions(Sandbox):
    def test_billing_and_admin_always_blocked(self):
        for tool in ("mcp__adplane__meta_update_billing", "mcp__adplane__meta_add_user_role"):
            r = gate.decide(self.hook(tool, {"account_id": ALPHA_META}))
            self.assertEqual(r.decision, gate.DENY, tool)

    def test_full_auto_still_asks_for_delete(self):
        self.set_mode("full_auto")
        os.environ["ADS_GODMODE_ENABLE_FULL_AUTO"] = "1"
        self.plan("delete", "--account", ALPHA_META, "--entity", "120000000000001")
        r = gate.decide(self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "status": "DELETED"}))
        self.assertEqual(r.decision, gate.ASK)

    def test_archive_treated_as_delete(self):
        c = gate.classify(META + "ads_update_entity", {"entity_id": "1", "status": "ARCHIVED"})
        from godmode.extract import extract
        self.assertEqual(gate.refine_action(c, extract({"status": "ARCHIVED"})), "delete")

    def test_geo_change_needs_geo_ticket(self):
        self.plan("update", "--account", ALPHA_META, "--entity", "120000000000001")
        r = gate.decide(self.hook(META + "ads_update_entity",
                                  {"entity_id": "120000000000001",
                                   "targeting": json.dumps({"geo_locations": {"countries": ["US"]}})}))
        self.assertEqual(r.decision, gate.DENY)  # update ticket does not cover geo_expansion


class ConnectorFailureFailsClosed(Sandbox):
    def run_hook(self, payload, phase="pre"):
        mod = load_hook_module()
        stdout = io.StringIO()
        with mock.patch.object(sys, "argv", ["write_gate.py", phase]), \
                mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
            code = mod.main()
        return code, stdout.getvalue()

    def test_gate_crash_blocks_ads_write(self):
        with mock.patch("godmode.gate.decide", side_effect=RuntimeError("boom")):
            code, _ = self.run_hook(self.hook(META + "ads_activate_entity", {"entity_id": "1"}))
        self.assertEqual(code, 2)

    def test_gate_crash_does_not_block_unrelated_tools(self):
        with mock.patch("godmode.gate.decide", side_effect=RuntimeError("boom")):
            code, _ = self.run_hook(self.hook("mcp__gmail__search_threads", {}))
        self.assertEqual(code, 0)

    def test_corrupt_profile_denies(self):
        from godmode import paths
        (paths.clients_dir() / "alpha-remodeling.json").write_text("{not json")
        code, out = self.run_hook(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_hook_output_shape(self):
        code, out = self.run_hook(self.hook(META + "ads_create_campaign", {"ad_account_id": ALPHA_META}))
        hso = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(hso["hookEventName"], "PreToolUse")
        self.assertEqual(hso["permissionDecision"], "allow")

    def test_reads_produce_no_output(self):
        code, out = self.run_hook(self.hook(META + "ads_get_ad_entities", {"ad_account_id": "act_999"}))
        self.assertEqual((code, out), (0, ""))

    def test_failed_write_does_not_consume_ticket(self):
        out, _ = self.plan("pause", "--account", ALPHA_META, "--entity", "120000000000001")
        payload = self.hook(META + "ads_update_entity", {"entity_id": "120000000000001", "status": "PAUSED"})
        payload["tool_response"] = {"isError": True}
        self.run_hook(payload, "post")
        from godmode import tickets
        self.assertFalse(tickets.get(out["ticket"])["consumed"])


if __name__ == "__main__":
    unittest.main()
