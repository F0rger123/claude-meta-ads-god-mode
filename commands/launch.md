---
description: "Plan and build a campaign PAUSED, show exactly what was created, wait for activation approval"
argument-hint: "<client> <platform> <brief, e.g. kitchen remodel leads York PA $60/day>"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-strategy/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/campaign-launch.md`.
3. Load the platform skill (meta-ads or google-ads) for the build steps. Everything is created PAUSED. Do not activate in this command.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
