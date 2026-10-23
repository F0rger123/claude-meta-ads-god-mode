---
name: meta-ads
description: Meta (Facebook/Instagram) Ads platform expertise - campaign/ad set/ad hierarchy, objectives, Advantage+, budgets and bidding, audiences, placements, creatives, pixel/dataset and Conversions API, attribution, learning phase, breakdown effect, frequency and fatigue, delivery diagnostics, and the official Meta Ads MCP tool contracts. Use with ads-core whenever the work touches a Meta ad account.
---

# Meta Ads

Load with `ads-core`. This file is the map; open a reference only when the task needs it.

## How Meta's delivery system actually works (read before judging anything)

- **PLATFORM FACT - auction + optimizer.** Each impression goes to the ad with the highest total value (bid x estimated action rate + ad quality). The optimizer allocates budget to where the **next** result is cheapest (marginal cost), not where the **average** CPA looks best.
- **PLATFORM FACT - breakdown effect.** Segment-level averages (placement, age, gender, region, device, ad within an ad set) routinely look "inefficient" while being the reason the total is efficient. **Never pause or exclude a segment from a breakdown table alone.** Judge at the level the system optimizes (campaign under Advantage+ campaign budget, ad set otherwise). See [references/breakdown-effect.md](references/breakdown-effect.md).
- **PLATFORM FACT - learning phase.** An ad set learns after launch and after significant edits; Meta's guidance is about 50 optimization events within 7 days to exit. "Learning limited" means it is not getting enough. Verdicts on learning ad sets are noise. See [references/learning-phase.md](references/learning-phase.md).
- **PLATFORM FACT - attribution changed in 2026.** Since 2026-01-12 the Ads Insights API no longer returns 7-day-view and 28-day-view windows. Available: 1-day click, 7-day click, 28-day click, 1-day engaged-view, 1-day view. Historical comparisons that used view windows are not like-for-like. See [references/attribution-and-signals.md](references/attribution-and-signals.md).

## Hierarchy and what lives where

```
Ad account (act_...)  currency, timezone, payment (human only)
└─ Campaign           objective, buying type, Advantage+ campaign budget (CBO) on/off, special ad category
   └─ Ad set          optimization event, conversion location, budget (if no CBO), bid strategy, schedule,
                      audience + geo, placements, attribution setting
      └─ Ad           creative (image/video/carousel), primary text, headline, description, CTA, URL, UTMs
```

Objectives (ODAX): Awareness, Traffic, Engagement, Leads, App promotion, Sales. For local lead gen use **Leads** with website conversion location optimized for a real lead event (or instant forms only if the CRM can qualify them). Do not optimize for clicks/landing page views when the business wants leads unless conversion volume is too low to learn - and say so.

Details: [references/campaign-structure.md](references/campaign-structure.md) (structure, consolidation, Advantage+, bid strategies), [references/targeting.md](references/targeting.md) (geo radius, Advantage+ audience, custom audiences, lookalikes, special ad categories, exclusions).

## Diagnose performance in this order

1. **Tracking first** - is the optimization event firing, deduplicated (pixel + CAPI share `event_id`), on the right dataset, with decent Event Match Quality? Bad signal makes every other conclusion wrong. (`ads_get_dataset_quality`, `ads_get_dataset_stats`)
2. **Delivery state** - learning / learning limited / limited by budget / bid cap / audience size / rejected ads. (`ads_get_ad_entities` with effective_status, `ads_get_errors`)
3. **Funnel decomposition** - CPA = CPM / (CTR x CVR x 1000) for click-based results. Find which term moved: CPM (auction/competition/audience/season), CTR (creative/hook/fatigue/relevance), CVR (landing page, offer, form, tracking, lead quality).
4. **Creative** - fatigue (rising frequency + falling CTR + rising CPM at stable spend), hook rate, hold rate. See [references/creative-fatigue.md](references/creative-fatigue.md).
5. **Structure** - fragmentation (too many ad sets splitting too little budget), overlapping audiences, too many ads per ad set, budgets below ~what the optimization event needs.
6. **Business truth** - platform-reported leads vs CRM-qualified leads. A cheaper CPL with worse lead quality is not a win.

Delivery and relevance tools: [references/delivery-diagnostics.md](references/delivery-diagnostics.md).

## Using the official Meta Ads MCP

Exact tool names, params quirks and the paused-first launch sequence: [references/mcp-tool-contracts.md](references/mcp-tool-contracts.md). Key points:

- Creates (`ads_create_campaign`, `ads_create_ad_set`, `ads_create_ad`) produce PAUSED objects. `ads_activate_entity` is the spend switch - it always needs an approved ticket.
- `ads_update_entity` edits any field; the gate inspects the payload (status ACTIVE = activation, budget fields = budget change, geo = geo expansion).
- Use `ads_get_field_context` before unfamiliar fields; some params are JSON strings.
- Budgets are in the account currency's **minor unit** (cents for USD): $57.50/day = 5750.
- Rate limits are real (ad set budget changes: 4 per hour per ad set; one edit per object per 30 s). Space writes out.

## Workflows in this skill

- [workflows/launch-campaign.md](workflows/launch-campaign.md) - Meta lead/sales campaign build, paused-first.
- [workflows/account-audit.md](workflows/account-audit.md) - Meta-specific audit checklist with evidence fields.
- [workflows/creative-refresh.md](workflows/creative-refresh.md) - fatigue check to brief to paused swap.

## Never

- Never pause a placement/age/gender/region segment because its average CPA is higher (breakdown effect).
- Never judge an ad set in learning, or a test before it has enough spend (at least 2x target CPA per variant as a floor - HEURISTIC).
- Never make several significant edits to one ad set in one day; each can restart learning.
- Never switch the optimization event, attribution setting or dataset without approval (tracking change).
- Never run housing, employment, credit, or social-issue ads without the required special ad category; targeting is restricted there.
