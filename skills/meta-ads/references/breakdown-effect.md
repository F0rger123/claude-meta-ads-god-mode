# The breakdown effect

**Type:** PLATFORM FACT (mechanism documented by Meta) + HEURISTIC (how to act on it).

## Mechanism

Meta's optimizer spends each next dollar where the next result is cheapest. As a segment (placement, audience slice, age band, ad) gets more spend, its marginal cost rises, so the system moves budget elsewhere until marginal costs are roughly balanced. The consequence:

- A segment can have a **higher average CPA** and still be **correct to keep**, because it was bought cheaply at the margin earlier, or because removing it raises costs in the remaining segments (smaller pool, less auction flexibility).
- A segment with the **lowest average CPA** may already be saturated; forcing more money into it raises its CPA.

Example (illustrative): Stories CPA $42, Feed CPA $28 in the same ad set. Excluding Stories usually does **not** make the ad set's CPA $28. The ad set loses inventory, Feed must absorb the budget at rising marginal cost, and the total often gets worse.

## Rules

1. Evaluate performance at the level the system optimizes:
   - Advantage+ campaign budget (CBO) on: judge at **campaign** level for budget distribution between ad sets.
   - Ad set budget: judge at **ad set** level.
   - Advantage+ placements: judge the ad set, not individual placements.
   - Multiple ads in one ad set: Meta concentrates spend on the predicted winner; a low-spend ad is not "losing", it is untested.
2. Breakdown tables are for **diagnosis** (where is the creative failing, which format needs a variant, is a geo outside the service area leaking spend) not for **exclusion decisions**.
3. Valid reasons to exclude a segment are business facts, not averages: out-of-service-area geo, placement where the creative renders broken, an audience the client cannot serve, a brand-safety requirement.
4. If you still suspect a segment is wasteful, propose a **controlled test** (duplicate ad set with the exclusion, split budget, or Meta A/B test via `ads_experiment_abtest_create_test`) - an EXPERIMENT, with approval.

## How to word it to a client

"Stories shows a higher cost per lead than Feed, but that does not mean Stories is wasting money. Meta buys Stories impressions when they are the cheapest next lead available. Turning Stories off usually makes the whole ad set more expensive. We will keep it on and fix the Stories creative format instead."
