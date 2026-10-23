# Structure & Audience Strategy

## The premise
Meta has no native B2B firmographic targeting worth trusting — no reliable job title, company size, or vertical filters, and work emails match poorly (<~5–10%). Two consequences:
1. **Bring your own data.** The audience hierarchy below is a data-quality ladder.
2. **Creative is the targeting.** Specific, ICP-naming creative filters who clicks; the delivery system learns from who converts. Broad delivery + narrow creative beats narrow delivery + generic creative.

## Audience data hierarchy
| Tier | Source | Notes |
|---|---|---|
| 1 | **CRM lookalikes** seeded from best customers — highest-paying, fastest-closing, longest-retained (top slice, not the whole list) | Seed ≥1,000 where possible; 1% LAL first, widen tiers (1–2%, 2–3%) as tier-1 saturates |
| 2 | **Enriched third-party lists** — contacts matched on *personal* emails + mobile numbers (enrichment tools), uploaded as custom audiences + lookalikes of them | Fixes the work-email match problem; hash uploads (SHA-256), batch ≤10K |
| 3 | **Broad** (little/no targeting) with hard-filtering creative | Only with a large TAM; the creative must do the qualifying |

Refresh custom audiences at least every ~180 days; stale sources decay silently.

## Validation protocol (before any audience earns scaling budget)
ABO campaign · one ad set per audience source · identical ads in all · equal budgets · 2–4 weeks. Then judge **in the CRM**: pull the leads per ad set and audit job titles/companies/fit — not CPL. The cheapest audience is frequently the junk one.

## Standard audience map for a lead-gen account
- **Remarketing** (build first): site visitors 30/90/180d, video viewers 25/50/75%, lead-form openers, engaged social. Frequency tolerance is high (<8/wk fine).
- **Prospecting**: the hierarchy above, one validated source per ad set during validation, consolidated after.
- **Acceleration**: open-opportunity contact lists synced from CRM — low volume, high frequency, offer-heavy creative aimed at deals in flight.
- **Exclusions everywhere**: customers out of prospecting; each prospecting audience out of its siblings when overlap >20%; open opps out of cold prospecting.

## ABM on Meta (when there's a target-account list)
Viable when TAL ≥ ~1,000 companies and contacts are enriched to personal identifiers. Architecture: tiered TOF awareness → retargeting → acceleration on open pipeline → a separate broad prospecting campaign to feed the top. Caveat: **Advantage+ treats uploaded audiences as suggestions** — for strict list-only delivery, use manual campaigns with targeting expansion off. Measure by account penetration and pipeline influenced, not CPL.

## Lead forms vs. landing pages
| Use instant forms when | Use landing pages when |
|---|---|
| Speed/volume matters, mobile-heavy audience | Story or proof is needed to convert |
| CRM integration is wired (instant sync) | Offer needs explanation (demos, assessments) |
| Friction is designed in (below) | You need the pixel/CVR data on your own domain |

**Intentional friction for quality:** Higher Intent form type · work email field · 2–3 qualifying questions (role, company size, timeline — multiple choice) · a clear "what happens next." Frictionless forms produce social-amnesia leads who don't remember submitting. Volume drops, qualification rate more than compensates — verify with the 0–9 quality scoring in the ad-optimization skill.
