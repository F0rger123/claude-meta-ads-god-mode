"""Build real Google Ads API requests with Google's own client library (no network).

Skipped unless `google-ads` is installed (CI installs it on one Python version).
Catches field-name drift between our writer and the current API version.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import ALPHA_GOOGLE, Sandbox  # noqa: E402

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.oauth2.credentials import Credentials
    HAVE_LIB = True
except ImportError:  # pragma: no cover - depends on environment
    HAVE_LIB = False


@unittest.skipUnless(HAVE_LIB, "google-ads not installed")
class RealGoogleClient(Sandbox):
    def client(self):
        # Offline credentials: constructing the client makes no network call; no developer token needed.
        return GoogleAdsClient(Credentials(token="offline-test"), use_proto_plus=True)

    def plan(self):
        return {"client": "alpha-remodeling", "customer_id": ALPHA_GOOGLE, "operations": [
            {"op": "update_budget", "campaign_budget_id": "111", "amount": 65.0},
            {"op": "set_status", "resource": "campaign", "id": "222", "status": "PAUSED"},
            {"op": "set_status", "resource": "ad_group_ad", "ad_group_id": "333", "id": "444", "status": "PAUSED"},
            {"op": "set_status", "resource": "ad_group_criterion", "ad_group_id": "333", "id": "555", "status": "ENABLED"},
            {"op": "add_negative_keywords", "campaign_id": "222", "keywords": [{"text": "diy", "match_type": "PHRASE"}]},
            {"op": "create_search_campaign", "name": "Real proto check", "daily_budget": 60,
             "bidding": {"strategy": "maximize_conversions", "target_cpa": 80},
             "proximity": {"lat": 39.96, "lng": -76.72, "radius_miles": 25}, "locations": ["1025197"],
             "negative_keywords": [{"text": "jobs", "match_type": "PHRASE"}],
             "ad_groups": [{"name": "Core", "cpc_bid": 4.5,
                            "keywords": [{"text": "kitchen remodel", "match_type": "EXACT"}],
                            "rsa": {"headlines": ["Kitchen Remodeling", "Free Design Consult", "Local Craftsmen"],
                                    "descriptions": ["Plan your new kitchen with us.", "Book a free consult."],
                                    "final_url": "https://www.example.com/k", "path1": "kitchen", "path2": "york"}}]},
        ]}

    def test_writer_builds_valid_protos(self):
        from connectors.google import writer
        client = self.client()
        svc, ops = writer._to_mutate_operations(client, ALPHA_GOOGLE, writer.normalize(self.plan()))
        req = client.get_type("MutateGoogleAdsRequest")
        req.customer_id = ALPHA_GOOGLE
        req.mutate_operations.extend(ops)
        req.validate_only = True
        self.assertEqual(len(req.mutate_operations), 14)
        kinds = [o._pb.WhichOneof("operation") for o in ops]
        self.assertEqual(kinds.count("campaign_criterion_operation"), 5)
        created = [o.campaign_operation.create for o in ops
                   if o._pb.WhichOneof("operation") == "campaign_operation" and o.campaign_operation._pb.HasField("create")]
        c = created[0]
        self.assertEqual(c.status.name, "PAUSED")
        self.assertEqual(c.geo_target_type_setting.positive_geo_target_type.name, "PRESENCE")
        self.assertEqual(c.contains_eu_political_advertising.name, "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING")
        self.assertEqual(c.maximize_conversions.target_cpa_micros, 80_000_000)
        budget_update = ops[0].campaign_budget_operation
        self.assertEqual(list(budget_update.update_mask.paths), ["amount_micros"])
        self.assertEqual(budget_update.update.amount_micros, 65_000_000)
