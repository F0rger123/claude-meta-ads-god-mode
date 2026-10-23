---
description: "Budget review and changes with full current/proposed/percent/dollar/reason/risk disclosure"
argument-hint: "<client> [entity] [proposed amount]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-budgeting/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/budget-review.md`.
3. Every change goes through adsgm plan budget and shows the full disclosure block.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
