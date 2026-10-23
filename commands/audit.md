---
description: "Audit a client's Meta and/or Google Ads account with severity-ranked findings"
argument-hint: "<client> [meta|google]"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-audit/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/account-audit.md`.
3. Read-only audit. Every finding: severity, evidence, impact, confidence, action, approval required.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
