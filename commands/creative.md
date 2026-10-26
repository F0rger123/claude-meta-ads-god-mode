---
description: "Creative analysis, fatigue check, creative briefs, graphic ad rendering in the client's brand, and single-variable tests"
argument-hint: "<client> [ad set or campaign]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-creative-analysis/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/creative-testing.md`.
3. Produce briefs for the user's production workflow (no video rendering). For static graphics follow `${CLAUDE_PLUGIN_ROOT}/workflows/graphic-ads.md` and render with `adsgm creative render`; show the contact sheet; anything uploaded goes in PAUSED.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
