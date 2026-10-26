# Workflow: niche research

Trigger: `/ads:research <client or niche>`, onboarding a client in a niche without a playbook (or one older than 4 months), "what works for roofers", "what's a good conversion rate for dental ads".

Goal: before spending, know what tends to work for **this type of business in this kind of area**, with sources. Output: a saved niche playbook and 3–5 concrete launch recommendations for the client.

## 1. Name the niche

Use a specific, reusable slug, e.g. `kitchen-remodeling`, `roofing-storm`, `dental-implants`, `hvac-replacement`, `med-spa`. Save it on the client as `business.niche`. Check `adsgm niche list`: if a fresh playbook exists, reuse it and only fill gaps.

## 2. Gather, labelling every fact

| Source | Gives | Label |
|---|---|---|
| Meta Ads MCP: `ads_insights_industry_benchmark`, `ads_insights_auction_ranking_benchmarks` (on the client's account) | CPM, CTR and cost ranges for the vertical | PLATFORM FACT (Meta-reported) |
| Meta Ad Library (`ads_library_search`) for the niche and area | offers, hooks, formats, how long ads run | OBSERVED |
| Google Ads Transparency Center (browser) | competitors' search ads and messages | OBSERVED |
| Reputable benchmark reports (web search: publisher, year, sample) | typical conversion rate (landing page or form), CPL, CPC by industry | THIRD-PARTY BENCHMARK (with URL and date) |
| Bundled knowledge: `bundles/agrici-ads/ads/references/benchmarks.md`, `bundles/agrici-ads/skills/ads-plan/assets/<industry>.md` | industry plan template and ranges | HEURISTIC |
| `adsgm learn summary --niche <slug>` and `--portfolio` | what has worked across *your* clients in this niche | NICHE PATTERN |
| The client's own history, if any | the only real evidence for this client | OBSERVED (account data) |

Terms to report clearly:
- **Conversion rate (CVR):** the % of clicks that become leads.
- **Close rate:** the % of leads that become customers.
- **CPL:** cost per lead.
- **CPM:** cost per 1,000 impressions.
- **CTR:** click-through rate.

Give ranges, not single numbers, and say how old the data is.

## 3. Save the playbook

Write JSON with sections `benchmarks`, `what_converts`, `offers`, `hooks`, `audiences`, `seasonality`, `competitors_seen`, `platform_fit`, `landing_pages`. Each item is `{"text", "source", "date", "label"}`. Save it with `adsgm niche save --file playbook.json`. It's refused if any fact lacks a source, date or label.

Never put client numbers in a playbook. Client results reach the niche only as tactic win rates through the learning loop.

## 4. Recommend

For the client, combine the playbook, their economics (`adsgm budget-plan`) and their offer into:
- **expected ranges:** CPL, conversion rate and leads per month at the planned budget, labelled with their sources;
- **an offer** that tends to convert in this niche, adapted to the client's real offer;
- **2–3 hooks and formats** to test first, as briefs (and graphics via `adsgm creative render`);
- **audience and geo** starting points;
- **platform fit:** for example, roofing storm work is search-heavy, med-spa is visual, Meta-heavy;
- **what to watch in the first 2 weeks.**

Every recommendation names its evidence. If the evidence is thin, say so.

## 5. Keep it learning

Tag plans with niche-relevant tactic tags (`free-inspection-offer`, `before-after-static`, `financing-hook`). After a few clients in the same niche, `adsgm learn summary --niche <slug>` shows which tactics win there. Refresh the playbook when it's older than 4 months or when the season changes.
