# Attribution, pixel, datasets and Conversions API

## Attribution windows - PLATFORM FACT (changed 2026)

- Meta announced on 2025-10-16 (developers.facebook.com/blog/post/2025/10/16/ads-insights-api-metric-availability-updates/) that from **2026-01-12** the Ads Insights API no longer returns **7-day view** and **28-day view** attribution windows (including combinations such as 7-day click + 28-day view).
- Still available: **1-day click, 7-day click, 28-day click, 1-day engaged-view, 1-day view**, plus the ad set's configured default.
- Same announcement: unique-count and hourly breakdowns limited to 13 months of history; frequency breakdowns to 6 months.
- Consequence: year-over-year or pre/post-January-2026 comparisons that relied on view-through windows are not like-for-like. Flag it in every report spanning that date.
- Third-party claims about further 2026 changes (for example click attribution counting only link clicks) are **unverified** - check Meta's docs before relying on them.

## Choosing the attribution setting (BEST PRACTICE)

- Lead gen with short consideration: 7-day click (+ 1-day view if the client accepts view-through credit). Report the window used.
- Never change an ad set's attribution setting without approval - it changes what the optimizer learns from and breaks trend comparisons (tracking change).
- Platform-reported conversions are a model, not truth. Rank evidence: CRM-qualified outcomes > GA4/server data > platform-reported.

## Pixel + Conversions API (CAPI) - PLATFORM FACT

- Meta Pixel (browser) and Conversions API (server) can send the same event. They are **deduplicated** when both carry the same `event_name` and `event_id` (and the server event's `action_source` is set). Missing or mismatched `event_id` = double counting.
- **Event Match Quality (EMQ)** scores how well customer information parameters (hashed email, phone, external_id, fbp/fbc, IP/user agent) match Meta users. Low EMQ weakens optimization and attribution.
- Datasets group pixel + CAPI + offline events. Make sure the ad set's promoted object points at the client's own dataset (wrong dataset = account mismatch).

## Checks (read-only, via official MCP)

- `ads_get_datasets`, `ads_get_dataset_details`, `ads_get_dataset_stats`, `ads_get_dataset_quality` - volume, dedup, match quality.
- `ads_pixel_event_read`, `ads_get_customconversions` - which events/custom conversions exist.
- Compare event counts with GA4 key events and CRM leads for the same days. A >30% unexplained gap (HEURISTIC) is a tracking issue to investigate before optimizing.

## Common failures

| Symptom | Likely cause |
|---|---|
| Leads in Meta ≈ 2x CRM | pixel + CAPI without dedup, or thank-you page reloads |
| Leads in Meta ≪ CRM | event not on all forms, CAPI missing, consent banner blocking, wrong dataset |
| Optimization event "Lead" but conversions are PageView | wrong event chosen at ad set level |
| Sudden drop to zero | site redeploy removed pixel/GTM tag, domain change, token expired on CAPI gateway |

All fixes that change event definitions, ad set optimization events, or dataset connections are **tracking changes** - plan with `adsgm plan tracking` and get approval.
