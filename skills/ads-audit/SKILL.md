---
name: ads-audit
description: Structured ad account audits for Meta and Google Ads - structure, objectives, budgets, audiences, placements, keywords, creatives, copy, tracking, learning state, spend efficiency, fatigue, attribution and landing-page alignment, with severity, evidence, impact, confidence, action and approval flag per finding. Use for "audit", "review the account", "what's wrong with", "health check".
---

# Ads audit

Read-only by nature. Load with `ads-core` and the platform skill, then follow [workflows/account-audit.md](../../workflows/account-audit.md) with the platform checklist:
- Meta: [skills/meta-ads/workflows/account-audit.md](../meta-ads/workflows/account-audit.md)
- Google: [skills/google-ads/workflows/account-audit.md](../google-ads/workflows/account-audit.md)

## Finding format (every finding, no exceptions)

```
[SEVERITY] Title
Evidence   : numbers, dates, entity ids/names (from data you read in this session)
Impact     : what it likely costs or blocks ($/month, leads, learning)
Confidence : HIGH | MODERATE | EXPERIMENT  (+ why, if not HIGH)
Action     : concrete next step
Approval   : yes | no   (no only for read-only follow-ups or paused drafts)
```

Severity: **CRITICAL** (money is being wasted or results are untrustworthy now: broken/duplicated tracking, spend outside service area, wrong account, disapproved core ads), **HIGH** (large measurable waste or blocked growth), **MEDIUM** (meaningful inefficiency), **LOW** (hygiene), **OPPORTUNITY** (upside, not a problem).

## Rules

- Start with tracking. If conversions are untrustworthy, say every CPA/ROAS finding below is provisional.
- Rank findings by impact, not by checklist order. Top 3 first in an executive summary.
- Never present breakdown-table averages as reasons to exclude segments (Meta breakdown effect).
- Learning ad sets / new campaigns: "monitor", not verdicts.
- Separate PLATFORM FACT vs HEURISTIC when a finding rests on a rule of thumb.
- End with a prioritized action plan grouped: fix now (approval needed) / test next / monitor. Offer to draft the changes with `adsgm plan`.
- Template: [templates/optimization-report.md](../../templates/optimization-report.md).
