---
name: ads-portfolio
description: Multi-client agency operations - sweep all clients at once (who's on track, overspending, broken, or ready to scale), the self-learning loop (predict, change, judge the outcome, learn what works and what doesn't per client), and scheduled daily/weekly/monthly runs. Use for "review all my clients", "which accounts need attention", "what's working across clients", "set up weekly reports", "automate the reviews".
---

# Portfolio, learning loop and schedules

Load with `ads-core`. Workflows: [portfolio sweep](../../workflows/portfolio-sweep.md) · [learning loop](../../workflows/learning-loop.md) · [scheduled runs](../../workflows/scheduled-runs.md).

## Sweep: every client, one view

For each client profile (`adsgm clients list`):
1. Read numbers with the platform MCP tools (read-only). Use the last 7 complete days and the prior 7, today and yesterday for spend checks, month-to-date spend, entity rows (campaign / ad set or ad group) with status, learning state, spend, results, CTR (with prior CTR), frequency, daily budget, today's spend and hours elapsed. For Google, also search-term waste and impression share lost to budget.
2. Build a snapshot ([schema](../../godmode/snapshots.py)) and save it with `adsgm snapshot save --file snap.json`. Account IDs must belong to that client, or the save is refused.
3. After every client is saved, run `adsgm sweep`. It writes `portfolio.md`, `portfolio.html` (dashboard) and `portfolio.json` to `~/.ads-godmode/reports/<date>/` and returns clients ranked RED / AMBER / GREEN, each with its top issues and next step.
4. Report: the portfolio table first, then per-client issues. Offer to open the clients that need work (`/ads:optimize <client>`). A sweep never changes anything.

One client at a time for data. Never mix numbers between clients. If a client's accounts can't be read, mark that client "no data" rather than guessing.

## Learning loop: get smarter per client

- **When planning a change**, attach a prediction:
  `adsgm plan budget ... --predict-metric results --predict-direction up --predict-pct 15 --baseline 11 --baseline-n 11 --read-after 7 --tags budget-up-20`.
  Pick the metric that expresses the goal: budget up → results up; negatives → cpl down; new hook → ctr up.
- **At the read date** (or during weekly sweeps), run `adsgm learn auto --client X` to judge the outcome from the latest snapshot. Or record it by hand with `adsgm learn record ...`. Each outcome is graded **worked / failed / inconclusive**, with sample-size and noise checks.
- **Creative tests and other insights:** `adsgm learn lesson --client X --tags ugc-hook --verdict worked --text "..."`.
- **Before recommending anything** for a client, run `adsgm learn summary --client X`. Lead with what has worked for this client. Don't repeat what failed without a new hypothesis. Label the learnings as **CLIENT-SPECIFIC RULE** (HIGH or MODERATE when decided on 3+ outcomes, EXPERIMENT below that).
- **Across clients:** `adsgm learn summary --portfolio` shows tactic-level win rates (label: PORTFOLIO HEURISTIC). Use it as a starting hypothesis for a new client, never as evidence about that client.
- **Learnings change recommendations, never limits.** If lessons suggest looser guarded-auto limits, propose it. The human edits the profile.

## Autopilot (per client, on/off)

Hands-off day-to-day fixes inside budgets the human already approved: pause clear losers, swap tired or failing ads for fixed ones in the same ad set (while the account's total daily budget is at or under the client's cap; max 3 swaps a week), and add small Google negative lists. Never: new campaigns live, budget increases, new geos, tracking, deletes, billing. Switch it with `adsgm autopilot on|off --client X --cap <daily max>`. Workflow: [autopilot](../../workflows/autopilot.md). Always mention it during onboarding and ask whether they want it.

## Scheduled runs

`/ads:schedule` sets up daily, weekly and monthly runs. They run with `ADS_GODMODE_UNATTENDED=1`:
- Writes are denied unless the client's profile sets `automation.allow_unattended_writes: true`.
- Even then, nothing that needs approval can run.
- Scheduled runs refresh snapshots, judge due predictions, run the sweep and write reports. Problems become recommendations in the report, waiting for you.

## Reporting what works / what doesn't

For each client, close every sweep or weekly review with:
- **What worked**: from the learning summary and this week's winners, with numbers.
- **What didn't**: failed tactics and losing campaigns/ads, with numbers.
- **What to fix next**: 3 items max per client, each tagged "needs approval" or "no approval needed", with the exact command or plan.
