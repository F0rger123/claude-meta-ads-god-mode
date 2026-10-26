"""Gate decisions on the real parameter shapes of the connectors we support.

getmcpads-com/meta-ads-mcp-server v2.0.0 (read from its source, src/platforms/meta/writes.ts and
extended-writes.ts): camelCase ids (adAccountId, campaignId, adSetId, adId), status ACTIVE|PAUSED,
budgets in MAJOR currency units (dailyBudget: 10 = 10.00), writes preview until confirm: true.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_META, BETA_META, META_SELF, Sandbox  # noqa: E402

from godmode import gate  # noqa: E402

ADSET = "120000000000321"


class GetMcpAdsShapes(Sandbox):
    alpha_mode = "guarded_auto"

    def test_preview_is_harmless(self):
        call = {"adAccountId": ALPHA_META, "adSetId": ADSET, "status": "ACTIVE"}
        self.assertIsNone(gate.decide(self.hook(META_SELF + "meta_update_adset_status", call)))

    def test_confirmed_activation_needs_plan(self):
        call = {"adAccountId": ALPHA_META, "adSetId": ADSET, "status": "ACTIVE", "confirm": True}
        self.assertEqual(gate.decide(self.hook(META_SELF + "meta_update_adset_status", call)).decision, gate.DENY)
        self.plan("activate", "--account", ALPHA_META, "--entity", ADSET)
        self.assertEqual(gate.decide(self.hook(META_SELF + "meta_update_adset_status", call)).decision, gate.ASK)

    def test_bare_account_id_for_other_client_is_caught(self):
        call = {"adAccountId": BETA_META.replace("act_", ""), "adSetId": ADSET, "status": "PAUSED", "confirm": True}
        r = gate.decide(self.hook(META_SELF + "meta_update_adset_status", call))
        self.assertEqual(r.decision, gate.DENY)
        self.assertIn("WRONG ACCOUNT", r.reason)

    def test_major_unit_budget_matches_plan(self):
        self.plan("budget", "--account", ALPHA_META, "--entity", ADSET, "--current", "50", "--proposed", "58",
                  "--spend", "900", "--conversions", "22", "--confidence", "HIGH")
        ok = {"adAccountId": ALPHA_META, "adSetId": ADSET, "currency": "USD", "dailyBudget": 58, "confirm": True}
        self.assertEqual(gate.decide(self.hook(META_SELF + "meta_update_adset_budget", ok)).decision, gate.ALLOW)
        wrong = dict(ok, dailyBudget=85)
        self.assertEqual(gate.decide(self.hook(META_SELF + "meta_update_adset_budget", wrong)).decision, gate.DENY)

    def test_confirmed_create_is_paused_create(self):
        call = {"adAccountId": ALPHA_META, "name": "x", "objective": "OUTCOME_LEADS", "currency": "USD",
                "dailyBudget": 40, "confirm": True}
        self.assertEqual(gate.decide(self.hook(META_SELF + "meta_create_campaign", call)).decision, gate.ALLOW)
