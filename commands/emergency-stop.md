---
description: "Detect runaway or anomalous spend for a named client and pause precisely identified entities"
argument-hint: "<client>"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/emergency-stop.md`.
3. Require an explicitly named client. Pause only; no deletes, budget or billing changes.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
