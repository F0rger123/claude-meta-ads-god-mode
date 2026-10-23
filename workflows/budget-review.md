# Workflow: budget review

Trigger: `/ads:budget`, "increase budget", "pacing", "move money". Skill: [ads-budgeting](../skills/ads-budgeting/SKILL.md).

1. **Pacing** - month-to-date spend vs plan per platform and campaign; flag ±15%.
2. **Constraints** - Meta: entities spending ~100% of budget with CPA ≤ target; Google: `search_budget_lost_impression_share` high with CPA ≤ target.
3. **Candidates** - increase (constrained winners), decrease (sustained losers after fixes), reallocate (between campaigns; cross-platform only with the strategy skill's evidence rules).
4. **Gate** - not in learning, tracking verified, lag closed, outside cooldown, enough conversions.
5. **Plan each change** - `adsgm plan budget ... --current --proposed --reason --evidence --expected --risks --confidence --spend --conversions`. Present the full block: CURRENT BUDGET, PROPOSED BUDGET, PERCENT CHANGE, DOLLAR CHANGE, REASON, DATA SUPPORTING IT, EXPECTED EFFECT, RISKS, CONFIDENCE.
6. **Approval** by default; guarded-auto only inside limits. Large increases, budgets above `high_budget_daily_threshold`, and anything outside limits always ask.
7. **Execute** with the exact planned amount (Meta minor units; Google writer `update_budget` in currency units -> micros). Read back.
8. **Record** the read date (≥ 7 days; longer for low volume).
