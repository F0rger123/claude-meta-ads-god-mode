---
name: pulse
description: Quick Meta Ads account health check — last 7 days vs. prior 7, top-line deltas, learning status, fatigue and delivery flags, and the top 3 actions. Use when the user asks "how are we doing", wants a daily/weekly pulse, or before a standup. For deep diagnosis use ad-analysis; this is the fast scorecard.
---

# Account Pulse

A pulse is a 5-minute scorecard, not a report. Verdict first, numbers second, at most three recommended actions.

## Data
1. Freshest data wins: `data/raw/` files covering the last 14 full days at ad-set level, else pull:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pull_insights.py" --level adset --last 14 --daily`
   and `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pull_structure.py"` for statuses/learning info.
2. No API and no files → ask for an Ads Manager export (ad-set level, last 14 days, daily breakdown) and stop until it arrives.

## Compute (last 7 full days vs. prior 7)
- **Top line**: spend · results (the account's primary event) · cost per result · vs. target from `_config/account.md` (no target set → say so, compare to trailing average).
- **Deltas**: cost per result, CPM, link CTR, CVR — WoW %. Decompose the cost move: which of CPM/CTR/CVR drove it.
- **Flags** (each with the entity named):
  - Learning: ad sets in learning or learning-limited (from structure pull / effective_status).
  - Fatigue: frequency >3.0 (prospecting) with CTR down ≥20% vs. prior week.
  - Delivery: active ads with ~zero spend; ad sets spending <50% of budget.
  - Pacing: 7-day spend vs. plan (monthly budget ÷ days) — over/under 15%+.
  - Change collisions: shifts that coincide with entries in `optimization/CHANGELOG.md` — attribute, don't alarm.

## Output format
```
## Pulse — <date range>
**Verdict**: <one sentence: healthy / watch / act, and why>

| | last 7d | prior 7d | Δ |
|Spend|…|…|…|
|<Results>|…|…|…|
|Cost/<result> (target $X)|…|…|…|
|CPM / CTR / CVR|…|…|…|

**Flags**: <bulleted, entity-named, max 5 — or "none">
**Top actions**: 1) … 2) … 3) …   (each cites its number; anything execution-worthy routes to the ad-optimization skill)
```

## Rules
- 20–30% day-to-day cost variance is normal — flag only sustained (>3 days) or >50% moves as urgent.
- No verdicts on in-learning entities; mark them "(learning)" in tables.
- Sample honesty: under ~30 results/week account-wide, report weekly numbers only, skip the CVR decomposition.
- Never recommend a live change here — actions are hand-offs to ad-optimization, with its approval flow.
