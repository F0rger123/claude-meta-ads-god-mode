# Campaign structure, Advantage+, budgets and bidding

## Structure principles

- **BEST PRACTICE - consolidate.** Fewer ad sets with more budget learn faster than many small ones. For a local service business spending under ~$5k/month, one prospecting campaign with 1-2 ad sets is usually right. Each extra ad set must earn its place with a real difference (different offer, geo with different economics, or a genuinely different audience strategy).
- **BEST PRACTICE - separate by economics, not by curiosity.** Split campaigns when budgets, goals or reporting must be controlled separately (different service lines, different CPL targets, retargeting vs prospecting at higher spend).
- **HEURISTIC - 3-6 ads per ad set.** More ads dilute learning; Meta concentrates spend on a few anyway.
- Name everything per [references/naming-conventions.md](../../../references/naming-conventions.md).

## Advantage+ (PLATFORM FACT: names and availability change; check `ads_get_field_context`)

- **Advantage+ campaign budget** (formerly CBO): budget at campaign level, distributed across ad sets toward lowest marginal cost. Judge distribution at campaign level (breakdown effect).
- **Advantage+ audience**: your targeting becomes a suggestion; Meta can go beyond it. Hard constraints (location, minimum age, exclusions where allowed) still apply. For local service, location stays a hard limit - verify geo in the ad set after creation.
- **Advantage+ placements**: recommended default unless creative cannot render in a placement.
- **Advantage+ sales / app / leads campaigns**: streamlined automated campaign types. Fewer manual levers; good when signal is strong, risky with weak tracking.

When to use: Advantage+ options when the conversion signal is healthy and volume is meaningful. Manual constraints when the business has hard limits (service area, regulated category, B2B niche) or tracking is weak.

## Budgets

- Daily vs lifetime: lifetime budgets cap total spend structurally - good for tests and flights. Daily for always-on.
- Minimum viable budget per ad set (HEURISTIC): enough for several optimization events per week. Below ~1 event/day the ad set will likely sit in learning limited.
- Budget changes: see [skills/ads-budgeting](../../ads-budgeting/SKILL.md). Rate limit (PLATFORM FACT): 4 budget changes per ad set per hour.
- Budgets are in minor units via API.

## Bid strategies (PLATFORM FACT: options; HEURISTIC: when)

| Strategy | Use when |
|---|---|
| Highest volume (lowest cost) | default; learning, no hard CPA ceiling |
| Cost per result goal (cost cap) | stable account with history; you accept lower volume to protect CPA |
| Bid cap | advanced; strict auction control; often under-delivers |
| ROAS goal | sales with reliable value tracking |

Set cost goals near recent actual CPA, not an aspirational number - a cap far below reality stops delivery.

## Special ad categories (PLATFORM FACT)

Housing, employment, credit (financial products), and social issues/elections/politics require declaring the category; targeting options (age, gender, zip-level geo, some detailed targeting) are restricted. Home remodeling is usually not "housing" unless offering housing/real-estate transactions or financing - when financing offers are in the ad, check whether the credit category applies. When unsure, flag it and ask; do not guess.
