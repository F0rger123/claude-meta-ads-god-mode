---
name: opportunity-spotting
description: Find growth opportunities in and around a Meta Ads account — underexploited audiences and angles in account data, competitor gaps via Meta Ad Library research, seasonal/auction timing windows, offer and market expansion. Use when the user asks where to grow, what to test next, for competitor/market research, new audience or angle ideas, or why performance has plateaued.
---

# Meta Ads Opportunity Spotting

Opportunities are found where evidence already points and competitors aren't looking. The output is never "ideas" — it's an **opportunity brief**: a falsifiable hypothesis, graded evidence, a size estimate, and a bounded test design ready for the campaign-management skill.

## The five lenses (run the ones the question calls for; a full sweep runs all)

### 1. Account mining (strongest evidence — start here)
Work from performance data (analysis reports if the workspace has them, else pull `--daily` insights):
- **Efficient-but-starved segments**: strong cost per result, low spend share, and a *flat marginal curve* (daily CPA not rising as spend grows — the breakdown-effect test from the ad-analysis skill distinguishes real headroom from already-harvested pockets).
- **Coverage gaps**: compare live creative against the buyer-situations list (creative-playbook) — situations with zero ads are free test ideas.
- **Saturation signals as redirects**: frequency climbing + CTR decaying in a segment = its budget needs a destination; that destination is the opportunity.
- **Untested rungs**: audience tiers never tried (next lookalike %, new seed source), formats absent, placements excluded historically for reasons nobody remembers.

### 2. Competitor recon (medium evidence)
Meta Ad Library shows every active ad for any advertiser, free, no auth. Protocol in `references/ad-library-recon.md`. Core signal: **longevity ≈ money** — an ad running 3+ months is very likely profitable. Map competitors' angles/offers/formats; the white space (angles nobody runs, offers nobody makes) is yours to test first.

### 3. Timing & auction windows (medium evidence)
- **Q1**: cheapest CPMs of the year — the aggressive testing/scaling window; front-load creative in December.
- **Q4**: CPMs +30–80%; lead-gen accounts bank budget and creative for January.
- Vertical buying cycles (from `_config/account.md` seasonality notes): plan campaigns to *land* when the ICP decides, launch 2–3 weeks earlier for learning.
- Platform shifts: new placements/formats typically under-priced early (early-majority CPM discount) — worth a bounded test when format-fit exists.

### 4. Audience & market expansion (weaker evidence — size carefully)
Expansion ladder, nearest first: next lookalike tier → new seed (different best-customer slice) → adjacent segment/vertical → new geo. Prefer the **top-5% in-market** framing: who is buying *now*? Target them first; expand to demand creation only when capture saturates.

### 5. Offer innovation (weaker evidence, highest ceiling)
Match offer to traffic temperature: cold traffic wants low-commitment value (benchmark/report, ROI calculator, assessment) — not a demo — unless the product is low-ACV/self-serve where direct trial/demo can work cold. Warm: case study, comparison, product tour. Hot: tailored assessment. A quality plateau across many creative tests usually means the *offer* is the ceiling — the "nuclear option" escalation from the optimization skill lands here.

## Sizing & the brief
Every opportunity gets: estimated audience size (range) · expected cost per result range (analogous segments or vertical benchmarks, sources labeled) · budget to significance (**3 × target per concept tested** — from the optimization skill's data floor) · payback logic. Grade every evidence item: **account data > competitor behavior > market inference**.

Brief template in `references/opportunity-lenses.md` — hypothesis, evidence table, sizing, test design (audience/creative/budget/duration), success & kill criteria, go/no-go recommendation. A brief that can't be tested within the workspace's test budget guardrail gets shrunk until it can.

## What to avoid
- Trend-chasing with no offer/audience fit; novelty is not evidence.
- Copying a competitor's creative (copy the *angle*, differentiate the execution — and never copy much-larger advertisers whose economics you don't share).
- Point-estimate sizing theater — ranges with stated assumptions.
- Opportunities requiring account-structure upheaval to test — smallest viable test wins.

## References
- `references/ad-library-recon.md` — the competitor research protocol, step by step, with what to record.
- `references/opportunity-lenses.md` — full lens checklists, sizing method, brief template.
