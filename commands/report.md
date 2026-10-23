---
description: "Business-owner report: spend, results, cost per result, what won/lost/changed, next steps"
argument-hint: "<client> [this week|last month|dates]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-reporting/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/reporting.md`.
3. Owner summary first, platform detail second. State the exact dates used.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
