# Scaling, Budget & Measurement Rules

## Vertical scaling (same ad set/campaign, more budget)
Preconditions (all): cost at/below target for 2+ weeks · conversion volume near ~50/week · frequency <3.0 · no fatigue signals · CRM confirms lead quality.
- Step: **+20% per 3–5 days** (never >30% in one move — resets learning).
- After each step, watch 3–5 days before the next.
- **Decreasing-returns rollback:** cost per result +15% or more after a step → roll back 20–30%, hold 7 days, scale horizontally instead.

## Horizontal scaling (more surface area, same budget discipline)
Order of preference: new audience tier (next lookalike %, new seed) → new geo → new format/placement coverage → duplicate winner into an adjacent segment **with exclusions** so it can't cannibalize the original.

## Portfolio allocation
- **70/20/10**: ~70% of spend on proven performers, 20% on promising (graduated but young), 10% on experiments.
- **Structural 80/20**: two CBO campaigns — Scaling (80%, graduated winners only) and Testing (20%, hard budget so tests can't be starved by winners). Both numbers are portfolio defaults; the hard rule is that testing has a protected budget.
- Minimum viable Meta budget sanity check: supporting learning needs roughly `TCPL × 50 ÷ 7` per ad set per day. If the total budget can't fund that for even one ad set, consolidate before optimizing.

## Kill rules with data-sufficiency gates
| Rule | Trigger | Gate before acting |
|---|---|---|
| Hard kill | spend ≥ 3× target with 0 conversions | ≥7 days live AND ≥20 clicks (skip gates only for runaway spend, broken links, policy rejection) |
| Maintenance pause | sustained cost 1.5–2× target after a swap cycle | full 14-day window, out of learning |
| Frequency kill | prospecting frequency >5–6 with decaying CTR | iteration ready to replace it |
| Never | pause a segment because its breakdown-average CPA is higher | see ad-analysis breakdown-effect — this is the classic false positive |

Don't restart a killed ad unchanged. Something must differ: creative, audience, offer, or landing page.

## Learning-limited remediation ladder
In order: 1) broaden the audience → 2) raise budget toward `TCPL × 50 ÷ 7` → 3) optimize a higher-funnel event that fires ≥50×/week → 4) consolidate overlapping/fragmented ad sets. Structural learning-limited ad sets never stabilize — consolidation beats hope.

## Seasonality
- Q4: CPMs +30–80% (consumer gifting auction). B2B/lead-gen: reduce targets or spend, bank creative for January.
- Q1: cheapest auctions of the year — the aggressive testing and scaling window. Front-load creative production in December.
- Compare seasonal periods to the same period last year, never to the adjacent week.

## Measurement hierarchy (what to trust when numbers disagree)
1. **CRM truth** (qualified leads, pipeline, revenue by ad)
2. **MER** — total revenue ÷ total ad spend (blended; immune to attribution games)
3. Post-purchase/post-lead surveys ("how did you hear about us")
4. GA4 / analytics
5. **Platform-reported conversions — last** (typically overclaims 20–40%)
Never present platform ROAS/CPL alone when a higher-tier source exists; when tiers disagree, show both and say which decision each supports. Never sum conversions across platforms with different attribution windows — reconcile windows first or report side by side.
