# GAQL cookbook (official Google Ads MCP `search` tool)

API version at time of writing: Google Ads API **v26** (released 2026-10-14; developers.google.com/google-ads/api/docs/release-notes). Use `get_resource_metadata` to confirm fields if a query errors. All money fields are micros.

## Campaign performance (last 30 days)

```sql
SELECT campaign.id, campaign.name, campaign.status, campaign.advertising_channel_type,
       campaign.bidding_strategy_type, campaign_budget.amount_micros,
       metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions,
       metrics.conversions_value, metrics.cost_per_conversion,
       metrics.search_impression_share, metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS AND campaign.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
```

## Search terms with spend and no conversions (wasted spend)

```sql
SELECT search_term_view.search_term, search_term_view.status, campaign.name, ad_group.name,
       metrics.cost_micros, metrics.clicks, metrics.impressions, metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS AND metrics.cost_micros > 0
ORDER BY metrics.cost_micros DESC
LIMIT 500
```
Filter `conversions = 0` client-side so you still see what converted (needed to check negatives against converters).

## Performance Max search term insights (categories, not raw queries)

```sql
SELECT campaign_search_term_insight.category_label, campaign_search_term_insight.id,
       metrics.clicks, metrics.impressions, metrics.conversions
FROM campaign_search_term_insight
WHERE segments.date DURING LAST_30_DAYS AND campaign_search_term_insight.campaign_id = 1234567890
```
Requires a single campaign id filter.

## Keywords with Quality Score

```sql
SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
       ad_group_criterion.status, ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.quality_info.creative_quality_score,
       ad_group_criterion.quality_info.post_click_quality_score,
       ad_group_criterion.quality_info.search_predicted_ctr,
       metrics.cost_micros, metrics.clicks, metrics.conversions
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS AND ad_group_criterion.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
```

## Existing negatives

```sql
SELECT campaign.name, campaign_criterion.keyword.text, campaign_criterion.keyword.match_type
FROM campaign_criterion
WHERE campaign_criterion.negative = TRUE AND campaign_criterion.type = 'KEYWORD'
```
Plus shared negative lists: `shared_criterion` joined via `campaign_shared_set`.

## Conversion actions

```sql
SELECT conversion_action.id, conversion_action.name, conversion_action.status, conversion_action.type,
       conversion_action.category, conversion_action.primary_for_goal,
       conversion_action.counting_type, conversion_action.value_settings.default_value
FROM conversion_action
WHERE conversion_action.status = 'ENABLED'
```

## Conversions by conversion action (find duplicates)

```sql
SELECT segments.conversion_action_name, metrics.all_conversions, metrics.conversions
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

## Device / location / hour

```sql
SELECT segments.device, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date DURING LAST_30_DAYS
SELECT geographic_view.country_criterion_id, geographic_view.location_type, segments.geo_target_city,
       metrics.cost_micros, metrics.conversions FROM geographic_view WHERE segments.date DURING LAST_30_DAYS
SELECT segments.day_of_week, segments.hour, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date DURING LAST_30_DAYS
```
`location_type` separates LOCATION_OF_PRESENCE from AREA_OF_INTEREST - spend from outside the service area shows here.

## Ads and assets

```sql
SELECT ad_group.name, ad_group_ad.ad.id, ad_group_ad.ad.final_urls, ad_group_ad.ad_strength,
       ad_group_ad.ad.responsive_search_ad.headlines, ad_group_ad.status, metrics.clicks, metrics.conversions
FROM ad_group_ad WHERE ad_group_ad.status != 'REMOVED' AND segments.date DURING LAST_30_DAYS
```

## Change history (recent major changes)

```sql
SELECT change_event.change_date_time, change_event.change_resource_type, change_event.client_type,
       change_event.user_email, change_event.resource_change_operation, change_event.changed_fields
FROM change_event
WHERE change_event.change_date_time DURING LAST_14_DAYS
ORDER BY change_event.change_date_time DESC LIMIT 100
```
(`change_event` requires a date filter within the last 30 days and a LIMIT.)
