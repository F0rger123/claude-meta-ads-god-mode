# Google Ads conversion tracking

## Check

1. List enabled conversion actions with `primary_for_goal`, `counting_type`, category, value ([gaql-cookbook.md](gaql-cookbook.md#conversion-actions)).
2. Conversions by action for the last 30 days - more than one primary action counting the same lead = double counting (e.g., "form submit" event + "thank-you page view").
3. Lead gen should usually count **one** per interaction (`ONE_PER_CLICK`); purchases count every.
4. Calls: calls from ads with a minimum duration (e.g., 60 s) and website call conversions via forwarding numbers; not every click-to-call tap.
5. GA4-imported conversions vs Google tag conversions: do not have both primary for the same action.
6. Enhanced conversions for leads / offline conversion import from CRM: recommended when CRM qualification exists (BEST PRACTICE).
7. Compare Google Ads conversions with GA4 key events and CRM leads by day; large unexplained gaps = tracking issue.
8. GA4 <-> Google Ads link: `list_google_ads_links` on the GA4 MCP.

## Conversion lag (PLATFORM FACT + HEURISTIC)

Google attributes conversions to the click date. Recent days are undercounted until the lag passes. Lead gen lag is often 1-7 days; longer for considered purchases. Read `metrics.conversions` by `segments.conversion_lag_bucket` (or compare a closed older window) before judging the last few days.

## Changes

Changing which action is primary, counting type, values, or attribution model changes what Smart Bidding optimizes - always `tracking` action, approval required, and note it in the change log because trend lines break.
