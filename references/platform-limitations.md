# Platform and connector limitations (PLATFORM FACT unless marked)

Checked 2026-10-23. Sources: developers.facebook.com/docs/graph-api/changelog, developers.facebook.com/docs/marketing-api/overview/rate-limiting, developers.google.com/google-ads/api/docs/release-notes, .../productionize/access-levels, .../productionize/rate-limits.

## Meta Marketing API

- Graph API versions: v26.0 (2026-07-29, latest), v25.0 (2026-02-18), v24.0 (2025-10-08). Marketing API auto-upgrade began 2026-07-29; Marketing API v24 listed "available until 2026-10-06" - treat v24 as sunset.
- Ad-account rate score: read = 1 point, write = 3 points. Development tier max 60 (block 300 s); Full access max 9000 (block 60 s). Watch `X-Ad-Account-Usage`, `X-Business-Use-Case`, `X-FB-Ads-Insights-Throttle`.
- Mutations: 100 QPS per app per ad account (error 613 / 5044001).
- Same object: one edit per 30 s (subcode 4841018).
- **Ad set budget changes: 4 per hour per ad set** (613 / 1487632).
- **Account spend-limit changes: 10 per day** (17 / 1885172) - and spend limits are human-only here anyway.
- Access tiers renamed: Standard -> Limited, Advanced -> Full; Full access threshold 500 Marketing API calls in 15 days.
- Insights: 7-day-view and 28-day-view windows removed from the API since 2026-01-12; unique/hourly breakdowns limited to 13 months, frequency breakdowns to 6 months.
- Budgets in minor currency units.
- HEURISTIC: bursts of automated writes can trigger integrity systems; space changes.

## Official Meta Ads MCP

- Hosted; access requires `ads_mcp_management` + `ads_read`/`ads_management`. Employee-role system users only (not Admin).
- No campaign delete tool, no billing/admin tools. Creative multi-media optimization "limited availability".
- Per-call account selection behaviour not fully documented - always pass the account id explicitly.

## Google Ads API

- Latest v26 (2026-10-14); v25 (2026-07-22); v24 (2026-04-22); v23 (2026-01-28). Check the sunset table before pinning.
- Developer token access: Test (test accounts only), Explorer, Basic, Standard (Standard review can take days-weeks; RMF applies to Standard).
- Rate limits: QPS per customer id + developer token (token bucket) plus operations per minute; `RESOURCE_TEMPORARILY_EXHAUSTED` -> exponential backoff with jitter.
- Money in micros. `validate_only` validates a mutate without applying it.
- Official Google Ads MCP: read-only (`search`, `get_resource_metadata`, `list_accessible_customers`).
- Performance Max: search terms only as insight categories; limited asset-level control.
- Google may spend up to 2x average daily budget on a given day, keeping the month at or under 30.4x daily.

## Bundled Google writer (this repo)

- Supports: Search campaign creation (budget, campaign, geo/proximity, language, campaign negatives, ad groups, keywords, RSA), budget updates, status changes (campaign, ad group, ad, keyword), campaign negative keywords.
- Not yet: assets (sitelinks, callouts, call, location), PMax/Display/Video creation, shared negative lists, bid adjustments, audiences, conversion actions. Recommend these in the UI and say so.
