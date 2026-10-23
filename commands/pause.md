---
description: "Pause specific, clearly identified campaigns / ad sets / ads for a named client"
argument-hint: "<client> <entity names or ids>"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/emergency-stop.md`.
3. Pause only the entities the user named, after verifying client, platform, account and entity ids by a read. Use steps 1, 3, 4 and 5 of the emergency workflow.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
