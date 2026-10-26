# Workflow: portfolio sweep (all clients)

Trigger: `/ads:sweep [daily|weekly|monthly]`, "review all my clients", "which accounts need attention". Skill: [ads-portfolio](../skills/ads-portfolio/SKILL.md).

| Mode | Window | Per client | Extra |
|---|---|---|---|
| `daily` | today + yesterday, month-to-date | spend, results, today's spend vs budget per entity, tracking flag | anomaly focus. Fast: skip creative/search-term detail |
| `weekly` (default) | last 7 complete days vs prior 7 | full snapshot incl. entity CTR/frequency, learning state, search-term waste, lost IS (budget) | `adsgm learn auto` per client, per-client "what worked / didn't / fix next" |
| `monthly` | last calendar month vs the one before | totals + top entities | monthly report per client ([template](../templates/monthly-report.md)) |

Steps:
1. `adsgm clients list`. For each client, one at a time:
   - read accounts in the profile only (Meta official MCP / Google GAQL), build the snapshot, `adsgm snapshot save --file <tmp>.json`;
   - weekly: `adsgm learn auto --client <slug>`; then `adsgm learn summary --client <slug>`;
   - if a client's data can't be read, note "no data" and continue.
2. `adsgm sweep` → ranked portfolio + dashboard paths.
3. Report in this order:
   - **Portfolio table**: status, client, spend, results, CPL vs target, top issue, next step.
   - **RED clients first**: issues with evidence and the exact next step. Mark CRITICAL spend anomalies as candidates for `/ads:emergency-stop` (needs approval).
   - **Per client (weekly)**: what worked / what didn't (learning + this week) / fix next (max 3, approval flag).
   - **Portfolio patterns** (`adsgm learn summary --portfolio`) when 2+ clients share a tactic.
4. Nothing is changed during a sweep. Offer: "Open D-Hauss to fix the 2 RED items?"

Unattended (scheduled) sweeps: same steps; finish by writing the report files; don't ask questions; list approvals waiting for the human at the top.
