# Workflow: account audit

Trigger: `/ads:audit <client> [meta|google]`, "audit", "review the account". Skill: [ads-audit](../skills/ads-audit/SKILL.md).

1. **Resolve + select** - `adsgm use`; confirm platforms/accounts.
2. **Data pull (read-only)** - last 30 days, previous 30, last 7; structure + statuses; tracking state; change history/activity log.
3. **Tracking first** - run the [ads-tracking](../skills/ads-tracking/SKILL.md) reconciliation at summary depth. Decide whether performance findings are trustworthy.
4. **Platform checklist** - Meta: [checklist](../skills/meta-ads/workflows/account-audit.md). Google: [checklist](../skills/google-ads/workflows/account-audit.md).
5. **Landing pages** - top 1-3 destination URLs by spend through [ads-landing-page](../skills/ads-landing-page/SKILL.md) at summary depth.
6. **Write findings** - each with severity · evidence · impact · confidence · action · approval required.
7. **Executive summary** - account health in 3 sentences, top 3 findings, estimated monthly waste addressed (range).
8. **Action plan** - fix now (approval) / test next / monitor; offer to prepare `adsgm plan` tickets for the fix-now items.

Severity: CRITICAL · HIGH · MEDIUM · LOW · OPPORTUNITY (definitions in the skill).

Output template: [templates/optimization-report.md](../templates/optimization-report.md). No writes happen during an audit.
