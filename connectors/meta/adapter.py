"""MetaAdsAdapter.

Backends, in preference order:
  1. official  - Meta Ads MCP (https://mcp.facebook.com/ads). Meta-hosted,
                 OAuth via Facebook Login for Business, creates PAUSED,
                 ads_activate_entity is the only path to spend.
  2. selfhosted - getmcpads-com/meta-ads-mcp-server (Apache-2.0). Local stdio,
                 your own System User token, writes off by default
                 (META_ENABLE_WRITES=1), every write previews until called
                 again with confirm: true. Used when the official server is not
                 enabled for an account or lacks a field/breakdown.

Tool names for the official server come from Meta's published tool list
(developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/
ads-mcp-server). Self-hosted names follow the getmcpads README; confirm with
meta_health_check / tools/list after install because they may change.
"""

from ..base import Adapter, Backend

OFFICIAL = Backend(
    key="official",
    name="Meta Ads MCP (official)",
    kind="official_mcp",
    server_hint="meta",
    license="Meta Platform Terms (hosted service)",
    priority=10,
    ops={
        "list_accounts": "ads_get_ad_accounts",
        "account_info": "ads_get_ad_accounts",
        "list_campaigns": "ads_get_ad_entities",
        "list_adsets": "ads_get_ad_entities",
        "list_ads": "ads_get_ad_entities",
        "insights": "ads_insights_performance_trend",
        "breakdowns": "ads_insights_performance_trend",
        "creatives": "ads_get_creatives",
        "ad_preview": "ads_get_ad_preview",
        "audiences": "ads_get_ad_account_custom_audiences",
        "datasets": "ads_get_datasets",
        "dataset_quality": "ads_get_dataset_quality",
        "activity_log": "ads_account_get_activity_logs",
        "ad_library": "ads_library_search",
        "create_campaign": "ads_create_campaign",
        "create_adset": "ads_create_ad_set",
        "create_ad": "ads_create_ad",
        "create_creative": "ads_create_creative",
        "update_budget": "ads_update_entity",
        "update_status": "ads_update_entity",
        "pause": "ads_update_entity",
        "activate": "ads_activate_entity",
        "update_targeting": "ads_update_entity",
        "update_bid": "ads_update_entity",
        "create_experiment": "ads_experiment_abtest_create_test",
    },
    notes=[
        "Use ads_get_field_context before unfamiliar fields; params are sometimes JSON strings.",
        "Also offers ads_insights_anomaly_signal, ads_insights_auction_ranking_benchmarks, "
        "ads_get_opportunity_score, ads_get_errors.",
        "No campaign delete tool: pause instead. Billing and admin are not exposed.",
    ],
)

SELFHOSTED = Backend(
    key="selfhosted",
    name="getmcpads meta-ads-mcp-server (self-hosted)",
    kind="selfhosted_mcp",
    server_hint="meta",
    license="Apache-2.0",
    priority=20,
    ops={
        "list_accounts": "meta_list_ad_accounts",
        "account_info": "meta_get_account_details",
        "list_campaigns": "meta_get_campaigns",
        "list_adsets": "meta_get_adsets",
        "list_ads": "meta_get_ads",
        "insights": "meta_get_insights",
        "breakdowns": "meta_get_insights",
        "creatives": "meta_get_creatives",
        "ad_preview": "meta_get_ad_preview",
        "audiences": "meta_get_audiences",
        "datasets": "meta_get_pixels",
        "activity_log": "meta_get_ad_activity",
        "create_campaign": "meta_create_campaign",
        "create_adset": "meta_create_adset",
        "create_ad": "meta_create_ad",
        "create_creative": "meta_create_adcreative",
        "update_budget": "meta_update_adset_budget | meta_update_campaign_budget",
        "update_status": "meta_update_campaign_status | meta_update_adset_status | meta_update_ad_status",
        "pause": "meta_update_campaign_status | meta_update_adset_status | meta_update_ad_status",
        "activate": "meta_update_campaign_status | meta_update_adset_status | meta_update_ad_status",
        "update_targeting": "meta_update_adset_configuration",
    },
    notes=[
        "Writes register only with META_ENABLE_WRITES=1, and apply only on a second call with confirm: true.",
        "meta_get_delivery_diagnostics and meta_get_entity_configuration explain delivery problems.",
        "meta_validate_query checks metric/breakdown combinations before spending an API call.",
        "Run meta_health_check first; it reports missing scopes without printing the token.",
    ],
)


class MetaAdsAdapter(Adapter):
    platform = "meta"
    backends = [OFFICIAL, SELFHOSTED]
