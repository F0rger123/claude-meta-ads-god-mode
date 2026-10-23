---
description: "Diagnose pixel, CAPI, Google conversions, GA4, GTM, UTMs and CRM attribution"
argument-hint: "<client>"
---

Arguments: $ARGUMENTS

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/ads-core/SKILL.md` (client resolution, `adsgm use`, connector routing, write gate).
2. Load `${CLAUDE_PLUGIN_ROOT}/skills/ads-tracking/SKILL.md` and follow `${CLAUDE_PLUGIN_ROOT}/skills/meta-ads/references/attribution-and-signals.md`.
3. Read-only diagnosis. Tracking fixes are approval-only tracking actions.

`adsgm` = `python "${CLAUDE_PLUGIN_ROOT}/adsgm.py"`. If the client in the arguments is missing or ambiguous, ask - never guess.
