---
name: ads-strategy
description: Paid-media strategy and campaign planning - channel roles (Meta demand generation vs Google Search demand capture), offer and funnel, campaign architecture, budget split, cross-platform comparison, and campaign briefs for new launches. Use for "build/launch/plan a campaign", "compare Meta and Google", "where should the budget go", "media plan".
---

# Ads strategy

## Channel roles (BEST PRACTICE, not interchangeable)

| | Meta | Google Search |
|---|---|---|
| Role | demand generation, discovery, interruption | demand capture, people already searching |
| Lever that matters most | creative + offer | keyword/intent coverage + message match |
| Lead quality pattern | more top-of-funnel; qualification matters | higher intent; volume capped by search demand |
| Attribution bias | view-through and cross-device undercount/overcount; last-click undercredits it | last-click overcredits it (captures demand others created) |
| Scaling limit | creative fatigue, audience size in small geos | search volume, impression share |

## Cross-platform comparison ("Compare Meta and Google for this client")

Report side by side for the same dates: spend, leads, **qualified leads** (CRM), revenue if known, CPL, cost per qualified lead, CPA, ROAS, conversion rate, and **attribution confidence** per platform (how each counts, window, tracking health). Then interpret:

- Do not move budget based on last-click ROAS alone. Google Search often harvests demand Meta created.
- Prefer evidence in this order: CRM-qualified outcomes > blended metrics (total leads / total spend over time, MER) > platform-reported.
- Check for overlap: branded search volume and direct traffic rising with Meta spend suggests Meta contributes beyond its reported numbers (HEURISTIC; test with a holdout or geo split before concluding).
- If Search is budget-limited at good CPA, fund it first (capturing existing demand is cheapest). Meta budget then scales demand.
- Recommend reallocations as small steps (10-20%) with a read date - EXPERIMENT unless evidence is strong.

## Niche research first

New client or new niche? Run [workflows/niche-research.md](../../workflows/niche-research.md) before planning. Use the playbook (`adsgm niche show <niche>`) and niche patterns (`adsgm learn summary --niche <niche>`) to set expected CPL and conversion-rate ranges, offers and first hooks. Label every number with its source.

## Planning a new campaign

Use [workflows/campaign-planning.md](../../workflows/campaign-planning.md) then [workflows/campaign-launch.md](../../workflows/campaign-launch.md). Brief: [templates/campaign-brief.md](../../templates/campaign-brief.md); launch plan: [templates/launch-plan.md](../../templates/launch-plan.md).

Decide in this order: business goal and unit economics -> offer -> audience and geo -> channel -> campaign architecture -> conversion event and tracking readiness -> budget and bidding -> creative and copy requirements -> risks -> measurement and read dates.

## Budget split heuristics (HEURISTIC; replace with client data)

- New local service client, modest budget: Google Search first for demand capture at the CPL target; Meta for volume and awareness once creative exists.
- Minimum to learn: enough budget per campaign for several conversions a week. If total budget cannot fund both platforms to that level, recommend one platform first and say why.
- Hold back 10-20% for tests.
