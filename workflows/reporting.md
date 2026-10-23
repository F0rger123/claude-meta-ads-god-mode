# Workflow: reporting

Trigger: `/ads:report`, "Review D-Hauss ads this week." Skill: [ads-reporting](../skills/ads-reporting/SKILL.md).

1. **Resolve** client and dates (this week = last 7 complete days vs previous 7; month = calendar month vs previous; state the dates).
2. **Pull** per platform: spend, results (the profile's primary conversion), cost per result, value/ROAS if tracked; CRM-qualified leads if available (ask the user or read the CRM connector if one exists).
3. **Changes** - our changes (`adsgm log`, change history, activity log) and outside changes (seasonality, tracking incidents, attribution window changes).
4. **Winners / losers** - campaign and ad level, by impact in $ and leads, with confidence notes.
5. **Owner summary** in the fixed order: SPEND · RESULTS · COST PER RESULT · REVENUE/ROAS · WHAT WON · WHAT LOST · WHAT CHANGED · WHAT WE SHOULD DO NEXT.
6. **Platform detail** only for numbers that explain the summary.
7. **Next actions** - each marked "needs approval" or not; offer to plan them.

Monthly: use [templates/monthly-report.md](../templates/monthly-report.md) and add cross-platform comparison (if both platforms run) per the strategy skill.
