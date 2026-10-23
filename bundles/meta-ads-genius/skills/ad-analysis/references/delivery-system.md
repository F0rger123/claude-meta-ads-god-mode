# Meta Delivery System Mechanics

## The auction
Every impression opportunity runs an auction. Winner = highest **Total Value**:

> Total Value = (Advertiser Bid) × (Estimated Action Rate) + (Ad Quality)

- **Bid** — set by bid strategy.
- **Estimated action rate** — predicted probability this person takes the optimized action.
- **Ad quality** — user feedback, hide rates, low-quality attributes (clickbait, engagement bait).

Implications: a more relevant ad beats a higher bid; low delivery often means low total value, not low budget; improving creative quality is frequently cheaper than raising bids; high CPA can come from low estimated action rates (audience-creative mismatch), not "expensive auctions."

## Bid strategies
| Type | Strategy | Behavior |
|---|---|---|
| Spend-based | Highest volume | Spend full budget, maximize result count |
| Spend-based | Highest value | Spend full budget, maximize conversion value |
| Goal-based | Cost per result goal | Hold average CPA near target — adherence not guaranteed |
| Goal-based | ROAS goal | Hold average ROAS near target — adherence not guaranteed |
| Manual | Bid cap | Hard max bid per auction; needs sophisticated rate estimates |

Goal-based strategies trade volume for cost control: underdelivery under a cost goal usually means the goal is set below what the auction clears at.

## Pacing
- **Budget pacing** spreads spend over the schedule; **bid pacing** adjusts bids to cost goals as budget depletes.
- Explains: daily spend variance under a constant budget, the system "holding back" during expensive hours/days, and why efficiency must be judged over the full window, not daily snapshots.

## Learning phase
- New or significantly edited ad sets enter learning; the Delivery column shows **Learning**.
- Exit: ~**50 optimization events within 7 days** of the last significant edit. (Shops ads exception: 17 website + 5 Meta purchases.)
- **Significant edits that reset learning:** budget (large changes), bid strategy/amount, targeting, creative, optimization goal. Small budget nudges (≲20%) usually don't reset.
- During learning: volatile performance, elevated CPA, results not indicative of long-term performance.
- **Learning limited**: the ad set can't reach ~50 events/week — budget too small relative to CPA, audience too narrow, or auction overlap. Structurally learning-limited ad sets never stabilize; consolidate them.
- Budget-for-learning math: daily budget ≥ (target CPA × 50) ÷ 7, per ad set, or accept learning-limited delivery knowingly.

### Analysis gates
1. Never issue winner/loser verdicts for entities in learning.
2. A significant edit means the clock restarted — compare post-edit to post-edit, not across the reset.
3. Batch edits into one session per ad set; each separate edit session is another reset.
