import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers import GOOGLE, META, META_SELF, ROOT  # noqa: E402

sys.path.insert(0, ROOT)
from connectors.analytics import AnalyticsAdapter  # noqa: E402
from connectors.base import CapabilityNotSupported  # noqa: E402
from connectors.google import GoogleAdsAdapter  # noqa: E402
from connectors.meta import MetaAdsAdapter  # noqa: E402
from godmode import actions as A  # noqa: E402
from godmode.classify import classify  # noqa: E402


class ClassifyOfficialMeta(unittest.TestCase):
    def test_reads(self):
        for tool in ("ads_get_ad_accounts", "ads_insights_performance_trend", "ads_library_search",
                     "ads_get_dataset_quality", "ads_account_get_activity_logs", "ads_pixel_event_read"):
            self.assertEqual(classify(META + tool).action, A.READ, tool)

    def test_writes(self):
        cases = {"ads_create_campaign": A.CREATE, "ads_create_ad_set": A.CREATE, "ads_create_ad": A.CREATE,
                 "ads_activate_entity": A.ACTIVATE, "ads_update_entity": A.UPDATE,
                 "ads_boost_ig_post": A.ACTIVATE, "ads_delete_custom_audience": A.DELETE,
                 "ads_pixel_event_create": A.TRACKING, "ads_catalog_product_set_delete": A.DELETE,
                 "ads_experiment_abtest_create_test": A.EXPERIMENT}
        for tool, action in cases.items():
            c = classify(META + tool)
            self.assertEqual((c.platform, c.action), ("meta", action), tool)

    def test_unknown_tool_on_meta_server_is_unknown_write(self):
        self.assertEqual(classify(META + "ads_brand_new_thing").action, A.UNKNOWN_WRITE)

    def test_non_ads_tools_ignored(self):
        self.assertIsNone(classify("mcp__gmail__search_threads"))
        self.assertIsNone(classify("mcp__uploads-service__create_file"))
        self.assertIsNone(classify("Read", {"file_path": "x"}))
        self.assertIsNone(classify("Bash", {"command": "ls"}))


class ClassifySelfHosted(unittest.TestCase):
    def test_write_without_confirm_is_preview(self):
        c = classify(META_SELF + "meta_update_adset_budget", {"adSetId": "123", "dailyBudget": 50})
        self.assertEqual(c.action, A.PREVIEW)

    def test_write_with_confirm_is_write(self):
        c = classify(META_SELF + "meta_update_adset_budget", {"adSetId": "123", "dailyBudget": 50, "confirm": True})
        self.assertEqual(c.action, A.BUDGET)
        c = classify(META_SELF + "meta_update_campaign_status", {"campaignId": "1", "status": "ACTIVE", "confirm": "true"})
        self.assertEqual(c.action, A.UPDATE)

    def test_reads(self):
        self.assertEqual(classify(META_SELF + "meta_get_insights").action, A.READ)
        self.assertEqual(classify(META_SELF + "meta_validate_query").action, A.READ)


class ClassifyGoogleAndAnalytics(unittest.TestCase):
    def test_official_google_mcp_reads(self):
        for tool in ("search", "get_resource_metadata", "list_accessible_customers",
                     "customers_list_accessible_customers", "search_search"):
            c = classify(GOOGLE + tool)
            self.assertEqual((c.platform, c.action), ("google", A.READ), tool)

    def test_unexpected_google_tool_is_unknown_write(self):
        self.assertEqual(classify(GOOGLE + "mutate_campaigns").action, A.UNKNOWN_WRITE)

    def test_analytics(self):
        self.assertEqual(classify("mcp__google-analytics__run_report").action, A.READ)
        self.assertEqual(classify("mcp__google-analytics__create_property_annotation").action, A.TRACKING)

    def test_bash_google_writer(self):
        cmd = 'python "/x/adsgm.py" google apply --plan p.json --ticket tkt_1 --execute'
        self.assertEqual(classify("Bash", {"command": cmd}).family, "godmode_google_writer")
        self.assertIsNone(classify("Bash", {"command": 'python adsgm.py google apply --plan p.json'}))

    def test_generic_third_party(self):
        c = classify("mcp__adplane__google_update_object", {"status": "ENABLED"})
        self.assertEqual(c.platform, "google")
        c = classify("mcp__adplane__meta_get_insights")
        self.assertEqual(c.action, A.READ)


class AdapterRouting(unittest.TestCase):
    def test_meta_prefers_official(self):
        r = MetaAdsAdapter().route("create_campaign", ["plugin_ads_meta-ads", "selfhosted"])
        self.assertEqual((r.backend, r.tool, r.is_write), ("official", "ads_create_campaign", True))

    def test_meta_falls_back_to_selfhosted(self):
        r = MetaAdsAdapter().route("update_budget", ["selfhosted"])
        self.assertEqual(r.backend, "selfhosted")

    def test_meta_capability_gap_is_reported_not_faked(self):
        with self.assertRaises(CapabilityNotSupported):
            MetaAdsAdapter().route("ad_library", ["selfhosted"])

    def test_google_reads_use_official_mcp(self):
        r = GoogleAdsAdapter().route("search_terms")
        self.assertEqual(r.backend, "official_mcp")
        self.assertFalse(r.is_write)

    def test_google_writes_never_route_to_read_only_mcp(self):
        for op in ("create_campaign", "update_budget", "pause", "add_negatives"):
            self.assertEqual(GoogleAdsAdapter().route(op).backend, "bundled_writer", op)
        with self.assertRaises(CapabilityNotSupported):
            GoogleAdsAdapter().route("update_budget", ["google-ads-mcp"])

    def test_connector_missing_entirely(self):
        with self.assertRaises(CapabilityNotSupported):
            MetaAdsAdapter().route("insights", [])

    def test_analytics(self):
        self.assertEqual(AnalyticsAdapter().route("ga4_report").tool, "run_report")


if __name__ == "__main__":
    unittest.main()
