---
name: ads-tracking
description: Conversion tracking and attribution diagnostics - Meta Pixel, Conversions API, datasets, Event Match Quality, Google Ads conversion actions, GA4 key events, GTM, UTM parameters, CRM attribution and landing-page events. Detects missing tracking, duplicates, wrong events, broken UTMs, missing conversion actions, wrong destinations, account mismatches and attribution gaps. Use for "is tracking working", "pixel", "CAPI", "conversions look wrong", "GA4 doesn't match".
---

# Ads tracking

Tracking is checked before any performance conclusion. All diagnostics are read-only; every fix that changes events, conversion actions, datasets, tags or attribution settings is a **tracking** action: `adsgm plan tracking ...`, approval required, never destructive without approval.

Platform detail: Meta - [skills/meta-ads/references/attribution-and-signals.md](../meta-ads/references/attribution-and-signals.md); Google - [skills/google-ads/references/conversion-tracking.md](../google-ads/references/conversion-tracking.md); concepts - [references/attribution.md](../../references/attribution.md).

## Diagnostic sequence

1. **Inventory** - from the profile and platforms: Meta dataset ids + events + custom conversions; Google conversion actions (primary?); GA4 key events (`run_report` on `eventName` with `keyEvents`); GTM container (if accessible); landing pages and their forms/phone numbers.
2. **Fire check** - for each conversion path (form, call, booking): is there a Meta event, a Google conversion, a GA4 key event? Open the landing page in the browser and inspect network requests on submit when needed (test submissions only with the user's OK; never submit personal data).
3. **Volume reconciliation** - same 14-30 days, by day: CRM leads vs Meta reported vs Google reported vs GA4 key events. Explain gaps (attribution windows, view-through, cross-device, consent, duplicates).
4. **Duplicates** - pixel + CAPI without shared `event_id`; Google tag + GA4 import both primary; thank-you page reloads; multiple tags in GTM.
5. **Wrong event / destination** - ad set optimizing for PageView/ViewContent; conversion action "page view" primary; ads sending to a URL without the tag; final URL redirects dropping parameters.
6. **UTMs** - every ad has utm_source/medium/campaign (+content); consistent naming; no spaces/uppercase chaos; GA4 shows the sessions under the expected source/medium.
7. **Account mismatch** - pixel/dataset/conversion action owned by another business or account; GA4 property linked to the wrong Google Ads customer.
8. **Attribution gaps** - no CRM feedback (offline conversions/CAPI for qualified leads); calls not tracked; Jan-2026 Meta view-window removal affecting comparisons.

## Output

Table: issue · evidence · impact on optimization/reporting · severity · fix · who does it (Claude via tool with approval / developer / client) · approval.
