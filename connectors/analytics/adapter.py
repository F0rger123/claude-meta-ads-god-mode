"""AnalyticsAdapter: GA4 and Search Console, read-only.

  GA4 - googleanalytics/google-analytics-mcp (official, Apache-2.0). Tools:
        get_account_summaries, get_property_details, run_report,
        run_realtime_report, run_funnel_report,
        get_custom_dimensions_and_metrics, list_google_ads_links.
        (create_property_annotation is its only write; the gate treats it as a
        tracking change needing approval.)
  GSC - no official Google MCP exists. Use any installed Search Console
        connector (server name containing "search-console"/"gsc"/"seo"), or
        skip; ads analysis never depends on it.
"""

from ..base import Adapter, Backend

GA4 = Backend(
    key="ga4_official",
    name="Google Analytics MCP (official)",
    kind="official_mcp",
    server_hint="analytics",
    license="Apache-2.0",
    priority=10,
    ops={
        "ga4_report": "run_report",
        "list_accounts": "get_account_summaries",
        "account_info": "get_property_details",
    },
    notes=["list_google_ads_links confirms GA4 <-> Google Ads linking for a property."],
)

GSC = Backend(
    key="gsc_any",
    name="Search Console (any installed connector)",
    kind="hosted_mcp",
    server_hint="search",
    priority=30,
    ops={"gsc_query": "the installed connector's search analytics query tool"},
    notes=["Optional. Used for landing-page and query-intent context only."],
)


class AnalyticsAdapter(Adapter):
    platform = "analytics"
    backends = [GA4, GSC]
