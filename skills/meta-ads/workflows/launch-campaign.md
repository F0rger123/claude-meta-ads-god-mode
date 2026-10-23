# Meta campaign build (paused-first)

Example request: "Build a Meta campaign for D-Hauss Remodeling targeting homeowners around York, PA for kitchen remodel leads at $60/day."

Follow the generic flow in [workflows/campaign-launch.md](../../../workflows/campaign-launch.md); this file holds the Meta specifics.

## 1. Context (read-only)

- `adsgm use "D-Hauss"`; read `business`, `economics`, `platforms.meta`, `geographic_limits`, `prohibited_claims`, `brand_voice`.
- `ads_get_ad_accounts`: the profile's `act_` id is present, ACTIVE, has payment, currency known.
- `ads_get_ad_entities`: existing campaigns. Overlap? An existing kitchen campaign means extend or replace, not duplicate.
- `ads_get_dataset_quality`: Lead event firing, deduped, EMQ acceptable. If broken, the campaign can still be **drafted** but recommend fixing tracking before activation.

## 2. Strategy decisions (write them down)

| Decision | Default for local lead gen | Change when |
|---|---|---|
| Objective | Leads, website conversion location | instant forms only if CRM qualification is fast |
| Optimization event | client's primary lead event | volume < ~10/week across account: consider a higher-funnel proxy as EXPERIMENT |
| Budget | campaign-level (Advantage+ campaign budget), daily | lifetime for a fixed-length test |
| Bid | highest volume | cost goal only with stable history |
| Ad sets | 1 (broad homeowners in radius) | 2 if testing a genuinely different audience idea |
| Geo | radius from the business, people living there, within `max_radius_miles` | never beyond limits without client OK |
| Audience | Advantage+ audience, age floor 30-35 if the offer needs homeowners | detailed targeting suggestions: homeownership, home improvement interests |
| Placements | Advantage+ | creative lacks a 9:16 version -> make one, do not exclude |
| Attribution | 7-day click (+1-day view if client accepts) | per client rule |
| Special ad category | none for remodeling | financing / credit offers -> check credit category |

Budget sanity: $60/day at a $90 target CPL ≈ 4-5 leads/week. Say that it will likely stay in learning limited and that results need 2-3 weeks to read. Do not hide it.

## 3. Copy and creative requirements

- 3-5 ads. Each: primary text (hook in the first 125 characters), headline (≤40 chars shows best), description, CTA (Learn More / Get Quote / Book Now), URL with UTMs (`utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`).
- Message match with the landing page headline and offer.
- No prohibited claims; no invented reviews, prices, licenses or financing terms.
- Creative needs as briefs ([templates/creative-brief.md](../../../templates/creative-brief.md)): one founder/crew UGC-style video, one before/after (client-supplied photos only), one static offer card. Each with hypothesis.

## 4. Build (PAUSED)

Run the [paused-first launch sequence](../references/mcp-tool-contracts.md#paused-first-launch-sequence). Pass the account id explicitly on every create. Name per [naming conventions](../../../references/naming-conventions.md).

## 5. Show exactly what was created

```
CREATED (all PAUSED) - D-Hauss Remodeling - act_...
Campaign  1202...  MDX_LEADS_KitchenRemodel_York_2026-10    Leads · $60/day (campaign) · highest volume
 Ad set   1202...  Broad_HO_30-65_York25mi                  Lead (dataset 1234) · 25 mi radius York, PA · Advantage+ placements
  Ad      1202...  UGC_FounderWalkthrough_v1                preview: <link>
  Ad      1202...  Static_FreeDesignConsult_v1              preview: <link>
Risks: learning limited at this budget; CAPI EMQ 5.8 (fair); landing page has no phone CTA.
Next: approve activation -> adsgm plan activate --entity <campaign id>
```

## 6. Activation (separate approval)

Only when the user says go: `adsgm plan activate --platform meta --account act_... --entity <campaign id> --reason "user approved launch"`, show summary, `ads_activate_entity`. Then read back `effective_status` and confirm ads are in review/active.
