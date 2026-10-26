# Workflow: autopilot (hands-off day-to-day fixes)

Trigger: `/ads:autopilot <client> [on|off|status|run]`, the daily `autopilot-run` scheduled job, "run it for me", "fix what's tanking without asking".

## What autopilot does and never does

| Does on its own (once switched on) | Still asks you |
|---|---|
| Pauses ads or ad sets that clearly fail the loser rules | New campaigns or ad sets going live |
| Fixes a failing or tired ad: builds a replacement, puts it in the **same ad set**, pauses the old one | Any budget increase |
| Adds small negative-keyword lists on Google (≤10 per run) | New locations, audiences, tracking changes |
| Stops completely if tracking looks broken | Deleting anything, billing, account settings |

The guard rails:
- It only swaps while the account's total daily budget is **at or under the client's daily spend cap**.
- It makes at most 3 swaps a week and touches at most 3 things per run, so it can't thrash.
- It never judges anything younger than 3 days or still in learning.

## Turn it on (part of onboarding)

1. Explain the table above in plain words. Then ask:
   - "Do you want autopilot on for this client?"
   - "What's the most it should ever spend per day across the account?" Suggest the budget plan's daily figure plus 10–20%.
   - "Which of the three fixes do you want?" (all are on by default)
2. Run `adsgm autopilot on --client <slug> --cap <amount> [--actions pause_losers,fix_and_relaunch,google_negatives]`. It refuses without a cap, and in read_only or draft mode.
3. Ask whether it should also run on its own every morning. If yes, add the `autopilot-run` job from `/ads:schedule` with their OK.
4. To switch it off any time: `adsgm autopilot off --client <slug>` (or just say "turn autopilot off for X").

## Each run

1. `adsgm use <client>`. Refresh the snapshot (read-only). `adsgm autopilot candidates --client <slug>` lists losers, tired ads and Google waste by the client's rules. If it says tracking is broken, stop and report.
2. **Losers:** for each one (max 3), run `adsgm plan pause --account ... --entity <id> --reason "<why>" --predict-metric cpl --predict-direction down --baseline <cpl> --baseline-n <results> --tags autopilot-pause`. Then pause it (`ads_update_entity` status PAUSED). The verdict should be `auto`. If it isn't, leave it for approval in the report.
3. **Fix and relaunch:** diagnose the failure (hook, offer, landing page, audience fit, fatigue) using `ads-creative-analysis` and the client's learning summary.
   - Write the replacement: new copy, and a graphic via `adsgm creative render` if the ad was static.
   - Upload and **create it PAUSED in the same ad set**.
   - Run `adsgm plan creative_swap --account ... --entity <new ad id> --replaces <old ad id> --adset <ad set id> --account-daily-budget <current total> --predict-metric ctr --predict-direction up --baseline <old ctr> --baseline-n <clicks> --tags autopilot-swap,<hook-type>`.
   - If the verdict is `auto`: activate the new ad (`ads_activate_entity`), then pause the old one. Read both back.
   - Before planning, confirm by a read that the new entity is an **ad** in the same ad set as the old one, and that no budget changes. The gate checks the ticket, the cap and the count, but it can't see the entity's type.
4. **Google waste:** search-term review, then up to 10 phrase or exact negatives that block no converting query. Use a writer plan with `add_negative_keywords`, then `adsgm plan --google-plan` (`auto` within the limit), then execute.
5. **Report** (what autopilot did, why, with ids, plus what is waiting for approval). Add it to the client's weekly report. Everything is in the audit log and the learning loop, so next week's run knows which fixes worked.

## Campaign-level problems

If a whole campaign is failing (several ad sets losing, or the offer itself not converting), autopilot **pauses** the losers and writes a rebuild plan: a new campaign created PAUSED, with the reasons and the learning data behind them. Launching the new campaign waits for a human yes, because it's new spend.
