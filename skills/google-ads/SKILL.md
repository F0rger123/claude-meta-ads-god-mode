---
name: google-ads
description: Google Ads expertise - Search, Performance Max, Display/Video analysis, keywords and match types, search terms and negatives, RSAs and assets, budgets, bid strategies, conversion actions, Quality Score, impression share, device/location/schedule, GAQL queries through the official read-only Google Ads MCP, and writes through the bundled validate-first writer. Use with ads-core whenever the work touches a Google Ads account.
---

# Google Ads

Load with `ads-core`. Open references only as needed.

## Which layer does what (never blur this)

| Job | Layer | Notes |
|---|---|---|
| Reads, reports, search terms, QS, impression share | official Google Ads MCP: `search` (GAQL), `get_resource_metadata`, `list_accessible_customers` | read-only |
| Campaign creation (Search) | `adsgm google apply` | always PAUSED |
| Budget changes | `adsgm google apply` (op `update_budget`) | ticket + policy |
| Pause / enable / remove | `adsgm google apply` (op `set_status`) | enable = activation = approval |
| Negative keywords | `adsgm google apply` (op `add_negative_keywords`) | preview first |
| PMax / Display / Video edits | not supported by the bundled writer | recommend in Google Ads UI; say so |

The writer validates with Google (`validate_only`) by default and changes nothing. `--execute` needs a ticket and passes the write gate. Plan format: [references/writer-plan-format.md](references/writer-plan-format.md).

## Reading the account

GAQL patterns for every common question: [references/gaql-cookbook.md](references/gaql-cookbook.md). Always filter by date range and `metrics.cost_micros > 0` to keep results small. Money is in **micros** (divide by 1,000,000). Customer ids are 10 digits without dashes; if access goes through a manager account, the MCP needs the login customer id configured.

## Diagnose in this order

1. **Conversion setup** - which conversion actions are primary (included in "Conversions"), duplicates (form submit + thank-you page view both primary), calls counted at sensible length, enhanced conversions / offline imports, values. Wrong primary actions poison Smart Bidding. See [references/conversion-tracking.md](references/conversion-tracking.md).
2. **Budget vs demand** - Search lost impression share (budget) vs (rank). Budget-limited campaigns with good CPA are scaling candidates; rank-limited ones need quality/bid work, not budget.
3. **Search terms** - wasted spend, intent mismatch, missing negatives, cannibalization between ad groups/campaigns. Workflow: [workflows/search-term-review.md](workflows/search-term-review.md).
4. **Keywords and match types** - [references/match-types-and-negatives.md](references/match-types-and-negatives.md).
5. **Ads and assets** - RSA ad strength is a guide not a KPI; message match with keyword theme and landing page; sitelinks, callouts, call asset, location asset for local.
6. **Quality Score and impression share** - [references/quality-score-and-impression-share.md](references/quality-score-and-impression-share.md).
7. **Bidding** - is the strategy right for conversion volume? [references/bidding.md](references/bidding.md).
8. **Segments** - device, location (user location vs interest), ad schedule. Do not exclude a segment on a few conversions.
9. **Landing page** - speed, mobile, message match, form friction, call tracking.

Campaign types and what is visible for each: [references/campaign-types.md](references/campaign-types.md).

## Workflows

- [workflows/launch-search-campaign.md](workflows/launch-search-campaign.md)
- [workflows/search-term-review.md](workflows/search-term-review.md)
- [workflows/account-audit.md](workflows/account-audit.md)

## Never

- Never claim the official MCP made a change - it cannot.
- Never apply a large negative keyword list without preview + approval (guarded-auto default caps at 10 per change).
- Never add a broad negative that blocks converting queries - check every negative against converting search terms first.
- Never switch bid strategy, primary conversion actions, or conversion values without approval.
- Never move budget between Google and Meta on last-click ROAS alone (see ads-strategy).
