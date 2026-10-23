# Delivery diagnostics

## Statuses to read first

`effective_status` on campaign/ad set/ad (ACTIVE, PAUSED, CAMPAIGN_PAUSED, ADSET_PAUSED, DISAPPROVED, PENDING_REVIEW, WITH_ISSUES, IN_PROCESS, ARCHIVED, DELETED) and the learning stage (learning, learning limited, active). A "PAUSED" campaign with ACTIVE children still spends nothing; an ACTIVE campaign with a DISAPPROVED ad delivers through the other ads only.

## Official MCP tools that help

| Tool | Use |
|---|---|
| `ads_get_ad_entities` | structure, statuses, budgets |
| `ads_insights_performance_trend` | time series for spend/results |
| `ads_insights_anomaly_signal` | Meta's own anomaly detection - start an emergency check here |
| `ads_insights_auction_ranking_benchmarks` | quality / engagement / conversion rate ranking vs ads competing for the same audience |
| `ads_insights_industry_benchmark` | context only; never a target |
| `ads_get_opportunity_score` | Meta's recommendations - evaluate, do not auto-apply |
| `ads_get_errors` | error codes and fixes |
| `ads_account_get_activity_logs` | who changed what and when (recent major changes) |

Self-hosted equivalents: `meta_get_delivery_diagnostics`, `meta_get_entity_configuration`, `meta_get_ad_activity`.

## Under-delivery checklist

1. Payment issue / account disabled (human fixes in Ads Manager).
2. Ads in review or rejected.
3. Cost goal / bid cap set below achievable CPA.
4. Audience too small after geo + exclusions (radius in rural areas).
5. Budget too low for the optimization event.
6. Schedule / end date passed.
7. Overlap: several ad sets targeting the same people compete in the same auctions.

## Relevance rankings (PLATFORM FACT: diagnostic, not a ranking factor you set)

Below-average quality ranking -> creative perceived as low quality / clickbait. Below-average engagement -> hook/creative. Below-average conversion rate -> landing page / offer / audience fit. Use them to pick which part to fix, never as the sole reason to pause.

## Recommendations from Meta (opportunity score)

Each suggestion goes through the same evidence check as any other recommendation. Some (e.g., "raise budget", "use Advantage+ audience") are reasonable; apply only with a plan and, where required, approval.
