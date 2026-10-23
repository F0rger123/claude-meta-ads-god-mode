# Targeting

## Geography (local service businesses)

- Use radius targeting around the business address or a city center: `geo_locations.custom_locations` with `latitude`, `longitude`, `radius`, `distance_unit` ("mile"/"kilometer"). This avoids city-key lookups.
- Location type: target people **living in** the area for home services (not "recently in" / travelling). Check the field names with `ads_get_field_context` - they change across API versions.
- Exclusions: add excluded regions from `business.geographic_limits.excluded` as `excluded_geo_locations`.
- Every geo change after launch is a `geo_expansion` action (approval). Verify geo by reading the ad set back after creation.
- Respect `geographic_limits.max_radius_miles`. Expanding beyond it needs the client's explicit OK, not just approval of the change.

## Audiences

| Audience | Use | Notes |
|---|---|---|
| Advantage+ audience / broad | default prospecting with healthy signal | location + age floor as hard limits |
| Detailed targeting (interests, behaviors) | weak signal, niche B2B, early accounts | treat as suggestions under Advantage+ |
| Custom audiences: website visitors, engagers, customer lists | retargeting, exclusions | customer lists need consent and hashing; audience writes need approval |
| Lookalikes | seed with qualified customers, not all leads | 1-3% for small markets often exceeds the service area; geo still limits |

- Exclude existing customers and recent converters when the offer is acquisition-only.
- Retargeting pools for small local businesses are often tiny; a separate retargeting ad set may never exit learning. Consider one campaign where retargeting is part of broad delivery.
- **Never** reuse one client's custom audience or lookalike in another client's account.

## Placements

Advantage+ placements by default. Restrict only for a business reason (creative format not available, brand safety). Breakdown CPA differences alone are not a reason - see [breakdown-effect.md](breakdown-effect.md).

## Special ad categories

Restricted targeting applies - see [campaign-structure.md](campaign-structure.md#special-ad-categories-platform-fact).
