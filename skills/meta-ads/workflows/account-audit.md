# Meta account audit checklist

Generic output format and severity rules: [workflows/account-audit.md](../../../workflows/account-audit.md). Every finding needs **severity, evidence, likely impact, confidence, recommended action, approval required (yes/no)**.

Pull once (last 30 days + previous 30, plus last 7): account info, all campaigns/ad sets/ads with status and budgets, insights by campaign/ad set/ad, dataset quality, activity log (recent changes), opportunity score.

| Area | Check | Typical severity if failing |
|---|---|---|
| Tracking | optimization event fires, pixel+CAPI deduped, right dataset, EMQ, Meta vs CRM/GA4 gap | CRITICAL (no/incorrect event), HIGH (dedup/gap) |
| Account | payment issues, disabled ads, policy rejections, special ad category correct | CRITICAL |
| Objectives | objective + optimization event match the business goal (leads not traffic) | HIGH |
| Structure | fragmentation (ad sets with < ~1 event/day), overlapping ad sets, duplicate campaigns for same goal | MEDIUM-HIGH |
| Learning | share of spend in learning / learning limited, frequency of significant edits (activity log) | MEDIUM |
| Budgets | budget vs target CPA (can it get events?), pacing, lifetime vs daily misuse, money on paused-campaign leftovers | MEDIUM |
| Bidding | cost goals far below actual CPA (under-delivery), bid caps | MEDIUM |
| Audiences | geo matches service area and `geographic_limits`, location type "living in", exclusions of customers, audience size | HIGH if geo leaks outside service area |
| Placements | restrictions without reason; creative missing 9:16 / 1:1 versions | LOW-MEDIUM |
| Creative | ads per ad set, age of top spenders, fatigue signature, hook/hold rates, format mix (static/video/UGC) | MEDIUM |
| Copy | message match, CTA, prohibited claims, offer clarity | MEDIUM (HIGH if prohibited claim) |
| Spend efficiency | CPL/CPA vs target and vs lead value; spend on ads with zero results after ≥2-3x target CPA | HIGH |
| Attribution | window used, view-through share, Jan-2026 window change affecting comparisons | LOW-MEDIUM |
| Landing page | load speed (mobile), headline/offer match, form length, phone CTA, thank-you event | MEDIUM-HIGH |

Rules:
- Breakdown tables are evidence for creative/format/geo-leak findings only, never for "pause this placement/age" findings ([breakdown effect](../references/breakdown-effect.md)).
- Findings on learning ad sets are capped at LOW / "monitor".
- "Approval required" is yes for any change except paused creation (and except guarded-auto actions inside the client's limits).
