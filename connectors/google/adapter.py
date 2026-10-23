"""GoogleAdsAdapter.

Reads and writes are deliberately split across two layers:

  READS  - googleads/google-ads-mcp (official, Apache-2.0). Tools: search
           (GAQL), get_resource_metadata, list_accessible_customers. It is
           READ-ONLY. It cannot create, pause or change anything.
  WRITES - the bundled writer in connectors/google/writer.py, run as
           `adsgm google apply --plan <file> [--ticket tkt_...] [--execute]`.
           It calls the official Google Ads API through Google's
           `google-ads` Python client. Default is validate_only (the API checks
           the mutate and changes nothing); --execute applies it, and the
           write gate requires an approved ticket for that.

Swap the write layer (for example to a hosted connector) by adding a Backend
here and a family in connectors/registry.json.
"""

from ..base import Adapter, Backend

_GAQL = "search (GAQL)"

OFFICIAL_MCP = Backend(
    key="official_mcp",
    name="Google Ads MCP (official, read-only)",
    kind="official_mcp",
    server_hint="google",
    license="Apache-2.0",
    priority=10,
    ops={
        "list_accounts": "list_accessible_customers",
        "account_info": _GAQL,
        "list_campaigns": _GAQL,
        "list_adsets": _GAQL + " on ad_group",
        "list_ads": _GAQL + " on ad_group_ad",
        "insights": _GAQL,
        "breakdowns": _GAQL + " with segments.*",
        "search_terms": _GAQL + " on search_term_view / campaign_search_term_insight",
        "keywords": _GAQL + " on keyword_view",
        "gaql": "search",
    },
    notes=[
        "Use get_resource_metadata to discover selectable fields before writing GAQL.",
        "Tools may be namespaced (customers_list_accessible_customers, search_search) per tools_config.yaml.",
        "Read-only: route every write to the bundled writer.",
    ],
)

BUNDLED_WRITER = Backend(
    key="bundled_writer",
    name="adsgm google apply (Google Ads API via google-ads client)",
    kind="bundled_cli",
    server_hint="adsgm",
    license="MIT (this repo); google-ads client is Apache-2.0",
    priority=20,
    ops={
        "create_campaign": "adsgm google apply --plan plan.json  (op: create_search_campaign)",
        "create_adset": "adsgm google apply --plan plan.json  (op: create_ad_group)",
        "create_ad": "adsgm google apply --plan plan.json  (op: create_rsa)",
        "update_budget": "adsgm google apply --plan plan.json  (op: update_budget)",
        "update_status": "adsgm google apply --plan plan.json  (op: set_status)",
        "pause": "adsgm google apply --plan plan.json  (op: set_status PAUSED)",
        "activate": "adsgm google apply --plan plan.json  (op: set_status ENABLED)",
        "add_negatives": "adsgm google apply --plan plan.json  (op: add_negative_keywords)",
    },
    notes=[
        "Needs `pip install google-ads` and GOOGLE_ADS_* env vars; see .env.example.",
        "validate_only by default; --execute requires a ticket and passes through the write gate.",
        "New campaigns are always created PAUSED.",
    ],
)


class GoogleAdsAdapter(Adapter):
    platform = "google"
    backends = [OFFICIAL_MCP, BUNDLED_WRITER]
