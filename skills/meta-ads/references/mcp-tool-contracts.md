# Meta Ads MCP tool contracts

Source: Meta's published tool list for the Ads MCP server (developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/), read 2026-10-23. Meta changes this surface; if a tool errors on a param, call `ads_get_field_context` and `ads_get_help_article` rather than guessing.

## Connect

```bash
claude mcp add --transport http meta-ads https://mcp.facebook.com/ads
```
Then `/mcp` -> `meta-ads` -> sign in with Facebook Login for Business. Permissions: `ads_mcp_management` plus `ads_read` (read-only) or `ads_management` (writes). Employee-role system-user tokens are supported for programmatic use; Admin-role tokens are not.

## Read tools (gate passes them through)

Accounts and structure: `ads_get_ad_accounts`, `ads_get_ad_account_pages`, `ads_get_pages_for_business`, `ads_get_user_pages`, `ads_get_ad_entities`, `ads_get_field_context`
Reporting: `ads_insights_performance_trend`, `ads_insights_anomaly_signal`, `ads_insights_advertiser_context`, `ads_insights_auction_ranking_benchmarks`, `ads_insights_industry_benchmark`, `ads_get_opportunity_score`
Creative: `ads_get_creatives`, `ads_get_creative_ads`, `ads_get_ad_images`, `ads_get_ad_videos`, `ads_get_ad_preview`, `ads_get_ig_accounts`, `ads_get_ig_media`
Audiences: `ads_get_ad_account_custom_audiences`, `ads_get_custom_audience`, `ads_get_custom_audience_adsets`
Signals: `ads_get_datasets`, `ads_get_dataset_details`, `ads_get_dataset_stats`, `ads_get_dataset_quality`, `ads_pixel_event_read`, `ads_pixel_parameter_read`, `ads_get_customconversions`
Research and help: `ads_library_search`, `ads_get_errors`, `ads_get_help_article`, `ads_account_get_activity_logs`
Experiments: `ads_experiment_list_tests`, `ads_experiment_check_eligibility`, `ads_experiment_abtest_get_test`, `ads_experiment_lift_get_test`
Catalog reads: `ads_catalog_list_*`, `ads_catalog_get_*`, `ads_catalog_event_source_get*`

## Write tools and how the gate treats them

| Tool | Gate action | Needs |
|---|---|---|
| `ads_create_campaign`, `ads_create_ad_set`, `ads_create_ad`, `ads_create_creative` | create | account id in the call, client's account, not ACTIVE |
| `ads_update_entity` | refined from payload: status ACTIVE -> activate, PAUSED -> pause, DELETED/ARCHIVED -> delete, budget fields -> budget, geo -> geo_expansion, pixel/promoted_object -> tracking, bid -> bid, else update | matching ticket |
| `ads_activate_entity`, `ads_boost_ig_post` | activate (starts spend) | ticket + human approval |
| `ads_create_custom_audience`, `ads_update_custom_audience*` | audience | ticket |
| `ads_delete_custom_audience`, catalog deletes | delete | ticket + approval |
| `ads_pixel_*` writes, `ads_catalog_event_source_connect/disconnect` | tracking | ticket + approval |
| `ads_experiment_abtest_create_test`, `..._update_test`, `ads_experiment_lift_create_test` | experiment | ticket |

There is no campaign delete tool and no billing/admin tool on the official server - by design.

## Paused-first launch sequence

1. `ads_get_ad_accounts` -> confirm the client's `act_` id, currency, timezone, account status, that a payment method exists (if not: stop, human fixes it).
2. `ads_get_ad_account_pages` -> confirm the client's Page (`platforms.meta.page_id`).
3. `ads_get_datasets` / `ads_get_dataset_quality` -> confirm the client's dataset and that the optimization event fires.
4. `ads_create_campaign` (objective, special_ad_categories, budget if Advantage+ campaign budget) -> PAUSED.
5. `ads_create_ad_set` (optimization goal, promoted object = client dataset + event, geo, age, placements, schedule, budget if no CBO) -> PAUSED.
6. `ads_create_creative` (Page id, image hash/video id, primary text, headline, description, CTA, URL with UTMs).
7. `ads_create_ad` (ad set id + creative id) -> PAUSED.
8. `ads_get_ad_preview` for each ad; read back campaign/ad set/ad and show the user exactly what exists.
9. **Stop.** Activation is a separate request: `adsgm plan activate --entity <campaign id>`, user approves, then `ads_activate_entity`.

## Param quirks (verify with ads_get_field_context)

- Some complex params (targeting, promoted_object) are passed as JSON strings.
- Budgets in minor units (cents). Read currency from the account first; JPY/KRW etc. have no minor unit.
- Account ids: tools usually want `act_<digits>`; the profile stores the same form.
