---
description: "Competitor ad research from Meta Ad Library and Google Ads Transparency Center"
argument-hint: "<client> [competitor names]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-competitor-research/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/competitor-analysis.md`.
3. Public sources only. Never copy competitor ads verbatim.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
