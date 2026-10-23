---
description: "Optimization cycle: wasted spend, constraints, fatigue, search terms, confidence-graded changes"
argument-hint: "<client> [meta|google] [timeframe]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-optimization/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/optimization-cycle.md`.
3. Max 3-5 changes per platform. Plan every write with adsgm plan.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
