# The Breakdown Effect

The single most common analytical error in Meta Ads: concluding from a breakdown report (placement, age, gender, region…) that the system is "wasting" budget on segments with higher average costs. In reality the delivery system maximizes total results by optimizing **marginal efficiency** — the cost of the *next* result — not average efficiency.

## Evaluation levels

Never evaluate below the level the system optimizes at:

| Automation in play | Correct evaluation level |
|---|---|
| Advantage+ campaign budget (CBO) | Campaign |
| Automatic/Advantage+ placements (no CBO) | Ad set |
| Multiple ads in one ad set | Ad set |

Below that level, budget distribution is the optimizer's output, not a scorecard of segment quality.

## Worked example

Engagement campaign, $500, Facebook Stories + Instagram Stories placements.

Day 1: FB Stories delivers at $0.35 CPA vs. IG's $0.72 — FB looks like the obvious winner. But FB's CPA rises fast as its cheap inventory saturates. The system finds the inflection point where FB's **marginal** CPA crosses IG's, and shifts budget.

Final: IG Stories $1.46 average CPA on $450 spend; FB Stories $1.10 average CPA on $50 spend.

The naive read: "the system spent 90% of budget on the worse placement." The correct read: average CPA ≠ marginal CPA. FB's average is low *because* the system stopped spending there before its rising marginal cost destroyed campaign efficiency. Cutting IG here would have raised total costs.

## How to detect the marginal story

Pull daily time series (`--daily`) per segment and look at the CPA trajectory as spend concentrates:
- Segment CPA flat/falling while spend grows → genuine headroom.
- Segment CPA rising as spend grows → saturation; the system will (correctly) rebalance away.
- Low-spend segment with low average CPA → often already-harvested cheap inventory, not an untapped goldmine.

## Rules

1. **Never** judge system budget allocation by average CPA in breakdown reports alone.
2. **Never** recommend pausing a segment solely because its breakdown-average cost is higher — removing it can raise total costs.
3. Frame any segment-level change as a testable hypothesis with a rollback, stating the marginal-efficiency caveat.
4. When a stakeholder asks "why is Meta spending on the expensive segment?", answer with the marginal story, with the daily series as evidence.
