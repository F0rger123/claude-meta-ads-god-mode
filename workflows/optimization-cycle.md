# Workflow: optimization cycle

Trigger: `/ads:optimize`, "what wasted the most spend this month", weekly optimization. Skill: [ads-optimization](../skills/ads-optimization/SKILL.md).

1. **Select client**; note the date and last cycle's changes (`adsgm log`, change history, activity log).
2. **Pull** today, 3, 7, 14, 30 days for each platform (campaign + ad set/ad group + ad; Google search terms 30 d).
3. **Data quality gate** - for each entity: conversions, spend, learning status, days since last major change, conversion lag, tracking health, seasonality. `adsgm quality` when borderline. Entities that fail the gate get "insufficient data - read on <date>".
4. **Analyze** spend, conversions, value, CPA/CPL, ROAS, CTR, CPC, CPM, frequency, impression share, fatigue, search terms, budget constraints, learning, attribution quality.
5. **Classify** each candidate change HIGH / MODERATE / EXPERIMENT; class waste as certain / probable / not waste.
6. **Choose ≤ 3-5 changes per platform**, highest expected impact with lowest risk first. Prefer reversible changes.
7. **Plan each** with `adsgm plan ...` (budget changes with full disclosure; negatives with preview list).
8. **Present** the cycle report ([templates/optimization-report.md](../templates/optimization-report.md)): what we looked at, what we change, what we deliberately do not change and why.
9. **Execute** approved/auto changes one at a time; read back after each.
10. **Set read dates** for every change and test.
