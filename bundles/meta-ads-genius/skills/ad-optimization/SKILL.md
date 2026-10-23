---
name: ad-optimization
description: Turn Meta Ads findings into specific, safe, approved changes — kill/scale/iterate decisions, budget shifts, creative swaps, fatigue fixes, learning-phase-aware scheduling of edits. Use when the user wants to improve results, decide what to pause or scale, reallocate budget, fix creative fatigue or rising CPA/CPL, or asks "what should I change?"
---

# Meta Ads Optimization

Optimization is an operating system, not a bag of tricks: a target number, a decision tree run on a cadence, and change discipline that never fights the delivery optimizer. Every change is proposed → approved → executed → logged → checked.

## Prime directives
1. **Read-only by default.** Every live change needs the user's explicit approval of that specific change. Execution details and hard limits: `references/safety-governance.md` — load it before executing anything.
2. **Never fight the optimizer.** No pausing segments off breakdown-average CPA (see the ad-analysis skill's breakdown-effect reference); no daily knob-fiddling; batch edits; respect learning phase.
3. **Every swap needs a replacement.** Pausing without replacing = shrinking. What to build in place of each failure type is in the decision tree.
4. **Log everything.** In a workspace with `optimization/CHANGELOG.md`, append every executed change immediately: date, entity, change, reason, expected outcome, check date.

## The target number: TCPL
Optimize to **target cost per qualified lead/result**, not raw CPL. Derive (pick the strongest available, label the source):
- From economics: `TCPL = target cost per sales-meeting × (qualified-lead → meeting rate)` — or for e-comm, breakeven CPA = AOV × margin.
- From history: `TCPL = trailing-30-day cost per qualified lead × 0.80` (a stretch, not a fantasy).
- Both available → take the MIN.
Raw platform leads lie; qualification lives in the CRM. If the workspace `_config/account.md` has targets, use those.

## Derived thresholds (from TCPL)
| Rule | Formula | Meaning |
|---|---|---|
| Minimum data before judging | spend ≥ **3 × TCPL** | Below this, WAIT (at 3× with zero results, ~95% confidence it's not luck) |
| Swap line | cost/QL > **1.5 × TCPL** | Persistent breach → swap the ad |
| Kill line (hard) | spend ≥ 3 × TCPL **and** 0 conversions | Pause now (still requires ≥7 days or ≥20 clicks unless spend is runaway) |
| Ad-count ceiling | (daily budget × 14) ÷ (2 × TCPL) | More live ads than this = starvation; sweet spot 6–10 |
| Tests per week | (monthly budget × 0.20) ÷ (3 × TCPL) ÷ 4 | Sustainable test velocity |
| Learning budget | daily ≥ (TCPL × 50) ÷ 7 per ad set | Else knowingly learning-limited |

## Weekly cadence
- **Monday — decision day.** Pull rolling 14-day data (`--daily`), run the decision tree (`references/decision-tree.md`) on every active ad, execute approved swaps/graduations, log.
- **Wednesday — test day.** Launch the week's new tests (paused → approved → live); run day-7 delivery checks on last week's launches.
- **Friday — budget day.** Scaling moves, rollbacks, reallocations per `references/scaling-budget.md`.
- **Monthly** — full review against TCPL trend; re-derive TCPL if the funnel shifted.

## Decision quick card (full tree in references/decision-tree.md)
1. Spend < 3×TCPL → **WAIT**
2. Delivery ~zero after 7 days (CBO chose not to spend it) → **KILL** (the auction rejected the creative; rebuild hook/visual, not copy)
3. Zero platform leads at 3×TCPL → **SWAP**, abandon the concept
4. Leads but ~zero qualified → **SWAP**, keep format, add ICP-filtering specificity
5. Cost/QL ≤ TCPL → winner track; 1–1.5× → **MONITOR**; >1.5× → **SWAP** (same angle, new execution)
6. **Graduate** to scaling only when ALL: ≥5 QLs · QL rate ≥60% · cost ≤ TCPL · ≥14 days live · ≥1 QL in last 7 days
7. Fatigue (scaling ads): frequency 3.0–3.5 or cost +20% → build 2 iterations now; >3.5 or +40% → swap immediately

## Scaling & budget rules (details in references/scaling-budget.md)
- Vertical: **+20% per 3–5 days** (30% absolute max) — bigger jumps reset learning. Rollback if cost >1.5× target after a step: cut 20–30%, wait 7 days, then scale horizontally instead.
- Portfolio: ~70% proven / 20% promising / 10% experiments; structural 80/20 scaling-vs-testing campaign split.
- Learning-limited remediation ladder: broaden audience → raise budget → optimize a higher-funnel event → consolidate ad sets.

## Change hygiene
- Significant edits (budget >~20%, targeting, creative, optimization goal) reset learning — batch them into one session per ad set, never a drip.
- One variable at a time on anything you call a test.
- Set the check date (3–7 days) at execution time; on the check date, verify against the expected outcome and close the changelog loop.

## References
- `references/decision-tree.md` — full two-stage tree, swap-replacement rules, graduation, fatigue playbook, quality scoring.
- `references/scaling-budget.md` — scaling protocols, kill rules with data gates, 70/20/10, seasonality, measurement hierarchy.
- `references/safety-governance.md` — **mandatory before any live execution**: approval gates, paused-by-default, rate limits, account-ban failure modes.
