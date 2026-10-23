# Tracking & Signal Quality

Meta optimizes for exactly what you feed it. Feeding it raw form-fills gets you form-fillers; feeding it qualified-stage events gets you qualified leads. Signal setup is the highest-leverage work in the account.

## The required stack
1. **Pixel** on every page, standard events on key actions.
2. **CAPI** (server-side) alongside — browser-only loses a large share of events to tracking prevention.
3. **Deduplication**: identical `event_id` on the pixel and CAPI copies of the same event; target ≥90% dedup rate in Events Manager.
4. **EMQ (Event Match Quality)** on the optimized event: send hashed email (`em`, biggest lift), phone (`ph`), name, city/state/zip, and `external_id` (cross-device). Targets: purchase-type events ≥8, mid-funnel ≥6.5, PageView ≥5.5. EMQ <6 on the event you optimize on is a fix-before-anything-else problem.
5. **Never hash `fbp`/`fbc`** (browser/click ids) — hashing them breaks matching entirely.
6. **Domain verified**; Events Manager freshness lag <4h.

## CRM feedback loop (B2B: Conversion Leads)
The compounding move: teach Meta which leads were *good*.
- Capture and store **fbclid / Meta Lead ID at lead creation** and carry it through every CRM stage change. Without the stored click id, downstream events can't attribute back to the ad and the whole loop silently breaks.
- Send stage changes (Lead → MQL → SQL/Opportunity → Customer) back daily via CAPI / Conversion Leads integration.
- Optimize on the deepest stage that still fires ~10+/week per ad set (50/week exits learning). Gates for Conversion Leads optimization: roughly ≥200 leads/month account-wide, and the optimized stage converting at 1–40% from raw lead.
- Middleware (e.g., n8n) over native CRM connectors when: EMQ is low (hash more identifiers yourself), multiple destinations, or custom filtering.

## Verification protocol (before launch, after any site change)
1. Events Manager → Test Events: fire the event yourself, watch it arrive (both pixel and server, deduped).
2. Check EMQ score on the optimized event.
3. Confirm the event fires exactly once per action (double-fires poison CPA reporting).
4. Cheap insurance: have two people independently verify tracking before spending — broken tracking silently burns whole budgets, and "Meta stopped working" reports are tracking bugs more often than delivery problems.

## UTM discipline
Template every ad: `utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}` (dynamic parameters). This is what makes CRM-side ad-level quality attribution possible — no UTMs, no feedback loop, no quality scoring.

## Attribution sanity
- Know the account's setting (commonly 7-day click / 1-day view) and state it in every report.
- Platform numbers overclaim vs. CRM/blended truth (often 20–40%) — treat platform conversions as a directional optimization signal, CRM as the money truth.
- Never compare or sum windows across platforms without reconciling definitions.
