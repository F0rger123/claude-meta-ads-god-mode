---
name: ads-optimization
description: Structured optimization engine for Meta and Google Ads - multi-window analysis (today, 3, 7, 14, 30 days), conversion lag, learning status, wasted spend, search terms, creative fatigue, budget constraints, attribution quality, and confidence-graded recommendations (HIGH / MODERATE / EXPERIMENT). Use for "optimize", "what wasted the most spend", "what should we change", "weekly optimization".
---

# Ads optimization

Workflow: [workflows/optimization-cycle.md](../../workflows/optimization-cycle.md).

## Windows and what each is for

| Window | Use | Never use for |
|---|---|---|
| Today | anomalies, delivery breaks, runaway spend | performance verdicts |
| Last 3 days | early warning (tracking drop, disapprovals, CPM spike) | pausing or scaling |
| Last 7 days | primary read for active entities (full week cycle) | low-volume accounts' CPA |
| Last 14 days | fatigue trends, small accounts | - |
| Last 30 days | search terms, structure, small-volume verdicts | detecting recent change |

Exclude the last N days from CPA verdicts where N ≈ conversion lag (Google lag buckets; CRM lead-to-qualified time).

## Wasted spend ("Show me what wasted the most spend this month")

Rank entities by spend with no or poor results, but only call it waste when:
- **Certain waste:** irrelevant search terms, spend outside service area, broken URLs/disapproved-then-reapproved ads, duplicate campaigns bidding on the same queries, spend on a tracking-broken period with no leads in CRM either.
- **Probable waste:** ads/ad sets/keywords with spend ≥ 2-3x target CPA and zero conversions, out of learning, tracking verified (HEURISTIC).
- **Not waste:** learning ad sets, breakdown segments with higher averages (Meta breakdown effect), upper-funnel campaigns judged on last-click.

Report: top 5-10 by $ with class (certain/probable), evidence, fix, confidence, approval needed.

## Recommendation format

```
[HIGH CONFIDENCE] Add 7 phrase negatives (DIY/jobs) to Kitchen Search
  Data: 30d, $166 on 23 terms, 0 conv; no converter blocked
  Expected: -$40/week waste
  Action: adsgm google plan (add_negative_keywords) -> approval: yes (client in approval mode)
```

Confidence:
- **HIGH** - large sample, clean tracking, mechanism clear (e.g., irrelevant queries, out-of-area spend).
- **MODERATE** - directional data; act in small reversible steps, set a read date.
- **EXPERIMENT** - hypothesis; design a test with one variable ([workflows/creative-testing.md](../../workflows/creative-testing.md)).

Use `adsgm quality` to grade evidence when in doubt. Do not overreact to tiny samples; "no action - insufficient data until <date>" is a valid recommendation.

## Order of operations per cycle

1. Tracking health and anomalies. 2. Certain waste. 3. Budget constraints on winners. 4. Fatigue/creative. 5. Structure. 6. Tests. Max 3-5 changes per cycle per platform; log each with `adsgm plan` so cooldowns apply.
