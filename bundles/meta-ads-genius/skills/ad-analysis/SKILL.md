---
name: ad-analysis
description: Expert diagnosis of Meta Ads performance — interpret Ads Manager/API data, find root causes, and produce evidence-cited reports that respect Meta's delivery mechanics (breakdown effect, learning phase, auction dynamics). Use when the user asks how ads/campaigns are performing, why CPA/CPL/ROAS/CPM changed, to analyze exported Meta ads data, to run a weekly review, or to diagnose delivery problems.
---

# Meta Ads Analysis

You are analyzing a machine-learning delivery system, not a spreadsheet. Meta's system optimizes for **marginal** efficiency (cost of the *next* result), dynamically. Most naive analyses fail by judging **average** metrics in breakdown reports and recommending changes that fight the optimizer.

## Core principles
1. **Holistic first** — evaluate at the aggregate level before drilling down; the system optimizes the whole, not the parts.
2. **Dynamic over static** — analyze trends over time, never single snapshots.
3. **Marginal over average** — a segment with a higher *average* CPA may be protecting the campaign from even higher *marginal* costs elsewhere. Read `references/breakdown-effect.md` before interpreting any breakdown.

## Workflow

### Step 0 — Get the data
- In a workspace with a `data/raw/` convention: use the freshest matching export there.
- With API access configured (`META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`): run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pull_insights.py" --level adset --last 7 --daily` (add `--breakdowns` only for the specific question at hand). `--daily` matters: marginal analysis needs time series.
- Otherwise: ask for an Ads Manager export (campaign + ad set + ad level, the analysis window plus the prior comparison window).

### Step 1 — Identify the correct evaluation level (do this first, always)
| Campaign setup | Evaluate at |
|---|---|
| Advantage+ campaign budget (CBO) | **Campaign** level |
| Automatic placements, no CBO | **Ad set** level |
| Multiple ads in one ad set | **Ad set** level |

Judging entities below their evaluation level is how the breakdown effect produces false conclusions.

### Step 2 — Gate on learning phase
For each ad set in scope: still learning (~50 optimization events within 7 days of last significant edit)? Learning limited? Significant edit recently (budget, bid, targeting, creative, optimization goal — all reset learning)? Findings about in-learning entities are **preliminary** and must say so. Details: `references/delivery-system.md`.

### Step 3 — Analyze through five lenses
1. **Funnel decomposition** — CPA = CPM ÷ (CTR × CVR × 10). Which term moved? Fix the biggest broken term first.
2. **Marginal efficiency** — from daily time series, is a segment's CPA *rising* as spend concentrates? That, not average CPA, explains budget shifts.
3. **Relevance diagnostics** — Quality / Engagement / Conversion rankings triage creative vs. targeting vs. post-click problems: `references/diagnostics.md`.
4. **Auction overlap & pacing** — ad sets competing for the same people; budget held back by pacing. Both mimic "performance problems": `references/diagnostics.md`.
5. **Fluctuation triage** — 20–30% day-to-day CPA variation is normal; >50% sustained for multiple days, delivery near zero, or CVR falling while spend rises are real: `references/diagnostics.md`.

### Step 4 — Synthesize with the breakdown effect in mind
Before writing any "segment X is underperforming" finding, check the daily series for the marginal story. Example of a correct read: "Placement A shows $10 average CPA vs. B's $15, but A's daily CPA is rising sharply — its marginal CPA likely exceeds B's, so the system's shift toward B is correct."

### Step 5 — Report
Structure every report as:
1. **Executive summary** — 2–3 findings, verdict first
2. **Evaluation level used** and why
3. **Learning phase status** per ad set in scope
4. **Performance analysis** — correct metric names, trends not snapshots
5. **Diagnosis** — root causes with evidence (metric + comparison + date range + sample size)
6. **Recommendations** — each framed as a testable hypothesis with expected impact on *overall* performance, ranked by dollar impact
7. **Breakdown-effect notes** — any place average-vs-marginal could mislead the reader

## Hard rules
- **NEVER** recommend pausing or cutting budget for a segment based solely on higher average CPA/CPM in a breakdown report. Frame such changes as testable hypotheses with the marginal-efficiency caveat stated.
- Every insight carries data evidence; every recommendation is actionable and verifiable.
- Disambiguate clicks: "clicks (all)" ≠ "link clicks". Never say "clicks" bare. CTR likewise: link CTR vs. CTR (all).
- No winner/loser verdicts mid-learning or under ~50 conversions per arm — say "insufficient data" and what would settle it.
- If Meta's own recommendations are available (Account Overview, or the API recommendations endpoint), check them; when you diverge, say so and justify.
- State attribution settings when comparing windows; flag platform-vs-CRM conversion gaps rather than treating either as ground truth.

## Metric naming (API field → report name)
`impressions`→Impressions · `reach`→Reach · `frequency`→Frequency · `spend`→Amount Spent · `cpm`→CPM · `clicks`→Clicks (all) · `ctr`→CTR (all) · `inline_link_clicks`→Link Clicks · `inline_link_click_ctr`→CTR (link) · `act__lead`→Leads · `cpa__lead`→Cost per Lead · `act__purchase`→Purchases · `val__purchase`→Purchase Value · `roas__omni_purchase`→Purchase ROAS · `thruplays`→ThruPlays

## References
- `references/breakdown-effect.md` — marginal vs. average, evaluation levels, worked example. **Read first for any breakdown analysis.**
- `references/delivery-system.md` — auctions, pacing, bid strategies, learning phase mechanics.
- `references/diagnostics.md` — relevance rankings triage, auction overlap, fluctuation thresholds.
- `references/audit-checklist.md` — weighted full-account audit catalog (signals 30 / creative 30 / structure 20 / audience 20) with scoring. Load for "audit the account" requests; the `meta-ads-auditor` agent runs on it.
