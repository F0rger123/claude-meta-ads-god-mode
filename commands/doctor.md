---
description: "Check Ads God Mode setup: Python, profiles, isolation, env vars present, connectors"
argument-hint: "(none)"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/references/tool-comparison.md`.
3. Run adsgm doctor, list which ads MCP servers are connected in this session, and report what is missing with setup steps from README.md. Never print secret values.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
