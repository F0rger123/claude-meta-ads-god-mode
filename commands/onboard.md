---
description: "Add or update an ads client profile (business, accounts, tracking, approval policy)"
argument-hint: "<client name>"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-client-onboarding/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/workflows/client-onboarding.md`.
3. Onboard the client named in the arguments. Ask questions in small groups. Verify every account id with a read before saving.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
