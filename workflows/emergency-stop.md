# Workflow: emergency stop

Trigger: `/ads:emergency-stop <client>`, "something is spending like crazy", "stop everything for X". Also `/ads:pause` for a single named entity.

Precision beats speed. A wrong pause in the wrong account is its own emergency.

## 1. Target precisely

- `adsgm use "<client>"` - the client must be named. If the user did not name one, ask. Never "pause everything in whatever account is connected."
- Read accounts for that client only; list them back: `CLIENT / PLATFORM / ACCOUNT`.

## 2. Detect

- Meta: `ads_insights_anomaly_signal`; today's spend by campaign/ad set vs budget; `ads_account_get_activity_logs` for recent changes (budget edits, new ads, someone else activating things).
- Google: GAQL today's `metrics.cost_micros` by campaign vs `campaign_budget.amount_micros`; `change_event` last 2 days.
- Build rows and run `adsgm anomaly --input rows.json` (flags: over 125% of daily budget, pace ≥1.5x for hours elapsed, ≥3 sd above trailing mean, spending with no history/budget, over budget with zero conversions).

## 3. Decide what to pause - only clearly identified entities

List each candidate: platform, account, entity id, name, spend today, budget, reason flagged. The user confirms the exact list. Prefer the lowest level that stops the problem (one ad set rather than the whole campaign) unless the user says otherwise.

## 4. Pause

```bash
adsgm plan pause --platform meta --account act_... --entity <id> --entity <id> --reason "runaway: $412 today vs $60 budget, 0 leads"
```
Pause is allowed even in read_only/draft mode, always with approval (the hook will prompt). Meta: `ads_update_entity` with `status: PAUSED` for each id. Google: writer plan with `set_status PAUSED`.

Never delete, never change budgets, never touch billing during an emergency - pause only.

## 5. Verify and summarize

Read each entity back (status PAUSED). Then:

```
EMERGENCY STOP - <client> - <time, timezone>
Paused: <entity list with ids>
What happened: <data: spend vs budget, when it started, recent changes found>
Likely cause: <evidence-based, labeled confidence>
Still running: <anything not paused and why>
Next: <investigate X; billing/limit changes are for the account owner in Ads Manager>
```
